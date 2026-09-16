# AI-Assisted: Claude Code (model: Claude Sonnet 5) - 010 R13 task 3: assembly-level tests for
# `pipeline.curate.assemble._link_wargear_abilities`, the post-pass run in both `_datasheet_for`
# and `_detail_only_datasheet` after `_option_structure` and `_equipment` return.
# AI-Assisted: Claude Code (model: Claude Sonnet 5) - 010 R13 task 3 review fix (Important
# finding): added the wiring tests every prior test in this file skipped -- they all called
# `_link_wargear_abilities` directly, so nothing exercised the two real call sites and nothing
# would fail if a future edit threaded the wrong `faction_id`, dropped `wargear_abilities`, or
# discarded the post-pass's return instead of reassigning `options.choices`/`equipment.groups`.
"""010 R13 task 3: the item-to-wargear-ability post-pass, proven against `assemble.py` itself.

Five things this test proves:

1. A single unambiguous match links, and the match is faction-scoped.
2. A curator-authored item -- one built by `_authored_items`, not the parsed-row path -- links
   on the identical terms, because it is already part of the items `_option_structure` returns
   before the post-pass runs; there is no separate authored-only code path to forget.
3. A two-or-more match is the advisory `WGA-LINK-AMBIGUOUS`, with the item name and the sorted
   candidate ids, and the item ships unlinked.
4. `emit_bundle` carries `wargearAbilityId` only on the row that actually linked.
5. `_datasheet_for` and `_detail_only_datasheet` -- the two real call sites, driven end to end
   over a small CSV export -- actually thread `wargear_abilities` through, pass the datasheet's
   own `faction_id`, and reassign `options.choices`/`equipment.groups` from the post-pass's
   return rather than discarding it.
"""

from __future__ import annotations

from collections.abc import Mapping

import pytest

from pipeline.acquire.detail_source import read_export_payloads
from pipeline.acquire.fixtures import FixturePayload
from pipeline.curate.assemble import (
    _authored_items,
    _datasheet_for,
    _detail_only_datasheet,
    _link_wargear_abilities,
    _provenance,
)
from pipeline.curate.authored import AuthoredContent
from pipeline.curate.summaries import ability_name_index
from pipeline.models.authored import OptionOverrideChoice
from pipeline.models.curated import (
    CuratedEquipmentGroup,
    CuratedEquipmentItem,
    CuratedOptionChoice,
    CuratedOptionChoiceItem,
    CuratedWargearAbility,
    EquipmentAppliesTo,
    OptionItemRole,
)
from pipeline.models.source import SourceAcquisition, SourceKey
from pipeline.parse.wahapedia_csv import CsvReadResult
from pipeline.reconcile.identity import IdRegistry
from pipeline.reconcile.match import UnitMatch

DATASHEET = "ds-fen-warden"
FACTION = "f-ex"

ENTRY = CuratedWargearAbility(
    id="wga-ex-hover-limpet",
    faction_id=FACTION,
    name="Hover Limpet",
    summary="placeholder",
)
ENTRY_MK2 = CuratedWargearAbility(
    id="wga-ex-hover-limpet-mk2", faction_id=FACTION, name="Hover Limpet", summary="placeholder"
)
OTHER_FACTION_ENTRY = CuratedWargearAbility(
    id="wga-other-hover-limpet", faction_id="f-other", name="Hover Limpet", summary="placeholder"
)


def _choice(
    item_name: str, *, role: OptionItemRole = OptionItemRole.GRANTED
) -> CuratedOptionChoice:
    return CuratedOptionChoice(
        id="oc-fen-warden-1-1",
        group_id="og-fen-warden-1",
        name=item_name,
        grants_weapon_line=1 if role is OptionItemRole.GRANTED else None,
        replaces_weapon_line=1 if role is OptionItemRole.REPLACED else None,
        items=(CuratedOptionChoiceItem(role=role, item_index=1, item_name=item_name),),
    )


def _equipment_group(item_name: str) -> CuratedEquipmentGroup:
    return CuratedEquipmentGroup(
        id="eq-fen-warden-1",
        line=1,
        applies_to=EquipmentAppliesTo.UNIT,
        items=(CuratedEquipmentItem(item_index=1, item_name=item_name),),
    )


# --- one unambiguous match links, faction-scoped --------------------------------------------


def test_a_single_match_links_the_option_item() -> None:
    choices, groups, findings = _link_wargear_abilities(
        datasheet_id=DATASHEET,
        faction_id=FACTION,
        choices=[_choice("Hover Limpet")],
        equipment_groups=[],
        wargear_abilities=[ENTRY, OTHER_FACTION_ENTRY],
    )

    assert findings == []
    assert choices[0].items[0].wargear_ability_id == "wga-ex-hover-limpet"


