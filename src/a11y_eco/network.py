"""Download the resources of a page, to measure what really travels on the network.

Only used with --fetch-resources. Files are requested the way browsers request them,
announcing the compressions they accept: the counted bytes are the transferred bytes.
Stylesheets are also read, to download the stylesheets they import. Nothing is
executed.
"""

from __future__ import annotations

import zlib
from collections.abc import Collection, Sequence
from concurrent.futures import ThreadPoolExecutor
from email.message import Message
from functools import partial
from http.client import HTTPException
from urllib.error import HTTPError
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen

from a11y_eco.css import read_css
from a11y_eco.dom import Document
from a11y_eco.imagesize import HEADER_BYTES, image_size
from a11y_eco.loader import USER_AGENT
from a11y_eco.models import Download, NetworkMetrics, ResourceType
from a11y_eco.resources import find_resources, is_external

MAX_DOWNLOADS = 50
PARALLEL_DOWNLOADS = 4
MAX_DOWNLOAD_BYTES = 10 * 1024 * 1024
ACCEPT_ENCODING = "gzip, deflate, br"
READABLE_ENCODING = "gzip, deflate"


def fetch_resources(
    document: Document, *, include_external: bool, timeout: float, limit: int = MAX_DOWNLOADS
) -> NetworkMetrics:
    """Download the page, its resources and the stylesheets they import.

    The downloads go in waves: the page and its resources first, then the stylesheets
    imported by the stylesheets of the previous wave, and so on. An address is never
    downloaded twice, so a loop of imports ends.

    Args:
        document: The parsed page.
        include_external: Whether to include resources served by another host.
        timeout: Network timeout in seconds, for each download.
        limit: Maximum number of measured downloads.

    Returns:
        The downloads, and how many addresses were left out by the limit.
    """
    wave = plan_downloads(document, include_external=include_external)
    stylesheets = {r.url for r in find_resources(document) if r.type is ResourceType.STYLESHEET}
    seen = set(wave)
    downloads: list[Download] = []
    skipped = 0

    while wave:
        room = max(0, limit - len(downloads))
        skipped += len(wave[room:])
        imports = []

        for result, body in _transfer_all(wave[:room], keep=stylesheets, timeout=timeout):
            downloads.append(result)
            if result.url not in stylesheets or not result.ok:
                continue
            for url in _imports(result, body, timeout=timeout):
                if url not in seen and (include_external or _same_host(url, document)):
                    seen.add(url)
                    stylesheets.add(url)
                    imports.append(url)

        wave = imports

    return NetworkMetrics(downloads=tuple(downloads), skipped=skipped)


def plan_downloads(document: Document, *, include_external: bool) -> list[str]:
    """Choose the addresses to download: the page, then its resources.

    Only resources loaded with the page are kept, and only those with an absolute
    address: the relative addresses of a local file cannot be downloaded. Like a
    browser, each address is downloaded once, even if the page uses it twice.

    Args:
        document: The parsed page.
        include_external: Whether to include resources served by another host.

    Returns:
        The addresses, the page first, in document order.
    """
    urls = [document.url] if document.url else []
    for resource in find_resources(document):
        if resource.deferred or urlsplit(resource.url).scheme not in {"http", "https"}:
            continue
        if include_external or not is_external(resource, document):
            urls.append(resource.url)

    return list(dict.fromkeys(urls))  # removes duplicates, keeps the order


def download(url: str, *, timeout: float, max_bytes: int = MAX_DOWNLOAD_BYTES) -> Download:
    """Download one address, without ever raising an exception.

    Args:
        url: The address.
        timeout: Network timeout in seconds.
        max_bytes: The download stops after this many bytes.

    Returns:
        What happened; a failed download has no status.
    """
    return _transfer(url, timeout=timeout, max_bytes=max_bytes)[0]


def download_all(
    urls: Sequence[str], *, timeout: float, workers: int = PARALLEL_DOWNLOADS
) -> list[Download]:
    """Download several addresses, a few at a time.

    Args:
        urls: The addresses.
        timeout: Network timeout in seconds, for each download.
        workers: How many downloads run at the same time.

    Returns:
        One Download per address, in the same order.
    """
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(partial(download, timeout=timeout), urls))


def _transfer(
    url: str,
    *,
    timeout: float,
    max_bytes: int = MAX_DOWNLOAD_BYTES,
    accept_encoding: str = ACCEPT_ENCODING,
) -> tuple[Download, bytes]:
    """Download one address, and also return the body as received, possibly compressed."""
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept-Encoding": accept_encoding})

    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read(max_bytes + 1)
            result = Download(
                url,
                status=response.status,
                transferred=min(len(body), max_bytes),
                complete=len(body) <= max_bytes,
                redirected=response.url != url,
                headers=_lowercase_headers(response.headers),
                image_size=image_size(body[:HEADER_BYTES]),
            )
            return result, body[:max_bytes]
    except HTTPError as error:
        return Download(url, status=error.code, headers=_lowercase_headers(error.headers)), b""
    except (OSError, HTTPException, ValueError):
        return Download(url), b""


def _transfer_all(
    urls: Sequence[str], *, keep: Collection[str], timeout: float
) -> list[tuple[Download, bytes]]:
    """Download several addresses, keeping the body only of those in ``keep``."""

    def transfer(url: str) -> tuple[Download, bytes]:
        result, body = _transfer(url, timeout=timeout)
        return result, body if url in keep else b""  # images and scripts are not kept

    with ThreadPoolExecutor(max_workers=PARALLEL_DOWNLOADS) as pool:
        return list(pool.map(transfer, urls))


def _imports(stylesheet: Download, body: bytes, *, timeout: float) -> list[str]:
    """Return the absolute addresses of the stylesheets that a stylesheet imports."""
    text = _readable(stylesheet, body)

    if text is None:  # Brotli, which the standard library cannot read: ask for gzip
        text = _readable(
            *_transfer(stylesheet.url, timeout=timeout, accept_encoding=READABLE_ENCODING)
        )

    if text is None:
        return []

    urls = (urljoin(stylesheet.url, url) for url in read_css(text).imports)
    return [url for url in urls if urlsplit(url).scheme in {"http", "https"}]


def _readable(response: Download, body: bytes) -> str | None:
    """Decode a stylesheet, or return None when its compression cannot be undone."""
    encoding = response.headers.get("content-encoding", "identity").strip().lower()

    if encoding in {"", "identity"}:
        data = body
    elif encoding in {"gzip", "x-gzip", "deflate"}:
        data = _inflate(body)
    else:
        return None

    return data.decode("utf-8", errors="replace")


def _inflate(data: bytes) -> bytes:
    """Decompress gzip or zlib data, never beyond MAX_DOWNLOAD_BYTES.

    The limit protects against "decompression bombs": a few kilobytes that expand
    into gigabytes. A truncated stream gives what could be read; a damaged one, nothing.
    """
    inflater = zlib.decompressobj(wbits=47)  # 32 + 15: gzip or zlib header, detected

    try:
        return inflater.decompress(data, MAX_DOWNLOAD_BYTES)
    except zlib.error:
        return b""


def _same_host(url: str, document: Document) -> bool:
    page_host = urlsplit(document.url).hostname if document.url else None

    return page_host is not None and urlsplit(url).hostname == page_host


def _lowercase_headers(headers: Message) -> dict[str, str]:
    lowered: dict[str, list[str]] = {}

    for name, value in headers.items():
        lowered.setdefault(name.lower(), []).append(value)

    return {name: "\n".join(values) for name, values in lowered.items()}
