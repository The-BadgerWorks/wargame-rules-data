<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Documented the break-glass exception
     (task T151): hand-editing site/manifest.json or a release asset directly, permitted only
     under genuine pressure and only with the after-the-fact remediation this page requires,
     including exactly how state/published-checksums.json reconciliation works
     (pipeline/publish/pages.py, pipeline/publish/verify.py, .github/workflows/integrity.yml).
     This documents plan.md's Principle 5 exception. -->
<!-- AI-Assisted: Claude Code (model: claude-opus-5) - 009 rung R02a-fix2: added the second
     section, rolling back a merged digest re-baseline. The digest guard
     (tools/check_summary_approvals.py) refuses a plain `git revert` of one, and that refusal
     is deliberate -- nothing inside a base/head diff separates a rollback from stripping a
     stamp while moving a digest. The ordinary path (an attributed rollback) is documented
     first, and this page is named as the escape hatch only for the case where even that
     cannot be done in time. -->
<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - 009 rung R02a-fix4, item 2: this page
     contradicted itself -- "the reverted records carry a stamp describing a re-baseline that is
     no longer in effect" versus, a few paragraphs earlier, "no attribution pair" for the same
     records. The second was correct; corrected the first, and named the interim exposure it was
     hiding: with no stamp, prior_version/prior_authorization are None, which disarms the
     staleness half of the guard's check on exactly those records until remediation lands. Also
     corrected the revert-vs-stripped-stamp test citation to describe how R02a-fix4 item 1
     actually builds the two arms now that they are independently constructed. -->
# Break glass: hand-editing published state directly

**This is an exception, not a procedure to reach for.** Every other document in this repository
describes the pipeline's normal path: build, validate, gate, publish, withdraw — all
committed-generator-driven, all reproducible outside CI (`contracts/pipeline-run-interface.md`
§1). This page describes the one deliberately-permitted way around all of that, and what has to
happen afterward to make the committed generator authoritative again.

## When this is permitted

