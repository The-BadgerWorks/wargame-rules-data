<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Constitution compliance review and
     evidence capture for the Polish phase (task T162): re-ran plan.md's eight gates against the
     delivered repository, confirmed the Principle 5 exception's drift check, the Principle 11
     limitation's compensating controls, and the Principle 14 exception's confinement, and swept
     every file and commit landed in this phase for the required disclosure. -->
<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Appended the 006-unit-loadout-fidelity
     T053 constitution compliance review: re-ran the eight gates against the delivered repository
     after wh40k-11e-2026-08-2 published, checked each of Risks R-A through R-I against a concrete,
     opened file or passing test rather than the plan's description of intent, and swept every
     non-data file and commit in the feature's range for Principle 16 disclosure.
     AI-Assisted: Claude Code (model: claude-sonnet-5) - Appended the 007-loadout-display-fidelity
     T072 constitution compliance review: re-ran the eight gates against the delivered repository
     after wh40k-11e-2026-08-3 published, live (ruff/mypy/pytest, not re-asserted from memory),
     checked all seventeen named risks across research.md D8 (R-1..R-8) and plan.md's own risk
     table (R-A..R-J) against a concrete file or passing test, and swept every non-data,
     non-machine-written file and every substantive commit in the feature's range for Principle 16
     disclosure. -->
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

---

# T072 (007-loadout-display-fidelity) — constitution compliance review and evidence capture

`specs/007-loadout-display-fidelity/plan.md`'s Constitution Check (`WargameCompanion`) recorded, at
planning time, **PASS, zero N/A gates, no new exception requested, the two `002`-inherited
exceptions unchanged, and two Product Owner items (O1, O2) decided 2026-08-13 rather than resolved
unilaterally**. This re-runs the same eight gates against the *delivered* repository, now that
`wh40k-11e-2026-08-3` has published (2026-08-14), and checks all seventeen named risks — `research
.md` D8's `R-1`..`R-8` and `plan.md`'s own risk table's `R-A`..`R-J` (two separate, deliberately
distinct lettering schemes in this feature's own planning documents, both re-run here) — against a
concrete file or passing test rather than the plan's description of intent.

## The eight gates, re-run live

