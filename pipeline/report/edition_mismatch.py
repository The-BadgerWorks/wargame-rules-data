# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the edition-mismatch and
# unverified-pricing sub-reports (task T097), each leading with count AND proportion before any
# enumeration (FR-060, FR-035, SC-013). `scale_line` is shared with
# `pipeline.report.coverage` (task T130), which carries the same rule for `summary-coverage.md`.
"""Two enumerating sub-reports, each of which leads with its scale.

`validation-report.md` §1.3 makes this a rule rather than a style preference: **every category
states a count and a proportion of the snapshot, not merely an enumeration.** At a few thousand
datasheets a bare list is unreadable, and the approver's actual question is not "which entities
are hybrid" but "how much of this release is". A list answers the first; only the proportion
answers the second, and the second is the one the approval decision turns on.

At launch the hybrid proportion is expected to be 100%: the points source is 11th Edition and the
detail export is 10th (research §0.1). That is a fact about the release, stated plainly, rather
than an alarm — which is exactly why the number has to be there. An unlabelled list of 1 487
entities reads like a catastrophe; "100% of the release, as expected until the export catches up"
reads like a decision.
"""

from __future__ import annotations

from pipeline.models.curated import CuratedDatasheet, CuratedSnapshot
from pipeline.models.provenance import PricingConfidenceState


def _proportion(count: int, total: int) -> str:
    return f"{(count / total * 100) if total else 0.0:.1f}%"


def hybrid_datasheets(snapshot: CuratedSnapshot) -> list[CuratedDatasheet]:
    """Datasheets whose detail came from an older edition than their points (FR-058)."""
    return [
        datasheet
        for datasheet in sorted(snapshot.datasheets, key=lambda d: d.datasheet_id)
        if datasheet.provenance.is_hybrid_edition
    ]


def unverified_datasheets(snapshot: CuratedSnapshot) -> list[CuratedDatasheet]:
    """Datasheets shipping on last-known pricing (FR-035)."""
    return [
        datasheet
        for datasheet in sorted(snapshot.datasheets, key=lambda d: d.datasheet_id)
        if datasheet.pricing_confidence.state is PricingConfidenceState.UNVERIFIED
    ]


def scale_line(label: str, count: int, total: int) -> list[str]:
    """A leading count-and-proportion line, per `validation-report.md` §1.3.

    Public (not `_scale_line`) because :mod:`pipeline.report.coverage` reuses it for
    `summary-coverage.md`, which carries the identical rule (FR-025).
    """
    return [
        f"**{count}** of {total} {label} — **{_proportion(count, total)}** of the release.",
        "",
    ]


def render_edition_mismatch(snapshot: CuratedSnapshot) -> str:
    """`edition-mismatch.md` (FR-060)."""
    hybrids = hybrid_datasheets(snapshot)
    total = len(snapshot.datasheets)

    out = ["# Edition mismatch", "", *scale_line("datasheets are hybrid", len(hybrids), total)]
    if not hybrids:
        out.append("Both sources declare the same edition; no entity is hybrid.")
        return "\n".join(out).rstrip() + "\n"

    out += ["| datasheet | faction | points edition | detail edition |", "|---|---|---|---|"]
    out += [
        f"| `{d.datasheet_id}` | `{d.faction_id}` | "
        f"{d.provenance.points_edition_code} | {d.provenance.detail_edition_code} |"
        for d in hybrids
    ]
    return "\n".join(out).rstrip() + "\n"


def render_unverified_pricing(snapshot: CuratedSnapshot) -> str:
    """`unverified-pricing.md` (FR-035, SC-013)."""
    unverified = unverified_datasheets(snapshot)
    total = len(snapshot.datasheets)

    out = [
        "# Unverified pricing",
        "",
        *scale_line("datasheets ship on last-known pricing", len(unverified), total),
    ]
    if not unverified:
        out.append("Every published price was confirmed by the points source this release.")
        return "\n".join(out).rstrip() + "\n"

    out += [
        "| datasheet | faction | unverified since | consecutive releases | last verified |",
        "|---|---|---|---|---|",
    ]
    for datasheet in unverified:
        confidence = datasheet.pricing_confidence
        out.append(
            f"| `{datasheet.datasheet_id}` | `{datasheet.faction_id}` | "
            f"{confidence.unverified_since_version or '-'} | "
            f"{confidence.consecutive_unverified_releases} | "
            f"{confidence.last_verified_version or '-'} |"
        )
    return "\n".join(out).rstrip() + "\n"
