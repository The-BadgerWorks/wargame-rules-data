# AI-Assisted: Claude Code (model: claude-sonnet-5) - Implemented V7, the ability-summary
# blocking and advisory checks (task T129): SUM-MISSING, SUM-UNAPPROVED, SUM-NEEDS-REREVIEW as
# blocking, and SUM-OVERLENGTH as advisory (FR-020, FR-022, FR-023).
# AI-Assisted: Claude Code (model: claude-opus-5) - Reduced this module to the abilities-shaped
# call of the generalised :mod:`pipeline.validate.gates` (004 task T046). Not deleted and not
# re-implemented: the abilities class keeps its own named entry point, its callers, and its test
# suite, and every one of them now exercises the same code path the three new classes do.
"""V7 — every ability the snapshot uses carries an approved, current, in-length summary.

The three blocking codes are three different reasons publication is refused, kept distinct
because a curator reading the report needs to know which one to act on: `SUM-MISSING` means
"nobody has started this one", `SUM-UNAPPROVED` means "someone has, it is not signed off yet",
and `SUM-NEEDS-REREVIEW` means "it was signed off, but the mechanic moved since". Only the last
of the three can ever apply to a key a curator has already worked on — the state machine only
reaches it from `approved` (data-model.md §4.1).

**The abilities class has no gate switch and is always on.** It predates
`004-rules-data-enrichment` and FR-001 forbids weakening a guarantee this repository already
provides, so the generalisation below passes `Gate.ON` unconditionally and no configuration
variable exists that could say otherwise (`contracts/authored-summary-gates.md` §1).
"""

from __future__ import annotations

from collections.abc import Mapping

from pipeline.config import Gate
from pipeline.curate.summaries import AuthoredSummary
from pipeline.models.authored import SummaryClass
from pipeline.models.curated import CuratedSnapshot
from pipeline.models.findings import Finding
from pipeline.validate.gates import ClassCheck, check_class, used_ability_keys

__all__ = ["check_summaries", "used_ability_keys"]


def check_summaries(
    snapshot: CuratedSnapshot,
    *,
    authored_summaries: Mapping[str, AuthoredSummary],
    current_digests: Mapping[str, str] | None = None,
    summary_max_chars: int,
) -> list[Finding]:
    """V7: the blocking summary-coverage checks, plus the advisory length check.

    Args:
        authored_summaries: the freshly loaded `curation/abilities/` content — **not**
            necessarily `snapshot.ability_summaries`, which a snapshot reconstructed from
            `data/` alone (a bare `validate` re-run) never carries, since authored content is
            never written to the curated tree (FR-017).
        current_digests: this run's freshly computed digests, or ``None`` when this run
            acquired no source text (see :func:`pipeline.curate.summaries.effective_status`).
    """
    return check_class(
        ClassCheck(
            summary_class=SummaryClass.ABILITIES,
            keys=sorted(used_ability_keys(snapshot)),
            authored=authored_summaries,
            current_digests=current_digests,
            gate=Gate.ON,
            max_chars=summary_max_chars,
        )
    )
