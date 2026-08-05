<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Documented every variable in
     pipeline/config.py's CONFIG_VARS table (task T146): default, effect, and the requirement it
     serves, cross-referencing the `purpose` string already in the code and the module
     docstring's FR references, per contracts/pipeline-run-interface.md §5. -->
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

Every **non-sensitive** resolved name and value is logged (`PipelineConfig.log_resolved`).
Sensitive values are never logged, printed, or included in an exception message — only whether
they are set (`PipelineConfig.redacted`, Principle 7). See the dedicated section at the end of
this page.

## The variables

| Variable | Default | Effect | Requirement it serves |
|---|---|---|---|
| `WGC_MFM_BASE_URL` | `https://mfm.warhammer-community.com/en` | The points source's base URL — every faction-page fetch is resolved against it. | Points-source location (FR-001 acquisition). |
| `WGC_DETAIL_SOURCE_URL` | *(empty)* | The datasheet-detail source's location, read according to `WGC_DETAIL_ACQUISITION_MODE`: under `csv` it is the directory the export files sit in; under `html` it is the current-edition tree the sweep resolves `SiteMap.xml` and `factions/<slug>/datasheets.html` against (e.g. `https://wahapedia.ru/wh40k11ed`). Must be set for a live acquisition; a fixture build never reads it. The previous-edition and staging trees are refused before a request is constructed, whatever this is set to (`pipeline/acquire/robots.py`). | Detail-source location; FR-004 permitted path. |
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
| `WGC_SUMMARY_MAX_CHARS` | `240` | The target length ceiling for an authored ability summary. `SUM-OVERLENGTH` is the advisory finding an approved summary over this length raises (`docs/authoring-summaries.md`). | Summary length target (FR-022). |
| `WGC_UNVERIFIED_ESCALATE_RELEASES` | `2` | How many consecutive releases a datasheet may carry `pricing_confidence: unverified` before the advisory `PRC-UNVERIFIED-STALE` finding fires — the early signal that a unit has quietly left the authoritative source's listing. | Unverified-pricing escalation. |
| `WGC_NOTIFY_WEBHOOK_URL` | *(empty)* | **Sensitive.** See below. | Notification delivery (FR-052, FR-055). |
| `WGC_MECHANIC_DIGEST_KEY` | *(empty)* | **Sensitive.** See below. | Keyed mechanic digest (research D6, C6/R8). |

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
