# AI-Assisted: Claude Code (model: claude-sonnet-5) - 008-wargear-option-completion Phase 7
# machinery (T066, T069, T070): the curator escape hatch's own new guarantees, layered on top of
# the resolving/dangling-reference behaviour `test_composition_option_overrides.py` and
# `test_equipment_overrides.py` already cover for the option- and equipment-override files
# individually. This file is the first to exercise both override files together, and the first to
# assert the redundancy advisory FR-011 requires once a later production starts reaching a row a
# curator already resolved by hand.
"""FR-009 to FR-012: the curator escape hatch's own contract, not the two files' resolving path.

Three things this feature adds beyond what `004`'s and `007`'s override files already proved:

1. **Redundancy is visible, not silent** (FR-011, T066/T067/T068). An override still wins when a
   later production could also resolve its row -- that half is structural already, proven by the
   two older test files above. What is new is that the pipeline now says so: it tries the
   production anyway, discards the result, and raises the advisory `OPT-OVERRIDE-REDUNDANT` naming
   the datasheet and row, so a curator can retire the now-unnecessary entry deliberately rather than
   it quietly outliving its own reason to exist.
2. **Both override loops fire together** (T069), proven here over `GF25` -- this feature's own
   override-target fixture -- rather than over `004`'s Mirefen Tanglers or `007`'s Marshwatch Line,
   which each exercise one file in isolation.
3. **An override-closed row counts as resolved, at the coverage figure, not only at the
   per-datasheet state** (T070) -- `wargear_option_state`/`default_equipment_state` already read
   `extracted` once an override resolves a datasheet's only unparsed row (the two older files
   proved that at the `_option_structure`/`_equipment` level); this proves the loadout coverage
   functions that feed `loadout.options_resolved` and `loadout.default_equipment` count it too.
"""

from __future__ import annotations

from pathlib import Path

from pipeline.curate.assemble import _equipment, _option_structure
from pipeline.curate.authored import AuthoredContent
from pipeline.models.authored import (
    EquipmentOverrideEntry,
    EquipmentOverrideItem,
    OptionOverrideChoice,
    OptionOverrideEntry,
)
from pipeline.models.curated import (
    CuratedCompositionEntry,
    CuratedEquipmentGroup,
    CuratedEquipmentItem,
    DefaultEquipmentState,
    EquipmentAppliesTo,
    WargearOptionState,
)
from pipeline.models.findings import Severity
from pipeline.parse.equipment_grammar import EQUIPMENT_TABLE
from pipeline.parse.wahapedia_csv import CsvReadResult, read_file, read_text
from pipeline.report.catalogue import CATALOGUE
from pipeline.validate.coverage import (
    default_equipment_resolved_datasheets,
    options_resolved_datasheets,
)
from pipeline.validate.refs import check_authored_references
from tests import factories
from tests.enrichment.conftest import weapon

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "enrichment" / "wahapedia"

# --- T066: redundancy is visible, not silent ----------------------------------------------------
#
# A self-contained fixture, not GF25: GF25 is deliberately unresolvable by any production this
# feature builds (T010), so it cannot stand in for "a production could ALSO resolve this row".
# `REDUNDANT_DETAIL_ID`/`REDUNDANT_DATASHEET` invent a row a `004` baseline production has always
# resolved (`can be equipped with`), so the override sits beside a production that reaches the
# same row independently -- the only shape the redundancy advisory exists to catch.

REDUNDANT_DETAIL_ID = "GF26"
REDUNDANT_DATASHEET = "ds-gf26-redundant"

RESOLVABLE_OPTION_ROW = (
    "datasheet_id|line|button|description|\n"
    f"{REDUNDANT_DETAIL_ID}|1|Wargear Options|This model can be equipped with 1 dusk lantern.|\n"
)

RESOLVABLE_EQUIPMENT_ROW = (
    "datasheet_id|line|description|\n"
    f"{REDUNDANT_DETAIL_ID}|1|Every model is equipped with: signal lantern.|\n"
)


def _redundant_option_detail() -> dict[str, CsvReadResult]:
    return {"Datasheets_options.csv": read_text("Datasheets_options.csv", RESOLVABLE_OPTION_ROW)}


def _redundant_option_override() -> AuthoredContent:
    return AuthoredContent(
        option_overrides=(
            OptionOverrideEntry.model_validate(
                {
                    "datasheet_id": REDUNDANT_DATASHEET,
                    "line": 1,
                    "scope": "unit",
                    # Deliberately DIFFERENT from what `parse_row` would build (`dusk lantern`,
                    # scope MODEL) -- the point is that the override's own values publish even
                    # though a production could independently resolve the row.
                    "choices": [
                        OptionOverrideChoice(name="curator lantern", count=2, grants_weapon_line=1)
                    ],
                }
            ),
        )
    )


