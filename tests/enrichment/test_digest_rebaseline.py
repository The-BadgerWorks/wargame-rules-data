# AI-Assisted: Claude Code (model: claude-opus-5) - The five digest re-baseline guards (009
# tasks T074-T078, FR-025 to FR-029, SC-007), written BEFORE the classification pass (T080) they
# exist to constrain, so that pass is bounded by them rather than trusted to respect them. Each
# guard was demonstrated red against the violation it exists to prevent and green after
# restoring; the per-guard red output is recorded in this rung's report.
"""Feature 009 re-baselines every approved summary digest once. These five rules bound it.

A bulk digest refresh is mechanically indistinguishable from **laundering an approval** —
quietly re-stamping as "reviewed" a summary whose underlying mechanic actually moved. The
repository has two precedents that drew the line in opposite directions, and every rule below is
read off the difference between them:

* ``3b4766a9`` refreshed 39 digests as bookkeeping. It was permissible **because none of the 39
  records had ever been approved** — its own commit message says so in as many words: "no
  approval is being carried over a text change".
* ``59f2986b`` refreshed 23 digests on records that **were** approved. It was permissible only
  because a named human confirmed, on a named date, that those mechanics were unchanged.

So the discriminator is not "did the digest move" — it is **"is an approval being carried across
the move"**, and that question is answered by the review state at *both* ends of the diff.

============================================================  =====================
Guard                                                          Enforced by
============================================================  =====================
T074 a never-approved record refreshes freely                  the tool's classifier
T075 an approved record may not, and no code path may do it    the tool + two structural refusals
T076 a changed mechanic still blocks, at the unchanged 100     the summary gate itself
T077 every refresh names its version and its authorization     the tool's attribution pair
T078 the re-baseline is an event, not a setting                config + a source scan
============================================================  =====================

Every record below is synthetic: invented keys, invented names, invented placeholder prose.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from pipeline import cli
from pipeline.config import CONFIG_VARS, PipelineConfig, load_config
from pipeline.curate.authored import AuthoredWriteAttempt, assert_not_authored
from pipeline.curate.summaries import SummaryStatus, effective_status
from pipeline.models.authored import AbilitySummary, ReviewState, SummaryClass
from pipeline.models.findings import Severity
from pipeline.validate.gates import ClassCheck, check_class, class_coverage, gate_for

REPO_ROOT = Path(__file__).resolve().parents[2]

# `tools/` is not an installed package, so the module is loaded from its file path — the same
# convention `tests/summaries/test_self_approval_refused.py` and
# `tests/unit/test_check_change_classes.py` already use.
_MODULE_PATH = REPO_ROOT / "tools" / "check_summary_approvals.py"
_spec = importlib.util.spec_from_file_location("check_summary_approvals", _MODULE_PATH)
assert _spec is not None and _spec.loader is not None
check_summary_approvals = importlib.util.module_from_spec(_spec)
sys.modules["check_summary_approvals"] = check_summary_approvals
_spec.loader.exec_module(check_summary_approvals)

digest_refreshes = check_summary_approvals.digest_refreshes
unattributed_refreshes = check_summary_approvals.unattributed_refreshes
REBASELINE_VERSION_FIELD = check_summary_approvals.REBASELINE_VERSION_FIELD
REBASELINE_AUTHORIZATION_FIELD = check_summary_approvals.REBASELINE_AUTHORIZATION_FIELD

KEY = "core:invented-guard-mechanic"
OTHER_KEY = "faction:invented-guard-order"
SUMMARY = "Invented mechanics-only placeholder authored for this guard suite."
OLD_DIGEST = "a" * 32
NEW_DIGEST = "b" * 32

#: A synthetic stand-in for the named, dated artefact FR-029 requires. Not a real authorization
#: and not a real version — this suite authors no data and cites no live record.
VERSION = "invented-edition-0000-00"
AUTHORIZATION = "invented-authorization-record-0000-00-00"


def _record(
    key: str = KEY,
    *,
    review_state: str,
    mechanic_digest: str = OLD_DIGEST,
    version: str | None = None,
    authorization: str | None = None,
) -> dict[str, object]:
    """One synthetic curation record, in the on-disk shape the tool reads from a diff."""
    record: dict[str, object] = {
        "ability_key": key,
        "name": key.split(":")[-1].replace("-", " ").title(),
        "summary": SUMMARY,
        "review_state": review_state,
        "mechanic_digest": mechanic_digest,
        "reviewed_by": "invented-curator",
        "reviewed_at": "2026-01-01T00:00:00Z",
    }
    if version is not None:
        record[REBASELINE_VERSION_FIELD] = version
    if authorization is not None:
        record[REBASELINE_AUTHORIZATION_FIELD] = authorization
    return record


def _summary(
    *,
    review_state: ReviewState,
    mechanic_digest: str = OLD_DIGEST,
    version: str | None = None,
    authorization: str | None = None,
) -> AbilitySummary:
    """The same record as a validated model, for the gate-side guards."""
    return AbilitySummary(
        ability_key=KEY,
        name="Invented Guard Mechanic",
        summary=SUMMARY,
        review_state=review_state,
        mechanic_digest=mechanic_digest,
        digest_refreshed_at_version=version,
        digest_refreshed_under_authorization=authorization,
    )


# ---------------------------------------------------------------------------------------
# T074 / FR-026 — a record that was never approved refreshes freely, as bookkeeping.
# ---------------------------------------------------------------------------------------


@pytest.mark.parametrize("state", ["draft", "in_review", "needs_rereview"])
def test_a_never_approved_record_may_have_its_digest_refreshed(state: str) -> None:
    """Precedent ``3b4766a9``: no approval is being carried, so nothing is being laundered."""
    base = [_record(review_state=state, mechanic_digest=OLD_DIGEST)]
    head = [_record(review_state=state, mechanic_digest=NEW_DIGEST)]

    refreshes = digest_refreshes(base, head)

    assert [refresh.key for refresh in refreshes] == [KEY]
    assert refreshes[0].carries_approval is False
    assert refreshes[0].is_permitted is True
    assert unattributed_refreshes(refreshes) == []


def test_a_bookkeeping_refresh_needs_no_version_or_authorization() -> None:
    """The attribution pair is the price of carrying an approval, not of touching a digest."""
    base = [_record(review_state="in_review", mechanic_digest=OLD_DIGEST)]
    head = [_record(review_state="in_review", mechanic_digest=NEW_DIGEST)]

    assert unattributed_refreshes(digest_refreshes(base, head)) == []


def test_a_bookkeeping_refresh_does_not_change_what_the_record_blocks_on() -> None:
    """The refresh is invisible to the gate: an unapproved record still blocks, as before.

    This is what makes ``3b4766a9``'s class of change safe — refreshing the digest of a record
    nobody has approved cannot buy publication, because the state, not the digest, is what
    refuses.
    """
    before = _summary(review_state=ReviewState.IN_REVIEW, mechanic_digest=OLD_DIGEST)
    after = _summary(review_state=ReviewState.IN_REVIEW, mechanic_digest=NEW_DIGEST)

    assert (
        effective_status(KEY, authored={KEY: before}, current_digest=NEW_DIGEST)
        is SummaryStatus.IN_REVIEW
    )
    assert (
        effective_status(KEY, authored={KEY: after}, current_digest=NEW_DIGEST)
        is SummaryStatus.IN_REVIEW
    )


def test_a_record_becoming_approved_in_the_same_change_is_not_a_re_baseline() -> None:
    """First-time authoring against a moved digest is a NEW approval, not a carried one.

    It is governed by the self-approval check (:func:`newly_approved`) and by review, and
    demanding a re-baseline authorization for it too would refuse ordinary curation.
    """
    base = [_record(review_state="in_review", mechanic_digest=OLD_DIGEST)]
    head = [_record(review_state="approved", mechanic_digest=NEW_DIGEST)]

    refreshes = digest_refreshes(base, head)

    assert refreshes[0].carries_approval is False
    assert unattributed_refreshes(refreshes) == []


# ---------------------------------------------------------------------------------------
# T075 / FR-026, FR-027 — an approved record may not, and no code path may do it.
# ---------------------------------------------------------------------------------------


def test_an_approved_record_refreshed_without_a_recorded_decision_is_refused() -> None:
    """Precedent ``59f2986b``, and the single most important assertion in this file.

    An approved record whose digest moves is carrying that approval across a change in what the
    digest describes. Silently, that is a laundered approval.
    """
    base = [_record(review_state="approved", mechanic_digest=OLD_DIGEST)]
    head = [_record(review_state="approved", mechanic_digest=NEW_DIGEST)]

    refreshes = digest_refreshes(base, head)

    assert refreshes[0].carries_approval is True
    assert refreshes[0].is_permitted is False
    assert [refresh.key for refresh in unattributed_refreshes(refreshes)] == [KEY]


def test_an_approved_record_refreshed_with_a_recorded_decision_is_allowed() -> None:
    """The true positive still fires and the false positive is gone — both directions."""
    base = [_record(review_state="approved", mechanic_digest=OLD_DIGEST)]
    head = [
        _record(
            review_state="approved",
            mechanic_digest=NEW_DIGEST,
            version=VERSION,
            authorization=AUTHORIZATION,
        )
    ]

    refreshes = digest_refreshes(base, head)

    assert refreshes[0].carries_approval is True
    assert unattributed_refreshes(refreshes) == []


def test_only_the_unattributed_approved_refresh_among_several_is_refused() -> None:
    base = [
        _record(KEY, review_state="approved", mechanic_digest=OLD_DIGEST),
        _record(OTHER_KEY, review_state="approved", mechanic_digest=OLD_DIGEST),
    ]
    head = [
        _record(KEY, review_state="approved", mechanic_digest=NEW_DIGEST),
        _record(
            OTHER_KEY,
            review_state="approved",
            mechanic_digest=NEW_DIGEST,
            version=VERSION,
            authorization=AUTHORIZATION,
        ),
    ]

    assert [r.key for r in unattributed_refreshes(digest_refreshes(base, head))] == [KEY]


def test_an_untouched_approved_record_is_not_a_refresh_at_all() -> None:
    """FR-024's carry-forward: an unchanged digest is not a re-baseline and raises nothing."""
    base = [_record(review_state="approved", mechanic_digest=OLD_DIGEST)]
    head = [_record(review_state="approved", mechanic_digest=OLD_DIGEST)]

    assert digest_refreshes(base, head) == []


