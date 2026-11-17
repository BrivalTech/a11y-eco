import json
from pathlib import Path

import pytest

from a11y_eco.checks import ALL_RULES
from a11y_eco.i18n import CATALOGS, Catalog, Language
from a11y_eco.rule_list import LIST_FORMATS, render_rules

EN = CATALOGS[Language.EN]
DOCS = Path(__file__).parent.parent / "docs"


@pytest.mark.parametrize("output_format", LIST_FORMATS)
def test_every_rule_is_listed(output_format: str) -> None:
    listing = render_rules(EN, output_format)

    assert [rule.rule_id for rule in ALL_RULES if rule.rule_id not in listing] == []


def test_json_list_describes_every_rule() -> None:
    rules = json.loads(render_rules(EN, "json"))["rules"]

    assert [rule["rule_id"] for rule in rules] == [rule.rule_id for rule in ALL_RULES]
    assert rules[0] == {
        "rule_id": "A11Y-LANG-MISSING",
        "group": "a11y",
        "severity": "error",
        "reference": "RGAA 8.3",
        "about": EN.text("about.A11Y-LANG-MISSING"),
    }
    assert {rule["group"] for rule in rules} == {"a11y", "eco", "network"}


def test_console_list_ends_with_the_number_of_rules() -> None:
    assert render_rules(EN, "console").endswith(f"\n{len(ALL_RULES)} rules.\n")


@pytest.mark.parametrize(
    ("file_name", "catalog"),
    [("rules.md", CATALOGS[Language.EN]), ("rules.fr.md", CATALOGS[Language.FR])],
)
def test_rules_documentation_is_up_to_date(file_name: str, catalog: Catalog) -> None:
    command = f"a11y-eco rules --format markdown --lang {catalog.language} > docs/{file_name}"

    written = (DOCS / file_name).read_text(encoding="utf-8")

    assert written == render_rules(catalog, "markdown"), f"Run: {command}"