def test_a_single_match_links_the_equipment_item() -> None:
    choices, groups, findings = _link_wargear_abilities(
        datasheet_id=DATASHEET,
        faction_id=FACTION,
        choices=[],
        equipment_groups=[_equipment_group("Hover Limpet")],
        wargear_abilities=[ENTRY],
    )

    assert findings == []
    assert groups[0].items[0].wargear_ability_id == "wga-ex-hover-limpet"


def test_no_entries_for_the_faction_leaves_the_item_unlinked_with_no_finding() -> None:
    choices, _groups, findings = _link_wargear_abilities(
        datasheet_id=DATASHEET,
        faction_id=FACTION,
        choices=[_choice("Hover Limpet")],
        equipment_groups=[],
        wargear_abilities=[OTHER_FACTION_ENTRY],
    )

    assert findings == []
    assert choices[0].items[0].wargear_ability_id is None


def test_a_weapon_named_item_links_nowhere_and_raises_nothing() -> None:
    choices, _groups, findings = _link_wargear_abilities(
        datasheet_id=DATASHEET,
        faction_id=FACTION,
        choices=[_choice("Fen glaive")],
        equipment_groups=[],
        wargear_abilities=[ENTRY],
    )

    assert findings == []
    assert choices[0].items[0].wargear_ability_id is None


# --- a curator-authored item links on the identical terms ------------------------------------


def test_a_curator_authored_option_item_links() -> None:
    """`_authored_items` builds the item; the post-pass covers it with no separate code path."""
    override = OptionOverrideChoice(name="Hover Limpet")
    items = _authored_items(override)
    authored_choice = CuratedOptionChoice(
        id="oc-fen-warden-1-1", group_id="og-fen-warden-1", name="Hover Limpet", items=items
    )

    choices, _groups, findings = _link_wargear_abilities(
        datasheet_id=DATASHEET,
        faction_id=FACTION,
        choices=[authored_choice],
        equipment_groups=[],
        wargear_abilities=[ENTRY],
    )

    assert findings == []
    assert choices[0].items[0].wargear_ability_id == "wga-ex-hover-limpet"


# --- two-or-more matches: WGA-LINK-AMBIGUOUS, item ships unlinked ----------------------------


def test_two_matches_raise_wga_link_ambiguous_and_ship_unlinked() -> None:
    choices, _groups, findings = _link_wargear_abilities(
        datasheet_id=DATASHEET,
        faction_id=FACTION,
        choices=[_choice("Hover Limpet")],
        equipment_groups=[],
        wargear_abilities=[ENTRY, ENTRY_MK2],
    )

    assert [f.finding_code for f in findings] == ["WGA-LINK-AMBIGUOUS"]
    assert list(findings[0].entity_refs) == [DATASHEET]
    assert findings[0].detail["item_name"] == "Hover Limpet"
    assert findings[0].detail["candidate_ids"] == sorted(
        ["wga-ex-hover-limpet", "wga-ex-hover-limpet-mk2"]
    )
    assert choices[0].items[0].wargear_ability_id is None


def test_two_matches_on_an_equipment_item_raise_the_same_finding() -> None:
    _choices, groups, findings = _link_wargear_abilities(
        datasheet_id=DATASHEET,
        faction_id=FACTION,
        choices=[],
        equipment_groups=[_equipment_group("Hover Limpet")],
        wargear_abilities=[ENTRY, ENTRY_MK2],
    )

    assert [f.finding_code for f in findings] == ["WGA-LINK-AMBIGUOUS"]
    assert groups[0].items[0].wargear_ability_id is None


# --- emission: wargearAbilityId present only where it linked ---------------------------------


def test_emit_bundle_carries_wargear_ability_id_only_where_linked() -> None:
    from pipeline.build.bundle_emit import emit_bundle
    from tests import factories

    linked_item = CuratedOptionChoiceItem(
        role=OptionItemRole.GRANTED,
        item_index=1,
        item_name="Hover Limpet",
        wargear_ability_id="wga-ex-hover-limpet",
    )
    unlinked_item = CuratedOptionChoiceItem(
        role=OptionItemRole.GRANTED, item_index=1, item_name="Fen glaive"
    )
    linked_choice = CuratedOptionChoice(
        id="oc-fen-warden-1-1",
        group_id="og-fen-warden-1",
        name="Hover Limpet",
        grants_weapon_line=1,
        items=(linked_item,),
    )
    unlinked_choice = CuratedOptionChoice(
        id="oc-fen-warden-2-1",
        group_id="og-fen-warden-2",
        name="Fen glaive",
        grants_weapon_line=1,
        items=(unlinked_item,),
    )
    datasheet = factories.datasheet(DATASHEET, faction_id=FACTION).model_copy(
        update={
            "option_groups": [],
            "option_choices": [linked_choice, unlinked_choice],
        }
    )
    bundle = emit_bundle(factories.snapshot(datasheets=[datasheet]), factories.meta())

    rows = {row["choiceId"]: row for row in bundle["datasheetOptionChoiceItems"]}
    assert rows["oc-fen-warden-1-1"]["wargearAbilityId"] == "wga-ex-hover-limpet"
    assert "wargearAbilityId" not in rows["oc-fen-warden-2-1"]


