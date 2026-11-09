"""Accessibility semantics shared by several rules.

These helpers only read the HTML: anything decided by CSS or JavaScript
(``display: none``, a role added by a script…) cannot be seen.
"""

from __future__ import annotations

from a11y_eco.dom import Element


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


def is_hidden(element: Element) -> bool:
    """Tell whether the element is removed from what assistive technologies expose.

    This is the case when the element or one of its ancestors has the ``hidden``
    attribute or ``aria-hidden="true"``.

    Args:
        element: The element to inspect.

    Returns:
        True if the element is hidden from assistive technologies.
    """
    node: Element | None = element
    while node is not None:
        if node.has("hidden") or (node.get("aria-hidden") or "").strip().lower() == "true":
            return True
        node = node.parent
    return False
