# AI-Assisted: Claude Code (model: claude-opus-5) - The one loadout-extended snapshot Phase 5's
# four proofs share (006 tasks T033-T035, T042): the 004-enriched fixture with every 006 addition
# layered on top -- all three new arrays non-empty, all four new columns set -- so "additive" is
# proven against a bundle that actually carries the additions rather than against an empty one.
"""`004`'s enriched snapshot, plus **every** addition `006-unit-loadout-fidelity` makes.

`tests/contract/enrichment_bundle.py` did this job for `004` and is deliberately left alone: its
`enriched_snapshot()` is the *input* here, extended rather than forked, so the two fixtures can
never drift into disagreeing about what a Fen Warden is. Everything `004`'s proofs assert about
that bundle keeps holding, and everything below is strictly additional — which is the same claim
the schema makes, made in the fixture.

Density is the point, exactly as it was for `004`. An ingestor ignores an empty array by accident
as readily as by design, so the extended snapshot carries:

* a **multi-item swap** — two items replaced, two granted, and therefore *no* singular
  `grants_weapon_line` / `replaces_weapon_line` at all, which is the truncation this feature
  exists to remove (contract §2.1, guarantee 13);
* a **single-item choice** whose lone `granted` item mirrors the `grants_weapon_line` `004`
  already publishes — guarantee 12's redundancy, the invariant that makes the consumer's read
  uniform;
* an **unlinked item** whose name matches no weapon line, shipping beside a linked sibling
  (FR-007);
* an **eligibility-scoped group** carrying all three of `eligible_model_name`,
  `eligible_max_count` and `is_per_model`, on a group whose `scope` stays `unit` — because
  `scope` is a closed set a consumer validates, and a fourth member would be a MAJOR break
  wearing an additive costume;
* both `applies_to` codes for default equipment, one with a resolved `composition_line` and one
  **unit**-wide sentence with none; and
* both a `partial` and an `extracted` `default_equipment_state`.

Everything here is invented, like every fixture in this repository.

**The pricing is untouched, and that is load-bearing.** :data:`~tests.contract.enrichment_bundle.
EXERCISE_ARMY` and its total are re-exported unchanged, so `tests/publication/
test_consumer_compat_loadout.py` can compare a loadout-extended run against a stripped one and
know that any difference came from the additions rather than from the fixture having moved.
"""

from __future__ import annotations

from pipeline.models.curated import (
    CuratedDatasheet,
    CuratedEquipmentGroup,
    CuratedEquipmentItem,
    CuratedOptionChoice,
    CuratedOptionChoiceItem,
    CuratedOptionGroup,
    CuratedSnapshot,
    CuratedWeaponLine,
    DefaultEquipmentState,
    EquipmentAppliesTo,
    OptionItemRole,
    OptionScope,
)
from tests.contract.enrichment_bundle import (  # noqa: F401 - re-exported for the compat proof
    EXERCISE_ARMY,
    EXERCISE_ARMY_TOTAL,
    enriched_snapshot,
)

#: The two weapon lines the multi-item swap grants. Added to the Warden rather than reusing its
#: existing two, so the swap has a genuinely distinct pair on each side and a per-item link can
#: be told apart from a coincidence.
GRANTED_WEAPON_LINES = (3, 4)


def _weapon(line: int, name: str) -> CuratedWeaponLine:
    return CuratedWeaponLine(
        line=line,
        name=name,
        is_melee=False,
        range='18"',
        attacks="3",
        skill="3+",
        strength="4",
        armour_penetration="-1",
        damage="1",
    )


def _warden_option_groups(existing: list[CuratedOptionGroup]) -> list[CuratedOptionGroup]:
    """`004`'s two groups, one of them now eligibility-scoped, plus the multi-item swap's group.

    The scoped group keeps ``scope = unit``. That is the truthful coarse reading a `004`-era
    consumer already knows how to render, and the restriction rides in the three new columns
    beside it — which is precisely why they are columns and not a new `scope` member.
    """
    scoped = existing[0].model_copy(
        update={
            "eligible_model_name": "Fen Warden Prime",
            "eligible_max_count": 1,
            "is_per_model": True,
        }
    )
    swap = CuratedOptionGroup(
        id="og-fen-warden-3",
        line=3,
        scope=OptionScope.UNIT,
        min_choices=0,
        max_choices=1,
    )
    return [scoped, *existing[1:], swap]


