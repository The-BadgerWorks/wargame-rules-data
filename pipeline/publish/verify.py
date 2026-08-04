# AI-Assisted: Claude Code (model: claude-sonnet-5) - Implemented `rules-pipeline verify`
# (task T143): re-fetch every published `fileUrl` and assert its sha256 still matches
# `state/published-checksums.json`, so "we promise not to edit a release asset" becomes a
# monitored control rather than a promise (SC-007, SC-009).
"""Re-verify every published version's checksum against its recorded value.

`state/published-checksums.json` (T140) is the ledger; this module is what turns it from a
write-only record into a control. `.github/workflows/integrity.yml` (T144) runs this daily, so a
silently replaced release asset is a detected incident within a day rather than a mispriced army
nobody can explain.

Deliberately read-only and manifest-independent: this checks the **assets**, not the manifest.
It re-downloads exactly what a consumer would download — the same public, unauthenticated
`fileUrl`, with no auth header — and compares the bytes' sha256 against what was recorded at
publication time. It writes nothing but its own ledger line.

**Exit-code mapping**, chosen from the contract's fixed stable set
(`contracts/pipeline-run-interface.md` §2) rather than inventing a new code for this command: a
checksum that no longer matches is the same class of fact `50` already names for a rebuild — the
artifact and its recorded checksum have diverged — and an asset that cannot be fetched at all is
the same class of fact `40` already names for a source that refuses or is unreachable. Neither
code touches a published artifact, which both hold for `verify` too: this command never writes
`site/` or a Release, only the ledger.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from pipeline.build.canonical_json import JsonValue
from pipeline.build.checksum import checksum
from pipeline.exit_codes import ExitCode
from pipeline.publish.pages import read_published_checksums


class AssetDownloader(Protocol):
    """The one operation `verify` needs. `pipeline.publish.github_api.GitHubReleaseApi` and the
    test suite's `FakeReleaseApi` both already satisfy this — no new implementation is needed,
    only this narrower view of the same capability `pipeline.publish.release.ReleaseApi`
    exposes, since `verify` has no business creating a release or uploading an asset."""

    def download_asset(self, *, url: str) -> bytes:
        """Fetch the asset from its public URL, exactly as a consumer would."""


@dataclass(frozen=True, slots=True)
class VerificationResult:
    """The outcome of re-checking one published version's recorded checksum."""

    rules_version_id: str
    file_url: str
    expected_sha256: str
    actual_sha256: str | None
    matched: bool
    error: str | None = None


def verify_one(entry: Mapping[str, JsonValue], *, api: AssetDownloader) -> VerificationResult:
    """Re-fetch and re-hash one ledger entry's asset."""
    rules_version_id = str(entry["rulesVersionId"])
    file_url = str(entry["fileUrl"])
    expected = str(entry["sha256"])
    try:
        payload = api.download_asset(url=file_url)
    except Exception as exc:  # noqa: BLE001 - any transport failure is "unreachable" alike
        return VerificationResult(
            rules_version_id=rules_version_id,
            file_url=file_url,
            expected_sha256=expected,
            actual_sha256=None,
            matched=False,
            error=f"{type(exc).__name__}: {exc}",
        )
    actual = checksum(payload).sha256
    return VerificationResult(
        rules_version_id=rules_version_id,
        file_url=file_url,
        expected_sha256=expected,
        actual_sha256=actual,
        matched=actual == expected,
    )


def verify_all(
    entries: Sequence[Mapping[str, JsonValue]], *, api: AssetDownloader
) -> list[VerificationResult]:
    """Re-verify every ledger entry, in the order the ledger lists them."""
    return [verify_one(entry, api=api) for entry in entries]


@dataclass(frozen=True, slots=True)
class VerifyOutcome:
    """What one `verify` sweep produced."""

    exit_code: ExitCode
    results: tuple[VerificationResult, ...]


def mismatched(results: Sequence[VerificationResult]) -> list[VerificationResult]:
    """Fetched successfully, but the hash moved — the tamper/corruption case."""
    return [result for result in results if not result.matched and result.error is None]


def unreachable(results: Sequence[VerificationResult]) -> list[VerificationResult]:
    """Could not be fetched at all — the availability case."""
    return [result for result in results if result.error is not None]


def run_verify(*, state_dir: Path, api: AssetDownloader) -> VerifyOutcome:
    """Re-verify every recorded checksum and return the verdict (contract §2 mapping above)."""
    entries = read_published_checksums(state_dir / "published-checksums.json")
    results = verify_all(entries, api=api)

    if mismatched(results):
        exit_code = ExitCode.NONDETERMINISTIC
    elif unreachable(results):
        exit_code = ExitCode.SOURCE_UNAVAILABLE
    else:
        exit_code = ExitCode.SUCCESS

    return VerifyOutcome(exit_code=exit_code, results=tuple(results))


__all__ = [
    "AssetDownloader",
    "VerificationResult",
    "VerifyOutcome",
    "mismatched",
    "run_verify",
    "unreachable",
    "verify_all",
    "verify_one",
]
