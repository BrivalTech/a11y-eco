import pytest

from a11y_eco.css import CssReferences, read_css


@pytest.mark.parametrize(
    ("css", "imports"),
    [
        pytest.param('@import url("theme.css");', ("theme.css",), id="url-double-quotes"),
        pytest.param("@import url('theme.css');", ("theme.css",), id="url-single-quotes"),
        pytest.param("@import url(theme.css);", ("theme.css",), id="url-unquoted"),
        pytest.param('@import "theme.css";', ("theme.css",), id="string"),
        pytest.param("@IMPORT 'print.css' print;", ("print.css",), id="media-and-case"),
        pytest.param('@import "a.css"; @import "b.css";', ("a.css", "b.css"), id="several"),
    ],
)
def test_imports(css: str, imports: tuple[str, ...]) -> None:
    assert read_css(css).imports == imports


def test_font_faces_keep_the_first_source_of_each_font() -> None:
    css = """
        @font-face { font-family: Inter; src: url(inter.woff2) format("woff2"),
                                              url(inter.woff) format("woff"); }
        @font-face { font-family: Local; src: local("Arial"); }
        @font-face { font-family: Serif; src: url("serif.woff2"); }
    """

    assert read_css(css).font_faces == ("inter.woff2", "serif.woff2")


def test_other_urls_exclude_imports_and_fonts() -> None:
    css = """
        @import url(theme.css);
        @font-face { font-family: Inter; src: url(inter.woff2); }
        .hero { background: #fff url( "hero.jpg" ) no-repeat; }
        .icon { mask-image: url(icon.svg); }
    """

    assert read_css(css) == CssReferences(
        imports=("theme.css",), font_faces=("inter.woff2",), urls=("hero.jpg", "icon.svg")
    )


@pytest.mark.parametrize(
    "css",
    [
        pytest.param("/* @import url(old.css); */", id="import-in-comment"),
        pytest.param(".a { background: /* url(old.png) */ red; }", id="url-in-comment"),
        pytest.param('.a::before { content: "url(not-a-file.png)"; }', id="url-in-string"),
        pytest.param(".a { background: url(); }", id="empty-url"),
        pytest.param("", id="empty-css"),
    ],
)
def test_text_that_only_looks_like_a_reference_is_ignored(css: str) -> None:
    assert read_css(css) == CssReferences()


def test_comment_markers_inside_strings_are_text() -> None:
    css = '.a::before { content: "/*"; } .b { background: url(b.png); } /* "*/'

    assert read_css(css).urls == ("b.png",)


def test_style_attribute_declarations_are_read_too() -> None:
    assert read_css("background-image: url('banner.jpg'); color: red").urls == ("banner.jpg",)


def test_escaped_characters_are_unescaped() -> None:
    assert read_css(r".a { background: url(a\(1\).png); }").urls == ("a(1).png",)


def test_unclosed_comment_hides_the_rest() -> None:
    assert read_css(".a { background: url(a.png); } /* .b { background: url(b.png); }").urls == (
        "a.png",
    )
