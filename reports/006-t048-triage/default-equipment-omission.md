<!-- AI-Assisted: Claude Code (model: claude-opus-5) - Triaged the spot-check package's open
     question 11 for the wh40k-11e-2026-08-2 candidate: classified all 658 datasheets carrying no
     `default_equipment_state`, verified the classification against the cached current-edition
     corpus, and recorded the defect and its fix. Counts only -- no sentence, fragment, item name
     or model name from either source appears anywhere in this file, on the same standard
     reports/006-t032-checkpoint/ holds itself to (Constitution Principle 4). -->
# T048 triage — the 658 datasheets with no `default_equipment_state`

**Measured** 2026-08-11 against `candidate/wh40k-11e-2026-08-2` (`b7200c7`), read-only, and
against the cached current-edition datacard corpus the T032 checkpoint used.

**Verdict: the candidate must be re-authored.** 647 of the 658 are a real extraction gap, not the
documented FR-016 omission. The fix is on `006-unit-loadout-fidelity`; this candidate cannot ship
as it stands.

## 1. The classification, and it accounts for all 658

Every published datasheet in the candidate was classified by its own `provenance`, with no
reference to the equipment extraction at all:

| Class | Datasheets | `default_equipment_state` | Correct? |
|---|---:|---|---|
| Detail-matched **and** priced by the points source | 1 426 | set (`extracted` 1 386, `partial` 30, `none` 10) | yes |
| Detail-matched, priced, composition did not resolve | 5 | **absent** | yes — FR-016 |
| Points-only (no detail card was ever read) | 6 | **absent** | yes — the source was not consulted |
| **Detail-only** (a card was read; the points authority did not price it) | **647** | **absent** | **no — defect** |
| total | 2 084 | | |

5 + 6 + 647 = **658**, exactly the figure the spot-check package reports, and 638 of the 647
publish composition rows — exactly the "638 of the 658" the package also reports. The
classification is therefore complete rather than approximate: there is no residual to explain.

**The hypothesis under test is disproved, and inverted.** These are not datasheets whose
composition derives from the points source's model-count bands. They are the opposite: datasheets
the *detail* source published and the *points* source did not price. Their cards were read end to
end — composition (638), weapon lines (640), `wargear_option_state` (**647 of 647**, always set).
Only the equipment half is missing.

## 2. The cause: one assembly path, and only one, was wired for US2

`pipeline/curate/assemble.py` builds a datasheet down two paths. `_datasheet_for` handles a
datasheet the two sources agree on and calls `_equipment`. `_detail_only_datasheet` handles one the
points authority did not price this release (FR-026, FR-035) — and did **not** call `_equipment`
at all, nor pass `equipment_groups` / `default_equipment_state` to the `CuratedDatasheet` it
constructs. The fields simply defaulted to empty and `None`.

That is why **no `EQP-UNPARSED` was raised for any of the 647**: nothing was refused, because
nothing was attempted. It is also why the omission is invisible to a consumer as an *error* — the
absent state is a legitimate code meaning "the source was not consulted", which is a true statement
about a code path that never ran and a false statement about the card, which had been read.

**Why the T032 checkpoint predicted 14 and not 658.** T032 measures the extraction through
`parse_faction_page` → `emit_records` → `_detail_datasheet_fields` → `_composition_entries` →
`_equipment`. Every one of those is downstream of the branch that was missing, so the checkpoint
measured the extractor — which is sound — and could not have seen the wiring gap above it. The
extractor's own figures reproduce exactly on re-measurement today: 1 688 datacards, 1 937 equipment
sentences over the same 24 cached faction pages.

## 3. Spot-verification against the cached corpus

Each of the 647 was resolved to its cached datacard by normalised name and asked one question: does
that card state a default-equipment block at all?

| Outcome | Datasheets |
|---|---:|
| Every candidate cached card for that name states **at least one** equipment sentence | **640** |
| No candidate card states one (these would correctly publish `none`) | 7 |
| Ambiguous — some do, some do not | **0** |
| not resolvable to a cached card | 0 |

