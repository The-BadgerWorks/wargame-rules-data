<!-- AI-Assisted: Claude Code (model: claude-opus-5) - Scaffolded the 004 enrichment fixture
     catalogue (task T007): the quirk classes composition, options, keywords, and the four
     authored summary classes are each proven against, restating the synthetic-fixture rule that
     governs every fixture in this repository (FR-006, quickstart section 1, research D10). -->
<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Documented the 007-loadout-display-
     fidelity additions (Setup phase T005-T008): GF12-GF15, the CSV-only scoping decision, and
     why each new datasheet id exists. -->
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

## The quirk classes `006-unit-loadout-fidelity` added

`006` extends the same two grammars, so it extends this catalogue rather than starting another
one. Five datacards joined `wahapedia-html/glimmerfen-covenant.html`, with their option and
composition rows mirrored into `wahapedia/` — the option grammar is mode-blind and has to be
proven so over the new shapes exactly as it was over the old ones.

| Datasheet | What it carries | Why |
|---|---|---|
| `GF07` Purgeflight Wardens | one invented row per research D1b class (1a-1f, 2-13) plus the Purgation-Squad shape: a scoped stem naming a model subset and a maximum, a multi-item **replaced** set, and multi-item **granted** bundles | US1's whole surface. Also the legacy conflated single-string bundle label (the O1 class, which *parses today*), a `can each` distributive head, a footnote marker inside a stem, an item naming **two** weapon lines (`tide hammer`) and one naming **none** (`void net`) |
| `GF08` Mirebound Choir | two default-equipment sentences, each naming a different model group | FR-013's differentiated leader/squad shape, with one unlinkable item in each group |
| `GF09` Fenwatch Sentinel | **no** default-equipment sentence, and no options at all | FR-015: absence has to be distinguishable from a failed extraction |
| `GF10` Gloamtide Host | two composition rows and **one** whole-unit equipment sentence | Research D1e measured this on 195 cards. The correct result is `appliesTo = unit` with no `compositionLine`, which is why the link is resolved by name and never by ordinal |
| `GF11` Snarebound Wretches | a composition line neither production resolves, plus an equipment sentence | FR-016: no equipment attaches to a composition structure that does not exist |

`curation/option-overrides.json` and `curation/equipment-overrides.json` carry the override
escape hatch in both shapes: one row in `006`'s extended shape (eligibility scope, per-choice
`items`) and one in `004`'s single-item shape **unchanged**, because FR-011 requires an override
written before this feature to keep validating and resolving identically after it.

Two properties of the `006` additions are worth stating because a reader will otherwise assume
the opposite:

- **The new option rows are all residual today.** That is the point: they are the shapes the
  `004` grammar was never built for. `tests/enrichment/test_options_grammar.py`'s pinned residual
  is therefore scoped to `GF01`-`GF06`, so a deliberate `006` improvement cannot read as a `004`
  regression there.
- **Nothing in `GF07`-`GF11` is a capture.** Every model name, item name, count, and price is
  invented, and the option rows carry the *grammar's* vocabulary because that is the only part of
  a sentence a parser matches on.

## The quirk classes `007-loadout-display-fidelity` added (Setup phase, T005-T008)

Four more invented datasheet ids, `CSV-only` by deliberate scope decision (stated once here
rather than at each site): `007`'s Setup-phase fixtures serve the grammar- and curate-level unit
tests that read `option_rows`/`composition_rows` through `tests/enrichment/conftest.py` — the
same low-level access `004` and `006`'s own option/composition tests already use — which needs
only `wahapedia/`'s CSV mirror. Mode-blind HTML parity for these four ids is left to whichever
later-phase task first needs it (T042 onward), the same way `GF09`/`GF11` already omit files they
have no content for.

