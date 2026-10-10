# AI-Assisted: Claude Code (model: Claude Sonnet 5) - 2026-10-09 pipeline P3 task 6: the Owner's
# budget pin (P1 Task 2's receipt, recorded uncommitted until now). Pins curation/game-sizes.json's
# four band values and curation/edition-rules.json's enhancement_limit_per_army against the
# Owner's 2026-10-09 figures (DP 1/2/3/3, enhancement limit 4), plus the two cross-band invariants
# those figures satisfy, so an unreviewed curation edit that drifts either file is caught here
# rather than discovered downstream. curation/ itself is READ-ONLY to this task -- nothing here
# writes it; the "bite" receipt (see task-6-report.md) edits it only transiently, in the working
# tree, and reverts before anything is committed.
"""The Owner's 2026-10-09 budget ruling, pinned.

These three facts are curated in ``curation/game-sizes.json`` and
``curation/edition-rules.json``, not derived by any production, so nothing else in this suite
would notice a drift in either file. This is the one test that reads them as contract values
rather than as arbitrary authored content.
"""

from __future__ import annotations

import pytest

from pipeline.config import repo_root
from pipeline.curate.authored import load_authored

REPO = repo_root()

#: (band id, max_detachments, detachment_points_budget, enhancement cap) -- the Owner's
#: 2026-10-09 ruling, transcribed by hand from curation/game-sizes.json, independently of the
#: pipeline reading the same file.
_OWNER_BUDGETS = (
    ("gs-combat-patrol", 1, 1, 1),
    ("gs-incursion", 2, 2, 2),
    ("gs-strike-force", 3, 3, 4),
    ("gs-onslaught", 3, 3, 3),
)


def _bands() -> dict[str, object]:
    return {band.id: band for band in load_authored(REPO / "curation").game_sizes}


@pytest.mark.parametrize(
    ("band_id", "max_detachments", "detachment_points_budget", "max_enhancements"), _OWNER_BUDGETS
)
def test_each_bands_budget_matches_the_owners_2026_10_09_ruling(
    band_id: str, max_detachments: int, detachment_points_budget: int, max_enhancements: int
) -> None:
    band = _bands()[band_id]
    assert band.max_detachments == max_detachments  # type: ignore[attr-defined]
    assert band.detachment_points_budget == detachment_points_budget  # type: ignore[attr-defined]
    assert band.max_enhancements == max_enhancements  # type: ignore[attr-defined]


def test_the_edition_wide_enhancement_limit_is_four() -> None:
    edition_rules = {
        rule.rule_key: rule.value for rule in load_authored(REPO / "curation").edition_rules
    }
    assert edition_rules["enhancement_limit_per_army"] == 4


def test_every_band_is_covered_and_the_two_cross_band_invariants_hold() -> None:
    """A deleted band must not pass vacuously -- the id set is asserted exactly, not just >=.

    Then the two invariants the Owner's figures satisfy: every band's detachment count and its
    points budget move together (one detachment, one budget point), and the edition-wide
    enhancement limit is never tighter than any single band's own per-band cap.
    """
    bands = _bands()
    assert set(bands) == {b[0] for b in _OWNER_BUDGETS}

    edition_rules = {
        rule.rule_key: rule.value for rule in load_authored(REPO / "curation").edition_rules
    }
    enhancement_limit = edition_rules["enhancement_limit_per_army"]

    for band in bands.values():
        assert band.max_detachments == band.detachment_points_budget  # type: ignore[attr-defined]
        assert enhancement_limit >= band.max_enhancements  # type: ignore[attr-defined]
