<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Recorded the T160 clean-checkout
     quickstart validation: every §1-§7 command actually run against a fresh clone and venv, one
     real defect found and fixed, and what was and was not exercised live and why. -->
# T160 — clean-checkout quickstart validation

`specs/002-rules-data-pipeline/quickstart.md` (in `WargameCompanion`) walks a curator through
bootstrap, local runs, the curator loops, publishing, withdrawal, and the app's CI fixture. This
records running its §1-§7 commands for real, against a genuinely clean checkout, and what was
corrected.

## Setup (§1)

```
git clone <wargame-rules-data> /c/tmp/qsclean2
cd /c/tmp/qsclean2
python -m venv .venv
.venv/Scripts/python.exe -m pip install -e ".[dev]"
.venv/Scripts/python.exe -m pytest -q
```

Result: clean venv, `pip install -e ".[dev]"` succeeds, **642 passed** offline (no network —
`tests/conftest.py`'s socket guard would fail anything that opened one). `.venv/Scripts/rules-
pipeline.exe --help` also confirmed the console-script entry point itself resolves correctly, not
just `python -m pipeline.cli`, since §3 onward uses the bare `rules-pipeline` form.

(First clone attempt used a deeply nested scratch path and hit Windows' `MAX_PATH` on a long
fixture path under `fixtures/disagreements/previous/...` — an environment artifact of the chosen
temp location, not a repository defect; re-cloning to a short path (`/c/tmp/qsclean2`) resolved
it. Noted here only so it isn't mistaken for a real finding.)

## §3 Local runs — one real defect found and fixed

Ran every documented command:

| Command | Result |
|---|---|
| `rules-pipeline build --offline --fixtures fixtures/sample --rules-version-id mfm-2026-06` (as originally documented) | **exit 41**, `SRC-STRUCTURE-CHANGED` — see below |
| `rules-pipeline build --offline --fixtures fixtures/minimal --rules-version-id mfm-2026-06` | exit 20 (advisory only) — builds cleanly |
| `rules-pipeline validate --offline` (no `--fixtures`, fresh clone, no prior build) | exit 60, `no curated tree at .../data/wh40k-11e; run 'build' first` — correct, expected behaviour for a repository with nothing published yet, not a defect |
| `rules-pipeline build --offline --fixtures fixtures/minimal --rules-version-id fixture-minimal` (§7) | exit 20, bundle + report written — matches §7's description exactly |

**Defect found**: quickstart §3 presented `--fixtures fixtures/sample` as "the normal development
loop" example. `fixtures/sample` deliberately ships a page with an unfilled `<template>`
placeholder (task T041, research D10) so `tests/unit/test_mfm_swap_replay.py` can assert the
structural-change failure path — building it always exits `41` by design. Presenting it as the
everyday-loop example was simply wrong: a curator following the quickstart verbatim on a clean
checkout would hit a failure on their very first command and have no way to know it was
intentional. **Fixed** in `specs/002-rules-data-pipeline/quickstart.md`: the example now uses
`fixtures/minimal` (which does build cleanly), with a short note distinguishing the two fixture
sets' purposes so the next reader who does reach for `fixtures/sample` understands why it fails.

`rules-pipeline detect` (§3, "against the real site") and the live `rules-pipeline build
--rules-version-id mfm-2026-06 --since mfm-2026-03` (§3, "against the real sources") were **not**
run live in this validation — see `docs/verification/timing.md`'s "Why not a live measurement"
section for the two reasons (no `WGC_DETAIL_SOURCE_URL`, and the same live-fetch constraint this
session applied elsewhere), which apply identically here. Both commands' argument shapes are
covered by `tests/contract/test_cli_surface.py` regardless.

## §4 Curator loops

Not independently re-verified beyond what the existing test suite already covers (`curation/`
schema validation, `unit-map.json`/`resolutions.json` behaviour — `tests/unit/`,
`tests/reconcile/`) — §4 is a set of editorial procedures, not commands with an exit code, and
nothing in it referenced a file or command that this validation's other steps didn't already
exercise or find correct.

## §5 Publishing and §6 Withdrawal

Already exercised **live**, for real, in earlier verification work this validation deliberately
did not repeat: `docs/verification/approval-rehearsal.md` (task T122) dispatched a real
`publish.yml` run against the live `prerelease` environment and confirmed the approval-gate flow
§5 describes; `docs/verification/withdrawal-rehearsal.md` (task T145) timed a real `withdraw.yml`
dispatch. Both documents' commands match what §5/§6 currently document — `commit_sha` /
`expect_sha256` for `publish.yml`, `rules_version_id` / `reason` / `channel` for `withdraw.yml` —
confirmed by re-reading both workflows' `workflow_dispatch.inputs` blocks against the quickstart
text as part of this validation. No divergence found; no re-dispatch performed, to avoid
duplicating rehearsal evidence that already exists.

## §7 App CI fixture

Covered above — `fixtures/minimal` builds cleanly under exactly the command §7 documents.

## §8 Resolved decisions

Prose-only, no commands to run; skimmed against the current `pipeline/models/curated.py` and
`pipeline/build/bundle_emit.py` for R2 (`copy_index_min`) and R10 (JSON, not SQLite) and found
consistent with what §8 states.

## Cleanup

`/c/tmp/qsclean2` (and an earlier abandoned nested-path clone attempt) were scratch clones used
only for this validation and were not committed anywhere; removed after this document was
written.
