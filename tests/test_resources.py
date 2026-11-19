import gc
import weakref

import pytest

from a11y_eco import resources as resources_module
from a11y_eco.dom import Document, parse_html
from a11y_eco.resources import Resource, ResourceType, find_resources, is_external

PAGE = "https://www.example.com/blog/post.html"


def resources(markup: str, url: str | None = PAGE) -> list[Resource]:
    return find_resources(parse_html(markup, url=url))


def summary(markup: str, url: str | None = PAGE) -> list[tuple[str, ResourceType, bool]]:
    """Return (url, type, deferred) for every resource of the markup."""
    return [(r.url, r.type, r.deferred) for r in resources(markup, url)]


@pytest.mark.parametrize(
    ("markup", "expected"),
    [
        pytest.param(
            '<link rel="stylesheet" href="/s.css">',
            [("https://www.example.com/s.css", ResourceType.STYLESHEET, False)],
            id="stylesheet",
        ),
        pytest.param(
            '<link rel="preload" href="/f.woff2" as="font">',
            [("https://www.example.com/f.woff2", ResourceType.FONT, False)],
            id="preloaded-font",
        ),
        pytest.param(
            '<link rel="modulepreload" href="m.js">',
            [("https://www.example.com/blog/m.js", ResourceType.SCRIPT, False)],
            id="modulepreload",
        ),
        pytest.param(
            '<link rel="icon" href="/favicon.svg">',
            [("https://www.example.com/favicon.svg", ResourceType.IMAGE, False)],
            id="icon",
        ),
        pytest.param(
            '<link rel="manifest" href="/app.webmanifest">',
            [("https://www.example.com/app.webmanifest", ResourceType.OTHER, False)],
            id="manifest",
        ),
        pytest.param(
            '<script src="https://cdn.net/lib.js"></script>',
            [("https://cdn.net/lib.js", ResourceType.SCRIPT, False)],
            id="script",
        ),
        pytest.param(
            '<script type="module" src="app.js"></script>',
            [("https://www.example.com/blog/app.js", ResourceType.SCRIPT, False)],
            id="module-script",
        ),
        pytest.param(
            '<img src="a.png" loading="lazy">',
            [("https://www.example.com/blog/a.png", ResourceType.IMAGE, True)],
            id="lazy-image",
        ),
        pytest.param(
            '<img srcset="small.jpg 480w, big.jpg 1080w">',
            [("https://www.example.com/blog/small.jpg", ResourceType.IMAGE, False)],
            id="srcset-counts-once",
        ),
        pytest.param(
            '<input type="image" src="go.png">',
            [("https://www.example.com/blog/go.png", ResourceType.IMAGE, False)],
            id="image-button",
        ),
        pytest.param(
            '<video poster="p.jpg" preload="none">'
            '<source src="v.webm"><source src="v.mp4"></video>',
            [
                ("https://www.example.com/blog/p.jpg", ResourceType.IMAGE, False),
                ("https://www.example.com/blog/v.webm", ResourceType.MEDIA, True),
            ],
            id="video-first-source-on-demand",
        ),
        pytest.param(
            '<audio src="a.mp3" preload="none" autoplay></audio>',
            [("https://www.example.com/blog/a.mp3", ResourceType.MEDIA, False)],
            id="autoplay-is-never-deferred",
        ),
        pytest.param(
            '<iframe src="https://maps.net/embed" loading="lazy"></iframe>',
            [("https://maps.net/embed", ResourceType.FRAME, True)],
            id="lazy-iframe",
        ),
        pytest.param(
            '<object data="doc.pdf"></object>',
            [("https://www.example.com/blog/doc.pdf", ResourceType.FRAME, False)],
            id="object",
        ),
    ],
)
def test_finds_referenced_resources(
    markup: str, expected: list[tuple[str, ResourceType, bool]]
) -> None:
    assert summary(markup) == expected


@pytest.mark.parametrize(
    "markup",
    [
        pytest.param('<link rel="alternate stylesheet" href="dark.css">', id="alternate-css"),
        pytest.param('<link rel="canonical" href="/post">', id="not-a-download"),
        pytest.param('<link rel="stylesheet">', id="no-href"),
        pytest.param("<script>inline()</script>", id="inline-script"),
        pytest.param('<script nomodule src="legacy.js"></script>', id="nomodule"),
        pytest.param('<script type="text/template" src="t.html"></script>', id="not-code"),
        pytest.param('<img src="data:image/png;base64,iVBOR">', id="data-url"),
        pytest.param('<img src="  ">', id="blank-src"),
        pytest.param('<input type="text" src="x.png">', id="not-an-image-button"),
        pytest.param('<a href="/page">Link</a>', id="links-are-not-downloads"),
    ],
)
def test_ignores_what_is_not_downloaded(markup: str) -> None:
    assert resources(markup) == []


