# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented reading the previous curated tree
# and the previous published version back (task T090), so last-known pricing, rename detection,
# coverage ratios, and the change summary all have a baseline without re-acquiring anything
# (FR-032, FR-035, spec Support implications).
"""The baseline: what we published last time.

Four of US2's guarantees are statements *about a previous release* — last-known pricing, rename
detection, coverage ratios, and the change summary — and none of them may cost a second
acquisition. A support enquiry about a mispriced unit has to be answerable from what is already
in the repository, months later, without touching either upstream source (spec: *Support
implications*).

It already is. The curated tree is committed on `main`, so **a checkout is the read**: the
previous release is the tree as it stood before this run rewrote it, and the previously published
version id is in the channel manifest beside it. There is no separate history store to keep in
step, and nothing here makes a network request.

Two readers live here, and the distinction matters:

* :func:`read_curated_tree` reconstructs a whole :class:`CuratedSnapshot` from the files. That is
  what lets ``validate`` and ``report`` re-run against the existing tree without acquiring — the
  tree is the canonical state, so anything that can be checked at all can be checked from it.
* :class:`PriorSnapshot` is the *projection* of that used for comparison: ids, names, costs, and
  pricing-confidence bookkeeping. Deliberately narrow, because a comparison that reads every
  field would report every field.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pipeline.models.curated import (
    CuratedDatasheet,
    CuratedDatasheetCost,
    CuratedDetachment,
    CuratedDetachmentRestriction,
    CuratedEdition,
    CuratedEditionRule,
    CuratedEnhancement,
    CuratedEnhancementEligibility,
    CuratedFaction,
    CuratedGameSizeRule,
    CuratedKeyword,
    CuratedModelLine,
    CuratedSnapshot,
    CuratedWargearOption,
    CuratedWeaponLine,
)
from pipeline.models.provenance import (
    DetailSource,
    EntityProvenance,
    PointsSource,
    PricingConfidence,
    PricingConfidenceState,
)


@dataclass(frozen=True, slots=True)
class PriorDatasheet:
    """One datasheet as the previous release published it."""

    datasheet_id: str
    faction_id: str
    name: str
    costs: Mapping[tuple[int, int], int]
    """``(copy_index_min, model_count) -> points``."""

    pricing_confidence: PricingConfidence

    @property
    def is_priced(self) -> bool:
        return bool(self.costs)

    @property
    def has_escalating_tier(self) -> bool:
        return any(copy_index > 1 for copy_index, _ in self.costs)


@dataclass(frozen=True, slots=True)
class PriorCostBearer:
    """A detachment or an enhancement, reduced to the one value a player pays."""

    entity_id: str
    name: str
    points: int


@dataclass(frozen=True, slots=True)
class PriorSnapshot:
    """The previous release, as much of it as a comparison needs."""

    rules_version_id: str | None
    factions: Mapping[str, str] = field(default_factory=dict)
    datasheets: Mapping[str, PriorDatasheet] = field(default_factory=dict)
    detachments: Mapping[str, PriorCostBearer] = field(default_factory=dict)
    enhancements: Mapping[str, PriorCostBearer] = field(default_factory=dict)

    @property
    def faction_count(self) -> int:
        return len(self.factions)

    @property
    def datasheet_count(self) -> int:
        return len(self.datasheets)

    @property
    def priced_datasheet_count(self) -> int:
        return sum(1 for datasheet in self.datasheets.values() if datasheet.is_priced)


# --- reading the tree -------------------------------------------------------------------------


def _read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _provenance(raw: Mapping[str, Any] | None, *, edition_code: str) -> EntityProvenance:
    """Reconstruct provenance, tolerating a tree written before a field existed.

    Lenient on purpose. The alternative is that adding a provenance field makes every previously
    committed tree unreadable, and the tree a curator most needs to read back is by definition an
    old one.
    """
    data = dict(raw or {})
    return EntityProvenance(
        points_source=PointsSource(data.get("points_source", PointsSource.NONE.value)),
        points_acquisition_id=data.get("points_acquisition_id"),
        points_edition_code=data.get("points_edition_code", edition_code),
        detail_source=DetailSource(data.get("detail_source", DetailSource.NONE.value)),
        detail_acquisition_id=data.get("detail_acquisition_id"),
        detail_edition_code=data.get("detail_edition_code", edition_code),
    )


def _pricing_confidence(raw: Mapping[str, Any] | None) -> PricingConfidence:
    data = dict(raw or {})
    return PricingConfidence(
        state=PricingConfidenceState(data.get("state", PricingConfidenceState.VERIFIED.value)),
        unverified_since_version=data.get("unverified_since_version"),
        consecutive_unverified_releases=int(data.get("consecutive_unverified_releases", 0)),
        last_verified_version=data.get("last_verified_version"),
        last_verified_points_digest=data.get("last_verified_points_digest"),
    )


def _restrictions(
    rows: Sequence[Mapping[str, Any]], *, edition_id: str, detachment_id: str | None
) -> list[CuratedDetachmentRestriction]:
    return [
        CuratedDetachmentRestriction(
            id=str(row["id"]),
            edition_id=edition_id,
            detachment_id=detachment_id,
            restriction_type=str(row["restriction_type"]),
            params=row.get("params", {}),
            message_template=str(row.get("message_template", "")),
        )
        for row in rows
    ]


def _datasheet(raw: Mapping[str, Any], *, edition_id: str, edition_code: str) -> CuratedDatasheet:
    return CuratedDatasheet(
        datasheet_id=str(raw["datasheet_id"]),
        edition_id=edition_id,
        faction_id=str(raw["faction_id"]),
        name=str(raw["name"]),
        role=raw.get("role"),
        is_legends=bool(raw.get("is_legends", False)),
        is_character=bool(raw.get("is_character", False)),
        is_epic_hero=bool(raw.get("is_epic_hero", False)),
        is_battleline=bool(raw.get("is_battleline", False)),
        is_dedicated_transport=bool(raw.get("is_dedicated_transport", False)),
        max_copies_per_army=raw.get("max_copies_per_army"),
        damaged_threshold=raw.get("damaged_threshold"),
        models=[CuratedModelLine(**row) for row in raw.get("models", [])],
        weapons=[CuratedWeaponLine(**row) for row in raw.get("weapons", [])],
        keywords=[CuratedKeyword(**row) for row in raw.get("keywords", [])],
        ability_keys=list(raw.get("ability_keys", [])),
        leader_pairs=list(raw.get("leader_pairs", [])),
        wargear_options=[CuratedWargearOption(**row) for row in raw.get("wargear_options", [])],
        costs=[
            CuratedDatasheetCost(
                model_count=int(row["model_count"]),
                copy_index_min=int(row.get("copy_index_min", 1)),
                points=int(row["points"]),
                label=str(row["label"]),
                pricing_confidence=PricingConfidenceState(
                    row.get("pricing_confidence", PricingConfidenceState.VERIFIED.value)
                ),
                source_acquisition_id=row.get("source_acquisition_id"),
            )
            for row in raw.get("costs", [])
        ],
        pricing_confidence=_pricing_confidence(raw.get("pricing_confidence")),
        provenance=_provenance(raw.get("provenance"), edition_code=edition_code),
    )


def read_curated_tree(data_dir: Path) -> CuratedSnapshot | None:
    """Reconstruct a snapshot from ``data/<edition-code>``, or ``None`` when there is no tree.

    ``None`` rather than an exception: a repository at the start of its first release
    legitimately has no previous tree, and that is not an error condition — it is the reason
    coverage collapse cannot be checked in US1.
    """
    edition_file = data_dir / "edition.json"
    if not edition_file.is_file():
        return None

    edition_doc = _read(edition_file)
    edition_raw = edition_doc["edition"]
    edition = CuratedEdition(
        id=str(edition_raw["id"]),
        code=str(edition_raw["code"]),
        name=str(edition_raw["name"]),
        display_order=int(edition_raw.get("display_order", 1)),
    )

    game_sizes = [
        CuratedGameSizeRule(edition_id=edition.id, **row)
        for row in _read(data_dir / "game-sizes.json")
    ]

    factions: list[CuratedFaction] = []
    detachments: list[CuratedDetachment] = []
    enhancements: list[CuratedEnhancement] = []
    datasheets: list[CuratedDatasheet] = []

    for raw in _read(data_dir / "factions.json"):
        factions.append(
            CuratedFaction(
                faction_id=str(raw["faction_id"]),
                edition_id=edition.id,
                code=str(raw["code"]),
                name=str(raw["name"]),
                parent_faction_id=raw.get("parent_faction_id"),
                mfm_slug=str(raw.get("mfm_slug", "")),
                detail_source_faction_id=str(raw.get("detail_source_faction_id", "")),
                provenance=_provenance(raw.get("provenance"), edition_code=edition.code),
            )
        )

    for faction in factions:
        faction_dir = data_dir / "factions" / faction.faction_id
        if not faction_dir.is_dir():
            continue

        for row in _read(faction_dir / "detachments.json").get("detachments", []):
            detachment_id = str(row["detachment_id"])
            detachments.append(
                CuratedDetachment(
                    detachment_id=detachment_id,
                    edition_id=edition.id,
                    faction_id=faction.faction_id,
                    name=str(row["name"]),
                    detachment_points_cost=int(row["detachment_points_cost"]),
                    is_legends=bool(row.get("is_legends", False)),
                    force_disposition=row.get("force_disposition"),
                    is_unique=row.get("is_unique"),
                    restrictions=_restrictions(
                        row.get("restrictions", []),
                        edition_id=edition.id,
                        detachment_id=detachment_id,
                    ),
                    provenance=_provenance(row.get("provenance"), edition_code=edition.code),
                )
            )

        for row in _read(faction_dir / "enhancements.json").get("enhancements", []):
            enhancements.append(
                CuratedEnhancement(
                    enhancement_id=str(row["enhancement_id"]),
                    edition_id=edition.id,
                    detachment_id=str(row["detachment_id"]),
                    name=str(row["name"]),
                    points=int(row["points"]),
                    max_per_army=int(row.get("max_per_army", 1)),
                    eligibility=[
                        CuratedEnhancementEligibility(**item) for item in row.get("eligibility", [])
                    ],
                    provenance=_provenance(row.get("provenance"), edition_code=edition.code),
                )
            )

        for path in sorted((faction_dir / "datasheets").glob("*.json")):
            datasheets.append(
                _datasheet(_read(path), edition_id=edition.id, edition_code=edition.code)
            )

    return CuratedSnapshot(
        edition=edition,
        edition_rules=[
            CuratedEditionRule(rule_key=str(rule["rule_key"]), value=rule["value"])
            for rule in edition_doc.get("edition_rules", [])
        ],
        game_sizes=game_sizes,
        factions=factions,
        detachments=detachments,
        enhancements=enhancements,
        datasheets=datasheets,
    )


# --- the comparison projection -----------------------------------------------------------------


def prior_from_snapshot(
    snapshot: CuratedSnapshot, *, rules_version_id: str | None
) -> PriorSnapshot:
    """Project a snapshot into the narrow view a comparison needs."""
    return PriorSnapshot(
        rules_version_id=rules_version_id,
        factions={faction.faction_id: faction.name for faction in snapshot.factions},
        datasheets={
            datasheet.datasheet_id: PriorDatasheet(
                datasheet_id=datasheet.datasheet_id,
                faction_id=datasheet.faction_id,
                name=datasheet.name,
                costs={
                    (cost.copy_index_min, cost.model_count): cost.points for cost in datasheet.costs
                },
                pricing_confidence=datasheet.pricing_confidence,
            )
            for datasheet in snapshot.datasheets
        },
        detachments={
            detachment.detachment_id: PriorCostBearer(
                entity_id=detachment.detachment_id,
                name=detachment.name,
                points=detachment.detachment_points_cost,
            )
            for detachment in snapshot.detachments
        },
        enhancements={
            enhancement.enhancement_id: PriorCostBearer(
                entity_id=enhancement.enhancement_id,
                name=enhancement.name,
                points=enhancement.points,
            )
            for enhancement in snapshot.enhancements
        },
    )


def previous_published_version(manifest_path: Path) -> str | None:
    """The most recently published ``rulesVersionId`` in a channel manifest, or ``None``.

    Withdrawn versions are skipped: a withdrawn release is one we have said should not be used,
    and measuring the next release's coverage against it would compare against something we
    already disowned (FR-044).
    """
    if not manifest_path.is_file():
        return None
    document = json.loads(manifest_path.read_text(encoding="utf-8"))
    live = [
        entry
        for entry in document.get("versions", [])
        if not entry.get("withdrawn", False) and entry.get("rulesVersionId")
    ]
    if not live:
        return None
    latest = max(
        live, key=lambda entry: (str(entry.get("publishedAt", "")), str(entry["rulesVersionId"]))
    )
    return str(latest["rulesVersionId"])


def load_prior(
    root: Path, *, edition_code: str, manifest_relative_path: str = "site/manifest.json"
) -> PriorSnapshot | None:
    """Read the previous release from a repository root, or ``None`` when there is none.

    ``root`` is a checkout — the repository itself in a real run, a fixture set's ``previous/``
    directory in a test. Both are the same read, which is what keeps the fixture path honest.
    """
    snapshot = read_curated_tree(root / "data" / edition_code)
    if snapshot is None:
        return None
    return prior_from_snapshot(
        snapshot, rules_version_id=previous_published_version(root / manifest_relative_path)
    )
