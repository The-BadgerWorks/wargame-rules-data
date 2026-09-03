<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Assembled per tasks.md T046: the
     four-criterion evidence package T047 (Product Owner review checkpoint) reads. This session
     stops BEFORE T047 -- no decision is recorded here, only cited measurement. -->
# Shape-decision evidence package (T046)

**Status: package assembled, T047 NOT executed.** This document exists to be read by the Product
Owner at T047; it makes no decision. Every figure below is either transcribed from an existing
`reports/009-diagnosis/` file or freshly measured this session against a real, live acquisition
through the pipeline's own client (never a fixture, per rule 3/FR-018 for criteria 2 and 4).
Text-free throughout: counts, ratios, finding codes, and identifiers only.

## FR-009's four criteria

### Criterion 1 — options parity

- **Residual attribution** (`2026-08-18-cause-attribution.md`, T036-T045): 357 of 358 delta rows
  (99.7%) carry a named cause; zero rows attributed to a genuine vocabulary cause; rule 5 holds
  as a measured consequence.
- **Post-normalization-fix re-run** (`2026-08-18-post-t030.md`, T041): byte-identical to the
  pre-T030 baseline, class by class — T030's fix produced zero measurable residual movement in
  this corpus, despite fixing a real, fixture-confirmed defect.
- **`loadout.options_resolved` against its 96 floor** (T062, live full build, csv mode, this
  session): **1218 / 1992 = 85.0%** (previous published: 1992). **Below the 96 floor.**

**Verdict: FAILS.** The residual is well-explained (99.7% named), but the explained residual has
not translated into the ratcheted coverage figure clearing its floor on a real build.

### Criterion 2 — default-equipment parity

- **Derivation implemented** (T057/T058, commit `c989a7fd`): `Datasheets_unit_composition.csv`
  rows carrying the equipment marker are split into a derived `Datasheets_unit_equipment.csv`, in
  the reader, and no longer poison composition resolution. Verified against synthetic fixtures (7
  new tests) and the full suite (2173/8 skipped).
- **Live measurement of the derivation's own input** (this session): the marker occurs in **0**
  of 2131 `Datasheets_unit_composition.csv` rows on the live corpus. It occurs in **22** of 2780
  `Datasheets_options.csv` rows instead — the SAME 22 rows the export-mode taxonomy already names
  as class 6, the default-equipment sentence misfiled into the options block, already attributed
  as part of criterion 1's residual. **`plan.md` finding 9's premise (the marker lives in the
  composition table) does not hold against this corpus on this date; both are stated rather than
  the newer one silently overwriting the plan.** The derivation is implemented correctly for the
  location the plan named; that location currently carries none of the rows live.
- **`loadout.default_equipment` against its 97 floor** (T063, live full build, csv mode, this
  session): **0 / 2016 = 0.0%** (previous published: 2016). **Below the 97 floor by the whole
  figure.**

**Verdict: FAILS**, and by a wide margin. Extending the derivation to also read
`Datasheets_options.csv`'s class-6 rows would recover exactly 22 datasheets' worth of equipment —
not enough on its own to approach the 97 floor, and not implemented in this session (a source-list
change beyond T057's literal scope, recorded as a finding for the Product Owner rather than acted
on unilaterally).

### Criterion 3 — disambiguation

- **Collision set, six Space Marine factions, csv mode** (T002, prior session): 292 `faction_id=SM`
  rows, 282 distinct names, 10 names with >1 distinct `datasheet_id` among non-Legends candidates
  (T002's own report recorded 9; this session's re-measurement of the same population found 10 —
  both are stated, the difference is not reconciled here).
- **Live identification against real acquired identifiers** (this session): 9 of the 10 pairs are
  core-codex-vs-Black-Templars-supplement duplicates, already resolved by the EXISTING
  publication-id rung (`source_id` 000000139 vs 000000162, matching the already-curated
  `detail_source_publication_id` on `black-templars`) whenever the recipient scope IS
  black-templars. Confirmed by running `resolve_factions`/`match_units` for all six chapters
  against their own published rosters (`data/wh40k-11e`), not merely counting the raw collisions.
