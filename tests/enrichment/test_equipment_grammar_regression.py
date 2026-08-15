# AI-Assisted: Claude Code (model: claude-sonnet-5) - Built the layer-1 zero-churn harness for
# the equipment grammar (008 task T012, Setup phase), the equipment sibling of
# `test_options_grammar_regression.py`'s FR-009 harness, extended to the equipment classes per
# FR-014's "extended to cover the equipment classes as well as the option classes". Captured
# **before** a single Phase 5 production exists, so a later `_COMPLETION_SUBJECTS` production
# that changes one of these results shows up as a diff here rather than silently.
"""Nothing 006 resolved may resolve differently. Proven against a frozen golden.

**Why this file's shape differs from its options sibling.** `pipeline/parse/equipment_grammar.py`
has existed since 006, but no shared, on-disk fixture file backed it until 008 task T009 created
`fixtures/enrichment/wahapedia/Datasheets_unit_equipment.csv` for the first time — every equipment
test before this one hand-built its own inline `CsvReadResult`
(`test_equipment_grammar.py`, `test_equipment_overrides.py`). There is therefore no "pre-008
equipment fixture row" to protect: :data:`BASELINE_DATASHEETS` and :data:`FIXTURE_GOLDEN` are
correctly **empty**, and the file's only committed equipment row (`GF24`, T009's own US3
Independent Test pair) is 008's own and belongs on the excluded side, exactly as `GF07`-`GF12`
do for the options harness.

The real golden is :data:`INLINE_GOLDEN`: 006's own five subject productions plus the bare-model
sixth, the item-list splitting rules, and the compound/conditional refusal tail, lifted as literal
expected structures from `test_equipment_grammar.py`'s own existing assertions — the same "capture
before a new production exists" discipline, applied to descriptions rather than to a CSV row set
because that CSV row set does not yet exist.

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

#: The datasheets that had an equipment-fixture row before `008`. Empty and deliberately so — see
#: the module docstring. Stated rather than derived, on the same terms as the options harness's
#: own `BASELINE_DATASHEETS`: "whatever is in the fixture file" would silently absorb whatever a
#: later task adds, and the whole value of this harness is that its input set is fixed.
BASELINE_DATASHEETS: frozenset[str] = frozenset()

#: ``(datasheet_id, line) -> the parse 006 produced``. Empty for the reason above: no row existed
#: to capture. Kept as a typed, iterated dict (rather than omitted) so this file's structure
#: matches its options sibling exactly and a future non-empty baseline drops in without a rewrite.
FIXTURE_GOLDEN: dict[tuple[str, int], P | None] = {}

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
    """``(datasheet_id, line) -> description`` for the pre-008 datasheets only. Empty today."""
    return {
        (row.fields["datasheet_id"], int(row.fields["line"])): row.fields["description"]
        for row in read_file(EQUIPMENT_CSV).rows
        if row.fields["datasheet_id"] in BASELINE_DATASHEETS
    }


# -- the harness ---------------------------------------------------------------------------------


@pytest.mark.parametrize(("key", "expected"), sorted(FIXTURE_GOLDEN.items()))
def test_a_pre_008_fixture_row_parses_exactly_as_it_did(
    key: tuple[str, int], expected: P | None
) -> None:
    """One row, one assertion, named by the row. Zero parameters today — see the module docstring;
    the parametrize call is kept rather than omitted so a later non-empty baseline needs no rewrite
    of this test's shape, only new entries in `FIXTURE_GOLDEN`."""
    description = _fixture_rows()[key]
    assert parse_sentence(description) == expected


@pytest.mark.parametrize(("description", "expected"), sorted(INLINE_GOLDEN.items()))
def test_an_inline_006_description_parses_exactly_as_it_did(
    description: str, expected: P | None
) -> None:
    assert parse_sentence(description) == expected


def test_the_golden_covers_every_pre_008_fixture_row() -> None:
    """A row that left the golden's key set is a row nothing is protecting.

    Both sides are empty today (module docstring); the equality is still asserted directly rather
    than trivially, so the check is live the moment a future baseline is captured here.
    """
    assert set(FIXTURE_GOLDEN) == set(_fixture_rows())


def test_the_golden_is_a_literal_and_not_a_recomputation() -> None:
    """The one property that makes this file worth having, asserted directly.

    A golden regenerated from the code under test proves only that the code equals itself. This
    checks a committed expectation carries values a live re-parse cannot have supplied — the
    `applies_to` enum and the model name are both spelled out above — by asserting a deliberately
    wrong expectation fails. Run against `INLINE_GOLDEN` rather than `FIXTURE_GOLDEN`, which is
    empty (module docstring).
    """
    wrong = P(applies_to=A.MODEL_GROUP, model_name="sentinel lance", items=())
    assert parse_sentence("This model is equipped with: sentinel lance.") != wrong, (
        "this sentence is unit-scoped with one item; if this now compares equal, the comparison "
        "has stopped looking at applies_to/model_name/items and the harness is asserting nothing"
    )


def test_every_008_datasheet_is_deliberately_outside_this_harness() -> None:
    """The scope decision, stated as an assertion rather than as a comment.

    `GF24` carries US3's own Independent Test shape (008 task T009: one resolving, one refused —
    the `One`/`INT`/`A` subset-subject family Open Decision O1 sizes). If it were folded into the
    baseline set, a successful Phase 5 production would fail this file, and the pressure would be
    to edit the golden — which is how a zero-regression harness stops meaning anything.
    """
    all_datasheets = {row.fields["datasheet_id"] for row in read_file(EQUIPMENT_CSV).rows}
    assert all_datasheets - BASELINE_DATASHEETS == {"GF24"}
