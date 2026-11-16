import gzip
from collections.abc import Iterator

import pytest
from http_server import REQUESTS, Route, serve

from a11y_eco.dom import parse_html
from a11y_eco.loader import USER_AGENT
from a11y_eco.models import Download
from a11y_eco.network import (
    ACCEPT_ENCODING,
    download,
    download_all,
    fetch_resources,
    plan_downloads,
)

CSS = b"body { color: black; }\n" * 100
ROUTES = {
    "/plain.css": Route(CSS, headers={"Content-Type": "text/css"}),
    "/packed.css": Route(gzip.compress(CSS), headers={"Content-Encoding": "gzip"}),
    "/moved.css": Route(status=301, headers={"Location": "/plain.css"}),
    "/cookies.js": Route(b"x", headers={"Set-Cookie": "a=1", "set-cookie": "b=2"}),
    "/broken.js": Route(b"error", status=500),
    "/slow.js": Route(b"x", delay=0.5),
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