def test_same_address_is_counted_once_and_eager_wins() -> None:
    markup = '<img src="a.png" loading="lazy"><img src="/blog/a.png">'

    [resource] = resources(markup)

    assert resource.url == "https://www.example.com/blog/a.png"
    assert resource.deferred is False


def test_base_element_changes_the_resolution_of_relative_urls() -> None:
    markup = '<base href="https://static.example.com/v2/"><img src="a.png">'

    assert resources(markup)[0].url == "https://static.example.com/v2/a.png"


def test_local_file_keeps_relative_urls_as_written() -> None:
    assert summary('<img src="img/a.png">', url=None) == [("img/a.png", ResourceType.IMAGE, False)]


@pytest.mark.parametrize(
    ("url", "page", "expected"),
    [
        pytest.param("https://www.example.com/a.js", PAGE, False, id="same-host"),
        pytest.param("https://cdn.net/a.js", PAGE, True, id="other-host"),
        pytest.param("https://static.example.com/a.js", PAGE, True, id="other-subdomain"),
        pytest.param("a.js", None, False, id="local-relative"),
        pytest.param("https://cdn.net/a.js", None, True, id="local-absolute"),
    ],
)
def test_is_external(url: str, page: str | None, expected: bool) -> None:
    document = parse_html(f'<script src="{url}"></script>', url=page)
    [resource] = find_resources(document)

    assert is_external(resource, document) is expected


def test_page_is_walked_once_per_document(monkeypatch: pytest.MonkeyPatch) -> None:
    walks: list[Document] = []
    real_walk = resources_module._walk

    def counting_walk(document: Document) -> list[Resource]:
        walks.append(document)
        return real_walk(document)

    monkeypatch.setattr(resources_module, "_walk", counting_walk)
    first, second = parse_html('<img src="a.png">'), parse_html('<img src="a.png">')
    find_resources(first)
    find_resources(first)
    find_resources(second)

    assert walks == [first, second]


def test_changing_the_returned_list_does_not_change_the_cache() -> None:
    document = parse_html('<img src="a.png" alt="">', url=PAGE)
    find_resources(document).clear()

    assert len(find_resources(document)) == 1


def test_cache_does_not_keep_documents_alive() -> None:
    document = parse_html('<img src="a.png" alt="">')
    find_resources(document)
    reference = weakref.ref(document)

    del document
    gc.collect()

    assert reference() is None


@pytest.mark.parametrize(
    ("markup", "expected"),
    [
        pytest.param(
            "<style>@import url(theme.css);</style>",
            [("https://www.example.com/blog/theme.css", ResourceType.STYLESHEET, False)],
            id="style-import",
        ),
        pytest.param(
            "<div style=\"background-image: url('/img/banner.jpg')\"></div>",
            [("https://www.example.com/img/banner.jpg", ResourceType.IMAGE, False)],
            id="style-attribute",
        ),
        pytest.param(
            "<style>@font-face { font-family: Inter; src: url(/fonts/inter.woff2); }</style>",
            [("https://www.example.com/fonts/inter.woff2", ResourceType.FONT, True)],
            id="font-face-on-demand",
        ),
    ],
)
def test_finds_resources_in_the_css_of_the_page(
    markup: str, expected: list[tuple[str, ResourceType, bool]]
) -> None:
    assert summary(markup) == expected


@pytest.mark.parametrize(
    "markup",
    [
        pytest.param("<style>.hero { background: url(hero.jpg); }</style>", id="selector"),
        pytest.param('<div hidden style="background: url(a.png)"></div>', id="hidden"),
        pytest.param('<div hidden><p style="background: url(a.png)"></p></div>', id="in-hidden"),
        pytest.param('<p style="background: url(data:image/png;base64,iVBOR)"></p>', id="data"),
    ],
)
def test_css_references_that_may_not_load_are_left_out(markup: str) -> None:
    assert resources(markup) == []


def test_image_of_a_style_attribute_is_counted_once_with_the_same_img() -> None:
    markup = '<img src="a.png"><div style="background: url(a.png)"></div>'

    assert summary(markup) == [("https://www.example.com/blog/a.png", ResourceType.IMAGE, False)]
