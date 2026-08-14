<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Documented every variable in
     pipeline/config.py's CONFIG_VARS table (task T146): default, effect, and the requirement it
     serves, cross-referencing the `purpose` string already in the code and the module
     docstring's FR references, per contracts/pipeline-run-interface.md §5.
     AI-Assisted: Claude Code (model: claude-opus-5) - Recorded the dotenv-quoting rule beside
     the resolution order (004 T076 follow-up), with the incident that made it a rule.
     AI-Assisted: Claude Code (model: claude-sonnet-5) - 006 T050: documented
     WGC_RATCHET_TOLERANCE_OPTIONS (the only new CONFIG_VARS entry T009 added — the
     equipment-vocabulary knob it considered turned out not to be needed, per research D1e's
     ≈99.5% coverage of the measured subject vocabulary with no tunable threshold) and the two
     `build` options `--published-at` / `--published-at-from-report` that follow-ups item 12
     added ahead of their owed pipeline-run-interface.md §1 amendment.
     AI-Assisted: Claude Code (model: claude-sonnet-5) - 007 T014: documented
     WGC_EQUIVALENCE_CHECK_ENABLED and recorded that the comparison's elision-word set is
     deliberately NOT a second environment variable — it is authored, versioned-with-the-check
     configuration, per contract §9.1's "not derived from any source page." -->
# Configuration

Every variable the pipeline reads is declared exactly once, in `pipeline/config.py`'s
`CONFIG_VARS` table. This page is that table in prose: what each variable defaults to, what it
actually changes about a run, and which requirement it exists to serve. If this page and
`pipeline/config.py` ever disagree, the code is authoritative — update this page to match it,
not the other way around.

## Resolution order

`pipeline.config.load_config` layers three sources, most general first (`pipeline/config.py`
module docstring):

1. the documented default (below),
2. the process environment — repository variables in CI,
3. a `--config <path>` JSON file — the per-run override a curator reaches for locally.

The CLI's `--channel` option, when given, overrides `WGC_DATA_CHANNEL` last, because it is the
most specific input of all.

**A value's own quoting is not part of the value.** A variable read from the environment loses
one matched pair of surrounding quotes (`pipeline.config.unquote_env_value`), because that is
what a `.env` file's quoting means and because a local run is configured from one. The reason it
is written down here rather than left as an implementation detail: on 2026-08-05 a `.env.local`
loaded by a hand-rolled `KEY=VALUE` split put the quotes *into* `WGC_MECHANIC_DIGEST_KEY`, so
every mechanic digest was computed under a key two characters longer than the one the curation
was authored under. Nothing failed. The run simply reported that all 1 703 approved ability
summaries in the snapshot needed re-review — a phantom campaign eight times the real figure of
203, and indistinguishable from an editorial one until the key was checked.

Every **non-sensitive** resolved name and value is logged (`PipelineConfig.log_resolved`).
Sensitive values are never logged, printed, or included in an exception message — only whether
they are set (`PipelineConfig.redacted`, Principle 7). See the dedicated section at the end of
this page.

## The variables

