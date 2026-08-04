<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote the per-published-version spot-check
     template (task T153): manual sampling of unit points, detachment costs, and enhancement
     costs against the live source page, with mandatory unverified-pricing and hybrid-edition
     sample coverage per reports/<rulesVersionId>/unverified-pricing.md and edition-mismatch.md. -->
# Spot-check template

Fill in a copy of this template once per published version, as a manual, by-hand sanity check
that sits alongside the automated validation — a human comparing what shipped against what the
live source actually says, on the same day, for a small deliberately-chosen sample. This is not a
substitute for `reports/<rulesVersionId>/` (which is generated, exhaustive within its own checks,
and the authority for a support enquiry per `docs/operational-readiness.md`) — it is independent
evidence that the numbers a player actually sees match reality, sampled by eye rather than by
code.

Save the filled-in copy as `docs/verification/spot-check-<rulesVersionId>.md`.

## What "unverified" and "hybrid edition" mean, and why the sample must include one of each

**`pricing_confidence: unverified`** (`reference-db-schema.md` §3.3) means a datasheet is shipping
on its **last-known price** rather than a price the authoritative points source restated this
release. The points source does not necessarily republish every unit's cost on every release; a
unit that goes silent carries its previous verified price forward, marked `unverified`, rather
than losing a price entirely (which would instead be the blocking `unpriced` state). An
unverified entry is the one case in this data set where "what we're shipping" and "what the
source currently states" are not the same claim — which is exactly why a spot check has to look
at one: it is the entry most likely to have quietly drifted from reality, and the automated
pipeline cannot detect that drift on its own (there is nothing to compare against — the source is
silent). Find candidates in `reports/<rulesVersionId>/unverified-pricing.md`, which leads with the
count and proportion of the release in this state (`validation-report.md` §1.3) before
enumerating the affected datasheets.

**`is_hybrid_edition: true`** (`reference-db-schema.md` §3.5, FR-060) means a datasheet's
mechanical detail (stats, weapons, abilities) came from a different declared edition than its
points cost did — at launch the normal case, not an edge case, because the points source runs
11th Edition and the detail source runs 10th (research §0.1). A hybrid entity is the one case
where two different pages, possibly describing two different rules baselines, were reconciled
into one datasheet — worth eyeballing because the detail and the price are not attestable against
a single live page the way a same-edition entity's are. Find candidates in
`reports/<rulesVersionId>/edition-mismatch.md`, which leads the same way with count and
proportion.

**The template below requires at least one sampled entry of each kind.** A spot check that only
samples ordinary, currently-verified, same-edition entries checks the easy case and skips the two
kinds of entry most likely to be wrong.

## Template

```markdown
# Spot check — <rulesVersionId>

**Checked by**: <name>
**Date**: <date this check was performed — this is the date every "source retrieval date" cell
below should match or be close to>
**Published version's own report**: reports/<rulesVersionId>/report.json (verdict: <verdict>)

## Sample

At least six entries: two unit points, two detachment costs, two enhancement costs. At least one
row total must carry `pricing_confidence: unverified` and at least one row total must carry
`is_hybrid_edition: true` (the same row may satisfy both, or two different rows may each satisfy
one — mark which with the Notes column).

| # | Entity (faction / name) | Category | Shipped value | Source page retrieved | Retrieval date | Live source value | Outcome | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | | unit points | | | | | match / mismatch | |
| 2 | | unit points | | | | | match / mismatch | |
| 3 | | detachment cost | | | | | match / mismatch | |
| 4 | | detachment cost | | | | | match / mismatch | |
| 5 | | enhancement cost | | | | | match / mismatch | |
| 6 | | enhancement cost | | | | | match / mismatch | |
| ... | (unverified-pricing sample, from reports/<rulesVersionId>/unverified-pricing.md) | | | | | | match / mismatch | pricing_confidence: unverified |
| ... | (hybrid-edition sample, from reports/<rulesVersionId>/edition-mismatch.md) | | | | | | match / mismatch | is_hybrid_edition: true |

**Column notes**:
- **Shipped value**: exactly what the published snapshot carries for this entity (points, DP
  cost, or enhancement cost) — quote it, do not paraphrase.
- **Source page retrieved**: the URL actually opened to check this row.
- **Retrieval date**: the date the live page was actually viewed for this row — should match
  "Date" above; if a row was checked on a different day, say so explicitly rather than let the
  header date stand in for it.
- **Live source value**: what the live page states right now for the same entity. For an
  `unverified` row, this is expected to be **absent** from the current page listing (that is what
  `unverified` means) — record that absence as the "live source value" rather than leaving the
  cell blank, so a reader can tell "checked, and it's genuinely not listed" from "not checked".
- **Outcome**: `match` if the shipped value is what a player should be charged today per the live
  source (for an `unverified` row, "match" means the source is still silent and the carried-
  forward price is still the best available answer, not that a number was literally re-confirmed);
  `mismatch` otherwise.

## Mismatches found

For every row marked `mismatch` above, state what was done about it:

- If already corrected in a later version: which `rulesVersionId`, and how (a normal rebuild
  picking up the source's current value, or a withdrawal — see `docs/runbook.md`'s rollback
  section).
- If not yet corrected: an open item, with an owner and where it is tracked (e.g. a
  `curation/resolutions.json` entry, an issue, or a note that the next scheduled `detect` sweep
  is expected to pick it up automatically since the pipeline re-derives verified prices from the
  source on every release).
- If the "mismatch" turned out to be an artifact of the check itself (wrong page, stale browser
  cache, mis-read units): say so — a spot check's own false positives are worth recording too, so
  a future checker does not repeat the same misreading.

## Verdict

One line: how many of the sampled rows matched, whether every mismatch has a stated resolution or
open item, and whether this spot check gives confidence in the published version's pricing
accuracy beyond what the automated report alone establishes.
```
