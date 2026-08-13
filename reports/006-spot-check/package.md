<!-- AI-Assisted: Claude Code (model: claude-opus-5) - Re-issued for the SECOND re-authoring of the
     wh40k-11e-2026-08-2 candidate (006 T049). Entry 13 becomes an answer, the header states the
     new bundle, and the outcome table names the single decision left. Entries 1-12 are unchanged
     because the arrays behind them are byte-identical to the build this replaces.
     AI-Assisted: Claude Code (model: claude-opus-5) - Re-assembled the Product Owner spot-check
     package for the RE-AUTHORED wh40k-11e-2026-08-2 candidate (006 task T047), after the T048
     triage invalidated the 2026-08-11 build. Every table below is this repository's OWN
     structured output, re-rendered from the new bundle, the way a reader meets it. No sentence,
     phrase, or fragment of the publisher's or the detail source's wording appears anywhere on
     this page: the "what to check" column states the question to ask of the live page, never the
     answer the live page gives. -->
# Spot-check package — candidate `wh40k-11e-2026-08-2`

**For**: the Product Owner, task T047 and the T048 sign-off.
**Candidate**: bundle sha256 `7ab360b180181b2536a97946a0d2334b75ed9afc642019a629edb3c19393db9d`,
11 253 406 bytes, built 2026-08-12 from a live acquisition.
**Branch**: `candidate/wh40k-11e-2026-08-2`.

> **This package replaces the one issued on 2026-08-11**, which was itself replaced on
> 2026-08-12. That first candidate published `defaultEquipmentState` absent on 647 datasheets
> whose cards the pipeline had read in full — its own entry 11 asked the question that found it,
> and `reports/006-t048-triage/default-equipment-omission.md` has the classification.
> **Entry 11 below is now the answer**, and entries 6 to 9 sit beside a default-equipment coverage
> figure that moved from 67 % to 97 %.
>
> **This issue answers entry 13** on your decision of 2026-08-11. Reading it first is worth the
> minute: the defect was five times larger than the entry said, most of it is in the release you
> already published, and it leaves you exactly one decision to make. Everything else in this
> candidate is byte-identical to the 2026-08-12 morning build — all 30 bundle arrays except
> `datasheetKeywords` — so entries 1 to 12 are unchanged and demonstrably so.

## How to use this page

Each entry below shows **what this candidate publishes** for one datasheet, laid out the way the
reference site and the app present it, followed by **what to compare on the live source**. Open
the datasheet on the detail source in a browser, read its wargear-options and unit-composition
blocks yourself, and answer the questions. Ten entries, chosen to cover every shape this feature
introduced plus the shapes it still cannot handle.

**The IP rule holds on this page too.** Nothing here reproduces the source's wording — the item
names are the mechanical nouns our own grammar extracted, and the questions are phrased so that
answering them requires reading the source, not this file. Please do not paste source sentences
into a review comment either; describe the disagreement instead.

**Where to look.** The detail source is the current-edition datacard tree the pipeline itself
acquires: `https://wahapedia.ru/wh40k11ed/factions/FACTION-SLUG/datasheets.html`, with the faction
slug given per entry. Prices, where an entry mentions one, come from the points source
(`https://mfm.warhammer-community.com/en/FACTION-SLUG`), which this feature did not touch. Please
honour the same courtesy the pipeline does: a browser, one page at a time, no scraping.

**How to record an outcome.** Add a row to the table at the bottom: entry number, date you looked,
and `agrees` / `disagrees` / `cannot tell`. A single `disagrees` on entries 1-9 is a release
blocker; entry 10 is a known gap and is here to be *seen*, not to pass.

---

## Part A — scoped and multi-item wargear options (US1)

*Unchanged from the 2026-08-11 package. The equipment fix did not touch a single option row:
`datasheetOptionGroups`, `datasheetOptionChoices`, `datasheetOptionChoiceItems` and
`datasheetWargearOptions` are byte-identical between the two candidates' bundles. Every table in
this Part was nonetheless re-rendered from the new bundle rather than copied.*

