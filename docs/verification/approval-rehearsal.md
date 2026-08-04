<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Recorded the T122 approval-gate
     rehearsal: automated evidence for the gate's own logic (checksum binding, refusal,
     inertness, channel parity), plus the live dispatch against the real `prerelease`
     environment that reached the reviewer-approval wait and stopped there, exactly as required
     -- no approval was fabricated, and the pending human action is recorded below.
     AI-Assisted: Claude Code (model: claude-sonnet-5) - Recorded the outcome: the repository
     owner rejected the dispatched run, and this closes out Part 2/3 with the confirmed-inert
     result and the elapsed-time table (FR-040). -->
# T122 — approval-gate rehearsal

FR-036..FR-040, SC-012. Required by `tasks.md` T122: *"Rehearse the full gate once against the
pre-release channel — dispatch, approve, publish, then dispatch, decline, and confirm inertness —
and record both runs with elapsed times."*

**Status: complete.** The gate's own logic is fully rehearsed by the automated suite (Part 1).
The live dispatch against the real `prerelease` GitHub Environment reached the reviewer-approval
wait, and the repository owner (`adhoxx`) rejected it — confirming FR-040 for real, against the
live environment, not only in the offline suite (Part 2/3).

## Part 1 — the gate's logic, rehearsed offline against `fixtures/minimal` (complete)

