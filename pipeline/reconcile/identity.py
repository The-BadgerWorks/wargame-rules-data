# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented curated id minting and the id
# registry (task T039): prefixed slugs of the first-seen name plus a disambiguator, the
# never-reuse rule, and the registry read from curation/unit-map.json and
# curation/faction-map.json (FR-014, FR-015, research D5 stage 1).
"""Curated identity.

Curated ids are the pipeline's own, and they are the reason a rename is a rename rather than a
deletion plus an insertion (FR-015). Three rules, all of which the registry enforces:

1. **Minted once, from the first-seen name.** An id is a slug of the name the entity carried
   the first time we saw it, plus a numeric disambiguator when that slug is taken. Later
   renames do not change it — the *display name* changes and the id does not, which is what
   makes a saved army resolve across a rename.
2. **Never re-derived.** A key already in the registry returns its existing id without
   consulting a name at all. This is D5 stage 1, and it runs before any name comparison.
3. **Never reused.** Retiring an entity releases the *key*, not the id: the id stays reserved
   forever, so a later entity with the same name gets a disambiguated one. Reuse would make a
   player's saved army silently resolve to a different unit (FR-014).

The registry's keys are **upstream** identities — the points source's faction slug, the detail
source's datasheet id — because those are what the pipeline actually re-encounters each run.
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections.abc import Iterable, Mapping
from enum import StrEnum
from pathlib import Path
from typing import Final

_NON_ALNUM: Final = re.compile(r"[^a-z0-9]+")

#: Apostrophes are DROPPED rather than collapsed to a hyphen, so ``T'au`` and ``T’au`` both
#: slug to ``tau`` and the two sources' typographic disagreement cannot produce two ids.
_APOSTROPHES: Final = str.maketrans("", "", "'’‘′`")


class EntityKind(StrEnum):
    """The four curated entity kinds and, through :data:`ID_PREFIXES`, their id prefixes."""

    FACTION = "faction"
    DETACHMENT = "detachment"
    ENHANCEMENT = "enhancement"
    DATASHEET = "datasheet"


#: The id prefixes fixed by ``curated-snapshot-format.md`` §2.
ID_PREFIXES: Final[Mapping[EntityKind, str]] = {
    EntityKind.FACTION: "f",
    EntityKind.DETACHMENT: "d",
    EntityKind.ENHANCEMENT: "e",
    EntityKind.DATASHEET: "ds",
}


class IdentityError(ValueError):
    """An id that cannot be minted, or a registry that contradicts itself."""


def slugify(name: str) -> str:
    """Reduce a display name to an ASCII slug.

    Deliberately lossy and deliberately simple: NFKD, drop combining marks, casefold, collapse
    every run of non-alphanumerics to a single hyphen. It is *not* the D5 matching
    normalisation — this one only has to produce a stable, readable, filename-safe token, and
    collisions are handled by the disambiguator rather than by cleverness here.
    """
    decomposed = unicodedata.normalize("NFKD", name)
    stripped = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    slug = _NON_ALNUM.sub("-", stripped.translate(_APOSTROPHES).casefold()).strip("-")
    if not slug:
        raise IdentityError(f"name {name!r} yields an empty slug; it cannot be minted into an id")
    return slug


class IdRegistry:
    """The mapping from an upstream key to a curated id, plus every id ever issued.

    Args:
        assignments: ``(kind, upstream_key) -> curated_id`` already confirmed.
        reserved: ids that exist but whose key is no longer live — retired entities. They are
            never issued again.
    """

    def __init__(
        self,
        assignments: Mapping[tuple[EntityKind, str], str] | None = None,
        reserved: Iterable[str] = (),
    ) -> None:
        self._assignments: dict[tuple[EntityKind, str], str] = dict(assignments or {})
        self._issued: set[str] = set(self._assignments.values()) | set(reserved)
        self._retired: set[str] = set(reserved)

        if len(set(self._assignments.values())) != len(self._assignments):
            raise IdentityError("registry assigns one curated id to two different upstream keys")

    # -- reads -------------------------------------------------------------------------

    @property
    def issued_ids(self) -> frozenset[str]:
        """Every id ever issued, live or retired. Nothing here may ever be minted again."""
        return frozenset(self._issued)

    @property
    def retired_ids(self) -> frozenset[str]:
        """Ids whose entity is gone. Still reserved forever (FR-014)."""
        return frozenset(self._retired)

    def existing(self, kind: EntityKind, key: str) -> str | None:
        """The curated id already assigned to ``key``, or ``None``."""
        return self._assignments.get((kind, key))

    def is_known(self, kind: EntityKind, key: str) -> bool:
        return (kind, key) in self._assignments

    # -- writes ------------------------------------------------------------------------

    def mint(self, kind: EntityKind, key: str, name: str) -> str:
        """Return ``key``'s curated id, minting one from ``name`` only if it has none.

        Idempotent by construction: calling this every run with a changed ``name`` returns the
        same id, which is precisely the rename behaviour FR-015 requires.
        """
        existing = self._assignments.get((kind, key))
        if existing is not None:
            return existing

        prefix = ID_PREFIXES[kind]
        base = f"{prefix}-{slugify(name)}"
        candidate = base
        suffix = 2
        while candidate in self._issued:
            candidate = f"{base}-{suffix}"
            suffix += 1

        self._assignments[(kind, key)] = candidate
        self._issued.add(candidate)
        return candidate

    def adopt(self, kind: EntityKind, key: str, curated_id: str) -> None:
        """Record an already-decided assignment — used when loading ``curation/``."""
        current = self._assignments.get((kind, key))
        if current is not None and current != curated_id:
            raise IdentityError(
                f"{kind.value} key {key!r} is already assigned {current!r}; refusing to "
                f"reassign it to {curated_id!r} (FR-014)"
            )
        owner = next(
            (k for k, v in self._assignments.items() if v == curated_id and k != (kind, key)),
            None,
        )
        if owner is not None:
            raise IdentityError(
                f"curated id {curated_id!r} is already held by {owner[0].value} key "
                f"{owner[1]!r}; two entities may never share an id (FR-014)"
            )
        self._assignments[(kind, key)] = curated_id
        self._issued.add(curated_id)

    def retire(self, kind: EntityKind, key: str) -> str | None:
        """Release ``key``'s binding while keeping its id reserved forever."""
        curated_id = self._assignments.pop((kind, key), None)
        if curated_id is not None:
            self._retired.add(curated_id)
        return curated_id


