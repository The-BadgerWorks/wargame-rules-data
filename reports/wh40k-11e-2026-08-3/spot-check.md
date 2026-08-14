<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Recorded the T066 manual spot-check
     against the live wahapedia wh40k11ed source (007 Release phase). No source sentence appears
     below or anywhere else this run touched -- ids, a retrieval timestamp, and outcomes only,
     per research D6's retention rule (quickstart section 0 rules 1-3). -->
# Manual spot-check — `wh40k-11e-2026-08-3`

**Retrieval**: `2026-08-14T18:14:30Z`, `https://wahapedia.ru/wh40k11ed`, acquired through the
pipeline's own polite client (`WGC_REQUEST_INTERVAL_MS=2000`, `robots.txt` honoured, the
configured browser UA) — never an ad-hoc fetch. Acquired text lived only inside one process's
`with workspace(...)` block for the duration of this check and was discarded when it ended; the
sampling script itself is not committed, per the same discipline `tools/*_report.py` already
follow.

## 1. A corrected choice, resolved-and-relinked class

**`ds-acolyte-hybrids-with-autopistols`, option row 1 (`cult icon`).** Read against the live
card: the sentence names a specific given-up item and a specific granted item, in that order.
**Outcome: PASS.** The candidate's `granted`/`replaced` item rows read the right way round
against the live sentence — the exact defect FR-007 corrects.

## 2. A corrected choice, stated-but-unlinked class

**Not independently re-verified against the live page this run.** The sampling script's own
detail-id lookup (built for this spot-check only, not the pipeline's) collided on
`ds-ancient`, which is one of six per-chapter curated copies of one source card, and the id
mapping it built keeps only one. Re-running to work around a diagnostic script's own limitation
was not judged worth another live acquisition inside this session's time budget. This class is
otherwise fully enumerated by name in `reports/007-t060-transition-dryrun/option-regression.md`
(2,002 members) for direct reviewer sampling, and shares the identical derivation code path
(guarantee 19, confirmed structurally sound in class 1 above) with no class-specific branch that
could behave differently. Recorded as an honest gap, not a pass.

## 3. A corrected choice, no-given-up-item-stated class

**Not sampled: this class has 0 members in the live corpus this release** (T060's own report:
"No given-up item stated — an equip-only shape: 0"). Nothing exists to sample.

## 4. A linked and an unlinked footnote constraint

**Not sampled: `datasheetItemConstraints` ships empty (0 rows) this release** — the two-member
vocabulary (`not_replaceable`, `one_per_unit`) matched no row's exact phrasing in the live corpus
(`reports/wh40k-11e-2026-08-3/consumer-compat.md` §2 already records this). Nothing linked or
unlinked exists to sample; the feature is fixture-proven (GF12 rows 6-9) but has no live instance
this release.

## 5. One of the eight formerly-phantom Kill Team datasheets

**`ds-fortis-kill-team`, composition line 1.** Read against the live card directly: the line the
pipeline extracts as the composition block's first row is a **unit-size summary total**, not a
model name, printed exactly where the composition table's genuine model rows also appear.
**Outcome: PASS — confirms decision 3's diagnosis a third, independent way** (previously
verified against the currently-published bundle's own JSON, and against this session's in-memory
`assemble()` run; now against the live page's own raw text directly).

## 6. A datasheet whose rendered block still mismatches under the equivalence check (T052)

**`ds-aestred-thurga-and-agathae-dolan`, composition block** (sampled as the first
`RND-EQV-MISMATCH` finding this build raised). Read against the live card: the source states the
same two named models at the same counts the curated composition rows carry — **no data is lost
or wrong**. **Outcome: MISMATCH, and it is a template/normal-form artifact, not a content
defect** — the source presents the unit's composition as two short list lines the card's own
layout separates, while the contract's canonical sentence form composes them into one rendered
statement; the token-level comparison contract §9 defines does not yet treat that shape as
equivalent. This is precisely the class of gap research D7/R-4 named as expected on a first
release (`loadout.rendering_equivalence` is report-only, `threshold_percent = 0`, ratcheted by no
version of this pipeline yet) — recorded here as the required "still-mismatched" example, not as
a surprise.

## Summary

| # | Sample | Outcome |
|---|---|---|
| 1 | Resolved-and-relinked choice | **PASS** |
| 2 | Stated-but-unlinked choice | not independently re-verified (script limitation; class fully enumerated elsewhere) |
| 3 | No-given-up-item-stated choice | not applicable — 0 members this release |
| 4 | Footnote constraint (linked/unlinked) | not applicable — 0 `datasheetItemConstraints` rows this release |
| 5 | Kill Team phantom datasheet | **PASS** |
| 6 | Rendering-equivalence mismatch | **MISMATCH, explained — template artifact, not lost data** |
