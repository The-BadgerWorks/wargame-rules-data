# AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote the FR-017/SC-005 name-hygiene test
# (008 task T024, Foundational phase): every name any option or equipment production resolves,
# over the WHOLE fixture corpus rather than a hand-listed set of datasheet ids, carries no
# footnote-marker artifact, no leftover markup fragment, and no trailing punctuation artifact.
# Driven from the fixture corpus (every row of `Datasheets_options.csv` and
# `Datasheets_unit_equipment.csv`, read the ordinary way) so a production Phase 3/4/5 adds later
# — and every fixture row it newly resolves — is covered automatically; nobody has to remember to
# list its datasheet id here.
"""FR-017 / SC-005: a published name is never the display residue of something extraction should
already have removed.

`_parse_object`/`_item` (`options_grammar.py`) already strip `FOOTNOTE_MARK` and a trailing
``.;,:`` run (`007` research D4.1, guarantee 21); `equipment_grammar.py`'s own item/model readers
do the same. This file does not re-test that stripping in isolation —
`test_options_grammar.py`/`test_equipment_grammar.py` already cover it per production — it is the
**corpus-wide** guarantee: every name any production resolves, over every row the fixture corpus
states, passes the same three checks `pipeline/validate/contract_checks.py::check_marker_residue`
enforces at build time against the live corpus (guarantee 21, blocking). Catching an escape here,
at parse time against a synthetic fixture, is cheaper than catching it there.

**Why three separate checks rather than one combined regex.** Each artifact has a different
origin and a different fix: a footnote marker surviving means the `FOOTNOTE_MARK` strip was
skipped; a markup fragment (`<`/`>`) surviving means the `<ul>`/`<li>` split or `pre_pass` missed
a variant form; a trailing punctuation artifact surviving means the `.rstrip(".;,:")` was skipped
or applied before a marker strip that then exposed a new one. A single merged assertion would
report "a name is dirty" — three report *which* extraction step let it through.
"""

from __future__ import annotations

import re
from pathlib import Path

from pipeline.parse.composition_grammar import FOOTNOTE_MARK
from pipeline.parse.equipment_grammar import parse_sentence
from pipeline.parse.options_grammar import parse_row, split_conjuncts, split_replaced
from pipeline.parse.wahapedia_csv import read_file

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "enrichment" / "wahapedia"
OPTIONS_CSV = FIXTURES / "Datasheets_options.csv"
EQUIPMENT_CSV = FIXTURES / "Datasheets_unit_equipment.csv"

#: A leftover HTML/markup fragment — the ``<ul>``/``<li>`` split failed to remove, or a stray
#: angle bracket escaped `pre_pass`. Distinct from `FOOTNOTE_MARK`, which is typographic rather
#: than markup.
_MARKUP_FRAGMENT: re.Pattern[str] = re.compile(r"[<>]")

#: A trailing punctuation artifact — a name ending in one of the four characters
#: `_parse_object`/`_item` already ``.rstrip(".;,:")``. A name legitimately containing one of
#: these mid-string (an abbreviation, say) is not what this catches — only a **trailing** one,
#: which is always either the sentence's own full stop or a list separator that leaked through.
_TRAILING_PUNCTUATION: re.Pattern[str] = re.compile(r"[.;,:]$")

#: ``(datasheet_id, line, name)`` — one entry per name, so a failure names the exact fixture row
#: and the exact name that failed, never merely "some name somewhere".
_NameOccurrence = tuple[str, int, str]


def _option_names(description: str) -> list[str]:
    """Every name one option row resolves to: each choice's own name, its eligible model name
    (where the head scopes to a subset), and the given-up side's decomposed items (007 T021) —
    the same fields `check_marker_residue`'s candidate list scans at build time, read here
    straight off `parse_row` rather than through a full `_option_structure` assembly."""
    parsed = parse_row(description)
    if parsed is None:
        return []
    names: list[str] = [choice.name for choice in parsed.choices]
    names.extend(
        item.name
        for choice in parsed.choices
        for item in split_conjuncts(choice.name, choice.count)
    )
    if parsed.eligible_model_name is not None:
        names.append(parsed.eligible_model_name)
    if parsed.replaced_clause:
        names.extend(item.name for item in split_replaced(parsed.replaced_clause))
    return names


def _equipment_names(description: str) -> list[str]:
    """Every name one equipment sentence resolves to: each item's own name, and the model name
    where the subject scopes to a model group."""
    parsed = parse_sentence(description)
    if parsed is None:
        return []
    names = [item.item_name for item in parsed.items]
    if parsed.model_name is not None:
        names.append(parsed.model_name)
    return names


def _all_option_names() -> list[_NameOccurrence]:
    """Every name every option row in the fixture corpus resolves to — the WHOLE corpus, not a
    hand-listed subset of datasheet ids, which is what makes a later production's fixture rows
    covered automatically the moment they start resolving."""
    return [
        (row.fields["datasheet_id"], int(row.fields["line"]), name)
        for row in read_file(OPTIONS_CSV).rows
        for name in _option_names(row.fields["description"])
    ]


def _all_equipment_names() -> list[_NameOccurrence]:
    """Same, for every equipment sentence in the fixture corpus."""
    return [
        (row.fields["datasheet_id"], int(row.fields["line"]), name)
        for row in read_file(EQUIPMENT_CSV).rows
        for name in _equipment_names(row.fields["description"])
    ]


def test_the_fixture_corpus_resolves_at_least_one_name_of_each_kind() -> None:
    """A guard against this file silently protecting nothing: if either fixture ever stopped
    resolving a single name, every check below would vacuously pass."""
    assert _all_option_names()
    assert _all_equipment_names()


def test_no_resolved_option_name_carries_a_footnote_marker() -> None:
    offenders = [occ for occ in _all_option_names() if FOOTNOTE_MARK.search(occ[2])]
    assert offenders == []


def test_no_resolved_option_name_carries_a_markup_fragment() -> None:
    offenders = [occ for occ in _all_option_names() if _MARKUP_FRAGMENT.search(occ[2])]
    assert offenders == []


def test_no_resolved_option_name_carries_a_trailing_punctuation_artifact() -> None:
    offenders = [occ for occ in _all_option_names() if _TRAILING_PUNCTUATION.search(occ[2])]
    assert offenders == []


def test_no_resolved_equipment_name_carries_a_footnote_marker() -> None:
    offenders = [occ for occ in _all_equipment_names() if FOOTNOTE_MARK.search(occ[2])]
    assert offenders == []


def test_no_resolved_equipment_name_carries_a_markup_fragment() -> None:
    offenders = [occ for occ in _all_equipment_names() if _MARKUP_FRAGMENT.search(occ[2])]
    assert offenders == []


def test_no_resolved_equipment_name_carries_a_trailing_punctuation_artifact() -> None:
    offenders = [occ for occ in _all_equipment_names() if _TRAILING_PUNCTUATION.search(occ[2])]
    assert offenders == []
