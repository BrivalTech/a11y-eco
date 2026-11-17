"""The list of the audit rules, for the ``rules`` command and the documentation.

Everything comes from ``RULES`` and ``NETWORK_RULES``: the list can never forget a rule.
``docs/rules.md`` and ``docs/rules.fr.md`` are this list in Markdown, and a test checks
that they are up to date.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Sequence

from a11y_eco import __version__
from a11y_eco.checks import NETWORK_RULES, RULES, NetworkRule, Rule
from a11y_eco.i18n import Catalog

LIST_FORMATS = ("console", "json", "markdown")
AnyRule = Rule | NetworkRule


def render_rules(catalog: Catalog, output_format: str) -> str:
    """List every rule, grouped by family, in the language of the catalog.

    Args:
        catalog: The messages of the language to write in.
        output_format: One of LIST_FORMATS.

    Returns:
        The list, ending with a newline.
    """
    renderers: dict[str, Callable[[Catalog], str]] = {
        "console": _console,
        "json": _json,
        "markdown": _markdown,
    }

    return renderers[output_format](catalog)


def _groups() -> list[tuple[str, Sequence[AnyRule]]]:
    """The families of rules, in the order of the audit."""
    return [
        ("a11y", [rule for rule in RULES if rule.rule_id.startswith("A11Y-")]),
        ("eco", [rule for rule in RULES if rule.rule_id.startswith("ECO-")]),
        ("network", NETWORK_RULES),
    ]


def _console(catalog: Catalog) -> str:
    rules = [rule for _, group in _groups() for rule in group]
    id_width = max(len(rule.rule_id) for rule in rules)
    severity_width = max(len(_severity(rule, catalog)) for rule in rules)
    reference_width = max(len(rule.reference) for rule in rules)
    lines = []

    for group, members in _groups():
        lines.append(catalog.text(f"rules.group.{group}"))
        lines += [
            f"  {rule.rule_id:<{id_width}}  {_severity(rule, catalog):<{severity_width}}  "
            f"{rule.reference:<{reference_width}}  {catalog.text(f'about.{rule.rule_id}')}"
            for rule in members
        ]
        lines.append("")
    lines.append(catalog.text("rules.count", count=len(rules)))

    return "\n".join(lines) + "\n"


def _json(catalog: Catalog) -> str:
    document = {
        "tool": {"name": "a11y-eco", "version": __version__},
        "language": catalog.language,
        "rules": [
            {
                "rule_id": rule.rule_id,
                "group": group,
                "severity": rule.severity.value,
                "reference": rule.reference,
                "about": catalog.text(f"about.{rule.rule_id}"),
            }
            for group, members in _groups()
            for rule in members
        ],
    }

    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


def _markdown(catalog: Catalog) -> str:
    text = catalog.text
    count = sum(len(members) for _, members in _groups())
    lines = [
        f"# {text('rules.title')}",
        "",
        f"<!-- {text('rules.generated', language=catalog.language)} -->",
        "",
        text("rules.count", count=count),
    ]
    header = [text(f"rules.column.{column}") for column in ("rule", "severity", "reference")]
    header.append(text("rules.column.about"))

    for group, members in _groups():
        lines += [
            "",
            f"## {text(f'rules.group.{group}')}",
            "",
            "| " + " | ".join(header) + " |",
            "|---|---|---|---|",
        ]
        lines += [
            f"| `{rule.rule_id}` | {_severity(rule, catalog)} | {rule.reference} "
            f"| {text(f'about.{rule.rule_id}')} |"
            for rule in members
        ]

    return "\n".join(lines) + "\n"


def _severity(rule: AnyRule, catalog: Catalog) -> str:
    return catalog.text(f"severity.{rule.severity}")
