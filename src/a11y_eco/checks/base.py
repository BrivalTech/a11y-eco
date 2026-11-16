"""What a rule is, and how to declare one.

Most rules read the HTML (``Rule``, declared with ``@rule``). Network rules read the
downloads made with --fetch-resources (``NetworkRule``, declared with ``@network_rule``):
they only run when those downloads exist.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from typing import NamedTuple

from a11y_eco.dom import Document, Element
from a11y_eco.models import Download, Finding, NetworkMetrics, Severity


class Violation(NamedTuple):
    """An element that breaks a rule, with values that describe the problem."""

    element: Element
    details: Mapping[str, int]


CheckFunction = Callable[[Document], Iterable[Element | Violation]]


@dataclass(frozen=True, slots=True)
class Rule:
    """An audit rule: an identifier, a severity, a reference and a check."""

    rule_id: str
    """Stable identifier, used in reports and in ``--checks``, e.g. ``A11Y-LANG-MISSING``."""

    severity: Severity

    reference: str
    """The standard the rule comes from, e.g. ``RGAA 8.3``."""

    check: CheckFunction

    def run(self, document: Document) -> list[Finding]:
        """Run the check and turn every faulty element into a finding.

        Args:
            document: The parsed page.

        Returns:
            The findings, in document order.
        """
        findings = []
        for result in self.check(document):
            violation = result if isinstance(result, Violation) else Violation(result, {})
            findings.append(
                Finding(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    location=violation.element.location,
                    snippet=violation.element.start_tag,
                    reference=self.reference,
                    details=violation.details,
                )
            )

        return findings


def rule(rule_id: str, *, severity: Severity, reference: str) -> Callable[[CheckFunction], Rule]:
    """Turn a check function into a rule.

    Args:
        rule_id: Stable identifier of the rule.
        severity: Severity of every finding of this rule.
        reference: The standard the rule comes from.

    Returns:
        A decorator that wraps the check function in a ``Rule``.
    """

    def decorate(check: CheckFunction) -> Rule:
        return Rule(rule_id=rule_id, severity=severity, reference=reference, check=check)

    return decorate


class NetworkViolation(NamedTuple):
    """A download that breaks a network rule, with values that describe the problem."""

    download: Download
    details: Mapping[str, int]


NetworkCheckFunction = Callable[[NetworkMetrics], Iterable[Download | NetworkViolation]]


@dataclass(frozen=True, slots=True)
class NetworkRule:
    """An audit rule that reads the downloads instead of the HTML."""

    rule_id: str
    severity: Severity
    reference: str
    check: NetworkCheckFunction

    def run(self, network: NetworkMetrics) -> list[Finding]:
        """Run the check and turn every faulty download into a finding.

        A download has no position in the HTML: its address is the snippet.

        Args:
            network: The downloads of the page.

        Returns:
            The findings, in download order.
        """
        findings = []

        for result in self.check(network):
            violation = (
                result if isinstance(result, NetworkViolation) else NetworkViolation(result, {})
            )
            findings.append(
                Finding(
                    rule_id=self.rule_id,
                    severity=self.severity,
                    snippet=violation.download.url,
                    reference=self.reference,
                    details=violation.details,
                )
            )

        return findings


def network_rule(
    rule_id: str, *, severity: Severity, reference: str
) -> Callable[[NetworkCheckFunction], NetworkRule]:
    """Turn a network check function into a network rule.

    Args:
        rule_id: Stable identifier of the rule.
        severity: Severity of every finding of this rule.
        reference: The standard the rule comes from.

    Returns:
        A decorator that wraps the check function in a ``NetworkRule``.
    """

    def decorate(check: NetworkCheckFunction) -> NetworkRule:
        return NetworkRule(rule_id=rule_id, severity=severity, reference=reference, check=check)

    return decorate
