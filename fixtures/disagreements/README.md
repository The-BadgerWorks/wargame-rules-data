<!-- AI-Assisted: Claude Code (model: claude-opus-5) - Authored the disagreement-class fixture
     set and the table of which case each invented record realises (task T078, spec Edge Cases,
     research D10). Every name here is invented; nothing was captured. -->
# `fixtures/disagreements/`

One case per disagreement class in the spec's *Edge Cases* list, in a single set, so a build
against it produces the whole finding profile at once and a regression in any one class is a
failing assertion rather than a quiet absence.

Like every fixture in this repository the set is **synthetic**: invented factions, invented
units, invented placeholder prose, hand-authored from the structure descriptions in
`research.md` §0. Nothing here was captured, and nothing here may be a redacted capture
(`fixtures/README.md`).

## Layout

```text
fixtures/disagreements/
├── mfm/                  # the points source: three invented faction pages
├── wahapedia/            # the detail source: the fourteen export files
├── curation/             # the authored tree this set is built against
├── previous/             # the PREVIOUS release, as a curated tree + published manifest
└── collapsed/            # a second set: the same release after a partial/error page
```

`previous/` is what makes half of these cases expressible at all. Last-known pricing, rename
detection, coverage ratios, and the change summary are all statements *about a baseline*, and
US2 is the first phase that has one (`tasks.md` Phase 4 note).

## The cases

| Class | Realised by | Expected |
|---|---|---|
| Unit in the points source only | `SLATE HERALD` on `slateguard.html`, no detail row | `REC-UNMATCHED-POINTS-ONLY` |
| Datasheet in the detail source only | `SG06 Slate Lantern`, priced only by `Datasheets_models_cost.csv` | `REC-UNMATCHED-DETAIL-ONLY` + `PRC-UNVERIFIED` |
| Priced by neither, ever | `SG07 Slate Cipher`, no cost row anywhere | `REC-NEVER-PRICED` (**blocking**) |
| Model-count band outside the composition | `SLATE PHALANX` bands 5 and 20; composition `5-10 Slate Phalanx` | `REC-BAND-MISMATCH` |
| Unparseable composition text | `SG03` composition `A cohort of Slate Wardens` | `REC-COMPOSITION-UNPARSED` |
| Conflicting overlapping value | `SLATE PHALANX` 5 models: points 90, detail 85 | `REC-VALUE-CONFLICT`, points wins |
| Gap in the point bands | `curation/game-sizes.json` leaves 2000..2499 uncovered | `CON-BAND-GAP` (**blocking**) |
| Mixed-edition entity | points `wh40k-11e` against detail `wh40k-10e` (the launch default) | `EDN-HYBRID-ENTITY` |
| Upstream rename | `ds-slate-aegis` was `SLATE AEGIS`, the page now prints `SLATE BULWARK` | `REC-RENAME` on an unchanged id |
| Two same-name datasheets in different factions | `Slate Warden` in both `SG` and `QC` | two ids, no ambiguity |
| Two in one faction differing only by Legends | `SG04` / `SG05`, both `Slate Revenant`, `SG05` from the Legends publication | disambiguated before the name is compared |
| Partial/error page that parses but collapses coverage | `collapsed/`, one faction where the baseline had three | `COV-COLLAPSE` (**blocking**), exit `42` |
| Pricing marker cleared | `SG03` was unverified in `previous/`, the points source prices it now | `PRC-REVERIFIED` |
| Pricing unverified too long | `SG05` unverified since `mfm-2026-05` for two releases | `PRC-UNVERIFIED-STALE` |
| Source delta disagrees with ours | `SLATE PHALANX` marked `▲ (+5)` where the computed move is `+10` | `CHG-DELTA-DISAGREEMENT` |

### The one case that is not a source document

**A missing enhancement parent** (`CON-ORPHAN-ENHANCEMENT`) has no source-level realisation, and
that is a property worth stating rather than a gap to paper over. Enhancements are built only
from the points source's detachment cards, and an enhancement is keyed to the card it was
published on using the same registry key the detachment was minted under — so the assembler
*cannot* construct an orphan from any input this set could contain. The guarantee is therefore
asserted where it can be asserted, at the snapshot level, in
`tests/contract/test_contract_guarantees.py`.

## Running it

```bash
rules-pipeline build --fixtures fixtures/disagreements --rules-version-id fixture-disagreements \
  --offline
```

The run exits `30`: `REC-NEVER-PRICED` and `CON-BAND-GAP` both stand, and there is no override
flag (FR-029). That is the point of the set.

The finding profile it produces, for reference when a change to the reconcile stage moves it:

| Code | Count | | Code | Count |
|---|---|---|---|---|
| `REC-UNMATCHED-POINTS-ONLY` | 1 | | `PRC-UNVERIFIED` | 2 |
| `REC-UNMATCHED-DETAIL-ONLY` | 3 | | `PRC-UNVERIFIED-STALE` | 1 |
| `REC-NEVER-PRICED` | 1 | | `PRC-REVERIFIED` | 1 |
| `REC-VALUE-CONFLICT` | 1 | | `EDN-HYBRID-ENTITY` | 10 |
| `REC-BAND-MISMATCH` | 1 | | `CHG-DELTA-DISAGREEMENT` | 1 |
| `REC-COMPOSITION-UNPARSED` | 1 | | `CON-BAND-GAP` | 1 |
| `REC-RENAME` | 1 | | | |

Eleven datasheets across three factions, matching the baseline's counts exactly, so nothing in
this set collapses coverage — `collapsed/` is where that is tested, and it exits `42`.

## The collapsed set

```bash
rules-pipeline build --fixtures fixtures/disagreements/collapsed \
  --rules-version-id fixture-collapsed --offline
```

One faction and two datasheets where the baseline had three and eleven: ratios of 0.33, 0.18 and
0.18 against thresholds of 0.95, 0.90 and 0.90. Exit `42`, not `30` — coverage collapse gets its
own code because "the source went strange" and "a curator has work to do" want different alerts.
