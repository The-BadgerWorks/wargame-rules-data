<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Documented the manual path around
     detection (task T111): rules-pipeline build and workflow_dispatch on candidate.yml both run
     regardless of detection state, per FR-056 and US3 acceptance scenario 6.
     AI-Assisted: Claude Code (model: claude-sonnet-5) - Expanded with the scheduled detection
     loop overview, the exit-code operational table, the MFM structure-change procedure, and the
     two rollback paths (task T150) — additive to the existing manual-path content above, per
     contracts/pipeline-run-interface.md §2-§4 and the parser modules in pipeline/parse/.
     AI-Assisted: Claude Code (model: claude-opus-5) - Documented the publication-date input and
     the exit-51-that-is-only-a-date, after the wh40k-11e-2026-08-2 dispatch crossed 00:00Z.
     AI-Assisted: Claude Code (model: claude-sonnet-5) - 006 T050: added the equipment-overrides.json
     authoring loop beside the pre-existing option-overrides one, what resolving an
     OPT-UNPARSED/EQP-UNPARSED row under the extended grammar actually looks like, and what a
     non-empty option-regression Corrected section means operationally.
     AI-Assisted: Claude Code (model: claude-sonnet-5) - 007 T069: added resolving a
     CST-UNPARSED/OPT-SCOPE-UNRESOLVED row, reading the two new report-only loadout figures beside
     their not_compared/threshold_percent context, and what a Corrected-section entry outside 007's
     three named transition classes means. -->
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

## Resolving an unparsed loadout row (006): the option- and equipment-overrides loop

`006-unit-loadout-fidelity` widened `options_grammar.py` and added `equipment_grammar.py`, but a
residual tail is expected by design (spec Edge Cases: "expected to shrink, not vanish"). A row
either grammar cannot resolve is never guessed — it is reported (`OPT-UNPARSED` for an option row,
`EQP-UNPARSED` for a default-equipment sentence, both advisory) and named by structural position
only: `datasheet_id` and `line`, never the sentence itself (Policy and Safety Constraints).

A curator resolves one of these the same way `004` always resolved a composition or option row:
author an entry in the matching curation override file, keyed the same way. Both files are human-
authored, the pipeline never writes either, and every member is optional so a `004`-shaped override
still validates unchanged.

**`curation/option-overrides.json`** — for `OPT-UNPARSED`. The `006` extension adds `scope`'s two
independent eligibility columns and an optional per-choice `items[]` array for a multi-item bundle:

```jsonc
{ "datasheet_id": "ds-...", "line": 3,
  "scope": "unit",
  "eligible_model_name": "Fenmire Skirmisher",   // new in 006; optional
  "eligible_max_count": 4,                        // new in 006; optional
  "is_per_model": true,                           // new in 006; optional
  "choices": [
    { "name": "bracklight lance and close combat weapon",
      "items": [                                  // new in 006; optional
        { "role": "replaced", "item_name": "storm bolter",  "weapon_line": 1 },
        { "role": "granted",  "item_name": "bracklight lance", "count": 1, "weapon_line": 7 }
      ] } ] }
```

**`curation/equipment-overrides.json`** — new in `006`, for `EQP-UNPARSED`. Same key shape
(`datasheet_id`, `line`), no points field anywhere (default equipment is never priced), no
description field (Policy gate: no new prose surface):

```jsonc
{ "datasheet_id": "ds-...", "line": 2,
  "applies_to": "model_group", "model_name": "Skirmish Warden", "composition_line": 1,
  "items": [ { "item_name": "storm bolter", "weapon_line": 1 },
             { "item_name": "force halberd", "weapon_line": 4 } ] }
```

Both files enforce the same discipline: a `weapon_line` (or `composition_line`) naming a row that
does not exist on that datasheet is a **blocking** dangling-reference finding, never silently
dropped; a curator's stated link is **used, never re-derived** — the pipeline does not check it
against a name match, because a human already resolved the ambiguity a grammar could not. See
`contracts/loadout-schema-delta.md` §3 for the columns these overrides ultimately populate and
`specs/006-unit-loadout-fidelity/quickstart.md` §4 for the same loop from the authoring side.

## Reading a non-empty option-regression `Corrected` section (006)

