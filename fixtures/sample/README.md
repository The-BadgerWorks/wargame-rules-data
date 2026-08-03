<!-- AI-Assisted: Claude Code (model: claude-opus-5) - Authored the sample fixture set's
     provenance note (tasks T041, T042). It carries the Principle 16 header for the CSVs in
     `wahapedia/`, which are pipe-delimited data files and admit no comment syntax of their own. -->
# `fixtures/sample/`

The general-purpose synthetic fixture set: one case per observed structure and per observed
quirk class. **Nothing here was captured from a real source, and nothing here was produced by
redacting a capture** — see [`../README.md`](../README.md) for why that distinction is the whole
point rather than a technicality. Every faction, unit, detachment, enhancement and ability name
below is invented, and every description field holds invented placeholder prose.

## `mfm/` — the points source

| File | What it exists to exercise |
|---|---|
| `emberwrights.html` | The happy path. `<template id="P:n">` placeholders, hidden `<div id="S:n">` blocks and `$RS("S:n","P:n")` id-to-id move instructions — including one **nested** placeholder a later swap fills — plus the streamed-boundary form `$RC("B:n","S:n")` whose arguments are the other way round. Carries a plain `YOUR UNIT COSTS` table, a `YOUR 1ST TO 2ND UNITS COST` + `YOUR 3RD + UNIT COSTS` requisition-threshold pair for one datasheet, two detachment cards with DP costs, force dispositions, enhancement lists, an `UPDATED` tag and a `Unique` tag, and `▲ (+15)` / `▼ (-10)` change-delta spans |
| `glasswold-covenant.html` | The **structural breakage** case, which must fail the run. One `<template id="P:2">` is never filled and one `<div hidden id="S:9">` is claimed by no placeholder. Either condition means a cost cell is unknowable, so the run raises `SRC-STRUCTURE-CHANGED` and exits `41` rather than mispricing a faction silently (FR-008, research D4a) |

Because of `glasswold-covenant.html`, **this set does not build end to end and is not meant
to**. It is the parser and quirk set. The set that builds is `fixtures/minimal/`.

## `wahapedia/` — the datasheet-detail source

Pipe-delimited, UTF-8 **with BOM**, one trailing empty field per record, file names matching the
real export's so the record-aware reader's per-file expected field count is exercised.

| Quirk class (research §0.1) | Where |
|---|---|
| `<span class="kwb">` markup in a description | `Datasheets.csv`, `Datasheets_wargear.csv`, `Datasheets_unit_composition.csv`, `Abilities.csv`, `Enhancements.csv`, `Datasheets_options.csv` |
| HTML entities | `Datasheets.csv`, `Datasheets_wargear.csv` (`&#8217;`) |
| `<table>` and `<img>` in an ability | `Abilities.csv` (`A002`) |
| Unresolved `$` token | `Abilities.csv` (`A003`) |
| Cyrillic ability-type artefacts | `Datasheets_abilities.csv` — all three observed values |
| A record split across two physical lines by an unescaped newline | `Stratagems.csv` (`S002`, 6 pipes then 5 where 11 are required) |
| Free-text unit composition, including a line naming no model count | `Datasheets_unit_composition.csv` |