Sentences that the candidate should have carried and does not: **734**, over the cached corpus
alone. The release reads more faction pages than the cache holds, so the live figure is at least
this.

A twelve-datasheet random sample was inspected row by row; all twelve carry one equipment sentence
each and a published composition matching the cached card's composition row count.

**The two datasheets the spot-check package names.** Both were re-run through the *fixed*
`_detail_only_datasheet` against the cached pages:

| Datasheet | Before | After the fix |
|---|---|---|
| `ds-amallyn-shadowguide` | field absent | `extracted`, 1 group, 2 items, both weapon-line linked |
| `ds-ancient-on-bike` | field absent | `extracted`, 1 group, 3 items, all three linked |

So the answer to the package's question 11 is the first of the two readings it offers: **these
cards do state a default-equipment sentence.** The reviewer does not need to open a browser to
settle it.

## 4. Does any datasheet with a real equipment block lack a state?

**Yes — 640 of them**, which is the whole finding. Stated the other way, so the boundary is
explicit: of the 658, exactly **11** are correct omissions (5 FR-016 + 6 never-consulted), and of
those 11 none has a readable equipment block the pipeline declined to publish for a reason it
cannot name. Every remaining case is the defect.

## 5. What the coverage figure actually described

The published 67 % (`loadout.default_equipment`, 1 396 / 2 084) has the right denominator — every
datasheet in the release — but its numerator was suppressed by the defect, not by the source. With
the fix the numerator gains the 640 detail-only cards that state a block plus the 7 that state
none, less any that resolve `partial` (which the coverage reading deliberately excludes), landing
near **98 %**. The remaining residual is the 11 correct omissions and the `partial` tail.

`loadout.default_equipment` is reported and **not ratcheted** in this first extended release
(`LOADOUT_RATCHETED_KEYS`, research D4), so no threshold moves and no gate is being loosened to
accommodate this. The next release inherits the corrected figure as its baseline, which is the
right one to inherit — ratcheting 67 % would have frozen the defect into the floor.

## 6. The fix and its regression tests

`pipeline/curate/assemble.py` — `_detail_only_datasheet` now calls `_equipment` with the
composition it has already resolved, extends its findings, and passes `equipment_groups` and
`default_equipment_state` to the datasheet it constructs, on exactly the terms `_datasheet_for`
does. FR-016 travels with it: the call still refuses to attach a loadout to a composition that did
not resolve.

`tests/enrichment/test_us2_independent.py` gains three tests, in the module that already owns US2's
end-to-end proof and against the same synthetic fixture:

* an unpriced datasheet still carries its equipment — written to fail against the pre-fix code;
* both assembly paths yield the **same** groups and the same state for the same card, over three
  cards covering the unit-wide, model-group and multi-sentence shapes; and
* FR-016 still suppresses equipment on the unpriced path, so the fix did not buy coverage by
  weakening the refusal.

Gate: `ruff check` clean, `ruff format --check` clean (255 files), `mypy` strict clean (92 source
files), `pytest` **1 654 passed, 8 skipped**.

## 7. What this means for the candidate

`candidate/wh40k-11e-2026-08-2` **cannot ship as-is**. The defect is not cosmetic: roughly a third
of the roster publishes a code that tells a consumer the equipment source was never consulted for
cards the pipeline read in full, and it does so silently, with no finding an approver could have
acted on. Re-author the candidate from `006-unit-loadout-fidelity` with this fix in it, then
regenerate `reports/006-spot-check/package.md` — entry 11 disappears, and the coverage figure
entries 6 to 9 sit beside change with it.

Two things carry forward unchanged and do **not** need re-checking: the FR-009 option-regression
proof (options are untouched by this fix) and the 256-row unparsed-option residual. The text-
encoding defect noted as item 12 in the spot-check package is likewise unrelated and still open.
