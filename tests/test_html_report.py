import pytest

from a11y_eco.audit import audit
from a11y_eco.dom import Document, parse_html
from a11y_eco.i18n import CATALOGS, Catalog, Language
from a11y_eco.loader import Source
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
from a11y_eco.reporters.html_report import render

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
FULL_REPORT = Report(
    location="https://www.example.com/",
    page_size=2048,
    findings=FINDINGS,
    metrics=Metrics(requests=3, resources_by_type={ResourceType.IMAGE: 2}, dom_elements=40),
    network=NetworkMetrics(downloads=(Download("https://www.example.com/", status=200),)),
)


def page(report: Report, catalog: Catalog = EN) -> Document:
    return parse_html(render(report, catalog))


@pytest.mark.parametrize("catalog", CATALOGS.values(), ids=lambda c: c.language)
@pytest.mark.parametrize(
    "report",
    [
        pytest.param(FULL_REPORT, id="with-findings"),
        pytest.param(Report(location="page.html", page_size=0, findings=()), id="clean"),
    ],
)
def test_the_report_passes_its_own_audit(report: Report, catalog: Catalog) -> None:
    html = render(report, catalog)
    source = Source("report.html", html, size=len(html.encode()), encoding="utf-8")

    assert audit(source).findings == ()


def test_page_is_written_in_the_language_of_the_report() -> None:
    document = page(FULL_REPORT, FR)

    assert document.html is not None
    assert document.html.get("lang") == "fr"
    assert [h2.text_content() for h2 in document.find_all("h2")] == [
        FR.text("metrics.title"),
        FR.text("network.title"),
        FR.text("html.findings"),
    ]


def test_every_finding_writes_its_severity_in_full() -> None:
    html = render(FULL_REPORT, FR)
    headings = [h3.text_content() for h3 in parse_html(html).find_all("h3")]

    assert headings[0].startswith("erreur : ")  # text_content() collapses the spaces
    assert headings[1].startswith("avertissement : ")
    assert "52" in headings[1]  # values are filled in, as in the console
    assert '<span class="severity">erreur</span>\N{NO-BREAK SPACE}: ' in html


def test_findings_show_their_rule_reference_and_position() -> None:
    meta = [p.text_content() for p in page(FULL_REPORT).find_all("p") if p.get("class") == "meta"]

    assert meta == ["A11Y-IMG-ALT · RGAA 1.1 · line 12, column 5", "ECO-REQUESTS · RWEB_0047"]


def test_clean_report_says_a_manual_audit_is_still_needed() -> None:
    document = page(Report(location="page.html", page_size=0, findings=()))

    assert EN.text("report.clean") in [p.text_content() for p in document.find_all("p")]
    assert document.find_all("ul") == []


def test_content_of_the_audited_page_is_escaped() -> None:
    hostile = Finding(
        rule_id="A11Y-LINK-NAME",
        severity=Severity.ERROR,
        snippet='<script>alert("pwned")</script>',
    )
    report = Report(location='"><img src=x onerror=alert(1)>', page_size=1, findings=(hostile,))
    html = render(report, EN)
    document = parse_html(html)

    assert document.find_all("script", "img") == []
    assert "&lt;script&gt;" in html

    [code] = document.find_all("code")

    assert code.text_content() == '<script>alert("pwned")</script>'  # shown as text
