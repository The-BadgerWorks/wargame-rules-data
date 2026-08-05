# AI-Assisted: Claude Code (model: claude-opus-5) - Generalised V7 over the four summary classes
# (004 task T046): the gate-selects-a-code rule of contracts/authored-summary-gates.md §3, the
# three WGC_GATE_* switches beside the abilities class's switch-less always-on path, §4.1's
# per-class denominators, and the COV-SUMMARY-REGRESSION ratchet in integer percents
# (004 FR-029, FR-030).
# AI-Assisted: Claude Code (model: claude-opus-5) - Added the detachment-rule denominator (004
# task T054): every published detachment rule, read off the SOURCE-derived
# CuratedDetachment.rules rather than off the curator's own file.
# AI-Assisted: Claude Code (model: claude-opus-5) - Added the glossary denominator, its
# faction/chapter exclusion, and the GLS-ORPHANED advisory (004 task T061, contract §4.1/§5.1).
"""V7, generalised — every authored summary class, one gate mechanism.

**A gate selects a code. It never selects a severity.** That single sentence is why this module
exists rather than a boolean parameter on the existing ability check. `validation-report.md`'s
non-negotiable #1 fixes severity to the code, and FR-029 wants per-class gates that can be
switched independently; the careless reconciliation — a switch that makes a blocking finding
advisory — satisfies FR-029 and silently converts a governance guarantee into a per-run
judgement call. So the switch chooses *which* code is emitted, and each code's severity stays in
:mod:`pipeline.report.catalogue` where nothing here can reach it.

============  ======================================================  ===========
Gate          Entry state                                              Code
============  ======================================================  ===========
off           missing / draft / in_review / needs_rereview             ``-OUTSTANDING`` *(advisory)*
on            no record at all                                         ``-MISSING``
on            a record exists, not ``approved``                        ``-UNAPPROVED``
on            approved, digest moved                                   ``-NEEDS-REREVIEW``
either        approved, over the length target                         ``-OVERLENGTH`` *(advisory)*
============  ======================================================  ===========

Two properties worth stating because they are easy to lose:

* **The abilities class has no switch.** It predates this feature and FR-001 forbids weakening a
  guarantee inherited from `002`, so :func:`gate_for` returns ``on`` for it unconditionally and
  there is no configuration variable that could say otherwise.
* **Each class is evaluated on its own** (SC-013): a complete class is never held back by an
  incomplete one, and switching one gate on refuses publication for that class's gaps only.

**The ratchet applies whether or not a gate is on** (§4). That is precisely what makes a
gates-off first release safe: a campaign that has reached 40% cannot quietly fall back to 30%
just because nothing is blocking on it yet. Its tolerance is configuration; its severity is not,
and it is deliberately **one code across all four classes** with the class in its ``detail`` —
a per-class code would invite a per-class severity, which is the failure §3 exists to prevent.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

from pipeline.config import Gate, PipelineConfig
from pipeline.curate.summaries import (
    AuthoredSummary,
    SummaryStatus,
    glossary_key,
    summary_statuses,
)
from pipeline.models.authored import (
    DetachmentRuleSummary,
    FactionRuleFile,
    GlossaryEntry,
    SummaryClass,
)
from pipeline.models.curated import ArmyRuleState, CuratedSnapshot, KeywordClass
from pipeline.models.findings import CoverageFigure, Finding
from pipeline.normalize.keyword_key import keyword_key
from pipeline.report.catalogue import build_finding

#: The blocking code a gated-on class emits for each reason an entry lacks an approved summary.
#: Kept distinct because a curator reading the report needs to know which one to act on:
#: "nobody has started this", "someone has, it is not signed off", "it was signed off and the
#: mechanic moved since". Only the last can apply to an entry a curator has already worked on.
_STATUS_SUFFIX: Mapping[SummaryStatus, str] = {
    SummaryStatus.MISSING: "MISSING",
    SummaryStatus.DRAFT: "UNAPPROVED",
    SummaryStatus.IN_REVIEW: "UNAPPROVED",
    SummaryStatus.NEEDS_REREVIEW: "NEEDS-REREVIEW",
}


@dataclass(frozen=True, slots=True)
class ClassCheck:
    """Everything one class's gate needs, and nothing about any other class.

    The argument list is the independence guarantee written down: there is no field here through
    which one class's state could reach another's verdict.
    """

    summary_class: SummaryClass
    keys: Sequence[str]
    """The denominator — every key this snapshot uses in this class (contract §4.1)."""

    authored: Mapping[str, AuthoredSummary] = field(default_factory=dict)
    current_digests: Mapping[str, str] | None = None
    """This run's freshly computed digests, or ``None`` when it acquired no source text."""

    gate: Gate = Gate.ON
    max_chars: int = 240


