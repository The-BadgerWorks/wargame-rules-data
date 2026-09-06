<!-- AI-Assisted: Claude Code (model: Claude Opus 5) - Authored when the project moved to the
     rung/gate/receipt workflow, so /code-review and every executor session in the repo where
     the code actually lives read the same contract as the one in WargameCompanion. -->
# wargame-rules-data — working rules for agents

This repository is the whole rules-data pipeline: it acquires two upstream sources, strips
everything the product may not carry, reconciles them, and publishes immutable, versioned,
IP-clean snapshots that a Flutter app and a website read. **It must never retain the
publisher's words** — not in `data/`, not in `reports/`, not in `state/`, not in a fixture, not
in a log, not in a commit message, not in an issue. Everything else here is negotiable; that is
not.

**Governing documents.** The method is `Agent-workflow.md` in the sibling `WargameCompanion`
repo; the project-level contract is that repo's `CLAUDE.md`. This file is the code-side half
and does not contradict them — where it repeats a rule, it is because that rule is broken here
or nowhere.

**Plans do not live here.** The ladder and kickoffs for the in-flight feature are in
`WargameCompanion-009/specs/009-csv-migration/`. Tier-2 debt goes to
`WargameCompanion/workflow/debt-ledger.md`.

---

## Roles

- **Owner (human).** Product decisions, scope, every merge to `main`, every publish. Named in
  the record as the Product Owner.
- **Manager (persistent session).** Runs the gate first-hand, never on an executor's report.
  Owns every long-running run, because a subagent cannot block across its own turn boundary.
- **Executor (fresh session per rung).** Implements one kickoff. Reports evidence, not
  conclusions. Corrects the kickoff when the kickoff is wrong.

---

## What counts as a defect

**TIER 1 — blocks the rung. Stop, report exact values, wait for the Owner.**

1. Wrong or crashing behaviour a consumer would hit — the app, the site, or published data.
2. **A correctness invariant broken without a stated cause:** a published identifier that moved
   (`faction_id`, `ds-<slug>-N`, an ability key); a coverage ratio below its floor; a summary
   digest refreshed without citing its authorization; the faction model leaving 30; a rebuild
   from unchanged curated inputs producing different output.
3. **A report, finding, or doc that contradicts actual behaviour** — including one asserting
   something it never checked. A ratchet reading green over an empty roster is this defect, not
   a passing test.
4. **Any retained publisher wording anywhere.** No exceptions, no "it is only a fixture".

**TIER 2 — never blocks.** Coverage, naming, style, structure, commit shape, known residuals.
File it in the ledger with evidence and origin, and keep going.

---

## Receipts

**A green check is not a covered case.** A test that would look identical if the feature were
deleted protects nothing, and this repo has shipped several: a pinned hash whose test path
never touched the changed code, a "same output" test asserting only `exit_code == 0`.

- Every change ships **at least one receipt that fails if the change is reverted**. Say what
  the failure looks like before you write the fix.
- **Failing-first is the house form.** Write the test, run it, record the red output, then fix.
  Findings A and B in 009 were both closed this way.
- **Prove both directions when fixing a check.** The false positive is gone *and* the true
  positive still fires.
- **Anything you added on your own judgement needs the same receipt as anything you were told
  to do.** In this project's worst round, both mandated changes were correct and both
  self-directed ones were broken, because nobody asked those for evidence.
- The non-vacuous form for an arm swap: build twice, once per arm for a moved class, and
  **assert the outputs differ**, with a message saying identical outputs mean the mechanism is
  not wired up.

---

## Build and test

```bash
pytest                             # full suite; last known good 2270 passed / 8 skipped
ruff check . && ruff format --check .
mypy                               # strict, packages = ["pipeline"]
```

`pytest` alone — `testpaths` and `pythonpath` are configured in `pyproject.toml`, and invoking
a subset by path can change import resolution. Run it once and block until it finishes; do not
re-run a suite already green for the same commit, but **do** re-run if HEAD moved after it.

The CLI is `rules-pipeline` (`pipeline.cli:main`):

