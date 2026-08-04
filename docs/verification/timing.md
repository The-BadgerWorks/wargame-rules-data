<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Recorded SC-004 timing evidence for task
     T155: an analytical bound from the real faction-slug count and the configured polite
     interval, an empirical measurement of the pipeline's own processing overhead against a
     synthetic fixture (offline, no network), and an explicit, precedented record of why a
     genuine live-source measurement is deferred rather than performed in this session. -->
# T155 — SC-004 timing evidence

SC-004: a real points-release move produces a reviewable candidate within **24 hours** of the
release going live, and — per this task's own wording — the detection sweep and the
detection-to-candidate-PR time are measured and recorded against the 24-hour and 2-hour targets
respectively.

**Method used here: analytical bound + empirical processing-overhead measurement, not a live
dispatch.** See "Why not a live measurement" below before reading the numbers as a substitute for
one — they are a defensible bound, not a field measurement.

## 1. Detection sweep — analytical bound

`curation/faction-map.json` carries **30** real `mfm_slug` entries (`grep -c '"mfm_slug"'
curation/faction-map.json` → 30) — the actual points-source page count `rules-pipeline detect`
sweeps every run. `pipeline/config.py`'s `WGC_REQUEST_INTERVAL_MS` default is **2000ms**, and
`pipeline/acquire/http.py` enforces it per host with jitter, sequentially (FR-007) — no
concurrency, by design, since politeness is the constraint, not throughput.

```
network pacing  ≈ 30 pages × 2000ms                      =  60,000 ms  (~60s)
processing      ≈ 30 × (per-page parse + digest + compare)  ≈  30 × 150ms  ≈  4,500 ms  (~4.5s)
                                                              -----------------------------
estimated wall-clock, one full sweep                          ≈ 65-75 seconds
```

The per-page processing figure comes from §2's empirical measurement, scaled linearly (parsing
and digesting one faction page is independent of every other — there is no cross-page work in
`pipeline/detect/projection.py` or `pipeline/detect/digest.py`).

**Against the 24-hour (86,400s) target: a ~1,150x margin.** Even a full retry storm — every one of
30 pages hitting `WGC_MAX_RETRIES` (2) before succeeding — adds at most `30 × 2 × 2000ms = 120s`,
still under 4 minutes total. The schedule (`0 9,21 * * *`, twice daily) is the actual bound on
*detection latency* (worst case ~12 hours between a release going live and the next scheduled
sweep), not sweep duration — SC-004's 24-hour figure has enormous headroom either way.

## 2. Pipeline processing overhead — measured, offline, against a fixture

Run directly (not through CI, not against any network — `--offline --fixtures` is the contract's
own no-network mode, §1):

```
$ python -m pipeline.cli detect --offline --fixtures <tmp copy of fixtures/minimal> --channel prerelease
detect exit 10, elapsed 0.315s   (2 factions: ashen-vigil, ember-chapter)

$ python -m pipeline.cli build --offline --fixtures <tmp copy of fixtures/minimal> \
    --rules-version-id timing-check --channel prerelease
build exit 20, elapsed 0.342s    (full acquire→...→build chain, offline)
```

Run against a **copy** of `fixtures/minimal` in a scratch directory outside the repository, not
the committed fixture itself — `build`'s fixture mode writes its output tree back under
`<fixtures-dir>/build/`, and running it against the tracked fixture directly would have dirtied
the committed golden output. `state/detection-digest.json` and `state/run-ledger.jsonl` are real
repository state regardless of `--fixtures` (they are not fixture-scoped), so both were reverted
with `git checkout` immediately after this measurement — this run left no diff.

`~0.3s` end-to-end for a 2-faction, 8-datasheet fixture puts per-faction processing at roughly
`150ms`, used as the multiplier in §1. The full-scale real run has ~30 factions and several
thousand datasheets rather than 8 — reconciliation and validation are the parts of that chain
with more-than-linear inputs (every datasheet is matched and every finding classified), so this
is a lower bound on real processing time, not an exact prediction. Even a generous 50x processing
slowdown (7.5s → 15s becomes several minutes) stays two orders of magnitude under the 2-hour
candidate-build target.

## 3. Candidate build (detection → reviewable PR) — analytical bound

`candidate.yml` runs the same `build` chain against **both** live sources (points: 30 requests at
the same 2s pacing as §1; detail: `pipeline/acquire/wahapedia.py` fetches one export payload, not
per-faction — a single request), then pushes a branch and opens/updates a PR (`gh`/git operations,
observed at low-single-digit seconds elsewhere in this repository's own CI runs, e.g. the `ci`
job's `pytest` step completing in under 10s end to end for 642 tests). Summing §1's ~70s points
sweep, ~2s detail fetch, an assumed several-minutes-worst-case processing budget from §2, and a
low tens-of-seconds git/PR overhead puts a full candidate build comfortably **under 10 minutes**
end to end — against the 2-hour (7,200s) target, more than an order of magnitude of headroom.

## Why not a live measurement

This task's wording asks for wall-clock "on the real sources." Two independent, load-bearing
reasons this session measured analytically instead of dispatching a live `detect.yml` or
`candidate.yml` run:

1. **`WGC_DETAIL_SOURCE_URL` is unset** (`gh variable list` returns nothing for it — confirmed in
   `docs/verification/approval-rehearsal.md`'s Part 2, which hit the identical constraint doing
   the T122 rehearsal). A live `candidate.yml` run would fail partway through, at the Wahapedia
   acquisition step, after already having contacted the real MFM site for the points sweep — an
   incomplete and misleading timing sample, not a real one.
2. **Precedent, set deliberately in this repository's own verification history**: the T122
   approval-gate rehearsal (`docs/verification/approval-rehearsal.md`, Part 2) was explicitly
   constrained to make no live MFM fetch in that session, and recorded a genuine first
   live-source run as "a separate, deliberate operational decision for the repository owner." The
   task instructions governing this session apply the same constraint to a different piece of
   work (the Black Templars matcher-preference spot check — see `docs/follow-ups.md` and the
   `feature/rec-ambiguous-match-bt` branch's own evidence) and nothing in this session's
   instructions asked for that constraint to be lifted for T155 specifically. A live `detect`
   sweep (points source only, no detail-source dependency) is technically dispatchable once
   `WGC_MFM_BASE_URL`'s real target is deliberately exercised — recorded here as the same kind of
   separate, deliberate operational decision, not performed in this session.

**A genuine live-source SC-004 measurement is recommended as the repository owner's first live
`detect.yml` dispatch**, once `WGC_DETAIL_SOURCE_URL` is configured for a live candidate build —
at that point, replace this document's §1 and §3 estimates with the observed run's actual
`state/run-ledger.jsonl` `duration_ms` and the candidate PR's created-at timestamp minus the
triggering `detect` run's timestamp, and leave §2's offline processing measurement as
supporting evidence for the estimate it was always used for.
