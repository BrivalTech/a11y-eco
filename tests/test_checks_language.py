import pytest

from a11y_eco.checks import language
from a11y_eco.dom import parse_html
from a11y_eco.models import Location

LANGUAGE_RULES = (language.html_lang_missing, language.html_lang_invalid)


def rule_ids(markup: str) -> list[str]:
    document = parse_html(markup)

    return [finding.rule_id for rule in LANGUAGE_RULES for finding in rule.run(document)]


@pytest.mark.parametrize(
    "markup",
    [
        pytest.param('<html lang="fr">', id="language-code"),
        pytest.param('<html lang="fr-FR">', id="language-and-region"),
        pytest.param('<html lang="zh-Hant-TW">', id="language-script-region"),
        pytest.param('<html xml:lang="fr">', id="xml-lang"),
        pytest.param('<html lang=" en ">', id="surrounding-spaces"),
    ],
)
def test_valid_language_raises_nothing(markup: str) -> None:
    assert rule_ids(markup) == []


@pytest.mark.parametrize(
    ("markup", "expected"),
    [
        pytest.param("<html><p>Bonjour</p></html>", "A11Y-LANG-MISSING", id="no-lang"),
        pytest.param('<html lang="">', "A11Y-LANG-MISSING", id="empty-lang"),
        pytest.param('<html lang="   ">', "A11Y-LANG-MISSING", id="blank-lang"),
        pytest.param("<p>No html element</p>", "A11Y-LANG-MISSING", id="no-html-element"),
        pytest.param('<html lang="french">', "A11Y-LANG-INVALID", id="language-name"),
        pytest.param('<html lang="fr_FR">', "A11Y-LANG-INVALID", id="underscore"),
        pytest.param('<html lang="f">', "A11Y-LANG-INVALID", id="too-short"),
    ],
)
def test_missing_or_invalid_language_raises_one_finding(markup: str, expected: str) -> None:
    assert rule_ids(markup) == [expected]


def test_finding_points_to_the_html_element() -> None:
    document = parse_html('<!DOCTYPE html>\n<html lang="">')
    [finding] = language.html_lang_missing.run(document)

    assert finding.location == Location(line=2, column=1)
    assert finding.snippet == '<html lang="">'


def test_finding_without_html_element_has_no_location() -> None:
    [finding] = language.html_lang_missing.run(parse_html("<p>text</p>"))

    assert finding.location is None
    assert finding.snippet == ""
