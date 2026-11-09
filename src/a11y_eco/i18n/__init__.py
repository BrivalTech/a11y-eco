"""Translations of the texts shown to people.

Every text lives in a catalog, one per language, under a stable key. The code
never writes a sentence itself: it asks a catalog for the text of a key.
"""

import os
import re
from collections.abc import Mapping
from enum import StrEnum

from a11y_eco.i18n import en, fr
from a11y_eco.i18n.catalog import Catalog


class Language(StrEnum):
    """Languages the tool speaks."""

    EN = "en"
    FR = "fr"


CATALOGS: dict[Language, Catalog] = {
    Language.EN: en.CATALOG,
    Language.FR: fr.CATALOG,
}

DEFAULT_LANGUAGE = Language.FR
_LOCALE_VARIABLES = ("LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG")
_LOCALE_SEPARATORS = re.compile(r"[_.@-]")


def detect_language(environ: Mapping[str, str] = os.environ) -> Language:
    """Choose the language from the environment variables of the system.

    The first variable naming a language the tool speaks wins. Values such as
    ``C`` or ``POSIX``, or unsupported languages, are skipped.

    Args:
        environ: The environment variables.

    Returns:
        The detected language, or ``DEFAULT_LANGUAGE``.
    """
    supported = {language.value for language in Language}
    for variable in _LOCALE_VARIABLES:
        for locale_name in environ.get(variable, "").split(":"):
            code = _LOCALE_SEPARATORS.split(locale_name.strip(), maxsplit=1)[0].lower()
            if code in supported:
                return Language(code)
    return DEFAULT_LANGUAGE


__all__ = ["CATALOGS", "DEFAULT_LANGUAGE", "Catalog", "Language", "detect_language"]
