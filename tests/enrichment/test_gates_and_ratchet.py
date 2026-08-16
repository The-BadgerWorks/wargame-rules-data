# AI-Assisted: Claude Code (model: claude-opus-5) - Wrote the gate and ratchet suite (004 task
# T044), confirmed failing before pipeline/validate/gates.py existed: gate independence, the
# gate-selects-a-code rule of contracts/authored-summary-gates.md §3, and the coverage ratchet
# that applies whether or not a class's gate is on (004 FR-029, FR-030, SC-011, SC-013).
# AI-Assisted: Claude Code (model: claude-opus-5) - Added the COV-OPTION-REGRESSION ratchet's
# suite (006 task T037), confirmed failing before pipeline/validate/gates.py knew the code: a
# missing baseline never blocks, a fall past the tolerance blocks, an improvement and a hold never
# do, a rejected candidate never moves the baseline, and loadout.default_equipment is reported
# without being ratcheted (006 FR-022, research D4).
"""A gate selects a code. It never selects a severity, and it never selects another class's.

This is the single most important rule in `contracts/authored-summary-gates.md`, and the reason
it needs its own suite is that the careless implementation — a boolean that flips a finding from
advisory to blocking — passes every obvious test while quietly turning `validation-report.md`'s
non-negotiable #1 into a per-run judgement call. So the assertions below check the *code* that is
emitted and read the severity back out of the catalogue, never out of the occurrence.

The ratchet is here for the mirror-image reason: it applies **whether or not the gate is on**,
which is what makes a gates-off first release safe. Without it a campaign that had reached 40%
could quietly fall back to 30% precisely because nothing was blocking on it yet.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pipeline.cli import run_build
from pipeline.config import Gate, load_config
from pipeline.curate.authored import load_authored
from pipeline.curate.prior import (
    previous_loadout_coverage,
    previous_summary_coverage,
    prior_from_snapshot,
)
from pipeline.models.authored import ReviewState, SummaryClass
from pipeline.models.curated import (
    CuratedItemConstraint,
    DefaultEquipmentState,
    ItemConstraintType,
    WargearOptionState,
)
from pipeline.models.findings import Severity
from pipeline.report.catalogue import CATALOGUE
from pipeline.validate.coverage import (
    DEFAULT_EQUIPMENT_KEY,
    ITEM_CONSTRAINTS_KEY,
    LOADOUT_RATCHETED_KEYS,
    OPTIONS_RESOLVED_KEY,
    RENDERING_EQUIVALENCE_KEY,
    RENDERING_EQUIVALENCE_NOT_COMPARED_KEY,
    LoadoutCoverage,
    check_coverage,
    default_equipment_resolved_datasheets,
    loadout_coverages,
    options_resolved_datasheets,
)
from pipeline.validate.equivalence import EquivalenceSummary
from pipeline.validate.gates import (
    ClassCheck,
    check_option_ratchet,
    check_summary_gates,
    check_summary_ratchet,
    class_coverage,
    faction_rule_keys,
)
from tests.enrichment.test_class_state_machine import KEYS, record
from tests.factories import datasheet, faction, snapshot

FIXTURE_CURATION = Path(__file__).resolve().parents[2] / "fixtures" / "enrichment" / "curation"


def _check(summary_class: SummaryClass, *, review_state: ReviewState, gate: Gate) -> ClassCheck:
    key = KEYS[summary_class]
    return ClassCheck(
        summary_class=summary_class,
        keys=(key,),
        authored={key: record(summary_class, key, review_state=review_state)},  # type: ignore[dict-item]
        gate=gate,
    )


def _complete(summary_class: SummaryClass, *, gate: Gate) -> ClassCheck:
    key = KEYS[summary_class]
    return ClassCheck(
        summary_class=summary_class,
        keys=(key,),
        authored={key: record(summary_class, key)},  # type: ignore[dict-item]
        current_digests={key: "d" * 32},
        gate=gate,
    )


# --- the gate-selects-a-code table (contract §3) ------------------------------------------------


@pytest.mark.parametrize(
    ("review_state", "expected"),
    [
        (None, "MISSING"),
        (ReviewState.DRAFT, "UNAPPROVED"),
        (ReviewState.IN_REVIEW, "UNAPPROVED"),
        (ReviewState.NEEDS_REREVIEW, "NEEDS-REREVIEW"),
    ],
)
def test_the_on_state_emits_the_blocking_code_for_the_entrys_reason(
    review_state: ReviewState | None, expected: str
) -> None:
    key = KEYS[SummaryClass.FACTION_RULES]
    check = ClassCheck(
        summary_class=SummaryClass.FACTION_RULES,
        keys=(key,),
        authored=(
            {}
            if review_state is None
            else {key: record(SummaryClass.FACTION_RULES, key, review_state=review_state)}  # type: ignore[dict-item]
        ),
        gate=Gate.ON,
    )

    findings = check_summary_gates([check])

    assert [f.finding_code for f in findings] == [f"FRL-{expected}"]
    assert findings[0].severity is Severity.BLOCKING
    assert findings[0].severity is CATALOGUE[f"FRL-{expected}"].severity


@pytest.mark.parametrize(
    "review_state", [None, ReviewState.DRAFT, ReviewState.IN_REVIEW, ReviewState.NEEDS_REREVIEW]
)
def test_the_off_state_collapses_every_reason_into_one_advisory(
    review_state: ReviewState | None,
) -> None:
    """Off, the distinction between the reasons is editorial rather than operational."""
    key = KEYS[SummaryClass.FACTION_RULES]
    check = ClassCheck(
        summary_class=SummaryClass.FACTION_RULES,
        keys=(key,),
        authored=(
            {}
            if review_state is None
            else {key: record(SummaryClass.FACTION_RULES, key, review_state=review_state)}  # type: ignore[dict-item]
        ),
        gate=Gate.OFF,
    )

    findings = check_summary_gates([check])

    assert [f.finding_code for f in findings] == ["FRL-OUTSTANDING"]
    assert findings[0].severity is Severity.ADVISORY
    assert findings[0].severity is CATALOGUE["FRL-OUTSTANDING"].severity


def test_the_gate_never_changes_a_codes_severity() -> None:
    """Every code either class of gate can emit carries its catalogued severity, always."""
    for gate in (Gate.OFF, Gate.ON):
        for summary_class in SummaryClass:
            findings = check_summary_gates(
                [_check(summary_class, review_state=ReviewState.DRAFT, gate=gate)]
            )
            for finding in findings:
                assert finding.severity is CATALOGUE[finding.finding_code].severity


# --- independence (FR-029, SC-013) --------------------------------------------------------------


def test_each_class_gate_is_evaluated_independently() -> None:
    """A complete class is never held back by an incomplete one."""
    findings = check_summary_gates(
        [
            _complete(SummaryClass.ABILITIES, gate=Gate.ON),
            _check(SummaryClass.FACTION_RULES, review_state=ReviewState.DRAFT, gate=Gate.ON),
            _complete(SummaryClass.DETACHMENT_RULES, gate=Gate.OFF),
            _check(SummaryClass.GLOSSARY, review_state=ReviewState.DRAFT, gate=Gate.OFF),
        ]
    )

    codes = sorted(f.finding_code for f in findings)
    assert codes == ["FRL-UNAPPROVED", "GLS-OUTSTANDING"]


def test_switching_one_gate_on_refuses_that_classs_gaps_only() -> None:
    incomplete = [
        _check(SummaryClass.FACTION_RULES, review_state=ReviewState.DRAFT, gate=Gate.ON),
        _check(SummaryClass.DETACHMENT_RULES, review_state=ReviewState.DRAFT, gate=Gate.OFF),
        _check(SummaryClass.GLOSSARY, review_state=ReviewState.DRAFT, gate=Gate.OFF),
    ]

    blocking = [
        f.finding_code for f in check_summary_gates(incomplete) if f.severity is Severity.BLOCKING
    ]

    assert blocking == ["FRL-UNAPPROVED"]


def test_the_abilities_class_has_no_switch_and_stays_on() -> None:
    """FR-001 forbids weakening a guarantee this feature inherits."""
    assert not SummaryClass.ABILITIES.has_gate_switch
    assert all(cls.has_gate_switch for cls in SummaryClass if cls is not SummaryClass.ABILITIES)


# --- the FR-021 denominator (contract §4.1) -----------------------------------------------------


def test_the_faction_rule_denominator_counts_present_and_uncurated_but_not_none() -> None:
    authored = load_authored(FIXTURE_CURATION)
    snap = snapshot(
        factions=[
            faction("f-glimmerfen-covenant"),
            faction("f-bracklight-host"),
            faction("f-sedgeward-conclave"),
            faction("f-mirefen-enclave"),
            faction("f-ashen-vigil"),
        ],
        faction_rules=authored.faction_rule_files,
        datasheets=[],
        detachments=[],
        enhancements=[],
    )

    keys = faction_rule_keys(snap)

    assert "faction:f-glimmerfen-covenant:tidewalk" in keys
    assert "faction:f-glimmerfen-covenant:fenlight-veil" in keys
    # `none` is a finished curation decision, and contributes nothing.
    assert not any(key.startswith("faction:f-mirefen-enclave") for key in keys)
    # An omitted file is unfinished work, and counts as outstanding.
    assert "faction:f-ashen-vigil" in keys


def test_the_fixture_set_reports_the_expected_coverage() -> None:
    authored = load_authored(FIXTURE_CURATION)
    snap = snapshot(
        factions=[
            faction("f-glimmerfen-covenant"),
            faction("f-bracklight-host"),
            faction("f-sedgeward-conclave"),
            faction("f-mirefen-enclave"),
            faction("f-ashen-vigil"),
        ],
        faction_rules=authored.faction_rule_files,
        datasheets=[],
        detachments=[],
        enhancements=[],
    )
    summaries = {
        rule.summary_key: rule
        for file in authored.faction_rule_files.values()
        for rule in file.rules
    }

    coverage = class_coverage(
        ClassCheck(
            summary_class=SummaryClass.FACTION_RULES,
            keys=faction_rule_keys(snap),
            authored=summaries,
            gate=Gate.OFF,
        )
    )

    # Five keys: two Glimmerfen rules, one Bracklight, one Sedgeward, one uncurated Ashen Vigil.
    # Exactly one of them — Glimmerfen's `tidewalk` — is approved.
    assert (coverage.approved, coverage.total) == (1, 5)
    assert coverage.ratio_percent == 20


# --- the ratchet (FR-030, contract §4) ----------------------------------------------------------


def _coverage(summary_class: SummaryClass, approved: int, total: int, *, gate: Gate):  # type: ignore[no-untyped-def]
    keys = tuple(f"{summary_class.value}:{index}" for index in range(total))
    authored = {key: record(summary_class, key) for key in keys[:approved]}
    return class_coverage(
        ClassCheck(
            summary_class=summary_class,
            keys=keys,
            authored=authored,  # type: ignore[arg-type]
            current_digests={key: "d" * 32 for key in keys},
            gate=gate,
        )
    )


@pytest.mark.parametrize("gate", [Gate.OFF, Gate.ON])
def test_a_regression_fires_regardless_of_gate_state(gate: Gate) -> None:
    coverage = _coverage(SummaryClass.FACTION_RULES, 3, 10, gate=gate)

    findings = check_summary_ratchet(
        [coverage],
        previous_percent={SummaryClass.FACTION_RULES: 40},
        tolerances={SummaryClass.FACTION_RULES: 0.0},
    )

    assert [f.finding_code for f in findings] == ["COV-SUMMARY-REGRESSION"]
    assert findings[0].severity is Severity.BLOCKING


def test_the_regression_detail_carries_integer_percents_and_the_class() -> None:
    """The canonical scalar set excludes floats so bundle and report bytes stay reproducible."""
    coverage = _coverage(SummaryClass.GLOSSARY, 3, 10, gate=Gate.OFF)

    finding = check_summary_ratchet(
        [coverage],
        previous_percent={SummaryClass.GLOSSARY: 40},
        tolerances={SummaryClass.GLOSSARY: 0.05},
    )[0]

    assert finding.detail == {
        "class": "glossary",
        "previous_ratio_percent": 40,
        "current_ratio_percent": 30,
        "tolerance_percent": 5,
    }
    assert all(isinstance(value, int) for value in finding.detail.values() if value != "glossary")


def test_advancing_coverage_is_never_a_regression() -> None:
    coverage = _coverage(SummaryClass.FACTION_RULES, 6, 10, gate=Gate.OFF)

    assert (
        check_summary_ratchet(
            [coverage],
            previous_percent={SummaryClass.FACTION_RULES: 40},
            tolerances={SummaryClass.FACTION_RULES: 0.0},
        )
        == []
    )


def test_a_drop_inside_the_configured_tolerance_is_not_a_regression() -> None:
    coverage = _coverage(SummaryClass.FACTION_RULES, 38, 100, gate=Gate.OFF)

    assert (
        check_summary_ratchet(
            [coverage],
            previous_percent={SummaryClass.FACTION_RULES: 40},
            tolerances={SummaryClass.FACTION_RULES: 0.02},
        )
        == []
    )


def test_a_class_with_no_previously_published_figure_cannot_regress() -> None:
    """A first release, or a class whose campaign has not started, has nothing to fall from."""
    coverage = _coverage(SummaryClass.DETACHMENT_RULES, 0, 10, gate=Gate.OFF)

    assert check_summary_ratchet([coverage], previous_percent={}, tolerances={}) == []


def test_the_ratchet_names_only_the_class_that_regressed() -> None:
    coverages = [
        _coverage(SummaryClass.ABILITIES, 10, 10, gate=Gate.ON),
        _coverage(SummaryClass.FACTION_RULES, 3, 10, gate=Gate.OFF),
    ]

    findings = check_summary_ratchet(
        coverages,
        previous_percent={SummaryClass.ABILITIES: 100, SummaryClass.FACTION_RULES: 40},
        tolerances={},
    )

    assert [f.entity_refs for f in findings] == [("coverage:summaries.faction_rules",)]


# --- the wiring, end to end ---------------------------------------------------------------------


def _minimal_build(tmp_path_factory, env: dict[str, str]):  # type: ignore[no-untyped-def]
    """A whole `build` over `fixtures/minimal`, with a throwaway first-release baseline.

    The throwaway `repository_root` matters for the same reason it does in
    `tests/contract/test_minimal_fixture_bundle.py`: without it the coverage baseline falls back
    to whatever `data/` the ambient checkout happens to carry, and a dozen fixture datasheets
    collapse against a real published tree for reasons that have nothing to do with gates.
    """
    minimal = Path(__file__).resolve().parents[2] / "fixtures" / "minimal"
    if not minimal.is_dir():
        pytest.skip("fixtures/minimal does not exist yet")
    repository_root = tmp_path_factory.mktemp("gates-repo")
    for relative in ("data/wh40k-11e/factions", "curation/abilities", "reports", "state", "work"):
        (repository_root / relative).mkdir(parents=True, exist_ok=True)
    return run_build(
        config=load_config(env=env),
        rules_version_id="gates-fixture",
        fixtures_dir=minimal,
        offline=True,
        output_root=tmp_path_factory.mktemp("gates-build"),
        repository_root=repository_root,
    )


def test_a_gates_off_build_reports_the_backlog_without_refusing_the_release(
    tmp_path_factory,  # type: ignore[no-untyped-def]
) -> None:
    """The whole point of shipping the machinery before the campaign (T050 is not a blocker)."""
    result = _minimal_build(tmp_path_factory, {})

    codes = {f.finding_code for f in result.findings}
    assert "FRL-OUTSTANDING" in codes
    assert not any(code.startswith(("FRL-MISSING", "FRL-UNAPPROVED")) for code in codes)
    assert not [
        f for f in result.findings if f.severity is Severity.BLOCKING and not f.is_suppressed
    ]


def test_switching_the_faction_rule_gate_on_refuses_the_same_build(
    tmp_path_factory,  # type: ignore[no-untyped-def]
) -> None:
    result = _minimal_build(tmp_path_factory, {"WGC_GATE_FACTION_RULES": "on"})

    blocking = {
        f.finding_code
        for f in result.findings
        if f.severity is Severity.BLOCKING and not f.is_suppressed
    }
    assert blocking == {"FRL-MISSING"}


def test_the_report_carries_one_coverage_row_per_wired_class(
    tmp_path_factory,  # type: ignore[no-untyped-def]
) -> None:
    result = _minimal_build(tmp_path_factory, {})

    assert "summaries.abilities" in result.report.coverage
    assert "summaries.faction_rules" in result.report.coverage
    assert result.report.coverage["summaries.abilities"].ratio == 1.0


# --- the second ratchet: resolved-option coverage (006 FR-022, research D4) ----------------------
#
# A SECOND, stricter test over the counts `pipeline/validate/coverage.py` already computes for its
# `wargear_options` collapse check. The two are not redundant and the difference is the whole
# point: the collapse check compares this version's COUNT with the previous version's count
# against a configured floor, and so tolerates a steady 10% decline indefinitely. This compares
# PERCENTS, against the previous PUBLISHED version, with a tolerance that defaults to nothing.
#
# Raising `WGC_COVERAGE_MIN_OPTION_RATIO` to 1.0 instead would not do: that ratio's denominator
# moves. A release in which the source adds 40 datasheets can raise the count while lowering the
# proportion, and SC-001 is about the proportion.


def _loadout(resolved: int, total: int, key: str = OPTIONS_RESOLVED_KEY) -> LoadoutCoverage:
    return LoadoutCoverage(key=key, resolved=resolved, total=total)


def _write_previous_report(
    root: Path, rules_version_id: str, figures: dict[str, tuple[int, int]]
) -> None:
    directory = root / "reports" / rules_version_id
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "report.json").write_text(
        json.dumps(
            {
                "coverage": {
                    name: {"current": current, "previous": 0, "ratio_percent": percent}
                    for name, (current, percent) in figures.items()
                }
            }
        ),
        encoding="utf-8",
    )


def test_a_first_release_has_nothing_to_fall_from() -> None:
    """No previous published version, no baseline, no block — the ratchet's introduction rule.

    This is what makes it safe to add mid-campaign rather than needing a seeded baseline, and it
    is the same rule `check_summary_ratchet` already lives by. The first extended release
    ESTABLISHES the baseline; the one after it is the first that can regress.
    """
    assert check_option_ratchet(_loadout(0, 100), previous_percent=None, tolerance=0.0) == []


def test_a_fall_below_the_previous_published_percent_blocks() -> None:
    coverage = _loadout(30, 100)

    findings = check_option_ratchet(coverage, previous_percent=40, tolerance=0.0)

    assert [f.finding_code for f in findings] == ["COV-OPTION-REGRESSION"]
    assert findings[0].severity is Severity.BLOCKING
    assert findings[0].entity_refs == ("coverage:loadout.options_resolved",)


def test_the_option_regression_detail_carries_integer_percents_only() -> None:
    """The canonical scalar set excludes floats so report bytes stay reproducible."""
    finding = check_option_ratchet(_loadout(30, 100), previous_percent=40, tolerance=0.05)[0]

    assert finding.detail == {
        "figure": "loadout.options_resolved",
        "previous_ratio_percent": 40,
        "current_ratio_percent": 30,
        "tolerance_percent": 5,
    }
    assert all(isinstance(v, int) for k, v in finding.detail.items() if k != "figure")


def test_an_improvement_is_never_an_option_regression() -> None:
    assert check_option_ratchet(_loadout(60, 100), previous_percent=40, tolerance=0.0) == []


def test_holding_the_previous_percent_exactly_is_never_a_regression() -> None:
    """The boundary, stated rather than left to a `<` versus `<=` reading of the source."""
    assert check_option_ratchet(_loadout(40, 100), previous_percent=40, tolerance=0.0) == []


def test_an_option_drop_inside_the_configured_tolerance_is_not_a_regression() -> None:
    assert check_option_ratchet(_loadout(38, 100), previous_percent=40, tolerance=0.02) == []


def test_the_edge_of_the_option_tolerance_is_inside_it() -> None:
    assert check_option_ratchet(_loadout(35, 100), previous_percent=40, tolerance=0.05) == []
    assert check_option_ratchet(_loadout(34, 100), previous_percent=40, tolerance=0.05) != []


def test_an_empty_option_denominator_is_complete_rather_than_zero() -> None:
    """A snapshot with no datasheets has no outstanding option work to have failed at."""
    assert _loadout(0, 0).ratio_percent == 100


def test_default_equipment_is_reported_and_never_ratcheted(tmp_path: Path) -> None:
    """Research D4: there is nothing yet to compare it against.

    Inventing a first-release threshold for it would be exactly the absolute ceiling the
    2026-08-09 clarification rules out — a figure that can wedge a release ahead of a parser fix.
    It gets a report row (T039) and no gate.
    """
    _write_previous_report(tmp_path, "prev", {"loadout.default_equipment": (900, 90)})

    assert previous_loadout_coverage(tmp_path, "prev") == {"default_equipment": (900, 90)}
    assert LOADOUT_RATCHETED_KEYS == (OPTIONS_RESOLVED_KEY,)


# --- the baseline: the previous PUBLISHED version, never the previous candidate ------------------


def test_the_baseline_is_read_from_the_published_versions_retained_report(tmp_path: Path) -> None:
    _write_previous_report(tmp_path, "v-published", {"loadout.options_resolved": (402, 19)})

    assert previous_loadout_coverage(tmp_path, "v-published") == {"options_resolved": (402, 19)}


def test_a_rejected_candidates_report_never_becomes_the_baseline(tmp_path: Path) -> None:
    """The rejected candidate's report is sitting right there, and is not consulted.

    `load_prior` resolves the version id from the channel MANIFEST, which only a publication
    writes. A candidate that was reviewed and turned down leaves a `reports/<id>/report.json`
    behind exactly like an approved one, and reading "the newest report" instead of "the report
    of the published version" would let a rejected candidate lower the bar for the next one.
    """
    _write_previous_report(tmp_path, "v-published", {"loadout.options_resolved": (402, 19)})
    _write_previous_report(tmp_path, "v-rejected", {"loadout.options_resolved": (10, 1)})

    assert previous_loadout_coverage(tmp_path, "v-published") == {"options_resolved": (402, 19)}


def test_no_previous_version_and_no_retained_report_both_yield_no_baseline(tmp_path: Path) -> None:
    assert previous_loadout_coverage(tmp_path, None) == {}
    assert previous_loadout_coverage(tmp_path, "never-published") == {}


def test_an_unreadable_baseline_removes_the_ratchet_rather_than_stopping_the_run(
    tmp_path: Path,
) -> None:
    """Acting on evidence is the ratchet's whole job; it cannot refuse for want of it."""
    directory = tmp_path / "reports" / "v-corrupt"
    directory.mkdir(parents=True)
    (directory / "report.json").write_text("{not json", encoding="utf-8")

    assert previous_loadout_coverage(tmp_path, "v-corrupt") == {}


