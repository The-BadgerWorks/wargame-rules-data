# AI-Assisted: Claude Code (model: claude-sonnet-5) - Implemented `summary-coverage.md` (task
# T130): rendered on every run, not only a blocked one, so the editorial backlog is visible long
# before it blocks a release (FR-025).
"""`summary-coverage.md` — the standing editorial backlog, rendered on every run.

Moved out of :mod:`pipeline.report.edition_mismatch` (where it first landed under T097, ahead
of US5) once :mod:`pipeline.curate.summaries` existed to answer the real question: not "does
`curation/` say `approved`" but "is it still approved *against the mechanic as it stands right
now*". The earlier version read `snapshot.ability_summaries` directly, which is also wrong for a
bare `rules-pipeline validate` re-run — a snapshot reconstructed from `data/` alone never carries
authored content, because authored content is never written to the curated tree (FR-017). This
version takes the freshly loaded authored content as its own argument instead.
"""

from __future__ import annotations

from collections.abc import Mapping

from pipeline.curate.summaries import SummaryStatus, summary_statuses
from pipeline.models.authored import AbilitySummary
from pipeline.models.curated import CuratedSnapshot
from pipeline.report.edition_mismatch import scale_line
from pipeline.validate.summaries import used_ability_keys


def render_summary_coverage(
    snapshot: CuratedSnapshot,
    *,
    authored_summaries: Mapping[str, AbilitySummary],
    current_digests: Mapping[str, str] | None = None,
) -> str:
    """`summary-coverage.md`: per faction, approved over total, and the named gaps (FR-025).

    "Approved" here means :attr:`~pipeline.curate.summaries.SummaryStatus.APPROVED` — current
    against this run's freshly computed digest where one is available, not merely stored as
    `approved` in `curation/`. A key flipped to `needs_rereview` by a moved digest counts as
    outstanding here exactly as it does for the blocking `SUM-NEEDS-REREVIEW` check, so the
    coverage figure and the publication gate can never disagree about one key's status.
    """
    per_faction: dict[str, set[str]] = {}
    for datasheet in snapshot.datasheets:
        per_faction.setdefault(datasheet.faction_id, set()).update(datasheet.ability_keys)

    statuses = summary_statuses(
        used_ability_keys(snapshot),
        authored=authored_summaries,
        current_digests=current_digests,
    )
    approved = {key for key, status in statuses.items() if status is SummaryStatus.APPROVED}

    total_keys = {key for keys in per_faction.values() for key in keys}
    out = [
        "# Summary coverage",
        "",
        *scale_line(
            "ability keys carry an approved summary", len(total_keys & approved), len(total_keys)
        ),
        "| faction | approved / total | outstanding |",
        "|---|---|---|",
    ]
    for faction_id in sorted(per_faction):
        keys = per_faction[faction_id]
        outstanding = sorted(keys - approved)
        out.append(
            f"| `{faction_id}` | {len(keys & approved)} / {len(keys)} | "
            f"{', '.join(f'`{key}`' for key in outstanding) if outstanding else '—'} |"
        )
    return "\n".join(out).rstrip() + "\n"
