# AI-Assisted: Claude Code (model: claude-opus-5) - Keeps the consumer-compatibility check green
# in CI (task T077): the minimal bundle ingests into reference-db-schema.md v1.2.0's schema with
# real foreign keys, satisfies the §1 guarantees, and prices a multi-detachment army exactly.
# AI-Assisted: Claude Code (model: claude-opus-5) - Added the two conditions the first real-bundle
# run hit and the fixtures never reproduced (docs/follow-ups.md item 8): a self-referencing
# faction foreign key loaded in id order, and duplicate primary keys — including the ones SQLite
# itself cannot catch because a key component is NULL.
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

import json
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


# --- the two conditions the fixtures never reproduced -------------------------------------------


@pytest.fixture
def base():  # type: ignore[no-untyped-def]
    if not BUNDLE.is_file():
        pytest.skip("the minimal fixture bundle has not been built yet")
    return json.loads(BUNDLE.read_text(encoding="utf-8"))


def test_a_chapter_sorted_before_its_parent_still_ingests(base, tmp_path: Path) -> None:  # type: ignore[no-untyped-def]
    """`faction.parent_faction_id` is self-referencing and the array is sorted by id.

    `curated-snapshot-format.md` requires that sort, for determinism, so a chapter whose id sorts
    before its parent's is *normal* rather than exceptional. A per-row foreign-key check fails on
    it; deferring to `COMMIT` — which is what any real ingestor must do — still enforces every
    key. This is what the first real-bundle run died on.
    """
    parent = base["factions"][0]
    chapter = dict(parent, id="f-aaa-chapter", code="aaa-chapter", parentFactionId=parent["id"])
    bundle = dict(base, factions=[chapter, *base["factions"]])
    path = tmp_path / "rules-chapter-first.json"
    path.write_text(json.dumps(bundle), encoding="utf-8")

    result = run(path)

    assert result.tables["faction"] == len(bundle["factions"])
    assert not [v for v in result.violations if "foreign key" in v]


def test_a_duplicate_primary_key_is_reported_rather_than_raised(base, tmp_path: Path) -> None:  # type: ignore[no-untyped-def]
    bundle = dict(base, datasheetCosts=[*base["datasheetCosts"], base["datasheetCosts"][0]])
    path = tmp_path / "rules-duplicate-cost.json"
    path.write_text(json.dumps(bundle), encoding="utf-8")

    result = run(path)

    assert [v for v in result.violations if "datasheet_cost" in v and "duplicate" in v]


def test_a_bundle_without_the_exercise_army_skips_pricing_rather_than_failing(  # type: ignore[no-untyped-def]
    base, tmp_path: Path
) -> None:
    """Every real bundle is this case, so it must not read as a defect in the bundle."""
    bundle = dict(base, detachments=[], enhancements=[], datasheetDetachmentEligibility=[])
    path = tmp_path / "rules-no-exercise-army.json"
    path.write_text(json.dumps(bundle), encoding="utf-8")

    result = run(path)

    assert result.army_lines == [
        "pricing exercise skipped: this bundle does not carry the exercise army's entities, "
        "which is expected for any bundle but the minimal fixture"
    ]
    assert not [v for v in result.violations if "pricing failed" in v]


def test_a_duplicate_whose_key_component_is_absent_is_still_reported(base, tmp_path: Path) -> None:  # type: ignore[no-untyped-def]
    """The one SQLite cannot catch, and therefore the one worth a test of its own.

    `datasheet_keyword`'s key ends in the nullable `model_scope`, and SQLite treats NULLs in a
    unique index as distinct — so it inserts both rows without complaint and the app shows the
    keyword twice. The check has to compare on the contract's key, not on the engine's.
    """
    row = next(r for r in base["datasheetKeywords"] if "modelScope" not in r)
    bundle = dict(base, datasheetKeywords=[*base["datasheetKeywords"], dict(row)])
    path = tmp_path / "rules-duplicate-keyword.json"
    path.write_text(json.dumps(bundle), encoding="utf-8")

    result = run(path)

    assert [v for v in result.violations if "datasheet_keyword" in v and "duplicate" in v]