def test_the_summary_and_loadout_baselines_do_not_read_each_others_rows(tmp_path: Path) -> None:
    """One generalised reader, two prefixes, and no leakage between them.

    Worth an assertion because the generalisation is exactly where a bug would put
    `summaries.abilities` into the option ratchet's baseline, where it would be a plausible
    number that means nothing.
    """
    directory = tmp_path / "reports" / "v-mixed"
    directory.mkdir(parents=True)
    (directory / "report.json").write_text(
        json.dumps(
            {
                "coverage": {
                    "summaries.abilities": {"current": 7, "ratio_percent": 70},
                    "loadout.options_resolved": {"current": 402, "ratio_percent": 19},
                    "datasheets": {"current": 1, "ratio_percent": 100},
                }
            }
        ),
        encoding="utf-8",
    )

    assert previous_loadout_coverage(tmp_path, "v-mixed") == {"options_resolved": (402, 19)}
    assert previous_summary_coverage(tmp_path, "v-mixed") == {"abilities": (7, 70)}


# --- and the same two figures, computed from a snapshot the pipeline actually builds ------------


def test_the_option_figure_counts_exactly_what_the_collapse_check_counts() -> None:
    """One count, two tests over it — not two counts that could drift apart (T038).

    `pipeline/validate/coverage.py` already had to decide what "resolved" means: `none` and
    `extracted` both count, because a datasheet the source describes no options for is FINISHED
    rather than outstanding. Counting it as a gap would make the figure fall every time a faction
    of characters shipped. The ratchet reuses that decision rather than restating it.
    """
    resolved = datasheet("ds-a").model_copy(
        update={"wargear_option_state": WargearOptionState.NONE}
    )
    extracted = datasheet("ds-b").model_copy(
        update={"wargear_option_state": WargearOptionState.EXTRACTED}
    )
    partial = datasheet("ds-c").model_copy(
        update={"wargear_option_state": WargearOptionState.PARTIAL}
    )
    unconsulted = datasheet("ds-d")

    figures = loadout_coverages(snapshot(datasheets=[resolved, extracted, partial, unconsulted]))

    assert figures[OPTIONS_RESOLVED_KEY].resolved == 2
    assert figures[OPTIONS_RESOLVED_KEY].total == 4
    assert figures[OPTIONS_RESOLVED_KEY].ratio_percent == 50


