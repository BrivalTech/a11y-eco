import re

from a11y_eco.checks import RULES
from a11y_eco.checks.base import Violation, rule
from a11y_eco.dom import Document, Element, parse_html
from a11y_eco.models import Severity


def test_rule_ids_are_unique() -> None:
    ids = [r.rule_id for r in RULES]

    assert len(ids) == len(set(ids))


def test_rule_ids_follow_the_naming_convention() -> None:
    for r in RULES:
        assert re.fullmatch(r"[A-Z0-9]+(-[A-Z0-9]+)+", r.rule_id), r.rule_id


def test_every_rule_has_a_reference() -> None:
    assert all(r.reference for r in RULES)


def test_decorator_wraps_check_into_rule_that_builds_findings() -> None:
    @rule("TEST-IMG", severity=Severity.WARNING, reference="Test 1.1")
    def every_image(document: Document) -> list[Element]:
        return document.find_all("img")

    findings = every_image.run(parse_html('<img src="a.png"><p></p><img src="b.png">'))

    assert [f.rule_id for f in findings] == ["TEST-IMG", "TEST-IMG"]
    assert [f.severity for f in findings] == [Severity.WARNING, Severity.WARNING]
    assert [f.snippet for f in findings] == ['<img src="a.png">', '<img src="b.png">']
    assert {f.reference for f in findings} == {"Test 1.1"}


def test_eco_design_rules_are_never_errors() -> None:
    eco_rules = [r for r in RULES if r.rule_id.startswith("ECO-")]

    assert eco_rules
    assert all(r.severity is not Severity.ERROR for r in eco_rules)


def test_violation_carries_details_to_the_finding() -> None:
    @rule("TEST-COUNT", severity=Severity.INFO, reference="Test")
    def count_paragraphs(document: Document) -> list[Element | Violation]:
        paragraphs = document.find_all("p")
        return [Violation(document.root, {"count": len(paragraphs)}), *paragraphs]

    findings = count_paragraphs.run(parse_html("<p>a</p><p>b</p>"))

    assert [dict(f.details) for f in findings] == [{"count": 2}, {}, {}]
