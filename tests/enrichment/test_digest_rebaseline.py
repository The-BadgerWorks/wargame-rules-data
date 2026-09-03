# AI-Assisted: Claude Code (model: claude-opus-5) - The five digest re-baseline guards (009
# tasks T074-T078, FR-025 to FR-029, SC-007), written BEFORE the classification pass (T080) they
# exist to constrain, so that pass is bounded by them rather than trusted to respect them. Each
# guard was demonstrated red against the violation it exists to prevent and green after
# restoring; the per-guard red output is recorded in this rung's report.
# AI-Assisted: Claude Code (model: claude-opus-5) - Rung R02a: the guards above tested the
# library functions, not the path CI runs, and read the attribution pair from head alone --
# so a stale stamp permitted a fresh digest move, which is what every approved record would
# carry the moment 009's blanket pass stamped it. Added the freshness cases, the rename case,
# and an end-to-end `cmd_diff` section over a real throwaway repository, because `cmd_diff` is
# the wiring that makes CI refuse anything and it appeared nowhere in this file.
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Rung R02a-fix3: added the merge-base
# section (`_diverge` plus the false-refusal, fail-open-mirror, and merge-base-unavailable
# cases), which builds two branches diverging from one common ancestor -- the shape an
# un-rebased PR takes once its target branch moves, which every prior repo in this file could
# not represent because each committed in a single straight line. Folded
# `commit.gpgsign=false` and `core.hooksPath=/dev/null` into `_git` itself, so every throwaway
# repository this file creates runs isolated from the contributor's own ambient git config.
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

import argparse
import ast
import importlib.util
import json
import subprocess
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

#: A *second*, later stamp. A record refreshed twice has been refreshed at two versions under
#: two recorded decisions; re-presenting the first pair describes the first move, not this one.
NEWER_VERSION = "invented-edition-0000-01"
NEWER_AUTHORIZATION = "invented-authorization-record-0000-01-01"

#: Two synthetic curation paths in the same class, so a reshard can move a record between them.
CURATION_PATH = "curation/abilities/f-invented.json"
OTHER_CURATION_PATH = "curation/abilities/f-invented-reshard.json"


