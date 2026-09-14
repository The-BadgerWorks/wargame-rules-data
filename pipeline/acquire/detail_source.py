# AI-Assisted: Claude Code (model: claude-opus-5) - 010 R5 fix round 1: dropped the reader's
# vestigial `edition_code` parameter, accepted and `del`d on entry because the two arms'
# readers had to be callable identically. One reader, no shared signature to honour, and a
# parameter plumbed from config to a `del` invites an edition switch that silently does
# nothing. `read_detail` no longer takes `config` either -- that was the plumbing.
# AI-Assisted: Claude Code (model: claude-opus-5) - 010 R5: deleted the
# WGC_DETAIL_ACQUISITION_MODE dispatch. There is one acquisition arm, so `acquire_detail`
# calls `acquire_wahapedia` and `read_detail` calls `read_export_payloads`, and the mode
# enum, the two protocols, the two lookup tables and their validators are gone with it.
# AI-Assisted: Claude Code (model: claude-opus-5) - 010 R5: deleted `resolve_carried_forward`,
# `CarriedForwardOutcome` and `_fetched_slugs` along with the per-faction carry-forward mechanism
# they served. A bulk export answers whole or not at all, so there is no per-faction page failure
# for a declaration to cover.
# AI-Assisted: Claude Code (model: claude-opus-5) - 010 R5: deleted
# `_derive_equipment_from_composition`. It split a default-equipment sentence out of the
# composition table, a shape 009 T011 measured before 010 R1 found the export states the
# sentence in `Datasheets.csv`'s own `loadout` column. `derive_equipment_from_loadout` reads
# it there, which is the export's own filing rather than a salvage from the wrong table.
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

from collections.abc import Sequence
from datetime import datetime
from pathlib import Path

from pipeline.acquire.export_rows import derive_equipment_from_loadout, drop_non_option_rows
from pipeline.acquire.fixtures import FixturePayload
from pipeline.acquire.http import PoliteClient
from pipeline.acquire.wahapedia import acquire_wahapedia
from pipeline.config import PipelineConfig
from pipeline.models.source import SourceAcquisition
from pipeline.parse.wahapedia_csv import CsvReadResult, read_text


def read_export_payloads(payloads: Sequence[FixturePayload]) -> dict[str, CsvReadResult]:
    """The reader: one acquired export file per payload.

    A payload's name is the file name, with or without its suffix - the live adapter carries
    ``Datasheets.csv`` and the fixture adapter carries the stem - so the suffix is normalised
    here rather than at each call site.

    010 R1: `drop_non_option_rows` runs first, so the options table reaches the grammar carrying
    only rows that are options, and `derive_equipment_from_loadout` builds the
    ``Datasheets_unit_equipment.csv`` the export does not publish (FR-018) from
    `Datasheets.csv`'s `loadout` column, which is where the export actually states it.
    """
    results = {
        (name if (name := payload.name).endswith(".csv") else f"{name}.csv"): read_text(
            name if name.endswith(".csv") else f"{name}.csv", payload.text
        )
        for payload in payloads
    }
    return derive_equipment_from_loadout(drop_non_option_rows(results))


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


def read_detail(payloads: Sequence[FixturePayload]) -> dict[str, CsvReadResult]:
    """Read what :func:`acquire_detail` returned into the export's own table shape.

    Kept as a name of its own rather than folded into :func:`read_export_payloads`: this is the
    acquire-layer boundary every stage below calls, and :func:`read_export_payloads` is how that
    boundary is currently satisfied. A caller naming the boundary cannot be made to care which.
    """
    return read_export_payloads(payloads)
