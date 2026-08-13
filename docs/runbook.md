<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Documented the manual path around
     detection (task T111): rules-pipeline build and workflow_dispatch on candidate.yml both run
     regardless of detection state, per FR-056 and US3 acceptance scenario 6.
     AI-Assisted: Claude Code (model: claude-sonnet-5) - Expanded with the scheduled detection
     loop overview, the exit-code operational table, the MFM structure-change procedure, and the
     two rollback paths (task T150) — additive to the existing manual-path content above, per
     contracts/pipeline-run-interface.md §2-§4 and the parser modules in pipeline/parse/.
     AI-Assisted: Claude Code (model: claude-opus-5) - Documented the publication-date input and
     the exit-51-that-is-only-a-date, after the wh40k-11e-2026-08-2 dispatch crossed 00:00Z. -->
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

## The scheduled detection loop, end to end

`detect.yml` runs twice daily (`0 9,21 * * *`, `WGC_DETECT_CRON`) and on manual
`workflow_dispatch`. One sweep proceeds like this:

1. **Detect.** `rules-pipeline detect --channel published` sweeps every points-source faction
   page, digests the presentation-free mechanical projection (`pipeline/detect/projection.py`),
   and compares it against `state/detection-digest.json`. The sweep's own exit code is read back
   from `detect.log` in the workflow (`set +e`, because a non-zero exit here is expected data,
   not a step failure) and mapped to the contract's stable set — see the exit-code table below.
2. **Record, always.** `state/detection-digest.json` is updated only on a *successful* sweep
   (exit `0` or `10`); `state/run-ledger.jsonl` gets one line appended for **every** sweep,
   including a failed one, and both are committed straight to `main`. This is deliberate: a quiet
   period (nobody released anything) has to be distinguishable from a broken detector (nothing is
   running) purely by reading the ledger, never by inference.
3. **Branch on the outcome.** Exit `10` (a mechanical change) computes a candidate id
   (`mfm-YYYY-MM` from the calendar month) and calls `candidate.yml` as a reusable workflow
   (`workflow_call`), which runs the full build, pushes `candidate/<id>`, and opens or updates a
   PR carrying the curated diff and every report. Exit `0` triggers nothing further. Exit `40` or
   `41` fails the job and raises an alert (see below) rather than calling `candidate.yml` at all.
4. **Notify.** A raised candidate (exit `10`), a detector fault (exit `40`/`41`), and the
   staleness alarm each send a distinct notification via
   `python -m pipeline.observability.notify`, which is a documented no-op when
   `WGC_NOTIFY_WEBHOOK_URL` is unset. Every notification step is followed by an assertion that the
   webhook secret never appears in that step's own captured output — a second, independent check
   beyond GitHub's own log masking (task T107).
