# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the publication sequence (task
# T071) in the strict order create release -> upload asset -> re-download and verify size and
# sha256 -> regenerate the manifest -> append to state/published-checksums.json -> deploy Pages,
# so the manifest never names an unretrievable artifact (FR-045, research D3).
"""Publish one approved candidate, in an order chosen for what an interruption leaves behind.

The sequence is the requirement (contract §4, FR-045):

1. create the Release,
2. upload the bundle as its asset,
3. **re-download the asset and verify its size and sha256**,
4. regenerate the channel's manifest,
5. append to `state/published-checksums.json`,
6. deploy Pages.

Read it by asking what a crash between any two steps leaves. Before step 4 the manifest is
untouched, so consumers see the previous release and at worst an unreferenced asset exists that
nothing points at — invisible. After step 4 the manifest names an artifact that step 3 already
proved retrievable. **At no point does the manifest name something a player cannot download**,
which is the atomicity FR-045 asks for without a transaction.

Step 3 is not paranoia about our own upload. It is the check that turns "we promise the asset
matches the checksum we published" into something a machine verified once and `integrity.yml`
re-verifies daily (SC-007, SC-009).

The API surface is injected rather than imported. This module is the one place a mistake is
irreversible in public, so it is also the one place a test must be able to drive end to end
without a network or a token.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from pipeline.build.bundle_emit import BundleMeta
from pipeline.build.canonical_json import write_bundle
from pipeline.build.checksum import BundleChecksum, assert_reproducible, checksum
from pipeline.build.manifest import manifest_entry, manifest_relative_path, regenerate_manifest
from pipeline.config import Channel
from pipeline.publish.pages import deploy_pages, record_published_checksum


class ReleaseApi(Protocol):
    """The publishing operations, injected so this module can be driven without a network.

    Deliberately minimal: create, upload, download. Anything richer would be an invitation to
    do something else here, and the set of things this module may do is the point of it.
    """

    def create_release(self, *, tag: str, name: str, commit_sha: str) -> str:
        """Create the release and return its id."""

    def upload_asset(self, *, release_id: str, name: str, payload: bytes) -> str:
        """Upload the bundle and return the URL it will be served from."""

    def download_asset(self, *, url: str) -> bytes:
        """Fetch the uploaded asset back, for verification."""


class PublicationError(RuntimeError):
    """A publication step failed its own verification. Nothing consumer-visible was written."""


@dataclass(frozen=True, slots=True)
class PublicationRequest:
    """Everything the publish job needs, resolved before the first irreversible step."""

    meta: BundleMeta
    payload: bytes
    display_name: str
    edition_codes: Sequence[str]
    commit_sha: str
    expect_sha256: str
    channel: Channel = Channel.PRERELEASE


@dataclass(frozen=True, slots=True)
class PublicationResult:
    release_id: str
    file_url: str
    checksum: BundleChecksum
    manifest_path: Path


def bundle_file_name(rules_version_id: str) -> str:
    """The asset's name, and the last path segment of `manifest.fileUrl`."""
    return f"rules-{rules_version_id}.json"


def release_tag(rules_version_id: str, channel: Channel) -> str:
    """The release tag. The channel prefixes it so the two never collide on one repository."""
    return rules_version_id if channel is Channel.PUBLISHED else f"prerelease-{rules_version_id}"


def publish(
    request: PublicationRequest,
    *,
    api: ReleaseApi,
    site_dir: Path,
    state_dir: Path,
    generated_at: str,
    deploy: bool = True,
) -> PublicationResult:
    """Run the publication sequence, or raise before anything consumer-visible changes."""
    # Step 0 — the approval assertion. An approval authorises *content*, not a rebuild
    # (FR-039), so the bytes about to be uploaded must be the bytes that were approved.
    built = assert_reproducible(
        request.payload, expected_sha256=request.expect_sha256, approval=True
    )

    tag = release_tag(request.meta.rules_version_id, request.channel)
    asset_name = bundle_file_name(request.meta.rules_version_id)

    release_id = api.create_release(
        tag=tag, name=request.display_name, commit_sha=request.commit_sha
    )
    file_url = api.upload_asset(release_id=release_id, name=asset_name, payload=request.payload)

    # Step 3 — re-download and verify. Until this passes, the manifest is not touched.
    retrieved = api.download_asset(url=file_url)
    verified = checksum(retrieved)
    if verified != built:
        raise PublicationError(
            f"the uploaded asset does not match what was built: retrieved {verified.sha256} "
            f"({verified.size_bytes} bytes), built {built.sha256} ({built.size_bytes} bytes). "
            "The manifest has not been touched, so consumers still see the previous release."
        )

    entry = manifest_entry(
        meta=request.meta,
        display_name=request.display_name,
        edition_codes=request.edition_codes,
        file_url=file_url,
        checksum=verified,
    )

    manifest_path = site_dir / manifest_relative_path(request.channel)
    regenerate_manifest(manifest_path, entry, generated_at=generated_at)

    record_published_checksum(
        state_dir / "published-checksums.json",
        rules_version_id=request.meta.rules_version_id,
        file_url=file_url,
        checksum=verified,
        published_at=request.meta.published_at,
    )

    if deploy:
        deploy_pages(site_dir)

    return PublicationResult(
        release_id=release_id,
        file_url=file_url,
        checksum=verified,
        manifest_path=manifest_path,
    )


def write_bundle_artifact(path: Path, bundle: object) -> bytes:
    """Write the bundle to disk with the canonical serialiser and return its bytes."""
    return write_bundle(path, bundle)  # type: ignore[arg-type]
