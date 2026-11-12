from a11y_eco.dom import Element, Text, parse_html
from a11y_eco.models import Location


def tags(element: Element) -> list[str]:
    return [e.tag for e in element.iter()]


def test_builds_nested_tree() -> None:
    doc = parse_html("<html><body><h1>Title</h1><p>Text <a href='/'>link</a></p></body></html>")

    assert tags(doc.root) == ["html", "body", "h1", "p", "a"]
    assert doc.find_all("a")[0].parent is doc.find_all("p")[0]


def test_decodes_character_references_in_text_and_attributes() -> None:
    doc = parse_html('<p title="a &amp; b">Caf&eacute; &amp; th&#233;</p>')
    p = doc.find_all("p")[0]

    assert p.text_content() == "Café & thé"
    assert p.get("title") == "a & b"


def test_lowercases_tag_and_attribute_names() -> None:
    img = parse_html('<IMG SRC="logo.png" Alt="Logo">').find_all("img")[0]

    assert img.attrs == {"src": "logo.png", "alt": "Logo"}


def test_attribute_without_value_is_empty_string() -> None:
    img = parse_html("<img alt>").find_all("img")[0]

    assert img.has("alt")
    assert img.get("alt") == ""


def test_first_duplicated_attribute_wins() -> None:
    img = parse_html('<img alt="first" alt="second">').find_all("img")[0]

    assert img.get("alt") == "first"


def test_void_elements_have_no_children() -> None:
    p = parse_html("<p>before<br>after<img src='x.png'>end</p>").find_all("p")[0]
    expected = ["Text", "Element", "Text", "Element", "Text"]

    assert [type(child).__name__ for child in p.children] == expected
    assert p.text_content() == "beforeafterend"


def test_self_closing_syntax_closes_the_element() -> None:
    doc = parse_html('<svg><path d="M0"/><circle r="1"/></svg><p>after</p>')
    svg = doc.find_all("svg")[0]

    assert [child.tag for child in svg.children if isinstance(child, Element)] == ["path", "circle"]
    assert doc.find_all("p")[0].parent is doc.root


def test_records_location_with_one_based_column() -> None:
    doc = parse_html("<html>\n  <body>\n    <img src='x.png'>\n  </body>\n</html>")

    assert doc.find_all("img")[0].location == Location(line=3, column=5)


def test_keeps_start_tag_as_written_for_reports() -> None:
    img = parse_html('<p><img  src="a.png" alt></p>').find_all("img")[0]

    assert img.start_tag == '<img  src="a.png" alt>'


def test_ignores_doctype_and_comments() -> None:
    doc = parse_html("<!DOCTYPE html><!-- note --><html></html>")

    assert doc.root.children == [doc.html]


def test_keeps_script_content_as_hidden_text() -> None:
    doc = parse_html("<script>if (a < b) { go(); }</script><p>ok</p>")
    script = doc.find_all("script")[0]

    assert isinstance(script.children[0], Text)
    assert script.children[0].data == "if (a < b) { go(); }"
    assert doc.root.text_content() == "ok"


def test_flushes_buffered_text_at_the_end() -> None:
    assert parse_html("Tom &amp").root.text_content() == "Tom &"


def test_keeps_the_page_url() -> None:
    assert parse_html("<p>", url="https://example.com/").url == "https://example.com/"
    assert parse_html("<p>").url is None
