# AI-Assisted: Claude Code (model: claude-sonnet-5) - User Story 4's test for the curated-tree
# round-trip (007 task T029): write -> read -> compare through `pipeline/curate/writer.py` and
# `pipeline/curate/prior.py`, per class, for all five classes `006` added and the curated tree
# lost (FR-012, research D2, issue #14).
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Added the item_constraints round-trip (007
# US3, the carried-over gap US4's T032 deliberately left for this entity — recorded in
# `.impl-progress.md`'s US3 section — since US3 is the phase that creates the first real
# producer for it).
"""User Story 4: the curated `data/` tree round-trips everything `006` published.

research D2 found the curated writer's per-datasheet serialisation and the prior-snapshot reader
that mirrors it lose **all** of `006`'s additions, not the three shapes issue #14 names:
equipment groups (with their items), `default_equipment_state`, `option_choices[].items`, and the
three `option_groups` eligibility columns. A bundle re-emitted *from the tree* — what the
`validate` path does — silently carried empty arrays and no default-equipment state; published
bundles were only correct because `publish` re-runs the full acquire-to-build chain instead.

`tests/factories.py::loadout_datasheet()` (Setup task T009) is the fixture built for exactly this
test: one datasheet exercising all five classes at once, so a round-trip failure on any one of
them is legible without cross-referencing a second function's defaults.
"""

from __future__ import annotations

from pathlib import Path

from pipeline.curate.prior import read_curated_tree
from pipeline.curate.writer import write_tree
from tests.factories import faction, loadout_datasheet, snapshot


def _round_tripped(tmp_path: Path) -> tuple[object, object]:
    """Write `loadout_datasheet()` through `writer.py`, read it back through `prior.py`."""
    original = loadout_datasheet()
    original_snapshot = snapshot(factions=[faction()], datasheets=[original])

    data_dir = tmp_path / "data" / "wh40k-11e"
    curation_dir = tmp_path / "curation"
    write_tree(original_snapshot, data_dir=data_dir, curation_dir=curation_dir)

    rebuilt_snapshot = read_curated_tree(data_dir)
    assert rebuilt_snapshot is not None
    assert len(rebuilt_snapshot.datasheets) == 1
    return original, rebuilt_snapshot.datasheets[0]


# --- 006 class 1: equipment groups, with their items -----------------------------------------


def test_equipment_groups_round_trip(tmp_path: Path) -> None:
    original, rebuilt = _round_tripped(tmp_path)
    assert len(rebuilt.equipment_groups) == len(original.equipment_groups) == 1
    original_group = original.equipment_groups[0]
    rebuilt_group = rebuilt.equipment_groups[0]
    assert rebuilt_group.id == original_group.id
    assert rebuilt_group.applies_to == original_group.applies_to
    assert rebuilt_group.model_name == original_group.model_name
    assert rebuilt_group.composition_line == original_group.composition_line
    assert [(i.item_name, i.weapon_line) for i in rebuilt_group.items] == [
        (i.item_name, i.weapon_line) for i in original_group.items
    ]


# --- 006 class 2: default_equipment_state -----------------------------------------------------


def test_default_equipment_state_round_trips(tmp_path: Path) -> None:
    original, rebuilt = _round_tripped(tmp_path)
    assert rebuilt.default_equipment_state == original.default_equipment_state is not None


# --- 006 class 3: option_choices[].items -------------------------------------------------------


def test_option_choice_items_round_trip(tmp_path: Path) -> None:
    original, rebuilt = _round_tripped(tmp_path)
    original_bundle = next(c for c in original.option_choices if c.items)
    rebuilt_bundle = next(c for c in rebuilt.option_choices if c.id == original_bundle.id)
    assert [(i.role, i.item_index, i.item_name, i.weapon_line) for i in rebuilt_bundle.items] == [
        (i.role, i.item_index, i.item_name, i.weapon_line) for i in original_bundle.items
    ]
    # The single-choice-with-no-items case must also survive: an empty bundle stays empty, not a
    # fabricated one-item array.
    original_no_change = next(c for c in original.option_choices if c.is_no_change)
    rebuilt_no_change = next(c for c in rebuilt.option_choices if c.id == original_no_change.id)
    assert rebuilt_no_change.items == ()


# --- 006 class 4/5/6: the three option-group eligibility columns -------------------------------


def test_option_group_eligibility_columns_round_trip(tmp_path: Path) -> None:
    original, rebuilt = _round_tripped(tmp_path)
    original_group = original.option_groups[0]
    rebuilt_group = rebuilt.option_groups[0]
    assert rebuilt_group.eligible_model_name == original_group.eligible_model_name is not None
    assert rebuilt_group.eligible_max_count == original_group.eligible_max_count is not None
    assert rebuilt_group.is_per_model == original_group.is_per_model is not None


# --- 007's own sixth class: item_constraints, carried over from US4's T032 scope note ----------


def test_item_constraints_round_trip(tmp_path: Path) -> None:
    """Not one of `006`'s five classes T029/T032 scoped to — `007`'s own new entity, closed here
    because this phase creates the first real producer for it (`.impl-progress.md` US3 section,
    carried-over gap). Covers both an optional field present (`weapon_line`) and absent
    (`model_name` on the first row; `weapon_line` on the second) so neither optional field's
    round trip is proven only by coincidence of the other being set."""
    original, rebuilt = _round_tripped(tmp_path)
    assert len(rebuilt.item_constraints) == len(original.item_constraints) == 2
    assert [
        (c.constraint_index, c.constraint_type, c.item_name, c.weapon_line, c.model_name)
        for c in rebuilt.item_constraints
    ] == [
        (c.constraint_index, c.constraint_type, c.item_name, c.weapon_line, c.model_name)
        for c in original.item_constraints
    ]


# --- the whole point: a bundle rebuilt from the tree matches a freshly-acquired one -------------


def test_all_five_classes_together_leave_no_field_silently_dropped(tmp_path: Path) -> None:
    """SC-007's determinism claim: a datasheet rebuilt from `data/` carries what was written to
    it, not empty arrays and an absent state — the second-order defect research D2 names."""
    original, rebuilt = _round_tripped(tmp_path)
    assert rebuilt.equipment_groups != ()
    assert rebuilt.default_equipment_state is not None
    assert any(choice.items for choice in rebuilt.option_choices)
    assert rebuilt.option_groups[0].eligible_model_name is not None
    assert rebuilt.option_groups[0].eligible_max_count is not None
    assert rebuilt.option_groups[0].is_per_model is not None
    assert rebuilt.item_constraints != ()
