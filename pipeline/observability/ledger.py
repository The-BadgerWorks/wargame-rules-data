# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the append-only run ledger
# (task T031) per contracts/pipeline-run-interface.md §6 and data-model.md §6.4: one entry per
# command carrying run id, trigger, channel, timings, stage outcomes, coverage, finding counts,
# unverified and hybrid counts, candidate ref, and exit code — mechanical values only.
"""The append-only run ledger, ``state/run-ledger.jsonl``.

Every command appends exactly one entry (contract §6). Two properties matter more than the
field list:

* **Ledger entries carry mechanical values only.** No free text, no publisher prose, no
  diagnostic quoting a source fragment (FR-013). :func:`append_entry` refuses an entry that
  violates this, so the guarantee is enforced at the write rather than audited afterwards.
* **A completed no-change check is recorded**, which is what makes a quiet period
  distinguishable from a broken detector (FR-054). Silence in this file is a fault signal.

Coverage is recorded as **counts, not ratios**. The ratio is derivable from the counts and the
configured threshold, and keeping the ledger integer-only lets every line go through the same
canonical serialiser as every other artifact in this repository.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from enum import StrEnum
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from pipeline.build.canonical_json import JsonValue, dumps_bundle
from pipeline.models.mechanical import assert_mechanical_string

#: The ledger's path relative to the repository root.
LEDGER_RELATIVE_PATH = "state/run-ledger.jsonl"


class Trigger(StrEnum):
    """What started the run (data-model.md §6.4)."""

    SCHEDULED = "scheduled"
    MANUAL = "manual"
    DETECTION = "detection"


class StageOutcome(StrEnum):
    """How one pipeline stage ended."""

    OK = "ok"
    SKIPPED = "skipped"
    FAILED = "failed"


class NonMechanicalLedgerEntryError(RuntimeError):
    """An entry carrying something other than ids, names, numbers, and enumerated codes.

    Deliberately not a ``ValueError``: pydantic wraps those into a ``ValidationError``, and a
    prose leak should surface as itself rather than as one failure among a field list.
    """


class RunLedgerEntry(BaseModel):
    """One command's ledger line."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    entry_kind: Literal["run"] = "run"
    run_id: str = Field(description="the workflow run id, or a local run identifier")
    command: str
    trigger: Trigger
    channel: str
    started_at: str = Field(description="ISO-8601 UTC")
    duration_ms: int = 0
    stage_outcomes: Mapping[str, StageOutcome] = Field(default_factory=dict)
    coverage: Mapping[str, int] = Field(
        default_factory=dict, description="counts, not ratios — see the module docstring"
    )
    finding_counts_by_class: Mapping[str, int] = Field(default_factory=dict)
    finding_counts_by_severity: Mapping[str, int] = Field(default_factory=dict)
    unverified_count: int = 0
    hybrid_count: int = 0
    candidate_ref: str | None = None
    rules_version_id: str | None = None
    exit_code: int = 0

    @model_validator(mode="after")
    def _no_free_text(self) -> RunLedgerEntry:
        _assert_mechanical(self.model_dump(mode="json"), path="entry")
        return self


def _assert_mechanical(value: object, *, path: str) -> None:
    """Recursively assert every string in ``value`` is a mechanical value."""
    if isinstance(value, str):
        try:
            assert_mechanical_string(value, field=path)
        except ValueError as exc:
            raise NonMechanicalLedgerEntryError(str(exc)) from exc
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            # Keys are checked too: a mapping key is just as capable of carrying a source
            # fragment as a value, and rather easier to overlook.
            _assert_mechanical(key, path=f"{path}.<key>")
            _assert_mechanical(item, path=f"{path}.{key}")
        return
    if isinstance(value, Sequence) and not isinstance(value, str | bytes):
        for index, item in enumerate(value):
            _assert_mechanical(item, path=f"{path}[{index}]")


def append_entry(path: Path, entry: RunLedgerEntry) -> str:
    """Append one canonical JSON line to the ledger and return the line written.

    Append-only: the ledger is evidence, and rewriting evidence defeats the point.
    """
    payload: JsonValue = entry.model_dump(mode="json", exclude_none=True)
    line = dumps_bundle(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(line + "\n")
    return line


def read_entries(path: Path) -> list[dict[str, Any]]:
    """Read every ledger entry, oldest first. A missing ledger reads as empty."""
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.strip():
            entries.append(json.loads(raw))
    return entries
