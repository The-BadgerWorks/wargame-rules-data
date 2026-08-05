# AI-Assisted: Claude Code (model: claude-sonnet-5) - Implemented `summary-coverage.md` (task
# T130): rendered on every run, not only a blocked one, so the editorial backlog is visible long
# before it blocks a release (FR-025).
# AI-Assisted: Claude Code (model: claude-opus-5) - Generalised it to a per-class table (004 task
# T049): one row per authored summary class with its gate state, above the per-faction ability
# breakdown that already existed. The gate column is the point — a class's backlog means a
# different thing depending on whether anything is blocking on it yet.
# AI-Assisted: Claude Code (model: claude-opus-5) - Enumerated the glossary's digest-less
# subset (004 task T061), the list contract §7 item 4 requires a reviewer to sweep by hand
# before WGC_GATE_GLOSSARY is ever switched on.
"""`summary-coverage.md` — the standing editorial backlog, rendered on every run.

Moved out of :mod:`pipeline.report.edition_mismatch` (where it first landed under T097, ahead
of US5) once :mod:`pipeline.curate.summaries` existed to answer the real question: not "does
`curation/` say `approved`" but "is it still approved *against the mechanic as it stands right
now*". The earlier version read `snapshot.ability_summaries` directly, which is also wrong for a
bare `rules-pipeline validate` re-run — a snapshot reconstructed from `data/` alone never carries
authored content, because authored content is never written to the curated tree (FR-017). This
version takes the freshly loaded authored content as its own argument instead.

`004-rules-data-enrichment` adds three more classes and the per-class table above. Two things
that table has to say, because a bare percentage says neither:

* **the gate state**, since an outstanding entry in a gated-off class is planned work while the
  same entry in a gated-on class is a refused release; and
* **the denominator**, since `faction_rules`'s is three-valued — a faction with a curated "no
  army rule" contributes nothing, while a faction nobody has curated counts as outstanding
  (contract §4.1).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from pipeline.config import Gate
from pipeline.curate.summaries import AuthoredSummary, SummaryStatus, summary_statuses
from pipeline.models.authored import SummaryClass
from pipeline.models.curated import CuratedSnapshot
from pipeline.report.edition_mismatch import scale_line
from pipeline.validate.gates import ClassCheck, ClassCoverage, class_coverage, used_ability_keys

#: How many outstanding entries a class's row names before it stops enumerating. The point of
#: this table is the *scale* of the backlog; a 336-entry list belongs to the finding set, which
#: names every one of them, not to a report meant to be read at a glance.
NAMED_OUTSTANDING_LIMIT = 8


def _class_rows(coverages: Sequence[ClassCoverage]) -> list[str]:
    rows = [
        "| class | gate | approved / total | outstanding |",
        "|---|---|---|---|",
    ]
    for coverage in sorted(coverages, key=lambda c: c.summary_class.value):
        named = ", ".join(f"`{key}`" for key in coverage.outstanding[:NAMED_OUTSTANDING_LIMIT])
        remainder = len(coverage.outstanding) - NAMED_OUTSTANDING_LIMIT
        if remainder > 0:
            named += f", and {remainder} more"
        rows.append(
            f"| `{coverage.summary_class.value}` | {coverage.gate.value} | "
            f"{coverage.approved} / {coverage.total} | {named or '—'} |"
        )
    return rows


def _digestless_rows(keyword_keys: Sequence[str]) -> list[str]:
    """The §5.1 subset, enumerated so a reviewer can sweep it (contract §7 item 4).

    This section exists because of a limitation that is **recorded rather than engineered
    around**: no keyword glossary source exists, so where the edition publishes no description
    for a keyword its digest is taken over the normalised keyword stem — which is stable by
    construction, so such an entry can never auto-flag for re-review. Naming the subset here is
    what turns "these entries are never re-checked automatically" from a silent property into a
    reviewable list, and contract §7 requires that sweep before `WGC_GATE_GLOSSARY` is switched
    on for the first time.
    """
    out = [
        "## Glossary entries with no upstream digest",
        "",
        "The source publishes no description for these keywords, so their digest is over the "
        "**normalised keyword stem** and they will **never auto-flag for re-review** "
        "(`contracts/authored-summary-gates.md` §5.1). Sweep this list by hand before the "
        "glossary gate is switched on.",
        "",
    ]
    if not keyword_keys:
        out.append("None.")
        return out
    out.extend(f"- `{key}`" for key in keyword_keys)
    return out


def render_summary_coverage(
    snapshot: CuratedSnapshot,
    *,
    authored_summaries: Mapping[str, AuthoredSummary],
    current_digests: Mapping[str, str] | None = None,
    class_coverages: Sequence[ClassCoverage] = (),
    digestless_keywords: Sequence[str] = (),
) -> str:
    """`summary-coverage.md`: per class, then per faction, and the named gaps (FR-025, FR-028).

    "Approved" here means :attr:`~pipeline.curate.summaries.SummaryStatus.APPROVED` — current
    against this run's freshly computed digest where one is available, not merely stored as
    `approved` in `curation/`. A key flipped to `needs_rereview` by a moved digest counts as
    outstanding here exactly as it does for the blocking `SUM-NEEDS-REREVIEW` check, so the
    coverage figure and the publication gate can never disagree about one key's status.

    Args:
        class_coverages: every wired class, including `abilities`. Defaults to deriving the
            abilities row alone, so a caller that has not yet wired the newer classes still gets
            a table rather than an empty one.
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

    coverages = list(class_coverages) or [
        class_coverage(
            ClassCheck(
                summary_class=SummaryClass.ABILITIES,
                keys=sorted(used_ability_keys(snapshot)),
                authored=authored_summaries,
                current_digests=current_digests,
                gate=Gate.ON,
            )
        )
    ]

    total_keys = {key for keys in per_faction.values() for key in keys}
    out = [
        "# Summary coverage",
        "",
        *scale_line(
            "ability keys carry an approved summary", len(total_keys & approved), len(total_keys)
        ),
        *_class_rows(coverages),
        "",
        *_digestless_rows(digestless_keywords),
        "",
        "## Abilities, per faction",
        "",
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
