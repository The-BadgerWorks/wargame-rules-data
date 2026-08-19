# AI-Assisted: Claude Code (model: claude-sonnet-5) - Setup-phase sanity check for 009 task T009's
# sibling-collision fixture (fixtures_009_disambiguation.py): confirms the fixture is genuinely
# unresolvable under today's ladder, before Phase 5 builds a real disambiguation test against it.
"""Confirms `fixtures_009_disambiguation.py`'s data is shaped the way its own docstring claims.

Not FR-016's test. T051 (Phase 5) writes that, once a replacement disambiguation rung exists to
assert a *resolution* against this same collision data. This file only pins the "before" half: the
collision blocks today, exactly as `test_chapter_keyword_preference.py`'s own no-chapter-record
case already does for the html-mode shape.
"""

from __future__ import annotations

from pipeline.models.findings import Severity
from tests.reconcile.fixtures_009_disambiguation import run_sibling_match


def test_the_sibling_collision_blocks_with_no_narrowing_signal() -> None:
    outcome = run_sibling_match("ember-host")

    assert [f.finding_code for f in outcome.findings] == ["REC-AMBIGUOUS-MATCH"]
    assert outcome.findings[0].severity is Severity.BLOCKING
    assert not outcome.matches, "nothing narrows this collision today; picking would be a guess"


def test_the_sibling_collision_blocks_for_every_sibling_and_the_parent() -> None:
    """The refusal is not one faction's problem: every scope that could claim the name is equally
    unable to prefer one row over the other today."""
    for slug in ("march-legion", "ember-host", "ash-host"):
        outcome = run_sibling_match(slug)
        assert [f.finding_code for f in outcome.findings] == ["REC-AMBIGUOUS-MATCH"], slug
