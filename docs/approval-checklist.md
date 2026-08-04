<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote the approver's checklist (task
     T121): what an approver reads and in what order, what a clean report does not excuse, and
     the rule that approving content and shipping different content is impossible by
     construction (FR-037, FR-038). -->
# Approval checklist

This is what a reviewer reads before approving a `publish` deployment in the Actions UI, and in
what order. It exists so "I approved it" means the same specific thing every time, for every
release — including the plain, boring, points-only ones that are the majority of them.

## Reading order (FR-037)

The candidate PR body (`pipeline/report/pr_body.py`, task T119) is generated in exactly this
order, so reading it top to bottom *is* following this checklist:

1. **Verdict and scale.** Can this ship at all (`CLEAN` / `ADVISORY ONLY` / `BLOCKED`), and how
   much of the snapshot is uncertain — unverified pricing, hybrid-edition entities, escalating
   price tiers, outstanding summaries? A `BLOCKED` candidate never reaches this checklist in
   practice (`rules-pipeline validate` refuses it, exit `30`), but the count-and-proportion habit
   is the same one that makes "how much of this release is uncertain" answerable at a glance
   every time, not only when something is wrong.
2. **What changed** (`change-summary.md`) — every added, removed, or renamed datasheet and
   detachment, and every changed point, detachment-cost, or enhancement-cost value as `was →
   now`. This is the release, in the form a player would ask about it.
3. **Unverified pricing** (`unverified-pricing.md`) — entities carried forward on last-known
   pricing because the points source did not repeat them this cycle. Not a defect by itself; a
   *rising* count across releases is the signal worth noticing (`docs/runbook.md`).
4. **Edition mismatch** (`edition-mismatch.md`) — datasheets whose detail source has not caught
   up to the points source's declared edition. Same posture: expected while the Wahapedia export
   trails 11th Edition, worth watching if the count or proportion climbs.
5. **Ability-summary coverage** (`summary-coverage.md`) — the editorial backlog, per faction.
6. **The changed-file list** (the PR's own **Files changed** tab) — one JSON file per datasheet
   under `data/wh40k-11e/factions/*/datasheets/`, so the file list alone names the scope of the
   release before opening any report (research D3).

## What a clean report does not excuse

A `CLEAN` or `ADVISORY ONLY` verdict means the automated checks found nothing blocking. It does
not mean:

- **The approver may skip reading the change summary.** A points-only release with zero findings
  is still a release — the checklist above is read in full every time, not only when something
  is flagged. There is no "trust the green checkmark and skip to approve" path; the checklist has
  no shortcut for that case because FR-037 does not have one.
- **A rising unverified or hybrid count is fine because nothing is technically wrong.** Both are
  advisory by design (FR-035/FR-058) so a single release is never blocked by upstream drift the
  curator cannot fix — but a *trend* across releases is exactly the early signal
  `docs/runbook.md` and the ledger trend rendering exist to surface. An approver who notices one
  is expected to raise it, not wave it through because the report itself passed.
- **The summary-coverage backlog is someone else's problem.** It is reported on every run
  (FR-025) specifically so it never becomes a surprise at release time.

## The rule this checklist ultimately serves

**Approving content and shipping different content is impossible by construction** (FR-038,
FR-039). What a reviewer approves in the Actions UI is a deployment to an environment bound to a
`commitSha` and an `expectSha256` — not a description of a release, the bytes of one. The
`publish` job then:

1. rebuilds the snapshot from exactly `commitSha`,
2. **asserts the rebuilt bundle's sha256 equals `expectSha256`, or exits `51` and writes
   nothing** (`pipeline/publish/gate.py`, task T116),
3. re-validates the rebuilt tree and refuses on any blocking finding, exit `30`,
4. only then creates the Release, uploads the asset, re-downloads and verifies it, and
   regenerates the manifest.

An approver cannot approve "the PR as it looked when I reviewed it" and have something else
ship, because there is no step between approval and publication where the content could change
without the checksum assertion catching it. Reading this checklist and clicking **Approve** in
the Actions UI is the entire human contribution FR-038 requires — everything downstream of that
click is either the exact approved bytes or a refusal.

## What "approved" records (data-model.md §7.2)

GitHub's environment protection rule is the record of *who* approved and *when* — visible in the
Actions run's deployment history, and not a file this repository writes on its own initiative.
`state/published-checksums.json` carries the same fact forward beside the checksum it gates, as
`approvalRef: {deploymentId, approver, approvedAt}`, so a support enquiry about a specific
release can name who approved it without re-reading a workflow log months later.

**Known limitation, stated plainly rather than glossed over** (matching `docs/repo-settings.md`'s
own posture on the same fact): with a single maintainer and `prevent_self_review: false`,
`approver` is recorded as the run's dispatching actor, which is accurate today because the
dispatcher and the approver are the same person. The day a second reviewer exists, this should
be revisited to attribute the record to the specific approver via the Deployments API rather
than the run actor.