def _record(
    key: str = KEY,
    *,
    review_state: str,
    mechanic_digest: str = OLD_DIGEST,
    version: str | None = None,
    authorization: str | None = None,
    reviewed_by: str = "invented-curator",
) -> dict[str, object]:
    """One synthetic curation record, in the on-disk shape the tool reads from a diff."""
    record: dict[str, object] = {
        "ability_key": key,
        "name": key.split(":")[-1].replace("-", " ").title(),
        "summary": SUMMARY,
        "review_state": review_state,
        "mechanic_digest": mechanic_digest,
        "reviewed_by": reviewed_by,
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


# ---------------------------------------------------------------------------------------
# T077 / FR-028 — and the pair must be fresh FOR THIS REFRESH, not merely present at head.
# ---------------------------------------------------------------------------------------


def test_a_stale_attribution_does_not_authorize_a_second_refresh() -> None:
    """The bypass the guard would otherwise open the moment the pass it constrains happens.

    Reading the pair from head alone tests *presence*, not *freshness*. After 009's blanket
    re-baseline every approved record carries a stamp — so a later pull request could move any
    approved digest again, leave the existing stamp exactly where it is, and pass. The guard
    would protect the corpus precisely until the event it was written for, and be inert from
    then on. A pair identical to the one already on the record attributes nothing.
    """
    base = [
        _record(
            review_state="approved",
            mechanic_digest=OLD_DIGEST,
            version=VERSION,
            authorization=AUTHORIZATION,
        )
    ]
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
    assert refreshes[0].is_attributed is True, "presence is not the question being asked"
    assert refreshes[0].is_permitted is False
    assert [r.key for r in unattributed_refreshes(refreshes)] == [KEY]


def test_a_genuine_re_baseline_replacing_an_older_stamp_is_still_permitted() -> None:
    """The direction that proves the rule tightened rather than banning re-baselines outright.

    A record may be re-baselined a second time. What it may not do is claim the *first*
    re-baseline's decision as authority for the second.
    """
    base = [
        _record(
            review_state="approved",
            mechanic_digest=OLD_DIGEST,
            version=VERSION,
            authorization=AUTHORIZATION,
        )
    ]
    head = [
        _record(
            review_state="approved",
            mechanic_digest=NEW_DIGEST,
            version=NEWER_VERSION,
            authorization=NEWER_AUTHORIZATION,
        )
    ]

    refreshes = digest_refreshes(base, head)

    assert refreshes[0].carries_approval is True
    assert refreshes[0].is_permitted is True
    assert unattributed_refreshes(refreshes) == []


def test_the_first_stamp_on_a_never_refreshed_record_is_fresh() -> None:
    """The blanket pass itself. Unstamped at base is the *absence* of a prior decision, not a

    stale one, so the very operation these guards were written for is not refused by them.
    """
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

    assert refreshes[0].prior_version is None
    assert refreshes[0].prior_authorization is None
    assert unattributed_refreshes(refreshes) == []


@pytest.mark.parametrize(
    ("version", "authorization", "defects"),
    [
        (VERSION, NEWER_AUTHORIZATION, [f"stale {REBASELINE_VERSION_FIELD}"]),
        (NEWER_VERSION, AUTHORIZATION, [f"stale {REBASELINE_AUTHORIZATION_FIELD}"]),
        (
            VERSION,
            AUTHORIZATION,
            [f"stale {REBASELINE_VERSION_FIELD}", f"stale {REBASELINE_AUTHORIZATION_FIELD}"],
        ),
        (None, NEWER_AUTHORIZATION, [f"missing {REBASELINE_VERSION_FIELD}"]),
        (NEWER_VERSION, None, [f"missing {REBASELINE_AUTHORIZATION_FIELD}"]),
    ],
)
def test_half_a_refreshed_pair_is_not_a_refreshed_pair(
    version: str | None, authorization: str | None, defects: list[str]
) -> None:
    """Freshness is per half, for the same reason presence is.

    A new version beside the previous authorization says *when* this refresh happened but names
    the decision that authorised the previous one; a new authorization beside the previous
    version names a decision but not the build it was taken against. FR-029's blanket
    authorization covers *one* operation, so a record's second refresh is a second operation and
    cites its own.
    """
    base = [
        _record(
            review_state="approved",
            mechanic_digest=OLD_DIGEST,
            version=VERSION,
            authorization=AUTHORIZATION,
        )
    ]
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
    assert refused[0].attribution_defects == defects


def test_an_unapproved_record_may_reuse_a_stale_stamp_because_it_carries_nothing() -> None:
    """Freshness is the price of carrying an approval, exactly as presence already was.

    FR-026's distinction is unchanged by this rung: a record nobody has approved launders no
    approval, so its stamp — fresh, stale or absent — buys and costs nothing.
    """
    base = [
        _record(
            review_state="needs_rereview",
            mechanic_digest=OLD_DIGEST,
            version=VERSION,
            authorization=AUTHORIZATION,
        )
    ]
    head = [
        _record(
            review_state="needs_rereview",
            mechanic_digest=NEW_DIGEST,
            version=VERSION,
            authorization=AUTHORIZATION,
        )
    ]

    assert unattributed_refreshes(digest_refreshes(base, head)) == []


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


#: Where a *record* object lives inside each class's schema document. `faction-rules` is the one
#: file shape that is not a bare array, so its records sit a wrapper deeper -- and that difference
#: is exactly what a whole-document substring match cannot see.
_RECORD_SUBSCHEMA_PATH: dict[str, tuple[str, ...]] = {
    "abilities": ("items",),
    "faction-rules": ("properties", "rules", "items"),
    "detachment-rules": ("items",),
    "glossary": ("items",),
}


@pytest.mark.parametrize("schema_name", sorted(_RECORD_SUBSCHEMA_PATH))
def test_every_summary_class_schema_declares_the_attribution_pair(schema_name: str) -> None:
    """All four classes, because the re-baseline is not an abilities-only operation.

    Asserted at the **path**, not as a substring of the serialised document. Every one of these
    record objects sets ``additionalProperties: false``, so a declaration placed anywhere but
    inside the record's own ``properties`` leaves the pair unwritable -- a curation file carrying
    it would be rejected outright -- while a whole-document ``in`` check still reads green. The
    nesting is correct as shipped; this is what can prove it.
    """
    node = json.loads(
        (REPO_ROOT / "schemas" / "curation" / f"{schema_name}.schema.json").read_text(
            encoding="utf-8"
        )
    )
    for step in _RECORD_SUBSCHEMA_PATH[schema_name]:
        node = node[step]

    assert node["additionalProperties"] is False, "an undeclared key must be rejected outright"
    assert REBASELINE_VERSION_FIELD in node["properties"]
    assert REBASELINE_AUTHORIZATION_FIELD in node["properties"]


# ---------------------------------------------------------------------------------------
# The path CI actually runs. Everything above exercises the library; `ci.yml` invokes
# `check_summary_approvals.py diff`, and until this section existed the whole `unattributed`
# block could be deleted from `cmd_diff` with every test in this file still green. Each case
# below builds a real throwaway repository, because the thing under test is `git diff` output
# and a hand-built record list cannot stand in for it.
# ---------------------------------------------------------------------------------------


#: Isolates every throwaway repository below from the contributor's own ambient git config.
#: `_init_repo` used to set only `user.name`/`user.email`, so a global `commit.gpgsign = true` or
#: `core.hooksPath` pointed at a real hook script made `_git(..., check=True)` raise on `commit`
#: and errored the whole section -- on a contributor's machine, never in CI, which starts from a
#: clean `$HOME`. One tuple, spliced into every invocation by `_git` itself, so the flags cannot
#: drift between the ~25 `cmd_diff` tests in this section that create and commit into one of
#: these repos.
_HOSTILE_CONFIG_GUARD: tuple[str, ...] = (
    "-c",
    "commit.gpgsign=false",
    "-c",
    "core.hooksPath=/dev/null",
)


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *_HOSTILE_CONFIG_GUARD, *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def _init_repo(tmp_path: Path) -> Path:
    """A throwaway repository with one seed commit on ``main``."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.name", "seed")
    _git(repo, "config", "user.email", "seed@example.com")
    (repo / "README.md").write_text("seed\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-q", "-m", "seed")
    return repo


def _commit_curation(
    repo: Path,
    files: dict[str, list[dict[str, object]]],
    *,
    message: str,
    removing: tuple[str, ...] = (),
) -> str:
    """Write synthetic curation files, delete any named, commit, and return the sha."""
    for relative in removing:
        _git(repo, "rm", "-q", relative)
    for relative, records in files.items():
        path = repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
        _git(repo, "add", relative)
    _git(repo, "commit", "-q", "-m", message)
    return _git(repo, "rev-parse", "HEAD").strip()


def _run_diff(base: str, head: str, *, actor: str = "") -> int:
    """`cmd_diff` exactly as `ci.yml` calls the script, in the current working directory."""
    return int(
        check_summary_approvals.cmd_diff(argparse.Namespace(base=base, head=head, actor=actor))
    )


def test_cmd_diff_refuses_an_unattributed_refresh_and_names_the_file_and_the_key(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The refusal CI emits, asserted against what the command actually printed.

    Auditable without re-running the pipeline: a rollback has to be able to say which record in
    which file it reverts, and a refusal reading only "some digest moved" would not support that.
    """
    repo = _init_repo(tmp_path)
    base = _commit_curation(
        repo,
        {CURATION_PATH: [_record(review_state="approved", mechanic_digest=OLD_DIGEST)]},
        message="synthetic base",
    )
    head = _commit_curation(
        repo,
        {CURATION_PATH: [_record(review_state="approved", mechanic_digest=NEW_DIGEST)]},
        message="synthetic refresh",
    )
    monkeypatch.chdir(repo)

    code = _run_diff(base, head)

    assert code == 1
    error = capsys.readouterr().err
    assert f"{CURATION_PATH}: {KEY}" in error
    assert f"missing {REBASELINE_VERSION_FIELD}" in error
    assert f"missing {REBASELINE_AUTHORIZATION_FIELD}" in error


def test_cmd_diff_refuses_a_stale_stamp_carried_across_a_second_refresh(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """End to end, the case that becomes the normal state of the corpus after the blanket pass."""
    repo = _init_repo(tmp_path)
    base = _commit_curation(
        repo,
        {
            CURATION_PATH: [
                _record(
                    review_state="approved",
                    mechanic_digest=OLD_DIGEST,
                    version=VERSION,
                    authorization=AUTHORIZATION,
                )
            ]
        },
        message="synthetic base, already re-baselined once",
    )
    head = _commit_curation(
        repo,
        {
            CURATION_PATH: [
                _record(
                    review_state="approved",
                    mechanic_digest=NEW_DIGEST,
                    version=VERSION,
                    authorization=AUTHORIZATION,
                )
            ]
        },
        message="synthetic second refresh under the first refresh's stamp",
    )
    monkeypatch.chdir(repo)

    code = _run_diff(base, head)

    assert code == 1
    error = capsys.readouterr().err
    assert f"{CURATION_PATH}: {KEY}" in error
    assert f"stale {REBASELINE_VERSION_FIELD}" in error
    assert f"stale {REBASELINE_AUTHORIZATION_FIELD}" in error


def test_cmd_diff_permits_a_genuine_re_baseline_carrying_a_new_stamp(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """And the command still exits 0 for the operation it exists to permit."""
    repo = _init_repo(tmp_path)
    base = _commit_curation(
        repo,
        {
            CURATION_PATH: [
                _record(
                    review_state="approved",
                    mechanic_digest=OLD_DIGEST,
                    version=VERSION,
                    authorization=AUTHORIZATION,
                )
            ]
        },
        message="synthetic base, already re-baselined once",
    )
    head = _commit_curation(
        repo,
        {
            CURATION_PATH: [
                _record(
                    review_state="approved",
                    mechanic_digest=NEW_DIGEST,
                    version=NEWER_VERSION,
                    authorization=NEWER_AUTHORIZATION,
                )
            ]
        },
        message="synthetic second re-baseline, its own recorded decision",
    )
    monkeypatch.chdir(repo)

    code = _run_diff(base, head)

    assert code == 0
    assert "OK:" in capsys.readouterr().out


def test_cmd_diff_permits_a_bookkeeping_refresh_on_a_never_approved_record(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Precedent ``3b4766a9`` through the command, not merely through the classifier."""
    repo = _init_repo(tmp_path)
    base = _commit_curation(
        repo,
        {CURATION_PATH: [_record(review_state="in_review", mechanic_digest=OLD_DIGEST)]},
        message="synthetic base",
    )
    head = _commit_curation(
        repo,
        {CURATION_PATH: [_record(review_state="in_review", mechanic_digest=NEW_DIGEST)]},
        message="synthetic bookkeeping refresh",
    )
    monkeypatch.chdir(repo)

    assert _run_diff(base, head) == 0


def test_cmd_diff_refuses_an_approved_refresh_hidden_behind_a_file_rename(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Resharding a curation file must not launder the digests moved in the same commit.

    Matching per path let a rename walk straight through: at the new path the record has no
    prior, so it reads as authoring, and at the old path there is no head record to compare.
    Worse, ``git diff --name-only`` applies rename detection by default and reports the pair as
    a single destination path, so the old content is not even in the changed set. The tool now
    matches by key across every changed file of the same class, over a ``--no-renames`` diff.
    """
    repo = _init_repo(tmp_path)
    base = _commit_curation(
        repo,
        {CURATION_PATH: [_record(review_state="approved", mechanic_digest=OLD_DIGEST)]},
        message="synthetic base",
    )
    head = _commit_curation(
        repo,
        {OTHER_CURATION_PATH: [_record(review_state="approved", mechanic_digest=NEW_DIGEST)]},
        message="synthetic reshard that also refreshes",
        removing=(CURATION_PATH,),
    )
    monkeypatch.chdir(repo)

    code = _run_diff(base, head)

    assert code == 1
    assert f"{OTHER_CURATION_PATH}: {KEY}" in capsys.readouterr().err


def test_cmd_diff_still_refuses_a_self_approval_introduced_behind_a_rename(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The other half of the same wiring: a rename must not launder a *new* approval either."""
    repo = _init_repo(tmp_path)
    base = _commit_curation(
        repo,
        {
            CURATION_PATH: [
                _record(
                    review_state="in_review",
                    mechanic_digest=OLD_DIGEST,
                    reviewed_by="invented-actor",
                )
            ]
        },
        message="synthetic base",
    )
    head = _commit_curation(
        repo,
        {
            OTHER_CURATION_PATH: [
                _record(
                    review_state="approved",
                    mechanic_digest=OLD_DIGEST,
                    reviewed_by="invented-actor",
                )
            ]
        },
        message="synthetic reshard that also approves",
        removing=(CURATION_PATH,),
    )
    monkeypatch.chdir(repo)

    code = _run_diff(base, head, actor="invented-actor")

    assert code == 1
    assert f"{OTHER_CURATION_PATH}: {KEY}" in capsys.readouterr().err


def test_cmd_diff_no_longer_calls_a_carried_forward_approval_a_self_approval_on_reshard(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The one thing this rung **loosens**, stated plainly and asserted.

    Matching by key across the class also removes a false positive the per-path matching had: a
    record already ``approved`` at base, moved to another file with nothing else changed, used
    to read as newly approved at its new path and so as a self-approval whenever the resharding
    actor happened to be its reviewer. FR-024's carry-forward says that approval was not
    introduced by this pull request, and :func:`newly_approved`'s own docstring already said so
    -- per-path matching simply could not see it. The tightening direction is asserted directly
    above; this is the false positive it removes.
    """
    repo = _init_repo(tmp_path)
    carried = _record(
        review_state="approved", mechanic_digest=OLD_DIGEST, reviewed_by="invented-actor"
    )
    base = _commit_curation(repo, {CURATION_PATH: [carried]}, message="synthetic base")
    head = _commit_curation(
        repo,
        {OTHER_CURATION_PATH: [carried]},
        message="synthetic reshard, nothing else changed",
        removing=(CURATION_PATH,),
    )
    monkeypatch.chdir(repo)

    assert _run_diff(base, head, actor="invented-actor") == 0


# ---------------------------------------------------------------------------------------
# A git answer this guard cannot get is a refusal, not a pass. Every case below is the SAME
# pull request -- an approved record whose digest moves with no attribution, which the section
# above proves is refused -- with one git question made unanswerable. Before this rung each one
# exited 0, because an empty base side classifies every record as new and demands nothing.
# ---------------------------------------------------------------------------------------


def _unreachable_blob(repo: Path, ref: str, path: str) -> str:
    """Delete ``ref:path``'s blob from the object store and return the sha it used to name.

    This is the reachable shape of the fail-open, and the reason it is worth constructing rather
    than asserting on :func:`read_records_at` alone: ``git diff --name-only`` compares tree
    entries by oid and still answers, so :func:`changed_curation_files` reports the path as
    changed and the command runs its full length -- only the base content is missing. A partial
    (``--filter=blob:none``) clone with no network reaches the same state without any tampering.
    """
    blob = _git(repo, "rev-parse", f"{ref}:{path}").strip()
    loose = repo / ".git" / "objects" / blob[:2] / blob[2:]
    assert loose.exists(), (
        f"expected {blob} to be a loose object in a three-commit throwaway repository; if git "
        "has packed it, this construction needs to unpack it first"
    )
    loose.chmod(0o600)  # git writes loose objects read-only; Windows enforces it on unlink
    loose.unlink()
    return blob


def _refresh_pair(repo: Path) -> tuple[str, str]:
    """Base and head of an unattributed approved refresh -- refused whenever git can answer."""
    base = _commit_curation(
        repo,
        {CURATION_PATH: [_record(review_state="approved", mechanic_digest=OLD_DIGEST)]},
        message="synthetic base",
    )
    head = _commit_curation(
        repo,
        {CURATION_PATH: [_record(review_state="approved", mechanic_digest=NEW_DIGEST)]},
        message="synthetic refresh",
    )
    return base, head


def test_cmd_diff_refuses_when_the_base_content_cannot_be_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The silent half of the bug: `git show` fails, the base side empties, the guard clears it.

    The polarity is why it survived. The same empty base side makes :func:`newly_approved`
    **over**-report -- everything looks newly approved, which is noisy -- while making
    :func:`digest_refreshes` **under**-report, which is silent. This asserts the silent one.
    """
    repo = _init_repo(tmp_path)
    base, head = _refresh_pair(repo)
    _unreachable_blob(repo, base, CURATION_PATH)
    monkeypatch.chdir(repo)

    code = _run_diff(base, head)

    assert code == 1, "an unreadable base side must refuse, not clear, the pull request"
    error = capsys.readouterr().err
    assert "could not be performed" in error
    assert CURATION_PATH in error
    assert base in error


def test_cmd_diff_refuses_an_unresolvable_base_ref_and_says_which(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A base sha that was never fetched -- a shallow checkout, a mis-wired workflow input.

    It must not merely crash: `ci.yml` runs this as a shell step, and a traceback and a refusal
    are the same red X to a reviewer, but only one of them says what to do about it.
    """
    repo = _init_repo(tmp_path)
    _, head = _refresh_pair(repo)
    absent = "deadbeef" * 5
    monkeypatch.chdir(repo)

    code = _run_diff(absent, head)

    assert code == 1
    error = capsys.readouterr().err
    assert "cannot resolve" in error
    assert absent in error


def test_a_file_absent_at_a_ref_still_reads_as_an_empty_record_list(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The fail-open's legitimate twin, which must keep working exactly as it did.

    Absence has to stay cheap and silent in both directions -- a file this pull request **adds**
    is genuinely not at base, and a file it **deletes** in a reshard is genuinely not at head.
    Closing the fail-open by refusing every non-zero git exit would have turned ordinary
    authoring into a red build, which is the worse defect of the two.
    """
    repo = _init_repo(tmp_path)
    base = _git(repo, "rev-parse", "HEAD").strip()
    head = _commit_curation(
        repo,
        {CURATION_PATH: [_record(review_state="approved", mechanic_digest=NEW_DIGEST)]},
        message="synthetic first authoring of this file",
    )
    monkeypatch.chdir(repo)

    assert check_summary_approvals.read_records_at(base, CURATION_PATH) == []
    assert check_summary_approvals.read_records_at(head, OTHER_CURATION_PATH) == []
    assert _run_diff(base, head) == 0, "authoring a new curation file must stay green"


def test_absence_is_established_rather_than_inferred_from_a_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The distinction itself, at the level it is drawn.

    ``git show`` cannot tell these two apart -- both exit non-zero -- so the guard must not ask
    it to. :func:`path_exists_at` answers over a ref proven to resolve, and the two cases part
    company there: absent means ``[]``, present-but-unreadable raises.
    """
    repo = _init_repo(tmp_path)
    base, _ = _refresh_pair(repo)
    monkeypatch.chdir(repo)

    assert check_summary_approvals.path_exists_at(base, CURATION_PATH) is True
    assert check_summary_approvals.path_exists_at(base, OTHER_CURATION_PATH) is False

    _unreachable_blob(repo, base, CURATION_PATH)
    assert check_summary_approvals.path_exists_at(base, CURATION_PATH) is True
    with pytest.raises(check_summary_approvals.GitAnswerUnavailable):
        check_summary_approvals.read_records_at(base, CURATION_PATH)


# ---------------------------------------------------------------------------------------
# Rolling a re-baseline back. A plain `git revert` of a merged re-baseline is refused, and that
# refusal is DELIBERATE: the two tests below construct a rollback and the abuse this guard
# exists to catch, and assert that the guard receives byte-identical input from both. Nothing
# inside a base/head diff can separate them, so the sanctioned path is not an exemption but the
# ordinary rule -- a rollback names its own decision. `docs/break-glass.md` carries it.
# ---------------------------------------------------------------------------------------


def _rolled_back_pair(repo: Path, *, head_record: dict[str, object]) -> tuple[str, str]:
    """A merged, properly attributed re-baseline at base, and ``head_record`` at head."""
    base = _commit_curation(
        repo,
        {
            CURATION_PATH: [
                _record(
                    review_state="approved",
                    mechanic_digest=NEW_DIGEST,
                    version=VERSION,
                    authorization=AUTHORIZATION,
                )
            ]
        },
        message="synthetic merged re-baseline",
    )
    head = _commit_curation(repo, {CURATION_PATH: [head_record]}, message="synthetic head")
    return base, head


def test_a_plain_revert_and_a_stripped_stamp_are_the_same_pull_request(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Why this guard does not discriminate a rollback: there is nothing to discriminate on.

    A ``git revert`` of a merged re-baseline restores the record as it stood before -- old
    digest, still approved, no attribution pair, because the reverted commit is what added it.
    An actor stripping a stamp while moving a digest writes the same record. Both are refused,
    with the same two defects named, and a rule that admitted the first would admit the second.
    """
    outcomes = []
    for name in ("revert", "stripped-stamp"):
        sub = tmp_path / name
        sub.mkdir()
        repo = _init_repo(sub)
        base, head = _rolled_back_pair(
            repo, head_record=_record(review_state="approved", mechanic_digest=OLD_DIGEST)
        )
        monkeypatch.chdir(repo)
        code = _run_diff(base, head)
        outcomes.append((code, capsys.readouterr().err.splitlines()[-1].strip()))

    assert outcomes[0] == outcomes[1], (
        "a rollback and the abuse are indistinguishable to this guard; if these ever differ, "
        "some signal has appeared that the (b) break-glass decision should be revisited on"
    )
    code, entry = outcomes[0]
    assert code == 1
    assert f"{KEY} (missing {REBASELINE_VERSION_FIELD}, missing " in entry


def test_a_rollback_that_names_its_own_decision_is_permitted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The documented way through, asserted so `docs/break-glass.md` cannot drift from it.

    Undoing a re-baseline moves ``mechanic_digest`` on a record approved at both ends, which is
    the very thing FR-028 says must cite a named, dated artefact. The rollback is a decision, so
    it names one -- and then the existing rule permits it, with no exemption and no new code.
    """
    repo = _init_repo(tmp_path)
    base, head = _rolled_back_pair(
        repo,
        head_record=_record(
            review_state="approved",
            mechanic_digest=OLD_DIGEST,
            version=NEWER_VERSION,
            authorization=NEWER_AUTHORIZATION,
        ),
    )
    monkeypatch.chdir(repo)

    assert _run_diff(base, head) == 0


@pytest.mark.xfail(
    strict=True,
    reason=(
        "Open narrowing, follow-ups.md item 25: records are matched by key alone, so changing "
        "the key while refreshing the digest leaves no prior to compare against and the refresh "
        "is classified as authoring. The day this passes, the bypass is closed and this xfail "
        "must be promoted into an ordinary assertion."
    ),
)
def test_cmd_diff_refuses_an_approved_refresh_hidden_behind_a_rekeying(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Same family as the rename bypass this rung closed, but on identity rather than path.

    Deliberately not fixed here: unlike a reshard, rekeying an approved record requires
    deliberate intent and is plainly visible in a pull request's diff. Pinned rather than merely
    written down, so closing it cannot leave a stale note behind.
    """
    repo = _init_repo(tmp_path)
    base = _commit_curation(
        repo,
        {CURATION_PATH: [_record(KEY, review_state="approved", mechanic_digest=OLD_DIGEST)]},
        message="synthetic base",
    )
    head = _commit_curation(
        repo,
        {CURATION_PATH: [_record(OTHER_KEY, review_state="approved", mechanic_digest=NEW_DIGEST)]},
        message="synthetic rekey plus refresh",
    )
    monkeypatch.chdir(repo)

    assert _run_diff(base, head) == 1


# ---------------------------------------------------------------------------------------
# Rung R02a-fix3: both sides of the diff must be read from the same commit -- the merge-base,
# never `base`'s own tip. `changed_curation_files` already measured the changed-file set from
# `base...head` (git's own `merge-base(base,head)..head`), while `read_records_at` was reading
# base-side CONTENT at `base`'s tip directly -- a different commit whenever `base` had moved past
# the point `head` branched from. Every case below builds two branches that diverge from one
# common ancestor and never merge back, which is the shape an un-rebased PR takes once its target
# branch gains new commits -- a fake diff on two unrelated tips cannot stand in for it.
# ---------------------------------------------------------------------------------------


def _diverge(repo: Path, *, from_ref: str, branch: str) -> None:
    """Check out a new branch named ``branch`` starting at ``from_ref``, so later commits on
    ``main`` and on ``branch`` diverge from a shared ancestor instead of stacking on each other.
    """
    _git(repo, "checkout", "-q", "-b", branch, from_ref)


def test_merge_base_resolves_the_common_ancestor_of_diverging_branches(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _init_repo(tmp_path)
    ancestor = _git(repo, "rev-parse", "HEAD").strip()

    _diverge(repo, from_ref=ancestor, branch="pr-head")
    head = _commit_curation(
        repo,
        {CURATION_PATH: [_record(review_state="in_review")]},
        message="synthetic head commit",
    )

    _git(repo, "checkout", "-q", "main")
    base = _commit_curation(
        repo,
        {CURATION_PATH: [_record(OTHER_KEY, review_state="in_review")]},
        message="synthetic base commit, unrelated to the head commit",
    )
    monkeypatch.chdir(repo)

    assert check_summary_approvals.merge_base(base, head) == ancestor


def test_merge_base_refuses_when_base_and_head_share_no_common_history(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The named failure mode: unrelated histories, or history the checkout does not have.

    Orphan branches are the reachable shape of "no merge-base exists" -- a shallow clone missing
    the branch point answers `git merge-base` the same way, with the same non-zero exit.
    """
    repo = _init_repo(tmp_path)
    head = _git(repo, "rev-parse", "HEAD").strip()

    _git(repo, "checkout", "-q", "--orphan", "unrelated")
    _git(repo, "rm", "-q", "-rf", ".")
    (repo / "OTHER.md").write_text("synthetic unrelated history\n", encoding="utf-8")
    _git(repo, "add", "OTHER.md")
    _git(repo, "commit", "-q", "-m", "synthetic unrelated history")
    base = _git(repo, "rev-parse", "HEAD").strip()
    monkeypatch.chdir(repo)

    with pytest.raises(check_summary_approvals.GitAnswerUnavailable):
        check_summary_approvals.merge_base(base, head)


def test_cmd_diff_refuses_when_base_and_head_share_no_common_history(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """End to end: an unfindable merge-base is a named refusal through `cmd_diff`, never a pass.

    Keeps fix2's fail-closed contract -- a git question this guard's verdict depends on that git
    cannot answer refuses the pull request, and this is now true of the merge-base question too.
    """
    repo = _init_repo(tmp_path)
    head = _git(repo, "rev-parse", "HEAD").strip()

    _git(repo, "checkout", "-q", "--orphan", "unrelated")
    _git(repo, "rm", "-q", "-rf", ".")
    (repo / "OTHER.md").write_text("synthetic unrelated history\n", encoding="utf-8")
    _git(repo, "add", "OTHER.md")
    _git(repo, "commit", "-q", "-m", "synthetic unrelated history")
    base = _git(repo, "rev-parse", "HEAD").strip()
    monkeypatch.chdir(repo)

    code = _run_diff(base, head)

    assert code == 1
    error = capsys.readouterr().err
    assert "could not be performed" in error
    assert "merge-base" in error


def test_cmd_diff_does_not_refuse_an_unrebased_pr_for_a_move_it_never_saw(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The false refusal. Base has since re-baselined `KEY`; head branched before that and only
    ever edits `OTHER_KEY`, in the same file.

    Reading base-side content at `base`'s own tip sees `KEY` moved from `NEW_DIGEST` (base) to
    `OLD_DIGEST` (head) with no attribution on the head record, and refuses a pull request that
    never touched `KEY` at all. Reading it from the merge-base instead, `KEY` is identical on both
    sides of the diff -- head's copy is exactly the branch point's copy -- and nothing is refused
    for it.
    """
    repo = _init_repo(tmp_path)
    ancestor = _commit_curation(
        repo,
        {
            CURATION_PATH: [
                _record(KEY, review_state="approved", mechanic_digest=OLD_DIGEST),
                _record(OTHER_KEY, review_state="in_review", mechanic_digest=OLD_DIGEST),
            ]
        },
        message="synthetic common ancestor",
    )

    _diverge(repo, from_ref=ancestor, branch="pr-head")
    head = _commit_curation(
        repo,
        {
            CURATION_PATH: [
                _record(KEY, review_state="approved", mechanic_digest=OLD_DIGEST),
                _record(OTHER_KEY, review_state="in_review", mechanic_digest=NEW_DIGEST),
            ]
        },
        message="synthetic PR commit, touches only OTHER_KEY",
    )

    _git(repo, "checkout", "-q", "main")
    base = _commit_curation(
        repo,
        {
            CURATION_PATH: [
                _record(
                    KEY,
                    review_state="approved",
                    mechanic_digest=NEW_DIGEST,
                    version=VERSION,
                    authorization=AUTHORIZATION,
                ),
                _record(OTHER_KEY, review_state="in_review", mechanic_digest=OLD_DIGEST),
            ]
        },
        message="synthetic main re-baseline, unrelated to the PR branch",
    )
    monkeypatch.chdir(repo)

    code = _run_diff(base, head)

    out, err = capsys.readouterr()
    assert code == 0, err
    assert "OK:" in out


def test_cmd_diff_refuses_a_refresh_that_an_independently_advanced_base_tip_would_hide(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The fail-open mirror. Base's tip already carries the exact digest head introduces, but
    head's own copy carries no fresh attribution.

    Reading base-side content at `base`'s own tip sees identical digests on both sides and
    detects no refresh at all -- the missing attribution is never even asked about, and an
    approved record's digest moves in complete silence. Reading it from the merge-base, where the
    digest is still the old one on both sides, the move is visible and the missing attribution
    refuses the pull request as it must.
    """
    repo = _init_repo(tmp_path)
    ancestor = _commit_curation(
        repo,
        {CURATION_PATH: [_record(review_state="approved", mechanic_digest=OLD_DIGEST)]},
        message="synthetic common ancestor",
    )

    _diverge(repo, from_ref=ancestor, branch="pr-head")
    head = _commit_curation(
        repo,
        {CURATION_PATH: [_record(review_state="approved", mechanic_digest=NEW_DIGEST)]},
        message="synthetic PR refresh, no attribution",
    )

    _git(repo, "checkout", "-q", "main")
    base = _commit_curation(
        repo,
        {CURATION_PATH: [_record(review_state="approved", mechanic_digest=NEW_DIGEST)]},
        message="synthetic main, independently arrived at the same digest",
    )
    monkeypatch.chdir(repo)

    code = _run_diff(base, head)

    assert code == 1
    error = capsys.readouterr().err
    assert f"{CURATION_PATH}: {KEY}" in error
    assert f"missing {REBASELINE_VERSION_FIELD}" in error
    assert f"missing {REBASELINE_AUTHORIZATION_FIELD}" in error


# ---------------------------------------------------------------------------------------
# T078 / FR-025 — the re-baseline is an event, not a setting.
# ---------------------------------------------------------------------------------------

#: The vocabulary a standing re-baseline mode would have to be spelled in. Substrings, not whole
#: words, so `WGC_REBASELINE_ENABLED`, `WGC_DIGEST_REFRESH_MODE` and anything of that family are
#: all caught by the same rule. Matched against :func:`_scannable`, never against raw text: this
#: repository's CLI names everything with hyphens (`--rules-version-id`, `--commit-sha`), so an
#: underscore-only vocabulary would have let a `digest-refresh` subcommand or a `--re-baseline`
#: flag straight through the scan written to forbid exactly those.
_REBASELINE_VOCABULARY: tuple[str, ...] = ("rebaseline", "re_baseline", "digest_refresh")


def _scannable(text: str) -> str:
    """Lowercased with hyphens folded to underscores, so one vocabulary covers both spellings."""
    return text.lower().replace("-", "_")


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
        if any(token in _scannable(var.env_name) for token in _REBASELINE_VOCABULARY)
    ]

    assert offenders == []


def test_the_resolved_configuration_carries_no_re_baseline_field() -> None:
    config = load_config(env={})
    fields = set(PipelineConfig.__dataclass_fields__)

    assert isinstance(config, PipelineConfig)
    assert [
        name
        for name in fields
        if any(token in _scannable(name) for token in _REBASELINE_VOCABULARY)
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
    """A re-baseline is not one of the eight things the pipeline can be asked to do.

    Scanned through :func:`_scannable`, because a subcommand or flag in this CLI would be
    *spelled* with hyphens -- ``digest-refresh``, ``--re-baseline`` -- and the underscore-only
    reading of this same scan would have passed every one of them.
    """
    source = _scannable((REPO_ROOT / "pipeline" / "cli.py").read_text(encoding="utf-8"))

    assert cli is not None
    assert [token for token in _REBASELINE_VOCABULARY if token in source] == []


def test_the_help_text_names_the_diff_subcommand_once_and_is_not_the_policy_docstring(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """``--help`` used to print the tool's one subcommand twice.

    The module docstring documented the same ``check_summary_approvals.py diff --base ...``
    invocation under two identical headings -- once for the self-approval half, once for the
    re-baseline half -- and ``argparse`` was handed ``__doc__`` as its description, so both
    reached the help output. The docstring now documents the invocation once, and ``argparse``
    is handed a short description instead of several hundred words of rule.
    """
    docstring = check_summary_approvals.__doc__
    assert docstring is not None
    assert docstring.count("check_summary_approvals.py diff --base") == 1

    with pytest.raises(SystemExit) as exit_info:
        check_summary_approvals.main(["--help"])

    assert exit_info.value.code == 0
    help_text = capsys.readouterr().out
    # Three: the usage line, the `{diff}` choice list, and the subcommand's own help line. When
    # `__doc__` was the description it was five, because the duplicated heading came through too.
    assert help_text.count("diff") == 3
    assert "--base" not in help_text, (
        "the top-level help must not carry the subcommand's own flags -- it did only because "
        "the whole module docstring was being reflowed into the description"
    )
    assert "FR-026" not in help_text, "the rule belongs in the docstring, not in --help"
