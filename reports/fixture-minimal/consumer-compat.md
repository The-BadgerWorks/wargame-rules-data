<!-- AI-Assisted: Claude Code (model: claude-opus-5) - Recorded the consumer-compatibility result
     for the minimal fixture bundle (task T077). -->
# Consumer compatibility — `fixture-minimal`

**Result: pass.** The bundle ingests into the schema `reference-db-schema.md` v1.2.0 declares,
every guarantee in its §1 holds with foreign keys enforced, and a multi-detachment army prices
to the expected total with zero contract violations.

| | |
|---|---|
| Bundle | `fixtures/minimal/build/rules-fixture-minimal.json` |
| Rules version id | `fixture-minimal` |
| Built by | `rules-pipeline build --offline --fixtures fixtures/minimal --rules-version-id fixture-minimal` |
| Build verdict | exit `20` — advisory findings only |
| Checked by | `tools/consumer_compat.py`, kept green in CI by `tests/publication/test_consumer_compat.py` |
| Contract versions | schema `1`, restriction vocabulary `1` |

## A substitution, recorded rather than glossed

The task's own wording is to install the bundle "through `001`'s own ingestion and contract
checks". **`001` has no code yet** — the repository holds its specifications and contracts and
nothing else — so its ingestor cannot be run against anything.

Rather than defer the check, it is performed here against the ingestion target itself:
`tools/consumer_compat.py` creates the SQLite schema exactly as §3 declares it, turns on
`PRAGMA foreign_keys`, loads every bundle array into its table mechanically, and then evaluates
the §1 guarantees and prices an army using §3.1's copy-index lookup and §3.2's round-up rule.

That is precisely the work `001`'s ingestor has to do, and the contract puts the obligation on
the producer to emit a bundle from which exactly that schema can be built with no additional
input. **When `001`'s ingestor exists, this check should be replaced by a run of it** — the
substitution is a stand-in for an absent consumer, not a preferred alternative to one.

## What was ingested

| Table | Rows |
|---|---|
| `edition` / `edition_rule` | 1 / 2 |
| `game_size_rule` | 2 |
| `faction` | 2 (one with a `parent_faction_id`) |
| `detachment` / `enhancement` | 3 / 4 |
| `datasheet` | 9 |
| `datasheet_cost` / `datasheet_cost_tier` | 10 / 11 |
| `datasheet_ability` | 11 |
| `datasheet_leader_pair` | 3 |
| `datasheet_wargear_option` | 1 |
| `datasheet_detachment_eligibility` | 0 — always empty, by contract |

## Guarantees checked at ingestion time

| Guarantee | Result |
|---|---|
| 2 — self-description: the contract and vocabulary versions are stamped | pass |
| 3 — completeness: every datasheet has a cost row; every enhancement resolves to a detachment; the bands are contiguous, non-overlapping and cover `500`..`5000` | pass |
| 4 — referential integrity: `PRAGMA foreign_key_check` over the built database | pass, no rows |
| 5 — IP boundary: no ability summary is empty | pass |
| 7 — tier projection: every `datasheet_cost` row has a matching first-copy tier row with identical points and label | pass |

## The pricing exercise

Deliberately the awkward army: two detachments, an escalating unit taken past its threshold, a
squad size that is not a listed band, a cost-bearing wargear option, and an enhancement in each
detachment. Every v1.2.0 addition changes the answer, so the total is asserted as a number.

```text
detachment ASHEN VANGUARD (1DP)
  ASHEN WARDEN x3 (copy 1): 70
  ASHEN WARDEN x3 (copy 2): 70
  ASHEN WARDEN x3 (copy 3): 80
  enhancement Cinderbrand: 20
detachment CINDER HOST (2DP)
  ASHEN SENTINEL x6 (copy 1): 175
    wargear Sentinel Banner: +15
  LORD ASHEN x1 (copy 1): 110
  enhancement Emberward: 25
total 565 points
```

Three lines of that are the whole point of the v1.2.0 additions:

- **`copy 3: 80`** — the third copy of `ASHEN WARDEN` crosses the requisition threshold the
  points source publishes as a separate `YOUR 3RD + UNIT COSTS` table. An app reading only
  `datasheet_cost` prices it at 70 and under-charges by 10, which is exactly the backward
  compatibility v1.2.0 describes: correct for the common case, wrong past the threshold.
- **`x6 ... 175`** — six models is not a listed band. Under §3.2 the unit pays the smallest
  listed count at or above six, which is the 10-model price of 175 rather than the 5-model
  price of 90.
- **`+15`** — the wargear cost comes from the points source, which is the only place it is
  published at all; the detail source's options export has no cost column (C8/R3).

Three DP against the Incursion band's budget of six, two detachments against a maximum of two,
and 565 points inside the band's `500`..`1999` range: the army is legal as well as priced.
