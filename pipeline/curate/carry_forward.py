# AI-Assisted: Claude Code (model: claude-sonnet-5) - Implemented the per-faction carry-forward
# splice (008 FR-024/FR-025, Product Owner decision 2026-08-17, following T074's dry-run finding
# that the live detail source currently omits several factions from its own sitemap). A declared
# faction the acquisition layer could not fetch this run (pipeline/acquire/wahapedia_html.py) is
# spliced in here from the previous published tree, AFTER assembly and BEFORE coverage/ratchet
# comparison runs -- so a carried faction's datasheets simply look "present, unchanged" to every
# coverage figure, which is what makes FR-025's "no figure regresses because of a carry-forward"
# true structurally rather than by a special case in pipeline/validate/coverage.py.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 009 rung R06a (T096, FR-033): added the
# per-class composition `class_carried_slugs` drives. Under a hybrid, a declared faction may
# answer live on its build-configured arm (so it is `unused`, never `carried`, at the
# whole-faction level) while a class `curation/detail-source-authority.json` sends to a DIFFERENT
# arm still fails to fetch that faction's page. The resulting datasheet is mixed-vintage --
# current for every field the configured arm supplied, frozen at the previous published version
# for exactly the class(es) whose own arm did not answer -- and this is the one place that
# freezing happens: only `curate` has the previous published tree already in curated (post-parse)
# shape to compose it from.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - R06a-fix item 1: corrected `_CLASS_FIELDS`
# in both directions. `wargear_options` is NOT options-arm-sourced -- traced to
# `curate/assemble.py::_costs()`, which returns it and `costs` from ONE call over the SAME
# points-source blocks for THIS run (also stated on `CuratedDatasheet.wargear_options`'s own
# field docstring: "same producer (_costs())" as `costs`). Freezing `wargear_options` alone while
# `costs` stayed current split one atomic computation across two points acquisitions -- a real
# price disagreement, not merely a stale-looking one. `item_constraints` IS options-arm-sourced
# (`_option_structure`'s own `_OptionOutcome`, same call that fills `option_groups`/
# `option_choices`) and was missing, which silently dropped a carried faction's restrictions
# while keeping its option groups -- the FR-025 regression this splice exists to prevent.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - R06a-fix2 item 1: `_CLASS_FIELDS` freezes
# fields that carry ORDINALS into `weapons`/`composition` -- `item_constraints[].weapon_line`,
# `option_choices[].grants_weapon_line`/`replaces_weapon_line` (and, one level down, its own
# `items[].weapon_line`), `equipment_groups[].composition_line`, and
# `equipment_groups[].items[].weapon_line` -- frozen from the PRIOR publish onto a datasheet whose
# `weapons`/`composition` are THIS run's own (neither field is named in `_CLASS_FIELDS`, so
# neither is ever frozen). A prior ordinal can point at the wrong current row, or at no row at
# all, and nothing re-resolved it: the name-to-line joins in `reconcile/options_link.py` and
# `reconcile/equipment_link.py` run inside `assemble`, BEFORE this splice. Every one of the four
# fields carries the referent's NAME beside (or one step from) the ordinal -- `item_name` on
# `CuratedItemConstraint` and `CuratedEquipmentItem`, `model_name` on `CuratedEquipmentGroup`
# (composition_line is only ever set when `applies_to` is `model_group`, i.e. exactly when
# `model_name` is present), and `items[].item_name` on `CuratedOptionChoice` (a present singular
# field always mirrors exactly one item on that role, per `link_choice_items`'s own contract) --
# so every field is re-resolvable, never refused. `_reresolve_options_ordinals` and
# `_reresolve_equipment_ordinals` below reset the frozen ordinals to `None` (the "freshly parsed,
# not yet linked" shape those reconcile-stage functions expect) and then call THIS run's own
# `reconcile.options_link.link_choice_items` / `reconcile.equipment_link.link_equipment` against
# THIS run's own `weapons`/`composition` -- the same name-to-line join every other datasheet in
# the run gets, rather than a second implementation of that rule. `item_constraints` has no
# existing bulk "link" pass to reuse (`curate/assemble.py::_item_constraint` also re-parses the
# raw description text, which frozen data does not carry) -- re-linked here with the same public
# `weapon_lines_named` join and the same `CST-UNLINKED` code the parse-time path already reports a
# 0-or-2-plus-match under, so a referent that no longer exists is a finding, never a silent
# mis-point or a silent drop.
"""Splice declared, unreachable-this-run factions in from the previous published tree.

Three outcomes, one per declared or newly-carried slug, and each is a `Finding` — never silent
(FR-025):

* **Carried** — the faction could not be fetched this run and was declared; its datasheets are
  copied from the previous published tree unchanged. `SRC-FACTION-CARRIED-FORWARD`, advisory.
* **Unused declaration** — the faction fetched live successfully anyway (the source recovered).
  The live data is used, exactly as for any other faction; the declaration did nothing this run,
  and a curator is told so it can be retired. `SRC-FACTION-CARRY-FORWARD-UNUSED`, advisory.
* **No prior to carry from** — a faction is declared and could not be fetched, but the previous
  published tree has no data for it at all (a first-release faction, or a slug that never
  matched one). There is nothing to substitute. `SRC-FACTION-CARRY-FORWARD-NO-PRIOR`, blocking —
  the same refusal an undeclared unreachable faction gets, because a declaration cannot manufacture
  data that was never published (FR-008's guarantee holds for exactly this case too).

A fourth outcome composes ON TOP of the first three rather than replacing one (009 rung R06a,
T096, FR-033): **per-class carry**, when a hybrid-declared class's own arm could not answer for a
declared faction whose OTHER classes came through fine. Only the named class's own fields are
overwritten on the datasheet(s) this run already assembled for that faction, from the matching
prior published datasheet — never the whole datasheet, and never reported or composed twice for a
slug already `carried` in full. It reuses `SRC-FACTION-CARRIED-FORWARD` (rule 10: a class, rung,
or cause measured at zero gets no code, and this condition already has a reporting home), with
``data_class`` added to the finding's own `detail` so "which class, which arm" stays legible.

Determinism (008 FR-024's requirement (c)): every carried datasheet — whole or per-class — is
copied from ``read_curated_tree``'s own parse of the git-committed `data/<edition>/` tree at the
commit this run reads — the same input `_reconcile_against_prior`'s ratchet baseline already
reads, and already reproducible for the same reason that comparison is. Nothing here touches a
live source a second time.
"""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Final

