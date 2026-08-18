<!-- AI-Assisted: Claude Code (model: claude-sonnet-5) - Generated for 008 T071/T072 preparation,
     following the Product Owner's 2026-08-17 decision to start override authoring against the
     corpus-complete residual. Text-free: datasheet id, row line ordinal, and the D1b/footnote-
     restriction-taxonomy diagnosis class only -- no source sentence, no item name, no count. Real
     entries (item names, counts, subject shape) require a human reading each source card and are
     the next action; this worklist is the structural preparation for that action, sourced live
     via the pipeline's own acquisition path (sitemap UNION curation/carried-forward-factions.json)
     and immediately discarded once classified. -->
# Override-candidate worklist (T071/T072 preparation, corpus-complete)

Measured against the near-corpus-complete build (29 of 30 factions by direct live fetch — the
carried-forward declaration's corrected slugs resolved the earlier partial-corpus run's slug
mismatches; the 5 remaining Space Marine chapter slugs still 404 direct and contribute zero
additional datasheets, since their content already arrives via the consolidated `space-marines`
page). Superseder of `reports/008-dryrun/2026-08-17.md`'s own 21/30-faction floor figures for
this specific worklist — see that file's "Addendum" section for the reconciled headline numbers.

60 datasheets carry at least one `OPT-UNPARSED` row (79 rows total, 2422-row corpus). Two
populations, disjoint:

## Permanently refused — 34 datasheets, never override-eligible (FR-006)

Every remaining unparsed row on these datasheets classifies
`refused_conditional_or_equipment_qualified`: an availability predicate or an equipment
qualification, not a structure the grammar or an override may resolve without publishing a
permission the source does not grant. These stay `partial` for the life of this feature —
correct, not a gap.

`adepta-sororitas:Canoness` (3, 4), `adepta-sororitas:Celestian-Insidiants` (6),
`aeldari:Corsair-Voidreavers` (5), `aeldari:Corsair-Voidscarred` (5, 6, 7), `aeldari:Dire-Avengers`
(2), `aeldari:Troupe` (3, 4), `astra-militarum:Catachan-Command-Squad` (2, 3),
`astra-militarum:Ratlings` (1, 2, 3), `chaos-daemons:Raptors` (7), `chaos-space-marines:Helbrute`
(3), `chaos-space-marines:Plague-Marines` (8), `chaos-space-marines:Raptors` (7),
`death-guard:Blightlord-Terminators` (6), `death-guard:Helbrute` (4), `death-guard:Plague-Marines`
(8), `drukhari:Corsair-Voidreavers` (5), `drukhari:Corsair-Voidscarred` (5, 6, 7),
`drukhari:Hellions` (3), `drukhari:Troupe` (3, 4), `genestealer-cults:Catachan-Command-Squad` (2,
3), `genestealer-cults:Neophyte-Hybrids` (1), `imperial-agents:Inquisitor` (3),
`imperial-agents:Inquisitor-In-Terminator-Armour` (3, 4), `imperial-agents:Spectrus-Kill-Team` (1,
2), `necrons:Overlord` (2), `space-marines:Captain-With-Jump-Pack` (4), `space-marines:Execrator`
(2), `space-marines:Reiver-Squad` (2), `space-marines:Spectrus-Kill-Team` (1),
`space-marines:Wolf-Scouts-1` (4), `space-marines:Wulfen-Dreadnought-1` (2),
`t-au-empire:Vespid-Stingwings` (1), `thousand-sons:Helbrute` (3), `world-eaters:Helbrute` (3).

## Override-addressable — 26 datasheets, 30 rows — T071/T072's real target

Every row here classifies `head_ok_no_verb` or `no_head_match` (occasionally alongside a
`refused_conditional_or_equipment_qualified` row on the *same* datasheet — that row stays refused
even after the others are closed). A curator opens the source card at the named line and authors a
`curation/option-overrides.json` entry with the item(s) the row actually states.

| Datasheet | Lines | Diagnosis |
|---|---|---|
| `aeldari:War-Walkers` | 1 | no_head_match |
| `aeldari:Wraithblades` | 1 | no_head_match |
| `aeldari:Wraithguard` | 1 | no_head_match |
| `astra-militarum:Cadian-Recon-Squad` | 3, 4, 5 | no_head_match + refused (line-specific) |
| `astra-militarum:Tempestus-Aquilons` | 7 | no_head_match |
| `chaos-daemons:Renegade-Heavy-Weapons-Squad` | 1 | no_head_match |
| `chaos-knights:Renegade-Heavy-Weapons-Squad` | 1 | no_head_match |
| `chaos-space-marines:Nemesis-Claw` | 4, 6 | no_head_match + refused (line-specific) |
| `chaos-space-marines:Red-Corsairs-Raiders` | 2 | head_ok_no_verb |
| `chaos-space-marines:Renegade-Heavy-Weapons-Squad` | 1 | no_head_match |
| `drukhari:Ravager` | 1 | no_head_match |
| `drukhari:Talos` | 2, 3 | head_ok_no_verb |
| `drukhari:Wracks` | 1, 3 | head_ok_no_verb + refused (line-specific) |
| `orks:Grot-Tanks` | 2 | no_head_match |
| `space-marines:Assault-Squad` | 3 | head_ok_no_verb |
| `space-marines:Assault-Squad-with-Jump-Packs` | 3 | head_ok_no_verb |
| `space-marines:Deathwing-Knights` | 2 | no_head_match |
| `space-marines:Desolation-Squad` | 1 | no_head_match |
| `space-marines:Eliminator-Squad` | 2 | no_head_match |
| `space-marines:Long-Fangs` | 2 | head_ok_no_verb |
| `space-marines:Stormwolf` | 1 | head_ok_no_verb |
| `space-marines:Tarantula-Sentry-Battery` | 1 | head_ok_no_verb |
| `space-marines:Techmarine-on-Bike` | 3 | head_ok_no_verb |
| `space-marines:Vanguard-Veteran-Squad` | 1 | head_ok_no_verb |
| `space-marines:Vanguard-Veteran-Squad-With-Jump-Packs` | 1, 2 | head_ok_no_verb + no_head_match |
| `space-marines:Wolf-Guard-Headtakers` | 1 | no_head_match |

**Where a row on a partly-addressable datasheet carries `refused_conditional_or_equipment_qualified`
alongside an addressable one** (`astra-militarum:Cadian-Recon-Squad`, `chaos-space-marines:Nemesis-Claw`,
`drukhari:Wracks`), only the addressable line(s) are override candidates — the conditional line
stays refused even once the others close, so the datasheet moves `partial` (some-group) rather than
fully `extracted` from this override authoring alone.

**This closes 26 of the 37-datasheet gap** between this build's own measured
`loadout.options_resolved` (1,992/2,084) and the restated SC-002 ceiling (2,029/2,084) — the
remainder is accounted for by datasheets whose `options_resolved` flag depends on more than the
option rows alone (equipment/item-constraint state on the same datasheet).

**No item name, count, or source sentence appears anywhere above.** Authoring the 30 real entries
(subject, item name(s), count where stated) is a human action against the live source card,
packaged for Product Owner review before `curation/option-overrides.json` gains them and before
T080's merge — not performed in this pass.
