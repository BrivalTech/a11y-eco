"""Run the rules on a page and gather the results."""

from __future__ import annotations

from collections.abc import Iterable

from a11y_eco.checks import RULES, Rule
from a11y_eco.dom import parse_html
from a11y_eco.loader import Source, is_url
from a11y_eco.models import Report


def audit(source: Source, rules: Iterable[Rule] = RULES) -> Report:
    """Audit a loaded page.

    Args:
        source: The page to audit.
        rules: The rules to run. Defaults to every rule.

    Returns:
        The audit report.
    """
    url = source.location if is_url(source.location) else None
    document = parse_html(source.text, url=url)
    findings = tuple(finding for rule in rules for finding in rule.run(document))

    return Report(location=source.location, page_size=source.size, findings=findings)
