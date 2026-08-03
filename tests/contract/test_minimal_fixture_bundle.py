# AI-Assisted: Claude Code (model: claude-opus-5) - Wrote the minimal-fixture conformance tests
# (task T054): the fixtures/minimal build satisfies every item of reference-db-schema.md §7,
# including the v1.2.0 additions.
"""Tests for the minimal fixture snapshot the consuming app's CI runs against (FR-048, SC-008).

`reference-db-schema.md` §7 exists so `001` can develop against a real bundle without waiting
for a real release. The thing that makes it trustworthy is that it comes out of **the same
builder** as a published snapshot — a hand-written fixture drifts from the emitter the first
time the emitter changes, and the drift shows up as a green app CI against a bundle no producer
would ever emit.

So this module asserts two different things: that the bundle satisfies §7's shopping list, and
that it was produced by the ordinary build path with nothing special-cased for fixtures.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from pipeline.cli import run_build
from pipeline.config import load_config
from pipeline.exit_codes import ExitCode
from pipeline.schema_validation import validate_bundle

REPO_ROOT = Path(__file__).resolve().parents[2]
MINIMAL = REPO_ROOT / "fixtures" / "minimal"


@pytest.fixture(scope="module")
def bundle(tmp_path_factory) -> dict:  # type: ignore[no-untyped-def, type-arg]
    if not MINIMAL.is_dir():
        pytest.skip("fixtures/minimal does not exist yet")
    result = run_build(
        config=load_config(env={}),
        rules_version_id="fixture-minimal",
        fixtures_dir=MINIMAL,
        offline=True,
        output_root=tmp_path_factory.mktemp("minimal-build"),
    )
    assert result.exit_code in (ExitCode.SUCCESS, ExitCode.ADVISORY_ONLY), [
        f.finding_code for f in result.findings if f.severity == "blocking"
    ]
    return result.bundle


def test_the_bundle_validates_against_its_schema(bundle: dict) -> None:
    validate_bundle(bundle, source="fixtures/minimal")


def test_two_factions_one_of_them_a_sub_faction_with_a_parent(bundle: dict) -> None:
    factions = bundle["factions"]
    assert len(factions) >= 2
    children = [f for f in factions if "parentFactionId" in f]
    assert children, "§3.5's ancestor query rule is not exercised without a sub-faction"
    parent_ids = {f["id"] for f in factions}
    assert all(child["parentFactionId"] in parent_ids for child in children)


def test_the_sub_faction_holds_an_exclusive_datasheet_and_the_parent_a_shared_one(
    bundle: dict,
) -> None:
    child = next(f for f in bundle["factions"] if "parentFactionId" in f)
    parent_id = child["parentFactionId"]
    by_faction: dict[str, list[str]] = {}
    for datasheet in bundle["datasheets"]:
        by_faction.setdefault(datasheet["factionId"], []).append(datasheet["id"])

    assert by_faction.get(child["id"]), "the sub-faction holds no exclusive datasheet"
    assert by_faction.get(parent_id), "the parent holds no shared datasheet"


def test_three_detachments_with_different_dp_costs(bundle: dict) -> None:
    costs = [d["detachmentPointsCost"] for d in bundle["detachments"]]
    assert len(costs) >= 3
    assert len(set(costs)) >= 2


def test_about_eight_datasheets(bundle: dict) -> None:
    assert len(bundle["datasheets"]) >= 8


@pytest.mark.parametrize(
    "flag", ["isEpicHero", "isLegends", "isCharacter", "isBattleline", "isDedicatedTransport"]
)
def test_each_datasheet_flag_is_exercised_at_least_once(bundle: dict, flag: str) -> None:
    assert any(datasheet[flag] for datasheet in bundle["datasheets"]), flag


def test_a_character_with_leader_pairs(bundle: dict) -> None:
    assert bundle["datasheetLeaderPairs"]
    characters = {d["id"] for d in bundle["datasheets"] if d["isCharacter"]}
    assert {pair["leaderDatasheetId"] for pair in bundle["datasheetLeaderPairs"]} <= characters


def test_a_datasheet_with_multiple_cost_bands_and_cost_bearing_wargear(bundle: dict) -> None:
    per_datasheet: dict[str, int] = {}
    for cost in bundle["datasheetCosts"]:
        per_datasheet[cost["datasheetId"]] = per_datasheet.get(cost["datasheetId"], 0) + 1
    assert max(per_datasheet.values()) >= 2

    assert bundle["datasheetWargearOptions"]
    assert all(option["pointsDelta"] != 0 for option in bundle["datasheetWargearOptions"])


def test_two_enhancements_from_different_detachments(bundle: dict) -> None:
    detachment_ids = {e["detachmentId"] for e in bundle["enhancements"]}
    assert len(bundle["enhancements"]) >= 2
    assert len(detachment_ids) >= 2


def test_at_least_two_point_bands_covering_the_declared_range(bundle: dict) -> None:
    bands = sorted(bundle["gameSizeRules"], key=lambda b: b["minPoints"])
    assert len(bands) >= 2
    assert bands[0]["minPoints"] == 500
    assert bands[-1]["maxPoints"] == 5000
    for earlier, later in zip(bands, bands[1:], strict=False):
        assert later["minPoints"] == earlier["maxPoints"] + 1


def test_every_datasheet_carries_at_least_one_ability_with_a_non_empty_summary(
    bundle: dict,
) -> None:
    with_abilities = {row["datasheetId"] for row in bundle["datasheetAbilities"]}
    assert with_abilities == {d["id"] for d in bundle["datasheets"]}
    assert all(row["summary"].strip() for row in bundle["datasheetAbilities"])


# --- the v1.2.0 additions -------------------------------------------------------------------


def test_an_escalating_price_tier(bundle: dict) -> None:
    assert any(tier["copyIndexMin"] > 1 for tier in bundle["datasheetCostTiers"])


def test_non_contiguous_size_bands_exercising_the_round_up_rule(bundle: dict) -> None:
    """Rows at 5 and 10 mean a 6-model unit pays the 10-model price (§3.2)."""
    per_datasheet: dict[str, list[int]] = {}
    for cost in bundle["datasheetCosts"]:
        per_datasheet.setdefault(cost["datasheetId"], []).append(cost["modelCount"])
    assert any(
        sorted(counts) != list(range(min(counts), max(counts) + 1))
        for counts in per_datasheet.values()
        if len(counts) >= 2
    )


def test_an_unverified_cost_row(bundle: dict) -> None:
    assert any(cost["pricingConfidence"] == "unverified" for cost in bundle["datasheetCosts"])
    assert any(cost["pricingConfidence"] == "verified" for cost in bundle["datasheetCosts"])


def test_a_non_null_detail_edition_code(bundle: dict) -> None:
    assert any("detailEditionCode" in d for d in bundle["datasheets"])
    assert any("detailEditionCode" not in d for d in bundle["datasheets"])


def test_the_bundle_was_built_by_the_ordinary_builder(bundle: dict) -> None:
    assert bundle["bundleFormatVersion"] == 1
    assert bundle["snapshotMeta"]["rulesVersionId"] == "fixture-minimal"
    assert bundle["datasheetDetachmentEligibility"] == []