Hand-editing `site/manifest.json` directly, or editing/replacing a GitHub Release asset directly,
bypassing `publish.yml` / `withdraw.yml` entirely, is permitted **only under genuine pressure** —
an incident where the normal gated path cannot act fast enough or at all (for example: the
`publish`/`withdraw` GitHub Environment approval mechanism itself is unavailable, or a live
consumer-facing defect needs to stop being served before a workflow run, however fast, could
plausibly complete). This is plan.md's documented Principle 5 exception: the pipeline's own
write-boundary and gate guarantees are structural (`data/` vs. `curation/`, `candidate.yml`'s lack
of Pages/Releases credentials, `publish.yml`'s checksum-binding assertion), and Principle 5
concedes there has to be a human escape hatch for the case those structures themselves are the
thing blocking an urgent fix — but concedes it as an exception that must be visible, not a
quietly-available second way to publish.

**It is not permitted** as a convenience — not to skip an approval that is merely slow, not to
avoid rebuilding when `rules-pipeline build` would have worked, and not to correct a mispriced
unit that `rules-pipeline withdraw` (docs/runbook.md's data-withdrawal path, executable in
roughly a millisecond of actual pipeline work) already handles in under a minute once dispatched
and approved. If the normal gated path can reach the outcome, use it.

## What must be documented, after the fact, every time

A break-glass action is only acceptable if it is followed immediately by a written record and by
remediation. The record must state:

- **Reason** — the specific incident or pressure that made the gated path unusable or too slow,
  stated factually (what was broken, what was at stake for a consumer).
- **Actor** — who made the edit, by name.
- **Time** — when the edit was made (UTC), and separately, when this record was written (it should
  be as close to immediate as the incident allowed).
- **Affected resources** — exactly which file(s), which `rulesVersionId`(s), and which release
  asset(s) were touched, with enough detail (paths, urls, before/after values) that someone
  reconstructing the incident later does not have to guess.
- **Remediation** — see below. Not optional, and not "will do later" — the record is not complete
  until remediation is either done or has a concrete, dated plan with an owner.

## Remediation: making the committed generator authoritative again

A break-glass edit leaves the live site or a release asset saying something the pipeline's own
records do not agree with. Remediation closes that gap in two parts, both required.

### Part 1 — re-run the real command

Whatever the hand edit was trying to achieve, re-run the equivalent gated pipeline command so
the *next* time anyone or anything (including `integrity.yml`) inspects the repository's own
state, it already reflects what was hand-edited:

- If the break-glass edit withdrew or should have withdrawn a version: dispatch
  `withdraw.yml` (or run `rules-pipeline withdraw --rules-version-id <id> --reason <text>`
  through the gate) for the same `rulesVersionId`, with the same reason. This regenerates
  `site/manifest.json`'s entry through the normal code path (`pipeline.publish.withdraw.
  run_withdraw`), so the committed generator's output and the hand-edited file converge — after
  this step, the manifest is once again something the pipeline itself produced, not something a
  human wrote by hand and left as the last word on it.
- If the break-glass edit published, or replaced, or corrected an asset: dispatch `publish.yml`
  through the normal gate for a **new** `rulesVersionId` carrying the correct content (never
  re-publish the same id with different bytes — that is exactly the case `ChecksumLedgerError`
  in `pipeline/publish/pages.py` exists to refuse under the normal path, and a hand edit does not
  get to route around that invariant permanently, only temporarily under pressure).

### Part 2 — reconcile `state/published-checksums.json`

`state/published-checksums.json` is the ledger `integrity.yml` checks daily against every
published `fileUrl` (`rules-pipeline verify`, `pipeline/publish/verify.py`): it re-downloads each
asset from its public URL — no auth header, exactly what a consumer would fetch — and re-hashes
it, comparing against the `sha256` recorded here. A break-glass asset edit, by definition, makes
a real asset's bytes disagree with whatever the ledger currently says (or the ledger is silent
about a manifest entry a hand-editor just added). Left alone, this is exactly the condition
`integrity.yml` exists to catch and alert on — which is correct behavior for an *unauthorized*
tamper, but not what you want for a break-glass action you are actively documenting and fixing.

Reconciliation means the ledger entry, after remediation, is true again:

1. Once Part 1's real command has run (a genuine `publish` or `withdraw` through the gate), the
   ledger is usually already consistent — `publish`'s own `record_published_checksum` call
   appended (or confirmed) the entry for the real, gate-produced bytes, and `withdraw` never
   touches the checksum ledger at all (it only edits `withdrawn`/`withdrawnReason` on the
   manifest — the asset and its recorded checksum are untouched by a withdrawal, which is exactly
   why a checksum entry for a withdrawn version keeps verifying successfully).
2. If a break-glass edit left an asset or a manifest entry that Part 1 did not fully supersede
   (for example, the hand edit touched a release asset in place rather than through a new
   `rulesVersionId`, which should not happen but is exactly the kind of thing genuine pressure
   produces), reconcile the ledger entry by hand, using
   `pipeline.publish.pages.record_published_checksum` directly (or an equivalent manual edit of
   `state/published-checksums.json` matching its shape) with the asset's **actual, current**
   sha256 — not the value that was true before the incident. `commit_sha` and `approval` are
   optional on that function specifically so a break-glass reconciliation entry can be recorded
   honestly, without inventing a commit or an approval that never happened. An entry recorded
   this way is visibly distinguishable from a normal gate-produced entry (it lacks `commitSha`
   and `approvalRef`), which is intentional — anyone reading the ledger later can tell which
   entries came from the gate and which came from a documented break-glass reconciliation.
3. **Run `rules-pipeline verify` (or wait for the next `integrity.yml` sweep, at most one day
   later) and confirm it exits `0`.** This is the check that closes the loop: reconciliation is
   not "done" until the automated daily control that would otherwise alert on this exact
   discrepancy runs clean against it.

## Template: fill this in at the moment break-glass is invoked

```markdown
## Break-glass action — <date, UTC>

**Reason**: <what was broken, what was at stake, why the gated path could not be used in time>

**Actor**: <name>

**Time of edit**: <UTC timestamp>
**Time this record was written**: <UTC timestamp>

**Affected resources**:
- File(s): <e.g. site/manifest.json, site/prerelease/manifest.json>
- rulesVersionId(s): <affected version ids>
- Release asset(s): <asset name/URL, if a release asset was touched>
- Before: <what the field/asset said before the edit>
- After: <what it says now>

**Remediation**:
- [ ] Part 1 — re-ran the equivalent gated command: <withdraw.yml run link / publish.yml run
      link, with the rulesVersionId and channel>
- [ ] Part 2 — state/published-checksums.json reconciled: <"already consistent after Part 1" /
      "manually reconciled, entry lacks commitSha and approvalRef by design" — describe which>
- [ ] `rules-pipeline verify` (or the next `integrity.yml` sweep) confirmed exit 0 on
      <date/run link>

**Follow-up / prevention** (optional but encouraged): <anything about why the gated path was not
fast enough this time, and whether that is itself worth fixing>
```

---

# Break glass, second case: rolling back a merged digest re-baseline

This section is about `curation/`, not the published site — a different resource, the same
structure: a gate that is right to exist, a rare situation in which it is the thing standing in
the way, and a documented path through that leaves a record behind.

## What the gate does, and why it refuses a revert

`tools/check_summary_approvals.py diff` refuses a pull request that moves `mechanic_digest` on a
record `approved` at both ends of the diff without freshly naming
`digest_refreshed_at_version` and `digest_refreshed_under_authorization` (FR-026 to FR-029). A
bulk digest refresh is mechanically indistinguishable from laundering an approval, and that pair
is the named, dated human decision that tells them apart.

**A plain `git revert` of a merged re-baseline is refused by that rule.** Reverting restores the
record as it stood before the re-baseline: the old digest, still `approved`, and **no**
attribution pair — because the commit being reverted is the one that added it. To the guard that
reads as an approved record whose digest moved with both halves of its attribution missing, which
is exactly the refusal above.

**The refusal is deliberate, not an oversight.** An actor stripping a stamp while moving a digest
— the abuse this check exists to catch — writes a byte-identical record. Nothing inside a
base/head diff separates the two, so a rule admitting the rollback would admit the abuse with it.
`tests/enrichment/test_digest_rebaseline.py`'s
`test_a_plain_revert_and_a_stripped_stamp_are_the_same_pull_request` builds the rollback through
an actual `git revert` of a real merged commit and the abuse through a hand-authored head record,
in two separate throwaway repositories, and asserts the guard returns an identical verdict on
both; if that test ever fails, some signal has appeared that this decision should be revisited on.
This is recorded as follow-up item 25's companion decision, and it is **not** a weakness the guard
is unaware of.

## The ordinary path: a rollback names its own decision

**Try this first. It is not break-glass, and in almost every case it is all that is needed.**

Rolling a re-baseline back *is itself a re-baseline*: it moves an approved record's
`mechanic_digest`, which is precisely the operation FR-028 says must cite a named, dated artefact.
So the rollback cites one. FR-029's blanket authorization covers one operation; a rollback is a
second operation and carries its own.

1. Record the rollback decision as its own dated artefact, the same way the re-baseline it undoes
   was recorded (`docs/verification/` is where those live).
2. Revert the re-baseline's content — the digests go back to their previous values.
3. On every record whose digest you moved back, set `digest_refreshed_at_version` to the version
   the rollback was made at and `digest_refreshed_under_authorization` to the artefact from step
   1. Both must differ from what the record carried before the rollback, or the guard reads them
   as stale and refuses — which is correct, because the previous pair describes the move you are
   undoing, not this one.
4. Open the pull request normally. The guard permits it, with no exemption and no override:
   `tests/enrichment/test_digest_rebaseline.py`'s
   `test_a_rollback_that_names_its_own_decision_is_permitted` asserts exactly this, so this page
   cannot drift away from the code.

Note what this does **not** ask you to do: it does not ask for a re-review of the summary text.
Whether the summary still describes the current mechanic is a separate question, answered by the
summary gate (`pipeline/validate/gates.py`) against the digest the pipeline computes, not by this
check.

## When this becomes break-glass

Only when the ordinary path above cannot be taken in time — a consumer-facing defect where a
plain `git revert` must land immediately and unedited, and stopping to author and stamp a
rollback decision would cost more than the defect is worth. In that case, and only in that case,
the Product Owner merges the revert with the guard's check overridden, and:

- **The break-glass record template above is mandatory**, with the same fields, filled in against
  `curation/` and the affected summary keys instead of a manifest and a `rulesVersionId`.
- **Remediation is the ordinary path, run late.** A follow-up pull request adds the attribution
  pair naming the rollback decision to every record the revert touched, so the corpus ends up in
  the state the ordinary path would have produced and the next digest move on those records has a
  truthful `prior` to be measured fresh against. **Until that lands, the reverted records carry
  no attribution pair at all** — `digest_refreshed_at_version` and
  `digest_refreshed_under_authorization` are both absent, exactly as reverting is described above:
  the commit that added the pair is the one being undone.
  - **This is a real interim exposure, not merely an untidy state.** With `prior_version` and
    `prior_authorization` both `None`, the guard's staleness half of `attribution_defects` is
    disarmed on exactly these records for as long as remediation is outstanding: a later pull
    request can re-present the *reverted* commit's own version/authorization pair verbatim — the
    stamp this page has just said describes a re-baseline that is no longer in effect — and
    because there is no prior value for it to match, the guard reads it as freshly attributed
    rather than stale, and passes it. Presence, not truth, is what the staleness check can see.
  - **What closes the window**: either the follow-up pull request above lands, naming the
    rollback's own new decision, or the affected records are moved out of `approved` (returned to
    `in_review`) until it does. Until one of those happens, the presence of *some* version/
    authorization pair on one of these records is not by itself evidence it was genuinely
    re-authorized after the rollback.
- **Never** loosen the guard, add an exemption path to it, or skip it in `ci.yml` to make a
  rollback land. An override is visible and leaves a record; a loosened guard is neither, and it
  stays loose for every pull request afterwards.
