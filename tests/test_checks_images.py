import pytest

from a11y_eco.checks import images
from a11y_eco.dom import parse_html


def snippets(markup: str) -> list[str]:
    """Return the start tag of every element reported by the rule."""
    return [f.snippet for f in images.image_without_alternative.run(parse_html(markup))]


@pytest.mark.parametrize(
    "markup",
    [
        pytest.param('<img src="a.png" alt="Logo">', id="alt"),
        pytest.param('<img src="a.png" alt="">', id="decorative-empty-alt"),
        pytest.param('<img src="a.png" alt>', id="decorative-alt-without-value"),
        pytest.param('<img src="a.png" aria-label="Logo">', id="aria-label"),
        pytest.param('<img src="a.png" aria-labelledby="caption">', id="aria-labelledby"),
        pytest.param('<img src="a.png" title="Logo">', id="title"),
        pytest.param('<img src="a.png" aria-hidden="true">', id="aria-hidden"),
        pytest.param('<div hidden><img src="a.png"></div>', id="hidden-ancestor"),
        pytest.param('<img src="a.png" role="presentation">', id="role-presentation"),
        pytest.param('<area href="/" alt="Home">', id="area-link-with-alt"),
        pytest.param('<area shape="rect">', id="area-without-href"),
        pytest.param('<input type="image" src="ok.png" alt="Send">', id="image-button"),
        pytest.param('<input type="text" name="q">', id="other-input"),
    ],
)
def test_image_with_alternative_raises_nothing(markup: str) -> None:
    assert snippets(markup) == []


@pytest.mark.parametrize(
    "markup",
    [
        pytest.param('<img src="a.png">', id="no-alt"),
        pytest.param('<img src="a.png" aria-label="  ">', id="blank-aria-label"),
        pytest.param('<img src="a.png" aria-hidden="false">', id="aria-hidden-false"),
        pytest.param('<area href="/">', id="area-link-without-alt"),
        pytest.param('<area href="/" alt="">', id="area-link-with-empty-alt"),
        pytest.param('<input type="image" src="ok.png">', id="image-button-without-alt"),
        pytest.param('<input type="IMAGE" src="ok.png" alt="">', id="image-button-empty-alt"),
    ],
)
def test_image_without_alternative_is_reported(markup: str) -> None:
    assert snippets(markup) == [markup]


def test_reports_every_faulty_image_in_document_order() -> None:
    markup = '<img src="1.png"><img src="2.png" alt=""><p><img src="3.png"></p>'

    assert snippets(markup) == ['<img src="1.png">', '<img src="3.png">']