def test_the_guard_reads_the_three_other_summary_classes_by_their_own_key_field() -> None:
    """One code path, four classes — the rule is not abilities-only.

    ``contracts/authored-summary-gates.md`` §1 says the four classes share the review state, the
    record shape and the carry-forward rule without variation, so a re-baseline rule that held
    only for ``ability_key`` would leave three doors open.
    """
    base = [{"summary_key": KEY, "review_state": "approved", "mechanic_digest": OLD_DIGEST}]
    head = [{"summary_key": KEY, "review_state": "approved", "mechanic_digest": NEW_DIGEST}]

    refreshes = digest_refreshes(base, head, key_field="summary_key")

    assert [r.key for r in unattributed_refreshes(refreshes)] == [KEY]


def test_no_code_path_can_mutate_a_stored_digest_in_memory() -> None:
    """Half one of "no code path may do it": the authored records are frozen.

    A re-baseline cannot be smuggled in as an in-memory edit during a run, because there is no
    assignment that would survive it.
    """
    summary = _summary(review_state=ReviewState.APPROVED)

    with pytest.raises(ValidationError):
        summary.mechanic_digest = NEW_DIGEST  # type: ignore[misc]


def test_no_code_path_can_write_a_refreshed_record_back_to_curation(tmp_path: Path) -> None:
    """Half two: the pipeline physically cannot write under ``curation/``.

    ``pipeline/curate/authored.py`` states the invariant as "the pipeline *cannot*", and every
    pipeline write that takes a caller-supplied path goes through this refusal — but nothing
    asserted that it fires until this guard. Without it, "no code path may refresh an approved
    digest" rested on a docstring.
    """
    curation_dir = tmp_path / "curation"
    (curation_dir / "abilities").mkdir(parents=True)
    target = curation_dir / "abilities" / "f-invented.json"

    with pytest.raises(AuthoredWriteAttempt):
        assert_not_authored(target, curation_dir)

    # And the direction that must NOT fire: the curated tree the pipeline does own.
    data_dir = tmp_path / "data" / "invented-edition"
    assert assert_not_authored(data_dir / "abilities.json", curation_dir) is not None


