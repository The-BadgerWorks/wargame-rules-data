# AI-Assisted: Claude Code (model: claude-opus-5) - Asserts the run ledger carries mechanical
# values only and appends one canonical line per command (task T031,
# contracts/pipeline-run-interface.md §6).
"""The ledger is evidence, so it is append-only, canonical, and free of prose.

A quiet period must be distinguishable from a broken detector (FR-054), which only works if
every command really does leave a line behind — and the line has to be safe to keep forever,
which is why the free-text guard runs at the write rather than in a later scan.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pipeline.observability.ledger import (
    NonMechanicalLedgerEntryError,
    RunLedgerEntry,
    StageOutcome,
    Trigger,
    append_entry,
    read_entries,
)


def _entry(**overrides: object) -> RunLedgerEntry:
    base: dict[str, object] = {
        "run_id": "17252891234",
        "command": "build",
        "trigger": Trigger.SCHEDULED,
        "channel": "prerelease",
        "started_at": "2026-08-02T09:00:00Z",
        "duration_ms": 128_000,
        "stage_outcomes": {"acquire": StageOutcome.OK, "publish": StageOutcome.SKIPPED},
        "coverage": {"factions": 30, "datasheets": 1487, "priced_datasheets": 1487},
        "finding_counts_by_class": {"reconciliation": 44, "data_quality": 31},
        "finding_counts_by_severity": {"blocking": 0, "advisory": 96},
        "unverified_count": 23,
        "hybrid_count": 1487,
        "candidate_ref": "candidate/mfm-2026-06",
        "rules_version_id": "mfm-2026-06",
        "exit_code": 20,
    }
    base.update(overrides)
    return RunLedgerEntry(**base)  # type: ignore[arg-type]


def test_one_entry_is_one_canonical_line(tmp_path: Path) -> None:
    path = tmp_path / "run-ledger.jsonl"
    line = append_entry(path, _entry())

    raw = path.read_bytes()
    assert raw.endswith(b"\n")
    assert raw.count(b"\n") == 1
    assert b"\r" not in raw
    assert line == raw.decode("utf-8").rstrip("\n")

    keys = list(json.loads(line))
    assert keys == sorted(keys), "the ledger goes through the canonical serialiser"


def test_the_contracts_fields_are_all_present(tmp_path: Path) -> None:
    path = tmp_path / "run-ledger.jsonl"
    append_entry(path, _entry())
    written = read_entries(path)[0]

    for field in (
        "run_id",
        "trigger",
        "channel",
        "started_at",
        "duration_ms",
        "stage_outcomes",
        "coverage",
        "finding_counts_by_class",
        "finding_counts_by_severity",
        "unverified_count",
        "hybrid_count",
        "candidate_ref",
        "exit_code",
    ):
        assert field in written, f"contract §6 requires {field}"


def test_entries_append_and_never_rewrite(tmp_path: Path) -> None:
    path = tmp_path / "run-ledger.jsonl"
    append_entry(path, _entry(command="detect", exit_code=0))
    append_entry(path, _entry(command="build", exit_code=20))

    entries = read_entries(path)
    assert [e["command"] for e in entries] == ["detect", "build"]


def test_a_missing_ledger_reads_as_empty(tmp_path: Path) -> None:
    assert read_entries(tmp_path / "absent.jsonl") == []


@pytest.mark.parametrize(
    "smuggled",
    [
        '<span class="kwb">Deep Strike</span>',
        "Special (правая колонка)",
        "$RS_PLACEHOLDER",
        "Land&nbsp;Raider",
        "x" * 400,
    ],
)
def test_an_entry_carrying_free_text_or_source_residue_is_refused(smuggled: str) -> None:
    with pytest.raises(NonMechanicalLedgerEntryError):
        _entry(candidate_ref=smuggled)


def test_nested_values_are_checked_too() -> None:
    with pytest.raises(NonMechanicalLedgerEntryError):
        _entry(stage_outcomes={"<script>": StageOutcome.OK})


def test_coverage_is_recorded_as_counts_so_the_line_stays_canonical() -> None:
    # Ratios are floats and floats are not canonically serialisable; the ratio is derivable
    # from the counts and the configured threshold anyway.
    with pytest.raises(ValueError, match="valid integer"):
        _entry(coverage={"factions": 0.95})
