<!-- AI-Assisted: Claude Code (model: claude-opus-5) - Recorded the 006 T032 checkpoint: the
     User Story 2 extraction measured over the cached current-edition corpus, and the
     before/after proof that it perturbs neither composition nor options. Counts only -- no
     sentence, fragment, item name, or model name appears anywhere in this file, on the same
     standard reports/option-taxonomy/ holds itself to (Constitution Principle 4). -->
# T032 checkpoint — default equipment over the cached corpus

**Measured** 2026-08-10, against the cached current-edition datacard corpus (27 pages; the two
non-datacard pages in the cache are skipped structurally, not filtered). The extraction runs
through the pipeline's own path — `parse_faction_page` → `emit_records` → `_detail_datasheet_fields`
→ `_composition_entries` → `_equipment` — so what is counted here is what a run publishes, FR-016
and both joins already applied.

## 1. Coverage

| Measure | Value |
|---|---:|
| Datacards on the page set | 1 688 |
| **Cards carrying a default-equipment block** | **1 676 (99.3 %)** |
| Sentences extracted | 1 937 |
| Sentences resolved by a production | 1 838 (**94.9 %**) |
| — subject `unit` / `model_group` | 1 510 / 328 |
| Sentences refused (`EQP-UNPARSED`) | 99 |

Research D1e predicted 1 676 / 1 688 cards and 1 932 groups. The card figure reproduces exactly;
the sentence count comes out 5 higher, which is the difference between D1e's own instrument and a
direct-children DOM walk, and is in the direction that loses nothing.

## 2. What the pipeline publishes

| Measure | Value |
|---|---:|
| Datasheets carrying a `defaultEquipmentState` | 1 674 / 1 688 |
| — `extracted` | 1 627 |
| — `partial` | 37 |
| — `none` | 10 |
| — **omitted** (composition did not resolve, FR-016) | 14 |
| Equipment groups published | 1 816 |
| Equipment items published | 4 500 |
| **Items linked to a weapon line** | **3 718 (82.6 %)** |
| `model_group` groups linked to a composition row | 168 / 306 (54.9 %) |

Findings raised: `EQP-UNPARSED` 99, `EQP-GROUP-UNRESOLVED` 138, `EQP-ITEM-UNLINKED` 782 — all
three advisory, and every one of them ships the row it is about.

## 3. The residual is D1e's mixed class, refused on purpose

Every one of the 99 refusals is one of the compound-or-conditional subjects research D1e
enumerated and the design deliberately did not build a production for. Counted by which refusal
fired first:

| Refusal | Sentences |
|---|---:|
| leading `INT` + MODEL | 35 |
| `One` / `A` / `An` + MODEL | 34 |
| `MODEL with ITEM` (subject qualified by equipment) | 22 |
| `For every` / `If` / `Unless` / `Up to` (+ comma) | 8 |
| **Total** | **99** |

D1e sized this class at 104 groups, so the refusals land inside its own measurement. Each of these
subjects matches a built production perfectly well and would resolve to a *model name that is not a
model*; they go to `curation/equipment-overrides.json`, which is what that file is for.

**One correction to research D1e.** Its prose says the five subject productions cover "≈99.5 %" of
groups. Its own table does not: 1 143 + 367 + 163 + 137 + 18 = 1 828 of 1 932, which is 94.6 %. The
measured 94.9 % here agrees with D1e's table, and the ≈99.5 % figure appears to have counted the
mixed class as covered. Nothing in the build plan depended on the higher number — the mixed class
was always routed to overrides — but the coverage figure this feature reports is 94.9 %, not 99.5 %.

## 4. Why the group-link rate is 54.9 %, and what would move it

`compositionLine` is resolved by `link_model_line`'s exactly-one-match **name** rule and never by
ordinal (data-model.md §1.2; D1e's 195 two-lines/one-group cards are why). Of the 138 that do not
resolve, 133 match **zero** composition rows and 5 match two or more.

A follow-up measurement, taken and **not acted on**: under a naive singular/plural fold, 100 of the
138 would resolve to exactly one row, 6 would become ambiguous, and 32 would still match nothing.
That fold is not applied here, and deliberately:

* `link_model_line` is shared with composition itself, so changing it changes a `004` join that
  US1's zero-regression guarantee covers; and
* stemming a name to make a link land is precisely the guess this feature's whole design refuses.
  A wrong `compositionLine` attaches a squad's loadout to its leader silently, which is the failure
  mode the ordinal rule was rejected for.

The honest routes are a measured research amendment or the curator's own
`composition_line` in `curation/equipment-overrides.json`. Both leave the rule stated once.

## 5. Zero-diff proof — the extraction perturbs neither composition nor options

Risk **R-E**'s claim, checked rather than argued. The same corpus was extracted twice: once at
`82bbef0` (the pre-Phase-4 head) and once at the candidate, dumping every
`Datasheets_unit_composition.csv` and `Datasheets_options.csv` row each produced.

| Table | Rows before | Rows after | Result |
|---|---:|---:|---|
| `Datasheets_unit_composition.csv` | 2 121 | 2 121 | **identical** |
| `Datasheets_options.csv` | 2 424 | 2 424 | **identical** |

Byte-identical row sets, field for field. This is structural rather than lucky: `_equipment(block)`
walks the composition element's **direct children** and takes the bold subject element and the bare text
nodes after it, so it never enters the `ul.dsUl` that `_composition_and_costs` reads, and the two
extractors touch disjoint nodes.

The layer-1 option-regression harness (T010) is green in the same run, as is the whole suite:
**1 520 passed, 4 skipped**, mypy strict clean, ruff clean.
