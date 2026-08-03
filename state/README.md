<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Explains the seeded state files (task
     T011), since JSON and JSONL admit no comment syntax for an AI-Assisted header. -->
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
