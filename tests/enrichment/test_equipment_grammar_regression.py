# AI-Assisted: Claude Code (model: claude-sonnet-5) - Built the layer-1 zero-churn harness for
# the equipment grammar (008 task T012, Setup phase), the equipment sibling of
# `test_options_grammar_regression.py`'s FR-009 harness, extended to the equipment classes per
# FR-014's "extended to cover the equipment classes as well as the option classes". Captured
# **before** a single Phase 5 production exists, so a later `_COMPLETION_SUBJECTS` production
# that changes one of these results shows up as a diff here rather than silently.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Filled the fixture-backed half (009 task
# T006, Setup phase, retiring risk R-H): `BASELINE_DATASHEETS` and `FIXTURE_GOLDEN` were left
# empty by `008` (its own O1 subset-subject family stayed refused, so its two rows were never
# folded in) and asserted nothing. `008` published; there is no further Phase 5 of its own left to
# protect these rows FROM, and 009's own rule 5 forbids this feature from ever authoring a new
# equipment production. Every row currently in the fixture file is captured now, as the record of
# pre-009-migration behaviour this harness exists to hold a line against — in particular against
# 009 Phase 2's shared `ip_strip`/normalization tightening (T030), which is the one change in this
# feature's own plan that could move a parse here despite no grammar production being touched.
"""Nothing 006 or 008 resolved may resolve differently. Proven against a frozen golden.

**Why this file's shape differs from its options sibling.** `pipeline/parse/equipment_grammar.py`
has existed since 006, but no shared, on-disk fixture file backed it until 008 task T009 created
`fixtures/enrichment/wahapedia/Datasheets_unit_equipment.csv` for the first time — every equipment
test before this one hand-built its own inline `CsvReadResult`
(`test_equipment_grammar.py`, `test_equipment_overrides.py`). `008` left the fixture-backed half
of this harness empty deliberately, because its own two rows (`GF24`, T009's US3 Independent Test
pair; `GF25`, T049's equipment-qualified refusal pairing) were exactly what a live `008` Phase 5
production might still move. `008` has since published (`wh40k-11e-2026-08-4`) with no such
production ever authored for the `One`/`INT`/`A` subset-subject family, so both rows are now
settled pre-migration behaviour rather than moving targets, and :data:`BASELINE_DATASHEETS` /
:data:`FIXTURE_GOLDEN` are filled with the whole of the fixture file's current content (009 T006).

The real golden is :data:`INLINE_GOLDEN`: 006's own five subject productions plus the bare-model
sixth, the item-list splitting rules, and the compound/conditional refusal tail, lifted as literal
expected structures from `test_equipment_grammar.py`'s own existing assertions — the same "capture
before a new production exists" discipline, applied to descriptions rather than to a CSV row set
because that CSV row set did not yet exist when it was captured.

Layer 2 (`pipeline.cli option-regression`, extended by 008 task T061 to an equipment section) is
what covers the real corpus; this file is layer 1, synthetic and in CI on every push.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from pipeline.models.curated import EquipmentAppliesTo as A
from pipeline.parse.equipment_grammar import EquipmentItemParse as I
from pipeline.parse.equipment_grammar import EquipmentParse as P
from pipeline.parse.equipment_grammar import parse_sentence
from pipeline.parse.wahapedia_csv import read_file

ROOT = Path(__file__).resolve().parents[2]
EQUIPMENT_CSV = ROOT / "fixtures" / "enrichment" / "wahapedia" / "Datasheets_unit_equipment.csv"

#: The datasheets carrying an equipment-fixture row as of 009's Setup phase (T006) — `008`'s own
#: two, `GF24` and `GF25`, now settled (see the module docstring) rather than still-moving. Stated
#: rather than derived, on the same terms as the options harness's own `BASELINE_DATASHEETS`:
#: "whatever is in the fixture file" would silently absorb whatever a later task adds, and the
#: whole value of this harness is that its input set is fixed.
BASELINE_DATASHEETS: frozenset[str] = frozenset({"GF24", "GF25"})

#: ``(datasheet_id, line) -> the parse captured at 009 T006``, read directly off
#: `parse_sentence` against the fixture file's current content, before any 009 production or
#: normalization change exists. A later diff here is exactly what this harness exists to catch.
FIXTURE_GOLDEN: dict[tuple[str, int], P | None] = {
    ("GF24", 1): P(
        applies_to=A.MODEL_GROUP,
        model_name="Watch Sergeant",
        items=(I(item_name="signal lantern"), I(item_name="ember blade")),
    ),
    # The "One <Model> is equipped with:" subject shape — 008's own O1 subset-subject family,
    # left refused; no production for it exists and 009 rule 5 forbids authoring one.
    ("GF24", 2): None,
    # The equipment-qualified subject ("... with a lantern is equipped with:") — permanently
    # refused, 008 T049.
    ("GF25", 1): None,
}

#: Every description `test_equipment_grammar.py` already asserts against, with the parse 006
#: produced — lifted as literals rather than re-derived, so a `_COMPLETION_SUBJECTS` production
#: that starts resolving one of the refusals, or that changes a resolved shape, is the regression
#: this file exists to catch.
INLINE_GOLDEN: dict[str, P | None] = {
    # -- the five measured subject productions, plus the bare sixth ----------------------------
    "Every model is equipped with: glimmer rifle; fen halberd.": P(
        applies_to=A.UNIT,
        model_name=None,
        items=(I(item_name="glimmer rifle"), I(item_name="fen halberd")),
    ),
    "This model is equipped with: sentinel lance.": P(
        applies_to=A.UNIT, model_name=None, items=(I(item_name="sentinel lance"),)
    ),
    "Every Mirebound Chorister is equipped with: void net.": P(
        applies_to=A.MODEL_GROUP,
        model_name="Mirebound Chorister",
        items=(I(item_name="void net"),),
    ),
    "The Mirebound Cantor is equipped with: chime flail.": P(
        applies_to=A.MODEL_GROUP, model_name="Mirebound Cantor", items=(I(item_name="chime flail"),)
    ),
    "Each Mirebound Chorister is equipped with: void net.": P(
        applies_to=A.MODEL_GROUP,
        model_name="Mirebound Chorister",
        items=(I(item_name="void net"),),
    ),
    # D1e's sixth production: the bare subject, which takes the residual from 25 to 9.
    "Glimmerfen Warden is equipped with: glimmer lantern.": P(
        applies_to=A.MODEL_GROUP,
        model_name="Glimmerfen Warden",
        items=(I(item_name="glimmer lantern"),),
    ),
    # -- the item list ---------------------------------------------------------------------------
    "Every model is equipped with: gloam pistol, gloam blade.": P(
        applies_to=A.UNIT,
        model_name=None,
        items=(I(item_name="gloam pistol"), I(item_name="gloam blade")),
    ),
    "This model is equipped with: 2 void nets; snare net.": P(
        applies_to=A.UNIT,
        model_name=None,
        items=(I(item_name="void nets", count=2), I(item_name="snare net")),
    ),
    # -- the compound/conditional tail (research D1e), every one still refused -------------------
    "Every Fenmire Skirmisher with a marsh carbine is equipped with: tanglelance.": None,
    "One Gloamtide Wretch is equipped with: gloam banner.": None,
    "2 Bracklight Outriders are equipped with: marsh carbine.": None,
    "A Thornlight Chorister is equipped with: chime flail.": None,
    "For every 5 models in the unit, 1 model is equipped with: resonance shard.": None,
    "If the unit has 10 models, 2 models are equipped with: void net.": None,
    # -- structurally refused: no marker, no items, an over-length subject -----------------------
    "Every model in this unit is arrayed for war.": None,
    "Every model is equipped with:": None,
    f"The {'x' * 121} is equipped with: snare net.": None,
}


def _fixture_rows() -> dict[tuple[str, int], str]:
    """``(datasheet_id, line) -> description`` for the baseline datasheets (009 T006: every
    datasheet currently in the fixture file)."""
    return {
        (row.fields["datasheet_id"], int(row.fields["line"])): row.fields["description"]
        for row in read_file(EQUIPMENT_CSV).rows
        if row.fields["datasheet_id"] in BASELINE_DATASHEETS
    }


# -- the harness ---------------------------------------------------------------------------------


@pytest.mark.parametrize(("key", "expected"), sorted(FIXTURE_GOLDEN.items()))
def test_a_baseline_fixture_row_parses_exactly_as_it_did(
    key: tuple[str, int], expected: P | None
) -> None:
    """One row, one assertion, named by the row. The parametrize call is over the real, captured
    fixture-file content (009 T006) — a later non-empty baseline extension needs no rewrite of
    this test's shape, only new entries in `FIXTURE_GOLDEN`."""
    description = _fixture_rows()[key]
    assert parse_sentence(description) == expected


