<!-- AI-Assisted: Claude Code (model: claude-opus-5) - Re-recorded the FR-020 consumer-compatibility
     evidence for the re-authored wh40k-11e-2026-08-2 candidate (006 tasks T045, T046), after the
     T048 default-equipment fix invalidated the 2026-08-11 candidate.
     AI-Assisted: Claude Code (model: claude-opus-5) - Re-recorded again on 2026-08-12 for the
     T049 keyword-cell fix, which invalidated the bundle this file described. Both consumers were
     re-run against the new bundle, sha256 7ab360b1...93db9d; §2's array table, §3's dist figures,
     §4's drift table and §5 are restated from those runs, and §5 stops being an open question.
     Both consumers unmodified: tools/consumer_compat.py at its deliberate v1.2.0 pin, and the
     released 003/005 site build at wargame-rules-web 2cbbf36 with a clean working tree. -->
# Consumer compatibility — `wh40k-11e-2026-08-2`

**This candidate's bundle**: `rules-wh40k-11e-2026-08-2.json`,
sha256 `7ab360b180181b2536a97946a0d2334b75ed9afc642019a629edb3c19393db9d`, 11 253 406 bytes,
`bundleFormatVersion` 1, `snapshotMeta.schemaContractVersion` 1.

**Baseline it is compared against**: the published `wh40k-11e-2026-08`,
sha256 `f9ad67b34c5d4f2beb3089d495916ed812aef30c0f9d85e9d4625418ffcce566`, 9 401 976 bytes,
checksum-matched against the channel manifest before use.

**Why this file was re-recorded, twice.** The candidate of 2026-08-11 (`6f30c6b5…8443d4`)
published `defaultEquipmentState` absent on 647 datasheets whose cards the pipeline had in fact
read end to end — `reports/006-t048-triage/default-equipment-omission.md` has that classification.
The candidate of 2026-08-12 morning (`76d37f2b…88b35c`) fixed it and published 356
`datasheetKeywords` rows whose value was two keywords joined by a printed separator, which is §5
below. Both consumer proofs were re-run against each fixed build rather than carried forward.

**This file is hand-authored evidence, not pipeline output.** The build does not produce it and a
later rebuild will not regenerate it. Read every claim as "a person ran this command and this is
what it printed", and re-run anything you would otherwise take on trust.

## Verdict in one line

**Both consumers pass, unmodified, against the re-authored candidate: `consumer_compat.py` exits 0
with zero violations, and the released site build produces 2 462 pages with `verify-dist` green on
all four checks.** Two things a reviewer must still read: a site-side display precedence change on
six pages (§3.1), unchanged since the 2026-08-11 candidate, and the live-source drift of §4.

## 1. App-side ingest (T045) — **PASS**

```bash
python -m tools.consumer_compat rules-wh40k-11e-2026-08-2.json   # exit 0, no violation lines
python -m tools.consumer_compat rules-wh40k-11e-2026-08.json     # exit 0, no violation lines
```

`tools/consumer_compat.py` is **unmodified and deliberately pinned at schema contract v1.2.0**
(`git diff HEAD -- tools/consumer_compat.py` is empty). That pin is the whole point: it stands in
for a consumer built against the released schema, so what it proves is that this candidate is
ingestible by software that predates every addition in it. It builds the v1.2.0 schema verbatim,
loads each array into its table, turns on real foreign keys, and reports rather than dies on the
first collision.

| Guarantee exercised | Result |
|---|---|
| 12 — one row per declared primary key, every table | pass, zero duplicate keys |
| 4 — foreign keys resolve under `PRAGMA foreign_keys=ON` | pass |
| 3 — cost bands contiguous, every tier has its cost row | pass |
| 5 — no ability row carries an empty summary | pass |

It knows **none** of the three arrays this release adds — `datasheetOptionChoiceItems`,
`datasheetEquipmentGroups`, `datasheetEquipmentItems` — and none of the new optional columns,
`defaultEquipmentState` among them. It does not have to: an array a consumer has never heard of is
ignored by a consumer that loads the tables it declares. **That it passes while not knowing about
them is the additive-compatibility proof**, and the fix makes that proof larger rather than
smaller: 2 017 datasheets now carry the column this ingestor does not read, where the previous
candidate had 1 426. The same run over the previous published bundle behaves identically, so the
check's own behaviour is not what changed.

