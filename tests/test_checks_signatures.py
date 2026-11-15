import pytest

from a11y_eco.checks.signatures import (
    ANALYTICS,
    CAROUSELS,
    SOCIAL_BUTTONS,
    Signature,
    find_elements,
    find_tools,
)
from a11y_eco.dom import parse_html

ALL_LISTS = {"analytics": ANALYTICS, "social": SOCIAL_BUTTONS, "carousels": CAROUSELS}
HOTJAR = Signature("Hotjar", (r"static\.hotjar\.com/",))
SWIPER = Signature("Swiper", classes=frozenset({"swiper"}))


def tags(markup: str, signatures: tuple[Signature, ...]) -> list[str]:
    return [element.start_tag for element in find_tools(parse_html(markup), signatures)]


@pytest.mark.parametrize("signatures", ALL_LISTS.values(), ids=ALL_LISTS.keys())
def test_every_signature_can_match_something(signatures: tuple[Signature, ...]) -> None:
    assert all(signature.patterns or signature.classes for signature in signatures)


@pytest.mark.parametrize("signatures", ALL_LISTS.values(), ids=ALL_LISTS.keys())
def test_tool_names_are_unique(signatures: tuple[Signature, ...]) -> None:
    names = [signature.name for signature in signatures]

    assert len(names) == len(set(names))


@pytest.mark.parametrize(
    ("markup", "found"),
    [
        pytest.param('<script src="https://static.hotjar.com/c/h.js"></script>', True, id="src"),
        pytest.param('<script src="HTTPS://STATIC.HOTJAR.COM/c/h.js"></script>', True, id="case"),
        pytest.param('<script>load("//static.hotjar.com/c/h.js")</script>', True, id="inline"),
        pytest.param('<a href="https://static.hotjar.com/">Hotjar</a>', True, id="link-href"),
        pytest.param("<p>We use static.hotjar.com</p>", False, id="plain-text-ignored"),
        pytest.param('<script src="https://hotjar.example.com/h.js"></script>', False, id="other"),
    ],
)
def test_patterns_are_searched_in_addresses_and_inline_scripts(markup: str, found: bool) -> None:
    assert bool(tags(markup, (HOTJAR,))) is found


@pytest.mark.parametrize(
    ("markup", "found"),
    [
        pytest.param('<div class="swiper hero">', True, id="class-token"),
        pytest.param('<div class="swiper-wrapper">', False, id="other-class-sharing-a-prefix"),
        pytest.param('<div id="swiper">', False, id="id-is-not-a-class"),
    ],
)
def test_classes_are_matched_as_whole_tokens(markup: str, found: bool) -> None:
    assert bool(tags(markup, (SWIPER,))) is found


def test_find_tools_reports_each_tool_once_with_its_first_element() -> None:
    markup = (
        '<script src="https://static.hotjar.com/a.js"></script>'
        '<script src="https://static.hotjar.com/b.js"></script>'
    )

    assert tags(markup, (HOTJAR,)) == ['<script src="https://static.hotjar.com/a.js">']


def test_find_elements_reports_every_occurrence() -> None:
    document = parse_html('<div class="swiper"></div><p></p><div class="swiper"></div>')

    assert len(find_elements(document, (SWIPER,))) == 2


@pytest.mark.parametrize(
    ("markup", "tool"),
    [
        pytest.param(
            '<script async src="https://www.googletagmanager.com/gtag/js?id=G-1"></script>',
            "Google Analytics",
            id="ga4",
        ),
        pytest.param(
            "<script>(function(w,d,s,l,i){j.src='https://www.googletagmanager.com/gtm.js?id='+i;"
            "})(window,document,'script','dataLayer','GTM-1');</script>",
            "Google Tag Manager",
            id="gtm-inline",
        ),
        pytest.param(
            "<script>var u='//stats.example.org/';_paq.push(['setTrackerUrl', u+'matomo.php']);"
            "</script>",
            "Matomo",
            id="matomo-self-hosted",
        ),
        pytest.param(
            '<script src="https://connect.facebook.net/en_US/fbevents.js"></script>',
            "Meta Pixel",
            id="meta-pixel",
        ),
    ],
)
def test_recognises_real_analytics_snippets(markup: str, tool: str) -> None:
    document = parse_html(markup)

    assert [s.name for s in ANALYTICS if find_tools(document, (s,))] == [tool]


def test_facebook_sdk_is_a_social_button_but_not_an_analytics_tool() -> None:
    document = parse_html('<script src="https://connect.facebook.net/fr_FR/sdk.js"></script>')

    assert len(find_tools(document, SOCIAL_BUTTONS)) == 1
    assert find_tools(document, ANALYTICS) == []
