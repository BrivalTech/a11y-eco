"""JSON report, for continuous integration and other programs.

The keys are a public contract: renaming or removing one is a breaking change that
requires a new SCHEMA_VERSION. Adding a key is not. Values are never translated,
except ``message``, which is meant for people.
"""

from __future__ import annotations

import json
from typing import Any

from a11y_eco import __version__
from a11y_eco.i18n import Catalog
from a11y_eco.models import (
    Download,
    Finding,
    Metrics,
    NetworkMetrics,
    Report,
    ResourceType,
    Severity,
)
from a11y_eco.reporters.base import finding_message

SCHEMA_VERSION = 1


def render(report: Report, catalog: Catalog, *, color: bool = False) -> str:
    """Render a report as an indented JSON document.

    Args:
        report: The audit report.
        catalog: Language of the ``message`` of each finding.
        color: Ignored: JSON has no colours.

    Returns:
        The JSON document, ending with a newline.
    """
    document = {
        "schema_version": SCHEMA_VERSION,
        "tool": {"name": "a11y-eco", "version": __version__},
        "language": catalog.language,
        "page": {"location": report.location, "size": report.page_size},
        "summary": {severity.value: report.count(severity) for severity in reversed(Severity)},
        "metrics": _metrics(report.metrics) if report.metrics else None,
        "network": _network(report.network) if report.network else None,
        "findings": [_finding(finding, catalog) for finding in report.findings],
    }
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


def _finding(finding: Finding, catalog: Catalog) -> dict[str, Any]:
    location = finding.location
    return {
        "rule_id": finding.rule_id,
        "severity": finding.severity.value,
        "reference": finding.reference,
        "message": finding_message(finding, catalog),
        "line": location.line if location else None,
        "column": location.column if location else None,
        "snippet": finding.snippet,
        "details": dict(finding.details),
    }


def _metrics(metrics: Metrics) -> dict[str, Any]:
    return {
        "requests": metrics.requests,
        # Every type, even at zero, so that programs always find the same keys.
        "resources_by_type": {
            kind.value: metrics.resources_by_type.get(kind, 0) for kind in ResourceType
        },
        "deferred": metrics.deferred,
        "external": metrics.external,
        "domains": metrics.domains,
        "dom_elements": metrics.dom_elements,
    }


def _network(network: NetworkMetrics) -> dict[str, Any]:
    return {
        "requests": network.requests,
        "failed": network.failed,
        "transferred": network.transferred,
        "complete": network.complete,
        "skipped": network.skipped,
        "downloads": [_download(download) for download in network.downloads],
    }


def _download(download: Download) -> dict[str, Any]:
    return {
        "url": download.url,
        "status": download.status,
        "transferred": download.transferred,
        "complete": download.complete,
        "redirected": download.redirected,
        "image_size": (
            {"width": download.image_size.width, "height": download.image_size.height}
            if download.image_size
            else None
        ),
    }
