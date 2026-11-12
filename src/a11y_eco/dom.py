"""Lightweight DOM built from static HTML.

It only holds what the checks need: elements with their attributes, text, and the
links between parents and children. There is no CSS, no script execution, no layout.

The parser recovers from common errors the way browsers do: omitted end tags
(``li``, ``p``, ``td``, ``option``…), unclosed elements and stray end tags. It is not
a full implementation of the HTML standard: overlapping formatting elements and
elements that browsers insert on their own (``tbody``, a missing ``body``) are not
handled.
"""

from __future__ import annotations

from collections.abc import Collection, Iterator
from dataclasses import dataclass, field
from html.parser import HTMLParser

from a11y_eco.models import Location

HIDDEN_TEXT_ELEMENTS = frozenset({"script", "style", "template"})
VOID_ELEMENTS = frozenset(
    {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "source",
        "track",
        "wbr",
    }
)
_CLOSES_PARAGRAPH = frozenset(
    {
        "address",
        "article",
        "aside",
        "blockquote",
        "dd",
        "details",
        "div",
        "dl",
        "dt",
        "fieldset",
        "figcaption",
        "figure",
        "footer",
        "form",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "header",
        "hr",
        "li",
        "main",
        "nav",
        "ol",
        "p",
        "pre",
        "section",
        "table",
        "ul",
    }
)
_PARAGRAPH_SCOPE = frozenset({"button", "caption", "table", "td", "template", "th"})
_IMPLIED_END_TAGS: dict[str, tuple[frozenset[str], frozenset[str]]] = {
    "li": (frozenset({"li"}), frozenset({"ol", "ul"})),
    "dt": (frozenset({"dd", "dt"}), frozenset({"dl"})),
    "dd": (frozenset({"dd", "dt"}), frozenset({"dl"})),
    "option": (frozenset({"option"}), frozenset({"datalist", "optgroup", "select"})),
    "tr": (frozenset({"tr"}), frozenset({"table", "tbody", "tfoot", "thead"})),
    "td": (frozenset({"td", "th"}), frozenset({"table", "tr"})),
    "th": (frozenset({"td", "th"}), frozenset({"table", "tr"})),
}


@dataclass(eq=False, slots=True)
class Text:
    """A run of text inside an element."""

    data: str
    parent: Element | None = field(default=None, repr=False)


@dataclass(eq=False, slots=True)
class Element:
    """An HTML element.

    Tag and attribute names are lowercase. An attribute written without a value,
    such as ``<img alt>``, has the empty string as value, as in the HTML standard.
    """

    tag: str
    attrs: dict[str, str] = field(default_factory=dict)
    location: Location | None = None
    start_tag: str = field(default="", repr=False)
    parent: Element | None = field(default=None, repr=False)
    children: list[Element | Text] = field(default_factory=list, repr=False)

    def append(self, node: Element | Text) -> None:
        """Add a node as the last child of this element.

        Args:
            node: The element or text to attach.
        """
        node.parent = self
        self.children.append(node)

    def get(self, name: str) -> str | None:
        """Return the value of an attribute, or None if it is absent.

        Args:
            name: Lowercase attribute name.

        Returns:
            The attribute value, possibly empty, or None.
        """
        return self.attrs.get(name)

    def has(self, name: str) -> bool:
        """Tell whether an attribute is present, even with an empty value.

        Args:
            name: Lowercase attribute name.

        Returns:
            True if the attribute is present.
        """
        return name in self.attrs

    def iter(self) -> Iterator[Element]:
        """Yield every descendant element in document order.

        Yields:
            Descendant elements, this element excluded.
        """
        stack = list(reversed(self.children))
        while stack:
            node = stack.pop()
            if isinstance(node, Element):
                yield node
                stack.extend(reversed(node.children))

    def find_all(self, *tags: str) -> list[Element]:
        """Return the descendant elements with one of the given tags.

        Args:
            *tags: Lowercase tag names.

        Returns:
            Matching elements in document order.
        """
        wanted = set(tags)
        return [element for element in self.iter() if element.tag in wanted]

    def find(self, tag: str) -> Element | None:
        """Return the first descendant element with the given tag.

        Args:
            tag: Lowercase tag name.

        Returns:
            The first matching element, or None.
        """
        return next((element for element in self.iter() if element.tag == tag), None)

    def text_content(self) -> str:
        """Return the visible text of the element, with whitespace collapsed.

        Text inside ``script``, ``style`` and ``template`` is ignored.

        Returns:
            The text, possibly empty.
        """
        parts: list[str] = []
        stack: list[Element | Text] = list(reversed(self.children))
        while stack:
            node = stack.pop()
            if isinstance(node, Text):
                parts.append(node.data)
            elif node.tag not in HIDDEN_TEXT_ELEMENTS:
                stack.extend(reversed(node.children))
        return " ".join("".join(parts).split())