@dataclass(frozen=True, slots=True)
class ClassCoverage:
    """One class's approved coverage, as the report states it and the ratchet compares it."""

    summary_class: SummaryClass
    approved: int
    total: int
    outstanding: tuple[str, ...]
    gate: Gate = Gate.ON

    @property
    def ratio_percent(self) -> int:
        """Approved over the denominator, as an **integer percent**.

        Integer because the canonical scalar set excludes ``float`` so bundle and report bytes
        stay reproducible (FR-039/SC-012), and because the ratchet's comparison has to survive a
        round trip through the previous release's `report.json` unchanged. A class with an empty
        denominator is complete rather than zero: there is no work outstanding to have done.
        """
        if self.total <= 0:
            return 100
        return round(100 * self.approved / self.total)


def gate_for(summary_class: SummaryClass, config: PipelineConfig) -> Gate:
    """The class's gate. **Always on for abilities**, which has no switch (FR-001)."""
    if summary_class is SummaryClass.FACTION_RULES:
        return config.gate_faction_rules
    if summary_class is SummaryClass.DETACHMENT_RULES:
        return config.gate_detachment_rules
    if summary_class is SummaryClass.GLOSSARY:
        return config.gate_glossary
    return Gate.ON


def max_chars_for(summary_class: SummaryClass, config: PipelineConfig) -> int:
    """The class's configured length target. Over-length is advisory, never blocking."""
    if summary_class is SummaryClass.FACTION_RULES:
        return config.faction_rule_max_chars
    if summary_class is SummaryClass.DETACHMENT_RULES:
        return config.detachment_rule_max_chars
    if summary_class is SummaryClass.GLOSSARY:
        return config.glossary_max_chars
    return config.summary_max_chars


def tolerance_for(summary_class: SummaryClass, config: PipelineConfig) -> float:
    """The class's ratchet tolerance. Configuration; the ratchet's severity is not (§4)."""
    if summary_class is SummaryClass.FACTION_RULES:
        return config.ratchet_tolerance_faction_rules
    if summary_class is SummaryClass.DETACHMENT_RULES:
        return config.ratchet_tolerance_detachment_rules
    if summary_class is SummaryClass.GLOSSARY:
        return config.ratchet_tolerance_glossary
    return config.ratchet_tolerance_abilities


def class_statuses(check: ClassCheck) -> dict[str, SummaryStatus]:
    """The effective status of every key in this class, once each."""
    return summary_statuses(
        check.keys, authored=check.authored, current_digests=check.current_digests
    )


def check_class(check: ClassCheck) -> list[Finding]:
    """The findings one class's gate raises — see the module docstring's table."""
    prefix = check.summary_class.finding_prefix
    key_field = check.summary_class.key_field

    findings: list[Finding] = []
    for key, status in sorted(class_statuses(check).items()):
        if status is not SummaryStatus.APPROVED:
            # The `-OUTSTANDING` collapse is deliberate: while a gate is off, the difference
            # between "not started" and "not signed off" is editorial rather than operational,
            # and the coverage report names the entries either way.
            code = (
                f"{prefix}-OUTSTANDING"
                if check.gate is Gate.OFF and check.summary_class.has_gate_switch
                else f"{prefix}-{_STATUS_SUFFIX[status]}"
            )
            findings.append(build_finding(code, entity_refs=[key], detail={key_field: key}))
            continue

        # APPROVED is the only status left, and the only one the length check applies to: a
        # summary that is not approved yet is already reported for a different reason, and naming
        # a length problem on an unfinished draft asks a curator to fix the wrong thing.
        summary = check.authored[key]
        if len(summary.summary) > check.max_chars:
            findings.append(
                build_finding(
                    f"{prefix}-OVERLENGTH",
                    entity_refs=[key],
                    detail={
                        key_field: key,
                        "length": len(summary.summary),
                        "max_chars": check.max_chars,
                    },
                )
            )

    return findings


