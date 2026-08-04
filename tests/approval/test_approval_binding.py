# AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote the approval-binding tests (task
# T113): a rebuild whose sha256 differs from --expect-sha256 exits 51 and touches nothing, an
# identical rebuild proceeds, and the same assertion is shown to carry FR-039 and FR-033/SC-006
# together (contract §4 step 3).
"""Tests for FR-039: an approval authorises content, never a rebuild.

One assertion is supposed to deliver two guarantees at once (contract §4): FR-039 (approving a
candidate does not authorise whatever a later rebuild happens to produce) and FR-033/SC-006
(determinism — two builds from the same inputs are byte-identical). This suite drives both
through the same code path, `pipeline.publish.gate.run_publish`, so a change that breaks either
guarantee breaks a test named for it.
"""

from __future__ import annotations

import json

import pytest

from pipeline.cli import run_publish_command
from pipeline.exit_codes import ExitCode
from pipeline.publish.gate import AlreadyPublishedError, blocking_finding_codes


def test_a_checksum_mismatch_exits_51_and_touches_nothing(
    built_candidate, fake_api, config
) -> None:  # type: ignore[no-untyped-def]
    root, result = built_candidate()
    wrong_sha256 = "0" * 64
    assert wrong_sha256 != result.checksum.sha256

    outcome = run_publish_command(
        config=config,
        commit_sha="deadbeefcafefeed",
        expect_sha256=wrong_sha256,
        api=fake_api,
        repository_root=root,
        generated_at="2026-06-13T12:00:00Z",
        require_ci_context=False,
    )

    assert outcome.exit_code == ExitCode.APPROVAL_MISMATCH == 51
    assert outcome.result is None
    assert fake_api.create_calls == []
    assert fake_api.upload_calls == []

    manifest = json.loads((root / "site" / "prerelease" / "manifest.json").read_text())
    assert manifest["versions"] == []
    assert json.loads((root / "state" / "published-checksums.json").read_text()) == []


def test_an_identical_rebuild_proceeds_to_publication(built_candidate, fake_api, config) -> None:  # type: ignore[no-untyped-def]
    root, result = built_candidate()

    outcome = run_publish_command(
        config=config,
        commit_sha="deadbeefcafefeed",
        expect_sha256=result.checksum.sha256,
        api=fake_api,
        repository_root=root,
        generated_at="2026-06-13T12:00:00Z",
        require_ci_context=False,
    )

    assert outcome.exit_code == ExitCode.SUCCESS == 0
    assert outcome.result is not None
    assert outcome.result.checksum.sha256 == result.checksum.sha256
    assert fake_api.create_calls and fake_api.upload_calls

    manifest = json.loads((root / "site" / "prerelease" / "manifest.json").read_text())
    assert [v["rulesVersionId"] for v in manifest["versions"]] == ["candidate-2026-01"]
    assert manifest["versions"][0]["sha256"] == result.checksum.sha256


def test_the_mismatch_message_names_both_the_determinism_and_the_approval_guarantee(
    built_candidate, fake_api, config
) -> None:  # type: ignore[no-untyped-def]
    """The diagnostic is what makes the "one assertion, two guarantees" design legible: a
    reader must be able to tell FR-039 (approval scope) and FR-033 (determinism) are both live
    here without reading the implementation."""
    root, result = built_candidate()
    wrong_sha256 = "f" * 64

    outcome = run_publish_command(
        config=config,
        commit_sha="deadbeefcafefeed",
        expect_sha256=wrong_sha256,
        api=fake_api,
        repository_root=root,
        generated_at="2026-06-13T12:00:00Z",
        require_ci_context=False,
    )

    assert outcome.diagnostic is not None
    assert result.checksum.sha256 in outcome.diagnostic
    assert wrong_sha256 in outcome.diagnostic
    assert "FR-039" in outcome.diagnostic


def test_a_republished_rules_version_id_is_refused_before_any_rebuild(
    built_candidate, fake_api, config
) -> None:  # type: ignore[no-untyped-def]
    """FR-041's pre-flight (T118): the id already listed refuses before step 3 even runs."""
    root, result = built_candidate()
    run_publish_command(
        config=config,
        commit_sha="deadbeefcafefeed",
        expect_sha256=result.checksum.sha256,
        api=fake_api,
        repository_root=root,
        generated_at="2026-06-13T12:00:00Z",
        require_ci_context=False,
    )
    calls_before = len(fake_api.create_calls)

    with pytest.raises(AlreadyPublishedError):
        run_publish_command(
            config=config,
            commit_sha="deadbeefcafefeed",
            expect_sha256=result.checksum.sha256,
            api=fake_api,
            repository_root=root,
            generated_at="2026-06-13T12:01:00Z",
            require_ci_context=False,
        )
    assert len(fake_api.create_calls) == calls_before


def test_blocking_finding_codes_reports_only_unsuppressed_blocking_findings() -> None:
    assert blocking_finding_codes([]) == []
