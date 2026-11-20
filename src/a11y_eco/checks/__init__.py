"""The audit rules.

Each module groups the rules of one theme. A new rule is declared with the
``@rule`` decorator in its module, then added to ``RULES`` below. A rule that reads
the downloads of --fetch-resources is declared with ``@network_rule`` and added to
``NETWORK_RULES``.
"""

from a11y_eco.checks import (
    graphics,
    headings,
    images,
    language,
    media,
    names,
    sobriety,
    structure,
    tools,
    transfer,
)
from a11y_eco.checks.base import NetworkRule, Rule

RULES: tuple[Rule, ...] = (
    language.html_lang_missing,
    language.html_lang_invalid,
    structure.missing_page_title,
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
    structure.missing_viewport,
    structure.missing_title,
    structure.missing_description,
    tools.too_many_analytics,
    tools.official_social_buttons,
    tools.too_many_carousels,
    graphics.too_many_animations,
    graphics.unoptimised_svg,
)

NETWORK_RULES: tuple[NetworkRule, ...] = (
    transfer.uncompressed_text,
    transfer.missing_cache_headers,
    transfer.static_files_with_cookies,
    transfer.too_many_redirects,
    transfer.oversized_images,
)

ALL_RULES: tuple[Rule | NetworkRule, ...] = (*RULES, *NETWORK_RULES)

__all__ = ["ALL_RULES", "NETWORK_RULES", "RULES", "NetworkRule", "Rule"]
