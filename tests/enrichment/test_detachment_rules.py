# AI-Assisted: Claude Code (model: claude-opus-5) - Wrote the detachment-rule suite (004 task
# T052), confirmed failing before CuratedDetachmentRule and detachment_rule_key existed: the
# three keying edge cases of 004 data-model.md §2.2, and the FR-022 guarantee that a rule with no
# approved summary still ships with its name while its gate is off (004 FR-022, US4 scenario 2).
"""The key is the design, and it is the whole design.

Three edge cases decide whether the detachment-rule class works, and a name-based key gets every
one of them wrong:

* two detachments in **different factions** sharing a rule name must be **distinct** entries, or
  approving one silently approves the other's;
* a detachment **renamed upstream** while its rule is unchanged must keep its key *and* its
  digest, or a cosmetic rename re-reviews a campaign; and
* a **rule** changed while its name is unchanged must move its digest and re-review, which is the
  entire reason the digest is taken over the mechanic rather than over the name.

The fourth property here is the one that lets the ~336-record campaign start at all: a rule with
no approved summary **still ships, named**, and publication is not refused while the gate is off
(FR-022). The name comes from the source; only the explanation is authored.
"""

from __future__ import annotations

from pathlib import Path

from pipeline.build.bundle_emit import emit_bundle
from pipeline.config import Gate
from pipeline.curate.authored import load_authored
from pipeline.curate.summaries import SummaryStatus, detachment_rule_key, effective_status
from pipeline.models.authored import ReviewState, SummaryClass
from pipeline.models.curated import CuratedDetachmentRule
from pipeline.models.findings import Severity
from pipeline.schema_validation import validate_bundle
from pipeline.validate.gates import (
    ClassCheck,
    check_summary_gates,
    class_coverage,
    detachment_rule_keys,
    detachment_rule_summaries,
)
from tests import factories

FIXTURE_CURATION = Path(__file__).resolve().parents[2] / "fixtures" / "enrichment" / "curation"


def _authored():  # type: ignore[no-untyped-def]
    return load_authored(FIXTURE_CURATION)


def _detachment(detachment_id: str, *, faction_id: str, rule_names: tuple[str, ...]):  # type: ignore[no-untyped-def]
    """A detachment carrying the rule identities the source publishes for it."""
    return factories.detachment(detachment_id, faction_id=faction_id).model_copy(
        update={
            "rules": [
                CuratedDetachmentRule(
                    summary_key=detachment_rule_key(detachment_id, name), name=name
                )
                for name in rule_names
            ]
        }
    )


# --- the three keying edge cases (data-model.md §2.2) --------------------------------------------


def test_two_factions_sharing_a_rule_name_are_distinct_keys() -> None:
    glimmerfen = detachment_rule_key("d-fenlight-vigil", "Veiled Advance")
    bracklight = detachment_rule_key("d-bracklight-charge", "Veiled Advance")

    assert glimmerfen != bracklight
    # And the fixture set really carries both, in two different faction files.
    records = _authored().detachment_rule_summaries
    assert {glimmerfen, bracklight} <= set(records)
    assert records[glimmerfen].name == records[bracklight].name == "Veiled Advance"
    assert records[glimmerfen].summary != records[bracklight].summary


def test_a_detachment_renamed_upstream_keeps_its_rules_keys_and_digests() -> None:
    """The key embeds the detachment's **id**, which a display-name change never moves."""
    before = _detachment(
        "d-fenlight-vigil", faction_id="f-glimmerfen-covenant", rule_names=("Veiled Advance",)
    )
    after = before.model_copy(update={"name": "Fenlight Vigil Host"})

    assert detachment_rule_keys(factories.snapshot(detachments=[before])) == detachment_rule_keys(
        factories.snapshot(detachments=[after])
    )

    key = detachment_rule_key("d-fenlight-vigil", "Veiled Advance")
    records = _authored().detachment_rule_summaries
    stored = records[key].mechanic_digest
    assert effective_status(key, authored=records, current_digest=stored) is SummaryStatus.APPROVED


def test_a_rule_changed_under_an_unchanged_name_moves_its_digest_and_re_reviews() -> None:
    """The point of digesting the mechanic rather than the name."""
    key = detachment_rule_key("d-fenlight-vigil", "Veiled Advance")
    records = _authored().detachment_rule_summaries

    assert records[key].review_state is ReviewState.APPROVED
    assert effective_status(key, authored=records, current_digest="9" * 32) is (
        SummaryStatus.NEEDS_REREVIEW
    )
    # And no other key is touched by it.
    other = detachment_rule_key("d-tidewalk-column", "Veiled Advance")
    assert (
        effective_status(other, authored=records, current_digest=records[other].mechanic_digest)
        is SummaryStatus.APPROVED
    )