Every check below was executed against the delivered `main` (`229c2b3d`, the publish commit, plus
`eb353f0e`, this Polish phase's own T069 documentation commit) during this review, not re-asserted
from a prior run.

| Gate | Plan-time | Delivered-repository check | Result |
|---|---|---|---|
| Spec-first | PASS | `spec.md` still governs; O1 (all 2,039 corrections ship in one release, plus the `CMP-HEADER-ROW` T030 refusal-to-advisory demotion) and O2 (one-sided consumer-compat evidence accepted) are both resolved with a dated Product Owner ruling in `tasks.md`'s T061/T067 entries, not silently dropped | **PASS** |
| Verification | PASS | Full gate green, run live for this review: `ruff check .` — all checks passed; `ruff format --check .` — 302 files already formatted; `mypy pipeline --strict` — no issues in 95 source files; `pytest -q` — **1,894 passed, 8 skipped** (matches PR #18's own recorded CI figure exactly); `pytest tests/ip/ -q` — 83 passed. `specs/007-loadout-display-fidelity/verification-evidence.md` (T070) traces all 20 acceptance scenarios to a named test, live report, or the manual spot-check — three honest gaps named there (SC-005's one-sided implementation proof, US4 scenario 1's reworded mechanism, US4 scenario 3's unmeasured cluster ratio), none of which is a hole in the 20 scenarios themselves | **PASS** |
| Policy/safety | PASS | `pytest tests/ip/ -v` — 83/83 passed (up from 006's 31, growing with every new field family this feature adds); `tests/validate/test_equivalence.py::test_a_mismatch_finding_never_carries_either_sides_text` and `::test_the_source_text_used_for_a_mismatched_comparison_is_never_written_anywhere` confirm Part C's central promise directly, the second as a real-build, grep-the-disk regression test (T051, written *before* T052's implementation existed to pass it, per `docs/failed-then-fixed.md`'s standing rule); no new upstream source — `pipeline/acquire/` untouched by this feature's own diff | **PASS** |
| Infrastructure | PASS | No new workflow, no new job. The two `002` exceptions (Principle 5 settings-drift, Principle 11 self-deploying workflows) are unchanged and not touched by this feature. `candidate.yml`'s PR-creation step still cannot complete unattended for a genuinely new PR against this org's current settings — surfaced twice this release (PR #16→#17, and again for #20), tracked as `docs/follow-ups.md`'s new item on that exact gap rather than treated as a regression this feature introduced | **PASS** |
| Environment | PASS | Exactly one new `CONFIG_VARS` entry landed, `WGC_EQUIVALENCE_CHECK_ENABLED` (confirmed at `docs/configuration.md`'s own table, written ahead of T072 at T014) — a switch, not a logic branch: disabled, the check simply does not run, and the two report-only figures do not appear that build. The elision-word set is deliberately **not** a second environment variable, per the plan's own argument (contract §9.1's "not derived from any source page") — confirmed by grepping `pipeline/config.py`'s `CONFIG_VARS` for any elision-related key: none exists. `WGC_DATA_CHANNEL` remains the only branch point | **PASS** |
| Security/configuration | PASS | No new credential, secret, or permission. `WGC_MECHANIC_DIGEST_KEY` untouched — nothing this feature adds is authored prose subject to digesting, confirmed by the same IP-scan sweep above finding zero new prose-bearing fields | **PASS** |
| Operational readiness | PASS | Both new report-only figures appear in `reports/wh40k-11e-2026-08-3/report.json`'s `coverage` block, confirmed live: `loadout.rendering_equivalence` 388/2,587 compared (15.0%, 1,525 `not_compared`), `loadout.item_constraints` 0/0 (100% by the zero-attempts convention). `docs/runbook.md`'s T069 addition (this Polish phase) makes both readable operationally, not just visible in the JSON. Rollback is additive per-class by construction — `pipeline/build/bundle_emit.py`'s new array is populated only from `curate/assemble.py`'s `_item_constraint` outputs, so nothing needs a flag for it to fall back to empty | **PASS** |
| Separation | PASS, with a real mid-release exception that was corrected before publication | `tools/check_change_classes.py` and CODEOWNERS themselves are unchanged. **But the delivery did not hold to the planned separation on the first attempt**: `candidate.yml`'s first live dispatch (PR #17) built the candidate branch on top of the still-unmerged feature branch, so its diff against `main` mixed `pipeline+tests` and `curation` — the guard caught it (`FAIL: this PR touches more than one change class`), and the release was restructured into PR #18 (`pipeline+tests`) then PR #19 (`curation`, dependent on #18) before a `data`+`reports`-only PR #20 could pass the guard cleanly. This is the guard doing exactly its documented job, not a bypass of it — recorded in full in `.impl-progress.md`'s Release Phase section and carried forward as a named follow-up (below) so the next feature plans the split-PR path from the start rather than discovering it under release pressure | **PASS, guard exercised for real and held** |

## Risks R-1 through R-8 (research.md D8): mitigation landed, checked against the delivered repository

| Risk | Plan's mitigation | Confirmed landed |
|---|---|---|
| **R-1** — the five-signal header refusal suppresses a genuine first model row outside the measured eight | Re-derive the refusal set over the whole corpus, report every refused row by datasheet id, before the fix ships | **Materialised as a finding, not a surprise, exactly as the mitigation predicted.** T031's live re-derivation (`tools/composition_header_refusal_report.py`, `reports/composition-header-refusal/2026-08-14.md`) found 3 refused rows, **none matching the 8 originally-measured Kill Team datasheets** — the false-positive-on-genuine-rows risk was real, which is exactly why the Product Owner's T061 decision 3 withdrew the automatic refusal in favour of an advisory `CMP-HEADER-ROW` finding plus curator-only suppression (`tests/enrichment/test_composition_header_refusal.py`) |
| **R-2** — the header shape occurs on cards where the rows do not sum (**UNVERIFIED** at plan time) | Not refused; ships as today, under-delivery not over-refusal | **Confirmed, live.** T004's real population probe (`reports/header-refusal-population/2026-08-14.md`): 316 structural candidates, 11 sum, 305 do not — the non-summing majority ships unrefused exactly as designed, never suppressed by the conjunction |
| **R-3** — the curated round-trip's one-time `data/` addition is mistaken for a data change during review | Stated in the candidate PR body; change summary shows zero published value changes beside it | `pipeline/report/pr_body.py`'s candidate body text plus `reports/wh40k-11e-2026-08-3/change-summary.md`, confirmed present on PR #20 and referenced in its own description (`.impl-progress.md`'s "the fresh, guard-compliant candidate" section) |
| **R-4** — the equivalence figure is low on its first release and reads as a defect rather than a baseline | Report-only decision; `not_compared` reported as its own count | `loadout.rendering_equivalence` 15.0% with `not_compared` 1,525 reported alongside it in the same `report.json`/`report.md` row family; `docs/runbook.md`'s T069 addition now reads this explicitly as "a statement about how much of the corpus the check currently reaches," not a quality signal |
| **R-5** — the two renderers agree with the corpus but the corpus does not cover a shape the real data contains | Corpus required to cover every template id and every omission row | `tests/contract/test_rendering_conformance.py`'s parametrised cases cover every template in `contracts/rendering-fixtures/cases.json`, including the `O-007`/`C-003` omission cases; `test_omitted_codes_match` asserts every selection table's `else` produces an `RND-*` code, never a fabricated line |
| **R-6** — the equipment-override escape hatch has no test coverage at all (pipeline follow-up 14) | Override tests land with this feature rather than after the first override is authored | T034, paid in full: `tests/enrichment/test_equipment_overrides.py` (resolving, dangling-datasheet, dangling-line, dangling-weapon cases) — confirmed present, distinct from GitHub issue #14 (an unrelated coincidence of numbering the task itself calls out) |
| **R-7** — the FR-007 correction touches ≈2,030 published choices, a diff no approver can read row by row | Group by transition class with counts; manual spot-check samples each class | `reports/wh40k-11e-2026-08-3/option-regression.md`'s *Corrected* section groups all 2,039 by the three D3.3 classes (37/2,002/0); `spot-check.md` samples from classes 1 and 2 live (class 3 has zero live members to sample); PO acknowledgement recorded at T061 (2026-08-14) before the live candidate carried the correction |
| **R-8** — a legacy stem states a given-up item the new production cannot resolve, so a published link is lost | Accepted and reported, not worked around; option-regression shows the transition explicitly | This is exactly the 2,002-row "stated but unlinked" class above — `tests/enrichment/test_legacy_option_roles.py::test_d3_3_case_2_the_given_up_item_is_stated_but_does_not_link_uniquely` confirms the item ships unlinked rather than wrongly linked, and the report names every instance |

## Risks R-A through R-J (plan.md's own table): mitigation landed, checked against the delivered repository

| Risk | Plan's mitigation | Confirmed landed |
|---|---|---|
| **R-A** — same risk as R-1, plan.md's own numbering | Same mitigation | Same evidence as R-1, above |
| **R-B** — correcting the role inversion changes a value the `006` item rows already publish | Expected, bounded, enumerated in the same report; baseline-first ordering keeps every previously-resolved shape resolving | `pipeline/parse/options_grammar.py`'s clause table still runs every `004`/`006` production before any `007` production (structural, confirmed by reading the file); `option-regression.md`'s *Corrected* section enumerates both the link and the item-role change together, per choice |
| **R-C** — the 2,030-row approval item is approved without being read | Grouped by transition class with counts (O1); manual spot-check samples each class | Same evidence as R-7, above — this is R-7 restated from the review-process angle rather than the data angle |
| **R-D** — the source block text is no longer available in `work/` when `validate` runs (**UNVERIFIED** at plan time) | Measured by the first implementation task; the check moves to whichever stage holds the text if the window is wrong | **Refuted as framed, and fixed accordingly.** T001's live trace (`reports/equivalence-availability/2026-08-13.md`) found the source text unreachable at either originally-planned `validate` call site — reachable only inside `build`'s own `with workspace()` block, the same scope the mechanic-digest computation already uses. `pipeline/cli.run_build` calls the comparison from inside that block (`pipeline/validate/equivalence.py`), confirmed by `tests/validate/test_equivalence.py` running the real comparison end to end rather than against a call site that never has the text |
| **R-E** — a retention bug puts source text into a report | Four compounding controls: nothing typed to hold it, enumeration outcome type, IP scan with no allowlist, a retention test with a distinctive synthetic token | T051's retention test (`tests/validate/test_equivalence.py::test_the_source_text_used_for_a_mismatched_comparison_is_never_written_anywhere`), written *before* T052's implementation existed to pass it — confirmed still passing; `tests/ip/` grew from 31 (006) to 83 (007) tests, all green |
| **R-F** — the marker strip changes a published display name a consumer keys on | Low and measured: the marker is already invisible to every join because the name normaliser collapses non-alphanumeric runs before matching | `tests/contract/test_contract_guarantees.py::test_a_marker_in_any_name_field_is_blocking`, `::test_a_fully_built_loadout_fixture_carries_zero_marker_residue` (guarantee 21); `pipeline/normalize/names.py` unchanged in its join-normalisation behaviour by this feature |
| **R-G** — the vendored conformance corpus drifts from the contract | A stamped version in the corpus; a drift check in CI; changelog discipline | `tests/contract/test_rendering_conformance.py::test_vendored_corpus_contract_version_matches_the_renderer` — confirmed present and green; `contracts/rendering-fixtures/{cases,expected}.json` both stamp `contract_version` |
| **R-H** — the one-time curated `data/` addition is read as a data change | Stated in the candidate PR body; change summary shows zero published value changes beside it | Same evidence as R-3, above — this is R-3 restated from plan.md's own risk table |
| **R-I** — the rendering contract accretes presentation concerns | Scope fixed in contract §1; the segment stream exists so styling never requires changing the sentence | `contracts/rendering-contract.md` §1's scope statement, now **Frozen** (T071) rather than merely proposed; §7's optional segment stream is unchanged from its 2026-08-13 authoring |
| **R-J** — not every footnote restriction arrives as a refused option row (**UNVERIFIED** at plan time) | The first implementation task measures the refused-row population by structural class | **Confirmed, live.** T003's real measurement (`reports/footnote-restriction-taxonomy/2026-08-14.md`): both the composition and equipment residuals are `neither`-only — every footnote-style restriction in the measured live corpus arrives as a refused option row, no second arrival path was needed this release |

## Principle 16 (AI-Assisted Content Disclosure) — swept for this feature's own delivery

Swept every file changed between the pre-007 commit (`6e9013aa`, 006's own close-out) and the
published tip (`229c2b3d`), excluding `data/`, `reports/` (machine-written, exempt by the same
established convention prior reviews on this page use), and `fixtures/**/*.{json,csv,html}`
(synthetic data, exempt for the same reason `curation/*.json` is):

- **62** non-`data/`, non-`reports/`, non-fixture-data files changed in this feature's range were
  checked; **59 of the 62** carry an `AI-Assisted:` header in their first ~4,000 characters. The
  **3** without one are `site/manifest.json`, `state/published-checksums.json`, and `state/
  run-ledger.jsonl` — all three machine-written state, exempt by the same convention the manifest
  and ledger have always been exempt under (never human-authored prose or logic).
- **Every** commit carrying substantive, human-directed content in the feature's range (`3ec083b2`
  "pipeline, tests, tools, schemas, fixtures, docs, contracts, reports"; `fed9e5ca` "curator remove
  overrides"; `0b03eeb0` "post-merge option-regression evidence") carries both the `AI-Assisted-By:
  Claude Code (model: claude-sonnet-5)` trailer and `Co-Authored-By: Claude Fable 5
  <noreply@anthropic.com>`. Merge commits (`a7f0d475`, `c06280b8`, `66d79a7b`, `16e01c75`) and
  machine-generated `detect`/`integrity` sweep commits and the `publish.yml` publish commit itself
  (`229c2b3d`) carry neither, consistent with every prior release on this page — those are GitHub's
  own merge-commit text or the pipeline's own automated commit messages, not human-authored content
  requiring disclosure.

No exceptions found in either direction beyond the machine-written-state class already named above.

## Open items carried forward (not gate failures — recorded, not hidden)

Four items surfaced by this feature and this review are named in `docs/follow-ups.md` rather than
folded into this verdict as if resolved:

1. The footnote-constraint vocabulary (`not_replaceable`, `one_per_unit`) matched **zero** real
   rows this release, despite the taxonomy finding real restriction-shaped candidates in the live
   corpus — worth widening against real shapes in a future feature.
2. `loadout.rendering_equivalence`'s 15.0% baseline is report-only by design (FR-022); the
   mismatch/`not_compared` split needs investigation before any future ratchet decision, not a
   ratchet applied to the raw number as it stands today.
3. The org still blocks Actions-created pull requests for a genuinely new PR
   (`candidate.yml`'s own PR-creation step edited the already-closed PR #17's body rather than
   opening a new one on its second dispatch) — a repository-settings gap, not a data or code defect,
   surfaced twice this release.
4. The change-class guard's one-class-per-PR discipline means a future feature that touches more
   than one class must plan the split-PR release path (code → curation → data) **from the start**,
   not discover it under release pressure the way this feature's PR #17→#18/#19/#20 restructure did.

## Verdict

**PASS.** All eight gates hold against the delivered repository, confirmed by a live re-run of the
full `ruff`/`mypy`/`pytest`/`tests/ip` gate rather than by re-reading the plan's description of
intent. Every one of the seventeen named risks across both of this feature's own risk-numbering
schemes (`R-1`..`R-8`, `R-A`..`R-J`) has a concrete, checked mitigation in the delivered tree, most
with live (not only fixture) evidence from the `wh40k-11e-2026-08-3` release itself — including two
risks (`R-1`/`R-A` and `R-J`) whose live measurement changed the shipped mechanism from what the
plan originally described, which is the risk process working as designed rather than a defect. The
Separation gate's guard fired for real mid-release (PR #17's mixed change classes) and the release
was correctly restructured rather than the guard being weakened — recorded as the one gate result
this review states with more nuance than a bare "PASS." Principle 16 disclosure is complete across
every non-machine-written file and every substantive commit this feature produced. Four open items
are named in full rather than left for the next reviewer to rediscover.
