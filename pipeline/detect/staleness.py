# AI-Assisted: Claude Code (model: claude-sonnet-5) - Implemented the detection staleness alarm
# (task T103's implementation surface, FR-055): no successful check within
# WGC_DETECT_STALENESS_HOURS raises the alert, and a successful check resets it.
"""The detection staleness alarm (FR-055).

A **successful** check is a ``detect`` run that completed and returned ``0`` (no change) or
``10`` (change detected) — exit ``40``/``41`` mean the detector itself failed, which is exactly
the fault this alarm exists to surface, so a failed run does not reset it. This is the same
"a completed no-change check is recorded" property ``pipeline.observability.ledger`` documents:
silence, or a run of failures, in ``state/run-ledger.jsonl`` is a fault signal, not a quiet
period.

This module reads plain ledger dictionaries (:func:`pipeline.observability.ledger.read_entries`)
rather than :class:`~pipeline.observability.ledger.RunLedgerEntry` objects, so it can be tested
against a synthetic history with no pydantic model construction in the way.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from typing import Any

#: The detect command's successful exit codes — a completed check, whichever verdict it reached.
_SUCCESSFUL_DETECT_EXIT_CODES: frozenset[int] = frozenset({0, 10})


def _is_successful_detect(entry: Mapping[str, Any]) -> bool:
    if entry.get("command") != "detect":
        return False
    return entry.get("exit_code") in _SUCCESSFUL_DETECT_EXIT_CODES


def last_successful_check_at(entries: Sequence[Mapping[str, Any]]) -> datetime | None:
    """The timestamp of the most recent successful ``detect`` run, or ``None`` if there is none."""
    moments = [
        datetime.fromisoformat(str(entry["started_at"]).replace("Z", "+00:00"))
        for entry in entries
        if _is_successful_detect(entry)
    ]
    return max(moments) if moments else None


def is_stale(entries: Sequence[Mapping[str, Any]], *, now: datetime, staleness_hours: int) -> bool:
    """Whether no successful ``detect`` check has completed within ``staleness_hours`` of ``now``.

    No successful check ever recorded is stale by definition — that is the state a fresh
    repository starts in, and it is exactly the condition the alarm must not stay silent about.
    """
    last = last_successful_check_at(entries)
    if last is None:
        return True
    if now.tzinfo is None:
        now = now.replace(tzinfo=UTC)
    age_hours = (now - last).total_seconds() / 3600.0
    return age_hours > staleness_hours
