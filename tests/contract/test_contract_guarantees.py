# AI-Assisted: Claude Code (model: claude-opus-5) - Wrote the FR-030 guarantee tests (task T048):
# each guarantee asserted against a generated snapshot AND asserted to refuse publication when
# violated, one case per catalogued CON-* code.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Added guarantee 21's marker-residue tests
# (007 task T036): one poisoned field per name-shaped family, plus proof that a fully built
# loadout fixture carries zero marker residue.
"""Tests for the FR-030 contract guarantees (FR-049, SC-001).

Each guarantee gets two tests, and the pairing is the point. Asserting that a good snapshot
passes proves nothing on its own — a check that always returns "fine" passes that test too. So
every guarantee is also broken deliberately, and the break must produce its **catalogued**
code at its **catalogued** severity, because `curation/resolutions.json` entries reference those
codes and a run may not decide that a normally-blocking finding is advisory today
(`validation-report.md` §1.1).
"""

from __future__ import annotations

from collections.abc import Callable

import pytest

from pipeline.models.curated import (
    CuratedDatasheet,
    CuratedDetachmentRestriction,
    CuratedGameSizeRule,
)
from pipeline.models.findings import Severity
from pipeline.report.catalogue import severity_of
from pipeline.validate.contract_checks import (
    MAX_CUSTOM_POINT_LIMIT,
    MIN_CUSTOM_POINT_LIMIT,
    check_snapshot,
)
from tests import factories


def _codes(snapshot, meta=None):  # type: ignore[no-untyped-def]
    return [f.finding_code for f in check_snapshot(snapshot, meta or factories.meta())]


def test_the_point_range_comes_from_the_consumer_contract_not_configuration() -> None:
    """`reference-db-schema.md` §3.4 is the single source of truth for the range (C7/R9)."""
    assert (MIN_CUSTOM_POINT_LIMIT, MAX_CUSTOM_POINT_LIMIT) == (500, 5000)


def test_a_well_formed_snapshot_raises_nothing() -> None:
    assert _codes(factories.snapshot()) == []


# --- guarantee 3, completeness: every datasheet has a cost row -----------------------------


def test_a_datasheet_with_no_cost_row_is_blocking() -> None:
    snapshot = factories.snapshot(datasheets=[factories.datasheet(cost_rows=[])])
    assert "CON-NO-COST" in _codes(snapshot)
    assert severity_of("CON-NO-COST") is Severity.BLOCKING


# --- guarantee 3, completeness: every enhancement belongs to a detachment -------------------


def test_an_orphan_enhancement_is_blocking() -> None:
    snapshot = factories.snapshot(
        enhancements=[factories.enhancement(detachment_id="d-does-not-exist")]
    )
    assert "CON-ORPHAN-ENHANCEMENT" in _codes(snapshot)
    assert severity_of("CON-ORPHAN-ENHANCEMENT") is Severity.BLOCKING


# --- guarantee 3, bands: contiguous, non-overlapping, covering 500..5000 --------------------


def _band(id_: str, lo: int, hi: int) -> CuratedGameSizeRule:
    return CuratedGameSizeRule(
        id=id_,
        edition_id=factories.EDITION_ID,
        label=id_,
        min_points=lo,
        max_points=hi,
        detachment_points_budget=6,
        max_detachments=2,
        max_enhancements=2,
    )


@pytest.mark.parametrize(
    ("bands", "expected"),
    [
        pytest.param(
            [_band("a", 500, 1999), _band("b", 2100, 5000)], "CON-BAND-GAP", id="interior-gap"
        ),
        pytest.param([_band("a", 700, 5000)], "CON-BAND-GAP", id="range-starts-late"),
        pytest.param([_band("a", 500, 4000)], "CON-BAND-GAP", id="range-ends-early"),
        pytest.param(
            [_band("a", 500, 2200), _band("b", 2000, 5000)], "CON-BAND-OVERLAP", id="overlap"
        ),
        pytest.param([], "CON-BAND-GAP", id="no-bands-at-all"),
    ],
)
def test_band_coverage_defects_are_blocking(bands, expected: str) -> None:  # type: ignore[no-untyped-def]
    assert expected in _codes(factories.snapshot(game_sizes=bands))
    assert severity_of(expected) is Severity.BLOCKING


