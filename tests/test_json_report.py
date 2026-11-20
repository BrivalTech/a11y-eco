import json
from typing import Any

import pytest

from a11y_eco import __version__
from a11y_eco.i18n import CATALOGS, Catalog, Language
from a11y_eco.models import (
    Download,
    Finding,
    Location,
    Metrics,
    NetworkMetrics,
    Report,
    ResourceType,
    Severity,
)
from a11y_eco.reporters.json_report import SCHEMA_VERSION, render

EN = CATALOGS[Language.EN]
FR = CATALOGS[Language.FR]
FINDINGS = (
    Finding(
        rule_id="A11Y-IMG-ALT",
        severity=Severity.ERROR,
        location=Location(12, 5),
        snippet='<img src="logo.png">',
        reference="RGAA 1.1",
    ),
    Finding(
        rule_id="ECO-REQUESTS",
        severity=Severity.WARNING,
        reference="RWEB_0047",
        details={"count": 52, "limit": 40},
    ),
)


def parse(report: Report, catalog: Catalog = EN) -> dict[str, Any]:
    document: dict[str, Any] = json.loads(render(report, catalog))

    return document


@pytest.fixture
def report() -> Report:
    return Report(
        location="https://www.example.com/",
        page_size=2048,
        findings=FINDINGS,
        metrics=Metrics(requests=3, resources_by_type={ResourceType.IMAGE: 2}, dom_elements=40),
    )


def test_document_starts_with_what_programs_need_to_trust_it(report: Report) -> None:
    document = parse(report)

    assert document["schema_version"] == SCHEMA_VERSION
    assert document["tool"] == {"name": "a11y-eco", "version": __version__}
    assert document["language"] == "en"
    assert document["page"] == {"location": "https://www.example.com/", "size": 2048}


def test_summary_counts_every_severity(report: Report) -> None:
    assert parse(report)["summary"] == {"error": 1, "warning": 1, "info": 0}


def test_findings_keep_ids_for_programs_and_messages_for_people(report: Report) -> None:
    image, requests = parse(report, FR)["findings"]

    assert image == {
        "rule_id": "A11Y-IMG-ALT",
        "severity": "error",
        "reference": "RGAA 1.1",
        "message": FR.rule_title("A11Y-IMG-ALT"),
        "line": 12,
        "column": 5,
        "snippet": '<img src="logo.png">',
        "details": {},
    }
    assert (requests["line"], requests["column"]) == (None, None)
    assert requests["details"] == {"count": 52, "limit": 40}  # numbers, never translated


def test_metrics_list_every_resource_type(report: Report) -> None:
    metrics = parse(report)["metrics"]

    assert list(metrics["resources_by_type"]) == [kind.value for kind in ResourceType]
    assert metrics["resources_by_type"]["image"] == 2
    assert metrics["resources_by_type"]["font"] == 0
    assert (metrics["requests"], metrics["dom_elements"]) == (3, 40)


def test_missing_measures_are_null() -> None:
    document = parse(Report(location="page.html", page_size=10, findings=()))

    assert (document["metrics"], document["network"], document["findings"]) == (None, None, [])


def test_network_downloads_never_include_headers() -> None:
    page = Download(
        "https://www.example.com/",
        status=200,
        transferred=900,
        headers={"set-cookie": "session=secret"},
    )
    network = NetworkMetrics(downloads=(page, Download("https://www.example.com/a.css")))
    report = Report(location=page.url, page_size=900, findings=(), network=network)
    output = render(report, EN)

    assert "secret" not in output
    assert json.loads(output)["network"] == {
        "requests": 2,
        "failed": 1,
        "transferred": 900,
        "complete": True,
        "skipped": 0,
        "downloads": [
            {
                "url": "https://www.example.com/",
                "status": 200,
                "transferred": 900,
                "complete": True,
                "redirected": False,
                "image_size": None,
            },
            {
                "url": "https://www.example.com/a.css",
                "status": None,
                "transferred": 0,
                "complete": True,
                "redirected": False,
                "image_size": None,
            },
        ],
    }


def test_text_stays_readable_and_the_document_ends_with_a_newline(report: Report) -> None:
    output = render(report, FR)

    assert "\\u00" not in output  # accents are written as they are, not escaped
    assert output.endswith("}\n")
