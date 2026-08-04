# AI-Assisted: Claude Code (model: claude-sonnet-5) - Implemented the real GitHub-backed
# ReleaseApi (task T116) that pipeline.publish.release.publish() drives: create the Release,
# upload the bundle as its asset, and re-download it from the public asset URL for verification
# -- the same Protocol tests already drive with a fake, now with a concrete implementation the
# `publish` workflow job can actually call (FR-045, FR-046, contract §4).
"""The concrete :class:`~pipeline.publish.release.ReleaseApi`, backed by the GitHub REST API.

Deliberately thin. :mod:`pipeline.publish.release` is the module that decides the sequence and
what each step means; this module only knows how to ask GitHub to do the three things that
sequence needs. The workflow's own ``GITHUB_TOKEN`` is the only credential (``contents: write``)
-- no long-lived PAT exists anywhere in this design (FR-046, research D7).

``download_asset`` fetches the **public** ``browser_download_url`` with no auth header, on
purpose: that is the same URL the manifest publishes and the same request a consumer makes, so
the re-download verification step (FR-045) is checking exactly what a player would get, not a
privileged view of it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

import httpx

API_BASE: Final = "https://api.github.com"
DEFAULT_TIMEOUT_SECONDS: Final = 60.0


class GitHubApiError(RuntimeError):
    """A GitHub API call failed. Carries the response body so a CI log is self-explanatory."""


@dataclass(frozen=True, slots=True)
class GitHubReleaseApi:
    """Create a release, upload its asset, and read the asset back — nothing else.

    ``repository`` is ``owner/name``, exactly the form ``GITHUB_REPOSITORY`` is set to inside
    every Actions job. ``token`` is the workflow's own ``GITHUB_TOKEN``.
    """

    repository: str
    token: str
    timeout: float = DEFAULT_TIMEOUT_SECONDS

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def create_release(self, *, tag: str, name: str, commit_sha: str) -> str:
        """Create the release and return its id, as :class:`~pipeline.publish.release.ReleaseApi`
        expects. Encodes the release id and the (templated) upload URL together, since both are
        needed by :meth:`upload_asset` and the Protocol only carries one string between them."""
        with httpx.Client(base_url=API_BASE, timeout=self.timeout) as client:
            response = client.post(
                f"/repos/{self.repository}/releases",
                headers=self._headers(),
                json={
                    "tag_name": tag,
                    "name": name,
                    "target_commitish": commit_sha,
                    "draft": False,
                    "prerelease": False,
                    "generate_release_notes": False,
                },
            )
            if response.status_code >= httpx.codes.BAD_REQUEST:
                raise GitHubApiError(
                    f"creating release {tag!r} failed: {response.status_code} {response.text}"
                )
            body = response.json()
            # `upload_url` is templated (`...{?name,label}`); the release id alone is enough to
            # reconstruct the plain upload endpoint, so only the id is carried forward.
            return str(body["id"])

    def upload_asset(self, *, release_id: str, name: str, payload: bytes) -> str:
        """Upload ``payload`` as the release's asset and return its public download URL."""
        with httpx.Client(base_url="https://uploads.github.com", timeout=self.timeout) as client:
            response = client.post(
                f"/repos/{self.repository}/releases/{release_id}/assets",
                params={"name": name},
                headers={**self._headers(), "Content-Type": "application/json"},
                content=payload,
            )
            if response.status_code >= httpx.codes.BAD_REQUEST:
                raise GitHubApiError(
                    f"uploading asset {name!r} to release {release_id} failed: "
                    f"{response.status_code} {response.text}"
                )
            body = response.json()
            return str(body["browser_download_url"])

    def download_asset(self, *, url: str) -> bytes:
        """Re-fetch the asset from its **public** URL, with no auth header (FR-046).

        This is the verification step (contract §4 step 3): what comes back here is exactly
        what an unauthenticated consumer would receive, which is the point of checking it before
        the manifest is allowed to name it.
        """
        with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
            response = client.get(url)
            if response.status_code >= httpx.codes.BAD_REQUEST:
                raise GitHubApiError(
                    f"re-downloading {url} failed: {response.status_code} {response.text}"
                )
            return response.content
