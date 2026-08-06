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

from pipeline.config import PipelineConfig
from pipeline.curate.prior import PriorSnapshot, classified_keywords
from pipeline.exit_codes import ExitCode
from pipeline.models.curated import CuratedSnapshot, WargearOptionState
from pipeline.models.findings import CoverageFigure, Finding
from pipeline.report.catalogue import build_finding


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
    options_resolved = sum(
        1
        for datasheet in snapshot.datasheets
        if datasheet.wargear_option_state in {WargearOptionState.NONE, WargearOptionState.EXTRACTED}
    )
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
