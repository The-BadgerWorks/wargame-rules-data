# AI-Assisted: Claude Code (model: claude-sonnet-5) - 010 round 1: csv-arm row routing at the reader
# boundary. Ports the two non-option row shapes wahapedia_html_dom._options drops, and derives
# the default-equipment table from the Datasheets export's loadout column. Row routing only:
# no grammar production, no normalization, no mode branch.
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
#: Sentence boundaries inside one ``loadout`` cell: a line-break tag, or a full stop followed by
#: whitespace. Item lists end in a full stop, so a stop at end-of-text closes the last sentence.
_SENTENCE_BREAK: Final = re.compile(r"(?:<br\s*/?>|(?<=\.)\s+)", re.IGNORECASE)


def split_equipment_sentences(text: str) -> tuple[str, ...]:
    """Every sentence of ``text`` that states a default loadout, in text order."""
    parts = (part.strip() for part in _SENTENCE_BREAK.split(text))
    return tuple(part for part in parts if part and _EQUIPMENT_MARKER.search(part))


def derive_equipment_from_loadout(detail: dict[str, CsvReadResult]) -> dict[str, CsvReadResult]:
    """csv-mode's source for ``Datasheets_unit_equipment.csv`` (010 R1, spec §4.2).

    The export publishes no equipment table; it states each datasheet's default loadout in
    ``Datasheets.csv``'s ``loadout`` column, one prose cell per datasheet, sometimes holding more
    than one sentence. Each sentence becomes one row in the same ``datasheet_id|line|description``
    shape the html arm manufactured, numbered from 1 in text order, so ``curate/assemble.py`` and
    the equipment grammar are unchanged. The text is carried as-is: it is a prose-bearing field
    and the grammar's own ``pre_pass`` is the only reader that may look inside it.
    """
    datasheets = detail.get(DATASHEETS_TABLE)
    if datasheets is None:
        return detail
    derived: list[WahapediaRow] = []
    for row in datasheets.rows:
        datasheet_id = row.fields.get("id", "")
        if not datasheet_id:
            continue
        for line, sentence in enumerate(
            split_equipment_sentences(row.fields.get("loadout", "")), start=1
        ):
            derived.append(
                WahapediaRow(
                    file_name=EQUIPMENT_TABLE,
                    line_number=row.line_number,
                    fields={
                        "datasheet_id": datasheet_id,
                        "line": str(line),
                        "description": sentence,
                    },
                    repaired=row.repaired,
                )
            )
    if not derived:
        return detail
    existing = detail.get(EQUIPMENT_TABLE)
    updated = dict(detail)
    updated[EQUIPMENT_TABLE] = CsvReadResult(
        file_name=EQUIPMENT_TABLE,
        field_names=("datasheet_id", "line", "description"),
        rows=(existing.rows if existing else ()) + tuple(derived),
        repairs=existing.repairs if existing else 0,
        findings=existing.findings if existing else (),
    )
    return updated