@dataclass(eq=False, slots=True)
class Document:
    """A parsed HTML document."""

    root: Element = field(default_factory=lambda: Element("#document"))
    url: str | None = None
    """Address of the page when it was loaded from the web, like ``document.URL``."""

    @property
    def html(self) -> Element | None:
        """The ``<html>`` element, or None if the source has none."""
        return self.root.find("html")

    def find_all(self, *tags: str) -> list[Element]:
        """Return every element of the document with one of the given tags.

        Args:
            *tags: Lowercase tag names.

        Returns:
            Matching elements in document order.
        """
        return self.root.find_all(*tags)

    def get_element_by_id(self, element_id: str) -> Element | None:
        """Return the first element with the given ``id``, as browsers do.

        Args:
            element_id: The identifier to look for.

        Returns:
            The first matching element, or None.
        """
        return next((e for e in self.root.iter() if e.get("id") == element_id), None)


def parse_html(markup: str, *, url: str | None = None) -> Document:
    """Parse HTML source into a document.

    Args:
        markup: The HTML source, already decoded to text.
        url: Address of the page, used to resolve relative links; None for a local file

    Returns:
        The parsed document.
    """
    builder = _TreeBuilder()
    builder.feed(markup)
    builder.close()
    builder.document.url = url

    return builder.document


class _TreeBuilder(HTMLParser):
    """Turn the events emitted by ``html.parser`` into a tree of nodes."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.document = Document()
        self._open_elements: list[Element] = [self.document.root]

    @property
    def _current(self) -> Element:
        return self._open_elements[-1]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._close_implied_elements(tag)
        line, offset = self.getpos()
        element = Element(
            tag,
            _normalize_attrs(attrs),
            location=Location(line, offset + 1),
            start_tag=self.get_starttag_text() or "",
        )
        self._current.append(element)
        if tag not in VOID_ELEMENTS:
            self._open_elements.append(element)

    def handle_endtag(self, tag: str) -> None:
        if tag in VOID_ELEMENTS:
            return
        self._close_nearest({tag})

    def handle_data(self, data: str) -> None:
        self._current.append(Text(data))

    def _close_implied_elements(self, tag: str) -> None:
        """Close the elements whose end tag may be omitted before ``tag``."""
        if tag in _CLOSES_PARAGRAPH:
            self._close_nearest({"p"}, boundaries=_PARAGRAPH_SCOPE)
        if tag in _IMPLIED_END_TAGS:
            targets, boundaries = _IMPLIED_END_TAGS[tag]
            self._close_nearest(targets, boundaries=boundaries)

    def _close_nearest(self, targets: Collection[str], boundaries: Collection[str] = ()) -> None:
        """Close the nearest open element among ``targets``, unless a boundary comes first.

        The search goes from the most recently opened element outwards. The element
        found is closed together with every element opened after it. The document
        root is never closed.
        """
        for index in range(len(self._open_elements) - 1, 0, -1):
            tag = self._open_elements[index].tag
            if tag in targets:
                del self._open_elements[index:]
                return
            if tag in boundaries:
                return


def _normalize_attrs(attrs: list[tuple[str, str | None]]) -> dict[str, str]:
    """Convert ``html.parser`` attributes into a dictionary.

    An attribute without a value becomes the empty string, and when an attribute is
    duplicated the first occurrence wins, as in browsers.
    """
    normalized: dict[str, str] = {}
    for name, value in attrs:
        normalized.setdefault(name, value or "")
    return normalized
