# AI-Assisted: Claude Code (model: claude-sonnet-5) - Tests for the Cyrillic/Latin homoglyph
# fold: the real observed case, the all-Cyrillic negative case that must never be transliterated,
# the mixed-script cases either side of the heuristic's edge, and the wiring through strip_field.
"""Tests for :mod:`pipeline.normalize.homoglyphs` (and its one call site).

The negative cases carry the weight here. A missed fold is a blocking `CON-IP-BOUNDARY` that a
curator sees, reads, and resolves once; a **wrong** fold silently transliterates a genuinely
Cyrillic string into a plausible-looking Latin one that nothing downstream can flag, because the
result passes every check the pipeline has. So each case states not just what happens but which
condition of the heuristic decides it.
"""

from __future__ import annotations

import pytest

from pipeline.normalize.homoglyphs import fold_homoglyphs, has_homoglyphs
from pipeline.normalize.ip_strip import strip_field

#: The real case. `Сombi-bolter` in the detail source's weapon export begins with
#: U+0421 CYRILLIC CAPITAL LETTER ES where U+0043 LATIN CAPITAL LETTER C was meant, which is
#: what raised `CON-IP-BOUNDARY /datasheetWeapons/826/name` on the first live candidate build.
OBSERVED_COMBI_WEAPON = "Сombi-bolter"


def test_the_observed_weapon_name_folds_to_its_latin_spelling() -> None:
    assert fold_homoglyphs(OBSERVED_COMBI_WEAPON) == "Combi-bolter"
    assert OBSERVED_COMBI_WEAPON != "Combi-bolter", "the fixture must really carry the look-alike"


def test_the_observed_weapon_name_is_clean_by_the_time_it_leaves_strip_field() -> None:
    """The wiring, not the transform: the IP scan must never be handed the Cyrillic form."""
    result = strip_field(OBSERVED_COMBI_WEAPON, field="weapon.name")
    assert result.text == "Combi-bolter"
    assert result.text.isascii()


def test_an_all_cyrillic_string_is_left_completely_untouched() -> None:
    """`Раса` is four Cyrillic letters that *all* have Latin homoglyphs.

    Transliterating it would produce `Paca` — a word that looks entirely legitimate and that
    nothing downstream could ever flag, because the result passes every check the pipeline has.
    Two conditions refuse it independently (`MIN_LATIN_LETTERS` and `MAX_INTERLOPER_SHARE`),
    which is exactly the redundancy this case is here to hold in place.
    """
    cyrillic_word = "Раса"
    assert fold_homoglyphs(cyrillic_word) == cyrillic_word
    assert not has_homoglyphs(cyrillic_word)


def test_the_observed_classification_artefact_survives_the_fold_unchanged() -> None:
    """`Special (правая колонка)` is a layout label, not a name with a slipped keystroke.

    It stays the business of `pipeline.normalize.ability_types` and the IP scan. Two independent
    conditions refuse it — unmappable Cyrillic letters, and a share far above the ceiling — so
    loosening either one alone cannot start rewriting it.
    """
    artefact = "Special (правая колонка)"
    assert fold_homoglyphs(artefact) == artefact
    assert strip_field(artefact, field="type").text == artefact


@pytest.mark.parametrize(
    ("value", "why"),
    [
        pytest.param(
            "Раса A",
            "one Latin letter among four look-alikes is not evidence of a Latin-script string",
            id="mostly-cyrillic-with-a-latin-fragment",
        ),
        pytest.param(
            "Сореа",
            "no Latin letters at all, every character mappable — the transliteration trap",
            id="all-mappable-cyrillic",
        ),
        pytest.param(
            "Сомбі",
            "an unmappable Cyrillic letter means this is Cyrillic text, not a typo",
            id="one-unmappable-letter",
        ),
        pytest.param(
            "Соmbat",
            "two look-alikes among six letters is a third of them — over the share ceiling",
            id="just-over-the-share-ceiling",
        ),
    ],
)
def test_a_predominantly_cyrillic_string_is_never_rewritten(value: str, why: str) -> None:
    assert fold_homoglyphs(value) == value, why


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        pytest.param("Bolt rifle", "Bolt rifle", id="pure-latin-is-a-no-op"),
        pytest.param("", "", id="empty"),
        pytest.param("2+", "2+", id="no-letters-at-all"),
        pytest.param("T’au pulse rifle", "T’au pulse rifle", id="typography-untouched"),
    ],
)
def test_strings_with_nothing_to_fold_come_back_identical(value: str, expected: str) -> None:
    assert fold_homoglyphs(value) == expected


def test_a_name_carrying_more_look_alikes_than_the_ceiling_is_left_for_a_human() -> None:
    """Four interlopers is not a keystroke slip, however low the share works out at.

    Every character here is individually mappable and the share is well under the ceiling — it
    is the *absolute* limit that refuses this one, which exists so a long Latin string cannot
    quietly absorb an arbitrary number of rewrites just by being long enough.
    """
    heavily_mixed = "Сombi-bоlter аttachment kіt"
    assert fold_homoglyphs(heavily_mixed) == heavily_mixed


def test_a_name_exactly_at_the_share_ceiling_still_folds() -> None:
    """One look-alike in four letters is the boundary, and the boundary is inclusive."""
    assert fold_homoglyphs("Аtom") == "Atom"


def test_the_fold_is_idempotent() -> None:
    once = fold_homoglyphs(OBSERVED_COMBI_WEAPON)
    assert fold_homoglyphs(once) == once


def test_a_single_interloper_mid_string_folds() -> None:
    """The observed class is a leading character, but nothing about it is positional."""
    assert fold_homoglyphs("Plasma incinerаtor") == "Plasma incinerator"
