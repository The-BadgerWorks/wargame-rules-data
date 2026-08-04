# AI-Assisted: Claude Code (model: claude-sonnet-5) - Implemented `rules-pipeline publish`
# (task T116): refuse to run outside the approved CI context, rebuild from the checked-out
# commit, assert the rebuilt bundle's sha256 equals the approved value or exit 51, re-run
# validation and refuse on any blocking finding, and only then hand off to the release and
# Pages steps -- plus the FR-041 pre-flight refusal on an already-published rulesVersionId
# (task T118), since both refusals belong before the first irreversible step for the same
# reason (FR-038, FR-039, FR-041, contract §4).
"""The publish gate: the one function the `publish` workflow job's CLI step calls.

Contract §4 fixes the order. This module owns steps 0-4; step 5 onward (create release, upload
asset, re-download and verify, regenerate the manifest, append the checksum ledger, deploy
Pages) is :func:`pipeline.publish.release.publish`, unchanged from task T071 — this module's job
is only to decide *whether* that sequence may run at all, and to do so before anything
consumer-visible is touched.

0. **Refuse outside the approved CI context** (FR-038). This is not a substitute for the GitHub
   Environment approval — that has already happened, or this function would never have been
   reached, since GitHub does not start the job until a named reviewer approves it in the
   Actions UI. This is the pipeline's own refusal to be run unattended from anywhere else: a
   curator's laptop, a `pull_request` job, or any workflow other than `publish`.
1. **Pre-flight refuse a duplicate `rulesVersionId`** (FR-041, V12) — before the rebuild, so a
   re-run against an already-published version costs nothing.
2. **Rebuild** from the commit the caller has already checked out. This function does not run
   `git checkout` itself — the workflow's `actions/checkout@v4` step with
   `ref: ${{ inputs.commit_sha }}` has already put the working tree there, exactly as `build`
   would find it on a curator's laptop given the same commit — which is what keeps this
   reproducible outside CI (contract §1's "no CI-only code path") even though this gate itself
   is CI-only by design.
3. **Assert the rebuild reproduces the approved bundle** (FR-039, FR-033/SC-006) — one
   assertion, exit `51` on mismatch, nothing written.
4. **Refuse on any blocking finding** the rebuild's own validation raised (FR-029) — exit `30`,
   even for a candidate whose report was clean when it was approved: content can drift between
   approval and dispatch only if the commit itself changed, and a blocking finding on the exact
   approved commit means the finding was already there and unnoticed, not that this check is
   redundant with step 3.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from os import environ as _environ
from pathlib import Path

from pipeline.build.bundle_emit import BundleMeta
from pipeline.build.checksum import checksum
from pipeline.build.manifest import manifest_relative_path, read_manifest
from pipeline.config import PipelineConfig
from pipeline.exit_codes import ExitCode
from pipeline.models.findings import Finding, Severity
from pipeline.publish.pages import ApprovalRecord
from pipeline.publish.release import PublicationRequest, PublicationResult, ReleaseApi
from pipeline.publish.release import publish as publish_release
from pipeline.validate.contract_checks import (
    RESTRICTION_VOCABULARY_VERSION,
    SCHEMA_CONTRACT_VERSION,
)


class OutsideApprovedContextError(RuntimeError):
    """`publish` was invoked somewhere the environment gate does not cover (FR-038)."""


class AlreadyPublishedError(RuntimeError):
    """FR-041 pre-flight: this `rulesVersionId` is already listed in the target manifest."""


@dataclass(frozen=True, slots=True)
class RebuildOutcome:
    """What one rebuild of the approved commit hands the gate.

    Deliberately smaller than :class:`pipeline.cli.BuildResult` — the gate needs the bytes, the
    findings, and the manifest-entry fields, nothing about how they were produced.
    """

    payload: bytes
    findings: Sequence[Finding]
    display_name: str
    edition_codes: Sequence[str]
    published_at: str


@dataclass(frozen=True, slots=True)
class GateOutcome:
    """The publish gate's own verdict — a superset of the exit codes `publish` may return."""

    exit_code: ExitCode
    diagnostic: str | None = None
    result: PublicationResult | None = None


