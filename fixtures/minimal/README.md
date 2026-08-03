<!-- AI-Assisted: Claude Code (model: claude-opus-5) - Documented the minimal fixture set and the
     bundle it produces (task T076). Carries the Principle 16 header for the CSV and JSON files
     beside it, which admit no comment syntax of their own. -->
# `fixtures/minimal/`

The minimal snapshot `reference-db-schema.md` §7 requires, so the consuming app's CI can develop
against a real bundle without waiting for a real release.

**Everything here is invented.** Two factions that do not exist, nine units that do not exist,
and placeholder prose in every description field. Nothing was captured, and nothing was produced
by redacting a capture — see [`../README.md`](../README.md).

## The one property that matters

The bundle is produced by **the same builder that produces a published snapshot**:

```bash
rules-pipeline build --offline --fixtures fixtures/minimal --rules-version-id fixture-minimal
```

There is no fixture-only code path anywhere in that command. A hand-written fixture bundle would
drift from the emitter the first time the emitter changed, and the drift would show up as a green
app CI run against a bundle no producer would ever emit — which is worse than no fixture at all,
because it looks like coverage.

The set therefore ships its **own** `curation/` tree. It has to: the repository's `curation/`
maps the publisher's real faction slugs, and this set's invented slugs would every one of them be
the blocking `REC-FACTION-UNMAPPED`.

## What it produces, and why each piece is there

`build/rules-fixture-minimal.json` is the bundle; `build/data/` is the curated tree the same run
wrote, kept so a reviewer can see both representations of the same content.

| §7 requirement | How the set exercises it |
|---|---|
| Two factions, one a sub-faction | `f-ashen-vigil` and `f-ember-chapter`, the second carrying `parentFactionId` |
| Sub-faction exclusive + parent shared datasheet | `EMBER PALADIN` sits on the chapter; the other eight sit on the parent, so §3.5's ancestor query rule is exercised |
| Three detachments with different DP costs | 1DP, 2DP and 3DP |
| ~8 datasheets | nine |
| One Epic Hero | `LORD ASHEN`, flagged from its `EPIC HERO` **keyword** rather than from the role column |
| One Character with leader pairs | `ASHEN CAPTAIN`, leading two units |
| One Legends unit | `ASHEN RELIC WALKER` |
| One with multiple cost bands and cost-bearing wargear | `ASHEN SENTINEL`: 5- and 10-model bands plus a `+ 1 Sentinel Banner` row, which is how the points source publishes a wargear cost (C8/R3) |
| Two enhancements from different detachments | four, across three detachments |
| At least two point bands | Incursion and Strike Force, covering `500`..`5000` end to end |
| An ability with a non-empty authored summary on every datasheet | every one, resolved from `curation/abilities/f-ashen-vigil.json` |

Since contract v1.2.0, additionally:

| v1.2.0 requirement | How |
|---|---|
| An escalating price tier | `ASHEN WARDEN` is priced by the `YOUR 1ST TO 2ND` / `YOUR 3RD +` pair, so it carries a `copyIndexMin: 3` tier |
| Non-contiguous size bands | `ASHEN SENTINEL` is priced at 5 and 10 models, so a 6-model unit exercises §3.2's round-up rule |
| An `unverified` cost row | `ASHEN REVENANT` exists in the detail source and is not priced by the points authority, so it ships on the detail source's own price with the marker set — never withheld (FR-035) |
| A non-NULL `detailEditionCode` | every matched datasheet: the detail source is an edition behind the points source, which at launch is the *normal* case rather than the exception (research §0.1) |

The run exits `20` — advisory findings only — carrying `REC-UNMATCHED-DETAIL-ONLY` and
`PRC-UNVERIFIED` for `ASHEN REVENANT`. That is the correct verdict for this set rather than an
imperfection in it: a snapshot with nothing to report would not exercise the reporting.
