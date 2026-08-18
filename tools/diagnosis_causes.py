# AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote the FR-005/FR-006 cause-kind mapping
# (009 task T033/T036): a small, deliberately narrow classification of the three named
# hypotheses FR-006 requires an outcome for, so the diagnosis report and its test can both cite
# one definition rather than restating FR-005's three kinds as prose in two places.
"""FR-005's three cause kinds, over FR-006's three named hypotheses.

**Deliberately narrow.** This is not a general classifier over `option_taxonomy.classify()`'s
thirteen research D1b classes -- that broader row-count attribution is `reports/009-diagnosis/`'s
own prose, written by a human reading the measured deltas (task T036), not code. This module
names only the three hypotheses FR-006 requires an outcome for, and answers the one question each
of them turns on: which of FR-005's three kinds -- **denominator**, **normalization**, or
**vocabulary** -- does it belong to, if real.

FR-005: *"Only vocabulary causes may motivate a new production."* Rule 5 means no production is
authored by this feature regardless of the answer -- this module exists so the report and its
test can both point at one definition instead of two.
"""

from __future__ import annotations

from typing import Final, Literal

CauseKind = Literal["denominator", "normalization", "vocabulary"]

#: FR-006's three named hypotheses, each mapped to the FR-005 kind it belongs to if real.
#:
#: * ``markup_form_asymmetry`` (a) is a **normalization** cause: a text form the shared
#:   pre-pass now strips (post T030) that the export emits and the html arm's tags never reach
#:   in the first place (`plan.md` finding 7) -- a shared fix, not a new production.
#: * ``extractor_row_drop`` (b) is a **denominator** cause: a row the html extractor discards at
#:   extraction (`wahapedia_html_dom.py:910-924`) and the export delivers as an ordinary row --
#:   it was never a real option sentence under either arm's own accounting, so no production
#:   could ever resolve it.
#: * ``row_granularity`` (c) is a **vocabulary** cause *if real* (research.md Q1's stated
#:   fallback): a genuine geometry difference would change the stem-versus-alternative shape the
#:   grammar reads, which is exactly what a vocabulary gap looks like from the grammar's side --
#:   research.md's own text is explicit that this is not settled by a fixture, only by the
#:   aggregate row-granularity measurement (`option_taxonomy.py --compare-modes`'s own section).
HYPOTHESIS_KIND: Final[dict[str, CauseKind]] = {
    "markup_form_asymmetry": "normalization",
    "extractor_row_drop": "denominator",
    "row_granularity": "vocabulary",
}
