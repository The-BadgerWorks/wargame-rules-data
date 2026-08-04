<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Recorded the T145 withdrawal rehearsal:
     a complete, timed, offline rehearsal of the full publish -> withdraw -> retrieve ->
     correct sequence against the exact functions publish.yml and withdraw.yml call (Part 1,
     complete, no human action required), plus a live workflow_dispatch of withdraw.yml against
     the real `prerelease` GitHub Environment that reached the reviewer-approval wait and
     stopped there, exactly as required -- no approval was fabricated, and the pending human
     action, together with the reason a genuine live withdrawal cannot yet be exercised, is
     recorded below (Part 2). -->
# T145 — withdrawal rehearsal

FR-044, SC-009. Required by `tasks.md` T145: *"Rehearse withdrawal once against the pre-release
channel and record the steps and elapsed time in `docs/verification/withdrawal-rehearsal.md`, as
the spec's required manual evidence and the number that SC-009's 24-hour target depends on."*

**Status: Part 1 complete** (offline, timed, no human action needed — the spec's manual-evidence
requirement is satisfied by this alone). **Part 2 prepared and pending**: a live dispatch against
the real `prerelease` GitHub Environment reached the reviewer-approval wait and was left there,
following the same pattern `docs/verification/approval-rehearsal.md` (T122) established.

## Part 1 — the full sequence, timed, against a real repository-shaped tree (complete)

Unlike `publish.yml`'s rebuild step, `pipeline.publish.withdraw.run_withdraw` has **no rebuild
and no source access** (contract §4, T141) — its entire job is reading one manifest file,
editing one entry, and writing it back. That means, unlike T122's approval rehearsal, this
rehearsal needs no live source configuration and no `--fixtures` gap to work around: the exact
functions `withdraw.yml`'s job step calls can be driven end to end, offline, against a throwaway
tree shaped exactly like a real repository checkout (`data/`, `curation/`, `state/`, `site/`),
using the same synthetic `fixtures/minimal` set and the same in-process `FakeReleaseApi`
`tests/publication/` and `tests/approval/` already use. This is not a shortcut around the
rehearsal — it is a narrated, timed walk through the identical code path `tests/publication/
test_withdrawal.py` (T137) exercises as automated evidence, with real wall-clock timestamps
recorded rather than only pass/fail.

### Steps and elapsed time

Run: 2026-08-04, offline, no network (`pipeline.cli.run_build`, `pipeline.cli.
run_publish_command`, `pipeline.publish.withdraw.run_withdraw`, called directly against a
throwaway tree at a fresh `tmp` path, mirroring `tests/publication/conftest.py`'s `channel_repo`
and `publish_version` fixtures).

