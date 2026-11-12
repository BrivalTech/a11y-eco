"""Data model shared by checks and reporters."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum


class Severity(StrEnum):
    """How serious a finding is, from least to most severe."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

    @property
    def rank(self) -> int:
        """Position of the severity on the scale, 0 being the least severe."""
        return list(Severity).index(self)

    def is_at_least(self, threshold: Severity) -> bool:
        """Tell whether this severity reaches a threshold.

        Args:
            threshold: The minimum severity to compare against.

        Returns:
            True if this severity is equal to or more severe than ``threshold``.
        """
        return self.rank >= threshold.rank


@dataclass(frozen=True, slots=True)
class Location:
    """Position of an element in the HTML source, both values starting at 1."""

    line: int
    column: int

    def __str__(self) -> str:
        """Return a string representation of this location."""
        return f"{self.line}:{self.column}"


@dataclass(frozen=True, slots=True)
class Finding:
    """A problem detected by a check."""

    rule_id: str
    severity: Severity
    location: Location | None = None
    snippet: str = ""
    reference: str = ""


class ResourceType(StrEnum):
    """Kinds of downloaded resources."""

    STYLESHEET = "stylesheet"
    SCRIPT = "script"
    IMAGE = "image"
    FONT = "font"
    MEDIA = "media"
    FRAME = "frame"
    OTHER = "other"


@dataclass(frozen=True, slots=True)
class Metrics:
    """Sobriety measures of a page, read from its HTML only.

    The HTML does not show what stylesheets and scripts download in turn: request
    and resource counts are minimum values.
    """

    requests: int
    """Requests made when the page loads, the HTML itself included."""

    resources_by_type: Mapping[ResourceType, int] = field(default_factory=dict)
    """Resources downloaded when the page loads, by type."""

    deferred: int = 0
    """Resources downloaded only on demand (lazy loading, ``preload="none"``)."""

    external: int = 0
    """Resources downloaded when the page loads from another host than the page."""

    domains: int = 1
    """Hosts that serve the page and the resources it downloads when it loads."""

    dom_elements: int = 0
    """Number of elements in the page."""


@dataclass(frozen=True, slots=True)
class Report:
    """The result of an audit."""

    location: str
    """Path or URL of the audited page."""

    page_size: int
    """Size of the HTML in bytes."""

    findings: tuple[Finding, ...]
    """Every problem found, in rule order then document order."""

    metrics: Metrics | None = None
    """Sobriety measures, or None when they were not computed."""

    def count(self, severity: Severity) -> int:
        """Count the findings of exactly one severity.

        Args:
            severity: The severity to count.

        Returns:
            The number of findings with this severity.
        """
        return sum(1 for finding in self.findings if finding.severity is severity)

    def reaches(self, threshold: Severity) -> bool:
        """Tell whether at least one finding is at or above a severity.

        Args:
            threshold: The minimum severity.

        Returns:
            True if a finding reaches the threshold.
        """
        return any(finding.severity.is_at_least(threshold) for finding in self.findings)
