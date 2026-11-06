"""Data model shared by checks and reporters."""

from __future__ import annotations

from dataclasses import dataclass
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
