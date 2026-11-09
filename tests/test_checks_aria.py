import pytest

from a11y_eco.checks.aria import has_role, has_text, heading_level, hides_itself, is_hidden
from a11y_eco.dom import Element, parse_html


def first(markup: str, tag: str) -> Element:
    element = parse_html(markup).root.find(tag)

    assert element is not None
    return element


@pytest.mark.parametrize(
    ("markup", "expected"),
    [
        ('<img alt="Logo">', True),
        ('<img alt="  ">', False),
        ('<img alt="">', False),
        ("<img>", False),
    ],
)
def test_has_text(markup: str, expected: bool) -> None:
    assert has_text(first(markup, "img"), "alt") is expected


@pytest.mark.parametrize(
    ("markup", "expected"),
    [
        ('<img role="presentation">', True),
        ('<img role="NONE">', True),
        ('<img role="none img">', True),
        ('<img role="img none">', False),
        ("<img>", False),
    ],
)
def test_has_role_reads_the_first_declared_role(markup: str, expected: bool) -> None:
    assert has_role(first(markup, "img"), "presentation", "none") is expected


@pytest.mark.parametrize(
    ("markup", "expected"),
    [
        pytest.param('<img aria-hidden="true">', True, id="aria-hidden"),
        pytest.param('<img aria-hidden="TRUE">', True, id="aria-hidden-uppercase"),
        pytest.param('<img aria-hidden="false">', False, id="aria-hidden-false"),
        pytest.param("<img hidden>", True, id="hidden-attribute"),
        pytest.param('<div aria-hidden="true"><p><img></p></div>', True, id="hidden-ancestor"),
        pytest.param("<div><img></div>", False, id="visible"),
    ],
)
def test_is_hidden(markup: str, expected: bool) -> None:
    assert is_hidden(first(markup, "img")) is expected


@pytest.mark.parametrize(
    ("markup", "expected"),
    [
        pytest.param("<h1>", 1, id="h1"),
        pytest.param("<h6>", 6, id="h6"),
        pytest.param('<div role="heading" aria-level="3">', 3, id="aria-heading"),
        pytest.param('<div role="heading">', 2, id="aria-heading-default-level"),
        pytest.param('<h4 role="heading">', 4, id="native-level-kept"),
        pytest.param('<h1 role="heading" aria-level="2">', 2, id="aria-level-wins"),
        pytest.param('<div role="heading" aria-level="0">', 2, id="invalid-level"),
        pytest.param('<div role="heading" aria-level="²">', 2, id="superscript-digit"),
        pytest.param('<h2 role="presentation">', None, id="heading-role-removed"),
        pytest.param('<h2 role="tab">', None, id="other-role"),
        pytest.param("<p>", None, id="not-a-heading"),
    ],
)
def test_heading_level(markup: str, expected: int | None) -> None:
    element = next(parse_html(markup).root.iter())
    assert heading_level(element) == expected


def test_hides_itself_ignores_ancestors() -> None:
    img = first('<div hidden><img aria-hidden="false"></div>', "img")

    assert not hides_itself(img)
    assert is_hidden(img)
