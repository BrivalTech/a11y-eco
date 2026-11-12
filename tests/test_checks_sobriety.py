import pytest

from a11y_eco.checks import sobriety
from a11y_eco.checks.base import Rule
from a11y_eco.dom import parse_html

PAGE = "https://www.example.com/"


def details(rule: Rule, markup: str) -> list[dict[str, int]]:
    """Return the details of every finding of a rule on a web page."""
    return [dict(f.details) for f in rule.run(parse_html(markup, url=PAGE))]


def images(count: int, *, lazy: bool = False) -> str:
    loading = ' loading="lazy"' if lazy else ""

    return "".join(f'<img src="/{i}.png" alt=""{loading}>' for i in range(count))


def stylesheets(count: int) -> str:
    return "".join(f'<link rel="stylesheet" href="/{i}.css">' for i in range(count))


def scripts_from(hosts: int) -> str:
    return "".join(f'<script src="https://cdn{i}.example.net/a.js"></script>' for i in range(hosts))


@pytest.mark.parametrize(
    ("markup", "expected"),
    [
        pytest.param(images(39), [], id="40-requests-is-the-limit"),
        pytest.param(images(40), [{"count": 41, "limit": 40}], id="41-requests"),
        pytest.param(images(30) + images(30, lazy=True), [], id="lazy-images-not-counted"),
    ],
)
def test_too_many_requests(markup: str, expected: list[dict[str, int]]) -> None:
    assert details(sobriety.too_many_requests, markup) == expected


@pytest.mark.parametrize(
    ("markup", "expected"),
    [
        pytest.param(stylesheets(10), [], id="10-is-the-limit"),
        pytest.param(stylesheets(11), [{"count": 11, "limit": 10}], id="11-stylesheets"),
        pytest.param(
            stylesheets(10) + '<link rel="stylesheet" href="/0.css">', [], id="same-file-twice"
        ),
    ],
)
def test_too_many_stylesheets(markup: str, expected: list[dict[str, int]]) -> None:
    assert details(sobriety.too_many_stylesheets, markup) == expected


@pytest.mark.parametrize(
    ("markup", "expected"),
    [
        pytest.param(scripts_from(4), [], id="page-and-4-hosts-is-the-limit"),
        pytest.param(scripts_from(5), [{"count": 6, "limit": 5}], id="page-and-5-hosts"),
    ],
)
def test_too_many_domains(markup: str, expected: list[dict[str, int]]) -> None:
    assert details(sobriety.too_many_domains, markup) == expected


LARGE_CSS = "<style>" + "a{color:red}" * 100 + "</style>"  # 1,200 bytes
LARGE_JS = "<script>" + "f();" * 300 + "</script>"  # 1,200 bytes


@pytest.mark.parametrize(
    ("markup", "expected"),
    [
        pytest.param(LARGE_CSS + LARGE_JS, [], id="2-large-blocks-is-the-limit"),
        pytest.param(LARGE_CSS * 2 + LARGE_JS, [{"count": 3, "limit": 2}], id="3-large-blocks"),
        pytest.param(LARGE_CSS + LARGE_JS + "<style>p{}</style>" * 5, [], id="small-blocks"),
        pytest.param(
            LARGE_CSS * 2 + '<script type="application/ld+json">' + "{}" * 600 + "</script>",
            [],
            id="json-ld-is-data",
        ),
        pytest.param(
            LARGE_CSS * 2 + '<script src="a.js">' + "f();" * 300 + "</script>",
            [],
            id="external-script",
        ),
    ],
)
def test_too_much_inline_code(markup: str, expected: list[dict[str, int]]) -> None:
    assert details(sobriety.too_much_inline_code, markup) == expected


def test_page_level_findings_have_no_location() -> None:
    [finding] = sobriety.too_many_stylesheets.run(parse_html(stylesheets(11)))

    assert finding.location is None
    assert finding.reference == "RWEB_0035"
