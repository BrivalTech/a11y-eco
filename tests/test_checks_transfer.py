import pytest

from a11y_eco.checks import transfer
from a11y_eco.checks.base import NetworkRule
from a11y_eco.dom import parse_html
from a11y_eco.models import Download, ImageSize, NetworkMetrics

CSS = {"content-type": "text/css; charset=utf-8", "cache-control": "max-age=3600"}
BIG = transfer.MIN_COMPRESSIBLE_BYTES
ANY_PAGE = parse_html("", url="https://www.example.com/")
SITE = "https://www.example.com/"


def file(url: str = "https://www.example.com/a.css", **headers: str) -> Download:
    """A received file of 1 KiB, with CSS headers unless told otherwise."""
    return Download(url, status=200, transferred=BIG, headers={**CSS, **headers})


def run(rule: NetworkRule, *downloads: Download) -> list[str]:
    """Return the addresses reported by a rule."""
    return [finding.snippet for finding in rule.run(NetworkMetrics(downloads=downloads), ANY_PAGE)]


def details(rule: NetworkRule, *downloads: Download) -> list[dict[str, int]]:
    findings = rule.run(NetworkMetrics(downloads=downloads), ANY_PAGE)
    return [dict(finding.details) for finding in findings]


@pytest.mark.parametrize(
    ("download", "reported"),
    [
        pytest.param(file(), True, id="uncompressed-css"),
        pytest.param(file(**{"content-encoding": "gzip"}), False, id="gzip"),
        pytest.param(file(**{"content-encoding": "br"}), False, id="brotli"),
        pytest.param(file(**{"content-encoding": "identity"}), True, id="identity-is-none"),
        pytest.param(file(**{"content-type": "image/svg+xml"}), True, id="svg"),
        pytest.param(file(**{"content-type": "text/html"}), True, id="html"),
        pytest.param(file(**{"content-type": "image/png"}), False, id="png-already-compressed"),
        pytest.param(
            Download("u", status=200, transferred=BIG - 1, headers=CSS), False, id="tiny-file"
        ),
        pytest.param(
            Download("u", status=404, transferred=BIG, headers=CSS), False, id="not-received"
        ),
    ],
)
def test_uncompressed_text(download: Download, reported: bool) -> None:
    assert run(transfer.uncompressed_text, download) == ([download.url] if reported else [])


@pytest.mark.parametrize(
    ("headers", "reported"),
    [
        pytest.param({"content-type": "text/css"}, True, id="no-cache-header"),
        pytest.param({"cache-control": "max-age=60"}, False, id="cache-control"),
        pytest.param({"cache-control": "no-store"}, False, id="deliberately-not-cached"),
        pytest.param({"expires": "Thu, 01 Dec 2033 16:00:00 GMT"}, False, id="expires"),
        pytest.param({"content-type": "text/html"}, False, id="html-page-not-checked"),
    ],
)
def test_missing_cache_headers(headers: dict[str, str], reported: bool) -> None:
    download = Download("https://www.example.com/a.css", status=200, headers=headers)

    assert run(transfer.missing_cache_headers, download) == ([download.url] if reported else [])


PAGE = Download(
    "https://www.example.com/",
    status=200,
    headers={"content-type": "text/html", "set-cookie": "session=1"},
)


def test_one_cookie_domain_is_tolerated() -> None:
    assert run(transfer.static_files_with_cookies, PAGE, file()) == []


def test_two_cookie_domains_report_one_static_file_each() -> None:
    tracker = "https://cdn.example.net/"
    downloads = (
        PAGE,
        file(),
        file("https://www.example.com/b.css"),  # same domain: reported once only
        file(f"{tracker}pixel.gif", **{"set-cookie": "id=42"}),
        file(f"{tracker}lib.js"),
    )

    assert run(transfer.static_files_with_cookies, *downloads) == [
        "https://www.example.com/a.css",
        f"{tracker}pixel.gif",
    ]
    assert details(transfer.static_files_with_cookies, *downloads) == [{"count": 2, "limit": 1}] * 2


def test_domains_without_cookies_are_not_counted() -> None:
    downloads = (file(), file("https://cdn.example.net/a.js"), file("https://img.example.org/a"))

    assert run(transfer.static_files_with_cookies, *downloads) == []


def redirected(url: str) -> Download:
    return Download(url, status=200, redirected=True)


def test_one_redirection_is_tolerated() -> None:
    assert run(transfer.too_many_redirects, redirected("http://example.com/"), file()) == []


def test_every_redirection_is_reported_beyond_the_limit() -> None:
    downloads = (redirected("http://example.com/"), file(), redirected("https://example.com/a"))

    assert run(transfer.too_many_redirects, *downloads) == [
        "http://example.com/",
        "https://example.com/a",
    ]
    assert details(transfer.too_many_redirects, *downloads) == [{"count": 2, "limit": 1}] * 2


def image(name: str, width: int, height: int, transferred: int = 41_000) -> Download:
    size = ImageSize(width, height)

    return Download(f"{SITE}{name}", status=200, transferred=transferred, image_size=size)


def oversized(markup: str, *downloads: Download) -> list[dict[str, int]]:
    """Return the details of the images reported on a page."""
    page = parse_html(markup, url=SITE)
    findings = transfer.oversized_images.run(NetworkMetrics(downloads=downloads), page)

    return [dict(finding.details) for finding in findings]


def test_thumbnail_of_a_large_image_is_reported() -> None:
    details = oversized('<img src="a.png" width="70" height="60">', image("a.png", 350, 300))

    assert details == [
        {"width": 350, "height": 300, "shown_width": 70, "shown_height": 60, "wasted": 34_440}
    ]


@pytest.mark.parametrize(
    "markup",
    [
        pytest.param('<img src="a.png" width="175" height="150">', id="high-density-screen"),
        pytest.param('<img src="a.png">', id="size-unknown"),
        pytest.param('<img src="a.png" width="70">', id="height-unknown"),
        pytest.param('<img src="a.png" width="20%" height="60">', id="not-in-pixels"),
        pytest.param(
            '<img src="a.png" width="70" height="60" srcset="a.png 350w">', id="responsive"
        ),
        pytest.param(
            '<picture><img src="a.png" width="70" height="60"></picture>', id="in-picture"
        ),
        pytest.param(
            '<img src="a.png" width="70" height="60"><img src="a.png" width="350" height="300">',
            id="also-shown-large",
        ),
        pytest.param(
            '<img src="a.png" width="70" height="60"><img src="a.png">',
            id="also-shown-at-unknown-size",
        ),
        pytest.param('<img src="b.png" width="70" height="60">', id="not-downloaded"),
    ],
)
def test_images_that_may_be_shown_at_their_size_are_not_reported(markup: str) -> None:
    assert oversized(markup, image("a.png", 350, 300)) == []


def test_waste_below_five_percent_of_the_page_is_tolerated() -> None:
    markup = '<img src="a.png" width="70" height="60">'
    heavy_video = Download(f"{SITE}film.mp4", status=200, transferred=1_000_000)

    assert oversized(markup, image("a.png", 350, 300), heavy_video) == []
