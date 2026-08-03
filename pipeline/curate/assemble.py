# AI-Assisted: Claude Code (model: claude-opus-5) - Assemble the CuratedSnapshot from the two
# normalized sources plus the authored tree (needed by the T073 build wiring, which names the
# curate stage but assigns it no assembly module of its own).
"""Build one :class:`~pipeline.models.curated.CuratedSnapshot` from everything upstream.

This is where the two sources stop being two sources. The **points** source is authoritative for
every value a player pays — unit costs, detachment DP, enhancement points, wargear deltas —
and the **detail** source supplies characteristics, weapons, keywords, abilities and
composition (FR-001, FR-002, as amended by C8/R3 for wargear costs).

Three consequences of that split show up directly in the code below:

* a datasheet exists because the points source prices it, and its detail is attached if a match
  was found — so a unit the detail source has never heard of still ships, priced;
* cost-table labels become copy-index tiers here, because that is where the label literals and
  the model counts are in the same place (C1/R2); and
* every entity carries provenance naming both acquisitions and both declared editions, so a
  hybrid entity is self-describing all the way through to `datasheet.detail_edition_code`
  (FR-058..FR-061, C5/R4).

Nothing here reads a `curation/` file directly — it takes an already-validated
:class:`~pipeline.curate.authored.AuthoredContent` — and nothing here writes anything at all.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Final

from pipeline.curate.authored import AuthoredContent
from pipeline.models.curated import (
    CuratedDatasheet,
    CuratedDatasheetCost,
    CuratedDetachment,
    CuratedDetachmentRestriction,
    CuratedEdition,
    CuratedEditionRule,
    CuratedEnhancement,
    CuratedFaction,
    CuratedGameSizeRule,
    CuratedKeyword,
    CuratedModelLine,
    CuratedSnapshot,
    CuratedWargearOption,
    CuratedWeaponLine,
)
from pipeline.models.findings import Finding
from pipeline.models.provenance import (
    DetailSource,
    EntityProvenance,
    PointsSource,
    PricingConfidence,
    PricingConfidenceState,
)
from pipeline.models.source import MfmDetachmentCard, MfmUnitCostBlock, SourceAcquisition
from pipeline.normalize.ability_types import classify
from pipeline.normalize.ip_strip import strip_field
from pipeline.normalize.names import normalize_name
from pipeline.normalize.numerics import (
    NumericParseError,
    model_count,
    optional_characteristic,
    to_int,
    upper_bound,
)
from pipeline.parse.mfm_dom import MfmPage
from pipeline.parse.wahapedia_csv import CsvReadResult
from pipeline.reconcile.identity import EntityKind, IdRegistry, slugify
from pipeline.reconcile.match import (
    FactionScope,
    UnitMatch,
    match_units,
    report_orphan_detail_factions,
    resolve_factions,
)
from pipeline.report.catalogue import build_finding

#: The cost-table label that carries the *later* copies of an escalating price. The publisher
#: writes the threshold into the label — `YOUR 3RD + UNIT COSTS` — and that literal is the only
#: place the copy index appears, which is why data-model.md §1.2 preserves it verbatim (C1).
_TIER_THRESHOLD: Final = re.compile(r"\b(\d+)\s*(?:ST|ND|RD|TH)\b", re.IGNORECASE)

#: A cost-table row that prices a *wargear item* rather than a squad size. The points source
#: writes it as `+ 1 Invader ATV`, and that price is "applied on top of the unit's main points
#: cost" (research §0.2). This is the only place a wargear cost appears anywhere — the detail
#: source's options file has no cost column at all — which is what FR-001/FR-002 were amended
#: for (C8/R3). Reading such a row as a model count would invent a size band nobody printed.
_WARGEAR_ROW: Final = re.compile(r"^\+\s*(?:(\d+)\s+)?(?P<name>.+?)\s*$")

#: The detail source's role vocabulary, mapped onto the flags the consumer contract carries.
_BATTLELINE_ROLES: Final[frozenset[str]] = frozenset({"battleline"})
_CHARACTER_ROLES: Final[frozenset[str]] = frozenset({"characters", "character"})
_TRANSPORT_ROLES: Final[frozenset[str]] = frozenset({"dedicated transports", "dedicated transport"})


@dataclass(slots=True)
class AssemblyResult:
    snapshot: CuratedSnapshot
    findings: list[Finding] = field(default_factory=list)


def _tier_indices(label: str) -> int:
    """The `copy_index_min` a cost-table label states. A plain table is the first copy."""
    match = _TIER_THRESHOLD.search(label)
    return int(match.group(1)) if match else 1


def _provenance(
    points: SourceAcquisition | None,
    detail: SourceAcquisition | None,
    *,
    snapshot_edition: str,
) -> EntityProvenance:
    return EntityProvenance(
        points_source=PointsSource.MFM if points else PointsSource.NONE,
        points_acquisition_id=points.acquisition_id if points else None,
        points_edition_code=points.declared_edition_code if points else snapshot_edition,
        detail_source=DetailSource.WAHAPEDIA if detail else DetailSource.NONE,
        detail_acquisition_id=detail.acquisition_id if detail else None,
        detail_edition_code=detail.declared_edition_code if detail else snapshot_edition,
    )


def _costs(
    blocks: Sequence[MfmUnitCostBlock], acquisition_id: str | None, datasheet_id: str
) -> tuple[list[CuratedDatasheetCost], list[CuratedWargearOption], list[Finding]]:
    """Turn one unit's cost tables into copy-indexed price rows and cost-bearing wargear.

    A datasheet priced by a single `YOUR UNIT COSTS` table yields one row per model count, all at
    `copy_index_min = 1`. A datasheet priced by the requisition-threshold pair yields the same
    rows plus a second set at the threshold the later table's label states — the label is the
    only place the copy index appears, which is why it is preserved verbatim upstream (C1).

    A row whose label opens with `+` is not a squad size at all: it is a wargear item and its
    price is a delta on top of the unit's cost. Reading it as a model count would invent a size
    band the publisher never printed.
    """
    rows: list[CuratedDatasheetCost] = []
    options: list[CuratedWargearOption] = []
    findings: list[Finding] = []

    for block in blocks:
        copy_index = _tier_indices(block.cost_table_label)
        for row in block.rows:
            label = row.model_count_label.strip()
            if label.startswith("+"):
                wargear = _WARGEAR_ROW.match(label)
                name = wargear.group("name") if wargear else label.lstrip("+ ")
                options.append(
                    CuratedWargearOption(
                        id=f"wo-{datasheet_id.removeprefix('ds-')}-{slugify(name)}",
                        group_key=slugify(name),
                        name=name,
                        points_delta=row.points,
                        max_per_unit=int(wargear.group(1))
                        if wargear and wargear.group(1)
                        else None,
                    )
                )
                continue
            try:
                count = model_count(label, field="cost.model_count")
            except NumericParseError:
                findings.append(
                    build_finding(
                        "REC-COMPOSITION-UNPARSED",
                        entity_refs=[datasheet_id],
                        detail={"datasheet_id": datasheet_id, "field": "model_count_label"},
                    )
                )
                continue
            rows.append(
                CuratedDatasheetCost(
                    model_count=count,
                    copy_index_min=copy_index,
                    points=row.points,
                    label=label,
                    pricing_confidence=PricingConfidenceState.VERIFIED,
                    source_acquisition_id=acquisition_id,
                )
            )

    return rows, _deduplicate_options(options), findings


def _deduplicate_options(
    options: Sequence[CuratedWargearOption],
) -> list[CuratedWargearOption]:
    """One row per option id. The threshold pair prints the same wargear row in both tables."""
    unique: dict[str, CuratedWargearOption] = {}
    for option in options:
        unique.setdefault(option.id, option)
    return sorted(unique.values(), key=lambda option: option.id)


def _detail_datasheet_fields(
    detail_id: str,
    detail: Mapping[str, CsvReadResult],
) -> tuple[dict[str, object], list[Finding]]:
    """Everything the detail source contributes to one datasheet."""
    findings: list[Finding] = []
    fields: dict[str, object] = {}

    row = detail["Datasheets.csv"].by_id("id").get(detail_id)
    if row is None:
        return fields, findings

    role_raw = strip_field(row.fields.get("role", ""), field="role").text
    role = role_raw or None
    role_key = (role or "").casefold()

    fields["role"] = role
    fields["is_dedicated_transport"] = role_key in _TRANSPORT_ROLES
    fields["is_legends"] = bool(row.fields.get("legend", "").strip())
    fields["damaged_threshold"] = upper_bound(row.fields.get("damaged_w"), field="damaged_w")

    models: list[CuratedModelLine] = []
    for model in detail["Datasheets_models.csv"].grouped_by("datasheet_id").get(detail_id, []):
        try:
            models.append(
                CuratedModelLine(
                    line=to_int(model.fields["line"], field="model.line"),
                    name=strip_field(model.fields["name"], field="model.name").text,
                    movement=model.fields["M"].strip() or "-",
                    toughness=to_int(model.fields["T"], field="model.T"),
                    save=model.fields["Sv"].strip() or "-",
                    invuln_save=optional_characteristic(model.fields.get("inv_sv")),
                    wounds=to_int(model.fields["W"], field="model.W"),
                    leadership=model.fields["Ld"].strip() or "-",
                    objective_control=to_int(model.fields["OC"], field="model.OC"),
                    base_size=optional_characteristic(model.fields.get("base_size")),
                )
            )
        except (NumericParseError, KeyError):
            findings.append(
                build_finding(
                    "DQ-MALFORMED-ROW",
                    entity_refs=[f"wahapedia:{detail_id}"],
                    detail={"file_name": "Datasheets_models.csv", "field": "characteristics"},
                )
            )
    fields["models"] = models

    weapons: list[CuratedWeaponLine] = []
    for weapon in detail["Datasheets_wargear.csv"].grouped_by("datasheet_id").get(detail_id, []):
        weapon_range = optional_characteristic(weapon.fields.get("range"))
        is_melee = (weapon.fields.get("type", "") or "").strip().casefold() == "melee"
        try:
            weapons.append(
                CuratedWeaponLine(
                    line=to_int(weapon.fields["line"], field="weapon.line"),
                    name=strip_field(weapon.fields["name"], field="weapon.name").text,
                    is_melee=is_melee,
                    range=None if is_melee else weapon_range,
                    attacks=weapon.fields["A"].strip() or "-",
                    skill=weapon.fields["BS_WS"].strip() or "-",
                    strength=weapon.fields["S"].strip() or "-",
                    armour_penetration=weapon.fields["AP"].strip() or "0",
                    damage=weapon.fields["D"].strip() or "-",
                )
            )
        except (NumericParseError, KeyError):
            findings.append(
                build_finding(
                    "DQ-MALFORMED-ROW",
                    entity_refs=[f"wahapedia:{detail_id}"],
                    detail={"file_name": "Datasheets_wargear.csv", "field": "profile"},
                )
            )
    fields["weapons"] = weapons

    keywords: list[CuratedKeyword] = []
    for keyword in detail["Datasheets_keywords.csv"].grouped_by("datasheet_id").get(detail_id, []):
        text = strip_field(keyword.fields.get("keyword", ""), field="keyword").text
        if not text:
            continue
        keywords.append(
            CuratedKeyword(
                keyword=text,
                is_faction_keyword=keyword.fields.get("is_faction_keyword", "").strip().casefold()
                == "true",
                model_scope=strip_field(keyword.fields.get("model", ""), field="model").text
                or None,
            )
        )
    fields["keywords"] = keywords

    # The flags come from the KEYWORDS, not from the role column. A datasheet's keywords are
    # what the rules themselves key on — `EPIC HERO` is the only place that status is published
    # at all — and the role column is a presentation grouping that lumps most units under
    # "Other". Role is kept as a fallback for the two flags it does express.
    keyword_set = {keyword.keyword.casefold() for keyword in keywords}
    fields["is_epic_hero"] = "epic hero" in keyword_set
    fields["is_character"] = "character" in keyword_set or role_key in _CHARACTER_ROLES
    fields["is_battleline"] = "battleline" in keyword_set or role_key in _BATTLELINE_ROLES

    ability_keys: list[str] = []
    for binding in detail["Datasheets_abilities.csv"].grouped_by("datasheet_id").get(detail_id, []):
        name = strip_field(binding.fields.get("name", ""), field="ability.name").text
        if not name:
            continue
        ability_type, finding = classify(
            binding.fields.get("type", ""), entity_ref=f"wahapedia:{detail_id}"
        )
        if finding is not None:
            findings.append(finding)
            continue
        assert ability_type is not None
        ability_keys.append(f"{ability_type.value}:{slugify(name)}")
    fields["ability_keys"] = sorted(set(ability_keys))

    return fields, findings


def _wargear_options(
    detail_id: str, datasheet_id: str, detail: Mapping[str, CsvReadResult]
) -> tuple[list[CuratedWargearOption], list[Finding]]:
    """Wargear options whose **cost** the points source publishes.

    The detail source has the structure and no cost column at all (research §0.1), and FR-001
    was amended so the points source owns the cost (C8/R3). Until an option's cost is matched
    from the points source, the option is reported rather than emitted as a zero — a free
    upgrade in a player's list is worse than a missing one.
    """
    findings: list[Finding] = []
    rows = detail.get("Datasheets_options.csv")
    if rows is None:
        return [], findings
    for option in rows.grouped_by("datasheet_id").get(detail_id, []):
        findings.append(
            build_finding(
                "CON-WARGEAR-COST-MISSING",
                entity_refs=[datasheet_id],
                detail={
                    "datasheet_id": datasheet_id,
                    "line": to_int(option.fields.get("line", "0"), field="option.line"),
                },
            )
        )
    return [], findings


def assemble(  # noqa: PLR0913 - the stage genuinely needs every upstream input
    *,
    pages: Sequence[MfmPage],
    detail: Mapping[str, CsvReadResult],
    authored: AuthoredContent,
    points_acquisition: SourceAcquisition,
    detail_acquisition: SourceAcquisition,
    edition_code: str,
    edition_name: str,
    registry: IdRegistry | None = None,
) -> AssemblyResult:
    """Build the whole curated snapshot."""
    findings: list[Finding] = []
    registry = registry or IdRegistry()
    edition_id = f"ed-{edition_code}"

    factions_outcome = resolve_factions([page.faction_slug for page in pages], authored)
    findings.extend(factions_outcome.findings)
    scopes = {scope.entry.mfm_slug: scope for scope in factions_outcome.scopes}

    detail_datasheets = detail["Datasheets.csv"]
    findings.extend(
        report_orphan_detail_factions(
            [row.fields.get("faction_id", "") for row in detail_datasheets.rows], authored
        )
    )

    provenance = _provenance(points_acquisition, detail_acquisition, snapshot_edition=edition_code)
    # A unit the detail source has never heard of has no *detail* edition, so it is not hybrid
    # and emits no `detail_edition_code` (§5). A unit the points source has not priced this
    # release has no *points* acquisition, and ships on the best price known (FR-035).
    points_only_provenance = _provenance(points_acquisition, None, snapshot_edition=edition_code)
    detail_only_provenance = _provenance(None, detail_acquisition, snapshot_edition=edition_code)

    factions: list[CuratedFaction] = []
    detachments: list[CuratedDetachment] = []
    enhancements: list[CuratedEnhancement] = []
    datasheets: list[CuratedDatasheet] = []
    detail_to_curated: dict[str, str] = {}

    for page in sorted(pages, key=lambda p: p.faction_slug):
        scope = scopes.get(page.faction_slug)
        if scope is None:
            continue

        factions.append(
            CuratedFaction(
                faction_id=scope.faction_id,
                edition_id=edition_id,
                code=scope.faction_id.removeprefix("f-"),
                name=scope.faction_id.removeprefix("f-").replace("-", " ").title(),
                parent_faction_id=scope.entry.parent_faction_id,
                mfm_slug=scope.entry.mfm_slug,
                detail_source_faction_id=scope.entry.detail_source_faction_id,
                provenance=provenance,
            )
        )

        detachments.extend(
            _detachments_for(page.detachments, scope.faction_id, edition_id, provenance, registry)
        )
        enhancements.extend(
            _enhancements_for(page.detachments, scope.faction_id, edition_id, provenance, registry)
        )

        blocks_by_unit: dict[str, list[MfmUnitCostBlock]] = {}
        for block in page.unit_blocks:
            blocks_by_unit.setdefault(block.unit_display_name, []).append(block)

        in_scope = {
            row.fields["id"]: strip_field(row.fields["name"], field="datasheet.name").text
            for row in detail_datasheets.rows
            if row.fields.get("faction_id") in scope.detail_faction_ids
        }
        legends = {
            row.fields["id"]: bool(row.fields.get("legend", "").strip())
            for row in detail_datasheets.rows
        }

        outcome = match_units(
            scope,
            display_names=list(blocks_by_unit),
            detail_names=in_scope,
            detail_is_legends=legends,
            authored=authored,
            registry=registry,
        )
        findings.extend(outcome.findings)

        for match in outcome.matches:
            datasheet, datasheet_findings = _datasheet_for(
                match,
                blocks=blocks_by_unit.get(match.display_name, []),
                detail=detail,
                authored=authored,
                edition_id=edition_id,
                points_acquisition=points_acquisition,
                provenance=provenance if match.wahapedia_datasheet_id else points_only_provenance,
                edition_code=edition_code,
            )
            findings.extend(datasheet_findings)
            datasheets.append(datasheet)
            if match.wahapedia_datasheet_id:
                detail_to_curated[match.wahapedia_datasheet_id] = match.datasheet_id

    # The detail-only pass runs **after every faction has been matched**, not inside the loop.
    # A detail-source faction supplies several curated factions — the chapters all draw on one
    # id — so a datasheet unclaimed while the first of them is being assembled may well be
    # claimed by the third. Deciding early would file a chapter's exclusive unit under its
    # parent, which is precisely the mis-attribution §3.5 exists to get right.
    owning_faction = _owning_factions(factions_outcome.scopes)
    for row in detail_datasheets.rows:
        detail_id = row.fields.get("id", "")
        if not detail_id or detail_id in detail_to_curated:
            continue
        scope = owning_faction.get(row.fields.get("faction_id", ""))
        if scope is None:
            continue
        unverified, unverified_findings = _detail_only_datasheet(
            detail_id,
            display_name=strip_field(row.fields.get("name", ""), field="datasheet.name").text,
            faction_id=scope.faction_id,
            detail=detail,
            authored=authored,
            edition_id=edition_id,
            provenance=detail_only_provenance,
            registry=registry,
            detail_acquisition=detail_acquisition,
        )
        findings.extend(unverified_findings)
        if unverified is not None:
            datasheets.append(unverified)
            detail_to_curated[detail_id] = unverified.datasheet_id

    datasheets = _attach_leader_pairs(datasheets, detail, detail_to_curated)

    snapshot = CuratedSnapshot(
        edition=CuratedEdition(
            id=edition_id, code=edition_code, name=edition_name, display_order=1
        ),
        edition_rules=[
            CuratedEditionRule(rule_key=rule.rule_key, value=rule.value)
            for rule in authored.edition_rules
        ],
        game_sizes=[
            CuratedGameSizeRule(
                id=band.id,
                edition_id=edition_id,
                label=band.label,
                min_points=band.min_points,
                max_points=band.max_points,
                detachment_points_budget=band.detachment_points_budget,
                max_detachments=band.max_detachments,
                max_enhancements=band.max_enhancements,
            )
            for band in authored.game_sizes
        ],
        factions=factions,
        detachments=detachments,
        enhancements=enhancements,
        datasheets=datasheets,
        restrictions=[
            CuratedDetachmentRestriction(
                id=restriction.id,
                edition_id=edition_id,
                detachment_id=restriction.detachment_id,
                restriction_type=restriction.restriction_type,
                params=restriction.params,
                message_template=restriction.message_template,
            )
            for restriction in authored.restrictions
        ],
        ability_summaries=authored.ability_summaries,
    )

    return AssemblyResult(snapshot=snapshot, findings=findings)


def _detachments_for(
    cards: Sequence[MfmDetachmentCard],
    faction_id: str,
    edition_id: str,
    provenance: EntityProvenance,
    registry: IdRegistry,
) -> list[CuratedDetachment]:
    built: list[CuratedDetachment] = []
    for card in cards:
        key = f"{faction_id}/{normalize_name(card.detachment_name)}"
        built.append(
            CuratedDetachment(
                detachment_id=registry.mint(EntityKind.DETACHMENT, key, card.detachment_name),
                edition_id=edition_id,
                faction_id=faction_id,
                name=card.detachment_name,
                detachment_points_cost=card.dp_cost,
                is_legends=False,
                force_disposition=card.force_disposition,
                is_unique=any(tag.upper().startswith("UNIQUE") for tag in card.tags),
                provenance=provenance,
            )
        )
    return built


def _enhancements_for(
    cards: Sequence[MfmDetachmentCard],
    faction_id: str,
    edition_id: str,
    provenance: EntityProvenance,
    registry: IdRegistry,
) -> list[CuratedEnhancement]:
    """Enhancements, each keyed to the detachment card it was published on.

    The detachment id is looked up from the registry using the same key
    :func:`_detachments_for` minted it under, rather than re-derived — a second derivation is a
    second chance to disagree, and an enhancement whose parent does not resolve is the blocking
    `CON-ORPHAN-ENHANCEMENT`.
    """
    built: list[CuratedEnhancement] = []
    for card in cards:
        detachment_key = f"{faction_id}/{normalize_name(card.detachment_name)}"
        detachment_id = registry.existing(EntityKind.DETACHMENT, detachment_key) or ""
        for entry in card.enhancements:
            key = f"{detachment_key}/{normalize_name(entry.name)}"
            built.append(
                CuratedEnhancement(
                    enhancement_id=registry.mint(EntityKind.ENHANCEMENT, key, entry.name),
                    edition_id=edition_id,
                    detachment_id=detachment_id,
                    name=entry.name,
                    points=entry.points,
                    max_per_army=1,
                    provenance=provenance,
                )
            )
    return built


def _datasheet_for(  # noqa: PLR0913 - one datasheet needs both sources and the authored tree
    match: UnitMatch,
    *,
    blocks: Sequence[MfmUnitCostBlock],
    detail: Mapping[str, CsvReadResult],
    authored: AuthoredContent,
    edition_id: str,
    points_acquisition: SourceAcquisition,
    provenance: EntityProvenance,
    edition_code: str,
) -> tuple[CuratedDatasheet, list[Finding]]:
    findings: list[Finding] = []
    costs, wargear_options, cost_findings = _costs(
        blocks, points_acquisition.acquisition_id, match.datasheet_id
    )
    findings.extend(cost_findings)

    fields: dict[str, object] = {}
    if match.wahapedia_datasheet_id:
        fields, detail_findings = _detail_datasheet_fields(match.wahapedia_datasheet_id, detail)
        findings.extend(detail_findings)
        _, wargear_findings = _wargear_options(
            match.wahapedia_datasheet_id, match.datasheet_id, detail
        )
        findings.extend(wargear_findings)
    else:
        findings.append(
            build_finding(
                "EDN-HYBRID-ENTITY"
                if provenance.is_hybrid_edition
                else "REC-UNMATCHED-DETAIL-ONLY",
                entity_refs=[match.datasheet_id],
                detail={"datasheet_id": match.datasheet_id, "edition_code": edition_code},
            )
        )

    datasheet = CuratedDatasheet(
        datasheet_id=match.datasheet_id,
        edition_id=edition_id,
        faction_id=match.faction_id,
        name=match.display_name,
        role=fields.get("role"),  # type: ignore[arg-type]
        is_legends=bool(fields.get("is_legends", False)),
        is_character=bool(fields.get("is_character", False)),
        is_epic_hero=bool(fields.get("is_epic_hero", False)),
        is_battleline=bool(fields.get("is_battleline", False)),
        is_dedicated_transport=bool(fields.get("is_dedicated_transport", False)),
        max_copies_per_army=authored.copy_limit_for(match.datasheet_id),
        damaged_threshold=fields.get("damaged_threshold"),  # type: ignore[arg-type]
        models=fields.get("models", ()),  # type: ignore[arg-type]
        weapons=fields.get("weapons", ()),  # type: ignore[arg-type]
        keywords=fields.get("keywords", ()),  # type: ignore[arg-type]
        ability_keys=fields.get("ability_keys", ()),  # type: ignore[arg-type]
        leader_pairs=(),
        wargear_options=wargear_options,
        costs=costs,
        pricing_confidence=PricingConfidence(state=PricingConfidenceState.VERIFIED),
        provenance=provenance,
    )
    return datasheet, findings


def _owning_factions(scopes: Sequence[FactionScope]) -> dict[str, FactionScope]:
    """Which curated faction owns each detail-source faction id.

    Several curated factions can share one detail-source id — the chapters all draw on the
    parent's. A datasheet nobody priced is filed under the **root** of that group, because the
    consumer contract's §3.5 query rule then shows it to the parent *and* to every chapter,
    whereas filing it under one chapter would hide it from the other four.
    """
    owners: dict[str, FactionScope] = {}
    for scope in sorted(
        scopes, key=lambda s: (s.entry.parent_faction_id is not None, s.faction_id)
    ):
        owners.setdefault(scope.entry.detail_source_faction_id, scope)
    return owners


def _detail_only_datasheet(  # noqa: PLR0913 - one datasheet needs both trees and the registry
    detail_id: str,
    *,
    display_name: str,
    faction_id: str,
    detail: Mapping[str, CsvReadResult],
    authored: AuthoredContent,
    edition_id: str,
    provenance: EntityProvenance,
    registry: IdRegistry,
    detail_acquisition: SourceAcquisition,
) -> tuple[CuratedDatasheet | None, list[Finding]]:
    """A datasheet the points authority did not price this release (FR-026, FR-035).

    It is **not** dropped for being unpriced by the authority: FR-035 is explicit that a unit
    ships on the best price known rather than being withheld, so it takes the detail source's
    own published cost and is marked `unverified` — the marker exists precisely so a value the
    authority did not confirm is visible as such rather than indistinguishable from one it did.

    A datasheet no source has ever priced is a different case entirely. There is nothing to fall
    back to, so it is reported and left out rather than emitted at zero: an unpriced unit in a
    player's list is worse than an absent one, and `CON-NO-COST` would block the whole release
    for a unit that is not part of this edition.
    """
    findings: list[Finding] = [
        build_finding(
            "REC-UNMATCHED-DETAIL-ONLY",
            entity_refs=[f"wahapedia:{detail_id}"],
            detail={"faction_id": faction_id, "detail_datasheet_id": detail_id},
        )
    ]

    prices = detail.get("Datasheets_models_cost.csv")
    rows = prices.grouped_by("datasheet_id").get(detail_id, []) if prices else []

    costs: list[CuratedDatasheetCost] = []
    for row in rows:
        label = strip_field(row.fields.get("description", ""), field="cost.label").text
        try:
            count = model_count(label, field="cost.model_count")
            points = to_int(row.fields.get("cost", ""), field="cost.points")
        except NumericParseError:
            continue
        costs.append(
            CuratedDatasheetCost(
                model_count=count,
                copy_index_min=1,
                points=points,
                label=label,
                pricing_confidence=PricingConfidenceState.UNVERIFIED,
                source_acquisition_id=detail_acquisition.acquisition_id,
            )
        )

    if not costs:
        return None, findings

    findings.append(
        build_finding(
            "PRC-UNVERIFIED",
            entity_refs=[f"wahapedia:{detail_id}"],
            detail={"faction_id": faction_id, "detail_datasheet_id": detail_id},
        )
    )

    datasheet_id = registry.mint(EntityKind.DATASHEET, normalize_name(display_name), display_name)
    fields, detail_findings = _detail_datasheet_fields(detail_id, detail)
    findings.extend(detail_findings)

    datasheet = CuratedDatasheet(
        datasheet_id=datasheet_id,
        edition_id=edition_id,
        faction_id=faction_id,
        name=display_name,
        role=fields.get("role"),  # type: ignore[arg-type]
        is_legends=bool(fields.get("is_legends", False)),
        is_character=bool(fields.get("is_character", False)),
        is_epic_hero=bool(fields.get("is_epic_hero", False)),
        is_battleline=bool(fields.get("is_battleline", False)),
        is_dedicated_transport=bool(fields.get("is_dedicated_transport", False)),
        max_copies_per_army=authored.copy_limit_for(datasheet_id),
        damaged_threshold=fields.get("damaged_threshold"),  # type: ignore[arg-type]
        models=fields.get("models", ()),  # type: ignore[arg-type]
        weapons=fields.get("weapons", ()),  # type: ignore[arg-type]
        keywords=fields.get("keywords", ()),  # type: ignore[arg-type]
        ability_keys=fields.get("ability_keys", ()),  # type: ignore[arg-type]
        leader_pairs=(),
        wargear_options=(),
        costs=costs,
        pricing_confidence=PricingConfidence(state=PricingConfidenceState.UNVERIFIED),
        provenance=provenance,
    )
    return datasheet, findings


def _attach_leader_pairs(
    datasheets: Sequence[CuratedDatasheet],
    detail: Mapping[str, CsvReadResult],
    detail_to_curated: Mapping[str, str],
) -> list[CuratedDatasheet]:
    """Attach leader pairings once every datasheet has an id.

    A second pass rather than an inline one, because a pairing names *two* datasheets and the
    second may not have been assembled yet when the first is. Pairings whose other end is not in
    the snapshot are dropped here rather than emitted — a dangling pair would be a blocking
    `CON-DANGLING-REF` for a relationship neither source disputes.
    """
    pairs = detail.get("Datasheets_leader.csv")
    if pairs is None:
        return list(datasheets)

    known = {ds.datasheet_id for ds in datasheets}

    attachments: dict[str, set[str]] = {}
    for row in pairs.rows:
        leader = detail_to_curated.get(row.fields.get("leader_id", ""))
        bodyguard = detail_to_curated.get(row.fields.get("attached_id", ""))
        if leader and bodyguard and leader in known and bodyguard in known:
            attachments.setdefault(leader, set()).add(bodyguard)

    if not attachments:
        return list(datasheets)

    return [
        datasheet.model_copy(update={"leader_pairs": sorted(attachments[datasheet.datasheet_id])})
        if datasheet.datasheet_id in attachments
        else datasheet
        for datasheet in datasheets
    ]
