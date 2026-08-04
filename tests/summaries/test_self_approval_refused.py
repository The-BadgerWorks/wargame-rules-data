# AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote the self-approval guard test suite
# (task T126), confirmed failing before tools/check_summary_approvals.py existed: a PR that
# introduces `review_state: "approved"` on a record whose author is the PR author fails CI
# (research D6). tools/ is not an installed package, so the module is loaded directly from its
# file path, matching tests/unit/test_check_change_classes.py's convention.
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_MODULE_PATH = Path(__file__).resolve().parents[2] / "tools" / "check_summary_approvals.py"
_spec = importlib.util.spec_from_file_location("check_summary_approvals", _MODULE_PATH)
assert _spec is not None and _spec.loader is not None
check_summary_approvals = importlib.util.module_from_spec(_spec)
sys.modules["check_summary_approvals"] = check_summary_approvals
_spec.loader.exec_module(check_summary_approvals)

newly_approved = check_summary_approvals.newly_approved
self_approved_keys = check_summary_approvals.self_approved_keys


def _record(key: str, *, review_state: str, reviewed_by: str = "someone") -> dict[str, object]:
    return {
        "ability_key": key,
        "name": key.split(":")[-1].title(),
        "summary": "Invented mechanics-only summary authored for this data set.",
        "review_state": review_state,
        "mechanic_digest": "d" * 32,
        "reviewed_by": reviewed_by,
        "reviewed_at": "2026-06-13T00:00:00Z",
    }


def test_a_brand_new_approved_record_is_newly_approved() -> None:
    head = [_record("core:deep-strike", review_state="approved")]
    assert newly_approved([], head) == head


def test_a_record_transitioning_into_approved_is_newly_approved() -> None:
    base = [_record("core:deep-strike", review_state="in_review")]
    head = [_record("core:deep-strike", review_state="approved")]
    assert newly_approved(base, head) == head


def test_an_already_approved_record_carried_forward_untouched_is_not_newly_approved() -> None:
    """FR-024's carry-forward: an unchanged approval was not introduced by this PR."""
    base = [_record("core:deep-strike", review_state="approved", reviewed_by="alice")]
    head = [_record("core:deep-strike", review_state="approved", reviewed_by="alice")]
    assert newly_approved(base, head) == []


def test_a_record_that_stays_draft_is_not_newly_approved() -> None:
    base = [_record("core:deep-strike", review_state="draft")]
    head = [_record("core:deep-strike", review_state="draft")]
    assert newly_approved(base, head) == []


def test_self_approval_is_flagged() -> None:
    head = [_record("core:deep-strike", review_state="approved", reviewed_by="pr-author")]
    assert self_approved_keys(newly_approved([], head), actor="pr-author") == ["core:deep-strike"]


def test_a_non_author_approval_is_not_flagged() -> None:
    head = [_record("core:deep-strike", review_state="approved", reviewed_by="a-different-curator")]
    assert self_approved_keys(newly_approved([], head), actor="pr-author") == []


def test_only_the_self_authored_key_among_several_is_flagged() -> None:
    head = [
        _record("core:deep-strike", review_state="approved", reviewed_by="pr-author"),
        _record("core:leader", review_state="approved", reviewed_by="a-different-curator"),
    ]
    assert self_approved_keys(newly_approved([], head), actor="pr-author") == ["core:deep-strike"]


def test_an_empty_actor_flags_nothing() -> None:
    """A CI context that could not resolve an actor must not silently flag every approval."""
    head = [_record("core:deep-strike", review_state="approved", reviewed_by="")]
    assert self_approved_keys(newly_approved([], head), actor="") == []