def test_the_default_equipment_figure_reads_its_own_state_and_not_the_option_one() -> None:
    """The two states routinely disagree on one card, which is why they are separate enums."""
    both = datasheet("ds-a").model_copy(
        update={
            "wargear_option_state": WargearOptionState.PARTIAL,
            "default_equipment_state": DefaultEquipmentState.EXTRACTED,
        }
    )
    neither = datasheet("ds-b").model_copy(
        update={"wargear_option_state": WargearOptionState.EXTRACTED}
    )

    figures = loadout_coverages(snapshot(datasheets=[both, neither]))

    assert figures[OPTIONS_RESOLVED_KEY].resolved == 1
    assert figures[DEFAULT_EQUIPMENT_KEY].resolved == 1
    assert figures[DEFAULT_EQUIPMENT_KEY].total == 2


# --- 007 T054: the two new loadout figures -------------------------------------------------


def test_item_constraints_figure_counts_datasheets_whose_restrictions_all_linked() -> None:
    """Of the datasheets stating a restriction, the proportion whose restrictions ALL resolved
    (quickstart §4) — one unlinked row is enough to keep the whole datasheet out of the
    numerator."""
    all_linked = datasheet("ds-a").model_copy(
        update={
            "item_constraints": [
                CuratedItemConstraint(
                    constraint_index=1,
                    constraint_type=ItemConstraintType.NOT_REPLACEABLE,
                    item_name="Storm maul",
                    weapon_line=1,
                )
            ]
        }
    )
    one_unlinked = datasheet("ds-b").model_copy(
        update={
            "item_constraints": [
                CuratedItemConstraint(
                    constraint_index=1,
                    constraint_type=ItemConstraintType.NOT_REPLACEABLE,
                    item_name="Storm maul",
                    weapon_line=1,
                ),
                CuratedItemConstraint(
                    constraint_index=2,
                    constraint_type=ItemConstraintType.ONE_PER_UNIT,
                    item_name="Nowhere weapon",
                ),
            ]
        }
    )
    no_restriction = datasheet("ds-c")

    figures = loadout_coverages(snapshot(datasheets=[all_linked, one_unlinked, no_restriction]))

    assert figures[ITEM_CONSTRAINTS_KEY].resolved == 1
    assert figures[ITEM_CONSTRAINTS_KEY].total == 2  # no_restriction is outside the question
    assert ITEM_CONSTRAINTS_KEY not in LOADOUT_RATCHETED_KEYS