def in_approved_ci_context(env: Mapping[str, str]) -> bool:
    """True only inside the Actions job the `published`/`prerelease` environment gates.

    A curator's own machine, a `pull_request`-triggered run, and every workflow other than
    `publish` fail at least one of these three together. None of them is a security boundary on
    its own — they are ordinary environment variables — which is exactly why the real control is
    the environment approval GitHub already enforced before this job could start; this check
    only stops the accidental or convenience case of running the *command* somewhere that
    approval was never asked for.
    """
    return (
        env.get("GITHUB_ACTIONS") == "true"
        and bool(env.get("GITHUB_JOB"))
        and env.get("GITHUB_WORKFLOW") == "publish"
    )


def blocking_finding_codes(findings: Sequence[Finding]) -> list[str]:
    """The unresolved blocking codes on a rebuild, sorted (FR-029)."""
    return sorted(
        {
            finding.finding_code
            for finding in findings
            if finding.severity is Severity.BLOCKING and not finding.is_suppressed
        }
    )


def run_publish(
    *,
    config: PipelineConfig,
    commit_sha: str,
    expect_sha256: str,
    rules_version_id: str,
    rebuild: Callable[[], RebuildOutcome],
    api: ReleaseApi,
    site_dir: Path,
    state_dir: Path,
    generated_at: str,
    approval: ApprovalRecord | None = None,
    env: Mapping[str, str] | None = None,
    require_ci_context: bool = True,
    deploy: bool = True,
) -> GateOutcome:
    """Run the publish gate end to end, or refuse before anything consumer-visible changes.

    ``require_ci_context`` exists so a test can exercise the sequence below step 0 without
    faking three environment variables in every case, and so the CLI's own ``--dry-run`` (the
    contract's "make no lasting change" global) can reproduce the gate's verdict locally. The
    real, non-dry-run `publish` workflow job never sets it to ``False``.
    """
    environment = _environ if env is None else env
    if require_ci_context and not in_approved_ci_context(environment):
        raise OutsideApprovedContextError(
            "rules-pipeline publish refuses outside the environment-gated `publish` workflow "
            "job (FR-038); the GitHub Environment approval is the real control, this is the "
            "pipeline's own refusal to be run unattended from anywhere else"
        )

    manifest_path = site_dir / manifest_relative_path(config.data_channel)
    manifest = read_manifest(manifest_path)
    if any(
        str(entry.get("rulesVersionId")) == rules_version_id
        for entry in manifest.get("versions", [])
    ):
        raise AlreadyPublishedError(
            f"{rules_version_id} is already listed in {manifest_path.name}; a published "
            "version is never re-published with different content — ship the correction as a "
            "new rulesVersionId (guarantee 1, FR-041)"
        )

    outcome = rebuild()
    built = checksum(outcome.payload)
    if built.sha256 != expect_sha256:
        return GateOutcome(
            exit_code=ExitCode.APPROVAL_MISMATCH,
            diagnostic=(
                f"rebuilt bundle {built.sha256} ({built.size_bytes} bytes) is not the approved "
                f"{expect_sha256}; the approval covered different content, so it does not carry "
                f"to this rebuild (FR-039) — nothing has been written"
            ),
        )

    blocking = blocking_finding_codes(outcome.findings)
    if blocking:
        return GateOutcome(
            exit_code=ExitCode.BLOCKING,
            diagnostic=(
                f"blocking findings on the approved commit: {', '.join(blocking)} (FR-029) — "
                "nothing has been written"
            ),
        )

    meta = BundleMeta(
        rules_version_id=rules_version_id,
        published_at=outcome.published_at,
        source_note=outcome.display_name,
        schema_contract_version=SCHEMA_CONTRACT_VERSION,
        restriction_vocabulary_version=RESTRICTION_VOCABULARY_VERSION,
    )
    request = PublicationRequest(
        meta=meta,
        payload=outcome.payload,
        display_name=outcome.display_name,
        edition_codes=outcome.edition_codes,
        commit_sha=commit_sha,
        expect_sha256=expect_sha256,
        channel=config.data_channel,
        approval=approval,
    )
    result = publish_release(
        request,
        api=api,
        site_dir=site_dir,
        state_dir=state_dir,
        generated_at=generated_at,
        deploy=deploy,
    )
    return GateOutcome(exit_code=ExitCode.SUCCESS, result=result)


__all__ = [
    "AlreadyPublishedError",
    "GateOutcome",
    "OutsideApprovedContextError",
    "RebuildOutcome",
    "blocking_finding_codes",
    "in_approved_ci_context",
    "run_publish",
]
