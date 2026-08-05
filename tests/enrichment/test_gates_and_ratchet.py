# AI-Assisted: Claude Code (model: claude-opus-5) - Wrote the gate and ratchet suite (004 task
# T044), confirmed failing before pipeline/validate/gates.py existed: gate independence, the
# gate-selects-a-code rule of contracts/authored-summary-gates.md §3, and the coverage ratchet
# that applies whether or not a class's gate is on (004 FR-029, FR-030, SC-011, SC-013).
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

from pathlib import Path

import pytest

from pipeline.cli import run_build
from pipeline.config import Gate, load_config
from pipeline.curate.authored import load_authored
from pipeline.models.authored import ReviewState, SummaryClass
from pipeline.models.findings import Severity
from pipeline.report.catalogue import CATALOGUE
from pipeline.validate.gates import (
    ClassCheck,
    check_summary_gates,
    check_summary_ratchet,
    class_coverage,
    faction_rule_keys,
)
from tests.enrichment.test_class_state_machine import KEYS, record
from tests.factories import faction, snapshot

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