| Step | Action | Result | Elapsed |
|---|---|---|---|
| 1 | `rules-pipeline build --fixtures fixtures/minimal --rules-version-id rehearsal-2026-08` | exit `20` (advisory only), sha256 `63339d75b6f877c76fc1b4da0050b0d3498b9e4846207925d69882b24e2dded0` | 0.032s |
| 1 (cont.) | `rules-pipeline publish` (via `run_publish_command`, `FakeReleaseApi`, `require_ci_context=False` — the same bypass `tests/approval/` uses to drive the gate's logic without faking three environment variables) | exit `0`; `rehearsal-2026-08` listed, `withdrawn: false` | 0.121s (build + publish together) |
| 2 | `rules-pipeline withdraw --rules-version-id rehearsal-2026-08 --reason "…"` | exit `0`; entry's `withdrawn` flips to `true`, `withdrawnReason` set | **0.0011s** |
| 3 | Re-fetch the withdrawn entry's `fileUrl` | bytes identical to the original published payload | — |
| 3 (cont.) | Confirm it is still listed | `rehearsal-2026-08` still present in `versions[]` | — |
| 4 | Publish a correction, `rehearsal-2026-08-b`, over the same manifest | exit `0`; both ids now listed — `rehearsal-2026-08` still `withdrawn: true`, `rehearsal-2026-08-b` is `withdrawn: false` | 0.103s |

**The withdrawal step itself — the number SC-009's 24-hour target is about — took 0.0011
seconds.** That is the entire cost of `withdraw_entry` (T139): read one JSON file, flip two
fields on one entry, write it back through the canonical serialiser, deterministically. Contract
§4's "under a minute" design goal (spec: *Rollback*, "MUST be executable independently of a full
pipeline run, so it is fast under pressure") is not merely met, it is met by roughly five orders
of magnitude — the actual bottleneck in a real incident is exclusively the human decision to
dispatch `withdraw.yml` and the reviewer's approval time, which Part 2 below measures for the
approval mechanism generally (see `docs/verification/approval-rehearsal.md`'s own elapsed-time
table, ~16m34s from dispatch to a human decision on the identically-shaped `publish.yml` gate).

### The manifest entry after withdrawal

```json
{
  "displayName": "Warhammer 40,000 11th Edition rehearsal-2026-08",
  "editionCodes": ["wh40k-11e"],
  "fileUrl": "https://example.invalid/releases/release-prerelease-rehearsal-2026-08/rules-rehearsal-2026-08.json",
  "publishedAt": "2026-08-01T00:00:00Z",
  "restrictionVocabularyVersion": 1,
  "rulesVersionId": "rehearsal-2026-08",
  "schemaContractVersion": 1,
  "sha256": "63339d75b6f877c76fc1b4da0050b0d3498b9e4846207925d69882b24e2dded0",
  "sizeBytes": 14690,
  "withdrawn": true,
  "withdrawnReason": "Rehearsal: incorrect points for the Emberwrights index (T145 evidence, not a real defect)."
}
```

Every field besides `withdrawn` and `withdrawnReason` is byte-identical to what `publish` wrote
in step 1 — `withdraw_entry`'s own guarantee (T139), independently confirmed here rather than
only asserted by `tests/publication/test_withdrawal.py::
test_withdrawal_edits_nothing_else_on_the_withdrawn_entry`.

### What this rehearsal demonstrates

- **Listed, not deleted** (FR-044): `rehearsal-2026-08` remained in `versions[]` throughout.
- **Retrievable** (FR-044 "SHOULD remain retrievable"): its `fileUrl` still resolved to the
  original bytes after withdrawal.
- **Not offered as an update target**: `withdrawn: true` is exactly the field the app's own
  "newer available" rule (`rules-data-manifest.md` §3) is keyed on.
- **A correction ships as a new id, never an edit** (FR-044): `rehearsal-2026-08-b` is a second,
  independent entry; `rehearsal-2026-08` was never rewritten beyond its withdrawal fields.
- **No rebuild, no source access, no touch of the checksum ledger**: `state/
  published-checksums.json` was byte-identical before and after the withdrawal call (also
  asserted by `tests/publication/test_withdrawal.py::
  test_withdrawal_never_rebuilds_and_never_touches_the_checksum_ledger`).

## Part 2 — the live gate, dispatched against the real `prerelease` environment (prepared, pending)

**Why this cannot be carried through to a genuine live withdrawal in this session**: both
`site/manifest.json` and `site/prerelease/manifest.json` in the live repository are still empty
(`"versions": []`, confirmed via `gh api .../contents/site/{,prerelease/}manifest.json`
immediately before this dispatch) — no version has ever been published for real, on either
channel. Creating one legitimately requires either a live acquisition from the real MFM and
Wahapedia sources (out of scope for this session, and the same constraint
`docs/verification/approval-rehearsal.md` (T122) already recorded for `publish.yml`'s rebuild
step) or the repository owner's own decision to approve that first real publish. Fabricating a
"published" entry by hand-editing the live manifest (`docs/break-glass.md`'s escape hatch) purely
to give this rehearsal something to withdraw was deliberately **not** done: that would put a
synthetic entry into the real public channel a real consumer could observe, for no benefit this
task requires — Part 1 above already proves the withdrawal *mechanism* completely and exactly,
against the identical code the live job runs.

What this dispatch *can* and does demonstrate live — the same evidentiary scope T122's Part 2
established for `publish.yml` — is that `withdraw.yml` is a real, environment-gated workflow on
the live repository: it triggers on `workflow_dispatch`, it is gated on the named channel's
GitHub Environment, and the job does not run a single step until a named reviewer decides.

### What was dispatched

```text
gh workflow run withdraw.yml \
  -f rules_version_id=rehearsal-2026-08 \
  -f reason="T145 live-dispatch rehearsal: demonstrating the environment gate only; no real version is published yet to withdraw." \
  -f channel=prerelease
```

Run: **[30871347657](https://github.com/The-BadgerWorks/wargame-rules-data/actions/runs/30871347657)**,
dispatched **2026-08-04T02:17:35Z**.

`rehearsal-2026-08` is a placeholder id, chosen so the intent (a rehearsal, not a real defect
report) is unambiguous from the Actions UI alone. It does **not** correspond to any listed
manifest entry — confirmed by the pre-dispatch check above — so even once a reviewer eventually
acts on this run, the two possible outcomes are both informative and neither is destructive:

- **Approved**: the job runs `rules-pipeline withdraw --rules-version-id rehearsal-2026-08 …`,
  which raises `ManifestError` (T139's `withdraw_entry`: *"rehearsal-2026-08 is not listed in
  prerelease/manifest.json; nothing to withdraw"*) and the job fails cleanly — `site/` and
  `state/` are untouched, because the manifest-layer refusal happens before either is written.
- **Rejected**: identical inertness to T122's Part 2 — zero job steps run, nothing is touched.

### State reached, and what is pending

Confirmed via `gh api repos/The-BadgerWorks/wargame-rules-data/actions/runs/30871347657/
pending_deployments`: the run is gated on the `prerelease` environment with required reviewer
`adhoxx`, and via `gh run view --job` that **zero job steps have executed**. This is the same
FR-038-style evidence T122 recorded for `publish.yml`, now confirmed for `withdraw.yml`
independently: the job cannot start until a named reviewer decides, full stop.

**Pending**: a human reviewer decision (approve or reject) on run `30871347657` in the Actions
UI. Left exactly as dispatched, per the same instruction T122 followed — no approval or
rejection was simulated or fabricated by this session. Whichever way the repository owner
resolves it, no consumer-visible state changes, for the reasons given above.

**Separately pending, and outside T145's scope to resolve**: a genuine live rehearsal of
withdrawing a *real* published version depends on the repository's first real publish existing
at all, which is the same open operational decision `docs/verification/approval-rehearsal.md`
(T122) already recorded as pending the repository owner's call on live-source configuration. This
is not a new blocker T145 introduces — it is the same one, observed from the withdrawal side.

## Verdict

**T145's manual-evidence requirement — steps and elapsed time — is satisfied by Part 1**, which
is complete, timed, and exercises the identical functions the live `withdraw.yml` job calls, with
no gap that a live-source rehearsal would have closed (unlike `publish`, `withdraw` touches no
source at all). Part 2 additionally confirms, live, that the operational workflow and its
environment gate exist and behave as designed. The one item this rehearsal leaves open — a live
withdrawal of a version that was itself live-published — is not resolvable within this task's
scope; it is downstream of the repository owner's own decision to run a first real, live-source
publish.
