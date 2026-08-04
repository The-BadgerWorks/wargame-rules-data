# AI-Assisted: Claude Code (model: claude-sonnet-5) - Shared fixtures for the US6 retention,
# immutability, withdrawal, and atomicity test suite (T135-T138): a throwaway two-channel
# repository root, a `ReleaseApi` fake that never leaves the process, and a `publish_version`
# helper that publishes one fixture-minimal build into an existing root -- mirroring
# tests/approval/conftest.py's pattern (`FakeReleaseApi`, `channel_repo`) so these tests drive
# the exact functions `publish.yml` and `withdraw.yml` call, offline, and can accumulate several
# published versions in one repository root the way a real one does release over release.
"""Shared fixtures for `tests/publication/` — no test here ever touches a real Release."""

from __future__ import annotations

import json
import shutil
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from pipeline.cli import BuildResult, run_build, run_publish_command
from pipeline.config import PipelineConfig, load_config
from pipeline.publish.gate import GateOutcome

FIXTURES_ROOT = Path(__file__).resolve().parents[2] / "fixtures"
EMPTY_MANIFEST = {"manifestVersion": 1, "generatedAt": "1970-01-01T00:00:00Z", "versions": []}


@dataclass
class FakeReleaseApi:
    """A :class:`~pipeline.publish.release.ReleaseApi` that lives entirely in memory.

    Every test in this suite exercises the real publication sequence — create, upload,
    re-download — against this instead of GitHub, which is what lets "publish three versions and
    withdraw one" be an ordinary, fast, offline assertion.
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
            self.corrupt_next_download = False
            return self.released[url] + b"\x00"
        return self.released[url]


@pytest.fixture
def fake_api() -> FakeReleaseApi:
    return FakeReleaseApi()


@pytest.fixture
def config() -> PipelineConfig:
    return load_config(env={})


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
        # The publish gate's rebuild re-validates from `root/curation` (matching a real CI
        # checkout, where the repository's own `curation/` at the approved commit is what
        # `git checkout` puts there), not from the fixture set's own `curation/` — see
        # `tests/approval/conftest.py`'s identical comment for why.
        shutil.copytree(
            FIXTURES_ROOT / "minimal" / "curation", root / "curation", dirs_exist_ok=True
        )
        return root

    return _make


@pytest.fixture
def publish_version(
    fake_api: FakeReleaseApi, config: PipelineConfig
) -> Callable[[Path, str, str], tuple[BuildResult, GateOutcome]]:
    """Build one `fixtures/minimal` version and publish it into an existing `channel_repo` root.

    Calling this more than once against the same root accumulates manifest entries the way a
    real repository accumulates published versions release over release, which is the shape
    every retention, immutability, and withdrawal test needs (FR-041, FR-043).
    """

    def _publish(root: Path, rules_version_id: str, moment: str) -> tuple[BuildResult, GateOutcome]:
        result = run_build(
            config=config,
            rules_version_id=rules_version_id,
            fixtures_dir=FIXTURES_ROOT / "minimal",
            output_root=root,
            repository_root=root,
            published_at=moment,
        )
        outcome = run_publish_command(
            config=config,
            commit_sha=f"sha-{rules_version_id}",
            expect_sha256=result.checksum.sha256,
            api=fake_api,
            repository_root=root,
            generated_at=moment,
            require_ci_context=False,
        )
        assert outcome.exit_code.value < 30, (
            f"publishing {rules_version_id} did not succeed: {outcome.diagnostic}"
        )
        # `run_build` leaves the rebuilt bundle on disk at the repository root
        # (`_discover_rebuilt_bundle`'s contract, contract §4 step 2). Clearing it here is what
        # lets this fixture publish a second version into the same root without that glob
        # finding two candidates the next time it is called.
        (root / f"rules-{rules_version_id}.json").unlink(missing_ok=True)
        return result, outcome

    return _publish
