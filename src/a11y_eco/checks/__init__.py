"""The audit rules.

Each module groups the rules of one theme. A new rule is declared with the
``@rule`` decorator in its module, then added to ``RULES`` below.
"""

from a11y_eco.checks import images, language
from a11y_eco.checks.base import Rule

RULES: tuple[Rule, ...] = (
    language.html_lang_missing,
    language.html_lang_invalid,
    images.image_without_alternative,
)

__all__ = ["RULES", "Rule"]
