# AI-Assisted: Claude Opus 5 - 010 R6 task 5. Failing-first receipt for the printed-form parity
# gap round 6 measured against the published tree: 6 720 skill pairs and 4 257 range pairs differ
# by format alone, plus 864 invulnerable-save pairs and 2 015 base-size pairs, and 1 660
# datasheets differ on keyword case alone (every figure derived by
# `tools/compare_published_tree.py`). The export states the bare value, the published tree
# states the printed one, and the cutover's parity target is the published form.
"""The printed forms the published tree carries, minted from the export's bare values.

The three functions are **pure and idempotent**: the reader may hand them either form, because
one arm of the acquisition states `3` and the other states `3+`, so an already-printed value has
to pass through untouched rather than grow a second suffix. Each table below therefore carries
its own pass-through case alongside the conversion it exists for.

All identifiers, names and prose here are invented; only the stat value shapes (``'3+'``,
``'12"'``, ``'(⌀32mm)'``) and the header shape come from the export and the published tree.
"""

from __future__ import annotations

import pytest

from pipeline.curate.assemble import _detail_datasheet_fields, _faction_keywords_by_datasheet
from pipeline.models.curated import CuratedKeyword, CuratedModelLine, CuratedWeaponLine
from pipeline.normalize.characteristics import printed_base_size, printed_range, printed_roll
from pipeline.parse.wahapedia_csv import CsvReadResult, read_text


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("3", "3+"),
        ("3+", "3+"),
        ("-", "-"),
        ("N/A", "N/A"),
    ],
)
def test_printed_roll(value: str, expected: str) -> None:
    assert printed_roll(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("12", '12"'),
        ('12"', '12"'),
        ("Melee", "Melee"),
    ],
)
def test_printed_range(value: str, expected: str) -> None:
    assert printed_range(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("32mm", "(⌀32mm)"),
        ("(⌀32mm)", "(⌀32mm)"),
        (None, None),
    ],
)
def test_printed_base_size(value: str | None, expected: str | None) -> None:
    assert printed_base_size(value) == expected


_DATASHEETS_CSV = (
    "id|name|faction_id|source_id|legend|role|loadout|transport|virtual|leader_head|"
    "leader_footer|damaged_w|damaged_description|link|\n"
    "ds1|Test Unit|TF|1||Battleline|||0|||||https://example.invalid/ds/ds1|\n"
)
_MODELS_HEADER = (
    "datasheet_id|line|name|M|T|Sv|inv_sv|inv_sv_descr|W|Ld|OC|base_size|base_size_descr|\n"
)
_WARGEAR_HEADER = (
    "datasheet_id|line|line_in_wargear|dice|name|description|range|type|A|BS_WS|S|AP|D|\n"
)
_KEYWORDS_HEADER = "datasheet_id|keyword|model|is_faction_keyword|\n"
_EMPTY_ABILITIES_CSV = "datasheet_id|line|ability_id|model|name|description|type|parameter|\n"

#: A model row stating the export's bare `inv_sv` and `base_size`, and a weapon row stating the
#: export's bare `range` and `BS_WS`. Invented names; the published tree prints `4+`, `(⌀32mm)`,
#: `12"` and `3+` for this shape.
_MODELS_CSV = _MODELS_HEADER + "ds1|1|Test Trooper|6|4|3|4||2|6|2|32mm||\n"
_WARGEAR_CSV = _WARGEAR_HEADER + "ds1|1|1||Test Emitter||12|Ranged|2|3|5|1|1|\n"
_KEYWORDS_CSV = _KEYWORDS_HEADER + "ds1|Fen Wardens||true|\n"


def _detail() -> dict[str, CsvReadResult]:
    return {
        "Datasheets.csv": read_text("Datasheets.csv", _DATASHEETS_CSV),
        "Datasheets_models.csv": read_text("Datasheets_models.csv", _MODELS_CSV),
        "Datasheets_wargear.csv": read_text("Datasheets_wargear.csv", _WARGEAR_CSV),
        "Datasheets_keywords.csv": read_text("Datasheets_keywords.csv", _KEYWORDS_CSV),
        "Datasheets_abilities.csv": read_text("Datasheets_abilities.csv", _EMPTY_ABILITIES_CSV),
    }


def test_a_weapon_row_publishes_the_printed_skill_and_range() -> None:
    """Reverted, this is red on `skill`: the bare `'3'` is published where `'3+'` is expected."""
    fields, _ = _detail_datasheet_fields("ds1", _detail(), frozenset(), ability_names={})

    weapons: list[CuratedWeaponLine] = fields["weapons"]  # type: ignore[assignment]
    assert [(w.skill, w.range) for w in weapons] == [("3+", '12"')]


def test_a_model_row_publishes_the_printed_invuln_save_and_base_size() -> None:
    """Reverted, this is red on `invuln_save`: `'4'` is published where `'4+'` is expected."""
    fields, _ = _detail_datasheet_fields("ds1", _detail(), frozenset(), ability_names={})

    models: list[CuratedModelLine] = fields["models"]  # type: ignore[assignment]
    assert [(m.invuln_save, m.base_size) for m in models] == [("4+", "(⌀32mm)")]


def test_a_keyword_stated_in_title_case_publishes_upper_case() -> None:
    """Reverted, this is red: the title-case token is published as stated."""
    fields, _ = _detail_datasheet_fields("ds1", _detail(), frozenset(), ability_names={})

    keywords: list[CuratedKeyword] = fields["keywords"]  # type: ignore[assignment]
    assert [k.keyword for k in keywords] == ["FEN WARDENS"]


#: A curated chapter keyword as `curation/keyword-classes.json` states one: upper-case, invented.
#: `match.py` builds `own_chapter_keywords` from exactly this token, and intersects it with the
#: sibling view below.
_CURATED_CHAPTER_KEYWORDS = frozenset({"FEN WARDENS"})


def test_the_sibling_keyword_view_meets_the_curated_chapter_vocabulary() -> None:
    """Match-ladder rung 3 reads this view; an empty intersection makes the rung inert.

    The assertion goes through the reader rather than around it: the fixture states the keyword
    in the export's own case, and the intersection has to survive that. Reverted, this is red —
    the reader yields the title-case token, the intersection with the upper-case curated
    vocabulary is empty, and no chapter disambiguation can ever fire on this arm.
    """
    observed = _faction_keywords_by_datasheet(_detail())["ds1"]

    assert observed & _CURATED_CHAPTER_KEYWORDS, (
        "the sibling keyword view does not meet the curated chapter vocabulary: read "
        f"{len(observed)} faction keyword(s), intersection empty — match-ladder rung 3 is "
        "inert on this arm and chapter disambiguation never fires"
    )
