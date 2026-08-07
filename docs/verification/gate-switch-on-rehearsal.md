<!-- AI-Assisted: Claude Code (model: claude-opus-5) - Recorded the gate switch-on rehearsal that
     contracts/authored-summary-gates.md §7 item 3 requires before any class gate is switched on
     for the first time (004 task T084). Rehearsed against the prerelease channel on 2026-08-06
     with the wh40k-11e-2026-08 candidate; three of the four gates go on, and the fourth is
     recorded here as refused with the measurement that refuses it. -->
# Gate switch-on rehearsal

`contracts/authored-summary-gates.md` §7 item 3 requires each class gate's **first** switch-on to
be rehearsed against the pre-release channel before it happens for real, with the steps, the
entries it blocks, and the elapsed time recorded per class. This is that record.

Rehearsed 2026-08-06 against `wh40k-11e-2026-08` on the `prerelease` channel, live source, `html`
acquisition mode, `WGC_DETAIL_EDITION=wh40k-11e`.

## The mechanism, and the two that were tried and rejected first

A gate is switched on by a **repository variable** read by `candidate.yml` and `publish.yml`
(`vars.WGC_GATE_FACTION_RULES` and its two siblings), not by a library default and not by a
`--config` entry. Two alternatives were tried first and both are wrong:

1. **Library default in `pipeline/config.py`.** A default reaches every fixture build in the test
   suite, where an un-curated fixture is the *expected* state. Switching the three gates on by
   default failed 25 tests with `FRL-MISSING`/`GLS-MISSING` against fixtures that were never
   meant to be complete. A gate describes this data set's release posture; a default describes
   the pipeline's behaviour, and they are not the same statement.
2. **`--config` file entry.** Nothing commits one, and `publish.yml` rebuilds the candidate and
   asserts the checksum matches byte for byte — a config file present on one run and absent on
   the other fails that assertion at the last gate before a release.

Both workflows therefore read the identical five variables, and both carry a preflight step that
refuses an unset one: an unset repository variable arrives as an **empty string**, not as absent,
so the library default never applies. `WGC_GATE_*` and `WGC_DETAIL_ACQUISITION_MODE` then fail
inside `load_config`, but `WGC_DETAIL_EDITION` passes validation as `""` and would stamp an empty
edition code on every entity.

## Per-class result

Elapsed time is the full live build (both upstreams acquired at the configured polite interval),
not the gate evaluation, which is not separately measurable and is not the interesting number.

| Class | Gate | Approved / denominator | Blocked entries at switch-on | Outcome |
|---|---|---|---|---|
| `abilities` | always on, no switch | 1934 / 1934 (100%) | 0 | on |
| `faction_rules` | `WGC_GATE_FACTION_RULES` | 28 / 28 (100%) | 0 | **on** |
| `detachment_rules` | `WGC_GATE_DETACHMENT_RULES` | 324 / 324 (100%) | 0 | **on** |
| `glossary` | `WGC_GATE_GLOSSARY` | 70 / 1491 (5%) | **1421** | **refused — stays off** |

Two live builds, ~6 minutes each including acquisition of 30 points-source faction pages and 26
current-edition datacard pages.

- **Rehearsal 1**, all four gates on: exit **30**, 1 421 blocking `GLS-MISSING`.
- **Rehearsal 2**, glossary off: exit **20**, verdict `advisory_only`, **zero** blocking findings.

## Why the glossary gate is refused, and what would change it

This is not an incomplete campaign. `T064` scoped the glossary at 60-100 entries and delivered 70,
all authored and reviewed. The denominator is the problem.

`contracts/authored-summary-gates.md` §4.1 defines the glossary denominator as *every distinct
`keywordKey` in use whose `keywordClass` is not `faction` or `chapter`*. The classification
vocabulary has exactly four values — `unit`, `faction`, `chapter`, and unclassified — and `unit`
conflates two things that are nothing alike:

- **game-term keywords** — `AIRCRAFT`, `INFANTRY`, `VEHICLE`, `CHARACTER`, `ARTILLERY`, `BEAST`.
  A glossary entry for each of these is exactly the work `T064` scoped, and 70 of them exist.
- **the datasheet's own name, repeated as a keyword** — `Abaddon the Despoiler`,
  `Wolf Guard Pack Leader with Jump Pack`, `Wraithlord`. Measured on the emitted bundle,
  **1 031 of the 1 441 distinct non-faction, non-chapter keyword strings match a datasheet name
  exactly** (the coverage report's denominator of 1 491 counts the same population under the
  normalised `keyword_key`, which collapses a slightly different set of variants). Nobody will
  ever write a glossary definition for these, and a gate that demands one is demanding work that
  should not be done.

So switching this gate on today does not mean "finish the campaign"; it means "author 1 421
definitions, roughly 1 031 of which are unit names". The gate is doing what §4.1 says and §4.1 is
describing a denominator that does not exist yet.

**What would change it**, in the order they should be considered:

1. Add a keyword class distinguishing a datasheet-name keyword from a game-term keyword, and
   amend §4.1 to exclude it alongside `faction` and `chapter`. This is a contract revision and a
   classification pass, and it is the fix that makes the gate mean what it was meant to mean.
2. Re-measure. Excluding exact datasheet-name matches leaves roughly 410 of the 1 441 — still
   well above the 70 authored, so a real campaign remains, but a finite and worthwhile one.
3. Then rehearse this gate again, against the pre-release channel, and record it below.

Until (1) lands, `WGC_GATE_GLOSSARY` stays `off`, unauthored keywords continue to ship with their
name only, publication is not blocked, and every gap stays named in `summary-coverage.md` — which
is precisely the behaviour the gates-off state was designed to give.

## Two data observations made during the rehearsal

Neither blocks anything; both are recorded because the rehearsal is where they surfaced.

- **Comma-joined keyword keys.** Several keys read as a joined list rather than as one keyword —
  `accursed cultists , undivided , shadow legion`, `ancient , deathwing`,
  `attack bike squad , ravenwing`. A comma-separated keyword list is reaching the key builder
  unsplit.
- **One mojibake key.** `glossary:�thar the destined` — an encoding fault on a non-ASCII unit
  name (`Ûthar the Destined`) somewhere between acquisition and key normalisation.

## Sweep of the digest-less subset (§7 item 4)

§7 item 4 requires a reviewer sweep of the entries whose digest is over the normalised keyword
stem — the ones that can never auto-flag for re-review — **before** the glossary gate is switched
on for the first time. That sweep has **not** been performed, and does not need to be until the
denominator question above is settled: the enumerated subset is currently dominated by the same
unit-name keywords, so sweeping it now would be sweeping a list that is about to change shape.
Recorded here as outstanding, so that switching this gate on later cannot skip it.