from pipeline.models.curated import CuratedDatasheet, CuratedSnapshot
from pipeline.models.findings import Finding
from pipeline.reconcile.equipment_link import link_equipment
from pipeline.reconcile.options_link import link_choice_items, weapon_lines_named
from pipeline.report.catalogue import build_finding

#: data_class (`schemas/curation/detail-source-authority.schema.json`'s closed enum) -> the
#: `CuratedDatasheet` field(s) that class owns. Deliberately its OWN copy rather than importing
#: `acquire/detail_source.py`'s `_CLASS_TABLES`: that mapping names EXPORT TABLE names (an
#: acquire-layer, pre-parse concept, e.g. `Datasheets_options.csv`); this one names CURATED MODEL
#: fields (a curate-layer, post-parse concept). The two vocabularies share the same two class
#: NAMES only because they describe the same two hybrid-declared classes from opposite ends of
#: the pipeline -- the same discipline `acquire/detail_source.py::_EQUIPMENT_MARKER` already
#: applies to its own copy of a pattern `parse/wahapedia_html_dom.py` also defines.
#:
#: `options` carries the three fields `curate/assemble.py::_option_structure` (the OPTIONS-arm
#: extraction) actually produces in its `_OptionOutcome`: `option_groups`, `option_choices`,
#: `wargear_option_state` -- and, alongside them, `item_constraints`, sourced from that SAME call
#: (`options.item_constraints` at the `_datasheet_for` call site), not a fourth raw field bolted
#: on. Carrying the groups without the restrictions the source stated against their items would
#: regress `loadout.item_constraints` for exactly the carried faction (the FR-025 regression this
#: splice exists to prevent).
#:
#: `wargear_options` is deliberately NOT here. It is the PRICED projection, but it is
#: POINTS-source-built: `_datasheet_for` calls `_costs(blocks, ...)` ONCE and that one call
#: returns both `costs` and `wargear_options` together, from the same points-source blocks, for
#: THIS run (`CuratedDatasheet.wargear_options`'s own field docstring: "same producer (_costs())"
#: as `costs`). `costs` is never in `_CLASS_FIELDS` -- the options-arm hybrid split has no
#: authority over it -- so freezing `wargear_options` from the prior publish while `costs` stayed
#: this run's own would split one atomic computation across two different points acquisitions:
#: two priced views of one datasheet disagreeing, and a stale wargear upgrade price shown beside
#: a current base cost.
_CLASS_FIELDS: Final[Mapping[str, tuple[str, ...]]] = {
    "options": ("option_groups", "option_choices", "wargear_option_state", "item_constraints"),
    "default_equipment": ("equipment_groups", "default_equipment_state"),
}

