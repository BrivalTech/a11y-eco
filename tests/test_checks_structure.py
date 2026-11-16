import pytest

from a11y_eco.checks import structure
from a11y_eco.checks.base import Rule
from a11y_eco.dom import parse_html
from a11y_eco.models import Severity

TITLE_RULES = [structure.missing_page_title, structure.missing_title]


def snippets(rule: Rule, markup: str) -> list[str]:
    return [f.snippet for f in rule.run(parse_html(markup))]


@pytest.mark.parametrize(
    ("markup", "reported"),
    [
        pytest.param(
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            False,
            id="viewport",
        ),
        pytest.param('<meta name="VIEWPORT" content="Width=device-width">', False, id="case"),
        pytest.param("<p>No viewport</p>", True, id="missing"),
        pytest.param('<meta name="viewport" content="">', True, id="empty"),
        pytest.param('<meta name="viewport" content="initial-scale=1">', True, id="no-width"),
    ],
)
def test_missing_viewport(markup: str, reported: bool) -> None:
    assert bool(snippets(structure.missing_viewport, markup)) is reported


@pytest.mark.parametrize("rule", TITLE_RULES, ids=lambda r: r.rule_id)
@pytest.mark.parametrize(
    ("markup", "expected"),
    [
        pytest.param("<head><title>Contact</title></head>", [], id="title"),
        pytest.param("<head><title> </title></head>", ["<title>"], id="blank-title"),
        pytest.param("<p>No title</p>", [""], id="missing-title-concerns-the-page"),
        pytest.param(
            "<body><svg><title>Logo</title></svg></body>",
            [""],
            id="svg-title-is-not-the-page-title",
        ),
    ],
)
def test_both_title_rules_detect_the_same_defect(
    rule: Rule, markup: str, expected: list[str]
) -> None:
    assert snippets(rule, markup) == expected


def test_title_rules_differ_by_standard_and_severity() -> None:
    a11y, eco = TITLE_RULES

    assert (a11y.reference, a11y.severity) == ("RGAA 8.5", Severity.ERROR)
    assert (eco.reference, eco.severity) == ("RWEB_0011", Severity.WARNING)


@pytest.mark.parametrize(
    ("markup", "reported"),
    [
        pytest.param('<meta name="description" content="Our services">', False, id="description"),
        pytest.param('<meta name="Description" content="Our services">', False, id="case"),
        pytest.param('<meta name="description" content="  ">', True, id="blank"),
        pytest.param('<meta property="og:description" content="Shared">', True, id="open-graph"),
        pytest.param("<p>No description</p>", True, id="missing"),
    ],
)
def test_missing_description(markup: str, reported: bool) -> None:
    assert bool(snippets(structure.missing_description, markup)) is reported
