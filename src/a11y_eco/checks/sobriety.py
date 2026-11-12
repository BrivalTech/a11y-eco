"""Rules about the number of requests, files and hosts of a page (RWEB).

The counts come from the HTML only: they are minimum values. A rule reports a
problem only when this minimum already exceeds the limit of the RWEB practice,
so that it never reports a page that respects it.
"""

from __future__ import annotations

from collections.abc import Iterator

from a11y_eco.checks.base import Violation, rule
from a11y_eco.dom import Document, Element, Text
from a11y_eco.metrics import measure
from a11y_eco.models import ResourceType, Severity
from a11y_eco.resources import find_resources

MAX_REQUESTS = 40  # RWEB_0047
MAX_STYLESHEETS = 10  # RWEB_0035
MAX_DOMAINS = 5  # RWEB_0082
MAX_LARGE_INLINE_BLOCKS = 2  # RWEB_0042
LARGE_INLINE_BLOCK = 1024
_SCRIPT_TYPES = frozenset({"", "module", "text/javascript", "application/javascript"})


@rule("ECO-REQUESTS", severity=Severity.WARNING, reference="RWEB_0047")
def too_many_requests(document: Document) -> Iterator[Violation]:
    """The page should not make more than 40 requests when it loads."""
    requests = measure(document).requests
    if requests > MAX_REQUESTS:
        yield Violation(document.root, {"count": requests, "limit": MAX_REQUESTS})


@rule("ECO-STYLESHEETS", severity=Severity.WARNING, reference="RWEB_0035")
def too_many_stylesheets(document: Document) -> Iterator[Violation]:
    """The page should not load more than 10 stylesheets."""
    stylesheets = sum(
        1
        for resource in find_resources(document)
        if resource.type is ResourceType.STYLESHEET and not resource.deferred
    )
    if stylesheets > MAX_STYLESHEETS:
        yield Violation(document.root, {"count": stylesheets, "limit": MAX_STYLESHEETS})


@rule("ECO-DOMAINS", severity=Severity.WARNING, reference="RWEB_0082")
def too_many_domains(document: Document) -> Iterator[Violation]:
    """The page and its resources should not come from more than 5 domains."""
    domains = measure(document).domains
    if domains > MAX_DOMAINS:
        yield Violation(document.root, {"count": domains, "limit": MAX_DOMAINS})


@rule("ECO-INLINE-CODE", severity=Severity.INFO, reference="RWEB_0042")
def too_much_inline_code(document: Document) -> Iterator[Violation]:
    """CSS and JavaScript should be in external files, which browsers can cache."""
    large_blocks = [
        element for element in _inline_code(document) if _size(element) >= LARGE_INLINE_BLOCK
    ]
    if len(large_blocks) > MAX_LARGE_INLINE_BLOCKS:
        details = {"count": len(large_blocks), "limit": MAX_LARGE_INLINE_BLOCKS}
        yield Violation(document.root, details)


def _inline_code(document: Document) -> Iterator[Element]:
    """Yield the <style> elements, and the <script> elements whose code is in the page."""
    for element in document.find_all("style", "script"):
        if element.tag == "style":
            yield element
        elif not element.has("src"):
            script_type = (element.get("type") or "").strip().lower()
            if script_type in _SCRIPT_TYPES:
                yield element


def _size(element: Element) -> int:
    """Size in bytes of the code of an element, as sent in the HTML."""
    code = "".join(child.data for child in element.children if isinstance(child, Text))

    return len(code.encode())