def test_rendering_equivalence_is_absent_when_no_equivalence_summary_is_given() -> None:
    """`equivalence=None` — the `run_validate` / check-disabled case (007 T001, T053) — omits the
    figure rather than reporting a false 100%: nothing was measured this run."""
    figures = loadout_coverages(snapshot(datasheets=[datasheet("ds-a")]))

    assert RENDERING_EQUIVALENCE_KEY not in figures
    assert RENDERING_EQUIVALENCE_NOT_COMPARED_KEY not in figures


def test_rendering_equivalence_excludes_not_compared_from_numerator_and_denominator() -> None:
    """Research D7 / data-model.md §5: `not_compared` moves neither side of the ratio and is
    reported as its own count instead."""
    equivalence = EquivalenceSummary(matched=3, mismatched=1, not_compared=5)

    figures = loadout_coverages(snapshot(datasheets=[datasheet("ds-a")]), equivalence=equivalence)

    assert figures[RENDERING_EQUIVALENCE_KEY].resolved == 3
    assert figures[RENDERING_EQUIVALENCE_KEY].total == 4  # matched + mismatched, not + 5
    assert figures[RENDERING_EQUIVALENCE_KEY].ratio_percent == 75
    assert figures[RENDERING_EQUIVALENCE_NOT_COMPARED_KEY].resolved == 5
    assert RENDERING_EQUIVALENCE_KEY not in LOADOUT_RATCHETED_KEYS
    assert RENDERING_EQUIVALENCE_NOT_COMPARED_KEY not in LOADOUT_RATCHETED_KEYS