`pipeline.cli option-regression` (`docs/configuration.md`'s sibling evidence command,
`reports/<rulesVersionId>/option-regression.md`) renders three sections: **Identical**, **Newly
resolved**, and **Corrected**. The third should be empty on every run — FR-009's zero-regression
guarantee means a row the baseline already resolved must resolve **identically** under the extended
grammar, and item decomposition is structurally forbidden from rewriting a choice's `name` or
`count` (research D5a, the O1 Ruling). A non-empty *Corrected* section is not automatically a
defect, but it is never routine — read every entry before approving anything:

1. **Check whether the moved value is a column `004` declared and never emitted**, rather than a
   value a consumer has ever actually read. The `wh40k-11e-2026-08` candidate's own *Corrected*
   section carried 21 entries, and all 21 were `maxChoices` moving from absent to a stated integer
   — T019 populating a column that was always declared and never populated, additive under
   `contracts/loadout-schema-delta.md` §3.3, not a regression FR-009 forbids.
2. **If the moved value is anything FR-009 actually promises** — eligibility, a replaced or granted
   item, a price — a new production reached a row the baseline had already resolved. Treat this as
   a defect in the production ordering (`pipeline/parse/options_grammar.py`'s clause table), not as
   a diff to wave through: baseline productions must run first and win, always.
3. **A legacy conflated choice (O1's ≈144-row class) acquiring item rows while keeping its existing
   `name`** is expected and is *not* a correction to that name — it shows up in *Newly resolved* or
   is invisible entirely, never in *Corrected*, because the label itself never moved.

An approver who sees a non-empty *Corrected* section and cannot account for every entry by rule 1
or rule 3 above should treat the candidate as **not ready for T048's Product Owner sign-off** until
the production ordering is fixed and layer 1's harness (`tests/enrichment/
test_options_grammar_regression.py`) is re-confirmed green.

### 007's three transition classes, and what an entry outside them means

`007-loadout-display-fidelity` adds a second, distinct reason for a non-empty *Corrected* section:
the FR-007 legacy-link correction, which touches every pre-`006` stem-object choice whose singular
link field pointed at the *granted* item under a field name that means "the removed item"
everywhere else in the bundle (`display-fidelity-schema-delta.md` §1.1, the one stated,
bounded exception to that document's additivity guarantee). Read the entry against research D3.3's
three named transition classes before reading anything else in it — `docs/configuration.md`'s
sibling table and `wh40k-11e-2026-08-3`'s own `reports/wh40k-11e-2026-08-3/option-regression.md`
are the worked example:

1. **Resolved and relinked** — the given-up item resolves to exactly one weapon line; `replaces`
   moves from the granted item's line to the given-up item's line, and `grants` is newly
   populated. Check: does the swap now read the right way round?
2. **Stated but unlinked** — the given-up item is named but does not link to exactly one weapon
   line; `replaces` moves from the granted item's line to **absent**, `grants` is populated.
   Expected — an unlinked item is better than a wrongly linked one.
3. **No given-up item stated at all** — the row was never a replacement in the first place;
   `replaces` moves from the granted item's line to **absent**, `grants` is populated. Expected.

The published `wh40k-11e-2026-08-3` candidate's own *Corrected* section carries all 2,039 legacy
choices this correction touches, split 37 / 2,002 / 0 across classes 1-3 above — every one
accounted for by rule 1, 2, or 3, none left over.

**A *Corrected* entry that fits none of these three classes, and is not one of `006`'s already-
documented `maxChoices` cases above, is the thing to stop on.** It means either the FR-007
correction reached a row research D3.3 did not anticipate, or a later, unrelated production
change moved a value FR-009's zero-regression guarantee protects. Treat it exactly as the 006
section above already instructs for its own out-of-class case: not ready for sign-off until the
production ordering (or the FR-007 role-correction pass, `pipeline/curate/assemble.py`'s
`_option_structure`) is checked against the specific row, and `tests/enrichment/
test_option_regression.py` and `test_legacy_option_roles.py` are re-confirmed green.

## Resolving an unparsed item-constraint row (007): the footnote-restriction loop

`007-loadout-display-fidelity` widened `options_grammar.py` with a closed, two-member restriction
vocabulary (`not_replaceable`, `one_per_unit` — `pipeline/models/curated.py`'s
`CuratedItemConstraint.constraint_type` docstring) for footnote-style restrictions ("this model's
storm bolter cannot be replaced") that `006` left as a stray marker glued to the item's own name.
Two advisory finding codes cover the two ways a restriction-shaped row can fail to become a clean
`datasheetItemConstraints` row, and they are deliberately never confused with each other
(`pipeline/parse/options_grammar.py`'s `is_constraint_shaped` module comment):

- **`CST-UNPARSED`** — the row is **restriction-shaped** (it matches the broader detector that
  looks for the restriction's grammatical pattern) but matches **neither** vocabulary member. This
  is "a restriction the closed vocabulary does not (yet) cover," never "this did not look like a
  restriction at all" — that second case falls through to the pre-existing `OPT-UNPARSED` exactly
  as it always has, and a row is reported under one code or the other, never both.
- **`OPT-SCOPE-UNRESOLVED`** — the restriction (or a scoped option stem more generally) names an
  eligibility subject that does not link, by the same exactly-one-match containment join
  `equipment_link.py` uses for `EQP-GROUP-UNRESOLVED`, to exactly one composition row of the same
  datasheet. The group still **ships**, carrying the stated `eligible_model_name` exactly as the
  source states it, unchecked — this is advisory and never a suppression (`tests/enrichment/
  test_legacy_option_roles.py::test_...` asserts the group survives with the finding attached, not
  instead of it).

**There is currently no dedicated curation override file for either code** — unlike `OPT-UNPARSED`
and `EQP-UNPARSED`, which resolve through `curation/option-overrides.json` and `curation/
equipment-overrides.json` respectively (above). `datasheetItemConstraints` shipped **zero rows** in
`wh40k-11e-2026-08-3` (`reports/wh40k-11e-2026-08-3/spot-check.md` §4): the taxonomy measurement
that sized the two-member vocabulary found real restriction-shaped candidates in the live corpus,
but none matched `not_replaceable` or `one_per_unit` closely enough to resolve, so `CST-UNPARSED`
has not yet had a real row to escalate against. Until one does, a curator who hits `CST-UNPARSED`
or a restriction-relevant `OPT-SCOPE-UNRESOLVED` has two choices, in order of preference: (1) widen
the vocabulary — a versioned bump of `itemConstraintVocabularyVersion`, per `curated.py`'s own
"grows only with a version bump" rule, not a curation-time patch; or (2) if the row is genuinely
one-off, author a curation override file for it following the `option-overrides.json`/
`equipment-overrides.json` precedent above — not yet built, because nothing has needed it yet. See
`docs/follow-ups.md` for the open item tracking the vocabulary-widening path.

## Reading the two new report-only loadout figures (007)

`loadout.rendering_equivalence` and `loadout.item_constraints` join `loadout.default_equipment` in
the `coverage` block, reported every build with a `threshold_percent` of `0` on every release — that
is correct, not a placeholder: neither is in the ratcheted-key tuple, and adding one there is the
entire implementation of a future decision to ratchet it (`docs/configuration.md`'s
`WGC_EQUIVALENCE_CHECK_ENABLED` row; plan.md research D7).

- **`loadout.rendering_equivalence`** — `matched / (matched + mismatched)`, **excluding**
  `not_compared` outcomes from both the numerator and the denominator entirely (`pipeline/validate/
  coverage.py`'s `loadout_coverages`, research D7): a datasheet nobody could compare must not move
  the proportion either way. `not_compared` is reported beside it as its own count,
  `loadout.rendering_equivalence_not_compared`, whose `resolved`/`total` are deliberately the same
  number — its own `ratio_percent` is therefore always `100` by construction and is **not** the
  figure to read from that row; the raw count is. **Always read the two together**: a matched
  proportion computed only over what was compared can look stable while the compared population
  itself shrinks or grows underneath it, and the `not_compared` count is what makes that movement
  visible. `wh40k-11e-2026-08-3` reports 388 matched of 2,587 compared (15.0%) alongside 1,525
  `not_compared` — most of the check's first-release population has not been compared at all yet,
  which is a statement about how much of the corpus the check currently reaches, not about how well
  the rendering agrees with the card where it does reach.
- **`loadout.item_constraints`** — of the datasheets **stating** a restriction
  (`item_constraints_stated_datasheets`, the row's own `total`), the proportion whose restrictions
  all resolved. On a release where nothing has resolved at all (`wh40k-11e-2026-08-3`, per the
  section above — zero real rows matched the vocabulary), this figure's denominator is itself zero
  and it reads as `100%` by the same "no attempts, nothing failed" convention `LoadoutCoverage`
  applies uniformly — not evidence the feature is complete, only that nothing has failed yet because
  nothing has been attempted.

Both are visible as **trends** from their first release onward, per `plan.md`'s Operational
readiness gate — read them release over release, not as a single snapshot.

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
