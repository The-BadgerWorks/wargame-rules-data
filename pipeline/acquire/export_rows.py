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
#: Candidate sentence boundaries inside one ``loadout`` cell: a line-break tag, or a full stop
#: followed by whitespace. Captured (not just matched), because an internal abbreviation-style
#: period ("Mk. II blade.") produces a false boundary here that :func:`split_equipment_sentences`
#: must undo — it needs the exact separator text back to rejoin what it wrongly split.
_SENTENCE_BREAK: Final = re.compile(r"(<br\s*/?>|(?<=\.)\s+)", re.IGNORECASE)
#: A line-break separator is reconstituted as a single space when rejoining a false split; a
#: whitespace separator is reconstituted verbatim.
_BR_TAG: Final = re.compile(r"^<br", re.IGNORECASE)


def split_equipment_sentences(text: str) -> tuple[str, ...]:
    """Every sentence of ``text`` that states a default loadout, in text order.

    ``_SENTENCE_BREAK`` only proposes candidate boundaries — a full stop followed by whitespace
    also fires inside an abbreviation ("Mk. II blade."), which would otherwise truncate the
    sentence and silently drop the tail (spec §4.2: the prose is carried as-is). A candidate
    fragment that does not itself carry the equipment marker is therefore folded back onto the
    fragment before it, provided that fragment DOES carry the marker — restoring the exact
    separator text the split consumed (a single space in place of a ``<br>`` tag). A marker-less
    fragment with no marker-bearing fragment before it (a leading clause, or the whole cell) is
    still discarded, never merged forward: :func:`derive_equipment_from_loadout` only wants rows
    that describe a default loadout, not scene-setting prose that happens to precede one.
    """
    tokens = _SENTENCE_BREAK.split(text)
    parts = tokens[0::2]
    separators = tokens[1::2]
    sentences: list[str] = []
    buffer: str | None = None
    buffer_has_marker = False
    for index, raw_part in enumerate(parts):
        part = raw_part.strip()
        if not part:
            continue
        has_marker = bool(_EQUIPMENT_MARKER.search(part))
        if buffer is None:
            buffer, buffer_has_marker = part, has_marker
            continue
        if has_marker:
            if buffer_has_marker:
                sentences.append(buffer)
            buffer, buffer_has_marker = part, True
        elif buffer_has_marker:
            separator = separators[index - 1] if index - 1 < len(separators) else " "
            if _BR_TAG.match(separator):
                separator = " "
            buffer = f"{buffer}{separator}{part}"
        else:
            buffer, buffer_has_marker = part, False
    if buffer is not None and buffer_has_marker:
        sentences.append(buffer)
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
