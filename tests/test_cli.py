import runpy
import sys

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
