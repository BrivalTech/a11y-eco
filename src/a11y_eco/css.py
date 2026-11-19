"""Read the parts of CSS that make the browser download files.

This is not a CSS parser: it only finds ``@import`` rules, ``@font-face`` sources
and ``url()`` values, which is all the audit needs. Comments and quoted strings are
recognised, so that ``content: "url(x)"`` or ``/* @import */`` are never mistaken
for references. Nothing is resolved here: addresses are returned as written.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_STRING_OR_COMMENT = re.compile(
    r"""(?P<string>"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')|(?P<comment>/\*.*?(?:\*/|$))""",
    re.DOTALL,
)
_URL_OR_STRING = re.compile(
    r"""url\(\s*(?:"(?P<double>(?:\\.|[^"\\])*)"|'(?P<single>(?:\\.|[^'\\])*)'"""
    r"""|(?P<bare>(?:\\.|[^)\s"'\\])*))\s*\)"""
    r"""|(?P<string>"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')""",
    re.IGNORECASE,
)
_IMPORT = re.compile(
    r"""@import\s+(?:"(?P<double>(?:\\.|[^"\\])*)"|'(?P<single>(?:\\.|[^'\\])*)'"""
    r"""|(?P<url>url\([^)]*\)))[^;]*;?""",
    re.IGNORECASE,
)
_FONT_FACE = re.compile(r"@font-face\s*\{(?P<body>[^}]*)\}?", re.IGNORECASE)
_ESCAPE = re.compile(r"\\(.)")


@dataclass(frozen=True, slots=True)
class CssReferences:
    """The files a piece of CSS may make the browser download, in source order."""

    imports: tuple[str, ...] = ()
    """Stylesheets of ``@import`` rules: always downloaded with the stylesheet."""

    font_faces: tuple[str, ...] = ()
    """First source of each ``@font-face``: downloaded only if a text uses the font."""

    urls: tuple[str, ...] = ()
    """Every other ``url()``, such as background images."""


def read_css(css: str) -> CssReferences:
    """Find the files referenced by a stylesheet or by a ``style`` attribute.

    Args:
        css: The CSS text.

    Returns:
        The referenced addresses, as written, without empty ones.
    """
    text = _without_comments(css)
    imports = [_import_target(match) for match in _IMPORT.finditer(text)]
    text = _IMPORT.sub(" ", text)
    font_faces = []

    for match in _FONT_FACE.finditer(text):
        # A browser downloads one source per font: the first one it supports.
        sources = _urls(match["body"])
        if sources:
            font_faces.append(sources[0])

    text = _FONT_FACE.sub(" ", text)

    return CssReferences(
        imports=tuple(url for url in imports if url),
        font_faces=tuple(font_faces),
        urls=tuple(_urls(text)),
    )


def _without_comments(css: str) -> str:
    return _STRING_OR_COMMENT.sub(lambda m: " " if m["comment"] is not None else m[0], css)


def _urls(css: str) -> list[str]:
    """Return the addresses of the url() values that are not inside a string."""
    found = []

    for match in _URL_OR_STRING.finditer(css):
        if match["string"] is not None:
            continue  # text such as content: "url(x)"
        address = _unescape(match["double"] or match["single"] or match["bare"] or "")
        if address:
            found.append(address)

    return found


def _import_target(match: re.Match[str]) -> str:
    if match["url"] is not None:
        urls = _urls(match["url"])
        return urls[0] if urls else ""

    return _unescape(match["double"] or match["single"] or "")


def _unescape(value: str) -> str:
    r"""Remove CSS escapes of single characters: ``a\)b`` → ``a)b``."""
    return _ESCAPE.sub(r"\1", value.strip())
