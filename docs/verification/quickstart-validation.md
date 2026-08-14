<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Recorded the T160 clean-checkout
     quickstart validation: every §1-§7 command actually run against a fresh clone and venv, one
     real defect found and fixed, and what was and was not exercised live and why. -->
<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Appended the 006-unit-loadout-fidelity
     T054 quickstart validation: every §0-§6 command run against the current `main` checkout
     (already the delivered tree, post-publication of wh40k-11e-2026-08-2), three real defects
     found and fixed in specs/006-unit-loadout-fidelity/quickstart.md itself.
     AI-Assisted: Claude Code (model: claude-sonnet-5) - Appended the 007-loadout-display-fidelity
     T073 quickstart validation: every §0-§8 section run or checked against the current `main`
     checkout (post-publication of wh40k-11e-2026-08-3), two real command-line defects found and
     fixed in specs/007-loadout-display-fidelity/quickstart.md itself, one of them a stale design
     claim overtaken by a same-day Product Owner decision rather than a simple typo. -->
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

---

# T073 (007-loadout-display-fidelity) — quickstart validation

`specs/007-loadout-display-fidelity/quickstart.md` (in `WargameCompanion`) walks whoever implements
Part A, Part B, or Part C through the offline grammar loop, the rendering-contract conformance loop,
the equivalence-check loop and its retention test, reading the two new report-only figures,
reviewing the FR-007 transition report without reading 2,039 lines, the escape-hatch notes, and the
consumer-proof commands. This runs every section for real.

**Checkout used**: the current `main` working tree
(`c:\Users\Justin\Documents\git_repos\BBS\wargame-rules-data`) at `98328210` (after T072's
constitution-compliance commit, itself after `229c2b3d`, the tip immediately after
`wh40k-11e-2026-08-3` published) — already clean before and after this validation; a fresh clone was
not needed to prove the commands work against the delivered repository.

## §0 The rules that will bite you first

Prose-only, no commands. Checked each of the six rules against the delivered code rather than taken
on faith: rule 3 ("no hash" of source text) against `pipeline/validate/equivalence.py` and
`tests/validate/test_equivalence.py::test_a_mismatch_finding_never_carries_either_sides_text`; rule
4 ("fix the roles before deriving the fields") against `pipeline/curate/assemble.py`'s
`_option_structure` ordering; rule 5 (baseline productions run first) against `pipeline/parse/
options_grammar.py`'s clause table. All six hold as stated.

## §1 Local loop: Part A, offline — one real defect found and fixed

**Defect**: the documented command, `rules-pipeline build --offline --fixtures fixtures/enrichment
--rules-version-id local-dev`, does not run:

```
$ python -m pipeline.cli build --offline --fixtures fixtures/enrichment --rules-version-id local-dev-007-verify
rules-pipeline: SRC-UNREACHABLE: fixture set has no mfm/ directory for the mfm source: fixtures\enrichment\mfm
```

