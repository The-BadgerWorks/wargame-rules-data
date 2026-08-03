# AI-Assisted: Claude Code (model: claude-opus-5) - Keeps the consumer-compatibility check green
# in CI (task T077): the minimal bundle ingests into reference-db-schema.md v1.2.0's schema with
# real foreign keys, satisfies the §1 guarantees, and prices a multi-detachment army exactly.
"""Tests for the consumer-compatibility check (US1 independent test, FR-048, SC-008).

Running this once and writing the result into a report would prove the bundle was ingestible
*that day*. Running it in CI proves it stays that way, which is the property the consuming app
actually depends on.

The expected total is asserted as a **number**, not as "it produced something". Every one of the
v1.2.0 additions changes it: drop the copy-index lookup and it falls to 555, drop §3.2's
round-up and it falls to 480, drop the wargear delta and it falls to 550. A test that only
asserted "no exception" would pass with all three broken.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.consumer_compat import EXERCISE_ARMY, run

BUNDLE = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "minimal"
    / "build"
    / "rules-fixture-minimal.json"
)

#: 70 + 70 + 80 (copies 1-2 then the third-copy tier) + 20 + 175 (6 models rounded up to the
#: 10-model band) + 15 (wargear) + 110 + 25.
EXPECTED_TOTAL = 565


@pytest.fixture(scope="module")
def result():  # type: ignore[no-untyped-def]
    if not BUNDLE.is_file():
        pytest.skip("the minimal fixture bundle has not been built yet")
    return run(BUNDLE)


def test_the_bundle_ingests_with_foreign_keys_enforced(result) -> None:  # type: ignore[no-untyped-def]
    assert result.tables["datasheet"] >= 8
    assert result.tables["datasheet_detachment_eligibility"] == 0


def test_every_consumer_guarantee_holds(result) -> None:  # type: ignore[no-untyped-def]
    assert result.violations == []


def test_a_multi_detachment_army_prices_exactly(result) -> None:  # type: ignore[no-untyped-def]
    assert result.army_total == EXPECTED_TOTAL


def test_the_escalating_tier_is_applied_to_the_third_copy(result) -> None:  # type: ignore[no-untyped-def]
    warden = [line for line in result.army_lines if "ASHEN WARDEN" in line]
    assert [line.rsplit(": ", 1)[1] for line in warden] == ["70", "70", "80"]


def test_a_squad_size_between_bands_rounds_up(result) -> None:  # type: ignore[no-untyped-def]
    """Six models is not a listed band, so it pays the 10-model price (§3.2)."""
    (sentinel,) = [line for line in result.army_lines if "ASHEN SENTINEL" in line]
    assert sentinel.endswith(": 175")


def test_the_army_exercises_more_than_one_detachment() -> None:
    detachments = {e["id"] for e in EXERCISE_ARMY if e["kind"] == "detachment"}
    assert len(detachments) >= 2
