"""Known tools, recognised by the addresses they load or the classes of their markup.

To recognise a new tool, add a Signature to the right list: no rule has to change.
A tool that is not listed is not detected, so the lists need occasional updates.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from a11y_eco.dom import Document, Element


@dataclass(frozen=True, slots=True)
class Signature:
    """How to recognise a tool in a page."""

    name: str
    """Name of the tool, e.g. ``Matomo``."""

    patterns: tuple[str, ...] = ()
    """Regular expressions searched, ignoring case, in the addresses the page loads and
    in its inline scripts, e.g. ``r"static\\.hotjar\\.com/"``."""

    classes: frozenset[str] = frozenset()
    """CSS classes found on the root element of the tool's markup, e.g. ``swiper``."""

    _regex: re.Pattern[str] | None = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        """Compile the patterns once, when the signature is created."""
        regex = re.compile("|".join(self.patterns), re.IGNORECASE) if self.patterns else None
        object.__setattr__(self, "_regex", regex)

    def reveals(self, element: Element, searchable: str) -> bool:
        """Tell whether an element shows that the tool is used.

        Args:
            element: The element.
            searchable: Its addresses and inline code, as built by ``find_tools``.

        Returns:
            True if a pattern or a class matches.
        """
        if self.classes and self.classes & set((element.get("class") or "").split()):
            return True

        return self._regex is not None and self._regex.search(searchable) is not None


ANALYTICS: tuple[Signature, ...] = (
    Signature("Google Analytics", (r"google-analytics\.com/", r"googletagmanager\.com/gtag/js")),
    Signature("Google Tag Manager", (r"googletagmanager\.com/(gtm\.js|ns\.html)",)),
    Signature("Matomo", (r"\b(matomo|piwik)\.(js|php)\b",)),
    Signature("Hotjar", (r"static\.hotjar\.com/",)),
    Signature("Microsoft Clarity", (r"clarity\.ms/tag/",)),
    Signature("Meta Pixel", (r"connect\.facebook\.net/[\w-]+/fbevents\.js", r"facebook\.com/tr\?")),
    Signature("Plausible", (r"plausible\.io/js/",)),
    Signature("Fathom", (r"usefathom\.com/script\.js",)),
    Signature("Mixpanel", (r"cdn\.mxpnl\.com/",)),
    Signature("Segment", (r"cdn\.segment\.com/analytics",)),
)
SOCIAL_BUTTONS: tuple[Signature, ...] = (
    Signature(
        "Facebook", (r"connect\.facebook\.net/[\w-]+/(sdk|all)\.js", r"facebook\.com/plugins/")
    ),
    Signature("X (Twitter)", (r"platform\.twitter\.com/widgets\.js",)),
    Signature("LinkedIn", (r"platform\.linkedin\.com/in\.js",)),
    Signature("Pinterest", (r"assets\.pinterest\.com/js/pinit",)),
    Signature("AddThis", (r"addthis\.com/js/",)),
    Signature("ShareThis", (r"sharethis\.com/js/",)),
    Signature("AddToAny", (r"static\.addtoany\.com/menu/",)),
)
CAROUSELS: tuple[Signature, ...] = (
    Signature("Swiper", classes=frozenset({"swiper", "swiper-container"})),
    Signature("Slick", classes=frozenset({"slick-slider", "slick-carousel"})),
    Signature("Splide", classes=frozenset({"splide"})),
    Signature("Glide", classes=frozenset({"glide"})),
    Signature("Owl Carousel", classes=frozenset({"owl-carousel"})),
    Signature("Bootstrap", classes=frozenset({"carousel"})),
    Signature("Flickity", classes=frozenset({"js-flickity", "flickity-enabled"})),
    Signature("Keen Slider", classes=frozenset({"keen-slider"})),
    Signature("Embla", classes=frozenset({"embla"})),
)
_ADDRESS_ATTRIBUTES = ("src", "href", "data")


def _searchable(element: Element) -> str:
    """The addresses an element loads, and its code if it is an inline script."""
    parts = [element.get(name) or "" for name in _ADDRESS_ATTRIBUTES]

    if element.tag == "script" and not element.has("src"):
        parts.append(element.text_content())

    return " ".join(part for part in parts if part)


def find_tools(document: Document, signatures: tuple[Signature, ...]) -> list[Element]:
    """Return, for each tool used by the page, the first element that reveals it.

    Args:
        document: The parsed page.
        signatures: The tools to look for.

    Returns:
        One element per tool found, in document order.
    """
    found: dict[str, Element] = {}

    for element in document.root.iter():
        searchable = _searchable(element)
        for signature in signatures:
            if signature.name not in found and signature.reveals(element, searchable):
                found[signature.name] = element

    return list(found.values())


def find_elements(document: Document, signatures: tuple[Signature, ...]) -> list[Element]:
    """Return every element that reveals one of the tools, in document order.

    Args:
        document: The parsed page.
        signatures: The tools to look for.

    Returns:
        The matching elements; one tool may appear several times.
    """
    elements = []

    for element in document.root.iter():
        searchable = _searchable(element)
        if any(signature.reveals(element, searchable) for signature in signatures):
            elements.append(element)

    return elements
