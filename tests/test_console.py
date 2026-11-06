import io
from textwrap import dedent

import pytest

from a11y_eco.models import Finding, Location, Report, Severity
from a11y_eco.reporters.console import render, should_use_color

LANG_MISSING = Finding(
    rule_id="A11Y-LANG-MISSING",
    severity=Severity.ERROR,
    location=Location(line=2, column=1),
    snippet='<html lang="">',
    reference="RGAA 8.3",
)


def test_renders_findings_with_position_title_and_snippet() -> None:
    report = Report(location="page.html", page_size=1234, findings=(LANG_MISSING,))

    assert render(report) == dedent(
        """\
        Audit of page.html (1,234 bytes)

        error    page.html:2:1
                 The default language of the page is not declared [A11Y-LANG-MISSING, RGAA 8.3]
                 <html lang="">

        Summary: 1 error, 0 warnings, 0 info
        """
    )


def test_renders_a_clean_report_without_claiming_full_compliance() -> None:
    report = Report(location="page.html", page_size=10, findings=())
    output = render(report)

    assert "No problem found by the automated checks. A manual audit is still needed." in output
    assert output.endswith("Summary: 0 errors, 0 warnings, 0 info\n")


def test_finding_without_location_shows_the_page_only() -> None:
    finding = Finding(rule_id="A11Y-LANG-MISSING", severity=Severity.ERROR)
    report = Report(location="page.html", page_size=10, findings=(finding,))

    assert "error    page.html\n" in render(report)


def test_long_snippet_is_put_on_one_line_and_shortened() -> None:
    snippet = '<img\n   src="' + "x" * 200 + '">'
    finding = Finding(rule_id="R-1", severity=Severity.INFO, snippet=snippet)
    report = Report(location="page.html", page_size=10, findings=(finding,))
    [snippet_line] = [line for line in render(report).splitlines() if "<img" in line]

    assert snippet_line.strip().startswith('<img src="xxx')
    assert len(snippet_line.strip()) == 80
    assert snippet_line.endswith("…")


def test_unknown_rule_falls_back_to_its_identifier() -> None:
    finding = Finding(rule_id="R-1", severity=Severity.WARNING)
    report = Report(location="page.html", page_size=10, findings=(finding,))

    assert "R-1 [R-1]" in render(report)


def test_colors_wrap_the_padded_label_and_are_off_by_default() -> None:
    report = Report(location="page.html", page_size=10, findings=(LANG_MISSING,))

    assert "\033[" not in render(report)
    assert "\033[1;31merror  \033[0m" in render(report, color=True)


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
