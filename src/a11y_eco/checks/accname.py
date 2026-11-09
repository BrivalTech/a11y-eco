"""Accessible name of an element, simplified.

The accessible name is what assistive technologies announce: the text of a link,
the label of a button… It follows the order of the W3C "Accessible Name and
Description Computation" specification, reduced to what static HTML allows:

1. ``aria-labelledby``: the text of the referenced elements; ids that do not exist
   are ignored (they are reported by a rule of their own);
2. ``aria-label``;
3. the native alternative: ``alt`` of images, ``value`` of input buttons;
4. the content: its text, and the names of the images and elements it contains;
5. ``title``.

Not handled: ``<label for>`` associations, CSS (``display: none``, generated
content), names set by scripts, and ``aria-labelledby`` inside the content.
"""

from __future__ import annotations

from a11y_eco.checks.aria import hides_itself
from a11y_eco.dom import HIDDEN_TEXT_ELEMENTS, Document, Element, Text

_INPUT_BUTTON_DEFAULT_NAMES = {"submit": "Submit", "reset": "Reset", "button": ""}


def accessible_name(element: Element, document: Document) -> str:
    """Compute the accessible name of an element.

    Args:
        element: The element to name.
        document: The page, needed to resolve ``aria-labelledby``.

    Returns:
        The name with whitespace collapsed, empty if the element has none.
    """
    # "or" stops at the first non-empty source: later sources are not computed.
    return (
        _from_labelledby(element, document)
        or _clean(element.get("aria-label"))
        or _native_name(element)
        or _from_content(element)
        or _clean(element.get("title"))
    )


def _clean(text: str | None) -> str:
    """Collapse whitespace; None becomes the empty string."""
    return " ".join((text or "").split())


def _from_labelledby(element: Element, document: Document) -> str:
    parts = []
    for element_id in (element.get("aria-labelledby") or "").split():
        referenced = document.get_element_by_id(element_id)
        if referenced is not None:
            # Referenced elements count even when hidden, as in the specification,
            # but their own aria-labelledby is not followed: no loops possible.
            parts.append(
                _clean(referenced.get("aria-label"))
                or _native_name(referenced)
                or _from_content(referenced)
            )
    return _clean(" ".join(parts))


def _native_name(element: Element) -> str:
    if element.tag in {"img", "area"}:
        return _clean(element.get("alt"))
    if element.tag == "input":
        input_type = (element.get("type") or "").strip().lower()
        if input_type == "image":
            return _clean(element.get("alt"))
        if input_type in _INPUT_BUTTON_DEFAULT_NAMES:
            if element.has("value"):
                return _clean(element.get("value"))
            return _INPUT_BUTTON_DEFAULT_NAMES[input_type]
    return ""


def _from_content(element: Element) -> str:
    # Explicit stack instead of recursion: deeply nested content cannot crash.
    parts: list[str] = []
    stack: list[Element | Text] = list(reversed(element.children))
    while stack:
        node = stack.pop()
        if isinstance(node, Text):
            parts.append(node.data)
        elif node.tag in HIDDEN_TEXT_ELEMENTS or hides_itself(node):
            continue
        elif own_name := _clean(node.get("aria-label")) or _native_name(node):
            # An image or a labelled element counts as a word of its own.
            parts.append(f" {own_name} ")
        else:
            stack.extend(reversed(node.children))
    return _clean("".join(parts))
