<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Recorded the T122 approval-gate
     rehearsal: automated evidence for the gate's own logic (checksum binding, refusal,
     inertness, channel parity), plus the live dispatch against the real `prerelease`
     environment that reached the reviewer-approval wait and stopped there, exactly as required
     -- no approval was fabricated, and the pending human action is recorded below. -->
# T122 — approval-gate rehearsal

FR-036..FR-040, SC-012. Required by `tasks.md` T122: *"Rehearse the full gate once against the
pre-release channel — dispatch, approve, publish, then dispatch, decline, and confirm inertness —
and record both runs with elapsed times."*

**Status: partially complete, one step pending a human action.** The gate's own logic is fully
rehearsed by the automated suite (below). The live dispatch against the real `prerelease`
GitHub Environment reached the reviewer-approval wait and was deliberately left there — this
document was written *before* any decision was made on it, so it could record the state honestly
rather than after the fact.

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

### What state it reached, precisely

The run is sitting in **"Waiting for review"** against environment `prerelease`. No step has
run. Nothing has been written anywhere. This is the terminal state this session left it in.

### What the human must do

Reviewer: **adhoxx**. Run URL:
**https://github.com/The-BadgerWorks/wargame-rules-data/actions/runs/30864663931**

Two ways to complete this rehearsal, and they record different halves of T122:

- **Reject the deployment** (Actions UI → this run → *Review deployments* → Reject, or decline).
  This is unconditionally safe — no step runs on rejection — and completes T122's "dispatch,
  decline, confirm inertness" half for real, against the live environment rather than only in
  the offline suite. After rejecting, re-run the `_digests`-style check by hand (or just confirm
  in the UI) that `site/manifest.json`, `site/prerelease/manifest.json`, and
  `state/published-checksums.json` on `main` are unchanged — they will be, since this job is the
  only writer of any of them and it never started.
- **Approve the deployment.** This completes the "dispatch, approve, publish" half for real, but
  — as stated above — the `Rebuild the snapshot` step will then contact the real MFM site and is
  very likely to fail at the Wahapedia step, since no live detail-source URL is configured yet.
  That is expected, not a bug in this candidate: it is the reason this session did not approve
  it. If the intent is a genuine first live-source publish rather than a rehearsal, that is a
  deliberate operational decision for the repository owner to make outside this rehearsal's
  scope, once `WGC_DETAIL_SOURCE_URL` and any other live-source configuration are actually set.

Whichever action is taken, update the table below with the elapsed time (dispatch → decision →
job completion) and the observed outcome, and only then should T122 be marked complete.

## Part 3 — elapsed times (fill in after the human decision above)

| Run | Dispatched | Decision | Decision → job end | Outcome |
|---|---|---|---|---|
| `30864663931` (this rehearsal, `prerelease`) | 2026-08-04 | *pending* | *pending* | *pending* |

## Cleanup

`candidate/rehearsal-2026-08-04` is a rehearsal-only branch built from synthetic fixtures
(`fixtures/README.md`'s rule — it contains no real points data). Delete it once this document's
table above is filled in: `git push origin --delete candidate/rehearsal-2026-08-04`.
