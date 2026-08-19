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