#: The immutable default for `apply_carried_forward`'s `class_carried_slugs` -- a plain `{}`
#: literal as a mutable default would be a classic Python trap; this is the module-level
#: singleton every un-hybrid caller (the overwhelming majority of runs) actually gets.
_NO_CLASS_CARRY: Final[Mapping[str, frozenset[str]]] = MappingProxyType({})


def _reresolve_options_ordinals(
    datasheet: CuratedDatasheet, findings: list[Finding]
) -> CuratedDatasheet:
    """Re-link a per-class-composed `options` datasheet's frozen ordinals (R06a-fix2 item 1).

    `item_constraints[].weapon_line` and `option_choices[].{grants,replaces}_weapon_line` (and
    the `items[]` each singular field mirrors) were frozen from the previous publish onto a
    datasheet whose `weapons` are THIS run's. Reset to the "freshly parsed" shape and re-linked by
    NAME against `datasheet.weapons` -- never frozen by `_CLASS_FIELDS`, so always this run's own
    -- reusing `reconcile.options_link.link_choice_items` (the sole writer of both option fields,
    per its own docstring) and the public `weapon_lines_named` join it shares with
    `curate/assemble.py::_item_constraint`, rather than a second implementation of either rule.
    """
    reset_choices = [
        choice.model_copy(
            update={
                "grants_weapon_line": None,
                "replaces_weapon_line": None,
                "items": tuple(
                    item.model_copy(update={"weapon_line": None}) for item in choice.items
                ),
            }
        )
        for choice in datasheet.option_choices
    ]
    relinked_choices, choice_findings = link_choice_items(
        datasheet_id=datasheet.datasheet_id, choices=reset_choices, weapons=datasheet.weapons
    )
    findings.extend(choice_findings)

    relinked_constraints = []
    for constraint in datasheet.item_constraints:
        matches = weapon_lines_named(constraint.item_name, datasheet.weapons)
        weapon_line = matches[0] if len(matches) == 1 else None
        if weapon_line is None:
            findings.append(
                build_finding(
                    "CST-UNLINKED",
                    entity_refs=[datasheet.datasheet_id],
                    detail={
                        "datasheet_id": datasheet.datasheet_id,
                        "constraint_index": constraint.constraint_index,
                        "item_name": constraint.item_name,
                        "match_count": len(matches),
                    },
                )
            )
        relinked_constraints.append(constraint.model_copy(update={"weapon_line": weapon_line}))

    return datasheet.model_copy(
        update={
            "option_choices": tuple(relinked_choices),
            "item_constraints": tuple(relinked_constraints),
        }
    )


def _reresolve_equipment_ordinals(
    datasheet: CuratedDatasheet, findings: list[Finding]
) -> CuratedDatasheet:
    """Equipment-side counterpart of :func:`_reresolve_options_ordinals` (R06a-fix2 item 1).

    `equipment_groups[].composition_line` and `equipment_groups[].items[].weapon_line` were
    frozen from the previous publish onto a datasheet whose `composition`/`weapons` are THIS
    run's -- neither is ever named in `_CLASS_FIELDS`. Reset and re-linked by NAME
    (`model_name`, `item_name`) against `datasheet.composition`/`datasheet.weapons`, reusing
    `reconcile.equipment_link.link_equipment` unchanged. The equipment side has no intra-snapshot
    referential check today (`validate/refs.py::check_intra_snapshot_references` covers only
    `item_constraints`), so a mis-pointed or dropped reference here would otherwise pass silently.
    """
    reset_groups = [
        group.model_copy(
            update={
                "composition_line": None,
                "items": tuple(
                    item.model_copy(update={"weapon_line": None}) for item in group.items
                ),
            }
        )
        for group in datasheet.equipment_groups
    ]
    relinked_groups, group_findings = link_equipment(
        datasheet_id=datasheet.datasheet_id,
        groups=reset_groups,
        composition=datasheet.composition,
        weapons=datasheet.weapons,
    )
    findings.extend(group_findings)
    return datasheet.model_copy(update={"equipment_groups": tuple(relinked_groups)})


