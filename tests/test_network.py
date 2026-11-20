import gzip
import struct
from collections.abc import Iterator

import pytest
from http_server import REQUESTS, Route, serve

from a11y_eco.dom import parse_html
from a11y_eco.imagesize import PNG_SIGNATURE
from a11y_eco.loader import USER_AGENT
from a11y_eco.models import Download, ImageSize
from a11y_eco.network import (
    ACCEPT_ENCODING,
    MAX_DOWNLOAD_BYTES,
    READABLE_ENCODING,
    _inflate,
    download,
    download_all,
    fetch_resources,
    plan_downloads,
)

CSS = b"body { color: black; }\n" * 100
PHOTO = PNG_SIGNATURE + struct.pack(">I4sII", 13, b"IHDR", 1280, 960) + bytes(5000)
ROUTES = {
    "/plain.css": Route(CSS, headers={"Content-Type": "text/css"}),
    "/packed.css": Route(gzip.compress(CSS), headers={"Content-Encoding": "gzip"}),
    "/moved.css": Route(status=301, headers={"Location": "/plain.css"}),
    "/cookies.js": Route(b"x", headers={"Set-Cookie": "a=1", "set-cookie": "b=2"}),
    "/broken.js": Route(b"error", status=500),
    "/slow.js": Route(b"x", delay=0.5),
    "/photo.png": Route(PHOTO, headers={"Content-Type": "image/png"}),
}


@pytest.fixture(scope="module")
def server() -> Iterator[str]:
    with serve(ROUTES) as base:
        yield base


def test_counts_the_bytes_as_transferred(server: str) -> None:
    plain = download(f"{server}/plain.css", timeout=2)
    packed = download(f"{server}/packed.css", timeout=2)

    assert plain.transferred == len(CSS)
    assert packed.transferred == len(gzip.compress(CSS))  # never decompressed
    assert packed.headers["content-encoding"] == "gzip"


def test_announces_itself_and_the_compressions_it_accepts(server: str) -> None:
    download(f"{server}/plain.css", timeout=2)

    assert REQUESTS[-1]["User-Agent"] == USER_AGENT
    assert REQUESTS[-1]["Accept-Encoding"] == ACCEPT_ENCODING


def test_follows_redirections_and_reports_them(server: str) -> None:
    result = download(f"{server}/moved.css", timeout=2)

    assert (result.status, result.redirected, result.ok) == (200, True, True)


def test_reads_the_dimensions_of_downloaded_images(server: str) -> None:
    photo = download(f"{server}/photo.png", timeout=2)
    stylesheet = download(f"{server}/plain.css", timeout=2)

    assert (photo.image_size, photo.transferred) == (ImageSize(1280, 960), len(PHOTO))
    assert stylesheet.image_size is None


def test_keeps_every_value_of_a_repeated_header(server: str) -> None:
    result = download(f"{server}/cookies.js", timeout=2)

    assert result.headers["set-cookie"].splitlines() == ["a=1", "b=2"]


def test_stops_at_the_size_limit(server: str) -> None:
    result = download(f"{server}/plain.css", timeout=2, max_bytes=100)

    assert (result.transferred, result.complete) == (100, False)


@pytest.mark.parametrize(
    ("path", "status"),
    [
        pytest.param("/broken.js", 500, id="server-error-is-a-response"),
        pytest.param("/missing.js", 404, id="not-found-is-a-response"),
    ],
)
def test_http_errors_are_responses_not_failures(server: str, path: str, status: int) -> None:
    result = download(f"{server}{path}", timeout=2)

    assert (result.status, result.ok) == (status, False)


@pytest.mark.parametrize(
    "url",
    [
        pytest.param("/slow.js", id="timeout"),
        pytest.param("http://127.0.0.1:9/", id="connection-refused"),
        pytest.param("http://", id="malformed-address"),
    ],
)
def test_failures_never_raise(server: str, url: str) -> None:
    address = f"{server}{url}" if url.startswith("/") else url

    assert download(address, timeout=0.2) == Download(address)


def test_download_all_keeps_the_order(server: str) -> None:
    urls = [f"{server}/plain.css", f"{server}/missing.js", f"{server}/packed.css"]

    results = download_all(urls, timeout=2, workers=2)

    assert [result.url for result in results] == urls
    assert [result.status for result in results] == [200, 404, 200]


PAGE = "https://www.example.com/"
MARKUP = (
    '<link rel="stylesheet" href="/site.css">'
    '<script src="https://cdn.example.net/lib.js"></script>'
    '<img src="/lazy.png" loading="lazy" alt="">'
    '<img src="data:image/png;base64,AA" alt="">'
)


def test_plan_starts_with_the_page_and_skips_external_by_default() -> None:
    urls = plan_downloads(parse_html(MARKUP, url=PAGE), include_external=False)

    assert urls == [PAGE, "https://www.example.com/site.css"]