5. **The staleness alarm fires independently of this sweep's own outcome.** `pipeline/detect/
   staleness.py`'s `is_stale` reads the whole ledger, not just this run: if no *successful*
   `detect` (exit `0` or `10`) has completed within `WGC_DETECT_STALENESS_HOURS` (default `48`),
   the alarm fires regardless of what today's attempt did. A detector that has been failing for
   three days in a row stays alarmed even on a day one of those three failed attempts happens to
   also be today's.

Nothing in this loop can reach Releases or Pages — `detect.yml`'s only permission is
`contents: write` over `state/`, and `candidate.yml` (which it calls) carries `contents: write`
and `pull-requests: write` only. Publication is a separate, always-manual step; see
`contracts/pipeline-run-interface.md` §4 and `docs/break-glass.md`.

## Exit codes: what each means operationally

Every exit code is fixed by `pipeline/exit_codes.py` and `contracts/pipeline-run-interface.md`
§2. This table restates the contract's own table with the on-call action spelled out for a
curator who has to decide what to do right now, not just what the code means abstractly.

| Code | Name | Meaning | On-call action |
|---|---|---|---|
| `0` | `SUCCESS` | Success; for `detect`, specifically **no change**. | None. A clean sweep or a clean build. |
| `10` | `CHANGE_DETECTED` | `detect` only: a mechanical change was found on the points source. | Nothing manual — `candidate.yml` is already triggered. Watch for the candidate PR; review it per `docs/authoring-summaries.md` / the approval checklist. |
| `20` | `ADVISORY_ONLY` | The candidate has advisory findings only; it is publishable pending approval. | Read the PR's sub-reports (`docs/operational-readiness.md` walks through what's in `reports/<id>/`), then dispatch `publish.yml` if satisfied. |
| `30` | `BLOCKING` | Blocking findings — publication refused. There is no override flag (FR-029). | Resolve the underlying finding (fix curated data, fix a parser bug, or update `curation/resolutions.json` if the finding itself is the thing that needs dating) and re-run `build`. The PR stays open until then. |
| `40` | `SOURCE_UNAVAILABLE` | A source was unreachable, refused (`403`/`429`), or throttled; the run stopped rather than evading (FR-007). | Alert only — the previously published version stays current. If the refusal persists across multiple sweeps, check whether the source's own availability or robots policy changed; do not raise the retry ceiling or retry the same host as a workaround (`pipeline/acquire/http.py`'s whole point is refusing to do that). |
| `41` | `SOURCE_STRUCTURE_CHANGED` | The points source's page structure changed; values are no longer extractable (FR-008). | Alert; the parser needs a fix. See "When the MFM page structure changes" below. |
| `42` | `COVERAGE_COLLAPSE` | Coverage (factions, datasheets, or priced datasheets) fell below the configured proportion of the previous published version. | Alert; do **not** publish. Investigate whether the source genuinely dropped content or the pipeline mis-parsed a page — `WGC_COVERAGE_MIN_*_RATIO` (`docs/configuration.md`) is the threshold that fired. |
| `50` | `NONDETERMINISTIC` | A rebuild produced a bundle with a different checksum than expected (FR-033, SC-006). | Block; investigate the serialiser (`pipeline/build/canonical_json.py` and neighbours) for a non-deterministic ordering or timestamp leak. Never touches a published artifact. |
| `51` | `APPROVAL_MISMATCH` | The rebuilt artifact is not the artifact that was approved (FR-039). | Re-approve the new content — this is `publish.yml`'s own checksum assertion refusing to publish something nobody actually reviewed. Never touches a published artifact. |
| `60` | `CONFIG_ERROR` | Configuration or invocation error. | Fix the invocation — an unknown `--config` key, an unparseable value, an out-of-range ratio (`pipeline/config.py`'s `ConfigError`), or a `build --published-at*` the run cannot resolve (below). |

Exit `40`, `41`, `42`, `50`, and `51` **never** touch a published artifact — this is a structural
property of where each check runs (before acquisition proceeds, before validation passes, or
before the approval gate's checksum assertion succeeds), not a convention to remember.

### The publication date, and the exit 51 that is not a content change

`snapshotMeta.publishedAt` is the only timestamp in the bundle (`curated-snapshot-format.md` §6),
so it is also the only field that can make an unchanged tree produce two different checksums.
`build` takes it as an input:

- **nothing given** — today's UTC date. Correct for a *first* build of a candidate, which is
  what `candidate.yml` does and why that workflow passes neither option.
- **`--published-at 2026-08-12`** (or `2026-08-12T00:00:00Z`) — an explicit date, for
  reproducing a historic build on a laptop.
- **`--published-at-from-report`** — the date this checkout's own `reports/<id>/report.json`
  recorded, which `candidate.yml` committed when it built the candidate. This is what
  `publish.yml`'s rebuild uses, so the approved commit's date travels with the approval and no
  dispatch input can disagree with it. If the record is missing or unreadable the run exits `60`
  rather than falling back to the clock.

**If a publish run exits `51`, check this field before assuming the sources moved.** Diff the
approved bundle against the rebuilt one; a single scalar difference at
`/snapshotMeta/publishedAt` means the rebuild dated itself, not that the content changed, and no
re-approval is owed. (This is exactly what happened to `wh40k-11e-2026-08-2`: approved
2026-08-12, dispatched 2026-08-13, one field apart. `published_at` was documented as a build
input from 002 onward and had never been wired to the CLI, so every build stamped its own day.)

## When the MFM page structure changes (exit 41, `SRC-STRUCTURE-CHANGED`)

The points source ships every value needed in one HTTP response, but defers *placement*: a grid
carries empty `<template id="P:n">` holes, and later in the same response come
`<div hidden id="S:n">` blocks paired with `$RS(...)`/`$RC(...)` instructions that say how to move
one into the other. Two modules own this:

- **`pipeline/parse/mfm_swap_replay.py`** reconstructs the finished DOM by replaying every
  `$RS("S:a","P:b")` / `$RC("B:a","S:b")` instruction as an explicit move, in-process, with no
  browser or JavaScript engine (a deliberate, documented Principle 14 exception — the replay is
  about thirty lines and total by construction; a headless browser would be neither small nor
  deterministic). **Totality is the safety property**: after every instruction is applied, no
  `<template>` may remain and no `hidden` source block may be left unclaimed. Either condition
  raises `StructureChanged` (`finding_code = "SRC-STRUCTURE-CHANGED"`, `exit_code = 41`) — the
  run stops rather than guessing at a partial reconstruction.
- **`pipeline/parse/mfm_dom.py`** extracts mechanical values from the reconstructed DOM
  afterward, reading through containment (a points value from inside the `<li>` that also carries
  its model-count label) rather than document order, and through structure and literal text
  (`YOUR UNIT COSTS`, `2DP`) rather than utility classes that churn on every redesign.

**Reproducing exit `41` against a fixture:**

1. Capture what changed about the live page's structure *as a description*, never as a saved
   copy of the real page (`fixtures/README.md`'s prohibition on committing or redacting a real
   capture applies here with full force — a captured page is raw source material, full stop).
2. Author a new or edited fixture under `fixtures/detection/` or `fixtures/sample/` (whichever
   set the change class fits) that reproduces the *structural quirk* — an unfilled placeholder, an
   `$RS` call naming a block the response no longer contains, a renamed heading literal — using
   invented faction and unit names.
3. Run `rules-pipeline build --offline --fixtures fixtures/<set> --rules-version-id
   fixture-check` and confirm it reproduces exit `41` (or whatever the new symptom actually is)
   against the fixture before touching any parser code — this is the "fixture reproduces the
   defect before the fix" half of `docs/failed-then-fixed.md`'s standing rule.
4. Fix the parser (`mfm_swap_replay.py` and/or `mfm_dom.py`) against the fixture, re-run the same
   command, and confirm it now succeeds (or fails with a *different*, expected finding if the
   fixture also encodes a case that should still block).
5. Add the fixture-driven test to `tests/` alongside the parser fix in the same PR, per
   `docs/failed-then-fixed.md` — a structure-change fix that ships without a fixture regression
   test is incomplete, because the whole point is that the same class of breakage cannot silently
   recur.

## Rollback: two paths, deliberately different in scope

### Data withdrawal — one already-published version, fast, no rebuild

```bash
rules-pipeline withdraw --rules-version-id <id> --reason "<short factual reason>"
```

or, in CI, `gh workflow run withdraw.yml -f rules_version_id=<id> -f reason="<text>" -f
channel=<prerelease|published>`.

`pipeline.publish.withdraw.run_withdraw` does exactly one thing: flip `withdrawn` and
`withdrawnReason` on one manifest entry and redeploy Pages. **No rebuild, no source access, no
touch of `data/` or `curation/`.** This is why `withdraw.yml` is its own workflow rather than a
mode of `publish.yml` — a defective release has to be neutralised in under a minute under
pressure (SC-009), and a workflow that has to check out a commit, reinstall the package, and
rebuild a multi-thousand-datasheet snapshot before it can flip one flag cannot meet that. The
withdrawn version stays **listed, not deleted**, and its `fileUrl` should remain retrievable — a
consumer pinned to it is not broken, only warned off treating it as current. A correction ships as
a **new** `rulesVersionId`; the withdrawn entry is never rewritten beyond its two withdrawal
fields. Like `publish.yml`, `withdraw.yml` is gated on the channel's GitHub Environment with a
required reviewer — withdrawal is fast once approved, not unreviewed.

### Pipeline revert — a `git revert` of a pipeline code change

A `git revert` of a commit under `pipeline/` (or its tests) undoes a code change going forward.
By construction, it **affects no already-published version**: every publication is
content-addressed and gated —

- `publish.yml`'s job asserts the rebuild's sha256 equals the approved `--expect-sha256` before
  anything is created (FR-039, exit `51` otherwise), so an already-published Release's bytes are
  never touched by anything that happens on `main` afterward.
- `site/manifest.json` only gains a new entry through the same gated `publish` job; a reverted
  pipeline commit changes what the *next* build produces, not what any past manifest entry names.
- `state/published-checksums.json` is append-only evidence of what was actually published, not a
  target `git revert` writes to.

So the revert's blast radius is exactly "the next candidate this pipeline builds," never "a
version already sitting in the manifest." If a bad pipeline change already shipped a bad
*published* version (as opposed to merely being merged to `main`), the fix is **both**: revert (or
forward-fix) the pipeline code, **and** withdraw the affected version if it is already published —
the two rollback paths are complementary, not alternatives, and `docs/failed-then-fixed.md`'s
fixture-regression-test rule applies to the pipeline-code half of that fix.