- **Genuine blocking case found**: 1 pair ("Venerable Dreadnought" / space-wolves) produces a real
  `REC-AMBIGUOUS-MATCH` against the published roster. `curation/unit-map.json` (T061, commit
  `5f50ddcb`) authored with the one entry this measurement required
  (`faction_id=f-space-wolves`), pointing at the already-published, C1-held
  `ds-venerable-dreadnought-2`.
- **Re-measurement with the crosswalk in place** (T064, live, this session): **0 blocking
  REC-AMBIGUOUS-MATCH across the six Space Marine factions** (was 1). **Meets the zero target
  (SC-005).**
- **research.md Q3** (T067, this session): the chapter-keyword rung is confirmed starved for the
  Black-Templars-shape pairs (already resolved by publication-id instead). For the one genuine
  case, the export DOES carry a per-datasheet chapter-identifying keyword (`Space Wolves`) —
  contradicting phase 0's zero-chapter-keyword-rows measurement — but it is **title-case** in the
  export while `curation/keyword-classes.json`'s vocabulary is
  **upper-case** (`SPACE WOLVES`), so the existing rung does not fire on it as authored. Not
  fixed here (a `pipeline/` code change is a different PR class from this session's `curation/`
  work); flagged as a finding, not a rung invented (rule 10 — the crosswalk entry already closes
  the one live case without it).

**Verdict: PASSES**, at the scope T002/T064 measure (the six Space Marine factions), with the
crosswalk populated per this session's live measurement of exactly which entries that requires.

### Criterion 4 — table coverage

- **Live measurement against a real acquisition** (T054/T065, `table-coverage-2026-08-18.md`,
  this session): 13 of 14 consumed tables present and populated. The one exception is the derived
  `Datasheets_unit_equipment.csv` at 0 rows — the same finding criterion 2 already names, not a
  new one.
- `Enhancements.csv` is acquired (`EXPORT_FILES`) but consumed by no `pipeline/curate/` code path
  today — not counted as a coverage gap; feeds Q2 below.

**Verdict: PASSES** on the 13 tables the build actually depends on for a non-zero result; the one
absence is criterion 2's own failure restated, not an independent table-coverage defect.

## research.md Q2 — the enhancements inversion (T066)

Live-confirmed this session: `Enhancements.csv` is not read by any code path in `pipeline/curate/`
(grepped across the whole package; the only reference anywhere in `pipeline/` is its own listing
in `EXPORT_FILES`). Published enhancement records are built from the **points source** (MFM
detachment cards), not from wahapedia's `Enhancements.csv`, at all. **Q2 closes**: the 1,028 vs
1,199 comparison research.md posed is between two figures with no producer/consumer relationship
— the export was never adopted as authoritative for this class, so there is no shortfall to
reconcile and nothing routes to the hybrid on this account.

## research.md Q3 — see criterion 3 above

## Sizing inputs (T002-T004, prior session; transcribed, not re-measured)

- Same-name collision set, six SM factions: 9 (T002's original count; this session's
  re-measurement of the same population found 10 non-Legends pairs — both stated, see criterion 3)
- `-N`-suffixed population: 793 across 18 of 30 factions (T003)
- Digest churn (approved ability summaries, pre-migration normalization): 76 of 2125 would need
  re-review (3.6%) (T004)

## An additional finding, outside FR-009's four named criteria

**General datasheet coverage collapses under a live full csv-mode build, and the cause is not
attributed by any measurement this feature has produced.** A real end-to-end build (both
upstreams, live, this session, `run_build` with `output_root`/`reports_root` diverted to a scratch
location, never written into the tracked repository) produced:

| Coverage category | csv mode (this session) | html mode (same-session baseline) |
|---|---:|---:|
| `datasheets` | 1437 / 2083 = 69.0% | 2084 / 2083 = 100.05% |
| `priced_datasheets` | 1437 / 2083 = 69.0% | 2084 / 2083 = 100.05% |
| `composition` | 1422 / 2063 = 68.9% | 2063 / 2063 = 100% |
| `wargear_options` | 1218 / 1992 = 61.1% | 1993 / 1992 = 100.05% |
| Exit code | 42 (COV-COLLAPSE) | 20 (pass) |

