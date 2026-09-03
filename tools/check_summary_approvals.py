#!/usr/bin/env python3
# AI-Assisted: Claude Code (model: claude-sonnet-5) - Self-approval guard for ability summaries
# (task T131): a PR that introduces `review_state: "approved"` on a record whose `reviewed_by`
# is the PR's own actor fails CI, complementing the CODEOWNERS routing on `curation/abilities/`
# (research D6). CODEOWNERS alone is not sufficient at this repository's current single-
# maintainer roster (see `.github/CODEOWNERS`'s own note) — this check is data-level and does
# not depend on a second reviewer existing.
# AI-Assisted: Claude Code (model: claude-opus-5) - Generalised the single hard-coded
# `curation/abilities/` prefix into contracts/authored-summary-gates.md §6's glob-to-key-field
# table (004 task T049), so one code path covers every authored summary class. The faction-rule
# row joins here; the detachment-rule and glossary rows join with their own phases.
# AI-Assisted: Claude Code (model: claude-opus-5) - Added the detachment-rule row (004 task
# T056) and the glossary row (004 task T063), completing contract §6's table. The glossary's
# `prefix` is a whole path rather than a directory, which `str.startswith` handles without a
# special case -- the table stays four uniform rows.
# AI-Assisted: Claude Code (model: claude-opus-5) - Added the digest re-baseline guard (009
# tasks T074/T075/T077, FR-026 to FR-029) into this tool's existing vocabulary rather than a
# second script: `digest_refreshes` classifies every mechanic_digest that moved in the diff by
# whether an APPROVAL is being carried across the move, and `unattributed_refreshes` refuses the
# ones that are without the version/authorization pair. The two precedents draw the line: the
# 39-record refresh (`3b4766a9`) touched records that were never approved and is bookkeeping;
# the 23-record refresh (`59f2986b`) touched approved records and needed a recorded human
# decision. A bulk refresh is mechanically indistinguishable from laundering an approval, and
# this is the check that tells them apart.
# AI-Assisted: Claude Code (model: claude-opus-5) - Rung R02a: the attribution pair was read from
# the head record alone, which tests PRESENCE, not FRESHNESS -- so the guard disarmed itself the
# moment the pass it constrains stamped every approved record, and any later PR could move any
# approved digest again under the stamp already sitting there. Attribution is now compared against
# the base record, and records are matched by key across every changed file of a class over a
# `--no-renames` diff, because resharding a curation file otherwise walked past both halves of
# this check at once.
"""Self-approval guard for every authored summary class.

  check_summary_approvals.py diff --base <ref> --head <ref> --actor <login>
      Used in CI on pull_request events. For every curation file the PR touches that matches a
      row of :data:`SOURCES`, compares the base and head content record by record. A record that
      is `approved` at head but was not `approved` at base (a new record, or one whose state just
      changed) is "newly approved" by this PR. If any newly approved record's `reviewed_by`
      equals `--actor`, the PR is a self-approval and this check fails.

      The same invocation ALSO refuses a **digest re-baseline that launders an approval**: a
      record `approved` at base and still `approved` at head whose `mechanic_digest` moved is
      carrying that approval across a change in what the digest describes, and it may do so only
      while naming `digest_refreshed_at_version` and `digest_refreshed_under_authorization`
      (FR-026 to FR-029). A record that was **not** approved at base is bookkeeping and passes
      freely -- no approval is being carried over anything.

**The attribution must be fresh for the refresh it attributes.** Both halves must be present and
non-empty, AND each must differ from the value the record already carried at base. A pair
identical to the base record's attributes nothing: it names the version and the decision of that
record's *previous* re-baseline, not this one. Presence alone would mean the guard disarms itself
the moment 009's blanket pass stamps the corpus -- protecting it exactly until the event the
guard was written to constrain, and inert from then on. Freshness is required per half for the
same reason presence is: a new version beside the previous authorization says *when* this refresh
happened but names the decision that authorised the previous one, and a new authorization beside
the previous version names a decision but not the build it was taken against. FR-029's blanket
authorization covers **one operation**, so a record's second refresh is a second operation and
cites its own named, dated artefact.

The rule deliberately refuses one honest case it cannot distinguish from a dishonest one: a
record refreshed twice under the same authorization at the same version. Nothing in the data
separates that from a stale stamp left untouched, and a guard resolves that ambiguity toward
refusal. The way through is a new recorded decision -- which is the thing this check exists to
demand.

The comparison is by **key**, never by file position, so reordering or an unrelated edit
elsewhere in the same file never produces a false positive. It is also by key **across every
changed file of the same class**, not within one path, so resharding a curation file does not
reset every record in it to "no prior" -- which had let a pull request that moved a file and
refreshed the approved digests inside it in the same commit walk past this check and the
self-approval check together. Which field carries the key differs per class — `ability_key` on
the existing class, `summary_key` on the three added by `004-rules-data-enrichment` — and that
difference is the whole of :data:`SOURCES`.

> **Known weakness, inherited from `002` and deliberately not diverged from here.** There is no
> `authored_by` field on any record; "author" is taken to be the pull-request actor. The rule
> actually enforced is therefore *the person opening the pull request may not be the person named
> as reviewer on a newly-approved record*, which is weaker than FR-025's wording implies. Adding
> `authored_by` across all four classes is recorded as a follow-up rather than done here, because
> it would touch the 2 031 existing ability records — a change-class collision with
> `004`'s transform work under `tools/check_change_classes.py`. **This limitation must be
> restated in the pull request that first switches a class gate on.**
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

ABILITIES_GLOB_PREFIX = "curation/abilities/"


@dataclass(frozen=True)
class CurationSource:
    """One row of `contracts/authored-summary-gates.md` §6's glob-to-key-field table."""

    prefix: str
    key_field: str
    wrapper_key: str | None = None
    """The array's key inside an object wrapper, for `curation/faction-rules/`.

    That class is the one file shape here that is **not** a bare array, because FR-021 needs
    `army_rule_state` — "this faction genuinely has no army rule" — expressible alongside the
    rules, and a bare array cannot carry it. The wrapper costs exactly this one field.
    """