def test_a_build_reports_the_two_007_loadout_rows_beside_the_006_ones(
    tmp_path_factory,  # type: ignore[no-untyped-def]
) -> None:
    """T056: confirm the US5 independent test's report-shape half — a fixture run's `report.json`
    carries `loadout.rendering_equivalence` beside its `loadout.rendering_equivalence_not_
    compared` count, and `loadout.item_constraints`, on the same first-release report-only terms
    as `006`'s two rows (FR-019..FR-022, SC-006)."""
    result = _minimal_build(tmp_path_factory, {})

    assert f"loadout.{RENDERING_EQUIVALENCE_KEY}" in result.report.coverage
    assert f"loadout.{RENDERING_EQUIVALENCE_NOT_COMPARED_KEY}" in result.report.coverage
    assert f"loadout.{ITEM_CONSTRAINTS_KEY}" in result.report.coverage
    for key in (RENDERING_EQUIVALENCE_KEY, RENDERING_EQUIVALENCE_NOT_COMPARED_KEY):
        assert result.report.coverage[f"loadout.{key}"].threshold == 0.0
    assert not [f for f in result.findings if f.finding_code == "COV-OPTION-REGRESSION"]


def test_the_equivalence_check_can_be_disabled(
    tmp_path_factory,  # type: ignore[no-untyped-def]
) -> None:
    """`WGC_EQUIVALENCE_CHECK_ENABLED=false` (007 T014, T053): the two new figures are simply
    absent from the report, and no `RND-EQV-*` finding is raised — the switch controls whether
    the check runs at all, never what happens when it finds a mismatch."""
    result = _minimal_build(tmp_path_factory, {"WGC_EQUIVALENCE_CHECK_ENABLED": "false"})

    assert f"loadout.{RENDERING_EQUIVALENCE_KEY}" not in result.report.coverage
    assert f"loadout.{RENDERING_EQUIVALENCE_NOT_COMPARED_KEY}" not in result.report.coverage
    assert not [f for f in result.findings if f.finding_code.startswith("RND-EQV-")]


