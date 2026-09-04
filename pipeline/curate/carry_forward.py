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
#: `options` carries `wargear_options` alongside the three raw fields it is derived from
#: (`option_groups`, `option_choices`, `wargear_option_state`): that is the PRICED projection
#: (`curate/assemble.py`'s own `_costs()`), and composing the raw fields from the prior tree
#: while leaving this run's own (empty-source) pricing in place would ship a datasheet whose own
#: two option views disagree with each other.
_CLASS_FIELDS: Final[Mapping[str, tuple[str, ...]]] = {
    "options": ("option_groups", "option_choices", "wargear_option_state", "wargear_options"),
    "default_equipment": ("equipment_groups", "default_equipment_state"),
}

#: The immutable default for `apply_carried_forward`'s `class_carried_slugs` -- a plain `{}`
#: literal as a mutable default would be a classic Python trap; this is the module-level
#: singleton every un-hybrid caller (the overwhelming majority of runs) actually gets.
_NO_CLASS_CARRY: Final[Mapping[str, frozenset[str]]] = MappingProxyType({})


def apply_carried_forward(
    snapshot: CuratedSnapshot,
    *,
    previous_tree: CuratedSnapshot | None,
    carried_slugs: frozenset[str],
    unused_declaration_slugs: frozenset[str],
    previous_version_id: str,
    class_carried_slugs: Mapping[str, frozenset[str]] = _NO_CLASS_CARRY,
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
                detail={"faction_id": faction_id, "faction_slug": slug},
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
                working[index] = current.model_copy(
                    update={field: getattr(prior_datasheet, field) for field in fields}
                )
                composed += 1
            if not composed:
                continue  # rule 10: a class measured at zero here gets no finding either
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
