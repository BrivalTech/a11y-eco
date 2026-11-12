"""The audit rules.

Each module groups the rules of one theme. A new rule is declared with the
``@rule`` decorator in its module, then added to ``RULES`` below.
"""

from a11y_eco.checks import headings, images, language, media, names, sobriety
from a11y_eco.checks.base import Rule

RULES: tuple[Rule, ...] = (
    language.html_lang_missing,
    language.html_lang_invalid,
    images.image_without_alternative,
    headings.missing_main_heading,
    headings.several_main_headings,
    headings.skipped_heading_level,
    headings.empty_heading,
    names.broken_labelledby_reference,
    names.link_without_name,
    names.button_without_name,
    sobriety.too_many_requests,
    sobriety.too_many_stylesheets,
    sobriety.too_many_domains,
    sobriety.too_much_inline_code,
    media.media_loaded_automatically,
    media.missing_lazy_loading,
    media.document_displayed_in_page,
    media.gif_image,
    media.too_many_web_fonts,
    media.canvas_element,
)

__all__ = ["RULES", "Rule"]
