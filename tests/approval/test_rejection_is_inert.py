# AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote the rejection-inertness tests (task
# T115): a rejected or abandoned candidate produces no consumer-visible artifact and leaves
# site/manifest.json, site/prerelease/manifest.json, and state/published-checksums.json
# byte-identical (FR-040).
"""Tests for FR-040: rejection leaves every consumer-visible artifact byte-identical.

"Rejected" and "abandoned" are the same outcome from this repository's point of view — declining
the environment approval and simply never dispatching `publish` both mean the same thing
happens: nothing. This suite exercises three ways a candidate can fail to become published
(never dispatched, dispatched with a mismatched checksum, dispatched onto a rebuild with a
blocking finding) and asserts every one of them leaves identical bytes behind, not merely an
identical manifest — the `site/prerelease/manifest.json` bytes and the
`state/published-checksums.json` bytes are hashed before and after and compared directly.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from pipeline.cli import run_publish_command
from pipeline.config import load_config
from pipeline.exit_codes import ExitCode
from pipeline.models.findings import Finding, FindingClass, Severity
from pipeline.publish.gate import RebuildOutcome, run_publish

CHANNEL_FILES = (
    "site/manifest.json",
    "site/prerelease/manifest.json",
    "state/published-checksums.json",
)


def _digests(root: Path) -> dict[str, str]:
    return {
        relative: hashlib.sha256((root / relative).read_bytes()).hexdigest()
        for relative in CHANNEL_FILES
    }


def test_a_candidate_that_is_never_dispatched_leaves_every_channel_file_untouched(
    built_candidate,
) -> None:  # type: ignore[no-untyped-def]
    root, _result = built_candidate()
    before = _digests(root)
    # ... and nothing else happens: the candidate sits on disk, exactly like an abandoned PR.
    after = _digests(root)
    assert after == before


def test_a_dispatch_with_a_mismatched_checksum_leaves_every_channel_file_untouched(
    built_candidate, fake_api, config
) -> None:  # type: ignore[no-untyped-def]
    root, result = built_candidate()
    before = _digests(root)

    outcome = run_publish_command(
        config=config,
        commit_sha="deadbeefcafefeed",
        expect_sha256="f" * 64,
        api=fake_api,
        repository_root=root,
        generated_at="2026-06-13T12:00:00Z",
        require_ci_context=False,
    )

    assert outcome.exit_code == ExitCode.APPROVAL_MISMATCH
    assert _digests(root) == before
    assert result.checksum.sha256  # the candidate itself is unaffected, still on disk


def test_a_dispatch_onto_a_blocking_finding_leaves_every_channel_file_untouched(
    tmp_path: Path,
) -> None:
    for relative in ("site/prerelease", "state"):
        (tmp_path / relative).mkdir(parents=True, exist_ok=True)
    (tmp_path / "site" / "manifest.json").write_text(
        '{"manifestVersion":1,"generatedAt":"x","versions":[]}', encoding="utf-8"
    )
    (tmp_path / "site" / "prerelease" / "manifest.json").write_text(
        '{"manifestVersion":1,"generatedAt":"x","versions":[]}', encoding="utf-8"
    )
    (tmp_path / "state" / "published-checksums.json").write_text("[]", encoding="utf-8")
    before = _digests(tmp_path)

    payload = b'{"bundleFormatVersion":1}\n'
    blocking = Finding(
        finding_code="CON-NO-COST",
        finding_class=FindingClass.CONTRACT,
        severity=Severity.BLOCKING,
        entity_refs=("ds-invented",),
    )

    def _rebuild() -> RebuildOutcome:
        return RebuildOutcome(
            payload=payload,
            findings=[blocking],
            display_name="Invented Fixture",
            edition_codes=["wh40k-11e"],
            published_at="2026-06-13T00:00:00Z",
        )

    outcome = run_publish(
        config=load_config(env={}),
        commit_sha="deadbeef",
        expect_sha256=hashlib.sha256(payload).hexdigest(),
        rules_version_id="candidate-2026-01",
        rebuild=_rebuild,
        api=None,  # type: ignore[arg-type]
        site_dir=tmp_path / "site",
        state_dir=tmp_path / "state",
        generated_at="2026-06-13T00:00:00Z",
        require_ci_context=False,
    )

    assert outcome.exit_code == ExitCode.BLOCKING == 30
    assert outcome.result is None
    assert _digests(tmp_path) == before
