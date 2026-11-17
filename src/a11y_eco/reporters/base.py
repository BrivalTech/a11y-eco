"""What every reporter has in common."""

from __future__ import annotations

from typing import Protocol

from a11y_eco.i18n import Catalog
from a11y_eco.models import Finding, Metrics, NetworkMetrics, Report, ResourceType, Severity


class Reporter(Protocol):
    """Turns a report into text, in the language of a catalog."""

    def __call__(self, report: Report, catalog: Catalog, *, color: bool = False) -> str:
        """Render the report.

        Args:
            report: The audit report.
            catalog: The messages of the chosen language.
            color: Whether the text goes to a terminal that shows colours. Formats
                without colours ignore it.

        Returns:
            The whole report, ready to be written.
        """
        ...


def finding_message(finding: Finding, catalog: Catalog) -> str:
    """Describe a finding, with its values written in the language of the catalog.

    Args:
        finding: The finding.
        catalog: The messages of the chosen language.

    Returns:
        The title of the rule, with numbers such as counts and limits filled in.
    """
    values = {name: catalog.number(value) for name, value in finding.details.items()}

    return catalog.rule_title(finding.rule_id, **values)


def summary(report: Report, catalog: Catalog) -> str:
    """Count the findings of each severity, the most severe first, in one sentence."""
    counts = ", ".join(
        catalog.count(f"count.{severity}", report.count(severity))
        for severity in reversed(Severity)
    )

    return catalog.text("report.summary", counts=counts)


def metrics_measures(metrics: Metrics, catalog: Catalog) -> list[str]:
    """Describe the measures read from the HTML, one sentence each."""
    number = catalog.number
    resources = ", ".join(
        catalog.count(f"resource.{kind}", metrics.resources_by_type[kind])
        for kind in ResourceType
        if metrics.resources_by_type.get(kind)
    ) or catalog.text("metrics.none")

    return [
        catalog.text("metrics.requests", count=number(metrics.requests)),
        catalog.text("metrics.resources", list=resources),
        catalog.text("metrics.deferred", count=number(metrics.deferred)),
        catalog.text("metrics.external", count=number(metrics.external)),
        catalog.text("metrics.domains", count=number(metrics.domains)),
        catalog.text("metrics.dom", count=number(metrics.dom_elements)),
    ]


def network_measures(network: NetworkMetrics, catalog: Catalog) -> list[str]:
    """Describe the measures taken on the network, one sentence each."""
    number = catalog.number
    transferred = "network.transferred" if network.complete else "network.transferred_minimum"
    measures = [
        catalog.text("network.requests", count=number(network.requests)),
        catalog.text("network.failed", count=number(network.failed)),
        catalog.text(transferred, size=number(network.transferred)),
    ]
    if network.skipped:
        measures.append(catalog.text("network.skipped", count=number(network.skipped)))

    return measures
