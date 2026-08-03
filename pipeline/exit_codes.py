# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the stable exit-code set of
# contracts/pipeline-run-interface.md §2 (task T017). CI branches on these values and alerting
# maps them to severities, so they are an interface, not an implementation detail.
"""The pipeline's stable exit codes.

Every value here is fixed by ``contracts/pipeline-run-interface.md`` §2. Changing one is a
breaking change to the operator contract: the workflows branch on them and alerting maps them
to severities. ``tests/unit/test_exit_codes.py`` asserts the values never drift.

Exit ``40``, ``41``, ``42``, ``50``, and ``51`` never touch a published artifact.
"""

from __future__ import annotations

from enum import IntEnum


class ExitCode(IntEnum):
    """Stable process exit codes (contract §2)."""

    SUCCESS = 0
    """Success; for ``detect``, **no change**."""

    CHANGE_DETECTED = 10
    """``detect`` only: a mechanical change was detected — trigger a candidate run (FR-051)."""

    ADVISORY_ONLY = 20
    """Advisory findings only; the candidate is publishable pending approval (FR-031)."""

    BLOCKING = 30
    """Blocking findings — publication refused. There is no override flag (FR-029)."""

    SOURCE_UNAVAILABLE = 40
    """A source was unreachable, refused, or throttled; the run stops rather than evading
    (FR-007). The previously published version stays current."""

    SOURCE_STRUCTURE_CHANGED = 41
    """A source's structure changed and values are no longer extractable (FR-008)."""

    COVERAGE_COLLAPSE = 42
    """Coverage fell below the configured proportion of the previous published version
    (FR-009). Do not publish."""

    NONDETERMINISTIC = 50
    """A rebuild produced a bundle with a different checksum (FR-033, SC-006)."""

    APPROVAL_MISMATCH = 51
    """The rebuilt artifact is not the approved artifact; re-approval is required (FR-039)."""

    CONFIG_ERROR = 60
    """Configuration or invocation error — fix the invocation (FR-055 diagnostics)."""


#: The exact set of codes the contract defines. Nothing else may be returned by ``main``.
STABLE_EXIT_CODES: frozenset[int] = frozenset(code.value for code in ExitCode)