def test_an_option_override_matching_a_production_still_wins_and_is_flagged_redundant() -> None:
    outcome = _option_structure(
        REDUNDANT_DETAIL_ID,
        REDUNDANT_DATASHEET,
        _redundant_option_detail(),
        _redundant_option_override(),
        [weapon(1, "Curator lantern")],
        [],
    )

    # FR-011's "the override wins" stays structural: the CURATOR's values publish, not the
    # production's (`dusk lantern` / scope MODEL / count 1).
    (group,) = outcome.groups
    assert group.scope.value == "unit"
    (choice,) = outcome.choices
    assert (choice.name, choice.count) == ("curator lantern", 2)

    redundant = [f for f in outcome.findings if f.finding_code == "OPT-OVERRIDE-REDUNDANT"]
    assert len(redundant) == 1
    assert redundant[0].detail["datasheet_id"] == REDUNDANT_DATASHEET
    assert redundant[0].detail["line"] == 1
    assert CATALOGUE["OPT-OVERRIDE-REDUNDANT"].severity is Severity.ADVISORY


def test_an_option_override_on_a_row_no_production_reaches_is_never_flagged_redundant() -> None:
    """The negative case T028/T068-T070 lean on elsewhere: `GF25`'s option row resolves through no
    production this feature builds, so an override closing it must NOT raise the advisory."""
    outcome = _option_structure(
        "GF25",
        "ds-gf25-override-target",
        {"Datasheets_options.csv": read_file(FIXTURES / "Datasheets_options.csv")},
        AuthoredContent(
            option_overrides=(
                OptionOverrideEntry.model_validate(
                    {
                        "datasheet_id": "ds-gf25-override-target",
                        "line": 1,
                        "scope": "unit",
                        "choices": [
                            OptionOverrideChoice(name="ember lance", count=1, grants_weapon_line=1)
                        ],
                    }
                ),
            )
        ),
        [weapon(1, "Ember lance")],
        [],
    )
    assert [f.finding_code for f in outcome.findings] == []
    assert outcome.state is WargearOptionState.EXTRACTED


def _redundant_equipment_detail() -> dict[str, CsvReadResult]:
    return {EQUIPMENT_TABLE: read_text(EQUIPMENT_TABLE, RESOLVABLE_EQUIPMENT_ROW)}


def _redundant_equipment_override() -> AuthoredContent:
    return AuthoredContent(
        equipment_overrides=(
            EquipmentOverrideEntry.model_validate(
                {
                    "datasheet_id": REDUNDANT_DATASHEET,
                    "line": 1,
                    "applies_to": "unit",
                    # Deliberately a different item than the sentence names (`signal lantern`).
                    "items": [EquipmentOverrideItem(item_name="curator lantern", count=2)],
                }
            ),
        )
    )


def test_an_equipment_override_matching_a_production_still_wins_and_is_flagged_redundant() -> None:
    composition = (
        CuratedCompositionEntry(line=1, model_name="Redundant Model", min_count=1, max_count=1),
    )
    outcome = _equipment(
        REDUNDANT_DETAIL_ID,
        REDUNDANT_DATASHEET,
        _redundant_equipment_detail(),
        _redundant_equipment_override(),
        composition,
        (),
    )

    (group,) = outcome.groups
    (item,) = group.items
    assert (item.item_name, item.count) == ("curator lantern", 2)

    redundant = [f for f in outcome.findings if f.finding_code == "OPT-OVERRIDE-REDUNDANT"]
    assert len(redundant) == 1
    assert redundant[0].detail["datasheet_id"] == REDUNDANT_DATASHEET
    assert redundant[0].detail["line"] == 1


def test_an_equipment_override_on_a_row_no_production_reaches_is_never_flagged_redundant() -> None:
    """The equipment twin of the option negative case, over `GF25`'s own equipment sentence
    (`Every Marsh Sentry with a lantern is equipped with: ember lance.` -- equipment-qualified
    subject, permanently refused, T049)."""
    composition = (
        CuratedCompositionEntry(line=1, model_name="Marsh Sentry", min_count=3, max_count=3),
    )
    outcome = _equipment(
        "GF25",
        "ds-gf25",
        {EQUIPMENT_TABLE: read_file(FIXTURES / "Datasheets_unit_equipment.csv")},
        AuthoredContent(
            equipment_overrides=(
                EquipmentOverrideEntry.model_validate(
                    {
                        "datasheet_id": "ds-gf25",
                        "line": 1,
                        "applies_to": "unit",
                        "items": [EquipmentOverrideItem(item_name="ember lance", count=1)],
                    }
                ),
            )
        ),
        composition,
        (weapon(1, "Ember lance"),),
    )
    assert [f.finding_code for f in outcome.findings] == []
    assert outcome.state is DefaultEquipmentState.EXTRACTED


# --- T069: both override loops resolve stale references together, over GF25 ---------------------
#
# `test_composition_option_overrides.py` and `test_equipment_overrides.py` each already prove
# `check_override_references` catches a dangling line/weapon/composition reference for their own
# file, individually. This is the first test where an option override AND an equipment override
# are both present in one `AuthoredContent` and checked in the same call -- the shape T071/T072's
# real entries will actually be in.


