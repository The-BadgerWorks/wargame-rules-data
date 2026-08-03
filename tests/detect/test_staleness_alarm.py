# AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote the staleness-alarm tests (task
# T103): no successful check within WGC_DETECT_STALENESS_HOURS raises the alert, and a
# successful check resets it (FR-055).
"""FR-055's staleness alarm, tested against synthetic ledger histories.

A **successful** check is a completed `detect` run — exit `0` (no change) or `10` (change
detected). Exit `40`/`41` mean the detector itself failed, so a run of nothing but failures must
not quietly reset the alarm: that would make the exact fault this alarm exists to surface
invisible to it.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pipeline.cli import run_detect
from pipeline.config import load_config
from pipeline.detect.staleness import is_stale, last_successful_check_at

DETECTION = Path(__file__).resolve().parents[2] / "fixtures" / "detection"


def _entry(command: str, exit_code: int, started_at: str) -> dict[str, Any]:
    return {"command": command, "exit_code": exit_code, "started_at": started_at}


def test_no_successful_check_ever_is_stale() -> None:
    assert is_stale([], now=datetime(2026, 8, 3, tzinfo=UTC), staleness_hours=48) is True


def test_a_recent_successful_check_is_not_stale() -> None:
    now = datetime(2026, 8, 3, 12, 0, tzinfo=UTC)
    entries = [_entry("detect", 0, "2026-08-03T10:00:00Z")]
    assert is_stale(entries, now=now, staleness_hours=48) is False


def test_no_successful_check_within_the_staleness_window_raises_the_alert() -> None:
    now = datetime(2026, 8, 5, tzinfo=UTC)
    entries = [_entry("detect", 0, "2026-08-01T00:00:00Z")]  # 4 days before `now`
    assert is_stale(entries, now=now, staleness_hours=48) is True


def test_a_run_of_nothing_but_failures_does_not_reset_the_alarm() -> None:
    now = datetime(2026, 8, 5, tzinfo=UTC)
    entries = [
        _entry("detect", 0, "2026-08-01T00:00:00Z"),
        _entry("detect", 40, "2026-08-02T00:00:00Z"),
        _entry("detect", 41, "2026-08-03T00:00:00Z"),
        _entry("detect", 40, "2026-08-04T23:00:00Z"),
    ]
    assert is_stale(entries, now=now, staleness_hours=48) is True


def test_a_successful_check_resets_it() -> None:
    now = datetime(2026, 8, 5, tzinfo=UTC)
    entries = [
        _entry("detect", 0, "2026-08-01T00:00:00Z"),
        _entry("detect", 40, "2026-08-02T00:00:00Z"),
        # exit 10 is a completed check too -- a change found is still a check that ran.
        _entry("detect", 10, "2026-08-04T23:00:00Z"),
    ]
    assert is_stale(entries, now=now, staleness_hours=48) is False


def test_last_successful_check_ignores_other_commands_and_failed_checks() -> None:
    entries = [
        _entry("build", 0, "2026-08-04T00:00:00Z"),
        _entry("detect", 41, "2026-08-04T12:00:00Z"),
        _entry("detect", 0, "2026-08-03T00:00:00Z"),
    ]
    assert last_successful_check_at(entries) == datetime(2026, 8, 3, tzinfo=UTC)


def test_run_detect_reports_not_stale_immediately_after_a_successful_check(temp_repo) -> None:  # type: ignore[no-untyped-def]
    repo = temp_repo()
    result = run_detect(
        config=load_config(env={}),
        fixtures_dir=DETECTION / "baseline",
        offline=True,
        repository_root=repo,
    )
    assert result.stale is False
