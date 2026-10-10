# AI-Assisted: Claude Code (model: claude-sonnet-5) - pipeline P3 task 4 (P4c, E=15): the fill of
# `CuratedOptionGroup.eligible_max_count` from a leading "N model(s) can …" stem, for the rows
# `options_grammar.py::parse_row` resolves to scope UNIT with both `eligible_max_count` and
# `eligible_model_name` left `None` — the stem states a headcount the grammar itself never
# extracts. `pipeline/parse/options_grammar.py` is never edited for this task; the fill lives
# entirely in `pipeline/curate/assemble.py::_leading_model_count`, applied only in that narrow
# band and never overriding a count the grammar already set.
"""`eligible_max_count` filled from a bare "N model(s) can …" stem (P4c)."""

from __future__ import annotations

from pipeline.curate.assemble import _option_structure
from pipeline.curate.authored import AuthoredContent
from pipeline.parse.wahapedia_csv import CsvReadResult, read_text
from tests.enrichment.conftest import weapon

DETAIL_ID = "GFfx"
DATASHEET = "ds-fx-eligible-max-count"


def _detail(description: str) -> dict[str, CsvReadResult]:
    rows = f"datasheet_id|line|button|description|\n{DETAIL_ID}|1|Wargear Options|{description}|\n"
    return {"Datasheets_options.csv": read_text("Datasheets_options.csv", rows)}


def _group(description: str):  # type: ignore[no-untyped-def]
    outcome = _option_structure(
        DETAIL_ID,
        DATASHEET,
        _detail(description),
        AuthoredContent(),
        [weapon(1, "Test lantern"), weapon(2, "Test blade"), weapon(3, "Test maul")],
        (),
    )
    (group,) = outcome.groups
    return group


def test_a_bare_model_count_stem_fills_eligible_max_count() -> None:
    # The grammar resolves this to scope UNIT with no eligible_max_count of its own: the "2" in
    # the stem is otherwise lost. Removing the fill leaves this `None`.
    group = _group("2 models can be equipped with 1 test lantern.")
    assert group.eligible_max_count == 2


def test_an_any_number_stem_is_never_filled() -> None:
    # "Any number" carries no leading digit for the fill's regex to match: it must stay None, not
    # be coerced into some sentinel count.
    group = _group("Any number of models can be equipped with 1 test lantern.")
    assert group.eligible_max_count is None


def test_the_grammars_own_count_and_model_name_are_never_overridden() -> None:
    # The grammar already resolves this scoped stem's own count (3) and subject model name: the
    # fill must never clobber a value the grammar itself set.
    group = _group(
        "Up to 3 Test Troopers can each have their test blade replaced with 1 test maul."
    )
    assert group.eligible_max_count == 3
    assert group.eligible_model_name == "Test Troopers"


def test_a_this_model_stem_is_never_filled() -> None:
    # Scope resolves to MODEL, not UNIT, for a "This model can ..." stem: the fill's condition
    # requires scope UNIT, so this must stay None.
    group = _group("This model can be equipped with 1 test lantern.")
    assert group.eligible_max_count is None
