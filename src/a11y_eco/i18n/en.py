"""English messages."""

from a11y_eco.i18n.catalog import Catalog, PluralForm


def _plural_form(count: int) -> PluralForm:
    return "one" if count == 1 else "other"


CATALOG = Catalog(
    language="en",
    plural_form=_plural_form,
    thousands_separator=",",
    messages={
        "report.title": "Audit of {location} ({size} bytes)",
        "report.clean": "No problem found by the automated checks. A manual audit is still needed.",
        "report.summary": "Summary: {counts}",
        "severity.error": "error",
        "severity.warning": "warning",
        "severity.info": "info",
        "count.error.one": "{count} error",
        "count.error.other": "{count} errors",
        "count.warning.one": "{count} warning",
        "count.warning.other": "{count} warnings",
        "count.info.one": "{count} info",
        "count.info.other": "{count} info",
        "rule.A11Y-LANG-MISSING": "The default language of the page is not declared",
        "rule.A11Y-LANG-INVALID": "The language code of the page is not valid",
        "rule.A11Y-IMG-ALT": "Image without a text alternative",
        "rule.A11Y-HEADING-H1-MISSING": "The page has no level 1 heading",
        "rule.A11Y-HEADING-H1-MULTIPLE": "The page has several level 1 headings",
        "rule.A11Y-HEADING-SKIP": "Heading level skipped since the previous heading",
        "rule.A11Y-HEADING-EMPTY": "Heading without text",
        "rule.A11Y-ARIA-LABELLEDBY": "aria-labelledby refers to an id that does not exist",
        "rule.A11Y-LINK-NAME": "Link without an accessible name",
        "rule.A11Y-BUTTON-NAME": "Button without an accessible name",
    },
)
