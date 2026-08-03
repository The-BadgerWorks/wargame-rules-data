<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Repository README stating what this data
     set is, its factual source attribution, the explicit non-endorsement statement, and the two
     write-boundary invariants, per Setup task T006 (FR-050, spec Policy and Safety Constraints). -->
# wargame-rules-data

Curated, IP-stripped, mechanical-only rules data for
[WargameCompanion](https://github.com/The-BadgerWorks/WargameCompanion) — a companion army-list
builder app. This repository holds the pipeline that produces it and the versioned JSON
snapshots it publishes.

## What this is

A data set of unit points, detachment costs, enhancement costs, and datasheet structure for a
tabletop miniatures wargame, reconciled from two publicly available third-party sources and
reduced to mechanical values only: numbers, ids, and short original mechanics summaries written
from scratch. It contains **no rules text, no stratagems, no missions, no lore, and no artwork**
from any publisher. Ability summaries are authored in-house, mechanics-only, and are never a
paraphrase — machine or human — of any publisher's wording.

## What this is not

**This project is not official, is not licensed, and is not endorsed by, or affiliated with,
any publisher of the source material it reconciles.** It is an independent, fan-made data set
produced for personal, non-commercial companion-app use. All trademarks and copyrighted rules
text remain the property of their respective owners.

## Sources

Two upstream sources, each authoritative for a different slice of the data (see
`specs/002-rules-data-pipeline/plan.md` in the `WargameCompanion` repository for the full
reconciliation design): a publicly published points-and-costs reference (authority for unit
points, detachment point costs, and enhancement costs) and a community-run datasheet-detail
export (authority for datasheet structure). Both are accessed politely and at a low request
rate, honouring `robots.txt` in every case.

## The two invariants this repository enforces structurally

1. **Raw acquired source material is never committed to any repository.** Ephemeral working
   state lives only in the gitignored, always-emptied `work/` directory. No publisher wording
   ever reaches curated data, intermediate artifacts, version control, logs, or reports.
2. **The `data/` <-> `curation/` write boundary never moves.** The pipeline writes `data/` and
   never `curation/`; humans write `curation/` and never hand-edit `data/`. CI enforces both
   directions, which is what makes rebuilds safe to run at any time without clobbering authored
   content.

## Repository layout

See `specs/002-rules-data-pipeline/plan.md` (in `WargameCompanion`) for the full design. In
short: `pipeline/` is the Python package; `data/` is the machine-written curated tree;
`curation/` is the human-authored tree; `state/`, `reports/`, and `site/` hold operational
state, per-version reports, and the two published manifest channels; `fixtures/` holds synthetic
(never real) test sources; `.github/workflows/` holds the detection, candidate, publish,
withdraw, and integrity automation.

## Getting started

See `specs/002-rules-data-pipeline/quickstart.md` (in `WargameCompanion`) for bootstrap, local
runs, the curator's authoring loops, and the publish/withdraw procedures.
