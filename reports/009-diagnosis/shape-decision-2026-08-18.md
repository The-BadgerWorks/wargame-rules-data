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
  as class 6 ("a default-equipment sentence misfiled into the options block"), already attributed
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
  contradicting phase 0's "zero rows bearing the five chapter keyword strings" measurement — but
  it is **title-case** in the export while `curation/keyword-classes.json`'s vocabulary is
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