The pricing exercise reports `pricing exercise skipped` on both bundles, exactly as it did for
`wh40k-11e-2026-08`. That is expected and is not a gap: the exercise army is composed of the
minimal synthetic fixture's entities, which no real bundle carries. The schema construction, the
load, the foreign-key pass and the four guarantees above all ran against the real 11.2 MB bundle.

## 2. Array-level diff against the published bundle

Every array both bundles carry, compared row by row as canonical JSON, both files read as UTF-8:

| Array | Published | Candidate | Moved |
|---|---:|---:|---|
| `datasheetOptionChoices` | 4 338 | 5 140 | **−0, +802** |
| `datasheetOptionGroups` | 2 370 | 2 773 | −21, +424 |
| `datasheets` | 2 084 | 2 084 | −2 071, +2 071 (same rows, new optional columns) |
| `datasheetOptionChoiceItems` | *absent* | 6 305 | new array |
| `datasheetEquipmentGroups` | *absent* | 2 206 | new array |
| `datasheetEquipmentItems` | *absent* | 5 631 | new array |
| `datasheetAbilities` | 7 909 | 7 909 | −1, +1 (§4) |
| `datasheetKeywords` | 14 060 | 14 456 | −293, +689 (§5) |
| `datasheetLeaderPairs` | 1 291 | 1 313 | −24, +46 (§4) |
| `detachmentRules` | 324 | 324 | −1, +1 (§4) |
| every other array (19 of them) | — | — | **byte-identical** |

The 19 byte-identical arrays are `chapterKeywords`, `datasheetCompositions`,
`datasheetCostContexts`, `datasheetCostTiers`, `datasheetCosts`,
`datasheetDetachmentEligibility`, `datasheetModels`, `datasheetWargearOptions`,
`datasheetWeapons`, `detachmentRestrictions`, `detachments`, `editionRules`, `editions`,
`enhancementEligibility`, `enhancements`, `factionRules`, `factions`, `gameSizeRules` and
`keywordGlossary`.

Reading the three rows that matter:

- **`datasheetOptionChoices`: −0.** Not one option choice the published bundle carried changed in
  any field. 802 rows were added and nothing was removed or rewritten. This is FR-009's promise,
  and `option-regression.md` is the field-level proof behind it.
- **`datasheetOptionGroups`: −21, +424.** The 21 removals are the same 21 groups
  `option-regression.md` lists under *Corrected*, re-emitted with the `maxChoices` value `004`
  declared and never populated. The remaining 403 additions are new groups.
- **`datasheetKeywords`: −293, +689.** Every one of the 293 removed rows held more than one
  keyword joined by a printed separator — 255 held two and 38 held three — and the 689 additions
  are those same keywords listed one per row. Measured rather than asserted: expand every
  published row on its separators and the resulting multiset of
  `(datasheetId, keyword, isFactionKeyword, modelScope)` is a **subset of the new array with
  nothing left over** — 0 rows lost — and the new array's only surplus is 65 rows of one Aeldari
  faction keyword, which is the source drift of §4. See §5.
- **`datasheets`: −2 071, +2 071.** Exactly two fields move across the whole array, and both are
  optional columns a v1.2.0 consumer does not read: `defaultEquipmentState` on 2 064 rows (it was
  absent everywhere in the published bundle) and `wargearOptionState` on 240 rows — which is
  precisely the 1 916 − 1 676 datasheets whose options newly resolve. 13 rows are byte-identical
  to the published bundle. **No other field of any datasheet row changed.**

## 3. Site-side build (T046) — **PASS, with a display change a reviewer must see**

```bash
# The unmodified released 003/005 site build, wargame-rules-web at 2cbbf36, working tree clean,
# nothing modified and nothing committed there. Run once per bundle from the same checkout.
CI=1 WGC_WEB_CHANNEL=published \
  WGC_WEB_MANIFEST_URL=/path/to/a/local/manifest/naming/the/bundle.json \
  npm run build      # astro check && astro build && build-info && verify-dist
```

