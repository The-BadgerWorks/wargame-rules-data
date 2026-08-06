# AI-Assisted: Claude Code (model: claude-opus-5) - Wrote the weapon-ability-keyword field
# reader's suite (issue #4), confirmed failing before pipeline/normalize/weapon_abilities.py
# existed: the bracketed-group rule, the parameterised forms, the prose boundary, and the
# round trip with the html emitter's own formatter.
"""The field reader that recovers a weapon's ability keywords, and the boundary it holds.

Two properties are load-bearing and neither is obvious from the implementation:

* **Prose is not a keyword.** The detail source's ``description`` column holds the keyword list
  on some rows and free publisher prose on others, and this repository retains no publisher
  wording anywhere (Constitution Principle 4). The reader's answer for a prose row must
  therefore be *nothing at all* — not a best-effort token, not a truncated one.
* **The parameter stays attached.** ``RAPID FIRE 2`` is one keyword here and collapses to one
  glossary key downstream; splitting it into ``RAPID FIRE`` and ``2`` at this layer would put a
  second, differently-shaped normalisation in front of the one
  :mod:`pipeline.normalize.keyword_key` publishes as normative for producer and consumer alike.

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
