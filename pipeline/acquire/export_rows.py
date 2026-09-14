# AI-Assisted: Claude Code (model: claude-sonnet-5) - Authored and carried this module
# through 010 rounds 1-4: csv-arm row routing at the reader boundary (which table a row
# belongs in), markup-anchored default-loadout sentence boundaries, refusal in place of a
# guess, and the export's own footnote rows routed out of the options table. The
# round-by-round narrative lives in the commit history, not here.
# AI-Assisted: Claude Code (model: claude-opus-5) - 010 round 5 task 1: closed the PR #35
# review's routing holes - any full stop mid-tail is ambiguous (not only one with three
# words after it) and `&nbsp;` counts as the whitespace after it; the bold boundary
# tolerates tag attributes; a marker-less bold run mid-sentence refuses its sentence
# instead of re-joining a guess; the non-option shape checks read through markup and
# collapsed whitespace; and a footnote row with no `datasheet_id` raises no finding that
# could never be located.
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

#: Any element. Only ever used to read *through* markup - the tag is never a boundary, a value
#: or a finding here; `normalize/ip_strip.py` owns removing it for real, downstream.
_ANY_TAG: Final = re.compile(r"<[^>]+>")
#: A run of whitespace, and the export's two spellings of a non-breaking space. ``\s`` already
#: matches U+00A0; the HTML entity is a literal six-character run that it does not.
_WHITESPACE_RUN: Final = re.compile(r"\s+")
_NBSP: Final = re.compile(r"&nbsp;|\u00a0", re.IGNORECASE)


def _plain_text(text: str) -> str:
    """``text`` with its markup read through and every whitespace spelling collapsed to a space.

    The one shape the non-option checks and the ambiguous-tail test both compare against, so a
    row carrying a tag or a non-breaking space is recognised as the same shape as one that does
    not.
    """
    return _WHITESPACE_RUN.sub(" ", _NBSP.sub(" ", _ANY_TAG.sub("", text))).strip()


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
    """Both shape checks read the description through its markup (``<i>None.</i>`` is the
    placeholder row, not an option) and through its whitespace spellings (a non-breaking space
    between the marker's words is still the marker). Otherwise a tagged or oddly spaced copy of
    a shape the html arm dropped survives here and reaches the options grammar."""
    if fields.get("button", "").strip() == _FOOTNOTE_BUTTON:
        return False
    text = _plain_text(fields.get("description", ""))
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
            datasheet_id = row.fields.get("datasheet_id", "").strip()
            if not datasheet_id:
                # A finding whose `entity_refs` is `("",)` names no record: it cannot be
                # located, triaged or resolved, and it would accumulate one bogus count per
                # malformed row. The row is still routed out; only the unlocatable report of it
                # is suppressed.
                continue
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
#: The pattern matches ``<b`` followed by whitespace or ``>``, so an opening bold tag is
#: recognised with or without attributes; requiring ``<b>`` exactly missed every attributed
#: subject and folded its sentences into one. ``<br>`` cannot match - ``r`` is neither
#: whitespace nor ``>`` - and `_BR_TAG` has in any case already replaced it.
_BOLD_OPEN: Final = re.compile(r"(?=<b[\s>])", re.IGNORECASE)
#: After the marker, ANY full stop with something following it is ambiguous: a trailing sentence
#: (which must never enter an item name) or an abbreviation inside an item name (which must never
#: be cut). Demanding three further words let a two-word trailing sentence fold into the last
#: item's name instead. Both readings are refused, never guessed.
_AMBIGUOUS_TAIL: Final = re.compile(r"\.\s+\S")


def _is_ambiguous(sentence: str) -> bool:
    marker = _EQUIPMENT_MARKER.search(sentence)
    if marker is None:
        return False
    return _AMBIGUOUS_TAIL.search(_plain_text(sentence[marker.end() :])) is not None


def _bold_segments(text: str) -> list[tuple[str, bool]]:
    """Cut at every opening bold tag; each segment paired with whether it is refused.

    A segment without the marker is one of two things. It is a separate sentence when the
    previous segment ended with a full stop - kept apart, so the marker filter below drops it.
    Otherwise it is a bold run inside the previous sentence's item list, and where that item
    list ends cannot be known without guessing: re-joining assumes the run is an item name,
    splitting assumes it is a new subject, and the export states neither. The previous sentence
    is therefore refused (``True``), which surfaces as `EQP-BOUNDARY-AMBIGUOUS` for a curator
    rather than as an invented item name in published data.
    """
    merged: list[tuple[str, bool]] = []
    for segment in _BOLD_OPEN.split(_BR_TAG.sub(" ", text)):
        if not segment.strip():
            continue
        if not merged or _EQUIPMENT_MARKER.search(segment):
            merged.append((segment, False))
            continue
        previous, _refused = merged[-1]
        if _plain_text(previous).endswith("."):
            merged.append((segment, False))
        else:
            merged[-1] = (previous, True)
    return merged


def split_equipment_sentences(text: str) -> tuple[str, ...]:
    """Every default-loadout sentence of ``text`` in text order — a refused one as ``""``.

    The empty string keeps the sentence's position, so the row emitted for it reserves its
    ordinal (later ``eq-…`` ids do not move) and ``curate/assemble.py`` counts it as unparsed
    (the datasheet's state is ``partial``, never ``extracted`` or ``none``).
    """
    return tuple(
        "" if refused or _is_ambiguous(segment) else segment.strip()
        for segment, refused in _bold_segments(text)
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