# --- the real call sites: `_datasheet_for` and `_detail_only_datasheet` ----------------------
#
# Every test above calls `_link_wargear_abilities` directly, which proves the post-pass itself
# is correct but proves nothing about its two callers: whether `wargear_abilities` actually
# reaches the call, whether the datasheet's own `faction_id` (and not some other value) is what
# gets passed, and whether the caller reassigns `options.choices` / `equipment.groups` from the
# post-pass's return rather than discarding it. This section drives both real functions over a
# small invented CSV export -- the same `read_export_payloads` pattern
# `tests/enrichment/test_us2_independent.py` uses -- so a regression at either call site fails
# here even though `_link_wargear_abilities` itself is untouched.

WIRING_FACTION = "f-glimmerfen-covenant"
WIRING_WRONG_FACTION = "f-thornlight-chorus"

WIRING_ENTRY = CuratedWargearAbility(
    id="wga-glimmerfen-covenant-hover-limpet",
    faction_id=WIRING_FACTION,
    name="Hover Limpet",
    summary="placeholder",
)
WIRING_WRONG_FACTION_ENTRY = CuratedWargearAbility(
    id="wga-thornlight-chorus-hover-limpet",
    faction_id=WIRING_WRONG_FACTION,
    name="Hover Limpet",
    summary="placeholder",
)

#: One invented datasheet: a default-equipment sentence naming "hover limpet" (for the
#: `_equipment` / `equipment.groups` half) and a wargear-option row granting the same name (for
#: the `_option_structure` / `options.choices` half), so one fixture drives both call sites.
_WIRING_DATASHEETS = (
    "id|name|faction_id|source_id|role|damaged_w|legend|loadout|\n"
    "GF01|Purgeflight Wardens|glimmerfen-covenant|current||||"
    "<b>Every model</b> is equipped with: hover limpet.|\n"
)
_WIRING_MODELS = (
    "datasheet_id|line|name|M|T|Sv|inv_sv|W|Ld|OC|base_size|\n"
    'GF01|1|Purgeflight Adept|6"|3|3+||2|6+|1|(25mm)|\n'
)
_WIRING_WARGEAR = "datasheet_id|line|name|description|type|range|A|BS_WS|S|AP|D|\n"
_WIRING_COMPOSITION = "datasheet_id|line|description|\nGF01|1|1 Purgeflight Adept|\n"
_WIRING_MODEL_COSTS = "datasheet_id|line|description|cost|\nGF01|1|5 models|90|\n"
_WIRING_OPTIONS = (
    "datasheet_id|line|button|description|\n"
    "GF01|1|Wargear Options|This model can be equipped with 1 hover limpet.|\n"
)
_WIRING_EMPTY_TABLES = {
    "Datasheets_keywords.csv": "datasheet_id|keyword|model|is_faction_keyword|\n",
    "Datasheets_abilities.csv": "datasheet_id|line|ability_id|model|name|description|type|\n",
    "Datasheets_leader.csv": "leader_id|attached_id|\n",
    "Abilities.csv": "id|name|legend|faction_id|description|\n",
    "Detachments.csv": "id|faction_id|name|legend|type|\n",
    "Detachment_abilities.csv": "id|detachment_id|name|legend|description|\n",
}


@pytest.fixture(scope="module")
def wiring_detail() -> Mapping[str, CsvReadResult]:
    return read_export_payloads(
        [
            FixturePayload(name="Datasheets.csv", text=_WIRING_DATASHEETS),
            FixturePayload(name="Datasheets_models.csv", text=_WIRING_MODELS),
            FixturePayload(name="Datasheets_wargear.csv", text=_WIRING_WARGEAR),
            FixturePayload(name="Datasheets_unit_composition.csv", text=_WIRING_COMPOSITION),
            FixturePayload(name="Datasheets_models_cost.csv", text=_WIRING_MODEL_COSTS),
            FixturePayload(name="Datasheets_options.csv", text=_WIRING_OPTIONS),
            *(
                FixturePayload(name=name, text=header)
                for name, header in _WIRING_EMPTY_TABLES.items()
            ),
        ]
    )


