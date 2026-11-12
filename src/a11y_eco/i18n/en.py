"""English messages."""

from a11y_eco.i18n.catalog import Catalog, PluralForm


def _plural_form(count: int) -> PluralForm:
    return "one" if count == 1 else "other"


CATALOG = Catalog(
    language="en",
    plural_form=_plural_form,
    thousands_separator=",",
    messages={
        "cli.description": "Audit a web page for accessibility and eco-design issues.",
        "cli.commands": "commands",
        "cli.arguments": "arguments",
        "cli.options": "options",
        "cli.help": "show this help message and exit",
        "cli.version": "show the version number and exit",
        "cli.error": "{prog}: error: {message}",
        "cli.not_a_number": "{value!r} is not a number",
        "cli.not_positive": "{value!r} must be greater than 0",
        "cli.audit.help": "audit a web page",
        "cli.audit.description": "Audit a web page and print the problems found.",
        "cli.audit.epilog": (
            "exit status:\n"
            "  0  no finding reaches the --fail-on severity\n"
            "  1  at least one finding reaches the --fail-on severity\n"
            "  2  invalid arguments, or the page could not be loaded\n"
        ),
        "cli.audit.target": "URL (http or https) or path of an HTML file",
        "cli.audit.fail_on": "lowest severity that makes the command fail (default: %(default)s)",
        "cli.audit.lang": "language of the report (default: the language of the system, or fr)",
        "cli.audit.timeout": "network timeout when auditing a URL (default: %(default)s)",
        "load.unreadable": "cannot read {path}: {reason}",
        "load.too_large": "{location} is larger than the {limit}-byte limit",
        "load.not_html": "{url} is not an HTML page ({content_type})",
        "load.http_status": "{url} answered with HTTP status {status}",
        "load.unreachable": "cannot reach {url}: {reason}",
        "load.timeout": "{url} did not answer within {timeout} s",
        "metrics.title": "Sobriety (minimum values, read from the HTML only)",
        "metrics.requests": "Requests when the page loads: at least {count}",
        "metrics.resources": "Resources: {list}",
        "metrics.none": "none",
        "metrics.deferred": "Loaded on demand: {count}",
        "metrics.external": "From another host: {count}",
        "metrics.domains": "Domains: {count}",
        "metrics.dom": "DOM elements: {count}",
        "resource.stylesheet.one": "{count} stylesheet",
        "resource.stylesheet.other": "{count} stylesheets",
        "resource.script.one": "{count} script",
        "resource.script.other": "{count} scripts",
        "resource.image.one": "{count} image",
        "resource.image.other": "{count} images",
        "resource.font.one": "{count} font",
        "resource.font.other": "{count} fonts",
        "resource.media.one": "{count} audio or video",
        "resource.media.other": "{count} audio or video files",
        "resource.frame.one": "{count} embedded content",
        "resource.frame.other": "{count} embedded contents",
        "resource.other.one": "{count} other",
        "resource.other.other": "{count} others",
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