#: The table itself. A class joins it when its curation tree lands, so a glob with no records
#: yet is simply a row that matches no changed file — never a special case in the code below.
SOURCES: tuple[CurationSource, ...] = (
    CurationSource(ABILITIES_GLOB_PREFIX, "ability_key"),
    CurationSource("curation/faction-rules/", "summary_key", wrapper_key="rules"),
    CurationSource("curation/detachment-rules/", "summary_key"),
    CurationSource("curation/glossary.json", "summary_key"),
)


def source_for(path: str) -> CurationSource | None:
    """The table row governing ``path``, or ``None`` when no class claims it."""
    stripped = path.strip()
    if not stripped.endswith(".json"):
        return None
    return next((source for source in SOURCES if stripped.startswith(source.prefix)), None)


def changed_curation_files(base: str, head: str) -> list[tuple[str, CurationSource]]:
    """Every changed file the table claims, paired with the row that claims it.

    ``--no-renames`` is load-bearing, not tidiness. Rename detection is on by default, and it
    reports a resharded curation file as a **single destination path** -- the source path never
    reaches this list, so the records as they stood at base become invisible and every record at
    the new path reads as brand new. Reported as delete-plus-add, both paths are present, which
    is what lets :func:`cmd_diff` find a record's prior after it has moved between files.
    """
    result = subprocess.run(
        ["git", "diff", "--name-only", "--no-renames", f"{base}...{head}"],
        capture_output=True,
        text=True,
        check=True,
    )
    pairs: list[tuple[str, CurationSource]] = []
    for line in result.stdout.splitlines():
        source = source_for(line)
        if source is not None:
            pairs.append((line.strip(), source))
    return pairs


def changed_ability_files(base: str, head: str) -> list[str]:
    """The abilities-only view, kept because CI and `002`'s docs both name it."""
    return [
        path
        for path, source in changed_curation_files(base, head)
        if source.prefix == ABILITIES_GLOB_PREFIX
    ]


def records_in(payload: Any, source: CurationSource) -> list[dict[str, Any]]:
    """The record array a parsed curation document holds, whatever its file shape."""
    if source.wrapper_key is not None:
        if not isinstance(payload, dict):
            raise ValueError(f"{source.prefix}*.json must hold a JSON object wrapper")
        payload = payload.get(source.wrapper_key, [])
    if not isinstance(payload, list):
        raise ValueError(f"{source.prefix}*.json must hold a JSON array of summary records")
    return payload


def read_records_at(
    ref: str, path: str, source: CurationSource | None = None
) -> list[dict[str, Any]]:
    """The records a curation file held at ``ref``, or ``[]`` if it did not exist there yet.

    A brand-new file is `[]` at base, so every record in it is by definition newly approved
    wherever it says so.
    """
    resolved = source if source is not None else source_for(path)
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    text = result.stdout.strip()
    if not text:
        return []
    return records_in(
        json.loads(text), resolved or CurationSource(ABILITIES_GLOB_PREFIX, "ability_key")
    )


def newly_approved(
    base_records: Sequence[dict[str, Any]],
    head_records: Sequence[dict[str, Any]],
    *,
    key_field: str = "ability_key",
) -> list[dict[str, Any]]:
    """Records `approved` at head that were not `approved` at base — new or just transitioned.

    A record that was already `approved` at base and remains `approved` at head (carried
    forward untouched, FR-024) is deliberately excluded: this PR did not introduce that
    approval, so it is not this PR's self-approval to fail on.
    """
    base_by_key = {record.get(key_field): record for record in base_records}
    result = []
    for record in head_records:
        if record.get("review_state") != "approved":
            continue
        prior = base_by_key.get(record.get(key_field))
        if prior is None or prior.get("review_state") != "approved":
            result.append(record)
    return result


