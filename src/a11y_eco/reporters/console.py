"""Human-readable report for the terminal.

Colours only reinforce the information, they never carry it alone: the severity is
always written in full, so the output stays readable without colours, by screen
readers, and once copied into a ticket.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import TextIO

from a11y_eco.messages import count_severity, rule_title
from a11y_eco.models import Finding, Report, Severity

_SEVERITY_COLORS = {Severity.ERROR: "31", Severity.WARNING: "33", Severity.INFO: "36"}
_BOLD = "1"
_DIM = "2"
_LABEL_WIDTH = max(len(severity) for severity in Severity)
_INDENT = " " * (_LABEL_WIDTH + 2)
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


def render(report: Report, *, color: bool = False) -> str:
    """Write a report as text for the terminal.

    Args:
        report: The audit report.
        color: Whether to add ANSI colour codes.

    Returns:
        The report, ending with a newline.
    """
    title = f"Audit of {report.location} ({report.page_size:,} bytes)"
    lines = [_style(title, _BOLD, enabled=color), ""]
    for finding in report.findings:
        lines.extend(_render_finding(finding, report.location, color=color))
    if not report.findings:
        lines.append("No problem found by the automated checks. A manual audit is still needed.")
        lines.append("")
    counts = (count_severity(report.count(severity), severity) for severity in reversed(Severity))
    lines.append("Summary: " + ", ".join(counts))
    return "\n".join(lines) + "\n"


def _render_finding(finding: Finding, page: str, *, color: bool) -> list[str]:
    label = f"{finding.severity:<{_LABEL_WIDTH}}"
    label = _style(label, _BOLD, _SEVERITY_COLORS[finding.severity], enabled=color)
    position = f"{page}:{finding.location}" if finding.location else page
    references = ", ".join(part for part in (finding.rule_id, finding.reference) if part)
    lines = [
        f"{label}  {position}",
        f"{_INDENT}{rule_title(finding.rule_id)} [{references}]",
    ]
    if finding.snippet:
        lines.append(_INDENT + _style(_shorten(finding.snippet), _DIM, enabled=color))
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
