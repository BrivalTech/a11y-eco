"""Command-line interface.

This module only handles argument parsing and exit codes.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from enum import IntEnum

from a11y_eco import __version__

PROG = "a11y-eco"


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
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
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
    parser.parse_args(argv)
    parser.print_help()

    return ExitCode.OK
