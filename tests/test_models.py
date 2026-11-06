import dataclasses

import pytest

from a11y_eco.models import Finding, Location, Severity


def test_severities_are_ranked_from_least_to_most_severe() -> None:
    assert [s.rank for s in (Severity.INFO, Severity.WARNING, Severity.ERROR)] == [0, 1, 2]


@pytest.mark.parametrize(
    ("severity", "threshold", "expected"),
    [
        (Severity.ERROR, Severity.WARNING, True),
        (Severity.WARNING, Severity.WARNING, True),
        (Severity.INFO, Severity.WARNING, False),
    ],
)
def test_is_at_least(severity: Severity, threshold: Severity, expected: bool) -> None:
    assert severity.is_at_least(threshold) is expected


def test_rank_does_not_follow_alphabetical_order() -> None:
    # As strings, "error" < "info": comparing with < would be silently wrong.
    assert Severity.ERROR < Severity.INFO
    assert Severity.ERROR.is_at_least(Severity.INFO)


def test_severity_behaves_as_a_plain_string() -> None:
    assert Severity.ERROR == "error"
    assert Severity("warning") is Severity.WARNING


def test_location_displays_as_line_and_column() -> None:
    assert str(Location(line=12, column=5)) == "12:5"


def test_finding_is_immutable() -> None:
    finding = Finding(rule_id="A11Y-IMG-ALT", severity=Severity.ERROR)

    with pytest.raises(dataclasses.FrozenInstanceError):
        finding.severity = Severity.INFO  # type: ignore[misc]