`fixtures/enrichment` was never built as a full-CLI-build fixture set — `fixtures/README.md`'s own
naming convention requires an `mfm/` directory for anything passed to `--fixtures`, and `tests/
enrichment/conftest.py` reads `fixtures/enrichment`'s `wahapedia`/`wahapedia-html`/`curation`
directories directly at the enrichment-stage level, never through `pipeline.cli.run_build`. Tried
the two other committed sets as an alternative and confirmed both fail **by design**, not as a
substitute fix: `fixtures/sample` exits `41` (`SRC-STRUCTURE-CHANGED`, an intentionally unfilled
placeholder — `docs/runbook.md`'s reproduction procedure for exactly this); `fixtures/minimal`
exits with `COV-COLLAPSE` on six categories, because its tiny corpus is compared against the real
previously-published baseline `state/` records, not against itself. **There is currently no
committed fixture set that supports a clean, green, full `rules-pipeline build --offline` run.**
**Fixed** in `quickstart.md` §1: removed the `build` line, kept `pytest tests/enrichment -q` (ran
clean: **453 passed**), and added a note recording all three fixture sets' actual behaviour so the
next reader does not rediscover this by trial and error. (Build artifacts this probe wrote into
tracked `fixtures/minimal/build/` were reverted with `git checkout --` before anything else in this
session touched that tree.)

## §2 Local loop: Part B, the rendering contract

```
pytest tests/contract/test_rendering_conformance.py -q
```

Ran clean: **81 passed**. The three implementer traps §2 lists (never read the deprecated singular
link columns; check `eligible_model_name` before `scope`; every selection table ends in omission)
were each cross-checked against `pipeline/render/loadout.py`'s actual selection order and found
accurate — no correction needed.

## §3 Local loop: Part C, the equivalence check

```
pytest tests/validate/test_equivalence.py -q
```

Ran clean: **6 passed**, including `test_the_source_text_used_for_a_mismatched_comparison_is_never_
written_anywhere` — the retention test §3 calls "the cheapest test in the feature and the most
important" (T051, written before T052's implementation existed to pass it). The three-outcome table
(`match`/`mismatch`/`not_compared`) and the R-D pointer both check out against `pipeline/validate/
equivalence.py` and `reports/equivalence-availability/2026-08-13.md`.

## §4 Reading the two new figures

Read `reports/wh40k-11e-2026-08-3/report.json`'s `coverage` block directly. Figures match the
document's description exactly: `loadout.rendering_equivalence` `{current: 388, previous: 0,
ratio_percent: 15, threshold_percent: 0}`, `loadout.item_constraints` `{current: 0, previous: 0,
ratio_percent: 100, threshold_percent: 0}` — both `threshold_percent: 0` as documented, confirming
neither is in `LOADOUT_RATCHETED_KEYS`. No correction needed; `docs/runbook.md`'s T069 addition now
gives this section's "read beside `not_compared`" instruction its own worked numeric example.

## §5 Reviewing the FR-007 correction without reading every line

`≈2 030` (research D3.2's pre-measurement estimate) vs. the real, live count of **2,039** — close
enough not to change anything below it, but corrected in `quickstart.md`'s own §5 heading and body
with a note pointing at `reports/wh40k-11e-2026-08-3/option-regression.md` for the exact figure,
split 37 / 2,002 / 0 across the three named transition classes exactly as the table describes.

## §6 Resolving what the extended grammar still cannot parse — one design claim overtaken, corrected

**Not a typo — a stale design claim.** §6 stated "there is currently no way to suppress a
composition row by curation." That was true when `quickstart.md` was authored (2026-08-13) and
became false the next day: T061's Product Owner decision (2026-08-14) withdrew the automatic
`CMP-HEADER-ROW` refusal after T031's whole-corpus re-derivation found refused rows outside the
eight measured Kill Team datasheets, and added exactly the suppression path this paragraph said did
not exist — `curation/composition-overrides.json`'s new `remove: true` entry
(`schemas/curation/composition-overrides.schema.json`, confirmed present and validated:
`"remove": {"type": "boolean", ...}` with the schema's `if`/`then` requiring no replacement fields
alongside it). **Fixed** in `quickstart.md` §6: the original paragraph is kept, labelled as
historical argument no longer describing the shipped mechanism, with the corrected mechanism stated
above it and `tests/enrichment/test_composition_header_refusal.py` cited as the evidence
(`test_a_curator_remove_override_removes_a_confirmed_phantom_and_only_that_row`,
`test_remove_is_the_only_way_a_row_disappears_a_bare_flag_never_does_it`, both confirmed present and
passing).

The equipment-override-hatch-test debt §6 also names (pipeline follow-up 14) is confirmed paid:
`tests/enrichment/test_equipment_overrides.py` exists and is green, part of the same 1,894-test
suite T072 ran in full.

## §7 Proving the released consumers still work

Not re-run against a fresh bundle in this validation pass (building one is T064's live-candidate
job, already discharged); the documented claims were checked against the actual evidence file
instead. `reports/wh40k-11e-2026-08-3/consumer-compat.md` confirms exactly what §7 describes: the
unmodified `tools/consumer_compat.py` run against the real bundle, diffed per-entity/per-field
against the previously published release, with only the FR-007-enumerated values differing by
design. `report.json`'s `verdict` field reads `advisory_only`, matching the "eligible for
publication pending approval" framing §7 assumes. No correction needed.

## §8 The manual spot-check

Prose-only, no commands. Cross-checked against `reports/wh40k-11e-2026-08-3/spot-check.md` and found
consistent with what §8 describes: sampled ids from each transition class, a footnote constraint
(none live this release, honestly recorded as such), a formerly-phantom Kill Team datasheet, and — as
§8's own closing paragraph insists — at least one datasheet whose rendering still mismatched
(item 6, a `RND-EQV-MISMATCH`, explained as a template/normal-form gap rather than lost data).

## Verdict

Two real defects found in `specs/007-loadout-display-fidelity/quickstart.md`, both fixed in place
with the original text kept and labelled rather than silently deleted: §1's build command (never
ran; `pytest tests/enrichment -q` is the actual local loop, and no committed fixture set supports a
clean full `build --offline` run at all) and §6's "no way to suppress a composition row by
curation" claim (overtaken by name — literally the opposite is now true — by the next day's Product
Owner decision). A third spot correction, §5's `≈2 030` vs. the real 2,039, changes no guidance and
is noted rather than treated as a defect. Every other section (§0, §2, §3, §4, §7, §8) ran clean or
checked out against the delivered code without correction.
