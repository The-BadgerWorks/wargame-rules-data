<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Authored the detection fixture set and
     documented why "an unreachable source" is not a fifth sub-directory here (task T100,
     research D4b, D10). Every name in every page below is invented; nothing was captured. -->
<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - R05-fix item 6 (gate on PR #30): `detect`
     now also probes the detail source's own `Last_update.csv`, so every set below gained a
     minimal synthetic `wahapedia/` directory -- one placeholder file, since `--fixtures` reads it
     by glob rather than by `EXPORT_FILES`'s exact name list and `detect` never parses the detail
     source's rows, only acquires and records its outcome. -->
# `fixtures/detection/`

Four page-set pairs, each a deliberate one-step edit away from `baseline/`, so
`tests/detect/test_digest_projection.py` and `tests/detect/test_detection_outcomes.py` can
assert exactly what research D4b claims: a mechanical change moves the digest, a presentation
change does not, and a structural break refuses to guess.

Like every fixture in this repository, every page is **synthetic** — invented factions, invented
units, invented placeholder prose, hand-authored from the structure description in
`research.md` §0.2 (`fixtures/README.md`).

## Layout

```text
fixtures/detection/
├── baseline/mfm/                    # the reference state: two factions, one unit and one
│   └── wahapedia/Last_update.csv    # detachment each; a placeholder detail-source probe --
│                                     # detect never parses these rows, only acquires them
├── mechanical-change/mfm/           # verdant-marchers' 5-model band moves 80 -> 85 pts;
│   └── wahapedia/Last_update.csv    # duskrail-cabal is byte-identical to baseline
├── presentation-only/mfm/           # both factions: reordered rows and sections, renumbered
│   └── wahapedia/Last_update.csv    # P:/S: ids, different colour/utility classes, an added
│                                     # UPDATED/Unique tag, an added delta marker on an
│                                     # UNCHANGED value, extra whitespace -- every mechanical
│                                     # value is identical to baseline
└── restructured/mfm/                # verdant-marchers' 5-model swap is gone, so its
    └── wahapedia/Last_update.csv    # <template> is never filled; duskrail-cabal is
                                      # unchanged, to prove one broken page fails the whole
                                      # sweep (FR-008)
```

## Running it

```bash
rules-pipeline detect --fixtures fixtures/detection/baseline --offline        # first run: exit 10 (no prior digest)
rules-pipeline detect --fixtures fixtures/detection/baseline --offline        # second run: exit 0 (nothing moved)
rules-pipeline detect --fixtures fixtures/detection/mechanical-change --offline  # exit 10
rules-pipeline detect --fixtures fixtures/detection/presentation-only --offline  # exit 0
rules-pipeline detect --fixtures fixtures/detection/restructured --offline      # exit 41
```

Each invocation reads and rewrites `state/detection-digest.json`, so the sequence above is
stateful in the order shown — the tests drive `run_detect` directly against an isolated
`state/` per case rather than sharing the repository's own.

## Why there is no `unreachable/` sub-directory

An unreachable source is a property of the network, and a fixture is a filesystem read that
always succeeds — there is no HTML this directory could hold that would make `--fixtures`
simulate a `403`, a `429`, or a connection refusal. `tests/detect/test_detection_outcomes.py`
exercises that case the way `tests/unit/test_http_politeness.py` already does: a real
`PoliteClient` against a mocked `httpx` transport (`pytest-httpx`) that refuses or times out,
passed into `run_detect(..., client=...)`, asserting exit `40`. Nothing under this directory is
skipped as a result; the case is realised as a behaviour test instead of a fixture pair, because
that is what it actually is.
