# AI-Assisted: Claude Code (model: claude-sonnet-5) - 2026-10-09 pipeline P3 task 3 (spec §4.2
# P4b): failing-first tests for `derive_line_scopes` -- the spec receipt in synthetic form, the
# omitted cases, a receipt that a unit-wide equipment group counts toward every candidate line
# (and alone yields nothing), a receipt that weapon-line matching beats a differing name, and the
# end-to-end receipt that a full offline build over `fixtures/minimal` scopes a real group.
"""Tests for `pipeline.reconcile.option_scope.derive_line_scopes` (spec §4.2 P4b).

`fixtures/minimal` carries zero option rows (`tests/enrichment/test_wargear_options_text.py`
already established this), so the end-to-end test follows that file's own pattern: copy the
fixture into `tmp_path`, inject synthetic rows there, and run the real build. The tracked fixture
itself is never touched.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from pipeline.models.curated import (
    CuratedEquipmentGroup,
    CuratedEquipmentItem,
    CuratedOptionChoice,
    CuratedOptionChoiceItem,
    CuratedOptionGroup,
    EquipmentAppliesTo,
    OptionItemRole,
    OptionScope,
)
from pipeline.reconcile.option_scope import derive_line_scopes

# --- local builders ------------------------------------------------------------------------------
# The brief's helper names (`equipment_group`, `option_group`, `option_choice`, `replaced`,
# `granted`) do not exist in `tests/factories.py`; these are built here against the real models.


def _equipment_group(
    line: int, model_name: str, *, composition_line: int | None, items: tuple[str, ...]
) -> CuratedEquipmentGroup:
    return CuratedEquipmentGroup(
        id=f"eq-fx-{line}",
        line=line,
        applies_to=EquipmentAppliesTo.MODEL_GROUP,
        model_name=model_name,
        composition_line=composition_line,
        items=tuple(
            CuratedEquipmentItem(item_index=index + 1, item_name=name)
            for index, name in enumerate(items)
        ),
    )


def _unit_wide_group(line: int, *, items: tuple[str, ...]) -> CuratedEquipmentGroup:
    return CuratedEquipmentGroup(
        id=f"eq-fx-{line}",
        line=line,
        applies_to=EquipmentAppliesTo.UNIT,
        items=tuple(
            CuratedEquipmentItem(item_index=index + 1, item_name=name)
            for index, name in enumerate(items)
        ),
    )


def _option_group(group_id: str, **kwargs: object) -> CuratedOptionGroup:
    return CuratedOptionGroup(id=group_id, line=1, scope=OptionScope.UNIT, **kwargs)  # type: ignore[arg-type]


def _option_choice(
    group_id: str, *, items: tuple[CuratedOptionChoiceItem, ...]
) -> CuratedOptionChoice:
    return CuratedOptionChoice(id=f"oc-{group_id}-1", group_id=group_id, name="choice", items=items)


def _replaced(name: str, index: int, *, weapon_line: int | None = None) -> CuratedOptionChoiceItem:
    return CuratedOptionChoiceItem(
        role=OptionItemRole.REPLACED, item_index=index, item_name=name, weapon_line=weapon_line
    )


def _granted(name: str, index: int, *, weapon_line: int | None = None) -> CuratedOptionChoiceItem:
    return CuratedOptionChoiceItem(
        role=OptionItemRole.GRANTED, item_index=index, item_name=name, weapon_line=weapon_line
    )


# --- the spec receipt, in synthetic form ----------------------------------------------------------

EQUIPMENT = (
    _equipment_group(1, "Test Sergeant", composition_line=1, items=("test blade",)),
    _equipment_group(2, "Test Trooper", composition_line=2, items=("test blade",)),
    _equipment_group(
        3, "Test Trooper with test shield", composition_line=3, items=("test shield", "test blade")
    ),
    # Unresolved: zero/two-or-more name matches. Carries a real item, but contributes nothing --
    # "carried only by an unresolved group" must read the same as "carried by nobody".
    _equipment_group(4, "Test Lantern Bearer", composition_line=None, items=("test lantern",)),
)

GROUP = _option_group("og-fx-1", eligible_max_count=1)
CHOICE = _option_choice("og-fx-1", items=(_replaced("test blade", 1), _granted("test maul", 2)))


def test_replaced_items_resolve_to_every_line_that_carries_them() -> None:
    (group,) = derive_line_scopes(
        option_groups=[GROUP], option_choices=[CHOICE], equipment_groups=list(EQUIPMENT)
    )
    assert group.eligible_composition_lines == (1, 2, 3)


def test_a_shield_only_replacement_scopes_to_the_shield_line() -> None:
    choice = _option_choice(
        "og-fx-1", items=(_replaced("test shield", 1), _granted("test maul", 2))
    )
    (group,) = derive_line_scopes(
        option_groups=[GROUP], option_choices=[choice], equipment_groups=list(EQUIPMENT)
    )
    assert group.eligible_composition_lines == (3,)


@pytest.mark.parametrize(
    "items",
    [
        (_granted("test maul", 1),),  # nothing replaced
        (_replaced("test lantern", 1),),  # carried only by an unresolved group
        (_replaced("test pike", 1),),  # carried by nobody
    ],
)
def test_underivable_groups_publish_nothing(
    items: tuple[CuratedOptionChoiceItem, ...],
) -> None:
    (group,) = derive_line_scopes(
        option_groups=[GROUP],
        option_choices=[_option_choice("og-fx-1", items=items)],
        equipment_groups=list(EQUIPMENT),
    )
    assert group.eligible_composition_lines == ()


def test_a_datasheet_with_no_line_resolved_equipment_group_at_all_publishes_nothing() -> None:
    """A unit-wide group never manufactures a candidate line by itself."""
    unit_only = (_unit_wide_group(1, items=("test blade",)),)
    (group,) = derive_line_scopes(
        option_groups=[GROUP], option_choices=[CHOICE], equipment_groups=list(unit_only)
    )
    assert group.eligible_composition_lines == ()


# --- controller ruling (a): a unit-wide group's items count toward every candidate line --------


def test_a_unit_wide_equipment_groups_item_counts_toward_every_candidate_line() -> None:
    """`test maul` is carried by nobody's own line, only by a unit-wide sentence -- every
    candidate line's loadout still includes it, because a unit-wide item sits on every model."""
    equipment = (
        _equipment_group(1, "Test Sergeant", composition_line=1, items=("test blade",)),
        _equipment_group(2, "Test Trooper", composition_line=2, items=("test shield",)),
        _unit_wide_group(3, items=("test maul",)),
    )
    choice = _option_choice("og-fx-1", items=(_replaced("test maul", 1), _granted("test pike", 2)))
    (group,) = derive_line_scopes(
        option_groups=[GROUP], option_choices=[choice], equipment_groups=list(equipment)
    )
    assert group.eligible_composition_lines == (1, 2)