def _read_json_list(path: Path) -> list[dict[str, object]]:
    """Read a JSON array of objects; a missing file reads as empty (a first run has none)."""
    if not path.exists():
        return []
    parsed = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(parsed, list):
        raise IdentityError(f"{path} must hold a JSON array")
    return [item for item in parsed if isinstance(item, dict)]


def load_registry(curation_dir: Path) -> IdRegistry:
    """Build the registry from ``curation/faction-map.json`` and ``curation/unit-map.json``.

    Factions are keyed by the points source's slug and datasheets by the detail source's
    datasheet id — the two upstream identities the pipeline re-encounters every run.
    """
    registry = IdRegistry()

    for entry in _read_json_list(curation_dir / "faction-map.json"):
        slug = entry.get("mfm_slug")
        faction_id = entry.get("faction_id")
        if isinstance(slug, str) and isinstance(faction_id, str):
            registry.adopt(EntityKind.FACTION, slug, faction_id)

    for entry in _read_json_list(curation_dir / "unit-map.json"):
        upstream = entry.get("wahapedia_datasheet_id")
        datasheet_id = entry.get("datasheet_id")
        if isinstance(upstream, str) and isinstance(datasheet_id, str):
            registry.adopt(EntityKind.DATASHEET, upstream, datasheet_id)

    return registry
