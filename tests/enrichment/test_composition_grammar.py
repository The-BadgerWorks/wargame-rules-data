# AI-Assisted: Claude Code (model: claude-opus-5) - The composition grammar's contract (004 task
# T021): the pre-pass, the two productions, "a fixed count is not missing data", exactly-one
# model linking, and the unresolved row that reports and never blocks (FR-007, FR-008).
"""What the composition grammar promises, stated against the synthetic fixture.

Three of these assertions are about what the parser **refuses** to do, and those are the ones
worth keeping: a grammar that resolves 98.7% of its input is unremarkable, while a grammar that
guesses the other 1.3% mis-prices a unit in a player's hands at a tournament.
"""

from __future__ import annotations

from collections.abc import Mapping

import pytest

from pipeline.models.curated import CuratedCompositionEntry
from pipeline.models.findings import Severity
from pipeline.parse.composition_grammar import (
    MAX_MODEL_NAME_CHARS,
    link_model_line,
    parse_entry,
    pre_pass,
)
from pipeline.report.catalogue import CATALOGUE
from tests.enrichment.conftest import model_lines


def test_the_pre_pass_maps_every_dash_form_and_collapses_whitespace() -> None:
    # The non-breaking hyphen is the one that matters: 11 rows of the measured baseline write
    # their range with it, and without the mapping they fall to the residual for a reason no
    # reader of the report could ever see.
    assert pre_pass("3‑6  Bracklight Outrider") == "3-6 Bracklight Outrider"
    assert pre_pass("3–6 Bracklight Outrider") == "3-6 Bracklight Outrider"
    assert pre_pass('<span class="kwb">1 Glimmerfen Warden</span>') == "1 Glimmerfen Warden"


def test_the_pre_pass_is_idempotent() -> None:
    once = pre_pass("5—10  Fenmire  Skirmisher")
    assert pre_pass(once) == once


@pytest.mark.parametrize(
    ("datasheet_id", "line", "expected"),
    [
        ("GF01", 1, ("Glimmerfen Warden", 1, 1)),
        ("GF02", 1, ("Fenmire Skirmisher", 5, 10)),
        ("GF02", 2, ("Fenmire Marshbearer", 1, 1)),
        ("GF03", 1, ("Bracklight Outrider", 3, 6)),
        ("GF04", 1, ("Sedgeward Adept", 1, 1)),
        ("GF04", 2, ("Sedgeward Acolyte", 4, 4)),
        ("GF06", 1, ("Thornlight Chorister Prime", 1, 1)),
        ("GF06", 2, ("Thornlight Chorister", 3, 9)),
    ],
)
def test_every_resolvable_fixture_row_resolves_to_integers(
    composition_rows: Mapping[str, list[tuple[int, str]]],
    datasheet_id: str,
    line: int,
    expected: tuple[str, int, int],
) -> None:
    description = dict(composition_rows[datasheet_id])[line]
    parsed = parse_entry(description)
    assert parsed is not None
    assert (parsed.model_name, parsed.min_count, parsed.max_count) == expected


def test_a_fixed_count_is_not_mistaken_for_missing_data() -> None:
    """``min == max`` is the majority shape, produced deliberately and never as a fallback."""
    parsed = parse_entry("4 Sedgeward Acolyte")
    assert parsed is not None
    assert parsed.min_count == parsed.max_count == 4
    # And it survives the curated model, whose own validator rejects a backwards range.
    entry = CuratedCompositionEntry(
        line=1, model_name=parsed.model_name, min_count=parsed.min_count, max_count=parsed.max_count
    )
    assert entry.max_count == entry.min_count


def test_the_range_production_is_tried_before_the_fixed_one() -> None:
    # Trying the fixed production first would read `5-10 Fenmire Skirmisher` as five models of
    # something called "-10 Fenmire Skirmisher" — a resolution, and a wrong one.
    parsed = parse_entry("5-10 Fenmire Skirmisher")
    assert parsed is not None
    assert (parsed.min_count, parsed.max_count) == (5, 10)


@pytest.mark.parametrize(
    "description",
    [
        "Every model in this unit is equipped with:",
        "Two Sedgeward Acolytes",
        "1 Sedgeward Adept and 4 Sedgeward Acolytes",
        "6-3 Bracklight Outrider",
        "3 " + "x" * (MAX_MODEL_NAME_CHARS + 1),
        "",
    ],
)
def test_an_unresolvable_row_yields_no_entry_rather_than_a_guess(description: str) -> None:
    assert parse_entry(description) is None


def test_the_fixtures_unresolvable_row_is_the_one_named(
    composition_rows: Mapping[str, list[tuple[int, str]]],
) -> None:
    unresolved = {
        (datasheet_id, line)
        for datasheet_id, rows in composition_rows.items()
        for line, description in rows
        if parse_entry(description) is None
    }
    assert unresolved == {("GF05", 1)}


def test_cmp_unresolved_is_advisory_and_therefore_never_blocks_publication() -> None:
    # FR-008 in one assertion: an unresolvable composition costs the datasheet its composition,
    # not the release its publication.
    assert CATALOGUE["CMP-UNRESOLVED"].severity is Severity.ADVISORY


def test_exactly_one_model_name_match_sets_the_link() -> None:
    assert link_model_line("Glimmerfen Warden", model_lines("GF01")) == 1
    assert link_model_line("Fenmire Skirmisher", model_lines("GF02")) == 1
    assert link_model_line("Fenmire Marshbearer", model_lines("GF02")) == 2


def test_zero_matches_leaves_the_link_omitted() -> None:
    assert link_model_line("Bracklight Outrider", model_lines("GF03")) is None


def test_two_or_more_matches_leaves_the_link_omitted() -> None:
    # "Thornlight Chorister" is a prefix of "Thornlight Chorister Prime", so the Prime line
    # matches both model rows. Attaching it to either would be a guess with a 50% error rate.
    assert link_model_line("Thornlight Chorister Prime", model_lines("GF06")) is None
    assert link_model_line("Thornlight Chorister", model_lines("GF06")) == 2


def test_linking_is_insensitive_to_casing_spacing_and_punctuation() -> None:
    assert link_model_line("GLIMMERFEN  WARDEN", {1: "Glimmerfen Warden"}) == 1
    assert link_model_line("Sedgeward-Adept", {1: "Sedgeward Adept"}) == 1


def test_parsing_is_deterministic_over_the_whole_fixture(
    composition_rows: Mapping[str, list[tuple[int, str]]],
) -> None:
    def run() -> list[tuple[str, int, str, int, int] | tuple[str, int, None]]:
        out: list[tuple[str, int, str, int, int] | tuple[str, int, None]] = []
        for datasheet_id, rows in sorted(composition_rows.items()):
            for line, description in rows:
                parsed = parse_entry(description)
                out.append(
                    (datasheet_id, line, parsed.model_name, parsed.min_count, parsed.max_count)
                    if parsed
                    else (datasheet_id, line, None)
                )
        return out

    assert run() == run()
