# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the points source's own delta
# markers as a cross-check on our computed change summary (task T098): parsed into the report,
# compared, and divergence raised as the advisory CHG-DELTA-DISAGREEMENT. The markers are a
# witness, never an authority (research D4d, FR-032).
"""The source's own ▲/▼ markers, used as a witness.

The points source annotates a changed price with its own delta — ``▲ (+15)`` — and comparing that
against what we computed costs almost nothing and gives FR-032 an *independent* witness, which no
other part of this design has. Agreement is reassurance. Disagreement points at exactly one of
two things: a parse error on our side, or an inconsistency on the publisher's.

**The markers are never an authority** (research D4d). They persist across a release cycle and
are cleared unannounced, so "no marker" does not mean "no change" and a marker's value is not a
price. That is why divergence is advisory and why nothing here ever writes a value: the marker
gets a finding, and the computed change summary keeps the number.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from pipeline.models.findings import Finding
from pipeline.normalize.numerics import NumericParseError, model_count
from pipeline.parse.mfm_dom import MfmPage
from pipeline.report.catalogue import build_finding
from pipeline.report.change_summary import ChangeSummary


@dataclass(frozen=True, slots=True)
class SourceDelta:
    """One ``▲/▼ (±n)`` the points source published, keyed to the row it annotated."""

    faction_slug: str
    unit_display_name: str
    model_count: int
    stated_delta: int


def collect_source_deltas(pages: Sequence[MfmPage]) -> list[SourceDelta]:
    """Every delta marker on every page, in a stable order.

    A row whose label is not a model count is skipped rather than reported: a wargear row's
    marker annotates an option's price, which the change summary accounts for elsewhere.
    """
    deltas: list[SourceDelta] = []
    for page in sorted(pages, key=lambda p: p.faction_slug):
        for block in page.unit_blocks:
            for row in block.rows:
                if row.delta_marker is None:
                    continue
                try:
                    count = model_count(row.model_count_label, field="cost.model_count")
                except NumericParseError:
                    continue
                deltas.append(
                    SourceDelta(
                        faction_slug=page.faction_slug,
                        unit_display_name=block.unit_display_name,
                        model_count=count,
                        stated_delta=int(row.delta_marker),
                    )
                )
    return sorted(deltas, key=lambda d: (d.faction_slug, d.unit_display_name, d.model_count))


def crosscheck_deltas(
    pages: Sequence[MfmPage],
    summary: ChangeSummary,
    *,
    datasheet_ids: Mapping[tuple[str, str], str],
) -> list[Finding]:
    """Compare each stated delta with the move the change summary computed.

    Args:
        datasheet_ids: ``(faction_slug, points-source display name) -> curated datasheet_id``,
            supplied by the reconcile stage rather than re-derived here — a second derivation is
            a second chance to disagree with the first.
    """
    computed = {
        (datasheet_id, model_count_value): now - was
        for datasheet_id, copy_index, model_count_value, was, now in summary.datasheet_cost_changes
        if copy_index == 1 and was >= 0 and now >= 0
    }

    findings: list[Finding] = []
    for delta in collect_source_deltas(pages):
        datasheet_id = datasheet_ids.get((delta.faction_slug, delta.unit_display_name))
        if datasheet_id is None:
            continue
        ours = computed.get((datasheet_id, delta.model_count), 0)
        if ours == delta.stated_delta:
            continue
        findings.append(
            build_finding(
                "CHG-DELTA-DISAGREEMENT",
                entity_refs=[datasheet_id],
                detail={
                    "datasheet_id": datasheet_id,
                    "model_count": delta.model_count,
                    "source_stated_delta": delta.stated_delta,
                    "computed_delta": ours,
                },
            )
        )
    return findings
