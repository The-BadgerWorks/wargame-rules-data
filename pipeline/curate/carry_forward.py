# AI-Assisted: Claude Code (model: claude-sonnet-5) - Implemented the per-faction carry-forward
# splice (008 FR-024/FR-025, Product Owner decision 2026-08-17, following T074's dry-run finding
# that the live detail source currently omits several factions from its own sitemap). A declared
# faction the acquisition layer could not fetch this run (pipeline/acquire/wahapedia_html.py) is
# spliced in here from the previous published tree, AFTER assembly and BEFORE coverage/ratchet
# comparison runs -- so a carried faction's datasheets simply look "present, unchanged" to every
# coverage figure, which is what makes FR-025's "no figure regresses because of a carry-forward"
# true structurally rather than by a special case in pipeline/validate/coverage.py.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - 009 rung R06a-fix3: reverted the per-class
# composition this module carried (009 T096, FR-033, added then corrected across R06a-fix and
# R06a-fix2). Withdrawn, not merely rolled back to an earlier bug: three fix rounds each closed
# one defect and exposed the next, and all four shared one root -- freezing a SUBSET of a
# datasheet's fields breaks invariants that only hold when the whole datasheet moves together
# (link passes assume a fresh parse; `curation/option-overrides.json` assumes a post-link merge
# and exists precisely because a name-join overrules it; priced projections assume same-run
# costs; and the splice kept reintroducing silent paths). Whole-faction freeze, below, is immune
# to all four because it moves ordinals, overrides, prices, and referents together as one unit.
# Recorded for whoever revisits T096 at R07 (once a class sits on the html arm in production) in
# `docs/follow-ups.md` item 37; item 36 there records the specific defect class this withdrawal
# leaves real but undemonstrated. What stays: `resolve_carried_forward` reporting a declared slug
# as `unused` rather than dropping it under any arm but `html`, and the arm-aware `unused`
# rendering in `pipeline/report/pr_body.py` -- the rung's actual purpose, untouched by this
# revert.
"""Splice declared, unreachable-this-run factions in from the previous published tree.

Three outcomes, one per declared slug, and each is a `Finding` — never silent (FR-025):

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

Determinism (008 FR-024's requirement (c)): every carried datasheet is copied from
``read_curated_tree``'s own parse of the git-committed `data/<edition>/` tree at the commit this
run reads — the same input `_reconcile_against_prior`'s ratchet baseline already reads, and
already reproducible for the same reason that comparison is. Nothing here touches a live source a
second time.
"""

from __future__ import annotations

from pipeline.models.curated import CuratedDatasheet, CuratedSnapshot
from pipeline.models.findings import Finding
from pipeline.report.catalogue import build_finding


def apply_carried_forward(
    snapshot: CuratedSnapshot,
    *,
    previous_tree: CuratedSnapshot | None,
    carried_slugs: frozenset[str],
    unused_declaration_slugs: frozenset[str],
    previous_version_id: str,
    unused_answers_per_faction: bool = True,
) -> tuple[CuratedSnapshot, tuple[Finding, ...]]:
    """Return ``snapshot`` with every carried faction's datasheets spliced in, plus findings.

    A no-op, returning ``snapshot`` unchanged, when neither ``carried_slugs`` nor
    ``unused_declaration_slugs`` names anything — the overwhelming majority of runs, including
    every run before this feature and every run once the source recovers, so a declaration-free
    build pays nothing for this function existing.

    ``unused_answers_per_faction`` (R06a-fix item 3): whether THIS run's configured detail arm can
    even answer "did this one faction's page come back" at all —
    :func:`pipeline.acquire.detail_source.resolve_carried_forward`'s own
    ``CarriedForwardOutcome.answers_per_faction``, true only under ``html``. Under a bulk arm
    (``csv``) a declared slug is unconditionally reported ``unused`` the moment the whole export
    answers (FR-032), which is a true but much weaker fact than "this faction's own page was
    reachable" — carried into the finding's ``detail`` so a reader (`pr_body.py`) does not confuse
    the two and advise retiring a declaration a bulk arm was never in a position to test.
    """
    if not carried_slugs and not unused_declaration_slugs:
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

    if not carried_datasheets:
        return snapshot, tuple(findings)

    merged = snapshot.model_copy(update={"datasheets": (*snapshot.datasheets, *carried_datasheets)})
    return merged, tuple(findings)
