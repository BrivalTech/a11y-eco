"""Command-line interface.

This module only handles arguments, output streams and exit codes. The work itself
is done by the loader, the audit and the reporters, which can all be used and
tested without going through the command line.

Texts written by this module come from the catalogs. The details of argparse's
own error messages ("invalid choice", "unrecognized arguments"…) stay in English:
argparse only translates them through gettext, which this tool does not use.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable, Sequence
from enum import IntEnum
from typing import Any, NoReturn

from a11y_eco import __version__
from a11y_eco.audit import audit
from a11y_eco.i18n import CATALOGS, Catalog, Language, detect_language
from a11y_eco.loader import LoadError, load
from a11y_eco.models import Severity
from a11y_eco.reporters.console import render, should_use_color

PROG = "a11y-eco"
FAIL_ON_CHOICES = [*(severity.value for severity in reversed(Severity)), "never"]
LANGUAGE_CHOICES = [language.value for language in Language]


class ExitCode(IntEnum):
    """Process exit codes, designed to be usable in CI pipelines."""

    OK = 0
    FINDINGS = 1
    USAGE_ERROR = 2


class _Parser(argparse.ArgumentParser):
    """An argument parser whose own messages come from a catalog."""

    def __init__(self, *, catalog: Catalog, **kwargs: Any) -> None:
        super().__init__(allow_abbrev=False, add_help=False, **kwargs)
        self.catalog = catalog

    def error(self, message: str) -> NoReturn:
        """Print the usage and a translated error, then exit with a usage error."""
        self.print_usage(sys.stderr)
        error = self.catalog.text("cli.error", prog=self.prog, message=message)
        self.exit(ExitCode.USAGE_ERROR, error + "\n")


def build_parser(catalog: Catalog) -> argparse.ArgumentParser:
    """Build the argument parser, with help texts in the language of the catalog.

    Args:
        catalog: The messages of the language to write in.

    Returns:
        The configured top-level parser.
    """
    text = catalog.text
    parser = _Parser(prog=PROG, description=text("cli.description"), catalog=catalog)
    options = parser.add_argument_group(text("cli.options"))
    options.add_argument("-h", "--help", action="help", help=text("cli.help"))
    options.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}", help=text("cli.version")
    )
    commands = parser.add_subparsers(dest="command", title=text("cli.commands"))
    audit_parser = commands.add_parser(
        "audit",
        help=text("cli.audit.help"),
        description=text("cli.audit.description"),
        epilog=text("cli.audit.epilog"),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        catalog=catalog,
    )
    arguments = audit_parser.add_argument_group(text("cli.arguments"))
    arguments.add_argument("target", help=text("cli.audit.target"))
    options = audit_parser.add_argument_group(text("cli.options"))
    options.add_argument("-h", "--help", action="help", help=text("cli.help"))
    options.add_argument(
        "--fail-on",
        choices=FAIL_ON_CHOICES,
        default=Severity.ERROR.value,
        help=text("cli.audit.fail_on"),
    )
    options.add_argument("--lang", choices=LANGUAGE_CHOICES, help=text("cli.audit.lang"))
    options.add_argument(
        "--timeout",
        type=_positive_number(catalog),
        default=10.0,
        metavar="SECONDS",
        help=text("cli.audit.timeout"),
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command-line interface.

    Args:
        argv: Arguments to parse, without the program name. Defaults to ``sys.argv[1:]``.

    Returns:
        The process exit code.
    """
    arguments = list(sys.argv[1:] if argv is None else argv)
    catalog = CATALOGS[_requested_language(arguments)]
    parser = build_parser(catalog)
    args = parser.parse_args(arguments)
    if args.command == "audit":
        return _run_audit(args.target, fail_on=args.fail_on, timeout=args.timeout, catalog=catalog)
    parser.print_help()

    return ExitCode.OK


def _requested_language(arguments: Sequence[str]) -> Language:
    """Find the language asked with --lang, or detect it from the system.

    An invalid value is ignored here: the parser reports it afterwards.
    """
    for index, argument in enumerate(arguments):
        if argument == "--lang" and index + 1 < len(arguments):
            value = arguments[index + 1]
        elif argument.startswith("--lang="):
            value = argument.removeprefix("--lang=")
        else:
            continue
        if value in LANGUAGE_CHOICES:
            return Language(value)

    return detect_language()


def _run_audit(target: str, *, fail_on: str, timeout: float, catalog: Catalog) -> ExitCode:
    try:
        source = load(target, timeout=timeout)
    except LoadError as error:
        message = catalog.text(error.key, **error.params)
        print(catalog.text("cli.error", prog=PROG, message=message), file=sys.stderr)
        return ExitCode.USAGE_ERROR

    report = audit(source)
    sys.stdout.write(render(report, catalog, color=should_use_color(sys.stdout)))

    if fail_on != "never" and report.reaches(Severity(fail_on)):
        return ExitCode.FINDINGS

    return ExitCode.OK


def _positive_number(catalog: Catalog) -> Callable[[str], float]:
    """Build an argparse type that accepts strictly positive numbers.

    Args:
        catalog: The messages used to explain an invalid value.

    Returns:
        The conversion function given to ``add_argument(type=...)``.
    """

    def convert(value: str) -> float:
        try:
            number = float(value)
        except ValueError:
            raise argparse.ArgumentTypeError(
                catalog.text("cli.not_a_number", value=value)
            ) from None
        if number <= 0:
            raise argparse.ArgumentTypeError(catalog.text("cli.not_positive", value=value))

        return number

    return convert