### 1. Assault Squad — a scoped stem, a two-item grant and a two-item replacement

**Faction slug** `space-marines` · **datasheet** `ds-assault-squad` · **group**
`og-assault-squad-4`

> **Wargear options**
> *Applies to: up to **2** models named **Assault Marines**, individually (per-model)*
>
> | This choice | Replaces | Grants |
> |---|---|---|
> | plasma pistol and 1 Astartes chainsword | bolt pistol · Astartes chainsword | plasma pistol · Astartes chainsword |
> | flamer and 1 close combat weapon | bolt pistol · Astartes chainsword | flamer · close combat weapon |
> | meltagun and 1 close combat weapon | bolt pistol · Astartes chainsword | meltagun · close combat weapon |
> | plasma gun and 1 close combat weapon | bolt pistol · Astartes chainsword | plasma gun · close combat weapon |
>
> No points change is published for any of these four.

**What to check on the live source**

1. Does the option line restrict itself to a named model group, and is that group's maximum **2**?
2. Is the restriction per-model (each eligible model chooses separately) rather than a single
   choice for the whole unit?
3. Are there exactly **four** alternatives, and does each one both take away **two** things and
   give **two** things? (This is the shape 004 could not represent at all.)
4. Does the source state a points change for any of the four? If it does, our omission is a
   defect — go to entry 5, which is the priced comparison.

