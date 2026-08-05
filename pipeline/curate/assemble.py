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
# carried the authored detachment-rule records onto the snapshot (004 task T054).
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
from pipeline.curate.summaries import detachment_rule_key
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
    CuratedFaction,
    CuratedGameSizeRule,
    CuratedKeyword,
    CuratedModelLine,
    CuratedOptionChoice,
    CuratedOptionGroup,
    CuratedSnapshot,
    CuratedWargearOption,
    CuratedWeaponLine,
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
from pipeline.parse.composition_grammar import link_model_line, parse_entry
from pipeline.parse.mfm_dom import MfmPage
from pipeline.parse.options_grammar import (
    OptionVerb,
    choice_id,
    group_id,
    option_state,
    parse_row,
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
from pipeline.reconcile.identity import EntityKind, IdRegistry, slugify
from pipeline.reconcile.match import (
    FactionScope,
    UnitMatch,
    datasheet_key,
    match_units,
    report_orphan_detail_factions,
    resolve_factions,
)
from pipeline.reconcile.options_link import link_choice_weapons, project_priced_options
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
    fields["is_dedicated_transport"] = role_key in _TRANSPORT_ROLES
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
    for weapon in detail["Datasheets_wargear.csv"].grouped_by("datasheet_id").get(detail_id, []):
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


@dataclass(slots=True)
class _OptionOutcome:
    """One datasheet's full option set, as `004`'s US1 produces it."""

    groups: list[CuratedOptionGroup] = field(default_factory=list)
    choices: list[CuratedOptionChoice] = field(default_factory=list)
    state: WargearOptionState | None = None
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
    return sorted(entries, key=lambda entry: entry.line), findings


def _option_structure(
    detail_id: str,
    datasheet_id: str,
    detail: Mapping[str, CsvReadResult],
    authored: AuthoredContent,
    weapons: Sequence[CuratedWeaponLine],
    priced: Sequence[CuratedWargearOption],
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
    groups: list[CuratedOptionGroup] = []
    parsed_choices: list[CuratedOptionChoice] = []
    authored_choices: list[CuratedOptionChoice] = []
    verbs: dict[str, OptionVerb] = {}
    findings: list[Finding] = []
    unparsed = 0

    for row in source_rows:
        line = _row_ordinal(row.fields.get("line", ""), field_name="option.line")
        override = authored.option_override_for(datasheet_id, line) if line else None
        if line is not None and override is not None:
            groups.append(
                CuratedOptionGroup(
                    id=group_id(datasheet_id, line),
                    line=line,
                    scope=OptionScope(override.scope),
                    scope_n=override.scope_n,
                    min_choices=override.min_choices,
                    max_choices=override.max_choices,
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
                )
                for index, choice in enumerate(override.choices, start=1)
            )
            continue

        parsed = parse_row(row.fields.get("description", "")) if line is not None else None
        if line is None or parsed is None:
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
            CuratedOptionGroup(id=group, line=line, scope=parsed.scope, scope_n=parsed.scope_n)
        )
        for index, choice in enumerate(parsed.choices, start=1):
            identifier = choice_id(group, index)
            verbs[identifier] = choice.verb
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
        datasheet_id=datasheet_id, choices=parsed_choices, verbs=verbs, weapons=weapons
    )
    findings.extend(link_findings)

    choices, price_findings = project_priced_options(
        datasheet_id=datasheet_id, choices=[*linked, *authored_choices], priced=priced
    )
    findings.extend(price_findings)

    return _OptionOutcome(
        groups=sorted(groups, key=lambda group: group.id),
        choices=sorted(choices, key=lambda choice: choice.id),
        state=option_state(row_count=len(source_rows), unparsed_count=unparsed),
        findings=findings,
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
) -> AssemblyResult:
    """Build the whole curated snapshot."""
    findings: list[Finding] = []
    registry = registry or IdRegistry()
    edition_id = f"ed-{edition_code}"

    factions_outcome = resolve_factions([page.faction_slug for page in pages], authored)
    findings.extend(factions_outcome.findings)
    scopes = {scope.entry.mfm_slug: scope for scope in factions_outcome.scopes}

    detail_datasheets = detail["Datasheets.csv"]
    legends_sources = _legends_source_ids(detail)
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
    )

    return AssemblyResult(snapshot=snapshot, findings=findings, datasheet_ids=datasheet_ids)


#: The detail export's detachment-rule file. **Not in `EXPORT_FILES`** — the current-edition
#: acquisition that brings it lands with Phase 9's own tasks, and adding it to the sweep here
#: would change acquisition behaviour under a task that is about curation. Until then the file
#: is simply absent from `detail`, which :func:`_source_detachment_rules` reads as "the source
#: published no rule names this run" rather than as an error.
DETACHMENT_ABILITIES_FILE: Final = "Detachment_abilities.csv"


def _source_detachment_rules(detail: Mapping[str, CsvReadResult]) -> Mapping[str, tuple[str, ...]]:
    """``normalised detachment name -> the rule names the source publishes for it``.

    Keyed by the **normalised name** rather than by the detail source's own detachment id,
    because the curated detachment is minted from the points source's card and the two taxonomies
    share no id — the same join :func:`_detachments_for` already performs to mint that id, so a
    detachment matches here exactly when it matches there.
    """
    detachments = detail.get("Detachments.csv")
    abilities = detail.get(DETACHMENT_ABILITIES_FILE)
    if detachments is None or abilities is None:
        return {}

    names_by_id = {
        row.fields.get("id", ""): normalize_name(
            strip_field(row.fields.get("name", ""), field="detachment.name").text
        )
        for row in detachments.rows
    }
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
        )
        findings.extend(options.findings)

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
    options = _option_structure(detail_id, datasheet_id, detail, authored, weapons, ())
    findings.extend(options.findings)

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
