"""Rules about third-party tools: analytics, social buttons and carousels (RWEB).

The tools are recognised by the signatures of checks/signatures.py.
"""

from __future__ import annotations

from collections.abc import Iterator

from a11y_eco.checks.base import Violation, rule
from a11y_eco.checks.signatures import (
    ANALYTICS,
    CAROUSELS,
    SOCIAL_BUTTONS,
    find_elements,
    find_tools,
)
from a11y_eco.dom import Document, Element
from a11y_eco.models import Severity

MAX_ANALYTICS = 1  # RWEB_0111
MAX_CAROUSELS = 1  # RWEB_0010


@rule("ECO-ANALYTICS", severity=Severity.WARNING, reference="RWEB_0111")
def too_many_analytics(document: Document) -> Iterator[Violation]:
    """A page should use one analytics tool at most."""
    tools = find_tools(document, ANALYTICS)

    if len(tools) > MAX_ANALYTICS:
        # Every tool is reported: the snippets show which ones the page uses.
        details = {"count": len(tools), "limit": MAX_ANALYTICS}
        for element in tools:
            yield Violation(element, details)


@rule("ECO-SOCIAL-BUTTONS", severity=Severity.WARNING, reference="RWEB_0059")
def official_social_buttons(document: Document) -> Iterator[Element]:
    """Official social scripts are heavy and track visitors; plain links are enough."""
    yield from find_tools(document, SOCIAL_BUTTONS)


@rule("ECO-CAROUSEL", severity=Severity.INFO, reference="RWEB_0010")
def too_many_carousels(document: Document) -> Iterator[Violation]:
    """A page should have one carousel at most."""
    carousels = find_elements(document, CAROUSELS)

    if len(carousels) > MAX_CAROUSELS:
        details = {"count": len(carousels), "limit": MAX_CAROUSELS}
        for element in carousels[MAX_CAROUSELS:]:
            yield Violation(element, details)
