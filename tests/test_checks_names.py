import pytest

from a11y_eco.checks import names
from a11y_eco.checks.base import Rule
from a11y_eco.dom import parse_html


def snippets(rule: Rule, markup: str) -> list[str]:
    return [f.snippet for f in rule.run(parse_html(markup))]


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
    assert snippets(names.broken_labelledby_reference, markup) == []


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
    assert snippets(names.broken_labelledby_reference, markup) == expected


@pytest.mark.parametrize(
    "markup",
    [
        pytest.param('<a href="/">Home</a>', id="text"),
        pytest.param('<a href="/"><img src="logo.png" alt="Home"></a>', id="image-alt"),
        pytest.param('<a href="/" aria-label="Home"><svg></svg></a>', id="aria-label"),
        pytest.param('<a href="/" title="Home"><svg></svg></a>', id="title"),
        pytest.param('<a id="top"></a>', id="anchor-without-href-is-not-a-link"),
        pytest.param('<a href="/" aria-hidden="true"></a>', id="hidden-link"),
        pytest.param('<span role="link" tabindex="0">Home</span>', id="aria-link-with-text"),
    ],
)
def test_link_with_name_raises_nothing(markup: str) -> None:
    assert snippets(names.link_without_name, markup) == []


@pytest.mark.parametrize(
    ("markup", "expected"),
    [
        pytest.param('<a href="/"></a>', '<a href="/">', id="empty"),
        pytest.param(
            '<a href="/"><img src="logo.png" alt=""></a>', '<a href="/">', id="decorative-image"
        ),
        pytest.param('<a href="/"><svg></svg></a>', '<a href="/">', id="unlabelled-svg"),
        pytest.param('<a href="/"><i class="icon-home"></i></a>', '<a href="/">', id="icon-font"),
        pytest.param(
            '<span role="link" tabindex="0"></span>',
            '<span role="link" tabindex="0">',
            id="aria-link",
        ),
    ],
)
def test_link_without_name_is_reported(markup: str, expected: str) -> None:
    assert snippets(names.link_without_name, markup) == [expected]


@pytest.mark.parametrize(
    "markup",
    [
        pytest.param("<button>Send</button>", id="text"),
        pytest.param('<button aria-label="Close"><svg></svg></button>', id="aria-label"),
        pytest.param('<input type="submit">', id="submit-default-name"),
        pytest.param('<input type="button" value="Print">', id="input-button-value"),
        pytest.param('<input type="image" src="go.png">', id="image-button-left-to-image-rule"),
        pytest.param('<button role="tab"></button>', id="other-role"),
        pytest.param('<div role="button">Menu</div>', id="aria-button-with-text"),
    ],
)
def test_button_with_name_raises_nothing(markup: str) -> None:
    assert snippets(names.button_without_name, markup) == []


@pytest.mark.parametrize(
    ("markup", "expected"),
    [
        pytest.param("<button></button>", "<button>", id="empty"),
        pytest.param(
            '<button><span aria-hidden="true">&times;</span></button>', "<button>", id="hidden-icon"
        ),
        pytest.param('<input type="button">', '<input type="button">', id="input-without-value"),
        pytest.param(
            '<input type="submit" value="">',
            '<input type="submit" value="">',
            id="submit-empty-value",
        ),
        pytest.param('<div role="button"></div>', '<div role="button">', id="aria-button"),
    ],
)
def test_button_without_name_is_reported(markup: str, expected: str) -> None:
    assert snippets(names.button_without_name, markup) == [expected]
