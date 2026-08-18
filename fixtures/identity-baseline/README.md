<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Authored the identity-baseline fixture and
     this README (009 task T014, Setup phase). Every value in the sibling JSON file is an
     identifier this project minted itself, extracted from the committed `data/wh40k-11e/` tree
     and `curation/abilities/`, not fetched from any source. -->
# `fixtures/identity-baseline/`

The complete set of consumer-facing identifiers the previous published version carries — nothing
else. For 009's US2 identity-survival test (`tasks.md` T049): every faction id, datasheet id, and
ability key here MUST be present, with the same identity, in a build performed under the CSV
acquisition migration. None may be renamed, re-suffixed, or dropped (FR-013, SC-004).

## Why this is committable

Every value is **this project's own identifier**, minted by `pipeline.reconcile.identity` or
authored in `curation/abilities/` — `f-<slug>`, `ds-<slug>[-N]`, `datasheet:<slug>` and friends —
never the publisher's wording. Committing the identifier set is exactly as safe as committing any
other curated file in this repository; it carries no name, no value, and no prose (compare
`curation/abilities/*.json`, which is excluded from this extraction precisely because its
`name`/`summary` fields are not identifiers).

## Provenance

Extracted from the committed `data/wh40k-11e/` tree and `curation/abilities/*.json` as they stood
at this branch's fork point (`main` at `816aa849`, the same commit `git log` names as this
worktree's base) — the pipeline's own already-governed, already-published output. No source page,
export file, or excerpt was fetched to build this file.

| File | Count |
|---|---:|
| `faction_ids` | 30 |
| `datasheet_ids` | 2083 |
| `ability_keys` | 2125 |

`rules_version_id: "wh40k-11e-2026-08-4"` names which published version this baseline was drawn
from — `site/manifest.json`'s own most recent, non-withdrawn entry at extraction time.

## What this is not

Not a full snapshot, not a regression fixture, and not a substitute for
`reports/wh40k-11e-2026-08-4/report.json` (which `curate/prior.py` already reads for the coverage
ratchet floors, FR-021). This file answers exactly one question — "which identifiers existed" —
and nothing about their values, prices, or wording.
