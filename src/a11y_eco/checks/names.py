"""Rules about the accessible names of elements."""

from __future__ import annotations

from collections.abc import Iterator

from a11y_eco.checks.base import rule
from a11y_eco.dom import Document, Element
from a11y_eco.models import Severity


@rule("A11Y-ARIA-LABELLEDBY", severity=Severity.ERROR, reference="RGAA 8.2")
def broken_labelledby_reference(document: Document) -> Iterator[Element]:
    """Every id listed in ``aria-labelledby`` must exist in the page."""
    for element in document.root.iter():
        ids = (element.get("aria-labelledby") or "").split()
        if any(document.get_element_by_id(element_id) is None for element_id in ids):
            yield element
