import re

from a11y_eco.checks import RULES
from a11y_eco.checks.base import rule
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
