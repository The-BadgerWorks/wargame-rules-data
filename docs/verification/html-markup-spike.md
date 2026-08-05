<!-- AI-Assisted: Claude Code (model: claude-opus-5) - Recorded the 004 T002 markup spike that
     retires risk R-A: two real current-edition faction datacard pages retrieved once, analysed
     for STRUCTURE ONLY (tag, class, and attribute names), and the resulting selector decision
     for pipeline/parse/wahapedia_html_dom.py (T073). No retrieved byte is committed here or
     anywhere else in this repository. -->
# T002 — the current-edition HTML markup spike (risk R-A)

`004-rules-data-enrichment` plan *Risks* **R-A**, research **D1c**. D1c established the labelled
block vocabulary of a current-edition faction datacard page by reading a Markdown *conversion* of
one, so the block identities were observed as **heading labels** and the **markup carrying them was
never seen**. That left `pipeline/parse/wahapedia_html_dom.py` (T073) unable to choose between
keying off stable selectors and falling back to label-anchored segmentation. This page closes that
question with a direct reading of the markup.

**Status: R-A retired. Stable selectors are viable**, with two named traps recorded below. The
label-anchored fallback is still used — not as a fallback, but as the *block identity* mechanism
inside each card, because block identity is genuinely not carried by a class (see §3).

## 0. Method, and what was and was not retained

Run 2026-08-05.

- **Two** pages retrieved, once each, from the permitted `/wh40k11ed/` tree
  (`factions/t-au-empire/datasheets.html`, `factions/adepta-sororitas/datasheets.html`) — two
  factions rather than one, so "stable" means *stable across factions* rather than *stable within
  one page*.
- `robots.txt` retrieved first and honoured; browser `User-Agent`; ≥ 2.5 s between requests to the
  one host; three requests in total for the whole spike.
- Both pages cached **outside the repository**, under the operating system's temporary directory,
  and analysed there with `selectolax` — the same parser `pipeline/parse/mfm_dom.py` already uses.
- **Nothing retrieved is committed, quoted, or summarised here.** What follows is tag names, class
  tokens, attribute names, element counts, and the all-caps *block labels* — structural markers,
  not publisher prose. No datasheet name, ability, rule, or option text appears on this page, and
  none was written to any file inside the repository (FR-006, Constitution Principle 4).

## 1. `robots.txt`, re-confirmed at the same time (FR-004, research D1a)

The `User-agent: *` group, read directly:

| Path | Directive | Consequence |
|---|---|---|
| `/wh40k10ed/` | `Disallow` | never requested; guarded pre-request by `pipeline/acquire/robots.py` (T003) |
| `/wh40k11ed_/` | `Disallow` | as above — the underscore-suffixed staging tree |
| `/wh40k11ed/` | **not listed** | permitted; the tree this feature moves onto |

`sitemap: https://wahapedia.ru/wh40k11ed/SiteMap.xml` is advertised in the `*` group. Research
D1a's finding is confirmed exactly, including the correction it makes to `002/plan.md` (T001).

## 2. Per-card segmentation — a stable class pair

