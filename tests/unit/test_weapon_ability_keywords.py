# AI-Assisted: Claude Code (model: claude-opus-5) - Wrote the weapon-ability-keyword field
# reader's suite (issue #4), confirmed failing before pipeline/normalize/weapon_abilities.py
# existed: the bracketed-group rule, the parameterised forms, the prose boundary, and the
# round trip with the html emitter's own formatter.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Added the unbracketed-list rule (009
# Finding B): a live probe of the real bulk export this session found `Datasheets_wargear.csv`'s
# `description` column states ability keywords as a bare, unbracketed comma/semicolon list on
# every one of 6,362 live non-empty rows measured (0 contain a bracket, 0 contain a period) --
# the bracket-only reader silently returned nothing for all of them, orphaning 50 of the 70
# authored glossary entries the moment `csv` mode supplied this table for real.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 009 PR32: added the bracket-free bound's
# receipts (a comma-split prose sentence with no terminal punctuation, previously unbounded and
# read straight through as ability keywords) and the per-item punctuation-guard receipts (one
# stray period no longer empties every keyword on the row). All shown failing first.
"""The field reader that recovers a weapon's ability keywords, and the boundary it holds.

Two properties are load-bearing and neither is obvious from the implementation:

* **Prose is not a keyword.** The detail source's ``description`` column holds the keyword list
  on some rows and free publisher prose on others, and this repository retains no publisher
  wording anywhere (Constitution Principle 4). The reader's answer for a prose row must
  therefore be *nothing at all* — not a best-effort token, not a truncated one. Sentence-final
  punctuation (``.``/``!``/``?``) is the guard: the live export's own ability-keyword rows never
  carry one (measured this session, 6,362/6,362), so a bracket-free field carrying one is prose,
  not a keyword list.
* **The parameter stays attached.** ``RAPID FIRE 2`` is one keyword here and collapses to one
  glossary key downstream; splitting it into ``RAPID FIRE`` and ``2`` at this layer would put a
  second, differently-shaped normalisation in front of the one
  :mod:`pipeline.normalize.keyword_key` publishes as normative for producer and consumer alike.
* **Brackets are optional, not required.** The html arm always wraps its keywords in ``[...]``
  (:func:`format_ability_keywords`'s own shape) and the real bulk export never does — both are
  read the same way once the bracket-or-not decision is made, so :mod:`pipeline.curate.assemble`
  still reads one field, by one rule, and still cannot tell which mode ran.

Every keyword named below is invented. The reader is a shape reader, so invented shapes prove
it exactly as well as printed ones, and no fixture in this repository needs to carry the
publisher's vocabulary to make the point.
"""

from __future__ import annotations

import pytest

from pipeline.normalize.keyword_key import keyword_key
from pipeline.normalize.weapon_abilities import (
    format_ability_keywords,
    parse_weapon_ability_keywords,
)

# -- the bracketed-group rule ----------------------------------------------------------------


def test_one_bracketed_group_yields_its_keywords_in_printed_order() -> None:
    assert parse_weapon_ability_keywords("[GLIMMERBURST, MARSHBIND 2, FENLOCK 4+]") == (
        "GLIMMERBURST",
        "MARSHBIND 2",
        "FENLOCK 4+",
    )


def test_a_semicolon_separates_as_a_comma_does() -> None:
    assert parse_weapon_ability_keywords("[GLIMMERBURST; MARSHBIND 2]") == (
        "GLIMMERBURST",
        "MARSHBIND 2",
    )


def test_two_groups_on_one_row_are_both_read() -> None:
    assert parse_weapon_ability_keywords("[GLIMMERBURST] [MARSHBIND 2]") == (
        "GLIMMERBURST",
        "MARSHBIND 2",
    )


@pytest.mark.parametrize("field", ["", "   ", "Invented placeholder prose.", "[]", "[ , ; ]"])
def test_a_row_stating_no_keyword_yields_nothing(field: str) -> None:
    assert parse_weapon_ability_keywords(field) == ()


