# AI-Assisted: Claude Code (model: claude-opus-5) - Assemble the CuratedSnapshot from the two
# normalized sources plus the authored tree (needed by the T073 build wiring, which names the
# curate stage but assigns it no assembly module of its own).
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Built the datasheet_id -> source_id mapping
# `match_units` needs for its publication-id disambiguation step, alongside the existing
# `legends_sources` read of the same column, and passed it through as `detail_source_ids`.
# AI-Assisted: Claude Code (model: claude-opus-5) - Built structured composition and the full
# wargear option set (004 task T031): the two grammars, the two curator override files, the
# three-state wargear_option_state, and the replacement of _wargear_options()'s blanket
# CON-WARGEAR-COST-MISSING with the OPT-PRICED-UNMATCHED / unlinked-choice pair.
# AI-Assisted: Claude Code (model: claude-opus-5) - Set CuratedKeyword.keyword_class per binding
# and carried the chapter vocabulary onto the snapshot (004 task T039), then set
# CuratedFaction.army_rule_state and carried the authored faction rules (004 task T047).
# AI-Assisted: Claude Code (model: claude-opus-5) - Attached each detachment's rule identities and
# carried the authored detachment-rule records onto the snapshot (004 task T054), then the
# authored keyword glossary (004 task T061).
# AI-Assisted: Claude Code (model: claude-opus-5) - Built the datasheet_id -> faction-keyword view
# `match_units` needs for its chapter-keyword disambiguation step (docs/follow-ups.md item 4),
# read through the same IP strip the curated keyword rows go through so a curator's
# keyword-classes.json record means the same token in both places.
# AI-Assisted: Claude Code (model: claude-opus-5) - Carried each weapon line's ability keywords
# into CuratedWeaponLine (issue #4). They were stated by both detail modes and read by neither,
# so all 9,305 published weapon lines shipped with an empty keyword list and the glossary
# denominator never saw the one keyword class that is a mechanic by construction.
# AI-Assisted: Claude Code (model: claude-opus-5) - Made the detachment-rule join drop a detachment
# id the detail source publishes under two different names instead of resolving it to whichever
# row was read last (issue #5), so an ambiguous id costs a missing rule rather than a rule
# attributed to a detachment in another faction.
# AI-Assisted: Claude Code (model: claude-opus-5) - Wired `_detail_only_datasheet` to `_equipment`
# (006 T048 triage): a datasheet the points authority did not price was assembled with no default
# equipment at all, so 647 of the wh40k-11e-2026-08-2 candidate's 658 absent
# `default_equipment_state` values were a missing branch rather than the documented FR-016 omission.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 007 US2 (T022, T024, T025): confirmed
# `_option_structure`'s `object_role` ternary self-corrects the moment T021 populates
# `replaced_clause` for a legacy stem, wired `OPT-ITEM-OVERLONG` into `_choice_items`'s two
# length filters, and wired `OPT-SCOPE-UNRESOLVED`'s producer using the same `link_model_line`
# containment join `equipment_link.py` already uses for `EQP-GROUP-UNRESOLVED`.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 007 US3 (T040): wired `CuratedItemConstraint`
# assembly into `_option_structure` via the new `_item_constraint` helper, tried only after
# `parse_row` has already refused a row (research D4.2); threaded `options.item_constraints` onto
# both `CuratedDatasheet` construction sites.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 007 Release phase, Product Owner decision
# 2026-08-14 (T061 review): renamed `_refuse_header_row` to `_flag_header_row_candidate` and
# stopped it from ever dropping a row -- it only raises the advisory `CMP-HEADER-ROW` finding now.
# Wired the new `CompositionOverrideEntry.remove` shape into `_composition_entries`'s override
# branch, the only remaining path that removes a composition row.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 009 task T019: computes the faction-id
# vocabulary actually acquired this run (arm-agnostic) and passes it to `resolve_factions`, so
# `REC-DETAIL-FACTION-EMPTY` is live against real builds rather than only unit-tested -- the
# `plan.md` finding 1 silent-failure shape this feature exists to make loud.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 009 task T028: updated
# DETACHMENT_ABILITIES_FILE's comment now that it has joined EXPORT_FILES under the csv arm too.
# AI-Assisted: Claude Code (model: claude-opus-5) - 009 rung R01b: forward
# `carried_forward_detail_ids` to `resolve_factions`, so a faction carried forward from the
# previous published tree is not reported as an unexplained empty faction.
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
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Final

