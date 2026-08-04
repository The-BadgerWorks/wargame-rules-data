# AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote the channel-selector tests (task
# T120): WGC_DATA_CHANNEL chooses the Pages path and the release tag prefix and nothing else
# branches on channel name below the CLI entry point, with a test asserting the two channels
# share every code path (FR-047, plan.md's Environment gate).
"""Tests for FR-047: the channel selects a path and a tag prefix, and nothing else.

Two consumer-facing channels exist so pre-release app builds (Dev/Test) and released app builds
(Prod) can point at different manifests without the pipeline running different code for either
one. This suite has two halves: a *static* sweep confirming only the three modules that legitimately
need to know the channel's identity reference it at all, and a *dynamic* run of the same publish
gate on both channels from the same candidate, confirming the observable difference is exactly
the Pages path and the release tag — never a behavioural branch.
"""

from __future__ import annotations

import dataclasses
from pathlib import Path

from pipeline.build.manifest import manifest_relative_path
from pipeline.cli import run_publish_command
from pipeline.config import Channel
from pipeline.exit_codes import ExitCode
from pipeline.publish.release import release_tag

PIPELINE_ROOT = Path(__file__).resolve().parents[2] / "pipeline"

#: The only modules allowed to know a `Channel` member's identity: the config property that
#: picks a manifest path, the manifest module's path table, and the release module's tag prefix.
#: Every other module may carry a `Channel` value around (as `PipelineConfig.data_channel`, or as
#: a `PublicationRequest.channel` field) without ever comparing it to a specific member.
_CHANNEL_BRANCH_ALLOWLIST = {
    PIPELINE_ROOT / "config.py",
    PIPELINE_ROOT / "build" / "manifest.py",
    PIPELINE_ROOT / "publish" / "release.py",
}


def test_only_the_allowlisted_modules_compare_against_a_specific_channel() -> None:
    offenders = []
    for path in sorted(PIPELINE_ROOT.rglob("*.py")):
        if path in _CHANNEL_BRANCH_ALLOWLIST:
            continue
        text = path.read_text(encoding="utf-8")
        if "Channel.PUBLISHED" in text or "Channel.PRERELEASE" in text:
            offenders.append(path.relative_to(PIPELINE_ROOT))
    assert offenders == []


def test_the_manifest_path_is_the_only_pages_difference() -> None:
    assert manifest_relative_path(Channel.PUBLISHED) == "manifest.json"
    assert manifest_relative_path(Channel.PRERELEASE) == "prerelease/manifest.json"


def test_the_release_tag_prefix_is_the_only_release_difference() -> None:
    published = release_tag("mfm-2026-06", Channel.PUBLISHED)
    prerelease = release_tag("mfm-2026-06", Channel.PRERELEASE)
    assert published == "mfm-2026-06"
    assert prerelease != published
    assert "mfm-2026-06" in prerelease


def test_both_channels_run_the_same_publish_gate_and_touch_only_their_own_manifest(
    built_candidate, fake_api, config
) -> None:  # type: ignore[no-untyped-def]
    """One candidate, published twice -- once per channel -- through the exact same function,
    with `--channel` the only input that differs (plus a distinct rulesVersionId, since a real
    version is never republished across channels; the point here is the code path, not the
    business rule against double-publishing one id)."""
    for channel, rules_version_id, manifest_relative in (
        (Channel.PRERELEASE, "candidate-2026-01", "site/prerelease/manifest.json"),
        (Channel.PUBLISHED, "candidate-2026-02", "site/manifest.json"),
    ):
        root, result = built_candidate(rules_version_id)
        channel_config = dataclasses.replace(config, data_channel=channel)

        outcome = run_publish_command(
            config=channel_config,
            commit_sha="deadbeefcafefeed",
            expect_sha256=result.checksum.sha256,
            api=fake_api,
            repository_root=root,
            generated_at="2026-06-13T12:00:00Z",
            require_ci_context=False,
        )

        assert outcome.exit_code == ExitCode.SUCCESS
        assert outcome.result is not None
        assert outcome.result.manifest_path == root / manifest_relative

        other = (
            "site/manifest.json"
            if manifest_relative == "site/prerelease/manifest.json"
            else "site/prerelease/manifest.json"
        )
        untouched = (root / other).read_text(encoding="utf-8")
        assert '"versions": []' in untouched or '"versions":[]' in untouched.replace(" ", "")
