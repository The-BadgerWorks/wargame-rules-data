# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented authored-content loading (task
# T064): every file under curation/ is schema-validated on read, exposed read-only, and the
# package asserts at process level that no code path opens a curation/ file for writing.
"""Load `curation/` — the authored tree — and expose it read-only.

Every file is validated against its schema **on read**, so a hand-edited file fails fast with a
path and a message rather than producing a snapshot with a quietly wrong band or a summary that
is not really approved.

The write guard is the interesting part. The `data/` ↔ `curation/` boundary is what makes
carry-forward structural: a rebuild rewrites `data/` wholesale and cannot touch an authored
summary, so an approved summary survives every rebuild without anyone remembering to preserve
it (FR-017, FR-024). CI enforces the boundary from the outside on a diff; this module enforces
it from the inside, at the moment a path is opened, so a bug cannot get as far as a diff.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

from pipeline.models.authored import (
    AbilitySummary,
    CopyLimit,
    EditionRuleValue,
    FactionMapEntry,
    FindingResolution,
    GameSizeBand,
    RestrictionAuthoring,
    UnitAlias,
    UnitMapEntry,
)
from pipeline.schema_validation import validate_authored

#: file stem -> schema kind, for the flat files. `abilities/` is per faction and handled apart.
_FILES: Final[Mapping[str, str]] = {
    "faction-map": "faction-map",
    "unit-map": "unit-map",
    "unit-aliases": "unit-aliases",
    "game-sizes": "game-sizes",
    "edition-rules": "edition-rules",
    "copy-limits": "copy-limits",
    "detachment-restrictions": "detachment-restrictions",
    "resolutions": "resolutions",
}

ABILITIES_DIR: Final = "abilities"


class AuthoredWriteAttempt(RuntimeError):
    """Something tried to write under ``curation/``.

    Raised rather than logged. The invariant is not "we try not to write there" — it is that the
    pipeline *cannot*, which is what lets FR-017 be stated as a guarantee to a curator whose
    week of authoring work is on the other side of it.
    """


def assert_not_authored(path: Path, curation_dir: Path) -> Path:
    """Return ``path``, or raise if it lies under ``curation_dir``.

    Every write in the pipeline that takes a caller-supplied path goes through here.
    """
    try:
        path.resolve().relative_to(curation_dir.resolve())
    except ValueError:
        return path
    raise AuthoredWriteAttempt(
        f"the pipeline may not write under curation/: refusing to open {path}. "
        "Humans write curation/, the pipeline writes data/, and CI enforces both directions."
    )


@dataclass(frozen=True, slots=True)
class AuthoredContent:
    """Everything under ``curation/``, validated and indexed. Read-only by construction."""

    faction_map: tuple[FactionMapEntry, ...] = ()
    unit_map: tuple[UnitMapEntry, ...] = ()
    unit_aliases: tuple[UnitAlias, ...] = ()
    game_sizes: tuple[GameSizeBand, ...] = ()
    edition_rules: tuple[EditionRuleValue, ...] = ()
    copy_limits: tuple[CopyLimit, ...] = ()
    restrictions: tuple[RestrictionAuthoring, ...] = ()
    resolutions: tuple[FindingResolution, ...] = ()
    ability_summaries: Mapping[str, AbilitySummary] = field(default_factory=dict)

    def faction_for_slug(self, slug: str) -> FactionMapEntry | None:
        return next((entry for entry in self.faction_map if entry.mfm_slug == slug), None)

    def copy_limit_for(self, datasheet_id: str) -> int | None:
        entry = next((c for c in self.copy_limits if c.datasheet_id == datasheet_id), None)
        return entry.max_copies_per_army if entry else None


def _read_json(path: Path) -> Any:
    if not path.is_file():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: not valid JSON — {exc.msg} at line {exc.lineno}") from exc


def _load_list(curation_dir: Path, stem: str, kind: str) -> list[Any]:
    path = curation_dir / f"{stem}.json"
    payload = _read_json(path)
    if not payload:
        return []
    validate_authored(kind, payload, source=str(path))
    return list(payload)


def _load_ability_summaries(curation_dir: Path) -> dict[str, AbilitySummary]:
    """One file per faction, keyed per **ability**, not per binding (data-model.md §4).

    Keying per binding would multiply the dominant editorial cost of release 1 by roughly an
    order of magnitude for no editorial benefit — the export carries thousands of `Core` and
    `Faction` bindings over a far smaller distinct set. The builder expands keys to
    per-datasheet rows at snapshot time, which is what satisfies the contract's `NOT NULL`
    per-datasheet summary.
    """
    summaries: dict[str, AbilitySummary] = {}
    directory = curation_dir / ABILITIES_DIR
    if not directory.is_dir():
        return summaries
    for path in sorted(directory.glob("*.json")):
        payload = _read_json(path)
        if not payload:
            continue
        validate_authored("abilities", payload, source=str(path))
        for record in payload:
            summary = AbilitySummary.model_validate(record)
            summaries[summary.ability_key] = summary
    return summaries


def load_authored(curation_dir: Path) -> AuthoredContent:
    """Load and validate the whole authored tree.

    A missing file reads as empty rather than as an error: a repository at the start of its
    first release legitimately has no aliases and no resolutions, and making that a failure
    would mean seeding files whose only content is `[]`.
    """
    return AuthoredContent(
        faction_map=tuple(
            FactionMapEntry.model_validate(r)
            for r in _load_list(curation_dir, "faction-map", _FILES["faction-map"])
        ),
        unit_map=tuple(
            UnitMapEntry.model_validate(r)
            for r in _load_list(curation_dir, "unit-map", _FILES["unit-map"])
        ),
        unit_aliases=tuple(
            UnitAlias.model_validate(r)
            for r in _load_list(curation_dir, "unit-aliases", _FILES["unit-aliases"])
        ),
        game_sizes=tuple(
            GameSizeBand.model_validate(r)
            for r in _load_list(curation_dir, "game-sizes", _FILES["game-sizes"])
        ),
        edition_rules=tuple(
            EditionRuleValue.model_validate(r)
            for r in _load_list(curation_dir, "edition-rules", _FILES["edition-rules"])
        ),
        copy_limits=tuple(
            CopyLimit.model_validate(r)
            for r in _load_list(curation_dir, "copy-limits", _FILES["copy-limits"])
        ),
        restrictions=tuple(
            RestrictionAuthoring.model_validate(r)
            for r in _load_list(
                curation_dir, "detachment-restrictions", _FILES["detachment-restrictions"]
            )
        ),
        resolutions=tuple(
            FindingResolution.model_validate(r)
            for r in _load_list(curation_dir, "resolutions", _FILES["resolutions"])
        ),
        ability_summaries=_load_ability_summaries(curation_dir),
    )


def authored_entity_refs(content: AuthoredContent) -> Sequence[tuple[str, str, str]]:
    """Every ``(file, field, referenced id)`` an authored record points at.

    Consumed by validation V9: an authored record naming an entity that curated data does not
    contain is the blocking ``AUT-DANGLING-REF``, which is what catches a copy limit or a
    restriction left behind by a retired datasheet (FR-018).
    """
    refs: list[tuple[str, str, str]] = []
    for entry in content.faction_map:
        refs.append(("faction-map.json", "faction_id", entry.faction_id))
        if entry.parent_faction_id:
            refs.append(("faction-map.json", "parent_faction_id", entry.parent_faction_id))
    for unit in content.unit_map:
        refs.append(("unit-map.json", "datasheet_id", unit.datasheet_id))
    for alias in content.unit_aliases:
        refs.append(("unit-aliases.json", "datasheet_id", alias.datasheet_id))
        refs.append(("unit-aliases.json", "faction_id", alias.faction_id))
    for limit in content.copy_limits:
        refs.append(("copy-limits.json", "datasheet_id", limit.datasheet_id))
    for restriction in content.restrictions:
        if restriction.detachment_id:
            refs.append(
                ("detachment-restrictions.json", "detachment_id", restriction.detachment_id)
            )
    return refs
