"""Run the rules on a page and gather the results."""

from __future__ import annotations

from collections.abc import Callable, Iterable

from a11y_eco.checks import NETWORK_RULES, RULES, NetworkRule, Rule
from a11y_eco.dom import Document, parse_html
from a11y_eco.loader import Source, is_url
from a11y_eco.metrics import measure
from a11y_eco.models import NetworkMetrics, Report

Fetcher = Callable[[Document], NetworkMetrics]


def audit(
    source: Source,
    rules: Iterable[Rule] = RULES,
    *,
    fetch: Fetcher | None = None,
    network_rules: Iterable[NetworkRule] = NETWORK_RULES,
) -> Report:
    """Audit a loaded page.

    Args:
        source: The page to audit.
        rules: The rules to run on the HTML. Defaults to every rule.
        fetch: Takes network measures of the page; None to stay offline.
        network_rules: The rules to run on the downloads, when ``fetch`` is given.

    Returns:
        The audit report.
    """
    url = source.location if is_url(source.location) else None
    document = parse_html(source.text, url=url)
    findings = [finding for rule in rules for finding in rule.run(document)]
    network = fetch(document) if fetch else None

    if network is not None:
        findings += [finding for rule in network_rules for finding in rule.run(network)]

    return Report(
        location=source.location,
        page_size=source.size,
        findings=tuple(findings),
        metrics=measure(document),
        network=network,
    )
