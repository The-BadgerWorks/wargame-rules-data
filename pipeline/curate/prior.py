# AI-Assisted: Claude Code (model: claude-opus-5) - Added the FR-030 ratchet's baseline (004
# tasks T041/T046): the previous release's classified-keyword set from the tree, and its
# per-class approved-summary percentages from its retained report.json, which is the only place
# they can come from since authored content never reaches the tree.
# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented reading the previous curated tree
# and the previous published version back (task T090), so last-known pricing, rename detection,
# coverage ratios, and the change summary all have a baseline without re-acquiring anything
# (FR-032, FR-035, spec Support implications).
# AI-Assisted: Claude Code (model: claude-opus-5) - Generalised the retained-report reader to a
# second key family (006 task T038): _previous_coverage takes the prefix, previous_loadout_
# coverage joins previous_summary_coverage, and the prefix is a FILTER rather than a lookup so
# a generalisation bug cannot feed summaries.abilities to the option ratchet.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Read item_constraints back (007 US3, the
# carried-over round-trip gap US4's T032 deliberately left for this entity).
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
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any

from pipeline.models.curated import (
    ArmyRuleState,
    CuratedChapterKeyword,
    CuratedCompositionEntry,
    CuratedDatasheet,
    CuratedDatasheetCost,
    CuratedDetachment,
    CuratedDetachmentRestriction,
    CuratedDetachmentRule,
    CuratedEdition,
    CuratedEditionRule,
    CuratedEnhancement,
    CuratedEnhancementEligibility,
    CuratedEquipmentGroup,
    CuratedFaction,
    CuratedGameSizeRule,
    CuratedItemConstraint,
    CuratedKeyword,
    CuratedModelLine,
    CuratedOptionChoice,
    CuratedOptionGroup,
    CuratedSnapshot,
    CuratedWargearOption,
    CuratedWeaponLine,
    DefaultEquipmentState,
    WargearOptionState,
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
    costs: Mapping[tuple[int, int, str], int]
    """``(copy_index_min, model_count, pricing_context or "") -> points``.

    The context is in the key because two rows of one datasheet may share a copy index and a
    model count and differ only by the condition they are priced under; without it the two
    prices would be one entry here and a change to either would read as a change to both.
    """

    pricing_confidence: PricingConfidence

    has_composition: bool = False
    """Did the previous release publish structured composition for this datasheet?"""

    wargear_option_state: WargearOptionState | None = None
    """Its previous ``none`` | ``extracted`` | ``partial``, or ``None`` when never consulted."""

    @property
    def options_resolved(self) -> bool:
        """``none`` and ``extracted`` both count as resolved; ``partial`` and absent do not.

        This is the denominator SC-002 measures: a datasheet the source describes no options for
        is *finished*, not outstanding, and counting it as a gap would make the figure fall every
        time a faction of characters shipped.
        """
        return self.wargear_option_state in {
            WargearOptionState.NONE,
            WargearOptionState.EXTRACTED,
        }

    @property
    def is_priced(self) -> bool:
        return bool(self.costs)

    @property
    def has_escalating_tier(self) -> bool:
        return any(copy_index > 1 for copy_index, _, _ in self.costs)


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
    classified_keywords: frozenset[str] = frozenset()
    """Distinct keywords the previous release published a ``keyword_class`` for (004 FR-038)."""

    summary_approved_count: Mapping[str, int] = field(default_factory=dict)
    """``<summary class> -> approved entries``, as the previously published version reported."""

    loadout_resolved_count: Mapping[str, int] = field(default_factory=dict)
    """``<loadout figure> -> resolved datasheets``, as the previously published version reported."""

    loadout_ratio_percent: Mapping[str, int] = field(default_factory=dict)
    """``<loadout figure> -> resolved percent``, the `006` FR-022 ratchet's baseline.

    Read back from the previously published version's retained `report.json` for the same reason
    the summary figures are: the tree records what each datasheet's state *is*, never what
    proportion of the roster reached it, and this run has already overwritten the tree it would
    otherwise have recomputed the proportion from.
    """

    summary_ratio_percent: Mapping[str, int] = field(default_factory=dict)
    """``<summary class> -> approved-coverage percent``, the FR-030 ratchet's baseline.

    Read back from the previously published version's retained `report.json` rather than from
    the curated tree, because authored content is never written to the tree — the tree could not
    answer this question even in principle (FR-017). The **previously published** version, not
    the previous candidate, so a rejected candidate cannot move the ratchet (contract §4).
    """

    @property
    def faction_count(self) -> int:
        return len(self.factions)

    @property
    def datasheet_count(self) -> int:
        return len(self.datasheets)

    @property
    def priced_datasheet_count(self) -> int:
        return sum(1 for datasheet in self.datasheets.values() if datasheet.is_priced)

    @property
    def composition_datasheet_count(self) -> int:
        """Datasheets the previous release published composition for (004 FR-038)."""
        return sum(1 for datasheet in self.datasheets.values() if datasheet.has_composition)

    @property
    def option_resolved_datasheet_count(self) -> int:
        """Datasheets whose option set the previous release fully resolved (004 FR-038)."""
        return sum(1 for datasheet in self.datasheets.values() if datasheet.options_resolved)

    @property
    def classified_keyword_count(self) -> int:
        """Distinct classified keywords last time — the FR-038 collapse baseline (SC-005)."""
        return len(self.classified_keywords)


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
        composition=[CuratedCompositionEntry(**row) for row in raw.get("composition", [])],
        option_groups=[CuratedOptionGroup(**row) for row in raw.get("option_groups", [])],
        option_choices=[CuratedOptionChoice(**row) for row in raw.get("option_choices", [])],
        wargear_option_state=(
            WargearOptionState(raw["wargear_option_state"])
            if raw.get("wargear_option_state")
            else None
        ),
        # `006` §1.2/§3, closed the round-trip by `007` T032 (research D2, issue #14). Nested
        # `items` inside each group validate into `CuratedEquipmentItem` automatically — pydantic
        # parses `**row`'s sequence-of-dicts against the field's declared item type, the same way
        # `option_choices` above already relies on for its own `items` array.
        equipment_groups=[CuratedEquipmentGroup(**row) for row in raw.get("equipment_groups", [])],
        default_equipment_state=(
            DefaultEquipmentState(raw["default_equipment_state"])
            if raw.get("default_equipment_state")
            else None
        ),
        # `007` §1.1, the carried-over round-trip gap closed alongside `006`'s five classes: a
        # flat row, no nested structure, so — like `option_groups`/`option_choices` above —
        # pydantic validates it directly from `**row`.
        item_constraints=[CuratedItemConstraint(**row) for row in raw.get("item_constraints", [])],
        wargear_options=[CuratedWargearOption(**row) for row in raw.get("wargear_options", [])],
        costs=[
            CuratedDatasheetCost(
                model_count=int(row["model_count"]),
                copy_index_min=int(row.get("copy_index_min", 1)),
                points=int(row["points"]),
                label=str(row["label"]),
                pricing_context=row.get("pricing_context"),
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
                army_rule_state=(
                    ArmyRuleState(raw["army_rule_state"]) if raw.get("army_rule_state") else None
                ),
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
                    # The rule identities the tree recorded: key and name, never a summary. A
                    # bare `validate` re-run reads its denominator back from here, which is what
                    # stops it disagreeing with `build` about a class's coverage (004 T054).
                    rules=[
                        CuratedDetachmentRule(
                            summary_key=str(rule["summary_key"]), name=str(rule["name"])
                        )
                        for rule in row.get("rules", [])
                    ],
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

    chapter_keywords_file = data_dir / "chapter-keywords.json"
    chapter_keywords = (
        [CuratedChapterKeyword(**row) for row in _read(chapter_keywords_file)]
        if chapter_keywords_file.is_file()
        else []
    )

    return CuratedSnapshot(
        edition=edition,
        chapter_keywords=chapter_keywords,
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
                    (cost.copy_index_min, cost.model_count, cost.pricing_context or ""): (
                        cost.points
                    )
                    for cost in datasheet.costs
                },
                pricing_confidence=datasheet.pricing_confidence,
                has_composition=bool(datasheet.composition),
                wargear_option_state=datasheet.wargear_option_state,
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
        classified_keywords=classified_keywords(snapshot),
    )


def classified_keywords(snapshot: CuratedSnapshot) -> frozenset[str]:
    """The distinct keywords carrying a class, over every datasheet (004 SC-005).

    Distinct rather than per binding, because the class is a property of the keyword: counting
    bindings would make the figure move whenever a common keyword gained or lost a datasheet,
    which is a change in the roster and not in the classification.
    """
    return frozenset(
        keyword.keyword
        for datasheet in snapshot.datasheets
        for keyword in datasheet.keywords
        if keyword.keyword_class is not None
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


#: The `report.json` coverage keys the four summary classes occupy (data-model.md §5).
SUMMARY_COVERAGE_PREFIX = "summaries."

#: The keys `006`'s two loadout figures occupy (006 data-model.md §5).
#:
#: A second prefix through the same reader rather than a second reader. The retained
#: `report.json` of the previous published version is the only place either family's percent can
#: come from, for the same reason: the curated tree records what a datasheet's state *is*, never
#: what proportion of the roster reached it, and a proportion cannot be recomputed from a tree
#: that has since been overwritten by this very run.
LOADOUT_COVERAGE_PREFIX = "loadout."


def _previous_coverage(
    root: Path, rules_version_id: str | None, *, prefix: str
) -> dict[str, tuple[int, int]]:
    """``<figure> -> (count, percent)`` for one coverage-key family, from a retained report.

    Returns an empty mapping when there is no previous version, no retained report, or no row
    under ``prefix`` — a first release, or a release predating whichever feature added the
    family. A figure with no previous value has nothing to fall from and therefore cannot
    regress, which is what makes a ratchet safe to introduce mid-campaign rather than needing a
    seeded baseline.

    The prefix is a **filter, not a lookup**: rows outside it are not merely ignored, they are
    unreachable, so a generalisation bug cannot feed `summaries.abilities` to the option ratchet
    as a plausible number that means nothing.
    """
    if not rules_version_id:
        return {}
    report_path = root / "reports" / rules_version_id / "report.json"
    if not report_path.is_file():
        return {}
    try:
        document = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        # An unreadable baseline must not stop this run: it removes the ratchet's evidence, and
        # acting on evidence is the ratchet's whole job.
        return {}
    coverage = document.get("coverage", {})
    return {
        name.removeprefix(prefix): (
            int(figure.get("current", 0)),
            int(figure.get("ratio_percent", 0)),
        )
        for name, figure in coverage.items()
        if name.startswith(prefix) and isinstance(figure, dict)
    }


def previous_summary_coverage(
    root: Path, rules_version_id: str | None
) -> dict[str, tuple[int, int]]:
    """``<summary class> -> (approved count, approved percent)`` from a retained report (FR-030)."""
    return _previous_coverage(root, rules_version_id, prefix=SUMMARY_COVERAGE_PREFIX)


def previous_loadout_coverage(
    root: Path, rules_version_id: str | None
) -> dict[str, tuple[int, int]]:
    """``<loadout figure> -> (resolved count, resolved percent)`` from a retained report (006).

    ``rules_version_id`` is the previously **published** version, resolved by
    :func:`previous_published_version` from the channel manifest — which only a publication
    writes. A candidate that was reviewed and turned down leaves a `reports/<id>/report.json`
    behind exactly like an approved one, so reading "the newest retained report" instead would
    let a rejected candidate lower the bar for the next one.
    """
    return _previous_coverage(root, rules_version_id, prefix=LOADOUT_COVERAGE_PREFIX)


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
    rules_version_id = previous_published_version(root / manifest_relative_path)
    prior = prior_from_snapshot(snapshot, rules_version_id=rules_version_id)
    summaries = previous_summary_coverage(root, rules_version_id)
    loadout = previous_loadout_coverage(root, rules_version_id)
    return replace(
        prior,
        summary_approved_count={name: count for name, (count, _) in summaries.items()},
        summary_ratio_percent={name: percent for name, (_, percent) in summaries.items()},
        loadout_resolved_count={name: count for name, (count, _) in loadout.items()},
        loadout_ratio_percent={name: percent for name, (_, percent) in loadout.items()},
    )