# --- the loadout ratchet, wired end to end (006 T038, T039) -------------------------------------


def test_a_build_reports_both_loadout_rows(tmp_path_factory) -> None:  # type: ignore[no-untyped-def]
    """The rows exist on a first release, where the ratchet has nothing to compare against.

    Reporting a figure and guarding it are separate acts, and this is the release that proves it:
    the throwaway repository root gives the build no previous published version at all, so both
    rows are stated and neither can block. The figure has to be *published* in this release for
    the next one to have a baseline — which is what makes a ratchet introduced mid-campaign work
    without a seeded number nobody measured.
    """
    result = _minimal_build(tmp_path_factory, {})

    assert "loadout.options_resolved" in result.report.coverage
    assert "loadout.default_equipment" in result.report.coverage
    assert not [f for f in result.findings if f.finding_code == "COV-OPTION-REGRESSION"]


def test_the_reported_row_agrees_with_the_collapse_checks_own_count() -> None:
    """Two figures over one count, and this is the assertion that keeps it one count.

    `wargear_options` (the collapse check) and `loadout.options_resolved` (the ratchet) state the
    same numerator by construction — they call the same function. If that ever stops being true,
    the report and the gate can disagree about whether a release regressed, and the report is
    what an approver reads.

    Note which of the two needs a baseline and which does not. The collapse row is a comparison
    and simply does not exist on a first release; the loadout row is a proportion of *this*
    snapshot and is stated always — which is what lets the first extended release publish the
    figure the next one will be measured against.
    """
    current = snapshot(
        datasheets=[
            datasheet("ds-a").model_copy(
                update={"wargear_option_state": WargearOptionState.EXTRACTED}
            ),
            datasheet("ds-b").model_copy(
                update={"wargear_option_state": WargearOptionState.PARTIAL}
            ),
        ]
    )
    figures = check_coverage(
        current, prior_from_snapshot(current, rules_version_id="v-prev"), load_config(env={})
    ).figures

    assert (
        figures["wargear_options"].current
        == loadout_coverages(current)[OPTIONS_RESOLVED_KEY].resolved
        == 1
    )