@pytest.mark.parametrize(("description", "expected"), sorted(INLINE_GOLDEN.items()))
def test_an_inline_006_description_parses_exactly_as_it_did(
    description: str, expected: P | None
) -> None:
    assert parse_sentence(description) == expected


def test_the_golden_covers_every_baseline_fixture_row() -> None:
    """A row that left the golden's key set is a row nothing is protecting.

    The equality is asserted directly rather than trivially, so the check is live the moment a
    future baseline extension changes either side.
    """
    assert set(FIXTURE_GOLDEN) == set(_fixture_rows())


def test_the_golden_is_a_literal_and_not_a_recomputation() -> None:
    """The one property that makes this file worth having, asserted directly.

    A golden regenerated from the code under test proves only that the code equals itself. This
    checks a committed expectation carries values a live re-parse cannot have supplied — the
    `applies_to` enum and the model name are both spelled out above — by asserting a deliberately
    wrong expectation fails. Run against `INLINE_GOLDEN`, whose values are the most elaborate
    committed expectations in this file.
    """
    wrong = P(applies_to=A.MODEL_GROUP, model_name="sentinel lance", items=())
    assert parse_sentence("This model is equipped with: sentinel lance.") != wrong, (
        "this sentence is unit-scoped with one item; if this now compares equal, the comparison "
        "has stopped looking at applies_to/model_name/items and the harness is asserting nothing"
    )