| Fact | Value |
|---|---|
| Datacard root | `div.dsOuterFrame.datasheet` |
| Cards found | 63 (T'au Empire), 38 (Adepta Sororitas) — one per datasheet, no wrapper duplication |
| Additional tokens on the same element | `pagebreak`, `clFl`, `sLegendary` (a Legends marker), and a run of faction-derived keyword codes (`TUTU`, `TUAC`, … / `ASAS`, `ASBF`, …) |

`div.dsOuterFrame.datasheet` is present, identical, and exactly card-counted on both faction pages.
Card enumeration is therefore a plain selector, not a heuristic.

## 3. Block segmentation — a stable class anchor, a label-asserted identity

Inside a card, the two-column body is `div.ds2col` containing `div.dsLeftСol` and
`div.dsRightСol` (**note the homoglyph — §5**). Blocks within a column are **flat siblings**:

```text
div.dsHeader          <- the block label, e.g. UNIT COMPOSITION
div.dsAbility         <- block content, one element per line
div.dsAbility
div.dsHeader          <- the next block begins
div.dsAbility
```

- `div.dsHeader` (and `td.dsHeader` inside the weapon tables) is the **only** block-label element,
  present 810 / 1 320 times across the two pages, always with the label as its text.
- **Class does not carry block identity.** A `UNIT COMPOSITION` line and an `ABILITIES` entry are
  *both* `div.dsAbility`. Identity comes from the preceding `dsHeader`'s text and from nothing else.
  This is why T073's label-anchored segmentation is the design rather than a contingency: segment on
  `div.dsHeader`, take the following siblings up to the next `div.dsHeader`, and assert the heading
  vocabulary structurally so a move fails the run loudly (the discipline `parse/mfm_dom.py` applies).

Observed `dsHeader` label vocabulary (T'au page, distinct values with counts — the structural
assertion T073 writes down):

```text
ABILITIES 63 · UNIT COMPOSITION 63 · STRATAGEMS 63 · DETACHMENT ABILITY 63 ·
RANGED WEAPONS 59 · MELEE WEAPONS 58 · WARGEAR OPTIONS 56 · WARGEAR ABILITIES 18 ·
ENHANCEMENTS 13 · LEADER 12 · LED BY 10 · TRANSPORT 6 · DAMAGED: <n>-<n> WOUNDS REMAINING 16 ·
RANGE/A/S/AP/D/BS/WS (weapon-table column heads, same class)
```

Two consequences worth stating before T073 is written:

1. The weapon-table **column heads** share the `dsHeader` class. A block scan must not treat
   `RANGE`, `A`, `S`, `AP`, `D`, `BS`, `WS` as block labels; they are distinguishable because they
   occur as `td.dsHeader` inside `table.wTable`, while block labels occur as `div.dsHeader` directly
   inside a column div.
2. `DAMAGED: …` labels embed integers, so the vocabulary assertion must match a **pattern** for that
   one label rather than a literal.

## 4. The blocks this feature actually needs

| Block | Markup | Note |
|---|---|---|
| `UNIT COMPOSITION` | `div.dsHeader` + following `div.dsAbility` siblings | one element per model line — feeds `parse/composition_grammar.py` unmodified |
| `WARGEAR OPTIONS` | `div.dsHeader` + a following `ul` (`ul.dsUl`), `li` children, nested `ul`/`li` for sub-selections | research D3's `<li>` split applies as designed; nesting is real markup nesting, not indentation |
| `KEYWORDS` | `div.ds2colKW` > `div.dsLeftСolKW`, whose text begins `KEYWORDS:` | **not** a `dsHeader` block — its own class pair |
| `FACTION KEYWORDS` | `div.ds2colKW` > `div.dsRightСolKW`, text begins `FACTION KEYWORDS:` | the FR-017 faction/non-faction split is carried **by the markup itself**, one `ds2colKW` per card (63 / 38, exactly card-counted) |
| individual keywords | `span.kwb` / `span.kwb.kwbu` inside those divs, with `data-tooltip-content="#tooltip_content<Keyword>"` | a machine-readable keyword token as well as its display text |
| weapon profiles | `table.wTable`, rows carrying `wTable2_long` / `wTable2_short` | one table per card |
| characteristics | `div.dsCharWrap` > `div.dsCharName` / `div.dsCharValue` | |
| unit cost | `td.dsUnitCostHeader`, `div.PriceTag` | not consumed — the points source remains authoritative |
| detachment metadata | `data-det-code`, `data-det-name`, `data-det-group` attributes | present on the page; relevant to T053's detachment-rule naming |

## 5. Two traps, recorded so T073 does not walk into them

**Trap 1 — a Cyrillic homoglyph in four class names.** The column classes are spelled with
`U+0421 CYRILLIC CAPITAL LETTER ES`, not ASCII `C`:

```text
'dsLeftСol'    С = U+0421 CYRILLIC CAPITAL LETTER ES
'dsLeftСolKW'  С = U+0421
'dsRightСol'   С = U+0421
'dsRightСolKW' С = U+0421
```

An ASCII selector `.dsLeftCol` matches **nothing**, silently — a zero-row extraction that looks like
a source change rather than a typo. Both spellings occur on both pages, so this is the source's
stable spelling and not a one-page defect. T073 must either write the literal codepoint (with a
comment) or select on the `ds2colKW` / `ds2col` parent and take children positionally. The
repository already owns the general defence for this class of problem in
`pipeline/normalize/homoglyphs.py`; this is the first time it has been needed in a **selector**
rather than in a value.

**Trap 2 — faction-varying colour classes.** `dsColorBgTAU` / `dsColorBgAS`, `dsColorFrTAU` /
`dsColorFrAS`, `dsColorBan…` and the `TU**` / `AS**` keyword-code tokens differ per faction: 173 of
the observed class tokens appear on one page and not the other, and every one of them is
colour-or-faction derived. **No selector may include them.** Every token this feature keys on
(`dsOuterFrame`, `datasheet`, `dsHeader`, `dsAbility`, `ds2col`, `ds2colKW`, `dsUl`, `wTable`,
`kwb`, `kwbu`, `dsCharName`, `dsCharValue`, `PriceTag`) was verified present on **both** pages with
consistent, card-proportional counts.

## 6. Verdict, and what it changes

| Question R-A asked | Answer |
|---|---|
| Can `wahapedia_html_dom.py` key off stable selectors? | **Yes** for card enumeration, column layout, weapon tables, and the keyword split |
| Must it use the label-anchored fallback? | **Yes**, for block identity within a column — not as a fallback but as the only correct mechanism, since `div.dsAbility` is shared by unrelated blocks |
| Is the heading vocabulary assertable? | **Yes** — the vocabulary in §3, with `DAMAGED: …` matched as a pattern and the weapon-table column heads excluded by their `td` / `table.wTable` context |
| Does anything about D1c's finding change? | Only in detail: `KEYWORDS` / `FACTION KEYWORDS` are separately labelled as D1c reported, but via `ds2colKW` classes rather than `dsHeader` blocks |
| Is a headless browser needed? | **No.** The pages are server-rendered static HTML; every block above was extracted from the retrieved bytes with `selectolax` alone, so FR-039/SC-012 determinism is unthreatened |

T073 is therefore unblocked and its design is fixed: **class-anchored card and column discovery,
label-anchored block identity, homoglyph-literal column selectors, and no colour class anywhere.**