def _warden_option_choices(existing: list[CuratedOptionChoice]) -> list[CuratedOptionChoice]:
    """The three `004` choices, each now carrying its items, plus the multi-item swap.

    Not one of the three has its ``name`` or ``count`` rewritten — the O1 Ruling made literal.
    What changes is what sits *beside* them.
    """
    by_id = {choice.id: choice for choice in existing}

    banner = by_id["oc-fen-warden-1-2"].model_copy(
        update={
            # Granted, and deliberately **unlinked**: no weapon line is named "Warden banner",
            # so the item ships with no `weaponLine` and the choice keeps the absent
            # `grants_weapon_line` it has today. An unlinked item is published, never dropped.
            "items": (
                CuratedOptionChoiceItem(
                    role=OptionItemRole.GRANTED, item_index=1, item_name="Warden banner", count=1
                ),
            )
        }
    )
    lance = by_id["oc-fen-warden-2-1"].model_copy(
        update={
            # Guarantee 12: a sole granted item mirrors the choice's own `grants_weapon_line`.
            # The redundancy is the invariant, not an accident of this fixture.
            "items": (
                CuratedOptionChoiceItem(
                    role=OptionItemRole.GRANTED,
                    item_index=1,
                    item_name="Marsh lance",
                    count=1,
                    weapon_line=2,
                ),
            )
        }
    )
    swap = CuratedOptionChoice(
        id="oc-fen-warden-3-1",
        group_id="og-fen-warden-3",
        # The name stays the conflated label the source states. Decomposing it into items is
        # what this feature does; rewriting it is what the O1 Ruling forbids.
        name="Fen glaive and marsh lance",
        # No `grants_weapon_line`, no `replaces_weapon_line`, and no fabricated pick from the
        # first item: two items on a side means the singular field is absent (guarantee 13).
        items=(
            CuratedOptionChoiceItem(
                role=OptionItemRole.GRANTED,
                item_index=1,
                item_name="Tide hook",
                count=1,
                weapon_line=3,
            ),
            CuratedOptionChoiceItem(
                role=OptionItemRole.GRANTED,
                item_index=2,
                item_name="Reed carbine",
                count=2,
                weapon_line=4,
            ),
            CuratedOptionChoiceItem(
                role=OptionItemRole.REPLACED,
                item_index=1,
                item_name="Fen glaive",
                weapon_line=1,
            ),
            CuratedOptionChoiceItem(
                role=OptionItemRole.REPLACED,
                item_index=2,
                item_name="Marsh lance",
                weapon_line=2,
            ),
        ),
    )
    return [by_id["oc-fen-warden-1-1"], banner, lance, swap]


def _warden_equipment() -> list[CuratedEquipmentGroup]:
    """Two sentences: one unit-wide with no composition link, one resolved to a named group."""
    return [
        CuratedEquipmentGroup(
            id="eq-fen-warden-1",
            line=1,
            # `unit` with **no** `composition_line`, which is the case a nullable foreign key
            # alone could not tell from "a group I could not identify" (FR-015).
            applies_to=EquipmentAppliesTo.UNIT,
            items=(
                CuratedEquipmentItem(item_index=1, item_name="Fen glaive", count=1, weapon_line=1),
            ),
        ),
        CuratedEquipmentGroup(
            id="eq-fen-warden-2",
            line=2,
            applies_to=EquipmentAppliesTo.MODEL_GROUP,
            model_name="Fen Warden Prime",
            # Resolved by NAME against the datasheet's own composition rows. The Prime is
            # composition line 1, which is not the line its *sentence* ordinal would suggest —
            # deliberately, so a positional pairing would produce the wrong answer here.
            composition_line=1,
            items=(
                CuratedEquipmentItem(item_index=1, item_name="Marsh lance", count=1, weapon_line=2),
            ),
        ),
    ]


def _rider_equipment() -> list[CuratedEquipmentGroup]:
    """One sentence, one linked item and one that matches nothing and ships anyway (FR-014)."""
    return [
        CuratedEquipmentGroup(
            id="eq-thornlight-rider-1",
            line=1,
            applies_to=EquipmentAppliesTo.MODEL_GROUP,
            model_name="Thornlight Rider",
            composition_line=1,
            items=(
                CuratedEquipmentItem(
                    item_index=1, item_name="Thornlight lance", count=1, weapon_line=1
                ),
                # No weapon line is named this: the item ships unlinked with
                # `EQP-ITEM-UNLINKED`, and neither its sibling nor its group is discarded.
                CuratedEquipmentItem(item_index=2, item_name="Duskrail carbine", count=2),
            ),
        )
    ]


def _extend_warden(datasheet: CuratedDatasheet) -> CuratedDatasheet:
    return datasheet.model_copy(
        update={
            "weapons": [
                *datasheet.weapons,
                _weapon(GRANTED_WEAPON_LINES[0], "Tide hook"),
                _weapon(GRANTED_WEAPON_LINES[1], "Reed carbine"),
            ],
            "option_groups": _warden_option_groups(list(datasheet.option_groups)),
            "option_choices": _warden_option_choices(list(datasheet.option_choices)),
            "equipment_groups": _warden_equipment(),
            "default_equipment_state": DefaultEquipmentState.EXTRACTED,
        }
    )


def _extend_rider(datasheet: CuratedDatasheet) -> CuratedDatasheet:
    return datasheet.model_copy(
        update={
            "equipment_groups": _rider_equipment(),
            # `partial`, not `none`: a second sentence on this card did not resolve, and what
            # did resolve still ships. The distinction is the whole reason the column exists.
            "default_equipment_state": DefaultEquipmentState.PARTIAL,
        }
    )


def loadout_snapshot() -> CuratedSnapshot:
    """`004`'s enriched snapshot with every `006` addition layered on top."""
    snapshot = enriched_snapshot()
    extend = {"ds-fen-warden": _extend_warden, "ds-thornlight-rider": _extend_rider}
    return snapshot.model_copy(
        update={
            "datasheets": [
                extend[datasheet.datasheet_id](datasheet) for datasheet in snapshot.datasheets
            ]
        }
    )
