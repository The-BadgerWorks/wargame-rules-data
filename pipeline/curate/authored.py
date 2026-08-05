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
    CompositionOverrideEntry,
    CopyLimit,
    DetachmentRuleSummary,
    EditionRuleValue,
    FactionMapEntry,
    FactionRuleFile,
    FindingResolution,
    GameSizeBand,
    GlossaryEntry,
    KeywordClassEntry,
    OptionOverrideEntry,
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
    # 004-rules-data-enrichment. The two per-faction trees are handled apart, below.
    "glossary": "glossary",
    "keyword-classes": "keyword-classes",
    "composition-overrides": "composition-overrides",
    "option-overrides": "option-overrides",
}

ABILITIES_DIR: Final = "abilities"
FACTION_RULES_DIR: Final = "faction-rules"
DETACHMENT_RULES_DIR: Final = "detachment-rules"


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
    # -- 004-rules-data-enrichment ---------------------------------------------------------
    # The three summary maps are keyed by `summary_key` (the glossary's is its `keyword_key`,
    # which its own summary_key embeds), exactly as `ability_summaries` is keyed by
    # `ability_key`: the generalised machinery in curate/summaries.py joins on that one field
    # for all four classes rather than learning a per-class key.
    faction_rule_files: Mapping[str, FactionRuleFile] = field(default_factory=dict)
    detachment_rule_summaries: Mapping[str, DetachmentRuleSummary] = field(default_factory=dict)
    glossary_entries: Mapping[str, GlossaryEntry] = field(default_factory=dict)
    keyword_classes: tuple[KeywordClassEntry, ...] = ()
    composition_overrides: tuple[CompositionOverrideEntry, ...] = ()
    option_overrides: tuple[OptionOverrideEntry, ...] = ()

    def faction_for_slug(self, slug: str) -> FactionMapEntry | None:
        return next((entry for entry in self.faction_map if entry.mfm_slug == slug), None)

    def copy_limit_for(self, datasheet_id: str) -> int | None:
        entry = next((c for c in self.copy_limits if c.datasheet_id == datasheet_id), None)
        return entry.max_copies_per_army if entry else None

    def army_rule_state_for(self, faction_id: str) -> str | None:
        """``present``, ``none``, or ``None`` when the faction has no curation file at all.

        The third case is the one worth having a method for: an omitted file means *nobody has
        curated this faction yet*, which FR-021 requires be distinguishable from a curated
        ``"none"``. Returning ``None`` rather than defaulting to ``"none"`` is what keeps that
        distinction alive all the way to the bundle.
        """
        entry = self.faction_rule_files.get(faction_id)
        return entry.army_rule_state if entry is not None else None

    def keyword_class_for(self, keyword: str) -> KeywordClassEntry | None:
        return next((k for k in self.keyword_classes if k.keyword == keyword), None)

    def composition_override_for(
        self, datasheet_id: str, line: int
    ) -> CompositionOverrideEntry | None:
        return next(
            (
                o
                for o in self.composition_overrides
                if o.datasheet_id == datasheet_id and o.line == line
            ),
            None,
        )

    def option_override_for(self, datasheet_id: str, line: int) -> OptionOverrideEntry | None:
        return next(
            (o for o in self.option_overrides if o.datasheet_id == datasheet_id and o.line == line),
            None,
        )


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


def _load_faction_rule_files(curation_dir: Path) -> dict[str, FactionRuleFile]:
    """``curation/faction-rules/<faction-id>.json`` — one object wrapper per faction.

    The **absence** of a file is meaningful here in a way it is not for the other trees: it is
    the "not yet curated" state, distinct from a curated ``army_rule_state: "none"`` (FR-021).
    So this returns only the files that exist, and a caller asking about a faction with no file
    gets ``None`` rather than a default.
    """
    files: dict[str, FactionRuleFile] = {}
    directory = curation_dir / FACTION_RULES_DIR
    if not directory.is_dir():
        return files
    for path in sorted(directory.glob("*.json")):
        payload = _read_json(path)
        if not payload:
            continue
        validate_authored("faction-rules", payload, source=str(path))
        entry = FactionRuleFile.model_validate(payload)
        files[entry.faction_id] = entry
    return files


def _load_detachment_rule_summaries(curation_dir: Path) -> dict[str, DetachmentRuleSummary]:
    """``curation/detachment-rules/<faction-id>.json`` — bare arrays, keyed by ``summary_key``.

    Filed per faction so the ~336-record campaign can advance faction by faction without holding
    a release, and keyed by the rule rather than the detachment because a detachment may own
    more than one.
    """
    summaries: dict[str, DetachmentRuleSummary] = {}
    directory = curation_dir / DETACHMENT_RULES_DIR
    if not directory.is_dir():
        return summaries
    for path in sorted(directory.glob("*.json")):
        payload = _read_json(path)
        if not payload:
            continue
        validate_authored("detachment-rules", payload, source=str(path))
        for record in payload:
            summary = DetachmentRuleSummary.model_validate(record)
            summaries[summary.summary_key] = summary
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
        faction_rule_files=_load_faction_rule_files(curation_dir),
        detachment_rule_summaries=_load_detachment_rule_summaries(curation_dir),
        glossary_entries={
            entry.keyword_key: entry
            for entry in (
                GlossaryEntry.model_validate(r)
                for r in _load_list(curation_dir, "glossary", _FILES["glossary"])
            )
        },
        keyword_classes=tuple(
            KeywordClassEntry.model_validate(r)
            for r in _load_list(curation_dir, "keyword-classes", _FILES["keyword-classes"])
        ),
        composition_overrides=tuple(
            CompositionOverrideEntry.model_validate(r)
            for r in _load_list(
                curation_dir, "composition-overrides", _FILES["composition-overrides"]
            )
        ),
        option_overrides=tuple(
            OptionOverrideEntry.model_validate(r)
            for r in _load_list(curation_dir, "option-overrides", _FILES["option-overrides"])
        ),
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
    # -- 004-rules-data-enrichment. Four new record types join the same check rather than
    # growing a check of their own: an override naming a datasheet, line, faction, or keyword
    # that does not exist is the same defect V9 already catches, and it is exactly what a
    # retired datasheet leaves behind (004 data-model.md §4).
    for faction_id in sorted(content.faction_rule_files):
        refs.append((f"faction-rules/{faction_id}.json", "faction_id", faction_id))
    for detachment_rule in content.detachment_rule_summaries.values():
        refs.append(("detachment-rules/*.json", "detachment_id", detachment_rule.detachment_id))
    for keyword_class in content.keyword_classes:
        if keyword_class.parent_faction_id:
            refs.append(
                ("keyword-classes.json", "parent_faction_id", keyword_class.parent_faction_id)
            )
        if keyword_class.chapter_faction_id:
            refs.append(
                ("keyword-classes.json", "chapter_faction_id", keyword_class.chapter_faction_id)
            )
    for composition_override in content.composition_overrides:
        refs.append(
            ("composition-overrides.json", "datasheet_id", composition_override.datasheet_id)
        )
    for option_override in content.option_overrides:
        refs.append(("option-overrides.json", "datasheet_id", option_override.datasheet_id))
    return refs
