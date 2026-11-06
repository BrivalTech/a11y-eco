import pytest

from a11y_eco.dom import Document, Element, Text


def el(tag: str, *children: Element | str, attrs: dict[str, str] | None = None) -> Element:
    """Build an element by hand; strings become text nodes."""
    element = Element(tag, attrs or {})
    for child in children:
        element.append(Text(child) if isinstance(child, str) else child)
    return element


@pytest.fixture
def document() -> Document:
    doc = Document()
    doc.root.append(
        el(
            "html",
            el(
                "body",
                el("h1", "Hello ", el("em", "world"), attrs={"id": "title"}),
                el("script", "var x = 1;"),
                el("img", attrs={"src": "logo.png", "alt": ""}),
                el("p", "Bye", attrs={"id": "title"}),
            ),
            attrs={"lang": "fr"},
        )
    )
    return doc


def test_append_links_child_to_parent() -> None:
    parent, child = el("div"), el("span")

    parent.append(child)

    assert child.parent is parent
    assert parent.children == [child]


def test_iter_yields_descendants_in_document_order(document: Document) -> None:
    expected = ["html", "body", "h1", "em", "script", "img", "p"]

    assert [e.tag for e in document.root.iter()] == expected


def test_iter_excludes_the_element_itself() -> None:
    assert list(el("div").iter()) == []


def test_find_all_accepts_several_tags(document: Document) -> None:
    assert [e.tag for e in document.find_all("p", "h1")] == ["h1", "p"]


def test_find_returns_first_match_or_none(document: Document) -> None:
    assert document.root.find("em") is not None
    assert document.root.find("video") is None


def test_empty_attribute_is_present_but_empty(document: Document) -> None:
    img = document.find_all("img")[0]

    assert img.has("alt")
    assert img.get("alt") == ""
    assert not img.has("title")
    assert img.get("title") is None


def test_text_content_collapses_whitespace_and_skips_scripts(document: Document) -> None:
    body = document.find_all("body")[0]

    assert body.text_content() == "Hello worldBye"
    assert el("p", "  a \n\t b  ").text_content() == "a b"
    assert el("div").text_content() == ""


def test_document_exposes_html_element(document: Document) -> None:
    assert document.html is not None
    assert document.html.get("lang") == "fr"
    assert Document().html is None


def test_get_element_by_id_returns_first_match(document: Document) -> None:
    element = document.get_element_by_id("title")

    assert element is not None
    assert element.tag == "h1"
    assert document.get_element_by_id("missing") is None


def test_elements_are_compared_by_identity() -> None:
    assert el("p") != el("p")


def test_deep_nesting_does_not_hit_recursion_limit() -> None:
    root = current = el("div")
    for _ in range(10_000):
        child = el("div")
        current.append(child)
        current = child
    current.append(Text("deep"))

    assert sum(1 for _ in root.iter()) == 10_000
    assert root.text_content() == "deep"
    assert repr(root)  # parent/children are excluded from repr: no infinite loop
