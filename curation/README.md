<!-- AI-Assisted: Claude Code (model: claude-opus-5) - Documented the authored tree and the
     provenance of the seeded values (tasks T074, T075). This file carries the Principle 16
     header for the JSON files beside it, which admit no comment syntax of their own. -->
<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Documented why the Black Templars
     faction-map entry alone carries detail_source_publication_id (curation/faction-map.json
     has no _comment field of its own, so this file records the change for it; the schema file,
     schemas/curation/faction-map.schema.json, does have its own _comment and its header was
     extended directly). -->
<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Recorded the mfm-2026-08 curation round:
     the core-codex detail_source_publication_id now carried by the five Space Marine entries
     that are not Black Templars, and the two dated REC-NEVER-PRICED exclusions seeded into
     curation/resolutions.json. Both JSON files admit no comment syntax of their own, so their
     rationale lives here. -->
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

**Black Templars alone also carries `detail_source_publication_id: "000000162"`.** All five
Space Marine chapters share the detail source's `SM` faction id with the core codex, so stage 2
of the match ladder (`pipeline/reconcile/match.py`) scopes candidates to all of `SM` for each of
them. In practice this collides for Black Templars specifically: its own supplement publication
(`source_id 000000162`) republishes several datasheets under the same or near-identical name as
their core-Codex-Space-Marines twin (`source_id 000000139`) — a Chaplain-type unit is one
example — and neither copy is Legends, so the existing Legends-flag narrowing cannot separate
them either. `detail_source_publication_id` records the chapter's own publication id so stage 2
can prefer the datasheet published there when, and only when, that preference narrows the
candidates to exactly one; otherwise it falls through to `REC-AMBIGUOUS-MATCH` unchanged.

**The other five Space Marine entries carry `detail_source_publication_id: "000000139"` — the
core codex — for the same reason, in the opposite direction.** That collision was observed for
real on the first `mfm-2026-08` candidate build, which raised 44 blocking
`REC-AMBIGUOUS-MATCH` findings: nine vehicles and squads that the Black Templars supplement
republishes verbatim under the shared `SM` detail-source faction id, each seen twice by every
chapter that is *not* Black Templars, plus by the parent faction itself. Black Templars was
already unaffected — its own entry prefers the supplement. So `f-space-marines`,
`f-blood-angels`, `f-dark-angels`, `f-deathwatch` and `f-space-wolves` now name the core codex,
which is the copy each of them is entitled to.

This is evidence-led rather than pre-emptive, which is the standard the Black Templars entry set
and is worth restating: the nine collisions above are the **only** duplicate normalised names
anywhere in the `SM` detail-source faction, and in every one of them the pair is exactly one
core-codex datasheet and one Black Templars supplement datasheet. No chapter's own supplement
republishes a core-codex name, so no chapter can lose its own datasheet to this preference. The
narrowing is also inert unless a name is genuinely ambiguous — stage 2 reaches it only after an
exact match has already found two or more candidates and the Legends flag has failed to separate
them — so a chapter-specific unit with a unique name never consults it at all.

State the residual risk plainly, because it is the price of the preference: if a chapter's own
supplement ever republishes a core-codex *name*, this field will quietly pick the core-codex
copy for that chapter rather than raise a finding — a preference that resolves to exactly one
candidate is indistinguishable, at that point in the ladder, from a preference that resolves to
the right one. That case does not exist in the data today and the check for it is cheap: the
`SM` faction's duplicate normalised names, grouped by publication. When it does appear, the fix
is a `unit-map.json` entry, which is stage 1 and outranks every rung below it.

**`resolutions.json` is seeded with two `REC-NEVER-PRICED` exclusions, and nothing else.** Both
came off the same first `mfm-2026-08` candidate build, and both are the honest answer to "no
source has ever published a price for this", which is what that finding says and why it blocks:
a unit shipped at zero points is worse in a player's list than one that is absent. The two here
are not units.

* One is an Epic Hero **infantry** character datasheet in the knightly faction — a companion
  model that belongs to another unit's datasheet. The detail source's own cost export carries no
  row for it at all, and the points source's faction page has no entry that could be its renamed
  self: every unit that page prices matched a datasheet, so there is no leftover name for a
  rename to be argued from. No source prices it because none is meant to.
* The other is an upstream placeholder row in the datasheet export: flagged `virtual`, with an
  empty publication id, an empty role, and no cost row anywhere. It is the export's own example
  record, not a datasheet.

Neither is a rename, so neither gets a `unit-map.json` entry — inventing a pairing to silence a
finding is precisely the fabrication FR-019 exists to prevent. And a resolution is not a mute
button: it is bound to the finding's `data_digest`, so if either row ever gains a publication, a
cost, or a faction, the digest moves, the resolution lapses, and the finding blocks again with
nobody having to remember to look. Both stay visible in every report as suppressed, with the
explanation above, so an approver can see what was waved through and why.

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
