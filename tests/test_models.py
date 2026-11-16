import dataclasses
import json

import pytest

from a11y_eco.models import Download, Finding, Location, NetworkMetrics, Severity


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
    assert isinstance(Severity.ERROR, str)
    assert str(Severity.ERROR) == "error"
    assert json.dumps({"severity": Severity.ERROR}) == '{"severity": "error"}'
    assert Severity("warning") is Severity.WARNING


def test_location_displays_as_line_and_column() -> None:
    assert str(Location(line=12, column=5)) == "12:5"


def test_finding_is_immutable() -> None:
    finding = Finding(rule_id="A11Y-IMG-ALT", severity=Severity.ERROR)

    with pytest.raises(dataclasses.FrozenInstanceError):
        finding.severity = Severity.INFO  # type: ignore[misc]


def test_download_is_ok_only_with_a_2xx_status() -> None:
    assert Download("u", status=204).ok
    assert not Download("u", status=304).ok
    assert not Download("u").ok  # no response at all


def test_network_metrics_add_up_the_downloads() -> None:
    network = NetworkMetrics(
        downloads=(
            Download("a", status=200, transferred=1000),
            Download("b", status=404, transferred=150),
            Download("c"),
        )
    )

    assert (network.requests, network.failed, network.transferred) == (3, 2, 1150)
    assert network.complete


@pytest.mark.parametrize(
    "network",
    [
        pytest.param(NetworkMetrics(downloads=(), skipped=2), id="files-skipped"),
        pytest.param(NetworkMetrics(downloads=(Download("a", complete=False),)), id="cut-short"),
    ],
)
def test_network_transfer_is_a_minimum_when_downloads_are_missing(
    network: NetworkMetrics,
) -> None:
    assert not network.complete
