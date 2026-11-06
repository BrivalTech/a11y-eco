"""Rules about the default language of the page (RGAA criteria 8.3 and 8.4)."""

from __future__ import annotations

import re
from collections.abc import Iterator

from a11y_eco.checks.base import rule
from a11y_eco.dom import Document, Element
from a11y_eco.models import Severity

_LANGUAGE_TAG = re.compile(r"[a-zA-Z]{2,3}(-[a-zA-Z0-9]{1,8})*")


def _declared_language(document: Document) -> tuple[Element, str]:
    """Return the ``html`` element and its declared language, possibly empty.

    RGAA accepts ``lang`` or ``xml:lang``. Without an ``html`` element, the document
    root stands for the whole page: it has no location and no start tag.
    """
    html = document.html
    if html is None:
        return document.root, ""
    language = html.get("lang") or html.get("xml:lang") or ""
    return html, language.strip()


@rule("A11Y-LANG-MISSING", severity=Severity.ERROR, reference="RGAA 8.3")
def html_lang_missing(document: Document) -> Iterator[Element]:
    """The default language of the page must be declared on the ``html`` element."""
    element, language = _declared_language(document)
    if not language:
        yield element


@rule("A11Y-LANG-INVALID", severity=Severity.ERROR, reference="RGAA 8.4")
def html_lang_invalid(document: Document) -> Iterator[Element]:
    """The declared default language must be a well-formed language code."""
    element, language = _declared_language(document)
    if language and not _LANGUAGE_TAG.fullmatch(language):
        yield element
