<!-- AI-Assisted: Claude Code (model: claude-opus-5) - Recorded the local proof that the
     published-at fix lets the approved wh40k-11e-2026-08-2 bundle be rebuilt, unchanged, on a
     later calendar day (FR-033, FR-039). -->
# wh40k-11e-2026-08-2: the approved bundle, rebuilt a day later

*Evidence for the candidate carrying the `published_at` fix. Nothing here changes the candidate's
content: it is the same data, the same curation, and the same checksum the Product Owner
approved.*

## Why this candidate exists at all

`publish.yml` refused the standing dispatch with exit 51 (run 31657300051). The refusal was
correct in form and wrong in substance: a whole-bundle structural diff of the approved artifact
against the rebuilt one came to **one scalar difference**, `/snapshotMeta/publishedAt`, 08-12
against 08-13. `published_at` had been documented as a build input since 002 and had never been
reachable from the CLI, so every build stamped its own UTC day and an approval could only be
published inside the day it was built.

The gate's rebuild runs **the checked-out commit's own code** (`pip install -e .` against the
approved tree), so a fix on `main` alone would not have reached it. This candidate is the
approved tree plus that fix, which is the whole of the difference.

## What changed relative to the approved candidate

Against `main` (which carries `a4d08a0`'s tree verbatim after the merges of PR #10 and PR #9):

| Path | Delta |
|---|---|
| `data/` | none |
| `curation/` | none |
| `reports/wh40k-11e-2026-08-2/` | none |
| `pipeline/`, `tests/`, `.github/workflows/publish.yml`, `docs/` | the published-at fix |
| `reports/006-published-at-fix/` | this file |

The approved data tree is byte-identical. That is deliberate: the rebuild reads `data/` as its
prior baseline and `reports/wh40k-11e-2026-08-2/report.json` as its publication date, so
committing a rebuilt `data/` over the approved one would change the inputs to the very rebuild
the approval assertion checks.

## The assertion

Live build from this candidate's tree, run on **2026-08-13**, in the environment `publish.yml`
uses (`html` mode, `wh40k-11e`, gates on/on/off, channel `published`):

```
rules-pipeline build --channel published --rules-version-id wh40k-11e-2026-08-2 \
                     --since wh40k-11e-2026-08 --published-at-from-report

rules-pipeline: publishedAt 2026-08-12T00:00:00Z
EXIT 20
```

```
expected  7ab360b180181b2536a97946a0d2334b75ed9afc642019a629edb3c19393db9d / 11 253 406 bytes
actual    7ab360b180181b2536a97946a0d2334b75ed9afc642019a629edb3c19393db9d / 11 253 406 bytes
```

**The approved checksum, on a day that is not the approved day.** `--published-at-from-report`
read `2026-08-12T00:00:00Z` out of this checkout's own
`reports/wh40k-11e-2026-08-2/report.json`, which is where the candidate build recorded it. No
value was typed at dispatch time, and none can be: the date travels with the commit the approval
names.

This is the sixth independent live sweep to produce these bytes, and the first to produce them on
a different calendar day from the build being reproduced.

## What the rebuild wrote to the working tree, and why it was discarded

2 141 files under `data/`, 10 632 lines each way. Filtering the provenance keys
(`detail_acquisition_id`, `points_acquisition_id`, `source_acquisition_id`, `acquisition_id`,
`content_fingerprint`, `retrieved_at`) leaves a residual of exactly one key:

```
644 x  consecutive_unverified_releases  3 -> 4
  3 x  consecutive_unverified_releases  2 -> 3
```

Not one curated datum moved. That residual is the counter defect filed as issue #12: it is named
for releases and increments once per build, off the working tree. It does not reach the bundle —
the checksum above is the proof, since this very rebuild bumped it and still produced the
approved bytes — and `publish.yml`'s bookkeeping commits `site state` only, never `data`. The
working tree was restored with `git checkout -- data/ reports/` and left clean.

## Dispatch

Unchanged in every parameter except the commit:

```
rules_version_id = wh40k-11e-2026-08-2
commit_sha       = the head of candidate/wh40k-11e-2026-08-2
expect_sha256    = 7ab360b180181b2536a97946a0d2334b75ed9afc642019a629edb3c19393db9d
channel          = published
```

`expect_sha256` is the one parameter that has survived every re-authoring of this release
unchanged, and it survives this one too.