def test_bands_covering_the_declared_range_exactly_are_accepted() -> None:
    covering = [_band("a", MIN_CUSTOM_POINT_LIMIT, 1999), _band("b", 2000, MAX_CUSTOM_POINT_LIMIT)]
    codes = _codes(factories.snapshot(game_sizes=covering))
    assert "CON-BAND-GAP" not in codes
    assert "CON-BAND-OVERLAP" not in codes


# --- guarantee 4, referential integrity ------------------------------------------------------


def test_a_dangling_intra_snapshot_reference_is_blocking() -> None:
    snapshot = factories.snapshot(datasheets=[factories.datasheet(faction_id="f-nowhere")])
    assert "CON-DANGLING-REF" in _codes(snapshot)
    assert severity_of("CON-DANGLING-REF") is Severity.BLOCKING


def test_a_leader_pair_naming_an_absent_datasheet_is_blocking() -> None:
    marshal = factories.datasheet("ds-forge-marshal").model_copy(
        update={"leader_pairs": ["ds-not-here"]}
    )
    assert "CON-DANGLING-REF" in _codes(factories.snapshot(datasheets=[marshal]))


def test_a_parent_faction_id_pointing_nowhere_is_blocking() -> None:
    child = factories.faction("f-cinder-chapter", parent="f-absent")
    snapshot = factories.snapshot(factions=[factories.faction(), child])
    assert "CON-DANGLING-REF" in _codes(snapshot)


# --- guarantee: restriction vocabulary -------------------------------------------------------


def test_an_out_of_vocabulary_restriction_type_is_blocking() -> None:
    restriction = CuratedDetachmentRestriction(
        id="r-invented",
        edition_id=factories.EDITION_ID,
        restriction_type="max_units_by_vibes",
        params={"max": 1},
        message_template="At most 1 of these.",
    )
    snapshot = factories.snapshot(restrictions=[restriction])
    assert "CON-RESTRICTION-VOCAB" in _codes(snapshot)
    assert severity_of("CON-RESTRICTION-VOCAB") is Severity.BLOCKING


def test_every_vocabulary_member_is_accepted() -> None:
    from pipeline.models.curated import RESTRICTION_VOCABULARY

    for index, restriction_type in enumerate(sorted(RESTRICTION_VOCABULARY)):
        restriction = CuratedDetachmentRestriction(
            id=f"r-{index}",
            edition_id=factories.EDITION_ID,
            restriction_type=restriction_type,
            params={},
            message_template="Invented mechanical message about {unit}.",
        )
        assert "CON-RESTRICTION-VOCAB" not in _codes(factories.snapshot(restrictions=[restriction]))


# --- guarantee 2, self-description -----------------------------------------------------------


def test_a_missing_version_stamp_is_blocking() -> None:
    meta = factories.meta().replace(schema_contract_version=0)
    assert "CON-VERSION-STAMP" in _codes(factories.snapshot(), meta)
    assert severity_of("CON-VERSION-STAMP") is Severity.BLOCKING


def test_a_mismatched_version_stamp_is_blocking() -> None:
    """The stamp must match what this build of the pipeline actually emits (FR-049)."""
    meta = factories.meta().replace(schema_contract_version=99)
    assert "CON-VERSION-STAMP" in _codes(factories.snapshot(), meta)


def test_a_malformed_rules_version_id_is_blocking() -> None:
    assert "CON-VERSION-STAMP" in _codes(factories.snapshot(), factories.meta(""))


# --- guarantee 21: no footnote-marker artifact in a published name (007 T036) ------------------


def _poison_weapon_name(ds: CuratedDatasheet) -> CuratedDatasheet:
    weapons = list(ds.weapons)
    weapons[0] = weapons[0].model_copy(update={"name": weapons[0].name + "*"})
    return ds.model_copy(update={"weapons": weapons})


def _poison_composition_model_name(ds: CuratedDatasheet) -> CuratedDatasheet:
    composition = list(ds.composition)
    composition[0] = composition[0].model_copy(
        update={"model_name": composition[0].model_name + "*"}
    )
    return ds.model_copy(update={"composition": composition})


def _poison_option_group_eligible_model_name(ds: CuratedDatasheet) -> CuratedDatasheet:
    groups = list(ds.option_groups)
    name = groups[0].eligible_model_name
    assert name is not None
    groups[0] = groups[0].model_copy(update={"eligible_model_name": name + "*"})
    return ds.model_copy(update={"option_groups": groups})


def _poison_option_choice_name(ds: CuratedDatasheet) -> CuratedDatasheet:
    choices = list(ds.option_choices)
    choices[0] = choices[0].model_copy(update={"name": choices[0].name + "*"})
    return ds.model_copy(update={"option_choices": choices})


