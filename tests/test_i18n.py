import string

import pytest

from a11y_eco.checks import RULES
from a11y_eco.i18n import CATALOGS, Language, detect_language
from a11y_eco.i18n.catalog import Catalog
from a11y_eco.models import ResourceType, Severity

EN = CATALOGS[Language.EN]
FR = CATALOGS[Language.FR]


def placeholders(template: str) -> set[str]:
    """Return the names between braces in a template: "{count} errors" -> {"count"}."""
    names = set()
    for _, name, _, _ in string.Formatter().parse(template):
        if name:
            names.add(name)
    return names


def test_every_language_has_its_catalog() -> None:
    assert set(CATALOGS) == set(Language)
    for language, catalog in CATALOGS.items():
        assert catalog.language == language


def test_catalogs_have_exactly_the_same_keys() -> None:
    assert sorted(EN.messages.keys() - FR.messages.keys()) == []
    assert sorted(FR.messages.keys() - EN.messages.keys()) == []


@pytest.mark.parametrize("key", sorted(EN.messages))
def test_translations_use_the_same_placeholders(key: str) -> None:
    assert placeholders(FR.messages[key]) == placeholders(EN.messages[key])


@pytest.mark.parametrize("catalog", CATALOGS.values(), ids=lambda c: c.language)
def test_every_rule_has_a_title(catalog: Catalog) -> None:
    missing = [r.rule_id for r in RULES if f"rule.{r.rule_id}" not in catalog.messages]
    assert missing == []


@pytest.mark.parametrize("catalog", CATALOGS.values(), ids=lambda c: c.language)
def test_every_severity_has_a_name_and_both_plural_forms(catalog: Catalog) -> None:
    for severity in Severity:
        assert f"severity.{severity}" in catalog.messages
        assert f"count.{severity}.one" in catalog.messages
        assert f"count.{severity}.other" in catalog.messages


@pytest.mark.parametrize(
    ("catalog", "count", "expected"),
    [
        pytest.param(EN, 0, "0 errors", id="en-zero"),
        pytest.param(EN, 1, "1 error", id="en-one"),
        pytest.param(EN, 2, "2 errors", id="en-two"),
        pytest.param(FR, 0, "0 erreur", id="fr-zero-is-singular"),
        pytest.param(FR, 1, "1 erreur", id="fr-one"),
        pytest.param(FR, 2, "2 erreurs", id="fr-two"),
    ],
)
def test_count_uses_the_plural_rules_of_the_language(
    catalog: Catalog, count: int, expected: str
) -> None:
    assert catalog.count("count.error", count) == expected


@pytest.mark.parametrize(
    ("catalog", "expected"),
    [(EN, "1,234,567"), (FR, "1\N{NARROW NO-BREAK SPACE}234\N{NARROW NO-BREAK SPACE}567")],
    ids=["en", "fr"],
)
def test_numbers_use_the_separator_of_the_language(catalog: Catalog, expected: str) -> None:
    assert catalog.number(1_234_567) == expected


def test_text_fills_in_placeholders() -> None:
    assert FR.text("report.title", location="page.html", size="12") == (
        "Audit de page.html (12 octets)"
    )


def test_missing_key_is_a_programming_error() -> None:
    with pytest.raises(KeyError):
        EN.text("no.such.key")


def test_unknown_rule_title_falls_back_to_its_identifier() -> None:
    assert FR.rule_title("UNKNOWN-RULE") == "UNKNOWN-RULE"
    assert FR.rule_title("A11Y-LINK-NAME") == "Lien sans intitulé"


@pytest.mark.parametrize(
    ("environ", "expected"),
    [
        pytest.param({"LANG": "fr_FR.UTF-8"}, Language.FR, id="french-locale"),
        pytest.param({"LANG": "en_GB.UTF-8"}, Language.EN, id="english-locale"),
        pytest.param({"LANG": "fr_CA"}, Language.FR, id="other-french-region"),
        pytest.param({"LANG": "FR_fr"}, Language.FR, id="uppercase"),
        pytest.param({"LANG": "fr@euro"}, Language.FR, id="locale-modifier"),
        pytest.param({"LANG": "en"}, Language.EN, id="code-only"),
        pytest.param({"LC_ALL": "en_US.UTF-8", "LANG": "fr_FR"}, Language.EN, id="lc-all-wins"),
        pytest.param(
            {"LC_MESSAGES": "en_US", "LANG": "fr_FR"}, Language.EN, id="lc-messages-before-lang"
        ),
        pytest.param({"LANGUAGE": "de:en", "LANG": "fr_FR"}, Language.EN, id="language-list"),
        pytest.param({"LC_ALL": "de_DE", "LANG": "en_US"}, Language.EN, id="unsupported-skipped"),
        pytest.param({"LANG": "C.UTF-8"}, Language.FR, id="c-locale-uses-default"),
        pytest.param({"LC_ALL": "", "LANG": "en_US"}, Language.EN, id="empty-variable-skipped"),
        pytest.param({}, Language.FR, id="nothing-set-uses-default"),
    ],
)
def test_detect_language(environ: dict[str, str], expected: Language) -> None:
    assert detect_language(environ) is expected


@pytest.mark.parametrize("catalog", CATALOGS.values(), ids=lambda c: c.language)
def test_every_resource_type_has_both_plural_forms(catalog: Catalog) -> None:
    for kind in ResourceType:
        assert f"resource.{kind}.one" in catalog.messages
        assert f"resource.{kind}.other" in catalog.messages
