<!-- AI-Assisted: Claude Code (model: claude-opus-5) - Wrote the synthetic-fixture rule as
     policy, with the two requirements behind it, the naming convention, and the explicit
     prohibition on redacting a capture into a fixture (task T036, research D10). -->
# Fixtures

**Every fixture in this directory is synthetic.** Hand-authored HTML and CSV that reproduce an
observed *structure* and *quirk class* using invented faction names, invented unit names, and
invented placeholder prose.

## The rule, and why it is a rule

The reflexive approach — capture a real points-source page and a real detail-source CSV and
commit them as golden files — is **prohibited here**. Not discouraged: prohibited. Two
requirements sit behind that, and each is independently sufficient:

- **FR-010** forbids committing raw acquired source material to any repository. A captured page
  *is* raw acquired source material. Saving it under `fixtures/` rather than `work/` does not
  change what it is.
- **FR-013** forbids publisher wording reaching curated data, intermediate artifacts, **version
  control**, logs, or reports. A captured CSV parks publisher prose in git history, where it is
  effectively permanent.

The consequence people get wrong: **you may not redact a capture into a fixture.** Taking a real
page and search-replacing the names still leaves the publisher's structure-plus-wording as the
thing you committed, and the redaction is one missed field away from being no redaction at all.
Author the fixture from the *description* of the structure instead — which is what the
observations in `research.md` §0 exist for.

Synthetic fixtures are therefore not a convenience. They are the only compliant option.

## Naming

```text
fixtures/<set>/mfm/<slug>.html          # one points-source faction page per file
fixtures/<set>/wahapedia/<Name>.csv     # one detail-source export file per file
```

`<slug>` is the invented faction slug; `<Name>` matches the export's own file naming so the
record-aware reader's per-file expected field count is exercised. Detail-source CSVs are
pipe-delimited and UTF-8 **with BOM**, because the real export is and the reader must strip it.

`--fixtures <dir>` points at one `<set>` directory. Both upstreams are sourced from it with no
network access at all, producing the same `SourceAcquisition` records the live path does — there
is no CI-only code path.

## The sets

| Set | Purpose |
|---|---|
| `sample/` | The general-purpose set: the `$RS` swap replay, cost tables and tiers, detachment cards, and one page with an **unfilled** placeholder that must fail the run |
| `minimal/` | The minimal snapshot `reference-db-schema.md` §7 requires, built by the same builder as a real release so it can never drift from the real emitter (FR-048) |
| `disagreements/` | One case per disagreement class in the spec's *Edge Cases* list |
| `detection/` | Baseline / mechanical-change / presentation-only-change / restructured page sets (research D4b) |

Each set is added by the task that needs it; a set is not a dumping ground for "a page that
looked interesting".

## Ability-summary digests (US5, task T133)

`curation/abilities/*.json` records inside `sample/` and `minimal/` carry a real
`mechanic_digest` — computed from that set's own `Datasheets_abilities.csv`/`Abilities.csv` text
with `pipeline.curate.summaries.compute_current_digests` — rather than a placeholder value, so a
future test exercising staleness end to end against a fixture set has a correct baseline to
diverge from. They are keyed under the fixture-only test key `fixture-mechanic-digest-key`,
which carries no significance beyond being a fixed, documented value every fixture-digest test
can reproduce; it is never `WGC_MECHANIC_DIGEST_KEY`'s real value in any environment. An
ordinary fixture build does not set that variable at all and so never compares digests (no
evidence of drift, `pipeline.curate.summaries.effective_status`) — the stored value only matters
to a test that deliberately sets the key to recompute and compare.