def self_approved_keys(
    records: Sequence[dict[str, Any]], *, actor: str, key_field: str = "ability_key"
) -> list[str]:
    """The keys among ``records`` whose `reviewed_by` is `actor` — a self-approval."""
    return sorted(
        str(record.get(key_field))
        for record in records
        if actor and record.get("reviewed_by") == actor
    )


#: The re-baseline attribution pair FR-028/FR-029 require on a refreshed record, and the ONE
#: place their spelling is written down on this side. `pipeline/models/authored.py` declares the
#: same two fields on `AbilitySummary` and `_SummaryRecord`; the four
#: `schemas/curation/*.schema.json` files declare them optional so the change stays additive over
#: the existing records. Optional in the schema, mandatory in the authoring rule -- this check is
#: what makes the second half true.
REBASELINE_VERSION_FIELD = "digest_refreshed_at_version"
REBASELINE_AUTHORIZATION_FIELD = "digest_refreshed_under_authorization"


@dataclass(frozen=True)
class DigestRefresh:
    """One record whose ``mechanic_digest`` moved between base and head.

    ``carries_approval`` is the whole distinction FR-026 draws, and it is deliberately read from
    **both** ends of the diff rather than from head alone:

    * ``approved`` at base and ``approved`` at head -- the approval is being carried ACROSS the
      refresh. Only a recorded human decision may do that (precedent ``59f2986b``);
    * anything else -- the record was not approved before the refresh, so the refresh carries no
      approval over anything and is bookkeeping (precedent ``3b4766a9``). A record that becomes
      approved in this same pull request is a *new* approval, which :func:`newly_approved` and
      the self-approval check above already govern; demanding a re-baseline authorization for it
      too would refuse ordinary first-time authoring.
    """

    key: str
    carries_approval: bool
    version: str | None = None
    authorization: str | None = None
    prior_version: str | None = None
    """The version half as it stood on the BASE record -- ``None`` if never re-baselined before.

    Without it this class can only ask whether a stamp is present, and presence is satisfied
    forever by the stamp a previous re-baseline left behind.
    """
    prior_authorization: str | None = None
    """The authorization half as it stood on the base record. See :attr:`prior_version`."""

    @property
    def is_attributed(self) -> bool:
        """Both halves of the pair present and non-empty.

        Both, because either alone leaves a question the record was added to answer: a version
        with no authorization says when but not under what, and an authorization with no version
        says under what but not against which build's digest.

        Presence only. It is deliberately **not** the permission test -- see
        :attr:`attribution_defects`.
        """
        return bool(self.version) and bool(self.authorization)

    @property
    def attribution_defects(self) -> list[str]:
        """Why this refresh's attribution does not authorize it, half by half, or ``[]``.

        A half is defective when it is absent (``missing``) or when it repeats the value the
        record already carried at base (``stale``). Stale is the case that matters: a stamp
        identical to the one already on the record describes that record's *previous* refresh,
        so it attributes this one to nothing. Reported per half so the refusal says which.
        """
        defects: list[str] = []
        for field, value, prior in (
            (REBASELINE_VERSION_FIELD, self.version, self.prior_version),
            (REBASELINE_AUTHORIZATION_FIELD, self.authorization, self.prior_authorization),
        ):
            if not value:
                defects.append(f"missing {field}")
            elif value == prior:
                defects.append(f"stale {field}")
        return defects

    @property
    def is_permitted(self) -> bool:
        """Bookkeeping is always permitted; a carried approval only when freshly attributed."""
        return not self.carries_approval or not self.attribution_defects


def _digest_of(record: dict[str, Any]) -> str:
    return str(record.get("mechanic_digest", ""))


def _text_or_none(record: dict[str, Any], field: str) -> str | None:
    value = record.get(field)
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def digest_refreshes(
    base_records: Sequence[dict[str, Any]],
    head_records: Sequence[dict[str, Any]],
    *,
    key_field: str = "ability_key",
) -> list[DigestRefresh]:
    """Every record whose ``mechanic_digest`` moved, classified by FR-026's distinction.

    Records absent at base are skipped: a brand-new record has no prior digest to have moved
    away from, so it is authoring rather than a re-baseline.

    ``base_records`` is expected to span the whole change class, not one file -- see
    :func:`cmd_diff`. A record that moved between files still has a prior, and a prior is what
    both this classification and the freshness test are read from.
    """
    base_by_key = {record.get(key_field): record for record in base_records}
    refreshes: list[DigestRefresh] = []
    for record in head_records:
        key = record.get(key_field)
        prior = base_by_key.get(key)
        if prior is None or _digest_of(prior) == _digest_of(record):
            continue
        refreshes.append(
            DigestRefresh(
                key=str(key),
                carries_approval=(
                    prior.get("review_state") == "approved"
                    and record.get("review_state") == "approved"
                ),
                version=_text_or_none(record, REBASELINE_VERSION_FIELD),
                authorization=_text_or_none(record, REBASELINE_AUTHORIZATION_FIELD),
                prior_version=_text_or_none(prior, REBASELINE_VERSION_FIELD),
                prior_authorization=_text_or_none(prior, REBASELINE_AUTHORIZATION_FIELD),
            )
        )
    return refreshes