def _poison_option_choice_item_name(ds: CuratedDatasheet) -> CuratedDatasheet:
    bundle = next(c for c in ds.option_choices if c.items)
    items = list(bundle.items)
    items[0] = items[0].model_copy(update={"item_name": items[0].item_name + "*"})
    poisoned_bundle = bundle.model_copy(update={"items": items})
    choices = [poisoned_bundle if c.id == bundle.id else c for c in ds.option_choices]
    return ds.model_copy(update={"option_choices": choices})


def _poison_equipment_group_model_name(ds: CuratedDatasheet) -> CuratedDatasheet:
    groups = list(ds.equipment_groups)
    name = groups[0].model_name
    assert name is not None
    groups[0] = groups[0].model_copy(update={"model_name": name + "*"})
    return ds.model_copy(update={"equipment_groups": groups})


def _poison_equipment_item_name(ds: CuratedDatasheet) -> CuratedDatasheet:
    groups = list(ds.equipment_groups)
    items = list(groups[0].items)
    items[0] = items[0].model_copy(update={"item_name": items[0].item_name + "*"})
    groups[0] = groups[0].model_copy(update={"items": items})
    return ds.model_copy(update={"equipment_groups": groups})


def _poison_item_constraint_item_name(ds: CuratedDatasheet) -> CuratedDatasheet:
    constraints = list(ds.item_constraints)
    constraints[0] = constraints[0].model_copy(update={"item_name": constraints[0].item_name + "*"})
    return ds.model_copy(update={"item_constraints": constraints})


def _poison_item_constraint_model_name(ds: CuratedDatasheet) -> CuratedDatasheet:
    scoped = next(c for c in ds.item_constraints if c.model_name is not None)
    updated = scoped.model_copy(update={"model_name": (scoped.model_name or "") + "*"})
    constraints = [
        updated if c.constraint_index == scoped.constraint_index else c for c in ds.item_constraints
    ]
    return ds.model_copy(update={"item_constraints": constraints})


#: One poisoning function per name-shaped field family guarantee 21 covers — every field
#: `check_marker_residue` walks, so a family the check silently stopped reaching is caught by the
#: field it stopped at rather than by an aggregate count (the same discipline
#: `tests/ip/test_ip_scan.py`'s `POISONED_LOADOUT` establishes for `CON-IP-BOUNDARY`).
_MARKER_POISONERS: dict[str, Callable[[CuratedDatasheet], CuratedDatasheet]] = {
    "weapon_name": _poison_weapon_name,
    "composition_model_name": _poison_composition_model_name,
    "option_group_eligible_model_name": _poison_option_group_eligible_model_name,
    "option_choice_name": _poison_option_choice_name,
    "option_choice_item_name": _poison_option_choice_item_name,
    "equipment_group_model_name": _poison_equipment_group_model_name,
    "equipment_item_name": _poison_equipment_item_name,
    "item_constraint_item_name": _poison_item_constraint_item_name,
    "item_constraint_model_name": _poison_item_constraint_model_name,
}


@pytest.mark.parametrize("field", sorted(_MARKER_POISONERS))
def test_a_marker_in_any_name_field_is_blocking(field: str) -> None:
    poisoned = _MARKER_POISONERS[field](factories.loadout_datasheet())
    codes = _codes(factories.snapshot(datasheets=[poisoned]))
    assert "CST-MARKER-RESIDUE" in codes, field
    assert severity_of("CST-MARKER-RESIDUE") is Severity.BLOCKING


def test_a_fully_built_loadout_fixture_carries_zero_marker_residue() -> None:
    """SC-002: a datasheet that exercises every name-shaped field this feature touches, built
    through the ordinary factory rather than deliberately poisoned, raises nothing."""
    clean = factories.snapshot(datasheets=[factories.loadout_datasheet()])
    assert "CST-MARKER-RESIDUE" not in _codes(clean)


# --- every raised finding is catalogued, always ----------------------------------------------


def test_every_finding_this_stage_can_raise_is_in_the_catalogue() -> None:
    broken = factories.snapshot(
        datasheets=[factories.datasheet(cost_rows=[], faction_id="f-nowhere")],
        enhancements=[factories.enhancement(detachment_id="d-gone")],
        game_sizes=[],
    )
    findings = check_snapshot(broken, factories.meta())
    assert findings
    for finding in findings:
        assert finding.severity is severity_of(finding.finding_code)