def class_coverage(check: ClassCheck) -> ClassCoverage:
    """One class's approved coverage over §4.1's denominator.

    "Approved" means :attr:`~pipeline.curate.summaries.SummaryStatus.APPROVED` *for this run* —
    current against the freshly computed digest where one exists, not merely stored as approved
    in ``curation/``. The coverage figure and the gate can therefore never disagree about one
    entry's status, which is what stops an approver reading a clean-looking table over a blocked
    release.
    """
    statuses = class_statuses(check)
    outstanding = tuple(
        key for key, status in sorted(statuses.items()) if status is not SummaryStatus.APPROVED
    )
    return ClassCoverage(
        summary_class=check.summary_class,
        approved=len(statuses) - len(outstanding),
        total=len(statuses),
        outstanding=outstanding,
        gate=check.gate,
    )


def check_summary_gates(checks: Sequence[ClassCheck]) -> list[Finding]:
    """Every class's gate, evaluated independently (FR-029, SC-013)."""
    return [finding for check in checks for finding in check_class(check)]


def check_summary_ratchet(
    coverages: Sequence[ClassCoverage],
    *,
    previous_percent: Mapping[SummaryClass, int],
    tolerances: Mapping[SummaryClass, float],
) -> list[Finding]:
    """``COV-SUMMARY-REGRESSION`` — approved coverage of a class must not fall (§4).

    Args:
        previous_percent: the **previously published** version's approved-coverage percent per
            class, read back from its retained `report.json`. The previous *published* version,
            not the previous candidate, so a rejected candidate cannot move the ratchet.
        tolerances: per-class, from configuration, defaulting to no regression at all. A class
            with no previous figure — a first release, or a campaign that has not started — has
            nothing to fall from and cannot regress.
    """
    findings: list[Finding] = []
    for coverage in coverages:
        previous = previous_percent.get(coverage.summary_class)
        if previous is None:
            continue
        tolerance_percent = round(100 * tolerances.get(coverage.summary_class, 0.0))
        if coverage.ratio_percent < previous - tolerance_percent:
            findings.append(
                build_finding(
                    "COV-SUMMARY-REGRESSION",
                    entity_refs=[f"coverage:summaries.{coverage.summary_class.value}"],
                    detail={
                        "class": coverage.summary_class.value,
                        "previous_ratio_percent": previous,
                        "current_ratio_percent": coverage.ratio_percent,
                        "tolerance_percent": tolerance_percent,
                    },
                )
            )
    return findings


def used_ability_keys(snapshot: CuratedSnapshot) -> set[str]:
    """Every ability key at least one shipped datasheet references (§4.1)."""
    return {key for datasheet in snapshot.datasheets for key in datasheet.ability_keys}


def faction_rule_files(
    snapshot: CuratedSnapshot, authored: Mapping[str, FactionRuleFile] | None = None
) -> Mapping[str, FactionRuleFile]:
    """The authored faction-rule files this run should read.

    ``authored`` wins where it is given, because a snapshot reconstructed from ``data/`` alone —
    a bare ``validate`` re-run — never carries authored content: it is never written to the
    curated tree (FR-017). The two callers therefore pass different things and get the same
    answer, which is the property that stops ``build`` and ``validate`` disagreeing about a
    faction's coverage.
    """
    return authored if authored is not None else snapshot.faction_rules


