<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote the operational-readiness overview
     (task T157): ownership and the single-maintainer limitation, the third-party dependency
     posture, monitoring signals and where they alert, candidate visibility, and the support path
     answered entirely from reports/<rulesVersionId>/ without re-running anything. -->
# Operational readiness

## Ownership

This repository has one operational role, the **data curator**, and at the time of writing one
person fills it: `adhoxx`. The curator builds candidates (or lets the scheduled detector do it),
reviews and approves publication, resolves blocking findings, authors ability summaries or routes
them to a reviewer, and is the one named reviewer on both GitHub Environments (`published` and
`prerelease`).

**Recorded honestly, not glossed over**: `docs/repo-settings.md` already states the limitation
this plainly for repository settings, and it is restated here because it governs the *people*
process, not just the config. `The-BadgerWorks` organization has no teams
(`gh api orgs/The-BadgerWorks/teams` returns `[]`) and no second maintainer exists. Two
consequences follow directly:

- **The Separation gate's "distinct non-author reviewer" control is not actually enforced.**
  `.github/CODEOWNERS` routes every change class to `@adhoxx`, and both `tools/
  check_summary_approvals.py` (self-approval guard on `curation/abilities/`) and branch
  protection's required-review count exist to *prepare* for a second reviewer, but with one
  maintainer, `adhoxx` approving their own candidate, publish, or ability summary is the
  operational reality, not the designed control. `enforce_admins` is deliberately left `false` on
  branch protection for the same reason — turning it on today would make `main` permanently
  unmergeable, since GitHub does not let a PR author satisfy their own required review.
- **There is no bus-factor redundancy.** If the sole curator is unavailable, nothing in this
  repository's automation degrades gracefully around that — detection still runs and still opens
  candidate PRs, but nobody is positioned to approve `publish.yml` or `withdraw.yml` until the
  curator (or a newly added second maintainer) is available again. This is a known gap, not a
  designed absorption of the risk.

Revisit this section — and `docs/repo-settings.md`'s reviewer lists and `.github/CODEOWNERS` —
the day a second maintainer or a reviewing bot with a human behind it joins.

## Third-party dependency posture

