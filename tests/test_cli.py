import runpy
import sys
from pathlib import Path

import pytest

from a11y_eco import __version__
from a11y_eco.cli import PROG, ExitCode, main


def test_version_flag_prints_version_and_exits_ok(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])

    assert exc_info.value.code == ExitCode.OK
    assert capsys.readouterr().out.strip() == f"{PROG} {__version__}"


def test_no_arguments_prints_help(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main([])

    assert exit_code == ExitCode.OK
    assert f"usage: {PROG}" in capsys.readouterr().out


def test_unknown_option_is_a_usage_error(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--does-not-exist"])

    assert exc_info.value.code == ExitCode.USAGE_ERROR

    captured = capsys.readouterr()

    assert captured.out == ""
    assert "unrecognized arguments" in captured.err


def test_package_runs_as_module(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "argv", ["a11y-eco", "--version"])

    with pytest.raises(SystemExit) as exc_info:
        runpy.run_module("a11y_eco", run_name="__main__")

    assert exc_info.value.code == ExitCode.OK
    assert capsys.readouterr().out.strip() == f"{PROG} {__version__}"


def test_exit_codes_are_stable() -> None:
    assert (ExitCode.OK, ExitCode.FINDINGS, ExitCode.USAGE_ERROR) == (0, 1, 2)


@pytest.fixture
def page_without_lang(tmp_path: Path) -> str:
    page = tmp_path / "page.html"
    page.write_text("<!DOCTYPE html>\n<html><p>Bonjour</p></html>", encoding="utf-8")

    return str(page)


@pytest.fixture
def clean_page(tmp_path: Path) -> str:
    page = tmp_path / "clean.html"
    page.write_text('<!DOCTYPE html>\n<html lang="fr"><p>Bonjour</p></html>', encoding="utf-8")

    return str(page)


def test_audit_of_a_clean_page_succeeds(
    clean_page: str, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = main(["audit", clean_page])
    output = capsys.readouterr().out

    assert exit_code == ExitCode.OK
    assert f"Audit of {clean_page}" in output
    assert "No problem found" in output


def test_audit_reports_findings_and_fails(
    page_without_lang: str, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = main(["audit", page_without_lang])
    output = capsys.readouterr().out

    assert exit_code == ExitCode.FINDINGS
    assert f"{page_without_lang}:2:1" in output
    assert "A11Y-LANG-MISSING" in output
    assert "\033[" not in output  # captured output is not a terminal: no colours


@pytest.mark.parametrize(
    ("fail_on", "expected"),
    [
        ("error", ExitCode.FINDINGS),
        ("warning", ExitCode.FINDINGS),
        ("info", ExitCode.FINDINGS),
        ("never", ExitCode.OK),
    ],
)
def test_fail_on_sets_the_failure_threshold(
    page_without_lang: str, fail_on: str, expected: ExitCode
) -> None:
    assert main(["audit", page_without_lang, "--fail-on", fail_on]) == expected


def test_unreadable_page_is_reported_on_stderr(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = main(["audit", str(tmp_path / "missing.html")])
    captured = capsys.readouterr()

    assert exit_code == ExitCode.USAGE_ERROR
    assert captured.out == ""
    assert captured.err.startswith(f"{PROG}: error: cannot read")


@pytest.mark.parametrize(
    ("arguments", "message"),
    [
        (["--timeout", "0"], "must be greater than 0"),
        (["--timeout", "soon"], "is not a number"),
        (["--fail-on", "critical"], "invalid choice"),
    ],
)
def test_invalid_options_are_usage_errors(
    clean_page: str,
    arguments: list[str],
    message: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["audit", clean_page, *arguments])

    assert exc_info.value.code == ExitCode.USAGE_ERROR
    assert message in capsys.readouterr().err


def test_audit_help_documents_exit_status(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        main(["audit", "--help"])

    assert "exit status:" in capsys.readouterr().out
