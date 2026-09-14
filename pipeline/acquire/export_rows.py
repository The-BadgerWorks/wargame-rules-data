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
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 010 round 2 task 1: the period heuristic
# (`_PERIOD_GAP`, `_MIN_SENTENCE_FINAL_WORD_CHARS`, `_word_ending_at`, `_segment_block`,
# `_split_on_suppressed`) is removed. Punctuation-length guessing could never tell an
# abbreviation's full stop from a genuine sentence boundary; it is replaced with a boundary
# anchored on the export's own markup — one bold subject per default-loadout sentence
# (`_BOLD_OPEN`) — which needs no guess at all. A segment whose tail is still ambiguous after
# tag-stripping (`_is_ambiguous`) is refused, not guessed either way, and reported as
# `EQP-BOUNDARY-AMBIGUOUS` on the equipment table's findings so the omission is visible.
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

from pipeline.models.findings import Finding
from pipeline.models.source import WahapediaRow
from pipeline.parse.equipment_grammar import EQUIPMENT_TABLE
from pipeline.parse.wahapedia_csv import CsvReadResult
from pipeline.report.catalogue import build_finding

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
#: A line-break tag inside a loadout cell is layout, never a sentence boundary: 20 live cells
#: carry one inside a single item list. Replaced by a space before anything else looks at the text.
_BR_TAG: Final = re.compile(r"<br\s*/?>", re.IGNORECASE)
#: The export states each default-loadout sentence with its subject in bold. Measured 2026-09-14
#: on the live export: 1636 of 1653 cells are exactly one bold subject per sentence. Splitting on
#: the opening tag (zero-width, so the tag stays with its sentence) is the structural boundary.
_BOLD_OPEN: Final = re.compile(r"(?=<b>)", re.IGNORECASE)
_ANY_TAG: Final = re.compile(r"<[^>]+>")
#: After the marker, a full stop followed by whitespace and three or more further words is
#: ambiguous: a trailing sentence (which must never enter an item name) or an abbreviation inside
#: an item name (which must never be cut). Ten of 1915 live sentences; refused, never guessed.
_AMBIGUOUS_TAIL: Final = re.compile(r"\.\s+(?:\S+\s+){2}\S+")


def _is_ambiguous(sentence: str) -> bool:
    marker = _EQUIPMENT_MARKER.search(sentence)
    if marker is None:
        return False
    tail = _ANY_TAG.sub("", sentence[marker.end() :]).strip()
    return _AMBIGUOUS_TAIL.search(tail) is not None


def _bold_segments(text: str) -> list[str]:
    """Cut at every opening bold tag, then re-join a tagless-marker segment onto its sentence.

    A segment without the marker is one of two things: a separate sentence (the previous
    segment ended with a full stop) — kept apart so it is dropped below — or emphasis inside the
    previous sentence's item list (no full stop before it) — re-joined so no item is lost.
    """
    merged: list[str] = []
    for segment in _BOLD_OPEN.split(_BR_TAG.sub(" ", text)):
        if not segment.strip():
            continue
        if not merged or _EQUIPMENT_MARKER.search(segment):
            merged.append(segment)
            continue
        previous_text = _ANY_TAG.sub("", merged[-1]).rstrip()
        if previous_text.endswith("."):
            merged.append(segment)
        else:
            merged[-1] += segment
    return merged


def split_equipment_sentences(text: str) -> tuple[str, ...]:
    """Every sentence of ``text`` that states a default loadout, in text order.

    Boundaries come from the export's own markup (one bold subject per sentence), never from
    punctuation. A segment carrying no marker is dropped. A segment whose tail is ambiguous
    (:func:`_is_ambiguous`) is dropped here too; :func:`derive_equipment_from_loadout` reports
    it as ``EQP-BOUNDARY-AMBIGUOUS`` so the omission is visible, not silent.
    """
    return tuple(
        segment.strip()
        for segment in _bold_segments(text)
        if _EQUIPMENT_MARKER.search(segment) and not _is_ambiguous(segment)
    )


def ambiguous_equipment_sentences(text: str) -> int:
    """How many marker-bearing segments of ``text`` :func:`split_equipment_sentences` refused."""
    return sum(
        1
        for segment in _bold_segments(text)
        if _EQUIPMENT_MARKER.search(segment) and _is_ambiguous(segment)
    )


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
    boundary_findings: list[Finding] = []
    for row in datasheets.rows:
        datasheet_id = row.fields.get("id", "")
        if not datasheet_id:
            continue
        sentences = split_equipment_sentences(row.fields.get("loadout", ""))
        refused = ambiguous_equipment_sentences(row.fields.get("loadout", ""))
        if refused:
            boundary_findings.append(
                build_finding(
                    "EQP-BOUNDARY-AMBIGUOUS",
                    entity_refs=[datasheet_id],
                    detail={
                        "datasheet_id": datasheet_id,
                        "refused_sentences": refused,
                        "file_name": EQUIPMENT_TABLE,
                    },
                )
            )
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
    if not derived and not boundary_findings:
        return detail
    updated = dict(detail)
    updated[EQUIPMENT_TABLE] = CsvReadResult(
        file_name=EQUIPMENT_TABLE,
        field_names=("datasheet_id", "line", "description"),
        rows=(existing.rows if existing else ()) + tuple(derived),
        repairs=existing.repairs if existing else 0,
        findings=(existing.findings if existing else ()) + tuple(boundary_findings),
    )
    return updated