# ---------------------------------------------------------------------------------------
# T076 / FR-028, SC-007 — a changed mechanic still blocks, at the unchanged 100 threshold.
# ---------------------------------------------------------------------------------------


def _abilities_check(summary: AbilitySummary, *, current_digest: str) -> ClassCheck:
    return ClassCheck(
        summary_class=SummaryClass.ABILITIES,
        keys=[KEY],
        authored={KEY: summary},
        current_digests={KEY: current_digest},
    )


def test_a_changed_mechanic_blocks_even_when_the_record_carries_attribution() -> None:
    """**The point of the whole rung.** Attribution is not a route around the summary gate.

    A record can be stamped with a version and an authorization and still be describing a
    mechanic that moved since. The gate compares digests and nothing else, so the stamp buys
    exactly nothing — which is what stops the blanket authorization from being spent on the
    property the gate exists to protect.
    """
    stamped = _summary(
        review_state=ReviewState.APPROVED,
        mechanic_digest=OLD_DIGEST,
        version=VERSION,
        authorization=AUTHORIZATION,
    )

    assert (
        effective_status(KEY, authored={KEY: stamped}, current_digest=NEW_DIGEST)
        is SummaryStatus.NEEDS_REREVIEW
    )


def test_a_changed_mechanic_raises_the_blocking_needs_rereview_finding() -> None:
    stamped = _summary(
        review_state=ReviewState.APPROVED,
        mechanic_digest=OLD_DIGEST,
        version=VERSION,
        authorization=AUTHORIZATION,
    )

    findings = check_class(_abilities_check(stamped, current_digest=NEW_DIGEST))

    assert [finding.finding_code for finding in findings] == ["SUM-NEEDS-REREVIEW"]
    assert findings[0].severity is Severity.BLOCKING