def faction_rule_keys(
    snapshot: CuratedSnapshot, authored: Mapping[str, FactionRuleFile] | None = None
) -> tuple[str, ...]:
    """§4.1's faction-rule denominator, which is three-valued rather than two.

    * ``army_rule_state = present`` — every rule of that faction, by its own ``summary_key``.
    * ``army_rule_state = none`` — **nothing**. A faction with genuinely no army rule is a
      finished curation decision, not outstanding work, and counting it as a gap would make the
      figure fall every time a mercenary faction shipped.
    * **no curation file at all** — one outstanding key, ``faction:<faction-id>``, standing for
      "nobody has looked at this faction yet". It has no authored record, so it reports as
      missing or outstanding exactly as an unwritten rule does.
    """
    files = faction_rule_files(snapshot, authored)
    keys: list[str] = []
    for faction in sorted(snapshot.factions, key=lambda f: f.faction_id):
        file = files.get(faction.faction_id)
        if file is None:
            keys.append(f"faction:{faction.faction_id}")
            continue
        if file.army_rule_state == ArmyRuleState.NONE:
            continue
        keys.extend(sorted(rule.summary_key for rule in file.rules))
    return tuple(keys)


def faction_rule_summaries(
    snapshot: CuratedSnapshot, authored: Mapping[str, FactionRuleFile] | None = None
) -> dict[str, AuthoredSummary]:
    """Every authored faction rule, keyed by ``summary_key`` across all factions."""
    return {
        rule.summary_key: rule
        for file in faction_rule_files(snapshot, authored).values()
        for rule in file.rules
    }


def detachment_rule_keys(snapshot: CuratedSnapshot) -> tuple[str, ...]:
    """§4.1's detachment-rule denominator: **every published detachment rule**.

    Two-valued rather than three, unlike the faction-rule denominator, and deliberately so. A
    detachment publishes the rules it publishes; there is no "this detachment genuinely has no
    rule" curation decision to record, because a detachment with no rules simply contributes no
    keys. The denominator therefore comes from :attr:`CuratedDetachment.rules` — the **source** —
    and never from the authored file, which would let coverage measure itself and report 100%
    for a campaign nobody had started.
    """
    return tuple(
        sorted(rule.summary_key for detachment in snapshot.detachments for rule in detachment.rules)
    )


def detachment_rule_summaries(
    snapshot: CuratedSnapshot, authored: Mapping[str, DetachmentRuleSummary] | None = None
) -> dict[str, AuthoredSummary]:
    """Every authored detachment rule, keyed by ``summary_key`` across all factions.

    ``authored`` wins where it is given, for the same reason it does for faction rules: a
    snapshot reconstructed from ``data/`` alone carries no authored content, so ``build`` and
    ``validate`` must read it from one place or disagree about a faction's coverage.
    """
    records = authored if authored is not None else snapshot.detachment_rules
    return dict(records)


def used_keyword_keys(snapshot: CuratedSnapshot) -> tuple[str, ...]:
    """Every distinct ``keyword_key`` a published datasheet or weapon uses, **excluding**
    faction and chapter keywords (§4.1, FR-023).

    The exclusion is the interesting half. A faction or chapter keyword is a *label for who the
    unit belongs to*, not a mechanic anyone could define, so counting it would make the glossary's
    denominator permanently unreachable and its coverage figure meaningless — which is why the
    keyword classification of US2 and this class ship in the same feature. Excluded means
    **excluded, not counted as missing work**: an unclassified keyword is still counted, because
    "nobody has classified this yet" is not evidence that it needs no definition.

    Weapon ability keywords are counted in full. They are mechanics by construction — a weapon
    ability is never a faction label — so there is nothing to exclude among them.
    """
    keys: set[str] = set()
    for datasheet in snapshot.datasheets:
        for keyword in datasheet.keywords:
            if keyword.keyword_class in (KeywordClass.FACTION, KeywordClass.CHAPTER):
                continue
            if resolved := keyword_key(keyword.keyword):
                keys.add(resolved)
        for weapon in datasheet.weapons:
            for ability in weapon.ability_keywords:
                if resolved := keyword_key(ability):
                    keys.add(resolved)
    return tuple(sorted(keys))


