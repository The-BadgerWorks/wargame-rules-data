# AI-Assisted: Claude Code (model: claude-sonnet-5) - 2026-10-09 pipeline P3 task 3 (spec §4.2
# P4b): implemented `derive_line_scopes`, the build-time derivation of
# `CuratedOptionGroup.eligible_composition_lines` from the REPLACED items an option group's
# choices name and the line-resolved default-equipment groups that carry them.
"""Derive which composition lines a wargear option group is eligible on.

An option group's `scope` stays whatever `004`/`006` already resolved it to -- `unit`, `model`,
or `per_n_models` -- and this module adds nothing to that closed vocabulary (spec §4.2 P4b: a
fourth member would be a MAJOR break wearing an additive costume, same reasoning as the three
eligibility columns `006` already carries beside it). What this module adds is a narrower,
*derived* fact: which of a multi-model unit's composition lines actually carry every item a
group's choices replace, so an app showing a per-model option can hide it on a row that could
never legally take it.

**The derivation, exactly** (spec §4.2 P4b, Owner-ruling-overridden terms):

* ``R`` is every item named with role ``REPLACED`` across the group's own choices (there may be
  more than one choice on a group, and a choice may replace more than one item).
* A composition line ``L`` is a *candidate* only when at least one of the datasheet's own
  equipment groups resolved to it (``composition_line == L``). A datasheet with no line-resolved
  equipment group at all has no candidates, and a unit-wide equipment group never manufactures one
  by itself.
* ``L``'s default loadout is the items of every equipment group whose ``composition_line == L``,
  **plus** the items of every equipment group that applies to the whole unit
  (``applies_to == unit``, no model name) -- a unit-wide sentence's items sit on every model's
  loadout, line-resolved or not.
* ``L`` is eligible when its loadout carries **every** member of ``R``. Matching one ``R`` item
  against one loadout item is by ``weapon_line`` when **both** sides carry one, otherwise by
  :func:`~pipeline.normalize.names.normalize_name` of the two item names.
* The result is empty when ``R`` is empty, when the datasheet has no candidate line at all, or
  when no candidate line's loadout covers every member of ``R``. Never guessed, same "report, not
  guess" discipline as every other derived link in this bundle.

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


def derive_line_scopes(
    *,
    option_groups: Sequence[CuratedOptionGroup],
    option_choices: Sequence[CuratedOptionChoice],
    equipment_groups: Sequence[CuratedEquipmentGroup],
) -> list[CuratedOptionGroup]:
    """Spec §4.2 P4b. See the module docstring for the derivation this function implements."""
    unit_wide_items: list[CuratedEquipmentItem] = [
        item
        for equipment_group in equipment_groups
        if equipment_group.applies_to is EquipmentAppliesTo.UNIT
        for item in equipment_group.items
    ]
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
                any(_matches(replaced, carried) for carried in (*own_items, *unit_wide_items))
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
