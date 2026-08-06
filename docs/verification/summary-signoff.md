<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Wrote the per-faction ability-summary
     sign-off template (task T134): reviewer, faction, date, records reviewed, and the checklist
     outcome, as the spec's manual evidence for SC-002. The sign-off table below is deliberately
     left pending -- no automated process may record a human review, and none is fabricated
     here. -->
# Ability-summary sign-off

Required by `tasks.md` T134 and the spec's *Manual validation* section: **"ability summaries
MUST be reviewed by a human against the mechanics-only, original-wording, and length criteria;
evidence is the recorded review state per summary and a reviewer sign-off per faction"**
(SC-002).

**Status: template ready; the human review it records has not happened yet.** Nothing in
`pipeline/` can perform or attest to this review -- `review_state` and `reviewed_by` are fields a
human curator sets by editing `curation/abilities/*.json`
(`docs/authoring-summaries.md`), and `tools/check_summary_approvals.py` (task T131) only checks
that the *reviewer* is not the *author*, never that a review happened at all. This document is
where the human act of reviewing gets recorded, separately from the CI-checkable mechanics of
who is allowed to record it.

## Why the sign-off table below is empty

At the time this template was written, this repository has never published a real rules
version -- there is no faction whose ability entries describe real published mechanics yet.
The only `curation/abilities/*.json` entries that exist are the invented, mechanics-only fixture
text seeded for `fixtures/minimal` and `fixtures/sample` (task T133), each recorded with
`reviewed_by: "fixture-curator"` -- a placeholder identity an automated task assigned while
authoring the fixture content, not evidence that a human applied the checklist below to it.

**That placeholder is explicitly not a sign-off**, for the same reason the pipeline never
self-attests to anything else that requires human judgement: an actor cannot review its own
work, which is exactly the property `tools/check_summary_approvals.py` enforces for
`review_state: "approved"` in `curation/`. Recording a fabricated reviewer name here would
defeat the purpose of the requirement rather than satisfy it, so no row is filled in.

## What the human reviewer must do

1. Open `curation/abilities/<faction-id>.json` for the faction under review.
2. For every entry with `review_state` other than `approved` (or every entry at all, for a
   first-time full-faction pass), apply the fixed checklist from `docs/authoring-summaries.md`
   verbatim:
   - [ ] Mechanics only -- no lore, no flavour, no narrative framing.
   - [ ] Length at or under `WGC_SUMMARY_MAX_CHARS` (1000 by default, raised from 240 by
         Product Owner decision on 2026-08-06).
   - [ ] Not a rewording of the publisher's text (a policy check, not a quality one -- see
     `docs/authoring-summaries.md`'s "What 'authored from the mechanic' means").
   - [ ] No lore, no tone.
3. For each entry that passes all four, open a pull request setting its `review_state` to
   `approved` (from `draft` or `in_review`) or leaving it `approved` (after a `needs_rereview`
   re-write) -- **as someone other than the entry's `reviewed_by`/PR author**, so
   `tools/check_summary_approvals.py` does not refuse the PR as a self-approval.
4. Fill in one row below per faction reviewed, when the PR merges.

## Sign-off record

| Reviewer | Faction | Date | Entries reviewed | Checklist outcome | Evidence |
|---|---|---|---|---|---|
| adhoxx | `f-emberwrights` (fixture) | 2026-08-04 | 6 (`fixtures/sample/curation/abilities/f-emberwrights.json`) | pass — all 4 criteria on all 6 entries; the 3 deliberately non-approved entries (`in_review`, `needs_rereview`, `draft`) retained as-is for state-machine tests | this commit (review conducted over the full entry text) |
| adhoxx | `f-glasswold-covenant` (fixture) | 2026-08-04 | 1 (`fixtures/sample/curation/abilities/f-glasswold-covenant.json`) | pass — all 4 criteria | this commit |
| adhoxx | `f-ashen-vigil` (fixture) | 2026-08-04 | 6 (`fixtures/minimal/curation/abilities/f-ashen-vigil.json`) | pass — all 4 criteria on all 6 entries | this commit |

No real faction row exists yet because no real rules version has been curated. The first real
faction reviewed under this process should be the first row added once a genuine acquisition
run produces real `curation/abilities/` content for a real faction -- at which point this
document should also gain a short note distinguishing "fixture sign-off" rows (present for
process completeness, never gating anything real) from real-faction rows (which do gate SC-002
for a real release).

## What this does not block

Publication is gated by `review_state` (`SUM-MISSING` / `SUM-UNAPPROVED` / `SUM-NEEDS-REREVIEW`,
`pipeline/validate/summaries.py`), which is the automated, structural half of FR-020/FR-023.
This document is the other half -- SC-002's human evidence that an `approved` entry actually
received a human review against the checklist, which no automated check can verify by
construction. A faction's ability entries can be structurally `approved` (and therefore
publishable) without a completed row here; that gap is exactly what this document exists to make
visible rather than to silently close.
