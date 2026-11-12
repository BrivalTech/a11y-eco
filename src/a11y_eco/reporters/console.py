"""Human-readable report for the terminal.

Colours only reinforce the information, they never carry it alone: the severity is
always written in full, so the output stays readable without colours, by screen
readers, and once copied into a ticket.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import TextIO

from a11y_eco.i18n import Catalog
from a11y_eco.models import Finding, Metrics, Report, ResourceType, Severity

_SEVERITY_COLORS = {Severity.ERROR: "31", Severity.WARNING: "33", Severity.INFO: "36"}
_BOLD = "1"
_DIM = "2"
_SNIPPET_MAX_LENGTH = 80


def should_use_color(stream: TextIO, environ: Mapping[str, str] = os.environ) -> bool:
    """Decide whether to colour the output.

    Colours are used only in an interactive terminal, and never when the
    ``NO_COLOR`` environment variable is set to a non-empty value (https://no-color.org).

    Args:
        stream: Where the report will be written.
        environ: The environment variables.

    Returns:
        True if ANSI colour codes should be used.
    """
    if environ.get("NO_COLOR"):
        return False
    return stream.isatty()


def render(report: Report, catalog: Catalog, *, color: bool = False) -> str:
    """Write a report as text for the terminal.

    Args:
        report: The audit report.
        catalog: The messages of the language to write in.
        color: Whether to add ANSI colour codes.

    Returns:
        The report, ending with a newline.
    """
    size = catalog.number(report.page_size)
    title = catalog.text("report.title", location=report.location, size=size)
    lines = [_style(title, _BOLD, enabled=color), ""]
    if report.metrics is not None:
        lines.extend(_render_metrics(report.metrics, catalog, color=color))
    label_width = max(len(catalog.text(f"severity.{severity}")) for severity in Severity)

    for finding in report.findings:
        lines.extend(_render_finding(finding, report.location, catalog, label_width, color=color))

    if not report.findings:
        lines.append(catalog.text("report.clean"))
        lines.append("")
    counts = ", ".join(
        catalog.count(f"count.{severity}", report.count(severity))
        for severity in reversed(Severity)
    )
    lines.append(catalog.text("report.summary", counts=counts))

    return "\n".join(lines) + "\n"


def _render_metrics(metrics: Metrics, catalog: Catalog, *, color: bool) -> list[str]:
    number = catalog.number
    resources = ", ".join(
        catalog.count(f"resource.{kind}", metrics.resources_by_type[kind])
        for kind in ResourceType
        if metrics.resources_by_type.get(kind)
    ) or catalog.text("metrics.none")
    measures = [
        catalog.text("metrics.requests", count=number(metrics.requests)),
        catalog.text("metrics.resources", list=resources),
        catalog.text("metrics.deferred", count=number(metrics.deferred)),
        catalog.text("metrics.external", count=number(metrics.external)),
        catalog.text("metrics.domains", count=number(metrics.domains)),
        catalog.text("metrics.dom", count=number(metrics.dom_elements)),
    ]
    title = _style(catalog.text("metrics.title"), _BOLD, enabled=color)
    return [title, *(f"  {measure}" for measure in measures), ""]


def _render_finding(
    finding: Finding, page: str, catalog: Catalog, label_width: int, *, color: bool
) -> list[str]:
    label = f"{catalog.text(f'severity.{finding.severity}'):<{label_width}}"
    label = _style(label, _BOLD, _SEVERITY_COLORS[finding.severity], enabled=color)
    indent = " " * (label_width + 2)
    position = f"{page}:{finding.location}" if finding.location else page
    references = ", ".join(part for part in (finding.rule_id, finding.reference) if part)
    lines = [
        f"{label}  {position}",
        f"{indent}{catalog.rule_title(finding.rule_id)} [{references}]",
    ]

    if finding.snippet:
        lines.append(indent + _style(_shorten(finding.snippet), _DIM, enabled=color))
    lines.append("")

    return lines


def _shorten(snippet: str) -> str:
    """Put a snippet on one line and cut it if it is too long."""
    text = " ".join(snippet.split())
    if len(text) <= _SNIPPET_MAX_LENGTH:
        return text
    return text[: _SNIPPET_MAX_LENGTH - 1] + "…"


def _style(text: str, *codes: str, enabled: bool) -> str:
    """Wrap text in ANSI codes, or return it unchanged."""
    if not enabled:
        return text
    return f"\033[{';'.join(codes)}m{text}\033[0m"
