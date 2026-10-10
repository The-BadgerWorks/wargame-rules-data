# AI-Assisted: Claude Code (model: claude-sonnet-5) - 2026-10-09 pipeline P3 task 3 (spec §4.2
# P4b): implemented `derive_line_scopes`, the build-time derivation of
# `CuratedOptionGroup.eligible_composition_lines` from the REPLACED items an option group's
# choices name and the line-resolved default-equipment groups that carry them.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - final review C1/I4: withhold on any
# datasheet whose default loadout is not fully known (a required `default_equipment_state`
# parameter, plus every model-group equipment group's own `composition_line` resolved), and
# removed the unit-wide union (`unit_wide_items`) -- standing rule 10, measured zero on the
# published tree.
"""Derive which composition lines a wargear option group is eligible on.

An option group's `scope` stays whatever `004`/`006` already resolved it to -- `unit`, `model`,
or `per_n_models` -- and this module adds nothing to that closed vocabulary (spec §4.2 P4b: a
fourth member would be a MAJOR break wearing an additive costume, same reasoning as the three
eligibility columns `006` already carries beside it). What this module adds is a narrower,
*derived* fact: which of a multi-model unit's composition lines actually carry every item a
group's choices replace, so an app showing a per-model option can hide it on a row that could
never legally take it.

**Preconditions (final review C1, controller ruling, grounded in spec §0 ruling 4 -- "where the
pipeline cannot derive it, the app falls back")**: a datasheet's option groups get
`eligible_composition_lines` ONLY when its default loadout is **fully known**, meaning BOTH:

* its `default_equipment_state` is `DefaultEquipmentState.EXTRACTED` (every sentence parsed), AND
* no equipment group that applies to a model group has `composition_line is None` (every
  model-group sentence resolved to exactly one line).

Otherwise every option group on that datasheet keeps `()` -- the same "report, not guess"
discipline as everything else this module derives, now applied to the datasheet as a whole
rather than only to one group's own candidate lines. A datasheet with a mixed-resolution loadout
(one model group resolved, a sibling unresolved) is exactly the case this precondition withholds
on: the old per-group rule could leave an unresolved model's legal options invisible to an app
that trusted the published list, which is the wrong side of the fallback ruling to be on.

**Within a fully-known datasheet, the per-line rule is unchanged**:

* ``R`` is every item named with role ``REPLACED`` across the group's own choices (there may be
  more than one choice on a group, and a choice may replace more than one item).
* A composition line ``L`` is a *candidate* only when at least one of the datasheet's own
  equipment groups resolved to it (``composition_line == L``).
* ``L``'s default loadout is the items of every equipment group whose ``composition_line == L``.
  A unit-wide equipment group (``applies_to == unit``) never joins any line's loadout here --
  measured zero (final review I4, standing rule 10): no datasheet on the published tree carries
  both a unit-wide equipment group and a line-resolved one, so a line's loadout is exactly the
  items of the equipment groups resolved to that line, nothing added from elsewhere.
* ``L`` is eligible when its loadout carries **every** member of ``R``. Matching one ``R`` item
  against one loadout item is by ``weapon_line`` when **both** sides carry one, otherwise by
  :func:`~pipeline.normalize.names.normalize_name` of the two item names.
* The result is empty when ``R`` is empty, when the datasheet has no candidate line at all, or
  when no candidate line's loadout covers every member of ``R``.

**This is narrower than spec §4.2 P4b's wording, in two declared ways, both pending the Owner**:
it withholds on any datasheet whose loadout is not fully known (spec §0 ruling 4), and it does
not add unit-wide groups to a line's loadout (measured zero, standing rule 10).

Groups are returned in input order; nothing but `eligible_composition_lines` changes on any of
them.
"""

from __future__ import annotations

from collections.abc import Sequence

from pipeline.models.curated import (
    CuratedEquipmentGroup,
    CuratedEquipmentItem,
    CuratedOptionChoice,
    CuratedOptionChoiceItem,
    CuratedOptionGroup,
    DefaultEquipmentState,
    EquipmentAppliesTo,
    OptionItemRole,
)
from pipeline.normalize.names import normalize_name


def _matches(replaced: CuratedOptionChoiceItem, carried: CuratedEquipmentItem) -> bool:
    """One `R` item against one loadout item, per spec §4.2 P4b's matching rule.

    By `weapon_line` when BOTH sides carry one -- the stronger, link-based identity. Otherwise by
    `normalize_name` of the two item names, so a differing weapon line on an otherwise
    same-named pair does NOT match: matching only ever strengthens from name to weapon_line, it
    never falls back from a weapon_line mismatch to a name match.
    """
    if replaced.weapon_line is not None and carried.weapon_line is not None:
        return replaced.weapon_line == carried.weapon_line
    return normalize_name(replaced.item_name) == normalize_name(carried.item_name)


def _default_loadout_fully_known(
    equipment_groups: Sequence[CuratedEquipmentGroup],
    default_equipment_state: DefaultEquipmentState | None,
) -> bool:
    """Final review C1's two-part precondition, checked together so neither half can be applied
    without the other."""
    if default_equipment_state is not DefaultEquipmentState.EXTRACTED:
        return False
    return not any(
        equipment_group.composition_line is None
        for equipment_group in equipment_groups
        if equipment_group.applies_to is EquipmentAppliesTo.MODEL_GROUP
    )


def derive_line_scopes(
    *,
    option_groups: Sequence[CuratedOptionGroup],
    option_choices: Sequence[CuratedOptionChoice],
    equipment_groups: Sequence[CuratedEquipmentGroup],
    default_equipment_state: DefaultEquipmentState | None,
) -> list[CuratedOptionGroup]:
    """Spec §4.2 P4b. See the module docstring for the derivation this function implements."""
    if not _default_loadout_fully_known(equipment_groups, default_equipment_state):
        return list(option_groups)

    line_items: dict[int, list[CuratedEquipmentItem]] = {}
    for equipment_group in equipment_groups:
        if equipment_group.composition_line is None:
            continue
        line_items.setdefault(equipment_group.composition_line, []).extend(equipment_group.items)

    results: list[CuratedOptionGroup] = []
    for option_group in option_groups:
        replaced_items = [
            item
            for choice in option_choices
            if choice.group_id == option_group.id
            for item in choice.items
            if item.role is OptionItemRole.REPLACED
        ]
        if not replaced_items or not line_items:
            results.append(option_group)
            continue

        eligible = [
            line
            for line, own_items in sorted(line_items.items())
            if all(
                any(_matches(replaced, carried) for carried in own_items)
                for replaced in replaced_items
            )
        ]

        if eligible:
            results.append(
                option_group.model_copy(update={"eligible_composition_lines": tuple(eligible)})
            )
        else:
            results.append(option_group)
    return results
