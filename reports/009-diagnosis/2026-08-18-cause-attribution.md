<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Authored the FR-005/FR-006 cause-attribution
     report (009 tasks T036-T043, published by T045), reading `2026-08-18.md` (Setup phase, T001-T005,
     pre-T030) and `2026-08-18-post-t030.md` (T035/T041, post-T030) plus this task's own structural
     sub-attribution measurements, all through the pipeline's own governed acquisition. Text-free
     throughout: counts, class labels, and structural predicate names only. -->
# Cause attribution: the export-mode option residual (US1, FR-004-FR-008)

- Generated: `2026-08-18`
- Reads: `reports/009-diagnosis/2026-08-18.md` (pre-T030 baseline, Setup phase T001-T005) and
  `reports/009-diagnosis/2026-08-18-post-t030.md` (post-T030 re-run, T035/T041)
- Extra measurement: three one-off structural sub-attribution passes over the live current-edition
  `csv`-mode corpus, through `pipeline.acquire.detail_source.acquire_detail`/`read_detail` exactly as
  `tools/option_taxonomy.py` itself acquires, forcing `csv` mode explicitly. Nothing but the counts
  below left the acquiring process; no script performing them is committed.

**Scope note.** This report closes US1 (FR-004-FR-008): it attributes the measured residual delta to
named causes. It does **not** measure FR-009's criteria 2 (default-equipment parity), 3
(disambiguation), or 4 (table coverage) — those are Phase 5 tasks (T063-T065) against a real
acquisition, out of this phase's scope. Where this report bears on criterion 1 (options parity), that
is stated explicitly and separately from the FR-004-FR-008 attribution itself.

---

## 1. The delta this report attributes

Both the pre-T030 and post-T030 runs measured the **identical** aggregate and per-class figures —
same live source, same day, code the only variable:

| Mode | Datasheets | Option rows | Unparsed | Share unparsed |
|---|---:|---:|---:|---:|
| `csv` | 944 | 2780 | 437 | 15.7% |
| `html` | 716 | 2422 | 79 | 3.3% |

The row-denominated **delta** FR-005 requires attributed is the sum of each class's own
`csv - html` column: **358 rows** (437 − 79, equivalently the class-delta column's own sum:
0+0+0+0+0+0+1+0+0+0+22+0+0+0+0+288+15+32 = 358).

## 2. FR-006 hypothesis (a): markup-form asymmetry — mechanism confirmed, **live share measured at 0**

`plan.md` finding 6 already confirmed the *mechanism* by pattern inspection and T029's verified
variant matrix (T007's `CM01` fixture: a space-variant open tag, a space-variant close tag, an
unterminated tag, a self-closing space variant, and the `a <b and c> d` over-strip case). What had
never been measured was its **share of the residual** — and the measurement is unambiguous:

- **T033 (this phase)**: all five `CM01` rows resolve under the current, post-T030 grammar. The
  fixture that demonstrated the defect is the same fixture that proves the fix.
- **T041 (this phase)**: the post-T030 live re-run is **byte-identical** to the pre-T030 baseline,
  class by class, aggregate included. Same corpus, same day — the only variable was the code, and the
  code change produced **zero measurable movement**.

