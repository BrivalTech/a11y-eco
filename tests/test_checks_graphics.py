import pytest

from a11y_eco.checks import graphics
from a11y_eco.dom import parse_html


def animations(markup: str) -> list[str]:
    return [f.snippet for f in graphics.too_many_animations.run(parse_html(markup))]


SPIN = '<div style="animation: spin 1s infinite"></div>'


@pytest.mark.parametrize(
    ("markup", "count"),
    [
        pytest.param(SPIN * 2, 0, id="2-animations-is-the-limit"),
        pytest.param(SPIN * 3, 3, id="3-inline-animations"),
        pytest.param(
            "<marquee>News</marquee>"
            '<lottie-player src="a.json"></lottie-player>'
            '<p class="animate__animated animate__bounce">Hi</p>',
            3,
            id="known-tools",
        ),
        pytest.param(
            '<svg><circle r="5"><animate attributeName="r" values="5;10"/></circle>'
            '<rect><animateTransform attributeName="transform" type="rotate"/></rect>'
            '<path><animateMotion dur="2s"/></path></svg>',
            3,
            id="svg-smil",
        ),
        pytest.param(
            '<div style="animation-name: fade"></div>' * 3, 3, id="animation-name-property"
        ),
        pytest.param('<div style="animation: none"></div>' * 3, 0, id="animation-none"),
        pytest.param(
            '<div style="transition: opacity 1s"></div>' * 3, 0, id="transitions-need-an-action"
        ),
        pytest.param(
            "<style>@keyframes spin{to{rotate:1turn}} .a{animation:spin 1s}</style>"
            '<div class="a"></div>' * 3,
            0,
            id="stylesheet-animations-not-counted",
        ),
    ],
)
def test_too_many_animations(markup: str, count: int) -> None:
    assert len(animations(markup)) == count


def test_animation_findings_carry_the_count() -> None:
    findings = graphics.too_many_animations.run(parse_html(SPIN * 3))

    assert dict(findings[0].details) == {"count": 3, "limit": 2}


CLEAN_SVG = '<svg viewBox="0 0 10 10"><path d="M0 0h10v10z"/></svg>'


@pytest.mark.parametrize(
    ("markup", "reported"),
    [
        pytest.param(CLEAN_SVG, False, id="clean"),
        pytest.param(
            '<svg xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape">'
            '<path d="M0 0"/></svg>',
            True,
            id="inkscape-namespace",
        ),
        pytest.param(
            '<svg><sodipodi:namedview pagecolor="#fff"/><path d="M0 0"/></svg>',
            True,
            id="sodipodi-element",
        ),
        pytest.param(
            '<svg><g inkscape:label="Layer 1"><path d="M0 0"/></g></svg>',
            True,
            id="inkscape-attribute",
        ),
        pytest.param(
            '<svg><metadata><rdf:RDF></rdf:RDF></metadata><path d="M0 0"/></svg>',
            True,
            id="metadata-element",
        ),
    ],
)
def test_unoptimised_svg(markup: str, reported: bool) -> None:
    findings = graphics.unoptimised_svg.run(parse_html(markup))

    assert bool(findings) is reported


def test_nested_svg_is_reported_once_with_the_outermost() -> None:
    markup = '<svg id="outer"><g><svg><metadata/></svg></g></svg>'

    findings = graphics.unoptimised_svg.run(parse_html(markup))

    assert [f.snippet for f in findings] == ['<svg id="outer">']
