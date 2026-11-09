"""Texts shown to people.

They live apart from the rules and the reporters so that they can be translated:
English only for now, French comes with the bilingual sprint.
"""

from a11y_eco.models import Severity

RULE_TITLES: dict[str, str] = {
    "A11Y-LANG-MISSING": "The default language of the page is not declared",
    "A11Y-LANG-INVALID": "The language code of the page is not valid",
    "A11Y-IMG-ALT": "Image without a text alternative",
    "A11Y-HEADING-H1-MISSING": "The page has no level 1 heading",
    "A11Y-HEADING-H1-MULTIPLE": "The page has several level 1 headings",
    "A11Y-HEADING-SKIP": "Heading level skipped since the previous heading",
    "A11Y-ARIA-LABELLEDBY": "aria-labelledby refers to an id that does not exist",
}
SEVERITY_NAMES: dict[Severity, tuple[str, str]] = {
    Severity.ERROR: ("error", "errors"),
    Severity.WARNING: ("warning", "warnings"),
    Severity.INFO: ("info", "info"),
}


def rule_title(rule_id: str) -> str:
    """Return the description of a rule, or its identifier if there is none.

    Args:
        rule_id: Identifier of the rule.

    Returns:
        A human-readable sentence.
    """
    return RULE_TITLES.get(rule_id, rule_id)


def count_severity(count: int, severity: Severity) -> str:
    """Write a number of findings, e.g. ``1 error`` or ``3 warnings``.

    Args:
        count: Number of findings.
        severity: Their severity.

    Returns:
        The count followed by the singular or plural name.
    """
    singular, plural = SEVERITY_NAMES[severity]
    return f"{count} {singular if count == 1 else plural}"
