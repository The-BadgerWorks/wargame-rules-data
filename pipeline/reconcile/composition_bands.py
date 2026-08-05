# AI-Assisted: Claude Code (model: claude-opus-5) - Reconciled resolved composition against the
# points source's model-count bands (004 task T029, FR-009): both values reported, the points
# bands left authoritative for pricing, and neither side adjusted to agree with the other.
"""Do the points source's size bands fit the composition we resolved?

The free-text version of this check already exists in :mod:`pipeline.reconcile.bands`, which
reads counts straight out of the description because, before `004`, that was the only form the
composition had. This module is the same question asked of the **structured** entries, and it
exists separately for one reason: a datasheet must be reconciled **once**. Raising both a
free-text mismatch and a structured mismatch for one band would double-count a single defect
across two categories, and the approver reads those counts as "how much of this release is
wrong".

So ``curate/assemble.py`` calls this one where composition resolved, and the free-text one where
it did not — which is also where the free-text module's ``REC-COMPOSITION-UNPARSED`` is still
the right thing to say.

**Neither side is adjusted** (FR-009). The points bands remain authoritative for pricing and the
composition remains what the detail source describes; the finding names both values and a human
decides which is wrong. Silently clamping a band into the composition's range would produce a
snapshot in which every value is internally consistent and one of them is a lie.
"""

from __future__ import annotations

from collections.abc import Sequence

from pipeline.models.curated import CuratedCompositionEntry
from pipeline.models.findings import Finding
from pipeline.report.catalogue import build_finding


def representable_range(entries: Sequence[CuratedCompositionEntry]) -> tuple[int, int]:
    """The model counts the unit can legally be fielded at, summed across its model lines.

    Summed rather than taken line by line because a composition names the unit's *parts*: a
    one-model leader plus a three-to-six-model body is fieldable at four to seven models, and it
    is that total the points source prices.
    """
    return (
        sum(entry.min_count for entry in entries),
        sum(entry.max_count for entry in entries),
    )


def reconcile_composition_bands(
    *,
    datasheet_id: str,
    entries: Sequence[CuratedCompositionEntry],
    model_counts: Sequence[int],
) -> list[Finding]:
    """Report every points band the resolved composition cannot represent. Advisory (FR-009)."""
    if not entries:
        return []

    minimum, maximum = representable_range(entries)
    return [
        build_finding(
            "REC-BAND-MISMATCH",
            entity_refs=[datasheet_id],
            detail={
                "datasheet_id": datasheet_id,
                "model_count": model_count,
                "composition_min": minimum,
                "composition_max": maximum,
                "composition_lines": len(entries),
            },
        )
        for model_count in sorted(set(model_counts))
        if not minimum <= model_count <= maximum
    ]
