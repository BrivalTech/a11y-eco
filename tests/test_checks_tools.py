from a11y_eco.checks import tools
from a11y_eco.dom import parse_html

GA4 = '<script src="https://www.googletagmanager.com/gtag/js?id=G-1"></script>'
HOTJAR = '<script src="https://static.hotjar.com/c/hotjar-1.js"></script>'
CLARITY = "<script>t.src='https://www.clarity.ms/tag/'+i;</script>"


def test_one_analytics_tool_is_the_limit() -> None:
    assert tools.too_many_analytics.run(parse_html(GA4 + GA4)) == []


def test_every_analytics_tool_is_reported_beyond_the_limit() -> None:
    findings = tools.too_many_analytics.run(parse_html(GA4 + HOTJAR + CLARITY))

    assert [f.snippet for f in findings] == [
        '<script src="https://www.googletagmanager.com/gtag/js?id=G-1">',
        '<script src="https://static.hotjar.com/c/hotjar-1.js">',
        "<script>",
    ]
    assert {tuple(f.details.items()) for f in findings} == {(("count", 3), ("limit", 1))}


def test_every_official_social_script_is_reported() -> None:
    markup = (
        '<script src="https://platform.twitter.com/widgets.js"></script>'
        '<iframe src="https://www.facebook.com/plugins/like.php?href=x"></iframe>'
        '<a href="https://www.linkedin.com/sharing/share-offsite/?url=x">Share</a>'
    )

    findings = tools.official_social_buttons.run(parse_html(markup))

    assert [f.snippet[:30] for f in findings] == [
        '<script src="https://platform.',
        '<iframe src="https://www.faceb',
    ]


def test_carousels_beyond_the_first_are_reported() -> None:
    markup = (
        '<div class="swiper"><div class="swiper-wrapper"></div></div>'
        '<div id="news" class="carousel slide"></div>'
        '<section class="splide"></section>'
    )

    findings = tools.too_many_carousels.run(parse_html(markup))

    assert [f.snippet for f in findings] == [
        '<div id="news" class="carousel slide">',
        '<section class="splide">',
    ]
    assert dict(findings[0].details) == {"count": 3, "limit": 1}


def test_one_carousel_is_the_limit() -> None:
    assert tools.too_many_carousels.run(parse_html('<div class="swiper"></div>')) == []