| Command | Does |
|---|---|
| `detect` | acquire the points source, digest mechanical values, compare with the last digest |
| `acquire` | acquire both sources into `work/`; commits nothing |
| `build` | full run: acquire, parse, normalize, reconcile, curate, validate, build |
| `validate` | re-validate the curated tree without acquiring |
| `report` | regenerate reports from the curated tree and the previous published version |
| `publish` | publish an approved candidate; refuses outside the approved CI context |
| `withdraw` | mark one published version withdrawn; manifest only |
| `verify` | re-verify every published version's checksum |

**A live run is not a test.** It reaches the network, honours `robots.txt`, a UA, and a
politeness interval, and it is the manager's to own — never an executor's to wait on.

---

## Traps

Every one of these has produced a confidently wrong answer in this repo.

1. **Ratchets read green on total loss.** `LoadoutCoverage.ratio_percent` returns **100** on an
   empty roster, and `report/coverage.py::_ratio` returns **1.0** when `previous <= 0` — which
   already leaves the `composition`, `wargear_options` and `keyword_classification` collapse
   floors inert in the live report. **Coverage floors are not a cutover guard.** The guards are
   the roster-identity assertion and `REC-DETAIL-FACTION-EMPTY`.
2. **The faction-vocabulary trap.** `curate/assemble.py` decides which detail rows a faction may
   match with `row.fields.get("faction_id") in scope.detail_faction_ids`. If the two sides speak
   different vocabularies — export codes on one, page slugs on the other — the candidate set is
   **empty for every row of every faction**, every unit mints a fresh id, and the run **ships**
   with an advisory. A total loss that looks like a successful build.
3. **A merged PR is not landed code.** PR #22 once reported merged and never reached `main`; it
   surfaced later as an unrelated-looking candidate build failure. After any merge:
   `git fetch origin && git show origin/main:<path>` and check the content.
4. **Never use GitHub's "Update branch" control** on this project's PRs. It has broken the
   bot-authorship guard on data-class PRs and silently changed what a reviewer approved.
5. **Do not stack PRs.** Cut each from `origin/main` directly. A stacked PR merged into its
   parent's branch instead of `main` is how #22 went missing.
6. **`work/` is ephemeral and gitignored**, emptied by the run itself. It is the only directory
   a live run may write. Measurement runs use a **scratch copy of `curation/`** and divert
   `output/` and `reports/` to scratch — nothing lands in the tracked tree.
7. **Raw source must never enter a transcript.** Fetch direct-to-disk into a scratch path.
   Never `cat` an acquired export, never quote a source row in a test, a report, a commit
   message, or a progress log. Counts, finding codes, and identifiers only. **A finding never
   quotes what it found** — `DQ-MARKUP-IN-FIELD` names the field, not the markup.
8. **Task IDs are reused across features.** A bare `T049` in this tree may belong to 002, 008,
   or 009. Only a `009 task T0xx`-style citation is evidence of which feature owns it.
9. **`ip_strip.py`'s markup hole is open on `main`.** There, `_TAG` is a single pattern
   requiring a name character immediately after `<` and a terminating `>`, so `< b>x</ b>`
   survives with **no finding** and `a <b and c> d` collapses to `a d`. `models/mechanical.py`'s
   `NON_MECHANICAL_PATTERNS["markup"]` is character-identical, so such a residue passes
   `assert_mechanical_string` and `validate/ip_scan.py` **and would publish**. Fixed on
   `009-csv-migration` (two-branch `_CLOSED_TAG` | `_UNTERMINATED_TAG`), waiting in PR #27.
   **These two patterns must move together, always.**
10. **A fixture may never stand in for a table the real export does not publish.**
    `fixtures/enrichment/wahapedia/Datasheets_unit_equipment.csv` fabricates one, while
    `fixtures/minimal/` and `fixtures/disagreements/` — the sets that model the real export —
    omit it. Table presence and population are asserted against the **acquired** set. That is
    the one class of assertion here that may not be fixture-backed.

---

## Standing rules

Breaking one of these is Tier 1.

1. **Raw source is never committed** — not as a fixture, a golden file, or an attachment.
   **Fixtures are synthetic**: invented ids, invented names, invented placeholder prose.
   `tests/ip/test_no_raw_source_committed.py` enforces it.
