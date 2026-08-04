<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Constitution compliance review and
     evidence capture for the Polish phase (task T162): re-ran plan.md's eight gates against the
     delivered repository, confirmed the Principle 5 exception's drift check, the Principle 11
     limitation's compensating controls, and the Principle 14 exception's confinement, and swept
     every file and commit landed in this phase for the required disclosure. -->
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
