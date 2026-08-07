<!-- AI-Assisted: Claude Code (model: claude-opus-5) - Re-recorded the FR-034 consumer-compatibility
     evidence for the wh40k-11e-2026-08 candidate (004 tasks T081, T082), replacing the version
     carried by the superseded candidate commit, whose sections 2b and 2c stated a duplicate-key
     diagnosis that a ground-truth re-run did not support. That diagnosis is now moot: the
     emitter collapses byte-identical rows and CON-DUPLICATE-KEY blocks the disagreeing ones, so
     the classes it described no longer reach a bundle. Every figure below is from a run against
     THIS candidate's bundle, sha256 f9ad67b3...cce566, on 2026-08-07. -->
# Consumer compatibility — `wh40k-11e-2026-08`

**This candidate's bundle**: `rules-wh40k-11e-2026-08.json`,
sha256 `f9ad67b34c5d4f2beb3089d495916ed812aef30c0f9d85e9d4625418ffcce566`, 9 401 976 bytes,
`bundleFormatVersion` 1, `snapshotMeta.schemaContractVersion` 1.

**This file is hand-authored evidence, not pipeline output.** The build does not produce it, and
a later rebuild of this branch will not regenerate it. Read every claim as "a person ran this
command and this is what it printed", and re-run anything you would otherwise take on trust.

## Verdict in one line

**The app-side ingest proof passes: exit 0, zero violations, zero duplicate primary keys.** This
is the second bundle to ingest end to end, and the first one that is also publishable.

## 1. App-side ingest (T081) — **PASS**

```bash
python tools/consumer_compat.py rules-wh40k-11e-2026-08.json   # exit 0, no violation lines
```

`tools/consumer_compat.py` is **unmodified and deliberately pinned at schema contract v1.2.0**.
That pin is the whole point of the check: it stands in for a consumer built against the released
schema, so what it proves is that this candidate is ingestible by software that predates every
addition in it. It builds the v1.2.0 schema verbatim, loads each array into its table, turns on
real foreign keys, and reports rather than dies on the first collision.

| Guarantee exercised | Result |
|---|---|
| 12 — one row per declared primary key, every table | pass, zero duplicate keys |
| 4 — foreign keys resolve under `PRAGMA foreign_keys=ON` | pass |
| 3 — cost bands contiguous, every tier has its cost row | pass |
| 5 — no ability row carries an empty summary | pass |

It does **not** know `datasheetCostContexts` / `datasheet_cost_context`, the array this release
adds, and it does not have to: an array a consumer has never heard of is ignored by a consumer
that loads the tables it declares. **That it passes while not knowing about the new array is the
additive-compatibility proof**, and it is why the conditional prices went to a new array rather
than into `datasheetCosts` under an extra key column — the latter would have put extra rows under
a primary key v1.3.x consumers already declare, which is a constraint error, not an ignorable
column.

The pricing exercise reports `pricing exercise skipped`. That is expected and is not a gap: the
exercise army is composed of the minimal synthetic fixture's entities, which a real bundle does
not carry. The schema construction, the load, the foreign-key pass and the four guarantees above
all ran against the real 9.4 MB bundle.

## 2. Site-side build (T082) — **carried forward, with the delta stated**

The unmodified released `003` site build (`The-BadgerWorks/wargame-rules-web`, `main` at
`c0e58f7`, nothing modified) was run on 2026-08-06 against the immediately preceding build of
this same tree — bundle sha256 `918465496b0d98968287fc8e1e206a288676ef3ef01da12143cdc6944b299bd6`
— and produced **2 462 pages** with `verify-dist` green on all four checks (coverage, internal
links, content boundary, banner). **It was not re-run against this candidate**, and this section
is therefore weaker than section 1. What makes it still worth reading is that the difference
between the two bundles is known exactly rather than assumed:

```
datasheetAbilities: 7 901 -> 7 909 rows   (+8, -0)
every other array, and snapshotMeta:      identical
```

The eight added rows are the seven newly approved Aeldari ability summaries (one of which is
bound to two datasheets) that were the sole remaining blocker on the previous build. No
datasheet, cost, tier, keyword, detachment or enhancement row moved.

The site check most sensitive to summary text is the content boundary check, which compares each
rendered text node — whitespace-collapsed — against the raw bundle string, un-collapsed, so any
summary carrying a newline, a tab or a double space fails it. Re-checked directly on this
candidate's bundle across every summary-bearing field of every array: **0 violations**. A
reviewer who wants the site proof at full strength should re-run the site build; a reviewer who
accepts a stated delta has the delta.

## 3. What is no longer true of the superseded evidence

The previous candidate's version of this file described `datasheetCosts` duplicates as
"byte-identical rows across 32 datasheets that appear under more than one faction". They were
neither byte-identical nor cross-faction: 19 of 36 groups disagreed about the price, and 32 of 36
were one faction whose points page prints two cost tables for the same unit. Both halves are now
resolved at source rather than at emission — the conditional prices carry a `pricingContext` and
live in `datasheetCostContexts` (39 rows), and any collision whose rows still disagree raises the
blocking `CON-DUPLICATE-KEY` instead of being silently deduplicated. **This candidate raises zero
`CON-DUPLICATE-KEY` findings of any class.**
