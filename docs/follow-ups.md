<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Recorded three items surfaced while
     landing the Polish phase (T146-T162): one operational setup step the settings-drift checker
     (T148) depends on but cannot perform itself, one pre-existing test-hygiene defect the T161
     stage-boundary audit exposed, and the stage-boundary exception T161 documented but did not
     resolve. None of these block acceptance; all three are named here so they are not lost. -->
<!-- AI-Assisted: Claude Code (model: claude-opus-5) - Added item 4 (004 T076 follow-up): the
     datasheet-coverage shortfall that survives the faction-map slug correction, and the
     chapter-disambiguation signal html mode does not carry. -->
# Follow-ups

Open items surfaced during implementation that are deliberately **not** fixed as part of the work
that found them — either because they need a human with credentials this session does not have,
or because fixing them would have widened a task past what it was scoped to touch. Each is honest
about why it was left rather than folded in.

## 1. `WGC_SETTINGS_AUDIT_TOKEN` secret needs to be created (T148)

`tools/check_repo_settings.py` and `.github/workflows/settings-drift.yml` (task T148) are
implemented and tested, but the workflow cannot run successfully against the live repository
until a maintainer creates the `WGC_SETTINGS_AUDIT_TOKEN` repository secret it reads. This is
deliberate, not an oversight: reading branch protection and environment settings back through the
GitHub API requires a token with real repository administration-read access, and the standard
Actions `GITHUB_TOKEN` has no such scope available to it (there is no `administration` permission
in the workflow `permissions:` block — that is an app-installation-only permission). Wiring an
admin-capable credential into the existing `pull_request`-triggered `ci.yml` job was rejected for
the same reason `docs/repo-settings.md` already reasons about credentials generally: keep anything
capable of reading or writing repository configuration on the narrowest trigger that still does
the job. `settings-drift.yml` is `workflow_dispatch` plus a weekly `schedule` only.

**Action needed**: a maintainer (`adhoxx`) creates a fine-grained personal access token scoped to
`The-BadgerWorks/wargame-rules-data` only, with **Administration: Read-only** repository
permission and nothing else, and stores it as the `WGC_SETTINGS_AUDIT_TOKEN` repository secret.
Until then, `settings-drift.yml` will fail with a clear "token not configured" diagnostic rather
than silently doing nothing — see `tools/check_repo_settings.py`'s own handling of a missing
token. This is the one narrow, documented exception to "no long-lived PAT anywhere in this
design" (`contracts/pipeline-run-interface.md` §5): it reads settings, never publishes, and holds
no write scope of any kind.

## 2. Test-hygiene defect: `test_cli_surface.py` writes to the real `state/run-ledger.jsonl`

`tests/contract/test_cli_surface.py::test_every_command_returns_a_code_from_the_stable_set`
parametrizes over every contract command including `verify`, calling
`main(["verify", "--offline"])`. Its comment (written at task T106, before `verify` existed) says
`verify` "remain[s] pending stage modules" and therefore falls through to the `_pending` handler
without touching anything. That was true then; it is no longer true — `rules-pipeline verify` was
implemented at T140-T143, and the test was never updated to isolate it from the repository's real
working directory. Every `pytest` run now appends one real ledger entry to the tracked
`state/run-ledger.jsonl`, because `verify`'s `--offline` flag only suppresses network access (it
never made any) and the test does not `monkeypatch` the CLI's working directory or use the
"temporary-repository factory for publication tests" `tests/conftest.py` already provides for
exactly this purpose.

**Effect observed**: confirmed directly while merging this phase's branches — running the full
suite twice added two real entries to `state/run-ledger.jsonl`, which then showed up as an
uncommitted, undesired diff. Reverted with `git checkout -- state/run-ledger.jsonl` before
committing; not committed as a "real" ledger entry.

**Fix needed** (not applied here, to keep this Polish-phase landing to what it was scoped to):
run the `verify` case of that parametrized test inside a temporary repository root (the same
fixture `tests/publication/` tests already use), or `monkeypatch` `pipeline.config.repo_root` for
the duration of that one parametrize case, so the assertion "every command returns a code from the
stable set" stops relying on mutating the real repository as a side effect of running `pytest`.

## 3. `pipeline/curate/assemble.py`'s documented source-model import exception (T161)

`tests/ip/test_stage_boundary.py` (T161) asserts no stage downstream of `normalize` imports
`pipeline.models.source` — except `pipeline/curate/assemble.py`, which imports
`SourceAcquisition`, `MfmUnitCostBlock`, and `MfmDetachmentCard` (none prose-bearing, but all
three are source-side by the module's own definition). The test pins this to an exact,
per-symbol allow-list (`KNOWN_EXCEPTIONS`) precisely so the exception cannot silently widen — but
it does not close the exception.

**Fix needed**: introduce a small `normalize`-owned projection (e.g. a
`NormalizedAssemblyContext` or similar, built once in `pipeline/normalize/` from the same
`SourceAcquisition`/`MfmUnitCostBlock`/`MfmDetachmentCard` records) carrying only the primitive
values `assemble.py` actually reads from them, so `curate` can consume that projection instead of
the source-side types themselves. That removes the exception entirely rather than merely fencing
it. Left as follow-up because it touches the `normalize` → `curate` boundary contract internally
and deserved its own review rather than riding along inside T161's cleanup pass.

## 4. `html` mode carries no publication id, so five chapters cannot be disambiguated (`004` T076)

The live `html`-mode build of 2026-08-05 exits `42` on datasheet coverage: **1 888 datasheets
against the published `mfm-2026-08` baseline's 2 099 — 89.95%, under the 90% floor**, on both
`datasheets` and `priced_datasheets`. Correcting the three faction-map detail slugs (see
`curation/README.md`) recovered 19 datasheets and moved the figure from 89.04% to 89.95%: real,
and 0.05 percentage points short of clearing the gate.

The largest identifiable recoverable component is **53 blocking `REC-AMBIGUOUS-MATCH` findings,
every one of them in a Space Marine faction** (9 each for Black Templars, Blood Angels, Dark
Angels, Space Wolves and the parent, 8 for Deathwatch). Each is a points-priced unit whose
normalised name matches two datasheets on the shared `space-marines` page, neither Legends. That
is the same collision `curation/README.md`'s provenance section already documents — and the field
that resolves it, `detail_source_publication_id`, **cannot resolve it under `html` mode**:
`pipeline/parse/wahapedia_html_dom.py` emits a `Source.csv` of exactly two rows and a `source_id`
of `current` or `legends`, because a datacard page states Legends as a class token on the card
and never states which publication a datasheet came from. So the five entries naming
`000000139`/`000000162` are inert, stage 2 has nothing to prefer with, and it correctly refuses
rather than guessing. Recovering those 53 would put datasheet coverage at roughly 92.5%.

**Not fixed here**, because it is a design question rather than a defect: the signal html mode
*does* carry is the card's own faction keywords, and preferring a chapter's datasheet by keyword
is a new rung on the D5 ladder — it needs its own contract wording, its own "never auto-apply a
fuzzy match" argument, and its own tests. The alternative, a `unit-map.json` entry per collision,
is stage 1 and already outranks everything below it: 53 curator-confirmed pairings would clear
the whole set today without any code change.

The remainder of the shortfall is not recoverable and should not be treated as a fault: 11th
edition publishes fewer datasheets than 10th, so a coverage ratio measured against a
previous-edition baseline is comparing two different editions' catalogues. That is the case for a
dated `curation/resolutions.json` entry when this candidate is raised, not for a threshold change.
