"""Inventory of the resources that a page asks the browser to download.

The HTML is read, with the CSS it contains: stylesheets imported by ``<style>``,
fonts of its ``@font-face`` rules (loaded on demand, when a text uses them) and images
of ``style`` attributes. Background images declared in stylesheets are left out,
because they are only downloaded when a selector matches; so are files requested by
scripts. Every count based on this inventory is therefore a minimum.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import NamedTuple
from urllib.parse import urljoin, urlsplit
from weakref import WeakKeyDictionary

from a11y_eco.css import read_css
from a11y_eco.dom import Document, Element
from a11y_eco.models import ResourceType

__all__ = ["Resource", "ResourceType", "find_resources", "is_external"]
_FOUND: WeakKeyDictionary[Document, tuple[Resource, ...]] = WeakKeyDictionary()


@dataclass(frozen=True, slots=True)
class Resource:
    """A file that the page asks the browser to download."""

    url: str
    """Absolute when the page address or ``<base>`` allows it, otherwise as written."""

    type: ResourceType

    element: Element
    """The first element that references the resource."""

    deferred: bool
    """True when it is only downloaded on demand (lazy loading, ``preload="none"``)."""

    @property
    def host(self) -> str | None:
        """Host name of the server, or None for a relative URL."""
        return urlsplit(self.url).hostname


def find_resources(document: Document) -> list[Resource]:
    """List the resources referenced by a page, each address only once.

    The page is walked only the first time; the document must not be changed after.

    Args:
        document: The parsed page.

    Returns:
        The resources, in the order of their first reference.
    """
    if document not in _FOUND:
        _FOUND[document] = tuple(_walk(document))
    return list(_FOUND[document])


def _walk(document: Document) -> list[Resource]:
    base = _base_url(document)
    found: dict[str, Resource] = {}
    for element in document.root.iter():
        for reference in _references(element):
            url = urljoin(base, reference.url) if base else reference.url

            if urlsplit(url).scheme not in _DOWNLOADED_SCHEMES:
                continue
            known = found.get(url)

            if known is None or (known.deferred and not reference.deferred):
                found[url] = Resource(url, reference.type, element, reference.deferred)

    return list(found.values())


def is_external(resource: Resource, document: Document) -> bool:
    """Tell whether a resource is served by another host than the page.

    For a local file, which has no host, every resource with a host is external.

    Args:
        resource: The resource.
        document: The page that references it.

    Returns:
        True if the resource comes from another host.
    """
    page_host = urlsplit(document.url).hostname if document.url else None

    return resource.host is not None and resource.host != page_host


_DOWNLOADED_SCHEMES = frozenset({"http", "https", ""})
_SCRIPT_TYPES = frozenset({"", "module", "text/javascript", "application/javascript"})
_PRELOAD_TYPES = {
    "style": ResourceType.STYLESHEET,
    "script": ResourceType.SCRIPT,
    "image": ResourceType.IMAGE,
    "font": ResourceType.FONT,
    "audio": ResourceType.MEDIA,
    "video": ResourceType.MEDIA,
    "document": ResourceType.FRAME,
}


class _Reference(NamedTuple):
    url: str
    type: ResourceType
    deferred: bool


def _references(element: Element) -> Iterator[_Reference]:
    handler = _HANDLERS.get(element.tag)

    if handler is not None:
        yield from handler(element)

    yield from _style_attribute(element)


def _attribute(element: Element, name: str) -> str:
    return (element.get(name) or "").strip()


def _is_lazy(element: Element) -> bool:
    return _attribute(element, "loading").lower() == "lazy"


def _base_url(document: Document) -> str | None:
    """Address against which relative URLs are resolved: <base href>, then the page."""
    base = document.root.find("base")
    href = _attribute(base, "href") if base is not None else ""

    if href and (document.url or urlsplit(href).scheme):
        return urljoin(document.url or "", href)

    return document.url


def _link(element: Element) -> Iterator[_Reference]:
    href = _attribute(element, "href")
    rel = set(_attribute(element, "rel").lower().split())

    if not href:
        return

    if "stylesheet" in rel and "alternate" not in rel:
        yield _Reference(href, ResourceType.STYLESHEET, deferred=False)
    elif "preload" in rel:
        kind = _PRELOAD_TYPES.get(_attribute(element, "as").lower(), ResourceType.OTHER)
        yield _Reference(href, kind, deferred=False)
    elif "modulepreload" in rel:
        yield _Reference(href, ResourceType.SCRIPT, deferred=False)
    elif "icon" in rel:
        yield _Reference(href, ResourceType.IMAGE, deferred=False)
    elif "manifest" in rel:
        yield _Reference(href, ResourceType.OTHER, deferred=False)


def _script(element: Element) -> Iterator[_Reference]:
    src = _attribute(element, "src")
    script_type = _attribute(element, "type").lower()

    if src and not element.has("nomodule") and script_type in _SCRIPT_TYPES:
        yield _Reference(src, ResourceType.SCRIPT, deferred=False)


def _img(element: Element) -> Iterator[_Reference]:
    srcset = _attribute(element, "srcset")
    url = _attribute(element, "src") or (srcset.split(",")[0].split() or [""])[0]

    if url:
        yield _Reference(url, ResourceType.IMAGE, deferred=_is_lazy(element))


def _input(element: Element) -> Iterator[_Reference]:
    src = _attribute(element, "src")

    if src and _attribute(element, "type").lower() == "image":
        yield _Reference(src, ResourceType.IMAGE, deferred=False)


def _media(element: Element) -> Iterator[_Reference]:
    poster = _attribute(element, "poster")
    if poster:
        yield _Reference(poster, ResourceType.IMAGE, deferred=False)

    sources = [_attribute(source, "src") for source in element.find_all("source")]
    src = _attribute(element, "src") or next((url for url in sources if url), "")

    if src:
        on_demand = _attribute(element, "preload").lower() == "none"
        deferred = on_demand and not element.has("autoplay")
        yield _Reference(src, ResourceType.MEDIA, deferred=deferred)


def _frame(element: Element) -> Iterator[_Reference]:
    url = _attribute(element, "data" if element.tag == "object" else "src")

    if url:
        yield _Reference(url, ResourceType.FRAME, deferred=_is_lazy(element))


def _style(element: Element) -> Iterator[_Reference]:
    css = read_css(element.text_content())

    for url in css.imports:
        yield _Reference(url, ResourceType.STYLESHEET, deferred=False)

    for url in css.font_faces:
        yield _Reference(url, ResourceType.FONT, deferred=True)


def _style_attribute(element: Element) -> Iterator[_Reference]:
    css = _attribute(element, "style")

    if not css or _is_hidden(element):
        return

    for url in read_css(css).urls:
        yield _Reference(url, ResourceType.IMAGE, deferred=False)


def _is_hidden(element: Element) -> bool:
    """Tell whether the element or an ancestor has the hidden attribute."""
    return element.has("hidden") or any(parent.has("hidden") for parent in element.ancestors())


_HANDLERS: dict[str, Callable[[Element], Iterator[_Reference]]] = {
    "link": _link,
    "script": _script,
    "img": _img,
    "input": _input,
    "video": _media,
    "audio": _media,
    "iframe": _frame,
    "embed": _frame,
    "object": _frame,
    "style": _style,
}