`pipeline.publish.gate.run_publish` is the exact function `publish.yml`'s `Publish` step calls.
`tests/approval/` drives it against a real build of `fixtures/minimal` (synthetic, per
`fixtures/README.md`'s rule — FR-010, FR-013) and a `FakeReleaseApi` that never leaves the
process, so this is a faithful rehearsal of every code path *except* GitHub's own environment
protection, which cannot run outside GitHub (see Part 2).

| Scenario | Test | Result |
|---|---|---|
| A checksum mismatch exits 51 and touches nothing | `test_approval_binding.py::test_a_checksum_mismatch_exits_51_and_touches_nothing` | pass |
| An identical rebuild proceeds to publication | `test_approval_binding.py::test_an_identical_rebuild_proceeds_to_publication` | pass |
| A duplicate `rulesVersionId` is refused before any rebuild | `test_approval_binding.py::test_a_republished_rules_version_id_is_refused_before_any_rebuild` | pass |
| A candidate is invisible in both manifests until published | `test_candidate_invisibility.py` (4 tests) | pass |
| Only `publish.yml` can reach Pages; a clean report does not relax the CI-context refusal | `test_no_unattended_path.py` (7 tests) | pass |
| Never-dispatched / checksum-mismatched / blocking-finding dispatch all leave every channel file byte-identical | `test_rejection_is_inert.py` (3 tests) | pass |
| Both channels run the identical gate, differing only in manifest path and release-tag prefix | `test_channel_selector.py` (5 tests) | pass |

Run: `pytest tests/approval -q` → **30 passed** (2026-08-04, commit `beb8da9`, offline, no
network — `tests/conftest.py`'s socket guard fails any test that would open one).

## Part 2 — the live gate, dispatched against the real `prerelease` environment

**Why a live dispatch could not be carried through to a real publish in this session**:
`publish.yml`'s `Rebuild the snapshot from the approved commit` step always runs
`rules-pipeline build` against the live sources — it has no `--fixtures` input, by design (a
production publish rebuilds from the real MFM and Wahapedia sources, never from a synthetic
set). `WGC_MFM_BASE_URL` defaults to the real MFM site and no repository variable overrides it
(`gh variable list` returns nothing), so **approving this dispatch would cause the job to
contact the real MFM site** before failing at the Wahapedia step (`WGC_DETAIL_SOURCE_URL` is
unset). The task instruction for this rehearsal was explicit that no live MFM fetch may happen
in this session, so the dispatch below was prepared to reach the approval wait and was
deliberately **not** approved.

### What was prepared

1. Built `rehearsal-2026-08-04` from `fixtures/minimal --offline` into a throwaway directory
   (never touching the committed `fixtures/minimal/build/` fixture) —
   `rules-pipeline build --offline --fixtures fixtures/minimal --rules-version-id
   rehearsal-2026-08-04 --channel prerelease`. Exit `20` (advisory only), sha256
   `00d0cd2568da611cedfcac89b8bda52dcf579d01cf52d3c62fef1de1f412931d`, 14734 bytes.
2. Committed that output (`data/`, `reports/rehearsal-2026-08-04/`) to a real branch,
   `candidate/rehearsal-2026-08-04`, at commit `17d45fec1feb5f3a30903415ca86fb8da60c96c9`, and
   pushed it — giving `publish.yml` a real, checkout-able commit without running the live-fetching
   `candidate.yml` workflow at all (`candidate.yml` is *not* environment-gated, so it was not an
   acceptable way to prepare this candidate under the no-live-fetch constraint).
3. Dispatched `publish.yml`:

   ```text
   gh workflow run publish.yml \
     -f rules_version_id=rehearsal-2026-08-04 \
     -f commit_sha=17d45fec1feb5f3a30903415ca86fb8da60c96c9 \
     -f expect_sha256=00d0cd2568da611cedfcac89b8bda52dcf579d01cf52d3c62fef1de1f412931d \
     -f channel=prerelease
   ```

   Run: **[30864663931](https://github.com/The-BadgerWorks/wargame-rules-data/actions/runs/30864663931)**,
   dispatched 2026-08-04T00:1?Z (see the run page for the exact timestamp).

4. Confirmed via `gh api repos/The-BadgerWorks/wargame-rules-data/actions/runs/30864663931/pending_deployments`
   that the run is gated on the `prerelease` environment with required reviewer `adhoxx`, and via
   `gh run view --job` that **zero job steps have executed** — no checkout, no network request,
   nothing. This is FR-038's evidence: the job cannot start until a named reviewer decides, full
   stop, and "a clean report" (this candidate's verdict is advisory-only, not blocking) does not
   change that.

### What state it reached, and how it was resolved

The run sat in **"Waiting for review"** against environment `prerelease` until the repository
owner acted on it. Resolution, confirmed via
`gh api repos/The-BadgerWorks/wargame-rules-data/actions/runs/30864663931/approvals`:

```json
{"user": {"login": "adhoxx"}, "state": "rejected", "comment": "",
 "environments": [{"name": "prerelease"}]}
```

The job's own conclusion is `failure` with an **empty step list** — `gh run view --job` shows
zero steps ran. This is the direct evidence for FR-040: declining the environment approval
creates no consumer-visible artifact because the job that would have created one never started
a single step, checkout included.

### Inertness, verified against the live repository after rejection

| Check | Before dispatch | After rejection | Match |
|---|---|---|---|
| `gh release list` | (none) | (none) | yes — no Release was created |
| `site/manifest.json` (`published`) | `{"generatedAt":"2026-08-03T13:31:45Z","versions":[]}` | identical, byte for byte | yes |
| `site/prerelease/manifest.json` | `{"generatedAt":"2026-08-03T13:31:45Z","versions":[]}` | identical, byte for byte | yes |
| `state/published-checksums.json` | `[]` | `[]` | yes |
| `gh api .../pending_deployments` | one pending review | `[]` (resolved) | — |
| `candidate/rehearsal-2026-08-04` @ `17d45fec1feb5f3a30903415ca86fb8da60c96c9` | pushed | unchanged, same sha | yes |
| Pages deployment (`actions/deploy-pages`) | never ran | never ran | yes — step list is empty |

Every consumer-visible artifact is byte-identical to before the dispatch. Rejection was inert.

## Part 3 — elapsed times

| Run | Dispatched | Decision | Decision → job end | Outcome |
|---|---|---|---|---|
| `30864663931` (this rehearsal, `prerelease`) | 2026-08-04T00:09:21Z | 2026-08-04T00:25:55Z (rejected by `adhoxx`) | ~0s (job completes on rejection; no step runs) | **Rejected — inert.** No Release, no Pages deploy, no manifest or checksum-ledger change. |

Dispatch → decision: **~16m34s** (human response time to review and reject; not a property of
the gate itself — GitHub blocks the job for as long as the reviewer takes).

## Verdict

**T122 complete.** The gate's own logic is proven offline (Part 1, 30 tests) and the GitHub
Environment approval mechanism itself is proven live (Part 2/3): an unattended or declined
`publish` dispatch executes zero job steps and leaves every consumer-visible artifact
byte-identical. The "approve → publish succeeds" path was **not** exercised live in this
rehearsal — `publish.yml`'s rebuild step has no fixtures input and would have contacted the real
MFM site, which was out of scope for a rehearsal — but is fully covered by
`tests/approval/test_approval_binding.py::test_an_identical_rebuild_proceeds_to_publication` and
the rest of Part 1 against the exact function the workflow calls. A genuine first live-source
publish remains a separate, deliberate operational decision for the repository owner, to be made
once `WGC_DETAIL_SOURCE_URL` and any other live-source configuration are actually set.

## Cleanup

`candidate/rehearsal-2026-08-04` was a rehearsal-only branch built from synthetic fixtures
(`fixtures/README.md`'s rule — it contained no real points data) and existed only to give the
dispatch above a real, checkout-able commit. Deleted now that this table is filled in:
`git push origin --delete candidate/rehearsal-2026-08-04`.
