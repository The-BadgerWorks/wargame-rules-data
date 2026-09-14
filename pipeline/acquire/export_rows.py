# AI-Assisted: Claude Code (model: claude-sonnet-5) - 010 round 1: csv-arm row routing at the reader
# boundary. Ports the two non-option row shapes wahapedia_html_dom._options drops, and derives
# the default-equipment table from the Datasheets export's loadout column. Row routing only:
# no grammar production, no normalization, no mode branch.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 010 round 1 fix round 1: `_SENTENCE_BREAK`
# now captures its separator so a false internal-period split can be rejoined onto the preceding
# marker-bearing fragment instead of dropping the tail (Finding 1), and
# `derive_equipment_from_loadout` numbers each datasheet's loadout-derived lines starting past the
# highest line `_derive_equipment_from_composition` already filed for it, instead of always from
# 1, so the two sources cannot mint colliding `(datasheet_id, line)` equipment-group ids
# (Finding 2). Fix round 2: no code change — see the header note in
# `tests/unit/test_export_row_routing.py` for the accepted, measured-at-zero residual this left.
# AI-Assisted: Claude Code (model: claude-opus-5) - 010 round 1 final-review fix wave: the
# fold-backward above is REVERSED (T1-1/T1-2). It appended a marker-less trailing sentence onto the
# preceding loadout sentence, and `equipment_grammar._parse_items` then carried that prose inside
# the LAST item's published `item_name`; it also deleted a marker-less buffer, losing the subject
# clause when the false full stop preceded the marker. `split_equipment_sentences` now applies one
# narrow rule instead: a line-break tag always ends a sentence, a full stop plus whitespace ends
# one only when the word ending at that full stop is longer than three characters, and only
# marker-bearing sentences are kept (a trailing non-equipment sentence is dropped, not folded).
# The two-marker guard in `_split_on_suppressed` makes the length rule self-verifying. The
# fix-round-2 pin test for the old misattribution is deleted: the misattribution no longer occurs.
"""Row routing for the bulk-export reader — which table a row belongs in, and whether it is a
row at all.

Everything here decides *membership*, never *meaning*: a row is dropped because the html arm
never delivered its shape to the grammar, or moved because the export files it under a
different heading than the one the grammar reads. The grammars stay mode-blind and unedited.
"""

from __future__ import annotations

import re
from dataclasses import replace
from typing import Final

from pipeline.models.source import WahapediaRow
from pipeline.parse.equipment_grammar import EQUIPMENT_TABLE
from pipeline.parse.wahapedia_csv import CsvReadResult

OPTIONS_TABLE: Final = "Datasheets_options.csv"
DATASHEETS_TABLE: Final = "Datasheets.csv"

#: Mirrors ``wahapedia_html_dom._NONE_TEXT``: the source's "publishes none" placeholder, compared
#: with trailing full stops removed because the page prints both spellings.
_NONE_TEXT: Final = "none"
#: Mirrors ``wahapedia_html_dom._DEFAULT_EQUIPMENT_SENTENCE`` and ``_GRANTS_A_CHOICE``.
_DEFAULT_EQUIPMENT_SENTENCE: Final = re.compile(r"\bis equipped with\s*:", re.IGNORECASE)
_GRANTS_A_CHOICE: Final = re.compile(r"\bcan\b", re.IGNORECASE)


def _is_option_row(description: str) -> bool:
    text = description.strip()
    if text.rstrip(".").strip().casefold() == _NONE_TEXT:
        return False
    return not (_DEFAULT_EQUIPMENT_SENTENCE.search(text) and not _GRANTS_A_CHOICE.search(text))


def drop_non_option_rows(detail: dict[str, CsvReadResult]) -> dict[str, CsvReadResult]:
    """Remove the two ``<li>`` shapes the html extractor never handed to the options grammar."""
    options = detail.get(OPTIONS_TABLE)
    if options is None:
        return detail
    kept = tuple(row for row in options.rows if _is_option_row(row.fields.get("description", "")))
    if len(kept) == len(options.rows):
        return detail
    updated = dict(detail)
    updated[OPTIONS_TABLE] = replace(options, rows=kept)
    return updated