def unattributed_refreshes(refreshes: Sequence[DigestRefresh]) -> list[DigestRefresh]:
    """The refreshes carrying an approval whose attribution is absent or stale.

    "Unattributed" covers both, because a stamp repeated unchanged from the base record
    attributes nothing to *this* refresh — it names the previous one's version and decision.
    """
    return sorted(
        (refresh for refresh in refreshes if not refresh.is_permitted), key=lambda r: r.key
    )


def cmd_diff(args: argparse.Namespace) -> int:
    offending: list[str] = []
    unattributed: list[str] = []

    # Grouped by change class, and the base side read across the whole group, because a record
    # that moved between two files of the same class must still find its prior. Matching within
    # one path let a pull request reshard a curation file and refresh the approved digests
    # inside it in the same commit: at the new path every record looked brand new, and at the
    # old path there was no head record left to compare against.
    changed = changed_curation_files(args.base, args.head)
    by_source: dict[CurationSource, list[str]] = {}
    for path, source in changed:
        by_source.setdefault(source, []).append(path)

    for source, paths in by_source.items():
        class_base_records = [
            record for path in paths for record in read_records_at(args.base, path, source)
        ]
        for path in paths:
            head_records = read_records_at(args.head, path, source)
            introduced = newly_approved(
                class_base_records, head_records, key_field=source.key_field
            )
            for key in self_approved_keys(introduced, actor=args.actor, key_field=source.key_field):
                offending.append(f"{path}: {key}")
            refreshes = digest_refreshes(
                class_base_records, head_records, key_field=source.key_field
            )
            for refresh in unattributed_refreshes(refreshes):
                unattributed.append(
                    f"{path}: {refresh.key} ({', '.join(refresh.attribution_defects)})"
                )

    failed = False
    if offending:
        failed = True
        print(
            f'FAIL: this PR introduces review_state: "approved" on a record authored by its '
            f"own actor ({args.actor!r}). Only a pull request approved by someone other than "
            "the record's author may introduce an approved summary (research D6):",
            file=sys.stderr,
        )
        for entry in offending:
            print(f"  {entry}", file=sys.stderr)

    if unattributed:
        failed = True
        print(
            "FAIL: this PR refreshes mechanic_digest on a record that is approved at both ends "
            "of the diff, carrying that approval across a change in what the digest describes, "
            "without freshly naming the version it was refreshed at and the authorization it "
            "was refreshed under (FR-026 to FR-029). A record that was never approved may be "
            "refreshed as bookkeeping; this one may not. A stamp repeated unchanged from the "
            "base record is stale: it names the version and the decision of this record's "
            "PREVIOUS re-baseline and attributes this one to nothing:",
            file=sys.stderr,
        )
        for entry in unattributed:
            print(f"  {entry}", file=sys.stderr)

    if failed:
        return 1

    print(
        "OK: no newly approved authored summary is self-authored, and no digest refresh "
        "carries an approval without naming its version and authorization"
    )
    return 0


#: What ``--help`` shows. Deliberately NOT this module's ``__doc__``: that docstring is the
#: written-down rule, several hundred words of it, and `argparse` reflows whatever it is given
#: into the help text. Passing it made ``--help`` a wall of policy prose -- and, while the rule
#: was documented under two identical ``check_summary_approvals.py diff ...`` headings, printed
#: the tool's single subcommand twice.
_HELP_DESCRIPTION = (
    "Self-approval and digest-re-baseline guard for every authored summary class. Refuses a "
    "pull request that approves a summary its own actor reviewed, and one that refreshes a "
    "mechanic_digest on an approved record without freshly naming the version and the "
    "authorization the refresh happened under. The full rule is this module's docstring."
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=_HELP_DESCRIPTION)
    sub = parser.add_subparsers(dest="mode", required=True)

    diff_parser = sub.add_parser("diff", help="check a PR's newly approved authored summaries")
    diff_parser.add_argument("--base", required=True)
    diff_parser.add_argument("--head", required=True)
    diff_parser.add_argument("--actor", default="")
    diff_parser.set_defaults(func=cmd_diff)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
