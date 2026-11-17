"""HTML report: one self-contained page, accessible and light.

No JavaScript, no external file: the page works offline and can be attached to an
email. The severity is always written in full, colours only reinforce it. Everything
that comes from the audited page is escaped, because that page may be hostile.
"""

from __future__ import annotations

import html

from a11y_eco import __version__
from a11y_eco.i18n import Catalog
from a11y_eco.models import Finding, Report
from a11y_eco.reporters.base import finding_message, metrics_measures, network_measures, summary

#: Colours checked for a contrast of at least 4.5:1 with the background (WCAG 1.4.3),
#: in both themes; borders reach at least 3:1 (WCAG 1.4.11).
_STYLE = """\
:root{color-scheme:light dark;--bg:#fff;--code:#f2f2f2;--text:#1b1b1b;--muted:#595959;
--border:#767676;--error:#b3261e;--warning:#8a4b00;--info:#005f73}
@media (prefers-color-scheme:dark){:root{--bg:#141414;--code:#242424;--text:#ececec;
--muted:#b4b4b4;--border:#8c8c8c;--error:#ff9e95;--warning:#ffc46b;--info:#7fd6e8}}
body{max-width:60rem;margin:0 auto;padding:1.5rem 1rem;background:var(--bg);
color:var(--text);font:1rem/1.5 system-ui,sans-serif}
h1,h3,pre{overflow-wrap:anywhere}
h1{font-size:1.5rem}
h2{font-size:1.25rem;margin-top:2rem;border-bottom:1px solid var(--border)}
h3{font-size:1rem;margin:0}
.findings{list-style:none;padding:0}
.finding{border-left:.3rem solid var(--color);padding:.5rem 1rem;margin:1rem 0}
.error{--color:var(--error)}.warning{--color:var(--warning)}.info{--color:var(--info)}
.severity{color:var(--color)}
.meta,footer{color:var(--muted)}
.meta{margin:.25rem 0}
pre{background:var(--code);padding:.5rem;margin:.5rem 0 0;white-space:pre-wrap}
@media print{.finding{break-inside:avoid}}
"""


def render(report: Report, catalog: Catalog, *, color: bool = False) -> str:
    """Render a report as a complete HTML page.

    Args:
        report: The audit report.
        catalog: The messages of the language to write in; also the page language.
        color: Ignored: the page has its own colours.

    Returns:
        The HTML page, ending with a newline.
    """
    title = catalog.text(
        "report.title", location=report.location, size=catalog.number(report.page_size)
    )
    lines = [
        "<!DOCTYPE html>",
        f'<html lang="{catalog.language}">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{_text(title)}</title>",
        f'<meta name="description" content="{html.escape(catalog.text("html.description"))}">',
        f"<style>\n{_STYLE}</style>",
        "</head>",
        "<body>",
        "<header>",
        f"<h1>{_text(title)}</h1>",
        f"<p>{_text(summary(report, catalog))}</p>",
        "</header>",
        "<main>",
    ]

    if report.metrics is not None:
        lines += _section(catalog.text("metrics.title"), metrics_measures(report.metrics, catalog))

    if report.network is not None:
        lines += _section(catalog.text("network.title"), network_measures(report.network, catalog))

    lines.append(f"<h2>{_text(catalog.text('html.findings'))}</h2>")

    if report.findings:
        lines.append('<ul class="findings">')
        lines += [_finding(finding, catalog) for finding in report.findings]
        lines.append("</ul>")
    else:
        lines.append(f"<p>{_text(catalog.text('report.clean'))}</p>")

    lines += [
        "</main>",
        f"<footer><p>{_text(catalog.text('html.generated', version=__version__))}</p></footer>",
        "</body>",
        "</html>",
    ]

    return "\n".join(lines) + "\n"


def _text(value: str) -> str:
    """Escape text put between tags; quotes need escaping only in attribute values."""
    return html.escape(value, quote=False)


def _section(title: str, measures: list[str]) -> list[str]:
    items = "".join(f"<li>{_text(measure)}</li>" for measure in measures)

    return [f"<h2>{_text(title)}</h2>", f"<ul>{items}</ul>"]


def _finding(finding: Finding, catalog: Catalog) -> str:
    severity = _text(catalog.text(f"severity.{finding.severity}"))
    heading = catalog.text(
        "html.finding",
        severity=f'<span class="severity">{severity}</span>',
        message=_text(finding_message(finding, catalog)),
    )
    meta = [finding.rule_id, finding.reference]

    if finding.location:
        meta.append(
            catalog.text(
                "html.position", line=finding.location.line, column=finding.location.column
            )
        )

    parts = [
        f'<li class="finding {finding.severity}">',
        f"<h3>{heading}</h3>",
        f'<p class="meta">{_text(" · ".join(part for part in meta if part))}</p>',
    ]

    if finding.snippet:
        parts.append(f"<pre><code>{_text(finding.snippet)}</code></pre>")

    parts.append("</li>")

    return "".join(parts)