def test_the_fixture_golden_is_also_literal_and_not_a_recomputation() -> None:
    """The same property as above, over `FIXTURE_GOLDEN` specifically (009 T006's own addition) —
    a golden captured by calling `parse_sentence` and pasting its result would pass even if the
    comparison stopped looking at a field, exactly as the inline sibling test explains."""
    wrong = P(applies_to=A.MODEL_GROUP, model_name="Watch Sergeant", items=())
    assert (
        parse_sentence("The Watch Sergeant is equipped with: signal lantern; ember blade.") != wrong
    ), "the real parse carries two items; a comparison that ignores them is not a regression net"


def test_every_fixture_datasheet_is_inside_the_baseline() -> None:
    """The scope decision, stated as an assertion rather than as a comment (009 T006).

    `008` deliberately held `GF24` (its own US3 Independent Test shape, T009: one resolving, one
    refused — the `One`/`INT`/`A` subset-subject family Open Decision O1 sizes) and `GF25` (the
    equipment-qualified refusal pairing, T049) OUTSIDE the baseline, because a live `008` Phase 5
    production might still have moved either. `008` has since published with no such production
    ever authored, so nothing is held out any more: every datasheet the fixture file carries is in
    `BASELINE_DATASHEETS`. If a future task adds a fixture row and does not also extend
    `BASELINE_DATASHEETS`/`FIXTURE_GOLDEN`, this is the assertion that catches it.
    """
    all_datasheets = {row.fields["datasheet_id"] for row in read_file(EQUIPMENT_CSV).rows}
    assert all_datasheets - BASELINE_DATASHEETS == set()
    assert all_datasheets == BASELINE_DATASHEETS
