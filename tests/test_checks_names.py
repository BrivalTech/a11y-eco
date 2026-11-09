import pytest

from a11y_eco.checks import names
from a11y_eco.dom import parse_html


def snippets(markup: str) -> list[str]:
    return [f.snippet for f in names.broken_labelledby_reference.run(parse_html(markup))]


@pytest.mark.parametrize(
    "markup",
    [
        pytest.param('<span id="l">Cart</span><a href="/" aria-labelledby="l">', id="valid"),
        pytest.param(
            '<span id="a"></span><span id="b"></span><button aria-labelledby="a b">',
            id="several-valid-ids",
        ),
        pytest.param('<a href="/" aria-labelledby="l"></a><p id="l">Later</p>', id="id-after"),
        pytest.param('<a href="/" aria-labelledby="">Home</a>', id="empty-attribute"),
        pytest.param('<a href="/">Home</a>', id="no-attribute"),
    ],
)
def test_existing_references_raise_nothing(markup: str) -> None:
    assert snippets(markup) == []


@pytest.mark.parametrize(
    ("markup", "expected"),
    [
        pytest.param(
            '<a href="/" aria-labelledby="missing">',
            ['<a href="/" aria-labelledby="missing">'],
            id="missing-id",
        ),
        pytest.param(
            '<span id="a"></span><img src="x.png" aria-labelledby="a b">',
            ['<img src="x.png" aria-labelledby="a b">'],
            id="one-of-several-ids-missing",
        ),
    ],
)
def test_missing_reference_is_reported(markup: str, expected: list[str]) -> None:
    assert snippets(markup) == expected
