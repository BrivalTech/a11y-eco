from a11y_eco.checks import RULES
from a11y_eco.messages import RULE_TITLES, count_severity, rule_title
from a11y_eco.models import Severity


def test_every_rule_has_a_title() -> None:
    assert {r.rule_id for r in RULES} <= RULE_TITLES.keys()


def test_rule_title_falls_back_to_identifier() -> None:
    assert rule_title("UNKNOWN-RULE") == "UNKNOWN-RULE"


def test_count_severity_uses_singular_and_plural() -> None:
    assert count_severity(1, Severity.ERROR) == "1 error"
    assert count_severity(0, Severity.ERROR) == "0 errors"
    assert count_severity(2, Severity.WARNING) == "2 warnings"