2. **The publisher's wording is never retained**, anywhere, including working storage and
   history. Change detection on an ability uses a one-way normalised digest, never a stored copy.
3. **Ability summaries are authored by a human from the mechanic.** Machine paraphrase, synonym
   substitution, or reordering of the publisher's text is a policy violation, not a shortcut.
4. **The pipeline writes `data/`; humans write `curation/`.** Neither ever writes the other. No
   code path may generate the crosswalk, the faction codes, the authority declaration, or a
   refreshed digest. Machine-**drafted** through the pipeline's own client, **human-verified per
   entry before merge**.
5. **Automation produces candidates only.** `publish.yml` is the only code path that may write a
   Release or the manifest, and it refuses outside the approved CI context. Never work around
   that refusal.
6. **No mode branch below `acquire`.** From `acquire/detail_source.py`'s own docstring: *"If a
   `if mode is …` appears anywhere below `acquire`, the design has been lost."* A hybrid is
   expressed as **which arm populates which table**, resolved at acquisition and declared in
   `curation/` — never as a conditional in `parse`, `normalize`, `reconcile`, `curate`,
   `validate` or `build`.
7. **No grammar production is authored while a normalization cause is unfixed.**
   `parse/options_grammar.py` and `parse/equipment_grammar.py` are not edited by feature 009. A
   production written to paper over a normalization defect is a second parallel vocabulary at
   permanent maintenance cost.
8. **A ratchet is never lowered, waived, or made tolerant because the source format changed.**
   Floors are *read* from the previous published `report.json`, never authored. The
   `WGC_RATCHET_TOLERANCE_*` and `WGC_COVERAGE_MIN_*` knobs exist for the Owner, not for a
   failing build.
9. **Every `curation/unit-map.json` entry carries `faction_id`.** Optional in schema so the
   change stays additive; **mandatory in the authoring rule**, because an entry without it is
   adopted into every faction scope and collapses the six per-chapter Space Marine identifiers
   the Owner's C1 ruling holds apart.
10. **A class, rung, or cause measured at zero gets no code.** 004 refused `may`, 006 refused
    the digit quantifier, 008 refused productions for classes it measured empty. `match.py`'s
    "report, never guess" stage 4 is designed behaviour, not a gap.
11. **One change class per commit, and one per PR**: `pipeline/` + `tests/` in one, `curation/`
    in another, `data/` candidates in a third. `tools/check_change_classes.py` enforces it.

---

## Branches, PRs, commits

- Work lands on a branch and a PR, **never straight to `main`**. `/code-review` needs a PR.
- Branch per rung: `<feature>-R<nn>-<slug>`, cut from `origin/main` directly, not stacked.
- Every file added or substantially edited gets an `AI-Assisted:` header comment; the commit
  gets the matching `AI-Assisted-By:` trailer.
- Candidate and publish runs are made under the pipeline bot's identity. A human-authored
  commit on a data-class PR fails the authorship guard.
- **Merges to `main`, candidate approval, and publication are Owner actions.** Prepare them and
  stop.

---

## Where things are

| Path | Holds |
|---|---|
| `pipeline/` | `acquire` → `parse` → `normalize` → `reconcile` → `curate` → `validate` → `build`, plus `detect`, `report`, `publish`, `render` |
| `curation/` | human-authored: faction map, unit map, glossary, overrides, authored summaries |
| `data/` | machine-written curated tree; never hand-edited |
| `reports/`, `state/` | run output and change-detection state; counts and codes only |
| `fixtures/` | synthetic only — `minimal/`, `disagreements/`, `enrichment/`, `identity-baseline/` |
| `schemas/`, `contracts/` | curated input schemas and the frozen consumer contracts |
| `docs/` | `runbook.md`, `configuration.md`, `follow-ups.md`, `failed-then-fixed.md`, `break-glass.md`, `approval-checklist.md`, `verification/` |
| `tools/` | measurement and guard scripts — taxonomy, churn dry-run, change-class check |
| `.github/workflows/` | `ci`, `detect`, `candidate`, `publish`, `withdraw`, `integrity`, `settings-drift` |

Record a defect you found and fixed in `docs/failed-then-fixed.md`. Record something you
deliberately left open in `docs/follow-ups.md`.
