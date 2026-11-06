"""What a rule is, and how to declare one."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass

from a11y_eco.dom import Document, Element
from a11y_eco.models import Finding, Severity

CheckFunction = Callable[[Document], Iterable[Element]]


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
        return [
            Finding(
                rule_id=self.rule_id,
                severity=self.severity,
                location=element.location,
                snippet=element.start_tag,
                reference=self.reference,
            )
            for element in self.check(document)
        ]


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
