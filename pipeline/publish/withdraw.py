# AI-Assisted: Claude Code (model: claude-sonnet-5) - Implemented `rules-pipeline withdraw`
# (task T141): set `withdrawn` and `withdrawnReason` on one manifest entry and redeploy Pages,
# with no rebuild and no source access, so it stays fast under pressure (FR-044, contract §4).
"""Withdraw one published version: manifest-only, no rebuild, no source access.

Deliberately the smallest module in `pipeline.publish`. `withdraw.yml` (T142) is not part of the
`publish` job on purpose — a defective release has to be neutralised in under a minute (SC-009),
and a workflow that has to check out a commit, reinstall the package, and rebuild a multi-
thousand-datasheet snapshot before it can flip one flag cannot meet that. This module does
exactly one thing: call :func:`pipeline.build.manifest.withdraw_entry`, then redeploy Pages.

Like `publish`, this refuses outside the workflow job its own GitHub Environment gates
(:func:`pipeline.publish.gate.in_approved_ci_context`, reused with ``workflow="withdraw"``) —
the environment approval is the real control, this is the pipeline's own refusal to be run
unattended from anywhere else.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from os import environ as _environ
from pathlib import Path

from pipeline.build.manifest import ManifestError, manifest_relative_path, withdraw_entry
from pipeline.config import PipelineConfig
from pipeline.exit_codes import ExitCode
from pipeline.publish.gate import OutsideApprovedContextError, in_approved_ci_context
from pipeline.publish.pages import deploy_pages


class WithdrawalError(ValueError):
    """An invocation error: a missing or blank reason. Distinct from :class:`ManifestError`,
    which is the manifest layer's own refusal (unlisted id), so a caller can tell an invocation
    mistake from a data-state refusal apart without inspecting the message."""


@dataclass(frozen=True, slots=True)
class WithdrawOutcome:
    """What one withdrawal produced."""

    exit_code: ExitCode
    manifest_path: Path
    rules_version_id: str


def run_withdraw(
    *,
    config: PipelineConfig,
    rules_version_id: str,
    reason: str,
    site_dir: Path,
    generated_at: str,
    env: Mapping[str, str] | None = None,
    require_ci_context: bool = True,
    deploy: bool = True,
) -> WithdrawOutcome:
    """Mark one manifest entry withdrawn, or refuse before anything is written.

    ``require_ci_context`` and ``deploy`` mirror :func:`pipeline.publish.gate.run_publish`'s own
    parameters, for the same reason: a test drives the sequence without faking environment
    variables, and the CLI's own ``--dry-run`` reproduces the verdict without touching Pages.
    The real `withdraw` workflow job never sets either to anything but the default.
    """
    environment = _environ if env is None else env
    if require_ci_context and not in_approved_ci_context(environment, workflow="withdraw"):
        raise OutsideApprovedContextError(
            "rules-pipeline withdraw refuses outside the environment-gated `withdraw` workflow "
            "job (FR-044); the GitHub Environment approval is the real control, this is the "
            "pipeline's own refusal to be run unattended from anywhere else"
        )
    if not rules_version_id:
        raise WithdrawalError("withdraw requires --rules-version-id")
    if not reason or not reason.strip():
        raise WithdrawalError(
            "withdraw requires --reason: a short factual note a player pinned to this version "
            "can be shown (FR-044)"
        )

    manifest_path = site_dir / manifest_relative_path(config.data_channel)
    withdraw_entry(
        manifest_path,
        rules_version_id=rules_version_id,
        reason=reason,
        generated_at=generated_at,
    )

    if deploy:
        deploy_pages(site_dir)

    return WithdrawOutcome(
        exit_code=ExitCode.SUCCESS,
        manifest_path=manifest_path,
        rules_version_id=rules_version_id,
    )


__all__ = [
    "WithdrawOutcome",
    "WithdrawalError",
    "ManifestError",
    "run_withdraw",
]
