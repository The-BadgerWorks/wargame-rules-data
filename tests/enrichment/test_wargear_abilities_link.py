# AI-Assisted: Claude Code (model: Claude Sonnet 5) - 010 R13 task 3: assembly-level tests for
# `pipeline.curate.assemble._link_wargear_abilities`, the post-pass run in both `_datasheet_for`
# and `_detail_only_datasheet` after `_option_structure` and `_equipment` return.
"""010 R13 task 3: the item-to-wargear-ability post-pass, proven against `assemble.py` itself.

Four things this test proves:

1. A single unambiguous match links, and the match is faction-scoped.
2. A curator-authored item -- one built by `_authored_items`, not the parsed-row path -- links
   on the identical terms, because it is already part of the items `_option_structure` returns
   before the post-pass runs; there is no separate authored-only code path to forget.
3. A two-or-more match is the advisory `WGA-LINK-AMBIGUOUS`, with the item name and the sorted
   candidate ids, and the item ships unlinked.
4. `emit_bundle` carries `wargearAbilityId` only on the row that actually linked.
"""

from __future__ import annotations

from pipeline.curate.assemble import _authored_items, _link_wargear_abilities
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
