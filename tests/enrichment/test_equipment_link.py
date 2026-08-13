# AI-Assisted: Claude Code (model: claude-opus-5) - The two equipment joins' contract (006 task
# T026): compositionLine resolved BY NAME and never by ordinal, EQP-GROUP-UNRESOLVED on zero or
# two-or-more matches, and a per-item EQP-ITEM-UNLINKED that discards neither the item's siblings
# nor its group.
"""Two joins the source does not publish, both refusing to guess.

**A sentence to a composition row.** Research D1e measured the pairings and they do not align:
1 331 cards carry one composition line and one sentence, but **195 carry two lines and one
sentence** — so a positional pairing would attach a squad's loadout to its leader on one card in
seven. The link is therefore the same exactly-one-match *name* join
:func:`pipeline.parse.composition_grammar.link_model_line` already performs for composition
itself, and there is deliberately no ordinal fallback for it to fall back to.

**An item to a weapon row.** `004`'s ``OPT-LINK-AMBIGUOUS`` discipline applied to a second class:
exactly one match links, zero or two-or-more ship the item **unlinked** with an advisory, and
neither the item's siblings nor its group is discarded. One ambiguous name in a loadout must not
cost the whole loadout.
"""

from __future__ import annotations

from collections.abc import Sequence

from pipeline.models.curated import (
    CuratedCompositionEntry,
    CuratedEquipmentGroup,
    CuratedEquipmentItem,
    EquipmentAppliesTo,
)
from pipeline.models.findings import Severity
from pipeline.reconcile.equipment_link import link_equipment
from pipeline.report.catalogue import CATALOGUE
from tests.enrichment.conftest import weapon

DATASHEET = "ds-mirebound-choir"

#: Two composition rows, the leader first — the shape 195 cards of the corpus carry, and the one
#: an ordinal pairing gets wrong.
COMPOSITION: Sequence[CuratedCompositionEntry] = (
    CuratedCompositionEntry(line=1, model_name="Mirebound Cantor", min_count=1, max_count=1),
    CuratedCompositionEntry(line=2, model_name="Mirebound Chorister", min_count=4, max_count=9),
)

#: `Tide hammer` appears twice — once ranged, once melee — which is the two-match case, and
#: `Void net` appears not at all, which is the zero-match one.
WEAPONS = (
    weapon(1, "Chime flail"),
    weapon(2, "Tide hammer"),
    weapon(3, "Tide hammer"),
    weapon(4, "Resonance shard"),
)


def group(
    line: int,
    *,
    applies_to: EquipmentAppliesTo = EquipmentAppliesTo.MODEL_GROUP,
    model_name: str | None = "Mirebound Chorister",
    items: Sequence[str] = ("resonance shard",),
) -> CuratedEquipmentGroup:
    return CuratedEquipmentGroup(
        id=f"eq-mirebound-choir-{line}",
        line=line,
        applies_to=applies_to,
        model_name=model_name,
        items=tuple(
            CuratedEquipmentItem(item_index=index, item_name=name)
            for index, name in enumerate(items, start=1)
        ),
    )


def _link(*groups: CuratedEquipmentGroup) -> tuple[list[CuratedEquipmentGroup], list[str]]:
    linked, findings = link_equipment(
        datasheet_id=DATASHEET, groups=groups, composition=COMPOSITION, weapons=WEAPONS
    )
    return linked, [finding.finding_code for finding in findings]


# --- the sentence-to-composition join ----------------------------------------------------------


def test_a_named_subject_resolves_to_the_composition_row_of_that_name() -> None:
    (linked,), codes = _link(group(1, model_name="Mirebound Chorister"))
    assert linked.composition_line == 2
    assert codes == []


def test_the_link_is_by_name_and_never_by_the_sentences_own_ordinal() -> None:
    # Sentence 1 names the SECOND composition row. An ordinal pairing would say 1 — and would be
    # confidently wrong on the leader/squad shape this fixture exists to state.
    (chorister,), _ = _link(group(1, model_name="Mirebound Chorister"))
    (cantor,), _ = _link(group(2, model_name="Mirebound Cantor"))
    assert (chorister.line, chorister.composition_line) == (1, 2)
    assert (cantor.line, cantor.composition_line) == (2, 1)