#: The same marker ``equipment_grammar._MARKER`` and ``detail_source._EQUIPMENT_MARKER`` carry,
#: kept as this module's own copy on the same terms they keep theirs.
_EQUIPMENT_MARKER: Final = re.compile(r"\b(?:is|are)\s+equipped\s+with\s*:", re.IGNORECASE)
#: A line-break tag: always a sentence boundary inside one ``loadout`` cell.
_BR_TAG: Final = re.compile(r"<br\s*/?>", re.IGNORECASE)
#: A full stop followed by whitespace: a boundary only when the word ending at that full stop is
#: longer than :data:`_MIN_SENTENCE_FINAL_WORD_CHARS` characters. The whitespace alone is the cut,
#: so the full stop stays with the sentence it ends.
_PERIOD_GAP: Final = re.compile(r"(?<=\.)\s+")
#: An abbreviation short enough to be one ("Mk.") does not end a sentence; a word longer than this
#: does. Measured against the ambiguous class this round counted in the live export, and made
#: self-verifying by the two-marker guard in :func:`split_equipment_sentences` rather than trusted.
_MIN_SENTENCE_FINAL_WORD_CHARS: Final = 3


def _word_ending_at(text: str, period_index: int) -> str:
    """The run of non-whitespace, non-full-stop characters immediately before ``period_index``.

    An *empty* run — a full stop directly after whitespace, or after another full stop — is the
    conservative branch: length 0 is not longer than the threshold, so the candidate is
    **suppressed** and no text can be split off and dropped. The two-marker guard still recovers a
    genuine boundary there, so suppressing costs nothing that the guard does not give back.
    """
    start = period_index
    while start > 0 and not text[start - 1].isspace() and text[start - 1] != ".":
        start -= 1
    return text[start:period_index]


def _segment_block(block: str) -> list[tuple[str, list[tuple[int, int]]]]:
    """One line-break-free block cut at its accepted full-stop boundaries.

    Each result is the segment text plus the candidate boundaries inside it that rule 2
    **suppressed**, as offsets into that segment, which is what the guard needs to undo a wrong
    suppression. The word run is measured inside the block, so a line-break tag can never be read
    as part of the word ending a sentence.
    """
    segments: list[tuple[str, list[tuple[int, int]]]] = []
    start = 0
    suppressed: list[tuple[int, int]] = []
    for match in _PERIOD_GAP.finditer(block):
        word = _word_ending_at(block, match.start() - 1)
        if len(word) > _MIN_SENTENCE_FINAL_WORD_CHARS:
            segments.append((block[start : match.start()], suppressed))
            start, suppressed = match.end(), []
        else:
            suppressed.append((match.start() - start, match.end() - start))
    segments.append((block[start:], suppressed))
    return segments


def _split_on_suppressed(segment: str, suppressed: list[tuple[int, int]]) -> list[str]:
    """The guard: a segment carrying two or more markers had a real boundary suppressed.

    Two default-loadout statements never share one sentence, so a second marker occurrence proves
    the length rule guessed wrong on a sentence whose final word is short. Split at the earliest
    suppressed candidate lying between the first marker and the second — the only place the real
    boundary can be — and re-check the tail, so three statements in a row resolve too.
    """
    markers = list(_EQUIPMENT_MARKER.finditer(segment))
    if len(markers) < 2:
        return [segment]
    for index, (cut_start, cut_end) in enumerate(suppressed):
        if markers[0].end() <= cut_start <= markers[1].start():
            tail = segment[cut_end:]
            tail_suppressed = [(s - cut_end, e - cut_end) for s, e in suppressed[index + 1 :]]
            return [segment[:cut_start], *_split_on_suppressed(tail, tail_suppressed)]
    return [segment]


