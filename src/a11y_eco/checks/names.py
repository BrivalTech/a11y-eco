"""Rules about the accessible names of elements (RGAA criteria 6.2, 8.2 and 11.9)."""

from __future__ import annotations

from collections.abc import Callable, Iterator

from a11y_eco.checks.accname import accessible_name
from a11y_eco.checks.aria import has_role, has_text, is_hidden
from a11y_eco.checks.base import rule
from a11y_eco.dom import Document, Element
from a11y_eco.models import Severity

_INPUT_BUTTON_TYPES = frozenset({"submit", "reset", "button"})


def _is_link(element: Element) -> bool:
    if has_role(element, "link"):
        return True

    return element.tag == "a" and element.has("href") and not has_text(element, "role")


def _is_button(element: Element) -> bool:
    if has_role(element, "button"):
        return True

    if has_text(element, "role"):
        return False

    if element.tag == "button":
        return True

    input_type = (element.get("type") or "").strip().lower()

    return element.tag == "input" and input_type in _INPUT_BUTTON_TYPES


def _without_name(document: Document, is_target: Callable[[Element], bool]) -> Iterator[Element]:
    """Yield the visible target elements whose accessible name is empty."""
    for element in document.root.iter():
        if is_target(element) and not is_hidden(element) and not accessible_name(element, document):
            yield element


@rule("A11Y-ARIA-LABELLEDBY", severity=Severity.ERROR, reference="RGAA 8.2")
def broken_labelledby_reference(document: Document) -> Iterator[Element]:
    """Every id listed in ``aria-labelledby`` must exist in the page."""
    for element in document.root.iter():
        ids = (element.get("aria-labelledby") or "").split()
        if any(document.get_element_by_id(element_id) is None for element_id in ids):
            yield element


@rule("A11Y-LINK-NAME", severity=Severity.ERROR, reference="RGAA 6.2")
def link_without_name(document: Document) -> Iterator[Element]:
    """Every link must have an accessible name."""
    yield from _without_name(document, _is_link)


@rule("A11Y-BUTTON-NAME", severity=Severity.ERROR, reference="RGAA 11.9")
def button_without_name(document: Document) -> Iterator[Element]:
    """Every button must have an accessible name."""
    yield from _without_name(document, _is_button)