def _acquisition() -> SourceAcquisition:
    return SourceAcquisition(
        acquisition_id="wahapedia-fixture",
        source_key=SourceKey.WAHAPEDIA,
        source_base_url="https://example.invalid/fixture",
        declared_edition_code="wh40k-11e",
        retrieved_at="2026-08-11T00:00:00Z",
        content_fingerprint="0" * 64,
    )


def _matched_datasheet(
    detail: Mapping[str, CsvReadResult], *, faction_id: str, wargear_abilities: tuple = ()
):
    """One datasheet down `_datasheet_for` -- the matched path -- as `assemble()` drives it."""
    acquisition = _acquisition()
    match = UnitMatch(
        datasheet_id="ds-purgeflight-wardens",
        faction_id=faction_id,
        display_name="Purgeflight Wardens",
        wahapedia_datasheet_id="GF01",
        stage="exact",
    )
    return _datasheet_for(
        match,
        blocks=[],
        detail=detail,
        authored=AuthoredContent(),
        edition_id="ed-wh40k-11e",
        points_acquisition=acquisition,
        provenance=_provenance(acquisition, acquisition, snapshot_edition="wh40k-11e"),
        legends_sources=frozenset(),
        ability_names=ability_name_index(detail),
        wargear_abilities=wargear_abilities,
    )


def _unpriced_datasheet(
    detail: Mapping[str, CsvReadResult], *, faction_id: str, wargear_abilities: tuple = ()
):
    """The same datasheet down `_detail_only_datasheet` -- the unpriced path."""
    acquisition = _acquisition()
    return _detail_only_datasheet(
        "GF01",
        display_name="Purgeflight Wardens",
        faction_id=faction_id,
        detail=detail,
        authored=AuthoredContent(),
        edition_id="ed-wh40k-11e",
        provenance=_provenance(None, acquisition, snapshot_edition="wh40k-11e"),
        registry=IdRegistry(),
        detail_acquisition=acquisition,
        legends_sources=frozenset(),
        ability_names=ability_name_index(detail),
        wargear_abilities=wargear_abilities,
    )


def test_datasheet_for_threads_wargear_abilities_and_links_the_option_item(
    wiring_detail: Mapping[str, CsvReadResult],
) -> None:
    datasheet, _findings = _matched_datasheet(
        wiring_detail, faction_id=WIRING_FACTION, wargear_abilities=(WIRING_ENTRY,)
    )

    (choice,) = datasheet.option_choices
    assert choice.items[0].wargear_ability_id == WIRING_ENTRY.id


def test_datasheet_for_passes_no_wargear_abilities_by_default(
    wiring_detail: Mapping[str, CsvReadResult],
) -> None:
    """The default parameter is `()`, so a caller that forgets to thread it links nothing."""
    datasheet, _findings = _matched_datasheet(wiring_detail, faction_id=WIRING_FACTION)

    (choice,) = datasheet.option_choices
    assert choice.items[0].wargear_ability_id is None


def test_datasheet_for_passes_the_datasheets_own_faction_id_not_some_other_value(
    wiring_detail: Mapping[str, CsvReadResult],
) -> None:
    """An entry in the WRONG faction never links -- proof the real `match.faction_id` governs."""
    datasheet, _findings = _matched_datasheet(
        wiring_detail, faction_id=WIRING_FACTION, wargear_abilities=(WIRING_WRONG_FACTION_ENTRY,)
    )

    (choice,) = datasheet.option_choices
    assert choice.items[0].wargear_ability_id is None


def test_detail_only_datasheet_threads_wargear_abilities_and_links_the_equipment_item(
    wiring_detail: Mapping[str, CsvReadResult],
) -> None:
    datasheet, _findings = _unpriced_datasheet(
        wiring_detail, faction_id=WIRING_FACTION, wargear_abilities=(WIRING_ENTRY,)
    )

    assert datasheet is not None
    (group,) = datasheet.equipment_groups
    assert group.items[0].wargear_ability_id == WIRING_ENTRY.id


def test_detail_only_datasheet_passes_no_wargear_abilities_by_default(
    wiring_detail: Mapping[str, CsvReadResult],
) -> None:
    datasheet, _findings = _unpriced_datasheet(wiring_detail, faction_id=WIRING_FACTION)

    assert datasheet is not None
    (group,) = datasheet.equipment_groups
    assert group.items[0].wargear_ability_id is None