from pipeline.curate.authored import AuthoredContent
from pipeline.curate.summaries import detachment_rule_key
from pipeline.models.authored import OptionOverrideChoice
from pipeline.models.curated import (
    ArmyRuleState,
    CuratedCompositionEntry,
    CuratedDatasheet,
    CuratedDatasheetCost,
    CuratedDetachment,
    CuratedDetachmentRestriction,
    CuratedDetachmentRule,
    CuratedEdition,
    CuratedEditionRule,
    CuratedEnhancement,
    CuratedEquipmentGroup,
    CuratedEquipmentItem,
    CuratedFaction,
    CuratedGameSizeRule,
    CuratedItemConstraint,
    CuratedKeyword,
    CuratedModelLine,
    CuratedOptionChoice,
    CuratedOptionChoiceItem,
    CuratedOptionGroup,
    CuratedSnapshot,
    CuratedWargearOption,
    CuratedWeaponLine,
    DefaultEquipmentState,
    EquipmentAppliesTo,
    OptionItemRole,
    OptionScope,
    WargearOptionState,
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
from pipeline.normalize.weapon_abilities import parse_weapon_ability_keywords
from pipeline.parse.composition_grammar import link_model_line, parse_entry
from pipeline.parse.equipment_grammar import (
    EQUIPMENT_TABLE,
    equipment_group_id,
    equipment_state,
    parse_sentence,
)
from pipeline.parse.mfm_dom import MfmPage
from pipeline.parse.options_grammar import (
    MAX_CHOICE_NAME_CHARS,
    ItemParse,
    OptionVerb,
    choice_id,
    group_id,
    is_constraint_shaped,
    option_state,
    parse_constraint_row,
    parse_row,
    split_conjuncts,
    split_replaced,
)
from pipeline.parse.wahapedia_csv import CsvReadResult
from pipeline.reconcile.bands import reconcile_bands
from pipeline.reconcile.chapters import (
    apply_keyword_classes,
    classify_keywords,
    observed_keywords,
)
from pipeline.reconcile.composition_bands import reconcile_composition_bands
from pipeline.reconcile.conflicts import resolve_cost_conflict
from pipeline.reconcile.equipment_link import link_equipment
from pipeline.reconcile.identity import EntityKind, IdRegistry, slugify
from pipeline.reconcile.match import (
    FactionScope,
    UnitMatch,
    _detail_ids_for,
    datasheet_key,
    match_units,
    report_orphan_detail_factions,
    resolve_factions,
)
from pipeline.reconcile.options_link import (
    link_choice_items,
    link_choice_weapons,
    project_priced_options,
    weapon_lines_named,
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

#: A unit section heading that states a **condition** rather than naming a group. The points
#: source publishes both through the same structure: `ULTRAMARINES` heads a section of units
#: only that chapter may field — a partition, and no unit appears twice — while
#: `EVERY MODEL HAS THE IMPERIUM KEYWORD` heads a *second copy of the whole unit list* at
#: different prices. Only the conditional form yields a pricing context; a grouping yields none,
#: because grouping sections never collide. A section heading this does not match, over a unit
#: the page has already priced, is left to collide and block as `CON-DUPLICATE-KEY` rather than
#: being guessed at.
_PRICING_CONDITION: Final = re.compile(
    r"^EVERY\s+MODEL\s+HAS\s+THE\s+(?P<keyword>.+?)\s+KEYWORDS?$", re.IGNORECASE
)

#: A band label segment: its count, then whatever it calls the models it counts.
_BAND_SEGMENT: Final = re.compile(r"^\s*\d+\s*(?:-\s*\d+)?\s*(?P<name>.*?)\s*$")

#: `5 models` names no model *type*, so it says nothing about which composition is being priced.
_GENERIC_MODEL_NOUNS: Final[frozenset[str]] = frozenset({"model", "models"})

#: The detail source's role vocabulary, mapped onto the flags the consumer contract carries.
_BATTLELINE_ROLES: Final[frozenset[str]] = frozenset({"battleline"})
_CHARACTER_ROLES: Final[frozenset[str]] = frozenset({"characters", "character"})
_TRANSPORT_ROLES: Final[frozenset[str]] = frozenset({"dedicated transports", "dedicated transport"})

#: How a Legends datasheet is actually identified. **Not** the datasheet's own `legend` column:
#: that is flavour text, which this pipeline must not read at all, and 1 220 datasheets carry it
#: where only 569 are Legends. The real signal is the publication the datasheet came from, so it
#: is resolved through `source_id` into `Source.csv`.
_LEGENDS_SOURCE: Final = "legends"


@dataclass(slots=True)
class AssemblyResult:
    snapshot: CuratedSnapshot
    findings: list[Finding] = field(default_factory=list)
    datasheet_ids: dict[tuple[str, str], str] = field(default_factory=dict)
    """``(points-source faction slug, unit display name) -> curated datasheet_id``.

    Carried out of the stage rather than re-derived downstream: the delta cross-check needs the
    same pairing this stage decided, and a second derivation is a second chance to disagree.
    """
    wahapedia_datasheet_ids: dict[str, str] = field(default_factory=dict)
    """``curated datasheet_id -> detail source's own datasheet id`` (007 US5, T053).

    The inverse of this function's own internal ``detail_to_curated`` join, carried out for the
    same reason ``datasheet_ids`` above already is: the build-time equivalence check
    (:mod:`pipeline.validate.equivalence`) needs to look up a datasheet's raw ``detail`` rows
    while iterating the curated snapshot, and re-deriving the join from a datasheet's name would
    be a second chance for it to disagree with the one this stage already decided. Present only
    for datasheets the detail source actually contributed to (points-only entries have none).
    """


def _composition_lines(detail_id: str | None, detail: Mapping[str, CsvReadResult]) -> list[str]:
    """The detail source's composition lines for one datasheet, in file order."""
    rows = detail.get("Datasheets_unit_composition.csv")
    if rows is None or detail_id is None:
        return []
    return [
        strip_field(row.fields.get("description", ""), field="composition").text
        for row in rows.grouped_by("datasheet_id").get(detail_id, [])
    ]


def _detail_prices(detail_id: str | None, detail: Mapping[str, CsvReadResult]) -> dict[int, int]:
    """``model_count -> points`` as the **detail** source publishes them.

    Read for two purposes only: to price a datasheet the points authority did not publish this
    release (FR-035), and to notice a disagreement about one it did (FR-028). It is never a
    fallback for a value the points source published — that would be the losing value of a
    conflict quietly coming back.
    """
    rows = detail.get("Datasheets_models_cost.csv")
    if rows is None or detail_id is None:
        return {}

    prices: dict[int, int] = {}
    for row in rows.grouped_by("datasheet_id").get(detail_id, []):
        label = strip_field(row.fields.get("description", ""), field="cost.label").text
        try:
            prices[model_count(label, field="cost.model_count")] = to_int(
                row.fields.get("cost", ""), field="cost.points"
            )
        except NumericParseError:
            continue
    return prices


def _tier_indices(label: str) -> int:
    """The `copy_index_min` a cost-table label states. A plain table is the first copy."""
    match = _TIER_THRESHOLD.search(label)
    return int(match.group(1)) if match else 1


@dataclass(frozen=True, slots=True)
class _Band:
    """One extracted size band, before its context is settled — internal to `_costs`."""

    copy_index: int
    model_count: int
    points: int
    label: str
    context: str | None


def _army_context(section_label: str) -> str | None:
    """The pricing context a unit *section* heading states, or `None` for the default one.

    `None` is the answer for twenty-nine of the thirty faction pages and for every unit on them:
    absence means "the price this unit costs in its own army", which is what every cost row has
    always meant, so nothing that already exists changes meaning by this field arriving.
    """
    match = _PRICING_CONDITION.match(section_label.strip())
    if match is None:
        return None
    return f"every-model-has-{slugify(match.group('keyword'))}"


def _band_model_types(label: str) -> frozenset[str]:
    """The model **types** a band label names, casefolded. `5 models` names none."""
    names: set[str] = set()
    for segment in label.split(","):
        match = _BAND_SEGMENT.match(segment)
        if match is None:
            continue
        name = match.group("name").strip().casefold()
        if name and name not in _GENERIC_MODEL_NOUNS:
            names.add(name)
    return frozenset(names)


def _composition_contexts(bands: Sequence[_Band]) -> list[str | None]:
    """A pricing context for the bands a model count cannot tell apart.

    The points source prices some units on two axes. `WOLF GUARD HEADTAKERS` is priced at
    `3 Wolf Guard Headtakers`, `3 Wolf Guard Headtakers, 3 Hunting Wolves`, `6 Wolf Guard
    Headtakers` and `6 Wolf Guard Headtakers, 6 Hunting Wolves` — and the second and third of
    those are **both six-model units**, at 115 and 170 points. No single model count separates
    them, so the consumer's `(datasheet_id, model_count)` key cannot hold both, and dropping
    either publishes a price nobody chose (`reference-db-schema.md` §3.8).

    So where two bands do collide, the thing that distinguishes them is used: the model types
    some bands name and others do not. `Hunting Wolves` becomes `with-hunting-wolves` and the
    two bands that include them move to their own context, leaving the plain size bands exactly
    where a consumer has always found them.

    **Only where they collide.** A datasheet whose bands already have distinct model counts is
    returned untouched, which is all but one of the 2 083 priced datasheets in the tree — the
    context exists to disambiguate, not to reclassify. Two colliding bands with nothing to tell
    them apart are also returned untouched, and block as `CON-DUPLICATE-KEY`.
    """
    contexts = [band.context for band in bands]
    collisions = Counter((band.copy_index, band.model_count, band.context) for band in bands)
    if all(count == 1 for count in collisions.values()):
        return contexts

    per_band = [_band_model_types(band.label) for band in bands]
    shared = frozenset.intersection(*per_band)
    optional = frozenset().union(*per_band) - shared
    for index, (band, own) in enumerate(zip(bands, per_band, strict=True)):
        extra = sorted(own & optional)
        if band.context is None and extra:
            contexts[index] = "with-" + "-and-".join(slugify(name) for name in extra)
    return contexts


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

    **A unit priced twice on one page is priced twice, not printed twice.** The Imperial Agents
    page carries every one of its twenty-nine units in two sections, the second headed
    `EVERY MODEL HAS THE IMPERIUM KEYWORD`, and nineteen of those pairs disagree about the
    price. The section heading is the only place the page says which price is which, so it
    becomes the row's `pricing_context` — absent for the unit's own-army price, explicit for the
    conditional one. Without it the two rows arrive indistinguishable and one of them is a
    `CON-DUPLICATE-KEY`.
    """
    bands: list[_Band] = []
    options: list[CuratedWargearOption] = []
    findings: list[Finding] = []

    for block in blocks:
        copy_index = _tier_indices(block.cost_table_label)
        context = _army_context(block.cost_section_label)
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
            bands.append(
                _Band(
                    copy_index=copy_index,
                    model_count=count,
                    points=row.points,
                    label=label,
                    context=context,
                )
            )

    rows = [
        CuratedDatasheetCost(
            model_count=band.model_count,
            copy_index_min=band.copy_index,
            points=band.points,
            label=band.label,
            pricing_context=context,
            pricing_confidence=PricingConfidenceState.VERIFIED,
            source_acquisition_id=acquisition_id,
        )
        for band, context in zip(bands, _composition_contexts(bands), strict=True)
    ]
    return rows, _deduplicate_options(options), findings


def _deduplicate_options(
    options: Sequence[CuratedWargearOption],
) -> list[CuratedWargearOption]:
    """One row per option id. The threshold pair prints the same wargear row in both tables."""
    unique: dict[str, CuratedWargearOption] = {}
    for option in options:
        unique.setdefault(option.id, option)
    return sorted(unique.values(), key=lambda option: option.id)


def _legends_source_ids(detail: Mapping[str, CsvReadResult]) -> frozenset[str]:
    """The publication ids that make a datasheet Legends."""
    sources = detail.get("Source.csv")
    if sources is None:
        return frozenset()
    return frozenset(
        row.fields["id"]
        for row in sources.rows
        if _LEGENDS_SOURCE
        in f"{row.fields.get('name', '')} {row.fields.get('type', '')}".casefold()
    )


def _faction_keywords_by_datasheet(
    detail: Mapping[str, CsvReadResult],
) -> dict[str, frozenset[str]]:
    """``datasheet_id -> the faction keywords it carries``, for the match ladder's rung 3.

    Only the *faction* keywords, because only those can name a chapter — a unit keyword shared by
    two datasheets says nothing about which faction may field either. Read through the same
    ``strip_field`` the curated keyword rows go through, so the token a curator writes in
    ``curation/keyword-classes.json`` means one thing across both files rather than two.
    """
    keywords = detail.get("Datasheets_keywords.csv")
    if keywords is None:
        return {}
    by_datasheet: dict[str, set[str]] = {}
    for row in keywords.rows:
        if row.fields.get("is_faction_keyword", "").strip().casefold() != "true":
            continue
        text = strip_field(row.fields.get("keyword", ""), field="keyword").text
        if not text:
            continue
        by_datasheet.setdefault(row.fields.get("datasheet_id", ""), set()).add(text)
    return {datasheet_id: frozenset(values) for datasheet_id, values in by_datasheet.items()}


def _detail_datasheet_fields(
    detail_id: str,
    detail: Mapping[str, CsvReadResult],
    legends_sources: frozenset[str] = frozenset(),
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
    fields["is_legends"] = row.fields.get("source_id", "") in legends_sources
    fields["damaged_threshold"] = upper_bound(row.fields.get("damaged_w"), field="damaged_w")

    models: list[CuratedModelLine] = []
    for model in detail["Datasheets_models.csv"].grouped_by("datasheet_id").get(detail_id, []):
        # A nameless line is a defect in the export, not a nameless model. Emitting it would put
        # an empty string into a NOT NULL column the app renders; skipping it and saying so
        # keeps the rest of the datasheet, which is the useful part.
        if not strip_field(model.fields.get("name", ""), field="model.name").text:
            findings.append(
                build_finding(
                    "DQ-MALFORMED-ROW",
                    entity_refs=[f"wahapedia:{detail_id}"],
                    detail={"file_name": "Datasheets_models.csv", "field": "name"},
                )
            )
            continue
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
    for line_number, weapon in enumerate(
        detail["Datasheets_wargear.csv"].grouped_by("datasheet_id").get(detail_id, []), start=1
    ):
        if not strip_field(weapon.fields.get("name", ""), field="weapon.name").text:
            findings.append(
                build_finding(
                    "DQ-MALFORMED-ROW",
                    entity_refs=[f"wahapedia:{detail_id}"],
                    detail={"file_name": "Datasheets_wargear.csv", "field": "name"},
                )
            )
            continue
        weapon_range = optional_characteristic(weapon.fields.get("range"))
        is_melee = (weapon.fields.get("type", "") or "").strip().casefold() == "melee"
        try:
            # `line` is minted from the row's own position in this datasheet's weapon list, not
            # read off the export's `line` column (009 Finding A, CON-DUPLICATE-KEY, 39 live
            # instances). The export's `line` numbers a wargear CHOICE, not a row: a multi-profile
            # weapon (plasma standard/supercharge, missile frag/krak, ...) states two rows under
            # one `line`, disambiguated only by `line_in_wargear` -- a column nothing here reads.
            # The html arm never had this collision, because its own scraper
            # (`wahapedia_html_dom.py::_weapon_profiles`) mints a fresh sequential number per row
            # it prints rather than reading one off the page, which is exactly what `line_number`
            # reproduces for the export too. `to_int` below still validates the raw column parses
            # -- a row whose own `line` is genuinely malformed is still `DQ-MALFORMED-ROW` -- it
            # is simply no longer what identifies the row.
            to_int(weapon.fields["line"], field="weapon.line")
            weapons.append(
                CuratedWeaponLine(
                    line=line_number,
                    name=strip_field(weapon.fields["name"], field="weapon.name").text,
                    is_melee=is_melee,
                    range=None if is_melee else weapon_range,
                    attacks=weapon.fields["A"].strip() or "-",
                    skill=weapon.fields["BS_WS"].strip() or "-",
                    strength=weapon.fields["S"].strip() or "-",
                    armour_penetration=weapon.fields["AP"].strip() or "0",
                    damage=weapon.fields["D"].strip() or "-",
                    # Issue #4. The keywords are stated in the export's `description` column,
                    # which also carries free prose — so the field is IP-stripped first and then
                    # read by the bracketed-group rule, which takes the keyword list and nothing
                    # else. Both detail modes reach this line: html mode re-emits the keywords
                    # its cards print into the same column, in the same shape.
                    ability_keywords=parse_weapon_ability_keywords(
                        strip_field(
                            weapon.fields.get("description", ""),
                            field="weapon.ability_keywords",
                        ).text
                    ),
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
    # Dedicated transport reads the same way, and it has to: the current-edition source publishes
    # no role column at all, and `DEDICATED TRANSPORT` is a keyword there exactly as
    # `EPIC HERO` is. Keeping the role as the second test costs nothing and leaves the previous
    # edition's reading untouched (`004` T074).
    fields["is_dedicated_transport"] = (
        "dedicated transport" in keyword_set or role_key in _TRANSPORT_ROLES
    )

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


@dataclass(slots=True)
class _OptionOutcome:
    """One datasheet's full option set, as `004`'s US1 produces it."""

    groups: list[CuratedOptionGroup] = field(default_factory=list)
    choices: list[CuratedOptionChoice] = field(default_factory=list)
    state: WargearOptionState | None = None
    findings: list[Finding] = field(default_factory=list)
    #: 007-loadout-display-fidelity US3: restrictions the same option rows state, captured
    #: alongside the option set they were refused out of rather than in a second pass over the
    #: same file (research D4.2).
    item_constraints: list[CuratedItemConstraint] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class _ConstraintOutcome:
    """One option row's fate against the item-constraint vocabulary (007 T039, T040).

    ``recognized`` is what lets the caller choose between the three advisory outcomes: a
    constraint present means it resolved (linked or not); ``recognized`` true with no constraint
    means it looked like a restriction but matched no vocabulary member (``CST-UNPARSED``); both
    false means the row was never restriction-shaped at all, and the caller's own ``OPT-UNPARSED``
    handling is unchanged (research D4.2).
    """

    constraint: CuratedItemConstraint | None
    findings: tuple[Finding, ...]
    recognized: bool


def _item_constraint(
    line: int, description: str, *, datasheet_id: str, weapons: Sequence[CuratedWeaponLine]
) -> _ConstraintOutcome:
    """One option row, tried against the item-constraint vocabulary after `parse_row` refused it.

    ``constraint_index`` is the row's own source ordinal (``line``), never re-numbered —
    :class:`CuratedCompositionEntry`'s ``line`` pattern, reused unchanged (data-model.md §1.1).
    Linking reuses :func:`~pipeline.reconcile.options_link.weapon_lines_named`'s exactly-one-match
    join — the same rule every other name-to-weapon join in this module uses — rather than a
    second linking rule invented for this one entity.
    """
    parsed = parse_constraint_row(description)
    if parsed is not None:
        matches = weapon_lines_named(parsed.item_name, weapons)
        weapon_line = matches[0] if len(matches) == 1 else None
        findings: list[Finding] = []
        if weapon_line is None:
            findings.append(
                build_finding(
                    "CST-UNLINKED",
                    entity_refs=[datasheet_id],
                    detail={
                        "datasheet_id": datasheet_id,
                        "constraint_index": line,
                        "item_name": parsed.item_name,
                        "match_count": len(matches),
                    },
                )
            )
        constraint = CuratedItemConstraint(
            constraint_index=line,
            constraint_type=parsed.constraint_type,
            item_name=parsed.item_name,
            weapon_line=weapon_line,
            model_name=parsed.model_name,
        )
        return _ConstraintOutcome(constraint=constraint, findings=tuple(findings), recognized=True)

    if is_constraint_shaped(description):
        finding = build_finding(
            "CST-UNPARSED",
            entity_refs=[datasheet_id],
            detail={
                "datasheet_id": datasheet_id,
                "line": line,
                "file_name": "Datasheets_options.csv",
            },
        )
        return _ConstraintOutcome(constraint=None, findings=(finding,), recognized=True)

    return _ConstraintOutcome(constraint=None, findings=(), recognized=False)


@dataclass(slots=True)
class _EquipmentOutcome:
    """One datasheet's default equipment (`006` US2), and how completely it extracted.

    ``groups`` is a tuple rather than a list because its default is the empty one and the
    suppression path returns it unchanged — the FR-016 case is *literally nothing*, and a shared
    mutable default is the one way that could stop being true.
    """

    groups: tuple[CuratedEquipmentGroup, ...] = ()
    state: DefaultEquipmentState | None = None
    findings: list[Finding] = field(default_factory=list)


def _row_ordinal(raw: str, *, field_name: str) -> int | None:
    """The source's own row ordinal, or ``None`` when it is missing or not a positive integer.

    The ordinal *is* the identity of an option group (FR-015) and the display order of a
    composition entry, so a row without a usable one cannot be published under a stable id and
    is handed to the residual rather than given a synthesised ordinal that would move between
    runs.

    Takes the raw *field*, not the source record. ``tests/ip/test_stage_boundary.py`` forbids
    this module importing ``WahapediaRow`` at all — the one source-side type that carries prose
    — and the boundary is worth more than the two characters it costs at each call site.
    """
    try:
        line = to_int(raw, field=field_name)
    except NumericParseError:
        return None
    return line if line >= 1 else None


def _composition_entries(
    detail_id: str,
    datasheet_id: str,
    detail: Mapping[str, CsvReadResult],
    authored: AuthoredContent,
    models: Sequence[CuratedModelLine],
) -> tuple[list[CuratedCompositionEntry], list[Finding]]:
    """One datasheet's structured composition — **all of it, or none of it** (FR-008).

    A single line the grammar cannot resolve suppresses the whole datasheet's composition. That
    is deliberate and it is the spec's own wording: "published without composition rather than
    with a guessed count". A partial composition is the worst of the three states, because it
    looks complete — a reader sums it, gets a smaller unit than the rules describe, and nothing
    anywhere says a line is missing.

    A curator resolves the line once in ``curation/composition-overrides.json`` and the finding
    disappears with it. The pipeline never writes that file.
    """
    rows = detail.get("Datasheets_unit_composition.csv")
    if rows is None:
        return [], []

    model_names = {model.line: model.name for model in models}
    entries: list[CuratedCompositionEntry] = []
    findings: list[Finding] = []
    unresolved = False

    for row in rows.grouped_by("datasheet_id").get(detail_id, []):
        line = _row_ordinal(row.fields.get("line", ""), field_name="composition.line")
        override = authored.composition_override_for(datasheet_id, line) if line else None
        if line is not None and override is not None:
            if override.remove:
                # 007, Product Owner decision 2026-08-14 T061 review: the only path left that
                # removes a composition row at all. The row is dropped entirely -- no entry, no
                # CMP-UNRESOLVED, no CMP-HEADER-ROW -- because a curator has already confirmed it
                # is a phantom and removed it, the same finality `remove` gives an equivalence
                # check's `not_compared` case has no analogue to.
                continue
            assert override.model_name is not None
            assert override.min_count is not None
            assert override.max_count is not None
            entries.append(
                CuratedCompositionEntry(
                    line=line,
                    model_name=override.model_name,
                    min_count=override.min_count,
                    max_count=override.max_count,
                    model_line=override.model_line,
                )
            )
            continue

        parsed = parse_entry(row.fields.get("description", "")) if line is not None else None
        if line is None or parsed is None:
            unresolved = True
            findings.append(
                build_finding(
                    "CMP-UNRESOLVED",
                    entity_refs=[datasheet_id],
                    detail={
                        "datasheet_id": datasheet_id,
                        "line": line if line is not None else 0,
                        "file_name": "Datasheets_unit_composition.csv",
                    },
                )
            )
            continue

        entries.append(
            CuratedCompositionEntry(
                line=line,
                model_name=parsed.model_name,
                min_count=parsed.min_count,
                max_count=parsed.max_count,
                model_line=link_model_line(parsed.model_name, model_names),
            )
        )

    if unresolved:
        return [], findings

    ordered = sorted(entries, key=lambda entry: entry.line)
    header_finding = _flag_header_row_candidate(datasheet_id, ordered)
    if header_finding is not None:
        findings.append(header_finding)
    return ordered, findings


def _flag_header_row_candidate(
    datasheet_id: str, entries: Sequence[CuratedCompositionEntry]
) -> Finding | None:
    """Issue #15's phantom unit-size header — flagged for human review, **never auto-dropped**.

    research D1: the header line is a *valid parse* of the fixed composition production — an
    integer, then a name — so nothing on the line itself says it is not a model row. The
    discriminating evidence is a **conjunction of five independent structural signals**, applied
    here rather than in ``pipeline/parse/composition_grammar.py``, which stays mode-blind and
    untouched:

    1. it is the first row of the datasheet's composition list;
    2. at least one row follows it;
    3. its minimum equals its maximum (a header states one number, not a range);
    4. its count equals the sum of the maxima of the rows that follow it — a first row that
       equals the aggregate of its successors is a *total*, not a part;
    5. its name resolves to no model entry of the datasheet.

    **Superseded design, recorded so it is not silently reintroduced (Product Owner decision,
    2026-08-14 T061 review of the live corpus's T031 re-derivation).** This function used to
    *return* the row set with the flagged row removed (T030's original design: an automatic,
    blocking refusal). The live corpus proved the conjunction's own documented false-positive
    risk (R-1/R-A) real: of the rows it would have auto-dropped, three were genuine duo-sheet
    first models (``Rein`` of ``astra-militarum:Rein-And-Raus``, the Techmarine Gunner leading
    ``space-marines:Thunderfire-Cannon``, ``Ri'Lantar`` leading ``t-au-empire:The-Twin-Lance``) —
    each one fixed-size, unlinked (its own name does not textually match its ``datasheet_model``
    row), and numerically equal to the total of its one squad-mate, which is exactly what a real
    duo's model count looks like. Automatic removal is not safe at this precision; **this
    function now only raises the advisory finding**, and a row leaves the published composition
    only via a curator's explicit ``remove`` entry in
    ``curation/composition-overrides.json`` (§_composition_entries's override branch, above) —
    matched against a genuine phantom by a human, the same discipline every other override in
    this file already applies. ``tools/composition_header_refusal_report.py`` (T031) is now this
    advisory's review-queue generator, not a post-hoc check of an automatic refusal.

    Each signal alone has a plausible false positive (a genuine first row can be fixed-size, can
    fail to link, and a two-row card can coincidentally sum); requiring all five at once is what
    lets GF15's near-miss go unflagged while GF13/GF14's two measured header shapes are both
    flagged — but, per the finding above, "flagged" is no longer "refused".
    """
    if len(entries) < 2:
        return None

    first, *rest = entries
    is_fixed = first.min_count == first.max_count
    sums_to_successors = first.max_count == sum(entry.max_count for entry in rest)
    is_unlinked = first.model_line is None

    if not (is_fixed and sums_to_successors and is_unlinked):
        return None

    return build_finding(
        "CMP-HEADER-ROW",
        entity_refs=[datasheet_id],
        detail={
            "datasheet_id": datasheet_id,
            "line": first.line,
            "model_name": first.model_name,
            "file_name": "Datasheets_unit_composition.csv",
        },
    )


def _equipment(
    detail_id: str,
    datasheet_id: str,
    detail: Mapping[str, CsvReadResult],
    authored: AuthoredContent,
    composition: Sequence[CuratedCompositionEntry],
    weapons: Sequence[CuratedWeaponLine],
) -> _EquipmentOutcome:
    """One datasheet's default equipment — but **only** if its composition stands (FR-016).

    Two suppressions, and they are different facts sharing one representation. A datasheet whose
    composition did not resolve carries no equipment at all: every sentence this feature can state
    attaches either to the unit or to one of the composition rows, and attaching a loadout to a
    structure the pipeline has already refused to publish would be an assertion about models
    nobody can enumerate. A run that never consulted the equipment source — every ``csv``-mode
    run, where the export publishes no such table — carries none either. Both leave
    ``default_equipment_state`` **omitted**, which is precisely what data-model.md §3 means by
    the fourth state being the absence of a value.

    Note the asymmetry with :func:`_composition_entries` above, and that it is deliberate: an
    unresolved composition line suppresses the whole datasheet's composition, while an unresolved
    equipment sentence suppresses **only itself** and the datasheet becomes ``partial``. A partial
    composition under-counts a unit and therefore mis-prices it; a partial loadout under-states
    what a model carries, and what did resolve is still true.
    """
    if not composition:
        return _EquipmentOutcome()
    rows = detail.get(EQUIPMENT_TABLE)
    if rows is None:
        return _EquipmentOutcome()

    source_rows = rows.grouped_by("datasheet_id").get(detail_id, [])
    parsed_groups: list[CuratedEquipmentGroup] = []
    authored_groups: list[CuratedEquipmentGroup] = []
    findings: list[Finding] = []
    unparsed = 0

    for row in source_rows:
        line = _row_ordinal(row.fields.get("line", ""), field_name="equipment.line")
        override = authored.equipment_override_for(datasheet_id, line) if line else None
        if line is not None and override is not None:
            # 008 FR-011/T068: tried anyway and DISCARDED — the override still wins, structurally,
            # by `continue`-ing below with the override's own values regardless of what comes
            # back. The only thing this changes is whether a production now ALSO reaches the row,
            # which is advisory information for a curator deciding whether to retire the entry,
            # never a reason to prefer the production's answer over the human's.
            if parse_sentence(row.fields.get("description", "")) is not None:
                findings.append(
                    build_finding(
                        "OPT-OVERRIDE-REDUNDANT",
                        entity_refs=[datasheet_id],
                        detail={
                            "datasheet_id": datasheet_id,
                            "line": line,
                            "file_name": "equipment-overrides.json",
                        },
                    )
                )
            authored_groups.append(
                CuratedEquipmentGroup(
                    id=equipment_group_id(datasheet_id, line),
                    line=line,
                    applies_to=EquipmentAppliesTo(override.applies_to),
                    model_name=override.model_name,
                    composition_line=override.composition_line,
                    items=tuple(
                        CuratedEquipmentItem(
                            item_index=index,
                            item_name=item.item_name,
                            count=item.count,
                            weapon_line=item.weapon_line,
                        )
                        for index, item in enumerate(override.items, start=1)
                    ),
                )
            )
            continue

        parsed = parse_sentence(row.fields.get("description", "")) if line is not None else None
        if line is None or parsed is None:
            unparsed += 1
            findings.append(
                build_finding(
                    "EQP-UNPARSED",
                    entity_refs=[datasheet_id],
                    detail={
                        "datasheet_id": datasheet_id,
                        "line": line if line is not None else 0,
                        "file_name": EQUIPMENT_TABLE,
                    },
                )
            )
            continue

        parsed_groups.append(
            CuratedEquipmentGroup(
                id=equipment_group_id(datasheet_id, line),
                line=line,
                applies_to=parsed.applies_to,
                model_name=parsed.model_name,
                items=tuple(
                    CuratedEquipmentItem(
                        item_index=index, item_name=item.item_name, count=item.count
                    )
                    for index, item in enumerate(parsed.items, start=1)
                ),
            )
        )

    # A curator-authored group already states its own links, so it is not re-joined: doing so
    # would let a name match overrule the human who wrote the override.
    linked, link_findings = link_equipment(
        datasheet_id=datasheet_id, groups=parsed_groups, composition=composition, weapons=weapons
    )
    findings.extend(link_findings)

    return _EquipmentOutcome(
        groups=tuple(sorted([*linked, *authored_groups], key=lambda group: group.id)),
        state=equipment_state(sentence_count=len(source_rows), unparsed_count=unparsed),
        findings=findings,
    )


def _option_structure(  # noqa: PLR0913 - composition is needed to resolve a scoped stem's subject
    detail_id: str,
    datasheet_id: str,
    detail: Mapping[str, CsvReadResult],
    authored: AuthoredContent,
    weapons: Sequence[CuratedWeaponLine],
    priced: Sequence[CuratedWargearOption],
    composition: Sequence[CuratedCompositionEntry] = (),
) -> _OptionOutcome:
    """One datasheet's full option set — not only the cost-bearing subset (FR-010).

    This replaces what used to be a blanket ``CON-WARGEAR-COST-MISSING`` per option row: the
    structure is now extracted, and the two findings that remain say something an approver can
    act on — ``OPT-UNPARSED`` for a row the grammar did not match, and the
    ``OPT-PRICED-UNMATCHED`` / unlinked-choice pair from the joins.

    ``priced`` is the untouched output of :func:`_costs`. It is read and never rebuilt, which is
    what keeps SC-004's byte-identical priced projection a structural property.
    """
    rows = detail.get("Datasheets_options.csv")
    if rows is None:
        # The source was not consulted at all: the state is **omitted**, which is a different
        # fact from `none` (FR-016).
        return _OptionOutcome()

    source_rows = rows.grouped_by("datasheet_id").get(detail_id, [])
    # 007 T025: the same exactly-one-match containment join `equipment_link.py` uses to resolve
    # an equipment sentence's subject, reused here for a scoped option stem's eligibility
    # subject — `OPT-SCOPE-UNRESOLVED`'s producer, wired the moment FR-004 makes a legacy stem
    # state a subject at all (research D3.4).
    model_names = {entry.line: entry.model_name for entry in composition}
    groups: list[CuratedOptionGroup] = []
    parsed_choices: list[CuratedOptionChoice] = []
    authored_choices: list[CuratedOptionChoice] = []
    object_roles: dict[str, OptionItemRole] = {}
    replaced_clauses: dict[str, str | None] = {}
    findings: list[Finding] = []
    item_constraints: list[CuratedItemConstraint] = []
    unparsed = 0

    for row in source_rows:
        line = _row_ordinal(row.fields.get("line", ""), field_name="option.line")
        override = authored.option_override_for(datasheet_id, line) if line else None
        if line is not None and override is not None:
            # 008 FR-011/T067: tried anyway and DISCARDED, mirroring `_equipment`'s own branch
            # above — the override still wins structurally, by `continue`-ing below regardless of
            # what `parse_row` returns.
            if parse_row(row.fields.get("description", "")) is not None:
                findings.append(
                    build_finding(
                        "OPT-OVERRIDE-REDUNDANT",
                        entity_refs=[datasheet_id],
                        detail={
                            "datasheet_id": datasheet_id,
                            "line": line,
                            "file_name": "option-overrides.json",
                        },
                    )
                )
            groups.append(
                CuratedOptionGroup(
                    id=group_id(datasheet_id, line),
                    line=line,
                    scope=OptionScope(override.scope),
                    scope_n=override.scope_n,
                    min_choices=override.min_choices,
                    max_choices=override.max_choices,
                    # `006` FR-011: every new member is optional, so a `004`-shaped override
                    # carries `None` here and resolves exactly as it did.
                    eligible_model_name=override.eligible_model_name,
                    eligible_max_count=override.eligible_max_count,
                    is_per_model=override.is_per_model,
                )
            )
            authored_choices.extend(
                CuratedOptionChoice(
                    id=choice_id(group_id(datasheet_id, line), index),
                    group_id=group_id(datasheet_id, line),
                    name=choice.name,
                    count=choice.count,
                    grants_weapon_line=choice.grants_weapon_line,
                    replaces_weapon_line=choice.replaces_weapon_line,
                    is_default=choice.is_default,
                    is_no_change=choice.is_no_change,
                    items=_authored_items(choice),
                )
                for index, choice in enumerate(override.choices, start=1)
            )
            continue

        description = row.fields.get("description", "")
        parsed = parse_row(description) if line is not None else None
        if line is None or parsed is None:
            # 007 US3 (T039/T040): a row `parse_row` could not resolve as an option gets one more
            # chance — against the closed item-constraint vocabulary — before it is reported as
            # unparsed. Tried only here, after `parse_row` has already failed, so no row that
            # resolves as an option today can ever reach this branch (research D4.2, rule 3/4).
            outcome = (
                _item_constraint(line, description, datasheet_id=datasheet_id, weapons=weapons)
                if line is not None
                else None
            )
            if outcome is not None:
                findings.extend(outcome.findings)
                if outcome.constraint is not None:
                    item_constraints.append(outcome.constraint)
                    continue
                if outcome.recognized:
                    # Restriction-shaped but out of vocabulary: CST-UNPARSED already names the
                    # row's fate. Raising OPT-UNPARSED too would report the same row under two
                    # codes for two readings of one failure — still counted toward `unparsed` for
                    # `wargear_option_state`, since nothing option-shaped came of it either.
                    unparsed += 1
                    continue

            unparsed += 1
            findings.append(
                build_finding(
                    "OPT-UNPARSED",
                    entity_refs=[datasheet_id],
                    detail={
                        "datasheet_id": datasheet_id,
                        "line": line if line is not None else 0,
                        "file_name": "Datasheets_options.csv",
                    },
                )
            )
            continue

        group = group_id(datasheet_id, line)
        groups.append(
            CuratedOptionGroup(
                id=group,
                line=line,
                scope=parsed.scope,
                scope_n=parsed.scope_n,
                min_choices=parsed.min_choices,
                max_choices=parsed.max_choices,
                eligible_model_name=parsed.eligible_model_name,
                eligible_max_count=parsed.eligible_max_count,
                is_per_model=parsed.is_per_model,
            )
        )
        if parsed.eligible_model_name is not None and (
            link_model_line(parsed.eligible_model_name, model_names) is None
        ):
            # The value ships exactly as the source states it, unchecked — this is advisory,
            # never a suppression, per the 2026-08-09 clarification `006` already wrote the code
            # for and never wired (research D3.4).
            findings.append(
                build_finding(
                    "OPT-SCOPE-UNRESOLVED",
                    entity_refs=[datasheet_id, group],
                    detail={
                        "datasheet_id": datasheet_id,
                        "group_id": group,
                        "eligible_model_name": parsed.eligible_model_name,
                    },
                )
            )
        for index, choice in enumerate(parsed.choices, start=1):
            identifier = choice_id(group, index)
            # Which side the object clause sits on, and therefore which singular field it may
            # occupy. A `004` replacement clause names its object in `replaces_weapon_line` and
            # keeps doing so; a distributive stem states the removed weapon in its own head
            # instead, so its object is the granted side and its head is the replaced one.
            object_role = (
                OptionItemRole.REPLACED
                if parsed.replaced_clause is None and choice.verb is OptionVerb.REPLACE
                else OptionItemRole.GRANTED
            )
            object_roles[identifier] = object_role
            replaced_clauses[identifier] = parsed.replaced_clause
            parsed_choices.append(
                CuratedOptionChoice(
                    id=identifier,
                    group_id=group,
                    name=choice.name,
                    count=choice.count,
                    is_no_change=choice.is_no_change,
                )
            )

    # A curator-authored structure already states its own links, so it is not re-joined: doing
    # so would let a name match overrule the human who wrote the override.
    linked, link_findings = link_choice_weapons(
        datasheet_id=datasheet_id, choices=parsed_choices, weapons=weapons
    )
    findings.extend(link_findings)

    # Decomposition runs AFTER the singular join, and that ordering is the O1 Ruling: whether a
    # choice's name is one item or several is decided by whether the baseline already matched it
    # to exactly one weapon — recomputed here directly (007 T023) rather than read off
    # `grants_`/`replaces_weapon_line`, since `link_choice_weapons` no longer writes either field.
    decomposed = []
    for linked_choice in linked:
        items, overlong_findings = _choice_items(
            linked_choice,
            datasheet_id=datasheet_id,
            object_role=object_roles[linked_choice.id],
            replaced_clause=replaced_clauses[linked_choice.id],
            weapons=weapons,
        )
        findings.extend(overlong_findings)
        decomposed.append(linked_choice.model_copy(update={"items": items}))
    item_linked, item_findings = link_choice_items(
        datasheet_id=datasheet_id, choices=decomposed, weapons=weapons
    )
    findings.extend(item_findings)

    choices, price_findings = project_priced_options(
        datasheet_id=datasheet_id, choices=[*item_linked, *authored_choices], priced=priced
    )
    findings.extend(price_findings)

    return _OptionOutcome(
        groups=sorted(groups, key=lambda group: group.id),
        choices=sorted(choices, key=lambda choice: choice.id),
        state=option_state(row_count=len(source_rows), unparsed_count=unparsed),
        findings=findings,
        item_constraints=sorted(
            item_constraints, key=lambda constraint: constraint.constraint_index
        ),
    )


def _choice_items(
    choice: CuratedOptionChoice,
    *,
    datasheet_id: str,
    object_role: OptionItemRole,
    replaced_clause: str | None,
    weapons: Sequence[CuratedWeaponLine],
) -> tuple[tuple[CuratedOptionChoiceItem, ...], list[Finding]]:
    """Every choice's items, including every pre-existing single-item one (`006` §1.1).

    The redundancy is deliberate and load-bearing: a consumer iterates items uniformly, and the
    spec's *one-element bundle must not diverge* edge case becomes guarantee 12 — an invariant
    checked on every build rather than an intention.

    **Decomposition is refused for a name that matches a weapon row on its own.** An exactly-one
    weapon match on the choice's *whole* name is itself the evidence that the name is one item,
    so such a choice gets its one mirroring row and nothing is split. That is the O1 Ruling's
    other half, and with it the 144 currently-parsing rows whose names conflate a bundle gain
    machine-readable items while not one value a consumer already reads changes.

    **007 T023**: this evidence is recomputed here via
    :func:`pipeline.reconcile.options_link.weapon_lines_named` rather than read off
    ``grants_``/``replaces_weapon_line`` — `link_choice_weapons` no longer writes either field
    (research D3), so the field itself can no longer carry the "already matched" signal.

    **007 T024**: an item name exceeding ``MAX_CHOICE_NAME_CHARS`` is dropped here — unchanged
    from `006` — but now raises the advisory ``OPT-ITEM-OVERLONG`` instead of vanishing with no
    trace (research D3.4).
    """
    if choice.is_no_change:
        # "Take nothing" names no item, and a row asserting it names one would be a swap.
        return (), []

    findings: list[Finding] = []

    def _within_limit(item: ItemParse, *, role: OptionItemRole) -> bool:
        if len(item.name) <= MAX_CHOICE_NAME_CHARS:
            return True
        findings.append(
            build_finding(
                "OPT-ITEM-OVERLONG",
                entity_refs=[datasheet_id, choice.id],
                detail={
                    "datasheet_id": datasheet_id,
                    "choice_id": choice.id,
                    "role": role.value,
                    "item_name_length": len(item.name),
                },
            )
        )
        return False

    whole_name_linked = len(weapon_lines_named(choice.name, weapons)) == 1
    parsed_items = (
        (ItemParse(name=choice.name, count=choice.count),)
        if whole_name_linked
        else split_conjuncts(choice.name, choice.count)
    )
    items = [
        CuratedOptionChoiceItem(
            role=object_role, item_index=index, item_name=item.name, count=item.count
        )
        for index, item in enumerate(parsed_items, start=1)
        if _within_limit(item, role=object_role)
    ]
    if replaced_clause is not None:
        items.extend(
            CuratedOptionChoiceItem(
                role=OptionItemRole.REPLACED,
                item_index=index,
                item_name=item.name,
                count=item.count,
            )
            for index, item in enumerate(split_replaced(replaced_clause), start=1)
            if _within_limit(item, role=OptionItemRole.REPLACED)
        )
    return tuple(sorted(items, key=lambda item: (item.role.value, item.item_index))), findings


def _authored_items(choice: OptionOverrideChoice) -> tuple[CuratedOptionChoiceItem, ...]:
    """A curator's own decomposition, used as written and never re-derived (FR-011).

    A `004`-shaped override states no items and gets the same mirroring row a parsed single-item
    choice gets, so guarantee 12 holds for authored structures without the override file having
    to be rewritten — which is what makes FR-011 a schema property rather than a migration.
    """
    if choice.is_no_change:
        return ()
    if choice.items:
        # `item_index` is 1-based **within its side**, in the curator's own order, exactly as it
        # is for a parsed choice — the two sides are one array, not one sequence.
        seen: dict[str, int] = {}
        authored: list[CuratedOptionChoiceItem] = []
        for item in choice.items:
            seen[item.role] = seen.get(item.role, 0) + 1
            authored.append(
                CuratedOptionChoiceItem(
                    role=OptionItemRole(item.role),
                    item_index=seen[item.role],
                    item_name=item.item_name,
                    count=item.count,
                    weapon_line=item.weapon_line,
                )
            )
        return tuple(sorted(authored, key=lambda row: (row.role.value, row.item_index)))

    role = (
        OptionItemRole.REPLACED
        if choice.replaces_weapon_line is not None
        else OptionItemRole.GRANTED
    )
    line = (
        choice.replaces_weapon_line
        if role is OptionItemRole.REPLACED
        else choice.grants_weapon_line
    )
    return (
        CuratedOptionChoiceItem(
            role=role,
            item_index=1,
            item_name=choice.name,
            count=choice.count,
            weapon_line=line,
        ),
    )


def _army_rule_state(authored: AuthoredContent, faction_id: str) -> ArmyRuleState | None:
    """``present`` | ``none`` | ``None`` — the third state being the **absence** of a file.

    Three facts, not two (004 FR-021): a faction with no army rule, a faction nobody has curated
    yet, and a faction with rules. A consumer that cannot tell the first two apart shows the same
    empty section for both, so the absent file stays absent all the way to the bundle.
    """
    state = authored.army_rule_state_for(faction_id)
    return ArmyRuleState(state) if state is not None else None


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
    carried_forward_detail_ids: frozenset[str] = frozenset(),
) -> AssemblyResult:
    """Build the whole curated snapshot.

    ``carried_forward_detail_ids`` (008 FR-024) is carried straight through to
    :func:`~pipeline.reconcile.match.resolve_factions` — the detail-source ids acquisition
    declared **and** could not fetch this run, so a faction contributing no rows for that reason
    is not the unexplained ``REC-DETAIL-FACTION-EMPTY``. Plain data resolved at acquisition by
    :func:`pipeline.acquire.detail_source.resolve_carried_forward`; nothing here knows a mode
    exists (rule 4). Defaults to empty, which is inert.
    """
    findings: list[Finding] = []
    registry = registry or IdRegistry()
    edition_id = f"ed-{edition_code}"

    detail_datasheets = detail["Datasheets.csv"]
    # The faction-id vocabulary actually acquired this run, arm-agnostic (009 FR-015,
    # data-model.md §2): whichever arm read `Datasheets.csv`, this is what its own `faction_id`
    # column carries. Passed to `resolve_factions` so a mapped faction matching NONE of it is the
    # loud, blocking `REC-DETAIL-FACTION-EMPTY` rather than the silent empty roster `plan.md`
    # finding 2 measured -- the coverage ratchets read 100% on the OTHER factions regardless.
    detail_faction_ids_present = frozenset(
        faction_id for row in detail_datasheets.rows if (faction_id := row.fields.get("faction_id"))
    )
    factions_outcome = resolve_factions(
        [page.faction_slug for page in pages],
        authored,
        detail_faction_ids_present=detail_faction_ids_present,
        carried_forward_detail_ids=carried_forward_detail_ids,
    )
    findings.extend(factions_outcome.findings)
    scopes = {scope.entry.mfm_slug: scope for scope in factions_outcome.scopes}

    legends_sources = _legends_source_ids(detail)
    detail_faction_keywords = _faction_keywords_by_datasheet(detail)
    source_detachment_rules = _source_detachment_rules(detail)
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
    datasheet_ids: dict[tuple[str, str], str] = {}

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
                # `None` when the faction has no curation file at all — *not yet curated*, which
                # FR-021 requires be distinguishable from a curated "no army rule". Defaulting
                # the absent file to `none` here would spend the distinction the object wrapper
                # in `curation/faction-rules/` exists to buy.
                army_rule_state=_army_rule_state(authored, scope.faction_id),
                provenance=provenance,
            )
        )

        detachments.extend(
            _detachments_for(
                page.detachments,
                scope.faction_id,
                edition_id,
                provenance,
                registry,
                source_rules=source_detachment_rules,
                authored=authored,
            )
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
        # Legends status comes from the **publication**, not from the datasheet's own `legend`
        # column: that column is flavour text this pipeline must not read, and it is set on
        # roughly twice as many datasheets as are actually Legends (research §0.1).
        legends = {
            row.fields["id"]: row.fields.get("source_id", "") in legends_sources
            for row in detail_datasheets.rows
        }
        # The detail source's own publication id per datasheet — the same `source_id` column
        # `legends` reads above, kept separately because it answers a different question (which
        # publication, not whether that publication is Legends). Only consulted by `match_units`
        # when a chapter's own supplement collides by name with the core codex (D5 stage 2).
        detail_source_ids = {
            row.fields["id"]: row.fields.get("source_id", "") for row in detail_datasheets.rows
        }

        outcome = match_units(
            scope,
            display_names=list(blocks_by_unit),
            detail_names=in_scope,
            detail_is_legends=legends,
            detail_source_ids=detail_source_ids,
            detail_faction_keywords=detail_faction_keywords,
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
                legends_sources=legends_sources,
            )
            findings.extend(datasheet_findings)
            datasheets.append(datasheet)
            datasheet_ids[(page.faction_slug, match.display_name)] = match.datasheet_id
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
            legends_sources=legends_sources,
        )
        findings.extend(unverified_findings)
        if unverified is not None:
            datasheets.append(unverified)
            detail_to_curated[detail_id] = unverified.datasheet_id

    datasheets = _attach_leader_pairs(datasheets, detail, detail_to_curated)

    # Classification runs **after** every faction and every datasheet exists, not inside the
    # loop, for the same reason the detail-only pass does: a keyword's class is a property of the
    # keyword across the whole snapshot, and the faction tree it is resolved against is not
    # complete until the last page has been assembled (004 FR-017..FR-020, research D7).
    classification = classify_keywords(
        observed=observed_keywords(datasheets),
        factions=factions,
        authored=authored.keyword_classes,
    )
    findings.extend(classification.findings)
    datasheets = apply_keyword_classes(datasheets, classification.classes)

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
        chapter_keywords=classification.chapter_keywords,
        ability_summaries=authored.ability_summaries,
        faction_rules=authored.faction_rule_files,
        detachment_rules=authored.detachment_rule_summaries,
        keyword_glossary=authored.glossary_entries,
    )

    return AssemblyResult(
        snapshot=snapshot,
        findings=findings,
        datasheet_ids=datasheet_ids,
        wahapedia_datasheet_ids={
            curated_id: detail_id for detail_id, curated_id in detail_to_curated.items()
        },
    )


#: The detail export's detachment-rule file. Joined `EXPORT_FILES` in the `csv` arm at 009 task
#: T028 (FR-019 parity restoration) — previously only the `html` arm supplied it, and
#: :func:`_source_detachment_rules` already reads its absence as "the source published no rule
#: names this run" rather than as an error, which is what let this join land with zero behaviour
#: change for any run that does not yet acquire it.
DETACHMENT_ABILITIES_FILE: Final = "Detachment_abilities.csv"


def _source_detachment_rules(detail: Mapping[str, CsvReadResult]) -> Mapping[str, tuple[str, ...]]:
    """``normalised detachment name -> the rule names the source publishes for it``.

    Keyed by the **normalised name** rather than by the detail source's own detachment id,
    because the curated detachment is minted from the points source's card and the two taxonomies
    share no id — the same join :func:`_detachments_for` already performs to mint that id, so a
    detachment matches here exactly when it matches there.

    An id the source publishes for two differently-named detachments names neither of them, so it
    is dropped rather than resolved to whichever row happened to be read last (issue #5). A rule
    that goes missing is one outstanding entry a curator sees; a rule attributed to the wrong
    detachment is a wrong summary approved against a rule it does not describe, and the second is
    not a milder form of the first.
    """
    detachments = detail.get("Detachments.csv")
    abilities = detail.get(DETACHMENT_ABILITIES_FILE)
    if detachments is None or abilities is None:
        return {}

    names_by_id: dict[str, str] = {}
    ambiguous: set[str] = set()
    for row in detachments.rows:
        identifier = row.fields.get("id", "")
        name = normalize_name(strip_field(row.fields.get("name", ""), field="detachment.name").text)
        if identifier in names_by_id and names_by_id[identifier] != name:
            ambiguous.add(identifier)
        names_by_id[identifier] = name
    for identifier in ambiguous:
        del names_by_id[identifier]
    grouped: dict[str, list[str]] = {}
    for row in abilities.rows:
        detachment = names_by_id.get(row.fields.get("detachment_id", ""))
        name = strip_field(row.fields.get("name", ""), field="detachment_rule.name").text
        if not detachment or not name:
            continue
        seen = grouped.setdefault(detachment, [])
        if name not in seen:
            seen.append(name)
    return {detachment: tuple(names) for detachment, names in grouped.items()}


def _detachment_rules(
    detachment_id: str,
    normalised_name: str,
    *,
    source_rules: Mapping[str, tuple[str, ...]],
    authored: AuthoredContent,
) -> list[CuratedDetachmentRule]:
    """The rule identities one detachment publishes, name always carried (FR-022).

    The source is authoritative where it speaks. Where it does not — which is every run until the
    current-edition detail acquisition lands — the authored records for this detachment supply
    the names instead, exactly as ``curation/faction-rules/`` already does for army rules. That
    fallback cannot inflate coverage: a rule only appears because a curator wrote a record for
    it, so the denominator it contributes to is one the same file already answers.
    """
    names = source_rules.get(normalised_name)
    if names is not None:
        return [
            CuratedDetachmentRule(summary_key=detachment_rule_key(detachment_id, name), name=name)
            for name in names
        ]
    return [
        CuratedDetachmentRule(summary_key=record.summary_key, name=record.name)
        for record in sorted(
            (
                record
                for record in authored.detachment_rule_summaries.values()
                if record.detachment_id == detachment_id
            ),
            key=lambda record: record.summary_key,
        )
    ]


def _detachments_for(  # noqa: PLR0913 - one argument per upstream input, as the module's style
    cards: Sequence[MfmDetachmentCard],
    faction_id: str,
    edition_id: str,
    provenance: EntityProvenance,
    registry: IdRegistry,
    *,
    source_rules: Mapping[str, tuple[str, ...]],
    authored: AuthoredContent,
) -> list[CuratedDetachment]:
    built: list[CuratedDetachment] = []
    for card in cards:
        normalised = normalize_name(card.detachment_name)
        key = f"{faction_id}/{normalised}"
        detachment_id = registry.mint(EntityKind.DETACHMENT, key, card.detachment_name)
        built.append(
            CuratedDetachment(
                detachment_id=detachment_id,
                edition_id=edition_id,
                faction_id=faction_id,
                name=card.detachment_name,
                detachment_points_cost=card.dp_cost,
                is_legends=False,
                force_disposition=card.force_disposition,
                is_unique=any(tag.upper().startswith("UNIQUE") for tag in card.tags),
                rules=_detachment_rules(
                    detachment_id, normalised, source_rules=source_rules, authored=authored
                ),
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
    legends_sources: frozenset[str],
) -> tuple[CuratedDatasheet, list[Finding]]:
    findings: list[Finding] = []
    costs, wargear_options, cost_findings = _costs(
        blocks, points_acquisition.acquisition_id, match.datasheet_id
    )
    findings.extend(cost_findings)

    fields: dict[str, object] = {}
    composition: list[CuratedCompositionEntry] = []
    options = _OptionOutcome()
    equipment = _EquipmentOutcome()
    if match.wahapedia_datasheet_id:
        fields, detail_findings = _detail_datasheet_fields(
            match.wahapedia_datasheet_id, detail, legends_sources
        )
        findings.extend(detail_findings)

        models: Sequence[CuratedModelLine] = fields.get("models", ())  # type: ignore[assignment]
        weapons: Sequence[CuratedWeaponLine] = fields.get("weapons", ())  # type: ignore[assignment]
        composition, composition_findings = _composition_entries(
            match.wahapedia_datasheet_id, match.datasheet_id, detail, authored, models
        )
        findings.extend(composition_findings)

        options = _option_structure(
            match.wahapedia_datasheet_id,
            match.datasheet_id,
            detail,
            authored,
            weapons,
            wargear_options,
            composition,
        )
        findings.extend(options.findings)

        # Called with the composition already resolved, and reading it: FR-016 refuses to attach
        # a loadout to a composition structure that does not exist, and passing the entries in is
        # what makes that refusal a property of the call rather than a rule to remember.
        equipment = _equipment(
            match.wahapedia_datasheet_id,
            match.datasheet_id,
            detail,
            authored,
            composition,
            weapons,
        )
        findings.extend(equipment.findings)

        # Both sources priced it: the points source wins, both values are reported, and the
        # losing value is carried nowhere (FR-028).
        detail_prices = _detail_prices(match.wahapedia_datasheet_id, detail)
        for cost in costs:
            conflict = resolve_cost_conflict(
                datasheet_id=match.datasheet_id,
                model_count=cost.model_count,
                points_value=cost.points,
                detail_value=detail_prices.get(cost.model_count),
            )
            findings.extend(conflict.findings)

        # Do the points source's size bands fit the unit the detail source describes (FR-027,
        # and `004`'s FR-009)? **Exactly one of the two reconciliations runs.** Where the
        # composition resolved, the structured entries are the better statement of the same
        # fact; where it did not, the free-text reader still has something to say and its
        # `REC-COMPOSITION-UNPARSED` is still the right finding. Running both would report one
        # defect twice, in two categories, to an approver reading the counts as "how much of
        # this release is wrong".
        findings.extend(
            reconcile_composition_bands(
                datasheet_id=match.datasheet_id,
                entries=composition,
                model_counts=[cost.model_count for cost in costs],
            )
            if composition
            else reconcile_bands(
                datasheet_id=match.datasheet_id,
                model_counts=[cost.model_count for cost in costs],
                composition_lines=_composition_lines(match.wahapedia_datasheet_id, detail),
            )
        )

        # A hybrid entity is self-describing all the way to the bundle, but the approver still
        # needs the scale of it, so each one is reported (FR-058, FR-060).
        if provenance.is_hybrid_edition:
            findings.append(
                build_finding(
                    "EDN-HYBRID-ENTITY",
                    entity_refs=[match.datasheet_id],
                    detail={
                        "datasheet_id": match.datasheet_id,
                        "points_edition_code": provenance.points_edition_code,
                        "detail_edition_code": provenance.detail_edition_code,
                    },
                )
            )
    # A points-only datasheet needs no finding here: `match_units` already raised
    # REC-UNMATCHED-POINTS-ONLY with its ranked suggestions, and raising a second one would
    # double-count one gap across two categories.

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
        composition=composition,
        option_groups=options.groups,
        option_choices=options.choices,
        wargear_option_state=options.state,
        equipment_groups=equipment.groups,
        default_equipment_state=equipment.state,
        item_constraints=options.item_constraints,
        wargear_options=wargear_options,
        costs=costs,
        pricing_confidence=PricingConfidence(state=PricingConfidenceState.VERIFIED),
        provenance=provenance,
    )
    return datasheet, findings


def _owning_factions(scopes: Sequence[FactionScope]) -> dict[str, FactionScope]:
    """Which curated faction owns each detail-source faction id, **in either arm's vocabulary**.

    Several curated factions can share one detail-source id — the chapters all draw on the
    parent's. A datasheet nobody priced is filed under the **root** of that group, because the
    consumer contract's §3.5 query rule then shows it to the parent *and* to every chapter,
    whereas filing it under one chapter would hide it from the other four.

    Keyed through :func:`pipeline.reconcile.match._detail_ids_for`, the same helper
    ``resolve_factions``/``match_units``'s own scope-building already uses (009 T020/T021,
    data-model.md §2) — **not** ``scope.entry.detail_source_faction_id`` alone. Without this, an
    unclaimed row's ``faction_id`` under ``csv`` mode is the export's own code (``"SM"``), which
    never matches the ``html``-arm slug this dict used to be keyed by alone, so every unclaimed
    detail-only row was silently dropped by the caller's ``owning_faction.get(...) is None``
    check — proven live (shape-decision diagnosis session) to be effectively the entire measured
    coverage collapse under a full ``csv``-mode build, discarding the whole FR-026/FR-035
    "ships on the best price known" recovery pass for every row. Arm-blind by construction, same
    as every other 009 arm-selection site (rule 4/FR-012): both vocabularies are always carried,
    never chosen between.
    """
    owners: dict[str, FactionScope] = {}
    for scope in sorted(
        scopes, key=lambda s: (s.entry.parent_faction_id is not None, s.faction_id)
    ):
        for detail_id in _detail_ids_for(scope.entry):
            owners.setdefault(detail_id, scope)
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
    legends_sources: frozenset[str],
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

    costs: list[CuratedDatasheetCost] = []
    for count, points in sorted(_detail_prices(detail_id, detail).items()):
        costs.append(
            CuratedDatasheetCost(
                model_count=count,
                copy_index_min=1,
                points=points,
                label=f"{count} model{'s' if count != 1 else ''}",
                pricing_confidence=PricingConfidenceState.UNVERIFIED,
                source_acquisition_id=detail_acquisition.acquisition_id,
            )
        )

    if not costs:
        # No source has ever priced it. There is nothing to carry forward and nothing to label,
        # so it is reported and left out rather than emitted at zero — a free unit in a player's
        # list is worse than an absent one (FR-026).
        findings.append(
            build_finding(
                "REC-NEVER-PRICED",
                entity_refs=[f"wahapedia:{detail_id}"],
                detail={"faction_id": faction_id, "detail_datasheet_id": detail_id},
            )
        )
        return None, findings

    # The Legends discriminator is part of the key, not an afterthought: a faction can publish
    # two datasheets whose only difference is that one is Legends, and they need two ids.
    source_row = detail["Datasheets.csv"].by_id("id").get(detail_id)
    is_legends = (
        source_row is not None and source_row.fields.get("source_id", "") in legends_sources
    )
    datasheet_id = registry.mint(
        EntityKind.DATASHEET,
        datasheet_key(faction_id, normalize_name(display_name), is_legends=is_legends),
        display_name,
    )
    fields, detail_findings = _detail_datasheet_fields(detail_id, detail, legends_sources)
    findings.extend(detail_findings)

    models: Sequence[CuratedModelLine] = fields.get("models", ())  # type: ignore[assignment]
    weapons: Sequence[CuratedWeaponLine] = fields.get("weapons", ())  # type: ignore[assignment]
    composition, composition_findings = _composition_entries(
        detail_id, datasheet_id, detail, authored, models
    )
    findings.extend(composition_findings)

    # No points source priced this datasheet, so there are no priced rows for its choices to
    # adopt — every one of them ships uncosted, which is exactly what FR-013 asks for.
    options = _option_structure(detail_id, datasheet_id, detail, authored, weapons, (), composition)
    findings.extend(options.findings)

    # Whether the points authority priced a datasheet says nothing about what its models carry,
    # so this path reads equipment on exactly the terms the matched path does. Omitting the call
    # here is the defect the wh40k-11e-2026-08-2 candidate carried: 647 datasheets reached the
    # bundle with a composition, weapons and a `wargear_option_state` but no
    # `default_equipment_state` at all, which reads as "the source was not consulted" for cards
    # the pipeline had in fact read end to end.
    equipment = _equipment(detail_id, datasheet_id, detail, authored, composition, weapons)
    findings.extend(equipment.findings)

    findings.extend(
        reconcile_composition_bands(
            datasheet_id=datasheet_id,
            entries=composition,
            model_counts=[cost.model_count for cost in costs],
        )
        if composition
        else reconcile_bands(
            datasheet_id=datasheet_id,
            model_counts=[cost.model_count for cost in costs],
            composition_lines=_composition_lines(detail_id, detail),
        )
    )

    # A detail-only datasheet is hybrid on exactly the same terms as a matched one, and is
    # reported on the same terms — otherwise the report's hybrid *count* and its hybrid
    # *findings* disagree, and an approver has to work out which of the two to believe.
    if provenance.is_hybrid_edition:
        findings.append(
            build_finding(
                "EDN-HYBRID-ENTITY",
                entity_refs=[datasheet_id],
                detail={
                    "datasheet_id": datasheet_id,
                    "points_edition_code": provenance.points_edition_code,
                    "detail_edition_code": provenance.detail_edition_code,
                },
            )
        )

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
        composition=composition,
        option_groups=options.groups,
        option_choices=options.choices,
        wargear_option_state=options.state,
        equipment_groups=equipment.groups,
        default_equipment_state=equipment.state,
        item_constraints=options.item_constraints,
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
