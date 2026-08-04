<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Recorded three items surfaced while
     landing the Polish phase (T146-T162): one operational setup step the settings-drift checker
     (T148) depends on but cannot perform itself, one pre-existing test-hygiene defect the T161
     stage-boundary audit exposed, and the stage-boundary exception T161 documented but did not
     resolve. None of these block acceptance; all three are named here so they are not lost. -->
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
