from a11y_eco.audit import audit
from a11y_eco.checks import language
from a11y_eco.loader import Source
from a11y_eco.models import Finding, Report, Severity


def make_source(html: str) -> Source:
    return Source(location="page.html", text=html, size=len(html.encode()), encoding="utf-8")


def test_audit_runs_the_given_rules_and_reports_page_details() -> None:
    report = audit(make_source("<html><p>été</p></html>"), rules=[language.html_lang_missing])

    assert report.location == "page.html"
    assert report.page_size == 25
    assert [f.rule_id for f in report.findings] == ["A11Y-LANG-MISSING"]


def test_audit_uses_every_rule_by_default() -> None:
    report = audit(make_source('<html lang="french">'))

    assert [f.rule_id for f in report.findings] == ["A11Y-LANG-INVALID"]


def test_report_counts_and_thresholds() -> None:
    findings = (
        Finding(rule_id="A", severity=Severity.WARNING),
        Finding(rule_id="B", severity=Severity.WARNING),
        Finding(rule_id="C", severity=Severity.INFO),
    )
    report = Report(location="page.html", page_size=0, findings=findings)

    assert report.count(Severity.WARNING) == 2
    assert report.count(Severity.ERROR) == 0
    assert report.reaches(Severity.WARNING)
    assert not report.reaches(Severity.ERROR)
    assert not Report(location="x", page_size=0, findings=()).reaches(Severity.INFO)
