# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented the deterministic core of the D5
# matching ladder for US1 (needed by the T073 reconcile stage): authored faction mapping, stable
# identity first, faction-scoped normalised exact match with a parent-faction fallback, authored
# aliases, and refusal on ambiguity. Suggestion ranking and the US2 finding set land in T088.
"""Pair the points source's units with the detail source's datasheets, deterministically.

The ladder, and the reason each rung exists (research D5):

**Stage 0 — faction mapping is authored, not derived.** The two taxonomies genuinely disagree:
the points source publishes 30 faction pages while the detail source carries 26 faction ids,
splitting the chapters one way and the titan legions the other. No rule derives one from the
other, so `curation/faction-map.json` states it, and an unmapped slug is **blocking** — the
alternative is a faction silently missing from the snapshot.

**Stage 1 — stable identity first.** `curation/unit-map.json` is consulted before any name is
compared. That is what makes an upstream rename land as a changed display name on an *unchanged*
curated id (FR-015), which in turn is what stops a rename from looking like a removal plus an
addition and breaking every saved army that names the unit.

**Stage 2 — normalised exact match**, scoped to the faction, falling back to the parent faction
for chapter sub-factions because the points source lists a chapter unit the detail source files
under its parent.

**Stage 3 — authored aliases**, for spellings a curator has confirmed once.

**Stage 4 — report, never guess.** *No automatic fuzzy match is ever accepted.* The failure mode
is not a missed match — that is a finding a human resolves once and which then carries forward —
it is a *wrong* match, which is a silently mispriced unit in a player's hands at a tournament.
An ambiguous pair is treated as **no** match and blocks.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

from pipeline.curate.authored import AuthoredContent
from pipeline.models.authored import FactionMapEntry
from pipeline.models.findings import Finding
from pipeline.normalize.names import normalize_name
from pipeline.reconcile.identity import EntityKind, IdRegistry
from pipeline.report.catalogue import build_finding


@dataclass(frozen=True, slots=True)
class FactionScope:
    """One curated faction, with the detail-source faction ids that may supply its datasheets."""

    faction_id: str
    entry: FactionMapEntry
    detail_faction_ids: tuple[str, ...]
    """The faction's own detail id first, then its ancestors' — the parent fallback (C3/R6)."""


@dataclass(frozen=True, slots=True)
class UnitMatch:
    """One resolved pairing. ``wahapedia_datasheet_id`` is ``None`` when only points exist."""

    datasheet_id: str
    faction_id: str
    display_name: str
    wahapedia_datasheet_id: str | None
    stage: str
    """Which rung resolved it: ``identity`` | ``exact`` | ``alias`` | ``unmatched``."""


@dataclass(slots=True)
class MatchOutcome:
    scopes: list[FactionScope] = field(default_factory=list)
    matches: list[UnitMatch] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)


def resolve_factions(slugs: Sequence[str], authored: AuthoredContent) -> MatchOutcome:
    """Stage 0. Map every points-source slug to a curated faction, or block.

    Also reports a detail-source faction id that no mapping references — advisory, because a
    faction the points source does not publish is not a faction a player can field, but it is
    worth an approver knowing about.
    """
    outcome = MatchOutcome()
    by_faction = {entry.faction_id: entry for entry in authored.faction_map}

    for slug in sorted(slugs):
        entry = authored.faction_for_slug(slug)
        if entry is None:
            outcome.findings.append(
                build_finding(
                    "REC-FACTION-UNMAPPED",
                    entity_refs=[f"mfm:{slug}"],
                    detail={"mfm_slug": slug},
                )
            )
            continue

        detail_ids = [entry.detail_source_faction_id]
        ancestor = entry.parent_faction_id
        seen = {entry.faction_id}
        while ancestor and ancestor not in seen:
            seen.add(ancestor)
            parent = by_faction.get(ancestor)
            if parent is None:
                break
            if parent.detail_source_faction_id not in detail_ids:
                detail_ids.append(parent.detail_source_faction_id)
            ancestor = parent.parent_faction_id

        outcome.scopes.append(
            FactionScope(
                faction_id=entry.faction_id, entry=entry, detail_faction_ids=tuple(detail_ids)
            )
        )

    return outcome


def report_orphan_detail_factions(
    detail_faction_ids: Sequence[str], authored: AuthoredContent
) -> list[Finding]:
    """A detail-source faction id no mapping references. Advisory (C3/R6)."""
    referenced = {entry.detail_source_faction_id for entry in authored.faction_map}
    return [
        build_finding(
            "REC-DETAIL-FACTION-ORPHAN",
            entity_refs=[f"wahapedia:{faction_id}"],
            detail={"detail_source_faction_id": faction_id},
        )
        for faction_id in sorted(set(detail_faction_ids) - referenced)
    ]


def match_units(
    scope: FactionScope,
    *,
    display_names: Sequence[str],
    detail_names: Mapping[str, str],
    detail_is_legends: Mapping[str, bool],
    authored: AuthoredContent,
    registry: IdRegistry,
) -> MatchOutcome:
    """Run stages 1-4 for one faction.

    Args:
        display_names: the points source's unit names for this faction, as published.
        detail_names: detail-source ``datasheet_id -> display name`` in scope (own + ancestors).
        detail_is_legends: the Legends flag per detail datasheet id, consulted **before** the
            name, so two datasheets differing only by Legends never collide.
    """
    outcome = MatchOutcome()

    by_normalised: dict[str, list[str]] = {}
    for candidate_id, candidate_name in detail_names.items():
        by_normalised.setdefault(normalize_name(candidate_name), []).append(candidate_id)

    # Stage 1's index. The authored map is authoritative on its own — the id registry is
    # consulted only when an id has to be *issued*, which by definition is not this case.
    identity_by_name = {entry.mfm_display_name: entry for entry in authored.unit_map}
    aliases = {
        normalize_name(alias.alias): alias.datasheet_id
        for alias in authored.unit_aliases
        if alias.faction_id == scope.faction_id
    }

    for display_name in sorted(set(display_names)):
        normalised = normalize_name(display_name)

        # Stage 1 — stable identity, consulted before any name comparison.
        mapped = identity_by_name.get(display_name)
        if mapped is not None:
            registry.adopt(EntityKind.DATASHEET, normalised, mapped.datasheet_id)
            outcome.matches.append(
                UnitMatch(
                    datasheet_id=mapped.datasheet_id,
                    faction_id=scope.faction_id,
                    display_name=display_name,
                    wahapedia_datasheet_id=mapped.wahapedia_datasheet_id or None,
                    stage="identity",
                )
            )
            continue

        candidates = by_normalised.get(normalised, [])

        # Legends disambiguation happens before the name is trusted to be unique (D5).
        if len(candidates) > 1:
            non_legends = [c for c in candidates if not detail_is_legends.get(c, False)]
            if len(non_legends) == 1:
                candidates = non_legends

        if len(candidates) > 1:
            outcome.findings.append(
                build_finding(
                    "REC-AMBIGUOUS-MATCH",
                    entity_refs=[f"mfm:{scope.entry.mfm_slug}/{normalised}"],
                    detail={
                        "faction_id": scope.faction_id,
                        "normalized_name": normalised,
                        "candidate_count": len(candidates),
                        "candidates": sorted(candidates),
                    },
                )
            )
            continue

        # Stage 3 — authored aliases, after the exact attempt and before giving up.
        alias_target = aliases.get(normalised)

        detail_id: str | None = None
        if candidates:
            datasheet_id = registry.mint(EntityKind.DATASHEET, normalised, display_name)
            stage = "exact"
            detail_id = candidates[0]
        elif alias_target is not None:
            datasheet_id = alias_target
            registry.adopt(EntityKind.DATASHEET, normalised, alias_target)
            stage = "alias"
            detail_id = next((d for d, name in detail_names.items() if name == display_name), None)
        else:
            # Stage 4 — reported, never guessed. Priced but with no detail: it still ships, on
            # the points the publisher gave it (FR-026, FR-035).
            datasheet_id = registry.mint(EntityKind.DATASHEET, normalised, display_name)
            stage = "unmatched"
            detail_id = None
            outcome.findings.append(
                build_finding(
                    "REC-UNMATCHED-POINTS-ONLY",
                    entity_refs=[f"mfm:{scope.entry.mfm_slug}/{normalised}"],
                    detail={"faction_id": scope.faction_id, "normalized_name": normalised},
                )
            )

        outcome.matches.append(
            UnitMatch(
                datasheet_id=datasheet_id,
                faction_id=scope.faction_id,
                display_name=display_name,
                wahapedia_datasheet_id=detail_id,
                stage=stage,
            )
        )

    return outcome