# --- controller ruling (b): weapon-line matching beats a differing name -------------------------


def test_weapon_line_matching_beats_a_differing_name() -> None:
    """The replaced item is named differently from the loadout item, but both carry the SAME
    weapon_line -- weapon_line wins, so the line is eligible despite the name mismatch."""
    equipment = (
        CuratedEquipmentGroup(
            id="eq-fx-1",
            line=1,
            applies_to=EquipmentAppliesTo.MODEL_GROUP,
            model_name="Test Sergeant",
            composition_line=1,
            items=(CuratedEquipmentItem(item_index=1, item_name="test spar", weapon_line=7),),
        ),
    )
    choice = _option_choice(
        "og-fx-1", items=(_replaced("test blade", 1, weapon_line=7), _granted("test maul", 2))
    )
    (group,) = derive_line_scopes(
        option_groups=[GROUP], option_choices=[choice], equipment_groups=list(equipment)
    )
    assert group.eligible_composition_lines == (1,)


def test_a_same_name_item_with_a_different_weapon_line_on_both_sides_does_not_match() -> None:
    """Both sides carry a weapon_line, so the match is by weapon_line only -- a same-named item
    whose weapon_line differs must NOT match, even though a name-only comparison would pass."""
    equipment = (
        CuratedEquipmentGroup(
            id="eq-fx-1",
            line=1,
            applies_to=EquipmentAppliesTo.MODEL_GROUP,
            model_name="Test Sergeant",
            composition_line=1,
            items=(CuratedEquipmentItem(item_index=1, item_name="test blade", weapon_line=7),),
        ),
    )
    choice = _option_choice(
        "og-fx-1", items=(_replaced("test blade", 1, weapon_line=9), _granted("test maul", 2))
    )
    (group,) = derive_line_scopes(
        option_groups=[GROUP], option_choices=[choice], equipment_groups=list(equipment)
    )
    assert group.eligible_composition_lines == ()


