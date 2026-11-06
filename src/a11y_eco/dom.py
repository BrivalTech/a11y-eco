"""Lightweight DOM built from static HTML.

It takes what the checks need: elements with their attributes, text, and the
links between parents and children. There is no CSS, no script execution, no layout.
"""

from __future__ import annotations

from collections.abc import Iterator
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


def parse_html(markup: str) -> Document:
    """Parse HTML source into a document.

    Args:
        markup: The HTML source, already decoded to text.

    Returns:
        The parsed document.
    """
    builder = _TreeBuilder()
    builder.feed(markup)
    builder.close()
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
        if self._current.tag == tag:
            self._open_elements.pop()

    def handle_data(self, data: str) -> None:
        self._current.append(Text(data))


def _normalize_attrs(attrs: list[tuple[str, str | None]]) -> dict[str, str]:
    """Convert ``html.parser`` attributes into a dictionary.

    An attribute without a value becomes the empty string, and when an attribute is
    duplicated the first occurrence wins, as in browsers.
    """
    normalized: dict[str, str] = {}
    for name, value in attrs:
        normalized.setdefault(name, value or "")
    return normalized
