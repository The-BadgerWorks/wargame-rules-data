<!-- AI-Assisted: Claude Code (model: claude-opus-5) - Documented the pre-enrichment schema
     baseline (004 task T065). The JSON beside this file admits no comment syntax of its own,
     and adding a `_comment` key to it would change the very document the baseline exists to
     freeze. -->
# `fixtures/contract/`

## `bundle.schema.pre-enrichment.json`

**A frozen copy of `schemas/bundle.schema.json` as it stood before
`004-rules-data-enrichment` touched it**, taken verbatim from commit `531ed4b` (*Add the curated,
bundle, and authored JSON Schemas and their loader*). Eighteen arrays, and the layout rules of
`curated-snapshot-format.md` §3 that the app and the reference site were both released against.

It exists so `tests/contract/test_additive_compatibility.py` can make FR-031's claim —
**nothing existing changed name, shape, meaning, ordering, or optionality** — as a *comparison*
rather than as an assertion someone wrote down while looking at the diff they had just made.

Two things about the way it is used are deliberate:

- **It is a copy, not a `git show`.** A test that reached into history would silently start
  comparing against something else the moment history was rewritten, squashed, or grafted, and
  would fail for reasons that have nothing to do with the schema. A committed file changes only
  when someone changes it, which is exactly the property a baseline needs.
- **Changing it is the point of failure, not the fix.** If the additive-compatibility test fails,
  the schema has moved something a released consumer reads. The response is to put it back —
  editing this file to match instead would delete the only evidence that anything moved, and the
  breakage would surface next in an app that cannot ingest a published snapshot.

The one legitimate reason to replace it is a **deliberate MAJOR** bump of `bundleFormatVersion`,
at which point the baseline moves with it and the test is comparing the new layout against the
new baseline.
