# AI-Assisted: Claude Code (model: Claude Sonnet 5) - 010 R13 task 3: failing-first tests for
# `wargear_ability_ids_named`, the exact-name, faction-scoped, exactly-one-match join between an
# option/equipment item's name and the curated `wargear_abilities` mapping task 2 built.
"""The item-to-wargear-ability join: exact name, faction-scoped, never guessed.

Mirrors `pipeline.reconcile.options_link.weapon_lines_named` in every respect that matters: the
only comparison allowed is `normalize_name`, so no substring, no fuzzy, and no stripping of
parentheticals. Callers apply `ids[0] if len(ids) == 1 else None`; a two-or-more match is the
advisory `WGA-LINK-AMBIGUOUS`, never a guess.
"""

from __future__ import annotations

from pipeline.models.curated import CuratedWargearAbility
from pipeline.reconcile.wargear_link import wargear_ability_ids_named

A = CuratedWargearAbility(
    id="wga-ex-hover-limpet",
    faction_id="f-ex",
    name="Hover Limpet",
    summary="placeholder",
    aliases=("hover limpet (one per unit)",),
)
B = CuratedWargearAbility(
    id="wga-ex-hover-limpet-mk2", faction_id="f-ex", name="Hover Limpet", summary="placeholder"
)
OTHER = CuratedWargearAbility(
    id="wga-other-hover-limpet", faction_id="f-other", name="Hover Limpet", summary="placeholder"
)


def test_exact_name_links() -> None:
    assert wargear_ability_ids_named("hover limpet", "f-ex", [A, OTHER]) == ["wga-ex-hover-limpet"]


def test_alias_links() -> None:
    assert wargear_ability_ids_named("Hover Limpet (one per unit)", "f-ex", [A]) == [
        "wga-ex-hover-limpet"
    ]


def test_other_faction_never_links() -> None:
    assert wargear_ability_ids_named("hover limpet", "f-ex", [OTHER]) == []


def test_substring_never_links() -> None:
    assert wargear_ability_ids_named("2 hover limpets", "f-ex", [A]) == []


def test_two_matches_are_ambiguous() -> None:
    assert len(wargear_ability_ids_named("hover limpet", "f-ex", [A, B])) == 2
