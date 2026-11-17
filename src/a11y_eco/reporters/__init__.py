"""Turn an audit report into something people or programs can read.

Each format has a reporter, a function that follows the ``Reporter`` protocol. A new
format is a new module, a new ``Format`` member and one line in ``REPORTERS``.
"""

from __future__ import annotations

from enum import StrEnum

from a11y_eco.reporters import console, html_report, json_report
from a11y_eco.reporters.base import Reporter, finding_message


class Format(StrEnum):
    """The output formats, as written on the command line."""

    CONSOLE = "console"
    JSON = "json"
    HTML = "html"


REPORTERS: dict[Format, Reporter] = {
    Format.CONSOLE: console.render,
    Format.JSON: json_report.render,
    Format.HTML: html_report.render,
}

__all__ = ["REPORTERS", "Format", "Reporter", "finding_message"]