```
2462 page(s) built
verify-dist: OK. 2462 page(s) checked against 2461 expected route(s): coverage, internal links,
content boundary, and banner presence all pass (rules version wh40k-11e-2026-08-2,
withdrawn false).
```

`bundleFormatVersion` and `snapshotMeta.schemaContractVersion` are both asserted by the loader
before a page is rendered, and both pass. The same build was run against the previous published
bundle first, from the same clean checkout, and also produced 2 462 pages with `verify-dist` green
— so the two `dist/` trees are directly comparable.

**The equipment half of this release is invisible to this consumer, and that is the point.** The
released site knows no equipment array and no `defaultEquipmentState`: `grep -ri equipment src/`
matches nothing, and **not one of the 2 462 built pages contains the word**. The largest change in
this candidate — 2 206 equipment groups and 5 631 equipment items, 632 datasheets carrying a group
for the first time — passes through the released site without altering a single byte of output.
An additive release is one an existing consumer can ignore, and this one measurably ignores it.

**`dist/` comparison, previous published vs this candidate**, with the version id, the publication
date and the bundle sha256 that every page's banner carries normalised away:

- **2 462 pages built by both. Zero pages added, zero pages removed, zero routes changed.**
- **1 835 files are byte-identical** after that normalisation.
- **627 pages differ: +13 726 / −427 lines**, counted at one HTML tag per line. Every one is under
  `factions/`. Most of the additions are the option half of the feature — new option groups, their
  eligibility scope and their per-item rows — rendering for the first time; the rest are keyword
  list items that used to share a line with another keyword.

**The 427 removed lines are accounted for, every one:**

| Removed text | Lines | Pages | Why |
|---|---:|---:|---|
| a keyword list item holding two or three keywords | 293 | 293 | the T049 fix — each is replaced by one list item per keyword, §5 |
| `Invader ATV` + `+60` | 12 | 6 | the display-precedence finding below |
| Space Wolves leader-pairing list items (3 distinct leaders) | 16 | 16 | source drift (§4) |
| other leader-pairing, ability and detachment-rule lines | 11 | 11 | source drift and one correction (§4) |
| markup-only lines carrying no text | 95 | 18 | the shape of the diffs above |

1. **Six pages stop showing a priced legacy wargear row** — `outrider-squad` and its five chapter
   variants. The site's unit template reads
   `showWargearFallback={optionGroups.length === 0}`: the legacy `datasheetWargearOptions` table is
   a **fallback** shown only when a datasheet has no structured option group. All six of these
   datasheets acquired their first resolved option group in this candidate, so the fallback
   switches off and the priced row it carried — *Invader ATV, +60 points* — is no longer displayed.
   The row is **still in the bundle**: `datasheetWargearOptions` is byte-identical at 7 rows, and
   the structured group that displaces it describes a different option (a weapon swap) the points
   source does not price.
   **This is a site-side precedence rule meeting newly-resolved data, not a bundle regression**,
   and it is a `wargame-rules-web` follow-up (render both, or merge them) rather than something
   this repository can fix. It is unchanged from the previous candidate — the option arrays are
   byte-identical between the two — so a reviewer who already considered it need not reconsider it.

## 4. Live-source drift, which this feature did not cause

The published baseline was acquired on 2026-08-07 and this candidate on 2026-08-12. Four rows moved
for reasons that have nothing to do with spec 006, and an approver should judge them as source
changes rather than as pipeline output:

| What moved | Detail |
|---|---|
| `datasheetKeywords` +65 | An Aeldari faction-keyword cell now lists two keywords where it listed one, on 65 datasheets. Those 65 datasheets each gain one keyword row. This is the only keyword movement that is source drift; the other 396 rows §2 counts are the T049 fix, §5. |
| `datasheetLeaderPairs` −24 / +46 | Leader eligibility changed upstream. Removals concentrate on `ds-ravenwing-command-squad` and Space Wolves characters; additions spread across jump-pack assault squads. |
| `datasheetAbilities` −1 / +1 | `ds-imperial-space-marine`'s core ability is now `Support` where it was `Leader`; the summary follows the mechanic and is otherwise the same shape. |
| `detachmentRules` −1 / +1 | `d-lions-blade-task-force`'s rule name was published with a mis-decoded UTF-8 apostrophe and now reads correctly. A correction, and one instance of the encoding defect item 12 of the spot-check package leaves open. |

