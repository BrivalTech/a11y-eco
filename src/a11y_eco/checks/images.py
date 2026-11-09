"""Rules about text alternatives of images (RGAA criterion 1.1)."""

from __future__ import annotations

from collections.abc import Callable, Iterator

from a11y_eco.checks.aria import has_role, has_text, is_hidden
from a11y_eco.checks.base import rule
from a11y_eco.dom import Document, Element
from a11y_eco.models import Severity

_LABEL_ATTRIBUTES = ("aria-label", "aria-labelledby", "title")


def _has_label(element: Element) -> bool:
    return any(has_text(element, attribute) for attribute in _LABEL_ATTRIBUTES)


def _img_has_alternative(img: Element) -> bool:
    return (
        img.has("alt") or _has_label(img) or is_hidden(img) or has_role(img, "presentation", "none")
    )


def _area_has_alternative(area: Element) -> bool:
    return not area.has("href") or has_text(area, "alt") or _has_label(area)


def _input_has_alternative(field: Element) -> bool:
    is_image_button = (field.get("type") or "").strip().lower() == "image"

    return not is_image_button or has_text(field, "alt") or _has_label(field)


_ALTERNATIVE_CHECKS: dict[str, Callable[[Element], bool]] = {
    "img": _img_has_alternative,
    "area": _area_has_alternative,
    "input": _input_has_alternative,
}


@rule("A11Y-IMG-ALT", severity=Severity.ERROR, reference="RGAA 1.1")
def image_without_alternative(document: Document) -> Iterator[Element]:
    """Every image must have a text alternative, empty when the image is decorative."""
    for element in document.find_all(*_ALTERNATIVE_CHECKS):
        if not _ALTERNATIVE_CHECKS[element.tag](element):
            yield element
