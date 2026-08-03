# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented bundle checksumming and the
# determinism assertion (task T070): sha256 and size over the bundle bytes, and a rebuild whose
# checksum differs fails with exit 50 (FR-033, SC-006).
"""The sha256 and size the manifest publishes, and the assertion that they are reproducible.

Both numbers are computed over the **bundle bytes** — the artifact the app downloads — and not
over the built SQLite file. The app verifies them before ingestion, so they are the integrity
control against a truncated or tampered download (`rules-data-manifest.md` §4). The locally
built database need only be row-equivalent, because nothing downstream checksums it.

:func:`assert_reproducible` is the same assertion in two different places, which is why it lives
here rather than in either of them: the build uses it to catch a nondeterministic emitter
(exit `50`), and the publish job uses it to refuse content that is not the content a human
approved (exit `51`, FR-039).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from pipeline.exit_codes import ExitCode


class DeterminismError(RuntimeError):
    """A rebuild produced different bytes from the same inputs.

    Blocking, and deliberately loud. If this fires, the manifest checksum has stopped meaning
    "this is that artifact" and every guarantee built on it — integrity verification, the
    approval assertion — is quietly untrue.
    """

    finding_code = "CON-NONDETERMINISTIC"
    exit_code = ExitCode.NONDETERMINISTIC


class ApprovalMismatch(RuntimeError):
    """The rebuilt artifact is not the artifact that was approved (FR-039).

    A different exit code from :class:`DeterminismError` on purpose: this one is not a bug, it
    is a *process* outcome — the content moved after approval, and the fix is to approve the new
    content rather than to investigate the serialiser.
    """

    finding_code = "CON-NONDETERMINISTIC"
    exit_code = ExitCode.APPROVAL_MISMATCH


@dataclass(frozen=True, slots=True)
class BundleChecksum:
    """What the manifest publishes about one bundle."""

    sha256: str
    size_bytes: int


def checksum(payload: bytes) -> BundleChecksum:
    """The sha256 and byte length of a bundle."""
    return BundleChecksum(sha256=hashlib.sha256(payload).hexdigest(), size_bytes=len(payload))


def assert_reproducible(
    payload: bytes, *, expected_sha256: str, approval: bool = False
) -> BundleChecksum:
    """Assert ``payload`` hashes to ``expected_sha256``.

    Args:
        approval: when true this is the publish job's check and a mismatch is
            :class:`ApprovalMismatch` (exit ``51``); otherwise it is the build's own check and a
            mismatch is :class:`DeterminismError` (exit ``50``).

    The message names both checksums and the size, and nothing from inside the bundle — the
    diagnostic for "these bytes are not those bytes" needs no content to be actionable.
    """
    actual = checksum(payload)
    if actual.sha256 == expected_sha256:
        return actual

    failure = ApprovalMismatch if approval else DeterminismError
    raise failure(
        f"bundle checksum mismatch: built {actual.sha256} ({actual.size_bytes} bytes), "
        f"expected {expected_sha256}"
    )
