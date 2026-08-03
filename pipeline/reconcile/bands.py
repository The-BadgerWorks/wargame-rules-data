# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented model-count band reconciliation
# (task T092): leading integers and n-m ranges extracted from composition free text, each points
# band checked against the representable sizes, and the two separately counted advisory classes
# of FR-027 kept separate (research D5).
"""Do the points source's size bands fit the unit the detail source describes?

The two sources say it differently on purpose. The points source publishes bands — ``5 models``,
``10 models`` — and the detail source publishes composition as free text — ``1 Warboss``,
``3-6 Nobz``. Neither is wrong; they answer different questions. Reconciling them catches the
case where a band prices a squad size the unit cannot legally be, which is a mispriced army list
that validates cleanly.

**The two failure classes stay separate** (FR-027). "The composition could not be read at all"
and "the composition was read and this band does not fit inside it" have different causes and
different fixes, and one number covering both tells an approver neither. An unparseable
composition therefore yields exactly one finding and **no** band mismatches — a band cannot be
mismatched against a range that was never established, and reporting it as though it were would
double-count one defect into two categories.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum

from pipeline.models.findings import Finding
from pipeline.normalize.numerics import leading_count
from pipeline.report.catalogue import build_finding


class BandClass(StrEnum):
    """How well the composition text pinned the unit's representable sizes."""

    EXACT = "exact"
    """Every line gave a single count: the unit has one legal size."""

    RANGE = "range"
    """At least one line gave a range: the unit has a span of legal sizes."""

    UNPARSED = "unparsed"
    """No line opened with a number. Advisory, never a failure (FR-027)."""


@dataclass(frozen=True, slots=True)
class CompositionRange:
    """The model counts a unit can legally be fielded at, as the composition describes them."""

    minimum: int | None
    maximum: int | None
    classification: BandClass

    def contains(self, model_count: int) -> bool:
        if self.minimum is None or self.maximum is None:
            return True
        return self.minimum <= model_count <= self.maximum


def parse_composition(lines: Sequence[str]) -> CompositionRange:
    """Sum the composition's per-line counts into one representable size range.

    Summed rather than taken line by line because a composition names the unit's *parts*: a
    ``1 Warboss`` plus ``3-6 Nobz`` unit is fieldable at four to seven models, and it is that
    total the points source prices. Reading each line as its own range would call a legitimate
    ``5 models`` band a mismatch against a line that only ever describes one model.
    """
    minimum = 0
    maximum = 0
    parsed_any = False
    ranged = False

    for line in lines:
        low, high = leading_count(line)
        if low is None:
            continue
        parsed_any = True
        minimum += low
        maximum += high if high is not None else low
        if high is not None and high != low:
            ranged = True

    if not parsed_any:
        return CompositionRange(None, None, BandClass.UNPARSED)
    return CompositionRange(minimum, maximum, BandClass.RANGE if ranged else BandClass.EXACT)


def reconcile_bands(
    *, datasheet_id: str, model_counts: Sequence[int], composition_lines: Sequence[str]
) -> list[Finding]:
    """Check each points band against the composition, and report what does not fit."""
    composition = parse_composition(composition_lines)

    if composition.classification is BandClass.UNPARSED:
        return [
            build_finding(
                "REC-COMPOSITION-UNPARSED",
                entity_refs=[datasheet_id],
                detail={
                    "datasheet_id": datasheet_id,
                    "composition_lines": len(composition_lines),
                    "model_counts": sorted(set(model_counts)),
                },
            )
        ]

    assert composition.minimum is not None and composition.maximum is not None
    return [
        build_finding(
            "REC-BAND-MISMATCH",
            entity_refs=[datasheet_id],
            detail={
                "datasheet_id": datasheet_id,
                "model_count": model_count,
                "composition_min": composition.minimum,
                "composition_max": composition.maximum,
                "composition_class": composition.classification.value,
            },
        )
        for model_count in sorted(set(model_counts))
        if not composition.contains(model_count)
    ]
