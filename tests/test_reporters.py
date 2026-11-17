import pytest

from a11y_eco.i18n import CATALOGS, Language
from a11y_eco.models import Finding, Report, Severity
from a11y_eco.reporters import REPORTERS, Format, finding_message

EN = CATALOGS[Language.EN]
FR = CATALOGS[Language.FR]


def test_every_format_has_a_reporter() -> None:
    assert set(REPORTERS) == set(Format)


@pytest.mark.parametrize("output_format", list(Format))
def test_every_reporter_renders_an_empty_report(output_format: Format) -> None:
    report = Report(location="page.html", page_size=0, findings=())

    assert REPORTERS[output_format](report, EN)


def test_finding_message_writes_values_in_the_language_of_the_catalog() -> None:
    finding = Finding(
        rule_id="ECO-REQUESTS",
        severity=Severity.WARNING,
        reference="RWEB_0047",
        details={"count": 1500, "limit": 40},
    )

    assert "1\N{NARROW NO-BREAK SPACE}500" in finding_message(finding, FR)
    assert "1,500" in finding_message(finding, EN)


def test_finding_message_falls_back_to_the_rule_id() -> None:
    finding = Finding(rule_id="UNKNOWN-RULE", severity=Severity.INFO, reference="Test")

    assert finding_message(finding, EN) == "UNKNOWN-RULE"
