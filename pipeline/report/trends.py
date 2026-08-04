# AI-Assisted: Claude Code (model: claude-sonnet-5) - Implemented the unverified/hybrid-count
# trend sub-report (task T149): reads `state/run-ledger.jsonl` (pipeline.observability.ledger),
# extracts the per-published-version series over time, and renders it as `trends.md`, wired in as
# one more sub-report alongside change-summary/edition-mismatch/unverified-pricing/summary-
# coverage (spec.md's Monitoring and logging concern).
"""`trends.md` — the unverified- and hybrid-count trend across published versions.

A rising unverified-pricing count is the early signal that the points source is drifting from
the edition currently in play: each consecutive release that ships on last-known pricing is one
more release the curator has not been able to confirm against a live source. A rising hybrid
count is the equivalent signal for the detail source. Neither number moving is an emergency by
itself — at launch the hybrid proportion is expected to be 100% (`pipeline.report.edition_
mismatch`'s own docstring) — but a number that keeps climbing release over release, rather than
holding steady, is exactly the drift this report exists to make visible before it is a surprise.

The series is read straight from :func:`pipeline.observability.ledger.read_entries`: every
ledger entry that carries a `rules_version_id` is one published-version data point, kept in the
ledger's own append order (chronological, per that module's docstring) rather than re-sorted by
this one. An entry with no `rules_version_id` — a `detect` sweep that found nothing to build, for
instance — has no version to plot against and does not participate.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class TrendPoint:
    """One published version's ledger entry, reduced to what the trend needs."""

    rules_version_id: str
    started_at: str
    unverified_count: int
    hybrid_count: int


def build_trend_series(entries: Sequence[Mapping[str, Any]]) -> list[TrendPoint]:
    """Extract the per-published-version series, in ledger (chronological) order.

    Only entries that carry a `rules_version_id` participate — that is what "per-published-
    version" means here.
    """
    points: list[TrendPoint] = []
    for entry in entries:
        rules_version_id = entry.get("rules_version_id")
        if not rules_version_id:
            continue
        points.append(
            TrendPoint(
                rules_version_id=str(rules_version_id),
                started_at=str(entry.get("started_at", "")),
                unverified_count=int(entry.get("unverified_count") or 0),
                hybrid_count=int(entry.get("hybrid_count") or 0),
            )
        )
    return points


def _is_rising(values: Sequence[int]) -> bool:
    """True if there is more than one point and the series moved up overall.

    Not strict monotonicity: the concern here is drift across releases, not noise between two
    adjacent points, so "the last point is higher than the first" is the right question.
    """
    return len(values) >= 2 and values[-1] > values[0]


def _trend_line(label: str, values: Sequence[int], *, point_count: int) -> str:
    if _is_rising(values):
        return (
            f"**Rising {label} trend**: {values[0]} -> {values[-1]} across {point_count} "
            "published version(s). This is the early signal that a source is drifting from "
            "the edition in play."
        )
    return f"{label[0].upper()}{label[1:]} count is not rising."


def render_trends(entries: Sequence[Mapping[str, Any]]) -> str:
    """`trends.md`: the unverified- and hybrid-count series across published versions.

    Renders something sane even for an empty ledger or a single published version — a quiet
    ledger is not a crash, and a first release has no trend yet, only a starting point.
    """
    points = build_trend_series(entries)
    out: list[str] = ["# Trends", ""]

    if not points:
        out += ["No published-version ledger entries yet; nothing to trend.", ""]
        return "\n".join(out).rstrip() + "\n"

    out += [
        "| rules version | started at | unverified count | hybrid count |",
        "|---|---|---|---|",
    ]
    out += [
        f"| `{p.rules_version_id}` | {p.started_at} | {p.unverified_count} | {p.hybrid_count} |"
        for p in points
    ]
    out.append("")

    unverified_values = [p.unverified_count for p in points]
    hybrid_values = [p.hybrid_count for p in points]

    out.append(_trend_line("unverified-pricing", unverified_values, point_count=len(points)))
    out.append("")
    out.append(_trend_line("hybrid-edition", hybrid_values, point_count=len(points)))
    out.append("")

    return "\n".join(out).rstrip() + "\n"
