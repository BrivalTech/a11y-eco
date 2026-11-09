"""Accessibility semantics shared by several rules.

These helpers only read the HTML: anything decided by CSS or JavaScript
(``display: none``, a role added by a script…) cannot be seen.
"""

from __future__ import annotations

from a11y_eco.dom import Element

_HEADING_TAGS = {f"h{level}": level for level in range(1, 7)}
_DEFAULT_ARIA_LEVEL = 2


def has_text(element: Element, attribute: str) -> bool:
    """Tell whether an attribute is present and contains more than whitespace.

    Args:
        element: The element to inspect.
        attribute: Lowercase attribute name.

    Returns:
        True if the attribute has a non-blank value.
    """
    return bool((element.get(attribute) or "").strip())


def has_role(element: Element, *roles: str) -> bool:
    """Tell whether the element's role is one of the given roles.

    ``role`` may list several roles, the first one being preferred: only the first
    one is considered here.

    Args:
        element: The element to inspect.
        *roles: Lowercase role names.

    Returns:
        True if the first declared role is one of ``roles``.
    """
    declared = (element.get("role") or "").lower().split()
    return bool(declared) and declared[0] in roles


def hides_itself(element: Element) -> bool:
    """Tell whether the element itself has ``hidden`` or ``aria-hidden="true"``.

    Args:
        element: The element to inspect.

    Returns:
        True if the element carries one of the hiding attributes.
    """
    return element.has("hidden") or (element.get("aria-hidden") or "").strip().lower() == "true"


def is_hidden(element: Element) -> bool:
    """Tell whether the element is removed from what assistive technologies expose.

    This is the case when the element or one of its ancestors hides itself.

    Args:
        element: The element to inspect.

    Returns:
        True if the element is hidden from assistive technologies.
    """
    node: Element | None = element
    while node is not None:
        if hides_itself(node):
            return True
        node = node.parent
    return False


def heading_level(element: Element) -> int | None:
    """Return the level of a heading, or None if the element is not a heading.

    ``h1`` to ``h6`` are headings unless another role is declared, and any element
    with ``role="heading"`` is one, its level coming from ``aria-level``.

    Args:
        element: The element to inspect.

    Returns:
        The heading level, from 1, or None.
    """
    tag_level = _HEADING_TAGS.get(element.tag)
    if has_role(element, "heading"):
        return _aria_level(element) or tag_level or _DEFAULT_ARIA_LEVEL
    if tag_level is not None and not has_text(element, "role"):
        return tag_level
    return None


def _aria_level(element: Element) -> int | None:
    value = (element.get("aria-level") or "").strip()
    # isdecimal() and not isdigit(): "²" is a digit, but int("²") fails.
    if value.isdecimal() and int(value) > 0:
        return int(value)
    return None