| Variable | Default | Effect | Requirement it serves |
|---|---|---|---|
| `WGC_MFM_BASE_URL` | `https://mfm.warhammer-community.com/en` | The points source's base URL — every faction-page fetch is resolved against it. | Points-source location (FR-001 acquisition). |
| `WGC_DETAIL_SOURCE_URL` | *(empty)* | The datasheet-detail source's location, read according to `WGC_DETAIL_ACQUISITION_MODE`: under `csv` it is the directory the export files sit in; under `html` it is the current-edition tree the sweep resolves `SiteMap.xml` and `factions/<slug>/datasheets.html` against (e.g. `https://wahapedia.ru/wh40k11ed`). Must be set for a live acquisition — an unset value is refused with `ExitCode.CONFIG_ERROR` (60) rather than interpreted, because an empty location under `csv` mode is a *relative path* and a relative path is the working directory. A fixture build never reads it. The previous-edition and staging trees are refused before a request is constructed, whatever this is set to (`pipeline/acquire/robots.py`). | Detail-source location; FR-004 permitted path. |
| `WGC_DETAIL_ACQUISITION_MODE` | `csv` | Which **shape** the detail source is read in: `csv` (the bulk export) or `html` (the current-edition datacard pages). A *variable, never a logic branch* — both arms emit the same `SourceAcquisition` and the same `file name -> CsvReadResult` mapping, so every stage below `acquire` is mode-blind and each grammar, linker and validator is written once. The mode selects a parser; **`WGC_DETAIL_EDITION` is what states which edition the content is**, and the two are set together when the edition is adopted. | Dual-mode detail acquisition (`004` research D1d, FR-003). |
| `WGC_MFM_EDITION` | `wh40k-11e` | The edition code declared for the points source's content. Stamped onto every entity's provenance and is one half of the `is_hybrid_edition` comparison. | Declared points edition (FR-005). |
| `WGC_DETAIL_EDITION` | `wh40k-10e` | The edition code declared for the detail source's content. The other half of the `is_hybrid_edition` comparison — see `pipeline/models/provenance.py`'s `EntityProvenance.is_hybrid_edition`. | Declared detail edition (FR-005). |
| `WGC_REQUEST_INTERVAL_MS` | `2000` | The minimum polite delay, per host, between requests (`pipeline/acquire/http.py`'s `PoliteClient._throttle`); jitter only ever adds to it. | Polite request rate (FR-007). |
| `WGC_MAX_RETRIES` | `2` | How many additional attempts a transient transport failure or a `5xx` response gets, at the same polite interval, never faster. A `403`/`429` refusal is never retried regardless of this value. | Retry ceiling that never escalates on refusal (FR-007). |
| `WGC_DETECT_CRON` | `0 9,21 * * *` | The cron expression documented as the detection schedule. `.github/workflows/detect.yml`'s own `schedule:` trigger is the actual mechanism that fires the sweep — this variable and that YAML value must be changed together, or they drift (see the comment in `detect.yml` recording exactly that risk). | Detection schedule (FR-051). |
| `WGC_DETECT_STALENESS_HOURS` | `48` | The window `pipeline/detect/staleness.py`'s `is_stale` checks: no *successful* `detect` run (exit `0` or `10`) within this many hours raises the staleness alarm, independent of what the last attempted check's own outcome was. | Staleness alarm (FR-055). |
| `WGC_COVERAGE_MIN_FACTION_RATIO` | `0.95` | The minimum proportion of the previous published version's faction count a new build must retain before `COVERAGE_COLLAPSE` (exit `42`) is raised instead of publishing. | Collapse threshold, factions (FR-009). |
| `WGC_COVERAGE_MIN_DATASHEET_RATIO` | `0.90` | Same mechanism, for datasheet count. | Collapse threshold, datasheets (FR-009). |
| `WGC_COVERAGE_MIN_PRICED_RATIO` | `0.90` | Same mechanism, for the proportion of datasheets that carry any price at all. | Collapse threshold, priced datasheets (FR-009). |
| `WGC_DATA_CHANNEL` | `prerelease` | Selects `prerelease` or `published`. This is the **only** difference between the two channels — it picks a manifest path and a release-tag prefix; there is no branch on channel name below the CLI entry point (`pipeline/config.py` module docstring; plan.md Environment gate). | Channel selector (FR-047). |
| `WGC_PUBLISHED_MANIFEST_PATH` | `manifest.json` | The Pages-relative path the `published` channel's manifest is written to and served from. | Published-channel manifest path. |
| `WGC_PRERELEASE_MANIFEST_PATH` | `prerelease/manifest.json` | Same, for the `prerelease` channel. | Pre-release-channel manifest path. |
| `WGC_SCHEMA_CONTRACT_VERSION` | `1` | Stamped into every published snapshot's `snapshotMeta`. This is the **MAJOR** of `reference-db-schema.md` (currently v1.2.0) — bumping it is a contract event, not a config tweak. | Consumer schema compatibility (FR-030). |
| `WGC_RESTRICTION_VOCABULARY_VERSION` | `1` | Stamped into `snapshotMeta` alongside the schema version, identifying which restriction-code vocabulary the snapshot's detachment/enhancement restrictions were written against. | Restriction-vocabulary compatibility. |
| `WGC_SUMMARY_MAX_CHARS` | `1000` | The target length ceiling for an authored ability summary. Raised from `240` by Product Owner decision on 2026-08-06 — full-fidelity summaries beat brevity, and a multi-clause mechanic stated completely is worth more than one that fits a phone line. The three sibling class targets (`WGC_FACTION_RULE_MAX_CHARS`, `WGC_DETACHMENT_RULE_MAX_CHARS`, `WGC_GLOSSARY_MAX_CHARS`) moved with it. `SUM-OVERLENGTH` is the advisory finding an approved summary over this length raises (`docs/authoring-summaries.md`). | Summary length target (FR-022). |
| `WGC_UNVERIFIED_ESCALATE_RELEASES` | `2` | How many consecutive releases a datasheet may carry `pricing_confidence: unverified` before the advisory `PRC-UNVERIFIED-STALE` finding fires — the early signal that a unit has quietly left the authoritative source's listing. | Unverified-pricing escalation. |
| `WGC_RATCHET_TOLERANCE_OPTIONS` | `0.00` | The proportion `pipeline/validate/gates.py`'s `COV-OPTION-REGRESSION` check allows `loadout.options_resolved` (the proportion of published datasheets whose `wargear_option_state` is `none` or `extracted`) to fall below the previous **published** version's own percent before it raises the blocking finding. Same shape as the four `WGC_RATCHET_TOLERANCE_*` variables above it, joining them unchanged. Deliberately the **only** variable `006-unit-loadout-fidelity` added: the 2026-08-09 clarification ratchets resolved-option coverage with no absolute ceiling, so no separate threshold knob exists for it, and an equipment-vocabulary knob was considered and dropped — the five subject productions cover ≈99.5% of the measured default-equipment sentences with nothing left to tune. `loadout.default_equipment` is reported every build but carries no ratchet and no tolerance variable in this first extended release, because there is nothing yet to compare it against. | Resolved-option coverage regression tolerance (006 FR-022). |
| `WGC_EQUIVALENCE_CHECK_ENABLED` | `true` | On/off switch for `007`'s build-time Part C equivalence check (`pipeline/validate/equivalence.py`): per published datasheet and per block, renders via `render/loadout.py`, reads the same block from the source card **in memory only**, and compares the two under `rendering-contract.md` §9's normal form. Accepted spellings are `true`/`false`/`1`/`0`, case-insensitive, trimmed; anything else is `ConfigError`. Always **advisory** — a mismatch never blocks publication (FR-022) — so this switch controls whether the check *runs* at all, not what happens when it finds a mismatch. **The comparison's elision-word set (contract §9 step 4) is deliberately NOT a second environment variable here.** It is authored, versioned-with-the-check configuration, because contract §9.1 requires the normal form to be "not derived from any source page" — an env override would let a run-time value do exactly that. | Build-time rendering equivalence check (007 FR-019..FR-022, plan.md Environment gate). |
| `WGC_NOTIFY_WEBHOOK_URL` | *(empty)* | **Sensitive.** See below. | Notification delivery (FR-052, FR-055). |
| `WGC_MECHANIC_DIGEST_KEY` | *(empty)* | **Sensitive.** See below. | Keyed mechanic digest (research D6, C6/R8). |

## The publication date: `build --published-at` / `--published-at-from-report`

Not a `CONFIG_VARS` entry — a `build` command option — but documented here because it resolves the
same configuration-table promise `curated-snapshot-format.md` §6 has made since `002`: that
`snapshotMeta.publishedAt` is "an explicit build input rather than `now`." Until `006`'s
`fix/published-at-input` change landed, nothing on the CLI could actually supply one; every build
silently stamped `datetime.now(UTC).date()` regardless.

| Option | Effect |
|---|---|
| *(neither given)* | `publishedAt` is today's UTC date. Correct for a **first** build of a candidate — `candidate.yml` passes neither option, so a fresh candidate still stamps its own build day. |
| `--published-at <YYYY-MM-DD \| YYYY-MM-DDTHH:MM:SSZ>` | An explicit date, for reproducing a historic build outside CI. Strict about the timezone: a local offset would make one real moment two different strings, and therefore two different checksums, for the same approval. |
| `--published-at-from-report` | Reads the date out of **this checkout's own** `reports/<rulesVersionId>/report.json`, which `candidate.yml` commits beside `data/` at candidate-build time. This is the option `publish.yml`'s rebuild step passes, so the date the approval names travels with the approved commit rather than with whatever day the dispatch happens to land on. |

Both options are mutually exclusive with each other and refuse a malformed or missing date with
`ExitCode.CONFIG_ERROR` (`60`) rather than falling back to the clock — a silent fallback is exactly
the defect this pair replaces. Neither is yet a declared row of `contracts/pipeline-run-interface.md`
§1 (frozen at 1.0.2); `pipeline/cli.py`'s `PUBLISHED_AT_OPTIONS` and `tests/contract/
test_cli_surface.py`'s `PENDING_CONTRACT_COMMAND_OPTIONS` hold them apart from the contract's own
declared set for exactly that reason (`docs/follow-ups.md` item 12). See `docs/runbook.md`'s "The
publication date, and the exit 51 that is not a content change" for the operational read of what to
do when a publish run exits `51` after this fix.

## What is deliberately *not* here

**The custom point-limit range (`500`..`5000`) is not a pipeline variable.**
`reference-db-schema.md` §3.4 declares that range as the single source of truth shared with the
consuming app (C7/R9), and the pipeline reads it from that frozen contract rather than from its
own configuration. This is stated explicitly at the end of `pipeline-run-interface.md` §5's
configuration table and restated in `pipeline/config.py`'s own module docstring: making the range
a `WGC_*` variable would be exactly the silent divergence between producer and consumer that the
contract's "single source of truth" resolution was written to close. If the range ever needs to
change, that is a contract revision coordinated with `001-army-builder-app`'s maintainers
(`docs/contracts.md`), never a value edited in this repository alone.

The channel's *behaviour* is likewise not configuration in any deeper sense than a path selector:
`WGC_DATA_CHANNEL` picks a manifest path and a release-tag prefix and nothing else. There is no
`if channel == "published"` branch anywhere below the CLI entry point that changes what the
pipeline computes.

## Sensitive configuration

Two variables are marked `sensitive: True` in `CONFIG_VARS` and are held to a stricter standard
than every other row above: **secret-store only, never logged, never committed.**

| Variable | Purpose |
|---|---|
| `WGC_NOTIFY_WEBHOOK_URL` | The destination `pipeline/observability/notify.py` posts curator notifications and alerts to (a raised candidate, a detection or integrity fault, the staleness alarm). Optional — an unconfigured webhook makes notification a documented no-op (`send_notification` returns `False`) rather than a failure, so a curator running locally against fixtures never sees a delivery failure for a destination nobody configured. |
| `WGC_MECHANIC_DIGEST_KEY` | The HMAC-SHA256 key `pipeline/normalize/mechanic_digest.py` uses to compute the keyed digest that detects when an ability's underlying mechanic has moved since a summary was last approved (`docs/authoring-summaries.md`'s "Staying current" section). Keyed rather than a plain hash specifically so the digest can never be used to reconstruct or confirm a guess at the publisher's wording (research D6, C6/R8). |

What "never logged" means concretely:

- `PipelineConfig.redacted()` — the function every logging and diagnostic path goes through —
  replaces a sensitive value with `<redacted> (set)` or `<redacted> (unset)`. The literal value
  never reaches `PipelineConfig.log_resolved()`'s output.
- `pipeline/observability/notify.py`'s own module docstring states the same discipline for
  `WGC_NOTIFY_WEBHOOK_URL` specifically: "never logged, printed, or included in an exception
  message." `.github/workflows/detect.yml` and `integrity.yml` each add a second, independent
  check — a step that greps the notification job's own captured output for the literal secret
  value and fails the job if it appears, even though GitHub already masks a registered secret in
  the raw log view.
- Both variables are supplied to CI exclusively as GitHub Actions secrets (`secrets.
  WGC_NOTIFY_WEBHOOK_URL`), never as repository variables, and neither has a default other than
  the empty string — there is no working value checked into this repository or any fixture that
  would function as a real secret.