def test_prose_outside_a_bracket_is_discarded_rather_than_read_as_a_keyword() -> None:
    """The IP boundary, stated as a test: unbracketed text never becomes curated data."""
    assert parse_weapon_ability_keywords(
        "Invented placeholder prose about this weapon. [GLIMMERBURST] More invented prose."
    ) == ("GLIMMERBURST",)


def test_a_comma_inside_parentheses_is_not_a_separator() -> None:
    """A keyword may qualify itself parenthetically; splitting there would invent two."""
    assert parse_weapon_ability_keywords("[MARSHBIND (WALKER, RIDER), GLIMMERBURST]") == (
        "MARSHBIND (WALKER, RIDER)",
        "GLIMMERBURST",
    )


def test_whitespace_inside_a_keyword_collapses_the_way_every_other_field_does() -> None:
    assert parse_weapon_ability_keywords("[ MARSHBIND\n  2 ]") == ("MARSHBIND 2",)


def test_a_keyword_printed_twice_in_two_spellings_is_carried_once() -> None:
    """Two spellings resolve to one glossary entry, so carrying both would inflate every count."""
    assert parse_weapon_ability_keywords("[Marshbind 2, MARSHBIND 2, marshbind-2]") == (
        "Marshbind 2",
    )


# -- what the keys do downstream --------------------------------------------------------------


def test_the_parameter_stays_attached_and_collapses_only_at_the_key() -> None:
    keywords = parse_weapon_ability_keywords("[MARSHBIND 1, MARSHBIND 3]")

    assert keywords == ("MARSHBIND 1", "MARSHBIND 3")
    assert {keyword_key(keyword) for keyword in keywords} == {"marshbind"}


def test_a_target_parameterised_keyword_keys_per_target() -> None:
    """``FENLOCK 4+`` and ``FENLOCK 2+`` are one entry; ``TIDELOCK 4+`` is another (FR-023)."""
    keywords = parse_weapon_ability_keywords("[FENLOCK 4+, FENLOCK 2+, TIDELOCK 4+]")

    assert {keyword_key(keyword) for keyword in keywords} == {"fenlock", "tidelock"}


# -- the round trip the html emitter depends on ------------------------------------------------


@pytest.mark.parametrize(
    "keywords",
    [
        (),
        ("GLIMMERBURST",),
        ("GLIMMERBURST", "MARSHBIND 2"),
        ("FENLOCK 4+", "TIDELOCK D3", "BRACKLIGHT-BOUND"),
    ],
)
def test_the_html_emitters_formatting_reads_back_unchanged(keywords: tuple[str, ...]) -> None:
    """Mode-blindness in one line: what html mode writes is what the csv reader reads."""
    assert parse_weapon_ability_keywords(format_ability_keywords(keywords)) == keywords


def test_an_empty_keyword_list_formats_to_an_empty_field_not_an_empty_bracket() -> None:
    """An empty field is what the export prints for a weapon with no ability keyword."""
    assert format_ability_keywords(()) == ""


# -- the unbracketed-list rule (009 Finding B) --------------------------------------------------


def test_a_single_unbracketed_keyword_is_read() -> None:
    """The real export's own shape: no brackets at all, one bare token."""
    assert parse_weapon_ability_keywords("Glimmerburst") == ("Glimmerburst",)


def test_an_unbracketed_comma_separated_list_is_read() -> None:
    assert parse_weapon_ability_keywords("Glimmerburst, Marshbind 2") == (
        "Glimmerburst",
        "Marshbind 2",
    )


def test_an_unbracketed_semicolon_separated_list_is_read() -> None:
    assert parse_weapon_ability_keywords("Glimmerburst; Marshbind 2") == (
        "Glimmerburst",
        "Marshbind 2",
    )


def test_an_unbracketed_comma_inside_parentheses_is_not_a_separator() -> None:
    assert parse_weapon_ability_keywords("Marshbind (Walker, Rider), Glimmerburst") == (
        "Marshbind (Walker, Rider)",
        "Glimmerburst",
    )


