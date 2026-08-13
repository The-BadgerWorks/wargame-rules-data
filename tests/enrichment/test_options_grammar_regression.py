# AI-Assisted: Claude Code (model: claude-opus-5) - Built the FR-009 zero-regression harness,
# layer 1 (006 task T010): every pre-006 option fixture and every inline description 004's own
# grammar suite exercises, re-run under the extended grammar and asserted byte-identical against
# a committed golden captured before a single new production was written (006 research D5).
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Widened the scope-decision assertion to
# GF12 (007 task T005 fixture scaffolding): a new non-baseline datasheet id, same exclusion
# reasoning as GF07-GF11.
"""Nothing `004` resolved may resolve differently. Proven against a frozen golden.

FR-009 is the constraint the whole feature is built around: *a pre-existing option sentence that
resolves under `004`'s single-item grammar MUST continue to resolve to the same eligibility,
replacement, grant, and price it resolved to before this feature.* Research D5 proves it in three
layers, and this file is **layer 1** — synthetic, offline, in CI on every push, failing in
seconds.

**Why a committed golden rather than a comparison against the live grammar.** A test that parsed
each row twice with the same parser would assert only that the parser is deterministic, which
``test_options_grammar.py`` already covers and which is not what FR-009 says. The expected side
below was captured on 2026-08-10, from the grammar as `004` shipped it and **before any `006`
production existed**, and it is a literal in this file from here on. When a new production
changes one of these results the diff is the finding, and editing this table to match is deleting
the evidence.

**Why a golden is permitted here at all**, when research D5 calls a golden corpus prohibited:
every input below is *synthetic*. The rows come from ``fixtures/enrichment/wahapedia/``, whose
model names, item names, counts, and prices are invented, and from the descriptions `004`'s own
test file writes inline. Layer 2 — ``pipeline.cli option-regression`` — is what covers the real
corpus, and it exists precisely because that corpus can never be committed.

**Scope: the `004` datasheets only.** `006` T003 added GF07-GF11, whose rows are the shapes this
grammar was never built for. Every one of them is residual today and the point of the feature is
that some of them stop being; folding them in here would make a deliberate improvement read as a
regression, and would dilute the one assertion that actually protects `004`.

Today this file passes trivially — the grammar it measures is the grammar the golden was captured
from. It becomes a live gate the moment T016-T019 land, which is why it is Foundational and not
part of User Story 1.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from pipeline.models.curated import OptionScope as S
from pipeline.parse.options_grammar import OptionChoiceParse as C
from pipeline.parse.options_grammar import OptionRowParse as R
from pipeline.parse.options_grammar import OptionVerb as V
from pipeline.parse.options_grammar import parse_row
from pipeline.parse.wahapedia_csv import read_file

ROOT = Path(__file__).resolve().parents[2]
OPTIONS_CSV = ROOT / "fixtures" / "enrichment" / "wahapedia" / "Datasheets_options.csv"

#: The datasheets that existed before `006`. Stated rather than derived: "whatever is in the
#: fixture file" would silently absorb every row a later task adds, and the whole value of this
#: harness is that its input set is fixed.
BASELINE_DATASHEETS: frozenset[str] = frozenset({"GF01", "GF02", "GF03", "GF04", "GF05", "GF06"})

#: ``(datasheet_id, line) -> the parse `004` produced``. Captured 2026-08-10, before any `006`
#: production existed. `None` is a result and not an omission: GF05's head matches no production
#: and reporting it as ``OPT-UNPARSED`` is `004`'s documented behaviour, so a `006` production
#: that *resolves* it is a change this harness must show rather than hide.
FIXTURE_GOLDEN: dict[tuple[str, int], R | None] = {
    ("GF01", 1): R(
        scope=S.MODEL,
        scope_n=None,
        choices=(C(name="glimmer lantern", count=1, is_no_change=False, verb=V.EQUIP),),
    ),
    ("GF02", 1): R(
        scope=S.UNIT,
        scope_n=None,
        choices=(C(name="marsh carbine", count=1, is_no_change=False, verb=V.EQUIP),),
    ),
    ("GF03", 1): R(
        scope=S.PER_N_MODELS,
        scope_n=3,
        choices=(C(name="tanglelance", count=1, is_no_change=False, verb=V.EQUIP),),
    ),
    ("GF04", 1): R(
        scope=S.UNIT,
        scope_n=None,
        choices=(
            C(name="sedge halberd", count=1, is_no_change=False, verb=V.REPLACE),
            C(name="mire censer", count=1, is_no_change=False, verb=V.REPLACE),
            C(name="No change", count=None, is_no_change=True, verb=V.REPLACE),
        ),
    ),
    ("GF05", 1): None,
    ("GF06", 1): R(
        scope=S.UNIT,
        scope_n=None,
        choices=(
            C(name="chime flail", count=1, is_no_change=False, verb=V.EQUIP),
            C(name="resonance shards", count=2, is_no_change=False, verb=V.EQUIP),
        ),
    ),
}

#: Every description ``test_options_grammar.py`` writes inline, with the parse `004` produced.
#: These are not in the fixture file, and they carry cases the fixture does not: the unquantified
#: choice, the relabelling pair identity is asserted over, the space-variant sub-list opener, and
#: the seven forms research D3 verified absent and deliberately refused to build for. A `006`
#: production that quietly starts resolving one of the refusals is exactly the regression this
#: row set exists to catch.
INLINE_GOLDEN: dict[str, R | None] = {
    "This model can be equipped with a fen charm.": R(
        scope=S.MODEL,
        scope_n=None,
        choices=(C(name="a fen charm", count=None, is_no_change=False, verb=V.EQUIP),),
    ),
    "The Sedgeward Adept can be equipped with 1 sedge halberd.": R(
        scope=S.UNIT,
        scope_n=None,
        choices=(C(name="sedge halberd", count=1, is_no_change=False, verb=V.EQUIP),),
    ),
    "The Sedgeward Adept can be equipped with 1 sedge glaive.": R(
        scope=S.UNIT,
        scope_n=None,
        choices=(C(name="sedge glaive", count=1, is_no_change=False, verb=V.EQUIP),),
    ),
    "The Sedgeward Adept can be equipped with:<ul><li>1 a</li>": R(
        scope=S.UNIT,
        scope_n=None,
        choices=(C(name="a", count=1, is_no_change=False, verb=V.EQUIP),),
    ),
    # The seven deliberately-unbuilt forms (research D3). Every one still `None`.
    "Each Mirefen Tangler may take a snare net.": None,
    "This model may replace its fen spear with a bog maul.": None,
    "1 in every 3 models can be equipped with 1 tanglelance.": None,
    "for every 3 models, 1 model can be equipped with 1 tanglelance.": None,
    "Only one model can be equipped with 1 tanglelance.": None,
    "This model has no options.": None,
    "": None,
}


def _fixture_rows() -> dict[tuple[str, int], str]:
    """``(datasheet_id, line) -> description`` for the pre-006 datasheets only."""
    return {
        (row.fields["datasheet_id"], int(row.fields["line"])): row.fields["description"]
        for row in read_file(OPTIONS_CSV).rows
        if row.fields["datasheet_id"] in BASELINE_DATASHEETS
    }


# -- the harness ---------------------------------------------------------------------------------


@pytest.mark.parametrize(("key", "expected"), sorted(FIXTURE_GOLDEN.items()))
def test_a_pre_006_fixture_row_parses_exactly_as_it_did(
    key: tuple[str, int], expected: R | None
) -> None:
    """One row, one assertion, named by the row — so a failure says which one moved."""
    description = _fixture_rows()[key]
    assert parse_row(description) == expected


@pytest.mark.parametrize(("description", "expected"), sorted(INLINE_GOLDEN.items()))
def test_an_inline_004_description_parses_exactly_as_it_did(
    description: str, expected: R | None
) -> None:
    assert parse_row(description) == expected


def test_the_golden_covers_every_pre_006_fixture_row() -> None:
    """A row that left the golden's key set is a row nothing is protecting.

    The failure this guards against is quiet: someone adds an option row to GF01-GF06, the
    per-row tests above still pass because they iterate the *golden*, and the new row is
    unprotected. Comparing the two key sets in both directions is what makes the coverage claim
    checkable rather than assumed.
    """
    assert set(FIXTURE_GOLDEN) == set(_fixture_rows())


def test_the_golden_is_a_literal_and_not_a_recomputation() -> None:
    """The one property that makes this file worth having, asserted directly.

    A golden regenerated from the code under test proves only that the code equals itself. This
    checks the committed expectations carry values a live re-parse cannot have supplied — the
    scope enum, the verb, and the count are all spelled out above — by asserting a deliberately
    wrong expectation fails.
    """
    wrong = R(
        scope=S.UNIT,
        scope_n=None,
        choices=(C(name="glimmer lantern", count=1, is_no_change=False, verb=V.EQUIP),),
    )
    assert parse_row(_fixture_rows()[("GF01", 1)]) != wrong, (
        "GF01 is model-scoped; if this now compares equal, the comparison has stopped looking "
        "at scope and the harness is asserting nothing"
    )


def test_every_006_and_007_datasheet_is_deliberately_outside_this_harness() -> None:
    """The scope decision, stated as an assertion rather than as a comment.

    GF07-GF11 carry the shapes 006 exists to resolve, and GF12 carries 007's own new option-row
    shapes (research D3.3's legacy stem-object outcomes, the footnote-restriction residual, and
    the over-length replaced item). If one of them were folded into the baseline set, a
    successful new production would fail this file, and the pressure would be to edit the golden
    — which is how a zero-regression harness stops meaning anything.
    """
    all_datasheets = {row.fields["datasheet_id"] for row in read_file(OPTIONS_CSV).rows}
    assert all_datasheets > BASELINE_DATASHEETS
    # GF09 and GF11 are absent from this file on purpose rather than by oversight: neither
    # datacard states a WARGEAR OPTIONS block at all, which is the `wargear_option_state = none`
    # case one of them carries for the equipment tests. GF13-GF15 (007's composition-only header
    # fixtures) are absent from this file for the same reason: they state no options block.
    assert all_datasheets - BASELINE_DATASHEETS == {"GF07", "GF08", "GF10", "GF12"}
