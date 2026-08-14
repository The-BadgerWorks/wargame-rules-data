<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Recorded the FR-020 consumer-compatibility
     evidence for the wh40k-11e-2026-08-3 candidate (007 task T064), against the real bundle built
     from the live corpus (PR #17, candidate/wh40k-11e-2026-08-3) and the actually-published
     wh40k-11e-2026-08-2 release asset downloaded via `gh release download` for an authoritative
     diff. This file is hand-authored evidence, not pipeline output — the build does not produce
     it and a later rebuild will not regenerate it. -->
# Consumer compatibility — `wh40k-11e-2026-08-3`

**This candidate's bundle**: `rules-wh40k-11e-2026-08-3.json`,
sha256 `3aa1043d580780db05696024b42dfcd8cc5e7daf621db991b04df27aec4adebf`, 11 635 213 bytes,
`bundleFormatVersion` 1, `snapshotMeta.schemaContractVersion` 1. Built live (`.env.local`,
`WGC_DETAIL_EDITION=wh40k-11e`, `WGC_DETAIL_ACQUISITION_MODE=html`) from
`007-loadout-display-fidelity` at the commit `candidate/wh40k-11e-2026-08-3` was pushed from.
`rules-pipeline build` exit code **20** (valid candidate, advisory findings attached — no
blocking finding; see the PR body's own "Blocking findings: None").

**Baseline it is compared against**: the actually-published `wh40k-11e-2026-08-2` release asset,
downloaded via `gh release download wh40k-11e-2026-08-2`, sha256 confirmed by its own file size
matching the prior release's own recorded evidence (11 253 406 bytes).

## 1. App-side ingest (T064) — **PASS**

```bash
python -m tools.consumer_compat rules-wh40k-11e-2026-08-3.json   # exit 0
python -m tools.consumer_compat rules-wh40k-11e-2026-08-2.json   # exit 0
```

`tools/consumer_compat.py` is **unmodified** (`git diff --stat HEAD -- tools/consumer_compat.py`
is empty). It builds the v1.2.0 schema verbatim, loads every array into its table, turns on real
foreign keys, and reports rather than dies on the first collision. Both runs exit 0 with no
violation line. The pricing exercise reports `pricing exercise skipped` on both bundles — expected
and not a gap: the exercise army is composed of the minimal synthetic fixture's own entities,
which no real bundle carries; the schema construction, load, and foreign-key pass all ran against
the real bundle.

It knows **none** of `007`'s new array (`datasheetItemConstraints`) or new optional
`snapshotMeta` fields. It does not have to: an array a consumer has never heard of is ignored by a
consumer that loads the tables it declares — the additive-compatibility proof this evidence exists
to make.

## 2. Array-level diff against the published bundle

Every array both bundles carry, compared as parsed JSON:

| Array | Published | Candidate | Status |
|---|---:|---:|---|
| `datasheetCompositions` | 2622 | 2614 | **moved: −8 rows** |
| `datasheetOptionChoiceItems` | 6305 | 9663 | **moved: +3358 rows** |
| `datasheetOptionChoices` | 5140 | 5140 | **moved: same count, values corrected** |
| `datasheetItemConstraints` | *absent* | 0 | **new array, empty this release** |
| every other array (26 of them) | — | — | **byte-identical** |

The 26 byte-identical arrays: `chapterKeywords`, `datasheetAbilities`, `datasheetCostContexts`,
`datasheetCostTiers`, `datasheetCosts`, `datasheetDetachmentEligibility`,
`datasheetEquipmentGroups`, `datasheetEquipmentItems`, `datasheetKeywords`,
`datasheetLeaderPairs`, `datasheetModels`, `datasheetOptionGroups`, `datasheetWargearOptions`,
`datasheetWeapons`, `datasheets`, `detachmentRestrictions`, `detachmentRules`, `detachments`,
`editionRules`, `editions`, `enhancementEligibility`, `enhancements`, `factionRules`, `factions`,
`gameSizeRules`, `keywordGlossary`.

Reading the four rows that moved:

- **`datasheetCompositions`: −8.** Exactly the 8 phantom `MODELS MAXIMUM` rows the Product
  Owner's 2026-08-14 T061 decision removed via `curation/composition-overrides.json`'s `remove`
  entries (decision 3). Verified by id: all 8 of `ds-fortis-kill-team`, `ds-indomitor-kill-team`,
  `ds-spectrus-kill-team`, `ds-talonstrike-kill-team`, `ds-fortis-kill-team-2`,
  `ds-indomitor-kill-team-2`, `ds-proteus-kill-team`, `ds-spectrus-kill-team-2` lose exactly their
  line-1 header row and nothing else; every other datasheet's composition is unchanged. No genuine
  model row was lost anywhere in the corpus (§3 below).
- **`datasheetOptionChoiceItems`: +3358.** More item rows resolve under the corrected legacy stem
  production (T021) and the wider clause table than the published bundle's pre-`007` extraction
  reached — additive, never a row removed from what already resolved (FR-009's zero-regression
  guarantee, confirmed separately by T060/T063's `option-regression` evidence: 2993/5140 choices
  identical, 0 newly *mis*-resolved).
- **`datasheetOptionChoices`: same count (5140), values corrected.** The 2039 FR-007 legacy-link
  corrections plus the 119 `CST-MARKER-RESIDUE` name-strip corrections T060/T061 already
  enumerate in full. No row added or removed from this array.
- **`datasheetItemConstraints`: new, empty (0 rows) this release.** The two-member vocabulary
  (`not_replaceable`, `one_per_unit`) implemented at T039 does not match any row's exact phrasing
  in the current live corpus — confirmed honestly rather than glossed over. This is not a defect:
  R-J (`reports/footnote-restriction-taxonomy/2026-08-14.md`) already confirmed every
  footnote-style restriction the corpus contains arrives as a refused **option** row (206 of them,
  unparsed), and none of the 206 happens to match this release's closed vocabulary's exact two
  shapes. The array, the schema, and the round-trip are all proven against the GF12 synthetic
  fixture (T037, T041); this release simply has nothing live to populate it with.

**`datasheetEquipmentGroups`/`datasheetEquipmentItems` are byte-identical**, confirming
`curated-snapshot-format.md` v1.4.0's own claim precisely: the bundle never lost this data (both
counts, 2206/5631, already matched the published bundle before this release) — only the curated
**tree** was missing the round-trip (issue #14), which is a reviewer-facing fix with **zero**
consumer-facing bundle-byte consequence for unchanged equipment data.

## 3. No real model was lost — confirmed by count, not just by the 8 ids above

`datasheetModels`, `datasheetWeapons`, and every faction/detachment/enhancement array are
byte-identical to the published bundle. The `datasheetCompositions` count fell by exactly 8 (one
per phantom datasheet) and by no more — the same fact `reports/wh40k-11e-2026-08-3/report.md`'s
own composition-resolved coverage figure independently confirms (unchanged proportion base minus
the phantoms, no genuine row dropped anywhere else in the corpus).

## 4. Site-side ingest (T065) — **not run this session**

`003-rules-reference-web` / `005-rules-web-enrichment-display`'s released build lives in
`The-BadgerWorks/wargame-rules-web`, a separate repository this session's working directories do
not include (same cross-repository boundary O2 already named at T048's rendering-contract
handoff). **This release therefore ships with one-sided app-side consumer-compat evidence**,
stated plainly rather than assumed: §1 above is real and passing; the site-side half of FR-020's
proof is unattempted, not merely unreported. A future session (or the Product Owner directly) with
that repository checked out should run its unmodified released build and `verify-dist.mjs` against
this candidate's bundle before treating FR-020/SC-006 as two-sided.
