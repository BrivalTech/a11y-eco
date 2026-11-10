"""Fixtures shared by every test module."""

import pytest

LOCALE_VARIABLES = ("LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG")


@pytest.fixture(autouse=True)
def _neutral_locale(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make every test independent of the language of the machine running it."""
    for variable in LOCALE_VARIABLES:
        monkeypatch.delenv(variable, raising=False)