def test_a_changed_mechanic_holds_the_summary_coverage_below_its_hundred_threshold() -> None:
    """SC-007's second half: the ``summaries.*`` figures never fall below 100 in a release."""
    stamped = _summary(
        review_state=ReviewState.APPROVED,
        mechanic_digest=OLD_DIGEST,
        version=VERSION,
        authorization=AUTHORIZATION,
    )

    coverage = class_coverage(_abilities_check(stamped, current_digest=NEW_DIGEST))

    assert coverage.outstanding == (KEY,)
    assert coverage.ratio_percent < 100


def test_a_record_re_authored_against_the_new_mechanic_clears_the_gate() -> None:
    """The other direction: the gate is not merely always-red once a digest has moved.

    A record whose stored digest agrees with the run's own is approved, reaches 100, and raises
    nothing — so the assertions above are about the mechanic having moved, not about the check
    being unsatisfiable.
    """
    reauthored = _summary(review_state=ReviewState.APPROVED, mechanic_digest=NEW_DIGEST)

    check = _abilities_check(reauthored, current_digest=NEW_DIGEST)

    assert check_class(check) == []
    assert class_coverage(check).ratio_percent == 100


def test_the_abilities_gate_cannot_be_switched_off_for_a_re_baseline() -> None:
    """There is no configuration under which the class being re-baselined stops blocking."""
    config = load_config(env={})

    assert gate_for(SummaryClass.ABILITIES, config).name == "ON"
    assert SummaryClass.ABILITIES.has_gate_switch is False


# ---------------------------------------------------------------------------------------
# T077 / FR-028 — every refresh names its version and its authorization.
# ---------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("version", "authorization", "missing"),
    [
        (None, None, [REBASELINE_VERSION_FIELD, REBASELINE_AUTHORIZATION_FIELD]),
        (VERSION, None, [REBASELINE_AUTHORIZATION_FIELD]),
        (None, AUTHORIZATION, [REBASELINE_VERSION_FIELD]),
        ("   ", "   ", [REBASELINE_VERSION_FIELD, REBASELINE_AUTHORIZATION_FIELD]),
    ],
)
def test_half_the_attribution_pair_is_not_attribution(
    version: str | None, authorization: str | None, missing: list[str]
) -> None:
    """Either half alone leaves a question the pair was added to answer.

    A version with no authorization says when but not under what; an authorization with no
    version says under what but not against which build's digest. A rollback needs both to say
    which of ``curation/`` and ``data/`` it is reverting and to what.
    """
    base = [_record(review_state="approved", mechanic_digest=OLD_DIGEST)]
    head = [
        _record(
            review_state="approved",
            mechanic_digest=NEW_DIGEST,
            version=version,
            authorization=authorization,
        )
    ]

    refused = unattributed_refreshes(digest_refreshes(base, head))

    assert [r.key for r in refused] == [KEY]
    absent = [
        name
        for name, value in (
            (REBASELINE_VERSION_FIELD, refused[0].version),
            (REBASELINE_AUTHORIZATION_FIELD, refused[0].authorization),
        )
        if not value
    ]
    assert absent == missing