def _dangling_option_override() -> OptionOverrideEntry:
    return OptionOverrideEntry.model_validate(
        {
            "datasheet_id": "ds-gf25-override-target",
            # GF25's option fixture has exactly one row (line 1); line 99 names no row at all.
            "line": 99,
            "scope": "unit",
            "choices": [OptionOverrideChoice(name="ember lance", count=1)],
        }
    )


def _dangling_equipment_override() -> EquipmentOverrideEntry:
    return EquipmentOverrideEntry.model_validate(
        {
            "datasheet_id": "ds-gf25",
            # GF25's equipment fixture has exactly one row (line 1); line 99 names no row at all.
            "line": 99,
            "applies_to": "unit",
            "items": [EquipmentOverrideItem(item_name="ember lance", count=1)],
        }
    )


def test_a_dangling_option_and_equipment_override_are_both_reported_in_one_candidate() -> None:
    authored = AuthoredContent(
        option_overrides=(_dangling_option_override(),),
        equipment_overrides=(_dangling_equipment_override(),),
    )
    # `ds-gf25`'s line check is guarded on the datasheet publishing SOME equipment already (the
    # same carve-out `test_a_still_valid_override_on_a_datasheet_with_no_equipment_at_all_is_not_
    # reported` pins in `test_equipment_overrides.py`: an empty `equipment_groups` reads as
    # "composition never resolved", not as "this reference has gone stale"). A published line-1
    # group makes line 99 a genuine dangling reference rather than a suppressed one.
    published_group = CuratedEquipmentGroup(
        id="eq-gf25-1",
        line=1,
        applies_to=EquipmentAppliesTo.UNIT,
        items=[CuratedEquipmentItem(item_index=1, item_name="Placeholder item")],
    )
    snapshot = factories.snapshot(
        datasheets=[
            factories.datasheet(datasheet_id="ds-gf25-override-target"),
            factories.datasheet(datasheet_id="ds-gf25").model_copy(
                update={"equipment_groups": [published_group]}
            ),
        ]
    )

    findings = check_authored_references(snapshot, authored)
    dangling = [f for f in findings if f.finding_code == "AUT-DANGLING-REF"]

    assert {f.detail["file_name"] for f in dangling} == {
        "option-overrides.json",
        "equipment-overrides.json",
    }
    assert {f.detail["field"] for f in dangling} == {"line"}
    assert {f.detail["missing_id"] for f in dangling} == {"99"}


# --- T070: an override-closed row counts toward the coverage figure, not only the per-datasheet
# state -------------------------------------------------------------------------------------------


def test_an_option_override_closing_a_datasheets_only_unparsed_row_counts_as_resolved() -> None:
    outcome = _option_structure(
        "GF25",
        "ds-gf25-override-target",
        {"Datasheets_options.csv": read_file(FIXTURES / "Datasheets_options.csv")},
        AuthoredContent(
            option_overrides=(
                OptionOverrideEntry.model_validate(
                    {
                        "datasheet_id": "ds-gf25-override-target",
                        "line": 1,
                        "scope": "unit",
                        "choices": [
                            OptionOverrideChoice(name="ember lance", count=1, grants_weapon_line=1)
                        ],
                    }
                ),
            )
        ),
        [weapon(1, "Ember lance")],
        [],
    )
    assert outcome.state is WargearOptionState.EXTRACTED

    snapshot = factories.snapshot(
        datasheets=[
            factories.datasheet(datasheet_id="ds-gf25-override-target").model_copy(
                update={"wargear_option_state": outcome.state}
            )
        ]
    )
    assert options_resolved_datasheets(snapshot) == 1


def test_an_equipment_override_closing_a_datasheets_only_unparsed_row_counts_as_resolved() -> None:
    composition = (
        CuratedCompositionEntry(line=1, model_name="Marsh Sentry", min_count=3, max_count=3),
    )
    outcome = _equipment(
        "GF25",
        "ds-gf25",
        {EQUIPMENT_TABLE: read_file(FIXTURES / "Datasheets_unit_equipment.csv")},
        AuthoredContent(
            equipment_overrides=(
                EquipmentOverrideEntry.model_validate(
                    {
                        "datasheet_id": "ds-gf25",
                        "line": 1,
                        "applies_to": "unit",
                        "items": [EquipmentOverrideItem(item_name="ember lance", count=1)],
                    }
                ),
            )
        ),
        composition,
        (weapon(1, "Ember lance"),),
    )
    assert outcome.state is DefaultEquipmentState.EXTRACTED

    snapshot = factories.snapshot(
        datasheets=[
            factories.datasheet(datasheet_id="ds-gf25").model_copy(
                update={"default_equipment_state": outcome.state}
            )
        ]
    )
    assert default_equipment_resolved_datasheets(snapshot) == 1
