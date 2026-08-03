# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the Pages side of publication
# (task T071): the published-checksum ledger and the Pages deployment marker, both written only
# after the uploaded asset has been re-downloaded and verified (FR-045).
"""The last two steps of publication: record the checksum, then serve the manifest.

`state/published-checksums.json` is what turns "we promise not to edit a release asset" into a
monitored control. `integrity.yml` re-fetches every published `fileUrl` daily and asserts the
sha256 still matches what is recorded here, so a silently replaced asset is a detected incident
rather than a mispriced army nobody can explain (SC-007, SC-009).

It holds hashes and URLs only. That is not an accident of design: a one-way digest of source
material is not source material, which is the same argument that lets
`state/detection-digest.json` be committed at all (FR-010).

Pages deployment is a *marker* written next to the manifest rather than an API call. GitHub
Pages serves whatever is on the branch, so the deployment is the commit the publish workflow
makes; this module's job is to leave the site directory in the state that should be served, and
to record which version it was left in for the run ledger.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Final

from pipeline.build.canonical_json import JsonValue, write_bundle
from pipeline.build.checksum import BundleChecksum

#: Written beside the manifest so an operator can tell, from the served site alone, which run
#: produced what is being served. Never a timestamp of "now" — it carries the version's own
#: `publishedAt`, so the file is a function of its inputs like everything else.
DEPLOYMENT_MARKER: Final = "deployed.json"


class ChecksumLedgerError(RuntimeError):
    """An attempt to record a checksum that contradicts one already recorded.

    A published version is immutable (guarantee 1). Two different checksums for one
    `rulesVersionId` means either a re-publication or a corrupted ledger, and both are incidents.
    """


def read_published_checksums(path: Path) -> list[dict[str, JsonValue]]:
    """The recorded checksums, or the empty list a fresh repository starts from."""
    if not path.is_file():
        return []
    payload: list[dict[str, JsonValue]] = json.loads(path.read_text(encoding="utf-8"))
    return list(payload) if payload else []


def record_published_checksum(
    path: Path,
    *,
    rules_version_id: str,
    file_url: str,
    checksum: BundleChecksum,
    published_at: str,
) -> list[dict[str, JsonValue]]:
    """Append one entry, refusing to contradict an existing one."""
    existing = read_published_checksums(path)

    for entry in existing:
        if entry.get("rulesVersionId") != rules_version_id:
            continue
        if entry.get("sha256") == checksum.sha256:
            return existing
        raise ChecksumLedgerError(
            f"{rules_version_id} is already recorded with a different sha256. A published "
            "version is never re-published with different content — ship the correction as a "
            "new rulesVersionId (guarantee 1)."
        )

    appended: dict[str, JsonValue] = {
        "rulesVersionId": rules_version_id,
        "fileUrl": file_url,
        "sha256": checksum.sha256,
        "sizeBytes": checksum.size_bytes,
        "publishedAt": published_at,
    }
    updated: list[dict[str, JsonValue]] = sorted(
        [*existing, appended], key=lambda entry: str(entry["rulesVersionId"])
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    write_bundle(path, updated)
    return updated


def deploy_pages(site_dir: Path) -> Path:
    """Leave the site directory in the state that should be served, and say so.

    Pages serves the branch, so "deploying" is the commit the publish workflow makes. Writing a
    marker means the served site itself answers "which version is live", which is the first
    question during an incident and the one that is otherwise answered by reading a workflow log.
    """
    marker = site_dir / DEPLOYMENT_MARKER
    manifests = sorted(p.name for p in site_dir.rglob("manifest.json"))
    write_bundle(marker, {"manifests": manifests})
    return marker
