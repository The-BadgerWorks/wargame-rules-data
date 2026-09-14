# AI-Assisted: Claude Code (model: claude-sonnet-5) - 010 round 1: csv-arm row routing at the reader
# boundary. Ports the two non-option row shapes wahapedia_html_dom._options drops, and derives
# the default-equipment table from the Datasheets export's loadout column. Row routing only:
# no grammar production, no normalization, no mode branch.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 010 round 1 fix round 1:
# `derive_equipment_from_loadout` numbers each datasheet's loadout-derived lines starting past the
# highest line `_derive_equipment_from_composition` already filed for it, instead of always from
# 1, so the two sources cannot mint colliding `(datasheet_id, line)` equipment-group ids
# (Finding 2). This rule is still live.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 010 round 2 task 1: the period heuristic
# (`_PERIOD_GAP`, `_MIN_SENTENCE_FINAL_WORD_CHARS`, `_word_ending_at`, `_segment_block`,
# `_split_on_suppressed`) is removed. Punctuation-length guessing could never tell an
# abbreviation's full stop from a genuine sentence boundary; it is replaced with a boundary
# anchored on the export's own markup — one bold subject per default-loadout sentence
# (`_BOLD_OPEN`) — which needs no guess at all. A segment whose tail is still ambiguous after
# tag-stripping (`_is_ambiguous`) is refused, not guessed either way, and reported as
# `EQP-BOUNDARY-AMBIGUOUS` on the equipment table's findings so the omission is visible.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 010 round 3 task 1: a refused sentence used
# to be dropped from `split_equipment_sentences`'s output entirely, which let later sentences on
# the same datasheet shift into its ordinal and let `derive_equipment_from_loadout` see zero
# source rows for a datasheet that in fact had one — publishing it as `none` (or `extracted`, if
# every other sentence on the card resolved) instead of `partial`. `split_equipment_sentences`
# now yields `""` at the refused sentence's own position instead of omitting it, so the row still
# reaches the equipment table (reserving the ordinal) and `curate/assemble.py` counts it as
# unparsed. `ambiguous_equipment_sentences` is removed; the refused count is read back off the
# `""` positions already in `sentences`.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 010 round 4 task 1: the live export's
# `Datasheets_options.csv` carries a `button` column the retired html arm never had — `•` marks a
# real option row, `*` marks a footnote the html arm's `<li>` walk never delivered to the options
# grammar. `_is_option_row` now takes the row's fields (not just the description) and refuses a
# footnote row before either existing check runs; `drop_non_option_rows` counts the routed rows
# per datasheet and raises one `OPT-FOOTNOTE-ROW` finding per affected datasheet so the omission
# is visible instead of silently lowering the denominator (a repeat of round 1's placeholder-row
# decision, at the reader boundary, never in the grammar).
"""Row routing for the bulk-export reader — which table a row belongs in, and whether it is a
row at all.

Everything here decides *membership*, never *meaning*: a row is dropped because the html arm
never delivered its shape to the grammar, or moved because the export files it under a
different heading than the one the grammar reads. The grammars stay mode-blind and unedited.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
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

#: The export's own bullet column. ``•`` is an option row; ``*`` is a footnote the html arm's
#: ``<li>`` walk never delivered to the grammar (55 of 2747 live rows, 2026-09-14). Routing it
#: out here is a denominator decision, the same one round 1 made for the placeholder row.
_FOOTNOTE_BUTTON: Final = "*"


def _is_option_row(fields: Mapping[str, str]) -> bool:
    if fields.get("button", "").strip() == _FOOTNOTE_BUTTON:
        return False
    text = fields.get("description", "").strip()
    if text.rstrip(".").strip().casefold() == _NONE_TEXT:
        return False
    return not (_DEFAULT_EQUIPMENT_SENTENCE.search(text) and not _GRANTS_A_CHOICE.search(text))


def drop_non_option_rows(detail: dict[str, CsvReadResult]) -> dict[str, CsvReadResult]:
    """Remove the two ``<li>`` shapes the html extractor never handed to the options grammar,
    plus the export's own footnote rows (``button`` ``*``), which the html arm never had."""
    options = detail.get(OPTIONS_TABLE)
    if options is None:
        return detail
    kept = []
    footnote_counts: dict[str, int] = {}
    for row in options.rows:
        if _is_option_row(row.fields):
            kept.append(row)
            continue
        if row.fields.get("button", "").strip() == _FOOTNOTE_BUTTON:
            datasheet_id = row.fields.get("datasheet_id", "")
            footnote_counts[datasheet_id] = footnote_counts.get(datasheet_id, 0) + 1
    if len(kept) == len(options.rows):
        return detail
    new_findings = [
        build_finding(
            "OPT-FOOTNOTE-ROW",
            entity_refs=[datasheet_id],
            detail={
                "datasheet_id": datasheet_id,
                "rows": count,
                "file_name": OPTIONS_TABLE,
            },
        )
        for datasheet_id, count in footnote_counts.items()
    ]
    updated = dict(detail)
    updated[OPTIONS_TABLE] = replace(
        options, rows=tuple(kept), findings=options.findings + tuple(new_findings)
    )
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
    """Every default-loadout sentence of ``text`` in text order — a refused one as ``""``.

    The empty string keeps the sentence's position, so the row emitted for it reserves its
    ordinal (later ``eq-…`` ids do not move) and ``curate/assemble.py`` counts it as unparsed
    (the datasheet's state is ``partial``, never ``extracted`` or ``none``).
    """
    return tuple(
        "" if _is_ambiguous(segment) else segment.strip()
        for segment in _bold_segments(text)
        if _EQUIPMENT_MARKER.search(segment)
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
        refused = sum(1 for sentence in sentences if not sentence)
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