def split_equipment_sentences(text: str) -> tuple[str, ...]:
    """Every sentence of ``text`` that states a default loadout, in text order.

    Two rules and one guard, and deliberately nothing else:

    1. A line-break tag is always a sentence boundary.
    2. A full stop followed by whitespace is a boundary only when the word ending at that full
       stop is longer than three characters, so an abbreviation-style internal full stop
       ("Mk. II blade") neither truncates the item list nor deletes the subject clause before the
       marker — the clause the equipment linker reads to attribute the equipment.
    3. Only the resulting sentences that carry the equipment marker are kept. A genuine trailing
       non-equipment sentence is **dropped**, never folded onto the loadout sentence before it:
       folding it put publisher prose inside a published ``item_name``, because the equipment
       grammar reads whatever trails the last list item as part of that item's name.

    The guard makes rule 2 self-verifying instead of a bare guess: a kept sentence holding two or
    more marker occurrences means rule 2 suppressed a real boundary, so it is split there after
    all (:func:`_split_on_suppressed`).
    """
    sentences: list[str] = []
    for block in _BR_TAG.split(text):
        for segment, suppressed in _segment_block(block):
            for piece in _split_on_suppressed(segment, suppressed):
                stripped = piece.strip()
                if stripped and _EQUIPMENT_MARKER.search(stripped):
                    sentences.append(stripped)
    return tuple(sentences)


def derive_equipment_from_loadout(detail: dict[str, CsvReadResult]) -> dict[str, CsvReadResult]:
    """csv-mode's source for ``Datasheets_unit_equipment.csv`` (010 R1, spec §4.2).

    The export publishes no equipment table; it states each datasheet's default loadout in
    ``Datasheets.csv``'s ``loadout`` column, one prose cell per datasheet, sometimes holding more
    than one sentence. Each sentence becomes one row in the same ``datasheet_id|line|description``
    shape the html arm manufactured, so ``curate/assemble.py`` and the equipment grammar are
    unchanged. The text is carried as-is: it is a prose-bearing field and the grammar's own
    ``pre_pass`` is the only reader that may look inside it.

    Numbering starts one past the highest existing integer ``line`` already recorded for that
    ``datasheet_id`` in ``detail``'s equipment table (0 when there is none, so "from 1" holds
    whenever nothing else derived a row for that datasheet) — never from 1 unconditionally.
    ``_derive_equipment_from_composition`` runs first and can already have filed a row for the
    same ``datasheet_id`` under ``line="1"``; numbering from 1 here too would mint two rows
    sharing one ``(datasheet_id, line)`` pair, and ``curate/assemble.py``'s
    ``equipment_group_id`` turns that pair into a single group id shared by two distinct rows —
    a published-identifier collision (spec §4.6), not merely a cosmetic duplicate.
    """
    datasheets = detail.get(DATASHEETS_TABLE)
    if datasheets is None:
        return detail
    existing = detail.get(EQUIPMENT_TABLE)
    next_line: dict[str, int] = {}
    if existing is not None:
        for existing_row in existing.rows:
            existing_id = existing_row.fields.get("datasheet_id", "")
            try:
                existing_line = int(existing_row.fields.get("line", ""))
            except ValueError:
                existing_line = 0
            if existing_line > next_line.get(existing_id, 0):
                next_line[existing_id] = existing_line

    derived: list[WahapediaRow] = []
    for row in datasheets.rows:
        datasheet_id = row.fields.get("id", "")
        if not datasheet_id:
            continue
        sentences = split_equipment_sentences(row.fields.get("loadout", ""))
        if not sentences:
            continue
        start = next_line.get(datasheet_id, 0)
        for offset, sentence in enumerate(sentences, start=1):
            derived.append(
                WahapediaRow(
                    file_name=EQUIPMENT_TABLE,
                    line_number=row.line_number,
                    fields={
                        "datasheet_id": datasheet_id,
                        "line": str(start + offset),
                        "description": sentence,
                    },
                    repaired=row.repaired,
                )
            )
        next_line[datasheet_id] = start + len(sentences)
    if not derived:
        return detail
    updated = dict(detail)
    updated[EQUIPMENT_TABLE] = CsvReadResult(
        file_name=EQUIPMENT_TABLE,
        field_names=("datasheet_id", "line", "description"),
        rows=(existing.rows if existing else ()) + tuple(derived),
        repairs=existing.repairs if existing else 0,
        findings=existing.findings if existing else (),
    )
    return updated
