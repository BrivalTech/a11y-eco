"""Rules about what really travels on the network (RWEB), with --fetch-resources.

They read the responses of the servers: compression, cache headers, cookies and
redirections. Cookies set by JavaScript are invisible here, and urllib reports a
chain of redirections as one: the counts are minimum values.
"""

from __future__ import annotations

from collections.abc import Iterator
from urllib.parse import urlsplit

from a11y_eco.checks.base import NetworkViolation, network_rule
from a11y_eco.dom import Document
from a11y_eco.models import Download, NetworkMetrics, Severity

MAX_COOKIE_DOMAINS = 1
MAX_REDIRECTS = 1
MIN_COMPRESSIBLE_BYTES = 1024
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


def _media_type(download: Download) -> str:
    """Return the media type without its parameters: "text/css; charset=utf-8" → "text/css"."""
    return download.headers.get("content-type", "").partition(";")[0].strip().lower()


def _is_static(download: Download) -> bool:
    """Tell whether a download is a file received as is, not an HTML page."""
    return download.ok and _media_type(download) != "text/html"


def _host(download: Download) -> str | None:
    return urlsplit(download.url).hostname