def glossary_keys(snapshot: CuratedSnapshot) -> tuple[str, ...]:
    """§4.1's glossary denominator, in the class's own ``summary_key`` vocabulary.

    One entry serves a keyword and **every casing, spacing, punctuation and numeric-parameter
    variant of it**, because the variants have already collapsed to one ``keyword_key`` before
    they reach here (FR-023). That is why the denominator counts keys and not usages.
    """
    return tuple(glossary_key(key) for key in used_keyword_keys(snapshot))


def glossary_summaries(
    snapshot: CuratedSnapshot, authored: Mapping[str, GlossaryEntry] | None = None
) -> dict[str, AuthoredSummary]:
    """Every authored glossary entry, re-keyed by ``summary_key``.

    The authored tree indexes the glossary by ``keyword_key`` because that is its primary key;
    the gate machinery indexes every class by its ``summary_key`` so that one code path serves
    four classes. This is the one line where the two meet.
    """
    entries = authored if authored is not None else snapshot.keyword_glossary
    return {glossary_key(keyword): entry for keyword, entry in entries.items()}


def check_glossary_orphans(
    snapshot: CuratedSnapshot, authored: Mapping[str, GlossaryEntry] | None = None
) -> list[Finding]:
    """``GLS-ORPHANED`` — a definition no published datasheet or weapon uses (§3.1, FR-023).

    Advisory, and deliberately so: a keyword that has left the edition is not a defect in the
    candidate, it is editorial debt. But it is debt that accumulates silently — nothing else in
    the pipeline would ever mention an entry nobody looks up — so the glossary would quietly fill
    with definitions for keywords that no longer exist. This is also one of the two compensating
    controls for the digest limitation of §5.1, since a stem-digested entry can never flag for
    re-review on its own.

    The comparison is against the **unfiltered** keyword vocabulary, not the coverage
    denominator: an entry a curator wrote for a keyword that turned out to be a faction keyword
    is defined-but-excluded, which is a different thing from unused, and calling it an orphan
    would send a curator to delete a correct entry.
    """
    entries = authored if authored is not None else snapshot.keyword_glossary
    in_use = {
        resolved
        for datasheet in snapshot.datasheets
        for source in (
            (keyword.keyword for keyword in datasheet.keywords),
            (ability for weapon in datasheet.weapons for ability in weapon.ability_keywords),
        )
        for value in source
        if (resolved := keyword_key(value))
    }
    return [
        build_finding(
            "GLS-ORPHANED",
            entity_refs=[glossary_key(keyword)],
            detail={"summary_key": glossary_key(keyword), "keyword_key": keyword},
        )
        for keyword in sorted(entries)
        if keyword not in in_use
    ]


def summary_coverage_figures(
    coverages: Sequence[ClassCoverage],
    *,
    previous_approved: Mapping[SummaryClass, int],
    previous_percent: Mapping[SummaryClass, int],
    tolerances: Mapping[SummaryClass, float],
) -> dict[str, CoverageFigure]:
    """The ``summaries.<class>`` rows of the report's coverage block (data-model.md §5).

    They belong in that block rather than in ``scale`` because the question they answer is the
    block's own question — how does this candidate compare with the previously published version
    — and because ``threshold`` is where the ratchet floor becomes visible to an approver
    without their having to know the tolerance configuration.
    """
    figures: dict[str, CoverageFigure] = {}
    for coverage in coverages:
        summary_class = coverage.summary_class
        floor = previous_percent.get(summary_class, 0) - round(
            100 * tolerances.get(summary_class, 0.0)
        )
        figures[f"summaries.{summary_class.value}"] = CoverageFigure(
            current=coverage.approved,
            previous=previous_approved.get(summary_class, 0),
            ratio=round(coverage.ratio_percent / 100, 4),
            threshold=round(max(floor, 0) / 100, 4),
        )
    return figures