This repository has **no support relationship with either upstream source**. Both are consumed as
publicly available third-party material, accessed politely (`docs/configuration.md`'s
`WGC_REQUEST_INTERVAL_MS`, `pipeline/acquire/http.py`'s robots.txt-honouring client), never with
an API key, a data-sharing agreement, or any channel to report an issue and expect a response.
The README states this as policy, not merely as a fact about the current state: **"This project
is not official, is not licensed, and is not endorsed by, or affiliated with, any publisher of the
source material it reconciles."** It is an independent, fan-made data set for personal,
non-commercial companion-app use.

Operationally, this means:

- **Neither source owes this pipeline stability.** A page redesign, a robots.txt change, a rate
  limit, or the source disappearing entirely are all things this pipeline has to detect and stop
  gracefully in response to (exit `40`/`41`, `docs/runbook.md`'s exit-code table), never things it
  can escalate to the source about.
- **There is no SLA to depend on.** The detection cadence (`WGC_DETECT_CRON`, twice daily) and the
  staleness alarm (`WGC_DETECT_STALENESS_HOURS`) are this repository's own commitments to
  *noticing* a change quickly, not a guarantee about how quickly a source publishes one.
- **No credential exists that could be revoked**, because none is used against either source —
  the only credential anywhere in this design is the workflow's own `GITHUB_TOKEN`, scoped to
  this repository (`contracts/pipeline-run-interface.md` §5).

## Monitoring signals and where they alert

Three independent signals, all routed through the same optional destination
(`WGC_NOTIFY_WEBHOOK_URL`, `pipeline/observability/notify.py`) and all also recorded permanently
in `state/run-ledger.jsonl` (`pipeline/observability/ledger.py`) whether or not a notification
was configured or delivered:

| Signal | Source | Fires on | What it means |
|---|---|---|---|
| Detector fault | `detect.yml`, exit `40`/`41` | The points source refused/was unreachable, or its structure changed. | The previously published version stays current; a curator needs to look — `docs/runbook.md`'s structure-change procedure for `41`. |
| Staleness alarm | `pipeline/detect/staleness.py`'s `is_stale`, checked every `detect.yml` run | No *successful* `detect` (exit `0` or `10`) within `WGC_DETECT_STALENESS_HOURS` (default 48h) of now. | The detector itself may be broken — a scheduling failure, a persistent fault — independent of whether a real release happened. Fires even if today's own attempt failed for a different, already-alerted reason. |
| Integrity check | `integrity.yml`, daily, `rules-pipeline verify` | A published asset's re-fetched sha256 no longer matches `state/published-checksums.json`, or an asset can't be fetched at all. | Turns "we promise not to edit a release asset" into a monitored control (SC-007) — catches tamper, corruption, or an asset that has become unreachable. |

**A completed no-change or no-mismatch check is itself recorded** — `state/run-ledger.jsonl` gets
one line per run regardless of outcome, and `state/detection-digest.json` is updated on every
successful sweep. This is what makes "quiet because nothing happened" distinguishable from "quiet
because the automation stopped running" by reading the ledger alone, without needing today's
alert to have fired to know the system is alive.

Every notification step in `detect.yml` and `integrity.yml` is immediately followed by a step
that greps that job's own captured output for the literal webhook secret and fails if it appears
— a second, independent check beyond GitHub's own log masking that the sensitive-value discipline
(`docs/configuration.md`) held in practice, not just in code review.

## How a candidate awaiting approval stays visible

A candidate does not sit in some internal queue only the curator's memory tracks. Two GitHub-native
mechanisms make it visible to anyone looking at the repository, per
`contracts/pipeline-run-interface.md` §6:

1. **An open pull request** — `candidate.yml` pushes `candidate/<rulesVersionId>` and opens (or
   updates, on a re-run) a PR whose body is assembled by `pipeline/report/pr_body.py` in the
   approver's actual reading order: verdict and scale first, then what changed, then unverified
   pricing and edition mismatch, then ability-summary coverage (`READING_ORDER` in that module,
   FR-037). The PR stays open, and stays exactly as informative, regardless of how long approval
   takes.
2. **A pending environment deployment** — once `publish.yml` is dispatched against a candidate,
   the run sits in "Waiting for review" against the `published` or `prerelease` GitHub
   Environment until a named reviewer acts (`docs/verification/approval-rehearsal.md`'s live
   rehearsal confirms this: zero job steps run until a reviewer decides). That pending deployment
   is visible in the repository's Actions tab and via `gh api .../pending_deployments`
   independent of the PR.

Together these mean a release is never silently lost waiting on a reviewer — it is either an open
PR nobody has dispatched yet, or a pending deployment nobody has approved yet, and both are
first-class, queryable GitHub state rather than something only a workflow log or a person's memory
tracks.

## The support path: answering a mispriced-unit enquiry from `reports/<rulesVersionId>/` alone

`reports/<rulesVersionId>/` is retained for the life of a published version specifically so a
support enquiry ("why does my unit cost X?") can be answered **without re-running anything** —
no rebuild, no re-acquisition, no need to reproduce the run (`pipeline/report/validation.py`'s
module docstring states this as the reason the report is retained, not merely as a nice property).
`write_reports` (same module) writes exactly this, every run, whether or not it published:

| File | What it answers |
|---|---|
| `report.json` / `report.md` | The verdict, the scale block (count **and** proportion for every category — `validation-report.md` §1.3), every finding by class and severity, and (for a published version) the source acquisitions that fed this build: which source, which declared edition, when it was retrieved. This alone answers "was this unit's price flagged as anything unusual in this release?" |
| `change-summary.md` (`SUB_REPORT_FILES["change_summary"]`) | What moved since the previous published version — the first place to look for "why did this change" rather than "is this right." |
| `unverified-pricing.md` | Every datasheet shipping on carried-forward, not source-restated, pricing (`pricing_confidence: unverified`) — leads with count and proportion (`docs/verification/spot-check-template.md` explains what this state means and how to sample it). If the enquiry is about a unit in this list, the answer is "the source did not restate this unit's price this release; it is shipping its last confirmed value." |
| `edition-mismatch.md` | Every datasheet whose mechanical detail came from a different declared edition than its points (`is_hybrid_edition`) — again led with count and proportion. If the enquiry is about a unit here, the answer is "its stats and its price were reconciled from two different source editions, which is the expected state at launch, not an error." |
| `summary-coverage.md` | Which ability keys a shipped datasheet uses but lack an approved current summary — relevant if the enquiry is about an ability's *description* rather than its cost. |

**Answering the enquiry**: open `reports/<rulesVersionId>/report.json` (or the human-readable
`report.md`) for the version the player is on, find the unit or ability in question in the
relevant sub-report (pricing question → `unverified-pricing.md` or the plain acquisition record if
it isn't listed there at all, meaning it shipped at a source-confirmed price; detail question →
`edition-mismatch.md`; description question → `summary-coverage.md`), and state what the report
already says. If the answer requires knowing what changed relative to the previous release,
`change-summary.md` has that too. None of this requires touching `pipeline/`, `work/`, or any
network access — the retained reports are the complete, standing answer.
