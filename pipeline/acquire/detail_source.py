# AI-Assisted: Claude Code (model: claude-opus-5) - 010 R5: deleted the
# WGC_DETAIL_ACQUISITION_MODE dispatch. There is one acquisition arm, so `acquire_detail`
# calls `acquire_wahapedia` and `read_detail` calls `read_export_payloads`, and the mode
# enum, the two protocols, the two lookup tables and their validators are gone with it.
# AI-Assisted: Claude Code (model: claude-opus-5) - 010 R5: deleted `resolve_carried_forward`,
# `CarriedForwardOutcome` and `_fetched_slugs` along with the per-faction carry-forward mechanism
# they served. A bulk export answers whole or not at all, so there is no per-faction page failure
# for a declaration to cover.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 010 R1: `read_export_payloads` now also runs
# `derive_equipment_from_loadout` (from `export_rows.py`) as the last step, so the csv arm's
# default-equipment table also picks up rows manufactured from `Datasheets.csv`'s `loadout`
# column, alongside what `_derive_equipment_from_composition` already split from composition.
# AI-Assisted: Claude Code (model: claude-opus-5) - 010 R5: deleted the hybrid per-class
# acquisition-arm overlay (`apply_detail_source_authority` and `_CLASS_TABLES`). It was never
# instantiated -- no `curation/detail-source-authority.json` ever existed -- and with a single
# arm there is no second arm for a class to be declared onto.
"""How the datasheet-detail source is acquired and read - and nothing else.

There is one arm: the bulk export on the permitted path. :func:`acquire_detail` fetches it and
:func:`read_detail` turns what it returned into the export's own table shape. Everything below
``acquire`` receives that shape and asks nothing about where it came from.

Two arms once lived here behind ``WGC_DETAIL_ACQUISITION_MODE``, and the rule that kept them
honest - no ``if mode is ...`` anywhere below ``acquire`` - is why their removal touches this
module and almost nothing else. Row routing that the export's own shape requires lives in
:mod:`pipeline.acquire.export_rows` and in this module's reader, never in a grammar.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import replace as _replace_csv_read_result
from datetime import datetime
from pathlib import Path
from typing import Final

from pipeline.acquire.export_rows import derive_equipment_from_loadout, drop_non_option_rows
from pipeline.acquire.fixtures import FixturePayload
from pipeline.acquire.http import PoliteClient
from pipeline.acquire.wahapedia import acquire_wahapedia
from pipeline.config import PipelineConfig
from pipeline.models.source import SourceAcquisition, WahapediaRow
from pipeline.parse.equipment_grammar import EQUIPMENT_TABLE
from pipeline.parse.wahapedia_csv import CsvReadResult, read_text

#: `Datasheets_unit_composition.csv`'s export name -- the table
#: :func:`_derive_equipment_from_composition` reads FROM.
_COMPOSITION_TABLE: Final = "Datasheets_unit_composition.csv"

#: The default-equipment marker (009 T057/T058, FR-017, plan.md finding 9). The SAME sentence
#: `parse/equipment_grammar.py::_MARKER` already matches, kept as its OWN copy here rather
#: than importing that private symbol. This is
#: acquire-layer row-routing (which table a row belongs in), never a grammar concern, and
#: `parse/equipment_grammar.py` is not edited by this feature (rule 5).
_EQUIPMENT_MARKER: Final = re.compile(r"\b(?:is|are)\s+equipped\s+with\s*:", re.IGNORECASE)


def _derive_equipment_from_composition(
    detail: dict[str, CsvReadResult],
) -> dict[str, CsvReadResult]:
    """The composition-filed default-equipment sentence, moved to its own table (009 T057/T058).

    The bulk export publishes no ``Datasheets_unit_equipment.csv`` at all (FR-018). It files the
    default-equipment sentence as an ordinary row of ``Datasheets_unit_composition.csv``
    (``plan.md`` finding 9's ``GF05|1``/``CM03|2`` shape).

    Left there, it does double harm: ``composition_grammar.parse_entry`` cannot resolve it
    (correctly — it is not a composition sentence), which sets ``_composition_entries``'s
    ``unresolved`` flag and suppresses the WHOLE datasheet's composition (FR-008's "all or
    none"); and because ``curate/assemble.py::_equipment`` refuses to attach equipment to a
    datasheet whose composition did not resolve, the datasheet's equipment is poisoned too — not
    merely absent, destructive. Splitting the row out here, before it ever reaches
    ``composition_grammar``, fixes both at once: composition no longer sees a row it cannot
    parse, and the equipment table gains the sentence in the
    ``datasheet_id|line|description`` shape ``curate/assemble.py`` reads.
    """
    composition = detail.get(_COMPOSITION_TABLE)
    if composition is None:
        return detail

    kept: list[WahapediaRow] = []
    derived: list[WahapediaRow] = []
    for row in composition.rows:
        if _EQUIPMENT_MARKER.search(row.fields.get("description", "")):
            derived.append(row.model_copy(update={"file_name": EQUIPMENT_TABLE}))
        else:
            kept.append(row)

    if not derived:
        return detail

    updated = dict(detail)
    updated[_COMPOSITION_TABLE] = _replace_csv_read_result(composition, rows=tuple(kept))
    existing_equipment = detail.get(EQUIPMENT_TABLE)
    updated[EQUIPMENT_TABLE] = CsvReadResult(
        file_name=EQUIPMENT_TABLE,
        field_names=("datasheet_id", "line", "description"),
        rows=(existing_equipment.rows if existing_equipment else ()) + tuple(derived),
        repairs=existing_equipment.repairs if existing_equipment else 0,
        findings=existing_equipment.findings if existing_equipment else (),
    )
    return updated


def read_export_payloads(
    payloads: Sequence[FixturePayload], *, edition_code: str = ""
) -> dict[str, CsvReadResult]:
    """The reader: one acquired export file per payload.

    A payload's name is the file name, with or without its suffix - the live adapter carries
    ``Datasheets.csv`` and the fixture adapter carries the stem - so the suffix is normalised
    here rather than at each call site. ``edition_code`` is accepted and unused; it is part of
    the reader's signature and is deleted on entry.

    009 T057/T058 (FR-017): the raw per-file read is followed by
    :func:`_derive_equipment_from_composition`, which moves any default-equipment sentence out of
    ``Datasheets_unit_composition.csv`` and into a derived ``Datasheets_unit_equipment.csv``.

    010 R1: `drop_non_option_rows` runs first, so the options table reaches the grammar carrying
    only rows that are options, and `derive_equipment_from_loadout` runs last, so a
    default-equipment table built from `Datasheets.csv`'s `loadout` column joins whatever
    `_derive_equipment_from_composition` already split out of the composition table.
    """
    del edition_code
    results = {
        (name if (name := payload.name).endswith(".csv") else f"{name}.csv"): read_text(
            name if name.endswith(".csv") else f"{name}.csv", payload.text
        )
        for payload in payloads
    }
    return derive_equipment_from_loadout(
        _derive_equipment_from_composition(drop_non_option_rows(results))
    )


def acquire_detail(
    config: PipelineConfig,
    *,
    fixtures_dir: Path | None = None,
    offline: bool = False,
    client: PoliteClient | None = None,
    retrieved_at: datetime | None = None,
    workspace: Path | None = None,
    state_path: Path | None = None,
) -> tuple[SourceAcquisition, list[FixturePayload]]:
    """Acquire the datasheet-detail source.

    Every caller below ``acquire`` takes what this returns and never asks how it was obtained.

    ``state_path`` (009 rung R05, T090) is forwarded unchanged - see
    :func:`pipeline.acquire.wahapedia.acquire_wahapedia`'s own docstring for the export-timestamp
    short-circuit it switches on. ``None`` (this function's default, and every call `run_build`
    makes) is a no-op.
    """
    return acquire_wahapedia(
        config,
        fixtures_dir=fixtures_dir,
        offline=offline,
        client=client,
        retrieved_at=retrieved_at,
        workspace=workspace,
        state_path=state_path,
    )


def read_detail(
    config: PipelineConfig, payloads: Sequence[FixturePayload]
) -> dict[str, CsvReadResult]:
    """Read what :func:`acquire_detail` returned into the export's own table shape."""
    return read_export_payloads(payloads, edition_code=config.detail_edition)
