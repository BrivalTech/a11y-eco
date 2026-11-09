import pytest

from a11y_eco.checks.accname import accessible_name
from a11y_eco.dom import Element, Text, parse_html


def name_of(markup: str, tag: str) -> str:
    """Return the accessible name of the first ``tag`` element of the markup."""
    document = parse_html(markup)
    element = document.root.find(tag)

    assert element is not None
    return accessible_name(element, document)


@pytest.mark.parametrize(
    ("markup", "expected"),
    [
        # Content
        pytest.param('<a href="/">Home</a>', "Home", id="text"),
        pytest.param('<a href="/">  Read <em>more</em>\n</a>', "Read more", id="nested-text"),
        pytest.param('<a href="/"><img src="l.png" alt="Home"></a>', "Home", id="image-alt"),
        pytest.param('<a href="/">Go<img alt="home"></a>', "Go home", id="image-is-a-word"),
        pytest.param('<a href="/"><img src="l.png" alt=""></a>', "", id="decorative-image"),
        pytest.param('<a href="/"><img src="logo.png"></a>', "", id="image-without-alt"),
        pytest.param('<a href="/"><svg aria-label="Home"></svg></a>', "Home", id="child-label"),
        pytest.param('<a href="/"><span aria-hidden="true">★</span></a>', "", id="hidden-child"),
        pytest.param('<a href="/"><span hidden>Home</span></a>', "", id="hidden-attribute"),
        pytest.param('<a href="/"><span class="sr-only">Home</span></a>', "Home", id="sr-only"),
        pytest.param('<a href="/"><script>x()</script></a>', "", id="script-ignored"),
        pytest.param('<a href="/" aria-label="Home page">Home</a>', "Home page", id="aria-label"),
        pytest.param('<a href="/" aria-label="  ">Home</a>', "Home", id="blank-aria-label"),
        pytest.param(
            '<span id="l">Cart</span><a href="/" aria-labelledby="l" aria-label="x">y</a>',
            "Cart",
            id="labelledby-wins",
        ),
        pytest.param(
            '<span id="a">Delete</span><span id="b">file.pdf</span>'
            '<button aria-labelledby="a b">X</button>',
            "Delete file.pdf",
            id="labelledby-several-ids",
        ),
        pytest.param(
            '<a href="/" aria-labelledby="missing">Home</a>', "Home", id="broken-id-ignored"
        ),
        pytest.param(
            '<span id="l" hidden>Cart</span><a href="/" aria-labelledby="l"></a>',
            "Cart",
            id="hidden-reference-counts",
        ),
        pytest.param(
            '<span id="a" aria-labelledby="b">A</span><span id="b">B</span>'
            '<a href="/" aria-labelledby="a"></a>',
            "A",
            id="no-chained-labelledby",
        ),
        pytest.param('<a href="/" title="Home"><svg></svg></a>', "Home", id="title-fallback"),
        pytest.param('<a href="/" title="Tip">Home</a>', "Home", id="content-before-title"),
        pytest.param("<button>Send</button>", "Send", id="button"),
    ],
)
def test_accessible_name(markup: str, expected: str) -> None:
    tag = "button" if "<button" in markup else "a"

    assert name_of(markup, tag) == expected


@pytest.mark.parametrize(
    ("markup", "expected"),
    [
        pytest.param('<input type="submit" value="Order">', "Order", id="submit-value"),
        pytest.param('<input type="submit">', "Submit", id="submit-default"),
        pytest.param('<input type="reset">', "Reset", id="reset-default"),
        pytest.param('<input type="submit" value="">', "", id="submit-empty-value"),
        pytest.param('<input type="button">', "", id="button-without-value"),
        pytest.param('<input type="image" alt="Search">', "Search", id="image-button"),
        pytest.param('<input type="text">', "", id="text-field"),
    ],
)
def test_accessible_name_of_inputs(markup: str, expected: str) -> None:
    assert name_of(markup, "input") == expected


def test_deeply_nested_content_does_not_hit_recursion_limit() -> None:
    document = parse_html('<a href="/"></a>')
    link = document.root.find("a")

    assert link is not None

    current = link
    for _ in range(10_000):
        child = Element("span")
        current.append(child)
        current = child
    current.append(Text("deep"))

    assert accessible_name(link, document) == "deep"
