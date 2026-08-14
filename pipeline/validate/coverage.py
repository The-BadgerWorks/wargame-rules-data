# AI-Assisted: Claude Code (model: claude-opus-5) - Implemented V10, coverage against the
# previous published version (task T094): faction, datasheet, and priced-datasheet counts checked
# against the three configured ratios, exiting 42 on collapse (FR-009).
# AI-Assisted: Claude Code (model: claude-opus-5) - Extended the refusal to composition and
# wargear-option coverage (004 task T033, 004 FR-038), so a source that shrinks either one below
# its configured proportion of the previous release stops the run on the same terms.
# AI-Assisted: Claude Code (model: claude-opus-5) - Extended it again to keyword classification
# (004 task T041, WGC_COVERAGE_MIN_KEYWORD_CLASS_RATIO).
# AI-Assisted: Claude Code (model: claude-opus-5) - Added check_weapon_ability_keywords (issue
# #4): the within-snapshot half of the same question, for the class whose emptiness the
# previous-release comparison cannot see because the previous release was empty too.
# AI-Assisted: Claude Code (model: claude-opus-5) - Added the two 006 loadout figures and the
# named counts behind them (006 task T038): options_resolved_datasheets is now a function
# rather than an inline sum, because the COV-OPTION-REGRESSION ratchet is a SECOND, stricter
# test over the SAME count -- two independently written counts of one thing is how a report
# and a gate end up disagreeing about whether a release regressed (006 FR-022, research D4).
"""V10 — did we just publish a fraction of the release without noticing?

This is the check for the failure that looks like success. A partial response, or an error page
that happens to be well-formed, produces a snapshot in which *every value is correct*: the parser
is satisfied, every FR-030 guarantee holds, the bundle builds, and its checksum reproduces
perfectly. It simply contains a third of the units. Nothing internal to the snapshot can tell —
"is this all of it?" is not a question a document can answer about itself.

So it is answered from outside, by comparing against what was published last time. Three counts,
three separately configured ratios, because they fail differently: a faction missing entirely is
a mapping or acquisition failure, while a datasheet drop inside a faction is more likely a parse
regression. Exit ``42`` is its own code, distinct from a blocking finding, so CI can alert on
"the source went strange" without conflating it with "a curator has work to do".

A first release has no previous published version and therefore cannot collapse. That is not a
gap; it is why FR-009 lands in US2 and not US1.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Final

from pipeline.config import PipelineConfig
from pipeline.curate.prior import PriorSnapshot, classified_keywords
from pipeline.exit_codes import ExitCode
from pipeline.models.curated import CuratedSnapshot, DefaultEquipmentState, WargearOptionState
from pipeline.models.findings import CoverageFigure, Finding
from pipeline.report.catalogue import build_finding
from pipeline.validate.equivalence import EquivalenceSummary

#: The `report.json` coverage rows `006` adds, without their `loadout.` prefix (data-model.md §5).
OPTIONS_RESOLVED_KEY: Final = "options_resolved"
DEFAULT_EQUIPMENT_KEY: Final = "default_equipment"

#: The two `007` US5 rows add (research D7, data-model.md §5). `RENDERING_EQUIVALENCE_KEY`'s
#: companion `_not_compared` count key is built from it below rather than declared separately, so
#: the two can never drift apart in spelling.
ITEM_CONSTRAINTS_KEY: Final = "item_constraints"
RENDERING_EQUIVALENCE_KEY: Final = "rendering_equivalence"
RENDERING_EQUIVALENCE_NOT_COMPARED_KEY: Final = f"{RENDERING_EQUIVALENCE_KEY}_not_compared"

#: Which of them the ratchet actually guards — one of two, and deliberately (research D4).
#:
#: `default_equipment` is **reported and not ratcheted in this first extended release**: no
#: version has ever published the figure, so there is nothing to compare it against, and a
#: first-release threshold picked to have *something* would be exactly the absolute ceiling the
#: 2026-08-09 clarification rules out — a number that can wedge a release ahead of a parser fix.
#: It becomes ratchetable for free the release after this one, when a baseline exists.
#:
#: **`item_constraints` and `rendering_equivalence` are deliberately absent** (007 research D7,
#: FR-022, PO decision 2026-08-13): both are new report-only baselines with no prior release to
#: compare against. Adding either key here is the entire implementation of a future decision to
#: ratchet it — nothing else about how it is computed or reported changes.
LOADOUT_RATCHETED_KEYS: Final[tuple[str, ...]] = (OPTIONS_RESOLVED_KEY,)


@dataclass(slots=True)
class CoverageOutcome:
    """The figures the report states, and the findings any collapse raised."""

    figures: dict[str, CoverageFigure] = field(default_factory=dict)
    findings: list[Finding] = field(default_factory=list)

    @property
    def collapsed(self) -> bool:
        return bool(self.findings)

    @property
    def exit_code(self) -> ExitCode | None:
        """``42`` on collapse. Distinct from ``30`` so alerting can tell the two apart."""
        return ExitCode.COVERAGE_COLLAPSE if self.collapsed else None


@dataclass(frozen=True, slots=True)
class LoadoutCoverage:
    """One `006` loadout figure: how much of the roster resolved, as a proportion of the roster.

    A **proportion**, not a count comparison, and that is the difference from every figure
    :func:`check_coverage` produces. The collapse check below asks "did this release publish a
    fraction of what the last one did?", which is a question about the *source*. This asks "how
    much of what we published did we manage to resolve?", which is a question about the
    *pipeline* — and the two move independently. A release in which the source adds 40 datasheets
    can raise the resolved count while lowering the proportion, and SC-001 is about the
    proportion.
    """

    key: str
    resolved: int
    total: int

    @property
    def ratio_percent(self) -> int:
        """Resolved over the whole roster, as an **integer percent**.

        Integer for the same two reasons ``ClassCoverage.ratio_percent`` is: the canonical scalar
        set excludes ``float`` so report bytes stay reproducible, and the ratchet's comparison has
        to survive a round trip through the previous release's `report.json` unchanged. An empty
        roster is complete rather than zero — there is no outstanding work to have failed at.
        """
        if self.total <= 0:
            return 100
        return round(100 * self.resolved / self.total)


def options_resolved_datasheets(snapshot: CuratedSnapshot) -> int:
    """Datasheets whose option set resolved — ``none`` and ``extracted`` both count.

    A datasheet the source describes no options for is **finished**, not outstanding; counting it
    as a gap would make the figure fall every time a faction of characters shipped. Extracted
    here as a named function rather than left inline because the ratchet
    (:func:`~pipeline.validate.gates.check_option_ratchet`) is a second test over *this* count,
    and two independently written counts of the same thing is how the report and the gate end up
    disagreeing about whether a release regressed.
    """
    return sum(
        1
        for datasheet in snapshot.datasheets
        if datasheet.wargear_option_state in {WargearOptionState.NONE, WargearOptionState.EXTRACTED}
    )


def default_equipment_resolved_datasheets(snapshot: CuratedSnapshot) -> int:
    """The same reading over ``default_equipment_state``, which is a **different enum**.

    Deliberately not folded together with the above. The two states routinely disagree on one
    card — a datacard that states no options and a full equipment sentence, or the reverse — so a
    single "loadout resolved" figure would average away exactly the signal each one exists to
    give.
    """
    return sum(
        1
        for datasheet in snapshot.datasheets
        if datasheet.default_equipment_state
        in {DefaultEquipmentState.NONE, DefaultEquipmentState.EXTRACTED}
    )


def item_constraints_stated_datasheets(snapshot: CuratedSnapshot) -> int:
    """Datasheets stating at least one footnote-style restriction (`007` FR-009, quickstart §4).

    The denominator of `loadout.item_constraints`: a datasheet the source states no restriction
    for is outside the question this figure asks, exactly as an option-free datasheet is outside
    `loadout.options_resolved`'s (`options_resolved_datasheets` above).
    """
    return sum(1 for datasheet in snapshot.datasheets if datasheet.item_constraints)


def item_constraints_resolved_datasheets(snapshot: CuratedSnapshot) -> int:
    """Of the datasheets above, those whose stated restrictions **all** resolved (linked).

    One unlinked (`CST-UNLINKED`) restriction is enough to keep the whole datasheet out of the
    numerator — a datasheet with two restrictions, one linked, is not "half resolved" for this
    figure's purpose, it is a datasheet a reviewer still needs to look at.
    """
    return sum(
        1
        for datasheet in snapshot.datasheets
        if datasheet.item_constraints
        and all(constraint.weapon_line is not None for constraint in datasheet.item_constraints)
    )


def loadout_coverages(
    snapshot: CuratedSnapshot, equivalence: EquivalenceSummary | None = None
) -> dict[str, LoadoutCoverage]:
    """`006`'s two figures plus `007`'s two new ones, keyed without their `loadout.` prefix
    (FR-022, data-model.md §5).

    ``equivalence`` is the `EquivalenceSummary` `pipeline.cli.run_build` computed inside its own
    `with workspace()` block (007 T053) — the only place source text is ever in scope (research
    D6). `None` means "not measured this run" (the check disabled, or a bare `validate` re-run
    with no source text at all): `rendering_equivalence` and its `_not_compared` companion are
    simply **absent** from the returned dict in that case, never reported as a false 100%.
    """
    total = len(snapshot.datasheets)
    coverages: dict[str, LoadoutCoverage] = {
        OPTIONS_RESOLVED_KEY: LoadoutCoverage(
            key=OPTIONS_RESOLVED_KEY, resolved=options_resolved_datasheets(snapshot), total=total
        ),
        DEFAULT_EQUIPMENT_KEY: LoadoutCoverage(
            key=DEFAULT_EQUIPMENT_KEY,
            resolved=default_equipment_resolved_datasheets(snapshot),
            total=total,
        ),
        ITEM_CONSTRAINTS_KEY: LoadoutCoverage(
            key=ITEM_CONSTRAINTS_KEY,
            resolved=item_constraints_resolved_datasheets(snapshot),
            total=item_constraints_stated_datasheets(snapshot),
        ),
    }
    if equivalence is not None:
        # `not_compared` outcomes are excluded from both numerator and denominator (research D7,
        # data-model.md §5) — a datasheet nobody could compare must not move the proportion
        # either way. Reported instead as its own count, a second `LoadoutCoverage` whose
        # `resolved`/`total` are deliberately the SAME number: its `ratio_percent` is therefore
        # always 100 and is not the figure a reader wants from this row — `current` (the raw
        # count) is. See `pipeline/report/pr_body.py::_loadout_coverage_section`'s footer text.
        compared = equivalence.matched + equivalence.mismatched
        coverages[RENDERING_EQUIVALENCE_KEY] = LoadoutCoverage(
            key=RENDERING_EQUIVALENCE_KEY, resolved=equivalence.matched, total=compared
        )
        coverages[RENDERING_EQUIVALENCE_NOT_COMPARED_KEY] = LoadoutCoverage(
            key=RENDERING_EQUIVALENCE_NOT_COMPARED_KEY,
            resolved=equivalence.not_compared,
            total=equivalence.not_compared,
        )
    return coverages


def _ratio(current: int, previous: int) -> float:
    """``current / previous``, with an empty baseline treated as full coverage.

    Dividing by a previous count of zero is not an error state: it means the previous release
    published none of this category, so there is nothing for the current one to have lost.
    """
    if previous <= 0:
        return 1.0
    return current / previous


def check_weapon_ability_keywords(snapshot: CuratedSnapshot) -> list[Finding]:
    """``COV-WEAPON-ABILITIES-EMPTY`` — weapon lines ship, and none states an ability keyword.

    The comparison above answers "is this all of it?" by looking at the previous release. That
    only works while the previous release had the thing. Issue #4 is the case where it did not:
    ``CuratedWeaponLine.ability_keywords`` was empty on all 9,305 published weapon lines, every
    release, so the ratio was a stable 1.0 and every other check was satisfied — the rows were
    present, the characteristics were right, the bundle reproduced byte for byte.

    So this one asks the question from *inside* the snapshot, where it can be asked at all: a
    release that publishes weapons and not one weapon ability keyword is not a plausible edition,
    it is an extraction that stopped. **Advisory**, deliberately: the reading is a judgement about
    plausibility rather than a violated guarantee, and refusing to publish a release over it would
    be refusing over a heuristic. It appears in the report and in the scale block beside it, which
    is all it needs to do — this defect survived because nothing said anything, not because
    somebody read a warning and shipped anyway.

    Deliberately **not** a proportional threshold. A partial recovery is a normal shape — most
    weapons state no ability keyword at all — and any floor picked for it would be invented. Zero
    is the one figure that means something on its own.

    Kept out of :class:`CoverageOutcome` because that type's ``collapsed`` property drives exit
    code 42: an advisory placed in it would refuse publication, which is precisely the severity
    override the catalogue exists to make impossible.
    """
    weapon_lines = sum(len(datasheet.weapons) for datasheet in snapshot.datasheets)
    if not weapon_lines:
        return []
    carrying = sum(
        1
        for datasheet in snapshot.datasheets
        for weapon in datasheet.weapons
        if weapon.ability_keywords
    )
    if carrying:
        return []
    return [
        build_finding(
            "COV-WEAPON-ABILITIES-EMPTY",
            entity_refs=["coverage:weapon_ability_keywords"],
            detail={"weapon_lines": weapon_lines, "weapon_lines_with_keywords": 0},
        )
    ]


def check_coverage(
    snapshot: CuratedSnapshot, prior: PriorSnapshot | None, config: PipelineConfig
) -> CoverageOutcome:
    """Compare this candidate's coverage with the previous published version."""
    outcome = CoverageOutcome()
    if prior is None:
        return outcome

    priced = sum(1 for datasheet in snapshot.datasheets if datasheet.costs)
    composed = sum(1 for datasheet in snapshot.datasheets if datasheet.composition)
    options_resolved = options_resolved_datasheets(snapshot)
    categories: Mapping[str, tuple[int, int, float]] = {
        "factions": (
            len(snapshot.factions),
            prior.faction_count,
            config.coverage_min_faction_ratio,
        ),
        "datasheets": (
            len(snapshot.datasheets),
            prior.datasheet_count,
            config.coverage_min_datasheet_ratio,
        ),
        "priced_datasheets": (
            priced,
            prior.priced_datasheet_count,
            config.coverage_min_priced_ratio,
        ),
        # 004-rules-data-enrichment (FR-038). The two new classes fail the same way as the
        # three above and for the same reason: a partial or error response that *parses* leaves
        # every value correct and simply contains less. A grammar that quietly stops matching
        # is indistinguishable from a source that quietly stopped publishing, and neither is
        # visible from inside the snapshot — only against what was published last time.
        "composition": (
            composed,
            prior.composition_datasheet_count,
            config.coverage_min_composition_ratio,
        ),
        "wargear_options": (
            options_resolved,
            prior.option_resolved_datasheet_count,
            config.coverage_min_option_ratio,
        ),
        # Keyword classification collapses the same way and is worth its own ratio: the class is
        # authored per keyword against a *derived* default, so a faction-map change that quietly
        # stops resolving a keyword to its parentless faction moves several dozen keywords from
        # `faction` to unclassified at once, with every remaining value still correct.
        "keyword_classification": (
            len(classified_keywords(snapshot)),
            prior.classified_keyword_count,
            config.coverage_min_keyword_class_ratio,
        ),
    }

    for category, (current, previous, threshold) in categories.items():
        ratio = _ratio(current, previous)
        outcome.figures[category] = CoverageFigure(
            current=current, previous=previous, ratio=round(ratio, 4), threshold=threshold
        )
        if ratio < threshold:
            outcome.findings.append(
                build_finding(
                    "COV-COLLAPSE",
                    entity_refs=[f"coverage:{category}"],
                    detail={
                        "category": category,
                        "current": current,
                        "previous": previous,
                        "previous_version": prior.rules_version_id or "",
                        "ratio_percent": round(ratio * 100),
                        "threshold_percent": round(threshold * 100),
                    },
                )
            )

    return outcome
