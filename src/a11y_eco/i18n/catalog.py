"""A catalog of translated messages, and how to use it."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Literal

PluralForm = Literal["one", "other"]


@dataclass(frozen=True, slots=True)
class Catalog:
    """The messages of one language, with its plural and number rules."""

    language: str
    """Language code, e.g. ``fr``."""

    messages: Mapping[str, str]
    """Message templates by key, using ``str.format`` placeholders: ``{count}``."""

    plural_form: Callable[[int], PluralForm]
    """Plural category of a number in this language."""

    thousands_separator: str
    """Character between groups of three digits: ``1,234`` or ``1 234``."""

    def text(self, key: str, /, **params: object) -> str:
        """Return a message, with its placeholders filled in.

        Args:
            key: Key of the message, e.g. ``report.title``.
            **params: Values of the placeholders.

        Returns:
            The translated message.

        Raises:
            KeyError: If the key is missing: this is a programming error.
        """
        return self.messages[key].format(**params)

    def count(self, key: str, count: int) -> str:
        """Return a counted message in the right plural form.

        ``count("count.error", 2)`` reads the message ``count.error.other``.

        Args:
            key: Key of the message, without the plural form.
            count: The number to write.

        Returns:
            The translated message, e.g. ``2 erreurs``.
        """
        return self.text(f"{key}.{self.plural_form(count)}", count=self.number(count))

    def number(self, value: int) -> str:
        """Write a whole number with the separators of the language.

        Args:
            value: The number.

        Returns:
            The formatted number.
        """
        return f"{value:,}".replace(",", self.thousands_separator)

    def rule_title(self, rule_id: str) -> str:
        """Return the description of a rule, or its identifier if there is none.

        Args:
            rule_id: Identifier of the rule.

        Returns:
            A human-readable sentence.
        """
        return self.messages.get(f"rule.{rule_id}", rule_id)
