<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Documented the break-glass exception
     (task T151): hand-editing site/manifest.json or a release asset directly, permitted only
     under genuine pressure and only with the after-the-fact remediation this page requires,
     including exactly how state/published-checksums.json reconciliation works
     (pipeline/publish/pages.py, pipeline/publish/verify.py, .github/workflows/integrity.yml).
     This documents plan.md's Principle 5 exception. -->
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
