<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Recorded three items surfaced while
     landing the Polish phase (T146-T162): one operational setup step the settings-drift checker
     (T148) depends on but cannot perform itself, one pre-existing test-hygiene defect the T161
     stage-boundary audit exposed, and the stage-boundary exception T161 documented but did not
     resolve. None of these block acceptance; all three are named here so they are not lost. -->
<!-- AI-Assisted: Claude Code (model: claude-opus-5) - Added item 4 (004 T076 follow-up): the
     datasheet-coverage shortfall that survives the faction-map slug correction, and the
     chapter-disambiguation signal html mode does not carry. -->
<!-- AI-Assisted: Claude Code (model: claude-opus-5) - Closed item 4: the chapter-keyword rung
     landed, and the coverage shortfall it attributed to an edition-boundary artefact turned out
     to be a cost-table parsing defect. The original text is kept beneath the resolution. -->
<!-- AI-Assisted: Claude Code (model: claude-opus-5) - Added item 5 (issue #4): the finding code
     the weapon-ability-keyword fix needed, implemented ahead of the additive row a frozen
     contract may not be given as a side effect of a bug fix. -->
<!-- AI-Assisted: Claude Code (model: claude-opus-5) - Added item 6 (issue #5): the per-detachment
     page hypothesis, tested live and refused, with the acquisition decision it settles and the
     detachName oracle the test surfaced. -->
<!-- AI-Assisted: Claude Code (model: claude-opus-5) - Added item 10 (006 T011, later renumbered
     to item 11 — see the housekeeping note below): the ninth CLI command an evidence tool needs,
     implemented ahead of the additive contract row a frozen cross-repository contract may not be
     given as a side effect of a feature branch. -->
<!-- AI-Assisted: Claude Code (model: claude-opus-5) - Added item 11 (later renumbered to item
     12): the two `build` options that finally make `snapshotMeta.publishedAt` a reachable input,
     landed ahead of the §1 amendment they are owed, after a rebuild that crossed 00:00Z refused an
     approved candidate with exit 51. -->
<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - 006 T050 housekeeping: this file had two
     items both numbered "10" (the option-regression command and the published-at build options,
     added independently and never cross-checked against each other's heading). Renumbered the
     second to 11 and the pre-existing item 11 to 12, and updated every in-repo cross-reference
     (`pipeline/cli.py`, `tests/contract/test_cli_surface.py`) to match. Added item 13, a release-
     process gap the wh40k-11e-2026-08-2 publication surfaced: PR #13's own rebuild-proof evidence
     file never reached `main`. -->
<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - 006 T050 housekeeping: added item 14, the
     genuine test-coverage gap this same review found — nothing exercises the equipment-overrides
     escape hatch T031 built (`curation/equipment-overrides.json`'s loading and dangling-reference
     checks). -->
<!-- AI-Assisted: Claude Code (model: claude-opus-5) - Added items 8 and 9 (004 T081, T084): the
     three defects the first real-bundle consumer-compat run exposed, two of them pre-existing in
     the published release, and the glossary denominator that makes its gate un-switchable. -->
<!-- AI-Assisted: Claude Code (model: claude-opus-5) - Added item 7 (004 T089): the self-approval
     guard's missing authored_by field, recorded against the five real records the 004 release
     preparation approved out of band, with the mitigation actually relied on and the reason it
     is not a bypass. -->
<!-- AI-Assisted: Claude Code (model: claude-opus-5) - Partly closed item 8: the tool defects and
     every byte-identical duplicate are fixed, and two of the item's own conclusions about the
     cost duplicates turned out to be wrong. The original text is kept beneath the resolution. -->
<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Added items 15-18, surfaced during
     007-loadout-display-fidelity's Polish phase and release: the footnote-constraint vocabulary's
     zero-real-row result despite real candidates existing, the rendering-equivalence baseline
     needing investigation before any ratchet decision, the org's Actions-PR-creation gap
     recurring for a second release, and the change-class guard's implication for how a future
     multi-class feature must plan its release. None resolved here; all four are forward-looking. -->
<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - 008 T026 (Foundational phase): marked
     item 18 discharged -- this feature planned and has so far executed its split-PR release path
     from the first commit, exactly the discipline item 18 asked a future multi-class feature to
     adopt. Referenced items 15, 16, and 17 as out of scope from this feature's own plan.md. Added
     item 19, this feature's own entry: the ahead-of-contract finding codes T018/T019 added
     (validation-report.md §3 owed an additive row, item 5's precedent) and the O2 restatement
     T014 decided but has not yet sized (T074 owes the exact figure). -->
# Follow-ups

Open items surfaced during implementation that are deliberately **not** fixed as part of the work
that found them — either because they need a human with credentials this session does not have,
or because fixing them would have widened a task past what it was scoped to touch. Each is honest
about why it was left rather than folded in.

## 1. `WGC_SETTINGS_AUDIT_TOKEN` secret needs to be created (T148)

`tools/check_repo_settings.py` and `.github/workflows/settings-drift.yml` (task T148) are
implemented and tested, but the workflow cannot run successfully against the live repository
until a maintainer creates the `WGC_SETTINGS_AUDIT_TOKEN` repository secret it reads. This is
deliberate, not an oversight: reading branch protection and environment settings back through the
GitHub API requires a token with real repository administration-read access, and the standard
Actions `GITHUB_TOKEN` has no such scope available to it (there is no `administration` permission
in the workflow `permissions:` block — that is an app-installation-only permission). Wiring an
admin-capable credential into the existing `pull_request`-triggered `ci.yml` job was rejected for
the same reason `docs/repo-settings.md` already reasons about credentials generally: keep anything
capable of reading or writing repository configuration on the narrowest trigger that still does
the job. `settings-drift.yml` is `workflow_dispatch` plus a weekly `schedule` only.

**Action needed**: a maintainer (`adhoxx`) creates a fine-grained personal access token scoped to
`The-BadgerWorks/wargame-rules-data` only, with **Administration: Read-only** repository
permission and nothing else, and stores it as the `WGC_SETTINGS_AUDIT_TOKEN` repository secret.
Until then, `settings-drift.yml` will fail with a clear "token not configured" diagnostic rather
than silently doing nothing — see `tools/check_repo_settings.py`'s own handling of a missing
token. This is the one narrow, documented exception to "no long-lived PAT anywhere in this
design" (`contracts/pipeline-run-interface.md` §5): it reads settings, never publishes, and holds
no write scope of any kind.

## 2. Test-hygiene defect: `test_cli_surface.py` writes to the real `state/run-ledger.jsonl`

`tests/contract/test_cli_surface.py::test_every_command_returns_a_code_from_the_stable_set`
parametrizes over every contract command including `verify`, calling
`main(["verify", "--offline"])`. Its comment (written at task T106, before `verify` existed) says
`verify` "remain[s] pending stage modules" and therefore falls through to the `_pending` handler
without touching anything. That was true then; it is no longer true — `rules-pipeline verify` was
implemented at T140-T143, and the test was never updated to isolate it from the repository's real
working directory. Every `pytest` run now appends one real ledger entry to the tracked
`state/run-ledger.jsonl`, because `verify`'s `--offline` flag only suppresses network access (it
never made any) and the test does not `monkeypatch` the CLI's working directory or use the
"temporary-repository factory for publication tests" `tests/conftest.py` already provides for
exactly this purpose.

**Effect observed**: confirmed directly while merging this phase's branches — running the full
suite twice added two real entries to `state/run-ledger.jsonl`, which then showed up as an
uncommitted, undesired diff. Reverted with `git checkout -- state/run-ledger.jsonl` before
committing; not committed as a "real" ledger entry.

**Fix needed** (not applied here, to keep this Polish-phase landing to what it was scoped to):
run the `verify` case of that parametrized test inside a temporary repository root (the same
fixture `tests/publication/` tests already use), or `monkeypatch` `pipeline.config.repo_root` for
the duration of that one parametrize case, so the assertion "every command returns a code from the
stable set" stops relying on mutating the real repository as a side effect of running `pytest`.

## 3. `pipeline/curate/assemble.py`'s documented source-model import exception (T161)

`tests/ip/test_stage_boundary.py` (T161) asserts no stage downstream of `normalize` imports
`pipeline.models.source` — except `pipeline/curate/assemble.py`, which imports
`SourceAcquisition`, `MfmUnitCostBlock`, and `MfmDetachmentCard` (none prose-bearing, but all
three are source-side by the module's own definition). The test pins this to an exact,
per-symbol allow-list (`KNOWN_EXCEPTIONS`) precisely so the exception cannot silently widen — but
it does not close the exception.

**Fix needed**: introduce a small `normalize`-owned projection (e.g. a
`NormalizedAssemblyContext` or similar, built once in `pipeline/normalize/` from the same
`SourceAcquisition`/`MfmUnitCostBlock`/`MfmDetachmentCard` records) carrying only the primitive
values `assemble.py` actually reads from them, so `curate` can consume that projection instead of
the source-side types themselves. That removes the exception entirely rather than merely fencing
it. Left as follow-up because it touches the `normalize` → `curate` boundary contract internally
and deserved its own review rather than riding along inside T161's cleanup pass.

## 4. ~~`html` mode carries no publication id, so five chapters cannot be disambiguated~~ — **closed 2026-08-06**

**Resolved.** The rung this item described as "a design question rather than a defect" was
implemented as sketched, driven by `curation/keyword-classes.json`'s curator-authored chapter
records rather than by any inference from a keyword's spelling — see `pipeline/reconcile/match.py`'s
module docstring (rung 3) and `tests/reconcile/test_chapter_keyword_preference.py`. All 53
`REC-AMBIGUOUS-MATCH` findings cleared. The `unit-map.json` alternative this item offered as the
cheaper option turned out not to be available: `unit-map.json` is keyed by
`mfm_display_name` alone, with no faction column, so one entry would resolve `Impulsor` identically
in all six Space Marine factions — which is the one thing the collision needs it not to do.

The item was also wrong about the size of the shortfall, and the correction is the more useful
half of it. Clearing the 53 raised datasheet coverage to 92.4%, not the ~92.5% estimated — but the
remaining gap was **not** the "not recoverable, two different editions' catalogues" this item
concluded it was. It was a second, unrelated defect in the same live run: the html cost-table
reader treated a repeated cost header as the start of the next pricing tier, so 160 datasheets
whose cost table was sitting on the card were read as priced by nobody. Coverage with both fixed
is **2 083 / 2 099 = 99.2%**, and no dated `resolutions.json` entry for a threshold shortfall is
needed after all. The lesson worth keeping: a coverage figure short of its floor was blamed on the
baseline being a different edition, and the baseline was almost right.

The original item follows, unedited.

### Original text

**`html` mode carries no publication id, so five chapters cannot be disambiguated (`004` T076)**

The live `html`-mode build of 2026-08-05 exits `42` on datasheet coverage: **1 888 datasheets
against the published `mfm-2026-08` baseline's 2 099 — 89.95%, under the 90% floor**, on both
`datasheets` and `priced_datasheets`. Correcting the three faction-map detail slugs (see
`curation/README.md`) recovered 19 datasheets and moved the figure from 89.04% to 89.95%: real,
and 0.05 percentage points short of clearing the gate.

The largest identifiable recoverable component is **53 blocking `REC-AMBIGUOUS-MATCH` findings,
every one of them in a Space Marine faction** (9 each for Black Templars, Blood Angels, Dark
Angels, Space Wolves and the parent, 8 for Deathwatch). Each is a points-priced unit whose
normalised name matches two datasheets on the shared `space-marines` page, neither Legends. That
is the same collision `curation/README.md`'s provenance section already documents — and the field
that resolves it, `detail_source_publication_id`, **cannot resolve it under `html` mode**:
`pipeline/parse/wahapedia_html_dom.py` emits a `Source.csv` of exactly two rows and a `source_id`
of `current` or `legends`, because a datacard page states Legends as a class token on the card
and never states which publication a datasheet came from. So the five entries naming
`000000139`/`000000162` are inert, stage 2 has nothing to prefer with, and it correctly refuses
rather than guessing. Recovering those 53 would put datasheet coverage at roughly 92.5%.

**Not fixed here**, because it is a design question rather than a defect: the signal html mode
*does* carry is the card's own faction keywords, and preferring a chapter's datasheet by keyword
is a new rung on the D5 ladder — it needs its own contract wording, its own "never auto-apply a
fuzzy match" argument, and its own tests. The alternative, a `unit-map.json` entry per collision,
is stage 1 and already outranks everything below it: 53 curator-confirmed pairings would clear
the whole set today without any code change.

The remainder of the shortfall is not recoverable and should not be treated as a fault: 11th
edition publishes fewer datasheets than 10th, so a coverage ratio measured against a
previous-edition baseline is comparing two different editions' catalogues. That is the case for a
dated `curation/resolutions.json` entry when this candidate is raised, not for a threshold change.

## 5. `COV-WEAPON-ABILITIES-EMPTY` is implemented ahead of its contract row (issue #4)

`pipeline/report/catalogue.py` now carries `COV-WEAPON-ABILITIES-EMPTY` (class `coverage`,
**advisory**), raised when a snapshot publishes weapon lines and not one of them states an
ability keyword. It exists because that is exactly the state every release shipped in until
issue #4: `CuratedWeaponLine.ability_keywords` was empty on all 9,305 published weapon lines,
every value present was correct, and no finding and no figure said anything.

The code is **not yet in `validation-report.md` §3.4**, which is the catalogue's source of truth.
That contract is Frozen (`002-rules-data-pipeline` accepted 2026-08-04) and its own changelog
states that any further change to it is a cross-feature versioning exercise (Principle 10) — so a
bug fix may not edit it as a side effect, and did not. `tests/unit/test_finding_catalogue.py`
keeps the code in a separate `PENDING_CONTRACT_SEVERITIES` block for the same reason: the
transcribed tables above it must stay a faithful copy of what the contracts actually say.

**Action needed**: an additive row in `WargameCompanion:specs/002-rules-data-pipeline/contracts/
validation-report.md` §3.4 —

| `COV-WEAPON-ABILITIES-EMPTY` | advisory | The snapshot publishes weapon lines and none states an ability keyword | issue #4 |

— with a changelog entry, made by whoever owns the 002 contracts. Adding a code is additive and
backward-compatible: no existing code's meaning or severity moves, `report_contract_version`
stays `1.0.0`, and a consumer that does not know the code treats it as any other advisory. Once
the row exists, move the entry out of `PENDING_CONTRACT_SEVERITIES` into the main transcription.

The `weapon_ability_keywords` scale figure added alongside it needs no contract change:
`validation-report.md` §1.3 requires every scale category to state a count and a proportion and
does not enumerate the categories.

## 6. Per-detachment pages do not exist: acquisition should not sweep for them (issue #5)

While diagnosing issue #5 the campaign notes carried a second, untested hypothesis: that the
publisher serves a separate page per detachment — `/factions/<slug>/<detachment-slug>` — carrying
rule text the faction datacard page omits, and that acquisition should therefore sweep those
pages too.

**Tested on 2026-08-06 and refused.** Eight polite requests through the pipeline's own
`PoliteClient` (robots, deny-list and the 2 000 ms interval unchanged):

* the publisher's `SiteMap.xml` enumerates **1 442 URLs, and not one is deeper than
  `factions/<slug>/<Datasheet-Anchor>`** — 39 at depth three (24 faction index pages, 15
  rules pages) and 1 403 datasheet anchors, so a per-detachment page is not published anywhere
  the publisher lists;
* six direct probes for the hypothesised shapes — `factions/t-au-empire/Starfire-Cadre`,
  its lower-case form, `factions/space-marines/Anvil-Siege-Force`,
  `factions/space-marines/detachments.html`, `factions/space-marines/detachments`, and
  `factions/thousand-sons/Sekhetar-Cohort` — **all responded 404**; and
* the faction datacard pages carry no link of that shape either: every in-tree `href` on a page
  is a faction index or a datasheet anchor.

**Decision: acquisition stays as it is.** The sweep remains one aggregate page per faction, and
the FR-004 politeness budget stays the order of magnitude the design argued for. There is nothing
to recover from such pages, because every detachment rule's text is already on the faction page —
in a `tooltip_content` template whose own `div.detachName` names the detachment that owns it.

That `detachName` is worth recording as an available signal, though it is deliberately **not**
used by the parser today: the class-token read in `_detachment_rules` is what attaches a rule to
its detachment, and it is correct now that the emitted id is faction-qualified. `detachName` was
used as the *independent* oracle that confirmed the issue #5 fix — of the 285 entries the first
authoring campaign worked from, the publisher's own tooltips confirm 197 and contradict 88, and
of the 324 the corrected build produces they confirm all 324 and contradict none. If the class
tokens ever move upstream, `detachName` is the second reading that would catch it.

## 7. The self-approval guard cannot see who *authored* a summary (004 T089, made concrete)

`contracts/authored-summary-gates.md` §6 and `tools/check_summary_approvals.py`'s own docstring
already record this gap in the abstract: there is no `authored_by` field on any summary record, so
the guard proxies "author" with the pull-request actor. The rule it actually enforces is therefore
*the person opening the pull request may not be the person named as reviewer on a newly-approved
record*, which is narrower than FR-025's wording implies. Adding `authored_by` across all four
classes would touch the 2 031 existing ability records — a change-class collision under
`tools/check_change_classes.py` — which is why it was deferred rather than fixed.

**On 2026-08-06 the release preparation hit it for real, and the outcome is worth recording so the
next person does not have to re-derive it.** Five records were approved by the Product Owner
(`adhoxx`) out of band: `glossary:beast`, `glossary:grenades`, `faction:templar-vows`,
`faction:f-black-templars:templar-vows` and `faction:f-genestealer-cults:cult-ambush`. Run against
those commits with `--actor adhoxx`, the guard fails all five. Run with the authoring identity, it
passes.

**The guard is right about what it measures and wrong about what it concludes**, and the
difference is exactly the missing field. The three replacement texts were authored by the AI
curator (see the `AI-Assisted-By` trailer on the authoring commit); `adhoxx` reviewed them and did
not write them. Reviewer and author are genuinely different parties. The guard reports a
self-approval only because `--actor` is the sole author signal it has, and on a hypothetical pull
request carrying these records `adhoxx` would be the actor in the *reviewer's* role, not the
author's.

**What was relied on instead, and why it is legitimate rather than a bypass**:

1. The guard is scoped to `pull_request` by design — `ci.yml`'s `change-class-guard` job carries
   `if: github.event_name == 'pull_request'`. These records landed on `main` by direct push, which
   is how every prior approval commit in this repository landed (`c4ddf25`, `820a915`, `111c796`).
2. The candidate pull request stages `data` and `reports` only (`candidate.yml`'s
   `git add data reports`). No path it carries is claimed by `SOURCES`, so the guard evaluates
   nothing on it — not because the check was skipped, but because there is no authored-summary
   change in that diff to evaluate.
3. The authoring and the approval were split into separate commits (`a0fc667` then `1b8b440`) so
   the history distinguishes the two acts. This is a record, **not** a fix: the guard compares
   `base...head`, so splitting commits inside one range does not and should not change its verdict.

**Nothing in the checker was weakened to get past it, and nothing should be.** The correct fix is
still `authored_by`, and until it exists an out-of-band approval by a maintainer who is also the
likely pull-request actor has to be reasoned about by a human rather than certified by CI. If a
future release ever needs these records to travel *inside* a pull request, that pull request must
be opened by someone other than the person named in `reviewed_by` — or `authored_by` must land
first.

## 8. ~~`tools/consumer_compat.py` cannot ingest any real bundle (004 T081)~~ — **closed 2026-08-06**

**Closed in two passes.** The first resolved the tool side and every byte-identical duplicate;
the second resolved the collisions whose rows *disagree*, which needed two Product Owner
decisions and could not be made as a bug fix.

*Second pass, 2026-08-06 — what the disagreeing collisions actually were.*

* **Nineteen cost and sixteen tier collisions were Imperial Agents dual pricing.** The points
  source splits a faction page's units into sections, and the Imperial Agents page carries all
  twenty-nine of its units **twice**: once in an unheaded section, once under
  `EVERY MODEL HAS THE IMPERIUM KEYWORD`. `cost_table_label` is `YOUR UNIT COSTS` in both, so it
  was never the signal that told them apart — the *section heading* is, and `mfm_dom` was
  discarding it. All thirty faction pages were probed to establish that this is the only page
  whose sections re-price a unit; the six Space Marines chapter sections use the same structure
  to partition units, which is why the heading's **form** decides and not its presence.
* **Four cost and six tier collisions were composite band labels**, on exactly three datasheets
  in the whole tree. Summing the segments a composite label states — the parse fix
  `REC-BAND-MISMATCH` was already asking for — resolves `ds-crusader-squad` and `ds-gretchin`.
  It does **not** resolve `ds-wolf-guard-headtakers`, and that is worth recording, because the
  original diagnosis assumed it would: `3 Wolf Guard Headtakers, 3 Hunting Wolves` (115) and
  `6 Wolf Guard Headtakers` (170) are both six-model units. That unit is priced on two axes and
  no single model count can key it.
* **Four ability collisions** were `core:super-heavy-walker` against
  `datasheet:super-heavy-walker` on the same datasheet.

*What landed — Product Owner decisions of 2026-08-06.*

* **(A) A price carries the condition it is published under.** `pricing_context` is absent for
  the price a unit costs unconditionally — what every cost row has always meant — and is derived
  only from what the source itself says: a section heading of the conditional form
  (`every-model-has-imperium`), or the model types some bands of a datasheet name and others do
  not (`with-hunting-wolves`), the latter only where the bands actually collide. Colliding bands
  with nothing to tell them apart are still left alone and still block.
* **(B) The narrower authored record wins the consumer key it shares.** Scope precedence — core,
  faction, datasheet, most specific first — resolves the four `Super-heavy Walker` collisions.
  It is per datasheet and takes nothing away: the core record still serves every other datasheet
  bound to it. Two records at the *same* scope still block, because that is a question about the
  data and not one the emitter may answer.
* **The bundle keeps conditional prices out of `datasheetCosts` and `datasheetCostTiers`
  entirely.** A `pricingContext` column on those would have carried extra rows under a primary
  key old consumers already declare, and an extra row under a declared key is a constraint error
  that refuses the whole snapshot — not a column a consumer can ignore. `datasheetCostContexts`
  is a new array whose key includes the condition, which is why the unmodified v1.2.0
  `tools/consumer_compat.py` still reads the bundle end to end. That tool staying at v1.2.0 *is*
  the additive-compatibility proof, so any shape that required changing it would have destroyed
  its own evidence.
* **Contracts.** `reference-db-schema.md` **v1.4.0** (`datasheet_cost_context`, guarantee 13,
  §3.9), `bundle-schema-delta.md` 1.1.0, `curated-snapshot-format.md` 1.2.0, and
  `validation-report.md` **1.1.0**, which catalogues `CON-DUPLICATE-KEY` — action 1 below, now
  discharged. `COV-WEAPON-ABILITIES-EMPTY` is still owed its row under item 5.

*First pass, 2026-08-06.* The original text is kept below because its counts are the
before-picture, but **two of its conclusions were wrong and the corrections matter more than the
fix**.

*What was wrong.* The item calls the `datasheet_cost` / `datasheet_cost_tier` duplicates
"byte-identical rows across 32 datasheets that appear under more than one faction, so a dedupe at
emission is mechanical". Neither half holds. Only **17 of the 36** cost keys carry identical rows;
the other **19 disagree about the price** — `ds-inquisitor` at 55 *and* 65, `ds-eversor-assassin`
at 100 *and* 110, `ds-inquisitor-draxus` at 75 *and* 110. And no datasheet appears under more than
one faction: every id resolves to exactly one file in the tree. **32 of the 36 are
`f-imperial-agents`**, where the points source prints two cost tables for one unit on one page and
`assemble._costs` concatenates the rows of every block matched to a display name. A "mechanical
dedupe" would have silently published whichever price sorted first.

The other four are a second, unrelated defect: `normalize.numerics.model_count` reads only the
*leading* integer of a band label, so `1 Sword Brother, 4 Neophytes, 5 Initiates` and
`1 Sword Brother, 8 Neophytes, 11 Initiates` both become `model_count = 1` — two real size bands
(10 and 20 models) collapsed onto one key at two prices. The pipeline already sees this and says
so: `REC-BAND-MISMATCH`, advisory, `composition_min 10 / composition_max 20 / model_count 1`.
Affects `ds-crusader-squad`, `ds-gretchin` and `ds-wolf-guard-headtakers` (twice).

*What landed.*

* **The tool** now defers foreign keys to `COMMIT` (a chapter sorting before its parent is the
  normal case, not a malformed bundle), **detects duplicate primary keys instead of dying on the
  first one**, and separates identical duplicates from disagreeing ones in what it reports. Its
  schema deliberately stays at v1.2.0 — `test_consumer_compat_enriched.py` asserts it names none
  of `004`'s arrays, and that assertion *is* the additive-compatibility proof. It also skips the
  fixture-only exercise army rather than reporting `pricing failed` on every real bundle.
* **The emitter** (`bundle_emit._rows`) now collapses byte-identical rows, with absence compared
  as a value. That is lossless by construction and clears **every** identical duplicate: the
  published tree's 3 869 excess `datasheet_keyword` rows, and 17 cost plus 19 tier rows in both
  trees.
* **Validation** raises the new blocking `CON-DUPLICATE-KEY` for what is left, which by
  construction is only collisions whose rows disagree. Rebuilt today: **published tree 84**
  (43 weapon, 19 cost, 22 tier), **candidate tree 45** (4 ability, 19 cost, 22 tier).
* **The consumer contract** gained guarantee 12 and §3.8 at **v1.3.2** — a PATCH, no schema
  change. The load-bearing sentence is that SQLite permits NULL in a `PRIMARY KEY` column and
  treats NULLs in a unique index as *distinct*, so the largest duplicate class in the published
  release — `datasheet_keyword`, whose key ends in the usually-absent `model_scope` — ingests
  without an error and reaches a player as a keyword listed twice. Only the producer can catch
  that class, which is why the guarantee is the producer's.

**Action needed after the first pass** (all three discharged by the second pass above):

1. ~~**An additive row in `validation-report.md` §3.4** for `CON-DUPLICATE-KEY`.~~ Done at
   `validation-report.md` 1.1.0; the code has left `PENDING_CONTRACT_SEVERITIES`.
2. ~~**The Imperial Agents double-pricing (32 groups).**~~ Decided (A) and mechanised from the
   section heading rather than from `cost_table_label`, which is identical in both tables. The points source prices these units twice
   on one page and the consumer schema has no way to hold both. Deciding *which* price a
   datasheet filed under `f-imperial-agents` should carry is a Product Owner question; mechanising
   it needs `MfmUnitCostBlock.cost_table_label`, which is available at build time and not in the
   tree.
3. ~~**`model_count` on composite band labels.**~~ Done, and it moved published prices and size
   bands exactly as predicted — but it was **not sufficient on its own**, see
   `ds-wolf-guard-headtakers` above. Original note: summing the counts a label states
   (`1 + 4 + 5 = 10`) is almost certainly right and is what `REC-BAND-MISMATCH` is already
   asking for, but it moves published prices and size bands, so it belongs to a build rather than
   to a bug fix landing beside it.

The four `datasheet_ability` collisions were, at the end of the first pass, unchanged in
substance and blocking rather than silent — resolved by decision (B) above: `ds-greater-brass-scorpion`, `ds-greater-brass-scorpion-2`, `ds-kytan-ravager` and
`ds-kytan-ravager-2` each carry `core:super-heavy-walker` **and** `datasheet:super-heavy-walker`,
two records with the same `name`, different `mechanic_digest`s and different approved summaries.
Contract §3.8 now says explicitly that `ability_type` is not part of the key and that exactly one
row may reach the bundle, so this is a curation decision — drop one binding, or merge the two
records — and no longer an open question about what the key means.

### Original text

**`tools/consumer_compat.py` cannot ingest any real bundle (004 T081)**

The first run of this tool against a real bundle rather than a fixture — 004 T081, on 2026-08-06 —
failed, and failed identically against the **currently published** `mfm-2026-08` release. Three
separate defects, recorded in full with counts in
`reports/wh40k-11e-2026-08/consumer-compat.md` §2. In short:

1. **Tool-side.** `faction.parent_faction_id` is a self-referencing foreign key and the array is
   sorted by id, so five chapters load before their parent and SQLite's per-row foreign-key check
   fails. `PRAGMA defer_foreign_keys = ON` inside the load transaction fixes it and still enforces
   every key at `COMMIT`. The tool does not do it; a real ingestor must.
2. **Data-side, pre-existing.** With foreign keys deferred, the published bundle fails on 842
   duplicate `datasheet_keyword` primary keys and 43 duplicate `datasheet_weapon` keys. The
   enriched candidate reduces both to **zero**.
3. **Data-side, this candidate.** 36 duplicate `datasheet_cost` and 41 duplicate
   `datasheet_cost_tier` keys survive from the published release — byte-identical rows across 32
   datasheets that appear under more than one faction, so a dedupe at emission is mechanical. And
   4 **new** duplicate `datasheet_ability` keys where the same datasheet carries both a `core` and
   a `datasheet` ability named `Super-heavy Walker`; the consumer's primary key is
   `(datasheet_id, name)` with no `ability_type`, so this one is a content decision rather than a
   dedupe.

**Not fixed during release preparation, deliberately.** (1) is a change to the tool that is the
release's own evidence, and fixing it in the same run that produces the evidence is marking one's
own homework. (2) and (3) are pipeline emission changes and one Product Owner decision, none of
which belong in a run whose job was to prepare a candidate. None of them is a regression: the
released `003` site build reads this candidate completely and correctly (T082, same report §1),
and on two of the five duplicate classes the candidate leaves consumers strictly better off than
the release already in production.

## 9. The glossary coverage denominator counts unit names (004 T064, T084)

`contracts/authored-summary-gates.md` §4.1 excludes `faction` and `chapter` keywords from the
glossary denominator, but the classification vocabulary has no value for *a datasheet's own name
repeated as a keyword*, and those dominate: **1 031 of the 1 441** distinct non-faction,
non-chapter keywords in the `wh40k-11e-2026-08` bundle match a datasheet name exactly.

The effect is that `WGC_GATE_GLOSSARY` cannot be switched on. The T064 campaign delivered 70
entries against its scoped 60-100, and the gate still blocks with 1 421 `GLS-MISSING` findings,
because it is asking for definitions of `Wolf Guard Pack Leader with Jump Pack`. Full measurement,
both rehearsal runs, and the ordered fix are in `docs/verification/gate-switch-on-rehearsal.md`.

The fix is a new keyword class plus a §4.1 amendment — a contract revision, not a code change, and
not one to make as a side effect of a release. The gate stays `off`, which is exactly the state
the design provides for: names ship, publication is not blocked, gaps stay named in
`summary-coverage.md`.

Two smaller observations from the same rehearsal, also unfixed: several keyword keys arrive
comma-joined (`ancient , deathwing`) rather than split, and one arrives mojibaked
(`Ûthar the Destined`).

## 10. The detail source moved mid-candidate, and seven abilities now have no summary

Between the `wh40k-11e-2026-08` candidate's acquisition at **2026-08-07T00:10Z** and a rebuild at
**02:56Z the same day**, the detail source's content fingerprint moved `658187f0` → `8356e6d9`.
The points source did **not** move (`6075ce5c` both times), so no price changed. What changed is
that four datasheets gained a detail match and one was added — `detail_source: none` fell from 10
to 6. `ds-clanblade` was priced but detail-less at 00:10Z and carries a full datacard now.

Those datacards bring **seven `datasheet:` abilities with no authored summary**, so the build
raises seven blocking `SUM-MISSING` and the candidate cannot be re-authored:

`agile-reach` · `blade-of-the-clans` · `cornered-prey` ·
`drakolithe-once-per-battle-per-token` · `elemental-ensnarement` · `on-the-hunt` ·
`panicked-quarry`

They are the **only** unresolved blocker on that build — every `REC-NEVER-PRICED` in the same
report carries an approved resolution and is suppressed. The pipeline fixes for follow-up item 8
are already on `main` and were verified against this very build: **zero `CON-DUPLICATE-KEY`**,
`tools/consumer_compat.py` clean, the unmodified `003` site green at 2 462 pages, and CI run
`31143570263` reproducing the local bundle byte for byte
(`918465496b0d98968287fc8e1e206a288676ef3ef01da12143cdc6944b299bd6`).

**Not a defect, and deliberately not fixed here.** Authoring a summary from the mechanic is a
human act; machine paraphrase of the publisher's text is a policy violation rather than a
shortcut, which is exactly the rule that makes these seven a gate. Two ways forward, both the
Product Owner's: author the seven summaries, or record dated resolutions accepting that those
Aeldari datasheets ship without those abilities this release. Either way, re-run `candidate.yml`.

**The general point is worth keeping even after these seven are cleared.** A candidate is built
against a source that keeps moving — the 11th-edition detail source is actively being populated —
so any candidate left open long enough will acquire new editorial work before it is approved. The
release flow has no answer to that yet beyond re-running and re-reviewing.

**Partially discharged by `008-wargear-option-completion` (2026-08-17), for one specific shape of
"the source moved": a whole faction becoming unreachable.** `008`'s T074 dry-run found the detail
source's own sitemap enumerating only 10 of 30 published factions, and several previously-published
faction slugs renamed or 404ing outright. The per-faction carry-forward mechanism (FR-024/FR-025,
`curation/carried-forward-factions.json`, `pipeline/curate/carry_forward.py`) gives the release flow
its first real answer for that one drift shape: a declared faction is sourced from the previous
published version rather than blocking the whole candidate, visibly and without regressing any
coverage figure. **Still open**: the *content* drift this item was originally about — an existing,
reachable faction's page gaining or changing editorial material (new abilities, moved keywords)
mid-candidate — has no carry-forward equivalent and still has no answer beyond re-running and
re-reviewing. The two are different failure shapes (a faction disappearing vs. a faction's content
changing) and only the first has a mechanism now.

**Materialised, same day (2026-08-18)**: the `wh40k-11e-2026-08-4` candidate dispatch (008's own
release) hit exactly the still-open half of this item. 24 approved ability summaries' live source
digests no longer match the digest each was approved against — `SUM-NEEDS-REREVIEW` on each,
`COV-SUMMARY-REGRESSION` on the resulting coverage drop, `BLOCKING`, exit 30, no candidate branch
pushed. None of the 24 keys are option- or equipment-related; the carry-forward mechanism itself
worked correctly in the same run (every declared faction resolved as designed). This is evidence
this item's general point is still true, not a new defect — "re-running and re-reviewing" is
exactly what happens next, and the Product Owner's two ways forward (author the 24 summaries, or
record 24 dated resolutions) are unchanged from this item's own original framing above.


## 11. `pipeline-run-interface.md` owes an additive row for the `option-regression` command

`006` T011 landed `rules-pipeline option-regression`: the FR-009 zero-regression harness's layer
2, which rebuilds the published option tree with the extended pipeline and diffs it, per choice
and per field, into `reports/<rulesVersionId>/option-regression.md`.

`contracts/pipeline-run-interface.md` is **frozen at 1.0.2** and its §1 declares exactly eight
commands. A ninth is a MINOR bump of a contract that lives in another repository
(`WargameCompanion:specs/002-rules-data-pipeline/contracts/`), and a feature branch may not
perform a cross-repository versioning exercise as a side effect of shipping a tool. So the
command is implemented ahead of its row, exactly as `COV-WEAPON-ABILITIES-EMPTY` was in item 5.

**What makes that defensible here rather than a habit**: an *evidence* command is not on the
approval-gate path. `option-regression` writes one report and nothing else — it never writes
`data/`, `curation/`, `state/`, a Release, or the manifest, and no workflow branches on its exit
code, which is always `0`. `pipeline/cli.py` holds it in `EVIDENCE_COMMANDS`, deliberately
**outside** `COMMANDS`, so anything reading the contract's own §1 list still sees the eight
commands the contract declares. `tests/contract/test_cli_surface.py` asserts both the separation
and the command's full option surface, so the drift protection is unchanged.

**Owed**: an additive §1 row and a 1.1.0 bump of `pipeline-run-interface.md`, with a changelog
entry, naming `option-regression` as an evidence command and stating the not-on-the-gate-path
property as part of the contract rather than as an implementation convention.
## 12. `pipeline-run-interface.md` owes `build --published-at` / `--published-at-from-report`

`snapshotMeta.publishedAt` is the only timestamp the bundle carries, and
`curated-snapshot-format.md` §6 has required since 002 that it be **"an explicit build input
rather than 'now'"** — that clause is what makes FR-033 ("byte-identical bundle from an unchanged
tree") and FR-039 (the approval assertion) mean anything at all.

`pipeline.cli.run_build` took it as an input. **No invocation could supply it.** The `build`
subparser declared only `--rules-version-id` and `--since`, `_run_build_command` never passed the
argument, and the fallback stamped `datetime.now(UTC).date()`. No configuration variable offered
a way round it either. So the documented guarantee described behaviour the pipeline did not have,
and it went unnoticed for as long as every build and its dispatch fell inside one UTC day.

`wh40k-11e-2026-08-2` is where it stopped being invisible: approved on 2026-08-12, dispatched on
2026-08-13, and `publish.yml`'s rebuild produced a bundle whose **only** difference from the
approved one — one scalar, in a whole-bundle structural diff — was
`/snapshotMeta/publishedAt`. Exit 51, on content nobody had changed.

The fix adds two options to `build`, neither of which the frozen contract declares:

- `--published-at <YYYY-MM-DD | YYYY-MM-DDTHH:MM:SSZ>` — the explicit input §6 always described.
- `--published-at-from-report` — read the date out of this checkout's own
  `reports/<id>/report.json`, which `candidate.yml` commits beside `data/`. `publish.yml`'s
  rebuild uses this one.

**Why the derived option rather than a fifth `workflow_dispatch` input.** The date has to be a
property of the *approved commit*, not of the dispatch that publishes it. A typed input is a
second place the truth can live, it can disagree with what was approved, and the gate cannot
notice: `pipeline/publish/gate.py` reads `publishedAt` back out of the bundle the rebuild just
produced, so anything the rebuild stamps is what the gate believes. Deriving it from the commit
makes the approval and the date the same fact, and keeps the dispatch parameters unchanged
(`rules_version_id`, `commit_sha`, `expect_sha256`, `channel`) — an approver's checklist does not
move because of a bug fix. Resolution happens before the acquisition sweep, and a missing or
unusable record exits `60` instead of falling back to the clock, because a silent fallback is
precisely the defect being replaced.

**What makes implementing ahead defensible here.** Item 11's argument does not apply — these two
options *are* on the approval-gate path. The different argument is that they add no new
capability to the contract: they make an existing clause of a sibling contract reachable. §1's
own wording is "**Selected** command options", the command itself is unchanged, every existing
invocation behaves exactly as before, and `candidate.yml` passes neither option, so a first build
still stamps its own day. `pipeline/cli.py` holds them in `PUBLISHED_AT_OPTIONS` and
`tests/contract/test_cli_surface.py` in `PENDING_CONTRACT_COMMAND_OPTIONS`, deliberately apart
from the contract's own set, so the surface stays asserted against the contract rather than
against itself and the debt is named rather than absorbed.

**Owed**: a 1.1.0 bump of `pipeline-run-interface.md` (in
`WargameCompanion:specs/002-rules-data-pipeline/contracts/`) declaring both options on §1's
`build` row, and a §4 sentence stating that the gate's rebuild takes the publication date from
the approved commit's recorded report. Worth stating in §4 rather than only in §1: it is a
property of the approval, not a convenience of the CLI.

## 13. PR #13's own rebuild-proof evidence never reached `main`

`wh40k-11e-2026-08-2` published successfully (`site/manifest.json`, `state/published-checksums.json`
committed at `51e586bf`, live at `reports/wh40k-11e-2026-08-2/`) — this item is not about the
release, which is sound. It is about a process gap the release's own paper trail left behind.

PR #11 (this item's own fix, item 12) merged **to `main`** at 2026-08-13T13:06:13Z. PR #13
("Candidate wh40k-11e-2026-08-2, rebuilt on a later day") merged one minute later, at 13:07:27Z —
but its base branch was `fix/published-at-input`, not `main`, because the candidate branch it
carried had to be re-authored on top of item 12's fix before `publish.yml`'s rebuild step could
reach it (the rebuild installs the checked-out commit's own code). Nobody re-merged
`fix/published-at-input` into `main` afterward. The result: `reports/006-published-at-fix/
rebuild-proof.md` — the one file PR #13 added, and the whole of its evidence that a rebuild on
2026-08-13 reproduces the `expect_sha256` approved on 2026-08-12 — exists on
`origin/fix/published-at-input` (head `69d5a9df`) and is unreachable from `origin/main`.

**Why this did not block or corrupt the release.** `publish.yml` dispatched against `main`'s own
head at the time (`781bb6ce`, PR #11's merge commit, which already carried item 12's fix on the
approved candidate's committed `data/`/`reports/` tree), rebuilt it, and the rebuild's own checksum
assertion — the thing `expect_sha256` exists to check — passed for real, live, in that run
(`https://github.com/The-BadgerWorks/wargame-rules-data/actions/runs/31703446027`). The published
bytes are exactly what was approved. What is missing from `main` is only the **standalone written
record** of the local proof PR #13's description walks through; the gate re-proved the same claim
itself, independently, at publish time.

**Not fixed here**, because doing so is a git operation on repository history
(cherry-pick or merge `fix/published-at-input`'s remaining commits onto `main`) that a documentation
task should not perform as a side effect, and because the fact it would recover — a rebuild on
2026-08-13 reproduces the 2026-08-12 approval — is now redundantly proven by the live publish run
itself. **Action needed**: a maintainer decides whether `reports/006-published-at-fix/
rebuild-proof.md` is worth cherry-picking onto `main` for the historical record, or whether the
live `publish.yml` run's own log is sufficient evidence and the orphaned branch can simply be
deleted once PR #13 is confirmed fully superseded. Either way, this is the kind of drift a
release-branch topology with two active fix branches invites, and it is worth a process note for
the next candidate that needs a fix landed mid-review: prefer basing the fix directly on `main` and
rebasing the candidate onto `main` afterward, rather than the reverse.

## 14. Nothing tests the equipment-overrides escape hatch (006 T031)

006 T031 built the equipment-overrides curation escape hatch — `EquipmentOverrideEntry`/
`EquipmentOverrideItem` (`pipeline/models/authored.py`), `schemas/curation/
equipment-overrides.schema.json`, `pipeline/curate/authored.py`'s `equipment_override_for` lookup
and its dangling-reference checks, and the `.github/CODEOWNERS` line for
`/curation/equipment-overrides.json` — mirroring the option-overrides escape hatch T023 extended
the same phase.

**What T023's sibling has that T031's does not**: `tests/enrichment/test_composition_option_overrides.py`
exercises the option-override path directly — an override resolving an `OPT-UNPARSED` row, an
override naming a datasheet/line/weapon row that does not exist (each asserted blocking), and a
still-valid override on a suppressed composition row. A repository-wide search for
`EquipmentOverride`, `equipment_override_for`, and `equipment-overrides` under `tests/` at the time
of this review (006 T053) returns **zero matches** outside the implementation itself and
`curation/README.md`-style documentation. No fixture in `fixtures/enrichment/curation/` exercises
`equipment-overrides.json` either, and no `curation/equipment-overrides.json` has ever been
authored in this repository — the escape hatch has never been exercised end to end, by a test or by
a real override.

**Why this is a real gap and not a scope mismatch.** `data-model.md` §4 describes the equipment
override in the same terms as the option override, and plan.md's Requirement-to-component mapping
lists FR-011 (extended overrides) as covering both. Nothing in spec.md's Acceptance Scenarios or
Verification Evidence Plan calls out an equipment-override test by name, which is why it did not
block T051's scenario-to-evidence mapping — but the code path it names (a dangling `weapon_line` or
`composition_line` failing validation, a resolved override clearing an `EQP-UNPARSED` finding) is
untested today.

**Not fixed here**, for the same reason item 3 was left alone: writing the missing test is a
substantive addition to `tests/enrichment/`, not a documentation task, and belongs in its own
change rather than riding along inside a Polish-phase review. **Action needed**: extend
`tests/enrichment/test_composition_option_overrides.py` (or a new sibling file) with the equipment
equivalent of its existing option-override cases — a resolving override, a dangling-datasheet
override, a dangling-line override, a dangling-weapon-row override — before the first real
`curation/equipment-overrides.json` is authored against live data, so the first real use of the
escape hatch is not also the first test of it.

**Closed by `007-loadout-display-fidelity` T034**: `tests/enrichment/test_equipment_overrides.py`
now exercises exactly the four cases this item asked for (resolving, dangling-datasheet,
dangling-line, dangling-weapon), landed ahead of the first real
`curation/equipment-overrides.json` being authored, per the item's own closing instruction.

## 15. The footnote-constraint vocabulary matched zero real rows this release, despite real candidates existing (007)

`007-loadout-display-fidelity` shipped a two-member closed vocabulary
(`not_replaceable`, `one_per_unit`, `pipeline/models/curated.py`'s `CuratedItemConstraint
.constraint_type`) for footnote-style restrictions, sized against the taxonomy T002/T036 built.
`datasheetItemConstraints` shipped **zero rows** in `wh40k-11e-2026-08-3`
(`reports/wh40k-11e-2026-08-3/spot-check.md` §4; `report.json`'s `loadout.item_constraints` reads
`0/0`, 100% by the zero-attempts convention) — not because no restriction-shaped rows exist in the
live corpus, but because none of the ones that do exist matched either vocabulary member closely
enough to resolve.

The live taxonomy measurement (`reports/footnote-restriction-taxonomy/2026-08-14.md`, T003) found
real candidates: of the options grammar's 206 unparsed rows, **12 carry a negation signal** (9
under `refused_conditional_or_equipment_qualified`, 3 under `head_ok_no_verb`) — genuine
restriction-shaped text the two-member vocabulary does not (yet) resolve to a structured fact,
reported as advisory `CST-UNPARSED` instead (`docs/runbook.md`'s new "Resolving an unparsed
item-constraint row" section). R-J itself is confirmed (every footnote-style restriction arrives
as a refused option row, not through a second, unwatched path — the composition and equipment
residual tables in the same report are both `neither`-only), so this is squarely a vocabulary-
coverage gap, not an arrival-path gap.

**Not fixed here**, deliberately: `curated.py`'s own docstring states the vocabulary "grows only
with a version bump of `itemConstraintVocabularyVersion`, on `restriction_type`'s precedent" — a
versioned decision, not a Polish-phase patch. **Action needed**: a future feature (or a dedicated
follow-up task) reads the 12 negation-signal candidates' actual structural shape (never their
text — the taxonomy tool is deliberately text-free) and either widens the vocabulary with a third
member, or confirms the 12 are a distinct restriction shape that needs its own production rather
than a vocabulary member at all. There is also currently no dedicated curation override file for
`CST-UNPARSED`/`OPT-SCOPE-UNRESOLVED` (unlike `OPT-UNPARSED`/`EQP-UNPARSED`, which resolve through
`option-overrides.json`/`equipment-overrides.json`) — building one, following that precedent, is
the one-off fallback if a widened vocabulary still leaves a residual.

## 16. `loadout.rendering_equivalence`'s 15.0% first-release baseline needs investigation before any ratchet decision (007)

`wh40k-11e-2026-08-3` reports `loadout.rendering_equivalence` at 388 matched of 2,587 compared
(15.0%), with 1,525 datasheets `not_compared` (`reports/wh40k-11e-2026-08-3/report.json`). This is
report-only by design (FR-022, Product Owner decision 2026-08-13) — neither figure is in
`LOADOUT_RATCHETED_KEYS`, and nothing about publishing this release depended on either number.

The figure is a first release with no prior baseline to compare against, so 15.0% is neither
"good" nor "bad" on its own — but it is also not yet **understood**: this session did not
decompose the ~85% of compared datasheets that mismatch (2,587 − 388 ≈ 2,199) into cause classes.
The one live sample this release's spot-check drew (`reports/wh40k-11e-2026-08-3/spot-check.md`
item 6, a `RND-EQV-MISMATCH`) was explained as a template/normal-form gap rather than lost data,
but one sample is not a distribution.

**Not investigated here**, because doing so is a data-analysis task over `not_compared`/mismatch
reasons that belongs in its own pass, not folded into a Polish-phase documentation review.
**Action needed before any future decision to ratchet either `loadout.rendering_equivalence` or
`loadout.rendering_equivalence_not_compared`**: sample a representative set of the ~2,199
mismatches (not just one), classify them by cause (template gap vs. genuine extraction defect vs.
normal-form gap), and separately investigate why 1,525 of ~4,112 attempted comparisons landed
`not_compared` — both are prerequisites the report-only decision explicitly deferred rather than
answered.

## 17. The org still blocks Actions-created pull requests, and it bit twice in one release (007)

`candidate.yml`'s own "open or update the candidate pull request" step has never completed
unattended in this repository, across two separate releases now. `wh40k-11e-2026-08-2`'s
candidate needed a manually-opened PR the first time this was hit. `wh40k-11e-2026-08-3` hit a
**second**, slightly different symptom of the same underlying restriction: the run that produced
the guard-compliant `data`+`reports`-only candidate completed every step successfully, including
"Open or update the candidate pull request" — but because `gh pr view <branch>` matches closed
PRs too, it found and edited the body of the already-closed PR #17 rather than creating a new one,
so a PR still had to be opened by hand as PR #20 (`.impl-progress.md`'s "#18 and #19 merged... the
fresh, guard-compliant candidate" section).

**Not fixed here**, because it is a repository-settings change (permitting the default
`GITHUB_TOKEN` — or a dedicated app installation — to create pull requests), not a workflow-code
fix, and this session has no administrative access to change it. **Action needed**: a maintainer
either enables "Allow GitHub Actions to create and approve pull requests" for this repository, or
provisions a scoped PAT/GitHub App installation token for `candidate.yml`'s PR-creation step
specifically (narrower than the general repository setting, if that is preferred) — see
`docs/repo-settings.md` for the pattern this repository already uses for scoping least-privilege
credentials to a single workflow step. Until then, every candidate needs a human to open (or, as
happened this release, re-open) its own PR, which is a process cost worth removing before the next
release depends on it going smoothly under time pressure.

## 18. ~~The change-class guard means a future multi-class feature must plan its split-PR release path from the start~~ — **discharged by 008-wargear-option-completion**

**Discharged, 2026-08-15 (008 T026).** `008-wargear-option-completion`'s `plan.md` names the exact
discipline this item asked for, before a single production was written: a *Delivery sequencing*
section stating the PR A (`pipeline/`+`tests/`) → PR B (`curation/`) → PR C (`data/`+`reports/`)
order up front, and `tasks.md` tagging every task with the pull request it belongs to in a table
at the top of the file, rather than discovering the split at release time. The Foundational phase
(T015-T026) landed entirely as PR A commits, each one `pipeline/`+`tests/`-only (confirmed by
`git status --short` before every commit in this phase — no `curation/` or `data/` file appeared
in any diff). Whether the discipline holds all the way through Phase 7's override authoring (a
genuinely different change class, landing later in the same feature) and the Release phase's PR
A → B → C merge order is still open — this item is marked discharged for the *planning and
Foundational-phase execution* the original text asked for, not for a release that has not
happened yet. If the split turns out to fail anyway at Phase 8, that is a new, sharper follow-up
in its own right, not a reason to reopen this one.

### Original text (007)

`007-loadout-display-fidelity`'s first candidate PR (#17) mixed `pipeline+tests` and `curation`
change classes, because `candidate.yml` built the candidate branch on top of the still-unmerged
feature branch — its diff against `main` therefore carried the whole feature's code alongside the
candidate's own data churn. `tools/check_change_classes.py`'s guard correctly refused it
(`FAIL: this PR touches more than one change class: curation, data, pipeline+tests`), and the
release had to be restructured under time pressure into three separate PRs (#18 `pipeline+tests`,
#19 `curation`, #20 `data`+`reports`) via `git worktree` + pathspec checkouts rather than a clean
commit-range split, because the feature's ~15 commits interleaved all classes throughout
(`.impl-progress.md`'s "T067 PASSED... then PR #17 turned out unmergeable, restructured"
section).

This is the guard doing exactly its documented job — nothing about it was weakened, and the
eventual release was correct — but discovering the restructuring need at release time, rather than
planning for it from the feature's first commit, cost real session time and required a
non-standard git technique (worktree-plus-pathspec-checkout, not cherry-pick) to execute cleanly.

**Not fixed here**, because the underlying discipline (one change class per PR) is correct and
already documented (`docs/repo-settings.md`, `tools/check_change_classes.py`'s own module
docstring) — what is missing is process guidance for *authoring*, not for the guard itself.
**Action needed**: a future feature whose plan already anticipates touching more than one change
class (code changes, a curation escape hatch, and eventually a data candidate — which describes
almost every substantive feature this pipeline ships) should structure its commit history from the
start as cleanly separable per-class ranges — either by branching each class off the previous
one's merge point rather than working on one long-lived feature branch, or by committing each
class's changes in a way that a `git diff --name-status` per commit never crosses a class
boundary. `plan.md`'s own Separation gate already states the discipline in the abstract ("Delivery
is planned as separate pull requests accordingly"); this item is the concrete lesson that "planned"
has to mean "structured in the commit history," not just "intended."

## 19. ~~Two~~ Five 008 finding codes are ahead of `validation-report.md`'s own contract row; O2's exact restated ceiling ~~is not sized yet~~ **is now sized (2026-08-17)** (008)

`008-wargear-option-completion`'s Foundational phase (T018/T019) catalogued two new finding codes
— `OPT-OVERRIDE-REDUNDANT` (advisory) and `COV-EQUIPMENT-REGRESSION` (blocking) — in
`pipeline/report/catalogue.py` and in `tests/unit/test_finding_catalogue.py`'s independently-
transcribed `PENDING_CONTRACT_SEVERITIES` block, on `COV-WEAPON-ABILITIES-EMPTY`'s precedent
(item 5 above): `validation-report.md` is Frozen (`002` accepted 2026-08-04), so adding its owed
§3 rows for these two codes is a cross-feature versioning exercise this feature's own scope does
not reach, exactly as item 5 was for its one code. **Not fixed here.**

**2026-08-17 addition**: Phase 8a's per-faction carry-forward mechanism (Product Owner decision
2026-08-17, FR-024/FR-025) added three more codes on the identical ahead-of-contract terms:
`SRC-FACTION-CARRIED-FORWARD` (advisory), `SRC-FACTION-CARRY-FORWARD-UNUSED` (advisory),
`SRC-FACTION-CARRY-FORWARD-NO-PRIOR` (blocking). **Action needed**: a future housekeeping pass (on
`006` T050's and `004` T076's own precedent of batching several owed contract rows into one
cross-feature update) adds all five of this feature's codes to `validation-report.md` §3 alongside
item 5's still-outstanding `COV-WEAPON-ABILITIES-EMPTY` row and item 11/12's still-outstanding
`pipeline-run-interface.md` rows, rather than five-plus separate single-code amendments to a frozen
contract.

Separately: **Open Decision O2 was decided at T014 and is now sized.** The Product Owner's
2026-08-15 T014 ruling committed to restating SC-002 to "the measured reachable ceiling" — not to
confirming the 98% as written — on the strength of T003's conditional-blocking census, whose own
low-end estimate (22 datasheets) already exceeded SC-002's entire 21-datasheet headroom. The exact
restated number was deliberately not guessed at T014: T074's mid-campaign real-corpus dry-run,
extended by Phase 8a's carry-forward mechanism once T074 found the corpus itself short several
factions, measured it precisely. **Resolved 2026-08-17**: SC-002 restates to **≥97% (≥2,029/2,084)**
— `1,916 + (147 addressable − 34 permanently-conditional-blocked) = 2,029` — recorded in `spec.md`
Clarifications session 2026-08-17 and `plan.md` Open Decision O3, exactly as T077's Product Owner
checkpoint was scoped to do. This item can be considered closed on the O2-sizing thread; the
finding-code contract-row debt (first paragraph) remains open.
