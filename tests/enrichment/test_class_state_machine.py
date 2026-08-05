# AI-Assisted: Claude Code (model: claude-opus-5) - Wrote the generalised state-machine suite
# (004 task T043), confirmed failing before pipeline/validate/gates.py existed: every assertion
# is parametrised over all four summary classes, because the point of US3's machinery is that
# there is exactly ONE state machine, one digest rule, one carry-forward rule, and one
# self-approval refusal — not four that happen to agree today (004 FR-021..FR-028).
"""One state machine, four classes.

Every test here runs four times. That is the whole design under test: `contracts/authored-summary-
gates.md` §1 says the four classes share the `ReviewState` enum, the record shape, the digest
algorithm, the carry-forward rule and the self-approval refusal **without variation**, and a
suite that checked the ability class and trusted the rest would let the three new ones drift the
first time one of them needed a small exception.

The one thing that legitimately differs is which finding code a class emits, and that is a
property of the class's gate — proven in `test_gates_and_ratchet.py`, not here.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from pipeline.config import Gate
from pipeline.curate.summaries import SummaryStatus, effective_status, summary_statuses
from pipeline.models.authored import (
    AbilitySummary,
    DetachmentRuleSummary,
    FactionRuleSummary,
    GlossaryEntry,
    ReviewState,
    SummaryClass,
)
from pipeline.models.findings import Severity
from pipeline.validate.gates import ClassCheck, check_class

_MODULE_PATH = Path(__file__).resolve().parents[2] / "tools" / "check_summary_approvals.py"
_spec = importlib.util.spec_from_file_location("check_summary_approvals", _MODULE_PATH)
assert _spec is not None and _spec.loader is not None
check_summary_approvals = importlib.util.module_from_spec(_spec)
sys.modules["check_summary_approvals"] = check_summary_approvals
_spec.loader.exec_module(check_summary_approvals)

ALL_CLASSES = list(SummaryClass)

#: One invented key per class, in that class's own key vocabulary (data-model.md §2).
KEYS = {
    SummaryClass.ABILITIES: "core:tidewalk",
    SummaryClass.FACTION_RULES: "faction:f-glimmerfen-covenant:tidewalk",
    SummaryClass.DETACHMENT_RULES: "detachment:d-fenlight-vigil:veiled-advance",
    SummaryClass.GLOSSARY: "glossary:sustained-hits",
}

SECOND_KEYS = {
    SummaryClass.ABILITIES: "core:fenlight-veil",
    SummaryClass.FACTION_RULES: "faction:f-glimmerfen-covenant:fenlight-veil",
    SummaryClass.DETACHMENT_RULES: "detachment:d-fenlight-vigil:massed-fire",
    SummaryClass.GLOSSARY: "glossary:deadly-demise",
}

SUMMARY = "Invented mechanics-only summary authored for this data set from the mechanic."


def record(
    summary_class: SummaryClass,
    key: str,
    *,
    review_state: ReviewState = ReviewState.APPROVED,
    mechanic_digest: str = "d" * 32,
    summary: str = SUMMARY,
    reviewed_by: str | None = "second-curator",
) -> AbilitySummary | FactionRuleSummary | DetachmentRuleSummary | GlossaryEntry:
    """One authored record in this class's own shape.

    The only field-name difference across the four is `ability_key` -> `summary_key`; everything
    else is identical, which is what lets one machinery serve all four (research D6).
    """
    common = {
        "name": "Tidewalk",
        "summary": summary,
        "review_state": review_state,
        "mechanic_digest": mechanic_digest,
        "reviewed_by": reviewed_by,
        "reviewed_at": "2026-07-01T00:00:00Z",
    }
    if summary_class is SummaryClass.ABILITIES:
        return AbilitySummary(ability_key=key, **common)  # type: ignore[arg-type]
    if summary_class is SummaryClass.FACTION_RULES:
        return FactionRuleSummary(summary_key=key, display_order=1, **common)  # type: ignore[arg-type]
    if summary_class is SummaryClass.DETACHMENT_RULES:
        return DetachmentRuleSummary(
            summary_key=key,
            detachment_id="d-fenlight-vigil",
            **common,  # type: ignore[arg-type]
        )
    return GlossaryEntry(
        summary_key=key,
        keyword_key="sustained hits",
        display_keyword="SUSTAINED HITS",
        has_numeric_parameter=True,
        **common,  # type: ignore[arg-type]
    )


def _check(
    summary_class: SummaryClass,
    *,
    authored: dict[str, object],
    gate: Gate,
    keys: tuple[str, ...] | None = None,
    current_digests: dict[str, str] | None = None,
    max_chars: int = 240,
) -> ClassCheck:
    return ClassCheck(
        summary_class=summary_class,
        keys=keys if keys is not None else tuple(authored),
        authored=authored,  # type: ignore[arg-type]
        current_digests=current_digests,
        gate=gate,
        max_chars=max_chars,
    )


@pytest.mark.parametrize("summary_class", ALL_CLASSES)
@pytest.mark.parametrize(
    "review_state",
    [ReviewState.DRAFT, ReviewState.IN_REVIEW, ReviewState.NEEDS_REREVIEW],
)
def test_an_unapproved_state_blocks_once_the_gate_is_on(
    summary_class: SummaryClass, review_state: ReviewState
) -> None:
    key = KEYS[summary_class]
    findings = check_class(
        _check(
            summary_class,
            authored={key: record(summary_class, key, review_state=review_state)},
            gate=Gate.ON,
        )
    )

    assert len(findings) == 1
    assert findings[0].severity is Severity.BLOCKING
    assert findings[0].finding_code.startswith(f"{summary_class.finding_prefix}-")
    assert findings[0].entity_refs == (key,)


@pytest.mark.parametrize("summary_class", ALL_CLASSES)
@pytest.mark.parametrize(
    "review_state",
    [ReviewState.DRAFT, ReviewState.IN_REVIEW, ReviewState.NEEDS_REREVIEW],
)
def test_an_unapproved_state_ships_name_only_and_advisory_while_the_gate_is_off(
    summary_class: SummaryClass, review_state: ReviewState
) -> None:
    """The abilities class has no off state — its gate predates this feature (FR-001)."""
    key = KEYS[summary_class]
    gate = Gate.OFF if summary_class.has_gate_switch else Gate.ON
    findings = check_class(
        _check(
            summary_class,
            authored={key: record(summary_class, key, review_state=review_state)},
            gate=gate,
        )
    )

    assert len(findings) == 1
    if summary_class.has_gate_switch:
        assert findings[0].finding_code == f"{summary_class.finding_prefix}-OUTSTANDING"
        assert findings[0].severity is Severity.ADVISORY
    else:
        assert findings[0].severity is Severity.BLOCKING


@pytest.mark.parametrize("summary_class", ALL_CLASSES)
def test_approved_carries_forward_with_no_re_authoring_while_the_digest_is_unchanged(
    summary_class: SummaryClass,
) -> None:
    key = KEYS[summary_class]
    authored = {key: record(summary_class, key, mechanic_digest="d" * 32)}

    status = effective_status(key, authored=authored, current_digest="d" * 32)  # type: ignore[arg-type]

    assert status is SummaryStatus.APPROVED
    assert not status.blocks_publication
    assert (
        check_class(
            _check(
                summary_class,
                authored=authored,
                gate=Gate.ON,
                current_digests={key: "d" * 32},
            )
        )
        == []
    )


@pytest.mark.parametrize("summary_class", ALL_CLASSES)
def test_a_run_with_no_fresh_digest_trusts_the_stored_approved_state(
    summary_class: SummaryClass,
) -> None:
    """A bare `validate` acquires nothing: no evidence of drift, so no flip (FR-026)."""
    key = KEYS[summary_class]
    authored = {key: record(summary_class, key)}
    assert effective_status(key, authored=authored, current_digest=None) is SummaryStatus.APPROVED  # type: ignore[arg-type]


@pytest.mark.parametrize("summary_class", ALL_CLASSES)
def test_a_moved_digest_flags_exactly_one_summary_and_no_other(
    summary_class: SummaryClass,
) -> None:
    first, second = KEYS[summary_class], SECOND_KEYS[summary_class]
    authored = {
        first: record(summary_class, first, mechanic_digest="d" * 32),
        second: record(summary_class, second, mechanic_digest="e" * 32),
    }

    statuses = summary_statuses(
        authored,
        authored=authored,  # type: ignore[arg-type]
        current_digests={first: "9" * 32, second: "e" * 32},
    )

    assert statuses[first] is SummaryStatus.NEEDS_REREVIEW
    assert statuses[second] is SummaryStatus.APPROVED
    flagged = [key for key, status in statuses.items() if status is SummaryStatus.NEEDS_REREVIEW]
    assert flagged == [first]


@pytest.mark.parametrize("summary_class", ALL_CLASSES)
def test_a_key_with_no_authored_record_is_missing_not_defaulted(
    summary_class: SummaryClass,
) -> None:
    key = KEYS[summary_class]
    assert effective_status(key, authored={}, current_digest=None) is SummaryStatus.MISSING


@pytest.mark.parametrize("summary_class", ALL_CLASSES)
def test_an_overlength_approved_summary_is_advisory_in_either_gate_state(
    summary_class: SummaryClass,
) -> None:
    """A good summary is never refused for a trailing clause (contract §2 item 3)."""
    key = KEYS[summary_class]
    authored = {key: record(summary_class, key, summary="x" * 241)}

    for gate in (Gate.OFF, Gate.ON):
        findings = check_class(
            _check(
                summary_class,
                authored=authored,
                gate=gate,
                current_digests={key: "d" * 32},
                max_chars=240,
            )
        )
        assert [f.finding_code for f in findings] == [f"{summary_class.finding_prefix}-OVERLENGTH"]
        assert findings[0].severity is Severity.ADVISORY


@pytest.mark.parametrize("summary_class", ALL_CLASSES)
def test_a_self_approval_is_refused(summary_class: SummaryClass) -> None:
    """Keyed by the class's own key field, per contract §6's glob-to-key-field table."""
    key_field = summary_class.key_field
    head = [
        {
            key_field: KEYS[summary_class],
            "review_state": "approved",
            "reviewed_by": "pr-author",
            "summary": SUMMARY,
        }
    ]

    introduced = check_summary_approvals.newly_approved([], head, key_field=key_field)
    offending = check_summary_approvals.self_approved_keys(
        introduced, actor="pr-author", key_field=key_field
    )

    assert offending == [KEYS[summary_class]]


@pytest.mark.parametrize("summary_class", ALL_CLASSES)
def test_an_approval_by_someone_other_than_the_actor_is_not_refused(
    summary_class: SummaryClass,
) -> None:
    key_field = summary_class.key_field
    head = [
        {
            key_field: KEYS[summary_class],
            "review_state": "approved",
            "reviewed_by": "second-curator",
        }
    ]

    introduced = check_summary_approvals.newly_approved([], head, key_field=key_field)

    assert (
        check_summary_approvals.self_approved_keys(
            introduced, actor="pr-author", key_field=key_field
        )
        == []
    )


@pytest.mark.parametrize("summary_class", ALL_CLASSES)
def test_a_carried_forward_approval_is_not_this_pull_requests_to_refuse(
    summary_class: SummaryClass,
) -> None:
    key_field = summary_class.key_field
    unchanged = [
        {
            key_field: KEYS[summary_class],
            "review_state": "approved",
            "reviewed_by": "pr-author",
        }
    ]

    assert check_summary_approvals.newly_approved(unchanged, unchanged, key_field=key_field) == []