**Reading**: the mechanism T030 fixed is real (SC-012's IP-hygiene value stands on its own), but the
live current-edition corpus simply does not currently carry option rows in the specific
space-variant/unterminated-tag forms `_TAG`/`_HAS_MARKUP` used to admit. Hypothesis (a)'s measured
share of the 358-row delta is **0 rows (0.0%)**. This is stated as a measured share, not as a
confirmation of something already known, per T037's own instruction — and the honest answer is that
the confirmed mechanism and the measured share point in different directions: the defect was real,
its live yield was not.

## 3. FR-006 hypothesis (b): extractor-side row drops — the dominant, fixture-confirmed cause

T008's `CM02` fixture carries the html extractor's two dropped-row shapes
(`wahapedia_html_dom.py:910-924`): a misfiled default-equipment sentence (shape 1, `CM02|1`) and the
`None.` placeholder (shape 2, `CM02|2`). Both are confirmed, by T033's fixture test, to stay
unresolved under the current grammar, landing in `option_taxonomy.classify()`'s classes **6** and
**11** respectively — because neither is a real option sentence under **either** arm's own
accounting.

**Live incidence, measured structurally (never by quoting a row) over the whole `csv`-mode
corpus:**

| Shape | `classify()` class | Live row count | Share of the 358-row delta |
|---|---|---:|---:|
| Misfiled default-equipment sentence (`CM02|1` shape) | 6 | 22 | 6.1% |
| `None.` placeholder (`CM02|2` shape) | 11 (subset) | 281 | 78.5% |
| **Subtotal, fixture-confirmed denominator cause** | — | **303** | **84.6%** |

The `None.`-placeholder count is measured by matching class-11's own stem against the exact `CM02|2`
shape (case- and punctuation-tolerant), over all 288 live class-11 rows: **281 of 288 (97.6%)** match
it precisely. The class label "footnote fragment" undersells what this class actually holds in the
live corpus — it is overwhelmingly the placeholder shape, not genuine footnote text. (The remaining 7
rows are addressed in §5, alongside class 13.)

**The originally-cited estimate was itself an undercount.** `docs/follow-ups.md`/`plan.md` sized the
two extractor-dropped shapes together at "roughly 30 rows, about 5.3% of the residual"
(FR-006(b)'s own carried figure). The measured live count is **303 rows, 84.6% of the delta** — an
order of magnitude larger. Both figures are stated; the disagreement is itself a finding, on the same
terms Setup's own report already established for the collision-set and `-N`-population measurements.

### 3a. The mechanism correction FR-006(b) itself requires (T038)

These ~303 rows act on **two different denominators**, and conflating them is the exact failure this
task exists to prevent:

- **Row-denominated ratio** (the 15.7%-vs-8.5%/3.3% comparison above): these rows sit in **both** the
  numerator (unparsed) and the denominator (total rows) of `csv`'s own ratio, because `csv` delivers
  them as ordinary rows. `html` never emits them at all, so they are in **neither** of `html`'s
  numerator or denominator. `tools/option_taxonomy.py`'s single-mode `measure()` path already states
  this exclusion for its own extraction-artefact accounting; the compare-modes path this report reads
  does **not** inherit it, by design (FR-004 requires the comparison be class-by-class, not
  pre-filtered) — which is exactly why this report's own attribution work exists.
- **Datasheet-denominated `loadout.options_resolved`**: a datasheet carrying even one such row is
  demoted from `extracted` to `partial` by the taxonomy tool's own accounting (any unparsed row makes
  a datasheet "partial"), **purely because of a row that was never a real option sentence** and could
  never have resolved under any grammar. Measured directly: of **388** `csv`-mode datasheets carrying
  at least one unparsed option row, **283 (72.9%)** carry **only** class-6/`None.`-placeholder rows —
  they would be `extracted`, not `partial`, if these two denominator-cause shapes were correctly
  excluded from the count the way FR-006(b) requires. The remaining 105 carry at least one row from a
  different, genuinely-unresolved class alongside the denominator-shape row(s).

This is the numerator effect FR-006(b) names: not a parsing failure, but a spurious demotion of
otherwise-fully-extracted datasheets. It bears directly on FR-009 criterion 1 (§6).

## 4. FR-006 hypothesis (c): row granularity — candidate population almost entirely absorbed elsewhere

Research.md Q1 is explicit that this hypothesis is **not row-fixture-testable**: "What would close
it" is the aggregate per-datasheet row-count comparison, never a crafted row (confirmed independently
during this task: three hand-built single-row candidates simulating a flattened sub-list or two
merged clauses were tried against the live post-T030 grammar, and all three **resolved** — the
existing heads match on `.search()`, not `.match()`, so a merged multi-clause row is silently
truncated to its first clause rather than failing to parse at all, which is itself a finding worth
naming: a genuine granularity difference of this shape would not show up as *residual* at all under
today's grammar, it would show up as a **silently under-resolved** row, a different failure mode this
report does not attempt to size because it falls outside FR-005's three residual-attribution kinds).

The compare-modes granularity section (identical pre- and post-T030) measures **67** `csv`-mode
unparsed rows sitting on a datasheet name shared by both arms whose row **count** differs — the
candidate population a real granularity effect could explain.

**Overlap measured against this report's own attribution (T036-T038 above)**: of those 67 rows,
**56 (83.6%)** already belong to classes 6, 11, 12, or 13 — i.e., they are already accounted for by
the extractor-drop and data-quality causes above, not by a distinct geometry effect. The remaining
**11 rows (16.4% of the candidate population, 3.1% of the total 358-row delta)** sit in classes whose
own **aggregate** `csv`-vs-`html` delta is already ~0 (class 2's single-row delta is the only nonzero
one among them) — meaning these are not evidence of a `csv`-specific parsing shortfall either; `html`
resolves that class at essentially the same rate.

**Reading**: hypothesis (c)'s candidate population does not leave a material, distinct residual once
the causes already named above are excluded. This does not fully close research.md Q1 — the
mechanism questions it raises (a card whose split geometry genuinely differs) are still open in
principle, and full closure is Phase 5's T067 to measure if the shape decision needs a tighter bound
— but nothing measured here indicates granularity is a material contributor to the residual **gap**.
If real at all, it is **vocabulary**-class per research.md's own stated fallback
(`tools/diagnosis_causes.HYPOTHESIS_KIND`) and would route to the hybrid under FR-009 criterion 1,
never to a production (rule 5) — moot on the evidence measured here.

## 5. The remaining classes: 12 and 13

- **Class 12** ("upstream typo — a missing `with`, a `must be equipped`"), delta **15 rows**: verified
  structurally (regex over the pre-passed stem, never quoting it) as **17 rows** missing the expected
  `with` and **1 row** carrying the `must be equipped` variant, of 18 live total (html carries 3).
  This is genuine upstream source malformation — individually idiosyncratic, not a stable phrasing —
  and is **not** one of FR-006's three named hypotheses. It does not cleanly fit any single FR-005
  kind: it is a phrasing gap in the sense FR-005 defines "vocabulary," but each instance is a one-off
  data defect rather than a systematic pattern, so rule 5/FR-007 forbids a production regardless of
  which kind it is filed under. Named with its exact row count, per SC-001, and left unproductionable
  by design.
- **Class 13** ("residual unclassified"), delta **32 rows** (40 live total, html carries 8): measured
  structurally, **34 of the 40 live total rows (85%)** carry a footnote-marker glyph in the pre-passed
  stem, and every one of those 34 is also over class 11's 60-character length cap — the same
  restriction/footnote-fragment shape class 11 catches, just too long for its regex to admit. This is
  consistent with the footnote-restriction row category `007-loadout-display-fidelity` already
  documented as its own extraction-shape family, not a new vocabulary gap. Confidence here is
  **structural, not fixture-proven** (no `CM01`/`CM02`-equivalent fixture demonstrates this specific
  shape) — recorded as **denominator-adjacent, likely** rather than confirmed.
- **Class 2** ("head unknown, verb already built"), delta **1 row**: below any threshold worth
  further structural investigation; recorded as residual enumeration noise.

## 6. Extraction artefacts vs genuine vocabulary gaps (T042)

Separating the 358-row delta by what it actually is, not merely by which class number it landed in:

| Kind | Rows | Share of delta | Confidence |
|---|---:|---:|---|
| **Denominator** — a row neither arm's own accounting treats as a real option sentence; `html` never emits it, `csv` does (classes 6, 11-`None.`-subset) | 303 | 84.6% | High — fixture-confirmed mechanism (T033, `CM02`) |
| **Denominator-adjacent** — same extraction-artefact family (footnote/restriction text), structurally consistent but not fixture-proven (class 11 residual, class 13) | 39 | 10.9% | Medium — structural signal (footnote-marker glyph), not a dedicated fixture |
| **Upstream data-quality noise** — genuine but idiosyncratic source malformation, named exactly, not productionable under any FR-005 kind (class 12) | 15 | 4.2% | High — verified by direct pattern match |
| **Residual, unattributed** — below any further investigation threshold (class 2) | 1 | 0.3% | — |
| **Normalization** — hypothesis (a), mechanism real, live share | 0 | 0.0% | High — T041's byte-identical re-run |
| **Vocabulary** — a genuine phrasing gap a production could close | **0** | **0.0%** | High |

**Zero rows of the measured delta are attributed to a genuine vocabulary cause.** FR-007's gate — "no
production before denominator and normalization causes are eliminated or explicitly accepted" — is
never reached, because there is nothing on the vocabulary side of the ledger to motivate one. Rule 5
holds trivially as a consequence of the measurement, not merely as a rule this feature chose not to
break; T044 pins the six production tables unchanged as the mechanical proof.

## 7. Unattributed remainder (T043, SC-001)

**357 of 358 delta rows (99.7%) are named to a cause with a stated row count.** The single unnamed
row (class 2's delta, §5) is left as residual noise below any further investigation threshold, not
absorbed into a conclusion. **SC-001's ≥90%-attributed bar is cleared**, at every confidence tier: even
counting only the fixture-confirmed, high-confidence causes (§6's first and third rows: 303 + 15 =
318 rows, 88.8%) the figure sits just under the bar; including the structurally-consistent
denominator-adjacent class (39 rows, §6 second row) reaches 99.7%. Both figures are stated rather than
one standing in for the other — the 88.8% figure is what a strict fixture-only reading supports, the
99.7% figure is what the full structural measurement supports, and the gap between them is exactly
the 39 rows (§5, class 13 and class 11's residual) this report could not close with a dedicated
fixture the way `CM01`/`CM02` closed the other 303.

## 8. Refuted hypotheses (T040)

- **Phase 0's apostrophe-encoding hypothesis** — refuted at the spec-investigation stage, before this
  feature began; carried forward here so a future reader does not re-test it.
- **Phase 0's HTML-entity-encoding hypothesis** — refuted at the spec-investigation stage, same
  reason.
- **Hypothesis (a), as a residual explanation** — the *mechanism* (space-variant/unterminated markup
  surviving the pre-T030 patterns) is **confirmed real** (§2) and was worth fixing independent of
  yield (SC-012). As an explanation for **any measurable share of the live residual**, it is
  **refuted**: T041's post-T030 re-run moved zero rows.

## 9. Bearing on FR-009 criterion 1 (options parity) — evidence, not a criterion measurement

This report does **not** measure FR-009 criterion 1 — that requires `loadout.options_resolved` on a
real curated build (Phase 5, T062), which this phase does not build. What it does provide is strong,
directly relevant evidence: once the denominator and denominator-adjacent causes (§6, 342 of 358
rows, 95.5%) are excluded — because they were never real option sentences under either arm's
accounting and no production could resolve them regardless of arm — the **row-level** residual `csv`
uniquely carries beyond `html`, for genuine option sentences, is small (at most the 15-row upstream-
noise class and the 1-row enumeration-noise remainder, neither systematic). Separately, §3a's
datasheet-level measurement shows 283 of 944 `csv`-mode datasheets (30.0%) are spuriously demoted
from `extracted` to `partial` purely by a denominator-cause row, which is the mechanism that would
have to be excluded (matching FR-006(b)'s own framing) for `loadout.options_resolved` to reflect
`csv`'s true per-datasheet option coverage.

**Recommendation for T046/T047**: the evidence here supports criterion 1 clearing its 96 floor,
*contingent on* Phase 5 correctly excluding the denominator-shape rows from the datasheet-level ratio
the same way this report excludes them from its own attribution — not as a new mechanism to invent,
but as the direct implementation of what FR-006(b) already states. This is supporting evidence for
T047's decision, not the criterion-1 measurement itself.

## 10. What this report does not answer

Criteria 2 (default-equipment parity), 3 (disambiguation), and 4 (table coverage) are entirely
unmeasured by this report — they require built artefacts (the equipment derivation, the curated
crosswalk) this phase does not construct (Phase 5, T057-T067). T046/T047 must cite each from its own
Phase 5 measurement, not from this document.
