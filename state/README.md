<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Explains the seeded state files (task
     T011), since JSON and JSONL admit no comment syntax for an AI-Assisted header. -->
<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - R05-fix (gate on PR #30): documented the
     export-digest state file's added identity fields (item 5) and that `detect` -- and only
     `detect` -- now reads and writes it (item 6, Product Owner ruling 2026-09-03). -->
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
- `wahapedia-export-digest.json` -- four fields: `digest` (sha256 hex over the detail source's
  `Last_update.csv` text, never the text itself -- 009 rung R05, task T090, FR-030) plus the
  source identity it was taken under -- `source_base_url`, `declared_edition_code`, `mode` (rung
  R05-fix item 5). Compared by `pipeline.acquire.wahapedia.acquire_wahapedia`'s opt-in
  short-circuit (its `state_path` parameter) to decide whether the rest of the export is worth
  re-fetching -- a convenience pre-check, never a substitute for the content fingerprint the
  pipeline already computes over whatever it actually fetches, and never comparable across a
  changed source identity: a digest match recorded under a different `source_base_url`,
  `declared_edition_code`, or `mode` is "no comparable prior," not a skip. Written only by
  `pipeline.acquire.wahapedia.save_export_digest_state`, called only by `rules-pipeline detect`
  (rung R05-fix item 6, Product Owner ruling) and only once that whole sweep has succeeded --
  never from inside acquisition itself, so a run that acquires a changed export and then fails
  downstream cannot advance this file (item 2). `rules-pipeline build` does not read or write it;
  `run_build` has no coverage guard behind an opt-in, which `docs/follow-ups.md` item 30 records
  as the precondition for ever wiring it too. Seeded empty (`{}`): no run has ever reached the
  short-circuit.
