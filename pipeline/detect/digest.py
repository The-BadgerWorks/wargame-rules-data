# AI-Assisted: Claude Code (model: claude-sonnet-5) - Implemented the per-faction and
# whole-release digest (task T105): sha256 over the canonical projection, read from and written
# to state/detection-digest.json, with a candidate raised only when a digest moves (FR-051,
# FR-053, research D4b).
"""Per-faction and whole-release digests over the presentation-free projection.

**The digest is plain, unkeyed sha256.** Research D4b projects a faction page to a structure
that already excludes every presentation detail; keying the hash would add nothing, because
unlike the ability ``mechanic_digest`` (research D6/R8) it is never used as a *substitute* for
retaining publisher wording — the projection retains nothing prose-typed at all, so there is no
verification-oracle risk to close with a key. ``WGC_MECHANIC_DIGEST_KEY`` is a different,
narrower control for a different problem (T147); this module does not use it.

``state/detection-digest.json`` therefore holds one-way hashes only, never source material
(FR-010) — the same argument ``state/README.md`` makes for the file's whole existence.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pipeline.build.canonical_json import JsonValue, dumps_bundle, write_tree_file
from pipeline.detect.projection import project_faction
from pipeline.parse.mfm_dom import MfmPage

#: The state file's path relative to the repository root (``state/README.md``).
DIGEST_STATE_RELATIVE_PATH = "state/detection-digest.json"


@dataclass(frozen=True, slots=True)
class DetectionState:
    """The persisted detection state: one digest per faction, plus a whole-release digest."""

    per_faction: Mapping[str, str] = field(default_factory=dict)
    release_digest: str | None = None

    @staticmethod
    def empty() -> DetectionState:
        """The seeded state (``T011``): no faction has ever been digested."""
        return DetectionState(per_faction={}, release_digest=None)


def digest_json(value: JsonValue) -> str:
    """sha256 over ``value``'s canonical serialisation — the one hash function this module uses."""
    return hashlib.sha256(dumps_bundle(value).encode("utf-8")).hexdigest()


def project_release(pages: Sequence[MfmPage]) -> dict[str, JsonValue]:
    """The presentation-free projection of every page, keyed by faction slug."""
    return {page.faction_slug: project_faction(page) for page in pages}


def load_state(path: Path) -> DetectionState:
    """Read the detection state, or the empty state if the file does not exist yet.

    A ``release_digest`` of JSON ``null`` (the seeded form, T011) and an absent key both read as
    ``None`` — the seed file predates this module having a writer, and canonical JSON omits an
    absent value rather than emitting ``null`` (``curated-snapshot-format.md`` §5), so the two
    forms are treated as the same fact rather than one being a migration this module must run.
    """
    if not path.exists():
        return DetectionState.empty()
    raw: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    per_faction = {str(slug): str(digest) for slug, digest in raw.get("per_faction", {}).items()}
    release_digest = raw.get("release_digest")
    return DetectionState(
        per_faction=per_faction,
        release_digest=str(release_digest) if release_digest is not None else None,
    )


def save_state(path: Path, state: DetectionState) -> bytes:
    """Write the detection state through the canonical serialiser and return the bytes written."""
    body: dict[str, JsonValue] = {"per_faction": dict(sorted(state.per_faction.items()))}
    if state.release_digest is not None:
        body["release_digest"] = state.release_digest
    return write_tree_file(path, body)


@dataclass(frozen=True, slots=True)
class DigestComparison:
    """The result of comparing a fresh sweep's digests against the prior state."""

    new_state: DetectionState
    changed_factions: tuple[str, ...]
    """Every faction slug whose digest differs from the prior state — added, removed, or moved.

    Sorted, so a diagnostic naming them is itself deterministic.
    """

    @property
    def changed(self) -> bool:
        """Whether anything mechanical moved. Equivalent to ``release_digest`` moving, because
        the release digest is a pure function of the per-faction map."""
        return bool(self.changed_factions)


def compare(pages: Sequence[MfmPage], prior: DetectionState) -> DigestComparison:
    """Digest a fresh sweep and compare it against ``prior``.

    A faction is "changed" if its digest differs from the prior state in either direction,
    including a faction the sweep no longer lists (removed) or lists for the first time (added)
    — either is exactly as reportable as a moved price, and neither may be silently absorbed
    into "no candidate" (FR-051).
    """
    projections = project_release(pages)
    new_per_faction = {slug: digest_json(proj) for slug, proj in projections.items()}

    all_slugs = set(prior.per_faction) | set(new_per_faction)
    changed = tuple(
        sorted(
            slug for slug in all_slugs if prior.per_faction.get(slug) != new_per_faction.get(slug)
        )
    )

    release_digest = digest_json(new_per_faction)
    return DigestComparison(
        new_state=DetectionState(per_faction=new_per_faction, release_digest=release_digest),
        changed_factions=changed,
    )