The html-mode run, in the same session against the same live MFM acquisition, scores at or above
100% on every one of these — which rules out an MFM-side (points source) fetch shortfall as the
cause, since the same roster is being matched in both runs. The csv-mode run raised **zero**
`REC-AMBIGUOUS-MATCH` and only 6 `REC-UNMATCHED-POINTS-ONLY` findings (identical to the html run's
6) — which rules out disambiguation failure and points-only-unmatched names as the cause of the
~646-datasheet shortfall. **Where the ~646 records are actually being lost between
`match_units`'s output and the final snapshot's `datasheets` count is not diagnosed by this
session** — it is outside every task this session was scoped to (Phase 3 diagnosed the options
residual specifically; this session's Phase 5 work diagnosed the SM disambiguation gap
specifically; neither covers a general datasheet-count collapse).

**This matters directly for O1.** A hybrid retaining the html arm for "options and/or default
equipment alone" (`plan.md`'s own stated likely outcome) does not, on the evidence in hand, address
a collapse of this size if it turns out to be systemic rather than confined to the classes already
characterized. **Recommend this gap be diagnosed with the same rigor `tools/option_taxonomy.py`
brought to the options residual, before O1 is decided** — the four FR-009 criteria as measured are
necessary evidence but may not be sufficient, and this session flags that rather than silently
reading the four criteria as the whole picture.

## Reading this package

- Criteria 1 and 2 fail their floors, measured on a real build. Criterion 3 passes at its measured
  scope. Criterion 4 passes on the tables the build depends on for a non-zero result.
- `plan.md`'s own falsifiable expectation ("criteria 3 and 4 pass once Phase 2 and Phase 5 land,
  criterion 1 passes only if T030 carried most of the gap, and criterion 2 is the genuinely open
  one") is **partially confirmed**: 3 and 4 do pass; criterion 1 does NOT pass despite T030's real,
  confirmed fix, because the fix's live yield was zero on this corpus (T041); criterion 2 is not
  merely "open," it measures at zero.
- **No shape (full or hybrid) is recommended by this document.** That is T047's decision, put to
  the Product Owner against these numbers, plus the additional unattributed coverage-collapse
  finding above.

## Session addendum — the coverage collapse, diagnosed and fixed; criteria 1/2 re-measured

<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Diagnosed and fixed the general
     coverage-collapse finding this document's own "additional finding" section flagged as
     unattributed, then re-measured criteria 1 and 2 against the fixed build, and measured the
     equipment-source redesign question US2/O1 needs. Text-free, structural counts only,
     matching this whole document's own convention. -->

**The collapse is diagnosed, root-caused, and fixed.** It was not an MFM-side (points source)
fetch shortfall, not a disambiguation gap, and not a structural export shortfall. Live
instrumentation of `pipeline.curate.assemble` under both arms, against the identical live MFM
roster, proved every points-source unit always produces exactly one match (`csv`-mode's own
matched-datasheet count equalled the live roster size exactly, per faction). The entire gap traced
to `_owning_factions()` (`curate/assemble.py`), which keyed its detail-source-faction-id lookup by
`detail_source_faction_id` alone (the `html`-arm slug vocabulary) rather than through
`_detail_ids_for()` (009 T020/T021's own helper, which also carries `detail_source_faction_code`).
Under `csv` mode, every unclaimed export row's `faction_id` is the export's own code, matching
nothing in the slug-keyed dict — silently discarding the entire FR-026/FR-035 "ships on the best
price known" detail-only recovery pass (the mechanism that recovers every unit the live points
source no longer prices but the detail source still carries). **Fixed**: `_owning_factions` now
keys through `_detail_ids_for`, the same two-tier shape every other 009 arm-selection site already
uses. Failing-first test added and confirmed failing pre-fix. Full suite green (2176/8, was
2173/8). `wargame-rules-data` commit `439df21f`.