# --- the denominator comes from the source, not from the curator's own file ----------------------


def test_the_denominator_is_every_published_rule_not_every_authored_one() -> None:
    """A campaign nobody has started must not report 100% coverage of itself."""
    snapshot = factories.snapshot(
        detachments=[
            _detachment(
                "d-fenlight-vigil",
                faction_id="f-glimmerfen-covenant",
                rule_names=("Veiled Advance", "Massed Fire", "Fenlight Muster"),
            )
        ]
    )

    keys = detachment_rule_keys(snapshot)

    assert len(keys) == 3
    # `Fenlight Muster` has no authored record at all, and is outstanding rather than absent.
    assert detachment_rule_key("d-fenlight-vigil", "Fenlight Muster") in keys

    coverage = class_coverage(
        ClassCheck(
            summary_class=SummaryClass.DETACHMENT_RULES,
            keys=keys,
            authored=detachment_rule_summaries(snapshot, _authored().detachment_rule_summaries),
            gate=Gate.OFF,
        )
    )
    assert (coverage.approved, coverage.total) == (1, 3)


# --- FR-022: the name always ships, the summary only once approved ------------------------------


def _bundle_rows():  # type: ignore[no-untyped-def]
    snapshot = factories.snapshot(
        detachments=[
            _detachment(
                "d-fenlight-vigil",
                faction_id="f-glimmerfen-covenant",
                rule_names=("Veiled Advance", "Massed Fire", "Fenlight Muster"),
            )
        ],
        detachment_rules=_authored().detachment_rule_summaries,
    )
    bundle = emit_bundle(snapshot, factories.meta())
    validate_bundle(bundle)
    return {row["id"]: row for row in bundle["detachmentRules"]}


def test_every_published_rule_carries_its_name_whatever_its_review_state() -> None:
    rows = _bundle_rows()

    assert sorted(row["name"] for row in rows.values()) == [
        "Fenlight Muster",
        "Massed Fire",
        "Veiled Advance",
    ]
    assert all(row["detachmentId"] == "d-fenlight-vigil" for row in rows.values())


def test_only_an_approved_summary_reaches_the_bundle() -> None:
    """A draft or an absent record ships the name alone — never wording nobody signed off."""
    rows = _bundle_rows()

    approved = rows[detachment_rule_key("d-fenlight-vigil", "Veiled Advance")]
    draft = rows[detachment_rule_key("d-fenlight-vigil", "Massed Fire")]
    unwritten = rows[detachment_rule_key("d-fenlight-vigil", "Fenlight Muster")]

    assert approved["summary"].startswith("Units from this detachment may make a Normal move")
    # Omitted, never `null` and never an empty string (contract §2).
    assert "summary" not in draft
    assert "summary" not in unwritten


def test_publication_is_not_refused_while_the_gate_is_off() -> None:
    snapshot = factories.snapshot(
        detachments=[
            _detachment(
                "d-fenlight-vigil",
                faction_id="f-glimmerfen-covenant",
                rule_names=("Veiled Advance", "Massed Fire", "Fenlight Muster"),
            )
        ]
    )
    check = ClassCheck(
        summary_class=SummaryClass.DETACHMENT_RULES,
        keys=detachment_rule_keys(snapshot),
        authored=detachment_rule_summaries(snapshot, _authored().detachment_rule_summaries),
        gate=Gate.OFF,
    )

    findings = check_summary_gates([check])

    assert {f.finding_code for f in findings} == {"DRL-OUTSTANDING"}
    assert all(f.severity is Severity.ADVISORY for f in findings)


def test_switching_the_gate_on_names_the_reason_for_each_outstanding_rule() -> None:
    snapshot = factories.snapshot(
        detachments=[
            _detachment(
                "d-fenlight-vigil",
                faction_id="f-glimmerfen-covenant",
                rule_names=("Veiled Advance", "Massed Fire", "Fenlight Muster"),
            )
        ]
    )
    check = ClassCheck(
        summary_class=SummaryClass.DETACHMENT_RULES,
        keys=detachment_rule_keys(snapshot),
        authored=detachment_rule_summaries(snapshot, _authored().detachment_rule_summaries),
        gate=Gate.ON,
    )

    findings = check_summary_gates([check])

    assert {f.finding_code for f in findings} == {"DRL-UNAPPROVED", "DRL-MISSING"}
    assert all(f.severity is Severity.BLOCKING for f in findings)