def test_one_sentence_over_two_composition_rows_is_a_unit_group_with_no_link() -> None:
    # The 195-card shape. `appliesTo = unit` with no `compositionLine` is exactly what the source
    # says, and no finding is raised: nothing failed here.
    (linked,), codes = _link(
        group(1, applies_to=EquipmentAppliesTo.UNIT, model_name=None, items=("chime flail",))
    )
    assert linked.applies_to is EquipmentAppliesTo.UNIT
    assert linked.composition_line is None
    assert codes == []


def test_a_subject_matching_no_composition_row_is_reported_and_left_unlinked() -> None:
    (linked,), codes = _link(group(1, model_name="Mirefen Tangler"))
    assert linked.composition_line is None
    assert codes == ["EQP-GROUP-UNRESOLVED"]


def test_a_subject_matching_two_composition_rows_is_reported_rather_than_picked() -> None:
    ambiguous = (
        CuratedCompositionEntry(line=1, model_name="Chorister", min_count=1, max_count=1),
        CuratedCompositionEntry(line=2, model_name="Mirebound Chorister", min_count=4, max_count=9),
    )
    linked, findings = link_equipment(
        datasheet_id=DATASHEET,
        groups=(group(1, model_name="Mirebound Chorister"),),
        composition=ambiguous,
        weapons=WEAPONS,
    )
    assert linked[0].composition_line is None
    assert [finding.finding_code for finding in findings] == ["EQP-GROUP-UNRESOLVED"]


def test_the_group_finding_is_advisory_and_the_group_still_ships() -> None:
    linked, codes = _link(group(1, model_name="Mirefen Tangler"))
    assert len(linked) == 1
    assert CATALOGUE["EQP-GROUP-UNRESOLVED"].severity is Severity.ADVISORY
    assert codes == ["EQP-GROUP-UNRESOLVED"]


# --- the item-to-weapon join -------------------------------------------------------------------


def test_an_item_naming_exactly_one_weapon_row_carries_that_line() -> None:
    (linked,), codes = _link(group(1, items=("resonance shard",)))
    assert [item.weapon_line for item in linked.items] == [4]
    assert codes == []


def test_an_item_matching_no_weapon_row_ships_unlinked_beside_its_siblings() -> None:
    (linked,), codes = _link(group(1, items=("resonance shard", "void net")))
    assert [(item.item_name, item.weapon_line) for item in linked.items] == [
        ("resonance shard", 4),
        ("void net", None),
    ]
    assert codes == ["EQP-ITEM-UNLINKED"]


def test_an_item_matching_two_weapon_rows_is_refused_rather_than_attached_to_the_first() -> None:
    (linked,), codes = _link(group(1, items=("tide hammer",)))
    assert [item.weapon_line for item in linked.items] == [None]
    assert codes == ["EQP-ITEM-UNLINKED"]


def test_an_unlinkable_item_costs_neither_its_group_nor_its_groups_link() -> None:
    # The whole point of a per-item advisory: the sentence still says what the model carries,
    # and the one name nobody could resolve is the only thing missing from it.
    (linked,), codes = _link(group(1, items=("void net", "resonance shard")))
    assert linked.composition_line == 2
    assert len(linked.items) == 2
    assert codes == ["EQP-ITEM-UNLINKED"]
    assert CATALOGUE["EQP-ITEM-UNLINKED"].severity is Severity.ADVISORY


def test_the_comparison_is_over_normalised_names() -> None:
    # Casing, punctuation and spacing variants of one name agree; two genuinely different names
    # stay apart. The same `normalize_name` the option join uses, and the ONLY thing the two
    # modules share.
    (linked,), codes = _link(group(1, items=("Resonance  Shard",)))
    assert [item.weapon_line for item in linked.items] == [4]
    assert codes == []
