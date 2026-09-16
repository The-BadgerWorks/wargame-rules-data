<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Explains the seeded state files (task
     T011), since JSON and JSONL admit no comment syntax for an AI-Assisted header. -->
<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - R05-fix (gate on PR #30): documented the
     export-digest state file's added identity fields (item 5) and that `detect` -- and only
     `detect` -- now reads and writes it (item 6, Product Owner ruling 2026-09-03). -->
<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - R05-fix2 (gate on PR #30, Product Owner
     ruling 2026-09-03 REVERSING the ruling above): documented the added `content_fingerprint`
     field (item 2) and that no caller reads or writes this file today -- `detect`'s wiring was
     reversed; wiring is deferred to a future rung. -->

<!-- AI-Assisted: Claude Code (model: Claude Opus 5) - 010 R5: the export-digest identity no
     longer carries an acquisition-arm field, so the field count and the two sentences that
     named it are corrected here. -->
<!-- AI-Assisted: Claude Code (model: claude-opus-5) - 010 R9 task 1: removed the
     `wahapedia-export-digest.json` entry. The file and the export-timestamp short-circuit that
     read it are deleted (Owner ruling 2026-09-15), so the entry documented four fields, a
     writer and an opt-in parameter that no longer exist. Replaced by one past-tense line under
     the list, so a curator who remembers the file learns it was removed rather than that the
     tree is broken. The three live entries above are untouched. -->
# state/

Operational state written and read only by the pipeline and its CI workflows. These files hold
**one-way digests and hashes only** -- never source material, never publisher wording, and
nothing from which any acquired text could be reconstructed (FR-010, FR-013).

- `detection-digest.json` -- per-faction and whole-release sha256 digests of the
  presentation-free projection the `detect` command computes
  (`contracts/pipeline-run-interface.md`, research D4b). Seeded empty: `per_faction: {}`,
  `release_digest: null`. A digest moving is what raises a candidate; the digest itself carries
  no recoverable content.
- `run-ledger.jsonl` -- one append-only JSON line per pipeline run: run id, trigger, channel,
  timings, stage outcomes, coverage figures, finding counts by class and severity, unverified
  count, hybrid count, candidate ref, and exit code (`pipeline-run-interface.md` §6). Seeded
  empty. Entries carry mechanical values only -- ids, counts, and codes, never free text.
- `published-checksums.json` -- sha256 and size for every published release asset, re-verified
  daily by `.github/workflows/integrity.yml`. Seeded as `[]`.

`wahapedia-export-digest.json` was a fourth file here. It held a one-way digest of the detail
source's whole-export change marker, and the export-timestamp short-circuit that compared it was
deleted in 010 R9 (Owner ruling 2026-09-15) having never had a caller. Both the file and the
mechanism are gone; `docs/follow-ups.md` items 30-34 record the close-out.
