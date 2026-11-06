"""The parser must build the same tree as browsers on real-world, imperfect HTML."""

import pytest

from a11y_eco.dom import parse_html


def structure(markup: str) -> list[tuple[str, str]]:
    """Return (tag, parent tag) for every element, in document order."""
    doc = parse_html(markup)
    return [(e.tag, e.parent.tag if e.parent else "") for e in doc.root.iter()]


@pytest.mark.parametrize(
    ("markup", "expected"),
    [
        pytest.param(
            "<ul><li>one<li>two</ul><p>after",
            [("ul", "#document"), ("li", "ul"), ("li", "ul"), ("p", "#document")],
            id="list-items-without-end-tags",
        ),
        pytest.param(
            "<p>one<p>two<div>block</div>",
            [("p", "#document"), ("p", "#document"), ("div", "#document")],
            id="paragraph-closed-by-block",
        ),
        pytest.param(
            "<ul><li><p>text<li>next</ul>",
            [("ul", "#document"), ("li", "ul"), ("p", "li"), ("li", "ul")],
            id="paragraph-closed-by-list-item",
        ),
        pytest.param(
            "<table><tr><td>a<td>b<tr><th>c</table><p>after",
            [
                ("table", "#document"),
                ("tr", "table"),
                ("td", "tr"),
                ("td", "tr"),
                ("tr", "table"),
                ("th", "tr"),
                ("p", "#document"),
            ],
            id="table-cells-and-rows-without-end-tags",
        ),
        pytest.param(
            "<select><option>a<option>b</select>",
            [("select", "#document"), ("option", "select"), ("option", "select")],
            id="options-without-end-tags",
        ),
        pytest.param(
            "<dl><dt>term<dd>definition<dt>other</dl>",
            [("dl", "#document"), ("dt", "dl"), ("dd", "dl"), ("dt", "dl")],
            id="definition-list-without-end-tags",
        ),
        pytest.param(
            "<div><span>unclosed</div><p>after",
            [("div", "#document"), ("span", "div"), ("p", "#document")],
            id="end-tag-closes-unclosed-children",
        ),
        pytest.param(
            "</section><div>text</span></div><p>after",
            [("div", "#document"), ("p", "#document")],
            id="stray-end-tags-are-ignored",
        ),
    ],
)
def test_builds_the_same_tree_as_browsers(markup: str, expected: list[tuple[str, str]]) -> None:
    assert structure(markup) == expected


def test_nested_list_item_does_not_close_the_enclosing_item() -> None:
    doc = parse_html("<ul><li>a<ul><li>b<li>c</ul><li>d</ul>")
    outer, inner = doc.find_all("ul")

    assert [li.parent for li in doc.find_all("li")] == [outer, inner, inner, outer]


def test_text_lands_in_the_right_element() -> None:
    doc = parse_html("<ul><li>one<li>two</ul>")

    assert [li.text_content() for li in doc.find_all("li")] == ["one", "two"]


def test_elements_left_open_at_the_end_are_kept() -> None:
    assert structure("<div><p>never closed") == [("div", "#document"), ("p", "div")]