def apply_carried_forward(
    snapshot: CuratedSnapshot,
    *,
    previous_tree: CuratedSnapshot | None,
    carried_slugs: frozenset[str],
    unused_declaration_slugs: frozenset[str],
    previous_version_id: str,
    class_carried_slugs: Mapping[str, frozenset[str]] = _NO_CLASS_CARRY,
    unused_answers_per_faction: bool = True,
) -> tuple[CuratedSnapshot, tuple[Finding, ...]]:
    """Return ``snapshot`` with every carried faction's datasheets spliced in, plus findings.

    A no-op, returning ``snapshot`` unchanged, when none of the three inputs names anything — the
    overwhelming majority of runs, including every run before this feature and every run once the
    source recovers, so a declaration-free build pays nothing for this function existing.

    ``class_carried_slugs`` (009 rung R06a, T096, FR-033): ``data_class -> declared slugs whose
    OWN declared arm did not answer this run`` — computed by
    :func:`pipeline.acquire.detail_source.apply_detail_source_authority`, which is where the
    mode question ("which arm populates this class") already lives (rule 4). A slug named here
    composes ONLY that class's own fields (:data:`_CLASS_FIELDS`) onto the datasheet(s) this run
    already assembled for the matching faction, from the previous published tree — never the
    whole datasheet, and never a slug already in ``carried_slugs``: the whole faction is already
    frozen there, so composing a class on top of it would do nothing and report twice (FR-033's
    "not double-counted"). This is what makes a mixed-vintage datasheet — some classes current
    from the configured arm, some frozen at the previous version — the same structural guarantee
    008's whole-faction splice already gives: composed here, strictly before
    `_reconcile_against_prior` runs in `pipeline/cli.py`, so no coverage figure moves because of
    the substitution alone.

    ``unused_answers_per_faction`` (R06a-fix item 3): whether THIS run's configured detail arm can
    even answer "did this one faction's page come back" at all —
    :func:`pipeline.acquire.detail_source.resolve_carried_forward`'s own
    ``CarriedForwardOutcome.answers_per_faction``, true only under ``html``. Under a bulk arm
    (``csv``) a declared slug is unconditionally reported ``unused`` the moment the whole export
    answers (FR-032), which is a true but much weaker fact than "this faction's own page was
    reachable" — carried into the finding's ``detail`` so a reader (`pr_body.py`) does not confuse
    the two and advise retiring a declaration a bulk arm was never in a position to test.
    """
    if not carried_slugs and not unused_declaration_slugs and not class_carried_slugs:
        return snapshot, ()

    findings: list[Finding] = []

    slug_to_faction_id: dict[str, str] = {}
    prior_datasheets_by_faction: dict[str, list[CuratedDatasheet]] = {}
    if previous_tree is not None:
        slug_to_faction_id = {
            faction.detail_source_faction_id: faction.faction_id
            for faction in previous_tree.factions
        }
        for datasheet in previous_tree.datasheets:
            prior_datasheets_by_faction.setdefault(datasheet.faction_id, []).append(datasheet)

    existing_ids = {datasheet.datasheet_id for datasheet in snapshot.datasheets}
    carried_datasheets: list[CuratedDatasheet] = []

    for slug in sorted(carried_slugs):
        faction_id = slug_to_faction_id.get(slug)
        prior_rows = prior_datasheets_by_faction.get(faction_id, []) if faction_id else []
        if faction_id is None or not prior_rows:
            findings.append(
                build_finding(
                    "SRC-FACTION-CARRY-FORWARD-NO-PRIOR",
                    entity_refs=(f"faction-slug:{slug}",),
                    detail={"faction_slug": slug},
                )
            )
            continue
        added = 0
        for datasheet in prior_rows:
            if datasheet.datasheet_id not in existing_ids:
                carried_datasheets.append(datasheet)
                existing_ids.add(datasheet.datasheet_id)
                added += 1
        findings.append(
            build_finding(
                "SRC-FACTION-CARRIED-FORWARD",
                entity_refs=(f"faction:{faction_id}",),
                detail={
                    "faction_id": faction_id,
                    "faction_slug": slug,
                    "frozen_at_version": previous_version_id,
                    "datasheets_carried": added,
                },
            )
        )

    for slug in sorted(unused_declaration_slugs):
        faction_id = slug_to_faction_id.get(slug, slug)
        findings.append(
            build_finding(
                "SRC-FACTION-CARRY-FORWARD-UNUSED",
                entity_refs=(f"faction-slug:{slug}",),
                detail={
                    "faction_id": faction_id,
                    "faction_slug": slug,
                    "answers_per_faction": unused_answers_per_faction,
                },
            )
        )

    # -- per-class composition (009 rung R06a, T096, FR-033) ------------------------------------
    #
    # `working` starts from the same two sources the whole-faction splice above already merged,
    # so a per-class target can equally well be an already-live datasheet or a just-carried one
    # (though in practice never the latter: a slug in `class_carried_slugs` is always skipped
    # below when it is also in `carried_slugs`, since the whole faction is frozen already).
    working: list[CuratedDatasheet] = [*snapshot.datasheets, *carried_datasheets]
    composed_any = False
    for data_class in sorted(class_carried_slugs):
        fields = _CLASS_FIELDS[data_class]
        for slug in sorted(class_carried_slugs[data_class]):
            if slug in carried_slugs:
                continue  # the whole faction is already frozen; nothing left to compose
            faction_id = slug_to_faction_id.get(slug)
            prior_rows = prior_datasheets_by_faction.get(faction_id, []) if faction_id else []
            if faction_id is None or not prior_rows:
                findings.append(
                    build_finding(
                        "SRC-FACTION-CARRY-FORWARD-NO-PRIOR",
                        entity_refs=(f"faction-slug:{slug}",),
                        detail={"faction_slug": slug, "data_class": data_class},
                    )
                )
                continue
            prior_by_id = {ds.datasheet_id: ds for ds in prior_rows}
            composed = 0
            for index, current in enumerate(working):
                if current.faction_id != faction_id:
                    continue
                prior_datasheet = prior_by_id.get(current.datasheet_id)
                if prior_datasheet is None:
                    continue  # a datasheet new since the last publish has no prior class to take
                composed_datasheet = current.model_copy(
                    update={field: getattr(prior_datasheet, field) for field in fields}
                )
                # R06a-fix2 item 1: the fields just composed carry ordinals into THIS run's own
                # `weapons`/`composition` (never frozen by `_CLASS_FIELDS`) -- re-resolve them by
                # name before publishing the mixed-vintage datasheet, rather than leaving a
                # frozen ordinal to silently name the wrong row or a now-missing one.
                if data_class == "options":
                    composed_datasheet = _reresolve_options_ordinals(composed_datasheet, findings)
                elif data_class == "default_equipment":
                    composed_datasheet = _reresolve_equipment_ordinals(composed_datasheet, findings)
                working[index] = composed_datasheet
                composed += 1
            if not composed:
                # R06a-fix item 2: prior data existed for the faction, but none of THIS run's
                # datasheet ids for it matched a prior one, so the class has nothing to compose
                # from -- practically the same "nothing to substitute" fact the block above
                # reports for a faction with no prior rows at all, just discovered one join later
                # (rule 10 does not apply here: that rule is about not writing production code
                # for a class never measured in the corpus, not about silencing an already-reached
                # runtime branch). Reusing the same code and detail shape rather than minting a
                # new one for a condition this vocabulary already describes correctly.
                findings.append(
                    build_finding(
                        "SRC-FACTION-CARRY-FORWARD-NO-PRIOR",
                        entity_refs=(f"faction-slug:{slug}",),
                        detail={"faction_slug": slug, "data_class": data_class},
                    )
                )
                continue
            composed_any = True
            findings.append(
                build_finding(
                    "SRC-FACTION-CARRIED-FORWARD",
                    entity_refs=(f"faction:{faction_id}",),
                    detail={
                        "faction_id": faction_id,
                        "faction_slug": slug,
                        "frozen_at_version": previous_version_id,
                        "datasheets_carried": composed,
                        "data_class": data_class,
                    },
                )
            )

    if not carried_datasheets and not composed_any:
        return snapshot, tuple(findings)

    merged = snapshot.model_copy(update={"datasheets": tuple(working)})
    return merged, tuple(findings)
