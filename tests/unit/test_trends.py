# AI-Assisted: Claude Code (model: claude-sonnet-5) - Tests for the unverified/hybrid-count trend
# sub-report (task T149): an empty ledger renders something sane, a ledger with one published
# version renders a single point, and a ledger with a rising unverified-count series across
# several published versions renders the rising trend visibly (spec.md Monitoring and logging).
"""The trend rendering is the early signal that a source is drifting from the edition in play.

Each test asserts on the *rendered content* rather than merely "did not crash" -- a trend report
that renders without error but never actually says "rising" anywhere is not doing its job.
"""

from __future__ import annotations

from pipeline.report.trends import build_trend_series, render_trends


def _entry(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "entry_kind": "run",
        "run_id": "local-1",
        "command": "build",
        "trigger": "manual",
        "channel": "prerelease",
        "started_at": "2026-06-01T00:00:00Z",
        "duration_ms": 1000,
        "stage_outcomes": {},
        "coverage": {},
        "finding_counts_by_class": {},
        "finding_counts_by_severity": {},
        "unverified_count": 0,
        "hybrid_count": 0,
        "candidate_ref": None,
        "rules_version_id": None,
        "exit_code": 0,
    }
    base.update(overrides)
    return base


def test_an_empty_ledger_renders_something_sane_not_a_crash() -> None:
    rendered = render_trends([])

    assert "Trends" in rendered
    assert rendered.endswith("\n")


def test_entries_with_no_rules_version_id_do_not_participate() -> None:
    # A `detect` sweep that found nothing to build has no version to plot against.
    entries = [_entry(command="detect", rules_version_id=None)]

    assert build_trend_series(entries) == []
    assert "No published-version" in render_trends(entries)


def test_a_single_published_version_renders_a_single_point() -> None:
    entries = [
        _entry(rules_version_id="mfm-2026-06", unverified_count=5, hybrid_count=1487),
    ]

    points = build_trend_series(entries)
    assert len(points) == 1
    assert points[0].rules_version_id == "mfm-2026-06"
    assert points[0].unverified_count == 5
    assert points[0].hybrid_count == 1487

    rendered = render_trends(entries)
    assert "mfm-2026-06" in rendered
    assert "5" in rendered
    assert "1487" in rendered
    # A single point has nowhere to trend from yet.
    assert "not rising" in rendered


def test_a_rising_unverified_count_series_renders_the_rising_trend_visibly() -> None:
    entries = [
        _entry(
            run_id="local-1",
            rules_version_id="mfm-2026-04",
            started_at="2026-04-01T00:00:00Z",
            unverified_count=2,
            hybrid_count=1487,
        ),
        _entry(
            run_id="local-2",
            rules_version_id="mfm-2026-05",
            started_at="2026-05-01T00:00:00Z",
            unverified_count=10,
            hybrid_count=1487,
        ),
        _entry(
            run_id="local-3",
            rules_version_id="mfm-2026-06",
            started_at="2026-06-01T00:00:00Z",
            unverified_count=23,
            hybrid_count=1487,
        ),
    ]

    points = build_trend_series(entries)
    assert [p.rules_version_id for p in points] == ["mfm-2026-04", "mfm-2026-05", "mfm-2026-06"]
    assert [p.unverified_count for p in points] == [2, 10, 23]

    rendered = render_trends(entries)
    for expected in ("mfm-2026-04", "mfm-2026-05", "mfm-2026-06", "2", "10", "23"):
        assert expected in rendered
    assert "Rising unverified-pricing trend" in rendered
    assert "2 -> 23" in rendered


def test_a_flat_hybrid_count_series_is_reported_as_not_rising() -> None:
    entries = [
        _entry(rules_version_id="mfm-2026-04", hybrid_count=1487),
        _entry(rules_version_id="mfm-2026-05", hybrid_count=1487),
    ]

    rendered = render_trends(entries)
    assert "Hybrid-edition count is not rising" in rendered


def test_entries_are_kept_in_ledger_append_order() -> None:
    # The ledger is append-only and chronological (pipeline.observability.ledger's own
    # docstring); the trend must not silently re-sort by rules_version_id or anything else.
    entries = [
        _entry(rules_version_id="mfm-2026-06", unverified_count=23),
        _entry(rules_version_id="mfm-2026-04", unverified_count=2),
    ]

    points = build_trend_series(entries)
    assert [p.rules_version_id for p in points] == ["mfm-2026-06", "mfm-2026-04"]