# --- end-to-end: a full offline build over `fixtures/minimal` scopes a real group ---------------

MINIMAL = Path(__file__).resolve().parents[2] / "fixtures" / "minimal"
FIRST_ID = "AV01"


def _empty_repo(tmp: Path) -> Path:
    for relative in (
        "data/wh40k-11e/factions",
        "curation/abilities",
        "reports",
        "state",
        "site/prerelease",
        "work",
    ):
        (tmp / relative).mkdir(parents=True, exist_ok=True)
    return tmp


def _fixture_with_scoped_option(tmp: Path) -> Path:
    """Copy `fixtures/minimal` to `tmp` and give `AV01` (composition line 1, a single-model unit
    named "Ashen Sentinel") one line-resolved default-equipment sentence and two option rows --
    an equip-only one (no REPLACED item, so its group must stay unscoped) and a replace one (so
    its group must scope to line 1). Follows the exact harness
    `tests/enrichment/test_wargear_options_text.py` already uses for this fixture: `fixtures/
    minimal` itself carries zero option rows and is never touched."""
    fixtures = tmp / "fixtures"
    shutil.copytree(MINIMAL, fixtures, ignore=shutil.ignore_patterns("build"))

    datasheets_path = fixtures / "wahapedia" / "Datasheets.csv"
    text = datasheets_path.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    header = lines[0].split("|")
    column = header.index("loadout")
    rewritten = [lines[0]]
    for line in lines[1:]:
        cells = line.split("|")
        if cells[0] == FIRST_ID:
            cells[column] = "The Ashen Sentinel is equipped with: test blade."
        rewritten.append("|".join(cells))
    datasheets_path.write_text("﻿" + "\n".join(rewritten) + "\n", encoding="utf-8")

    options_path = fixtures / "wahapedia" / "Datasheets_options.csv"
    options_text = options_path.read_text(encoding="utf-8-sig")
    options_lines = options_text.splitlines()
    options_lines.append(
        f"{FIRST_ID}|1|Wargear Options|This model can be equipped with 1 test lantern.|"
    )
    options_lines.append(
        f"{FIRST_ID}|2|Wargear Options|One Ashen Sentinel's test blade can be replaced with "
        "1 test maul.|"
    )
    options_path.write_text("﻿" + "\n".join(options_lines) + "\n", encoding="utf-8")
    return fixtures


def test_a_full_offline_build_scopes_the_minimal_fixtures_groups(tmp_path: Path) -> None:
    """A real build wires `derive_line_scopes` end to end: the replace group scopes to AV01's
    only composition line, and the sibling equip-only group (no REPLACED item) carries none."""
    from pipeline.cli import run_build
    from pipeline.config import load_config
    from pipeline.exit_codes import ExitCode

    fixtures = _fixture_with_scoped_option(tmp_path / "f")
    result = run_build(
        config=load_config(env={}),
        rules_version_id="fixture-line-scope",
        fixtures_dir=fixtures,
        offline=True,
        output_root=tmp_path / "out",
        repository_root=_empty_repo(tmp_path / "repo"),
    )
    assert result.exit_code in (ExitCode.SUCCESS, ExitCode.ADVISORY_ONLY), [
        f.finding_code for f in result.findings if f.severity == "blocking"
    ]

    datasheet = next(
        row for row in result.bundle["datasheets"] if str(row["name"]).upper() == "ASHEN SENTINEL"
    )
    datasheet_id = datasheet["id"]
    composition_lines = {
        row["line"]
        for row in result.bundle["datasheetCompositions"]
        if row["datasheetId"] == datasheet_id
    }
    groups = [
        row for row in result.bundle["datasheetOptionGroups"] if row["datasheetId"] == datasheet_id
    ]
    assert groups, "no option groups reached the bundle -- the fixture rows were not read"

    scoped = [row for row in groups if "eligibleCompositionLines" in row]
    unscoped = [row for row in groups if "eligibleCompositionLines" not in row]
    assert scoped, "no group carried eligibleCompositionLines -- derive_line_scopes is not wired"
    assert unscoped, "the equip-only group (no REPLACED item) must carry no scoping at all"
    for row in scoped:
        for line in row["eligibleCompositionLines"]:
            assert line in composition_lines, (line, composition_lines)