| Datasheet | What it carries | Why |
|---|---|---|
| `GF12` Marshlight Vigil | 11 option rows: `research D3.3`'s three legacy stem-object outcomes (given-up item resolves and links; stated but unlinkable; no given-up item at all) plus the `OPT-SCOPE-UNRESOLVED` edge case, a marker on a granted item's name, three footnote-restriction shapes (`not_replaceable` unscoped, `not_replaceable` scoped to a named model, `one_per_unit`), one unlinkable restriction, one restriction-shaped line matching no vocabulary member, and one over-length replaced item (135 chars) | `007` US2 (T005), US3 (T006), and D3.4's `OPT-ITEM-OVERLONG` (T008) |
| `GF13` Fenward Cohort Alpha | a two-row header (`9`) summing to its two successors (`3 + 6`) | research D1's first header shape (T007) |
| `GF14` Fenward Cohort Beta | a single-row header (`5`) equal to its one successor (`5`) | research D1's second header shape (T007) |
| `GF15` Fenward Relict Watch | a genuine first model row (`1`), then a **near-miss** row that is fixed-size, unlinkable, and numerically equal to the sum of the other two rows (`1 + 7 = 8`) — but is not itself the datasheet's first row | the one case research D1's five-signal rule is designed not to refuse: the position gate that opens the conjunction, not a fifth signal happening to fail (T007) |

`GF12`'s composition also carries a footnote marker on `Marshlight Sentry*` — the composition-side
half of the marker-residue fixture pair, alongside the option-side marker on `marsh axe*` in row 5.

Two properties worth stating, because a reader will otherwise assume the opposite:

- **`GF12`-`GF15`'s option and composition rows all parse successfully today** under the existing
  `004`/`006` grammar (verified against `pipeline.parse.options_grammar.parse_row` and
  `pipeline.parse.composition_grammar.parse_entry`) — none of them exercises `OPT-UNPARSED` or
  `CMP-UNRESOLVED` by itself. What each one exercises is a **later** stage `007` adds: the stem
  production (T021), the constraint production (T039), the five-signal header refusal (T030), or
  the over-length-item finding (T024) — none of which exists yet as this Setup phase lands.
  `GF12`'s five footnote-restriction-shaped rows (lines 6-10) are the deliberate exception: they
  are refused today (unparsed), which is the residual `T039`'s new production is added to.
- **`MODEL_LINES` in `tests/enrichment/conftest.py` carries `GF12`-`GF15`'s model-name entries**,
  on the same zero/one-match discipline `GF01`-`GF06` already establish — `GF13`'s and `GF14`'s
  header names and `GF15`'s near-miss name are deliberately absent from their own entries, the
  zero-match case.

## The equivalence-check fixture pair `007` added (Setup phase, T010)

Two more datasheets, HTML-only this time (the equivalence check, `007` FR-019-FR-022, reads
source text from the same in-memory `detail` the html-mode extractor produces — see `research.md`
D6 and `reports/equivalence-availability/`).

| Datasheet | What it carries | Why |
|---|---|---|
| `GF16` Emberlight Watch | a single-item, whole-unit default-equipment sentence — `Every model is equipped with: qzolthgeist rod.` — worded so its rendering (once `render/loadout.py` exists) is byte-identical to the source sentence itself, not merely normal-form-equal | the equivalence check's **matching** pair (T050), and — because `qzolthgeist` is a distinctive invented token found nowhere else in this repository — the **retention test** fixture (T051): grep every artifact a run writes for it and expect zero hits |
| `GF17` Duskmire Sentry | the same shape, stating `glow lance` — paired with a `curation/equipment-overrides.json` entry that publishes `storm maul` instead | the equivalence check's **mismatched** pair (T050): the published/rendered equipment deliberately disagrees with the card's own raw sentence, still readable in-process during a build |

**The `not_compared` case needs no new fixture.** `GF09` Fenwatch Sentinel already states no
default-equipment sentence at all (`006`'s own FR-015 fixture) — exactly contract §9's second
`not_compared` reading, "the block rendered empty because every row was legitimately omitted."

**Neither `GF16` nor `GF17` can be proven against `render/loadout.py` yet** — that module does not
exist until `007` Phase 6 (T044) lands. Both are constructed so the claim is checkable by
inspection today: `GF16`'s wording is chosen to equal contract §3.3's `E.group.unit` template
(`Every model is equipped with: {itemList}.`) verbatim once the single item's stored name fills
the slot, and both cards' equipment sentences are confirmed (by this Setup phase) to parse through
`pipeline.parse.equipment_grammar.parse_sentence` unmodified.

## Using them

```bash
rules-pipeline build --offline --fixtures fixtures/enrichment --rules-version-id local-dev
pytest tests/enrichment -q
```

`--offline` is not a convenience here either: it makes "the test suite made a network request" a
failure with a stack trace rather than a flake.
