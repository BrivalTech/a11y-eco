"""Download the resources of a page, to measure what really travels on the network.

Only used with --fetch-resources. Files are requested the way browsers request them,
announcing the compressions they accept, and are never decompressed: the counted
bytes are the transferred bytes. Nothing is executed or interpreted.
"""

from __future__ import annotations

from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from email.message import Message
from functools import partial
from http.client import HTTPException
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from a11y_eco.dom import Document
from a11y_eco.loader import USER_AGENT
from a11y_eco.models import Download, NetworkMetrics
from a11y_eco.resources import find_resources, is_external

MAX_DOWNLOADS = 50
PARALLEL_DOWNLOADS = 4
MAX_DOWNLOAD_BYTES = 10 * 1024 * 1024
ACCEPT_ENCODING = "gzip, deflate, br"


def fetch_resources(
    document: Document, *, include_external: bool, timeout: float, limit: int = MAX_DOWNLOADS
) -> NetworkMetrics:
    """Download the page and its resources, and measure what was transferred.

    Args:
        document: The parsed page.
        include_external: Whether to include resources served by another host.
        timeout: Network timeout in seconds, for each download.
        limit: Maximum number of downloads.

    Returns:
        The downloads, and how many addresses were left out by the limit.
    """
    urls = plan_downloads(document, include_external=include_external)
    downloads = download_all(urls[:limit], timeout=timeout)
    return NetworkMetrics(downloads=tuple(downloads), skipped=max(0, len(urls) - limit))


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
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept-Encoding": ACCEPT_ENCODING})

    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read(max_bytes + 1)
            return Download(
                url,
                status=response.status,
                transferred=min(len(body), max_bytes),
                complete=len(body) <= max_bytes,
                redirected=response.url != url,
                headers=_lowercase_headers(response.headers),
            )
    except HTTPError as error:  # a 404 or a 500 is a response: keep its headers
        return Download(url, status=error.code, headers=_lowercase_headers(error.headers))
    except (OSError, HTTPException, ValueError):
        return Download(url)


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


def _lowercase_headers(headers: Message) -> dict[str, str]:
    lowered: dict[str, list[str]] = {}

    for name, value in headers.items():
        lowered.setdefault(name.lower(), []).append(value)

    return {name: "\n".join(values) for name, values in lowered.items()}
