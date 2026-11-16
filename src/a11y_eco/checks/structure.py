"""Rules about the head of the page: title (RGAA 8.5 and RWEB), viewport and description."""

from __future__ import annotations

from collections.abc import Iterator

from a11y_eco.checks.base import rule
from a11y_eco.dom import Document, Element
from a11y_eco.models import Severity


def _meta_content(document: Document, name: str) -> str:
    """Content of the first <meta name="..."> with this name, blank if there is none."""
    for meta in document.find_all("meta"):
        if (meta.get("name") or "").strip().lower() == name:
            return (meta.get("content") or "").strip()

    return ""


def _in_svg(element: Element) -> bool:
    """Tell whether an element is part of an SVG image (an SVG <title> is not the page's)."""
    return any(ancestor.tag == "svg" for ancestor in element.ancestors())


def _untitled(document: Document) -> Iterator[Element]:
    """Yield the empty <title>, or the page root if there is no <title> at all.

    Shared by two rules that detect the same defect for two different reasons.
    """
    titles = [title for title in document.find_all("title") if not _in_svg(title)]

    if not any(title.text_content() for title in titles):
        yield titles[0] if titles else document.root


@rule("ECO-VIEWPORT", severity=Severity.INFO, reference="RWEB_0004")
def missing_viewport(document: Document) -> Iterator[Element]:
    """Without a viewport meta tag, mobile browsers show a shrunk desktop page."""
    if "width" not in _meta_content(document, "viewport").lower():
        yield document.root


@rule("A11Y-PAGE-TITLE", severity=Severity.ERROR, reference="RGAA 8.5")
def missing_page_title(document: Document) -> Iterator[Element]:
    """The title is the first thing a screen reader announces, and names the tab."""
    yield from _untitled(document)


@rule("ECO-TITLE", severity=Severity.WARNING, reference="RWEB_0011")
def missing_title(document: Document) -> Iterator[Element]:
    """A page title lets people and search engines find the right page at once."""
    yield from _untitled(document)


@rule("ECO-META-DESCRIPTION", severity=Severity.WARNING, reference="RWEB_0011")
def missing_description(document: Document) -> Iterator[Element]:
    """A meta description summarises the page in search results, saving visits."""
    if not _meta_content(document, "description"):
        yield document.root
