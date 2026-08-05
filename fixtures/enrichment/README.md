<!-- AI-Assisted: Claude Code (model: claude-opus-5) - Scaffolded the 004 enrichment fixture
     catalogue (task T007): the quirk classes composition, options, keywords, and the four
     authored summary classes are each proven against, restating the synthetic-fixture rule that
     governs every fixture in this repository (FR-006, quickstart section 1, research D10). -->
# `fixtures/enrichment/`

The quirk-class catalogue for `004-rules-data-enrichment`: structured unit composition, the full
wargear option set, keyword classification, and the three new authored summary classes.

**Every file here is synthetic** — invented faction names, invented unit names, invented model
names, invented placeholder prose, hand-authored from a *description* of the structure. That rule
is stated in full in [`../README.md`](../README.md) and it is not relaxed for this feature. In
particular:

- **`004` does not weaken it — it restates it twice.** `spec.md` FR-006 forbids committing raw
  acquired source material to any repository; FR-027 forbids the publisher's wording for a faction
  rule, a detachment rule, or a keyword reaching curated data, working storage, reports, run logs,
  or version control. A captured datacard page violates both, and **redacting a capture into a
  fixture is not a way round either** — the structure-plus-wording is still what was committed.
- The structure descriptions to author from are in `004/research.md` D2 (composition), D3
  (options), and D7 (keywords), and the measured baseline proportions there are what the coverage
  assertions are calibrated against.
- The `wahapedia-html/` set exists so the same grammars can be proven **mode-blind** (research
  D1d): the `csv` and `html` sets carry the *same* invented units in the *two* source shapes, and
  `pipeline/parse/composition_grammar.py` and `pipeline/parse/options_grammar.py` must consume
  both unmodified. `docs/verification/html-markup-spike.md` records the real markup's structure —
  class tokens, block segmentation, and the two traps — which is what the `wahapedia-html/`
  fixtures reproduce. Nothing retrieved during that spike was kept.

## Layout

```text
fixtures/enrichment/
├── wahapedia/        # csv-mode detail source: the pipe-delimited export shape
├── wahapedia-html/   # html-mode detail source: synthetic datacard markup, same units
└── curation/         # authored records in mixed review states, for the four summary classes
```

## The quirk classes each fixture set must cover

Transcribed from `quickstart.md` §1 so the catalogue is checkable against the plan without
opening another repository. **A new quirk gets a fixture before it gets a parser change.**

| Composition (research D2) | Wargear options (research D3) | Keywords (research D7) |
|---|---|---|
| fixed count (`min == max`) — the majority shape, and never "missing data" | a flat group | a parent faction and two chapter keywords beneath it |
| a ranged count | a nested `<li>` sub-list group | a datasheet carrying one, both, and neither |
| a non-breaking hyphen inside the range | a per-model group (`This model`) | a chapter also modelled as its own faction |
| a per-model attachment | a per-N-models group (`For every N models`) | an unclassified faction keyword |
| a conditional model line (a leader swap) | an explicit "no change" choice | a keyword used only on weapon profiles |
| an unresolvable free-text line | priced / unpriced / priced-but-unmatched choices | casing, spacing, and punctuation variants of one keyword |

| Authored class | Cases the `curation/` set must carry |
|---|---|
| `abilities` (existing) | unchanged — the generalisation must not move its behaviour |
| `faction_rules` | approved · draft · in_review · needs_rereview · `army_rule_state="none"` · an omitted file (uncurated), which is a *different* state from `"none"` |
| `detachment_rules` | two factions · mixed review states · two entries sharing a rule name across factions · a detachment owning more than one rule |
| `glossary` | one keyword used by several factions · casing/spacing/punctuation variants · a numeric-parameter keyword · a keyword only on weapon profiles · an orphaned entry · a digest-less entry |

## Using them

```bash
rules-pipeline build --offline --fixtures fixtures/enrichment --rules-version-id local-dev
pytest tests/enrichment -q
```

`--offline` is not a convenience here either: it makes "the test suite made a network request" a
failure with a stack trace rather than a flake.
