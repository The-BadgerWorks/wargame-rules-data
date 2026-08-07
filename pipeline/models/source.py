# AI-Assisted: Claude Code (model: claude-opus-5) - Defined the source-side records of
# data-model.md §1 (task T020): SourceAcquisition plus the MfmUnitCostBlock /
# MfmDetachmentCard / WahapediaRow family, with every prose-bearing field explicitly annotated
# as ephemeral.
"""Source-side records — **ephemeral, never committed**.

These are the only records in the pipeline that may hold publisher prose. They live in memory
and in ``work/`` for the duration of one run and are deleted at the end of it (FR-010), and
their prose fields may be read by exactly one stage — ``normalize`` — which strips them
(FR-013, research D8).

Every prose-bearing field is listed in :data:`PROSE_BEARING_FIELDS`, so "which fields must
never be copied downstream" is a fact this module states rather than a fact a reviewer has to
reconstruct.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from enum import StrEnum
from typing import Final

from pydantic import BaseModel, ConfigDict, Field


class SourceKey(StrEnum):
    """The two upstream sources, with split authority (FR-001, FR-002 as amended)."""

    MFM = "mfm"
    """The points source: unit points, detachment point costs, enhancement and wargear costs."""

    WAHAPEDIA = "wahapedia"
    """The datasheet-detail source: characteristics, weapons, keywords, structure."""


class AcquisitionOutcome(StrEnum):
    """How one retrieval ended. Anything but :attr:`OK` fails the run (FR-007, FR-008)."""

    OK = "ok"
    REFUSED = "refused"
    THROTTLED = "throttled"
    STRUCTURE_CHANGED = "structure_changed"
    UNREACHABLE = "unreachable"


class _SourceRecord(BaseModel):
    """Base for source-side records: frozen, and unknown fields are an error."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class SourceAcquisition(_SourceRecord):
    """One retrieval from one upstream source — the provenance root (FR-003).

    Every published value traces back to one of these. ``declared_edition_code`` is
    *configuration, not inference*: a source that starts serving a newer edition is adopted by
    changing a variable, and no published snapshot is altered by that change (FR-005, FR-061).
    """

    acquisition_id: str = Field(description="<source_key>-<utc_timestamp>-<short_digest>")
    source_key: SourceKey
    source_base_url: str = Field(description="from configuration, recorded as resolved")
    declared_edition_code: str = Field(description="wh40k-11e | wh40k-10e — configuration")
    retrieved_at: str = Field(description="ISO-8601 UTC")
    content_fingerprint: str = Field(description="sha256 over the canonicalised acquired set")
    coverage: Mapping[str, int] = Field(
        default_factory=dict, description="{faction_pages: 30, csv_files: 20, …} — feeds FR-009"
    )
    request_count: int = Field(default=0, description="politeness evidence (FR-007)")
    request_interval_ms: int = Field(default=0, description="politeness evidence (FR-007)")
    outcome: AcquisitionOutcome = AcquisitionOutcome.OK


class MfmCostRow(_SourceRecord):
    """One row of a points-source unit cost table."""

    model_count_label: str = Field(description="'5 models' — a band LOWER bound (C2/R5)")
    points: int
    delta_marker: str | None = Field(
        default=None,
        description="'▲ (+15)' — the source's own change marker. A witness for the D4d "
        "cross-check only; excluded from the detection digest and from curated data.",
    )


class MfmUnitCostBlock(_SourceRecord):
    """One unit's cost table, extracted by reference from the replayed DOM (never by order)."""

    faction_slug: str
    unit_display_name: str
    cost_table_label: str = Field(
        description="The observed literal — 'YOUR UNIT COSTS', 'YOUR 1ST TO 2ND UNITS COST', "
        "'YOUR 3RD + UNIT COSTS'. Preserved verbatim because tier detection keys on it (C1)."
    )
    cost_section_label: str = Field(
        default="",
        description="The heading of the section this block sits in — '' for the page's default "
        "section, 'EVERY MODEL HAS THE IMPERIUM KEYWORD' for a conditional re-pricing, "
        "'ULTRAMARINES' for a plain grouping. Preserved verbatim; `curate.assemble` decides "
        "which of the two it is.",
    )
    rows: Sequence[MfmCostRow]
    support_targets: Sequence[str] = Field(
        default=(), description="Leader/Support list entries, by name"
    )


class MfmEnhancementEntry(_SourceRecord):
    """One ``ENHANCEMENTS`` list entry on a detachment card: a name and a cost."""

    name: str
    points: int


class MfmDetachmentCard(_SourceRecord):
    """One detachment card: DP cost, force disposition, tags, and its enhancement list."""

    faction_slug: str
    detachment_name: str
    dp_cost: int
    force_disposition: str | None = Field(
        default=None, description="curated-only; deliberately not given a contract column (C4/R7)"
    )
    tags: Sequence[str] = Field(default=(), description="e.g. 'Unique' — curated-only (C4/R7)")
    enhancements: Sequence[MfmEnhancementEntry] = ()


class WahapediaRow(_SourceRecord):
    """One record from one detail-source CSV, still carrying its publisher fields.

    ``fields`` is the whole record as read. The keys named in
    ``PROSE_BEARING_FIELDS['WahapediaRow']`` carry publisher prose and may be read **only** by
    the ``normalize`` stage's IP strip. ``repaired`` marks a record that needed structural
    repair (the observed unescaped-newline row), which is counted as ``DQ-MALFORMED-ROW``.
    """

    file_name: str
    line_number: int
    fields: Mapping[str, str] = Field(
        description="EPHEMERAL. Structural and numeric fields alongside the prose-bearing "
        "legend / description / loadout / damaged_description / inv_sv_descr columns."
    )
    repaired: bool = Field(
        default=False, description="record needed continuation-line rejoining (DQ-MALFORMED-ROW)"
    )


#: The fields that may hold publisher prose, by record type. Anything listed here is readable
#: **only** inside ``pipeline.normalize`` and must never be copied into a normalized, curated,
#: authored, report, ledger, or state record (FR-013, research D8).
PROSE_BEARING_FIELDS: Final[Mapping[str, frozenset[str]]] = {
    "SourceAcquisition": frozenset(),
    "MfmUnitCostBlock": frozenset(),
    "MfmDetachmentCard": frozenset(),
    "WahapediaRow": frozenset(
        {"legend", "description", "loadout", "damaged_description", "inv_sv_descr"}
    ),
}
