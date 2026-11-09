"""Rules about the heading structure of the page (RGAA criterion 9.1)."""

from __future__ import annotations

from collections.abc import Iterator

from a11y_eco.checks.aria import heading_level, is_hidden
from a11y_eco.checks.base import rule
from a11y_eco.dom import Document, Element
from a11y_eco.models import Severity


def _headings(document: Document) -> list[tuple[Element, int]]:
    """Return the headings exposed to assistive technologies, with their level."""
    headings = []
    for element in document.root.iter():
        level = heading_level(element)
        if level is not None and not is_hidden(element):
            headings.append((element, level))
    return headings


@rule("A11Y-HEADING-H1-MISSING", severity=Severity.WARNING, reference="RGAA 9.1")
def missing_main_heading(document: Document) -> Iterator[Element]:
    """The page should have a level 1 heading."""
    if not any(level == 1 for _, level in _headings(document)):
        yield document.root


@rule("A11Y-HEADING-H1-MULTIPLE", severity=Severity.INFO, reference="RGAA 9.1")
def several_main_headings(document: Document) -> Iterator[Element]:
    """Several level 1 headings are allowed, but often reveal a structure problem."""
    main_headings = [element for element, level in _headings(document) if level == 1]
    yield from main_headings[1:]


@rule("A11Y-HEADING-SKIP", severity=Severity.ERROR, reference="RGAA 9.1")
def skipped_heading_level(document: Document) -> Iterator[Element]:
    """A heading must not be more than one level below the previous heading."""
    previous: int | None = None
    for element, level in _headings(document):
        if previous is not None and level > previous + 1:
            yield element
        previous = level
