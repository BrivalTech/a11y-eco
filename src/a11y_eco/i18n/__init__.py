"""Translations of the texts shown to people.

Every text lives in a catalog, one per language, under a stable key. The code
never writes a sentence itself: it asks a catalog for the text of a key.
"""

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

__all__ = ["CATALOGS", "Catalog", "Language"]
