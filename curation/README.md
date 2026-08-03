<!-- AI-Assisted: Claude Code (model: claude-opus-5) - Documented the authored tree and the
     provenance of the seeded values (tasks T074, T075). This file carries the Principle 16
     header for the JSON files beside it, which admit no comment syntax of their own. -->
# `curation/` — the authored tree

**Humans write this directory. The pipeline never does.** The pipeline writes `data/` and never
`curation/`; CI enforces both directions, and `pipeline/curate/authored.py` refuses at the moment
a path is opened rather than waiting for a diff.

That boundary is not bookkeeping. It is what makes FR-017's and FR-024's carry-forward guarantees
**structural**: a rebuild rewrites `data/` wholesale and *physically cannot* clobber an approved
ability summary, so a curator's editorial work survives every release without anyone remembering
to preserve it.

Every file is validated against `schemas/curation/*.schema.json` when it is read, so a hand edit
fails fast with a path and a message rather than producing a snapshot with a quietly wrong band.

## The files

| File | What it decides | Seeded by |
|---|---|---|
| `faction-map.json` | Which curated faction each points-source slug is, which detail-source faction supplies its datasheets, and which chapters hang off which parent | T074 |
| `game-sizes.json` | The point bands and their detachment-point budgets | T075 |
| `edition-rules.json` | Edition-level construction rules | T075 |
| `unit-map.json` | Confirmed unit pairings, consulted before any name is compared | curator, per confirmation |
| `unit-aliases.json` | Spellings a curator has confirmed once | curator |
| `copy-limits.json` | `max_copies_per_army`, which no upstream source publishes | curator |
| `detachment-restrictions.json` | Machine-evaluable restrictions, likewise unpublished upstream | curator |
| `abilities/<faction-id>.json` | The authored, mechanics-only ability summaries | curator (US5) |
| `resolutions.json` | Dated finding resolutions, which lapse when the data moves | curator |

## Provenance of the seeded values

**`faction-map.json` is derived from the two sources' own taxonomies**, which genuinely disagree:
the points source publishes 30 faction pages, the detail source carries 26 faction ids. The
mapping states the correspondence rather than deriving it, because no rule derives it. Five
chapters — Black Templars, Blood Angels, Dark Angels, Deathwatch and Space Wolves — are separate
points-source pages whose datasheet detail is filed under the parent, so each carries
`parent_faction_id: f-space-marines` and the consumer contract's §3.5 ancestor query rule is what
makes a chapter army see its parent's units. Two detail-source faction ids (`UN`, `UA`) are
referenced by no mapping and are reported as `REC-DETAIL-FACTION-ORPHAN`, which is advisory: a
faction the points source does not publish is not one a player can field.

**`game-sizes.json` and `edition-rules.json` are authored, not extracted.** No upstream source
publishes a machine-readable band table or construction-rule set — that gap is recorded in
`reference-db-schema.md` §5 as a known one the producer must curate. The bands below are
contiguous and non-overlapping and cover `500`..`5000` end to end, which is what V3 checks, and
they carry the conventional battle-size names and budgets:

| Band | Points | DP budget | Detachments | Enhancements |
|---|---|---|---|---|
| Combat Patrol | 500-999 | 3 | 1 | 1 |
| Incursion | 1000-1999 | 6 | 2 | 2 |
| Strike Force | 2000-2999 | 9 | 3 | 3 |
| Onslaught | 3000-5000 | 12 | 4 | 3 |

> **Confirm before the first publication.** These budgets are the pipeline's working values, not
> a transcription of a published table, and the product owner should confirm them against the
> edition in play before a candidate is approved. They are stated here rather than left implicit
> precisely so the confirmation has something to point at. The `500`..`5000` bounds are **not**
> negotiable here: `reference-db-schema.md` §3.4 declares them normative and shared with the app,
> and changing them is a contract revision on both sides.
