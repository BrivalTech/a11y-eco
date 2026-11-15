"""Rules about animations and vector images (RWEB)."""

from __future__ import annotations

import re
from collections.abc import Iterator

from a11y_eco.checks.base import Violation, rule
from a11y_eco.checks.signatures import ANIMATIONS, find_elements
from a11y_eco.dom import Document, Element
from a11y_eco.models import Severity

MAX_ANIMATIONS = 2
_INLINE_ANIMATION = re.compile(r"(^|;)\s*animation(-name)?\s*:\s*(?!none\b)[^;\s]", re.IGNORECASE)
EDITOR_PREFIXES = ("inkscape:", "sodipodi:", "sketch:", "xmlns:inkscape", "xmlns:sodipodi")
METADATA_TAGS = frozenset({"metadata"})


def _animated_elements(document: Document) -> list[Element]:
    """Elements that are certainly animated, in document order.

    Animations defined in stylesheets (@keyframes) are not counted: without the
    layout, the tool cannot know which elements they apply to.
    """
    known = set(find_elements(document, ANIMATIONS))

    return [
        element
        for element in document.root.iter()
        if element in known or _INLINE_ANIMATION.search(element.get("style") or "")
    ]


@rule("ECO-ANIMATIONS", severity=Severity.WARNING, reference="RWEB_0009")
def too_many_animations(document: Document) -> Iterator[Violation]:
    """A page should not have more than 2 animations."""
    animated = _animated_elements(document)

    if len(animated) > MAX_ANIMATIONS:
        details = {"count": len(animated), "limit": MAX_ANIMATIONS}
        for element in animated:
            yield Violation(element, details)


def _has_editor_data(svg: Element) -> bool:
    """Tell whether an SVG still holds data that only its drawing tool needed."""
    for element in (svg, *svg.iter()):
        names = (element.tag, *element.attrs)
        if element.tag in METADATA_TAGS or any(name.startswith(EDITOR_PREFIXES) for name in names):
            return True

    return False


@rule("ECO-SVG-METADATA", severity=Severity.WARNING, reference="RWEB_0100")
def unoptimised_svg(document: Document) -> Iterator[Element]:
    """Inline SVG should be cleaned of the metadata left by drawing tools."""
    for svg in document.find_all("svg"):
        # An SVG inside another one is checked with the outermost one.
        inside_svg = any(ancestor.tag == "svg" for ancestor in svg.ancestors())
        if not inside_svg and _has_editor_data(svg):
            yield svg