def test_the_attribution_pair_is_expressible_on_a_validated_record() -> None:
    """A guard that refuses a missing field is worthless if the field cannot be written.

    ``_Authored`` sets ``extra="forbid"``, so a curation file carrying these keys is rejected
    outright unless the model declares them.
    """
    stamped = _summary(
        review_state=ReviewState.APPROVED, version=VERSION, authorization=AUTHORIZATION
    )

    assert stamped.digest_refreshed_at_version == VERSION
    assert stamped.digest_refreshed_under_authorization == AUTHORIZATION


@pytest.mark.parametrize(
    "schema_name", ["abilities", "faction-rules", "detachment-rules", "glossary"]
)
def test_every_summary_class_schema_declares_the_attribution_pair(schema_name: str) -> None:
    """All four classes, because the re-baseline is not an abilities-only operation."""
    schema = json.loads(
        (REPO_ROOT / "schemas" / "curation" / f"{schema_name}.schema.json").read_text(
            encoding="utf-8"
        )
    )
    text = json.dumps(schema)

    assert REBASELINE_VERSION_FIELD in text
    assert REBASELINE_AUTHORIZATION_FIELD in text


def test_the_refusal_names_the_file_and_the_key_it_refuses(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Auditable without re-running the pipeline: the message carries the identifiers.

    A rollback has to be able to say which record in which of ``curation/`` and ``data/`` it
    reverts, and a refusal that said only "some digest moved" would not support that.
    """
    refused = unattributed_refreshes(
        digest_refreshes(
            [_record(review_state="approved", mechanic_digest=OLD_DIGEST)],
            [_record(review_state="approved", mechanic_digest=NEW_DIGEST)],
        )
    )
    print(f"curation/abilities/f-invented.json: {refused[0].key}")

    assert KEY in capsys.readouterr().out


# ---------------------------------------------------------------------------------------
# T078 / FR-025 — the re-baseline is an event, not a setting.
# ---------------------------------------------------------------------------------------

#: The vocabulary a standing re-baseline mode would have to be spelled in. Substrings, not whole
#: words, so `WGC_REBASELINE_ENABLED`, `WGC_DIGEST_REFRESH_MODE` and anything of that family are
#: all caught by the same rule.
_REBASELINE_VOCABULARY: tuple[str, ...] = ("rebaseline", "re_baseline", "digest_refresh")

#: Every stage an ordinary `rules-pipeline build` walks through. None of them may know about the
#: re-baseline at all: the machinery lives in `tools/`, which `pipeline/` cannot import because
#: it is not an installed package, and this asserts that stays true by name as well as by
#: packaging.
_PIPELINE_ROOT = REPO_ROOT / "pipeline"

#: The attribution pair, as the scan below looks for it.
_ATTRIBUTION_FIELDS = frozenset({REBASELINE_VERSION_FIELD, REBASELINE_AUTHORIZATION_FIELD})


def test_no_configuration_variable_switches_a_re_baseline_on() -> None:
    """FR-025: not a configuration flag left on. There is no flag to leave on."""
    offenders = [
        var.env_name
        for var in CONFIG_VARS
        if any(token in var.env_name.lower() for token in _REBASELINE_VOCABULARY)
    ]

    assert offenders == []


def test_the_resolved_configuration_carries_no_re_baseline_field() -> None:
    config = load_config(env={})
    fields = set(PipelineConfig.__dataclass_fields__)

    assert isinstance(config, PipelineConfig)
    assert [
        name for name in fields if any(token in name.lower() for token in _REBASELINE_VOCABULARY)
    ] == []


#: The ONE file under ``pipeline/`` allowed to name the attribution pair, and only as a field
#: DECLARATION. ``pipeline/models/authored.py`` is where a curation record's shape is written
#: down; a declaration is what makes the pair expressible at all (``_Authored`` sets
#: ``extra="forbid"``, so an undeclared key is rejected outright). What the exemption
#: deliberately does not permit is a *read*: the scan below still fails if that file, or any
#: other, loads either field's value anywhere.
_DECLARATION_SITE = "pipeline/models/authored.py"


def _annotated_declaration_targets(tree: ast.AST) -> set[int]:
    """The ``id()`` of every ``Name`` node that is an annotated-assignment target.

    A field declaration (``digest_refreshed_at_version: str | None = Field(...)``) reaches the
    walk below as a ``Name`` in store context, indistinguishable by name alone from a read. This
    is what tells the two apart.
    """
    return {
        id(node.target)
        for node in ast.walk(tree)
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
    }


def test_no_pipeline_stage_performs_or_reads_a_re_baseline() -> None:
    """FR-025: not a step any ordinary build performs.

    Three things at once, which is why the scan is over the parsed source rather than over
    imports alone:

    * no module under ``pipeline/`` may import from ``tools/``, where the machinery lives;
    * none may name either attribution field as a string literal, which is how a lookup on an
      already-parsed record would be spelled; and
    * none may **read** either field, anywhere but the one declaration site.

    The third matters most. A stage that branched on
    ``digest_refreshed_under_authorization`` would be exactly the route around the summary gate
    that T076 forbids — the attribution would start buying something, and a blanket
    authorization would then be spendable on the property the gate exists to protect.
    """
    offenders: list[str] = []
    for path in sorted(_PIPELINE_ROOT.rglob("*.py")):
        relative = path.relative_to(REPO_ROOT).as_posix()
        # Parsed, not grepped: a comment or a docstring may name the fields, executable code
        # may not, and only an AST can tell those apart.
        tree = ast.parse(path.read_text(encoding="utf-8"))
        declarations = (
            _annotated_declaration_targets(tree) if relative == _DECLARATION_SITE else set()
        )
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute | ast.Name):
                name = node.attr if isinstance(node, ast.Attribute) else node.id
                if name in _ATTRIBUTION_FIELDS and id(node) not in declarations:
                    offenders.append(f"{relative}: reads {name}")
            elif isinstance(node, ast.Constant) and node.value in _ATTRIBUTION_FIELDS:
                offenders.append(f"{relative}: names {node.value}")
            elif isinstance(node, ast.ImportFrom) and (node.module or "").startswith("tools"):
                offenders.append(f"{relative}: imports {node.module}")
            elif isinstance(node, ast.Import):
                offenders.extend(
                    f"{relative}: imports {alias.name}"
                    for alias in node.names
                    if alias.name.startswith("tools")
                )

    assert offenders == [], (
        "an ordinary build must neither perform a digest re-baseline nor read its attribution: "
        f"{offenders}"
    )


def test_the_declaration_site_exemption_covers_declarations_only() -> None:
    """The exemption above is narrow, and this is what keeps it narrow.

    If ``pipeline/models/authored.py`` ever *reads* one of the two fields — a validator, a
    computed property, a branch — the scan above must still catch it. That is only true while
    the exemption is a set of declaration nodes rather than a whitelisted filename, so assert
    the shape rather than trusting it.
    """
    tree = ast.parse((REPO_ROOT / _DECLARATION_SITE).read_text(encoding="utf-8"))
    named = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Name) and node.id in _ATTRIBUTION_FIELDS
    ]
    declarations = _annotated_declaration_targets(tree)

    assert named, "the declaration site no longer declares the attribution pair"
    assert all(id(node) in declarations for node in named)
    assert all(isinstance(node.ctx, ast.Store) for node in named)


def test_the_cli_exposes_no_re_baseline_command() -> None:
    """A re-baseline is not one of the eight things the pipeline can be asked to do."""
    source = (REPO_ROOT / "pipeline" / "cli.py").read_text(encoding="utf-8")

    assert cli is not None
    assert [token for token in _REBASELINE_VOCABULARY if token in source.lower()] == []
