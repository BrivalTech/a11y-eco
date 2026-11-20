import json
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from a11y_eco.i18n import CATALOGS, Language
from a11y_eco.models import (
    Download,
    Finding,
    ImageSize,
    Location,
    Metrics,
    NetworkMetrics,
    Report,
    ResourceType,
    Severity,
)
from a11y_eco.reporters.json_report import SCHEMA_VERSION, render

SCHEMA_FILE = Path(__file__).parent.parent / "schema" / f"report-v{SCHEMA_VERSION}.schema.json"
SCHEMA = json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))
VALIDATOR = Draft202012Validator(SCHEMA)
FULL_REPORT = Report(
    location="https://www.example.com/",
    page_size=2048,
    findings=(
        Finding("A11Y-IMG-ALT", Severity.ERROR, Location(12, 5), '<img src="a.png">', "RGAA 1.1"),
        Finding(
            "ECO-REQUESTS",
            Severity.WARNING,
            reference="RWEB_0047",
            details={"count": 52, "limit": 40},
        ),
    ),
    metrics=Metrics(requests=3, resources_by_type={ResourceType.IMAGE: 2}),
    network=NetworkMetrics(
        downloads=(
            Download("https://www.example.com/", status=200, transferred=2048),
            Download("https://www.example.com/a.png", status=200, image_size=ImageSize(350, 300)),
            Download("https://www.example.com/a.css"),
        ),
        skipped=1,
    ),
)


def test_the_schema_itself_is_valid() -> None:
    Draft202012Validator.check_schema(SCHEMA)


@pytest.mark.parametrize("language", list(Language))
@pytest.mark.parametrize(
    "report",
    [
        pytest.param(FULL_REPORT, id="full"),
        pytest.param(Report(location="page.html", page_size=0, findings=()), id="empty"),
    ],
)
def test_every_report_follows_the_schema(report: Report, language: Language) -> None:
    document = json.loads(render(report, CATALOGS[language]))

    assert list(VALIDATOR.iter_errors(document)) == []


def mutated(change: str) -> dict[str, Any]:
    document: dict[str, Any] = json.loads(render(FULL_REPORT, CATALOGS[Language.EN]))

    match change:
        case "unknown-key":
            document["surprise"] = True
        case "missing-key":
            del document["findings"][0]["message"]
        case "wrong-severity":
            document["findings"][0]["severity"] = "fatal"
        case "translated-detail":
            document["findings"][1]["details"]["count"] = "52"

    return document


@pytest.mark.parametrize(
    "change", ["unknown-key", "missing-key", "wrong-severity", "translated-detail"]
)
def test_the_schema_rejects_what_breaks_the_contract(change: str) -> None:
    assert not VALIDATOR.is_valid(mutated(change))