**Live re-measurement, full build, `csv` mode, post-fix** (output diverted to scratch, nothing
published): `datasheets` 2083/2083 = 100.0% (was 1437/2083 = 69.0%); `composition` 2058/2063 =
99.76% (was 68.9%); `factions` 100%; `priced_datasheets` 100%; `keyword_classification` 99.64%.
`COV-COLLAPSE` now fires on **one** category only — `wargear_options` — not on the general
datasheet/composition/faction counts. The collapse this document's own "additional finding"
section flagged as unattributed is closed.

**Criterion 1, re-measured post-fix**: `loadout.options_resolved` = **1646/2083 = 79%** — lower
than this document's original T062 figure (85.0%) not because the fix regressed anything, but
because the fix surfaces 648 previously-invisible detail-only datasheets (units the points source
no longer prices) whose options resolve at a materially worse rate than the roster-matched
population; the 85.0% figure was computed over an incomplete, collapsed population. Applying the
cause-attribution report's own recommended exclusion (denominator + denominator-adjacent causes,
`option_taxonomy.classify()` classes 6/11/13) — measured structurally this session, NOT
implemented in production code, since it is a design decision about which datasheets count as
"resolved," reserved for T047 — moves the figure to **≈1964/2083 ≈ 94.3%**: closes most, but not
all, of the gap to the 96 floor. **Residual ≈1.7 points**, concentrated in one under-sized,
previously-uncharacterized class (`option_taxonomy` class 2, "head unknown, verb already built,"
43 rows in this live population — the cause-attribution report only sized this class's csv-vs-html
**delta** at 1 row; its live **total** population is far larger and both arms carry most of it)
plus already-known unproductionable noise (class 12, 18 rows) plus genuine within-family grammar
gaps (classes 1f/7/8/5/4, 19 rows) plus class 9's already-accepted no-production case (7 rows).
**Verdict: still FAILS the 96 floor, before and after the exclusion — but by a much narrower
margin than the original 85.0% suggested, and the residual is now named down to specific classes
rather than left as an unattributed gap.**

**Criterion 2, re-measured post-fix**: unaffected by the collapse fix (a different mechanism) —
`loadout.default_equipment` = 0/2083 = 0.0% still, confirmed unchanged live. **Equipment-source
redesign evidence measured this session** (the composition-marker premise `plan.md` finding 9
named is confirmed dead, 0/2131, live): of every candidate table checked
(`Datasheets_unit_composition.csv`'s marker, `Datasheets_options.csv`'s class-6 misfiled rows,
`Datasheets_models.csv`, `Datasheets_wargear.csv`), the strongest by a wide margin is
`Datasheets.csv`'s own `loadout` column — already declared prose-bearing in
`PROSE_BEARING_FIELDS` (`pipeline/models/source.py:156`) but consumed by no reader today. Live
population: 1673/1680 export rows non-empty (99.6%). A read-only dry run through the existing,
UNMODIFIED `equipment_grammar.parse_sentence()` (rule 5 respected — nothing changed, nothing
published) parses 1665 of those 1673 (99.5%) as a valid equipment sentence, whole-field or its
first clause. Effective achievable coverage against the previously-published 2,016-datasheet
target: **≈82.6%** (1665/2016) — bounded by population presence, not by grammar coverage. Full
verdict table, all candidates, in this repo's implementation-progress ledger (specs repo,
`specs/009-csv-migration/.impl-progress.md`, "Finding 3"). **Not implemented this session** — a
`loadout`-column reader and derivation is a real design change, reserved for T047's decision.

**Updated shape recommendation.** The general-collapse finding that previously made even a
narrowly-scoped hybrid look potentially insufficient is now closed — a hybrid or a full migration
can both be evaluated against criteria 1-4 alone, with no unattributed residual risk hiding behind
them. Criterion 3 and 4 pass as before. Criterion 1 fails narrowly (94.3% vs 96, post-exclusion,
not yet implemented) rather than by a wide margin. Criterion 2 still fails by the whole figure
(0.0% vs 97), but the evidence now in hand shows a derive-from-export path could plausibly close
most of that gap (≈82.6% achievable via the `loadout` column) rather than being structurally
impossible — a materially different starting point for weighing derive-from-export against
hybrid-keep-html-equipment than "0% achievable, composition marker dead" was.