def test_plan_includes_external_resources_on_request() -> None:
    urls = plan_downloads(parse_html(MARKUP, url=PAGE), include_external=True)

    assert urls == [PAGE, "https://www.example.com/site.css", "https://cdn.example.net/lib.js"]


def test_plan_of_a_local_file_keeps_only_absolute_addresses() -> None:
    urls = plan_downloads(parse_html(MARKUP), include_external=True)

    assert urls == ["https://cdn.example.net/lib.js"]


def test_plan_downloads_each_address_once() -> None:
    markup = '<img src="/logo.png" alt=""><img src="/logo.png" alt="">'

    urls = plan_downloads(parse_html(markup, url=PAGE), include_external=False)

    assert urls == [PAGE, "https://www.example.com/logo.png"]


def test_fetch_resources_downloads_the_page_and_its_resources(server: str) -> None:
    markup = '<link rel="stylesheet" href="/packed.css"><script src="/missing.js"></script>'

    network = fetch_resources(
        parse_html(markup, url=f"{server}/plain.css"), include_external=False, timeout=2
    )

    assert [download.status for download in network.downloads] == [200, 200, 404]
    assert (network.requests, network.failed, network.skipped) == (3, 1, 0)
    assert network.transferred == len(CSS) + len(gzip.compress(CSS))
    assert network.complete


def test_fetch_resources_respects_the_limit(server: str) -> None:
    markup = "".join(f'<img src="/{i}.png" alt="">' for i in range(10))

    network = fetch_resources(
        parse_html(markup, url=f"{server}/"), include_external=False, timeout=2, limit=4
    )

    assert (network.requests, network.skipped, network.complete) == (4, 7, False)


GZIP = {"Content-Type": "text/css", "Content-Encoding": "gzip"}
FAKE_BROTLI = b"\x1b\x03\x00\x00brotli bytes that only a browser can read"
CSS_SITE = {
    "/index.html": Route(b"<p>Page</p>", headers={"Content-Type": "text/html"}),
    "/theme.css": Route(gzip.compress(b'@import url("parts/base.css"); body {}'), headers=GZIP),
    "/parts/base.css": Route(b'@import "../theme.css"; @import url(fonts.css);'),
    "/parts/fonts.css": Route(b"/* no import */"),
    "/brotli.css": Route(
        FAKE_BROTLI,
        headers={"Content-Encoding": "br"},
        negotiated={READABLE_ENCODING: Route(gzip.compress(b'@import "late.css";'), headers=GZIP)},
    ),
    "/late.css": Route(b"p {}"),
    "/cdn-import.css": Route(b"@import url(https://cdn.example.net/x.css);"),
}


@pytest.fixture(scope="module")
def css_site() -> Iterator[str]:
    with serve(CSS_SITE) as base:
        yield base


def fetch(css_site: str, stylesheet: str, limit: int = 50) -> list[str]:
    """Fetch a page that links one stylesheet; return the downloaded paths."""
    page = parse_html(f'<link rel="stylesheet" href="{stylesheet}">', url=f"{css_site}/index.html")
    network = fetch_resources(page, include_external=False, timeout=2, limit=limit)

    return [download.url.removeprefix(css_site) for download in network.downloads]


def test_imports_are_followed_wave_after_wave(css_site: str) -> None:
    assert fetch(css_site, "/theme.css") == [
        "/index.html",
        "/theme.css",
        "/parts/base.css",
        "/parts/fonts.css",
    ]


def test_stylesheet_measured_in_brotli_is_read_again_in_gzip(css_site: str) -> None:
    page = parse_html('<link rel="stylesheet" href="/brotli.css">', url=f"{css_site}/index.html")
    REQUESTS.clear()

    network = fetch_resources(page, include_external=False, timeout=2)
    brotli = network.downloads[1]

    assert brotli.transferred == len(FAKE_BROTLI)  # the measure keeps the Brotli size
    assert network.downloads[2].url == f"{css_site}/late.css"
    assert network.requests == 3  # the reading request is not counted
    assert [r["Accept-Encoding"] for r in REQUESTS].count(READABLE_ENCODING) == 1


def test_imports_from_other_hosts_are_not_followed_by_default(css_site: str) -> None:
    assert fetch(css_site, "/cdn-import.css") == ["/index.html", "/cdn-import.css"]


def test_imports_count_toward_the_limit(css_site: str) -> None:
    page = parse_html('<link rel="stylesheet" href="/theme.css">', url=f"{css_site}/index.html")
    network = fetch_resources(page, include_external=False, timeout=2, limit=3)

    assert (network.requests, network.skipped, network.complete) == (3, 1, False)


def test_decompression_stops_at_the_size_limit() -> None:
    bomb = gzip.compress(bytes(MAX_DOWNLOAD_BYTES + 1000))  # about 10 KB, expands to 10 MB

    assert len(_inflate(bomb)) == MAX_DOWNLOAD_BYTES


def test_damaged_compressed_data_gives_nothing() -> None:
    assert _inflate(b"not gzip at all") == b""
