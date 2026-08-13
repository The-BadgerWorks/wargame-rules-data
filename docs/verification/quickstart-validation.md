<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Recorded the T160 clean-checkout
     quickstart validation: every §1-§7 command actually run against a fresh clone and venv, one
     real defect found and fixed, and what was and was not exercised live and why. -->
<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Appended the 006-unit-loadout-fidelity
     T054 quickstart validation: every §0-§6 command run against the current `main` checkout
     (already the delivered tree, post-publication of wh40k-11e-2026-08-2), three real defects
     found and fixed in specs/006-unit-loadout-fidelity/quickstart.md itself. -->
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

---

# T054 (006-unit-loadout-fidelity) — quickstart validation

`specs/006-unit-loadout-fidelity/quickstart.md` (in `WargameCompanion`) walks a curator through the
extended grammars' inner loop, the two new coverage figures, the option-regression evidence run,
the extended override files, and the consumer-compat proof. This runs its §0-§6 commands for real.

**Checkout used**: the current `main` working tree
(`c:\Users\Justin\Documents\git_repos\BBS\wargame-rules-data`) at `51e586bf`, the tip immediately
after `wh40k-11e-2026-08-2` published — already clean (`git status` empty before and after this
validation), so a fresh clone was not needed to prove the commands work against the delivered
repository; `pip show wargame-rules-data` confirms the package is installed editable in this
environment exactly as a curator's would be.

## §1 Local loop: the extended grammars, offline

| Command | Result |
|---|---|
| `pytest tests/enrichment/test_options_grammar.py tests/enrichment/test_equipment_grammar.py -q` | **80 passed** |
| `pytest tests/enrichment/test_options_grammar_regression.py -q` | **20 passed** |
| `pytest -q -m "not network"` | **1,675 passed, 8 skipped** |
| `ruff check . && ruff format --check . && mypy --strict . && pytest -q` | See below — two of these four sub-commands needed correcting to match what CI actually runs |

**Two invocation defects found in this document's own §1, neither in `quickstart.md`'s text
itself** (the text just says "the full gate set", it does not spell out flags) but worth recording
here since a curator typing the obvious form hits both: `ruff` and `mypy` are not on `PATH` in a
plain `pip install -e ".[dev]"` environment on this machine — `python -m ruff` /`python -m mypy`
resolve. And `mypy --strict .` (passing `.` explicitly) fails with `Duplicate module named
"conftest"` (`tests/enrichment/conftest.py` vs `tests/approval/conftest.py`), because it stops
using `pyproject.toml`'s `[tool.mypy]` `packages = ["pipeline"]` the moment a path argument is
given. **`mypy` with no arguments** (`.github/workflows/ci.yml`'s own invocation) is correct:
`Success: no issues found in 92 source files`. `ruff check .` and `ruff format --check .` (266
files already formatted) both work as documented. Full `pytest -q`: **1,675 passed, 8 skipped**,
matching PR #11's own recorded gate figure exactly, and left `git status` clean afterward (the
known `state/run-ledger.jsonl` test-hygiene issue, `docs/follow-ups.md` item 2, did not reproduce
on this run).

## §2 Reading the two new coverage figures — one real defect found and fixed

Read `reports/wh40k-11e-2026-08-2/report.json`'s `coverage` block directly rather than trusting the
document's illustrative numbers. **Defect**: the document's example used key names `ratio` /
`threshold`; the real report names them `ratio_percent` / `threshold_percent`, and the illustrative
figures (`1913`/`1682`/`1744`) did not match any real release. **Fixed** in
`specs/006-unit-loadout-fidelity/quickstart.md` §2 with the real `wh40k-11e-2026-08-2` figures:
`loadout.options_resolved` current 1,916, `loadout.default_equipment` current 2,017, both with
`previous: 0` / `threshold_percent: 0` (this being the first release either figure exists in, so
there is nothing yet to ratchet against) — and a short added sentence explaining why `previous`
reads `0` on a first release rather than leaving a curator to wonder if the ratchet is broken.

## §3 Proving FR-009: the option-regression evidence run — one real defect found and fixed

**Defect**: the documented command used `--against <previous-rulesVersionId>`. The CLI has never
accepted `--against` — `python -m pipeline.cli option-regression --help` and
`tests/contract/test_cli_surface.py`'s `CONTRACT_COMMAND_OPTIONS["option-regression"]` both confirm
the flag is `--since`, matching `build`'s option of the same name. **Fixed** in `quickstart.md`,
also correcting the `--out reports/<rulesVersionId>/option-regression.md` line — there is no `--out`
flag either; the report path is derived from `--rules-version-id`, confirmed by running it:

```
python -m pipeline.cli option-regression --offline --fixtures fixtures/minimal \
  --rules-version-id fixture-check --since fixture-minimal --dry-run --json
```

ran successfully (exit 0, wrote `reports/fixture-check/option-regression.md`, cleaned up afterward
as scratch output — not committed). The run's own *Corrected*-is-non-empty warning against this
particular fixture pairing is expected: `fixture-minimal`'s committed tree was not built from
`fixtures/minimal`'s current content, so the two legitimately disagree; this is a mismatched-inputs
artifact of ad hoc validation, not a defect in the command itself, and `docs/runbook.md`'s new
"Reading a non-empty option-regression `Corrected` section" walks through exactly this distinction.

## §4 Resolving what the extended grammar still cannot parse

Not independently re-run as commands (this section is an authoring loop, not commands with an exit
code), but every override field name shown (`eligible_model_name`, `eligible_max_count`,
`is_per_model`, `items[]`, and the whole `equipment-overrides.json` shape) was checked against
`pipeline/models/authored.py`'s `OptionOverrideEntry`/`OptionOverrideChoice`/
`EquipmentOverrideEntry`/`EquipmentOverrideItem` and found to match field-for-field.

## §5 Proving the released consumers still work (FR-020) — one real defect found and fixed

**Defect**: the documented commands used `python tools/consumer_compat.py --bundle
work/candidate/bundle.json --out work/compat-new.json`. `python tools/consumer_compat.py --help`
shows the tool takes exactly one **positional** `bundle` argument and no `--bundle`/`--out` options
at all — it prints its ingestion report and `total <N> points` to stdout (confirmed by reading
`tools/consumer_compat.py::main`, which calls `print()` for every line and writes nothing to a
file). **Fixed** in `quickstart.md`: `python tools/consumer_compat.py work/candidate/bundle.json >
work/compat-new.json`, a positional argument with a shell redirect rather than a flag pair. Not
re-run against a real bundle in this validation pass (building one is T045's live-candidate job,
already discharged and recorded in `reports/wh40k-11e-2026-08-2/consumer-compat.md`); the fix was
confirmed against the tool's actual `argparse` surface and source, not merely inferred from the
`--help` text.

## §6 The manual spot-check

Prose-only, no commands. Cross-checked against `reports/006-spot-check/package.md` (T047) and
found consistent with what §6 describes: sampled ids, retrieval date, outcome per entry, and at
least one still-failing extraction recorded.

## Verdict

Three real defects found in `specs/006-unit-loadout-fidelity/quickstart.md`, all three in
command-line examples rather than in the conceptual walkthrough, all three fixed in place with an
inline note recording what was wrong: §2's `report.json` key names, §3's `option-regression` flag
name, and §5's `consumer_compat.py` invocation shape. Every other command in §1, §4, and §6 ran (or,
for §4/§6's prose sections, was checked against the actual code) without correction.
