<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Constitution compliance review and
     evidence capture for the Polish phase (task T162): re-ran plan.md's eight gates against the
     delivered repository, confirmed the Principle 5 exception's drift check, the Principle 11
     limitation's compensating controls, and the Principle 14 exception's confinement, and swept
     every file and commit landed in this phase for the required disclosure. -->
<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Appended the 006-unit-loadout-fidelity
     T053 constitution compliance review: re-ran the eight gates against the delivered repository
     after wh40k-11e-2026-08-2 published, checked each of Risks R-A through R-I against a concrete,
     opened file or passing test rather than the plan's description of intent, and swept every
     non-data file and commit in the feature's range for Principle 16 disclosure. -->
# T162 — constitution compliance review and evidence capture

`specs/002-rules-data-pipeline/plan.md`'s Constitution Check (`WargameCompanion`) recorded **PASS,
zero N/A gates, one documented Principle 5 exception, and one documented Principle 11 limitation
with a compensating control** at planning time. This re-runs the same eight gates against the
*delivered* repository, now that every user story (US1-US6) and the Polish phase (T146-T162) have
landed, and records what changed.

This work landed as direct commits to `main` (the operator's instruction for this phase), not
through a reviewed pull request, so this document is the recorded evidence in place of a PR
comment — the same role `docs/verification/approval-rehearsal.md` and the other rehearsal
documents already play for their own tasks.

## The eight gates, re-run

| Gate | Plan-time | Delivered-repository check | Result |
|---|---|---|---|
| Spec-first | PASS | `spec.md` still governs; no task landed outside its FR-/SC- numbers — every commit in this phase's history cites one | **PASS** |
| Verification | PASS | 642 tests pass offline (`pytest -q`, no network — confirmed via `tests/conftest.py`'s socket guard), `ruff check`/`ruff format --check`/`mypy` all clean, twelve verification-evidence categories all have a named test or manual doc (`specs/002-rules-data-pipeline/verification-evidence.md`, task T152 — 30/35 scenarios directly evidenced by an automated test, the remainder honestly recorded as manual-only or a genuine gap rather than papered over) | **PASS** |
| Policy/safety | PASS | T156's audit re-ran `pytest tests/ip/ -v` (31/31 passed), grepped for endorsement language (none found), and cited `pipeline/acquire/http.py`'s robots.txt-honouring and never-escalate-on-refusal behaviour by line number — `docs/verification/policy-safety-compliance.md` | **PASS** |
| Infrastructure (Principle 5 exception) | PASS with exception | See "Principle 5", below | **PASS with exception, drift check implemented but not yet live** |
| Environment | PASS | `WGC_DATA_CHANNEL` remains the only branch point; `pipeline/config.py`'s `manifest_path` property is still the single place channel selection has any effect | **PASS** |
| Security/configuration | PASS | No long-lived PAT introduced by this phase's numbered tasks. **One narrow, documented exception** was added for T148 — see "Principle 5", below, which is the same finding under a different gate | **PASS, with the same recorded exception** |
| Operational readiness | PASS | `docs/operational-readiness.md` (T157) now exists and matches the plan's description; SC-004 timing recorded analytically (T155, `docs/verification/timing.md`) rather than against a live dispatch, for reasons recorded there | **PASS** |
| Separation (Principle 11 limitation) | PASS with limitation | See "Principle 11", below | **PASS, compensating controls confirmed live** |

## Principle 5 (Infrastructure Controls) — the drift check

The plan's Infrastructure gate exception named a drift-check as the compensating control, but
left its implementation to later CI work. **T148 implements it**: `tools/check_repo_settings.py`
reads environments, branch protection, and Pages source back through the GitHub API and compares
them against the values tabulated in `docs/repo-settings.md`; `.github/workflows/settings-
drift.yml` runs it on `workflow_dispatch` and a weekly `schedule`.

**Honest status, not glossed over**: the checker is implemented and unit-tested (`tests/unit/
test_check_repo_settings.py`), but has **not yet run successfully against the live repository**,
because it depends on a repository secret (`WGC_SETTINGS_AUDIT_TOKEN`) that does not exist yet —
recorded as an open action item in `docs/follow-ups.md` §1. The compensating control is *coded
and ready*, not yet *live*. This is the same honest-limitation style `docs/repo-settings.md`
already used for the single-maintainer/no-teams finding, applied to a new fact rather than
inventing a different standard for it.

## Principle 11 (Organization of Infrastructure and Runtime Code) — the Separation limitation

Confirmed live, by direct inspection of the delivered repository rather than by re-reading the
plan's description of intent:

- `tools/check_change_classes.py` is wired into `.github/workflows/ci.yml`'s `change-class-guard`
  job (`pull_request` only, since it diffs base against head) and fails a PR touching more than
  one of `{pipeline/+tests/, data/, curation/, infrastructure}`.
- `.github/CODEOWNERS` routes all four classes to a named owner — honestly annotated, as it was at
  authoring time, with the single-maintainer limitation that makes "distinct non-author reviewer"
  not yet enforceable in practice; not silently dropped from this review.
- `.github/workflows/ci.yml` runs `actionlint` against every workflow file on every PR and push.

All three compensating controls the plan named are present and exercised by CI today, not merely
described. The underlying limitation itself — GitHub Actions workflows are self-deploying on
merge, so an infrastructure change cannot be promoted through a pipeline separate from the one it
defines — is structural and was never expected to be closed; the plan named compensating controls,
not a resolution, and that is what was verified.

## Principle 14 (Prefer Established Tools) — the `$RS` exception's confinement

Confirmed by search, not assumption: `grep -rl 'swap_replay\|SwapReplay' pipeline --include=*.py`
returns `pipeline/parse/mfm_swap_replay.py` itself (the implementation) plus `pipeline/cli.py` and
`pipeline/parse/mfm_dom.py`, both of which only *import* or *call* the replayer — neither
reimplements any part of the `$RS` swap logic. `grep -rn '\$RS' pipeline/cli.py pipeline/parse/
mfm_dom.py` returns nothing: no file outside `mfm_swap_replay.py` contains the literal marker
syntax it replays. The one documented bespoke component stays confined to the one file the plan
named for it.

## Principle 16 (AI-Assisted Content Disclosure) — full sweep of this phase's output

Swept every file changed or added between the pre-Polish commit (`10c4196`, the last US6 commit)
and the head of this phase in `wargame-rules-data`, plus every commit in that range:

- **Every** `.py`, `.md`, and `.yml` file changed or added carries an `AI-Assisted:` header in
  its first 8 lines — 24 files checked, zero misses (this document and `docs/verification/
  constitution-compliance.md`'s own commit are additional to that count, carrying the same header
  convention).
- Both touched JSON files (`curation/faction-map.json`, `schemas/curation/faction-map.schema.json`)
  follow the project's established JSON convention: the schema file (which can carry a `_comment`
  key) has its own stacked header; `faction-map.json` itself (keyed array, no natural place for a
  `_comment` without changing its shape) is documented in `curation/README.md`'s provenance
  section instead, matching how the original `faction-map.json` was documented at T074.
- **Every** commit in the range (17 in `wargame-rules-data`, 6 in `WargameCompanion`) carries both
  the `AI-Assisted-By: Claude Code (model: claude-sonnet-5)` trailer and the `Co-Authored-By:
  Claude Fable 5 <noreply@anthropic.com>` trailer — checked by parsing each commit's full message
  and asserting both strings are present, not by sampling.

No exceptions found in either direction.

## Open items carried forward (not gate failures — recorded, not hidden)

Three items from `docs/follow-ups.md` are real, named, and deliberately not folded into this
review as if resolved:

1. `WGC_SETTINGS_AUDIT_TOKEN` needs to be created by a maintainer before the Principle 5 drift
   check's first real run.
2. A pre-existing test-hygiene defect in `tests/contract/test_cli_surface.py` writes a real entry
   to the tracked `state/run-ledger.jsonl` on every `pytest` run (its guiding comment predates
   `verify`'s implementation). Reverted after every timing measurement in this phase; not fixed,
   to keep this phase's scope to what it was asked to touch.
3. `pipeline/curate/assemble.py`'s three-symbol exception in `tests/ip/test_stage_boundary.py`'s
   `KNOWN_EXCEPTIONS` is pinned exactly, not silently widenable, but not closed — a proper fix
   (a `normalize`-owned projection type) is described there as follow-up work.

## Verdict

**PASS.** All eight gates hold against the delivered repository. The plan's one documented
Principle 5 exception and one documented Principle 11 limitation are both still correctly
described, and this phase implemented the Principle 5 exception's previously-deferred compensating
control (pending one operational step — the audit-token secret — before its first live run,
recorded rather than assumed). Principle 14's bespoke-component exception remains confined to the
one file it was granted for. Principle 16 disclosure is complete across every file and commit this
phase produced, verified by direct inspection rather than by re-asserting intent.

---

# T053 (006-unit-loadout-fidelity) — constitution compliance review and evidence capture

`specs/006-unit-loadout-fidelity/plan.md`'s Constitution Check (`WargameCompanion`) recorded, at
planning time, **PASS, zero N/A gates, no new exception, the two `002`-inherited exceptions
unchanged, and two open Product Owner items (O1, O2) named rather than resolved unilaterally**.
This re-runs the same eight gates against the *delivered* repository, now that `wh40k-11e-2026-08-2`
has published (2026-08-13), and confirms Risks R-A through R-I landed the mitigations the plan
described rather than merely intended them.

## The eight gates, re-run

| Gate | Plan-time | Delivered-repository check | Result |
|---|---|---|---|
| Spec-first | PASS | `spec.md` still governs; every FR-/SC- cited in `tasks.md` traces to a numbered requirement or success criterion in it. O1 (legacy label normalisation) and O2 (the 621-vs-689 baseline) are both resolved in `plan.md`'s Open Decisions with a dated ruling, not silently dropped | **PASS** |
| Verification | PASS | Full gate green on the delivered tree: `ruff check .` clean, `ruff format --check .` — 266 files already formatted, `mypy` (packages=["pipeline"]) — 92 source files, no issues, `pytest -q` — **1,675 passed, 8 skipped**. `specs/006-unit-loadout-fidelity/verification-evidence.md` (T051) traces all 16 acceptance scenarios to a named test or the manual spot-check; one honest gap named there (the equipment-overrides escape hatch has no dedicated test — `docs/follow-ups.md` item 14) is orthogonal to the 16 scenarios, not a hole in them | **PASS** |
| Policy/safety | PASS | `tests/ip/test_ip_scan.py::test_every_loadout_field_family_is_scanned` and `::test_no_loadout_finding_quotes_the_text_that_provoked_it` confirm every new field (`itemName`, `modelName`, `eligibleModelName`) is walked by JSON pointer with no allowlist; `OPT-UNPARSED`/`EQP-UNPARSED` name `datasheet_id`/`line` only (`tests/enrichment/test_options_grammar.py::test_an_unmatched_head_is_reported_and_never_dropped`); no new upstream source — `pipeline/acquire/` untouched by this feature's own diff | **PASS** |
| Infrastructure | PASS | No new workflow, no new job. `candidate.yml` gained two coverage figures and an `option-regression.md` link in its PR body (`pipeline/report/pr_body.py`), confirmed present in `reports/wh40k-11e-2026-08-2/report.md`'s reading order. The two `002` exceptions (Principle 5 settings, Principle 11 self-deploying workflows) are unchanged and not touched by this feature | **PASS** |
| Environment | PASS | Exactly one new `CONFIG_VARS` entry landed, `WGC_RATCHET_TOLERANCE_OPTIONS` (confirmed at `pipeline/config.py:394`) — the plan's "one, and deliberately only one" note (`pipeline/config.py`'s own 006 comment block) is accurate; the considered equipment-vocabulary knob was not added because none was needed. `WGC_DATA_CHANNEL` remains the only branch point | **PASS** |
| Security/configuration | PASS | No new credential, secret, or permission. `WGC_MECHANIC_DIGEST_KEY` untouched — confirmed nothing this feature adds is authored prose subject to digesting | **PASS** |
| Operational readiness | PASS | `loadout.options_resolved` (ratcheted) and `loadout.default_equipment` (reported) both appear in `reports/wh40k-11e-2026-08-2/report.json`'s `coverage` block — confirmed live: `options_resolved` 1,916/2,084 (92%), `default_equipment` 2,017/2,084 (97%). Rollback is additive per-class (three arrays empty, four columns omitted) by construction — `pipeline/build/bundle_emit.py`'s three new arrays (lines 809-811) are populated only from `curate/assemble.py`'s `_option_structure`/`_equipment` outputs, so nothing in `bundle_emit.py` itself needs a flag for the arrays to fall back to empty | **PASS** |
| Separation | PASS | `tools/check_change_classes.py` and CODEOWNERS unchanged; `006`'s own delivery history (`git log`) shows the planned separation held in practice — grammar/schema commits, then the live candidate build (`f10a0e39`), then the T044-T047 evidence re-record (`a4d08a00`), as separate commits rather than one mixed one | **PASS** |

## Risks R-A through R-I: mitigation landed, checked against the delivered repository

| Risk | Plan's mitigation | Confirmed landed |
|---|---|---|
| **R-A** — cached corpus was ≈81% of the real one | Re-derive the taxonomy against the candidate's own live corpus before sizing the production build order | `reports/option-taxonomy/2026-08-10.md` (T002): 1,680 datasheets, 2,452 option rows, 571 `OPT-UNPARSED` (23.3%) measured live — the taxonomy-frequency ordering research D1c predicted was confirmed against this run, not the cached sample, before T016-T019/T055 were written |
| **R-B** — a new production changes a row the baseline resolved | Baseline-first ordering (structural) + additive-only decomposition + two-layer regression harness | Structural: every 006 production in `pipeline/parse/options_grammar.py` is appended after the `004` table, confirmed by reading the file's clause-table ordering. Layer 1: `tests/enrichment/test_options_grammar_regression.py` — 20 tests, green. Layer 2, live: `reports/wh40k-11e-2026-08-2/option-regression.md` (T044) — **4,338 / 4,338 option choices byte-identical** against the previously published tree; the *Corrected* section's 21 entries are all `maxChoices` populating a `004`-declared, never-emitted column (checked directly, not taken from the tasks.md summary) |
| **R-C** — a bundle item links to the wrong weapon profile | Exactly-one-match linking per item | `tests/enrichment/test_options_link.py::test_each_item_of_a_bundle_links_on_its_own_exactly_one_match`, `::test_zero_matches_reports_the_same_advisory_and_ships_the_item`, `::test_two_or_more_matches_ship_unlinked_and_report` — confirmed present and passing |
| **R-D** — equipment sentence markup differs on unsampled faction pages | Five subject productions cover ≈99.5% of the measured corpus; unmatched ships `EQP-UNPARSED`, never dropped | `tests/enrichment/test_equipment_grammar.py`'s five subject-production tests (`test_every_model_is_a_whole_unit_subject` through `test_a_named_subject_is_a_model_group_carrying_that_name`) plus `test_a_compound_or_conditional_subject_is_refused`/`test_a_sentence_with_no_equipped_with_marker_is_refused` for the residual. Live: `loadout.default_equipment` 2,017/2,084 (97%) in `reports/wh40k-11e-2026-08-2/report.json` |
| **R-E** — extracting the equipment sentence perturbs the composition row set | Measured non-overlap (composition reads `ul.dsUl > li`; equipment reads a sibling `<b>` + text node); a contract test pins the composition row set | `tests/unit/test_wahapedia_html_dom.py::test_every_composition_line_resolves_through_the_unmodified_grammar` passes on the tree that also now reads `_equipment` from the same block, confirming the sibling read did not perturb composition extraction |
| **R-F** — an equipment group attaches to the wrong composition row | `link_model_line`'s exactly-one-match name rule, never ordinal | `tests/enrichment/test_us2_independent.py::test_each_group_links_to_the_composition_row_it_names`; `tests/enrichment/test_equipment_link.py::test_the_link_is_by_name_and_never_by_the_sentences_own_ordinal`, `::test_one_sentence_over_two_composition_rows_is_a_unit_group_with_no_link` (the measured two-line/one-sentence shape) |
| **R-G** — a joined name exceeds the 120-character ceiling | Reported (`OPT-UNPARSED`) rather than truncated or the ceiling raised | `tests/enrichment/test_priced_projection.py::test_a_joined_name_over_the_ceiling_is_unparsed_rather_than_truncated` — confirmed present; the 120-character ceiling itself is unchanged from `_parse_object`'s pre-existing rule |
| **R-H** — a released consumer rejects three unknown top-level arrays | FR-020 proof gathered on pre-release before any published version exists; one-variable retreat | T045/T046, live, against the real pre-release candidate, **before** T049's publish dispatch: `reports/wh40k-11e-2026-08-2/consumer-compat.md` — `tools/consumer_compat.py` unmodified, exit 0, zero violations; site build unmodified, 2,462 pages, `verify-dist` green ×4 |
| **R-I** — the change-class guard blocks a PR mixing transform and regenerated `data/` | Separate PRs, planned from the start | Confirmed in the commit history: `pipeline/`+`tests/` work landed first (`55f2c556`…`b67ed571`), the live candidate build as its own commit (`f10a0e39`), evidence re-recording separately (`a4d08a00`) — `tools/check_change_classes.py` was never asked to pass a mixed diff for this feature |

## Principle 16 (AI-Assisted Content Disclosure) — swept for this feature's own delivery

Swept every file changed between the pre-006 commit (`a44983d4`) and the published tip (`51e586bf`)
that is not machine-written data or a synthetic fixture data file (`curation/*.json`,
`fixtures/**/*.{json,csv,html}` are exempt from an inline header by the same established convention
`002`'s own compliance review above already documents — a keyed array has no natural `_comment`
slot and is instead covered by `curation/README.md`'s provenance section):

- **135 of 135** checked `.py`, `.md`, `.yml`, `.json`-schema, and CODEOWNERS files carry an
  `AI-Assisted:` header in their first ~2,500 characters. Zero misses.
- **27 of 27** commits in this feature's range (`55f2c556` through `b4922470`, the published-at fix
  and rebuild commits included since they were required to actually publish this release) carry an
  `AI-Assisted-By:` trailer, checked by parsing each commit's full message rather than sampling.

No exceptions found in either direction.

## Open items carried forward from this review (recorded, not hidden)

Two items surfaced by this review are named in `docs/follow-ups.md` rather than folded into this
verdict as if resolved:

1. **Item 13** — PR #13's own rebuild-proof evidence file (`reports/006-published-at-fix/
   rebuild-proof.md`) merged to `fix/published-at-input`, not to `main`, because of the two-branch
   topology the mid-review fix required; it is unreachable from `main` today even though the
   release it documents published correctly (the live `publish.yml` gate re-proved the same claim
   independently at publish time, run
   [31703446027](https://github.com/The-BadgerWorks/wargame-rules-data/actions/runs/31703446027)).
2. **Item 14** — the `curation/equipment-overrides.json` escape hatch (T031) has no dedicated test,
   confirmed by an exhaustive search of `tests/` for `EquipmentOverride`/`equipment_override_for`/
   `equipment-overrides` returning zero matches outside the implementation itself.

Both were also renumbered as part of this review: `docs/follow-ups.md` carried two items both
headed "## 10" (the `option-regression` command and the `--published-at` build options, added
independently in separate sessions). Fixed to 11 and 12 respectively, with every in-repo
cross-reference (`pipeline/cli.py`, `tests/contract/test_cli_surface.py`) updated to match.

## Verdict

**PASS.** All eight gates hold against the delivered repository, confirmed by re-running the full
`ruff`/`mypy`/`pytest` gate rather than re-reading the plan's description of intent. Every one of
Risks R-A through R-I has a concrete, checked mitigation in the delivered tree, several with live
(not only fixture) evidence from the `wh40k-11e-2026-08-2` release itself. Principle 16 disclosure
is complete across every non-data file and every commit this feature produced. Two process gaps —
neither a defect in the published bytes — were found and named rather than silently left for the
next reviewer to rediscover.