def test_the_ratchet_refuses_a_candidate_that_fell_since_the_published_release() -> None:
    """The end-to-end shape, assembled from the parts a real run assembles it from.

    Not a whole build: a build cannot regress against a baseline no fixture has published, and
    manufacturing one would mean writing a `report.json` and a manifest that say a release
    happened. What matters is that the prior's percent, the config's tolerance and the snapshot's
    own count meet in one comparison, which is exactly what this asserts.
    """
    partial = datasheet("ds-a").model_copy(
        update={"wargear_option_state": WargearOptionState.PARTIAL}
    )
    resolved = datasheet("ds-b").model_copy(
        update={"wargear_option_state": WargearOptionState.EXTRACTED}
    )
    coverages = loadout_coverages(snapshot(datasheets=[partial, resolved]))

    findings = check_option_ratchet(
        coverages[OPTIONS_RESOLVED_KEY],
        previous_percent=90,
        tolerance=load_config(env={}).ratchet_tolerance_options,
    )

    assert [f.finding_code for f in findings] == ["COV-OPTION-REGRESSION"]
    assert CATALOGUE["COV-OPTION-REGRESSION"].severity is Severity.BLOCKING


def test_the_default_tolerance_permits_nothing(tmp_path_factory) -> None:  # type: ignore[no-untyped-def]
    """`WGC_RATCHET_TOLERANCE_OPTIONS` defaults to 0.00, like the four before it."""
    assert load_config(env={}).ratchet_tolerance_options == 0.0
    assert load_config(env={"WGC_RATCHET_TOLERANCE_OPTIONS": "0.05"}).ratchet_tolerance_options == (
        0.05
    )


