# AI-Assisted: Claude Code (model: claude-sonnet-5) - Added for 009 task T049 (FR-013, SC-004,
# Product Owner decision T047/O2 2026-08-18): every faction id, datasheet id, and ability key a
# previous published version carried MUST be present, with the same identity, in a migrated
# build. O2's decision designates this check as the standing guard for the id-stability risk
# (R-B) in place of pre-authoring the whole `-N`-suffix crosswalk population.
"""``CON-IDENTITY-DROPPED`` -- presence, not a ratio.

`plan.md` finding 2's lesson (an empty roster reads 100 on the coverage ratchets) is what makes a
presence check necessary beside the existing coverage figures: a single dropped id inside an
otherwise-healthy percentage would not necessarily move any ratio past its floor.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pipeline.validate.identity import (
    IdentityBaseline,
    check_identity_survival,
    load_identity_baseline,
    snapshot_identifiers,
)
from tests.factories import faction, snapshot, summaries


def _baseline(
    *, faction_ids: frozenset[str], datasheet_ids: frozenset[str], ability_keys: frozenset[str]
) -> IdentityBaseline:
    return IdentityBaseline(
        rules_version_id="wh40k-11e-invented",
        faction_ids=faction_ids,
        datasheet_ids=datasheet_ids,
        ability_keys=ability_keys,
    )


# -- the pure comparison ------------------------------------------------------------------------


def test_an_identical_identifier_set_raises_nothing() -> None:
    baseline = _baseline(
        faction_ids=frozenset({"f-emberwrights"}),
        datasheet_ids=frozenset({"ds-sootveil-warden"}),
        ability_keys=frozenset({"core:deep-strike"}),
    )

    findings = check_identity_survival(
        baseline,
        current_faction_ids=frozenset({"f-emberwrights"}),
        current_datasheet_ids=frozenset({"ds-sootveil-warden"}),
        current_ability_keys=frozenset({"core:deep-strike"}),
    )

    assert findings == []


def test_a_grown_identifier_set_raises_nothing() -> None:
    """Gaining ids is not a defect -- the upstream catalogue growing is ordinary, expected."""
    baseline = _baseline(
        faction_ids=frozenset({"f-emberwrights"}),
        datasheet_ids=frozenset({"ds-sootveil-warden"}),
        ability_keys=frozenset({"core:deep-strike"}),
    )

    findings = check_identity_survival(
        baseline,
        current_faction_ids=frozenset({"f-emberwrights", "f-glimmerfen-covenant"}),
        current_datasheet_ids=frozenset({"ds-sootveil-warden", "ds-marsh-warden"}),
        current_ability_keys=frozenset({"core:deep-strike", "core:lone-operative"}),
    )

    assert findings == []


def test_a_dropped_datasheet_id_is_the_blocking_finding_naming_it() -> None:
    baseline = _baseline(
        faction_ids=frozenset({"f-emberwrights"}),
        datasheet_ids=frozenset({"ds-sootveil-warden", "ds-marsh-warden"}),
        ability_keys=frozenset({"core:deep-strike"}),
    )

    findings = check_identity_survival(
        baseline,
        current_faction_ids=frozenset({"f-emberwrights"}),
        current_datasheet_ids=frozenset({"ds-sootveil-warden"}),  # ds-marsh-warden dropped
        current_ability_keys=frozenset({"core:deep-strike"}),
    )

    assert len(findings) == 1
    assert findings[0].finding_code == "CON-IDENTITY-DROPPED"
    assert findings[0].detail == {"kind": "datasheet_id", "id": "ds-marsh-warden"}


def test_a_renamed_datasheet_id_reads_as_one_dropped_and_the_new_slug_is_not_this_checks_job() -> (
    None
):
    """A rename is a dropped old id from this check's point of view -- it does not, and should
    not, try to guess that a new id is "the same unit renamed"; that judgement belongs to a
    curator with the crosswalk, not to an automatic set comparison."""
    baseline = _baseline(
        faction_ids=frozenset(),
        datasheet_ids=frozenset({"ds-sootveil-warden-2"}),
        ability_keys=frozenset(),
    )

    findings = check_identity_survival(
        baseline,
        current_faction_ids=frozenset(),
        current_datasheet_ids=frozenset({"ds-sootveil-warden"}),  # the `-2` suffix moved
        current_ability_keys=frozenset(),
    )

    assert [f.detail["id"] for f in findings] == ["ds-sootveil-warden-2"]


def test_every_dropped_kind_is_reported_independently() -> None:
    baseline = _baseline(
        faction_ids=frozenset({"f-emberwrights"}),
        datasheet_ids=frozenset({"ds-sootveil-warden"}),
        ability_keys=frozenset({"core:deep-strike"}),
    )

    findings = check_identity_survival(
        baseline,
        current_faction_ids=frozenset(),
        current_datasheet_ids=frozenset(),
        current_ability_keys=frozenset(),
    )

    kinds = {f.detail["kind"] for f in findings}
    assert kinds == {"faction_id", "datasheet_id", "ability_key"}
    assert len(findings) == 3


# -- extraction from a real snapshot -------------------------------------------------------------


def test_snapshot_identifiers_extracts_the_three_sets() -> None:
    built = snapshot(
        factions=[faction("f-emberwrights"), faction("f-glimmerfen-covenant")],
        ability_summaries=summaries(("core:deep-strike", "core:lone-operative")),
    )

    faction_ids, datasheet_ids, ability_keys = snapshot_identifiers(built)

    assert faction_ids == {"f-emberwrights", "f-glimmerfen-covenant"}
    assert datasheet_ids == {built.datasheets[0].datasheet_id}
    assert ability_keys == {"core:deep-strike", "core:lone-operative"}


def test_a_snapshot_missing_a_baseline_faction_is_caught_end_to_end() -> None:
    baseline = _baseline(
        faction_ids=frozenset({"f-emberwrights", "f-glimmerfen-covenant"}),
        datasheet_ids=frozenset(),
        ability_keys=frozenset(),
    )
    built = snapshot(factions=[faction("f-emberwrights")])  # f-glimmerfen-covenant dropped

    current_faction_ids, current_datasheet_ids, current_ability_keys = snapshot_identifiers(built)
    findings = check_identity_survival(
        baseline,
        current_faction_ids=current_faction_ids,
        current_datasheet_ids=frozenset(baseline.datasheet_ids) | current_datasheet_ids,
        current_ability_keys=frozenset(baseline.ability_keys) | current_ability_keys,
    )

    assert [f.detail["id"] for f in findings] == ["f-glimmerfen-covenant"]


# -- loading a committed baseline file ------------------------------------------------------------


def test_load_identity_baseline_reads_t014s_committed_shape(tmp_path: Path) -> None:
    path = tmp_path / "baseline.json"
    path.write_text(
        json.dumps(
            {
                "rules_version_id": "wh40k-11e-invented",
                "faction_ids": ["f-emberwrights"],
                "datasheet_ids": ["ds-sootveil-warden"],
                "ability_keys": ["core:deep-strike"],
            }
        ),
        encoding="utf-8",
    )

    baseline = load_identity_baseline(path)

    assert baseline.rules_version_id == "wh40k-11e-invented"
    assert baseline.faction_ids == frozenset({"f-emberwrights"})
    assert baseline.datasheet_ids == frozenset({"ds-sootveil-warden"})
    assert baseline.ability_keys == frozenset({"core:deep-strike"})


def test_the_real_committed_identity_baseline_loads_and_has_the_documented_counts() -> None:
    """`fixtures/identity-baseline/README.md`'s own counts, asserted against the real file so a
    silent edit cannot drift the two apart."""
    path = (
        Path(__file__).resolve().parents[2]
        / "fixtures"
        / "identity-baseline"
        / "wh40k-11e-2026-08-4.json"
    )
    if not path.is_file():
        pytest.skip("identity-baseline fixture not present in this checkout")

    baseline = load_identity_baseline(path)

    assert baseline.rules_version_id == "wh40k-11e-2026-08-4"
    assert len(baseline.faction_ids) == 30
    assert len(baseline.datasheet_ids) == 2083
    assert len(baseline.ability_keys) == 2125
