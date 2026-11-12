import io
from textwrap import dedent

import pytest

from a11y_eco.i18n import CATALOGS, Catalog, Language
from a11y_eco.models import Finding, Location, Metrics, Report, ResourceType, Severity
from a11y_eco.reporters.console import render, should_use_color

EN = CATALOGS[Language.EN]
FR = CATALOGS[Language.FR]
LANG_MISSING = Finding(
    rule_id="A11Y-LANG-MISSING",
    severity=Severity.ERROR,
    location=Location(line=2, column=1),
    snippet='<html lang="">',
    reference="RGAA 8.3",
)


def test_renders_findings_with_position_title_and_snippet() -> None:
    report = Report(location="page.html", page_size=1234, findings=(LANG_MISSING,))

    assert render(report, EN) == dedent(
        """\
        Audit of page.html (1,234 bytes)

        error    page.html:2:1
                 The default language of the page is not declared [A11Y-LANG-MISSING, RGAA 8.3]
                 <html lang="">

        Summary: 1 error, 0 warnings, 0 info
        """
    )


def test_renders_the_sobriety_measures_before_the_findings() -> None:
    metrics = Metrics(
        requests=1234,
        resources_by_type={ResourceType.SCRIPT: 2, ResourceType.STYLESHEET: 1},
        deferred=3,
        external=1,
        domains=2,
        dom_elements=812,
    )
    report = Report(location="page.html", page_size=10, findings=(), metrics=metrics)
    lines = render(report, EN).splitlines()

    assert lines[2:10] == [
        "Sobriety (minimum values, read from the HTML only)",
        "  Requests when the page loads: at least 1,234",
        "  Resources: 1 stylesheet, 2 scripts",  # always in the same order
        "  Loaded on demand: 3",
        "  From another host: 1",
        "  Domains: 2",
        "  DOM elements: 812",
        "",
    ]


def test_page_without_resources_says_none() -> None:
    report = Report(location="p.html", page_size=10, findings=(), metrics=Metrics(requests=1))

    assert "  Ressources\N{NO-BREAK SPACE}: aucune" in render(report, FR).splitlines()


def test_report_without_measures_has_no_sobriety_section() -> None:
    report = Report(location="page.html", page_size=10, findings=())

    assert "Sobriety" not in render(report, EN)


def test_renders_a_clean_report_without_claiming_full_compliance() -> None:
    report = Report(location="page.html", page_size=10, findings=())
    output = render(report, EN)

    assert "No problem found by the automated checks. A manual audit is still needed." in output
    assert output.endswith("Summary: 0 errors, 0 warnings, 0 info\n")


def test_finding_without_location_shows_the_page_only() -> None:
    finding = Finding(rule_id="A11Y-LANG-MISSING", severity=Severity.ERROR)
    report = Report(location="page.html", page_size=10, findings=(finding,))

    assert "error    page.html\n" in render(report, EN)


def test_long_snippet_is_put_on_one_line_and_shortened() -> None:
    snippet = '<img\n   src="' + "x" * 200 + '">'
    finding = Finding(rule_id="R-1", severity=Severity.INFO, snippet=snippet)
    report = Report(location="page.html", page_size=10, findings=(finding,))
    [snippet_line] = [line for line in render(report, EN).splitlines() if "<img" in line]

    assert snippet_line.strip().startswith('<img src="xxx')
    assert len(snippet_line.strip()) == 80
    assert snippet_line.endswith("…")


@pytest.mark.parametrize(
    ("catalog", "expected"),
    [
        (EN, "At least 1,234 requests when the page loads (recommended maximum: 40)"),
        (
            FR,
            "Au moins 1\N{NARROW NO-BREAK SPACE}234 requêtes au chargement "
            "(maximum recommandé\N{NO-BREAK SPACE}: 40)",
        ),
    ],
    ids=["en", "fr"],
)
def test_title_shows_the_details_of_the_finding(catalog: Catalog, expected: str) -> None:
    finding = Finding(
        rule_id="ECO-REQUESTS",
        severity=Severity.WARNING,
        reference="RWEB_0047",
        details={"count": 1234, "limit": 40},
    )
    report = Report(location="page.html", page_size=10, findings=(finding,))

    assert f"{expected} [ECO-REQUESTS, RWEB_0047]" in render(report, catalog)


def test_unknown_rule_falls_back_to_its_identifier() -> None:
    finding = Finding(rule_id="R-1", severity=Severity.WARNING)
    report = Report(location="page.html", page_size=10, findings=(finding,))

    assert "R-1 [R-1]" in render(report, EN)


def test_colors_wrap_the_padded_label_and_are_off_by_default() -> None:
    report = Report(location="page.html", page_size=10, findings=(LANG_MISSING,))

    assert "\033[" not in render(report, EN)
    assert "\033[1;31merror  \033[0m" in render(report, EN, color=True)


class FakeTerminal(io.StringIO):
    def isatty(self) -> bool:
        return True


@pytest.mark.parametrize(
    ("stream", "environ", "expected"),
    [
        pytest.param(FakeTerminal(), {}, True, id="terminal"),
        pytest.param(io.StringIO(), {}, False, id="redirected-to-file-or-pipe"),
        pytest.param(FakeTerminal(), {"NO_COLOR": "1"}, False, id="no-color"),
        pytest.param(FakeTerminal(), {"NO_COLOR": ""}, True, id="empty-no-color-is-ignored"),
    ],
)
def test_should_use_color(stream: io.StringIO, environ: dict[str, str], expected: bool) -> None:
    assert should_use_color(stream, environ) is expected


def test_renders_the_report_in_french() -> None:
    link = Finding(
        rule_id="A11Y-LINK-NAME",
        severity=Severity.ERROR,
        location=Location(line=8, column=3),
        snippet='<a href="/">',
        reference="RGAA 6.2",
    )
    report = Report(location="page.html", page_size=1234, findings=(link,))

    assert render(report, FR) == dedent(
        """\
        Audit de page.html (1\N{NARROW NO-BREAK SPACE}234 octets)

        erreur         page.html:8:3
                       Lien sans intitulé [A11Y-LINK-NAME, RGAA 6.2]
                       <a href="/">

        Résumé\N{NO-BREAK SPACE}: 1 erreur, 0 avertissement, 0 info
        """
    )
