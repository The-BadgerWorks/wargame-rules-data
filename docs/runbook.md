<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Documented the manual path around
     detection (task T111): rules-pipeline build and workflow_dispatch on candidate.yml both run
     regardless of detection state, per FR-056 and US3 acceptance scenario 6. -->
# Runbook: detection and the manual path

`.github/workflows/detect.yml` and `.github/workflows/candidate.yml` (tasks T108-T110) automate
the common case: a real points release moves a digest, a candidate is built, a curator reviews
it. This page is about the case that is *not* automated — a curator who needs a build **right
now**, independent of whatever the detector last decided.

## The manual path exists and does not consult detection state (FR-056)

Two entry points, neither of which reads `state/detection-digest.json` at all:

1. **A local build.**

   ```bash
   rules-pipeline build --rules-version-id mfm-2026-06
   # or, offline, against a synthetic fixture set:
   rules-pipeline build --offline --fixtures fixtures/sample --rules-version-id fixture-check
   ```

   `pipeline.cli.run_build` (the `build` command's implementation) never imports
   `pipeline.detect`, never opens `state/detection-digest.json`, and does not care whether the
   last `detect` sweep found a change, found nothing, or has never run. It is the same code
   `candidate.yml` calls.

2. **A manual `candidate.yml` dispatch**, from the Actions tab or `gh workflow run`:

   ```bash
   gh workflow run candidate.yml -f rules_version_id=mfm-2026-06
   ```

   `candidate.yml`'s trigger is `workflow_dispatch` **and** `workflow_call` (`detect.yml` uses
   the latter on exit `10`) — there is no `if:` condition anywhere in the workflow that reads
   `needs.detect.*` or any other detection output. A curator dispatching it directly gets exactly
   the same build, push, and PR that a detected release gets automatically.

**Why this matters operationally**: the detector can be down, stale, or simply not yet due to
run, and a curator who has independently confirmed a points release (a community report, a
manual check of the site) is never blocked on it. This is also the path used to rebuild a
candidate after a parser fix, where the detector's digest has not changed at all — the change
was in the pipeline, not the source.

## What *is* gated

Nothing above touches Releases or Pages. `candidate.yml` has no `pages: write` or `id-token:
write` permission (compare `.github/workflows/publish.yml`), so a manual candidate is exactly as
unpublished as an automated one — it still needs a `workflow_dispatch` of `publish.yml` against
the `published` (or `prerelease`) Environment, approved by a named reviewer, per
`contracts/pipeline-run-interface.md` §4.

## Detection itself, for reference

- `rules-pipeline detect [--channel published]` sweeps the points source, digests the
  presentation-free projection of every faction page (`pipeline/detect/projection.py`, research
  D4b), and compares it against `state/detection-digest.json`. Exit codes: `0` no change, `10` a
  mechanical change, `40` the source was unreachable or refused, `41` its structure changed and
  values could not be extracted (`contracts/pipeline-run-interface.md` §2).
- Every check — including a failed one — appends one line to `state/run-ledger.jsonl`
  (`pipeline/observability/ledger.py`), so a quiet period (nobody released anything) is
  distinguishable from a broken detector (nothing is running).
- `WGC_DETECT_STALENESS_HOURS` (default `48`) is the staleness alarm: no *successful* check
  (exit `0` or `10`) within that window is itself alerted on, independent of whatever the last
  attempted check's own outcome was (`pipeline/detect/staleness.py`, FR-055).
- `.github/workflows/detect.yml` runs the schedule (`0 9,21 * * *`, twice daily) and the manual
  `workflow_dispatch` equivalent of the same sweep. Its own manual dispatch is *also* independent
  of any prior state — it always performs a real sweep, it is simply the automated schedule's
  on-demand form rather than the candidate-build's.

## Arming (what happens to `detect.yml` once this lands on `main`)

`detect.yml`'s `schedule` trigger only fires from the repository's default branch, and only at
its next scheduled time (`0 9,21 * * *`) — merging this change does **not** cause an immediate
run. No credential is required for the sweep itself: `WGC_NOTIFY_WEBHOOK_URL` is optional, and an
unconfigured webhook makes notification a documented no-op (`pipeline/observability/notify.py`)
rather than a failure. The workflow's only permission is `contents: write` over `state/`; it
cannot reach Releases or Pages regardless of what it detects.
