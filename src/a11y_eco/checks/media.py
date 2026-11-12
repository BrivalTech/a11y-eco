"""Rules about images, audio, video, embedded content and fonts (RWEB)."""

from __future__ import annotations

import posixpath
from collections.abc import Iterator
from urllib.parse import urlsplit

from a11y_eco.checks.base import Violation, rule
from a11y_eco.dom import Document, Element
from a11y_eco.models import ResourceType, Severity
from a11y_eco.resources import find_resources

MAX_FONTS = 2
DOCUMENT_EXTENSIONS = frozenset(
    {".pdf", ".doc", ".docx", ".odt", ".rtf", ".xls", ".xlsx", ".ods", ".ppt", ".pptx", ".odp"}
)
FONT_SERVICES = frozenset({"fonts.googleapis.com", "use.typekit.net", "fonts.bunny.net"})


def _attribute(element: Element, name: str) -> str:
    return (element.get(name) or "").strip()


def _extension(url: str) -> str:
    """Lowercase extension of the file an address points to: "/a/Doc.PDF?v=2" -> ".pdf"."""
    return posixpath.splitext(urlsplit(url).path)[1].lower()


def _image_url(img: Element) -> str:
    """Address the browser downloads for an image: src, otherwise the first srcset candidate."""
    candidates = _attribute(img, "srcset").split(",")[0].split()
    url = _attribute(img, "src") or (candidates[0] if candidates else "")

    return "" if url.startswith("data:") else url


@rule("ECO-MEDIA-AUTOLOAD", severity=Severity.WARNING, reference="RWEB_0106")
def media_loaded_automatically(document: Document) -> Iterator[Element]:
    """Audio and video should only be downloaded when the user asks for them."""
    for element in document.find_all("video", "audio"):
        # Without preload="none", browsers download at least part of the file.
        if element.has("autoplay") or _attribute(element, "preload").lower() != "none":
            yield element


@rule("ECO-LAZY-LOADING", severity=Severity.INFO, reference="RWEB_0051")
def missing_lazy_loading(document: Document) -> Iterator[Element]:
    """Images and frames that may be out of view should use loading="lazy"."""
    seen_first: set[str] = set()

    for element in document.find_all("img", "iframe"):
        url = _image_url(element) if element.tag == "img" else _attribute(element, "src")
        if not url:
            continue

        if element.tag not in seen_first:
            seen_first.add(element.tag)
            continue

        if _attribute(element, "loading").lower() != "lazy":
            yield element


@rule("ECO-EMBEDDED-DOCUMENT", severity=Severity.WARNING, reference="RWEB_0033")
def document_displayed_in_page(document: Document) -> Iterator[Element]:
    """Documents (PDF, office files) should be linked to, not displayed in the page."""
    for element in document.find_all("iframe", "embed", "object"):
        url = _attribute(element, "data" if element.tag == "object" else "src")
        is_pdf = _attribute(element, "type").lower() == "application/pdf"

        if is_pdf or _extension(url) in DOCUMENT_EXTENSIONS:
            yield element


@rule("ECO-GIF", severity=Severity.INFO, reference="RWEB_0099")
def gif_image(document: Document) -> Iterator[Element]:
    """Animated GIFs are much heavier than a video; a GIF may be animated."""
    for img in document.find_all("img"):
        if _extension(_image_url(img)) == ".gif":
            yield img


@rule("ECO-WEB-FONTS", severity=Severity.INFO, reference="RWEB_0032")
def too_many_web_fonts(document: Document) -> Iterator[Violation]:
    """The page should not download more than 2 fonts."""
    at_load = [resource for resource in find_resources(document) if not resource.deferred]
    preloaded = sum(1 for resource in at_load if resource.type is ResourceType.FONT)
    services = sum(
        1
        for resource in at_load
        if resource.type is ResourceType.STYLESHEET and resource.host in FONT_SERVICES
    )
    declared = sum(
        style.text_content().lower().count("@font-face") for style in document.find_all("style")
    )
    fonts = max(preloaded, services, declared)
    if fonts > MAX_FONTS:
        yield Violation(document.root, {"count": fonts, "limit": MAX_FONTS})


@rule("ECO-CANVAS", severity=Severity.INFO, reference="RWEB_0055")
def canvas_element(document: Document) -> Iterator[Element]:
    """A canvas is redrawn by script: HTML and CSS are often enough and lighter."""
    yield from document.find_all("canvas")
