# AI-Assisted: Claude Code (model: Claude Sonnet 5) - New test for 010 R13 task 2: the curated
# `wargearAbilities` bundle table, the `WGA-DUPLICATE` collision guard, and the `AUT-DANGLING-REF`
# path for a wargear ability naming a faction the curated snapshot does not contain.
"""010 R13 task 2: curated table and emission.

Three things this task proves, none of them owned by task 1 (the authored model) or task 3 (the
item linker, not yet built):

1. `emit_bundle` carries a `wargearAbilities` row per curated entry, sorted by `id`, with
   `aliases` dropped at the boundary (it exists only to help the linker resolve a name).
2. Two authored entries computing the same id collide as the blocking `WGA-DUPLICATE`, and
   **neither** enters the curated snapshot -- proven directly against
   `pipeline.curate.assemble._wargear_abilities`, the function `assemble()` calls near the top,
   before any datasheet is built.
3. A wargear ability naming a faction the curated snapshot does not contain is the existing V9
   `AUT-DANGLING-REF`, reached through `authored_entity_refs` exactly as a stale composition or
   option override already is -- no new `WGA-UNKNOWN-FACTION` code is minted.
"""

from __future__ import annotations

from pipeline.curate.assemble import _wargear_abilities
from pipeline.curate.authored import AuthoredContent
from pipeline.models.authored import WargearAbilityEntry
from pipeline.models.curated import CuratedWargearAbility
from pipeline.report.catalogue import CATALOGUE
from pipeline.validate.refs import check_authored_references
from tests import factories

ENTRY = {
    "faction_id": "f-emberwrights",
    "name": "Hover Limpet",
    "aliases": ["hover limpet (one per unit)"],
    "summary": "Placeholder: the bearer's unit ignores one placeholder modifier.",
    "review_state": "approved",
    "reviewed_by": "owner-placeholder",
    "reviewed_at": "2026-09-16",
}


def _entry(**overrides: object) -> WargearAbilityEntry:
    return WargearAbilityEntry.model_validate({**ENTRY, **overrides})


# --- emission: the bundle row, and aliases dropped -----------------------------------------------


def test_emit_bundle_carries_one_wargear_ability_row_with_aliases_dropped() -> None:
    ability = CuratedWargearAbility(
        id="wga-emberwrights-hover-limpet",
        faction_id="f-emberwrights",
        name="Hover Limpet",
        summary="Placeholder: the bearer's unit ignores one placeholder modifier.",
        aliases=("hover limpet (one per unit)",),
    )
    from pipeline.build.bundle_emit import emit_bundle

    bundle = emit_bundle(
        factories.snapshot(wargear_abilities={ability.id: ability}), factories.meta()
    )

    assert bundle["wargearAbilities"] == [
        {
            "id": "wga-emberwrights-hover-limpet",
            "factionId": "f-emberwrights",
            "name": "Hover Limpet",
            "summary": "Placeholder: the bearer's unit ignores one placeholder modifier.",
        }
    ]
    assert "aliases" not in bundle["wargearAbilities"][0]


def test_emit_bundle_sorts_wargear_abilities_by_id() -> None:
    from pipeline.build.bundle_emit import emit_bundle

    second = CuratedWargearAbility(
        id="wga-emberwrights-second",
        faction_id="f-emberwrights",
        name="Second Placeholder",
        summary="Placeholder: a second invented ability.",
    )
    first = CuratedWargearAbility(
        id="wga-emberwrights-first",
        faction_id="f-emberwrights",
        name="First Placeholder",
        summary="Placeholder: a first invented ability.",
    )
    bundle = emit_bundle(
        factories.snapshot(wargear_abilities={second.id: second, first.id: first}),
        factories.meta(),
    )

    assert [row["id"] for row in bundle["wargearAbilities"]] == [
        "wga-emberwrights-first",
        "wga-emberwrights-second",
    ]


# --- WGA-DUPLICATE: two entries computing the same id ----------------------------------------


def test_two_entries_with_the_same_id_raise_wga_duplicate_and_neither_is_curated() -> None:
    authored = AuthoredContent(
        wargear_abilities=(
            _entry(summary="Placeholder: the first colliding entry's own text."),
            _entry(summary="Placeholder: the second colliding entry's own text."),
        )
    )

    result, findings = _wargear_abilities(authored)

    assert result == {}
    codes = [f.finding_code for f in findings]
    assert codes == ["WGA-DUPLICATE"]
    assert findings[0].detail["id"] == "wga-emberwrights-hover-limpet"
    assert findings[0].detail["count"] == 2
    assert CATALOGUE["WGA-DUPLICATE"].severity.value == "blocking"


def test_a_non_colliding_entry_is_curated_and_raises_nothing() -> None:
    authored = AuthoredContent(wargear_abilities=(_entry(),))

    result, findings = _wargear_abilities(authored)

    assert findings == []
    assert set(result) == {"wga-emberwrights-hover-limpet"}
    curated = result["wga-emberwrights-hover-limpet"]
    assert curated.faction_id == "f-emberwrights"
    assert curated.name == "Hover Limpet"
    assert curated.aliases == ("hover limpet (one per unit)",)


# --- AUT-DANGLING-REF: an unknown faction_id, through the existing V9 path -------------------


def test_a_wargear_ability_naming_an_unknown_faction_is_aut_dangling_ref() -> None:
    authored = AuthoredContent(wargear_abilities=(_entry(faction_id="f-does-not-exist"),))
    snapshot = factories.snapshot()  # factions=[faction()] -> only "f-emberwrights"

    findings = check_authored_references(snapshot, authored)
    dangling = [f for f in findings if f.finding_code == "AUT-DANGLING-REF"]

    assert len(dangling) == 1
    assert dangling[0].detail == {
        "file_name": "wargear-abilities.json",
        "field": "faction_id",
        "missing_id": "f-does-not-exist",
    }


def test_a_wargear_ability_naming_a_known_faction_raises_no_dangling_ref() -> None:
    authored = AuthoredContent(wargear_abilities=(_entry(),))
    snapshot = factories.snapshot()

    findings = check_authored_references(snapshot, authored)

    assert [f for f in findings if f.finding_code == "AUT-DANGLING-REF"] == []