# --- 008 T022 (FR-019): the two resolved-datasheet definitions do not drift ---------------------
#
# `loadout.options_resolved` and `loadout.default_equipment` are ESTABLISHED figures now (both
# published across two versions before this feature). Clarifications 2026-08-15's whole premise —
# that this release's high is a meaningful floor for the next one — depends on the two counts
# meaning exactly what they meant when `006` shipped them. A refactor that quietly narrowed the
# counted-state set, widened it to a hypothetical fourth state, or filtered the denominator would
# move both coverage figures without a single line of `008` grammar changing, and nothing else in
# this suite would catch it: every ratchet test above assumes the count it is handed already means
# what it says.


def test_both_loadout_figures_count_exactly_none_and_extracted() -> None:
    """FR-019: same numerator rule `006` shipped (`NONE`/`EXTRACTED` count, `PARTIAL` does not),
    same denominator (every published datasheet, unconditionally) -- for both loadout figures."""
    rows = [
        datasheet("ds-none").model_copy(
            update={
                "wargear_option_state": WargearOptionState.NONE,
                "default_equipment_state": DefaultEquipmentState.NONE,
            }
        ),
        datasheet("ds-extracted").model_copy(
            update={
                "wargear_option_state": WargearOptionState.EXTRACTED,
                "default_equipment_state": DefaultEquipmentState.EXTRACTED,
            }
        ),
        datasheet("ds-partial").model_copy(
            update={
                "wargear_option_state": WargearOptionState.PARTIAL,
                "default_equipment_state": DefaultEquipmentState.PARTIAL,
            }
        ),
    ]
    snap = snapshot(datasheets=rows)

    # The numerator: NONE and EXTRACTED both count, PARTIAL does not -- 2 of 3, for both figures.
    assert options_resolved_datasheets(snap) == 2
    assert default_equipment_resolved_datasheets(snap) == 2

    # The denominator: every published datasheet, unconditionally. Neither function filters its
    # input, so the count above is always compared against the full `len(snap.datasheets)` in
    # `loadout_coverages`, never a subset of it.
    assert loadout_coverages(snap)[OPTIONS_RESOLVED_KEY].total == len(rows) == 3
    assert loadout_coverages(snap)[DEFAULT_EQUIPMENT_KEY].total == len(rows) == 3

    # The counted-state set is exactly {NONE, EXTRACTED} for each enum, never PARTIAL and never a
    # hypothetical fourth member -- both enums are closed at three (research D1e's "the fourth
    # fact is the value's absence", carried into `008` unchanged). Neither numerator nor
    # denominator has therefore gained a condition since `006`.
    assert set(WargearOptionState) == {
        WargearOptionState.NONE,
        WargearOptionState.EXTRACTED,
        WargearOptionState.PARTIAL,
    }
    assert set(DefaultEquipmentState) == {
        DefaultEquipmentState.NONE,
        DefaultEquipmentState.EXTRACTED,
        DefaultEquipmentState.PARTIAL,
    }