*Known wart in this entry*: the choice's own label still reads `plasma pistol and 1 Astartes
chainsword`, i.e. the whole conflated string. That is the O1 Ruling working as decided — the
label is never rewritten, the decomposition appears in the Replaces/Grants columns beside it.

### 2. Deathwatch Terminator Squad — a scoped stem with a maximum of 3, and a parenthetical

**Faction slug** `deathwatch` · **datasheet** `ds-deathwatch-terminator-squad` · **group**
`og-deathwatch-terminator-squad-1`

> *Applies to: up to **3** models named **Deathwatch Terminators**, individually*
>
> | This choice | Replaces | Grants |
> |---|---|---|
> | assault cannon | storm bolter | assault cannon |
> | heavy flamer | storm bolter | heavy flamer |
> | plasma cannon | storm bolter | plasma cannon *(no weapon-line match)* |
> | cyclone missile launcher and 1 storm bolter (this model's storm bolter cannot be replaced) | storm bolter | cyclone missile launcher *(no match)* · storm bolter (this model's storm bolter cannot be replaced) *(no match)* |

**What to check on the live source**

1. Is the eligible-model maximum **3**?
2. On the fourth row, the source states a restriction inside the same clause. We have carried that
   restriction **into the item's name** rather than dropping it. Is the resulting item name
   faithful, or is it misleading enough that this row should have been refused instead?
3. `plasma cannon` and `cyclone missile launcher` did not link to a weapon line. Does the datacard
   list either of them under a name that differs from the option line's, or list it **twice**
   (e.g. two firing modes)? Two matches is a deliberate refusal, not a miss.

### 3. Devastator Squad — a scoped stem with a maximum of 4, six alternatives

**Faction slug** `black-templars` · **datasheet** `ds-devastator-squad` · **group**
`og-devastator-squad-1`

> *Applies to: up to **4** models named **Devastator Marines**, individually*
>
> Six alternatives, each replacing `boltgun`: **grav-cannon**, **heavy bolter**, **lascannon**,
> **missile launcher** *(no weapon-line match)*, **multi-melta**, **plasma cannon** *(no match)*.

**What to check**: the maximum is 4; there are six alternatives and no more; each replaces the
same one thing; and whether `missile launcher` / `plasma cannon` appear on the datacard under
different names or as two lines each.

### 4. Celestian Insidiants — a multi-item **replaced** side

**Faction slug** `adepta-sororitas` · **datasheet** `ds-celestian-insidiants` · **group**
`og-celestian-insidiants-3`

> *Applies to: up to **2** models named **Celestian Insidiants**, individually*
>
> | This choice | Replaces | Grants |
> |---|---|---|
> | blessed sword | condemnor bolt pistol · null mace | blessed sword |

**What to check**: does one model give up **both** of those to gain the one? This is the
asymmetric case — a bundle on the replaced side rather than the granted side — and it is where a
"fill the singular field from the first item" bug would show as *"replaces condemnor bolt pistol"*
with the null mace silently dropped. The published row carries **no** singular `replaces` field,
which is the guarantee-12 behaviour.

### 5. Bike Squad — the guarantee-12 mirror, and the price question

**Faction slug** `space-marines` · **datasheet** `ds-bike-squad` · **group** `og-bike-squad-3`

> *Applies to: up to **2** models named **Space Marine Bikers**, individually*
>
> Five single-item alternatives replacing `bolt pistol`: **flamer**, **grav-gun**, **meltagun**,
> **plasma gun** *(no match)*, **plasma pistol** *(no match)*. Each of the first three carries
> **both** a singular `grants`/`replaces` weapon-line link *and* a mirroring item row pointing at
> the same line — that redundancy is deliberate and is checked on every build.
>
> No points change is published for any of the five.

**What to check**: does the points source price any of these five swaps for this unit? If it
prices one and we publish nothing, that is a pricing gap worth a finding. If it prices none —
which is what we expect for 11th edition's model-count pricing — then a reader seeing no price is
correct.

---

## Part B — default equipment, shipping for the first time (US2)

**Release-wide, after the T048 fix:**

| `defaultEquipmentState` | Datasheets | Previous candidate |
|---|---:|---:|
| `extracted` | **2 002** | 1 386 |
| `partial` | 47 | 30 |
| `none` | 15 | 10 |
| field absent entirely | **20** | 658 |
| total | 2 084 | 2 084 |

Reported coverage `loadout.default_equipment` is **2 017 / 2 084 = 97 %** (`extracted` + `none`;
`partial` is deliberately excluded), against 1 396 / 67 % before the fix. The release publishes
**2 206 equipment groups** and **5 631 equipment items**, up from 1 528 and 3 890, and **632
datasheets carry an equipment group for the first time**. Every group and item the previous
candidate published is present here unchanged — the fix only ever adds.

This coverage key is **reported and not ratcheted** in this first extended release, so nothing
about the 67 % figure was ever going to become a floor. The next release inherits 97 %.

### 6. Aestred Thurga and Agathae Dolan — two model groups, both linked to composition

**Faction slug** `adepta-sororitas` · **datasheet** `ds-aestred-thurga-and-agathae-dolan` ·
state **extracted**

> **Default equipment**
>
> | Applies to | Composition link | Equipment |
> |---|---|---|
> | Aestred Thurga | line 1 | bolt pistol · Blade of Vigil |
> | Agathae Dolan | line 2 | bolt pistol · scribe’s staff |

**What to check**

1. Does the datacard state equipment **separately for the two named models**, rather than once for
   the whole unit? If it states it once, we have invented a distinction.
2. Do the two named model groups match the unit-composition block's own two rows, by name?
3. Are the item lists complete — nothing on the card's equipment sentence missing from our column?

### 7. Boyz — a model group we could **not** link to a composition row

**Faction slug** `orks` · **datasheet** `ds-boyz` · state **extracted**

> | Applies to | Composition link | Equipment |
> |---|---|---|
> | Boss Nob | line 1 | slugga · big choppa |
> | Boy | **unresolved** | slugga · choppa |

`EQP-GROUP-UNRESOLVED` is raised on the second group: the model name the equipment sentence uses
matched **zero** composition rows by name, so we publish the equipment without the link rather
than guessing at it by position.

**What to check**: on the composition block, is the second model group's name a **plural** of the
name the equipment sentence uses (or otherwise inflected)? If so, this is the known singular/plural
fold that the T032 checkpoint deliberately did not apply — **102 of the release's 143** unresolved
group links look like this one, across 119 datasheets. The equipment itself should still be
correct; only the link is missing.

### 8. Acastus Knight Asterius — unit-level equipment with unmatched plural names

**Faction slug** `imperial-knights` · **datasheet** `ds-acastus-knight-asterius` ·
state **extracted**

> | Applies to | Equipment |
> |---|---|
> | the whole unit | Asterius volkite culverins *(no weapon-line match)* · karacnos mortar battery · twin conversion beam cannons *(no match)* · titanic feet |

**What to check**: the datacard's weapon table almost certainly lists these in the **singular**
where the equipment sentence uses the plural. Confirm that the two unmatched items really are the
same weapons under a singular name, and that no item is missing from our list. The items still
publish; only the weapon-line link is absent, which is `EQP-ITEM-UNLINKED` — **897 of them across
703 datasheets** now that the unpriced half of the roster is extracted too, up from 579.

### 9. Aquila Kill Team — `partial`, the state that says "some of it did not parse"

**Faction slug** `imperial-agents` · **datasheet** `ds-aquila-kill-team` · state **partial**

> | Applies to | Composition link | Equipment |
> |---|---|---|
> | Kill Team Sergeant | **unresolved** | plasma pistol *(no match)* · power weapon |
> | Gravis Veteran | line 2 | infernus heavy bolter *(no match)* · bolt pistol · close combat weapon |
>
> Four further equipment sentences on this card (source lines 3, 4, 5, 6) **did not parse at all**
> and publish nothing — `EQP-UNPARSED` ×4. That is what `partial` means: what resolved is
> published and is true, and the rest is absent rather than guessed.

**What to check**: how many model groups does this card actually state equipment for? If it is
six and we publish two, the reader is seeing a third of this unit's loadout. Is that acceptable
as a first release of a field that previously did not exist at all, or should this card be
curator-overridden before publication?

Release-wide, `EQP-UNPARSED` is **114 rows across 47 datasheets** — 47 of 2 084, which is the
`partial` tail this state exists to make visible.

---

## Part C — what still fails, what is now answered, and one new question

### 10. Armoured Sentinels — an option line the extended grammar still refuses **(the required still-failing example)**

**Faction slug** `astra-militarum` · **datasheet** `ds-armoured-sentinels`

> **What we publish**: one option group, five single-item alternatives — **autocannon**,
> **heavy flamer**, **lascannon**, **missile launcher**, **plasma cannon**.
>
> **What we do not publish**: source option **lines 2 and 3**, both `OPT-UNPARSED`. Nothing about
> them reaches the bundle — no partial row, no guess.

**What to check**: read the second and third option lines on this datacard. Are they options a
player would care about (a second weapon slot, a hunter-killer missile, a searchlight)? Two
readings are possible and the Product Owner should pick one:

- they are minor and 256 such rows across the release (12.3%, down from 689 / 33.1%) is an
  acceptable residual for this release; or
- they are not minor, and this card wants a `curation/option-overrides.json` entry before publish.

The release-wide residual is **256 unparsed option rows across 162 datasheets** — the same 256
rows, on the same 162 datasheets, as the previous candidate. Of the classes deliberately refused,
the largest is the **availability-predicate** family — stems that condition the option on the
unit's size or on what it already carries (41 rows). No curated field can hold a predicate, so
resolving them would publish *"any unit may take this"* where the source says *"a unit of six or
more may"*. They stay unparsed on purpose.

### 11. **Answered**: the 658 datasheets with no `defaultEquipmentState` were a defect, and it is fixed

The previous package asked whether those 658 datacards state a default-equipment sentence at all,
and offered two readings. **The first reading was right.** The triage
(`reports/006-t048-triage/default-equipment-omission.md`) classified all 658 by provenance and
found 647 of them were a real extraction gap: `_detail_only_datasheet` — the assembly path for a
datasheet the *detail* source published and the *points* source did not price — never called the
equipment extractor at all. Their cards had been read end to end; only the equipment half was
dropped, silently, with no finding raised, because nothing was refused — nothing was attempted.

The two datasheets that package named as the ten most valuable minutes on the page now read:

| Datasheet | Previous candidate | This candidate |
|---|---|---|
| `ds-amallyn-shadowguide` (slug `aeldari`) | field absent | **`extracted`** — 1 unit-level group, 2 items |
| `ds-ancient-on-bike` (slug `space-marines`) | field absent | **`extracted`** — 1 unit-level group, 3 items |

**The 20 that still carry no state are all accounted for by the contract's own two reasons**, with
nothing left over:

| Why the field is absent | Datasheets |
|---|---:|
| composition did not resolve — `CMP-UNRESOLVED` is raised (FR-016) | 14 |
| the equipment source was never consulted — priced but no detail card was read | 6 |
| **any other reason** | **0** |
| total | 20 |

**None of the 20 publishes a composition row**, which is the check that exposed the defect last
time — 638 of the old 658 did. This entry no longer needs a reviewer's browser.

**What is still worth a spot-check**: not *whether* the equipment is there, but whether it is
*right* on a card that had never been through this path before. Entries 6 to 9 are the shapes;
`ds-amallyn-shadowguide` and `ds-ancient-on-bike` are two cards drawn from the newly-fixed
population, and either is a five-minute check.

### 12. **Withdrawn**: the "text-encoding defect" was an artefact of reading the bundle, not a defect in it

The previous package reported 2 481 rows in the candidate and 2 302 in the published bundle
"carrying a mis-decoded UTF-8 sequence where an apostrophe or accent belongs", 1 862 of them weapon
lines. **That measurement was wrong, and no such defect exists.** Re-measured directly:

- Both bundle files decode as **strict UTF-8** with no byte errors and **no BOM**.
- The literal mojibake byte sequence occurs **zero times** in either file.
- Every character involved is correctly encoded — the detachment rule the previous package cited as
  proof carries `U+2019`, a typographic apostrophe, in *both* bundles.
- The published bundle has **1 862 weapon rows containing a non-ASCII character** — exactly the
  "1 862 weapon lines" figure. Those rows are correct; they simply contain characters outside
  ASCII, the diameter sign among them.

The 1 862 is the tell. **Reading a UTF-8 file with Windows' default `cp1252` codec turns every one
of those characters into the `â€™`-style sequence the previous package described** — a typographic
apostrophe is the three bytes `E2 80 99`, which that codec renders as exactly those three glyphs.
The published bundle has 1 862 weapon rows with a non-ASCII character in them and the previous
package reported 1 862 mis-decoded weapon lines: the measurement was counting its own reader.
Anything that compares these bundles must open them as bytes or name
the encoding explicitly; the same trap sat in this re-authoring's first comparison run and was
caught by the disagreement it caused.

Nothing is owed here and no follow-up is needed. The item is kept rather than deleted so that a
reader of the previous package can see it retracted.

### 13. **Answered**: the keyword cell holding two keywords is split, and it was never only 65

The previous package asked whether 65 Aeldari datasheets carrying an unusable faction keyword
blocks publication. Your decision of 2026-08-11 was to fix it before publishing. Doing so found
that the entry understated the defect by a factor of five and mis-stated its age.

**It was 356 rows, not 65, and 291 of them are in the release you already published.** The Aeldari
rows stood out only because the 2026-08-11→12 source drift made their joined value new to the
keyword classifier; Dark Angels (`DEATHWING`, `RAVENWING`) and Chaos Daemons (`SHADOW LEGION`,
`UNDIVIDED`) have been shipping joined values since before this feature branch existed. 38 of the
293 published rows held **three** keywords, not two.

**It was also not a comma-joined text cell.** Each keyword is a run of `span.kwb` elements, and
the separator is whatever the page prints between two runs. That is `;` between ordinary keywords,
but a detachment-conditional keyword is appended after a `, ` carried in its own filter span, and
a conditional group may be introduced by a printed `:`. The parser split the flattened cell text
on `;` alone. It now splits on the boundary: a keyword is a run of `span.kwb`, and any
non-whitespace text between two runs ends it. No separator character is enumerated — a keyword's
own name may contain one, and the fixture now carries an invented keyword that does.

Measured over all 27 cached faction pages plus a fresh Aeldari fetch: 3 439 keyword groups, 219
split differently, and every disagreement a **pure split** — concatenate either result, drop
separators and spaces, and the strings are identical, so nothing is lost, merged or renamed. In
the bundle: expanding every published row on its separators gives a multiset the new array
contains in full with **0 rows left over**, and the only surplus is the 65 drift rows. No keyword
value in the candidate now contains a `,` or a `:` at all.

**What is left for you to decide**, and it is the only open item in this package: the
`keyword_classification` coverage check compares a raw *count* of classified keywords against the
previous release. 144 of the values it counted last time were composites this candidate no longer
invents, so the count falls 1 449 → 1 371 = 94.6%, under the 95% floor, and `COV-COLLAPSE` is
raised. The collapse is not real — the 66 values gained are the real keywords those composites
hid, all 66 are classified, distinct **unclassified** keywords is 18 in both releases, and the
classified proportion is 98.8% then against 98.7% now. `curation/resolutions.json` carries a
dated, digest-bound resolution saying exactly that, which is why the build is `advisory_only` and
exits 20. **It is drafted, not signed off**: `resolved_by` says so. Confirm the reasoning or delete
the entry — deleting it returns the build to exit 42, blocked, and no publication is possible.

Recording it also exposed a defect in the pipeline, now fixed: `_verdict` read the collapse flag
computed *before* resolutions were applied, so a dated resolution suppressed the finding in the
report and satisfied the publish gate while exit 42 alone still refused. See commit `6590f93`.

---

## Outcome table — please fill in

| Entry | Datasheet | Reviewed on | Outcome |
|---|---|---|---|
| 1 | Assault Squad | | |
| 2 | Deathwatch Terminator Squad | | |
| 3 | Devastator Squad | | |
| 4 | Celestian Insidiants | | |
| 5 | Bike Squad | | |
| 6 | Aestred Thurga and Agathae Dolan | | |
| 7 | Boyz | | |
| 8 | Acastus Knight Asterius | | |
| 9 | Aquila Kill Team | | |
| 10 | Armoured Sentinels *(known failure)* | | |
| 11 | Amallyn Shadowguide / Ancient on Bike *(the fixed path)* | | |
| 13 | The keyword split — **the one decision left**: confirm or delete the resolution | | |

## Evidence this package sits beside

- `reports/006-t048-triage/default-equipment-omission.md` — why the previous candidate was
  withdrawn: the classification of all 658, the cause, the fix and its three regression tests.
- `reports/wh40k-11e-2026-08-2/option-regression.md` — the FR-009 proof: 4 338 of 4 338 previously
  published option choices byte-identical. Carried forward, with the byte-identity evidence that
  makes carrying it forward legitimate stated at the top of the file.
- `reports/wh40k-11e-2026-08-2/consumer-compat.md` — both released consumers, unmodified, against
  this bundle, including the six site pages whose display changed and the keyword question above.
- `reports/wh40k-11e-2026-08-2/report.md` — the full validation report: exit 20, `advisory_only`,
  zero unresolved blocking findings, 9 016 advisory, 2 suppressed.
- `curation/resolutions.json` — the last object in that file is entry 13's drafted resolution.
  It is the only thing standing between this candidate and a blocked build.
