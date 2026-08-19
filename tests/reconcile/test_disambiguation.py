# AI-Assisted: Claude Code (model: claude-sonnet-5) - Added for 009 task T051 (FR-016, SC-005,
# Product Owner decision T047/O2 2026-08-18): the disambiguation rung `fixtures_009_disambiguation
# .py`'s own docstring left ready for this task -- a faction-scoped `unit-map.json` entry
# (T022-T024's mechanism) resolves a same-name sibling collision to exactly one row per faction,
# and a collision with NO entry authored still blocks rather than picks.
"""FR-016's replacement rung: a declared crosswalk entry, faction-scoped, resolves the collision.

`test_009_setup_fixtures.py` already pins the "before" half (the collision blocks with no
narrowing signal). This is the "after" half: once a curator authors a `unit-map.json` entry
scoped to one sibling, THAT sibling resolves to its own row and the collision no longer reaches
stage 4 for it — while a sibling with no entry authored keeps blocking, exactly as O2's decision
records (the crosswalk's scope is the measured minimal set, not every collision pre-emptively).
"""

from __future__ import annotations

from pipeline.models.authored import UnitMapEntry
from pipeline.models.findings import Severity
from tests.reconcile.fixtures_009_disambiguation import (
    ASH_HOST,
    EMBER_HOST,
    MARCH_LEGION,
    run_sibling_match,
    sibling_authored,
)

#: One entry per resolvable sibling, faction-scoped (rule 8: every entry this feature authors
#: carries `faction_id`) — `ember-host`'s row (`ML04`) is pinned to `f-ember-host` only.
EMBER_HOST_ENTRY = UnitMapEntry(
    datasheet_id="ds-bracklight-sentinel-ember-host",
    mfm_display_name="BRACKLIGHT SENTINEL",
    wahapedia_datasheet_id="ML04",
    confirmed_at="2026-08-18",
    confirmed_by="test-curator",
    faction_id="f-ember-host",
)
ASH_HOST_ENTRY = UnitMapEntry(
    datasheet_id="ds-bracklight-sentinel-ash-host",
    mfm_display_name="BRACKLIGHT SENTINEL",
    wahapedia_datasheet_id="ML09",
    confirmed_at="2026-08-18",
    confirmed_by="test-curator",
    faction_id="f-ash-host",
)


def test_a_faction_scoped_entry_resolves_its_own_sibling_to_exactly_one_row() -> None:
    content = sibling_authored(unit_map=(EMBER_HOST_ENTRY,))

    outcome = run_sibling_match("ember-host", content)

    assert outcome.findings == []
    assert len(outcome.matches) == 1
    match = outcome.matches[0]
    assert match.datasheet_id == "ds-bracklight-sentinel-ember-host"
    assert match.faction_id == "f-ember-host"
    assert match.wahapedia_datasheet_id == "ML04"
    assert match.stage == "identity"


def test_the_entry_does_not_leak_into_the_uncovered_sibling() -> None:
    """A pin scoped to `f-ember-host` must not resolve `ash-host`'s OWN collision candidate --
    the exact C1-breach shape T022's guard exists to prevent, re-asserted at the disambiguation
    rung specifically rather than only at the six-chapter fixture."""
    content = sibling_authored(unit_map=(EMBER_HOST_ENTRY,))

    outcome = run_sibling_match("ash-host", content)

    assert [f.finding_code for f in outcome.findings] == ["REC-AMBIGUOUS-MATCH"]
    assert outcome.findings[0].severity is Severity.BLOCKING
    assert not outcome.matches


def test_both_siblings_pinned_resolve_independently_to_distinct_ids() -> None:
    content = sibling_authored(unit_map=(EMBER_HOST_ENTRY, ASH_HOST_ENTRY))

    ember_outcome = run_sibling_match("ember-host", content)
    ash_outcome = run_sibling_match("ash-host", content)

    assert ember_outcome.findings == ash_outcome.findings == []
    assert len(ember_outcome.matches) == len(ash_outcome.matches) == 1
    ember_id = ember_outcome.matches[0].datasheet_id
    ash_id = ash_outcome.matches[0].datasheet_id
    assert ember_id != ash_id
    assert {ember_id, ash_id} == {
        "ds-bracklight-sentinel-ember-host",
        "ds-bracklight-sentinel-ash-host",
    }


def test_the_parent_scope_is_unaffected_by_either_childs_pin() -> None:
    """`unit-map.json`'s `faction_id` scopes to ONE faction; the parent scope T009's fixture also
    exercises must keep blocking, since neither child's pin names the parent."""
    content = sibling_authored(unit_map=(EMBER_HOST_ENTRY, ASH_HOST_ENTRY))

    outcome = run_sibling_match("march-legion", content)

    assert [f.finding_code for f in outcome.findings] == ["REC-AMBIGUOUS-MATCH"]
    assert not outcome.matches


def test_no_entry_authored_at_all_still_blocks_rather_than_picks() -> None:
    """O2's decision: the crosswalk's scope is the measured minimal set, not every collision
    pre-emptively — an un-pinned collision correctly keeps refusing (rule 10's "report, never
    guess" stage 4), which this reconfirms is still reachable with the mechanism now live."""
    outcome = run_sibling_match("ember-host", sibling_authored())

    assert [f.finding_code for f in outcome.findings] == ["REC-AMBIGUOUS-MATCH"]
    assert not outcome.matches


def test_march_legion_and_ember_host_fixture_constants_are_still_the_ones_this_test_assumes() -> (
    None
):
    """A cheap tripwire: if the fixture module's faction ids ever drift, this file's own entries
    would silently stop exercising the scope they claim to."""
    assert MARCH_LEGION.faction_id == "f-march-legion"
    assert EMBER_HOST.faction_id == "f-ember-host"
    assert ASH_HOST.faction_id == "f-ash-host"
