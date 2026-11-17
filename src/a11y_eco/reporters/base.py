"""What every reporter has in common."""

from __future__ import annotations

from typing import Protocol

from a11y_eco.i18n import Catalog
from a11y_eco.models import Finding, Report


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
