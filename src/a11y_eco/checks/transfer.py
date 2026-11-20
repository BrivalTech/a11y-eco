"""Rules about what really travels on the network (RWEB), with --fetch-resources.

They read the responses of the servers: compression, cache headers, cookies,
redirections and the dimensions of images. Cookies set by JavaScript are invisible
here, and urllib reports a chain of redirections as one: the counts are minimum values.
"""

from __future__ import annotations

from collections.abc import Collection, Iterator
from urllib.parse import urljoin, urlsplit

from a11y_eco.checks.base import NetworkViolation, network_rule
from a11y_eco.dom import Document, Element
from a11y_eco.models import Download, ImageSize, NetworkMetrics, Severity
from a11y_eco.resources import base_url

MAX_COOKIE_DOMAINS = 1
MAX_REDIRECTS = 1
MIN_COMPRESSIBLE_BYTES = 1024
MAX_WASTED_SHARE = 0.05
SCREEN_DENSITY = 2
_TEXT_TYPES = frozenset(
    {
        "text/html",
        "text/css",
        "text/javascript",
        "application/javascript",
        "application/x-javascript",
        "image/svg+xml",
    }
)


@network_rule("ECO-COMPRESSION", severity=Severity.WARNING, reference="RWEB_0076")
def uncompressed_text(network: NetworkMetrics, document: Document) -> Iterator[Download]:
    """HTML, CSS, JavaScript and SVG files should be sent compressed (gzip, Brotli…)."""
    for download in network.downloads:
        encoding = download.headers.get("content-encoding", "identity").strip().lower()
        if (
            download.ok
            and _media_type(download) in _TEXT_TYPES
            and encoding == "identity"
            and download.transferred >= MIN_COMPRESSIBLE_BYTES
        ):
            yield download


@network_rule("ECO-CACHE-HEADERS", severity=Severity.WARNING, reference="RWEB_0075")
def missing_cache_headers(network: NetworkMetrics, document: Document) -> Iterator[Download]:
    """Static files should say how long to keep them, with Expires or Cache-Control."""
    for download in network.downloads:
        if (
            _is_static(download)
            and "cache-control" not in download.headers
            and "expires" not in download.headers
        ):
            yield download


@network_rule("ECO-COOKIE-DOMAINS", severity=Severity.WARNING, reference="RWEB_0081")
def static_files_with_cookies(
    network: NetworkMetrics, document: Document
) -> Iterator[NetworkViolation]:
    """Static files should come from at most one domain that uses cookies.

    A domain uses cookies as soon as one of its responses sets one: the browser then
    sends them back with every request to that domain, static files included.
    """
    cookie_hosts = {_host(d) for d in network.downloads if "set-cookie" in d.headers}
    first_static_file: dict[str | None, Download] = {}

    for download in network.downloads:
        if _is_static(download) and _host(download) in cookie_hosts:
            first_static_file.setdefault(_host(download), download)

    if len(first_static_file) > MAX_COOKIE_DOMAINS:
        details = {"count": len(first_static_file), "limit": MAX_COOKIE_DOMAINS}
        for download in first_static_file.values():
            yield NetworkViolation(download, details)


@network_rule("ECO-REDIRECTS", severity=Severity.WARNING, reference="RWEB_0112")
def too_many_redirects(network: NetworkMetrics, document: Document) -> Iterator[NetworkViolation]:
    """Loading the page should not go through more than one redirection."""
    redirected = [download for download in network.downloads if download.redirected]

    if len(redirected) > MAX_REDIRECTS:
        details = {"count": len(redirected), "limit": MAX_REDIRECTS}
        for download in redirected:
            yield NetworkViolation(download, details)


@network_rule("ECO-IMAGE-SIZE", severity=Severity.INFO, reference="RWEB_0048")
def oversized_images(network: NetworkMetrics, document: Document) -> Iterator[NetworkViolation]:
    """Images should not be much larger than the size they are displayed at.

    The displayed size is read from the width and height attributes of <img>, which
    CSS may change: a heuristic, hence the "info" severity. Responsive images (srcset,
    <picture>) let the browser choose their file, and are left out.
    """
    files = {d.url: (d, d.image_size) for d in network.downloads if d.ok and d.image_size}
    wasted: list[tuple[Download, ImageSize, ImageSize, int]] = []

    for url, display in _largest_displays(document, files).items():
        file, size = files[url]
        useful = display.pixels * SCREEN_DENSITY**2
        if size.pixels > useful:
            # The bytes in excess, in proportion to the pixels in excess.
            wasted.append(
                (file, size, display, round(file.transferred * (1 - useful / size.pixels)))
            )

    if sum(waste for *_, waste in wasted) <= MAX_WASTED_SHARE * network.transferred:
        return

    for file, size, display, waste in wasted:
        details = {
            "width": size.width,
            "height": size.height,
            "shown_width": display.width,
            "shown_height": display.height,
            "wasted": waste,
        }
        yield NetworkViolation(file, details)


def _largest_displays(document: Document, files: Collection[str]) -> dict[str, ImageSize]:
    """Find the largest declared display of each downloaded image.

    An image shown at several sizes is judged by the largest one, and an image with
    one display of unknown size is left out: it may well be shown large there.
    """
    base = base_url(document)
    displays: dict[str, ImageSize | None] = {}

    for img in document.find_all("img"):
        src = (img.get("src") or "").strip()
        url = urljoin(base, src) if base else src
        if not src or url not in files:
            continue
        declared = _declared_size(img)
        if url not in displays:
            displays[url] = declared
            continue
        known = displays[url]
        if known is not None:  # None stays None: one unknown display is enough
            displays[url] = None if declared is None else max(known, declared, key=_pixels)

    return {url: size for url, size in displays.items() if size is not None}


def _pixels(size: ImageSize) -> int:
    return size.pixels


def _declared_size(img: Element) -> ImageSize | None:
    """Read the width and height attributes, unless the image is responsive."""
    responsive = img.has("srcset") or (img.parent is not None and img.parent.tag == "picture")
    width, height = (_positive_integer(img.get(name)) for name in ("width", "height"))

    if responsive or width is None or height is None:
        return None

    return ImageSize(width, height)


def _positive_integer(value: str | None) -> int | None:
    value = (value or "").strip()

    return int(value) if value.isdigit() and int(value) > 0 else None


def _media_type(download: Download) -> str:
    """Return the media type without its parameters: "text/css; charset=utf-8" → "text/css"."""
    return download.headers.get("content-type", "").partition(";")[0].strip().lower()


def _is_static(download: Download) -> bool:
    """Tell whether a download is a file received as is, not an HTML page."""
    return download.ok and _media_type(download) != "text/html"


def _host(download: Download) -> str | None:
    return urlsplit(download.url).hostname
