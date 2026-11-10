"""Load an HTML page from a local file or from a URL.

The loader returns the page as text, together with the raw size in bytes and the
encoding used to decode it. Every failure is reported as a ``LoadError``, so that
the command-line interface can show a clear message instead of a traceback.
"""

from __future__ import annotations

import codecs
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from a11y_eco import __version__
from a11y_eco.i18n import CATALOGS, Language

MAX_BYTES = 10 * 1024 * 1024
HTML_CONTENT_TYPES = frozenset({"text/html", "application/xhtml+xml"})
_BROWSER_ENCODINGS = {"ascii": "cp1252", "iso8859-1": "cp1252"}
_META_CHARSET = re.compile(rb"""<meta[^>]*?charset\s*=\s*["']?\s*([\w.:-]+)""", re.IGNORECASE)
_META_PRESCAN_BYTES = 1024


class LoadError(Exception):
    """The page could not be loaded.

    The error carries the key of its message and the values of its placeholders,
    so that the command-line interface can show it in the user's language.
    ``str(error)`` gives the English message, for logs and debugging.
    """

    def __init__(self, key: str, **params: object) -> None:
        """Create the error from a message key and the values of its placeholders."""
        self.key = key
        self.params = params
        super().__init__(CATALOGS[Language.EN].text(key, **params))


@dataclass(frozen=True, slots=True)
class Source:
    """An HTML page ready to be parsed."""

    location: str
    """Path of the file, or final URL after redirects."""

    text: str
    """The decoded HTML."""

    size: int
    """Size of the HTML in bytes, as read from the disk or the network."""

    encoding: str
    """Name of the Python codec used to decode the page."""


def load(target: str, *, timeout: float = 10.0, max_bytes: int = MAX_BYTES) -> Source:
    """Load a page from a URL (``http`` or ``https``) or from a local file.

    Args:
        target: A URL or a file path.
        timeout: Network timeout in seconds, for URLs only.
        max_bytes: Maximum accepted size of the page.

    Returns:
        The loaded page.

    Raises:
        LoadError: If the page cannot be read, is not HTML or is too large.
    """
    if urlsplit(target).scheme in {"http", "https"}:
        return _load_url(target, timeout=timeout, max_bytes=max_bytes)
    return _load_file(Path(target), max_bytes=max_bytes)


def detect_encoding(data: bytes, declared: str | None = None) -> str:
    """Find the encoding of an HTML page, in the order browsers use.

    1. A byte order mark at the start of the data.
    2. The charset declared by the server (``Content-Type`` header).
    3. A ``<meta>`` charset in the first 1024 bytes.
    4. UTF-8 by default.

    Unknown encoding names are ignored.

    Args:
        data: The raw page.
        declared: The charset sent by the server, if any.

    Returns:
        The name of a Python codec.
    """
    if data.startswith(codecs.BOM_UTF8):
        return "utf-8-sig"
    if data.startswith((codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)):
        return "utf-16"
    match = _META_CHARSET.search(data[:_META_PRESCAN_BYTES])
    meta = match.group(1).decode("ascii") if match else None
    for label in (declared, meta):
        if label and (encoding := _codec_name(label)):
            return encoding
    return "utf-8"


def _codec_name(label: str) -> str | None:
    """Return the Python codec for an encoding label, or None if it is unknown."""
    try:
        name = codecs.lookup(label.strip()).name
    except LookupError:
        return None
    return _BROWSER_ENCODINGS.get(name, name)


def _decode(location: str, data: bytes, max_bytes: int, declared: str | None = None) -> Source:
    """Check the size of the raw page, then decode it."""
    if len(data) > max_bytes:
        raise LoadError("load.too_large", location=location, limit=max_bytes)
    encoding = detect_encoding(data, declared)
    text = data.decode(encoding, errors="replace")
    return Source(location=location, text=text, size=len(data), encoding=encoding)


def _load_file(path: Path, *, max_bytes: int) -> Source:
    try:
        with path.open("rb") as file:
            data = file.read(max_bytes + 1)
    except OSError as error:
        raise LoadError("load.unreadable", path=path, reason=error.strerror) from error
    return _decode(str(path), data, max_bytes)


def _load_url(url: str, *, timeout: float, max_bytes: int) -> Source:
    request = Request(url, headers={"User-Agent": f"a11y-eco/{__version__}"})
    try:
        with urlopen(request, timeout=timeout) as response:
            content_type = response.headers.get_content_type()
            if content_type not in HTML_CONTENT_TYPES:
                raise LoadError("load.not_html", url=url, content_type=content_type)
            data = response.read(max_bytes + 1)
            final_url = response.url
            declared = response.headers.get_content_charset()
    except HTTPError as error:  # must come before URLError, its parent class
        raise LoadError("load.http_status", url=url, status=error.code) from error
    except URLError as error:
        raise LoadError("load.unreachable", url=url, reason=error.reason) from error
    except TimeoutError as error:
        raise LoadError("load.timeout", url=url, timeout=timeout) from error
    return _decode(final_url, data, max_bytes, declared)