def test_an_unbracketed_field_ending_in_a_period_is_prose_not_a_keyword_list() -> None:
    """The one guard: sentence-final punctuation means this row states no keyword at all."""
    assert parse_weapon_ability_keywords("Invented placeholder prose about this weapon.") == ()


def test_an_unbracketed_field_containing_an_exclamation_or_question_mark_is_also_prose() -> None:
    assert parse_weapon_ability_keywords("Beware this weapon!") == ()
    assert parse_weapon_ability_keywords("Is this a keyword?") == ()


def test_an_unbracketed_duplicate_keyword_in_two_spellings_is_carried_once() -> None:
    assert parse_weapon_ability_keywords("Marshbind 2, MARSHBIND 2, marshbind-2") == (
        "Marshbind 2",
    )


def test_a_bracketed_field_still_ignores_anything_outside_the_brackets() -> None:
    """The two rules do not blend: a bracket present anywhere still means bracket-only."""
    assert parse_weapon_ability_keywords(
        "Invented placeholder prose about this weapon. [Glimmerburst] More invented prose."
    ) == ("Glimmerburst",)


# -- the bracket-free bound (009 PR32, Finding B's fix had none) ------------------------------
#
# The bracket-free rule used to be "no bracket, no sentence-final punctuation anywhere in the
# field" -- which never asks whether a comma-split fragment is *plausibly a keyword*. A
# publisher sentence with an internal comma and no terminal punctuation sailed straight through.
# Invented here, never any real ability's wording.


def test_a_comma_split_prose_sentence_with_no_terminal_punctuation_yields_nothing() -> None:
    """The IP-boundary defect this round exists to close.

    Against the pre-bound code this returned the sentence's two comma-split halves verbatim --
    publisher-prose-shaped text emitted as two ability keywords. Neither half is anywhere near a
    real keyword's shape (each is 10+ words / 50+ characters; the widest entry this repository's
    approved glossary holds is 3 words / 35 characters), so the per-item ceiling rejects both.
    """
    assert (
        parse_weapon_ability_keywords(
            "Each time this weapon targets a unit within 6 inches, that unit suffers a "
            "mortal wound on a roll of 4 or more"
        )
        == ()
    )


def test_a_real_bare_list_still_yields_its_keywords_under_the_new_bound() -> None:
    assert parse_weapon_ability_keywords("Assault, Rapid Fire 1") == ("Assault", "Rapid Fire 1")


def test_a_single_bare_token_still_yields_one_keyword_under_the_new_bound() -> None:
    assert parse_weapon_ability_keywords("Blast") == ("Blast",)


def test_a_bracketed_field_is_byte_for_byte_unaffected_by_the_new_bound() -> None:
    """The ceiling and the per-item punctuation guard apply only to the bracket-free rule.

    A bracketed field is trusted verbatim, exactly as before -- even a group that would fail
    the bracket-free ceiling on word count and length passes through untouched.
    """
    assert parse_weapon_ability_keywords(
        "[Each time this weapon targets a unit within 6 inches]"
    ) == ("Each time this weapon targets a unit within 6 inches",)


# -- the per-item punctuation guard (009 PR32, item 2) -----------------------------------------


def test_one_trailing_period_no_longer_empties_the_whole_row() -> None:
    """Regression case: one stray period on a bare list used to drop every keyword on the row."""
    assert parse_weapon_ability_keywords("Assault, Rapid Fire 1.") == ("Assault", "Rapid Fire 1")


def test_a_lone_sentence_ending_in_a_period_is_still_prose_not_a_keyword() -> None:
    """No separator at all means the trailing period is not a list terminator to forgive."""
    assert parse_weapon_ability_keywords("Invented placeholder prose about this weapon.") == ()


def test_a_non_final_item_with_sentence_punctuation_is_dropped_without_emptying_the_row() -> None:
    assert parse_weapon_ability_keywords("Beware this weapon!, Assault") == ("Assault",)
