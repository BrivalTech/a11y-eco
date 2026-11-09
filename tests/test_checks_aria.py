import pytest

from a11y_eco.checks.aria import has_role, has_text, is_hidden
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
