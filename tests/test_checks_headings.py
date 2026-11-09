import pytest

from a11y_eco.checks import headings
from a11y_eco.checks.base import Rule
from a11y_eco.dom import parse_html


def snippets(rule: Rule, markup: str) -> list[str]:
    return [f.snippet for f in rule.run(parse_html(markup))]


@pytest.mark.parametrize(
    "markup",
    [
        pytest.param("<h1>Title</h1>", id="h1"),
        pytest.param('<div role="heading" aria-level="1">Title</div>', id="aria-h1"),
    ],
)
def test_page_with_a_main_heading_raises_nothing(markup: str) -> None:
    assert snippets(headings.missing_main_heading, markup) == []


@pytest.mark.parametrize(
    "markup",
    [
        pytest.param("<p>No heading at all</p>", id="no-heading"),
        pytest.param("<h2>Section</h2>", id="starts-at-h2"),
        pytest.param('<h1 aria-hidden="true">Title</h1>', id="hidden-h1"),
        pytest.param('<h1 role="presentation">Title</h1>', id="h1-without-heading-role"),
    ],
)
def test_page_without_main_heading_is_reported(markup: str) -> None:
    [finding] = headings.missing_main_heading.run(parse_html(markup))

    assert finding.location is None  # the whole page is concerned


def test_every_extra_main_heading_is_reported() -> None:
    markup = "<h1>A</h1><h2>B</h2><h1>C</h1><h1>D</h1>"

    assert snippets(headings.several_main_headings, markup) == ["<h1>", "<h1>"]
    assert snippets(headings.several_main_headings, "<h1>A</h1><h2>B</h2>") == []


@pytest.mark.parametrize(
    "markup",
    [
        pytest.param("<h1></h1><h2></h2><h3></h3>", id="one-level-at-a-time"),
        pytest.param("<h1></h1><h2></h2><h3></h3><h2></h2>", id="going-back-up"),
        pytest.param("<h1></h1><h2></h2><h3></h3><h4></h4><h2></h2>", id="going-up-several"),
        pytest.param("<h2></h2><h3></h3>", id="first-heading-is-free"),
        pytest.param('<h1></h1><h3 aria-hidden="true"></h3><h2></h2>', id="hidden-ignored"),
    ],
)
def test_coherent_hierarchy_raises_nothing(markup: str) -> None:
    assert snippets(headings.skipped_heading_level, markup) == []


@pytest.mark.parametrize(
    ("markup", "expected"),
    [
        pytest.param("<h1></h1><h3></h3>", ["<h3>"], id="h1-to-h3"),
        pytest.param("<h1></h1><h2></h2><h4></h4><h6></h6>", ["<h4>", "<h6>"], id="two-skips"),
        pytest.param(
            '<h1></h1><div role="heading" aria-level="4"></div>',
            ['<div role="heading" aria-level="4">'],
            id="aria-heading",
        ),
    ],
)
def test_skipped_level_is_reported(markup: str, expected: list[str]) -> None:
    assert snippets(headings.skipped_heading_level, markup) == expected
