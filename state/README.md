<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Explains the seeded state files (task
     T011), since JSON and JSONL admit no comment syntax for an AI-Assisted header. -->
<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - R05-fix (gate on PR #30): documented the
     export-digest state file's added identity fields (item 5) and that `detect` -- and only
     `detect` -- now reads and writes it (item 6, Product Owner ruling 2026-09-03). -->
<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - R05-fix2 (gate on PR #30, Product Owner
     ruling 2026-09-03 REVERSING the ruling above): documented the added `content_fingerprint`
     field (item 2) and that no caller reads or writes this file today -- `detect`'s wiring was
     reversed; wiring is deferred to a future rung. -->

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
- `wahapedia-export-digest.json` -- five fields: `digest` (sha256 hex over the detail source's
  `Last_update.csv` text, never the text itself -- 009 rung R05, task T090, FR-030), the source
  identity it was taken under -- `source_base_url`, `declared_edition_code`, `mode` (rung R05-fix
  item 5) -- and `content_fingerprint`, the corpus fingerprint the acquisition that recorded this
  state itself computed (rung R05-fix2 item 2), carried forward so a future short-circuited
  acquisition can report "the same corpus as this one had" rather than fingerprinting the
  near-empty payload set a skip actually fetches. Compared by
  `pipeline.acquire.wahapedia.acquire_wahapedia`'s opt-in short-circuit (its `state_path`
  parameter) to decide whether the rest of the export is worth re-fetching -- a convenience
  pre-check, never a substitute for the content fingerprint the pipeline already computes over
  whatever it actually fetches, and never comparable across a changed source identity: a digest
  match recorded under a different `source_base_url`, `declared_edition_code`, or `mode` is "no
  comparable prior," not a skip. Written only by
  `pipeline.acquire.wahapedia.save_export_digest_state`, and only once a caller's own whole sweep
  has succeeded -- never from inside acquisition itself, so a run that acquires a changed export
  and then fails downstream cannot advance this file (item 2). **No caller reads or writes it
  today**: `rung R05-fix` wired `rules-pipeline detect` to it, and the Product Owner reversed
  that ruling (`rung R05-fix2`, `docs/follow-ups.md` item 30) -- `detect` is reverted to its
  pre-wiring behaviour and `rules-pipeline build` was never wired either. Seeded empty (`{}`): no
  run has ever reached the short-circuit.
