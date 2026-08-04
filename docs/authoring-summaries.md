<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote the ability-summary authoring
     guide (task T132): the authoring loop, the fixed review checklist, and the explicit
     prohibition on machine paraphrase stated as a policy violation rather than a quality issue
     (FR-021, FR-022, reference-db-schema.md §6.1(2), research D6). -->
# Authoring ability summaries

This is what a curator does to add or update one entry in `curation/abilities/<faction-id>.json`,
and what a reviewer checks before approving it. It exists because `datasheet_ability.summary` is
`NOT NULL` in the consumer schema (`reference-db-schema.md` §6.1) — a faction with any
unsummarised ability a shipped datasheet uses cannot publish — and because the summary is the one
piece of this data set that is genuinely, originally written rather than transformed from a
source, which makes it the one place a shortcut is tempting and the one place it is prohibited
outright.

## The authoring loop

1. **Find what needs writing.** `summary-coverage.md` (`pipeline/report/coverage.py`, FR-025) is
   produced on every run, not only a blocked one, and names every ability key a shipped datasheet
   uses that lacks an approved, current summary — per faction, with the count and proportion
   leading the list. Start there rather than guessing.
2. **Read the mechanic, not the wording.** Look at what the ability actually does — its effect on
   the game, not the publisher's sentence describing it. This distinction is the whole point of
   §"What "authored from the mechanic" means" below.
3. **Write one entry** in `curation/abilities/<faction-id>.json`, keyed by `ability_key`
   (`<core|faction|datasheet>:<slug>`, matching `schemas/curation/abilities.schema.json`):

   ```jsonc
   { "ability_key": "core:deep-strike",
     "name": "Deep Strike",
     "summary": "…original, mechanics-only, ≤ WGC_SUMMARY_MAX_CHARS…",
     "review_state": "draft",
     "mechanic_digest": "…leave whatever value is already there, or omit for a new key…",
     "reviewed_by": null,
     "reviewed_at": null }
   ```

   A key is keyed **per ability, not per (datasheet, ability) binding** (research D6) — one entry
   covers every datasheet that uses it. `mechanic_digest` is written and read by the pipeline, not
   authored by hand; a curator never invents or edits its value directly (see below).
4. **Move it through the states** by editing `review_state`: `draft` (someone has started) →
   `in_review` (ready for a second pair of eyes) → `approved` (signed off). Only a pull request
   approved by someone **other than the record's author** may introduce `approved` — CI
   (`tools/check_summary_approvals.py`, task T131) fails a self-approved record even where
   `CODEOWNERS` alone cannot yet enforce a distinct reviewer.
5. **When `needs_rereview` appears**, the underlying mechanic changed since the last approval —
   the pipeline detected it, nobody has to notice on their own (see "Staying current" below).
   Re-read the (now current) mechanic, update `summary` if the mechanic actually changed what a
   player needs to know, and move `review_state` back to `in_review`.

## The fixed review checklist

Every summary, before it may be marked `approved`, is checked against exactly these four things
— not a style guide, a gate:

- [ ] **Mechanics only.** What the ability does in play. No lore, no flavour text, no narrative
  framing, no publisher adjectives that do not change a die roll (`reference-db-schema.md`
  §6.1(4)).
- [ ] **≤ `WGC_SUMMARY_MAX_CHARS`** (240 by default, `contracts/pipeline-run-interface.md` §5).
  Short enough to read on a phone. `SUM-OVERLENGTH` is the advisory finding when an otherwise
  approved summary exceeds it — fix it before it accumulates.
- [ ] **Not a rewording of the publisher's text.** See the next section — this is the one item on
  this list that is a policy question, not a quality one.
- [ ] **No lore, no tone.** A summary reads like a rules reference, not like the publisher's
  voice. Two summaries for unrelated abilities should not sound like they were written by the
  same narrator.

A summary that fails any one of these is not ready for `approved`, full stop — there is no
"approve now, fix later" for this list.

## What "authored from the mechanic" means

`reference-db-schema.md` §6.1(2) states the rule this whole workflow exists to satisfy:

> Summaries must be authored from the mechanic, describing what the ability does in the data
> set's own words. Machine paraphrase, synonym substitution, or sentence reordering applied to
> the publisher's text does **not** satisfy this contract.

**This is a policy violation, not a quality issue, and the distinction matters for what you do
about it.** A quality issue gets revised. A policy violation gets rejected outright, because the
thing it produces — however well-written — is not something this product is allowed to publish
at all (Principle 4, spec *Policy and Safety Constraints*). Concretely, none of the following
satisfy the contract, no matter how good the resulting sentence reads:

- Taking the publisher's ability text and running it through a paraphrasing tool, an LLM prompted
  to "reword this", a thesaurus pass, or a sentence-reordering script.
- Starting from the publisher's sentence and editing words until it "feels different enough".
- Translating the publisher's text and calling the translation original.

**What does satisfy it**: reading the mechanic — what happens at the table when the ability
triggers — and writing a sentence that states that, without the publisher's text open beside you
as a template to modify. If you cannot describe the mechanic without looking at how the publisher
phrased it, you do not yet understand the mechanic well enough to summarise it; go verify what it
actually does (test it, ask someone who has used it, check the errata) rather than paraphrase
around the gap.

This is also why the pipeline itself never retains the publisher's ability wording anywhere —
not in `data/`, not in a report, not in an intermediate artifact, not in version control, even
unpublished (`reference-db-schema.md` §6.1(3), FR-013). There is structurally nothing to
paraphrase *from* inside this repository. A curator authoring a summary is working from the
published rules material available to them outside this repository, the same way anyone learning
the game would, and writing down their own understanding of it — not transcribing or transforming
anything this pipeline captured.

## Staying current: the keyed mechanic digest

A curator never computes or edits `mechanic_digest` by hand. On every full run with source text
available, the pipeline (`pipeline/normalize/mechanic_digest.py`, `pipeline/curate/summaries.py`)
takes a keyed digest of the current, hard-normalised mechanic text for each ability key and
compares it against the digest an `approved` summary was last checked against:

- **Unchanged** — the summary carries forward untouched. No re-authoring, no re-review, and
  nobody has to remember to check (SC-011).
- **Moved** — the run treats that key as `needs_rereview` for this run's validation and coverage
  purposes, even though the committed file still says `approved` until a curator acts on it. Only
  the key whose mechanic actually changed is affected; every other approved key is unaffected
  (`tests/summaries/test_state_machine.py`).

The digest is **keyed** (HMAC-SHA256 under a repository-held secret, truncated to 128 bits) rather
than a plain hash, specifically so it can never be used to confirm a guess at the publisher's
wording (research D6, C6/R8) — closing the loop on the same prohibition the section above states
in prose. Nobody, including a curator with write access to this repository, can reconstruct the
mechanic text from a committed digest.

## Fixtures are exempt from none of this

Every summary seeded in `fixtures/*/curation/abilities/` is invented, mechanics-only prose for an
invented ability — never a paraphrase of any real publisher's text, exactly like every other
fixture in this repository (research D10, `fixtures/README.md`). The prohibition above applies to
test data with the same force it applies to a real release.
