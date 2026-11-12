import pytest

from a11y_eco.checks import media
from a11y_eco.checks.base import Rule
from a11y_eco.dom import parse_html

PAGE = "https://www.example.com/"


def snippets(rule: Rule, markup: str) -> list[str]:
    return [f.snippet for f in rule.run(parse_html(markup, url=PAGE))]


@pytest.mark.parametrize(
    ("markup", "expected"),
    [
        pytest.param('<video src="v.mp4" preload="none" controls>', [], id="on-demand"),
        pytest.param('<audio src="a.mp3" preload="NONE">', [], id="case-insensitive"),
        pytest.param('<video src="v.mp4">', ['<video src="v.mp4">'], id="default-preload"),
        pytest.param(
            '<video src="v.mp4" preload="metadata">',
            ['<video src="v.mp4" preload="metadata">'],
            id="metadata",
        ),
        pytest.param(
            '<audio src="a.mp3" preload="none" autoplay>',
            ['<audio src="a.mp3" preload="none" autoplay>'],
            id="autoplay-wins",
        ),
    ],
)
def test_media_loaded_automatically(markup: str, expected: list[str]) -> None:
    assert snippets(media.media_loaded_automatically, markup) == expected


@pytest.mark.parametrize(
    ("markup", "expected"),
    [
        pytest.param('<img src="hero.jpg" alt="">', [], id="first-image-is-free"),
        pytest.param(
            '<img src="1.jpg" alt=""><img src="2.jpg" alt="" loading="lazy">', [], id="lazy"
        ),
        pytest.param(
            '<img src="1.jpg" alt=""><img src="2.jpg" alt="">',
            ['<img src="2.jpg" alt="">'],
            id="second-image",
        ),
        pytest.param(
            '<iframe src="a.html"></iframe><img src="1.jpg" alt="">',
            [],
            id="first-of-each-kind-is-free",
        ),
        pytest.param(
            '<iframe src="a.html"></iframe><iframe src="b.html"></iframe>',
            ['<iframe src="b.html">'],
            id="second-frame",
        ),
        pytest.param(
            '<img src="data:image/png;base64,AA" alt=""><img src="1.jpg" alt="">',
            [],
            id="data-url-is-not-a-download",
        ),
    ],
)
def test_missing_lazy_loading(markup: str, expected: list[str]) -> None:
    assert snippets(media.missing_lazy_loading, markup) == expected


@pytest.mark.parametrize(
    ("markup", "expected"),
    [
        pytest.param('<iframe src="/docs/Report.PDF?v=2"></iframe>', 1, id="pdf-in-iframe"),
        pytest.param('<embed src="slides.pptx">', 1, id="office-file-in-embed"),
        pytest.param('<object data="doc.odt"></object>', 1, id="object"),
        pytest.param('<embed src="/viewer" type="application/pdf">', 1, id="pdf-type"),
        pytest.param('<iframe src="https://maps.example.com/"></iframe>', 0, id="map"),
        pytest.param('<a href="report.pdf">Report (PDF)</a>', 0, id="link-is-the-good-way"),
    ],
)
def test_document_displayed_in_page(markup: str, expected: int) -> None:
    assert len(snippets(media.document_displayed_in_page, markup)) == expected


def test_gif_images_are_reported() -> None:
    markup = '<img src="a.gif" alt=""><img src="b.webp" alt=""><img srcset="c.GIF 2x" alt="">'

    assert snippets(media.gif_image, markup) == [
        '<img src="a.gif" alt="">',
        '<img srcset="c.GIF 2x" alt="">',
    ]


def test_every_canvas_is_reported() -> None:
    assert snippets(media.canvas_element, '<canvas id="chart"></canvas><div></div>') == [
        '<canvas id="chart">'
    ]


def font_preloads(count: int) -> str:
    return "".join(
        f'<link rel="preload" as="font" href="/f{i}.woff2" crossorigin>' for i in range(count)
    )


def font_faces(count: int) -> str:
    return "<style>" + "@font-face{font-family:F;src:url(f.woff2)}" * count + "</style>"


GOOGLE_FONTS = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter">'


@pytest.mark.parametrize(
    ("markup", "expected"),
    [
        pytest.param(font_preloads(2), [], id="2-fonts-is-the-limit"),
        pytest.param(font_preloads(3), [{"count": 3, "limit": 2}], id="3-preloaded-fonts"),
        pytest.param(font_faces(3), [{"count": 3, "limit": 2}], id="3-font-faces"),
        pytest.param(
            font_preloads(2) + font_faces(2) + GOOGLE_FONTS, [], id="counts-are-not-added-up"
        ),
    ],
)
def test_too_many_web_fonts(markup: str, expected: list[dict[str, int]]) -> None:
    findings = media.too_many_web_fonts.run(parse_html(markup, url=PAGE))

    assert [dict(f.details) for f in findings] == expected
