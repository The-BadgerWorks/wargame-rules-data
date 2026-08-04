# AI-Assisted: Claude Code (model: claude-sonnet-5) - Shared fixtures for the approval-gate
# test suite (tasks T112-T115, T120): a throwaway two-channel repository root, a built candidate
# from `fixtures/minimal` ready to publish, and a `ReleaseApi` fake that never leaves the
# process, so every approval test runs offline like the rest of the suite (US4).
"""Shared fixtures for `tests/approval/` — no candidate here ever touches a real Release."""

from __future__ import annotations

import json
import shutil
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from pipeline.cli import BuildResult, run_build
from pipeline.config import PipelineConfig, load_config

FIXTURES_ROOT = Path(__file__).resolve().parents[2] / "fixtures"
EMPTY_MANIFEST = {"manifestVersion": 1, "generatedAt": "1970-01-01T00:00:00Z", "versions": []}


@dataclass
class FakeReleaseApi:
    """A :class:`~pipeline.publish.release.ReleaseApi` that lives entirely in memory.

    Every approval test exercises the real publication sequence — create, upload, re-download —
    against this instead of GitHub, which is what lets "reject a candidate" and "approve a
    candidate" both be ordinary, fast, offline assertions.
    """

    released: dict[str, bytes] = field(default_factory=dict)
    create_calls: list[tuple[str, str, str]] = field(default_factory=list)
    upload_calls: list[tuple[str, str]] = field(default_factory=list)
    download_calls: list[str] = field(default_factory=list)
    corrupt_next_download: bool = False

    def create_release(self, *, tag: str, name: str, commit_sha: str) -> str:
        self.create_calls.append((tag, name, commit_sha))
        return f"release-{tag}"

    def upload_asset(self, *, release_id: str, name: str, payload: bytes) -> str:
        self.upload_calls.append((release_id, name))
        url = f"https://example.invalid/releases/{release_id}/{name}"
        self.released[url] = payload
        return url

    def download_asset(self, *, url: str) -> bytes:
        self.download_calls.append(url)
        if self.corrupt_next_download:
            return self.released[url] + b"\x00"
        return self.released[url]


@pytest.fixture
def fake_api() -> FakeReleaseApi:
    return FakeReleaseApi()


@pytest.fixture
def channel_repo(tmp_path: Path) -> Callable[[str], Path]:
    """A throwaway repository root with both channel manifests seeded empty, like a real clone."""

    def _make(name: str = "repo") -> Path:
        root = tmp_path / name
        for relative in (
            "data/wh40k-11e/factions",
            "curation/abilities",
            "reports",
            "state",
            "site/prerelease",
            "work",
        ):
            (root / relative).mkdir(parents=True, exist_ok=True)
        (root / "site" / "manifest.json").write_text(json.dumps(EMPTY_MANIFEST), encoding="utf-8")
        (root / "site" / "prerelease" / "manifest.json").write_text(
            json.dumps(EMPTY_MANIFEST), encoding="utf-8"
        )
        (root / "state" / "published-checksums.json").write_text("[]", encoding="utf-8")
        return root

    return _make


@pytest.fixture
def config() -> PipelineConfig:
    return load_config(env={})


@pytest.fixture
def built_candidate(
    channel_repo: Callable[[str], Path], config: PipelineConfig
) -> Callable[[str], tuple[Path, BuildResult]]:
    """Build `fixtures/minimal` into a fresh repository root: one candidate, ready to publish.

    This is deliberately the same builder US1 uses (`rules-pipeline build`) against the same
    synthetic fixture set, so an approval test is exercising the real build-to-publish seam
    rather than a shortcut invented for the test.
    """

    def _build(rules_version_id: str = "candidate-2026-01") -> tuple[Path, BuildResult]:
        root = channel_repo(rules_version_id)
        # The publish gate's rebuild re-validates from `root/curation` (matching a real CI
        # checkout, where the repository's own `curation/` at the approved commit is what
        # `git checkout` puts there) rather than from `fixtures_dir`. Mirror that here: without
        # this, the rebuild would see an empty `curation/abilities/` and every ability the
        # fixture uses would be reported `SUM-MISSING`, which is not what the approved commit
        # actually holds.
        shutil.copytree(
            FIXTURES_ROOT / "minimal" / "curation", root / "curation", dirs_exist_ok=True
        )
        result = run_build(
            config=config,
            rules_version_id=rules_version_id,
            fixtures_dir=FIXTURES_ROOT / "minimal",
            output_root=root,
            repository_root=root,
        )
        return root, result

    return _build