None of the four touches a cost, a tier, a composition row, a weapon line, an option choice or an
equipment group. `datasheetCosts`, `datasheetCostTiers`, `datasheetCostContexts`,
`datasheetWeapons`, `datasheetModels`, `datasheetCompositions`, `enhancements`, `detachments` and
`factions` are all byte-identical between the two bundles.

Measured against the **previous candidate** (`76d37f2b…88b35c`, built 2026-08-12 morning) rather
than the published bundle, **nothing drifted at all**: all 30 bundle arrays except
`datasheetKeywords` are byte-identical to it, compared as raw UTF-8 slices — `datasheets`,
`datasheetEquipmentGroups`, `datasheetEquipmentItems`, all four option arrays, `datasheetWeapons`,
`datasheetModels`, `datasheetCompositions`, `datasheetCosts`, `datasheetLeaderPairs` and
`chapterKeywords` among them — and the bundle checksum was reproduced identically by four
independent live sweeps across the two builds. `datasheetKeywords` is the only array the T049 fix
touches.

## 5. Answered — the keyword cell that held two keywords is split

The previous candidate published 356 `datasheetKeywords` rows whose `keyword` value was two or
three keywords joined by a printed separator, so a consumer filtering on any one of them by exact
name found nothing. 291 of those rows are in the **published** release too: the 65 Aeldari rows
were only the subset the 2026-08-11→12 source drift added, and they stood out because their joined
value was one the keyword classifier had not seen.

The cause was not a comma inside a cell. Each keyword is a run of `span.kwb` elements, and what
separates two of them is whatever the page prints between the runs — `;` between ordinary
keywords, but `, ` in its own filter span before a detachment-conditional keyword, and `:` before
a conditional group appended to a model-scoped list. The parser split the flattened cell text on
`;` alone. It now splits on the boundary instead: **a keyword is a run of `span.kwb`, and the
separator is any non-whitespace text printed between two runs** — no separator character is
enumerated, because a keyword's own name may contain one.

**Nothing is lost and nothing is renamed.** Expanding every published row on its separators gives
a multiset of `(datasheetId, keyword, isFactionKeyword, modelScope)` that the new array contains
in full, with 0 rows left over, and the new array's only surplus is the 65 drift rows of §4. On
the site, 293 pages replace one keyword list item with two or three, and every difference between
the two `dist/` trees is inside a keyword list.

**One consequence a reviewer must weigh**, and it is why `curation/resolutions.json` gained its
first non-`REC-NEVER-PRICED` entry. The `keyword_classification` coverage check compares a raw
*count* of classified keywords with the previous release's, and 144 of the values it counted last
time were composites this candidate no longer invents. The count therefore falls 1 449 → 1 371,
94.6% of the previous, under the 95% floor, and the build raises `COV-COLLAPSE`. The collapse is
not real: all 144 values dropped carry a printed separator, the 66 gained are the real keywords
they hid and all 66 are classified, distinct **unclassified** keywords is 18 in both releases, and
the classified proportion is 98.8% then against 98.7% now. The resolution recording that is dated
and bound to the digest of exactly this pair of numbers, so it lapses the moment either moves —
and `resolved_by` says in as many words that it is **drafted, not signed off**. Deleting that one
JSON object re-blocks the build.

## What a reviewer should still do

`verify-dist` cannot see §3.1 — it checks coverage, links, the content boundary and the banner, and
a page that renders one true thing instead of another true thing passes all four. That judgement is
T048's, and it is the reason this section exists rather than a green tick.

Two decisions this file cannot make for a reviewer:

1. **§3.1**, unchanged: six pages stop showing a priced legacy wargear row because the structured
   option group that displaces it is a different option.
2. **§5's resolution.** The build is `advisory_only` and exits 20 *because* a dated resolution
   covers the `COV-COLLAPSE` on `keyword_classification`. It is drafted, not signed off. Confirm
   the reasoning or delete the entry — deleting it returns the build to exit 42, blocked.
