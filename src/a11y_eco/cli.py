"""Command-line interface.

This module only handles arguments, output streams and exit codes. The work itself
is done by the loader, the audit and the reporters, which can all be used and
tested without going through the command line.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from enum import IntEnum

from a11y_eco import __version__
from a11y_eco.audit import audit
from a11y_eco.i18n import CATALOGS, Language, detect_language
from a11y_eco.loader import LoadError, load
from a11y_eco.models import Severity
from a11y_eco.reporters.console import render, should_use_color

PROG = "a11y-eco"

FAIL_ON_CHOICES = [*(severity.value for severity in reversed(Severity)), "never"]
AUDIT_EPILOG = """\
exit status:
  0  no finding reaches the --fail-on severity
  1  at least one finding reaches the --fail-on severity
  2  invalid arguments, or the page could not be loaded
"""


class ExitCode(IntEnum):
    """Process exit codes, designed to be usable in CI pipelines."""

    OK = 0
    FINDINGS = 1
    USAGE_ERROR = 2


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser.

    Returns:
        The configured top-level parser.
    """
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="Audit a web page for accessibility and eco-design issues.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command", title="commands")

    audit_parser = commands.add_parser(
        "audit",
        help="audit a web page",
        description="Audit a web page and print the problems found.",
        epilog=AUDIT_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    audit_parser.add_argument("target", help="URL (http or https) or path of an HTML file")
    audit_parser.add_argument(
        "--fail-on",
        choices=FAIL_ON_CHOICES,
        default=Severity.ERROR.value,
        help="lowest severity that makes the command fail (default: %(default)s)",
    )
    audit_parser.add_argument(
        "--timeout",
        type=_positive_float,
        default=10.0,
        metavar="SECONDS",
        help="network timeout when auditing a URL (default: %(default)s)",
    )
    audit_parser.add_argument(
        "--lang",
        choices=[language.value for language in Language],
        help="language of the report (default: the language of the system, otherwise fr)",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command-line interface.

    Args:
        argv: Arguments to parse, without the program name. Defaults to ``sys.argv[1:]``.

    Returns:
        The process exit code.
    """
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "audit":
        language = Language(args.lang) if args.lang else detect_language()
        return _run_audit(
            args.target, fail_on=args.fail_on, timeout=args.timeout, language=language
        )
    parser.print_help()
    return ExitCode.OK


def _run_audit(target: str, *, fail_on: str, timeout: float, language: Language) -> ExitCode:
    try:
        source = load(target, timeout=timeout)
    except LoadError as error:
        # Same format as argparse errors; stdout stays reserved for the report.
        print(f"{PROG}: error: {error}", file=sys.stderr)
        return ExitCode.USAGE_ERROR

    report = audit(source)
    catalog = CATALOGS[language]
    sys.stdout.write(render(report, catalog, color=should_use_color(sys.stdout)))

    if fail_on != "never" and report.reaches(Severity(fail_on)):
        return ExitCode.FINDINGS
    return ExitCode.OK


def _positive_float(value: str) -> float:
    """Convert an argument to a strictly positive number, for argparse."""
    try:
        number = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value!r} is not a number") from None
    if number <= 0:
        raise argparse.ArgumentTypeError(f"{value!r} must be greater than 0")
    return number
