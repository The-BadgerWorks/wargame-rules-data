<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - T084 manual spot-check for the wh40k-11e-2026-08-4 candidate. Structural confirmation only (presence, row counts) against the live source page via the pipeline's own client -- no source sentence, item name, or ability text retained. -->
# T084 spot-check -- wh40k-11e-2026-08-4

Retrieval date: 2026-08-18. Source: https://wahapedia.ru/wh40k11ed (pipeline's own PoliteClient, html mode).

| Candidate datasheet id | Faction | Live page status | Name found on live page | Option rows on live page | Equipment rows on live page | Sampled because |
|---|---|---|---|---|---|---|
| `ds-land-speeder` | `space-marines` | 200 | True | 1 | 1 | newly extracted -- was zero-group partial pre-008 |
| `ds-wolf-guard` | `space-marines` | 200 | True | 1 | 1 | newly extracted -- was zero-group partial pre-008 |
| `ds-vespid-stingwings` | `t-au-empire` | 200 | True | 1 | 1 | newly extracted -- was zero-group partial pre-008 |
| `ds-overlord` | `necrons` | 200 | True | 2 | 1 | still partial -- conditional-only-blocked row (FR-006) |

**Outcome**: all three newly-extracted samples' names are confirmed present on the live source page with a non-zero option/equipment row count, consistent with the candidate now publishing structure for them where it previously published none. The still-`partial` sample (`ds-overlord`) is confirmed present with option rows still on the live page, consistent with the candidate's own `wargear_option_state: partial` for it (the row's own diagnosis class -- `refused_conditional_or_equipment_qualified` -- is a permanent, correct refusal under FR-006, not a gap). No source sentence, item name, or ability text is retained anywhere in this file.
