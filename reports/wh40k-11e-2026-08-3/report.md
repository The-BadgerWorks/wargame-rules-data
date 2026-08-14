# Validation report — wh40k-11e-2026-08-3

**ADVISORY ONLY** — eligible for publication pending approval.

Run `local-wh40k-11e-2026-08-3` on the `prerelease` channel, 2026-08-14T00:00:00Z.

## Scale

| category | count | proportion of the snapshot |
|---|---|---|
| composition resolved | 2064 | 99.0% |
| escalating price datasheets | 535 | 25.7% |
| hybrid edition | 0 | 0.0% |
| keyword classification | 1371 | 98.7% |
| summaries outstanding | 0 | 0.0% |
| unlinked choices | 1766 | 84.7% |
| unparsed option rows | 256 | 12.3% |
| unverified pricing | 647 | 31.1% |
| wargear options resolved | 1916 | 91.9% |
| weapon ability keywords | 7959 | 70.8% |

## Coverage against the previous published version

| category | current | previous | ratio | threshold |
|---|---|---|---|---|
| composition | 2064 | 2064 | 100.0% | 90.0% |
| datasheets | 2084 | 2084 | 100.0% | 90.0% |
| factions | 30 | 30 | 100.0% | 95.0% |
| keyword classification | 1371 | 1371 | 100.0% | 95.0% |
| loadout.default equipment | 2017 | 2017 | 97.0% | 0.0% |
| loadout.options resolved | 1916 | 1916 | 92.0% | 92.0% |
| priced datasheets | 2084 | 2084 | 100.0% | 90.0% |
| summaries.abilities | 1941 | 1941 | 100.0% | 100.0% |
| summaries.detachment rules | 324 | 324 | 100.0% | 100.0% |
| summaries.faction rules | 28 | 28 | 100.0% | 100.0% |
| summaries.glossary | 70 | 70 | 5.0% | 5.0% |
| wargear options | 1916 | 1916 | 100.0% | 90.0% |

## Blocking findings

None.

## All findings

0 blocking, 9019 advisory, 1 suppressed.

<details><summary>coverage (18)</summary>

| code | severity | entities | resolved |
|---|---|---|---|
| `KWD-UNCLASSIFIED` | advisory | `keyword:ADEPTUS ASTARTES` | — |
| `KWD-UNCLASSIFIED` | advisory | `keyword:ADEPTUS TITANICUS` | — |
| `KWD-UNCLASSIFIED` | advisory | `keyword:AGENTS OF THE IMPERIUM` | — |
| `KWD-UNCLASSIFIED` | advisory | `keyword:ASURYANI` | — |
| `KWD-UNCLASSIFIED` | advisory | `keyword:BLOOD LEGIONS` | — |
| `KWD-UNCLASSIFIED` | advisory | `keyword:HARLEQUINS` | — |
| `KWD-UNCLASSIFIED` | advisory | `keyword:HERETIC ASTARTES` | — |
| `KWD-UNCLASSIFIED` | advisory | `keyword:IMPERIAL FISTS` | — |
| `KWD-UNCLASSIFIED` | advisory | `keyword:IRON HANDS` | — |
| `KWD-UNCLASSIFIED` | advisory | `keyword:LEGIONES DAEMONICA` | — |
| `KWD-UNCLASSIFIED` | advisory | `keyword:LEGIONS OF EXCESS` | — |
| `KWD-UNCLASSIFIED` | advisory | `keyword:PLAGUE LEGIONS` | — |
| `KWD-UNCLASSIFIED` | advisory | `keyword:RAVEN GUARD` | — |
| `KWD-UNCLASSIFIED` | advisory | `keyword:SALAMANDERS` | — |
| `KWD-UNCLASSIFIED` | advisory | `keyword:SCINTILLATING LEGIONS` | — |
| `KWD-UNCLASSIFIED` | advisory | `keyword:ULTRAMARINES` | — |
| `KWD-UNCLASSIFIED` | advisory | `keyword:WHITE SCARS` | — |
| `KWD-UNCLASSIFIED` | advisory | `keyword:YNNARI` | — |

</details>

<details><summary>data_quality (474)</summary>

| code | severity | entities | resolved |
|---|---|---|---|
| `CHG-DELTA-DISAGREEMENT` | advisory | `ds-sisters-of-battle-immolator` | — |
| `CMP-UNRESOLVED` | advisory | `ds-cadian-shock-troops` | — |
| `CMP-UNRESOLVED` | advisory | `ds-cadian-shock-troops` | — |
| `CMP-UNRESOLVED` | advisory | `ds-cadian-shock-troops-2` | — |
| `CMP-UNRESOLVED` | advisory | `ds-cadian-shock-troops-2` | — |
| `CMP-UNRESOLVED` | advisory | `ds-catachan-jungle-fighters` | — |
| `CMP-UNRESOLVED` | advisory | `ds-catachan-jungle-fighters` | — |
| `CMP-UNRESOLVED` | advisory | `ds-catachan-jungle-fighters-2` | — |
| `CMP-UNRESOLVED` | advisory | `ds-catachan-jungle-fighters-2` | — |
| `CMP-UNRESOLVED` | advisory | `ds-death-korps-grenadier-squad` | — |
| `CMP-UNRESOLVED` | advisory | `ds-death-korps-grenadier-squad` | — |
| `CMP-UNRESOLVED` | advisory | `ds-death-korps-grenadier-squad-2` | — |
| `CMP-UNRESOLVED` | advisory | `ds-death-korps-grenadier-squad-2` | — |
| `CMP-UNRESOLVED` | advisory | `ds-death-korps-of-krieg` | — |
| `CMP-UNRESOLVED` | advisory | `ds-death-korps-of-krieg` | — |
| `CMP-UNRESOLVED` | advisory | `ds-death-korps-of-krieg-2` | — |
| `CMP-UNRESOLVED` | advisory | `ds-death-korps-of-krieg-2` | — |
| `CMP-UNRESOLVED` | advisory | `ds-gretchin` | — |
| `CMP-UNRESOLVED` | advisory | `ds-gretchin` | — |
| `CMP-UNRESOLVED` | advisory | `ds-jakhals` | — |
| `CMP-UNRESOLVED` | advisory | `ds-jakhals` | — |
| `CMP-UNRESOLVED` | advisory | `ds-kill-team-cassius` | — |
| `CMP-UNRESOLVED` | advisory | `ds-kill-team-cassius-2` | — |
| `CMP-UNRESOLVED` | advisory | `ds-regimental-attaches` | — |
| `CMP-UNRESOLVED` | advisory | `ds-regimental-attaches-2` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:adeptus-custodes:Ares-Gunship` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:adeptus-mechanicus:Archaeopter-Fusilave` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:adeptus-mechanicus:Archaeopter-Stratoraptor` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:aeldari:Crimson-Hunter` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:aeldari:Hemlock-Wraithfighter` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:aeldari:Nightwing` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:aeldari:Phoenix` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:aeldari:Vampire-Hunter` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:aeldari:Vampire-Raider` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:astra-militarum:Marauder-Bomber` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:astra-militarum:Marauder-Destroyer` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:astra-militarum:Valkyrie` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:astra-militarum:Voss-pattern-Lightning` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:chaos-space-marines:Chaos-Thunderhawk` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:chaos-space-marines:Fire-Raptor-Gunship` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:chaos-space-marines:Heldrake` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:chaos-space-marines:Hell-Blade` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:chaos-space-marines:Hell-Talon` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:chaos-space-marines:Storm-Eagle-Gunship` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:chaos-space-marines:Xiphon-Interceptor` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:death-guard:Chaos-Thunderhawk` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:death-guard:Fire-Raptor-Gunship` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:death-guard:Hell-Blade` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:death-guard:Hell-Talon` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:death-guard:Storm-Eagle-Gunship` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:death-guard:Xiphon-Interceptor` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:drukhari:Razorwing-Jetfighter` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:drukhari:Voidraven-Bomber` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:emperor-s-children:Heldrake` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:grey-knights:Stormhawk-Interceptor` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:grey-knights:Stormtalon-Gunship` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:necrons:Doom-Scythe` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:necrons:Night-Shroud` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:orks:Blitza-bommer` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:orks:Burna-bommer` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:orks:Dakkajet` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:orks:Wazbom-Blastajet` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:space-marines:Fire-Raptor-Gunship` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:space-marines:Nephilim-Jetfighter` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:space-marines:Ravenwing-Dark-Talon` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:space-marines:Storm-Eagle-Gunship` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:space-marines:Stormfang-Gunship` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:space-marines:Stormhawk-Interceptor` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:space-marines:Stormhawk-Interceptor` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:space-marines:Stormhawk-Interceptor` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:space-marines:Stormhawk-Interceptor` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:space-marines:Stormhawk-Interceptor` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:space-marines:Stormhawk-Interceptor` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:space-marines:Stormtalon-Gunship` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:space-marines:Stormtalon-Gunship` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:space-marines:Stormtalon-Gunship` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:space-marines:Stormtalon-Gunship` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:space-marines:Stormtalon-Gunship` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:space-marines:Stormtalon-Gunship` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:space-marines:Stormwolf` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:space-marines:Xiphon-Interceptor` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:t-au-empire:AX-1-0-Tiger-Shark` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:t-au-empire:Barracuda` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:t-au-empire:Manta` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:t-au-empire:Orca-Dropship` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:t-au-empire:Razorshark-Strike-Fighter` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:t-au-empire:Sun-Shark-Bomber` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:t-au-empire:Tiger-Shark` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:thousand-sons:Chaos-Thunderhawk` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:thousand-sons:Fire-Raptor-Gunship` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:thousand-sons:Heldrake` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:thousand-sons:Hell-Blade` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:thousand-sons:Hell-Talon` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:thousand-sons:Storm-Eagle-Gunship` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:thousand-sons:Xiphon-Interceptor` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:tyranids:Harpy` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:tyranids:Hive-Crone` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:world-eaters:Chaos-Thunderhawk` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:world-eaters:Fire-Raptor-Gunship` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:world-eaters:Heldrake` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:world-eaters:Hell-Blade` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:world-eaters:Hell-Talon` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:world-eaters:Storm-Eagle-Gunship` | — |
| `DQ-MALFORMED-ROW` | advisory | `wahapedia:world-eaters:Xiphon-Interceptor` | — |
| `EQP-UNPARSED` | advisory | `ds-aquila-kill-team` | — |
| `EQP-UNPARSED` | advisory | `ds-aquila-kill-team` | — |
| `EQP-UNPARSED` | advisory | `ds-aquila-kill-team` | — |
| `EQP-UNPARSED` | advisory | `ds-aquila-kill-team` | — |
| `EQP-UNPARSED` | advisory | `ds-bike-squad` | — |
| `EQP-UNPARSED` | advisory | `ds-brokhyr-iron-master` | — |
| `EQP-UNPARSED` | advisory | `ds-brokhyr-iron-master` | — |
| `EQP-UNPARSED` | advisory | `ds-brokhyr-iron-master` | — |
| `EQP-UNPARSED` | advisory | `ds-cadian-command-squad` | — |
| `EQP-UNPARSED` | advisory | `ds-cadian-command-squad` | — |
| `EQP-UNPARSED` | advisory | `ds-cadian-command-squad` | — |
| `EQP-UNPARSED` | advisory | `ds-cadian-command-squad` | — |
| `EQP-UNPARSED` | advisory | `ds-cadian-command-squad-2` | — |
| `EQP-UNPARSED` | advisory | `ds-cadian-command-squad-2` | — |
| `EQP-UNPARSED` | advisory | `ds-cadian-command-squad-2` | — |
| `EQP-UNPARSED` | advisory | `ds-cadian-command-squad-2` | — |
| `EQP-UNPARSED` | advisory | `ds-company-heroes` | — |
| `EQP-UNPARSED` | advisory | `ds-company-heroes` | — |
| `EQP-UNPARSED` | advisory | `ds-company-heroes-2` | — |
| `EQP-UNPARSED` | advisory | `ds-company-heroes-2` | — |
| `EQP-UNPARSED` | advisory | `ds-company-heroes-3` | — |
| `EQP-UNPARSED` | advisory | `ds-company-heroes-3` | — |
| `EQP-UNPARSED` | advisory | `ds-company-heroes-4` | — |
| `EQP-UNPARSED` | advisory | `ds-company-heroes-4` | — |
| `EQP-UNPARSED` | advisory | `ds-company-heroes-5` | — |
| `EQP-UNPARSED` | advisory | `ds-company-heroes-5` | — |
| `EQP-UNPARSED` | advisory | `ds-company-heroes-6` | — |
| `EQP-UNPARSED` | advisory | `ds-company-heroes-6` | — |
| `EQP-UNPARSED` | advisory | `ds-corsair-voidscarred` | — |
| `EQP-UNPARSED` | advisory | `ds-corsair-voidscarred` | — |
| `EQP-UNPARSED` | advisory | `ds-corsair-voidscarred` | — |
| `EQP-UNPARSED` | advisory | `ds-corsair-voidscarred-2` | — |
| `EQP-UNPARSED` | advisory | `ds-corsair-voidscarred-2` | — |
| `EQP-UNPARSED` | advisory | `ds-corsair-voidscarred-2` | — |
| `EQP-UNPARSED` | advisory | `ds-court-of-the-archon` | — |
| `EQP-UNPARSED` | advisory | `ds-court-of-the-archon` | — |
| `EQP-UNPARSED` | advisory | `ds-court-of-the-archon` | — |
| `EQP-UNPARSED` | advisory | `ds-court-of-the-archon` | — |
| `EQP-UNPARSED` | advisory | `ds-decimus-kill-team` | — |
| `EQP-UNPARSED` | advisory | `ds-decimus-kill-team` | — |
| `EQP-UNPARSED` | advisory | `ds-decimus-kill-team` | — |
| `EQP-UNPARSED` | advisory | `ds-decimus-kill-team` | — |
| `EQP-UNPARSED` | advisory | `ds-fortis-kill-team` | — |
| `EQP-UNPARSED` | advisory | `ds-fortis-kill-team` | — |
| `EQP-UNPARSED` | advisory | `ds-fortis-kill-team` | — |
| `EQP-UNPARSED` | advisory | `ds-fortis-kill-team` | — |
| `EQP-UNPARSED` | advisory | `ds-fortis-kill-team-2` | — |
| `EQP-UNPARSED` | advisory | `ds-fortis-kill-team-2` | — |
| `EQP-UNPARSED` | advisory | `ds-gaunts-ghosts` | — |
| `EQP-UNPARSED` | advisory | `ds-gaunts-ghosts` | — |
| `EQP-UNPARSED` | advisory | `ds-gaunts-ghosts` | — |
| `EQP-UNPARSED` | advisory | `ds-gaunts-ghosts` | — |
| `EQP-UNPARSED` | advisory | `ds-gaunts-ghosts` | — |
| `EQP-UNPARSED` | advisory | `ds-gellerpox-infected` | — |
| `EQP-UNPARSED` | advisory | `ds-gellerpox-infected-2` | — |
| `EQP-UNPARSED` | advisory | `ds-gellerpox-infected-3` | — |
| `EQP-UNPARSED` | advisory | `ds-gellerpox-infected-4` | — |
| `EQP-UNPARSED` | advisory | `ds-havocs` | — |
| `EQP-UNPARSED` | advisory | `ds-havocs` | — |
| `EQP-UNPARSED` | advisory | `ds-havocs-2` | — |
| `EQP-UNPARSED` | advisory | `ds-havocs-2` | — |
| `EQP-UNPARSED` | advisory | `ds-hells-last` | — |
| `EQP-UNPARSED` | advisory | `ds-hells-last` | — |
| `EQP-UNPARSED` | advisory | `ds-hells-last` | — |
| `EQP-UNPARSED` | advisory | `ds-hells-last` | — |
| `EQP-UNPARSED` | advisory | `ds-hells-last-2` | — |
| `EQP-UNPARSED` | advisory | `ds-hells-last-2` | — |
| `EQP-UNPARSED` | advisory | `ds-hells-last-2` | — |
| `EQP-UNPARSED` | advisory | `ds-hells-last-2` | — |
| `EQP-UNPARSED` | advisory | `ds-hyperadapted-raveners` | — |
| `EQP-UNPARSED` | advisory | `ds-hyperadapted-raveners` | — |
| `EQP-UNPARSED` | advisory | `ds-hyperadapted-raveners-2` | — |
| `EQP-UNPARSED` | advisory | `ds-hyperadapted-raveners-2` | — |
| `EQP-UNPARSED` | advisory | `ds-imperial-navy-breachers` | — |
| `EQP-UNPARSED` | advisory | `ds-imperial-navy-breachers` | — |
| `EQP-UNPARSED` | advisory | `ds-indomitor-kill-team` | — |
| `EQP-UNPARSED` | advisory | `ds-indomitor-kill-team` | — |
| `EQP-UNPARSED` | advisory | `ds-indomitor-kill-team-2` | — |
| `EQP-UNPARSED` | advisory | `ds-indomitor-kill-team-2` | — |
| `EQP-UNPARSED` | advisory | `ds-indomitor-kill-team-2` | — |
| `EQP-UNPARSED` | advisory | `ds-krieg-command-squad` | — |
| `EQP-UNPARSED` | advisory | `ds-krieg-command-squad` | — |
| `EQP-UNPARSED` | advisory | `ds-krieg-command-squad` | — |
| `EQP-UNPARSED` | advisory | `ds-krieg-command-squad` | — |
| `EQP-UNPARSED` | advisory | `ds-krieg-command-squad` | — |
| `EQP-UNPARSED` | advisory | `ds-krieg-command-squad-2` | — |
| `EQP-UNPARSED` | advisory | `ds-krieg-command-squad-2` | — |
| `EQP-UNPARSED` | advisory | `ds-krieg-command-squad-2` | — |
| `EQP-UNPARSED` | advisory | `ds-krieg-command-squad-2` | — |
| `EQP-UNPARSED` | advisory | `ds-krieg-command-squad-2` | — |
| `EQP-UNPARSED` | advisory | `ds-outrider-squad` | — |
| `EQP-UNPARSED` | advisory | `ds-outrider-squad-2` | — |
| `EQP-UNPARSED` | advisory | `ds-outrider-squad-3` | — |
| `EQP-UNPARSED` | advisory | `ds-outrider-squad-4` | — |
| `EQP-UNPARSED` | advisory | `ds-outrider-squad-5` | — |
| `EQP-UNPARSED` | advisory | `ds-outrider-squad-6` | — |
| `EQP-UNPARSED` | advisory | `ds-proteus-kill-team` | — |
| `EQP-UNPARSED` | advisory | `ds-sanctifiers` | — |
| `EQP-UNPARSED` | advisory | `ds-sanctifiers` | — |
| `EQP-UNPARSED` | advisory | `ds-sanctifiers-2` | — |
| `EQP-UNPARSED` | advisory | `ds-sanctifiers-2` | — |
| `EQP-UNPARSED` | advisory | `ds-servitor-battleclade` | — |
| `EQP-UNPARSED` | advisory | `ds-servitor-battleclade` | — |
| `EQP-UNPARSED` | advisory | `ds-spectrus-kill-team` | — |
| `EQP-UNPARSED` | advisory | `ds-spectrus-kill-team` | — |
| `EQP-UNPARSED` | advisory | `ds-spectrus-kill-team` | — |
| `EQP-UNPARSED` | advisory | `ds-spectrus-kill-team-2` | — |
| `EQP-UNPARSED` | advisory | `ds-spectrus-kill-team-2` | — |
| `EQP-UNPARSED` | advisory | `ds-spectrus-kill-team-2` | — |
| `EQP-UNPARSED` | advisory | `ds-spectrus-kill-team-2` | — |
| `EQP-UNPARSED` | advisory | `ds-talonstrike-kill-team` | — |
| `EQP-UNPARSED` | advisory | `ds-talonstrike-kill-team` | — |
| `EQP-UNPARSED` | advisory | `ds-talonstrike-kill-team` | — |
| `EQP-UNPARSED` | advisory | `ds-voidsmen-at-arms` | — |
| `OPT-UNPARSED` | advisory | `ds-armoured-sentinels` | — |
| `OPT-UNPARSED` | advisory | `ds-armoured-sentinels` | — |
| `OPT-UNPARSED` | advisory | `ds-armoured-sentinels-2` | — |
| `OPT-UNPARSED` | advisory | `ds-armoured-sentinels-2` | — |
| `OPT-UNPARSED` | advisory | `ds-assault-squad` | — |
| `OPT-UNPARSED` | advisory | `ds-assault-squad-with-jump-packs` | — |
| `OPT-UNPARSED` | advisory | `ds-atalan-jackals` | — |
| `OPT-UNPARSED` | advisory | `ds-blightlord-terminators` | — |
| `OPT-UNPARSED` | advisory | `ds-blightlord-terminators` | — |
| `OPT-UNPARSED` | advisory | `ds-boyz` | — |
| `OPT-UNPARSED` | advisory | `ds-boyz` | — |
| `OPT-UNPARSED` | advisory | `ds-boyz` | — |
| `OPT-UNPARSED` | advisory | `ds-broadside-battlesuits` | — |
| `OPT-UNPARSED` | advisory | `ds-broadside-battlesuits` | — |
| `OPT-UNPARSED` | advisory | `ds-brotherhood-terminator-squad` | — |
| `OPT-UNPARSED` | advisory | `ds-cadian-recon-squad` | — |
| `OPT-UNPARSED` | advisory | `ds-cadian-recon-squad` | — |
| `OPT-UNPARSED` | advisory | `ds-cadian-recon-squad` | — |
| `OPT-UNPARSED` | advisory | `ds-cadian-recon-squad` | — |
| `OPT-UNPARSED` | advisory | `ds-cadian-recon-squad` | — |
| `OPT-UNPARSED` | advisory | `ds-canoness` | — |
| `OPT-UNPARSED` | advisory | `ds-canoness` | — |
| `OPT-UNPARSED` | advisory | `ds-canoptek-spyders` | — |
| `OPT-UNPARSED` | advisory | `ds-canoptek-spyders` | — |
| `OPT-UNPARSED` | advisory | `ds-canoptek-spyders` | — |
| `OPT-UNPARSED` | advisory | `ds-canoptek-wraiths` | — |
| `OPT-UNPARSED` | advisory | `ds-captain-with-jump-pack` | — |
| `OPT-UNPARSED` | advisory | `ds-captain-with-jump-pack-2` | — |
| `OPT-UNPARSED` | advisory | `ds-captain-with-jump-pack-3` | — |
| `OPT-UNPARSED` | advisory | `ds-captain-with-jump-pack-4` | — |
| `OPT-UNPARSED` | advisory | `ds-captain-with-jump-pack-5` | — |
| `OPT-UNPARSED` | advisory | `ds-captain-with-jump-pack-6` | — |
| `OPT-UNPARSED` | advisory | `ds-carnifexes` | — |
| `OPT-UNPARSED` | advisory | `ds-carnifexes` | — |
| `OPT-UNPARSED` | advisory | `ds-catachan-command-squad` | — |
| `OPT-UNPARSED` | advisory | `ds-catachan-command-squad` | — |
| `OPT-UNPARSED` | advisory | `ds-catachan-command-squad-2` | — |
| `OPT-UNPARSED` | advisory | `ds-catachan-command-squad-2` | — |
| `OPT-UNPARSED` | advisory | `ds-celestian-insidiants` | — |
| `OPT-UNPARSED` | advisory | `ds-chaos-acastus-knight-porphyrion` | — |
| `OPT-UNPARSED` | advisory | `ds-chosen` | — |
| `OPT-UNPARSED` | advisory | `ds-chosen-2` | — |
| `OPT-UNPARSED` | advisory | `ds-company-veterans-on-bikes` | — |
| `OPT-UNPARSED` | advisory | `ds-company-veterans-on-bikes` | — |
| `OPT-UNPARSED` | advisory | `ds-corsair-skyreavers` | — |
| `OPT-UNPARSED` | advisory | `ds-corsair-skyreavers-2` | — |
| `OPT-UNPARSED` | advisory | `ds-corsair-voidreavers` | — |
| `OPT-UNPARSED` | advisory | `ds-corsair-voidreavers-2` | — |
| `OPT-UNPARSED` | advisory | `ds-corsair-voidscarred` | — |
| `OPT-UNPARSED` | advisory | `ds-corsair-voidscarred` | — |
| `OPT-UNPARSED` | advisory | `ds-corsair-voidscarred` | — |
| `OPT-UNPARSED` | advisory | `ds-corsair-voidscarred-2` | — |
| `OPT-UNPARSED` | advisory | `ds-corsair-voidscarred-2` | — |
| `OPT-UNPARSED` | advisory | `ds-corsair-voidscarred-2` | — |
| `OPT-UNPARSED` | advisory | `ds-crisis-battlesuits` | — |
| `OPT-UNPARSED` | advisory | `ds-cronos` | — |
| `OPT-UNPARSED` | advisory | `ds-cthonian-beserks` | — |
| `OPT-UNPARSED` | advisory | `ds-dark-reapers` | — |
| `OPT-UNPARSED` | advisory | `ds-death-korps-of-krieg` | — |
| `OPT-UNPARSED` | advisory | `ds-death-korps-of-krieg` | — |
| `OPT-UNPARSED` | advisory | `ds-death-korps-of-krieg` | — |
| `OPT-UNPARSED` | advisory | `ds-death-korps-of-krieg-2` | — |
| `OPT-UNPARSED` | advisory | `ds-death-korps-of-krieg-2` | — |
| `OPT-UNPARSED` | advisory | `ds-death-korps-of-krieg-2` | — |
| `OPT-UNPARSED` | advisory | `ds-deathwatch-kill-team` | — |
| `OPT-UNPARSED` | advisory | `ds-deathwatch-kill-team` | — |
| `OPT-UNPARSED` | advisory | `ds-deathwatch-kill-team` | — |
| `OPT-UNPARSED` | advisory | `ds-deathwatch-veterans` | — |
| `OPT-UNPARSED` | advisory | `ds-deathwatch-veterans` | — |
| `OPT-UNPARSED` | advisory | `ds-deathwatch-veterans` | — |
| `OPT-UNPARSED` | advisory | `ds-deathwing-command-squad` | — |
| `OPT-UNPARSED` | advisory | `ds-deathwing-knights` | — |
| `OPT-UNPARSED` | advisory | `ds-deathwing-terminator-squad` | — |
| `OPT-UNPARSED` | advisory | `ds-deff-dread` | — |
| `OPT-UNPARSED` | advisory | `ds-deff-dread` | — |
| `OPT-UNPARSED` | advisory | `ds-deffkoptas` | — |
| `OPT-UNPARSED` | advisory | `ds-deffkoptas-with-big-shootas` | — |
| `OPT-UNPARSED` | advisory | `ds-desolation-squad` | — |
| `OPT-UNPARSED` | advisory | `ds-desolation-squad-2` | — |
| `OPT-UNPARSED` | advisory | `ds-desolation-squad-3` | — |
| `OPT-UNPARSED` | advisory | `ds-desolation-squad-4` | — |
| `OPT-UNPARSED` | advisory | `ds-desolation-squad-5` | — |
| `OPT-UNPARSED` | advisory | `ds-desolation-squad-6` | — |
| `OPT-UNPARSED` | advisory | `ds-dire-avengers` | — |
| `OPT-UNPARSED` | advisory | `ds-dire-avengers` | — |
| `OPT-UNPARSED` | advisory | `ds-eliminator-squad` | — |
| `OPT-UNPARSED` | advisory | `ds-eliminator-squad-2` | — |
| `OPT-UNPARSED` | advisory | `ds-eliminator-squad-3` | — |
| `OPT-UNPARSED` | advisory | `ds-eliminator-squad-4` | — |
| `OPT-UNPARSED` | advisory | `ds-eliminator-squad-5` | — |
| `OPT-UNPARSED` | advisory | `ds-eliminator-squad-6` | — |
| `OPT-UNPARSED` | advisory | `ds-execrator` | — |
| `OPT-UNPARSED` | advisory | `ds-fire-dragons` | — |
| `OPT-UNPARSED` | advisory | `ds-fortis-kill-team` | — |
| `OPT-UNPARSED` | advisory | `ds-fortis-kill-team` | — |
| `OPT-UNPARSED` | advisory | `ds-fortis-kill-team` | — |
| `OPT-UNPARSED` | advisory | `ds-fortis-kill-team` | — |
| `OPT-UNPARSED` | advisory | `ds-fortis-kill-team` | — |
| `OPT-UNPARSED` | advisory | `ds-fortis-kill-team-2` | — |
| `OPT-UNPARSED` | advisory | `ds-grey-knights-terminator-squad` | — |
| `OPT-UNPARSED` | advisory | `ds-griffon-mortar-carrier` | — |
| `OPT-UNPARSED` | advisory | `ds-griffon-mortar-carrier-2` | — |
| `OPT-UNPARSED` | advisory | `ds-grot-tanks` | — |
| `OPT-UNPARSED` | advisory | `ds-grotesques` | — |
| `OPT-UNPARSED` | advisory | `ds-helbrute` | — |
| `OPT-UNPARSED` | advisory | `ds-helbrute-2` | — |
| `OPT-UNPARSED` | advisory | `ds-helbrute-3` | — |
| `OPT-UNPARSED` | advisory | `ds-helbrute-4` | — |
| `OPT-UNPARSED` | advisory | `ds-hellions` | — |
| `OPT-UNPARSED` | advisory | `ds-hernkyn-yaegirs` | — |
| `OPT-UNPARSED` | advisory | `ds-hernkyn-yaegirs` | — |
| `OPT-UNPARSED` | advisory | `ds-howling-banshees` | — |
| `OPT-UNPARSED` | advisory | `ds-indomitor-kill-team` | — |
| `OPT-UNPARSED` | advisory | `ds-indomitor-kill-team` | — |
| `OPT-UNPARSED` | advisory | `ds-indomitor-kill-team-2` | — |
| `OPT-UNPARSED` | advisory | `ds-indomitor-kill-team-2` | — |
| `OPT-UNPARSED` | advisory | `ds-inquisitor` | — |
| `OPT-UNPARSED` | advisory | `ds-inquisitor-in-terminator-armour` | — |
| `OPT-UNPARSED` | advisory | `ds-inquisitor-in-terminator-armour` | — |
| `OPT-UNPARSED` | advisory | `ds-kapricus-defenders` | — |
| `OPT-UNPARSED` | advisory | `ds-krieg-command-squad` | — |
| `OPT-UNPARSED` | advisory | `ds-krieg-command-squad-2` | — |
| `OPT-UNPARSED` | advisory | `ds-land-speeder` | — |
| `OPT-UNPARSED` | advisory | `ds-land-speeder-2` | — |
| `OPT-UNPARSED` | advisory | `ds-land-speeder-3` | — |
| `OPT-UNPARSED` | advisory | `ds-land-speeder-4` | — |
| `OPT-UNPARSED` | advisory | `ds-land-speeder-5` | — |
| `OPT-UNPARSED` | advisory | `ds-land-speeder-6` | — |
| `OPT-UNPARSED` | advisory | `ds-long-fangs` | — |
| `OPT-UNPARSED` | advisory | `ds-nemesis-claw` | — |
| `OPT-UNPARSED` | advisory | `ds-nemesis-claw` | — |
| `OPT-UNPARSED` | advisory | `ds-neophyte-hybrids` | — |
| `OPT-UNPARSED` | advisory | `ds-nobz-on-warbikes` | — |
| `OPT-UNPARSED` | advisory | `ds-noise-marines` | — |
| `OPT-UNPARSED` | advisory | `ds-noise-marines-2` | — |
| `OPT-UNPARSED` | advisory | `ds-ophydian-destroyers` | — |
| `OPT-UNPARSED` | advisory | `ds-overlord` | — |
| `OPT-UNPARSED` | advisory | `ds-paladin-squad` | — |
| `OPT-UNPARSED` | advisory | `ds-piranhas` | — |
| `OPT-UNPARSED` | advisory | `ds-plague-marines` | — |
| `OPT-UNPARSED` | advisory | `ds-plague-marines-2` | — |
| `OPT-UNPARSED` | advisory | `ds-proteus-kill-team` | — |
| `OPT-UNPARSED` | advisory | `ds-proteus-kill-team` | — |
| `OPT-UNPARSED` | advisory | `ds-proteus-kill-team` | — |
| `OPT-UNPARSED` | advisory | `ds-proteus-kill-team` | — |
| `OPT-UNPARSED` | advisory | `ds-proteus-kill-team` | — |
| `OPT-UNPARSED` | advisory | `ds-raptors` | — |
| `OPT-UNPARSED` | advisory | `ds-raptors` | — |
| `OPT-UNPARSED` | advisory | `ds-raptors-2` | — |
| `OPT-UNPARSED` | advisory | `ds-raptors-2` | — |
| `OPT-UNPARSED` | advisory | `ds-ratlings` | — |
| `OPT-UNPARSED` | advisory | `ds-ratlings` | — |
| `OPT-UNPARSED` | advisory | `ds-ratlings` | — |
| `OPT-UNPARSED` | advisory | `ds-ravager` | — |
| `OPT-UNPARSED` | advisory | `ds-ravenwing-black-knights` | — |
| `OPT-UNPARSED` | advisory | `ds-red-corsairs-raiders` | — |
| `OPT-UNPARSED` | advisory | `ds-reiver-squad` | — |
| `OPT-UNPARSED` | advisory | `ds-reiver-squad` | — |
| `OPT-UNPARSED` | advisory | `ds-reiver-squad` | — |
| `OPT-UNPARSED` | advisory | `ds-reiver-squad-2` | — |
| `OPT-UNPARSED` | advisory | `ds-reiver-squad-2` | — |
| `OPT-UNPARSED` | advisory | `ds-reiver-squad-2` | — |
| `OPT-UNPARSED` | advisory | `ds-reiver-squad-3` | — |
| `OPT-UNPARSED` | advisory | `ds-reiver-squad-3` | — |
| `OPT-UNPARSED` | advisory | `ds-reiver-squad-3` | — |
| `OPT-UNPARSED` | advisory | `ds-reiver-squad-4` | — |
| `OPT-UNPARSED` | advisory | `ds-reiver-squad-4` | — |
| `OPT-UNPARSED` | advisory | `ds-reiver-squad-4` | — |
| `OPT-UNPARSED` | advisory | `ds-reiver-squad-5` | — |
| `OPT-UNPARSED` | advisory | `ds-reiver-squad-5` | — |
| `OPT-UNPARSED` | advisory | `ds-reiver-squad-5` | — |
| `OPT-UNPARSED` | advisory | `ds-reiver-squad-6` | — |
| `OPT-UNPARSED` | advisory | `ds-reiver-squad-6` | — |
| `OPT-UNPARSED` | advisory | `ds-reiver-squad-6` | — |
| `OPT-UNPARSED` | advisory | `ds-renegade-heavy-weapons-squad` | — |
| `OPT-UNPARSED` | advisory | `ds-renegade-heavy-weapons-squad-2` | — |
| `OPT-UNPARSED` | advisory | `ds-renegade-heavy-weapons-squad-3` | — |
| `OPT-UNPARSED` | advisory | `ds-ripper-swarms` | — |
| `OPT-UNPARSED` | advisory | `ds-sabre-weapons-battery` | — |
| `OPT-UNPARSED` | advisory | `ds-sabre-weapons-battery-2` | — |
| `OPT-UNPARSED` | advisory | `ds-sanctifiers` | — |
| `OPT-UNPARSED` | advisory | `ds-sanctifiers` | — |
| `OPT-UNPARSED` | advisory | `ds-sanctifiers` | — |
| `OPT-UNPARSED` | advisory | `ds-sanctifiers-2` | — |
| `OPT-UNPARSED` | advisory | `ds-sanctifiers-2` | — |
| `OPT-UNPARSED` | advisory | `ds-sanctifiers-2` | — |
| `OPT-UNPARSED` | advisory | `ds-scourges-with-heavy-weapons` | — |
| `OPT-UNPARSED` | advisory | `ds-scout-sentinels` | — |
| `OPT-UNPARSED` | advisory | `ds-scout-sentinels` | — |
| `OPT-UNPARSED` | advisory | `ds-scout-sentinels-2` | — |
| `OPT-UNPARSED` | advisory | `ds-scout-sentinels-2` | — |
| `OPT-UNPARSED` | advisory | `ds-servitor-battleclade` | — |
| `OPT-UNPARSED` | advisory | `ds-skorpekh-destroyers` | — |
| `OPT-UNPARSED` | advisory | `ds-sky-slasher-swarms` | — |
| `OPT-UNPARSED` | advisory | `ds-spectrus-kill-team` | — |
| `OPT-UNPARSED` | advisory | `ds-spectrus-kill-team` | — |
| `OPT-UNPARSED` | advisory | `ds-spectrus-kill-team` | — |
| `OPT-UNPARSED` | advisory | `ds-spectrus-kill-team` | — |
| `OPT-UNPARSED` | advisory | `ds-spectrus-kill-team-2` | — |
| `OPT-UNPARSED` | advisory | `ds-spectrus-kill-team-2` | — |
| `OPT-UNPARSED` | advisory | `ds-spectrus-kill-team-2` | — |
| `OPT-UNPARSED` | advisory | `ds-spectrus-kill-team-2` | — |
| `OPT-UNPARSED` | advisory | `ds-spectrus-kill-team-2` | — |
| `OPT-UNPARSED` | advisory | `ds-stormwolf` | — |
| `OPT-UNPARSED` | advisory | `ds-striking-scorpions` | — |
| `OPT-UNPARSED` | advisory | `ds-swooping-hawks` | — |
| `OPT-UNPARSED` | advisory | `ds-talonstrike-kill-team` | — |
| `OPT-UNPARSED` | advisory | `ds-talonstrike-kill-team` | — |
| `OPT-UNPARSED` | advisory | `ds-talonstrike-kill-team` | — |
| `OPT-UNPARSED` | advisory | `ds-talos` | — |
| `OPT-UNPARSED` | advisory | `ds-talos` | — |
| `OPT-UNPARSED` | advisory | `ds-talos` | — |
| `OPT-UNPARSED` | advisory | `ds-tarantula-sentry-battery` | — |
| `OPT-UNPARSED` | advisory | `ds-techmarine-on-bike` | — |
| `OPT-UNPARSED` | advisory | `ds-tempestus-aquilons` | — |
| `OPT-UNPARSED` | advisory | `ds-tomb-blades` | — |
| `OPT-UNPARSED` | advisory | `ds-tomb-blades` | — |
| `OPT-UNPARSED` | advisory | `ds-troupe` | — |
| `OPT-UNPARSED` | advisory | `ds-troupe` | — |
| `OPT-UNPARSED` | advisory | `ds-troupe-2` | — |
| `OPT-UNPARSED` | advisory | `ds-troupe-2` | — |
| `OPT-UNPARSED` | advisory | `ds-vanguard-veteran-squad` | — |
| `OPT-UNPARSED` | advisory | `ds-vanguard-veteran-squad-with-jump-packs` | — |
| `OPT-UNPARSED` | advisory | `ds-vanguard-veteran-squad-with-jump-packs` | — |
| `OPT-UNPARSED` | advisory | `ds-vanguard-veteran-squad-with-jump-packs` | — |
| `OPT-UNPARSED` | advisory | `ds-vanguard-veteran-squad-with-jump-packs-2` | — |
| `OPT-UNPARSED` | advisory | `ds-vanguard-veteran-squad-with-jump-packs-2` | — |
| `OPT-UNPARSED` | advisory | `ds-vanguard-veteran-squad-with-jump-packs-2` | — |
| `OPT-UNPARSED` | advisory | `ds-vanguard-veteran-squad-with-jump-packs-3` | — |
| `OPT-UNPARSED` | advisory | `ds-vanguard-veteran-squad-with-jump-packs-3` | — |
| `OPT-UNPARSED` | advisory | `ds-vanguard-veteran-squad-with-jump-packs-3` | — |
| `OPT-UNPARSED` | advisory | `ds-vanguard-veteran-squad-with-jump-packs-4` | — |
| `OPT-UNPARSED` | advisory | `ds-vanguard-veteran-squad-with-jump-packs-4` | — |
| `OPT-UNPARSED` | advisory | `ds-vanguard-veteran-squad-with-jump-packs-4` | — |
| `OPT-UNPARSED` | advisory | `ds-vanguard-veteran-squad-with-jump-packs-5` | — |
| `OPT-UNPARSED` | advisory | `ds-vanguard-veteran-squad-with-jump-packs-5` | — |
| `OPT-UNPARSED` | advisory | `ds-vanguard-veteran-squad-with-jump-packs-5` | — |
| `OPT-UNPARSED` | advisory | `ds-vanguard-veteran-squad-with-jump-packs-6` | — |
| `OPT-UNPARSED` | advisory | `ds-vanguard-veteran-squad-with-jump-packs-6` | — |
| `OPT-UNPARSED` | advisory | `ds-vanguard-veteran-squad-with-jump-packs-6` | — |
| `OPT-UNPARSED` | advisory | `ds-vespid-stingwings` | — |
| `OPT-UNPARSED` | advisory | `ds-veteran-bike-squad` | — |
| `OPT-UNPARSED` | advisory | `ds-war-walkers` | — |
| `OPT-UNPARSED` | advisory | `ds-warboss` | — |
| `OPT-UNPARSED` | advisory | `ds-warp-spiders` | — |
| `OPT-UNPARSED` | advisory | `ds-wolf-guard` | — |
| `OPT-UNPARSED` | advisory | `ds-wolf-guard-headtakers` | — |
| `OPT-UNPARSED` | advisory | `ds-wolf-guard-terminators` | — |
| `OPT-UNPARSED` | advisory | `ds-wolf-scouts` | — |
| `OPT-UNPARSED` | advisory | `ds-wracks` | — |
| `OPT-UNPARSED` | advisory | `ds-wracks` | — |
| `OPT-UNPARSED` | advisory | `ds-wraithblades` | — |
| `OPT-UNPARSED` | advisory | `ds-wraithguard` | — |
| `OPT-UNPARSED` | advisory | `ds-wulfen-dreadnought` | — |
| `OPT-UNPARSED` | advisory | `ds-xv9-hazard-battlesuits` | — |
| `OPT-UNPARSED` | advisory | `ds-xv9-hazard-battlesuits` | — |

</details>

<details><summary>reconciliation (7180)</summary>

| code | severity | entities | resolved |
|---|---|---|---|
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-aberrants`, `eq-aberrants-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-accursed-cultists`, `eq-accursed-cultists-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-accursed-cultists`, `eq-accursed-cultists-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-accursed-cultists-2`, `eq-accursed-cultists-2-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-accursed-cultists-2`, `eq-accursed-cultists-2-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-accursed-cultists-3`, `eq-accursed-cultists-3-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-accursed-cultists-3`, `eq-accursed-cultists-3-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-aquila-kill-team`, `eq-aquila-kill-team-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-assault-intercessors-with-jump-packs`, `eq-assault-intercessors-with-jump-packs-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-assault-intercessors-with-jump-packs-2`, `eq-assault-intercessors-with-jump-packs-2-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-assault-intercessors-with-jump-packs-3`, `eq-assault-intercessors-with-jump-packs-3-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-assault-intercessors-with-jump-packs-4`, `eq-assault-intercessors-with-jump-packs-4-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-assault-intercessors-with-jump-packs-5`, `eq-assault-intercessors-with-jump-packs-5-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-assault-intercessors-with-jump-packs-6`, `eq-assault-intercessors-with-jump-packs-6-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-atalan-jackals`, `eq-atalan-jackals-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-atalan-jackals`, `eq-atalan-jackals-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-aunva`, `eq-aunva-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-beast-snagga-boyz`, `eq-beast-snagga-boyz-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-beastmaster`, `eq-beastmaster-3` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-blue-horrors`, `eq-blue-horrors-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-blue-horrors`, `eq-blue-horrors-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-blue-horrors-2`, `eq-blue-horrors-2-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-blue-horrors-2`, `eq-blue-horrors-2-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-boyz`, `eq-boyz-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-breaka-boyz`, `eq-breaka-boyz-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-burna-boyz`, `eq-burna-boyz-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-burna-boyz`, `eq-burna-boyz-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-cadian-recon-squad`, `eq-cadian-recon-squad-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-catachan-command-squad`, `eq-catachan-command-squad-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-catachan-command-squad-2`, `eq-catachan-command-squad-2-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-celestian-insidiants`, `eq-celestian-insidiants-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-chaplain-grimaldus`, `eq-chaplain-grimaldus-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-command-squad`, `eq-command-squad-4` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-corsair-voidscarred`, `eq-corsair-voidscarred-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-corsair-voidscarred-2`, `eq-corsair-voidscarred-2-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-crusader-squad`, `eq-crusader-squad-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-crusader-squad`, `eq-crusader-squad-3` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-cultist-mob-with-firearms`, `eq-cultist-mob-with-firearms-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-cultist-mob-with-firearms-2`, `eq-cultist-mob-with-firearms-2-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-cultist-mob-with-firearms-3`, `eq-cultist-mob-with-firearms-3-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-dark-apostle`, `eq-dark-apostle-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-dark-apostle-2`, `eq-dark-apostle-2-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-dark-commune`, `eq-dark-commune-4` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-dark-commune-2`, `eq-dark-commune-2-4` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-dark-commune-3`, `eq-dark-commune-3-4` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-deathwing-command-squad`, `eq-deathwing-command-squad-4` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-deathwing-knights`, `eq-deathwing-knights-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-deathwing-terminator-squad`, `eq-deathwing-terminator-squad-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-decimus-kill-team`, `eq-decimus-kill-team-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-fellgor-beastmen`, `eq-fellgor-beastmen-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-fellgor-beastmen-2`, `eq-fellgor-beastmen-2-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-fellgor-beastmen-3`, `eq-fellgor-beastmen-3-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-fire-dragons`, `eq-fire-dragons-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-flesh-hounds`, `eq-flesh-hounds-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-flesh-hounds-2`, `eq-flesh-hounds-2-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-fortis-kill-team-2`, `eq-fortis-kill-team-2-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-fortis-kill-team-2`, `eq-fortis-kill-team-2-4` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-gellerpox-infected`, `eq-gellerpox-infected-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-gellerpox-infected`, `eq-gellerpox-infected-3` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-gellerpox-infected-2`, `eq-gellerpox-infected-2-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-gellerpox-infected-2`, `eq-gellerpox-infected-2-3` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-gellerpox-infected-3`, `eq-gellerpox-infected-3-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-gellerpox-infected-3`, `eq-gellerpox-infected-3-3` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-gellerpox-infected-4`, `eq-gellerpox-infected-4-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-gellerpox-infected-4`, `eq-gellerpox-infected-4-3` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-grimnyr`, `eq-grimnyr-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-guardian-defenders`, `eq-guardian-defenders-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-hastarii-exterminators`, `eq-hastarii-exterminators-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-hastarii-fusiliers`, `eq-hastarii-fusiliers-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-hearthkyn-warriors`, `eq-hearthkyn-warriors-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-hybrid-metamorphs`, `eq-hybrid-metamorphs-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-imperial-navy-breachers`, `eq-imperial-navy-breachers-4` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-indomitor-kill-team`, `eq-indomitor-kill-team-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-indomitor-kill-team-2`, `eq-indomitor-kill-team-2-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-infractors`, `eq-infractors-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-inner-circle-companions`, `eq-inner-circle-companions-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-inquisitorial-agents`, `eq-inquisitorial-agents-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-inquisitorial-agents`, `eq-inquisitorial-agents-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-ironkin-steeljacks-with-heavy-volkanite-disintegrators`, `eq-ironkin-steeljacks-with-heavy-volkanite-disintegrators-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-ironkin-steeljacks-with-melee-weapons`, `eq-ironkin-steeljacks-with-melee-weapons-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-kasrkin`, `eq-kasrkin-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-kasrkin-2`, `eq-kasrkin-2-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-krieg-heavy-weapons-squad`, `eq-krieg-heavy-weapons-squad-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-krieg-heavy-weapons-squad-2`, `eq-krieg-heavy-weapons-squad-2-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-kroot-carnivores`, `eq-kroot-carnivores-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-kroot-farstalkers`, `eq-kroot-farstalkers-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-kroot-farstalkers`, `eq-kroot-farstalkers-3` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-lootas`, `eq-lootas-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-lootas`, `eq-lootas-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-militarum-tempestus-command-squad`, `eq-militarum-tempestus-command-squad-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-nemesis-claw`, `eq-nemesis-claw-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-pink-horrors`, `eq-pink-horrors-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-pink-horrors`, `eq-pink-horrors-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-pink-horrors`, `eq-pink-horrors-3` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-pink-horrors-2`, `eq-pink-horrors-2-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-pink-horrors-2`, `eq-pink-horrors-2-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-pink-horrors-2`, `eq-pink-horrors-2-3` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-proteus-kill-team`, `eq-proteus-kill-team-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-proteus-kill-team`, `eq-proteus-kill-team-3` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-proteus-kill-team`, `eq-proteus-kill-team-4` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-pteraxii-skystalkers`, `eq-pteraxii-skystalkers-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-pteraxii-sterylizors`, `eq-pteraxii-sterylizors-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-quartermaster-cadre-squad`, `eq-quartermaster-cadre-squad-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-quartermaster-cadre-squad-2`, `eq-quartermaster-cadre-squad-2-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-ravenwing-command-squad`, `eq-ravenwing-command-squad-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-red-corsairs-raiders`, `eq-red-corsairs-raiders-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-renegade-ogryn-beast-handler`, `eq-renegade-ogryn-beast-handler-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-renegade-ogryn-beast-handler-2`, `eq-renegade-ogryn-beast-handler-2-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-renegade-ogryn-beast-handler-3`, `eq-renegade-ogryn-beast-handler-3-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-repentia-squad`, `eq-repentia-squad-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-retributor-squad`, `eq-retributor-squad-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-rubric-marines`, `eq-rubric-marines-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-rubric-marines-2`, `eq-rubric-marines-2-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-sanctifiers`, `eq-sanctifiers-6` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-sanctifiers-2`, `eq-sanctifiers-2-6` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-scarab-occult-terminators`, `eq-scarab-occult-terminators-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-scourges-with-heavy-weapons`, `eq-scourges-with-heavy-weapons-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-serberys-raiders`, `eq-serberys-raiders-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-serberys-sulphurhounds`, `eq-serberys-sulphurhounds-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-servitor-battleclade`, `eq-servitor-battleclade-4` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-sisters-novitiate-squad`, `eq-sisters-novitiate-squad-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-spectrus-kill-team`, `eq-spectrus-kill-team-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-spectrus-kill-team-2`, `eq-spectrus-kill-team-2-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-squighog-boyz`, `eq-squighog-boyz-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-storm-guardians`, `eq-storm-guardians-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-striking-scorpions`, `eq-striking-scorpions-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-swooping-hawks`, `eq-swooping-hawks-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-tankbustas`, `eq-tankbustas-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-tempestus-aquilons`, `eq-tempestus-aquilons-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-tempestus-scions`, `eq-tempestus-scions-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-the-silent-king`, `eq-the-silent-king-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-tormentors`, `eq-tormentors-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-traitor-guardsmen-squad`, `eq-traitor-guardsmen-squad-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-traitor-guardsmen-squad-2`, `eq-traitor-guardsmen-squad-2-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-traitor-guardsmen-squad-3`, `eq-traitor-guardsmen-squad-3-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-voidsmen-at-arms`, `eq-voidsmen-at-arms-3` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-warp-spiders`, `eq-warp-spiders-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-webway-gate`, `eq-webway-gate-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-wolf-guard-headtakers`, `eq-wolf-guard-headtakers-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-wolf-guard-headtakers`, `eq-wolf-guard-headtakers-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-wolf-guard-terminators`, `eq-wolf-guard-terminators-2` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-wolf-scouts`, `eq-wolf-scouts-1` | — |
| `EQP-GROUP-UNRESOLVED` | advisory | `ds-wolf-scouts`, `eq-wolf-scouts-2` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-abaddon-the-despoiler`, `eq-abaddon-the-despoiler-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-acastus-knight-asterius`, `eq-acastus-knight-asterius-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-acastus-knight-asterius`, `eq-acastus-knight-asterius-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-acastus-knight-porphyrion`, `eq-acastus-knight-porphyrion-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-acastus-knight-porphyrion`, `eq-acastus-knight-porphyrion-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-achilles-ridgerunners`, `eq-achilles-ridgerunners-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-achilles-ridgerunners`, `eq-achilles-ridgerunners-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-aetaosraukeres`, `eq-aetaosraukeres-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-aggressor-squad`, `eq-aggressor-squad-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-aggressor-squad-2`, `eq-aggressor-squad-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-aggressor-squad-3`, `eq-aggressor-squad-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-aggressor-squad-4`, `eq-aggressor-squad-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-aggressor-squad-5`, `eq-aggressor-squad-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-aggressor-squad-6`, `eq-aggressor-squad-6-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-allarus-custodians`, `eq-allarus-custodians-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-anggrath-the-unbound`, `eq-anggrath-the-unbound-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-angron`, `eq-angron-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-aquila-kill-team`, `eq-aquila-kill-team-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-aquila-kill-team`, `eq-aquila-kill-team-2` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-archaeopter-fusilave`, `eq-archaeopter-fusilave-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-archaeopter-stratoraptor`, `eq-archaeopter-stratoraptor-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-archaeopter-stratoraptor`, `eq-archaeopter-stratoraptor-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-archaeopter-stratoraptor`, `eq-archaeopter-stratoraptor-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-archaeopter-transvector`, `eq-archaeopter-transvector-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-archon`, `eq-archon-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-ares-gunship`, `eq-ares-gunship-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-arjac-rockfist`, `eq-arjac-rockfist-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-arkanyst-evaluator`, `eq-arkanyst-evaluator-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-arkurian-stormhammer`, `eq-arkurian-stormhammer-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-arkurian-stormhammer-2`, `eq-arkurian-stormhammer-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-armiger-helverin`, `eq-armiger-helverin-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-armiger-warglaive`, `eq-armiger-warglaive-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-asmodai`, `eq-asmodai-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-astraeus`, `eq-astraeus-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-astraeus-2`, `eq-astraeus-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-astraeus-3`, `eq-astraeus-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-astraeus-4`, `eq-astraeus-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-astraeus-5`, `eq-astraeus-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-astraeus-6`, `eq-astraeus-6-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-attack-fighta`, `eq-attack-fighta-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-attack-fighta`, `eq-attack-fighta-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-attilan-rough-riders`, `eq-attilan-rough-riders-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-attilan-rough-riders-2`, `eq-attilan-rough-riders-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-autarch-skyrunner`, `eq-autarch-skyrunner-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-avenger-strike-fighter`, `eq-avenger-strike-fighter-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-ax-1-0-tiger-shark`, `eq-ax-1-0-tiger-shark-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-ax-1-0-tiger-shark`, `eq-ax-1-0-tiger-shark-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-azrael`, `eq-azrael-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-ballistus-dreadnought`, `eq-ballistus-dreadnought-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-ballistus-dreadnought-2`, `eq-ballistus-dreadnought-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-ballistus-dreadnought-3`, `eq-ballistus-dreadnought-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-ballistus-dreadnought-4`, `eq-ballistus-dreadnought-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-ballistus-dreadnought-5`, `eq-ballistus-dreadnought-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-ballistus-dreadnought-6`, `eq-ballistus-dreadnought-6-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-baneblade`, `eq-baneblade-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-baneblade`, `eq-baneblade-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-baneblade-2`, `eq-baneblade-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-baneblade-2`, `eq-baneblade-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-banehammer`, `eq-banehammer-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-banehammer`, `eq-banehammer-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-banehammer-2`, `eq-banehammer-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-banehammer-2`, `eq-banehammer-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-banesword`, `eq-banesword-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-banesword`, `eq-banesword-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-banesword-2`, `eq-banesword-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-banesword-2`, `eq-banesword-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-barbed-hierodule`, `eq-barbed-hierodule-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-barracuda`, `eq-barracuda-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-barracuda`, `eq-barracuda-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-battle-sanctum`, `eq-battle-sanctum-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-belakor`, `eq-belakor-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-belakor`, `eq-belakor-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-benefictus`, `eq-benefictus-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-berehk-stornbrow`, `eq-berehk-stornbrow-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-big-gunz`, `eq-big-gunz-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-big-mek`, `eq-big-mek-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-big-mek-dakkarig`, `eq-big-mek-dakkarig-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-big-mek-in-mega-armour`, `eq-big-mek-in-mega-armour-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-big-trakk`, `eq-big-trakk-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-biged-bossbunka`, `eq-biged-bossbunka-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-biophagus`, `eq-biophagus-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-blade-champion`, `eq-blade-champion-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-bloodthirster`, `eq-bloodthirster-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-bloodthirster-2`, `eq-bloodthirster-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-brotherhood-techmarine`, `eq-brotherhood-techmarine-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-bullgryn-squad`, `eq-bullgryn-squad-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-buri-aegnirssen`, `eq-buri-aegnirssen-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-burning-chariot`, `eq-burning-chariot-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-caanok-var`, `eq-caanok-var-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-canis-rex`, `eq-canis-rex-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-canis-rex`, `eq-canis-rex-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-canis-wolfborn`, `eq-canis-wolfborn-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-canoptek-reanimator`, `eq-canoptek-reanimator-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-canoptek-tomb-sentinel`, `eq-canoptek-tomb-sentinel-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-canoptek-tomb-stalker`, `eq-canoptek-tomb-stalker-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-carab-culln-the-risen`, `eq-carab-culln-the-risen-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-carab-culln-the-risen`, `eq-carab-culln-the-risen-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-carnodon`, `eq-carnodon-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-carnodon-2`, `eq-carnodon-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-castigator`, `eq-castigator-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-catacomb-command-barge`, `eq-catacomb-command-barge-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-cato-sicarius`, `eq-cato-sicarius-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-centaur-light-carrier`, `eq-centaur-light-carrier-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-centaur-light-carrier-2`, `eq-centaur-light-carrier-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-cerastus-knight-acheron`, `eq-cerastus-knight-acheron-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-cerastus-knight-atrapos`, `eq-cerastus-knight-atrapos-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-cerastus-knight-atrapos`, `eq-cerastus-knight-atrapos-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-cerastus-knight-castigator`, `eq-cerastus-knight-castigator-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-changecaster`, `eq-changecaster-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-chaos-acastus-knight-asterius`, `eq-chaos-acastus-knight-asterius-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-chaos-acastus-knight-asterius`, `eq-chaos-acastus-knight-asterius-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-chaos-acastus-knight-porphyrion`, `eq-chaos-acastus-knight-porphyrion-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-chaos-acastus-knight-porphyrion`, `eq-chaos-acastus-knight-porphyrion-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-chaos-cerastus-knight-acheron`, `eq-chaos-cerastus-knight-acheron-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-chaos-cerastus-knight-atrapos`, `eq-chaos-cerastus-knight-atrapos-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-chaos-cerastus-knight-atrapos`, `eq-chaos-cerastus-knight-atrapos-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-chaos-cerastus-knight-castigator`, `eq-chaos-cerastus-knight-castigator-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-chaos-deimos-predator`, `eq-chaos-deimos-predator-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-chaos-land-raider`, `eq-chaos-land-raider-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-chaos-land-raider-2`, `eq-chaos-land-raider-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-chaos-land-raider-3`, `eq-chaos-land-raider-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-chaos-land-raider-4`, `eq-chaos-land-raider-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-chaos-land-raider-5`, `eq-chaos-land-raider-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-chaos-lord`, `eq-chaos-lord-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-chaos-lord-2`, `eq-chaos-lord-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-chaos-questoris-knight-magaera`, `eq-chaos-questoris-knight-magaera-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-chaos-questoris-knight-styrix`, `eq-chaos-questoris-knight-styrix-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-chaos-thunderhawk`, `eq-chaos-thunderhawk-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-chaos-thunderhawk`, `eq-chaos-thunderhawk-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-chaos-thunderhawk`, `eq-chaos-thunderhawk-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-chaos-thunderhawk-2`, `eq-chaos-thunderhawk-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-chaos-thunderhawk-2`, `eq-chaos-thunderhawk-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-chaos-thunderhawk-2`, `eq-chaos-thunderhawk-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-chaos-thunderhawk-3`, `eq-chaos-thunderhawk-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-chaos-thunderhawk-3`, `eq-chaos-thunderhawk-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-chaos-thunderhawk-3`, `eq-chaos-thunderhawk-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-chaos-thunderhawk-4`, `eq-chaos-thunderhawk-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-chaos-thunderhawk-4`, `eq-chaos-thunderhawk-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-chaos-thunderhawk-4`, `eq-chaos-thunderhawk-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-chaplain-grimaldus`, `eq-chaplain-grimaldus-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-chief-librarian-mephiston`, `eq-chief-librarian-mephiston-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-chief-librarian-mephiston`, `eq-chief-librarian-mephiston-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-chief-librarian-tigurius`, `eq-chief-librarian-tigurius-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-chinork-warkopta`, `eq-chinork-warkopta-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-chronomancer`, `eq-chronomancer-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-command-squad`, `eq-command-squad-3` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-command-squad`, `eq-command-squad-4` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-commander-dante`, `eq-commander-dante-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-commander-farsight`, `eq-commander-farsight-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-commander-shadowsun`, `eq-commander-shadowsun-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-commander-shadowsun`, `eq-commander-shadowsun-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-commander-shadowsun`, `eq-commander-shadowsun-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-commissar-graves`, `eq-commissar-graves-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-commissar-graves`, `eq-commissar-graves-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-contemptor-achillus-dreadnought`, `eq-contemptor-achillus-dreadnought-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-contemptor-achillus-dreadnought`, `eq-contemptor-achillus-dreadnought-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-contemptor-galatus-dreadnought`, `eq-contemptor-galatus-dreadnought-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-corpuscarii-electro-priests`, `eq-corpuscarii-electro-priests-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-corvus-blackstar`, `eq-corvus-blackstar-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-corvus-blackstar-2`, `eq-corvus-blackstar-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-crassus`, `eq-crassus-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-crassus-2`, `eq-crassus-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-crimson-hunter`, `eq-crimson-hunter-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-crisis-sunforge-battlesuits`, `eq-crisis-sunforge-battlesuits-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-ctan-shard-of-the-nightbringer`, `eq-ctan-shard-of-the-nightbringer-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-cthonian-earthshakers`, `eq-cthonian-earthshakers-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-custodian-guard`, `eq-custodian-guard-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-custodian-guard-with-adrasite-and-pyrithite-spears`, `eq-custodian-guard-with-adrasite-and-pyrithite-spears-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-custodian-wardens`, `eq-custodian-wardens-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-cyclops-demolition-vehicle`, `eq-cyclops-demolition-vehicle-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-cyclops-demolition-vehicle-2`, `eq-cyclops-demolition-vehicle-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-cypher`, `eq-cypher-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-cypher`, `eq-cypher-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-daemon-prince-of-chaos`, `eq-daemon-prince-of-chaos-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-daemon-prince-of-chaos-with-wings`, `eq-daemon-prince-of-chaos-with-wings-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-daemon-prince-of-khorne`, `eq-daemon-prince-of-khorne-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-daemon-prince-of-khorne-with-wings`, `eq-daemon-prince-of-khorne-with-wings-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-daemon-prince-of-nurgle`, `eq-daemon-prince-of-nurgle-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-daemon-prince-of-nurgle-with-wings`, `eq-daemon-prince-of-nurgle-with-wings-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-daemon-prince-of-slaanesh`, `eq-daemon-prince-of-slaanesh-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-daemon-prince-of-slaanesh-with-wings`, `eq-daemon-prince-of-slaanesh-with-wings-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-daemon-prince-of-tzeentch`, `eq-daemon-prince-of-tzeentch-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-daemon-prince-of-tzeentch-with-wings`, `eq-daemon-prince-of-tzeentch-with-wings-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-dakkajet`, `eq-dakkajet-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-dark-commune`, `eq-dark-commune-2` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-dark-commune`, `eq-dark-commune-3` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-dark-commune-2`, `eq-dark-commune-2-2` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-dark-commune-2`, `eq-dark-commune-2-3` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-dark-commune-3`, `eq-dark-commune-3-2` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-dark-commune-3`, `eq-dark-commune-3-3` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-dark-reapers`, `eq-dark-reapers-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-death-guard-sorcerer-in-terminator-armour`, `eq-death-guard-sorcerer-in-terminator-armour-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-death-jester`, `eq-death-jester-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-death-jester-2`, `eq-death-jester-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-deathshroud-terminators`, `eq-deathshroud-terminators-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-decimator`, `eq-decimator-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-decimus-kill-team`, `eq-decimus-kill-team-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-decimus-kill-team`, `eq-decimus-kill-team-2` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-deff-dread`, `eq-deff-dread-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-deff-dread`, `eq-deff-dread-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-deff-rolla-battle-fortress`, `eq-deff-rolla-battle-fortress-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-deff-rolla-battle-fortress`, `eq-deff-rolla-battle-fortress-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-deff-rolla-battle-fortress`, `eq-deff-rolla-battle-fortress-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-deffkilla-wartrike`, `eq-deffkilla-wartrike-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-deffkilla-wartrike`, `eq-deffkilla-wartrike-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-defiler`, `eq-defiler-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-defiler`, `eq-defiler-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-defiler`, `eq-defiler-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-defiler-2`, `eq-defiler-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-defiler-2`, `eq-defiler-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-defiler-2`, `eq-defiler-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-defiler-3`, `eq-defiler-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-defiler-3`, `eq-defiler-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-defiler-3`, `eq-defiler-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-defiler-4`, `eq-defiler-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-defiler-4`, `eq-defiler-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-defiler-4`, `eq-defiler-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-defiler-5`, `eq-defiler-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-defiler-5`, `eq-defiler-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-defiler-5`, `eq-defiler-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-deimos-predator`, `eq-deimos-predator-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-devilfish`, `eq-devilfish-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-dominus-armoured-siege-bombard`, `eq-dominus-armoured-siege-bombard-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-dominus-armoured-siege-bombard-2`, `eq-dominus-armoured-siege-bombard-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-doomhammer`, `eq-doomhammer-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-doomhammer`, `eq-doomhammer-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-doomhammer-2`, `eq-doomhammer-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-doomhammer-2`, `eq-doomhammer-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-doomsday-ark`, `eq-doomsday-ark-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-dragon-knights`, `eq-dragon-knights-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-drazhar`, `eq-drazhar-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-dreadnought-drop-pod`, `eq-dreadnought-drop-pod-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-einhyr-champion`, `eq-einhyr-champion-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-emperors-champion`, `eq-emperors-champion-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-exalted-flamer`, `eq-exalted-flamer-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-ezekiel`, `eq-ezekiel-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-ezekiel`, `eq-ezekiel-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-falchion`, `eq-falchion-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-falchion-2`, `eq-falchion-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-falchion-3`, `eq-falchion-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-falchion-4`, `eq-falchion-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-falchion-5`, `eq-falchion-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-fateskimmer`, `eq-fateskimmer-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-feculent-gnarlmaw`, `eq-feculent-gnarlmaw-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-fellblade`, `eq-fellblade-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-fellblade`, `eq-fellblade-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-fellblade-2`, `eq-fellblade-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-fellblade-2`, `eq-fellblade-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-fellblade-3`, `eq-fellblade-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-fellblade-3`, `eq-fellblade-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-fellblade-4`, `eq-fellblade-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-fellblade-4`, `eq-fellblade-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-fellblade-5`, `eq-fellblade-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-fellblade-5`, `eq-fellblade-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-fighta-bommer`, `eq-fighta-bommer-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-fire-prism`, `eq-fire-prism-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-fire-raptor-gunship`, `eq-fire-raptor-gunship-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-fire-raptor-gunship`, `eq-fire-raptor-gunship-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-fire-raptor-gunship-2`, `eq-fire-raptor-gunship-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-fire-raptor-gunship-2`, `eq-fire-raptor-gunship-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-fire-raptor-gunship-3`, `eq-fire-raptor-gunship-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-fire-raptor-gunship-3`, `eq-fire-raptor-gunship-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-fire-raptor-gunship-4`, `eq-fire-raptor-gunship-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-fire-raptor-gunship-4`, `eq-fire-raptor-gunship-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-fire-raptor-gunship-5`, `eq-fire-raptor-gunship-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-fire-raptor-gunship-5`, `eq-fire-raptor-gunship-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-flesh-hounds`, `eq-flesh-hounds-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-flesh-hounds`, `eq-flesh-hounds-2` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-flesh-hounds-2`, `eq-flesh-hounds-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-flesh-hounds-2`, `eq-flesh-hounds-2-2` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-fluxmaster`, `eq-fluxmaster-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-forgefiend`, `eq-forgefiend-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-forgefiend-2`, `eq-forgefiend-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-forgefiend-3`, `eq-forgefiend-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-fuegan`, `eq-fuegan-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-fulgrim`, `eq-fulgrim-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-gargantuan-squiggoth`, `eq-gargantuan-squiggoth-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-ghazghkull-thraka`, `eq-ghazghkull-thraka-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-ghost-ark`, `eq-ghost-ark-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-gladiator-lancer`, `eq-gladiator-lancer-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-gladiator-lancer-2`, `eq-gladiator-lancer-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-gladiator-lancer-3`, `eq-gladiator-lancer-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-gladiator-lancer-4`, `eq-gladiator-lancer-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-gladiator-lancer-5`, `eq-gladiator-lancer-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-gladiator-lancer-6`, `eq-gladiator-lancer-6-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-gladiator-reaper`, `eq-gladiator-reaper-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-gladiator-reaper-2`, `eq-gladiator-reaper-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-gladiator-reaper-3`, `eq-gladiator-reaper-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-gladiator-reaper-4`, `eq-gladiator-reaper-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-gladiator-reaper-5`, `eq-gladiator-reaper-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-gladiator-reaper-6`, `eq-gladiator-reaper-6-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-gladiator-valiant`, `eq-gladiator-valiant-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-gladiator-valiant-2`, `eq-gladiator-valiant-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-gladiator-valiant-3`, `eq-gladiator-valiant-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-gladiator-valiant-4`, `eq-gladiator-valiant-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-gladiator-valiant-5`, `eq-gladiator-valiant-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-gladiator-valiant-6`, `eq-gladiator-valiant-6-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-gorgon-heavy-transport`, `eq-gorgon-heavy-transport-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-gorgon-heavy-transport`, `eq-gorgon-heavy-transport-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-gorgon-heavy-transport-2`, `eq-gorgon-heavy-transport-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-gorgon-heavy-transport-2`, `eq-gorgon-heavy-transport-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-gorkanaut`, `eq-gorkanaut-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-gorkanaut`, `eq-gorkanaut-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-gorkanaut`, `eq-gorkanaut-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-great-unclean-one`, `eq-great-unclean-one-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-great-unclean-one-2`, `eq-great-unclean-one-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-greater-brass-scorpion`, `eq-greater-brass-scorpion-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-greater-brass-scorpion-2`, `eq-greater-brass-scorpion-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-grey-knights-thunderhawk-gunship`, `eq-grey-knights-thunderhawk-gunship-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-grey-knights-thunderhawk-gunship`, `eq-grey-knights-thunderhawk-gunship-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-grey-knights-thunderhawk-gunship`, `eq-grey-knights-thunderhawk-gunship-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-grimnyr`, `eq-grimnyr-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-haarken-worldclaimer`, `eq-haarken-worldclaimer-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-hammerfall-bunker`, `eq-hammerfall-bunker-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-hammerfall-bunker-2`, `eq-hammerfall-bunker-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-hammerfall-bunker-3`, `eq-hammerfall-bunker-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-hammerfall-bunker-4`, `eq-hammerfall-bunker-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-hammerfall-bunker-5`, `eq-hammerfall-bunker-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-hammerfall-bunker-6`, `eq-hammerfall-bunker-6-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-hammerhead-gunship`, `eq-hammerhead-gunship-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-harridan`, `eq-harridan-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-hastarii-exterminators`, `eq-hastarii-exterminators-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-hastarii-exterminators`, `eq-hastarii-exterminators-2` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-hearthkyn-warriors`, `eq-hearthkyn-warriors-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-heavy-gun-drones`, `eq-heavy-gun-drones-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-hekaton-land-fortress`, `eq-hekaton-land-fortress-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-hekaton-land-fortress`, `eq-hekaton-land-fortress-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-helbrute`, `eq-helbrute-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-helbrute-3`, `eq-helbrute-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-helbrute-4`, `eq-helbrute-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-hell-blade`, `eq-hell-blade-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-hell-blade-2`, `eq-hell-blade-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-hell-blade-3`, `eq-hell-blade-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-hell-blade-4`, `eq-hell-blade-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-hellblaster-squad`, `eq-hellblaster-squad-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-hellblaster-squad-2`, `eq-hellblaster-squad-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-hellblaster-squad-3`, `eq-hellblaster-squad-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-hellblaster-squad-4`, `eq-hellblaster-squad-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-hellblaster-squad-5`, `eq-hellblaster-squad-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-hellblaster-squad-6`, `eq-hellblaster-squad-6-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-hellflayers`, `eq-hellflayers-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-hellhammer`, `eq-hellhammer-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-hellhammer`, `eq-hellhammer-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-hellhammer-2`, `eq-hellhammer-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-hellhammer-2`, `eq-hellhammer-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-hemlock-wraithfighter`, `eq-hemlock-wraithfighter-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-heretic-astartes-daemon-prince`, `eq-heretic-astartes-daemon-prince-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-heretic-astartes-daemon-prince-with-wings`, `eq-heretic-astartes-daemon-prince-with-wings-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-hierophant`, `eq-hierophant-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-high-marshal-helbrecht`, `eq-high-marshal-helbrecht-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-hornet`, `eq-hornet-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-hybrid-metamorphs`, `eq-hybrid-metamorphs-2` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-illuminor-szeras`, `eq-illuminor-szeras-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-imotekh-the-stormlord`, `eq-imotekh-the-stormlord-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-impulsor`, `eq-impulsor-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-impulsor-2`, `eq-impulsor-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-impulsor-3`, `eq-impulsor-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-impulsor-4`, `eq-impulsor-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-impulsor-5`, `eq-impulsor-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-impulsor-6`, `eq-impulsor-6-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-infernal-enrapturess`, `eq-infernal-enrapturess-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-infernal-master`, `eq-infernal-master-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-inner-circle-companions`, `eq-inner-circle-companions-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-inquisitor`, `eq-inquisitor-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-inquisitor-coteaz`, `eq-inquisitor-coteaz-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-inquisitor-greyfax`, `eq-inquisitor-greyfax-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-inquisitor-in-terminator-armour`, `eq-inquisitor-in-terminator-armour-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-inquisitor-ostromandeus`, `eq-inquisitor-ostromandeus-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-intranzia-fraye`, `eq-intranzia-fraye-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-invader-atv`, `eq-invader-atv-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-invader-atv-2`, `eq-invader-atv-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-invader-atv-3`, `eq-invader-atv-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-invader-atv-4`, `eq-invader-atv-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-invader-atv-5`, `eq-invader-atv-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-invader-atv-6`, `eq-invader-atv-6-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-irillyth`, `eq-irillyth-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-iron-hand-straken`, `eq-iron-hand-straken-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-iron-priest`, `eq-iron-priest-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-ironkin-steeljacks-with-heavy-volkanite-disintegrators`, `eq-ironkin-steeljacks-with-heavy-volkanite-disintegrators-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-ironkin-steeljacks-with-melee-weapons`, `eq-ironkin-steeljacks-with-melee-weapons-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-javelin-attack-speeder`, `eq-javelin-attack-speeder-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-jokaero-weaponsmith`, `eq-jokaero-weaponsmith-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-kahl`, `eq-kahl-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-kairos-fateweaver`, `eq-kairos-fateweaver-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-kairos-fateweaver-2`, `eq-kairos-fateweaver-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-kannonwagon`, `eq-kannonwagon-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-kaptin-badrukk`, `eq-kaptin-badrukk-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-karanak`, `eq-karanak-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-karandras`, `eq-karandras-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-karandras`, `eq-karandras-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-keeper-of-secrets`, `eq-keeper-of-secrets-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-keeper-of-secrets-2`, `eq-keeper-of-secrets-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-kharn-the-betrayer`, `eq-kharn-the-betrayer-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-kharybdis-assault-claw`, `eq-kharybdis-assault-claw-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-khorne-lord-of-skulls`, `eq-khorne-lord-of-skulls-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-khorne-lord-of-skulls-2`, `eq-khorne-lord-of-skulls-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-kill-krusha`, `eq-kill-krusha-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-knarloc-riders`, `eq-knarloc-riders-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-knight-castellan`, `eq-knight-castellan-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-knight-castellan`, `eq-knight-castellan-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-knight-castellan`, `eq-knight-castellan-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-knight-defender`, `eq-knight-defender-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-knight-desecrator`, `eq-knight-desecrator-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-knight-despoiler`, `eq-knight-despoiler-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-knight-despoiler`, `eq-knight-despoiler-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-knight-errant`, `eq-knight-errant-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-knight-gallant`, `eq-knight-gallant-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-knight-gallant`, `eq-knight-gallant-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-knight-paladin`, `eq-knight-paladin-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-knight-paladin`, `eq-knight-paladin-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-knight-preceptor`, `eq-knight-preceptor-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-knight-preceptor`, `eq-knight-preceptor-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-knight-preceptor`, `eq-knight-preceptor-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-knight-rampager`, `eq-knight-rampager-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-knight-rampager`, `eq-knight-rampager-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-knight-ruinator`, `eq-knight-ruinator-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-knight-tyrant`, `eq-knight-tyrant-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-knight-tyrant`, `eq-knight-tyrant-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-knight-tyrant`, `eq-knight-tyrant-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-knight-valiant`, `eq-knight-valiant-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-knight-valiant`, `eq-knight-valiant-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-knight-warden`, `eq-knight-warden-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-kratos`, `eq-kratos-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-kratos`, `eq-kratos-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-kratos-2`, `eq-kratos-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-kratos-2`, `eq-kratos-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-kratos-3`, `eq-kratos-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-kratos-3`, `eq-kratos-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-kratos-4`, `eq-kratos-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-kratos-4`, `eq-kratos-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-kratos-5`, `eq-kratos-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-kratos-5`, `eq-kratos-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-krootox-rampagers`, `eq-krootox-rampagers-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-krootox-rampagers`, `eq-krootox-rampagers-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-kytan-ravager`, `eq-kytan-ravager-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-kytan-ravager-2`, `eq-kytan-ravager-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-raider`, `eq-land-raider-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-raider-2`, `eq-land-raider-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-raider-3`, `eq-land-raider-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-raider-4`, `eq-land-raider-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-raider-5`, `eq-land-raider-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-raider-6`, `eq-land-raider-6-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-raider-7`, `eq-land-raider-7-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-raider-achilles`, `eq-land-raider-achilles-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-raider-achilles`, `eq-land-raider-achilles-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-raider-achilles-2`, `eq-land-raider-achilles-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-raider-achilles-2`, `eq-land-raider-achilles-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-raider-achilles-3`, `eq-land-raider-achilles-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-raider-achilles-3`, `eq-land-raider-achilles-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-raider-achilles-4`, `eq-land-raider-achilles-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-raider-achilles-4`, `eq-land-raider-achilles-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-raider-achilles-5`, `eq-land-raider-achilles-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-raider-achilles-5`, `eq-land-raider-achilles-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-raider-crusader`, `eq-land-raider-crusader-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-raider-crusader-2`, `eq-land-raider-crusader-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-raider-crusader-3`, `eq-land-raider-crusader-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-raider-crusader-4`, `eq-land-raider-crusader-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-raider-crusader-5`, `eq-land-raider-crusader-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-raider-crusader-6`, `eq-land-raider-crusader-6-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-raider-crusader-7`, `eq-land-raider-crusader-7-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-raider-excelsior`, `eq-land-raider-excelsior-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-raider-prometheus`, `eq-land-raider-prometheus-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-raider-proteus`, `eq-land-raider-proteus-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-raider-proteus-2`, `eq-land-raider-proteus-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-raider-proteus-3`, `eq-land-raider-proteus-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-raider-proteus-4`, `eq-land-raider-proteus-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-raider-proteus-5`, `eq-land-raider-proteus-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-raider-redeemer`, `eq-land-raider-redeemer-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-raider-redeemer-2`, `eq-land-raider-redeemer-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-raider-redeemer-3`, `eq-land-raider-redeemer-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-raider-redeemer-4`, `eq-land-raider-redeemer-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-raider-redeemer-5`, `eq-land-raider-redeemer-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-raider-redeemer-6`, `eq-land-raider-redeemer-6-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-raider-redeemer-7`, `eq-land-raider-redeemer-7-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-speeder-tempest`, `eq-land-speeder-tempest-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-speeder-typhoon`, `eq-land-speeder-typhoon-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-land-speeder-vengeance`, `eq-land-speeder-vengeance-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-leman-russ-executioner`, `eq-leman-russ-executioner-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-leman-russ-executioner-2`, `eq-leman-russ-executioner-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-leviathan-dreadnought`, `eq-leviathan-dreadnought-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-leviathan-dreadnought`, `eq-leviathan-dreadnought-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-leviathan-dreadnought-2`, `eq-leviathan-dreadnought-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-leviathan-dreadnought-2`, `eq-leviathan-dreadnought-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-leviathan-dreadnought-3`, `eq-leviathan-dreadnought-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-leviathan-dreadnought-3`, `eq-leviathan-dreadnought-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-leviathan-dreadnought-4`, `eq-leviathan-dreadnought-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-leviathan-dreadnought-4`, `eq-leviathan-dreadnought-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-leviathan-dreadnought-5`, `eq-leviathan-dreadnought-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-leviathan-dreadnought-5`, `eq-leviathan-dreadnought-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-leystalker`, `eq-leystalker-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-librarian`, `eq-librarian-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-librarian-2`, `eq-librarian-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-librarian-3`, `eq-librarian-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-librarian-4`, `eq-librarian-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-librarian-5`, `eq-librarian-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-librarian-dreadnought`, `eq-librarian-dreadnought-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-librarian-dreadnought`, `eq-librarian-dreadnought-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-librarian-in-phobos-armour`, `eq-librarian-in-phobos-armour-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-librarian-in-phobos-armour-2`, `eq-librarian-in-phobos-armour-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-librarian-in-phobos-armour-3`, `eq-librarian-in-phobos-armour-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-librarian-in-phobos-armour-4`, `eq-librarian-in-phobos-armour-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-librarian-in-phobos-armour-5`, `eq-librarian-in-phobos-armour-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-librarian-in-terminator-armour`, `eq-librarian-in-terminator-armour-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-librarian-in-terminator-armour-2`, `eq-librarian-in-terminator-armour-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-librarian-in-terminator-armour-3`, `eq-librarian-in-terminator-armour-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-librarian-in-terminator-armour-4`, `eq-librarian-in-terminator-armour-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-librarian-in-terminator-armour-5`, `eq-librarian-in-terminator-armour-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-librarian-with-jump-pack`, `eq-librarian-with-jump-pack-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-lion-eljonson`, `eq-lion-eljonson-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-lion-eljonson`, `eq-lion-eljonson-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-logan-grimnar`, `eq-logan-grimnar-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-logan-grimnar-on-stormrider`, `eq-logan-grimnar-on-stormrider-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-lokhust-lord`, `eq-lokhust-lord-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-longstrike`, `eq-longstrike-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-lord`, `eq-lord-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-lord-exultant`, `eq-lord-exultant-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-lord-invocatus`, `eq-lord-invocatus-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-lord-of-change`, `eq-lord-of-change-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-lord-of-change-2`, `eq-lord-of-change-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-lord-of-contagion`, `eq-lord-of-contagion-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-lord-of-poxes`, `eq-lord-of-poxes-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-lord-on-juggernaut`, `eq-lord-on-juggernaut-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-lukas-the-trickster`, `eq-lukas-the-trickster-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-macharius`, `eq-macharius-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-macharius-2`, `eq-macharius-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-macharius-omega`, `eq-macharius-omega-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-macharius-omega-2`, `eq-macharius-omega-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-macharius-vanquisher`, `eq-macharius-vanquisher-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-macharius-vanquisher-2`, `eq-macharius-vanquisher-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-macharius-vulcan`, `eq-macharius-vulcan-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-macharius-vulcan-2`, `eq-macharius-vulcan-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-magnus-the-red`, `eq-magnus-the-red-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-malcador`, `eq-malcador-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-malcador-2`, `eq-malcador-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-malcador-annihilator`, `eq-malcador-annihilator-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-malcador-annihilator-2`, `eq-malcador-annihilator-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-malcador-defender`, `eq-malcador-defender-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-malcador-defender-2`, `eq-malcador-defender-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-malcador-infernus`, `eq-malcador-infernus-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-malcador-infernus-2`, `eq-malcador-infernus-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-maleceptor`, `eq-maleceptor-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-malignant-plaguecaster`, `eq-malignant-plaguecaster-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-manta`, `eq-manta-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-manta`, `eq-manta-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-manta`, `eq-manta-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-manta`, `eq-manta-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-manta`, `eq-manta-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-marauder-bomber`, `eq-marauder-bomber-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-marauder-bomber`, `eq-marauder-bomber-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-marauder-bomber`, `eq-marauder-bomber-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-marauder-destroyer`, `eq-marauder-destroyer-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-marauder-destroyer`, `eq-marauder-destroyer-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-marneus-calgar-in-armour-of-antilochus`, `eq-marneus-calgar-in-armour-of-antilochus-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-marshal`, `eq-marshal-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-master-of-possession`, `eq-master-of-possession-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-master-of-possession-2`, `eq-master-of-possession-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-mastodon`, `eq-mastodon-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-mastodon`, `eq-mastodon-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-mastodon-2`, `eq-mastodon-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-mastodon-2`, `eq-mastodon-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-mastodon-3`, `eq-mastodon-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-mastodon-3`, `eq-mastodon-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-mastodon-4`, `eq-mastodon-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-mastodon-4`, `eq-mastodon-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-mastodon-5`, `eq-mastodon-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-mastodon-5`, `eq-mastodon-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-maugan-ra`, `eq-maugan-ra-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-megatrakk-scrapjet`, `eq-megatrakk-scrapjet-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-ministorum-priest`, `eq-ministorum-priest-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-ministorum-priest-2`, `eq-ministorum-priest-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-ministorum-priest-3`, `eq-ministorum-priest-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-monolith`, `eq-monolith-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-morkanaut`, `eq-morkanaut-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-morkanaut`, `eq-morkanaut-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-morkanaut`, `eq-morkanaut-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-mortarion`, `eq-mortarion-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-mortifiers`, `eq-mortifiers-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-mortis-dreadnought`, `eq-mortis-dreadnought-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-morvenn-vahl`, `eq-morvenn-vahl-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-morvenn-vahl`, `eq-morvenn-vahl-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-mucolid-spores`, `eq-mucolid-spores-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-mutalith-vortex-beast`, `eq-mutalith-vortex-beast-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-mutilators`, `eq-mutilators-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-myphitic-blight-hauler`, `eq-myphitic-blight-hauler-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-nekrosor-ammentar`, `eq-nekrosor-ammentar-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-nemesor-zahndrekh`, `eq-nemesor-zahndrekh-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-neyam-shai-murad`, `eq-neyam-shai-murad-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-njal-stormcaller`, `eq-njal-stormcaller-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-norn-assimilator`, `eq-norn-assimilator-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-norn-emissary`, `eq-norn-emissary-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-noxious-blightbringer`, `eq-noxious-blightbringer-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-obelisk`, `eq-obelisk-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-obliterators`, `eq-obliterators-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-ogryn-bodyguard`, `eq-ogryn-bodyguard-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-ogryn-squad`, `eq-ogryn-squad-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-old-one-eye`, `eq-old-one-eye-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-onager-dunecrawler`, `eq-onager-dunecrawler-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-orca-dropship`, `eq-orca-dropship-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-orion-assault-dropship`, `eq-orion-assault-dropship-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-orion-assault-dropship`, `eq-orion-assault-dropship-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-orion-assault-dropship`, `eq-orion-assault-dropship-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-overlord-with-translocation-shroud`, `eq-overlord-with-translocation-shroud-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-piranhas`, `eq-piranhas-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-plagueburst-crawler`, `eq-plagueburst-crawler-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-plasmancer`, `eq-plasmancer-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-praetor`, `eq-praetor-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-praetor`, `eq-praetor-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-praetor-2`, `eq-praetor-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-praetor-2`, `eq-praetor-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-primaris-psyker`, `eq-primaris-psyker-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-primaris-psyker-2`, `eq-primaris-psyker-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-psychomancer`, `eq-psychomancer-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-questoris-knight-magaera`, `eq-questoris-knight-magaera-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-questoris-knight-styrix`, `eq-questoris-knight-styrix-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-ravager`, `eq-ravager-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-raven-strike-fighter`, `eq-raven-strike-fighter-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-ravenwing-black-knights`, `eq-ravenwing-black-knights-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-ravenwing-command-squad`, `eq-ravenwing-command-squad-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-ravenwing-command-squad`, `eq-ravenwing-command-squad-2` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-ravenwing-dark-talon`, `eq-ravenwing-dark-talon-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-razorshark-strike-fighter`, `eq-razorshark-strike-fighter-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-razorshark-strike-fighter`, `eq-razorshark-strike-fighter-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-razorwing-jetfighter`, `eq-razorwing-jetfighter-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-razorwing-jetfighter`, `eq-razorwing-jetfighter-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-reaper`, `eq-reaper-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-relic-contemptor-dreadnought`, `eq-relic-contemptor-dreadnought-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-relic-contemptor-dreadnought-2`, `eq-relic-contemptor-dreadnought-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-relic-contemptor-dreadnought-3`, `eq-relic-contemptor-dreadnought-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-relic-contemptor-dreadnought-4`, `eq-relic-contemptor-dreadnought-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-relic-contemptor-dreadnought-5`, `eq-relic-contemptor-dreadnought-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-remora-stealth-drones`, `eq-remora-stealth-drones-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-remora-stealth-drones`, `eq-remora-stealth-drones-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-remote-sensor-tower`, `eq-remote-sensor-tower-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-repulsor-executioner`, `eq-repulsor-executioner-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-repulsor-executioner-2`, `eq-repulsor-executioner-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-repulsor-executioner-3`, `eq-repulsor-executioner-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-repulsor-executioner-4`, `eq-repulsor-executioner-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-repulsor-executioner-5`, `eq-repulsor-executioner-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-repulsor-executioner-6`, `eq-repulsor-executioner-6-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-rhino-primaris`, `eq-rhino-primaris-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-roboute-guilliman`, `eq-roboute-guilliman-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-rogue-psyker`, `eq-rogue-psyker-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-rogue-psyker-2`, `eq-rogue-psyker-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-rogue-psyker-3`, `eq-rogue-psyker-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-rogue-trader-entourage`, `eq-rogue-trader-entourage-4` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-rotigus`, `eq-rotigus-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-rotigus-2`, `eq-rotigus-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-rvarna-battlesuit`, `eq-rvarna-battlesuit-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-saint-celestine`, `eq-saint-celestine-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-sanctifiers`, `eq-sanctifiers-2` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-sanctifiers-2`, `eq-sanctifiers-2-2` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-scabeiathrax-the-bloated`, `eq-scabeiathrax-the-bloated-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-scout-sniper-squad`, `eq-scout-sniper-squad-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-secutarii-hoplites`, `eq-secutarii-hoplites-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-secutarii-peltasts`, `eq-secutarii-peltasts-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-seraphim-squad`, `eq-seraphim-squad-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-seraptek-heavy-construct`, `eq-seraptek-heavy-construct-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-seraptek-heavy-construct`, `eq-seraptek-heavy-construct-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-serberys-sulphurhounds`, `eq-serberys-sulphurhounds-2` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-shadow-spectres`, `eq-shadow-spectres-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-shadowseer`, `eq-shadowseer-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-shadowseer-2`, `eq-shadowseer-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-shalaxi-helbane`, `eq-shalaxi-helbane-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-shalaxi-helbane-2`, `eq-shalaxi-helbane-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-shaso-ralai`, `eq-shaso-ralai-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-shaso-ralai`, `eq-shaso-ralai-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-shield-captain`, `eq-shield-captain-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-shield-captain-in-allarus-terminator-armour`, `eq-shield-captain-in-allarus-terminator-armour-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-shining-spears`, `eq-shining-spears-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-sicaran-arcus`, `eq-sicaran-arcus-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-sicaran-omega`, `eq-sicaran-omega-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-skarbrand`, `eq-skarbrand-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-skarbrand-2`, `eq-skarbrand-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-skathach-wraithknight`, `eq-skathach-wraithknight-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-skorpius-disintegrator`, `eq-skorpius-disintegrator-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-skull-altar`, `eq-skull-altar-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-sky-ray-gunship`, `eq-sky-ray-gunship-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-sokar-pattern-stormbird`, `eq-sokar-pattern-stormbird-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-sokar-pattern-stormbird`, `eq-sokar-pattern-stormbird-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-sokar-pattern-stormbird-2`, `eq-sokar-pattern-stormbird-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-sokar-pattern-stormbird-2`, `eq-sokar-pattern-stormbird-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-sokar-pattern-stormbird-3`, `eq-sokar-pattern-stormbird-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-sokar-pattern-stormbird-3`, `eq-sokar-pattern-stormbird-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-sokar-pattern-stormbird-4`, `eq-sokar-pattern-stormbird-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-sokar-pattern-stormbird-4`, `eq-sokar-pattern-stormbird-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-sokar-pattern-stormbird-5`, `eq-sokar-pattern-stormbird-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-sokar-pattern-stormbird-5`, `eq-sokar-pattern-stormbird-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-solitaire`, `eq-solitaire-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-solitaire-2`, `eq-solitaire-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-sorcerer`, `eq-sorcerer-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-sorcerer-2`, `eq-sorcerer-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-sorcerer-4`, `eq-sorcerer-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-sorcerer-in-terminator-armour`, `eq-sorcerer-in-terminator-armour-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-sorcerer-in-terminator-armour-3`, `eq-sorcerer-in-terminator-armour-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-sorcerer-on-bike`, `eq-sorcerer-on-bike-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-sorcerer-on-disc-of-tzeentch`, `eq-sorcerer-on-disc-of-tzeentch-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-sorcerer-on-disc-of-tzeentch-2`, `eq-sorcerer-on-disc-of-tzeentch-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-sorcerer-on-palanquin-of-nurgle`, `eq-sorcerer-on-palanquin-of-nurgle-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-sorcerer-on-palanquin-of-nurgle-2`, `eq-sorcerer-on-palanquin-of-nurgle-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-sorcerer-on-palanquin-of-nurgle-3`, `eq-sorcerer-on-palanquin-of-nurgle-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-sorcerer-on-steed-of-slaanesh`, `eq-sorcerer-on-steed-of-slaanesh-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-sorcerer-on-steed-of-slaanesh-2`, `eq-sorcerer-on-steed-of-slaanesh-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-spartan`, `eq-spartan-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-spartan-2`, `eq-spartan-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-spartan-3`, `eq-spartan-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-spartan-4`, `eq-spartan-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-spartan-5`, `eq-spartan-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-spore-mines`, `eq-spore-mines-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-squiggoth`, `eq-squiggoth-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-squighog-boyz`, `eq-squighog-boyz-2` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-stalker`, `eq-stalker-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-starweaver`, `eq-starweaver-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-starweaver-2`, `eq-starweaver-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-stompa`, `eq-stompa-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-stompa`, `eq-stompa-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-storm-eagle-gunship`, `eq-storm-eagle-gunship-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-storm-eagle-gunship-2`, `eq-storm-eagle-gunship-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-storm-eagle-gunship-3`, `eq-storm-eagle-gunship-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-storm-eagle-gunship-4`, `eq-storm-eagle-gunship-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-storm-eagle-gunship-5`, `eq-storm-eagle-gunship-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-storm-guardians`, `eq-storm-guardians-2` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-storm-speeder-hailstrike`, `eq-storm-speeder-hailstrike-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-storm-speeder-hailstrike-2`, `eq-storm-speeder-hailstrike-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-storm-speeder-hailstrike-3`, `eq-storm-speeder-hailstrike-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-storm-speeder-hailstrike-4`, `eq-storm-speeder-hailstrike-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-storm-speeder-hailstrike-5`, `eq-storm-speeder-hailstrike-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-storm-speeder-hailstrike-6`, `eq-storm-speeder-hailstrike-6-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-storm-speeder-hammerstrike`, `eq-storm-speeder-hammerstrike-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-storm-speeder-hammerstrike-2`, `eq-storm-speeder-hammerstrike-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-storm-speeder-hammerstrike-3`, `eq-storm-speeder-hammerstrike-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-storm-speeder-hammerstrike-4`, `eq-storm-speeder-hammerstrike-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-storm-speeder-hammerstrike-5`, `eq-storm-speeder-hammerstrike-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-storm-speeder-hammerstrike-6`, `eq-storm-speeder-hammerstrike-6-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-stormblade`, `eq-stormblade-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-stormblade`, `eq-stormblade-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-stormblade`, `eq-stormblade-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-stormblade-2`, `eq-stormblade-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-stormblade-2`, `eq-stormblade-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-stormblade-2`, `eq-stormblade-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-stormfang-gunship`, `eq-stormfang-gunship-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-stormfang-gunship`, `eq-stormfang-gunship-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-stormlord`, `eq-stormlord-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-stormlord`, `eq-stormlord-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-stormlord`, `eq-stormlord-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-stormlord-2`, `eq-stormlord-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-stormlord-2`, `eq-stormlord-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-stormlord-2`, `eq-stormlord-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-stormraven-gunship`, `eq-stormraven-gunship-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-stormraven-gunship`, `eq-stormraven-gunship-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-stormraven-gunship-2`, `eq-stormraven-gunship-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-stormraven-gunship-2`, `eq-stormraven-gunship-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-stormraven-gunship-3`, `eq-stormraven-gunship-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-stormraven-gunship-3`, `eq-stormraven-gunship-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-stormraven-gunship-4`, `eq-stormraven-gunship-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-stormraven-gunship-4`, `eq-stormraven-gunship-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-stormraven-gunship-5`, `eq-stormraven-gunship-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-stormraven-gunship-5`, `eq-stormraven-gunship-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-stormraven-gunship-6`, `eq-stormraven-gunship-6-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-stormraven-gunship-6`, `eq-stormraven-gunship-6-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-stormraven-gunship-7`, `eq-stormraven-gunship-7-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-stormraven-gunship-7`, `eq-stormraven-gunship-7-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-stormsword`, `eq-stormsword-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-stormsword`, `eq-stormsword-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-stormsword-2`, `eq-stormsword-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-stormsword-2`, `eq-stormsword-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-stormwolf`, `eq-stormwolf-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-stormwolf`, `eq-stormwolf-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-sun-shark-bomber`, `eq-sun-shark-bomber-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-sun-shark-bomber`, `eq-sun-shark-bomber-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-syllesske`, `eq-syllesske-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-syllesske`, `eq-syllesske-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-tallyman`, `eq-tallyman-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-talos`, `eq-talos-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-tankbustas`, `eq-tankbustas-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-taunar-supremacy-armour`, `eq-taunar-supremacy-armour-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-taunar-supremacy-armour`, `eq-taunar-supremacy-armour-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-taunar-supremacy-armour`, `eq-taunar-supremacy-armour-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-taunar-supremacy-armour`, `eq-taunar-supremacy-armour-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-technomancer`, `eq-technomancer-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-telemon-heavy-dreadnought`, `eq-telemon-heavy-dreadnought-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-terminator-assault-squad`, `eq-terminator-assault-squad-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-terminator-assault-squad-2`, `eq-terminator-assault-squad-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-terminator-assault-squad-3`, `eq-terminator-assault-squad-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-terminator-assault-squad-4`, `eq-terminator-assault-squad-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-terminator-assault-squad-5`, `eq-terminator-assault-squad-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-terminus-ultra`, `eq-terminus-ultra-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-terminus-ultra`, `eq-terminus-ultra-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-terrax-pattern-termite`, `eq-terrax-pattern-termite-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-terrax-pattern-termite-2`, `eq-terrax-pattern-termite-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-terrax-pattern-termite-3`, `eq-terrax-pattern-termite-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-terrax-pattern-termite-4`, `eq-terrax-pattern-termite-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-terrax-pattern-termite-5`, `eq-terrax-pattern-termite-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-terrax-pattern-termite-6`, `eq-terrax-pattern-termite-6-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-tervigon`, `eq-tervigon-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-tesseract-ark`, `eq-tesseract-ark-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-tesseract-ark`, `eq-tesseract-ark-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-tetras`, `eq-tetras-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-the-changeling`, `eq-the-changeling-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-the-twin-lance`, `eq-the-twin-lance-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-the-twin-lance`, `eq-the-twin-lance-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-the-twin-lance`, `eq-the-twin-lance-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-the-twin-lance`, `eq-the-twin-lance-2` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-the-twin-lance`, `eq-the-twin-lance-2` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-the-visarch`, `eq-the-visarch-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-the-yncarne`, `eq-the-yncarne-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-thulia-ghuld`, `eq-thulia-ghuld-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-thulia-ghuld`, `eq-thulia-ghuld-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-thunderhawk-gunship`, `eq-thunderhawk-gunship-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-thunderhawk-gunship`, `eq-thunderhawk-gunship-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-thunderhawk-gunship`, `eq-thunderhawk-gunship-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-thunderhawk-gunship-2`, `eq-thunderhawk-gunship-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-thunderhawk-gunship-2`, `eq-thunderhawk-gunship-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-thunderhawk-gunship-2`, `eq-thunderhawk-gunship-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-thunderhawk-gunship-3`, `eq-thunderhawk-gunship-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-thunderhawk-gunship-3`, `eq-thunderhawk-gunship-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-thunderhawk-gunship-3`, `eq-thunderhawk-gunship-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-thunderhawk-gunship-4`, `eq-thunderhawk-gunship-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-thunderhawk-gunship-4`, `eq-thunderhawk-gunship-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-thunderhawk-gunship-4`, `eq-thunderhawk-gunship-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-thunderhawk-gunship-5`, `eq-thunderhawk-gunship-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-thunderhawk-gunship-5`, `eq-thunderhawk-gunship-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-thunderhawk-gunship-5`, `eq-thunderhawk-gunship-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-thunderhawk-gunship-6`, `eq-thunderhawk-gunship-6-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-thunderhawk-gunship-6`, `eq-thunderhawk-gunship-6-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-thunderhawk-gunship-6`, `eq-thunderhawk-gunship-6-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-thunderhawk-transporter`, `eq-thunderhawk-transporter-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-tiger-shark`, `eq-tiger-shark-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-tiger-shark`, `eq-tiger-shark-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-tiger-shark`, `eq-tiger-shark-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-tiger-shark`, `eq-tiger-shark-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-tormentbringer`, `eq-tormentbringer-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-toxicrene`, `eq-toxicrene-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-triarch-praetorians`, `eq-triarch-praetorians-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-triarch-stalker`, `eq-triarch-stalker-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-troupe`, `eq-troupe-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-troupe-2`, `eq-troupe-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-troupe-master`, `eq-troupe-master-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-troupe-master-2`, `eq-troupe-master-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-tx42-piranha`, `eq-tx42-piranha-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-typhus`, `eq-typhus-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-ulrik-the-slayer`, `eq-ulrik-the-slayer-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-uthar-the-destined`, `eq-uthar-the-destined-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-valerian`, `eq-valerian-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-valkyrie-sky-talon`, `eq-valkyrie-sky-talon-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-vampire-hunter`, `eq-vampire-hunter-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-vampire-raider`, `eq-vampire-raider-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-vashtorr-the-arkifane`, `eq-vashtorr-the-arkifane-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-venatari-custodians`, `eq-venatari-custodians-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-vendetta-gunship`, `eq-vendetta-gunship-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-venerable-land-raider`, `eq-venerable-land-raider-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-venomcrawler`, `eq-venomcrawler-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-victrix-honour-guard`, `eq-victrix-honour-guard-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-vindicator-laser-destroyer`, `eq-vindicator-laser-destroyer-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-voidraven-bomber`, `eq-voidraven-bomber-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-voidweaver`, `eq-voidweaver-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-voidweaver-2`, `eq-voidweaver-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-voss-pattern-lightning`, `eq-voss-pattern-lightning-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-vulture-gunship`, `eq-vulture-gunship-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-vulture-gunship`, `eq-vulture-gunship-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-war-dog-executioner`, `eq-war-dog-executioner-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-war-dog-huntsman`, `eq-war-dog-huntsman-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-war-walkers`, `eq-war-walkers-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-warbringer-nemesis-titan`, `eq-warbringer-nemesis-titan-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-warbringer-nemesis-titan`, `eq-warbringer-nemesis-titan-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-wardens-of-ultramar`, `eq-wardens-of-ultramar-2` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-wardens-of-ultramar`, `eq-wardens-of-ultramar-3` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-warhound-titan`, `eq-warhound-titan-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-warlord-titan`, `eq-warlord-titan-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-warlord-titan`, `eq-warlord-titan-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-warlord-titan`, `eq-warlord-titan-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-warp-hunter`, `eq-warp-hunter-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-warpsmith`, `eq-warpsmith-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-watch-master`, `eq-watch-master-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-watch-master-2`, `eq-watch-master-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-wazdakka-gutsmek`, `eq-wazdakka-gutsmek-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-webway-gate`, `eq-webway-gate-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-wolf-guard-battle-leader`, `eq-wolf-guard-battle-leader-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-wolf-guard-headtakers`, `eq-wolf-guard-headtakers-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-wolf-scouts`, `eq-wolf-scouts-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-wolf-scouts`, `eq-wolf-scouts-2` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-wraithknight`, `eq-wraithknight-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-wraithknight-with-ghostglaive`, `eq-wraithknight-with-ghostglaive-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-wraithknight-with-ghostglaive`, `eq-wraithknight-with-ghostglaive-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-wraithlord`, `eq-wraithlord-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-wraithseer`, `eq-wraithseer-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-wulfen`, `eq-wulfen-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-wulfen-dreadnought`, `eq-wulfen-dreadnought-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-wulfen-with-storm-shields`, `eq-wulfen-with-storm-shields-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-xiphon-interceptor`, `eq-xiphon-interceptor-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-xiphon-interceptor-2`, `eq-xiphon-interceptor-2-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-xiphon-interceptor-3`, `eq-xiphon-interceptor-3-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-xiphon-interceptor-4`, `eq-xiphon-interceptor-4-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-xiphon-interceptor-5`, `eq-xiphon-interceptor-5-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-ynnari-archon`, `eq-ynnari-archon-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-yvahra-battlesuit`, `eq-yvahra-battlesuit-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-zarakynel`, `eq-zarakynel-1` | — |
| `EQP-ITEM-UNLINKED` | advisory | `ds-zoanthropes`, `eq-zoanthropes-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-acastus-knight-porphyrion`, `oc-acastus-knight-porphyrion-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-achilles-ridgerunners`, `oc-achilles-ridgerunners-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-achilles-ridgerunners`, `oc-achilles-ridgerunners-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-achilles-ridgerunners`, `oc-achilles-ridgerunners-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-achilles-ridgerunners`, `oc-achilles-ridgerunners-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-acolyte-hybrids-with-autopistols`, `oc-acolyte-hybrids-with-autopistols-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-acolyte-hybrids-with-autopistols`, `oc-acolyte-hybrids-with-autopistols-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-acolyte-hybrids-with-autopistols`, `oc-acolyte-hybrids-with-autopistols-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-acolyte-hybrids-with-hand-flamers`, `oc-acolyte-hybrids-with-hand-flamers-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-allarus-custodians`, `oc-allarus-custodians-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-allarus-custodians`, `oc-allarus-custodians-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-allarus-custodians`, `oc-allarus-custodians-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-ancient-in-terminator-armour`, `oc-ancient-in-terminator-armour-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-ancient-in-terminator-armour-2`, `oc-ancient-in-terminator-armour-2-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-ancient-in-terminator-armour-3`, `oc-ancient-in-terminator-armour-3-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-ancient-in-terminator-armour-4`, `oc-ancient-in-terminator-armour-4-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-ancient-in-terminator-armour-5`, `oc-ancient-in-terminator-armour-5-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-ancient-in-terminator-armour-6`, `oc-ancient-in-terminator-armour-6-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-ancient-on-bike`, `oc-ancient-on-bike-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-aquila-kill-team`, `oc-aquila-kill-team-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-aquila-kill-team`, `oc-aquila-kill-team-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-aquila-kill-team`, `oc-aquila-kill-team-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-archaeopter-fusilave`, `oc-archaeopter-fusilave-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-archaeopter-stratoraptor`, `oc-archaeopter-stratoraptor-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-archaeopter-transvector`, `oc-archaeopter-transvector-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-archon`, `oc-archon-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-arkurian-stormhammer`, `oc-arkurian-stormhammer-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-arkurian-stormhammer`, `oc-arkurian-stormhammer-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-arkurian-stormhammer`, `oc-arkurian-stormhammer-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-arkurian-stormhammer-2`, `oc-arkurian-stormhammer-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-arkurian-stormhammer-2`, `oc-arkurian-stormhammer-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-arkurian-stormhammer-2`, `oc-arkurian-stormhammer-2-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-armoured-sentinels`, `oc-armoured-sentinels-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-armoured-sentinels`, `oc-armoured-sentinels-1-5` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-armoured-sentinels-2`, `oc-armoured-sentinels-2-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-armoured-sentinels-2`, `oc-armoured-sentinels-2-1-5` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-assault-intercessor-squad`, `oc-assault-intercessor-squad-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-assault-intercessor-squad-2`, `oc-assault-intercessor-squad-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-assault-intercessor-squad-3`, `oc-assault-intercessor-squad-3-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-assault-intercessor-squad-4`, `oc-assault-intercessor-squad-4-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-assault-intercessor-squad-5`, `oc-assault-intercessor-squad-5-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-assault-intercessor-squad-6`, `oc-assault-intercessor-squad-6-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-assault-intercessors-with-jump-packs`, `oc-assault-intercessors-with-jump-packs-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-assault-intercessors-with-jump-packs`, `oc-assault-intercessors-with-jump-packs-3-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-assault-intercessors-with-jump-packs-2`, `oc-assault-intercessors-with-jump-packs-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-assault-intercessors-with-jump-packs-2`, `oc-assault-intercessors-with-jump-packs-2-3-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-assault-intercessors-with-jump-packs-3`, `oc-assault-intercessors-with-jump-packs-3-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-assault-intercessors-with-jump-packs-3`, `oc-assault-intercessors-with-jump-packs-3-3-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-assault-intercessors-with-jump-packs-4`, `oc-assault-intercessors-with-jump-packs-4-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-assault-intercessors-with-jump-packs-4`, `oc-assault-intercessors-with-jump-packs-4-3-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-assault-intercessors-with-jump-packs-5`, `oc-assault-intercessors-with-jump-packs-5-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-assault-intercessors-with-jump-packs-5`, `oc-assault-intercessors-with-jump-packs-5-3-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-assault-intercessors-with-jump-packs-6`, `oc-assault-intercessors-with-jump-packs-6-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-assault-intercessors-with-jump-packs-6`, `oc-assault-intercessors-with-jump-packs-6-3-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-assault-squad`, `oc-assault-squad-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-assault-squad`, `oc-assault-squad-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-assault-squad`, `oc-assault-squad-4-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-assault-squad-with-jump-packs`, `oc-assault-squad-with-jump-packs-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-assault-squad-with-jump-packs`, `oc-assault-squad-with-jump-packs-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-assault-squad-with-jump-packs`, `oc-assault-squad-with-jump-packs-4-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-astartes-servitors`, `oc-astartes-servitors-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-astraeus`, `oc-astraeus-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-astraeus-2`, `oc-astraeus-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-astraeus-3`, `oc-astraeus-3-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-astraeus-4`, `oc-astraeus-4-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-astraeus-5`, `oc-astraeus-5-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-astraeus-6`, `oc-astraeus-6-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-atalan-jackals`, `oc-atalan-jackals-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-autarch`, `oc-autarch-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-autarch-wayleaper`, `oc-autarch-wayleaper-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-ax-1-0-tiger-shark`, `oc-ax-1-0-tiger-shark-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-ax-1-0-tiger-shark`, `oc-ax-1-0-tiger-shark-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-baal-predator`, `oc-baal-predator-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-baal-predator`, `oc-baal-predator-4-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-baneblade`, `oc-baneblade-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-baneblade`, `oc-baneblade-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-baneblade`, `oc-baneblade-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-baneblade`, `oc-baneblade-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-baneblade`, `oc-baneblade-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-baneblade-2`, `oc-baneblade-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-baneblade-2`, `oc-baneblade-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-baneblade-2`, `oc-baneblade-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-baneblade-2`, `oc-baneblade-2-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-baneblade-2`, `oc-baneblade-2-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-banehammer`, `oc-banehammer-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-banehammer`, `oc-banehammer-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-banehammer`, `oc-banehammer-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-banehammer`, `oc-banehammer-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-banehammer`, `oc-banehammer-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-banehammer-2`, `oc-banehammer-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-banehammer-2`, `oc-banehammer-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-banehammer-2`, `oc-banehammer-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-banehammer-2`, `oc-banehammer-2-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-banehammer-2`, `oc-banehammer-2-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-banesword`, `oc-banesword-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-banesword`, `oc-banesword-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-banesword`, `oc-banesword-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-banesword`, `oc-banesword-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-banesword`, `oc-banesword-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-banesword-2`, `oc-banesword-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-banesword-2`, `oc-banesword-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-banesword-2`, `oc-banesword-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-banesword-2`, `oc-banesword-2-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-banesword-2`, `oc-banesword-2-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-barracuda`, `oc-barracuda-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-barracuda`, `oc-barracuda-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-barracuda`, `oc-barracuda-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-battle-sisters-squad`, `oc-battle-sisters-squad-1-6` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-battle-sisters-squad`, `oc-battle-sisters-squad-5-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-battlewagon`, `oc-battlewagon-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-battlewagon`, `oc-battlewagon-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-battlewagon`, `oc-battlewagon-5-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-big-gunz`, `oc-big-gunz-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-big-gunz`, `oc-big-gunz-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-big-mek-in-mega-armour`, `oc-big-mek-in-mega-armour-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-big-mek-in-mega-armour`, `oc-big-mek-in-mega-armour-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-big-mek-on-warbike`, `oc-big-mek-on-warbike-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-big-mek-with-kustom-force-field`, `oc-big-mek-with-kustom-force-field-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-big-mek-with-shokk-attack-gun`, `oc-big-mek-with-shokk-attack-gun-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-big-trakk`, `oc-big-trakk-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-big-trakk`, `oc-big-trakk-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-biged-bossbunka`, `oc-biged-bossbunka-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-bike-squad`, `oc-bike-squad-1-7` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-bike-squad`, `oc-bike-squad-3-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-bike-squad`, `oc-bike-squad-3-5` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-bjorn-the-fell-handed`, `oc-bjorn-the-fell-handed-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-bladeguard-veteran-squad`, `oc-bladeguard-veteran-squad-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-bladeguard-veteran-squad-2`, `oc-bladeguard-veteran-squad-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-bladeguard-veteran-squad-3`, `oc-bladeguard-veteran-squad-3-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-bladeguard-veteran-squad-4`, `oc-bladeguard-veteran-squad-4-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-bladeguard-veteran-squad-5`, `oc-bladeguard-veteran-squad-5-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-bladeguard-veteran-squad-6`, `oc-bladeguard-veteran-squad-6-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-blood-claws`, `oc-blood-claws-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-bloodcrushers`, `oc-bloodcrushers-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-bloodcrushers`, `oc-bloodcrushers-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-bloodcrushers-2`, `oc-bloodcrushers-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-bloodcrushers-2`, `oc-bloodcrushers-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-bloodletters`, `oc-bloodletters-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-bloodletters`, `oc-bloodletters-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-bloodletters-2`, `oc-bloodletters-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-bloodletters-2`, `oc-bloodletters-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-breacher-team`, `oc-breacher-team-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-breacher-team`, `oc-breacher-team-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-breacher-team`, `oc-breacher-team-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-breacher-team`, `oc-breacher-team-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-brotherhood-terminator-squad`, `oc-brotherhood-terminator-squad-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-brotherhood-terminator-squad`, `oc-brotherhood-terminator-squad-3-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-brotherhood-terminator-squad`, `oc-brotherhood-terminator-squad-3-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-brotherhood-terminator-squad`, `oc-brotherhood-terminator-squad-3-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-brutalis-dreadnought`, `oc-brutalis-dreadnought-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-brutalis-dreadnought-2`, `oc-brutalis-dreadnought-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-brutalis-dreadnought-3`, `oc-brutalis-dreadnought-3-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-brutalis-dreadnought-4`, `oc-brutalis-dreadnought-4-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-brutalis-dreadnought-5`, `oc-brutalis-dreadnought-5-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-brutalis-dreadnought-6`, `oc-brutalis-dreadnought-6-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-bullgryn-squad`, `oc-bullgryn-squad-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-bullgryn-squad`, `oc-bullgryn-squad-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cadian-castellan`, `oc-cadian-castellan-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cadian-castellan-2`, `oc-cadian-castellan-2-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cadian-command-squad`, `oc-cadian-command-squad-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cadian-command-squad`, `oc-cadian-command-squad-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cadian-command-squad`, `oc-cadian-command-squad-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cadian-command-squad`, `oc-cadian-command-squad-3-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cadian-command-squad`, `oc-cadian-command-squad-4-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cadian-command-squad`, `oc-cadian-command-squad-4-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cadian-command-squad-2`, `oc-cadian-command-squad-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cadian-command-squad-2`, `oc-cadian-command-squad-2-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cadian-command-squad-2`, `oc-cadian-command-squad-2-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cadian-command-squad-2`, `oc-cadian-command-squad-2-3-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cadian-command-squad-2`, `oc-cadian-command-squad-2-4-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cadian-command-squad-2`, `oc-cadian-command-squad-2-4-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cadian-heavy-weapons-squad`, `oc-cadian-heavy-weapons-squad-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cadian-heavy-weapons-squad-2`, `oc-cadian-heavy-weapons-squad-2-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cadian-shock-troops`, `oc-cadian-shock-troops-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cadian-shock-troops`, `oc-cadian-shock-troops-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cadian-shock-troops`, `oc-cadian-shock-troops-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cadian-shock-troops-2`, `oc-cadian-shock-troops-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cadian-shock-troops-2`, `oc-cadian-shock-troops-2-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cadian-shock-troops-2`, `oc-cadian-shock-troops-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cadre-fireblade`, `oc-cadre-fireblade-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cadre-fireblade`, `oc-cadre-fireblade-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cadre-fireblade`, `oc-cadre-fireblade-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-canoness`, `oc-canoness-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-canoptek-macrocytes`, `oc-canoptek-macrocytes-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-canoptek-macrocytes`, `oc-canoptek-macrocytes-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain`, `oc-captain-1-5` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain`, `oc-captain-1-6` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain`, `oc-captain-1-7` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain`, `oc-captain-1-7` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-2`, `oc-captain-2-1-5` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-2`, `oc-captain-2-1-6` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-2`, `oc-captain-2-1-7` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-2`, `oc-captain-2-1-7` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-3`, `oc-captain-3-1-5` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-3`, `oc-captain-3-1-6` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-3`, `oc-captain-3-1-7` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-3`, `oc-captain-3-1-7` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-4`, `oc-captain-4-1-5` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-4`, `oc-captain-4-1-6` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-4`, `oc-captain-4-1-7` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-4`, `oc-captain-4-1-7` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-5`, `oc-captain-5-1-5` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-5`, `oc-captain-5-1-6` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-5`, `oc-captain-5-1-7` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-5`, `oc-captain-5-1-7` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-6`, `oc-captain-6-1-5` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-6`, `oc-captain-6-1-6` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-6`, `oc-captain-6-1-7` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-6`, `oc-captain-6-1-7` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-in-gravis-armour`, `oc-captain-in-gravis-armour-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-in-gravis-armour`, `oc-captain-in-gravis-armour-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-in-gravis-armour`, `oc-captain-in-gravis-armour-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-in-gravis-armour-2`, `oc-captain-in-gravis-armour-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-in-gravis-armour-2`, `oc-captain-in-gravis-armour-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-in-gravis-armour-2`, `oc-captain-in-gravis-armour-2-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-in-gravis-armour-3`, `oc-captain-in-gravis-armour-3-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-in-gravis-armour-3`, `oc-captain-in-gravis-armour-3-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-in-gravis-armour-3`, `oc-captain-in-gravis-armour-3-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-in-gravis-armour-4`, `oc-captain-in-gravis-armour-4-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-in-gravis-armour-4`, `oc-captain-in-gravis-armour-4-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-in-gravis-armour-4`, `oc-captain-in-gravis-armour-4-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-in-gravis-armour-5`, `oc-captain-in-gravis-armour-5-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-in-gravis-armour-5`, `oc-captain-in-gravis-armour-5-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-in-gravis-armour-5`, `oc-captain-in-gravis-armour-5-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-in-gravis-armour-6`, `oc-captain-in-gravis-armour-6-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-in-gravis-armour-6`, `oc-captain-in-gravis-armour-6-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-in-gravis-armour-6`, `oc-captain-in-gravis-armour-6-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-on-bike`, `oc-captain-on-bike-1-5` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-on-bike`, `oc-captain-on-bike-1-7` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-on-bike`, `oc-captain-on-bike-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-with-jump-pack`, `oc-captain-with-jump-pack-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-with-jump-pack`, `oc-captain-with-jump-pack-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-with-jump-pack-2`, `oc-captain-with-jump-pack-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-with-jump-pack-2`, `oc-captain-with-jump-pack-2-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-with-jump-pack-3`, `oc-captain-with-jump-pack-3-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-with-jump-pack-3`, `oc-captain-with-jump-pack-3-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-with-jump-pack-4`, `oc-captain-with-jump-pack-4-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-with-jump-pack-4`, `oc-captain-with-jump-pack-4-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-with-jump-pack-5`, `oc-captain-with-jump-pack-5-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-with-jump-pack-5`, `oc-captain-with-jump-pack-5-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-with-jump-pack-6`, `oc-captain-with-jump-pack-6-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-captain-with-jump-pack-6`, `oc-captain-with-jump-pack-6-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-carnodon`, `oc-carnodon-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-carnodon`, `oc-carnodon-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-carnodon`, `oc-carnodon-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-carnodon`, `oc-carnodon-2-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-carnodon`, `oc-carnodon-2-5` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-carnodon-2`, `oc-carnodon-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-carnodon-2`, `oc-carnodon-2-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-carnodon-2`, `oc-carnodon-2-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-carnodon-2`, `oc-carnodon-2-2-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-carnodon-2`, `oc-carnodon-2-2-5` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-catachan-command-squad`, `oc-catachan-command-squad-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-catachan-command-squad`, `oc-catachan-command-squad-1-5` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-catachan-command-squad`, `oc-catachan-command-squad-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-catachan-command-squad`, `oc-catachan-command-squad-5-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-catachan-command-squad-2`, `oc-catachan-command-squad-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-catachan-command-squad-2`, `oc-catachan-command-squad-2-1-5` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-catachan-command-squad-2`, `oc-catachan-command-squad-2-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-catachan-command-squad-2`, `oc-catachan-command-squad-2-5-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-catachan-heavy-weapons-squad`, `oc-catachan-heavy-weapons-squad-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-catachan-heavy-weapons-squad-2`, `oc-catachan-heavy-weapons-squad-2-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-catachan-jungle-fighters`, `oc-catachan-jungle-fighters-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-catachan-jungle-fighters-2`, `oc-catachan-jungle-fighters-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-catacomb-command-barge`, `oc-catacomb-command-barge-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-celestian-insidiants`, `oc-celestian-insidiants-5-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-celestian-sacresants`, `oc-celestian-sacresants-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-centurion-assault-squad`, `oc-centurion-assault-squad-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-centurion-assault-squad-2`, `oc-centurion-assault-squad-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-centurion-assault-squad-3`, `oc-centurion-assault-squad-3-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-centurion-assault-squad-4`, `oc-centurion-assault-squad-4-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-centurion-assault-squad-5`, `oc-centurion-assault-squad-5-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-centurion-assault-squad-6`, `oc-centurion-assault-squad-6-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cerberus`, `oc-cerberus-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cerberus`, `oc-cerberus-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cerberus-2`, `oc-cerberus-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cerberus-2`, `oc-cerberus-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cerberus-3`, `oc-cerberus-3-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cerberus-3`, `oc-cerberus-3-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cerberus-4`, `oc-cerberus-4-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cerberus-4`, `oc-cerberus-4-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cerberus-5`, `oc-cerberus-5-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cerberus-5`, `oc-cerberus-5-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-bikers`, `oc-chaos-bikers-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-bikers`, `oc-chaos-bikers-3-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-bikers`, `oc-chaos-bikers-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-deimos-predator`, `oc-chaos-deimos-predator-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-deimos-predator`, `oc-chaos-deimos-predator-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-deimos-predator`, `oc-chaos-deimos-predator-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-lord`, `oc-chaos-lord-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-lord-2`, `oc-chaos-lord-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-lord-on-bike`, `oc-chaos-lord-on-bike-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-lord-on-bike`, `oc-chaos-lord-on-bike-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-lord-on-disc-of-tzeentch`, `oc-chaos-lord-on-disc-of-tzeentch-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-lord-on-disc-of-tzeentch`, `oc-chaos-lord-on-disc-of-tzeentch-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-lord-on-disc-of-tzeentch-2`, `oc-chaos-lord-on-disc-of-tzeentch-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-lord-on-disc-of-tzeentch-2`, `oc-chaos-lord-on-disc-of-tzeentch-2-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-lord-on-disc-of-tzeentch-3`, `oc-chaos-lord-on-disc-of-tzeentch-3-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-lord-on-disc-of-tzeentch-3`, `oc-chaos-lord-on-disc-of-tzeentch-3-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-lord-on-juggernaut`, `oc-chaos-lord-on-juggernaut-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-lord-on-juggernaut`, `oc-chaos-lord-on-juggernaut-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-lord-on-juggernaut-2`, `oc-chaos-lord-on-juggernaut-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-lord-on-juggernaut-2`, `oc-chaos-lord-on-juggernaut-2-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-lord-on-palanquin-of-nurgle`, `oc-chaos-lord-on-palanquin-of-nurgle-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-lord-on-palanquin-of-nurgle`, `oc-chaos-lord-on-palanquin-of-nurgle-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-lord-on-palanquin-of-nurgle-2`, `oc-chaos-lord-on-palanquin-of-nurgle-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-lord-on-palanquin-of-nurgle-2`, `oc-chaos-lord-on-palanquin-of-nurgle-2-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-lord-on-palanquin-of-nurgle-3`, `oc-chaos-lord-on-palanquin-of-nurgle-3-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-lord-on-palanquin-of-nurgle-3`, `oc-chaos-lord-on-palanquin-of-nurgle-3-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-lord-on-steed-of-slaanesh`, `oc-chaos-lord-on-steed-of-slaanesh-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-lord-on-steed-of-slaanesh`, `oc-chaos-lord-on-steed-of-slaanesh-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-lord-on-steed-of-slaanesh-2`, `oc-chaos-lord-on-steed-of-slaanesh-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-lord-on-steed-of-slaanesh-2`, `oc-chaos-lord-on-steed-of-slaanesh-2-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-lord-with-jump-pack`, `oc-chaos-lord-with-jump-pack-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-lord-with-jump-pack-2`, `oc-chaos-lord-with-jump-pack-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-predator-annihilator`, `oc-chaos-predator-annihilator-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-predator-annihilator`, `oc-chaos-predator-annihilator-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-predator-annihilator-2`, `oc-chaos-predator-annihilator-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-predator-annihilator-2`, `oc-chaos-predator-annihilator-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-predator-annihilator-3`, `oc-chaos-predator-annihilator-3-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-predator-annihilator-3`, `oc-chaos-predator-annihilator-3-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-predator-annihilator-4`, `oc-chaos-predator-annihilator-4-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-predator-annihilator-4`, `oc-chaos-predator-annihilator-4-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-predator-destructor`, `oc-chaos-predator-destructor-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-predator-destructor`, `oc-chaos-predator-destructor-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-predator-destructor-2`, `oc-chaos-predator-destructor-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-predator-destructor-2`, `oc-chaos-predator-destructor-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-predator-destructor-3`, `oc-chaos-predator-destructor-3-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-predator-destructor-3`, `oc-chaos-predator-destructor-3-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-predator-destructor-4`, `oc-chaos-predator-destructor-4-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-predator-destructor-4`, `oc-chaos-predator-destructor-4-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-questoris-knight-magaera`, `oc-chaos-questoris-knight-magaera-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-questoris-knight-styrix`, `oc-chaos-questoris-knight-styrix-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-rhino`, `oc-chaos-rhino-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-rhino-2`, `oc-chaos-rhino-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-rhino-2`, `oc-chaos-rhino-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-rhino-3`, `oc-chaos-rhino-3-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-rhino-4`, `oc-chaos-rhino-4-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-rhino-4`, `oc-chaos-rhino-4-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-rhino-5`, `oc-chaos-rhino-5-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaos-rhino-5`, `oc-chaos-rhino-5-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaplain-in-terminator-armour`, `oc-chaplain-in-terminator-armour-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaplain-in-terminator-armour-2`, `oc-chaplain-in-terminator-armour-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaplain-in-terminator-armour-3`, `oc-chaplain-in-terminator-armour-3-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaplain-in-terminator-armour-4`, `oc-chaplain-in-terminator-armour-4-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaplain-in-terminator-armour-5`, `oc-chaplain-in-terminator-armour-5-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaplain-in-terminator-armour-6`, `oc-chaplain-in-terminator-armour-6-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaplain-venerable-dreadnought`, `oc-chaplain-venerable-dreadnought-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaplain-venerable-dreadnought`, `oc-chaplain-venerable-dreadnought-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaplain-with-jump-pack`, `oc-chaplain-with-jump-pack-1-6` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaplain-with-jump-pack-2`, `oc-chaplain-with-jump-pack-2-1-6` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaplain-with-jump-pack-3`, `oc-chaplain-with-jump-pack-3-1-6` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaplain-with-jump-pack-4`, `oc-chaplain-with-jump-pack-4-1-6` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaplain-with-jump-pack-5`, `oc-chaplain-with-jump-pack-5-1-6` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chaplain-with-jump-pack-6`, `oc-chaplain-with-jump-pack-6-1-6` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chinork-warkopta`, `oc-chinork-warkopta-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chinork-warkopta`, `oc-chinork-warkopta-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chosen`, `oc-chosen-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chosen`, `oc-chosen-5-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chosen-2`, `oc-chosen-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-chosen-2`, `oc-chosen-2-5-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cobra`, `oc-cobra-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-command-squad`, `oc-command-squad-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-command-squad`, `oc-command-squad-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-command-squad`, `oc-command-squad-5-11` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-command-squad`, `oc-command-squad-5-13` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-command-squad`, `oc-command-squad-5-14` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-command-squad`, `oc-command-squad-5-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-commander-in-coldstar-battlesuit`, `oc-commander-in-coldstar-battlesuit-1-10` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-commander-in-coldstar-battlesuit`, `oc-commander-in-coldstar-battlesuit-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-commander-in-coldstar-battlesuit`, `oc-commander-in-coldstar-battlesuit-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-commander-in-coldstar-battlesuit`, `oc-commander-in-coldstar-battlesuit-1-8` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-commander-in-coldstar-battlesuit`, `oc-commander-in-coldstar-battlesuit-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-commander-in-coldstar-battlesuit`, `oc-commander-in-coldstar-battlesuit-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-commander-in-coldstar-battlesuit`, `oc-commander-in-coldstar-battlesuit-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-commander-in-coldstar-battlesuit`, `oc-commander-in-coldstar-battlesuit-3-10` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-commander-in-coldstar-battlesuit`, `oc-commander-in-coldstar-battlesuit-3-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-commander-in-coldstar-battlesuit`, `oc-commander-in-coldstar-battlesuit-3-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-commander-in-coldstar-battlesuit`, `oc-commander-in-coldstar-battlesuit-3-8` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-commander-in-crisis-battlesuit`, `oc-commander-in-crisis-battlesuit-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-commander-in-crisis-battlesuit`, `oc-commander-in-crisis-battlesuit-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-commander-in-crisis-battlesuit`, `oc-commander-in-crisis-battlesuit-1-7` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-commander-in-crisis-battlesuit`, `oc-commander-in-crisis-battlesuit-1-9` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-commander-in-crisis-battlesuit`, `oc-commander-in-crisis-battlesuit-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-commander-in-crisis-battlesuit`, `oc-commander-in-crisis-battlesuit-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-commander-in-crisis-battlesuit`, `oc-commander-in-crisis-battlesuit-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-commander-in-crisis-battlesuit`, `oc-commander-in-crisis-battlesuit-3-10` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-commander-in-crisis-battlesuit`, `oc-commander-in-crisis-battlesuit-3-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-commander-in-crisis-battlesuit`, `oc-commander-in-crisis-battlesuit-3-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-commander-in-crisis-battlesuit`, `oc-commander-in-crisis-battlesuit-3-8` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-commander-in-enforcer-battlesuit`, `oc-commander-in-enforcer-battlesuit-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-commander-in-enforcer-battlesuit`, `oc-commander-in-enforcer-battlesuit-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-commander-in-enforcer-battlesuit`, `oc-commander-in-enforcer-battlesuit-1-7` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-commander-in-enforcer-battlesuit`, `oc-commander-in-enforcer-battlesuit-1-9` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-commander-in-enforcer-battlesuit`, `oc-commander-in-enforcer-battlesuit-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-commander-in-enforcer-battlesuit`, `oc-commander-in-enforcer-battlesuit-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-commander-in-enforcer-battlesuit`, `oc-commander-in-enforcer-battlesuit-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-commander-in-enforcer-battlesuit`, `oc-commander-in-enforcer-battlesuit-3-10` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-commander-in-enforcer-battlesuit`, `oc-commander-in-enforcer-battlesuit-3-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-commander-in-enforcer-battlesuit`, `oc-commander-in-enforcer-battlesuit-3-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-commander-in-enforcer-battlesuit`, `oc-commander-in-enforcer-battlesuit-3-8` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-commissar`, `oc-commissar-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-company-veterans-on-bikes`, `oc-company-veterans-on-bikes-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-contemptor-achillus-dreadnought`, `oc-contemptor-achillus-dreadnought-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-contemptor-achillus-dreadnought`, `oc-contemptor-achillus-dreadnought-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-corsair-reaver-band`, `oc-corsair-reaver-band-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-corsair-reaver-band-2`, `oc-corsair-reaver-band-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-corsair-voidreavers`, `oc-corsair-voidreavers-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-corsair-voidreavers-2`, `oc-corsair-voidreavers-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-corsair-voidscarred`, `oc-corsair-voidscarred-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-corsair-voidscarred`, `oc-corsair-voidscarred-8-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-corsair-voidscarred-2`, `oc-corsair-voidscarred-2-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-corsair-voidscarred-2`, `oc-corsair-voidscarred-2-8-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-corvus-blackstar`, `oc-corvus-blackstar-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-corvus-blackstar`, `oc-corvus-blackstar-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-corvus-blackstar`, `oc-corvus-blackstar-4-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-corvus-blackstar-2`, `oc-corvus-blackstar-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-corvus-blackstar-2`, `oc-corvus-blackstar-2-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-corvus-blackstar-2`, `oc-corvus-blackstar-2-4-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-crimson-hunter`, `oc-crimson-hunter-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-crisis-battlesuits`, `oc-crisis-battlesuits-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-crisis-battlesuits`, `oc-crisis-battlesuits-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-crisis-battlesuits`, `oc-crisis-battlesuits-1-7` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-crisis-battlesuits`, `oc-crisis-battlesuits-1-9` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-crisis-battlesuits`, `oc-crisis-battlesuits-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-crisis-battlesuits`, `oc-crisis-battlesuits-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-crisis-battlesuits`, `oc-crisis-battlesuits-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-crisis-fireknife-battlesuits`, `oc-crisis-fireknife-battlesuits-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-crisis-fireknife-battlesuits`, `oc-crisis-fireknife-battlesuits-3-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-crisis-fireknife-battlesuits`, `oc-crisis-fireknife-battlesuits-3-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-crisis-starscythe-battlesuits`, `oc-crisis-starscythe-battlesuits-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-crisis-starscythe-battlesuits`, `oc-crisis-starscythe-battlesuits-3-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-crisis-starscythe-battlesuits`, `oc-crisis-starscythe-battlesuits-3-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-crisis-sunforge-battlesuits`, `oc-crisis-sunforge-battlesuits-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-crisis-sunforge-battlesuits`, `oc-crisis-sunforge-battlesuits-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-crisis-sunforge-battlesuits`, `oc-crisis-sunforge-battlesuits-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cultist-mob-with-firearms`, `oc-cultist-mob-with-firearms-5-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cultist-mob-with-firearms-2`, `oc-cultist-mob-with-firearms-2-5-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-cultist-mob-with-firearms-3`, `oc-cultist-mob-with-firearms-3-5-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-custodian-guard`, `oc-custodian-guard-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-custodian-guard`, `oc-custodian-guard-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-custodian-guard`, `oc-custodian-guard-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-custodian-guard`, `oc-custodian-guard-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-custodian-guard`, `oc-custodian-guard-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-custodian-guard`, `oc-custodian-guard-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-custodian-guard-with-adrasite-and-pyrithite-spears`, `oc-custodian-guard-with-adrasite-and-pyrithite-spears-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-custodian-guard-with-adrasite-and-pyrithite-spears`, `oc-custodian-guard-with-adrasite-and-pyrithite-spears-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-custodian-wardens`, `oc-custodian-wardens-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-custodian-wardens`, `oc-custodian-wardens-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-custodian-wardens`, `oc-custodian-wardens-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-daemonettes`, `oc-daemonettes-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-daemonettes`, `oc-daemonettes-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-daemonettes-2`, `oc-daemonettes-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-daemonettes-2`, `oc-daemonettes-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-dakkajet`, `oc-dakkajet-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-damned-legionnaires`, `oc-damned-legionnaires-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-damned-legionnaires`, `oc-damned-legionnaires-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-damned-legionnaires`, `oc-damned-legionnaires-3-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-dark-reapers`, `oc-dark-reapers-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-death-company-captain-with-jump-pack`, `oc-death-company-captain-with-jump-pack-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-death-company-dreadnought`, `oc-death-company-dreadnought-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-death-company-dreadnought-with-magna-grapple`, `oc-death-company-dreadnought-with-magna-grapple-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-death-company-marines`, `oc-death-company-marines-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-death-company-marines`, `oc-death-company-marines-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-death-company-marines-with-bolt-rifles`, `oc-death-company-marines-with-bolt-rifles-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-death-company-marines-with-bolt-rifles`, `oc-death-company-marines-with-bolt-rifles-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-death-company-marines-with-boltguns`, `oc-death-company-marines-with-boltguns-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-death-company-marines-with-boltguns-and-jump-packs`, `oc-death-company-marines-with-boltguns-and-jump-packs-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-death-company-marines-with-jump-packs`, `oc-death-company-marines-with-jump-packs-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-death-company-marines-with-jump-packs`, `oc-death-company-marines-with-jump-packs-4-10` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-death-company-marines-with-jump-packs`, `oc-death-company-marines-with-jump-packs-4-11` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-death-company-marines-with-jump-packs`, `oc-death-company-marines-with-jump-packs-4-9` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-death-guard-chaos-lord`, `oc-death-guard-chaos-lord-1-5` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-death-guard-chaos-lord`, `oc-death-guard-chaos-lord-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-death-guard-chaos-lord-in-terminator-armour`, `oc-death-guard-chaos-lord-in-terminator-armour-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-death-guard-cultists`, `oc-death-guard-cultists-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-death-guard-possessed`, `oc-death-guard-possessed-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-death-guard-sorcerer-in-terminator-armour`, `oc-death-guard-sorcerer-in-terminator-armour-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-death-korps-grenadier-squad`, `oc-death-korps-grenadier-squad-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-death-korps-grenadier-squad`, `oc-death-korps-grenadier-squad-1-5` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-death-korps-grenadier-squad-2`, `oc-death-korps-grenadier-squad-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-death-korps-grenadier-squad-2`, `oc-death-korps-grenadier-squad-2-1-5` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-death-korps-of-krieg`, `oc-death-korps-of-krieg-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-death-korps-of-krieg`, `oc-death-korps-of-krieg-1-5` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-death-korps-of-krieg`, `oc-death-korps-of-krieg-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-death-korps-of-krieg`, `oc-death-korps-of-krieg-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-death-korps-of-krieg-2`, `oc-death-korps-of-krieg-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-death-korps-of-krieg-2`, `oc-death-korps-of-krieg-2-1-5` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-death-korps-of-krieg-2`, `oc-death-korps-of-krieg-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-death-korps-of-krieg-2`, `oc-death-korps-of-krieg-2-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-deathshroud-terminators`, `oc-deathshroud-terminators-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-deathshroud-terminators`, `oc-deathshroud-terminators-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-deathwatch-kill-team`, `oc-deathwatch-kill-team-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-deathwatch-kill-team`, `oc-deathwatch-kill-team-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-deathwatch-terminator-squad`, `oc-deathwatch-terminator-squad-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-deathwatch-terminator-squad`, `oc-deathwatch-terminator-squad-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-deathwatch-terminator-squad`, `oc-deathwatch-terminator-squad-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-deathwatch-terminator-squad`, `oc-deathwatch-terminator-squad-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-deathwatch-terminator-squad-2`, `oc-deathwatch-terminator-squad-2-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-deathwatch-terminator-squad-2`, `oc-deathwatch-terminator-squad-2-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-deathwatch-terminator-squad-2`, `oc-deathwatch-terminator-squad-2-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-deathwatch-terminator-squad-2`, `oc-deathwatch-terminator-squad-2-2-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-deathwatch-veterans`, `oc-deathwatch-veterans-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-deathwatch-veterans`, `oc-deathwatch-veterans-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-deathwing-command-squad`, `oc-deathwing-command-squad-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-deathwing-command-squad`, `oc-deathwing-command-squad-5-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-deathwing-knights`, `oc-deathwing-knights-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-deathwing-strikemaster`, `oc-deathwing-strikemaster-1-6` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-deathwing-terminator-squad`, `oc-deathwing-terminator-squad-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-decimator`, `oc-decimator-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-decimator`, `oc-decimator-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-decimus-kill-team`, `oc-decimus-kill-team-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-decimus-kill-team`, `oc-decimus-kill-team-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-decimus-kill-team`, `oc-decimus-kill-team-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-deff-rolla-battle-fortress`, `oc-deff-rolla-battle-fortress-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-deff-rolla-battle-fortress`, `oc-deff-rolla-battle-fortress-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-deffkoptas-with-big-shootas`, `oc-deffkoptas-with-big-shootas-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-defiler`, `oc-defiler-3-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-defiler`, `oc-defiler-4-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-defiler-2`, `oc-defiler-2-3-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-defiler-2`, `oc-defiler-2-4-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-defiler-3`, `oc-defiler-3-3-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-defiler-3`, `oc-defiler-3-4-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-defiler-4`, `oc-defiler-4-3-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-defiler-4`, `oc-defiler-4-4-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-defiler-5`, `oc-defiler-5-3-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-defiler-5`, `oc-defiler-5-4-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-deimos-predator`, `oc-deimos-predator-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-deimos-predator`, `oc-deimos-predator-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-deimos-predator`, `oc-deimos-predator-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-deredeo-dreadnought`, `oc-deredeo-dreadnought-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-deredeo-dreadnought-2`, `oc-deredeo-dreadnought-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-deredeo-dreadnought-3`, `oc-deredeo-dreadnought-3-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-deredeo-dreadnought-4`, `oc-deredeo-dreadnought-4-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-deredeo-dreadnought-5`, `oc-deredeo-dreadnought-5-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-devastator-squad`, `oc-devastator-squad-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-devastator-squad`, `oc-devastator-squad-1-6` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-devastator-squad`, `oc-devastator-squad-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-devastator-squad`, `oc-devastator-squad-2-6` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-devastator-squad-2`, `oc-devastator-squad-2-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-devastator-squad-2`, `oc-devastator-squad-2-1-6` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-devastator-squad-2`, `oc-devastator-squad-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-devastator-squad-2`, `oc-devastator-squad-2-2-6` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-devastator-squad-3`, `oc-devastator-squad-3-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-devastator-squad-3`, `oc-devastator-squad-3-1-6` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-devastator-squad-3`, `oc-devastator-squad-3-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-devastator-squad-3`, `oc-devastator-squad-3-2-6` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-devastator-squad-4`, `oc-devastator-squad-4-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-devastator-squad-4`, `oc-devastator-squad-4-1-6` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-devastator-squad-4`, `oc-devastator-squad-4-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-devastator-squad-4`, `oc-devastator-squad-4-2-6` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-devilfish`, `oc-devilfish-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-devilfish`, `oc-devilfish-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-dire-avengers`, `oc-dire-avengers-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-dominion-squad`, `oc-dominion-squad-1-6` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-dominion-squad`, `oc-dominion-squad-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-dominus-armoured-siege-bombard`, `oc-dominus-armoured-siege-bombard-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-dominus-armoured-siege-bombard`, `oc-dominus-armoured-siege-bombard-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-dominus-armoured-siege-bombard`, `oc-dominus-armoured-siege-bombard-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-dominus-armoured-siege-bombard-2`, `oc-dominus-armoured-siege-bombard-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-dominus-armoured-siege-bombard-2`, `oc-dominus-armoured-siege-bombard-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-dominus-armoured-siege-bombard-2`, `oc-dominus-armoured-siege-bombard-2-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-doomhammer`, `oc-doomhammer-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-doomhammer`, `oc-doomhammer-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-doomhammer`, `oc-doomhammer-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-doomhammer`, `oc-doomhammer-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-doomhammer`, `oc-doomhammer-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-doomhammer-2`, `oc-doomhammer-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-doomhammer-2`, `oc-doomhammer-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-doomhammer-2`, `oc-doomhammer-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-doomhammer-2`, `oc-doomhammer-2-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-doomhammer-2`, `oc-doomhammer-2-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-dragon-knights`, `oc-dragon-knights-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-dreadnought`, `oc-dreadnought-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-dreadnought`, `oc-dreadnought-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-dreadnought-2`, `oc-dreadnought-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-dreadnought-2`, `oc-dreadnought-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-dreadnought-3`, `oc-dreadnought-3-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-dreadnought-3`, `oc-dreadnought-3-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-dreadnought-4`, `oc-dreadnought-4-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-dreadnought-4`, `oc-dreadnought-4-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-dreadnought-5`, `oc-dreadnought-5-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-dreadnought-5`, `oc-dreadnought-5-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-dreadnought-6`, `oc-dreadnought-6-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-dreadnought-6`, `oc-dreadnought-6-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-einhyr-champion`, `oc-einhyr-champion-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-einhyr-hearthguard`, `oc-einhyr-hearthguard-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-ethereal`, `oc-ethereal-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-ethereal`, `oc-ethereal-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-ethereal`, `oc-ethereal-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-ethereal`, `oc-ethereal-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-exaction-squad`, `oc-exaction-squad-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-exaction-squad`, `oc-exaction-squad-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-exaction-squad`, `oc-exaction-squad-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-exaction-squad`, `oc-exaction-squad-5-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-falchion`, `oc-falchion-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-falchion-2`, `oc-falchion-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-falchion-3`, `oc-falchion-3-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-falchion-4`, `oc-falchion-4-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-falchion-5`, `oc-falchion-5-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-falcon`, `oc-falcon-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-farseer`, `oc-farseer-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-farseer-skyrunner`, `oc-farseer-skyrunner-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-fellblade`, `oc-fellblade-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-fellblade`, `oc-fellblade-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-fellblade-2`, `oc-fellblade-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-fellblade-2`, `oc-fellblade-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-fellblade-3`, `oc-fellblade-3-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-fellblade-3`, `oc-fellblade-3-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-fellblade-4`, `oc-fellblade-4-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-fellblade-4`, `oc-fellblade-4-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-fellblade-5`, `oc-fellblade-5-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-fellblade-5`, `oc-fellblade-5-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-fellgor-beastmen`, `oc-fellgor-beastmen-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-fellgor-beastmen`, `oc-fellgor-beastmen-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-fellgor-beastmen-2`, `oc-fellgor-beastmen-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-fellgor-beastmen-2`, `oc-fellgor-beastmen-2-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-fellgor-beastmen-3`, `oc-fellgor-beastmen-3-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-fellgor-beastmen-3`, `oc-fellgor-beastmen-3-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-fighta-bommer`, `oc-fighta-bommer-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-fighta-bommer`, `oc-fighta-bommer-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-fire-raptor-gunship`, `oc-fire-raptor-gunship-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-fire-raptor-gunship`, `oc-fire-raptor-gunship-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-fire-raptor-gunship-2`, `oc-fire-raptor-gunship-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-fire-raptor-gunship-2`, `oc-fire-raptor-gunship-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-fire-raptor-gunship-3`, `oc-fire-raptor-gunship-3-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-fire-raptor-gunship-3`, `oc-fire-raptor-gunship-3-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-fire-raptor-gunship-4`, `oc-fire-raptor-gunship-4-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-fire-raptor-gunship-4`, `oc-fire-raptor-gunship-4-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-fire-raptor-gunship-5`, `oc-fire-raptor-gunship-5-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-fire-raptor-gunship-5`, `oc-fire-raptor-gunship-5-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-flash-gitz`, `oc-flash-gitz-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-foetid-bloat-drone`, `oc-foetid-bloat-drone-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-forgefiend`, `oc-forgefiend-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-forgefiend-2`, `oc-forgefiend-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-forgefiend-3`, `oc-forgefiend-3-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-fortis-kill-team`, `oc-fortis-kill-team-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-fortis-kill-team-2`, `oc-fortis-kill-team-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-fortis-kill-team-2`, `oc-fortis-kill-team-2-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-furioso-dreadnought`, `oc-furioso-dreadnought-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-furioso-dreadnought`, `oc-furioso-dreadnought-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-gargantuan-squiggoth`, `oc-gargantuan-squiggoth-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-ghostkeel-battlesuit`, `oc-ghostkeel-battlesuit-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-ghostkeel-battlesuit`, `oc-ghostkeel-battlesuit-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-gladiator-lancer`, `oc-gladiator-lancer-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-gladiator-lancer-2`, `oc-gladiator-lancer-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-gladiator-lancer-3`, `oc-gladiator-lancer-3-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-gladiator-lancer-4`, `oc-gladiator-lancer-4-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-gladiator-lancer-5`, `oc-gladiator-lancer-5-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-gladiator-lancer-6`, `oc-gladiator-lancer-6-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-gorgon-heavy-transport`, `oc-gorgon-heavy-transport-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-gorgon-heavy-transport`, `oc-gorgon-heavy-transport-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-gorgon-heavy-transport`, `oc-gorgon-heavy-transport-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-gorgon-heavy-transport-2`, `oc-gorgon-heavy-transport-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-gorgon-heavy-transport-2`, `oc-gorgon-heavy-transport-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-gorgon-heavy-transport-2`, `oc-gorgon-heavy-transport-2-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-grand-master-in-nemesis-dreadknight`, `oc-grand-master-in-nemesis-dreadknight-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-great-knarloc`, `oc-great-knarloc-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-great-knarloc`, `oc-great-knarloc-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-grey-hunters`, `oc-grey-hunters-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-grey-knights-dreadnought`, `oc-grey-knights-dreadnought-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-grey-knights-dreadnought`, `oc-grey-knights-dreadnought-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-grey-knights-dreadnought`, `oc-grey-knights-dreadnought-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-grey-knights-dreadnought`, `oc-grey-knights-dreadnought-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-grey-knights-terminator-squad`, `oc-grey-knights-terminator-squad-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-grot-tanks`, `oc-grot-tanks-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-grot-tanks`, `oc-grot-tanks-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-grot-tanks`, `oc-grot-tanks-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-grot-tanks`, `oc-grot-tanks-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-guardian-defenders`, `oc-guardian-defenders-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hammerhead-gunship`, `oc-hammerhead-gunship-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hammerhead-gunship`, `oc-hammerhead-gunship-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hammerhead-gunship`, `oc-hammerhead-gunship-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hammerhead-gunship`, `oc-hammerhead-gunship-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hand-of-the-archon`, `oc-hand-of-the-archon-10-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hand-of-the-archon`, `oc-hand-of-the-archon-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hand-of-the-archon`, `oc-hand-of-the-archon-3-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-havocs`, `oc-havocs-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-havocs`, `oc-havocs-2-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-havocs`, `oc-havocs-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-havocs`, `oc-havocs-3-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-havocs`, `oc-havocs-3-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-havocs`, `oc-havocs-3-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-havocs`, `oc-havocs-3-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-havocs`, `oc-havocs-3-5` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-havocs-2`, `oc-havocs-2-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-havocs-2`, `oc-havocs-2-2-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-havocs-2`, `oc-havocs-2-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-havocs-2`, `oc-havocs-2-3-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-havocs-2`, `oc-havocs-2-3-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-havocs-2`, `oc-havocs-2-3-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-havocs-2`, `oc-havocs-2-3-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-havocs-2`, `oc-havocs-2-3-5` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hearthkyn-warriors`, `oc-hearthkyn-warriors-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hearthkyn-warriors`, `oc-hearthkyn-warriors-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hearthkyn-warriors`, `oc-hearthkyn-warriors-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hearthkyn-warriors`, `oc-hearthkyn-warriors-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hearthkyn-warriors`, `oc-hearthkyn-warriors-2-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hearthkyn-warriors`, `oc-hearthkyn-warriors-2-5` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hearthkyn-warriors`, `oc-hearthkyn-warriors-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-heavy-gun-drones`, `oc-heavy-gun-drones-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hekaton-land-fortress`, `oc-hekaton-land-fortress-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-helbrute-2`, `oc-helbrute-2-1-5` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-helbrute-2`, `oc-helbrute-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hell-blade`, `oc-hell-blade-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hell-blade-2`, `oc-hell-blade-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hell-blade-3`, `oc-hell-blade-3-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hell-blade-4`, `oc-hell-blade-4-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hellblaster-squad`, `oc-hellblaster-squad-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hellblaster-squad-2`, `oc-hellblaster-squad-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hellblaster-squad-3`, `oc-hellblaster-squad-3-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hellblaster-squad-4`, `oc-hellblaster-squad-4-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hellblaster-squad-5`, `oc-hellblaster-squad-5-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hellblaster-squad-6`, `oc-hellblaster-squad-6-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hellhammer`, `oc-hellhammer-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hellhammer`, `oc-hellhammer-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hellhammer`, `oc-hellhammer-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hellhammer`, `oc-hellhammer-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hellhammer`, `oc-hellhammer-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hellhammer-2`, `oc-hellhammer-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hellhammer-2`, `oc-hellhammer-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hellhammer-2`, `oc-hellhammer-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hellhammer-2`, `oc-hellhammer-2-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hellhammer-2`, `oc-hellhammer-2-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hellions`, `oc-hellions-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hernkyn-pioneers`, `oc-hernkyn-pioneers-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hernkyn-pioneers`, `oc-hernkyn-pioneers-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hernkyn-pioneers`, `oc-hernkyn-pioneers-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hornet`, `oc-hornet-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-howling-banshees`, `oc-howling-banshees-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-hybrid-metamorphs`, `oc-hybrid-metamorphs-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-imperial-navy-breachers`, `oc-imperial-navy-breachers-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-impulsor`, `oc-impulsor-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-impulsor`, `oc-impulsor-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-impulsor`, `oc-impulsor-3-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-impulsor`, `oc-impulsor-3-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-impulsor-2`, `oc-impulsor-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-impulsor-2`, `oc-impulsor-2-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-impulsor-2`, `oc-impulsor-2-3-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-impulsor-2`, `oc-impulsor-2-3-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-impulsor-3`, `oc-impulsor-3-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-impulsor-3`, `oc-impulsor-3-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-impulsor-3`, `oc-impulsor-3-3-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-impulsor-3`, `oc-impulsor-3-3-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-impulsor-4`, `oc-impulsor-4-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-impulsor-4`, `oc-impulsor-4-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-impulsor-4`, `oc-impulsor-4-3-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-impulsor-4`, `oc-impulsor-4-3-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-impulsor-5`, `oc-impulsor-5-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-impulsor-5`, `oc-impulsor-5-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-impulsor-5`, `oc-impulsor-5-3-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-impulsor-5`, `oc-impulsor-5-3-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-impulsor-6`, `oc-impulsor-6-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-impulsor-6`, `oc-impulsor-6-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-impulsor-6`, `oc-impulsor-6-3-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-impulsor-6`, `oc-impulsor-6-3-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-inceptor-squad`, `oc-inceptor-squad-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-inceptor-squad-2`, `oc-inceptor-squad-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-inceptor-squad-3`, `oc-inceptor-squad-3-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-inceptor-squad-4`, `oc-inceptor-squad-4-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-inceptor-squad-5`, `oc-inceptor-squad-5-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-inceptor-squad-6`, `oc-inceptor-squad-6-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-incubi`, `oc-incubi-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-incubi`, `oc-incubi-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-incursor-squad`, `oc-incursor-squad-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-incursor-squad-2`, `oc-incursor-squad-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-incursor-squad-3`, `oc-incursor-squad-3-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-incursor-squad-4`, `oc-incursor-squad-4-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-incursor-squad-5`, `oc-incursor-squad-5-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-incursor-squad-6`, `oc-incursor-squad-6-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-indomitor-kill-team-2`, `oc-indomitor-kill-team-2-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-infiltrator-squad`, `oc-infiltrator-squad-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-infiltrator-squad`, `oc-infiltrator-squad-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-infiltrator-squad-2`, `oc-infiltrator-squad-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-infiltrator-squad-2`, `oc-infiltrator-squad-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-infiltrator-squad-3`, `oc-infiltrator-squad-3-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-infiltrator-squad-3`, `oc-infiltrator-squad-3-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-infiltrator-squad-4`, `oc-infiltrator-squad-4-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-infiltrator-squad-4`, `oc-infiltrator-squad-4-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-infiltrator-squad-5`, `oc-infiltrator-squad-5-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-infiltrator-squad-5`, `oc-infiltrator-squad-5-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-infiltrator-squad-6`, `oc-infiltrator-squad-6-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-infiltrator-squad-6`, `oc-infiltrator-squad-6-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-infractors`, `oc-infractors-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-infractors`, `oc-infractors-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-inquisitor`, `oc-inquisitor-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-inquisitor-in-terminator-armour`, `oc-inquisitor-in-terminator-armour-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-inquisitorial-agents`, `oc-inquisitorial-agents-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-inquisitorial-agents`, `oc-inquisitorial-agents-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-inquisitorial-agents`, `oc-inquisitorial-agents-5-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-intercessor-squad`, `oc-intercessor-squad-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-intercessor-squad`, `oc-intercessor-squad-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-intercessor-squad-2`, `oc-intercessor-squad-2-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-intercessor-squad-2`, `oc-intercessor-squad-2-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-intercessor-squad-3`, `oc-intercessor-squad-3-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-intercessor-squad-3`, `oc-intercessor-squad-3-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-intercessor-squad-4`, `oc-intercessor-squad-4-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-intercessor-squad-4`, `oc-intercessor-squad-4-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-intercessor-squad-5`, `oc-intercessor-squad-5-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-intercessor-squad-5`, `oc-intercessor-squad-5-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-intercessor-squad-6`, `oc-intercessor-squad-6-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-intercessor-squad-6`, `oc-intercessor-squad-6-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-ironclad-dreadnought`, `oc-ironclad-dreadnought-5-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-ironclad-dreadnought`, `oc-ironclad-dreadnought-6-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-jakhals`, `oc-jakhals-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-javelin-attack-speeder`, `oc-javelin-attack-speeder-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-javelin-attack-speeder`, `oc-javelin-attack-speeder-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kabalite-warriors`, `oc-kabalite-warriors-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kabalite-warriors`, `oc-kabalite-warriors-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kahl`, `oc-kahl-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kannonwagon`, `oc-kannonwagon-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kapricus-carrier`, `oc-kapricus-carrier-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kasrkin`, `oc-kasrkin-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kasrkin`, `oc-kasrkin-1-5` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kasrkin`, `oc-kasrkin-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kasrkin`, `oc-kasrkin-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kasrkin`, `oc-kasrkin-6-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kasrkin-2`, `oc-kasrkin-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kasrkin-2`, `oc-kasrkin-2-1-5` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kasrkin-2`, `oc-kasrkin-2-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kasrkin-2`, `oc-kasrkin-2-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kasrkin-2`, `oc-kasrkin-2-6-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kataphron-destroyers`, `oc-kataphron-destroyers-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-keeper-of-secrets`, `oc-keeper-of-secrets-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-keeper-of-secrets-2`, `oc-keeper-of-secrets-2-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-khorne-berzerkers`, `oc-khorne-berzerkers-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-khorne-berzerkers`, `oc-khorne-berzerkers-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-khorne-berzerkers`, `oc-khorne-berzerkers-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-khorne-berzerkers-2`, `oc-khorne-berzerkers-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-khorne-berzerkers-2`, `oc-khorne-berzerkers-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-khorne-berzerkers-2`, `oc-khorne-berzerkers-2-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kill-krusha`, `oc-kill-krusha-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kill-krusha`, `oc-kill-krusha-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-knight-castellan`, `oc-knight-castellan-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-knight-desecrator`, `oc-knight-desecrator-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-knight-destrier`, `oc-knight-destrier-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-knight-destrier`, `oc-knight-destrier-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-knight-destrier`, `oc-knight-destrier-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-knight-destrier`, `oc-knight-destrier-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-knight-errant`, `oc-knight-errant-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-knight-paladin`, `oc-knight-paladin-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-knight-preceptor`, `oc-knight-preceptor-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-knight-tyrant`, `oc-knight-tyrant-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-knight-valiant`, `oc-knight-valiant-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-knight-warden`, `oc-knight-warden-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kommandos`, `oc-kommandos-6-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kommandos`, `oc-kommandos-7-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kratos`, `oc-kratos-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kratos`, `oc-kratos-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kratos`, `oc-kratos-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kratos`, `oc-kratos-3-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kratos-2`, `oc-kratos-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kratos-2`, `oc-kratos-2-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kratos-2`, `oc-kratos-2-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kratos-2`, `oc-kratos-2-3-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kratos-3`, `oc-kratos-3-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kratos-3`, `oc-kratos-3-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kratos-3`, `oc-kratos-3-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kratos-3`, `oc-kratos-3-3-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kratos-4`, `oc-kratos-4-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kratos-4`, `oc-kratos-4-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kratos-4`, `oc-kratos-4-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kratos-4`, `oc-kratos-4-3-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kratos-5`, `oc-kratos-5-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kratos-5`, `oc-kratos-5-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kratos-5`, `oc-kratos-5-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kratos-5`, `oc-kratos-5-3-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-krieg-combat-engineers`, `oc-krieg-combat-engineers-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-krieg-combat-engineers`, `oc-krieg-combat-engineers-4-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-krieg-combat-engineers-2`, `oc-krieg-combat-engineers-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-krieg-combat-engineers-2`, `oc-krieg-combat-engineers-2-4-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-krieg-command-squad`, `oc-krieg-command-squad-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-krieg-command-squad`, `oc-krieg-command-squad-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-krieg-command-squad`, `oc-krieg-command-squad-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-krieg-command-squad-2`, `oc-krieg-command-squad-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-krieg-command-squad-2`, `oc-krieg-command-squad-2-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-krieg-command-squad-2`, `oc-krieg-command-squad-2-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-kroot-farstalkers`, `oc-kroot-farstalkers-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-land-raider-proteus`, `oc-land-raider-proteus-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-land-raider-proteus-2`, `oc-land-raider-proteus-2-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-land-raider-proteus-3`, `oc-land-raider-proteus-3-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-land-raider-proteus-4`, `oc-land-raider-proteus-4-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-land-raider-proteus-5`, `oc-land-raider-proteus-5-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-legionaries`, `oc-legionaries-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-legionaries`, `oc-legionaries-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-legionaries`, `oc-legionaries-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-legionaries`, `oc-legionaries-7-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-legionaries`, `oc-legionaries-7-7` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-legionaries`, `oc-legionaries-7-8` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-legionaries-2`, `oc-legionaries-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-legionaries-2`, `oc-legionaries-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-legionaries-2`, `oc-legionaries-2-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-legionaries-2`, `oc-legionaries-2-7-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-legionaries-2`, `oc-legionaries-2-7-7` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-legionaries-2`, `oc-legionaries-2-7-8` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-battle-tank`, `oc-leman-russ-battle-tank-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-battle-tank`, `oc-leman-russ-battle-tank-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-battle-tank`, `oc-leman-russ-battle-tank-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-battle-tank`, `oc-leman-russ-battle-tank-2-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-battle-tank-2`, `oc-leman-russ-battle-tank-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-battle-tank-2`, `oc-leman-russ-battle-tank-2-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-battle-tank-2`, `oc-leman-russ-battle-tank-2-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-battle-tank-2`, `oc-leman-russ-battle-tank-2-2-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-commander`, `oc-leman-russ-commander-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-commander`, `oc-leman-russ-commander-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-commander`, `oc-leman-russ-commander-3-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-commander`, `oc-leman-russ-commander-3-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-commander`, `oc-leman-russ-commander-3-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-commander-2`, `oc-leman-russ-commander-2-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-commander-2`, `oc-leman-russ-commander-2-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-commander-2`, `oc-leman-russ-commander-2-3-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-commander-2`, `oc-leman-russ-commander-2-3-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-commander-2`, `oc-leman-russ-commander-2-3-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-demolisher`, `oc-leman-russ-demolisher-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-demolisher`, `oc-leman-russ-demolisher-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-demolisher`, `oc-leman-russ-demolisher-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-demolisher`, `oc-leman-russ-demolisher-2-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-demolisher-2`, `oc-leman-russ-demolisher-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-demolisher-2`, `oc-leman-russ-demolisher-2-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-demolisher-2`, `oc-leman-russ-demolisher-2-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-demolisher-2`, `oc-leman-russ-demolisher-2-2-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-eradicator`, `oc-leman-russ-eradicator-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-eradicator`, `oc-leman-russ-eradicator-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-eradicator`, `oc-leman-russ-eradicator-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-eradicator`, `oc-leman-russ-eradicator-2-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-eradicator-2`, `oc-leman-russ-eradicator-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-eradicator-2`, `oc-leman-russ-eradicator-2-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-eradicator-2`, `oc-leman-russ-eradicator-2-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-eradicator-2`, `oc-leman-russ-eradicator-2-2-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-executioner`, `oc-leman-russ-executioner-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-executioner`, `oc-leman-russ-executioner-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-executioner`, `oc-leman-russ-executioner-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-executioner`, `oc-leman-russ-executioner-2-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-executioner-2`, `oc-leman-russ-executioner-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-executioner-2`, `oc-leman-russ-executioner-2-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-executioner-2`, `oc-leman-russ-executioner-2-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-executioner-2`, `oc-leman-russ-executioner-2-2-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-exterminator`, `oc-leman-russ-exterminator-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-exterminator`, `oc-leman-russ-exterminator-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-exterminator`, `oc-leman-russ-exterminator-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-exterminator`, `oc-leman-russ-exterminator-2-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-exterminator-2`, `oc-leman-russ-exterminator-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-exterminator-2`, `oc-leman-russ-exterminator-2-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-exterminator-2`, `oc-leman-russ-exterminator-2-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-exterminator-2`, `oc-leman-russ-exterminator-2-2-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-punisher`, `oc-leman-russ-punisher-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-punisher`, `oc-leman-russ-punisher-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-punisher`, `oc-leman-russ-punisher-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-punisher`, `oc-leman-russ-punisher-2-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-punisher-2`, `oc-leman-russ-punisher-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-punisher-2`, `oc-leman-russ-punisher-2-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-punisher-2`, `oc-leman-russ-punisher-2-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-punisher-2`, `oc-leman-russ-punisher-2-2-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-vanquisher`, `oc-leman-russ-vanquisher-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-vanquisher`, `oc-leman-russ-vanquisher-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-vanquisher`, `oc-leman-russ-vanquisher-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-vanquisher`, `oc-leman-russ-vanquisher-2-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-vanquisher-2`, `oc-leman-russ-vanquisher-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-vanquisher-2`, `oc-leman-russ-vanquisher-2-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-vanquisher-2`, `oc-leman-russ-vanquisher-2-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leman-russ-vanquisher-2`, `oc-leman-russ-vanquisher-2-2-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leviathan-dreadnought`, `oc-leviathan-dreadnought-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leviathan-dreadnought`, `oc-leviathan-dreadnought-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leviathan-dreadnought-2`, `oc-leviathan-dreadnought-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leviathan-dreadnought-2`, `oc-leviathan-dreadnought-2-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leviathan-dreadnought-3`, `oc-leviathan-dreadnought-3-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leviathan-dreadnought-3`, `oc-leviathan-dreadnought-3-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leviathan-dreadnought-4`, `oc-leviathan-dreadnought-4-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leviathan-dreadnought-4`, `oc-leviathan-dreadnought-4-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leviathan-dreadnought-5`, `oc-leviathan-dreadnought-5-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-leviathan-dreadnought-5`, `oc-leviathan-dreadnought-5-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-librarian-on-bike`, `oc-librarian-on-bike-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-librarian-with-jump-pack`, `oc-librarian-with-jump-pack-1-6` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-lieutenant`, `oc-lieutenant-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-lieutenant`, `oc-lieutenant-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-lieutenant`, `oc-lieutenant-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-lieutenant-2`, `oc-lieutenant-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-lieutenant-2`, `oc-lieutenant-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-lieutenant-2`, `oc-lieutenant-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-lieutenant-3`, `oc-lieutenant-3-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-lieutenant-3`, `oc-lieutenant-3-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-lieutenant-3`, `oc-lieutenant-3-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-lieutenant-4`, `oc-lieutenant-4-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-lieutenant-4`, `oc-lieutenant-4-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-lieutenant-4`, `oc-lieutenant-4-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-lieutenant-5`, `oc-lieutenant-5-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-lieutenant-5`, `oc-lieutenant-5-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-lieutenant-5`, `oc-lieutenant-5-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-lieutenant-6`, `oc-lieutenant-6-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-lieutenant-6`, `oc-lieutenant-6-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-lieutenant-6`, `oc-lieutenant-6-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-lifta-wagon`, `oc-lifta-wagon-4-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-lifta-wagon`, `oc-lifta-wagon-4-5` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-lokhust-lord`, `oc-lokhust-lord-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-lokhust-lord`, `oc-lokhust-lord-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-long-fangs`, `oc-long-fangs-1-5` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-long-fangs`, `oc-long-fangs-1-7` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-longstrike`, `oc-longstrike-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-longstrike`, `oc-longstrike-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-longstrike`, `oc-longstrike-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-longstrike`, `oc-longstrike-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-lord`, `oc-lord-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-lychguard`, `oc-lychguard-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-lynx`, `oc-lynx-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-macharius`, `oc-macharius-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-macharius`, `oc-macharius-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-macharius-2`, `oc-macharius-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-macharius-2`, `oc-macharius-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-macharius-omega`, `oc-macharius-omega-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-macharius-omega`, `oc-macharius-omega-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-macharius-omega`, `oc-macharius-omega-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-macharius-omega-2`, `oc-macharius-omega-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-macharius-omega-2`, `oc-macharius-omega-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-macharius-omega-2`, `oc-macharius-omega-2-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-macharius-vanquisher`, `oc-macharius-vanquisher-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-macharius-vanquisher`, `oc-macharius-vanquisher-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-macharius-vanquisher-2`, `oc-macharius-vanquisher-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-macharius-vanquisher-2`, `oc-macharius-vanquisher-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-macharius-vulcan`, `oc-macharius-vulcan-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-macharius-vulcan`, `oc-macharius-vulcan-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-macharius-vulcan-2`, `oc-macharius-vulcan-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-macharius-vulcan-2`, `oc-macharius-vulcan-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-malcador`, `oc-malcador-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-malcador`, `oc-malcador-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-malcador-2`, `oc-malcador-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-malcador-2`, `oc-malcador-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-malcador-annihilator`, `oc-malcador-annihilator-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-malcador-annihilator`, `oc-malcador-annihilator-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-malcador-annihilator-2`, `oc-malcador-annihilator-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-malcador-annihilator-2`, `oc-malcador-annihilator-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-malcador-defender`, `oc-malcador-defender-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-malcador-defender`, `oc-malcador-defender-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-malcador-defender-2`, `oc-malcador-defender-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-malcador-defender-2`, `oc-malcador-defender-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-malcador-infernus`, `oc-malcador-infernus-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-malcador-infernus`, `oc-malcador-infernus-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-malcador-infernus`, `oc-malcador-infernus-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-malcador-infernus`, `oc-malcador-infernus-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-malcador-infernus-2`, `oc-malcador-infernus-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-malcador-infernus-2`, `oc-malcador-infernus-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-malcador-infernus-2`, `oc-malcador-infernus-2-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-malcador-infernus-2`, `oc-malcador-infernus-2-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-marauder-bomber`, `oc-marauder-bomber-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-marshal`, `oc-marshal-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mastodon`, `oc-mastodon-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mastodon`, `oc-mastodon-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mastodon`, `oc-mastodon-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mastodon`, `oc-mastodon-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mastodon`, `oc-mastodon-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mastodon`, `oc-mastodon-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mastodon-2`, `oc-mastodon-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mastodon-2`, `oc-mastodon-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mastodon-2`, `oc-mastodon-2-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mastodon-2`, `oc-mastodon-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mastodon-2`, `oc-mastodon-2-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mastodon-2`, `oc-mastodon-2-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mastodon-3`, `oc-mastodon-3-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mastodon-3`, `oc-mastodon-3-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mastodon-3`, `oc-mastodon-3-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mastodon-3`, `oc-mastodon-3-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mastodon-3`, `oc-mastodon-3-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mastodon-3`, `oc-mastodon-3-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mastodon-4`, `oc-mastodon-4-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mastodon-4`, `oc-mastodon-4-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mastodon-4`, `oc-mastodon-4-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mastodon-4`, `oc-mastodon-4-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mastodon-4`, `oc-mastodon-4-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mastodon-4`, `oc-mastodon-4-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mastodon-5`, `oc-mastodon-5-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mastodon-5`, `oc-mastodon-5-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mastodon-5`, `oc-mastodon-5-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mastodon-5`, `oc-mastodon-5-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mastodon-5`, `oc-mastodon-5-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mastodon-5`, `oc-mastodon-5-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-maulerfiend-3`, `oc-maulerfiend-3-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-maulerfiend-4`, `oc-maulerfiend-4-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mek-gunz`, `oc-mek-gunz-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-militarum-tempestus-command-squad`, `oc-militarum-tempestus-command-squad-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-militarum-tempestus-command-squad`, `oc-militarum-tempestus-command-squad-1-5` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-militarum-tempestus-command-squad`, `oc-militarum-tempestus-command-squad-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-militarum-tempestus-command-squad`, `oc-militarum-tempestus-command-squad-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-militarum-tempestus-command-squad`, `oc-militarum-tempestus-command-squad-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-militarum-tempestus-command-squad`, `oc-militarum-tempestus-command-squad-4-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-militarum-tempestus-command-squad`, `oc-militarum-tempestus-command-squad-4-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-militarum-tempestus-command-squad`, `oc-militarum-tempestus-command-squad-5-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-militarum-tempestus-command-squad`, `oc-militarum-tempestus-command-squad-5-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-monolith`, `oc-monolith-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mortifiers`, `oc-mortifiers-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mortifiers`, `oc-mortifiers-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mortifiers`, `oc-mortifiers-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mortifiers`, `oc-mortifiers-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mortis-dreadnought`, `oc-mortis-dreadnought-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mortis-dreadnought`, `oc-mortis-dreadnought-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mortis-dreadnought`, `oc-mortis-dreadnought-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mortis-dreadnought`, `oc-mortis-dreadnought-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mortis-dreadnought`, `oc-mortis-dreadnought-1-5` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mortis-dreadnought`, `oc-mortis-dreadnought-1-6` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mortis-dreadnought`, `oc-mortis-dreadnought-1-7` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mukaali-riders`, `oc-mukaali-riders-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mukaali-riders`, `oc-mukaali-riders-3-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mukaali-riders`, `oc-mukaali-riders-3-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mukaali-riders-2`, `oc-mukaali-riders-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mukaali-riders-2`, `oc-mukaali-riders-2-3-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-mukaali-riders-2`, `oc-mukaali-riders-2-3-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-munitorum-servitors`, `oc-munitorum-servitors-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-munitorum-servitors-2`, `oc-munitorum-servitors-2-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-nemesis-claw`, `oc-nemesis-claw-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-nemesis-claw`, `oc-nemesis-claw-5-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-nemesis-dreadknight`, `oc-nemesis-dreadknight-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-neophyte-hybrids`, `oc-neophyte-hybrids-3-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-nobz`, `oc-nobz-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-ogryn-bodyguard`, `oc-ogryn-bodyguard-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-ogryn-bodyguard`, `oc-ogryn-bodyguard-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-onager-dunecrawler`, `oc-onager-dunecrawler-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-onager-dunecrawler`, `oc-onager-dunecrawler-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-overlord`, `oc-overlord-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-painboss`, `oc-painboss-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-painboy`, `oc-painboy-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-paladin-squad`, `oc-paladin-squad-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-paladin-squad`, `oc-paladin-squad-3-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-paladin-squad`, `oc-paladin-squad-3-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-paladin-squad`, `oc-paladin-squad-3-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-palatine`, `oc-palatine-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-pathfinder-team`, `oc-pathfinder-team-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-pathfinder-team`, `oc-pathfinder-team-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-pathfinder-team`, `oc-pathfinder-team-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-pathfinder-team`, `oc-pathfinder-team-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-pathfinder-team`, `oc-pathfinder-team-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-pathfinder-team`, `oc-pathfinder-team-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-pathfinder-team`, `oc-pathfinder-team-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-pathfinder-team`, `oc-pathfinder-team-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-phantom-titan`, `oc-phantom-titan-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-phantom-titan`, `oc-phantom-titan-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-phantom-titan`, `oc-phantom-titan-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-phantom-titan`, `oc-phantom-titan-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-phantom-titan`, `oc-phantom-titan-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-phantom-titan`, `oc-phantom-titan-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-phantom-titan`, `oc-phantom-titan-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-phantom-titan`, `oc-phantom-titan-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-phantom-titan`, `oc-phantom-titan-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-phantom-titan`, `oc-phantom-titan-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-phantom-titan`, `oc-phantom-titan-2-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-phantom-titan`, `oc-phantom-titan-2-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-pink-horrors`, `oc-pink-horrors-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-pink-horrors`, `oc-pink-horrors-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-pink-horrors-2`, `oc-pink-horrors-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-pink-horrors-2`, `oc-pink-horrors-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-plague-drones`, `oc-plague-drones-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-plague-drones`, `oc-plague-drones-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-plague-drones-2`, `oc-plague-drones-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-plague-drones-2`, `oc-plague-drones-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-plague-marines`, `oc-plague-marines-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-plague-marines`, `oc-plague-marines-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-plague-marines`, `oc-plague-marines-5-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-plague-marines-2`, `oc-plague-marines-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-plague-marines-2`, `oc-plague-marines-2-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-plague-marines-2`, `oc-plague-marines-2-5-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-plaguebearers`, `oc-plaguebearers-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-plaguebearers`, `oc-plaguebearers-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-plaguebearers-2`, `oc-plaguebearers-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-plaguebearers-2`, `oc-plaguebearers-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-plagueburst-crawler`, `oc-plagueburst-crawler-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-possessed`, `oc-possessed-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-possessed-2`, `oc-possessed-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-pox-riders`, `oc-pox-riders-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-pox-riders`, `oc-pox-riders-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-predator-annihilator`, `oc-predator-annihilator-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-predator-annihilator`, `oc-predator-annihilator-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-predator-annihilator-2`, `oc-predator-annihilator-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-predator-annihilator-2`, `oc-predator-annihilator-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-predator-annihilator-3`, `oc-predator-annihilator-3-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-predator-annihilator-3`, `oc-predator-annihilator-3-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-predator-annihilator-4`, `oc-predator-annihilator-4-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-predator-annihilator-4`, `oc-predator-annihilator-4-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-predator-annihilator-5`, `oc-predator-annihilator-5-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-predator-annihilator-5`, `oc-predator-annihilator-5-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-predator-annihilator-6`, `oc-predator-annihilator-6-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-predator-annihilator-6`, `oc-predator-annihilator-6-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-predator-destructor`, `oc-predator-destructor-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-predator-destructor`, `oc-predator-destructor-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-predator-destructor-2`, `oc-predator-destructor-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-predator-destructor-2`, `oc-predator-destructor-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-predator-destructor-3`, `oc-predator-destructor-3-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-predator-destructor-3`, `oc-predator-destructor-3-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-predator-destructor-4`, `oc-predator-destructor-4-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-predator-destructor-4`, `oc-predator-destructor-4-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-predator-destructor-5`, `oc-predator-destructor-5-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-predator-destructor-5`, `oc-predator-destructor-5-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-predator-destructor-6`, `oc-predator-destructor-6-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-predator-destructor-6`, `oc-predator-destructor-6-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-proteus-kill-team`, `oc-proteus-kill-team-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-proteus-kill-team`, `oc-proteus-kill-team-6-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-proteus-kill-team`, `oc-proteus-kill-team-6-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-proteus-kill-team`, `oc-proteus-kill-team-6-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-questoris-knight-magaera`, `oc-questoris-knight-magaera-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-questoris-knight-styrix`, `oc-questoris-knight-styrix-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-rapier-carrier`, `oc-rapier-carrier-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-rapier-carrier-2`, `oc-rapier-carrier-2-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-rapier-carrier-3`, `oc-rapier-carrier-3-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-rapier-carrier-4`, `oc-rapier-carrier-4-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-rapier-carrier-5`, `oc-rapier-carrier-5-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-raptors`, `oc-raptors-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-raptors`, `oc-raptors-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-raptors`, `oc-raptors-6-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-raptors-2`, `oc-raptors-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-raptors-2`, `oc-raptors-2-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-raptors-2`, `oc-raptors-2-6-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-ravenwing-command-squad`, `oc-ravenwing-command-squad-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-razorwing-jetfighter`, `oc-razorwing-jetfighter-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-reaver-titan`, `oc-reaver-titan-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-reavers`, `oc-reavers-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-reavers`, `oc-reavers-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-red-corsairs-reave-captain`, `oc-red-corsairs-reave-captain-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-redemptor-dreadnought`, `oc-redemptor-dreadnought-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-redemptor-dreadnought-2`, `oc-redemptor-dreadnought-2-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-redemptor-dreadnought-3`, `oc-redemptor-dreadnought-3-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-redemptor-dreadnought-4`, `oc-redemptor-dreadnought-4-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-redemptor-dreadnought-5`, `oc-redemptor-dreadnought-5-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-redemptor-dreadnought-6`, `oc-redemptor-dreadnought-6-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-relic-contemptor-dreadnought`, `oc-relic-contemptor-dreadnought-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-relic-contemptor-dreadnought`, `oc-relic-contemptor-dreadnought-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-relic-contemptor-dreadnought-2`, `oc-relic-contemptor-dreadnought-2-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-relic-contemptor-dreadnought-2`, `oc-relic-contemptor-dreadnought-2-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-relic-contemptor-dreadnought-3`, `oc-relic-contemptor-dreadnought-3-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-relic-contemptor-dreadnought-3`, `oc-relic-contemptor-dreadnought-3-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-relic-contemptor-dreadnought-4`, `oc-relic-contemptor-dreadnought-4-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-relic-contemptor-dreadnought-4`, `oc-relic-contemptor-dreadnought-4-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-relic-contemptor-dreadnought-5`, `oc-relic-contemptor-dreadnought-5-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-relic-contemptor-dreadnought-5`, `oc-relic-contemptor-dreadnought-5-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-relic-terminator-squad`, `oc-relic-terminator-squad-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-relic-terminator-squad`, `oc-relic-terminator-squad-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-relic-terminator-squad`, `oc-relic-terminator-squad-5-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-retributor-squad`, `oc-retributor-squad-1-6` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-rhino-5`, `oc-rhino-5-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-riptide-battlesuit`, `oc-riptide-battlesuit-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-riptide-battlesuit`, `oc-riptide-battlesuit-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-rogal-dorn-battle-tank`, `oc-rogal-dorn-battle-tank-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-rogal-dorn-battle-tank`, `oc-rogal-dorn-battle-tank-3-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-rogal-dorn-battle-tank`, `oc-rogal-dorn-battle-tank-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-rogal-dorn-battle-tank`, `oc-rogal-dorn-battle-tank-4-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-rogal-dorn-battle-tank-2`, `oc-rogal-dorn-battle-tank-2-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-rogal-dorn-battle-tank-2`, `oc-rogal-dorn-battle-tank-2-3-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-rogal-dorn-battle-tank-2`, `oc-rogal-dorn-battle-tank-2-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-rogal-dorn-battle-tank-2`, `oc-rogal-dorn-battle-tank-2-4-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-rogal-dorn-commander`, `oc-rogal-dorn-commander-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-rogal-dorn-commander`, `oc-rogal-dorn-commander-3-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-rogal-dorn-commander`, `oc-rogal-dorn-commander-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-rogal-dorn-commander`, `oc-rogal-dorn-commander-4-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-rogal-dorn-commander-2`, `oc-rogal-dorn-commander-2-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-rogal-dorn-commander-2`, `oc-rogal-dorn-commander-2-3-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-rogal-dorn-commander-2`, `oc-rogal-dorn-commander-2-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-rogal-dorn-commander-2`, `oc-rogal-dorn-commander-2-4-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-rubric-marines`, `oc-rubric-marines-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-rubric-marines-2`, `oc-rubric-marines-2-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-rvarna-battlesuit`, `oc-rvarna-battlesuit-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sagitaur`, `oc-sagitaur-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sanctifiers`, `oc-sanctifiers-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sanctifiers-2`, `oc-sanctifiers-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sanguinary-guard`, `oc-sanguinary-guard-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-scorpion`, `oc-scorpion-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-scout-bike-squad`, `oc-scout-bike-squad-1-7` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-scout-bike-squad`, `oc-scout-bike-squad-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-scout-sentinels`, `oc-scout-sentinels-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-scout-sentinels`, `oc-scout-sentinels-1-5` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-scout-sentinels-2`, `oc-scout-sentinels-2-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-scout-sentinels-2`, `oc-scout-sentinels-2-1-5` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-scout-sniper-squad`, `oc-scout-sniper-squad-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-scout-squad`, `oc-scout-squad-4-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-scout-squad-2`, `oc-scout-squad-2-4-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-scout-squad-3`, `oc-scout-squad-3-4-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-scout-squad-4`, `oc-scout-squad-4-4-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-scout-squad-5`, `oc-scout-squad-5-4-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-secutarii-hoplites`, `oc-secutarii-hoplites-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-secutarii-hoplites`, `oc-secutarii-hoplites-3-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-secutarii-peltasts`, `oc-secutarii-peltasts-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-secutarii-peltasts`, `oc-secutarii-peltasts-3-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-seekers`, `oc-seekers-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-seekers`, `oc-seekers-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-seekers-2`, `oc-seekers-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-seekers-2`, `oc-seekers-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-seraphim-squad`, `oc-seraphim-squad-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-seraphim-squad`, `oc-seraphim-squad-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-seraphim-squad`, `oc-seraphim-squad-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-seraphim-squad`, `oc-seraphim-squad-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-seraphim-squad`, `oc-seraphim-squad-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-seraphim-squad`, `oc-seraphim-squad-2-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-seraphim-squad`, `oc-seraphim-squad-2-5` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-seraptek-heavy-construct`, `oc-seraptek-heavy-construct-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-seraptek-heavy-construct`, `oc-seraptek-heavy-construct-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-serberys-raiders`, `oc-serberys-raiders-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-servitors`, `oc-servitors-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-shadowsword`, `oc-shadowsword-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-shadowsword`, `oc-shadowsword-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-shadowsword`, `oc-shadowsword-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-shadowsword`, `oc-shadowsword-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-shadowsword`, `oc-shadowsword-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-shadowsword-2`, `oc-shadowsword-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-shadowsword-2`, `oc-shadowsword-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-shadowsword-2`, `oc-shadowsword-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-shadowsword-2`, `oc-shadowsword-2-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-shadowsword-2`, `oc-shadowsword-2-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-shield-captain`, `oc-shield-captain-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-shield-captain`, `oc-shield-captain-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-shield-captain`, `oc-shield-captain-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-shield-captain`, `oc-shield-captain-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-shield-captain`, `oc-shield-captain-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-shield-captain`, `oc-shield-captain-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-shield-captain-in-allarus-terminator-armour`, `oc-shield-captain-in-allarus-terminator-armour-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-shining-spears`, `oc-shining-spears-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-shining-spears`, `oc-shining-spears-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sicaran-arcus`, `oc-sicaran-arcus-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sicaran-arcus`, `oc-sicaran-arcus-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sicaran-battle-tank`, `oc-sicaran-battle-tank-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sicaran-battle-tank`, `oc-sicaran-battle-tank-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sicaran-battle-tank-2`, `oc-sicaran-battle-tank-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sicaran-battle-tank-2`, `oc-sicaran-battle-tank-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sicaran-battle-tank-3`, `oc-sicaran-battle-tank-3-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sicaran-battle-tank-3`, `oc-sicaran-battle-tank-3-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sicaran-battle-tank-4`, `oc-sicaran-battle-tank-4-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sicaran-battle-tank-4`, `oc-sicaran-battle-tank-4-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sicaran-battle-tank-5`, `oc-sicaran-battle-tank-5-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sicaran-battle-tank-5`, `oc-sicaran-battle-tank-5-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sicaran-omega`, `oc-sicaran-omega-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sicaran-omega`, `oc-sicaran-omega-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sicaran-punisher`, `oc-sicaran-punisher-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sicaran-punisher`, `oc-sicaran-punisher-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sicaran-punisher-2`, `oc-sicaran-punisher-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sicaran-punisher-2`, `oc-sicaran-punisher-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sicaran-punisher-3`, `oc-sicaran-punisher-3-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sicaran-punisher-3`, `oc-sicaran-punisher-3-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sicaran-punisher-4`, `oc-sicaran-punisher-4-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sicaran-punisher-4`, `oc-sicaran-punisher-4-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sicaran-punisher-5`, `oc-sicaran-punisher-5-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sicaran-punisher-5`, `oc-sicaran-punisher-5-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sicaran-venator`, `oc-sicaran-venator-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sicaran-venator`, `oc-sicaran-venator-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sicaran-venator-2`, `oc-sicaran-venator-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sicaran-venator-2`, `oc-sicaran-venator-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sicaran-venator-3`, `oc-sicaran-venator-3-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sicaran-venator-3`, `oc-sicaran-venator-3-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sicaran-venator-4`, `oc-sicaran-venator-4-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sicaran-venator-4`, `oc-sicaran-venator-4-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sicaran-venator-5`, `oc-sicaran-venator-5-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sicaran-venator-5`, `oc-sicaran-venator-5-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sicarian-ruststalkers`, `oc-sicarian-ruststalkers-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sicarian-ruststalkers`, `oc-sicarian-ruststalkers-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sisters-novitiate-squad`, `oc-sisters-novitiate-squad-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sisters-novitiate-squad`, `oc-sisters-novitiate-squad-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sisters-novitiate-squad`, `oc-sisters-novitiate-squad-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sisters-of-battle-squad`, `oc-sisters-of-battle-squad-1-6` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sisters-of-battle-squad`, `oc-sisters-of-battle-squad-5-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-skathach-wraithknight`, `oc-skathach-wraithknight-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-skathach-wraithknight`, `oc-skathach-wraithknight-3-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-skitarii-rangers`, `oc-skitarii-rangers-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-skitarii-rangers`, `oc-skitarii-rangers-6-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-skitarii-rangers`, `oc-skitarii-rangers-6-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-skitarii-rangers-2`, `oc-skitarii-rangers-2-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-skitarii-rangers-2`, `oc-skitarii-rangers-2-6-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-skitarii-rangers-2`, `oc-skitarii-rangers-2-6-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-skitarii-vanguard`, `oc-skitarii-vanguard-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-skitarii-vanguard`, `oc-skitarii-vanguard-6-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-skitarii-vanguard`, `oc-skitarii-vanguard-6-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-skitarii-vanguard-2`, `oc-skitarii-vanguard-2-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-skitarii-vanguard-2`, `oc-skitarii-vanguard-2-6-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-skitarii-vanguard-2`, `oc-skitarii-vanguard-2-6-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sky-ray-gunship`, `oc-sky-ray-gunship-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sky-ray-gunship`, `oc-sky-ray-gunship-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-skyclaws`, `oc-skyclaws-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-skyclaws`, `oc-skyclaws-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-skyclaws`, `oc-skyclaws-3-5` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sorcerer-in-terminator-armour`, `oc-sorcerer-in-terminator-armour-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sorcerer-in-terminator-armour-3`, `oc-sorcerer-in-terminator-armour-3-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sorcerer-on-bike`, `oc-sorcerer-on-bike-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sorcerer-on-disc-of-tzeentch`, `oc-sorcerer-on-disc-of-tzeentch-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sorcerer-on-disc-of-tzeentch-2`, `oc-sorcerer-on-disc-of-tzeentch-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sorcerer-on-palanquin-of-nurgle`, `oc-sorcerer-on-palanquin-of-nurgle-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sorcerer-on-palanquin-of-nurgle-2`, `oc-sorcerer-on-palanquin-of-nurgle-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sorcerer-on-palanquin-of-nurgle-3`, `oc-sorcerer-on-palanquin-of-nurgle-3-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sorcerer-on-steed-of-slaanesh`, `oc-sorcerer-on-steed-of-slaanesh-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sorcerer-on-steed-of-slaanesh-2`, `oc-sorcerer-on-steed-of-slaanesh-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-spartan`, `oc-spartan-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-spartan-2`, `oc-spartan-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-spartan-3`, `oc-spartan-3-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-spartan-4`, `oc-spartan-4-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-spartan-5`, `oc-spartan-5-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-squiggoth`, `oc-squiggoth-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-squighog-boyz`, `oc-squighog-boyz-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stealth-battlesuits`, `oc-stealth-battlesuits-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stealth-battlesuits`, `oc-stealth-battlesuits-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stealth-battlesuits`, `oc-stealth-battlesuits-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-storm-eagle-gunship`, `oc-storm-eagle-gunship-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-storm-eagle-gunship`, `oc-storm-eagle-gunship-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-storm-eagle-gunship-2`, `oc-storm-eagle-gunship-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-storm-eagle-gunship-2`, `oc-storm-eagle-gunship-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-storm-eagle-gunship-3`, `oc-storm-eagle-gunship-3-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-storm-eagle-gunship-3`, `oc-storm-eagle-gunship-3-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-storm-eagle-gunship-4`, `oc-storm-eagle-gunship-4-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-storm-eagle-gunship-4`, `oc-storm-eagle-gunship-4-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-storm-eagle-gunship-5`, `oc-storm-eagle-gunship-5-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-storm-eagle-gunship-5`, `oc-storm-eagle-gunship-5-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormblade`, `oc-stormblade-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormblade`, `oc-stormblade-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormblade`, `oc-stormblade-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormblade`, `oc-stormblade-4-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormblade`, `oc-stormblade-4-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormblade-2`, `oc-stormblade-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormblade-2`, `oc-stormblade-2-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormblade-2`, `oc-stormblade-2-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormblade-2`, `oc-stormblade-2-4-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormblade-2`, `oc-stormblade-2-4-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormfang-gunship`, `oc-stormfang-gunship-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormfang-gunship`, `oc-stormfang-gunship-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormhawk-interceptor`, `oc-stormhawk-interceptor-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormhawk-interceptor-2`, `oc-stormhawk-interceptor-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormhawk-interceptor-3`, `oc-stormhawk-interceptor-3-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormhawk-interceptor-4`, `oc-stormhawk-interceptor-4-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormhawk-interceptor-5`, `oc-stormhawk-interceptor-5-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormhawk-interceptor-6`, `oc-stormhawk-interceptor-6-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormhawk-interceptor-7`, `oc-stormhawk-interceptor-7-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormlord`, `oc-stormlord-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormlord`, `oc-stormlord-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormlord`, `oc-stormlord-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormlord`, `oc-stormlord-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormlord`, `oc-stormlord-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormlord-2`, `oc-stormlord-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormlord-2`, `oc-stormlord-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormlord-2`, `oc-stormlord-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormlord-2`, `oc-stormlord-2-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormlord-2`, `oc-stormlord-2-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormraven-gunship`, `oc-stormraven-gunship-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormraven-gunship`, `oc-stormraven-gunship-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormraven-gunship-2`, `oc-stormraven-gunship-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormraven-gunship-2`, `oc-stormraven-gunship-2-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormraven-gunship-3`, `oc-stormraven-gunship-3-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormraven-gunship-3`, `oc-stormraven-gunship-3-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormraven-gunship-4`, `oc-stormraven-gunship-4-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormraven-gunship-4`, `oc-stormraven-gunship-4-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormraven-gunship-5`, `oc-stormraven-gunship-5-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormraven-gunship-5`, `oc-stormraven-gunship-5-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormraven-gunship-6`, `oc-stormraven-gunship-6-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormraven-gunship-6`, `oc-stormraven-gunship-6-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormraven-gunship-7`, `oc-stormraven-gunship-7-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormraven-gunship-7`, `oc-stormraven-gunship-7-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormsurge`, `oc-stormsurge-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormsword`, `oc-stormsword-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormsword`, `oc-stormsword-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormsword`, `oc-stormsword-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormsword`, `oc-stormsword-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormsword`, `oc-stormsword-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormsword-2`, `oc-stormsword-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormsword-2`, `oc-stormsword-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormsword-2`, `oc-stormsword-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormsword-2`, `oc-stormsword-2-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormsword-2`, `oc-stormsword-2-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormtalon-gunship`, `oc-stormtalon-gunship-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormtalon-gunship-2`, `oc-stormtalon-gunship-2-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormtalon-gunship-3`, `oc-stormtalon-gunship-3-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormtalon-gunship-4`, `oc-stormtalon-gunship-4-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormtalon-gunship-5`, `oc-stormtalon-gunship-5-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormtalon-gunship-6`, `oc-stormtalon-gunship-6-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-stormtalon-gunship-7`, `oc-stormtalon-gunship-7-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-strike-team`, `oc-strike-team-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-strike-team`, `oc-strike-team-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-strike-team`, `oc-strike-team-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-strike-team`, `oc-strike-team-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-striking-scorpions`, `oc-striking-scorpions-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-subductor-squad`, `oc-subductor-squad-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-sword-brethren-squad`, `oc-sword-brethren-squad-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tactical-squad`, `oc-tactical-squad-1-10` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tactical-squad`, `oc-tactical-squad-1-7` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tactical-squad`, `oc-tactical-squad-1-9` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tactical-squad`, `oc-tactical-squad-2-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tactical-squad`, `oc-tactical-squad-3-6` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tactical-squad-2`, `oc-tactical-squad-2-1-10` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tactical-squad-2`, `oc-tactical-squad-2-1-7` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tactical-squad-2`, `oc-tactical-squad-2-1-9` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tactical-squad-2`, `oc-tactical-squad-2-2-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tactical-squad-2`, `oc-tactical-squad-2-3-6` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tactical-squad-3`, `oc-tactical-squad-3-1-10` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tactical-squad-3`, `oc-tactical-squad-3-1-7` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tactical-squad-3`, `oc-tactical-squad-3-1-9` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tactical-squad-3`, `oc-tactical-squad-3-2-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tactical-squad-3`, `oc-tactical-squad-3-3-6` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tactical-squad-4`, `oc-tactical-squad-4-1-10` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tactical-squad-4`, `oc-tactical-squad-4-1-7` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tactical-squad-4`, `oc-tactical-squad-4-1-9` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tactical-squad-4`, `oc-tactical-squad-4-2-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tactical-squad-4`, `oc-tactical-squad-4-3-6` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-talonstrike-kill-team`, `oc-talonstrike-kill-team-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tankbustas`, `oc-tankbustas-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tankbustas`, `oc-tankbustas-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-taunar-supremacy-armour`, `oc-taunar-supremacy-armour-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-taunar-supremacy-armour`, `oc-taunar-supremacy-armour-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tauros-assault-vehicle`, `oc-tauros-assault-vehicle-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tauros-assault-vehicle-2`, `oc-tauros-assault-vehicle-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-taurox-prime`, `oc-taurox-prime-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-taurox-prime-2`, `oc-taurox-prime-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tech-priest-dominus`, `oc-tech-priest-dominus-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tech-priest-dominus-2`, `oc-tech-priest-dominus-2-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-techmarine-on-bike`, `oc-techmarine-on-bike-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-telemon-heavy-dreadnought`, `oc-telemon-heavy-dreadnought-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-telemon-heavy-dreadnought`, `oc-telemon-heavy-dreadnought-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-telemon-heavy-dreadnought`, `oc-telemon-heavy-dreadnought-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-telemon-heavy-dreadnought`, `oc-telemon-heavy-dreadnought-1-5` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tempestus-aquilons`, `oc-tempestus-aquilons-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tempestus-aquilons`, `oc-tempestus-aquilons-4-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tempestus-aquilons`, `oc-tempestus-aquilons-5-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tempestus-scions`, `oc-tempestus-scions-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tempestus-scions`, `oc-tempestus-scions-1-5` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tempestus-scions`, `oc-tempestus-scions-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tempestus-scions`, `oc-tempestus-scions-4-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-terminator-assault-squad`, `oc-terminator-assault-squad-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-terminator-assault-squad-2`, `oc-terminator-assault-squad-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-terminator-assault-squad-3`, `oc-terminator-assault-squad-3-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-terminator-assault-squad-4`, `oc-terminator-assault-squad-4-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-terminator-assault-squad-5`, `oc-terminator-assault-squad-5-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-terminator-squad`, `oc-terminator-squad-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-terminator-squad-2`, `oc-terminator-squad-2-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-terminator-squad-3`, `oc-terminator-squad-3-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-terminator-squad-4`, `oc-terminator-squad-4-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-terminator-squad-5`, `oc-terminator-squad-5-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-terrax-pattern-termite`, `oc-terrax-pattern-termite-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-terrax-pattern-termite`, `oc-terrax-pattern-termite-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-terrax-pattern-termite-2`, `oc-terrax-pattern-termite-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-terrax-pattern-termite-2`, `oc-terrax-pattern-termite-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-terrax-pattern-termite-3`, `oc-terrax-pattern-termite-3-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-terrax-pattern-termite-3`, `oc-terrax-pattern-termite-3-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-terrax-pattern-termite-4`, `oc-terrax-pattern-termite-4-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-terrax-pattern-termite-4`, `oc-terrax-pattern-termite-4-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-terrax-pattern-termite-5`, `oc-terrax-pattern-termite-5-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-terrax-pattern-termite-5`, `oc-terrax-pattern-termite-5-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-terrax-pattern-termite-6`, `oc-terrax-pattern-termite-6-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-terrax-pattern-termite-6`, `oc-terrax-pattern-termite-6-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tesseract-ark`, `oc-tesseract-ark-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tesseract-ark`, `oc-tesseract-ark-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-thunderwolf-cavalry`, `oc-thunderwolf-cavalry-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-thunderwolf-cavalry`, `oc-thunderwolf-cavalry-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tidewall-shieldline`, `oc-tidewall-shieldline-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tiger-shark`, `oc-tiger-shark-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tiger-shark`, `oc-tiger-shark-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tiger-shark`, `oc-tiger-shark-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tiger-shark`, `oc-tiger-shark-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tiger-shark`, `oc-tiger-shark-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tomb-citadel-walls`, `oc-tomb-citadel-walls-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tomb-citadel-walls`, `oc-tomb-citadel-walls-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tormentors`, `oc-tormentors-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tormentors`, `oc-tormentors-4-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tormentors`, `oc-tormentors-5-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-traitor-guardsmen-squad`, `oc-traitor-guardsmen-squad-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-traitor-guardsmen-squad`, `oc-traitor-guardsmen-squad-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-traitor-guardsmen-squad-2`, `oc-traitor-guardsmen-squad-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-traitor-guardsmen-squad-2`, `oc-traitor-guardsmen-squad-2-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-traitor-guardsmen-squad-3`, `oc-traitor-guardsmen-squad-3-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-traitor-guardsmen-squad-3`, `oc-traitor-guardsmen-squad-3-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-triarch-praetorians`, `oc-triarch-praetorians-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tx42-piranha`, `oc-tx42-piranha-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tx42-piranha`, `oc-tx42-piranha-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tx42-piranha`, `oc-tx42-piranha-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-typhon`, `oc-typhon-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-typhon`, `oc-typhon-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-typhon-2`, `oc-typhon-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-typhon-2`, `oc-typhon-2-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-typhon-3`, `oc-typhon-3-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-typhon-3`, `oc-typhon-3-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-typhon-4`, `oc-typhon-4-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-typhon-4`, `oc-typhon-4-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-typhon-5`, `oc-typhon-5-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-typhon-5`, `oc-typhon-5-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tyrant-guard`, `oc-tyrant-guard-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tyrant-guard`, `oc-tyrant-guard-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tyrant-guard`, `oc-tyrant-guard-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tyrant-guard`, `oc-tyrant-guard-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tzaangors`, `oc-tzaangors-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-tzaangors`, `oc-tzaangors-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-valkyrie`, `oc-valkyrie-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-valkyrie`, `oc-valkyrie-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-valkyrie-sky-talon`, `oc-valkyrie-sky-talon-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-venatari-custodians`, `oc-venatari-custodians-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-venatari-custodians`, `oc-venatari-custodians-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-vendetta-gunship`, `oc-vendetta-gunship-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-venerable-dreadnought`, `oc-venerable-dreadnought-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-venerable-dreadnought-2`, `oc-venerable-dreadnought-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-venerable-dreadnought-2`, `oc-venerable-dreadnought-2-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-venerable-dreadnought-2`, `oc-venerable-dreadnought-2-3-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-venerable-dreadnought-3`, `oc-venerable-dreadnought-3-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-venerable-dreadnought-3`, `oc-venerable-dreadnought-3-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-veteran-bike-squad`, `oc-veteran-bike-squad-1-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-vigilant-squad`, `oc-vigilant-squad-1-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-vigilant-squad`, `oc-vigilant-squad-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-voidraven-bomber`, `oc-voidraven-bomber-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-voidraven-bomber`, `oc-voidraven-bomber-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-voidweaver`, `oc-voidweaver-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-voidweaver-2`, `oc-voidweaver-2-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-vulture-gunship`, `oc-vulture-gunship-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-vypers`, `oc-vypers-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-war-dog-stalker`, `oc-war-dog-stalker-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-warhound-titan`, `oc-warhound-titan-2-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-warlock`, `oc-warlock-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-warlock-conclave`, `oc-warlock-conclave-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-warlock-skyrunners`, `oc-warlock-skyrunners-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-warlord-titan`, `oc-warlord-titan-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-warlord-titan`, `oc-warlord-titan-2-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-warlord-titan`, `oc-warlord-titan-3-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-wasp-assault-walker`, `oc-wasp-assault-walker-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-wasp-assault-walker`, `oc-wasp-assault-walker-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-wave-serpent`, `oc-wave-serpent-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-wazbom-blastajet`, `oc-wazbom-blastajet-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-wolf-guard-battle-leader`, `oc-wolf-guard-battle-leader-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-wolf-guard-battle-leader-in-terminator-armour`, `oc-wolf-guard-battle-leader-in-terminator-armour-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-wolf-guard-battle-leader-on-thunderwolf`, `oc-wolf-guard-battle-leader-on-thunderwolf-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-wolf-guard-battle-leader-on-thunderwolf`, `oc-wolf-guard-battle-leader-on-thunderwolf-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-wolf-guard-battle-leader-on-thunderwolf`, `oc-wolf-guard-battle-leader-on-thunderwolf-3-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-wolf-guard-pack-leader`, `oc-wolf-guard-pack-leader-2-10` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-wolf-guard-pack-leader`, `oc-wolf-guard-pack-leader-2-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-wolf-guard-pack-leader-in-terminator-armour`, `oc-wolf-guard-pack-leader-in-terminator-armour-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-wolf-guard-pack-leader-in-terminator-armour`, `oc-wolf-guard-pack-leader-in-terminator-armour-2-8` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-wolf-guard-pack-leader-with-jump-pack`, `oc-wolf-guard-pack-leader-with-jump-pack-2-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-wolf-guard-pack-leader-with-jump-pack`, `oc-wolf-guard-pack-leader-with-jump-pack-2-9` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-wolf-guard-terminators`, `oc-wolf-guard-terminators-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-wolf-lord-on-thunderwolf`, `oc-wolf-lord-on-thunderwolf-1-3` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-wolf-lord-on-thunderwolf`, `oc-wolf-lord-on-thunderwolf-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-wolf-lord-on-thunderwolf`, `oc-wolf-lord-on-thunderwolf-2-4` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-wolf-scouts`, `oc-wolf-scouts-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-wolf-scouts`, `oc-wolf-scouts-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-wolf-scouts`, `oc-wolf-scouts-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-wracks`, `oc-wracks-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-wraithlord`, `oc-wraithlord-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-wraithlord`, `oc-wraithlord-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-wraithseer`, `oc-wraithseer-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-wulfen`, `oc-wulfen-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-wulfen-dreadnought`, `oc-wulfen-dreadnought-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-wulfen-with-storm-shields`, `oc-wulfen-with-storm-shields-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-ynnari-incubi`, `oc-ynnari-incubi-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-ynnari-kabalite-warriors`, `oc-ynnari-kabalite-warriors-2-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-ynnari-reavers`, `oc-ynnari-reavers-3-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-ynnari-reavers`, `oc-ynnari-reavers-3-2` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-yvahra-battlesuit`, `oc-yvahra-battlesuit-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-zephyrim-squad`, `oc-zephyrim-squad-1-1` | — |
| `OPT-BUNDLE-UNLINKED` | advisory | `ds-zephyrim-squad`, `oc-zephyrim-squad-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-acastus-knight-porphyrion`, `oc-acastus-knight-porphyrion-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-acastus-knight-porphyrion`, `oc-acastus-knight-porphyrion-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-achilles-ridgerunners`, `oc-achilles-ridgerunners-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-achilles-ridgerunners`, `oc-achilles-ridgerunners-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-acolyte-hybrids-with-autopistols`, `oc-acolyte-hybrids-with-autopistols-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-acolyte-hybrids-with-hand-flamers`, `oc-acolyte-hybrids-with-hand-flamers-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-aggressor-squad`, `oc-aggressor-squad-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-aggressor-squad-2`, `oc-aggressor-squad-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-aggressor-squad-3`, `oc-aggressor-squad-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-aggressor-squad-4`, `oc-aggressor-squad-4-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-aggressor-squad-5`, `oc-aggressor-squad-5-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-aggressor-squad-6`, `oc-aggressor-squad-6-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-allarus-custodians`, `oc-allarus-custodians-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-allarus-custodians`, `oc-allarus-custodians-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-ancient-in-terminator-armour`, `oc-ancient-in-terminator-armour-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-ancient-in-terminator-armour-2`, `oc-ancient-in-terminator-armour-2-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-ancient-in-terminator-armour-3`, `oc-ancient-in-terminator-armour-3-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-ancient-in-terminator-armour-4`, `oc-ancient-in-terminator-armour-4-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-ancient-in-terminator-armour-5`, `oc-ancient-in-terminator-armour-5-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-ancient-in-terminator-armour-6`, `oc-ancient-in-terminator-armour-6-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-ancient-on-bike`, `oc-ancient-on-bike-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-aquila-kill-team`, `oc-aquila-kill-team-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-aquila-kill-team`, `oc-aquila-kill-team-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-aquila-kill-team`, `oc-aquila-kill-team-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-archaeopter-fusilave`, `oc-archaeopter-fusilave-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-archaeopter-stratoraptor`, `oc-archaeopter-stratoraptor-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-archaeopter-transvector`, `oc-archaeopter-transvector-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-archon`, `oc-archon-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-arkurian-stormhammer`, `oc-arkurian-stormhammer-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-arkurian-stormhammer`, `oc-arkurian-stormhammer-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-arkurian-stormhammer`, `oc-arkurian-stormhammer-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-arkurian-stormhammer-2`, `oc-arkurian-stormhammer-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-arkurian-stormhammer-2`, `oc-arkurian-stormhammer-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-arkurian-stormhammer-2`, `oc-arkurian-stormhammer-2-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-armiger-moirax`, `oc-armiger-moirax-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-armiger-moirax`, `oc-armiger-moirax-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-armoured-sentinels`, `oc-armoured-sentinels-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-armoured-sentinels`, `oc-armoured-sentinels-1-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-armoured-sentinels-2`, `oc-armoured-sentinels-2-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-armoured-sentinels-2`, `oc-armoured-sentinels-2-1-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-assault-intercessor-squad`, `oc-assault-intercessor-squad-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-assault-intercessor-squad-2`, `oc-assault-intercessor-squad-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-assault-intercessor-squad-3`, `oc-assault-intercessor-squad-3-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-assault-intercessor-squad-4`, `oc-assault-intercessor-squad-4-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-assault-intercessor-squad-5`, `oc-assault-intercessor-squad-5-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-assault-intercessor-squad-6`, `oc-assault-intercessor-squad-6-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-assault-intercessors-with-jump-packs`, `oc-assault-intercessors-with-jump-packs-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-assault-intercessors-with-jump-packs`, `oc-assault-intercessors-with-jump-packs-3-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-assault-intercessors-with-jump-packs-2`, `oc-assault-intercessors-with-jump-packs-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-assault-intercessors-with-jump-packs-2`, `oc-assault-intercessors-with-jump-packs-2-3-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-assault-intercessors-with-jump-packs-3`, `oc-assault-intercessors-with-jump-packs-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-assault-intercessors-with-jump-packs-3`, `oc-assault-intercessors-with-jump-packs-3-3-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-assault-intercessors-with-jump-packs-4`, `oc-assault-intercessors-with-jump-packs-4-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-assault-intercessors-with-jump-packs-4`, `oc-assault-intercessors-with-jump-packs-4-3-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-assault-intercessors-with-jump-packs-5`, `oc-assault-intercessors-with-jump-packs-5-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-assault-intercessors-with-jump-packs-5`, `oc-assault-intercessors-with-jump-packs-5-3-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-assault-intercessors-with-jump-packs-6`, `oc-assault-intercessors-with-jump-packs-6-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-assault-intercessors-with-jump-packs-6`, `oc-assault-intercessors-with-jump-packs-6-3-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-assault-squad`, `oc-assault-squad-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-assault-squad`, `oc-assault-squad-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-assault-squad`, `oc-assault-squad-4-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-assault-squad`, `oc-assault-squad-4-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-assault-squad`, `oc-assault-squad-4-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-assault-squad-with-jump-packs`, `oc-assault-squad-with-jump-packs-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-assault-squad-with-jump-packs`, `oc-assault-squad-with-jump-packs-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-assault-squad-with-jump-packs`, `oc-assault-squad-with-jump-packs-4-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-assault-squad-with-jump-packs`, `oc-assault-squad-with-jump-packs-4-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-assault-squad-with-jump-packs`, `oc-assault-squad-with-jump-packs-4-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-astartes-servitors`, `oc-astartes-servitors-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-astartes-servitors`, `oc-astartes-servitors-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-astartes-servitors`, `oc-astartes-servitors-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-astraeus`, `oc-astraeus-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-astraeus-2`, `oc-astraeus-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-astraeus-3`, `oc-astraeus-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-astraeus-4`, `oc-astraeus-4-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-astraeus-5`, `oc-astraeus-5-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-astraeus-6`, `oc-astraeus-6-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-atalan-jackals`, `oc-atalan-jackals-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-autarch`, `oc-autarch-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-autarch-wayleaper`, `oc-autarch-wayleaper-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-ax-1-0-tiger-shark`, `oc-ax-1-0-tiger-shark-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-ax-1-0-tiger-shark`, `oc-ax-1-0-tiger-shark-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-baal-predator`, `oc-baal-predator-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-baal-predator`, `oc-baal-predator-4-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-baneblade`, `oc-baneblade-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-baneblade`, `oc-baneblade-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-baneblade`, `oc-baneblade-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-baneblade-2`, `oc-baneblade-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-baneblade-2`, `oc-baneblade-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-baneblade-2`, `oc-baneblade-2-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-banehammer`, `oc-banehammer-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-banehammer`, `oc-banehammer-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-banehammer`, `oc-banehammer-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-banehammer-2`, `oc-banehammer-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-banehammer-2`, `oc-banehammer-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-banehammer-2`, `oc-banehammer-2-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-banesword`, `oc-banesword-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-banesword`, `oc-banesword-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-banesword`, `oc-banesword-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-banesword-2`, `oc-banesword-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-banesword-2`, `oc-banesword-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-banesword-2`, `oc-banesword-2-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-barracuda`, `oc-barracuda-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-barracuda`, `oc-barracuda-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-barracuda`, `oc-barracuda-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-battle-sisters-squad`, `oc-battle-sisters-squad-1-6` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-battle-sisters-squad`, `oc-battle-sisters-squad-5-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-battlewagon`, `oc-battlewagon-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-battlewagon`, `oc-battlewagon-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-battlewagon`, `oc-battlewagon-5-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-beast-snagga-boyz`, `oc-beast-snagga-boyz-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-big-mek-in-mega-armour`, `oc-big-mek-in-mega-armour-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-big-mek-in-mega-armour`, `oc-big-mek-in-mega-armour-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-big-mek-on-warbike`, `oc-big-mek-on-warbike-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-big-mek-with-kustom-force-field`, `oc-big-mek-with-kustom-force-field-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-big-mek-with-shokk-attack-gun`, `oc-big-mek-with-shokk-attack-gun-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-big-trakk`, `oc-big-trakk-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-big-trakk`, `oc-big-trakk-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-biged-bossbunka`, `oc-biged-bossbunka-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-bike-squad`, `oc-bike-squad-1-7` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-bike-squad`, `oc-bike-squad-3-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-bike-squad`, `oc-bike-squad-3-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-bjorn-the-fell-handed`, `oc-bjorn-the-fell-handed-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-bladeguard-veteran-squad`, `oc-bladeguard-veteran-squad-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-bladeguard-veteran-squad-2`, `oc-bladeguard-veteran-squad-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-bladeguard-veteran-squad-3`, `oc-bladeguard-veteran-squad-3-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-bladeguard-veteran-squad-4`, `oc-bladeguard-veteran-squad-4-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-bladeguard-veteran-squad-5`, `oc-bladeguard-veteran-squad-5-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-bladeguard-veteran-squad-6`, `oc-bladeguard-veteran-squad-6-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-blood-claws`, `oc-blood-claws-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-bloodcrushers`, `oc-bloodcrushers-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-bloodcrushers`, `oc-bloodcrushers-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-bloodcrushers-2`, `oc-bloodcrushers-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-bloodcrushers-2`, `oc-bloodcrushers-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-bloodletters`, `oc-bloodletters-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-bloodletters`, `oc-bloodletters-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-bloodletters-2`, `oc-bloodletters-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-bloodletters-2`, `oc-bloodletters-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-breacher-team`, `oc-breacher-team-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-breacher-team`, `oc-breacher-team-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-breacher-team`, `oc-breacher-team-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-breacher-team`, `oc-breacher-team-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-brotherhood-terminator-squad`, `oc-brotherhood-terminator-squad-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-brotherhood-terminator-squad`, `oc-brotherhood-terminator-squad-3-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-brotherhood-terminator-squad`, `oc-brotherhood-terminator-squad-3-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-brotherhood-terminator-squad`, `oc-brotherhood-terminator-squad-3-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-brutalis-dreadnought`, `oc-brutalis-dreadnought-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-brutalis-dreadnought-2`, `oc-brutalis-dreadnought-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-brutalis-dreadnought-3`, `oc-brutalis-dreadnought-3-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-brutalis-dreadnought-4`, `oc-brutalis-dreadnought-4-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-brutalis-dreadnought-5`, `oc-brutalis-dreadnought-5-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-brutalis-dreadnought-6`, `oc-brutalis-dreadnought-6-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-bullgryn-squad`, `oc-bullgryn-squad-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cadian-castellan`, `oc-cadian-castellan-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cadian-castellan`, `oc-cadian-castellan-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cadian-castellan-2`, `oc-cadian-castellan-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cadian-castellan-2`, `oc-cadian-castellan-2-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cadian-command-squad`, `oc-cadian-command-squad-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cadian-command-squad`, `oc-cadian-command-squad-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cadian-command-squad`, `oc-cadian-command-squad-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cadian-command-squad`, `oc-cadian-command-squad-3-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cadian-command-squad`, `oc-cadian-command-squad-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cadian-command-squad`, `oc-cadian-command-squad-4-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cadian-command-squad`, `oc-cadian-command-squad-4-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cadian-command-squad`, `oc-cadian-command-squad-4-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cadian-command-squad-2`, `oc-cadian-command-squad-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cadian-command-squad-2`, `oc-cadian-command-squad-2-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cadian-command-squad-2`, `oc-cadian-command-squad-2-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cadian-command-squad-2`, `oc-cadian-command-squad-2-3-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cadian-command-squad-2`, `oc-cadian-command-squad-2-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cadian-command-squad-2`, `oc-cadian-command-squad-2-4-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cadian-command-squad-2`, `oc-cadian-command-squad-2-4-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cadian-command-squad-2`, `oc-cadian-command-squad-2-4-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cadian-heavy-weapons-squad`, `oc-cadian-heavy-weapons-squad-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cadian-heavy-weapons-squad-2`, `oc-cadian-heavy-weapons-squad-2-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cadian-shock-troops`, `oc-cadian-shock-troops-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cadian-shock-troops`, `oc-cadian-shock-troops-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cadian-shock-troops`, `oc-cadian-shock-troops-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cadian-shock-troops`, `oc-cadian-shock-troops-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cadian-shock-troops-2`, `oc-cadian-shock-troops-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cadian-shock-troops-2`, `oc-cadian-shock-troops-2-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cadian-shock-troops-2`, `oc-cadian-shock-troops-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cadian-shock-troops-2`, `oc-cadian-shock-troops-2-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cadre-fireblade`, `oc-cadre-fireblade-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cadre-fireblade`, `oc-cadre-fireblade-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cadre-fireblade`, `oc-cadre-fireblade-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-canoness`, `oc-canoness-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-canoness-with-jump-pack`, `oc-canoness-with-jump-pack-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-canoptek-macrocytes`, `oc-canoptek-macrocytes-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-canoptek-macrocytes`, `oc-canoptek-macrocytes-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain`, `oc-captain-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain`, `oc-captain-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain`, `oc-captain-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain`, `oc-captain-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain`, `oc-captain-1-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain`, `oc-captain-1-6` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain`, `oc-captain-1-7` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-2`, `oc-captain-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-2`, `oc-captain-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-2`, `oc-captain-2-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-2`, `oc-captain-2-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-2`, `oc-captain-2-1-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-2`, `oc-captain-2-1-6` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-2`, `oc-captain-2-1-7` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-3`, `oc-captain-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-3`, `oc-captain-3-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-3`, `oc-captain-3-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-3`, `oc-captain-3-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-3`, `oc-captain-3-1-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-3`, `oc-captain-3-1-6` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-3`, `oc-captain-3-1-7` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-4`, `oc-captain-4-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-4`, `oc-captain-4-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-4`, `oc-captain-4-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-4`, `oc-captain-4-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-4`, `oc-captain-4-1-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-4`, `oc-captain-4-1-6` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-4`, `oc-captain-4-1-7` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-5`, `oc-captain-5-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-5`, `oc-captain-5-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-5`, `oc-captain-5-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-5`, `oc-captain-5-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-5`, `oc-captain-5-1-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-5`, `oc-captain-5-1-6` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-5`, `oc-captain-5-1-7` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-6`, `oc-captain-6-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-6`, `oc-captain-6-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-6`, `oc-captain-6-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-6`, `oc-captain-6-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-6`, `oc-captain-6-1-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-6`, `oc-captain-6-1-6` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-6`, `oc-captain-6-1-7` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-in-gravis-armour`, `oc-captain-in-gravis-armour-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-in-gravis-armour`, `oc-captain-in-gravis-armour-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-in-gravis-armour`, `oc-captain-in-gravis-armour-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-in-gravis-armour-2`, `oc-captain-in-gravis-armour-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-in-gravis-armour-2`, `oc-captain-in-gravis-armour-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-in-gravis-armour-2`, `oc-captain-in-gravis-armour-2-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-in-gravis-armour-3`, `oc-captain-in-gravis-armour-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-in-gravis-armour-3`, `oc-captain-in-gravis-armour-3-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-in-gravis-armour-3`, `oc-captain-in-gravis-armour-3-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-in-gravis-armour-4`, `oc-captain-in-gravis-armour-4-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-in-gravis-armour-4`, `oc-captain-in-gravis-armour-4-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-in-gravis-armour-4`, `oc-captain-in-gravis-armour-4-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-in-gravis-armour-5`, `oc-captain-in-gravis-armour-5-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-in-gravis-armour-5`, `oc-captain-in-gravis-armour-5-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-in-gravis-armour-5`, `oc-captain-in-gravis-armour-5-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-in-gravis-armour-6`, `oc-captain-in-gravis-armour-6-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-in-gravis-armour-6`, `oc-captain-in-gravis-armour-6-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-in-gravis-armour-6`, `oc-captain-in-gravis-armour-6-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-on-bike`, `oc-captain-on-bike-1-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-on-bike`, `oc-captain-on-bike-1-7` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-on-bike`, `oc-captain-on-bike-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-with-jump-pack`, `oc-captain-with-jump-pack-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-with-jump-pack`, `oc-captain-with-jump-pack-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-with-jump-pack-2`, `oc-captain-with-jump-pack-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-with-jump-pack-2`, `oc-captain-with-jump-pack-2-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-with-jump-pack-3`, `oc-captain-with-jump-pack-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-with-jump-pack-3`, `oc-captain-with-jump-pack-3-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-with-jump-pack-4`, `oc-captain-with-jump-pack-4-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-with-jump-pack-4`, `oc-captain-with-jump-pack-4-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-with-jump-pack-5`, `oc-captain-with-jump-pack-5-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-with-jump-pack-5`, `oc-captain-with-jump-pack-5-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-with-jump-pack-6`, `oc-captain-with-jump-pack-6-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-captain-with-jump-pack-6`, `oc-captain-with-jump-pack-6-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-carnodon`, `oc-carnodon-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-carnodon`, `oc-carnodon-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-carnodon`, `oc-carnodon-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-carnodon`, `oc-carnodon-2-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-carnodon`, `oc-carnodon-2-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-carnodon-2`, `oc-carnodon-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-carnodon-2`, `oc-carnodon-2-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-carnodon-2`, `oc-carnodon-2-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-carnodon-2`, `oc-carnodon-2-2-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-carnodon-2`, `oc-carnodon-2-2-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-catachan-command-squad`, `oc-catachan-command-squad-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-catachan-command-squad`, `oc-catachan-command-squad-1-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-catachan-command-squad`, `oc-catachan-command-squad-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-catachan-command-squad`, `oc-catachan-command-squad-5-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-catachan-command-squad-2`, `oc-catachan-command-squad-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-catachan-command-squad-2`, `oc-catachan-command-squad-2-1-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-catachan-command-squad-2`, `oc-catachan-command-squad-2-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-catachan-command-squad-2`, `oc-catachan-command-squad-2-5-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-catachan-heavy-weapons-squad`, `oc-catachan-heavy-weapons-squad-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-catachan-heavy-weapons-squad-2`, `oc-catachan-heavy-weapons-squad-2-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-catachan-jungle-fighters`, `oc-catachan-jungle-fighters-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-catachan-jungle-fighters-2`, `oc-catachan-jungle-fighters-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-catacomb-command-barge`, `oc-catacomb-command-barge-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-celestian-insidiants`, `oc-celestian-insidiants-5-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-celestian-sacresants`, `oc-celestian-sacresants-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-centurion-assault-squad`, `oc-centurion-assault-squad-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-centurion-assault-squad-2`, `oc-centurion-assault-squad-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-centurion-assault-squad-3`, `oc-centurion-assault-squad-3-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-centurion-assault-squad-4`, `oc-centurion-assault-squad-4-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-centurion-assault-squad-5`, `oc-centurion-assault-squad-5-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-centurion-assault-squad-6`, `oc-centurion-assault-squad-6-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cerberus`, `oc-cerberus-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cerberus`, `oc-cerberus-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cerberus-2`, `oc-cerberus-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cerberus-2`, `oc-cerberus-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cerberus-3`, `oc-cerberus-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cerberus-3`, `oc-cerberus-3-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cerberus-4`, `oc-cerberus-4-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cerberus-4`, `oc-cerberus-4-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cerberus-5`, `oc-cerberus-5-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cerberus-5`, `oc-cerberus-5-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-bikers`, `oc-chaos-bikers-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-bikers`, `oc-chaos-bikers-3-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-bikers`, `oc-chaos-bikers-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-deimos-predator`, `oc-chaos-deimos-predator-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-deimos-predator`, `oc-chaos-deimos-predator-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-deimos-predator`, `oc-chaos-deimos-predator-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-lord`, `oc-chaos-lord-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-lord-2`, `oc-chaos-lord-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-lord-on-bike`, `oc-chaos-lord-on-bike-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-lord-on-bike`, `oc-chaos-lord-on-bike-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-lord-on-disc-of-tzeentch`, `oc-chaos-lord-on-disc-of-tzeentch-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-lord-on-disc-of-tzeentch`, `oc-chaos-lord-on-disc-of-tzeentch-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-lord-on-disc-of-tzeentch-2`, `oc-chaos-lord-on-disc-of-tzeentch-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-lord-on-disc-of-tzeentch-2`, `oc-chaos-lord-on-disc-of-tzeentch-2-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-lord-on-disc-of-tzeentch-3`, `oc-chaos-lord-on-disc-of-tzeentch-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-lord-on-disc-of-tzeentch-3`, `oc-chaos-lord-on-disc-of-tzeentch-3-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-lord-on-juggernaut`, `oc-chaos-lord-on-juggernaut-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-lord-on-juggernaut`, `oc-chaos-lord-on-juggernaut-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-lord-on-juggernaut-2`, `oc-chaos-lord-on-juggernaut-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-lord-on-juggernaut-2`, `oc-chaos-lord-on-juggernaut-2-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-lord-on-palanquin-of-nurgle`, `oc-chaos-lord-on-palanquin-of-nurgle-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-lord-on-palanquin-of-nurgle`, `oc-chaos-lord-on-palanquin-of-nurgle-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-lord-on-palanquin-of-nurgle-2`, `oc-chaos-lord-on-palanquin-of-nurgle-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-lord-on-palanquin-of-nurgle-2`, `oc-chaos-lord-on-palanquin-of-nurgle-2-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-lord-on-palanquin-of-nurgle-3`, `oc-chaos-lord-on-palanquin-of-nurgle-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-lord-on-palanquin-of-nurgle-3`, `oc-chaos-lord-on-palanquin-of-nurgle-3-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-lord-on-steed-of-slaanesh`, `oc-chaos-lord-on-steed-of-slaanesh-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-lord-on-steed-of-slaanesh`, `oc-chaos-lord-on-steed-of-slaanesh-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-lord-on-steed-of-slaanesh-2`, `oc-chaos-lord-on-steed-of-slaanesh-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-lord-on-steed-of-slaanesh-2`, `oc-chaos-lord-on-steed-of-slaanesh-2-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-lord-with-jump-pack`, `oc-chaos-lord-with-jump-pack-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-lord-with-jump-pack-2`, `oc-chaos-lord-with-jump-pack-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-predator-annihilator`, `oc-chaos-predator-annihilator-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-predator-annihilator`, `oc-chaos-predator-annihilator-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-predator-annihilator-2`, `oc-chaos-predator-annihilator-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-predator-annihilator-2`, `oc-chaos-predator-annihilator-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-predator-annihilator-3`, `oc-chaos-predator-annihilator-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-predator-annihilator-3`, `oc-chaos-predator-annihilator-3-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-predator-annihilator-4`, `oc-chaos-predator-annihilator-4-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-predator-annihilator-4`, `oc-chaos-predator-annihilator-4-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-predator-destructor`, `oc-chaos-predator-destructor-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-predator-destructor`, `oc-chaos-predator-destructor-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-predator-destructor-2`, `oc-chaos-predator-destructor-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-predator-destructor-2`, `oc-chaos-predator-destructor-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-predator-destructor-3`, `oc-chaos-predator-destructor-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-predator-destructor-3`, `oc-chaos-predator-destructor-3-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-predator-destructor-4`, `oc-chaos-predator-destructor-4-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-predator-destructor-4`, `oc-chaos-predator-destructor-4-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-questoris-knight-magaera`, `oc-chaos-questoris-knight-magaera-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-questoris-knight-styrix`, `oc-chaos-questoris-knight-styrix-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-rhino`, `oc-chaos-rhino-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-rhino-2`, `oc-chaos-rhino-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-rhino-2`, `oc-chaos-rhino-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-rhino-3`, `oc-chaos-rhino-3-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-rhino-4`, `oc-chaos-rhino-4-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-rhino-4`, `oc-chaos-rhino-4-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-rhino-5`, `oc-chaos-rhino-5-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaos-rhino-5`, `oc-chaos-rhino-5-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaplain-in-terminator-armour`, `oc-chaplain-in-terminator-armour-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaplain-in-terminator-armour-2`, `oc-chaplain-in-terminator-armour-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaplain-in-terminator-armour-3`, `oc-chaplain-in-terminator-armour-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaplain-in-terminator-armour-4`, `oc-chaplain-in-terminator-armour-4-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaplain-in-terminator-armour-5`, `oc-chaplain-in-terminator-armour-5-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaplain-in-terminator-armour-6`, `oc-chaplain-in-terminator-armour-6-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaplain-venerable-dreadnought`, `oc-chaplain-venerable-dreadnought-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaplain-venerable-dreadnought`, `oc-chaplain-venerable-dreadnought-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaplain-venerable-dreadnought`, `oc-chaplain-venerable-dreadnought-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaplain-venerable-dreadnought`, `oc-chaplain-venerable-dreadnought-2-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaplain-venerable-dreadnought`, `oc-chaplain-venerable-dreadnought-2-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaplain-with-jump-pack`, `oc-chaplain-with-jump-pack-1-6` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaplain-with-jump-pack-2`, `oc-chaplain-with-jump-pack-2-1-6` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaplain-with-jump-pack-3`, `oc-chaplain-with-jump-pack-3-1-6` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaplain-with-jump-pack-4`, `oc-chaplain-with-jump-pack-4-1-6` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaplain-with-jump-pack-5`, `oc-chaplain-with-jump-pack-5-1-6` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chaplain-with-jump-pack-6`, `oc-chaplain-with-jump-pack-6-1-6` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chinork-warkopta`, `oc-chinork-warkopta-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chinork-warkopta`, `oc-chinork-warkopta-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chosen`, `oc-chosen-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chosen`, `oc-chosen-5-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chosen-2`, `oc-chosen-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-chosen-2`, `oc-chosen-2-5-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cobra`, `oc-cobra-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-command-squad`, `oc-command-squad-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-command-squad`, `oc-command-squad-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-command-squad`, `oc-command-squad-5-11` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-command-squad`, `oc-command-squad-5-13` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-command-squad`, `oc-command-squad-5-14` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-command-squad`, `oc-command-squad-5-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-commander-in-coldstar-battlesuit`, `oc-commander-in-coldstar-battlesuit-1-10` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-commander-in-coldstar-battlesuit`, `oc-commander-in-coldstar-battlesuit-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-commander-in-coldstar-battlesuit`, `oc-commander-in-coldstar-battlesuit-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-commander-in-coldstar-battlesuit`, `oc-commander-in-coldstar-battlesuit-1-8` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-commander-in-coldstar-battlesuit`, `oc-commander-in-coldstar-battlesuit-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-commander-in-coldstar-battlesuit`, `oc-commander-in-coldstar-battlesuit-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-commander-in-coldstar-battlesuit`, `oc-commander-in-coldstar-battlesuit-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-commander-in-coldstar-battlesuit`, `oc-commander-in-coldstar-battlesuit-3-10` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-commander-in-coldstar-battlesuit`, `oc-commander-in-coldstar-battlesuit-3-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-commander-in-coldstar-battlesuit`, `oc-commander-in-coldstar-battlesuit-3-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-commander-in-coldstar-battlesuit`, `oc-commander-in-coldstar-battlesuit-3-8` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-commander-in-crisis-battlesuit`, `oc-commander-in-crisis-battlesuit-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-commander-in-crisis-battlesuit`, `oc-commander-in-crisis-battlesuit-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-commander-in-crisis-battlesuit`, `oc-commander-in-crisis-battlesuit-1-7` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-commander-in-crisis-battlesuit`, `oc-commander-in-crisis-battlesuit-1-9` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-commander-in-crisis-battlesuit`, `oc-commander-in-crisis-battlesuit-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-commander-in-crisis-battlesuit`, `oc-commander-in-crisis-battlesuit-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-commander-in-crisis-battlesuit`, `oc-commander-in-crisis-battlesuit-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-commander-in-crisis-battlesuit`, `oc-commander-in-crisis-battlesuit-3-10` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-commander-in-crisis-battlesuit`, `oc-commander-in-crisis-battlesuit-3-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-commander-in-crisis-battlesuit`, `oc-commander-in-crisis-battlesuit-3-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-commander-in-crisis-battlesuit`, `oc-commander-in-crisis-battlesuit-3-8` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-commander-in-enforcer-battlesuit`, `oc-commander-in-enforcer-battlesuit-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-commander-in-enforcer-battlesuit`, `oc-commander-in-enforcer-battlesuit-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-commander-in-enforcer-battlesuit`, `oc-commander-in-enforcer-battlesuit-1-7` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-commander-in-enforcer-battlesuit`, `oc-commander-in-enforcer-battlesuit-1-9` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-commander-in-enforcer-battlesuit`, `oc-commander-in-enforcer-battlesuit-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-commander-in-enforcer-battlesuit`, `oc-commander-in-enforcer-battlesuit-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-commander-in-enforcer-battlesuit`, `oc-commander-in-enforcer-battlesuit-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-commander-in-enforcer-battlesuit`, `oc-commander-in-enforcer-battlesuit-3-10` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-commander-in-enforcer-battlesuit`, `oc-commander-in-enforcer-battlesuit-3-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-commander-in-enforcer-battlesuit`, `oc-commander-in-enforcer-battlesuit-3-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-commander-in-enforcer-battlesuit`, `oc-commander-in-enforcer-battlesuit-3-8` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-commissar`, `oc-commissar-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-company-veterans-on-bikes`, `oc-company-veterans-on-bikes-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-contemptor-achillus-dreadnought`, `oc-contemptor-achillus-dreadnought-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-contemptor-achillus-dreadnought`, `oc-contemptor-achillus-dreadnought-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-contemptor-achillus-dreadnought`, `oc-contemptor-achillus-dreadnought-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-contemptor-achillus-dreadnought`, `oc-contemptor-achillus-dreadnought-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-contemptor-achillus-dreadnought`, `oc-contemptor-achillus-dreadnought-1-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-corsair-reaver-band`, `oc-corsair-reaver-band-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-corsair-reaver-band-2`, `oc-corsair-reaver-band-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-corsair-skyreavers`, `oc-corsair-skyreavers-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-corsair-skyreavers`, `oc-corsair-skyreavers-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-corsair-skyreavers`, `oc-corsair-skyreavers-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-corsair-skyreavers`, `oc-corsair-skyreavers-2-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-corsair-skyreavers-2`, `oc-corsair-skyreavers-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-corsair-skyreavers-2`, `oc-corsair-skyreavers-2-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-corsair-skyreavers-2`, `oc-corsair-skyreavers-2-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-corsair-skyreavers-2`, `oc-corsair-skyreavers-2-2-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-corsair-voidreavers`, `oc-corsair-voidreavers-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-corsair-voidreavers-2`, `oc-corsair-voidreavers-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-corsair-voidscarred`, `oc-corsair-voidscarred-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-corsair-voidscarred`, `oc-corsair-voidscarred-8-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-corsair-voidscarred-2`, `oc-corsair-voidscarred-2-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-corsair-voidscarred-2`, `oc-corsair-voidscarred-2-8-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-corvus-blackstar`, `oc-corvus-blackstar-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-corvus-blackstar`, `oc-corvus-blackstar-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-corvus-blackstar`, `oc-corvus-blackstar-4-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-corvus-blackstar-2`, `oc-corvus-blackstar-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-corvus-blackstar-2`, `oc-corvus-blackstar-2-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-corvus-blackstar-2`, `oc-corvus-blackstar-2-4-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-crimson-hunter`, `oc-crimson-hunter-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-crisis-battlesuits`, `oc-crisis-battlesuits-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-crisis-battlesuits`, `oc-crisis-battlesuits-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-crisis-battlesuits`, `oc-crisis-battlesuits-1-7` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-crisis-battlesuits`, `oc-crisis-battlesuits-1-9` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-crisis-battlesuits`, `oc-crisis-battlesuits-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-crisis-battlesuits`, `oc-crisis-battlesuits-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-crisis-battlesuits`, `oc-crisis-battlesuits-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-crisis-fireknife-battlesuits`, `oc-crisis-fireknife-battlesuits-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-crisis-fireknife-battlesuits`, `oc-crisis-fireknife-battlesuits-3-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-crisis-fireknife-battlesuits`, `oc-crisis-fireknife-battlesuits-3-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-crisis-starscythe-battlesuits`, `oc-crisis-starscythe-battlesuits-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-crisis-starscythe-battlesuits`, `oc-crisis-starscythe-battlesuits-3-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-crisis-starscythe-battlesuits`, `oc-crisis-starscythe-battlesuits-3-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-crisis-sunforge-battlesuits`, `oc-crisis-sunforge-battlesuits-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-crisis-sunforge-battlesuits`, `oc-crisis-sunforge-battlesuits-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-crisis-sunforge-battlesuits`, `oc-crisis-sunforge-battlesuits-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-crusader-squad`, `oc-crusader-squad-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-crusader-squad`, `oc-crusader-squad-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-crusader-squad`, `oc-crusader-squad-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cultist-mob-with-firearms`, `oc-cultist-mob-with-firearms-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cultist-mob-with-firearms`, `oc-cultist-mob-with-firearms-5-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cultist-mob-with-firearms-2`, `oc-cultist-mob-with-firearms-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cultist-mob-with-firearms-2`, `oc-cultist-mob-with-firearms-2-5-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cultist-mob-with-firearms-3`, `oc-cultist-mob-with-firearms-3-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-cultist-mob-with-firearms-3`, `oc-cultist-mob-with-firearms-3-5-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-custodian-guard`, `oc-custodian-guard-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-custodian-guard`, `oc-custodian-guard-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-custodian-guard`, `oc-custodian-guard-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-custodian-guard-with-adrasite-and-pyrithite-spears`, `oc-custodian-guard-with-adrasite-and-pyrithite-spears-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-custodian-wardens`, `oc-custodian-wardens-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-custodian-wardens`, `oc-custodian-wardens-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-daemonettes`, `oc-daemonettes-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-daemonettes`, `oc-daemonettes-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-daemonettes-2`, `oc-daemonettes-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-daemonettes-2`, `oc-daemonettes-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-dakkajet`, `oc-dakkajet-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-damned-legionnaires`, `oc-damned-legionnaires-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-damned-legionnaires`, `oc-damned-legionnaires-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-damned-legionnaires`, `oc-damned-legionnaires-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-damned-legionnaires`, `oc-damned-legionnaires-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-damned-legionnaires`, `oc-damned-legionnaires-3-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-dark-reapers`, `oc-dark-reapers-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-company-captain-with-jump-pack`, `oc-death-company-captain-with-jump-pack-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-company-dreadnought`, `oc-death-company-dreadnought-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-company-dreadnought-with-magna-grapple`, `oc-death-company-dreadnought-with-magna-grapple-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-company-marines`, `oc-death-company-marines-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-company-marines`, `oc-death-company-marines-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-company-marines-with-bolt-rifles`, `oc-death-company-marines-with-bolt-rifles-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-company-marines-with-bolt-rifles`, `oc-death-company-marines-with-bolt-rifles-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-company-marines-with-boltguns`, `oc-death-company-marines-with-boltguns-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-company-marines-with-boltguns`, `oc-death-company-marines-with-boltguns-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-company-marines-with-boltguns-and-jump-packs`, `oc-death-company-marines-with-boltguns-and-jump-packs-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-company-marines-with-boltguns-and-jump-packs`, `oc-death-company-marines-with-boltguns-and-jump-packs-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-company-marines-with-jump-packs`, `oc-death-company-marines-with-jump-packs-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-company-marines-with-jump-packs`, `oc-death-company-marines-with-jump-packs-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-company-marines-with-jump-packs`, `oc-death-company-marines-with-jump-packs-4-10` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-company-marines-with-jump-packs`, `oc-death-company-marines-with-jump-packs-4-11` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-company-marines-with-jump-packs`, `oc-death-company-marines-with-jump-packs-4-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-company-marines-with-jump-packs`, `oc-death-company-marines-with-jump-packs-4-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-company-marines-with-jump-packs`, `oc-death-company-marines-with-jump-packs-4-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-company-marines-with-jump-packs`, `oc-death-company-marines-with-jump-packs-4-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-company-marines-with-jump-packs`, `oc-death-company-marines-with-jump-packs-4-6` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-company-marines-with-jump-packs`, `oc-death-company-marines-with-jump-packs-4-7` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-company-marines-with-jump-packs`, `oc-death-company-marines-with-jump-packs-4-8` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-company-marines-with-jump-packs`, `oc-death-company-marines-with-jump-packs-4-9` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-guard-chaos-lord`, `oc-death-guard-chaos-lord-1-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-guard-chaos-lord`, `oc-death-guard-chaos-lord-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-guard-chaos-lord-in-terminator-armour`, `oc-death-guard-chaos-lord-in-terminator-armour-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-guard-cultists`, `oc-death-guard-cultists-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-guard-possessed`, `oc-death-guard-possessed-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-guard-sorcerer-in-terminator-armour`, `oc-death-guard-sorcerer-in-terminator-armour-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-korps-grenadier-squad`, `oc-death-korps-grenadier-squad-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-korps-grenadier-squad`, `oc-death-korps-grenadier-squad-1-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-korps-grenadier-squad-2`, `oc-death-korps-grenadier-squad-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-korps-grenadier-squad-2`, `oc-death-korps-grenadier-squad-2-1-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-korps-of-krieg`, `oc-death-korps-of-krieg-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-korps-of-krieg`, `oc-death-korps-of-krieg-1-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-korps-of-krieg`, `oc-death-korps-of-krieg-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-korps-of-krieg`, `oc-death-korps-of-krieg-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-korps-of-krieg-2`, `oc-death-korps-of-krieg-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-korps-of-krieg-2`, `oc-death-korps-of-krieg-2-1-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-korps-of-krieg-2`, `oc-death-korps-of-krieg-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-death-korps-of-krieg-2`, `oc-death-korps-of-krieg-2-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-deathshroud-terminators`, `oc-deathshroud-terminators-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-deathshroud-terminators`, `oc-deathshroud-terminators-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-deathwatch-kill-team`, `oc-deathwatch-kill-team-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-deathwatch-kill-team`, `oc-deathwatch-kill-team-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-deathwatch-kill-team`, `oc-deathwatch-kill-team-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-deathwatch-terminator-squad`, `oc-deathwatch-terminator-squad-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-deathwatch-terminator-squad`, `oc-deathwatch-terminator-squad-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-deathwatch-terminator-squad`, `oc-deathwatch-terminator-squad-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-deathwatch-terminator-squad`, `oc-deathwatch-terminator-squad-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-deathwatch-terminator-squad`, `oc-deathwatch-terminator-squad-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-deathwatch-terminator-squad-2`, `oc-deathwatch-terminator-squad-2-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-deathwatch-terminator-squad-2`, `oc-deathwatch-terminator-squad-2-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-deathwatch-terminator-squad-2`, `oc-deathwatch-terminator-squad-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-deathwatch-terminator-squad-2`, `oc-deathwatch-terminator-squad-2-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-deathwatch-terminator-squad-2`, `oc-deathwatch-terminator-squad-2-2-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-deathwatch-veterans`, `oc-deathwatch-veterans-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-deathwatch-veterans`, `oc-deathwatch-veterans-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-deathwatch-veterans`, `oc-deathwatch-veterans-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-deathwing-command-squad`, `oc-deathwing-command-squad-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-deathwing-command-squad`, `oc-deathwing-command-squad-5-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-deathwing-knights`, `oc-deathwing-knights-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-deathwing-strikemaster`, `oc-deathwing-strikemaster-1-6` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-deathwing-terminator-squad`, `oc-deathwing-terminator-squad-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-decimator`, `oc-decimator-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-decimator`, `oc-decimator-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-decimus-kill-team`, `oc-decimus-kill-team-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-decimus-kill-team`, `oc-decimus-kill-team-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-decimus-kill-team`, `oc-decimus-kill-team-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-deff-rolla-battle-fortress`, `oc-deff-rolla-battle-fortress-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-deff-rolla-battle-fortress`, `oc-deff-rolla-battle-fortress-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-deffkoptas-with-big-shootas`, `oc-deffkoptas-with-big-shootas-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-defiler`, `oc-defiler-3-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-defiler`, `oc-defiler-4-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-defiler-2`, `oc-defiler-2-3-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-defiler-2`, `oc-defiler-2-4-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-defiler-3`, `oc-defiler-3-3-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-defiler-3`, `oc-defiler-3-4-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-defiler-4`, `oc-defiler-4-3-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-defiler-4`, `oc-defiler-4-4-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-defiler-5`, `oc-defiler-5-3-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-defiler-5`, `oc-defiler-5-4-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-deimos-predator`, `oc-deimos-predator-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-deimos-predator`, `oc-deimos-predator-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-deimos-predator`, `oc-deimos-predator-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-deredeo-dreadnought`, `oc-deredeo-dreadnought-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-deredeo-dreadnought-2`, `oc-deredeo-dreadnought-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-deredeo-dreadnought-3`, `oc-deredeo-dreadnought-3-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-deredeo-dreadnought-4`, `oc-deredeo-dreadnought-4-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-deredeo-dreadnought-5`, `oc-deredeo-dreadnought-5-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-devastator-squad`, `oc-devastator-squad-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-devastator-squad`, `oc-devastator-squad-1-6` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-devastator-squad`, `oc-devastator-squad-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-devastator-squad`, `oc-devastator-squad-2-6` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-devastator-squad-2`, `oc-devastator-squad-2-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-devastator-squad-2`, `oc-devastator-squad-2-1-6` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-devastator-squad-2`, `oc-devastator-squad-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-devastator-squad-2`, `oc-devastator-squad-2-2-6` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-devastator-squad-3`, `oc-devastator-squad-3-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-devastator-squad-3`, `oc-devastator-squad-3-1-6` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-devastator-squad-3`, `oc-devastator-squad-3-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-devastator-squad-3`, `oc-devastator-squad-3-2-6` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-devastator-squad-4`, `oc-devastator-squad-4-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-devastator-squad-4`, `oc-devastator-squad-4-1-6` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-devastator-squad-4`, `oc-devastator-squad-4-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-devastator-squad-4`, `oc-devastator-squad-4-2-6` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-devilfish`, `oc-devilfish-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-devilfish`, `oc-devilfish-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-dire-avengers`, `oc-dire-avengers-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-dominion-squad`, `oc-dominion-squad-1-6` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-dominion-squad`, `oc-dominion-squad-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-dominus-armoured-siege-bombard`, `oc-dominus-armoured-siege-bombard-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-dominus-armoured-siege-bombard`, `oc-dominus-armoured-siege-bombard-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-dominus-armoured-siege-bombard`, `oc-dominus-armoured-siege-bombard-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-dominus-armoured-siege-bombard-2`, `oc-dominus-armoured-siege-bombard-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-dominus-armoured-siege-bombard-2`, `oc-dominus-armoured-siege-bombard-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-dominus-armoured-siege-bombard-2`, `oc-dominus-armoured-siege-bombard-2-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-doomhammer`, `oc-doomhammer-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-doomhammer`, `oc-doomhammer-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-doomhammer`, `oc-doomhammer-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-doomhammer-2`, `oc-doomhammer-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-doomhammer-2`, `oc-doomhammer-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-doomhammer-2`, `oc-doomhammer-2-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-dragon-knights`, `oc-dragon-knights-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-dreadnought`, `oc-dreadnought-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-dreadnought`, `oc-dreadnought-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-dreadnought`, `oc-dreadnought-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-dreadnought-2`, `oc-dreadnought-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-dreadnought-2`, `oc-dreadnought-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-dreadnought-2`, `oc-dreadnought-2-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-dreadnought-3`, `oc-dreadnought-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-dreadnought-3`, `oc-dreadnought-3-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-dreadnought-3`, `oc-dreadnought-3-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-dreadnought-4`, `oc-dreadnought-4-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-dreadnought-4`, `oc-dreadnought-4-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-dreadnought-4`, `oc-dreadnought-4-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-dreadnought-5`, `oc-dreadnought-5-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-dreadnought-5`, `oc-dreadnought-5-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-dreadnought-5`, `oc-dreadnought-5-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-dreadnought-6`, `oc-dreadnought-6-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-dreadnought-6`, `oc-dreadnought-6-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-dreadnought-6`, `oc-dreadnought-6-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-einhyr-champion`, `oc-einhyr-champion-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-einhyr-hearthguard`, `oc-einhyr-hearthguard-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-ethereal`, `oc-ethereal-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-ethereal`, `oc-ethereal-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-ethereal`, `oc-ethereal-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-ethereal`, `oc-ethereal-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-exaction-squad`, `oc-exaction-squad-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-exaction-squad`, `oc-exaction-squad-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-exaction-squad`, `oc-exaction-squad-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-exaction-squad`, `oc-exaction-squad-5-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-falchion`, `oc-falchion-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-falchion-2`, `oc-falchion-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-falchion-3`, `oc-falchion-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-falchion-4`, `oc-falchion-4-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-falchion-5`, `oc-falchion-5-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-falcon`, `oc-falcon-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-farseer`, `oc-farseer-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-farseer-skyrunner`, `oc-farseer-skyrunner-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-fellblade`, `oc-fellblade-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-fellblade`, `oc-fellblade-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-fellblade-2`, `oc-fellblade-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-fellblade-2`, `oc-fellblade-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-fellblade-3`, `oc-fellblade-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-fellblade-3`, `oc-fellblade-3-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-fellblade-4`, `oc-fellblade-4-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-fellblade-4`, `oc-fellblade-4-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-fellblade-5`, `oc-fellblade-5-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-fellblade-5`, `oc-fellblade-5-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-fellgor-beastmen`, `oc-fellgor-beastmen-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-fellgor-beastmen`, `oc-fellgor-beastmen-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-fellgor-beastmen-2`, `oc-fellgor-beastmen-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-fellgor-beastmen-2`, `oc-fellgor-beastmen-2-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-fellgor-beastmen-3`, `oc-fellgor-beastmen-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-fellgor-beastmen-3`, `oc-fellgor-beastmen-3-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-fighta-bommer`, `oc-fighta-bommer-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-fighta-bommer`, `oc-fighta-bommer-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-fire-dragons`, `oc-fire-dragons-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-fire-raptor-gunship`, `oc-fire-raptor-gunship-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-fire-raptor-gunship`, `oc-fire-raptor-gunship-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-fire-raptor-gunship-2`, `oc-fire-raptor-gunship-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-fire-raptor-gunship-2`, `oc-fire-raptor-gunship-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-fire-raptor-gunship-3`, `oc-fire-raptor-gunship-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-fire-raptor-gunship-3`, `oc-fire-raptor-gunship-3-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-fire-raptor-gunship-4`, `oc-fire-raptor-gunship-4-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-fire-raptor-gunship-4`, `oc-fire-raptor-gunship-4-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-fire-raptor-gunship-5`, `oc-fire-raptor-gunship-5-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-fire-raptor-gunship-5`, `oc-fire-raptor-gunship-5-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-flash-gitz`, `oc-flash-gitz-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-foetid-bloat-drone`, `oc-foetid-bloat-drone-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-forgefiend`, `oc-forgefiend-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-forgefiend`, `oc-forgefiend-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-forgefiend-2`, `oc-forgefiend-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-forgefiend-2`, `oc-forgefiend-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-forgefiend-3`, `oc-forgefiend-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-forgefiend-3`, `oc-forgefiend-3-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-fortis-kill-team`, `oc-fortis-kill-team-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-fortis-kill-team-2`, `oc-fortis-kill-team-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-fortis-kill-team-2`, `oc-fortis-kill-team-2-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-furioso-dreadnought`, `oc-furioso-dreadnought-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-furioso-dreadnought`, `oc-furioso-dreadnought-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-furioso-dreadnought`, `oc-furioso-dreadnought-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-gargantuan-squiggoth`, `oc-gargantuan-squiggoth-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-ghostkeel-battlesuit`, `oc-ghostkeel-battlesuit-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-ghostkeel-battlesuit`, `oc-ghostkeel-battlesuit-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-gladiator-lancer`, `oc-gladiator-lancer-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-gladiator-lancer-2`, `oc-gladiator-lancer-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-gladiator-lancer-3`, `oc-gladiator-lancer-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-gladiator-lancer-4`, `oc-gladiator-lancer-4-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-gladiator-lancer-5`, `oc-gladiator-lancer-5-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-gladiator-lancer-6`, `oc-gladiator-lancer-6-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-gorgon-heavy-transport`, `oc-gorgon-heavy-transport-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-gorgon-heavy-transport`, `oc-gorgon-heavy-transport-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-gorgon-heavy-transport`, `oc-gorgon-heavy-transport-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-gorgon-heavy-transport-2`, `oc-gorgon-heavy-transport-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-gorgon-heavy-transport-2`, `oc-gorgon-heavy-transport-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-gorgon-heavy-transport-2`, `oc-gorgon-heavy-transport-2-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-grand-master-in-nemesis-dreadknight`, `oc-grand-master-in-nemesis-dreadknight-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-great-knarloc`, `oc-great-knarloc-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-great-knarloc`, `oc-great-knarloc-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-grey-hunters`, `oc-grey-hunters-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-grey-knights-dreadnought`, `oc-grey-knights-dreadnought-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-grey-knights-dreadnought`, `oc-grey-knights-dreadnought-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-grey-knights-dreadnought`, `oc-grey-knights-dreadnought-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-grey-knights-dreadnought`, `oc-grey-knights-dreadnought-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-grey-knights-dreadnought`, `oc-grey-knights-dreadnought-3-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-grey-knights-terminator-squad`, `oc-grey-knights-terminator-squad-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-guardian-defenders`, `oc-guardian-defenders-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-hammerhead-gunship`, `oc-hammerhead-gunship-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-hammerhead-gunship`, `oc-hammerhead-gunship-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-hammerhead-gunship`, `oc-hammerhead-gunship-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-hammerhead-gunship`, `oc-hammerhead-gunship-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-hand-of-the-archon`, `oc-hand-of-the-archon-10-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-hand-of-the-archon`, `oc-hand-of-the-archon-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-hand-of-the-archon`, `oc-hand-of-the-archon-3-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-hand-of-the-archon`, `oc-hand-of-the-archon-9-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-havocs`, `oc-havocs-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-havocs`, `oc-havocs-2-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-havocs`, `oc-havocs-3-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-havocs-2`, `oc-havocs-2-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-havocs-2`, `oc-havocs-2-2-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-havocs-2`, `oc-havocs-2-3-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-hearthkyn-warriors`, `oc-hearthkyn-warriors-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-hekaton-land-fortress`, `oc-hekaton-land-fortress-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-hekaton-land-fortress`, `oc-hekaton-land-fortress-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-helbrute-2`, `oc-helbrute-2-1-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-helbrute-2`, `oc-helbrute-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-hell-blade`, `oc-hell-blade-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-hell-blade-2`, `oc-hell-blade-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-hell-blade-3`, `oc-hell-blade-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-hell-blade-4`, `oc-hell-blade-4-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-hellblaster-squad`, `oc-hellblaster-squad-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-hellblaster-squad-2`, `oc-hellblaster-squad-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-hellblaster-squad-3`, `oc-hellblaster-squad-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-hellblaster-squad-4`, `oc-hellblaster-squad-4-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-hellblaster-squad-5`, `oc-hellblaster-squad-5-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-hellblaster-squad-6`, `oc-hellblaster-squad-6-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-hellhammer`, `oc-hellhammer-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-hellhammer`, `oc-hellhammer-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-hellhammer`, `oc-hellhammer-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-hellhammer-2`, `oc-hellhammer-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-hellhammer-2`, `oc-hellhammer-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-hellhammer-2`, `oc-hellhammer-2-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-hellions`, `oc-hellions-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-hellions`, `oc-hellions-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-hellions`, `oc-hellions-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-hernkyn-pioneers`, `oc-hernkyn-pioneers-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-hernkyn-pioneers`, `oc-hernkyn-pioneers-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-hernkyn-pioneers`, `oc-hernkyn-pioneers-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-hernkyn-yaegirs`, `oc-hernkyn-yaegirs-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-hornet`, `oc-hornet-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-howling-banshees`, `oc-howling-banshees-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-hybrid-metamorphs`, `oc-hybrid-metamorphs-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-imperial-navy-breachers`, `oc-imperial-navy-breachers-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-imperial-navy-breachers`, `oc-imperial-navy-breachers-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-imperial-navy-breachers`, `oc-imperial-navy-breachers-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-imperial-navy-breachers`, `oc-imperial-navy-breachers-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-imperial-navy-breachers`, `oc-imperial-navy-breachers-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-impulsor`, `oc-impulsor-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-impulsor`, `oc-impulsor-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-impulsor`, `oc-impulsor-3-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-impulsor`, `oc-impulsor-3-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-impulsor-2`, `oc-impulsor-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-impulsor-2`, `oc-impulsor-2-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-impulsor-2`, `oc-impulsor-2-3-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-impulsor-2`, `oc-impulsor-2-3-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-impulsor-3`, `oc-impulsor-3-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-impulsor-3`, `oc-impulsor-3-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-impulsor-3`, `oc-impulsor-3-3-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-impulsor-3`, `oc-impulsor-3-3-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-impulsor-4`, `oc-impulsor-4-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-impulsor-4`, `oc-impulsor-4-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-impulsor-4`, `oc-impulsor-4-3-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-impulsor-4`, `oc-impulsor-4-3-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-impulsor-5`, `oc-impulsor-5-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-impulsor-5`, `oc-impulsor-5-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-impulsor-5`, `oc-impulsor-5-3-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-impulsor-5`, `oc-impulsor-5-3-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-impulsor-6`, `oc-impulsor-6-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-impulsor-6`, `oc-impulsor-6-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-impulsor-6`, `oc-impulsor-6-3-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-impulsor-6`, `oc-impulsor-6-3-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-inceptor-squad`, `oc-inceptor-squad-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-inceptor-squad-2`, `oc-inceptor-squad-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-inceptor-squad-3`, `oc-inceptor-squad-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-inceptor-squad-4`, `oc-inceptor-squad-4-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-inceptor-squad-5`, `oc-inceptor-squad-5-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-inceptor-squad-6`, `oc-inceptor-squad-6-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-incubi`, `oc-incubi-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-incubi`, `oc-incubi-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-incursor-squad`, `oc-incursor-squad-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-incursor-squad-2`, `oc-incursor-squad-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-incursor-squad-3`, `oc-incursor-squad-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-incursor-squad-4`, `oc-incursor-squad-4-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-incursor-squad-5`, `oc-incursor-squad-5-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-incursor-squad-6`, `oc-incursor-squad-6-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-indomitor-kill-team`, `oc-indomitor-kill-team-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-indomitor-kill-team-2`, `oc-indomitor-kill-team-2-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-indomitor-kill-team-2`, `oc-indomitor-kill-team-2-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-infiltrator-squad`, `oc-infiltrator-squad-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-infiltrator-squad`, `oc-infiltrator-squad-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-infiltrator-squad-2`, `oc-infiltrator-squad-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-infiltrator-squad-2`, `oc-infiltrator-squad-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-infiltrator-squad-3`, `oc-infiltrator-squad-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-infiltrator-squad-3`, `oc-infiltrator-squad-3-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-infiltrator-squad-4`, `oc-infiltrator-squad-4-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-infiltrator-squad-4`, `oc-infiltrator-squad-4-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-infiltrator-squad-5`, `oc-infiltrator-squad-5-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-infiltrator-squad-5`, `oc-infiltrator-squad-5-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-infiltrator-squad-6`, `oc-infiltrator-squad-6-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-infiltrator-squad-6`, `oc-infiltrator-squad-6-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-infractors`, `oc-infractors-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-infractors`, `oc-infractors-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-inquisitor`, `oc-inquisitor-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-inquisitor-in-terminator-armour`, `oc-inquisitor-in-terminator-armour-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-inquisitorial-agents`, `oc-inquisitorial-agents-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-inquisitorial-agents`, `oc-inquisitorial-agents-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-inquisitorial-agents`, `oc-inquisitorial-agents-5-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-interceptor-squad`, `oc-interceptor-squad-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-interceptor-squad`, `oc-interceptor-squad-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-interceptor-squad`, `oc-interceptor-squad-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-intercessor-squad`, `oc-intercessor-squad-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-intercessor-squad`, `oc-intercessor-squad-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-intercessor-squad-2`, `oc-intercessor-squad-2-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-intercessor-squad-2`, `oc-intercessor-squad-2-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-intercessor-squad-3`, `oc-intercessor-squad-3-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-intercessor-squad-3`, `oc-intercessor-squad-3-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-intercessor-squad-4`, `oc-intercessor-squad-4-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-intercessor-squad-4`, `oc-intercessor-squad-4-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-intercessor-squad-5`, `oc-intercessor-squad-5-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-intercessor-squad-5`, `oc-intercessor-squad-5-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-intercessor-squad-6`, `oc-intercessor-squad-6-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-intercessor-squad-6`, `oc-intercessor-squad-6-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-ironclad-dreadnought`, `oc-ironclad-dreadnought-5-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-ironclad-dreadnought`, `oc-ironclad-dreadnought-6-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-ironkin-steeljacks-with-heavy-volkanite-disintegrators`, `oc-ironkin-steeljacks-with-heavy-volkanite-disintegrators-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-jakhals`, `oc-jakhals-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-javelin-attack-speeder`, `oc-javelin-attack-speeder-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-javelin-attack-speeder`, `oc-javelin-attack-speeder-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kabalite-warriors`, `oc-kabalite-warriors-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kabalite-warriors`, `oc-kabalite-warriors-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kahl`, `oc-kahl-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kannonwagon`, `oc-kannonwagon-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kapricus-carrier`, `oc-kapricus-carrier-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kasrkin`, `oc-kasrkin-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kasrkin`, `oc-kasrkin-1-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kasrkin`, `oc-kasrkin-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kasrkin`, `oc-kasrkin-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kasrkin`, `oc-kasrkin-6-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kasrkin-2`, `oc-kasrkin-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kasrkin-2`, `oc-kasrkin-2-1-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kasrkin-2`, `oc-kasrkin-2-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kasrkin-2`, `oc-kasrkin-2-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kasrkin-2`, `oc-kasrkin-2-6-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kastelan-robots`, `oc-kastelan-robots-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kastelan-robots`, `oc-kastelan-robots-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kataphron-destroyers`, `oc-kataphron-destroyers-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-keeper-of-secrets`, `oc-keeper-of-secrets-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-keeper-of-secrets-2`, `oc-keeper-of-secrets-2-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-khorne-berzerkers`, `oc-khorne-berzerkers-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-khorne-berzerkers`, `oc-khorne-berzerkers-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-khorne-berzerkers`, `oc-khorne-berzerkers-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-khorne-berzerkers-2`, `oc-khorne-berzerkers-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-khorne-berzerkers-2`, `oc-khorne-berzerkers-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-khorne-berzerkers-2`, `oc-khorne-berzerkers-2-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kill-krusha`, `oc-kill-krusha-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kill-krusha`, `oc-kill-krusha-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-knight-castellan`, `oc-knight-castellan-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-knight-centura`, `oc-knight-centura-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-knight-centura`, `oc-knight-centura-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-knight-crusader`, `oc-knight-crusader-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-knight-desecrator`, `oc-knight-desecrator-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-knight-despoiler`, `oc-knight-despoiler-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-knight-despoiler`, `oc-knight-despoiler-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-knight-despoiler`, `oc-knight-despoiler-3-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-knight-despoiler`, `oc-knight-despoiler-3-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-knight-destrier`, `oc-knight-destrier-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-knight-destrier`, `oc-knight-destrier-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-knight-destrier`, `oc-knight-destrier-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-knight-destrier`, `oc-knight-destrier-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-knight-errant`, `oc-knight-errant-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-knight-paladin`, `oc-knight-paladin-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-knight-preceptor`, `oc-knight-preceptor-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-knight-tyrant`, `oc-knight-tyrant-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-knight-tyrant`, `oc-knight-tyrant-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-knight-valiant`, `oc-knight-valiant-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-knight-warden`, `oc-knight-warden-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kommandos`, `oc-kommandos-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kommandos`, `oc-kommandos-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kommandos`, `oc-kommandos-5-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kommandos`, `oc-kommandos-6-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kommandos`, `oc-kommandos-7-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kratos`, `oc-kratos-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kratos`, `oc-kratos-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kratos`, `oc-kratos-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kratos`, `oc-kratos-3-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kratos-2`, `oc-kratos-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kratos-2`, `oc-kratos-2-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kratos-2`, `oc-kratos-2-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kratos-2`, `oc-kratos-2-3-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kratos-3`, `oc-kratos-3-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kratos-3`, `oc-kratos-3-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kratos-3`, `oc-kratos-3-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kratos-3`, `oc-kratos-3-3-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kratos-4`, `oc-kratos-4-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kratos-4`, `oc-kratos-4-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kratos-4`, `oc-kratos-4-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kratos-4`, `oc-kratos-4-3-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kratos-5`, `oc-kratos-5-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kratos-5`, `oc-kratos-5-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kratos-5`, `oc-kratos-5-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kratos-5`, `oc-kratos-5-3-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-krieg-combat-engineers`, `oc-krieg-combat-engineers-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-krieg-combat-engineers`, `oc-krieg-combat-engineers-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-krieg-combat-engineers`, `oc-krieg-combat-engineers-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-krieg-combat-engineers`, `oc-krieg-combat-engineers-4-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-krieg-combat-engineers-2`, `oc-krieg-combat-engineers-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-krieg-combat-engineers-2`, `oc-krieg-combat-engineers-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-krieg-combat-engineers-2`, `oc-krieg-combat-engineers-2-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-krieg-combat-engineers-2`, `oc-krieg-combat-engineers-2-4-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-krieg-command-squad`, `oc-krieg-command-squad-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-krieg-command-squad`, `oc-krieg-command-squad-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-krieg-command-squad`, `oc-krieg-command-squad-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-krieg-command-squad-2`, `oc-krieg-command-squad-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-krieg-command-squad-2`, `oc-krieg-command-squad-2-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-krieg-command-squad-2`, `oc-krieg-command-squad-2-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kroot-farstalkers`, `oc-kroot-farstalkers-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-kroot-lone-spear`, `oc-kroot-lone-spear-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-land-raider-proteus`, `oc-land-raider-proteus-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-land-raider-proteus-2`, `oc-land-raider-proteus-2-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-land-raider-proteus-3`, `oc-land-raider-proteus-3-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-land-raider-proteus-4`, `oc-land-raider-proteus-4-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-land-raider-proteus-5`, `oc-land-raider-proteus-5-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-legionaries`, `oc-legionaries-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-legionaries`, `oc-legionaries-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-legionaries`, `oc-legionaries-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-legionaries`, `oc-legionaries-7-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-legionaries`, `oc-legionaries-7-7` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-legionaries`, `oc-legionaries-7-8` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-legionaries-2`, `oc-legionaries-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-legionaries-2`, `oc-legionaries-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-legionaries-2`, `oc-legionaries-2-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-legionaries-2`, `oc-legionaries-2-7-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-legionaries-2`, `oc-legionaries-2-7-7` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-legionaries-2`, `oc-legionaries-2-7-8` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-battle-tank`, `oc-leman-russ-battle-tank-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-battle-tank`, `oc-leman-russ-battle-tank-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-battle-tank`, `oc-leman-russ-battle-tank-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-battle-tank`, `oc-leman-russ-battle-tank-2-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-battle-tank-2`, `oc-leman-russ-battle-tank-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-battle-tank-2`, `oc-leman-russ-battle-tank-2-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-battle-tank-2`, `oc-leman-russ-battle-tank-2-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-battle-tank-2`, `oc-leman-russ-battle-tank-2-2-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-commander`, `oc-leman-russ-commander-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-commander`, `oc-leman-russ-commander-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-commander`, `oc-leman-russ-commander-3-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-commander`, `oc-leman-russ-commander-3-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-commander`, `oc-leman-russ-commander-3-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-commander-2`, `oc-leman-russ-commander-2-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-commander-2`, `oc-leman-russ-commander-2-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-commander-2`, `oc-leman-russ-commander-2-3-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-commander-2`, `oc-leman-russ-commander-2-3-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-commander-2`, `oc-leman-russ-commander-2-3-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-demolisher`, `oc-leman-russ-demolisher-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-demolisher`, `oc-leman-russ-demolisher-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-demolisher`, `oc-leman-russ-demolisher-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-demolisher`, `oc-leman-russ-demolisher-2-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-demolisher-2`, `oc-leman-russ-demolisher-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-demolisher-2`, `oc-leman-russ-demolisher-2-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-demolisher-2`, `oc-leman-russ-demolisher-2-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-demolisher-2`, `oc-leman-russ-demolisher-2-2-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-eradicator`, `oc-leman-russ-eradicator-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-eradicator`, `oc-leman-russ-eradicator-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-eradicator`, `oc-leman-russ-eradicator-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-eradicator`, `oc-leman-russ-eradicator-2-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-eradicator-2`, `oc-leman-russ-eradicator-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-eradicator-2`, `oc-leman-russ-eradicator-2-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-eradicator-2`, `oc-leman-russ-eradicator-2-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-eradicator-2`, `oc-leman-russ-eradicator-2-2-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-executioner`, `oc-leman-russ-executioner-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-executioner`, `oc-leman-russ-executioner-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-executioner`, `oc-leman-russ-executioner-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-executioner`, `oc-leman-russ-executioner-2-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-executioner-2`, `oc-leman-russ-executioner-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-executioner-2`, `oc-leman-russ-executioner-2-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-executioner-2`, `oc-leman-russ-executioner-2-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-executioner-2`, `oc-leman-russ-executioner-2-2-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-exterminator`, `oc-leman-russ-exterminator-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-exterminator`, `oc-leman-russ-exterminator-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-exterminator`, `oc-leman-russ-exterminator-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-exterminator`, `oc-leman-russ-exterminator-2-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-exterminator-2`, `oc-leman-russ-exterminator-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-exterminator-2`, `oc-leman-russ-exterminator-2-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-exterminator-2`, `oc-leman-russ-exterminator-2-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-exterminator-2`, `oc-leman-russ-exterminator-2-2-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-punisher`, `oc-leman-russ-punisher-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-punisher`, `oc-leman-russ-punisher-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-punisher`, `oc-leman-russ-punisher-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-punisher`, `oc-leman-russ-punisher-2-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-punisher-2`, `oc-leman-russ-punisher-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-punisher-2`, `oc-leman-russ-punisher-2-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-punisher-2`, `oc-leman-russ-punisher-2-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-punisher-2`, `oc-leman-russ-punisher-2-2-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-vanquisher`, `oc-leman-russ-vanquisher-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-vanquisher`, `oc-leman-russ-vanquisher-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-vanquisher`, `oc-leman-russ-vanquisher-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-vanquisher`, `oc-leman-russ-vanquisher-2-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-vanquisher-2`, `oc-leman-russ-vanquisher-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-vanquisher-2`, `oc-leman-russ-vanquisher-2-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-vanquisher-2`, `oc-leman-russ-vanquisher-2-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leman-russ-vanquisher-2`, `oc-leman-russ-vanquisher-2-2-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leviathan-dreadnought`, `oc-leviathan-dreadnought-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leviathan-dreadnought`, `oc-leviathan-dreadnought-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leviathan-dreadnought`, `oc-leviathan-dreadnought-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leviathan-dreadnought`, `oc-leviathan-dreadnought-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leviathan-dreadnought-2`, `oc-leviathan-dreadnought-2-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leviathan-dreadnought-2`, `oc-leviathan-dreadnought-2-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leviathan-dreadnought-2`, `oc-leviathan-dreadnought-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leviathan-dreadnought-2`, `oc-leviathan-dreadnought-2-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leviathan-dreadnought-3`, `oc-leviathan-dreadnought-3-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leviathan-dreadnought-3`, `oc-leviathan-dreadnought-3-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leviathan-dreadnought-3`, `oc-leviathan-dreadnought-3-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leviathan-dreadnought-3`, `oc-leviathan-dreadnought-3-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leviathan-dreadnought-4`, `oc-leviathan-dreadnought-4-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leviathan-dreadnought-4`, `oc-leviathan-dreadnought-4-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leviathan-dreadnought-4`, `oc-leviathan-dreadnought-4-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leviathan-dreadnought-4`, `oc-leviathan-dreadnought-4-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leviathan-dreadnought-5`, `oc-leviathan-dreadnought-5-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leviathan-dreadnought-5`, `oc-leviathan-dreadnought-5-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leviathan-dreadnought-5`, `oc-leviathan-dreadnought-5-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-leviathan-dreadnought-5`, `oc-leviathan-dreadnought-5-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-librarian-on-bike`, `oc-librarian-on-bike-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-librarian-with-jump-pack`, `oc-librarian-with-jump-pack-1-6` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-lieutenant`, `oc-lieutenant-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-lieutenant`, `oc-lieutenant-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-lieutenant-2`, `oc-lieutenant-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-lieutenant-2`, `oc-lieutenant-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-lieutenant-3`, `oc-lieutenant-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-lieutenant-3`, `oc-lieutenant-3-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-lieutenant-4`, `oc-lieutenant-4-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-lieutenant-4`, `oc-lieutenant-4-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-lieutenant-5`, `oc-lieutenant-5-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-lieutenant-5`, `oc-lieutenant-5-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-lieutenant-6`, `oc-lieutenant-6-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-lieutenant-6`, `oc-lieutenant-6-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-lifta-wagon`, `oc-lifta-wagon-4-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-lifta-wagon`, `oc-lifta-wagon-4-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-lifta-wagon`, `oc-lifta-wagon-4-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-lokhust-lord`, `oc-lokhust-lord-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-lokhust-lord`, `oc-lokhust-lord-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-long-fangs`, `oc-long-fangs-1-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-long-fangs`, `oc-long-fangs-1-7` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-longstrike`, `oc-longstrike-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-longstrike`, `oc-longstrike-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-longstrike`, `oc-longstrike-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-longstrike`, `oc-longstrike-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-lord`, `oc-lord-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-lord-kakophonist`, `oc-lord-kakophonist-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-lychguard`, `oc-lychguard-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-lynx`, `oc-lynx-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-macharius`, `oc-macharius-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-macharius`, `oc-macharius-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-macharius-2`, `oc-macharius-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-macharius-2`, `oc-macharius-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-macharius-omega`, `oc-macharius-omega-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-macharius-omega`, `oc-macharius-omega-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-macharius-omega`, `oc-macharius-omega-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-macharius-omega-2`, `oc-macharius-omega-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-macharius-omega-2`, `oc-macharius-omega-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-macharius-omega-2`, `oc-macharius-omega-2-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-macharius-vanquisher`, `oc-macharius-vanquisher-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-macharius-vanquisher`, `oc-macharius-vanquisher-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-macharius-vanquisher-2`, `oc-macharius-vanquisher-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-macharius-vanquisher-2`, `oc-macharius-vanquisher-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-macharius-vulcan`, `oc-macharius-vulcan-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-macharius-vulcan`, `oc-macharius-vulcan-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-macharius-vulcan-2`, `oc-macharius-vulcan-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-macharius-vulcan-2`, `oc-macharius-vulcan-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-malcador`, `oc-malcador-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-malcador`, `oc-malcador-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-malcador-2`, `oc-malcador-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-malcador-2`, `oc-malcador-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-malcador-annihilator`, `oc-malcador-annihilator-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-malcador-annihilator`, `oc-malcador-annihilator-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-malcador-annihilator-2`, `oc-malcador-annihilator-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-malcador-annihilator-2`, `oc-malcador-annihilator-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-malcador-defender`, `oc-malcador-defender-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-malcador-defender`, `oc-malcador-defender-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-malcador-defender-2`, `oc-malcador-defender-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-malcador-defender-2`, `oc-malcador-defender-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-malcador-infernus`, `oc-malcador-infernus-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-malcador-infernus`, `oc-malcador-infernus-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-malcador-infernus`, `oc-malcador-infernus-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-malcador-infernus`, `oc-malcador-infernus-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-malcador-infernus-2`, `oc-malcador-infernus-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-malcador-infernus-2`, `oc-malcador-infernus-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-malcador-infernus-2`, `oc-malcador-infernus-2-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-malcador-infernus-2`, `oc-malcador-infernus-2-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-marauder-bomber`, `oc-marauder-bomber-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-marshal`, `oc-marshal-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mastodon`, `oc-mastodon-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mastodon`, `oc-mastodon-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mastodon`, `oc-mastodon-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mastodon`, `oc-mastodon-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mastodon`, `oc-mastodon-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mastodon`, `oc-mastodon-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mastodon-2`, `oc-mastodon-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mastodon-2`, `oc-mastodon-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mastodon-2`, `oc-mastodon-2-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mastodon-2`, `oc-mastodon-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mastodon-2`, `oc-mastodon-2-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mastodon-2`, `oc-mastodon-2-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mastodon-3`, `oc-mastodon-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mastodon-3`, `oc-mastodon-3-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mastodon-3`, `oc-mastodon-3-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mastodon-3`, `oc-mastodon-3-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mastodon-3`, `oc-mastodon-3-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mastodon-3`, `oc-mastodon-3-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mastodon-4`, `oc-mastodon-4-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mastodon-4`, `oc-mastodon-4-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mastodon-4`, `oc-mastodon-4-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mastodon-4`, `oc-mastodon-4-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mastodon-4`, `oc-mastodon-4-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mastodon-4`, `oc-mastodon-4-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mastodon-5`, `oc-mastodon-5-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mastodon-5`, `oc-mastodon-5-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mastodon-5`, `oc-mastodon-5-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mastodon-5`, `oc-mastodon-5-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mastodon-5`, `oc-mastodon-5-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mastodon-5`, `oc-mastodon-5-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-maulerfiend-3`, `oc-maulerfiend-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-maulerfiend-4`, `oc-maulerfiend-4-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-meganobz`, `oc-meganobz-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-meganobz`, `oc-meganobz-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-meganobz`, `oc-meganobz-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-meganobz`, `oc-meganobz-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mek-gunz`, `oc-mek-gunz-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-militarum-tempestus-command-squad`, `oc-militarum-tempestus-command-squad-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-militarum-tempestus-command-squad`, `oc-militarum-tempestus-command-squad-1-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-militarum-tempestus-command-squad`, `oc-militarum-tempestus-command-squad-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-militarum-tempestus-command-squad`, `oc-militarum-tempestus-command-squad-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-militarum-tempestus-command-squad`, `oc-militarum-tempestus-command-squad-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-militarum-tempestus-command-squad`, `oc-militarum-tempestus-command-squad-4-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-militarum-tempestus-command-squad`, `oc-militarum-tempestus-command-squad-5-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-militarum-tempestus-command-squad`, `oc-militarum-tempestus-command-squad-5-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-ministorum-priest`, `oc-ministorum-priest-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-ministorum-priest-2`, `oc-ministorum-priest-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-ministorum-priest-3`, `oc-ministorum-priest-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-monolith`, `oc-monolith-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mortifiers`, `oc-mortifiers-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mortifiers`, `oc-mortifiers-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mortifiers`, `oc-mortifiers-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mortifiers`, `oc-mortifiers-3-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mortis-dreadnought`, `oc-mortis-dreadnought-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mortis-dreadnought`, `oc-mortis-dreadnought-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mortis-dreadnought`, `oc-mortis-dreadnought-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mortis-dreadnought`, `oc-mortis-dreadnought-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mortis-dreadnought`, `oc-mortis-dreadnought-1-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mortis-dreadnought`, `oc-mortis-dreadnought-1-6` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mortis-dreadnought`, `oc-mortis-dreadnought-1-7` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mukaali-riders`, `oc-mukaali-riders-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mukaali-riders`, `oc-mukaali-riders-3-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mukaali-riders`, `oc-mukaali-riders-3-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mukaali-riders-2`, `oc-mukaali-riders-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mukaali-riders-2`, `oc-mukaali-riders-2-3-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-mukaali-riders-2`, `oc-mukaali-riders-2-3-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-munitorum-servitors`, `oc-munitorum-servitors-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-munitorum-servitors-2`, `oc-munitorum-servitors-2-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-nemesis-claw`, `oc-nemesis-claw-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-nemesis-claw`, `oc-nemesis-claw-5-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-nemesis-dreadknight`, `oc-nemesis-dreadknight-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-neophyte-hybrids`, `oc-neophyte-hybrids-3-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-neophyte-hybrids`, `oc-neophyte-hybrids-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-neophyte-hybrids`, `oc-neophyte-hybrids-4-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-nobz`, `oc-nobz-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-nobz`, `oc-nobz-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-noise-marines`, `oc-noise-marines-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-noise-marines-2`, `oc-noise-marines-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-ogryn-bodyguard`, `oc-ogryn-bodyguard-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-ogryn-bodyguard`, `oc-ogryn-bodyguard-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-onager-dunecrawler`, `oc-onager-dunecrawler-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-onager-dunecrawler`, `oc-onager-dunecrawler-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-onager-dunecrawler`, `oc-onager-dunecrawler-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-onager-dunecrawler`, `oc-onager-dunecrawler-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-overlord`, `oc-overlord-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-painboss`, `oc-painboss-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-painboy`, `oc-painboy-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-paladin-squad`, `oc-paladin-squad-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-paladin-squad`, `oc-paladin-squad-3-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-paladin-squad`, `oc-paladin-squad-3-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-paladin-squad`, `oc-paladin-squad-3-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-palatine`, `oc-palatine-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-pathfinder-team`, `oc-pathfinder-team-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-pathfinder-team`, `oc-pathfinder-team-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-pathfinder-team`, `oc-pathfinder-team-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-pathfinder-team`, `oc-pathfinder-team-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-pathfinder-team`, `oc-pathfinder-team-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-pathfinder-team`, `oc-pathfinder-team-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-pathfinder-team`, `oc-pathfinder-team-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-pathfinder-team`, `oc-pathfinder-team-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-penitent-engines`, `oc-penitent-engines-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-phantom-titan`, `oc-phantom-titan-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-phantom-titan`, `oc-phantom-titan-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-phantom-titan`, `oc-phantom-titan-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-phantom-titan`, `oc-phantom-titan-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-phantom-titan`, `oc-phantom-titan-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-phantom-titan`, `oc-phantom-titan-2-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-pink-horrors`, `oc-pink-horrors-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-pink-horrors`, `oc-pink-horrors-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-pink-horrors-2`, `oc-pink-horrors-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-pink-horrors-2`, `oc-pink-horrors-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-plague-drones`, `oc-plague-drones-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-plague-drones`, `oc-plague-drones-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-plague-drones-2`, `oc-plague-drones-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-plague-drones-2`, `oc-plague-drones-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-plague-marines`, `oc-plague-marines-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-plague-marines`, `oc-plague-marines-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-plague-marines`, `oc-plague-marines-5-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-plague-marines-2`, `oc-plague-marines-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-plague-marines-2`, `oc-plague-marines-2-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-plague-marines-2`, `oc-plague-marines-2-5-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-plaguebearers`, `oc-plaguebearers-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-plaguebearers`, `oc-plaguebearers-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-plaguebearers-2`, `oc-plaguebearers-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-plaguebearers-2`, `oc-plaguebearers-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-plagueburst-crawler`, `oc-plagueburst-crawler-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-possessed`, `oc-possessed-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-possessed-2`, `oc-possessed-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-pox-riders`, `oc-pox-riders-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-pox-riders`, `oc-pox-riders-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-predator-annihilator`, `oc-predator-annihilator-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-predator-annihilator`, `oc-predator-annihilator-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-predator-annihilator-2`, `oc-predator-annihilator-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-predator-annihilator-2`, `oc-predator-annihilator-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-predator-annihilator-3`, `oc-predator-annihilator-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-predator-annihilator-3`, `oc-predator-annihilator-3-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-predator-annihilator-4`, `oc-predator-annihilator-4-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-predator-annihilator-4`, `oc-predator-annihilator-4-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-predator-annihilator-5`, `oc-predator-annihilator-5-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-predator-annihilator-5`, `oc-predator-annihilator-5-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-predator-annihilator-6`, `oc-predator-annihilator-6-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-predator-annihilator-6`, `oc-predator-annihilator-6-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-predator-destructor`, `oc-predator-destructor-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-predator-destructor`, `oc-predator-destructor-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-predator-destructor-2`, `oc-predator-destructor-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-predator-destructor-2`, `oc-predator-destructor-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-predator-destructor-3`, `oc-predator-destructor-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-predator-destructor-3`, `oc-predator-destructor-3-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-predator-destructor-4`, `oc-predator-destructor-4-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-predator-destructor-4`, `oc-predator-destructor-4-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-predator-destructor-5`, `oc-predator-destructor-5-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-predator-destructor-5`, `oc-predator-destructor-5-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-predator-destructor-6`, `oc-predator-destructor-6-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-predator-destructor-6`, `oc-predator-destructor-6-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-proteus-kill-team`, `oc-proteus-kill-team-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-proteus-kill-team`, `oc-proteus-kill-team-6-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-proteus-kill-team`, `oc-proteus-kill-team-6-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-purgation-squad`, `oc-purgation-squad-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-purgation-squad`, `oc-purgation-squad-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-purgation-squad`, `oc-purgation-squad-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-purifier-squad`, `oc-purifier-squad-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-purifier-squad`, `oc-purifier-squad-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-purifier-squad`, `oc-purifier-squad-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-questoris-knight-magaera`, `oc-questoris-knight-magaera-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-questoris-knight-styrix`, `oc-questoris-knight-styrix-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-rapier-carrier`, `oc-rapier-carrier-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-rapier-carrier-2`, `oc-rapier-carrier-2-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-rapier-carrier-3`, `oc-rapier-carrier-3-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-rapier-carrier-4`, `oc-rapier-carrier-4-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-rapier-carrier-5`, `oc-rapier-carrier-5-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-raptors`, `oc-raptors-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-raptors`, `oc-raptors-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-raptors`, `oc-raptors-6-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-raptors`, `oc-raptors-6-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-raptors`, `oc-raptors-6-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-raptors-2`, `oc-raptors-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-raptors-2`, `oc-raptors-2-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-raptors-2`, `oc-raptors-2-6-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-raptors-2`, `oc-raptors-2-6-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-raptors-2`, `oc-raptors-2-6-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-ravenwing-command-squad`, `oc-ravenwing-command-squad-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-razorwing-jetfighter`, `oc-razorwing-jetfighter-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-reaver-titan`, `oc-reaver-titan-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-reavers`, `oc-reavers-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-reavers`, `oc-reavers-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-red-corsairs-reave-captain`, `oc-red-corsairs-reave-captain-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-redemptor-dreadnought`, `oc-redemptor-dreadnought-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-redemptor-dreadnought-2`, `oc-redemptor-dreadnought-2-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-redemptor-dreadnought-3`, `oc-redemptor-dreadnought-3-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-redemptor-dreadnought-4`, `oc-redemptor-dreadnought-4-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-redemptor-dreadnought-5`, `oc-redemptor-dreadnought-5-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-redemptor-dreadnought-6`, `oc-redemptor-dreadnought-6-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-reiver-squad`, `oc-reiver-squad-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-reiver-squad-2`, `oc-reiver-squad-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-reiver-squad-3`, `oc-reiver-squad-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-reiver-squad-4`, `oc-reiver-squad-4-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-reiver-squad-5`, `oc-reiver-squad-5-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-reiver-squad-6`, `oc-reiver-squad-6-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-relic-contemptor-dreadnought`, `oc-relic-contemptor-dreadnought-1-8` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-relic-contemptor-dreadnought`, `oc-relic-contemptor-dreadnought-1-9` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-relic-contemptor-dreadnought`, `oc-relic-contemptor-dreadnought-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-relic-contemptor-dreadnought`, `oc-relic-contemptor-dreadnought-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-relic-contemptor-dreadnought-2`, `oc-relic-contemptor-dreadnought-2-1-8` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-relic-contemptor-dreadnought-2`, `oc-relic-contemptor-dreadnought-2-1-9` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-relic-contemptor-dreadnought-2`, `oc-relic-contemptor-dreadnought-2-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-relic-contemptor-dreadnought-2`, `oc-relic-contemptor-dreadnought-2-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-relic-contemptor-dreadnought-3`, `oc-relic-contemptor-dreadnought-3-1-8` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-relic-contemptor-dreadnought-3`, `oc-relic-contemptor-dreadnought-3-1-9` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-relic-contemptor-dreadnought-3`, `oc-relic-contemptor-dreadnought-3-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-relic-contemptor-dreadnought-3`, `oc-relic-contemptor-dreadnought-3-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-relic-contemptor-dreadnought-4`, `oc-relic-contemptor-dreadnought-4-1-8` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-relic-contemptor-dreadnought-4`, `oc-relic-contemptor-dreadnought-4-1-9` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-relic-contemptor-dreadnought-4`, `oc-relic-contemptor-dreadnought-4-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-relic-contemptor-dreadnought-4`, `oc-relic-contemptor-dreadnought-4-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-relic-contemptor-dreadnought-5`, `oc-relic-contemptor-dreadnought-5-1-8` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-relic-contemptor-dreadnought-5`, `oc-relic-contemptor-dreadnought-5-1-9` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-relic-contemptor-dreadnought-5`, `oc-relic-contemptor-dreadnought-5-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-relic-contemptor-dreadnought-5`, `oc-relic-contemptor-dreadnought-5-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-relic-terminator-squad`, `oc-relic-terminator-squad-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-relic-terminator-squad`, `oc-relic-terminator-squad-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-relic-terminator-squad`, `oc-relic-terminator-squad-5-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-retributor-squad`, `oc-retributor-squad-1-6` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-rhino-5`, `oc-rhino-5-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-riptide-battlesuit`, `oc-riptide-battlesuit-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-riptide-battlesuit`, `oc-riptide-battlesuit-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-rogal-dorn-battle-tank`, `oc-rogal-dorn-battle-tank-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-rogal-dorn-battle-tank`, `oc-rogal-dorn-battle-tank-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-rogal-dorn-battle-tank`, `oc-rogal-dorn-battle-tank-3-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-rogal-dorn-battle-tank`, `oc-rogal-dorn-battle-tank-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-rogal-dorn-battle-tank`, `oc-rogal-dorn-battle-tank-4-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-rogal-dorn-battle-tank-2`, `oc-rogal-dorn-battle-tank-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-rogal-dorn-battle-tank-2`, `oc-rogal-dorn-battle-tank-2-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-rogal-dorn-battle-tank-2`, `oc-rogal-dorn-battle-tank-2-3-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-rogal-dorn-battle-tank-2`, `oc-rogal-dorn-battle-tank-2-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-rogal-dorn-battle-tank-2`, `oc-rogal-dorn-battle-tank-2-4-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-rogal-dorn-commander`, `oc-rogal-dorn-commander-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-rogal-dorn-commander`, `oc-rogal-dorn-commander-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-rogal-dorn-commander`, `oc-rogal-dorn-commander-3-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-rogal-dorn-commander`, `oc-rogal-dorn-commander-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-rogal-dorn-commander`, `oc-rogal-dorn-commander-4-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-rogal-dorn-commander-2`, `oc-rogal-dorn-commander-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-rogal-dorn-commander-2`, `oc-rogal-dorn-commander-2-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-rogal-dorn-commander-2`, `oc-rogal-dorn-commander-2-3-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-rogal-dorn-commander-2`, `oc-rogal-dorn-commander-2-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-rogal-dorn-commander-2`, `oc-rogal-dorn-commander-2-4-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-rubric-marines`, `oc-rubric-marines-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-rubric-marines-2`, `oc-rubric-marines-2-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-rvarna-battlesuit`, `oc-rvarna-battlesuit-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sagitaur`, `oc-sagitaur-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sanctifiers`, `oc-sanctifiers-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sanctifiers-2`, `oc-sanctifiers-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sanctus`, `oc-sanctus-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sanguinary-guard`, `oc-sanguinary-guard-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-scorpion`, `oc-scorpion-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-scourges-with-heavy-weapons`, `oc-scourges-with-heavy-weapons-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-scourges-with-heavy-weapons`, `oc-scourges-with-heavy-weapons-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-scourges-with-shardcarbines`, `oc-scourges-with-shardcarbines-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-scourges-with-shardcarbines`, `oc-scourges-with-shardcarbines-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-scout-bike-squad`, `oc-scout-bike-squad-1-7` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-scout-bike-squad`, `oc-scout-bike-squad-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-scout-sentinels`, `oc-scout-sentinels-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-scout-sentinels`, `oc-scout-sentinels-1-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-scout-sentinels-2`, `oc-scout-sentinels-2-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-scout-sentinels-2`, `oc-scout-sentinels-2-1-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-scout-sniper-squad`, `oc-scout-sniper-squad-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-scout-squad`, `oc-scout-squad-4-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-scout-squad-2`, `oc-scout-squad-2-4-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-scout-squad-3`, `oc-scout-squad-3-4-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-scout-squad-4`, `oc-scout-squad-4-4-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-scout-squad-5`, `oc-scout-squad-5-4-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-secutarii-hoplites`, `oc-secutarii-hoplites-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-secutarii-hoplites`, `oc-secutarii-hoplites-3-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-secutarii-peltasts`, `oc-secutarii-peltasts-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-secutarii-peltasts`, `oc-secutarii-peltasts-3-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-seekers`, `oc-seekers-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-seekers`, `oc-seekers-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-seekers-2`, `oc-seekers-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-seekers-2`, `oc-seekers-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sekhetar-robots`, `oc-sekhetar-robots-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-seraphim-squad`, `oc-seraphim-squad-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-seraphim-squad`, `oc-seraphim-squad-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-seraphim-squad`, `oc-seraphim-squad-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-seraphim-squad`, `oc-seraphim-squad-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-seraphim-squad`, `oc-seraphim-squad-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-seraphim-squad`, `oc-seraphim-squad-2-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-seraphim-squad`, `oc-seraphim-squad-2-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-seraptek-heavy-construct`, `oc-seraptek-heavy-construct-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-serberys-raiders`, `oc-serberys-raiders-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-serberys-sulphurhounds`, `oc-serberys-sulphurhounds-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-servitors`, `oc-servitors-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-servitors`, `oc-servitors-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-servitors`, `oc-servitors-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-shadowsword`, `oc-shadowsword-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-shadowsword`, `oc-shadowsword-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-shadowsword`, `oc-shadowsword-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-shadowsword-2`, `oc-shadowsword-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-shadowsword-2`, `oc-shadowsword-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-shadowsword-2`, `oc-shadowsword-2-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-shield-captain`, `oc-shield-captain-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-shield-captain`, `oc-shield-captain-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-shield-captain`, `oc-shield-captain-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-shield-captain`, `oc-shield-captain-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-shield-captain-in-allarus-terminator-armour`, `oc-shield-captain-in-allarus-terminator-armour-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-shining-spears`, `oc-shining-spears-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-shining-spears`, `oc-shining-spears-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sicaran-arcus`, `oc-sicaran-arcus-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sicaran-arcus`, `oc-sicaran-arcus-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sicaran-battle-tank`, `oc-sicaran-battle-tank-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sicaran-battle-tank`, `oc-sicaran-battle-tank-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sicaran-battle-tank-2`, `oc-sicaran-battle-tank-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sicaran-battle-tank-2`, `oc-sicaran-battle-tank-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sicaran-battle-tank-3`, `oc-sicaran-battle-tank-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sicaran-battle-tank-3`, `oc-sicaran-battle-tank-3-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sicaran-battle-tank-4`, `oc-sicaran-battle-tank-4-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sicaran-battle-tank-4`, `oc-sicaran-battle-tank-4-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sicaran-battle-tank-5`, `oc-sicaran-battle-tank-5-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sicaran-battle-tank-5`, `oc-sicaran-battle-tank-5-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sicaran-omega`, `oc-sicaran-omega-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sicaran-omega`, `oc-sicaran-omega-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sicaran-punisher`, `oc-sicaran-punisher-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sicaran-punisher`, `oc-sicaran-punisher-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sicaran-punisher-2`, `oc-sicaran-punisher-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sicaran-punisher-2`, `oc-sicaran-punisher-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sicaran-punisher-3`, `oc-sicaran-punisher-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sicaran-punisher-3`, `oc-sicaran-punisher-3-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sicaran-punisher-4`, `oc-sicaran-punisher-4-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sicaran-punisher-4`, `oc-sicaran-punisher-4-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sicaran-punisher-5`, `oc-sicaran-punisher-5-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sicaran-punisher-5`, `oc-sicaran-punisher-5-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sicaran-venator`, `oc-sicaran-venator-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sicaran-venator`, `oc-sicaran-venator-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sicaran-venator-2`, `oc-sicaran-venator-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sicaran-venator-2`, `oc-sicaran-venator-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sicaran-venator-3`, `oc-sicaran-venator-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sicaran-venator-3`, `oc-sicaran-venator-3-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sicaran-venator-4`, `oc-sicaran-venator-4-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sicaran-venator-4`, `oc-sicaran-venator-4-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sicaran-venator-5`, `oc-sicaran-venator-5-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sicaran-venator-5`, `oc-sicaran-venator-5-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sicarian-infiltrators`, `oc-sicarian-infiltrators-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sisters-novitiate-squad`, `oc-sisters-novitiate-squad-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sisters-novitiate-squad`, `oc-sisters-novitiate-squad-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sisters-novitiate-squad`, `oc-sisters-novitiate-squad-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sisters-novitiate-squad`, `oc-sisters-novitiate-squad-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sisters-of-battle-squad`, `oc-sisters-of-battle-squad-1-6` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sisters-of-battle-squad`, `oc-sisters-of-battle-squad-5-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-skathach-wraithknight`, `oc-skathach-wraithknight-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-skathach-wraithknight`, `oc-skathach-wraithknight-3-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-skitarii-rangers`, `oc-skitarii-rangers-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-skitarii-rangers`, `oc-skitarii-rangers-6-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-skitarii-rangers`, `oc-skitarii-rangers-6-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-skitarii-rangers-2`, `oc-skitarii-rangers-2-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-skitarii-rangers-2`, `oc-skitarii-rangers-2-6-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-skitarii-rangers-2`, `oc-skitarii-rangers-2-6-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-skitarii-vanguard`, `oc-skitarii-vanguard-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-skitarii-vanguard`, `oc-skitarii-vanguard-6-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-skitarii-vanguard`, `oc-skitarii-vanguard-6-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-skitarii-vanguard-2`, `oc-skitarii-vanguard-2-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-skitarii-vanguard-2`, `oc-skitarii-vanguard-2-6-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-skitarii-vanguard-2`, `oc-skitarii-vanguard-2-6-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sky-ray-gunship`, `oc-sky-ray-gunship-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sky-ray-gunship`, `oc-sky-ray-gunship-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-skyclaws`, `oc-skyclaws-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-skyclaws`, `oc-skyclaws-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-skyclaws`, `oc-skyclaws-3-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-skyclaws`, `oc-skyclaws-3-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-skyclaws`, `oc-skyclaws-3-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-skyclaws`, `oc-skyclaws-3-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sorcerer-in-terminator-armour`, `oc-sorcerer-in-terminator-armour-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sorcerer-in-terminator-armour-3`, `oc-sorcerer-in-terminator-armour-3-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sorcerer-on-bike`, `oc-sorcerer-on-bike-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sorcerer-on-disc-of-tzeentch`, `oc-sorcerer-on-disc-of-tzeentch-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sorcerer-on-disc-of-tzeentch-2`, `oc-sorcerer-on-disc-of-tzeentch-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sorcerer-on-palanquin-of-nurgle`, `oc-sorcerer-on-palanquin-of-nurgle-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sorcerer-on-palanquin-of-nurgle-2`, `oc-sorcerer-on-palanquin-of-nurgle-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sorcerer-on-palanquin-of-nurgle-3`, `oc-sorcerer-on-palanquin-of-nurgle-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sorcerer-on-steed-of-slaanesh`, `oc-sorcerer-on-steed-of-slaanesh-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sorcerer-on-steed-of-slaanesh-2`, `oc-sorcerer-on-steed-of-slaanesh-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-spartan`, `oc-spartan-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-spartan-2`, `oc-spartan-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-spartan-3`, `oc-spartan-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-spartan-4`, `oc-spartan-4-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-spartan-5`, `oc-spartan-5-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-squiggoth`, `oc-squiggoth-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-squighog-boyz`, `oc-squighog-boyz-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stealth-battlesuits`, `oc-stealth-battlesuits-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stealth-battlesuits`, `oc-stealth-battlesuits-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stealth-battlesuits`, `oc-stealth-battlesuits-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sternguard-veteran-squad`, `oc-sternguard-veteran-squad-1-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sternguard-veteran-squad`, `oc-sternguard-veteran-squad-1-6` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sternguard-veteran-squad`, `oc-sternguard-veteran-squad-1-7` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sternguard-veteran-squad-2`, `oc-sternguard-veteran-squad-2-1-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sternguard-veteran-squad-2`, `oc-sternguard-veteran-squad-2-1-6` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sternguard-veteran-squad-2`, `oc-sternguard-veteran-squad-2-1-7` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sternguard-veteran-squad-3`, `oc-sternguard-veteran-squad-3-1-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sternguard-veteran-squad-3`, `oc-sternguard-veteran-squad-3-1-6` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sternguard-veteran-squad-3`, `oc-sternguard-veteran-squad-3-1-7` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sternguard-veteran-squad-4`, `oc-sternguard-veteran-squad-4-1-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sternguard-veteran-squad-4`, `oc-sternguard-veteran-squad-4-1-6` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sternguard-veteran-squad-4`, `oc-sternguard-veteran-squad-4-1-7` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sternguard-veteran-squad-5`, `oc-sternguard-veteran-squad-5-1-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sternguard-veteran-squad-5`, `oc-sternguard-veteran-squad-5-1-6` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sternguard-veteran-squad-5`, `oc-sternguard-veteran-squad-5-1-7` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sternguard-veteran-squad-6`, `oc-sternguard-veteran-squad-6-1-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sternguard-veteran-squad-6`, `oc-sternguard-veteran-squad-6-1-6` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sternguard-veteran-squad-6`, `oc-sternguard-veteran-squad-6-1-7` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-storm-eagle-gunship`, `oc-storm-eagle-gunship-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-storm-eagle-gunship`, `oc-storm-eagle-gunship-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-storm-eagle-gunship-2`, `oc-storm-eagle-gunship-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-storm-eagle-gunship-2`, `oc-storm-eagle-gunship-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-storm-eagle-gunship-3`, `oc-storm-eagle-gunship-3-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-storm-eagle-gunship-3`, `oc-storm-eagle-gunship-3-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-storm-eagle-gunship-4`, `oc-storm-eagle-gunship-4-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-storm-eagle-gunship-4`, `oc-storm-eagle-gunship-4-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-storm-eagle-gunship-5`, `oc-storm-eagle-gunship-5-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-storm-eagle-gunship-5`, `oc-storm-eagle-gunship-5-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormblade`, `oc-stormblade-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormblade`, `oc-stormblade-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormblade`, `oc-stormblade-4-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormblade-2`, `oc-stormblade-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormblade-2`, `oc-stormblade-2-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormblade-2`, `oc-stormblade-2-4-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormfang-gunship`, `oc-stormfang-gunship-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormfang-gunship`, `oc-stormfang-gunship-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormhawk-interceptor`, `oc-stormhawk-interceptor-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormhawk-interceptor-2`, `oc-stormhawk-interceptor-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormhawk-interceptor-3`, `oc-stormhawk-interceptor-3-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormhawk-interceptor-4`, `oc-stormhawk-interceptor-4-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormhawk-interceptor-5`, `oc-stormhawk-interceptor-5-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormhawk-interceptor-6`, `oc-stormhawk-interceptor-6-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormhawk-interceptor-7`, `oc-stormhawk-interceptor-7-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormlord`, `oc-stormlord-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormlord`, `oc-stormlord-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormlord`, `oc-stormlord-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormlord-2`, `oc-stormlord-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormlord-2`, `oc-stormlord-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormlord-2`, `oc-stormlord-2-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormraven-gunship`, `oc-stormraven-gunship-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormraven-gunship`, `oc-stormraven-gunship-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormraven-gunship-2`, `oc-stormraven-gunship-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormraven-gunship-2`, `oc-stormraven-gunship-2-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormraven-gunship-3`, `oc-stormraven-gunship-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormraven-gunship-3`, `oc-stormraven-gunship-3-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormraven-gunship-4`, `oc-stormraven-gunship-4-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormraven-gunship-4`, `oc-stormraven-gunship-4-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormraven-gunship-5`, `oc-stormraven-gunship-5-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormraven-gunship-5`, `oc-stormraven-gunship-5-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormraven-gunship-6`, `oc-stormraven-gunship-6-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormraven-gunship-6`, `oc-stormraven-gunship-6-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormraven-gunship-7`, `oc-stormraven-gunship-7-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormraven-gunship-7`, `oc-stormraven-gunship-7-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormsurge`, `oc-stormsurge-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormsword`, `oc-stormsword-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormsword`, `oc-stormsword-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormsword`, `oc-stormsword-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormsword-2`, `oc-stormsword-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormsword-2`, `oc-stormsword-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormsword-2`, `oc-stormsword-2-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormtalon-gunship`, `oc-stormtalon-gunship-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormtalon-gunship-2`, `oc-stormtalon-gunship-2-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormtalon-gunship-3`, `oc-stormtalon-gunship-3-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormtalon-gunship-4`, `oc-stormtalon-gunship-4-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormtalon-gunship-5`, `oc-stormtalon-gunship-5-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormtalon-gunship-6`, `oc-stormtalon-gunship-6-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-stormtalon-gunship-7`, `oc-stormtalon-gunship-7-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-strike-squad`, `oc-strike-squad-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-strike-squad`, `oc-strike-squad-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-strike-squad`, `oc-strike-squad-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-strike-team`, `oc-strike-team-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-strike-team`, `oc-strike-team-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-strike-team`, `oc-strike-team-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-strike-team`, `oc-strike-team-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-striking-scorpions`, `oc-striking-scorpions-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-striking-scorpions`, `oc-striking-scorpions-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-subductor-squad`, `oc-subductor-squad-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-swooping-hawks`, `oc-swooping-hawks-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-sword-brethren-squad`, `oc-sword-brethren-squad-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tactical-squad`, `oc-tactical-squad-1-10` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tactical-squad`, `oc-tactical-squad-1-7` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tactical-squad`, `oc-tactical-squad-1-9` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tactical-squad`, `oc-tactical-squad-2-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tactical-squad`, `oc-tactical-squad-3-6` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tactical-squad-2`, `oc-tactical-squad-2-1-10` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tactical-squad-2`, `oc-tactical-squad-2-1-7` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tactical-squad-2`, `oc-tactical-squad-2-1-9` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tactical-squad-2`, `oc-tactical-squad-2-2-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tactical-squad-2`, `oc-tactical-squad-2-3-6` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tactical-squad-3`, `oc-tactical-squad-3-1-10` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tactical-squad-3`, `oc-tactical-squad-3-1-7` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tactical-squad-3`, `oc-tactical-squad-3-1-9` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tactical-squad-3`, `oc-tactical-squad-3-2-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tactical-squad-3`, `oc-tactical-squad-3-3-6` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tactical-squad-4`, `oc-tactical-squad-4-1-10` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tactical-squad-4`, `oc-tactical-squad-4-1-7` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tactical-squad-4`, `oc-tactical-squad-4-1-9` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tactical-squad-4`, `oc-tactical-squad-4-2-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tactical-squad-4`, `oc-tactical-squad-4-3-6` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-talonstrike-kill-team`, `oc-talonstrike-kill-team-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tankbustas`, `oc-tankbustas-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tankbustas`, `oc-tankbustas-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-taunar-supremacy-armour`, `oc-taunar-supremacy-armour-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-taunar-supremacy-armour`, `oc-taunar-supremacy-armour-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-taunar-supremacy-armour`, `oc-taunar-supremacy-armour-3-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tauros-assault-vehicle`, `oc-tauros-assault-vehicle-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tauros-assault-vehicle-2`, `oc-tauros-assault-vehicle-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-taurox-prime`, `oc-taurox-prime-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-taurox-prime-2`, `oc-taurox-prime-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tech-priest-dominus`, `oc-tech-priest-dominus-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tech-priest-dominus-2`, `oc-tech-priest-dominus-2-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-techmarine-on-bike`, `oc-techmarine-on-bike-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-telemon-heavy-dreadnought`, `oc-telemon-heavy-dreadnought-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-telemon-heavy-dreadnought`, `oc-telemon-heavy-dreadnought-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-telemon-heavy-dreadnought`, `oc-telemon-heavy-dreadnought-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-telemon-heavy-dreadnought`, `oc-telemon-heavy-dreadnought-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-telemon-heavy-dreadnought`, `oc-telemon-heavy-dreadnought-1-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tempestus-aquilons`, `oc-tempestus-aquilons-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tempestus-aquilons`, `oc-tempestus-aquilons-4-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tempestus-aquilons`, `oc-tempestus-aquilons-5-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tempestus-scions`, `oc-tempestus-scions-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tempestus-scions`, `oc-tempestus-scions-1-5` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tempestus-scions`, `oc-tempestus-scions-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tempestus-scions`, `oc-tempestus-scions-4-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-terminator-squad`, `oc-terminator-squad-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-terminator-squad-2`, `oc-terminator-squad-2-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-terminator-squad-3`, `oc-terminator-squad-3-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-terminator-squad-4`, `oc-terminator-squad-4-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-terminator-squad-5`, `oc-terminator-squad-5-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-terrax-pattern-termite`, `oc-terrax-pattern-termite-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-terrax-pattern-termite`, `oc-terrax-pattern-termite-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-terrax-pattern-termite-2`, `oc-terrax-pattern-termite-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-terrax-pattern-termite-2`, `oc-terrax-pattern-termite-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-terrax-pattern-termite-3`, `oc-terrax-pattern-termite-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-terrax-pattern-termite-3`, `oc-terrax-pattern-termite-3-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-terrax-pattern-termite-4`, `oc-terrax-pattern-termite-4-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-terrax-pattern-termite-4`, `oc-terrax-pattern-termite-4-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-terrax-pattern-termite-5`, `oc-terrax-pattern-termite-5-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-terrax-pattern-termite-5`, `oc-terrax-pattern-termite-5-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-terrax-pattern-termite-6`, `oc-terrax-pattern-termite-6-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-terrax-pattern-termite-6`, `oc-terrax-pattern-termite-6-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tesseract-ark`, `oc-tesseract-ark-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tesseract-ark`, `oc-tesseract-ark-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-thunderwolf-cavalry`, `oc-thunderwolf-cavalry-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-thunderwolf-cavalry`, `oc-thunderwolf-cavalry-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tidewall-shieldline`, `oc-tidewall-shieldline-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tiger-shark`, `oc-tiger-shark-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tiger-shark`, `oc-tiger-shark-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tiger-shark`, `oc-tiger-shark-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tiger-shark`, `oc-tiger-shark-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tiger-shark`, `oc-tiger-shark-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tomb-citadel-walls`, `oc-tomb-citadel-walls-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tomb-citadel-walls`, `oc-tomb-citadel-walls-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tomb-citadel-walls`, `oc-tomb-citadel-walls-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tormentors`, `oc-tormentors-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tormentors`, `oc-tormentors-4-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tormentors`, `oc-tormentors-5-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-traitor-guardsmen-squad`, `oc-traitor-guardsmen-squad-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-traitor-guardsmen-squad`, `oc-traitor-guardsmen-squad-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-traitor-guardsmen-squad-2`, `oc-traitor-guardsmen-squad-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-traitor-guardsmen-squad-2`, `oc-traitor-guardsmen-squad-2-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-traitor-guardsmen-squad-3`, `oc-traitor-guardsmen-squad-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-traitor-guardsmen-squad-3`, `oc-traitor-guardsmen-squad-3-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-triarch-praetorians`, `oc-triarch-praetorians-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tx42-piranha`, `oc-tx42-piranha-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tx42-piranha`, `oc-tx42-piranha-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tx42-piranha`, `oc-tx42-piranha-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-typhon`, `oc-typhon-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-typhon`, `oc-typhon-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-typhon-2`, `oc-typhon-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-typhon-2`, `oc-typhon-2-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-typhon-3`, `oc-typhon-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-typhon-3`, `oc-typhon-3-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-typhon-4`, `oc-typhon-4-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-typhon-4`, `oc-typhon-4-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-typhon-5`, `oc-typhon-5-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-typhon-5`, `oc-typhon-5-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tzaangor-enlightened`, `oc-tzaangor-enlightened-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tzaangors`, `oc-tzaangors-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tzaangors`, `oc-tzaangors-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-tzaangors`, `oc-tzaangors-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-valkyrie`, `oc-valkyrie-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-valkyrie`, `oc-valkyrie-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-valkyrie-sky-talon`, `oc-valkyrie-sky-talon-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-venatari-custodians`, `oc-venatari-custodians-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-vendetta-gunship`, `oc-vendetta-gunship-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-venerable-dreadnought`, `oc-venerable-dreadnought-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-venerable-dreadnought-2`, `oc-venerable-dreadnought-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-venerable-dreadnought-2`, `oc-venerable-dreadnought-2-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-venerable-dreadnought-2`, `oc-venerable-dreadnought-2-3-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-venerable-dreadnought-3`, `oc-venerable-dreadnought-3-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-venerable-dreadnought-3`, `oc-venerable-dreadnought-3-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-venerable-dreadnought-3`, `oc-venerable-dreadnought-3-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-veteran-bike-squad`, `oc-veteran-bike-squad-1-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-vigilant-squad`, `oc-vigilant-squad-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-vigilant-squad`, `oc-vigilant-squad-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-voidraven-bomber`, `oc-voidraven-bomber-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-voidraven-bomber`, `oc-voidraven-bomber-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-voidweaver`, `oc-voidweaver-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-voidweaver-2`, `oc-voidweaver-2-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-vulture-gunship`, `oc-vulture-gunship-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-vypers`, `oc-vypers-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-war-dog-moirax`, `oc-war-dog-moirax-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-war-dog-moirax`, `oc-war-dog-moirax-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-war-dog-stalker`, `oc-war-dog-stalker-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-warhound-titan`, `oc-warhound-titan-2-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-warlock`, `oc-warlock-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-warlock-conclave`, `oc-warlock-conclave-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-warlock-skyrunners`, `oc-warlock-skyrunners-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-warlord-titan`, `oc-warlord-titan-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-warlord-titan`, `oc-warlord-titan-2-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-warlord-titan`, `oc-warlord-titan-3-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-warp-spiders`, `oc-warp-spiders-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-warp-spiders`, `oc-warp-spiders-1-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-wasp-assault-walker`, `oc-wasp-assault-walker-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-wasp-assault-walker`, `oc-wasp-assault-walker-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-wave-serpent`, `oc-wave-serpent-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-wazbom-blastajet`, `oc-wazbom-blastajet-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-wolf-guard-battle-leader`, `oc-wolf-guard-battle-leader-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-wolf-guard-battle-leader-in-terminator-armour`, `oc-wolf-guard-battle-leader-in-terminator-armour-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-wolf-guard-battle-leader-on-thunderwolf`, `oc-wolf-guard-battle-leader-on-thunderwolf-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-wolf-guard-battle-leader-on-thunderwolf`, `oc-wolf-guard-battle-leader-on-thunderwolf-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-wolf-guard-battle-leader-on-thunderwolf`, `oc-wolf-guard-battle-leader-on-thunderwolf-3-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-wolf-guard-pack-leader`, `oc-wolf-guard-pack-leader-2-10` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-wolf-guard-pack-leader`, `oc-wolf-guard-pack-leader-2-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-wolf-guard-pack-leader-in-terminator-armour`, `oc-wolf-guard-pack-leader-in-terminator-armour-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-wolf-guard-pack-leader-in-terminator-armour`, `oc-wolf-guard-pack-leader-in-terminator-armour-2-8` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-wolf-guard-pack-leader-with-jump-pack`, `oc-wolf-guard-pack-leader-with-jump-pack-2-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-wolf-guard-pack-leader-with-jump-pack`, `oc-wolf-guard-pack-leader-with-jump-pack-2-9` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-wolf-guard-terminators`, `oc-wolf-guard-terminators-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-wolf-lord-on-thunderwolf`, `oc-wolf-lord-on-thunderwolf-1-3` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-wolf-lord-on-thunderwolf`, `oc-wolf-lord-on-thunderwolf-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-wolf-lord-on-thunderwolf`, `oc-wolf-lord-on-thunderwolf-2-4` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-wolf-scouts`, `oc-wolf-scouts-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-wolf-scouts`, `oc-wolf-scouts-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-wolf-scouts`, `oc-wolf-scouts-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-wracks`, `oc-wracks-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-wraithlord`, `oc-wraithlord-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-wraithlord`, `oc-wraithlord-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-wraithseer`, `oc-wraithseer-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-wulfen-dreadnought`, `oc-wulfen-dreadnought-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-ynnari-incubi`, `oc-ynnari-incubi-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-ynnari-kabalite-warriors`, `oc-ynnari-kabalite-warriors-2-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-ynnari-reavers`, `oc-ynnari-reavers-3-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-ynnari-reavers`, `oc-ynnari-reavers-3-2` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-yvahra-battlesuit`, `oc-yvahra-battlesuit-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-zephyrim-squad`, `oc-zephyrim-squad-1-1` | — |
| `OPT-LINK-AMBIGUOUS` | advisory | `ds-zephyrim-squad`, `oc-zephyrim-squad-2-1` | — |
| `OPT-PRICED-UNMATCHED` | advisory | `ds-outrider-squad`, `wo-outrider-squad-invader-atv` | — |
| `OPT-PRICED-UNMATCHED` | advisory | `ds-outrider-squad-2`, `wo-outrider-squad-2-invader-atv` | — |
| `OPT-PRICED-UNMATCHED` | advisory | `ds-outrider-squad-3`, `wo-outrider-squad-3-invader-atv` | — |
| `OPT-PRICED-UNMATCHED` | advisory | `ds-outrider-squad-4`, `wo-outrider-squad-4-invader-atv` | — |
| `OPT-PRICED-UNMATCHED` | advisory | `ds-outrider-squad-5`, `wo-outrider-squad-5-invader-atv` | — |
| `OPT-PRICED-UNMATCHED` | advisory | `ds-outrider-squad-6`, `wo-outrider-squad-6-invader-atv` | — |
| `PRC-UNVERIFIED` | advisory | `ds-accursed-cultists-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-accursed-cultists-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-aegis-defence-line-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-aetaosraukeres` | — |
| `PRC-UNVERIFIED` | advisory | `ds-amallyn-shadowguide` | — |
| `PRC-UNVERIFIED` | advisory | `ds-ancient-on-bike` | — |
| `PRC-UNVERIFIED` | advisory | `ds-anggrath-the-unbound` | — |
| `PRC-UNVERIFIED` | advisory | `ds-anrakyr-the-traveller` | — |
| `PRC-UNVERIFIED` | advisory | `ds-apothecary-on-bike` | — |
| `PRC-UNVERIFIED` | advisory | `ds-aquila-lander` | — |
| `PRC-UNVERIFIED` | advisory | `ds-arkurian-stormhammer` | — |
| `PRC-UNVERIFIED` | advisory | `ds-arkurian-stormhammer-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-armageddon-pattern-medusa` | — |
| `PRC-UNVERIFIED` | advisory | `ds-armageddon-pattern-medusa-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-armoured-sentinels-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-artillery-team-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-arvus-lighter` | — |
| `PRC-UNVERIFIED` | advisory | `ds-assault-squad` | — |
| `PRC-UNVERIFIED` | advisory | `ds-assault-squad-with-jump-packs` | — |
| `PRC-UNVERIFIED` | advisory | `ds-astartes-servitors` | — |
| `PRC-UNVERIFIED` | advisory | `ds-atlas-recovery-vehicle` | — |
| `PRC-UNVERIFIED` | advisory | `ds-atlas-recovery-vehicle-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-attack-bike-squad` | — |
| `PRC-UNVERIFIED` | advisory | `ds-attack-fighta` | — |
| `PRC-UNVERIFIED` | advisory | `ds-attilan-rough-riders-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-aunshi` | — |
| `PRC-UNVERIFIED` | advisory | `ds-aunva` | — |
| `PRC-UNVERIFIED` | advisory | `ds-autarch-skyrunner` | — |
| `PRC-UNVERIFIED` | advisory | `ds-baneblade-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-banehammer-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-banesword-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-barbed-hierodule` | — |
| `PRC-UNVERIFIED` | advisory | `ds-barracuda` | — |
| `PRC-UNVERIFIED` | advisory | `ds-basilisk-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-battle-sanctum` | — |
| `PRC-UNVERIFIED` | advisory | `ds-beastmaster` | — |
| `PRC-UNVERIFIED` | advisory | `ds-big-gunz` | — |
| `PRC-UNVERIFIED` | advisory | `ds-big-mek-on-warbike` | — |
| `PRC-UNVERIFIED` | advisory | `ds-big-mek-with-kustom-force-field` | — |
| `PRC-UNVERIFIED` | advisory | `ds-big-trakk` | — |
| `PRC-UNVERIFIED` | advisory | `ds-bike-squad` | — |
| `PRC-UNVERIFIED` | advisory | `ds-blood-slaughterer` | — |
| `PRC-UNVERIFIED` | advisory | `ds-blood-slaughterer-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-bonesinger` | — |
| `PRC-UNVERIFIED` | advisory | `ds-boss-zagstruk` | — |
| `PRC-UNVERIFIED` | advisory | `ds-brother-captain-stern` | — |
| `PRC-UNVERIFIED` | advisory | `ds-brother-corbulo` | — |
| `PRC-UNVERIFIED` | advisory | `ds-cadian-castellan-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-cadian-command-squad-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-cadian-heavy-weapons-squad-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-cadian-shock-troops-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-caestus-assault-ram` | — |
| `PRC-UNVERIFIED` | advisory | `ds-canis-wolfborn` | — |
| `PRC-UNVERIFIED` | advisory | `ds-canoptek-acanthrites` | — |
| `PRC-UNVERIFIED` | advisory | `ds-canoptek-tomb-sentinel` | — |
| `PRC-UNVERIFIED` | advisory | `ds-canoptek-tomb-stalker` | — |
| `PRC-UNVERIFIED` | advisory | `ds-captain-on-bike` | — |
| `PRC-UNVERIFIED` | advisory | `ds-captain-tycho` | — |
| `PRC-UNVERIFIED` | advisory | `ds-carab-culln-the-risen` | — |
| `PRC-UNVERIFIED` | advisory | `ds-carnodon` | — |
| `PRC-UNVERIFIED` | advisory | `ds-carnodon-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-catachan-command-squad-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-catachan-heavy-weapons-squad-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-catachan-jungle-fighters-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-celestian-sacresant-aveline` | — |
| `PRC-UNVERIFIED` | advisory | `ds-centaur-light-carrier` | — |
| `PRC-UNVERIFIED` | advisory | `ds-centaur-light-carrier-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-centaur-rsv-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-cerberus` | — |
| `PRC-UNVERIFIED` | advisory | `ds-cerberus-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-cerberus-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-cerberus-4` | — |
| `PRC-UNVERIFIED` | advisory | `ds-cerberus-5` | — |
| `PRC-UNVERIFIED` | advisory | `ds-chaos-deimos-predator` | — |
| `PRC-UNVERIFIED` | advisory | `ds-chaos-lord-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-chaos-lord-in-terminator-armour-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-chaos-lord-on-bike` | — |
| `PRC-UNVERIFIED` | advisory | `ds-chaos-lord-on-disc-of-tzeentch` | — |
| `PRC-UNVERIFIED` | advisory | `ds-chaos-lord-on-disc-of-tzeentch-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-chaos-lord-on-disc-of-tzeentch-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-chaos-lord-on-juggernaut` | — |
| `PRC-UNVERIFIED` | advisory | `ds-chaos-lord-on-juggernaut-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-chaos-lord-on-palanquin-of-nurgle` | — |
| `PRC-UNVERIFIED` | advisory | `ds-chaos-lord-on-palanquin-of-nurgle-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-chaos-lord-on-palanquin-of-nurgle-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-chaos-lord-on-steed-of-slaanesh` | — |
| `PRC-UNVERIFIED` | advisory | `ds-chaos-lord-on-steed-of-slaanesh-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-chaos-lord-with-jump-pack-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-chaos-terminator-squad-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-chaos-thunderhawk` | — |
| `PRC-UNVERIFIED` | advisory | `ds-chaos-thunderhawk-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-chaos-thunderhawk-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-chaos-thunderhawk-4` | — |
| `PRC-UNVERIFIED` | advisory | `ds-chaplain-cassius` | — |
| `PRC-UNVERIFIED` | advisory | `ds-chaplain-venerable-dreadnought` | — |
| `PRC-UNVERIFIED` | advisory | `ds-chimera-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-chinork-warkopta` | — |
| `PRC-UNVERIFIED` | advisory | `ds-chosen-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-cobra` | — |
| `PRC-UNVERIFIED` | advisory | `ds-colossus` | — |
| `PRC-UNVERIFIED` | advisory | `ds-colossus-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-command-squad` | — |
| `PRC-UNVERIFIED` | advisory | `ds-commander-in-crisis-battlesuit` | — |
| `PRC-UNVERIFIED` | advisory | `ds-company-champion-on-bike` | — |
| `PRC-UNVERIFIED` | advisory | `ds-company-veterans-on-bikes` | — |
| `PRC-UNVERIFIED` | advisory | `ds-corsair-cloud-dancer-band` | — |
| `PRC-UNVERIFIED` | advisory | `ds-corsair-cloud-dancer-band-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-corsair-reaver-band` | — |
| `PRC-UNVERIFIED` | advisory | `ds-corsair-reaver-band-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-corsair-skyreavers-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-corsair-voidreavers-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-corsair-voidscarred-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-court-of-the-archon` | — |
| `PRC-UNVERIFIED` | advisory | `ds-crassus` | — |
| `PRC-UNVERIFIED` | advisory | `ds-crassus-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-crisis-battlesuits` | — |
| `PRC-UNVERIFIED` | advisory | `ds-crusaders` | — |
| `PRC-UNVERIFIED` | advisory | `ds-cultist-firebrand-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-cultist-firebrand-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-cultist-mob-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-cultist-mob-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-cultist-mob-with-firearms` | — |
| `PRC-UNVERIFIED` | advisory | `ds-cultist-mob-with-firearms-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-cultist-mob-with-firearms-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-cyberwolf` | — |
| `PRC-UNVERIFIED` | advisory | `ds-cyclops-demolition-vehicle-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-da-red-gobbo` | — |
| `PRC-UNVERIFIED` | advisory | `ds-daemonhost` | — |
| `PRC-UNVERIFIED` | advisory | `ds-damned-legionnaires` | — |
| `PRC-UNVERIFIED` | advisory | `ds-dark-apostle-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-dark-commune-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-dark-commune-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-death-company-dreadnought-with-magna-grapple` | — |
| `PRC-UNVERIFIED` | advisory | `ds-death-company-marines-with-boltguns` | — |
| `PRC-UNVERIFIED` | advisory | `ds-death-company-marines-with-boltguns-and-jump-packs` | — |
| `PRC-UNVERIFIED` | advisory | `ds-death-cult-assassins` | — |
| `PRC-UNVERIFIED` | advisory | `ds-death-guard-chaos-lord` | — |
| `PRC-UNVERIFIED` | advisory | `ds-death-guard-chaos-lord-in-terminator-armour` | — |
| `PRC-UNVERIFIED` | advisory | `ds-death-guard-cultists` | — |
| `PRC-UNVERIFIED` | advisory | `ds-death-guard-possessed` | — |
| `PRC-UNVERIFIED` | advisory | `ds-death-guard-sorcerer-in-terminator-armour` | — |
| `PRC-UNVERIFIED` | advisory | `ds-death-jester-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-death-korps-grenadier-squad` | — |
| `PRC-UNVERIFIED` | advisory | `ds-death-korps-grenadier-squad-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-death-korps-of-krieg-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-death-rider-commissar` | — |
| `PRC-UNVERIFIED` | advisory | `ds-death-rider-commissar-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-death-riders-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-deathleaper-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-deathstorm-drop-pod` | — |
| `PRC-UNVERIFIED` | advisory | `ds-deathstrike-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-deathwatch-terminator-squad-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-deathwing-command-squad` | — |
| `PRC-UNVERIFIED` | advisory | `ds-deathwing-strikemaster` | — |
| `PRC-UNVERIFIED` | advisory | `ds-decimator` | — |
| `PRC-UNVERIFIED` | advisory | `ds-deff-rolla-battle-fortress` | — |
| `PRC-UNVERIFIED` | advisory | `ds-deffkoptas-with-big-shootas` | — |
| `PRC-UNVERIFIED` | advisory | `ds-deimos-predator` | — |
| `PRC-UNVERIFIED` | advisory | `ds-deredeo-dreadnought` | — |
| `PRC-UNVERIFIED` | advisory | `ds-deredeo-dreadnought-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-deredeo-dreadnought-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-deredeo-dreadnought-4` | — |
| `PRC-UNVERIFIED` | advisory | `ds-deredeo-dreadnought-5` | — |
| `PRC-UNVERIFIED` | advisory | `ds-dimachaeron` | — |
| `PRC-UNVERIFIED` | advisory | `ds-dominus-armoured-siege-bombard` | — |
| `PRC-UNVERIFIED` | advisory | `ds-dominus-armoured-siege-bombard-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-doomhammer-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-dreadclaw-drop-pod` | — |
| `PRC-UNVERIFIED` | advisory | `ds-dreadnought-drop-pod` | — |
| `PRC-UNVERIFIED` | advisory | `ds-drone-sentry-turret` | — |
| `PRC-UNVERIFIED` | advisory | `ds-earthshaker-carriage-battery` | — |
| `PRC-UNVERIFIED` | advisory | `ds-earthshaker-carriage-battery-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-earthshaker-platform` | — |
| `PRC-UNVERIFIED` | advisory | `ds-earthshaker-platform-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-elysian-drop-sentinel` | — |
| `PRC-UNVERIFIED` | advisory | `ds-elysian-drop-sentinel-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-elysian-sniper-squad` | — |
| `PRC-UNVERIFIED` | advisory | `ds-elysian-sniper-squad-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-exalted-champion` | — |
| `PRC-UNVERIFIED` | advisory | `ds-falchion` | — |
| `PRC-UNVERIFIED` | advisory | `ds-falchion-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-falchion-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-falchion-4` | — |
| `PRC-UNVERIFIED` | advisory | `ds-falchion-5` | — |
| `PRC-UNVERIFIED` | advisory | `ds-fellblade` | — |
| `PRC-UNVERIFIED` | advisory | `ds-fellblade-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-fellblade-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-fellblade-4` | — |
| `PRC-UNVERIFIED` | advisory | `ds-fellblade-5` | — |
| `PRC-UNVERIFIED` | advisory | `ds-fellgor-beastmen-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-fellgor-beastmen-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-ferren-areios` | — |
| `PRC-UNVERIFIED` | advisory | `ds-field-ordnance-battery-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-fighta-bommer` | — |
| `PRC-UNVERIFIED` | advisory | `ds-fire-raptor-gunship` | — |
| `PRC-UNVERIFIED` | advisory | `ds-fire-raptor-gunship-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-fire-raptor-gunship-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-fire-raptor-gunship-4` | — |
| `PRC-UNVERIFIED` | advisory | `ds-fire-raptor-gunship-5` | — |
| `PRC-UNVERIFIED` | advisory | `ds-firestorm` | — |
| `PRC-UNVERIFIED` | advisory | `ds-fortis-kill-team-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-furies` | — |
| `PRC-UNVERIFIED` | advisory | `ds-furioso-dreadnought` | — |
| `PRC-UNVERIFIED` | advisory | `ds-gabriel-seth` | — |
| `PRC-UNVERIFIED` | advisory | `ds-gargoyles-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-gauss-pylon` | — |
| `PRC-UNVERIFIED` | advisory | `ds-gellerpox-infected` | — |
| `PRC-UNVERIFIED` | advisory | `ds-gellerpox-infected-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-gellerpox-infected-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-gellerpox-infected-4` | — |
| `PRC-UNVERIFIED` | advisory | `ds-giant-chaos-spawn` | — |
| `PRC-UNVERIFIED` | advisory | `ds-gorgon-heavy-transport` | — |
| `PRC-UNVERIFIED` | advisory | `ds-gorgon-heavy-transport-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-great-knarloc` | — |
| `PRC-UNVERIFIED` | advisory | `ds-greater-blight-drone` | — |
| `PRC-UNVERIFIED` | advisory | `ds-greater-blight-drone-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-greater-brass-scorpion` | — |
| `PRC-UNVERIFIED` | advisory | `ds-greater-brass-scorpion-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-grey-knights-dreadnought` | — |
| `PRC-UNVERIFIED` | advisory | `ds-grey-knights-relic-razorback` | — |
| `PRC-UNVERIFIED` | advisory | `ds-griffon-mortar-carrier` | — |
| `PRC-UNVERIFIED` | advisory | `ds-griffon-mortar-carrier-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-grot-bomm-launcha` | — |
| `PRC-UNVERIFIED` | advisory | `ds-grot-mega-tank` | — |
| `PRC-UNVERIFIED` | advisory | `ds-grot-tanks` | — |
| `PRC-UNVERIFIED` | advisory | `ds-grotesques` | — |
| `PRC-UNVERIFIED` | advisory | `ds-hades-breaching-drill` | — |
| `PRC-UNVERIFIED` | advisory | `ds-hades-breaching-drill-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-harald-deathwolf` | — |
| `PRC-UNVERIFIED` | advisory | `ds-havocs-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-heavy-gun-drones` | — |
| `PRC-UNVERIFIED` | advisory | `ds-heavy-mortar-team` | — |
| `PRC-UNVERIFIED` | advisory | `ds-heavy-mortar-team-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-heavy-quad-launcher-team` | — |
| `PRC-UNVERIFIED` | advisory | `ds-heavy-quad-launcher-team-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-hell-blade` | — |
| `PRC-UNVERIFIED` | advisory | `ds-hell-blade-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-hell-blade-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-hell-blade-4` | — |
| `PRC-UNVERIFIED` | advisory | `ds-hell-talon` | — |
| `PRC-UNVERIFIED` | advisory | `ds-hell-talon-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-hell-talon-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-hell-talon-4` | — |
| `PRC-UNVERIFIED` | advisory | `ds-hellflayers-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-hellhammer-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-hellhound-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-hells-last` | — |
| `PRC-UNVERIFIED` | advisory | `ds-hells-last-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-herald-of-slaanesh-on-steed-of-slaanesh` | — |
| `PRC-UNVERIFIED` | advisory | `ds-hippogriff-afv-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-hornet` | — |
| `PRC-UNVERIFIED` | advisory | `ds-hounds-of-morkai` | — |
| `PRC-UNVERIFIED` | advisory | `ds-hunter` | — |
| `PRC-UNVERIFIED` | advisory | `ds-hydra-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-hydra-platform` | — |
| `PRC-UNVERIFIED` | advisory | `ds-hydra-platform-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-hyperadapted-raveners-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-illic-nightspear` | — |
| `PRC-UNVERIFIED` | advisory | `ds-imperial-space-marine` | — |
| `PRC-UNVERIFIED` | advisory | `ds-indomitor-kill-team-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-inquisitor-eisenhorn` | — |
| `PRC-UNVERIFIED` | advisory | `ds-inquisitor-in-terminator-armour` | — |
| `PRC-UNVERIFIED` | advisory | `ds-inquisitor-karamazov` | — |
| `PRC-UNVERIFIED` | advisory | `ds-inquisitor-ostromandeus` | — |
| `PRC-UNVERIFIED` | advisory | `ds-irillyth` | — |
| `PRC-UNVERIFIED` | advisory | `ds-iron-hand-straken` | — |
| `PRC-UNVERIFIED` | advisory | `ds-ironclad-dreadnought` | — |
| `PRC-UNVERIFIED` | advisory | `ds-janus-draik` | — |
| `PRC-UNVERIFIED` | advisory | `ds-javelin-attack-speeder` | — |
| `PRC-UNVERIFIED` | advisory | `ds-jokaero-weaponsmith` | — |
| `PRC-UNVERIFIED` | advisory | `ds-kaldor-draigo` | — |
| `PRC-UNVERIFIED` | advisory | `ds-kannonwagon` | — |
| `PRC-UNVERIFIED` | advisory | `ds-kaptin-badrukk` | — |
| `PRC-UNVERIFIED` | advisory | `ds-karandras` | — |
| `PRC-UNVERIFIED` | advisory | `ds-kasrkin-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-kharseth-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-kharybdis-assault-claw` | — |
| `PRC-UNVERIFIED` | advisory | `ds-khorne-berzerkers-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-kill-krusha` | — |
| `PRC-UNVERIFIED` | advisory | `ds-kill-tank` | — |
| `PRC-UNVERIFIED` | advisory | `ds-kill-team-cassius` | — |
| `PRC-UNVERIFIED` | advisory | `ds-kill-team-cassius-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-knarloc-riders` | — |
| `PRC-UNVERIFIED` | advisory | `ds-kratos` | — |
| `PRC-UNVERIFIED` | advisory | `ds-kratos-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-kratos-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-kratos-4` | — |
| `PRC-UNVERIFIED` | advisory | `ds-kratos-5` | — |
| `PRC-UNVERIFIED` | advisory | `ds-krieg-combat-engineers-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-krieg-command-squad-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-krieg-heavy-weapons-squad-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-krom-dragongaze` | — |
| `PRC-UNVERIFIED` | advisory | `ds-kytan-ravager` | — |
| `PRC-UNVERIFIED` | advisory | `ds-kytan-ravager-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-land-raider-achilles` | — |
| `PRC-UNVERIFIED` | advisory | `ds-land-raider-achilles-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-land-raider-achilles-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-land-raider-achilles-4` | — |
| `PRC-UNVERIFIED` | advisory | `ds-land-raider-achilles-5` | — |
| `PRC-UNVERIFIED` | advisory | `ds-land-raider-excelsior` | — |
| `PRC-UNVERIFIED` | advisory | `ds-land-raider-helios` | — |
| `PRC-UNVERIFIED` | advisory | `ds-land-raider-prometheus` | — |
| `PRC-UNVERIFIED` | advisory | `ds-land-raider-proteus` | — |
| `PRC-UNVERIFIED` | advisory | `ds-land-raider-proteus-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-land-raider-proteus-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-land-raider-proteus-4` | — |
| `PRC-UNVERIFIED` | advisory | `ds-land-raider-proteus-5` | — |
| `PRC-UNVERIFIED` | advisory | `ds-land-speeder-storm` | — |
| `PRC-UNVERIFIED` | advisory | `ds-land-speeder-tempest` | — |
| `PRC-UNVERIFIED` | advisory | `ds-land-speeder-tornado` | — |
| `PRC-UNVERIFIED` | advisory | `ds-land-speeder-typhoon` | — |
| `PRC-UNVERIFIED` | advisory | `ds-legionaries-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-leman-russ-battle-tank-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-leman-russ-commander-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-leman-russ-demolisher-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-leman-russ-eradicator-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-leman-russ-executioner-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-leman-russ-exterminator-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-leman-russ-punisher-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-leman-russ-vanquisher-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-leviathan-dreadnought` | — |
| `PRC-UNVERIFIED` | advisory | `ds-leviathan-dreadnought-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-leviathan-dreadnought-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-leviathan-dreadnought-4` | — |
| `PRC-UNVERIFIED` | advisory | `ds-leviathan-dreadnought-5` | — |
| `PRC-UNVERIFIED` | advisory | `ds-librarian-dreadnought` | — |
| `PRC-UNVERIFIED` | advisory | `ds-librarian-on-bike` | — |
| `PRC-UNVERIFIED` | advisory | `ds-librarian-with-jump-pack` | — |
| `PRC-UNVERIFIED` | advisory | `ds-lictor-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-lifta-wagon` | — |
| `PRC-UNVERIFIED` | advisory | `ds-logan-grimnar-on-stormrider` | — |
| `PRC-UNVERIFIED` | advisory | `ds-long-fangs` | — |
| `PRC-UNVERIFIED` | advisory | `ds-longstrike` | — |
| `PRC-UNVERIFIED` | advisory | `ds-lord` | — |
| `PRC-UNVERIFIED` | advisory | `ds-lukas-the-trickster` | — |
| `PRC-UNVERIFIED` | advisory | `ds-lynx` | — |
| `PRC-UNVERIFIED` | advisory | `ds-macharius` | — |
| `PRC-UNVERIFIED` | advisory | `ds-macharius-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-macharius-omega` | — |
| `PRC-UNVERIFIED` | advisory | `ds-macharius-omega-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-macharius-vanquisher` | — |
| `PRC-UNVERIFIED` | advisory | `ds-macharius-vanquisher-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-macharius-vulcan` | — |
| `PRC-UNVERIFIED` | advisory | `ds-macharius-vulcan-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-mad-dok-grotsnik` | — |
| `PRC-UNVERIFIED` | advisory | `ds-malanthrope` | — |
| `PRC-UNVERIFIED` | advisory | `ds-malcador` | — |
| `PRC-UNVERIFIED` | advisory | `ds-malcador-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-malcador-annihilator` | — |
| `PRC-UNVERIFIED` | advisory | `ds-malcador-annihilator-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-malcador-defender` | — |
| `PRC-UNVERIFIED` | advisory | `ds-malcador-defender-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-malcador-infernus` | — |
| `PRC-UNVERIFIED` | advisory | `ds-malcador-infernus-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-manticore-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-manticore-platform` | — |
| `PRC-UNVERIFIED` | advisory | `ds-manticore-platform-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-marauder-bomber` | — |
| `PRC-UNVERIFIED` | advisory | `ds-marauder-destroyer` | — |
| `PRC-UNVERIFIED` | advisory | `ds-master-of-possession-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-mastodon` | — |
| `PRC-UNVERIFIED` | advisory | `ds-mastodon-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-mastodon-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-mastodon-4` | — |
| `PRC-UNVERIFIED` | advisory | `ds-mastodon-5` | — |
| `PRC-UNVERIFIED` | advisory | `ds-mawloc-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-medusa-carriage-battery` | — |
| `PRC-UNVERIFIED` | advisory | `ds-medusa-carriage-battery-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-mega-dread` | — |
| `PRC-UNVERIFIED` | advisory | `ds-meka-dread` | — |
| `PRC-UNVERIFIED` | advisory | `ds-mekboy-workshop` | — |
| `PRC-UNVERIFIED` | advisory | `ds-minotaur` | — |
| `PRC-UNVERIFIED` | advisory | `ds-minotaur-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-mortis-dreadnought` | — |
| `PRC-UNVERIFIED` | advisory | `ds-mukaali-riders` | — |
| `PRC-UNVERIFIED` | advisory | `ds-mukaali-riders-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-munitorum-servitors` | — |
| `PRC-UNVERIFIED` | advisory | `ds-munitorum-servitors-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-mutoid-vermin` | — |
| `PRC-UNVERIFIED` | advisory | `ds-mutoid-vermin-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-mutoid-vermin-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-mutoid-vermin-4` | — |
| `PRC-UNVERIFIED` | advisory | `ds-myphitic-blight-hauler` | — |
| `PRC-UNVERIFIED` | advisory | `ds-negavolt-cultists` | — |
| `PRC-UNVERIFIED` | advisory | `ds-negavolt-cultists-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-negavolt-cultists-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-nemesor-zahndrekh` | — |
| `PRC-UNVERIFIED` | advisory | `ds-neurolictor-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-neyam-shai-murad` | — |
| `PRC-UNVERIFIED` | advisory | `ds-night-shroud` | — |
| `PRC-UNVERIFIED` | advisory | `ds-nightwing` | — |
| `PRC-UNVERIFIED` | advisory | `ds-nobz-on-warbikes` | — |
| `PRC-UNVERIFIED` | advisory | `ds-noise-marines-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-orca-dropship` | — |
| `PRC-UNVERIFIED` | advisory | `ds-painboy-on-warbike` | — |
| `PRC-UNVERIFIED` | advisory | `ds-parasite-of-mortrex-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-phoenix` | — |
| `PRC-UNVERIFIED` | advisory | `ds-plague-marines-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-plague-toads` | — |
| `PRC-UNVERIFIED` | advisory | `ds-possessed-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-pox-riders` | — |
| `PRC-UNVERIFIED` | advisory | `ds-praetor` | — |
| `PRC-UNVERIFIED` | advisory | `ds-praetor-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-primaris-company-champion` | — |
| `PRC-UNVERIFIED` | advisory | `ds-primaris-psyker-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-prince-yriel-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-proteus-kill-team` | — |
| `PRC-UNVERIFIED` | advisory | `ds-provisionally-prepared` | — |
| `PRC-UNVERIFIED` | advisory | `ds-quartermaster-cadre-squad` | — |
| `PRC-UNVERIFIED` | advisory | `ds-quartermaster-cadre-squad-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-rapier-carrier` | — |
| `PRC-UNVERIFIED` | advisory | `ds-rapier-carrier-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-rapier-carrier-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-rapier-carrier-4` | — |
| `PRC-UNVERIFIED` | advisory | `ds-rapier-carrier-5` | — |
| `PRC-UNVERIFIED` | advisory | `ds-rapier-laser-destroyer-battery` | — |
| `PRC-UNVERIFIED` | advisory | `ds-rapier-laser-destroyer-battery-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-raptors-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-raven-strike-fighter` | — |
| `PRC-UNVERIFIED` | advisory | `ds-raveners-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-ravenwing-talonmaster` | — |
| `PRC-UNVERIFIED` | advisory | `ds-reaper` | — |
| `PRC-UNVERIFIED` | advisory | `ds-regimental-attaches` | — |
| `PRC-UNVERIFIED` | advisory | `ds-regimental-attaches-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-rein-and-raus` | — |
| `PRC-UNVERIFIED` | advisory | `ds-relic-contemptor-dreadnought` | — |
| `PRC-UNVERIFIED` | advisory | `ds-relic-contemptor-dreadnought-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-relic-contemptor-dreadnought-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-relic-contemptor-dreadnought-4` | — |
| `PRC-UNVERIFIED` | advisory | `ds-relic-contemptor-dreadnought-5` | — |
| `PRC-UNVERIFIED` | advisory | `ds-relic-razorback` | — |
| `PRC-UNVERIFIED` | advisory | `ds-relic-terminator-squad` | — |
| `PRC-UNVERIFIED` | advisory | `ds-remora-stealth-drones` | — |
| `PRC-UNVERIFIED` | advisory | `ds-remote-sensor-tower` | — |
| `PRC-UNVERIFIED` | advisory | `ds-renegade-enforcer` | — |
| `PRC-UNVERIFIED` | advisory | `ds-renegade-enforcer-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-renegade-enforcer-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-renegade-heavy-weapons-squad` | — |
| `PRC-UNVERIFIED` | advisory | `ds-renegade-heavy-weapons-squad-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-renegade-heavy-weapons-squad-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-renegade-ogryn-beast-handler` | — |
| `PRC-UNVERIFIED` | advisory | `ds-renegade-ogryn-beast-handler-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-renegade-ogryn-beast-handler-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-renegade-ogryn-brutes` | — |
| `PRC-UNVERIFIED` | advisory | `ds-renegade-ogryn-brutes-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-renegade-ogryn-brutes-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-renegade-plague-ogryns` | — |
| `PRC-UNVERIFIED` | advisory | `ds-renegade-plague-ogryns-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-renegade-plague-ogryns-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-repressor` | — |
| `PRC-UNVERIFIED` | advisory | `ds-rhino-primaris` | — |
| `PRC-UNVERIFIED` | advisory | `ds-rogal-dorn-battle-tank-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-rogal-dorn-commander-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-rogue-psyker` | — |
| `PRC-UNVERIFIED` | advisory | `ds-rogue-psyker-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-rogue-psyker-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-rubric-marines-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-rvarna-battlesuit` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sabre-weapons-battery` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sabre-weapons-battery-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-salamander-command-vehicle` | — |
| `PRC-UNVERIFIED` | advisory | `ds-salamander-command-vehicle-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-salamander-scout-vehicle` | — |
| `PRC-UNVERIFIED` | advisory | `ds-salamander-scout-vehicle-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sanguinary-priest-with-jump-pack` | — |
| `PRC-UNVERIFIED` | advisory | `ds-scabeiathrax-the-bloated` | — |
| `PRC-UNVERIFIED` | advisory | `ds-scorpion` | — |
| `PRC-UNVERIFIED` | advisory | `ds-scout-bike-squad` | — |
| `PRC-UNVERIFIED` | advisory | `ds-scout-sentinels-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-scout-sniper-squad` | — |
| `PRC-UNVERIFIED` | advisory | `ds-scythed-hierodule` | — |
| `PRC-UNVERIFIED` | advisory | `ds-secutarii-hoplites` | — |
| `PRC-UNVERIFIED` | advisory | `ds-secutarii-peltasts` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sentinel-powerlifter` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sentinel-powerlifter-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sentry-pylon` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sergeant-chronus` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sergeant-harker` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sergeant-telion` | — |
| `PRC-UNVERIFIED` | advisory | `ds-servitors` | — |
| `PRC-UNVERIFIED` | advisory | `ds-shadow-spectres` | — |
| `PRC-UNVERIFIED` | advisory | `ds-shadowseer-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-shadowsword-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-shaso-ralai` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sicaran-arcus` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sicaran-battle-tank` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sicaran-battle-tank-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sicaran-battle-tank-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sicaran-battle-tank-4` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sicaran-battle-tank-5` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sicaran-omega` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sicaran-punisher` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sicaran-punisher-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sicaran-punisher-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sicaran-punisher-4` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sicaran-punisher-5` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sicaran-venator` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sicaran-venator-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sicaran-venator-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sicaran-venator-4` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sicaran-venator-5` | — |
| `PRC-UNVERIFIED` | advisory | `ds-skathach-wraithknight` | — |
| `PRC-UNVERIFIED` | advisory | `ds-skitarii-marshal-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-skitarii-rangers-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-skitarii-vanguard-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-skorchas` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sky-slasher-swarms` | — |
| `PRC-UNVERIFIED` | advisory | `ds-skyclaws` | — |
| `PRC-UNVERIFIED` | advisory | `ds-skyweavers-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sokar-pattern-stormbird` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sokar-pattern-stormbird-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sokar-pattern-stormbird-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sokar-pattern-stormbird-4` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sokar-pattern-stormbird-5` | — |
| `PRC-UNVERIFIED` | advisory | `ds-solitaire-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sorcerer-4` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sorcerer-in-terminator-armour-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sorcerer-on-bike` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sorcerer-on-disc-of-tzeentch` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sorcerer-on-disc-of-tzeentch-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sorcerer-on-palanquin-of-nurgle` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sorcerer-on-palanquin-of-nurgle-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sorcerer-on-palanquin-of-nurgle-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sorcerer-on-steed-of-slaanesh` | — |
| `PRC-UNVERIFIED` | advisory | `ds-sorcerer-on-steed-of-slaanesh-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-spartan` | — |
| `PRC-UNVERIFIED` | advisory | `ds-spartan-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-spartan-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-spartan-4` | — |
| `PRC-UNVERIFIED` | advisory | `ds-spartan-5` | — |
| `PRC-UNVERIFIED` | advisory | `ds-spectrus-kill-team-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-spined-chaos-beast` | — |
| `PRC-UNVERIFIED` | advisory | `ds-squiggoth` | — |
| `PRC-UNVERIFIED` | advisory | `ds-stalker` | — |
| `PRC-UNVERIFIED` | advisory | `ds-starfangs-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-starweaver-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-storm-chimera` | — |
| `PRC-UNVERIFIED` | advisory | `ds-storm-chimera-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-storm-eagle-gunship` | — |
| `PRC-UNVERIFIED` | advisory | `ds-storm-eagle-gunship-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-storm-eagle-gunship-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-storm-eagle-gunship-4` | — |
| `PRC-UNVERIFIED` | advisory | `ds-storm-eagle-gunship-5` | — |
| `PRC-UNVERIFIED` | advisory | `ds-stormblade` | — |
| `PRC-UNVERIFIED` | advisory | `ds-stormblade-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-stormfang-gunship` | — |
| `PRC-UNVERIFIED` | advisory | `ds-stormlord-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-stormsword-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-stormwolf` | — |
| `PRC-UNVERIFIED` | advisory | `ds-stygies-destroyer-tank-hunter` | — |
| `PRC-UNVERIFIED` | advisory | `ds-stygies-destroyer-tank-hunter-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-tantalus` | — |
| `PRC-UNVERIFIED` | advisory | `ds-tarantula-air-defence-battery` | — |
| `PRC-UNVERIFIED` | advisory | `ds-tarantula-battery` | — |
| `PRC-UNVERIFIED` | advisory | `ds-tarantula-battery-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-tarantula-sentry-battery` | — |
| `PRC-UNVERIFIED` | advisory | `ds-tauros-assault-vehicle` | — |
| `PRC-UNVERIFIED` | advisory | `ds-tauros-assault-vehicle-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-tauros-venator` | — |
| `PRC-UNVERIFIED` | advisory | `ds-tauros-venator-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-taurox-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-taurox-prime-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-tech-priest-dominus-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-tech-priest-manipulus-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-techmarine-on-bike` | — |
| `PRC-UNVERIFIED` | advisory | `ds-tectonic-fragdrill` | — |
| `PRC-UNVERIFIED` | advisory | `ds-terminus-ultra` | — |
| `PRC-UNVERIFIED` | advisory | `ds-terrax-pattern-termite` | — |
| `PRC-UNVERIFIED` | advisory | `ds-terrax-pattern-termite-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-terrax-pattern-termite-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-terrax-pattern-termite-4` | — |
| `PRC-UNVERIFIED` | advisory | `ds-terrax-pattern-termite-5` | — |
| `PRC-UNVERIFIED` | advisory | `ds-terrax-pattern-termite-6` | — |
| `PRC-UNVERIFIED` | advisory | `ds-tesseract-ark` | — |
| `PRC-UNVERIFIED` | advisory | `ds-tetras` | — |
| `PRC-UNVERIFIED` | advisory | `ds-the-red-terror-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-thunderfire-cannon` | — |
| `PRC-UNVERIFIED` | advisory | `ds-thunderhawk-transporter` | — |
| `PRC-UNVERIFIED` | advisory | `ds-tomb-citadel-walls` | — |
| `PRC-UNVERIFIED` | advisory | `ds-traitor-enforcer-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-traitor-enforcer-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-traitor-guardsmen-squad-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-traitor-guardsmen-squad-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-trojan-support-vehicle` | — |
| `PRC-UNVERIFIED` | advisory | `ds-trojan-support-vehicle-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-troupe-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-troupe-master-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-trygon-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-tx42-piranha` | — |
| `PRC-UNVERIFIED` | advisory | `ds-tycho-the-lost` | — |
| `PRC-UNVERIFIED` | advisory | `ds-typhon` | — |
| `PRC-UNVERIFIED` | advisory | `ds-typhon-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-typhon-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-typhon-4` | — |
| `PRC-UNVERIFIED` | advisory | `ds-typhon-5` | — |
| `PRC-UNVERIFIED` | advisory | `ds-tyrannic-war-veterans` | — |
| `PRC-UNVERIFIED` | advisory | `ds-tyrannocyte-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-ufthak-blackhawk` | — |
| `PRC-UNVERIFIED` | advisory | `ds-ur-025` | — |
| `PRC-UNVERIFIED` | advisory | `ds-urien-rakarth` | — |
| `PRC-UNVERIFIED` | advisory | `ds-valdor` | — |
| `PRC-UNVERIFIED` | advisory | `ds-valdor-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-valkyrie-sky-talon` | — |
| `PRC-UNVERIFIED` | advisory | `ds-vampire-hunter` | — |
| `PRC-UNVERIFIED` | advisory | `ds-vampire-raider` | — |
| `PRC-UNVERIFIED` | advisory | `ds-vanguard-veteran-squad` | — |
| `PRC-UNVERIFIED` | advisory | `ds-vargard-obyron` | — |
| `PRC-UNVERIFIED` | advisory | `ds-vendetta-gunship` | — |
| `PRC-UNVERIFIED` | advisory | `ds-venerable-dreadnought-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-veteran-bike-squad` | — |
| `PRC-UNVERIFIED` | advisory | `ds-vindicator-laser-destroyer` | — |
| `PRC-UNVERIFIED` | advisory | `ds-voidweaver-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-von-ryans-leapers-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-voss-pattern-lightning` | — |
| `PRC-UNVERIFIED` | advisory | `ds-vulture-gunship` | — |
| `PRC-UNVERIFIED` | advisory | `ds-vypers` | — |
| `PRC-UNVERIFIED` | advisory | `ds-warboss-on-warbike` | — |
| `PRC-UNVERIFIED` | advisory | `ds-warbuggies` | — |
| `PRC-UNVERIFIED` | advisory | `ds-warp-hunter` | — |
| `PRC-UNVERIFIED` | advisory | `ds-warp-talons-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-wasp-assault-walker` | — |
| `PRC-UNVERIFIED` | advisory | `ds-webway-gate` | — |
| `PRC-UNVERIFIED` | advisory | `ds-whirlwind-scorpius` | — |
| `PRC-UNVERIFIED` | advisory | `ds-whirlwind-scorpius-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-whirlwind-scorpius-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-whirlwind-scorpius-4` | — |
| `PRC-UNVERIFIED` | advisory | `ds-whirlwind-scorpius-5` | — |
| `PRC-UNVERIFIED` | advisory | `ds-winged-hive-tyrant-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-winged-tyranid-prime-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-wolf-guard` | — |
| `PRC-UNVERIFIED` | advisory | `ds-wolf-guard-battle-leader-in-terminator-armour` | — |
| `PRC-UNVERIFIED` | advisory | `ds-wolf-guard-battle-leader-on-thunderwolf` | — |
| `PRC-UNVERIFIED` | advisory | `ds-wolf-guard-pack-leader` | — |
| `PRC-UNVERIFIED` | advisory | `ds-wolf-guard-pack-leader-in-terminator-armour` | — |
| `PRC-UNVERIFIED` | advisory | `ds-wolf-guard-pack-leader-with-jump-pack` | — |
| `PRC-UNVERIFIED` | advisory | `ds-wolf-lord-on-thunderwolf` | — |
| `PRC-UNVERIFIED` | advisory | `ds-wraithseer` | — |
| `PRC-UNVERIFIED` | advisory | `ds-wyvern-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-x-101` | — |
| `PRC-UNVERIFIED` | advisory | `ds-xiphon-interceptor` | — |
| `PRC-UNVERIFIED` | advisory | `ds-xiphon-interceptor-2` | — |
| `PRC-UNVERIFIED` | advisory | `ds-xiphon-interceptor-3` | — |
| `PRC-UNVERIFIED` | advisory | `ds-xiphon-interceptor-4` | — |
| `PRC-UNVERIFIED` | advisory | `ds-xiphon-interceptor-5` | — |
| `PRC-UNVERIFIED` | advisory | `ds-xv9-hazard-battlesuits` | — |
| `PRC-UNVERIFIED` | advisory | `ds-yvahra-battlesuit` | — |
| `PRC-UNVERIFIED` | advisory | `ds-zarakynel` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-accursed-cultists-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-accursed-cultists-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-aegis-defence-line-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-aetaosraukeres` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-amallyn-shadowguide` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-ancient-on-bike` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-anggrath-the-unbound` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-anrakyr-the-traveller` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-apothecary-on-bike` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-aquila-lander` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-arkurian-stormhammer` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-arkurian-stormhammer-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-armageddon-pattern-medusa` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-armageddon-pattern-medusa-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-armoured-sentinels-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-artillery-team-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-arvus-lighter` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-assault-squad` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-assault-squad-with-jump-packs` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-astartes-servitors` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-atlas-recovery-vehicle` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-atlas-recovery-vehicle-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-attack-bike-squad` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-attack-fighta` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-attilan-rough-riders-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-aunshi` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-aunva` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-autarch-skyrunner` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-baneblade-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-banehammer-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-banesword-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-barbed-hierodule` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-barracuda` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-basilisk-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-battle-sanctum` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-beastmaster` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-big-gunz` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-big-mek-on-warbike` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-big-mek-with-kustom-force-field` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-big-trakk` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-bike-squad` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-blood-slaughterer` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-blood-slaughterer-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-bonesinger` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-boss-zagstruk` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-brother-captain-stern` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-brother-corbulo` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-cadian-castellan-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-cadian-command-squad-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-cadian-heavy-weapons-squad-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-cadian-shock-troops-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-caestus-assault-ram` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-canis-wolfborn` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-canoptek-acanthrites` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-canoptek-tomb-sentinel` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-canoptek-tomb-stalker` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-captain-on-bike` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-captain-tycho` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-carab-culln-the-risen` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-carnodon` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-carnodon-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-catachan-command-squad-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-catachan-heavy-weapons-squad-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-catachan-jungle-fighters-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-celestian-sacresant-aveline` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-centaur-light-carrier` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-centaur-light-carrier-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-centaur-rsv-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-cerberus` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-cerberus-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-cerberus-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-cerberus-4` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-cerberus-5` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-chaos-deimos-predator` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-chaos-lord-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-chaos-lord-in-terminator-armour-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-chaos-lord-on-bike` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-chaos-lord-on-disc-of-tzeentch` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-chaos-lord-on-disc-of-tzeentch-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-chaos-lord-on-disc-of-tzeentch-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-chaos-lord-on-juggernaut` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-chaos-lord-on-juggernaut-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-chaos-lord-on-palanquin-of-nurgle` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-chaos-lord-on-palanquin-of-nurgle-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-chaos-lord-on-palanquin-of-nurgle-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-chaos-lord-on-steed-of-slaanesh` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-chaos-lord-on-steed-of-slaanesh-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-chaos-lord-with-jump-pack-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-chaos-terminator-squad-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-chaos-thunderhawk` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-chaos-thunderhawk-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-chaos-thunderhawk-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-chaos-thunderhawk-4` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-chaplain-cassius` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-chaplain-venerable-dreadnought` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-chimera-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-chinork-warkopta` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-chosen-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-cobra` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-colossus` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-colossus-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-command-squad` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-commander-in-crisis-battlesuit` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-company-champion-on-bike` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-company-veterans-on-bikes` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-corsair-cloud-dancer-band` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-corsair-cloud-dancer-band-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-corsair-reaver-band` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-corsair-reaver-band-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-corsair-skyreavers-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-corsair-voidreavers-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-corsair-voidscarred-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-court-of-the-archon` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-crassus` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-crassus-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-crisis-battlesuits` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-crusaders` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-cultist-firebrand-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-cultist-firebrand-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-cultist-mob-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-cultist-mob-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-cultist-mob-with-firearms` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-cultist-mob-with-firearms-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-cultist-mob-with-firearms-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-cyberwolf` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-cyclops-demolition-vehicle-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-da-red-gobbo` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-daemonhost` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-damned-legionnaires` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-dark-apostle-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-dark-commune-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-dark-commune-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-death-company-dreadnought-with-magna-grapple` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-death-company-marines-with-boltguns` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-death-company-marines-with-boltguns-and-jump-packs` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-death-cult-assassins` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-death-guard-chaos-lord` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-death-guard-chaos-lord-in-terminator-armour` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-death-guard-cultists` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-death-guard-possessed` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-death-guard-sorcerer-in-terminator-armour` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-death-jester-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-death-korps-grenadier-squad` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-death-korps-grenadier-squad-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-death-korps-of-krieg-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-death-rider-commissar` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-death-rider-commissar-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-death-riders-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-deathleaper-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-deathstorm-drop-pod` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-deathstrike-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-deathwatch-terminator-squad-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-deathwing-command-squad` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-deathwing-strikemaster` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-decimator` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-deff-rolla-battle-fortress` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-deffkoptas-with-big-shootas` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-deimos-predator` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-deredeo-dreadnought` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-deredeo-dreadnought-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-deredeo-dreadnought-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-deredeo-dreadnought-4` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-deredeo-dreadnought-5` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-dimachaeron` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-dominus-armoured-siege-bombard` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-dominus-armoured-siege-bombard-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-doomhammer-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-dreadclaw-drop-pod` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-dreadnought-drop-pod` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-drone-sentry-turret` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-earthshaker-carriage-battery` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-earthshaker-carriage-battery-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-earthshaker-platform` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-earthshaker-platform-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-elysian-drop-sentinel` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-elysian-drop-sentinel-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-elysian-sniper-squad` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-elysian-sniper-squad-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-exalted-champion` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-falchion` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-falchion-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-falchion-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-falchion-4` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-falchion-5` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-fellblade` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-fellblade-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-fellblade-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-fellblade-4` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-fellblade-5` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-fellgor-beastmen-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-fellgor-beastmen-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-ferren-areios` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-field-ordnance-battery-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-fighta-bommer` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-fire-raptor-gunship` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-fire-raptor-gunship-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-fire-raptor-gunship-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-fire-raptor-gunship-4` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-fire-raptor-gunship-5` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-firestorm` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-fortis-kill-team-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-furies` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-furioso-dreadnought` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-gabriel-seth` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-gargoyles-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-gauss-pylon` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-gellerpox-infected` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-gellerpox-infected-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-gellerpox-infected-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-gellerpox-infected-4` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-giant-chaos-spawn` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-gorgon-heavy-transport` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-gorgon-heavy-transport-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-great-knarloc` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-greater-blight-drone` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-greater-blight-drone-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-greater-brass-scorpion` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-greater-brass-scorpion-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-grey-knights-dreadnought` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-grey-knights-relic-razorback` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-griffon-mortar-carrier` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-griffon-mortar-carrier-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-grot-bomm-launcha` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-grot-mega-tank` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-grot-tanks` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-grotesques` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-hades-breaching-drill` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-hades-breaching-drill-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-harald-deathwolf` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-havocs-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-heavy-gun-drones` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-heavy-mortar-team` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-heavy-mortar-team-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-heavy-quad-launcher-team` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-heavy-quad-launcher-team-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-hell-blade` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-hell-blade-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-hell-blade-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-hell-blade-4` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-hell-talon` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-hell-talon-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-hell-talon-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-hell-talon-4` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-hellflayers-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-hellhammer-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-hellhound-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-hells-last` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-hells-last-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-herald-of-slaanesh-on-steed-of-slaanesh` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-hippogriff-afv-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-hornet` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-hounds-of-morkai` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-hunter` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-hydra-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-hydra-platform` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-hydra-platform-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-hyperadapted-raveners-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-illic-nightspear` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-imperial-space-marine` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-indomitor-kill-team-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-inquisitor-eisenhorn` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-inquisitor-in-terminator-armour` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-inquisitor-karamazov` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-inquisitor-ostromandeus` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-irillyth` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-iron-hand-straken` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-ironclad-dreadnought` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-janus-draik` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-javelin-attack-speeder` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-jokaero-weaponsmith` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-kaldor-draigo` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-kannonwagon` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-kaptin-badrukk` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-karandras` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-kasrkin-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-kharseth-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-kharybdis-assault-claw` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-khorne-berzerkers-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-kill-krusha` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-kill-tank` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-kill-team-cassius` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-kill-team-cassius-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-knarloc-riders` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-kratos` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-kratos-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-kratos-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-kratos-4` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-kratos-5` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-krieg-combat-engineers-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-krieg-command-squad-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-krieg-heavy-weapons-squad-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-krom-dragongaze` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-kytan-ravager` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-kytan-ravager-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-land-raider-achilles` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-land-raider-achilles-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-land-raider-achilles-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-land-raider-achilles-4` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-land-raider-achilles-5` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-land-raider-excelsior` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-land-raider-helios` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-land-raider-prometheus` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-land-raider-proteus` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-land-raider-proteus-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-land-raider-proteus-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-land-raider-proteus-4` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-land-raider-proteus-5` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-land-speeder-storm` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-land-speeder-tempest` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-land-speeder-tornado` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-land-speeder-typhoon` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-legionaries-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-leman-russ-battle-tank-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-leman-russ-commander-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-leman-russ-demolisher-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-leman-russ-eradicator-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-leman-russ-executioner-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-leman-russ-exterminator-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-leman-russ-punisher-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-leman-russ-vanquisher-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-leviathan-dreadnought` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-leviathan-dreadnought-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-leviathan-dreadnought-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-leviathan-dreadnought-4` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-leviathan-dreadnought-5` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-librarian-dreadnought` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-librarian-on-bike` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-librarian-with-jump-pack` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-lictor-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-lifta-wagon` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-logan-grimnar-on-stormrider` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-long-fangs` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-longstrike` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-lord` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-lukas-the-trickster` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-lynx` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-macharius` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-macharius-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-macharius-omega` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-macharius-omega-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-macharius-vanquisher` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-macharius-vanquisher-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-macharius-vulcan` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-macharius-vulcan-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-mad-dok-grotsnik` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-malanthrope` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-malcador` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-malcador-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-malcador-annihilator` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-malcador-annihilator-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-malcador-defender` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-malcador-defender-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-malcador-infernus` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-malcador-infernus-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-manticore-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-manticore-platform` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-manticore-platform-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-marauder-bomber` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-marauder-destroyer` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-master-of-possession-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-mastodon` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-mastodon-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-mastodon-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-mastodon-4` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-mastodon-5` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-mawloc-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-medusa-carriage-battery` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-medusa-carriage-battery-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-mega-dread` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-meka-dread` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-mekboy-workshop` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-minotaur` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-minotaur-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-mortis-dreadnought` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-mukaali-riders` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-mukaali-riders-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-munitorum-servitors` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-munitorum-servitors-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-mutoid-vermin` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-mutoid-vermin-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-mutoid-vermin-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-mutoid-vermin-4` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-myphitic-blight-hauler` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-negavolt-cultists` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-negavolt-cultists-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-negavolt-cultists-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-nemesor-zahndrekh` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-neurolictor-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-neyam-shai-murad` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-night-shroud` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-nightwing` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-nobz-on-warbikes` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-noise-marines-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-orca-dropship` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-painboy-on-warbike` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-parasite-of-mortrex-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-phoenix` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-plague-marines-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-plague-toads` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-possessed-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-pox-riders` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-praetor` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-praetor-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-primaris-company-champion` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-primaris-psyker-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-prince-yriel-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-proteus-kill-team` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-provisionally-prepared` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-quartermaster-cadre-squad` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-quartermaster-cadre-squad-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-rapier-carrier` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-rapier-carrier-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-rapier-carrier-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-rapier-carrier-4` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-rapier-carrier-5` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-rapier-laser-destroyer-battery` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-rapier-laser-destroyer-battery-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-raptors-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-raven-strike-fighter` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-raveners-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-ravenwing-talonmaster` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-reaper` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-regimental-attaches` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-regimental-attaches-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-rein-and-raus` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-relic-contemptor-dreadnought` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-relic-contemptor-dreadnought-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-relic-contemptor-dreadnought-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-relic-contemptor-dreadnought-4` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-relic-contemptor-dreadnought-5` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-relic-razorback` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-relic-terminator-squad` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-remora-stealth-drones` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-remote-sensor-tower` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-renegade-enforcer` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-renegade-enforcer-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-renegade-enforcer-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-renegade-heavy-weapons-squad` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-renegade-heavy-weapons-squad-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-renegade-heavy-weapons-squad-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-renegade-ogryn-beast-handler` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-renegade-ogryn-beast-handler-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-renegade-ogryn-beast-handler-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-renegade-ogryn-brutes` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-renegade-ogryn-brutes-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-renegade-ogryn-brutes-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-renegade-plague-ogryns` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-renegade-plague-ogryns-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-renegade-plague-ogryns-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-repressor` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-rhino-primaris` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-rogal-dorn-battle-tank-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-rogal-dorn-commander-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-rogue-psyker` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-rogue-psyker-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-rogue-psyker-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-rubric-marines-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-rvarna-battlesuit` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sabre-weapons-battery` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sabre-weapons-battery-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-salamander-command-vehicle` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-salamander-command-vehicle-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-salamander-scout-vehicle` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-salamander-scout-vehicle-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sanguinary-priest-with-jump-pack` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-scabeiathrax-the-bloated` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-scorpion` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-scout-bike-squad` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-scout-sentinels-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-scout-sniper-squad` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-scythed-hierodule` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-secutarii-hoplites` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-secutarii-peltasts` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sentinel-powerlifter` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sentinel-powerlifter-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sentry-pylon` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sergeant-chronus` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sergeant-harker` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sergeant-telion` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-servitors` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-shadow-spectres` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-shadowseer-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-shadowsword-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-shaso-ralai` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sicaran-arcus` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sicaran-battle-tank` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sicaran-battle-tank-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sicaran-battle-tank-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sicaran-battle-tank-4` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sicaran-battle-tank-5` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sicaran-omega` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sicaran-punisher` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sicaran-punisher-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sicaran-punisher-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sicaran-punisher-4` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sicaran-punisher-5` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sicaran-venator` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sicaran-venator-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sicaran-venator-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sicaran-venator-4` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sicaran-venator-5` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-skathach-wraithknight` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-skitarii-marshal-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-skitarii-rangers-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-skitarii-vanguard-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-skorchas` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sky-slasher-swarms` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-skyclaws` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-skyweavers-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sokar-pattern-stormbird` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sokar-pattern-stormbird-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sokar-pattern-stormbird-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sokar-pattern-stormbird-4` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sokar-pattern-stormbird-5` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-solitaire-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sorcerer-4` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sorcerer-in-terminator-armour-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sorcerer-on-bike` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sorcerer-on-disc-of-tzeentch` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sorcerer-on-disc-of-tzeentch-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sorcerer-on-palanquin-of-nurgle` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sorcerer-on-palanquin-of-nurgle-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sorcerer-on-palanquin-of-nurgle-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sorcerer-on-steed-of-slaanesh` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-sorcerer-on-steed-of-slaanesh-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-spartan` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-spartan-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-spartan-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-spartan-4` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-spartan-5` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-spectrus-kill-team-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-spined-chaos-beast` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-squiggoth` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-stalker` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-starfangs-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-starweaver-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-storm-chimera` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-storm-chimera-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-storm-eagle-gunship` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-storm-eagle-gunship-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-storm-eagle-gunship-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-storm-eagle-gunship-4` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-storm-eagle-gunship-5` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-stormblade` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-stormblade-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-stormfang-gunship` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-stormlord-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-stormsword-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-stormwolf` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-stygies-destroyer-tank-hunter` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-stygies-destroyer-tank-hunter-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-tantalus` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-tarantula-air-defence-battery` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-tarantula-battery` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-tarantula-battery-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-tarantula-sentry-battery` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-tauros-assault-vehicle` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-tauros-assault-vehicle-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-tauros-venator` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-tauros-venator-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-taurox-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-taurox-prime-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-tech-priest-dominus-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-tech-priest-manipulus-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-techmarine-on-bike` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-tectonic-fragdrill` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-terminus-ultra` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-terrax-pattern-termite` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-terrax-pattern-termite-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-terrax-pattern-termite-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-terrax-pattern-termite-4` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-terrax-pattern-termite-5` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-terrax-pattern-termite-6` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-tesseract-ark` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-tetras` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-the-red-terror-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-thunderfire-cannon` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-thunderhawk-transporter` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-tomb-citadel-walls` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-traitor-enforcer-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-traitor-enforcer-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-traitor-guardsmen-squad-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-traitor-guardsmen-squad-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-trojan-support-vehicle` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-trojan-support-vehicle-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-troupe-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-troupe-master-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-trygon-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-tx42-piranha` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-tycho-the-lost` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-typhon` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-typhon-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-typhon-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-typhon-4` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-typhon-5` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-tyrannic-war-veterans` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-tyrannocyte-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-ufthak-blackhawk` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-ur-025` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-urien-rakarth` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-valdor` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-valdor-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-valkyrie-sky-talon` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-vampire-hunter` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-vampire-raider` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-vanguard-veteran-squad` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-vargard-obyron` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-vendetta-gunship` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-venerable-dreadnought-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-veteran-bike-squad` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-vindicator-laser-destroyer` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-voidweaver-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-von-ryans-leapers-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-voss-pattern-lightning` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-vulture-gunship` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-vypers` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-warboss-on-warbike` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-warbuggies` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-warp-hunter` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-warp-talons-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-wasp-assault-walker` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-webway-gate` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-whirlwind-scorpius` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-whirlwind-scorpius-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-whirlwind-scorpius-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-whirlwind-scorpius-4` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-whirlwind-scorpius-5` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-winged-hive-tyrant-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-winged-tyranid-prime-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-wolf-guard` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-wolf-guard-battle-leader-in-terminator-armour` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-wolf-guard-battle-leader-on-thunderwolf` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-wolf-guard-pack-leader` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-wolf-guard-pack-leader-in-terminator-armour` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-wolf-guard-pack-leader-with-jump-pack` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-wolf-lord-on-thunderwolf` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-wraithseer` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-wyvern-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-x-101` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-xiphon-interceptor` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-xiphon-interceptor-2` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-xiphon-interceptor-3` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-xiphon-interceptor-4` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-xiphon-interceptor-5` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-xv9-hazard-battlesuits` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-yvahra-battlesuit` | — |
| `PRC-UNVERIFIED-STALE` | advisory | `ds-zarakynel` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-aquila-kill-team` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-aquila-kill-team` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-bike-squad` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-cadian-shock-troops` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-cadian-shock-troops` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-cadian-shock-troops-2` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-cadian-shock-troops-2` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-catachan-jungle-fighters` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-catachan-jungle-fighters` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-catachan-jungle-fighters-2` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-catachan-jungle-fighters-2` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-death-korps-grenadier-squad` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-death-korps-grenadier-squad-2` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-death-korps-of-krieg` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-death-korps-of-krieg` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-death-korps-of-krieg-2` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-death-korps-of-krieg-2` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-decimus-kill-team` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-decimus-kill-team` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-fortis-kill-team` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-fortis-kill-team-2` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-fortis-kill-team-2` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-gretchin` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-gretchin` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-gretchin` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-gretchin` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-gretchin` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-indomitor-kill-team` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-indomitor-kill-team-2` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-indomitor-kill-team-2` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-jakhals` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-jakhals` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-proteus-kill-team` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-proteus-kill-team` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-regimental-attaches` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-regimental-attaches-2` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-renegade-ogryn-beast-handler` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-renegade-ogryn-beast-handler-2` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-renegade-ogryn-beast-handler-3` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-shadow-spectres` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-spectrus-kill-team` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-spectrus-kill-team-2` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-spectrus-kill-team-2` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-talonstrike-kill-team` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-tarantula-sentry-battery` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-tarantula-sentry-battery` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-wolf-scouts` | — |
| `REC-BAND-MISMATCH` | advisory | `ds-wolf-scouts` | — |
| `REC-NEVER-PRICED` | blocking | `wahapedia:imperial-knights:Sir-Hekhtur` | The same datasheet the approved wahapedia:000002770 resolution already covers, re-identified under html mode where a detail id is the page anchor rather than an export id: an Epic Hero INFANTRY character in the knightly faction, no unit-cost table on its card, and no points entry on a faction page that leaves no unmatched unit at all. Carried forward unchanged in reasoning. |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:adepta-sororitas:Battle-Sanctum` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:adepta-sororitas:Celestian-Sacresant-Aveline` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:adepta-sororitas:Crusaders` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:adepta-sororitas:Death-Cult-Assassins` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:adepta-sororitas:Repressor` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:adeptus-mechanicus:Secutarii-Hoplites` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:adeptus-mechanicus:Secutarii-Peltasts` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:adeptus-mechanicus:Terrax-pattern-Termite` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:adeptus-mechanicus:X-101` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:aeldari:Amallyn-Shadowguide` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:aeldari:Autarch-Skyrunner` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:aeldari:Bonesinger` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:aeldari:Cobra` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:aeldari:Corsair-Cloud-Dancer-Band` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:aeldari:Corsair-Reaver-Band` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:aeldari:Firestorm` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:aeldari:Hornet` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:aeldari:Illic-Nightspear` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:aeldari:Irillyth` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:aeldari:Karandras` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:aeldari:Lynx` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:aeldari:Nightwing` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:aeldari:Phoenix` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:aeldari:Scorpion` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:aeldari:Shadow-Spectres` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:aeldari:Skathach-Wraithknight` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:aeldari:Vampire-Hunter` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:aeldari:Vampire-Raider` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:aeldari:Vypers` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:aeldari:Warp-Hunter` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:aeldari:Wasp-Assault-Walker` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:aeldari:Webway-Gate` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:aeldari:Wraithseer` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Aquila-Lander` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Arkurian-Stormhammer` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Armageddon-pattern-Medusa` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Arvus-Lighter` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Atlas-Recovery-Vehicle` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Carnodon` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Centaur-Light-Carrier` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Colossus` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Crassus` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Death-Korps-Grenadier-Squad` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Death-Rider-Commissar` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Dominus-Armoured-Siege-Bombard` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Earthshaker-Carriage-Battery` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Earthshaker-Platform` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Elysian-Drop-Sentinel` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Elysian-Sniper-Squad` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Gorgon-Heavy-Transport` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Griffon-Mortar-Carrier` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Hades-Breaching-Drill` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Heavy-Mortar-Team` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Heavy-Quad-Launcher-Team` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Hell-s-Last` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Hydra-Platform` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Iron-Hand-Straken` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Macharius` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Macharius-Omega` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Macharius-Vanquisher` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Macharius-Vulcan` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Malcador` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Malcador-Annihilator` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Malcador-Defender` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Malcador-Infernus` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Manticore-Platform` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Marauder-Bomber` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Marauder-Destroyer` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Medusa-Carriage-Battery` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Minotaur` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Mukaali-Riders` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Munitorum-Servitors` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Praetor` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Provisionally-Prepared` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Quartermaster-Cadre-Squad` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Rapier-Laser-Destroyer-Battery` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Regimental-Attach-s` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Rein-And-Raus` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Sabre-Weapons-Battery` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Salamander-Command-Vehicle` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Salamander-Scout-Vehicle` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Sentinel-Powerlifter` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Sergeant-Harker` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Storm-Chimera` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Stormblade` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Stygies-Destroyer-Tank-Hunter` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Tarantula-Battery` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Tauros-Assault-Vehicle` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Tauros-Venator` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Trojan-Support-Vehicle` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Valdor` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Valkyrie-Sky-Talon` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Vendetta-Gunship` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Voss-pattern-Lightning` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:astra-militarum:Vulture-Gunship` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Accursed-Cultists` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Aetaos-rau-keres` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:An-ggrath-the-Unbound` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Chaos-Lord` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Chaos-Lord-In-Terminator-Armour` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Chaos-Lord-On-Disc-Of-Tzeentch` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Chaos-Lord-On-Juggernaut` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Chaos-Lord-On-Palanquin-Of-Nurgle` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Chaos-Lord-On-Steed-Of-Slaanesh` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Chaos-Lord-with-Jump-Pack` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Chaos-Terminator-Squad` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Chosen` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Cultist-Firebrand` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Cultist-Mob` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Cultist-Mob-with-Firearms` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Dark-Apostle` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Dark-Commune` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Fellgor-Beastmen` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Furies` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Gellerpox-Infected` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Giant-Chaos-Spawn` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Havocs` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Hellflayers-1` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Herald-Of-Slaanesh-On-Steed-Of-Slaanesh` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Legionaries` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Master-Of-Possession` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Mutoid-Vermin` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Negavolt-Cultists` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Plague-Toads` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Possessed` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Pox-Riders` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Raptors` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Renegade-Enforcer` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Renegade-Heavy-Weapons-Squad` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Renegade-Ogryn-Beast-Handler` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Renegade-Ogryn-Brutes` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Renegade-Plague-Ogryns` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Rogue-Psyker` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Scabeiathrax-The-Bloated` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Sorcerer` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Sorcerer-In-Terminator-Armour` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Sorcerer-On-Disc-Of-Tzeentch` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Sorcerer-On-Palanquin-Of-Nurgle` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Sorcerer-On-Steed-Of-Slaanesh` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Spined-Chaos-Beast` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Traitor-Enforcer` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Traitor-Guardsmen-Squad` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Warp-Talons` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-daemons:Zarakynel` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-knights:Accursed-Cultists` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-knights:Cultist-Firebrand` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-knights:Cultist-Mob` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-knights:Cultist-Mob-with-Firearms` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-knights:Dark-Commune` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-knights:Fellgor-Beastmen` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-knights:Gellerpox-Infected` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-knights:Mutoid-Vermin` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-knights:Negavolt-Cultists` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-knights:Renegade-Enforcer` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-knights:Renegade-Heavy-Weapons-Squad` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-knights:Renegade-Ogryn-Beast-Handler` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-knights:Renegade-Ogryn-Brutes` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-knights:Renegade-Plague-Ogryns` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-knights:Rogue-Psyker` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-knights:Traitor-Enforcer` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-knights:Traitor-Guardsmen-Squad` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Blood-Slaughterer` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Cerberus` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Chaos-Deimos-Predator` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Chaos-Lord-On-Bike` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Chaos-Lord-On-Disc-Of-Tzeentch` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Chaos-Lord-On-Juggernaut` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Chaos-Lord-On-Palanquin-Of-Nurgle` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Chaos-Lord-On-Steed-Of-Slaanesh` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Chaos-Thunderhawk` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Cultist-Mob-with-Firearms` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Decimator` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Deredeo-Dreadnought` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Dreadclaw-Drop-Pod` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Exalted-Champion` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Falchion` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Fellblade` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Fire-Raptor-Gunship` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Gellerpox-Infected` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Greater-Blight-Drone` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Greater-Brass-Scorpion` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Hell-Blade` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Hell-Talon` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Kharybdis-Assault-Claw` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Khorne-Berzerkers` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Kratos` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Kytan-Ravager` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Land-Raider-Achilles` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Land-Raider-Proteus` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Leviathan-Dreadnought` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Mastodon` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Mutoid-Vermin` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Negavolt-Cultists` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Noise-Marines` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Plague-Marines` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Rapier-Carrier` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Relic-Contemptor-Dreadnought` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Renegade-Enforcer` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Renegade-Heavy-Weapons-Squad` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Renegade-Ogryn-Beast-Handler` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Renegade-Ogryn-Brutes` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Renegade-Plague-Ogryns` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Rogue-Psyker` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Rubric-Marines` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Sicaran-Battle-Tank` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Sicaran-Punisher` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Sicaran-Venator` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Sokar-pattern-Stormbird` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Sorcerer-On-Bike` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Sorcerer-On-Disc-Of-Tzeentch` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Sorcerer-On-Palanquin-Of-Nurgle` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Sorcerer-On-Steed-Of-Slaanesh` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Spartan` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Storm-Eagle-Gunship` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Terrax-pattern-Termite` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Typhon` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Whirlwind-Scorpius` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:chaos-space-marines:Xiphon-Interceptor` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:death-guard:Cerberus` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:death-guard:Chaos-Lord-On-Palanquin-Of-Nurgle` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:death-guard:Chaos-Thunderhawk` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:death-guard:Death-Guard-Chaos-Lord` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:death-guard:Death-Guard-Chaos-Lord-In-Terminator-Armour` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:death-guard:Death-Guard-Cultists` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:death-guard:Death-Guard-Possessed` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:death-guard:Death-Guard-Sorcerer-In-Terminator-Armour` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:death-guard:Deredeo-Dreadnought` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:death-guard:Falchion` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:death-guard:Fellblade` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:death-guard:Fire-Raptor-Gunship` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:death-guard:Gellerpox-Infected` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:death-guard:Greater-Blight-Drone` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:death-guard:Hell-Blade` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:death-guard:Hell-Talon` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:death-guard:Kratos` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:death-guard:Land-Raider-Achilles` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:death-guard:Land-Raider-Proteus` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:death-guard:Leviathan-Dreadnought` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:death-guard:Mastodon` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:death-guard:Mutoid-Vermin` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:death-guard:Myphitic-Blight-hauler` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:death-guard:Rapier-Carrier` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:death-guard:Relic-Contemptor-Dreadnought` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:death-guard:Sicaran-Battle-Tank` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:death-guard:Sicaran-Punisher` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:death-guard:Sicaran-Venator` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:death-guard:Sokar-pattern-Stormbird` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:death-guard:Sorcerer-On-Palanquin-Of-Nurgle` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:death-guard:Spartan` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:death-guard:Storm-Eagle-Gunship` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:death-guard:Terrax-pattern-Termite` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:death-guard:Typhon` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:death-guard:Whirlwind-Scorpius` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:death-guard:Xiphon-Interceptor` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:drukhari:Beastmaster` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:drukhari:Corsair-Cloud-Dancer-Band` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:drukhari:Corsair-Reaver-Band` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:drukhari:Corsair-Skyreavers` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:drukhari:Corsair-Voidreavers` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:drukhari:Corsair-Voidscarred` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:drukhari:Court-of-the-Archon` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:drukhari:Death-Jester` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:drukhari:Grotesques` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:drukhari:Kharseth` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:drukhari:Prince-Yriel` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:drukhari:Raven-Strike-Fighter` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:drukhari:Reaper` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:drukhari:Shadowseer` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:drukhari:Skyweavers` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:drukhari:Solitaire` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:drukhari:Starfangs` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:drukhari:Starweaver` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:drukhari:Tantalus` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:drukhari:Troupe` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:drukhari:Troupe-Master` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:drukhari:Urien-Rakarth` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:drukhari:Voidweaver` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Aegis-Defence-Line` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Arkurian-Stormhammer` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Armageddon-pattern-Medusa` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Armoured-Sentinels` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Artillery-Team` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Atlas-Recovery-Vehicle` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Attilan-Rough-Riders` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Baneblade` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Banehammer` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Banesword` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Basilisk` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Cadian-Castellan` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Cadian-Command-Squad` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Cadian-Heavy-Weapons-Squad` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Cadian-Shock-Troops` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Carnodon` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Catachan-Command-Squad` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Catachan-Heavy-Weapons-Squad` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Catachan-Jungle-Fighters` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Centaur-Light-Carrier` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Centaur-RSV` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Chimera` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Colossus` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Crassus` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Cyclops-Demolition-Vehicle` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Death-Korps-Grenadier-Squad` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Death-Korps-Of-Krieg` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Death-Rider-Commissar` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Death-Riders` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Deathleaper` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Deathstrike` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Dominus-Armoured-Siege-Bombard` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Doomhammer` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Earthshaker-Carriage-Battery` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Earthshaker-Platform` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Elysian-Drop-Sentinel` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Elysian-Sniper-Squad` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Field-Ordnance-Battery` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Gargoyles` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Gorgon-Heavy-Transport` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Griffon-Mortar-Carrier` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Hades-Breaching-Drill` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Heavy-Mortar-Team` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Heavy-Quad-Launcher-Team` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Hell-s-Last` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Hellhammer` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Hellhound` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Hippogriff-AFV` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Hydra` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Hydra-Platform` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Hyperadapted-Raveners` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Kasrkin` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Krieg-Combat-Engineers` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Krieg-Command-Squad` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Krieg-Heavy-Weapons-Squad` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Leman-Russ-Battle-Tank` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Leman-Russ-Commander` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Leman-Russ-Demolisher` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Leman-Russ-Eradicator` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Leman-Russ-Executioner` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Leman-Russ-Exterminator` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Leman-Russ-Punisher` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Leman-Russ-Vanquisher` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Lictor` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Macharius` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Macharius-Omega` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Macharius-Vanquisher` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Macharius-Vulcan` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Malcador` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Malcador-Annihilator` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Malcador-Defender` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Malcador-Infernus` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Manticore` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Manticore-Platform` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Mawloc` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Medusa-Carriage-Battery` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Minotaur` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Mukaali-Riders` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Munitorum-Servitors` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Neurolictor` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Parasite-Of-Mortrex` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Praetor` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Primaris-Psyker` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Quartermaster-Cadre-Squad` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Rapier-Laser-Destroyer-Battery` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Raveners` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Regimental-Attach-s` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Rogal-Dorn-Battle-Tank` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Rogal-Dorn-Commander` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Sabre-Weapons-Battery` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Salamander-Command-Vehicle` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Salamander-Scout-Vehicle` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Scout-Sentinels` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Sentinel-Powerlifter` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Shadowsword` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Storm-Chimera` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Stormblade` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Stormlord` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Stormsword` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Stygies-Destroyer-Tank-Hunter` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Tarantula-Battery` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Tauros-Assault-Vehicle` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Tauros-Venator` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Taurox` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Taurox-Prime` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Tectonic-Fragdrill` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:The-Red-Terror` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Trojan-Support-Vehicle` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Trygon` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Tyrannocyte` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Valdor` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Von-Ryan-s-Leapers` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Winged-Hive-Tyrant` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Winged-Tyranid-Prime` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:genestealer-cults:Wyvern` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:grey-knights:Brother-captain-Stern` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:grey-knights:Grey-Knights-Dreadnought` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:grey-knights:Grey-Knights-Relic-Razorback` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:grey-knights:Kaldor-Draigo` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:grey-knights:Servitors` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:imperial-agents:Daemonhost` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:imperial-agents:Damned-Legionnaires` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:imperial-agents:Deathwatch-Terminator-Squad` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:imperial-agents:Fortis-Kill-Team` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:imperial-agents:Indomitor-Kill-Team` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:imperial-agents:Inquisitor-Eisenhorn` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:imperial-agents:Inquisitor-In-Terminator-Armour` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:imperial-agents:Inquisitor-Karamazov` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:imperial-agents:Inquisitor-Ostromandeus` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:imperial-agents:Janus-Draik` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:imperial-agents:Jokaero-Weaponsmith` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:imperial-agents:Kill-Team-Cassius` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:imperial-agents:Neyam-Shai-Murad` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:imperial-agents:Proteus-Kill-Team` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:imperial-agents:Spectrus-Kill-Team` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:imperial-agents:UR-025` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:imperial-agents:Veteran-Bike-Squad` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:imperial-knights:Sir-Hekhtur` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:imperial-knights:Skitarii-Marshal` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:imperial-knights:Skitarii-Rangers` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:imperial-knights:Skitarii-Vanguard` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:imperial-knights:Tech-priest-Dominus` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:imperial-knights:Tech-priest-Manipulus` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:necrons:Anrakyr-The-Traveller` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:necrons:Canoptek-Acanthrites` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:necrons:Canoptek-Tomb-Sentinel` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:necrons:Canoptek-Tomb-Stalker` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:necrons:Gauss-Pylon` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:necrons:Lord` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:necrons:Nemesor-Zahndrekh` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:necrons:Night-Shroud` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:necrons:Sentry-Pylon` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:necrons:Tesseract-Ark` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:necrons:Tomb-Citadel-Walls` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:necrons:Vargard-Obyron` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:orks:Attack-Fighta` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:orks:Big-Gunz` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:orks:Big-Mek-On-Warbike` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:orks:Big-Mek-With-Kustom-Force-Field` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:orks:Big-Trakk` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:orks:Boss-Zagstruk` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:orks:Chinork-Warkopta` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:orks:Da-Red-Gobbo` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:orks:Deff-Rolla-Battle-Fortress` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:orks:Deffkoptas-With-Big-Shootas` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:orks:Fighta-bommer` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:orks:Grot-Bomm-Launcha` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:orks:Grot-Mega-tank` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:orks:Grot-Tanks` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:orks:Kannonwagon` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:orks:Kaptin-Badrukk` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:orks:Kill-Krusha` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:orks:Kill-Tank` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:orks:Lifta-Wagon` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:orks:Mad-Dok-Grotsnik` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:orks:Mega-Dread` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:orks:Meka-dread` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:orks:Mekboy-Workshop` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:orks:Nobz-On-Warbikes` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:orks:Painboy-On-Warbike` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:orks:Skorchas` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:orks:Squiggoth` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:orks:Ufthak-Blackhawk` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:orks:Warboss-On-Warbike` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:orks:Warbuggies` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Ancient-on-Bike` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Apothecary-on-Bike` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Assault-Squad` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Assault-Squad-with-Jump-Packs` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Astartes-Servitors` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Attack-Bike-Squad` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Bike-Squad` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Brother-Corbulo` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Caestus-Assault-Ram` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Canis-Wolfborn` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Captain-Tycho` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Captain-on-Bike` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Carab-Culln-The-Risen` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Cerberus` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Chaplain-Cassius` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Chaplain-Venerable-Dreadnought` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Command-Squad` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Company-Champion-on-Bike` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Company-Veterans-On-Bikes` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Cyberwolf` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Death-Company-Dreadnought-with-Magna-grapple` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Death-Company-Marines-with-Boltguns` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Death-Company-Marines-with-Boltguns-and-Jump-Packs` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Deathstorm-Drop-Pod` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Deathwing-Command-Squad` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Deathwing-Strikemaster` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Deimos-Predator` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Deredeo-Dreadnought` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Dreadnought-Drop-Pod` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Falchion` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Fellblade` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Ferren-Areios` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Fire-Raptor-Gunship` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Furioso-Dreadnought` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Gabriel-Seth` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Harald-Deathwolf` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Hounds-Of-Morkai` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Hunter` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Imperial-Space-Marine` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Ironclad-Dreadnought` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Javelin-Attack-Speeder` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Kill-Team-Cassius` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Kratos` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Krom-Dragongaze` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Land-Raider-Achilles` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Land-Raider-Excelsior` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Land-Raider-Helios` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Land-Raider-Prometheus` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Land-Raider-Proteus` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Land-Speeder-Storm` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Land-Speeder-Tempest` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Land-Speeder-Tornado` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Land-Speeder-Typhoon` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Leviathan-Dreadnought` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Librarian-Dreadnought` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Librarian-on-Bike` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Librarian-with-Jump-Pack` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Logan-Grimnar-On-Stormrider` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Long-Fangs` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Lukas-The-Trickster` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Mastodon` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Mortis-Dreadnought` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Primaris-Company-Champion` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Rapier-Carrier` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Ravenwing-Talonmaster` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Relic-Contemptor-Dreadnought` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Relic-Razorback` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Relic-Terminator-Squad` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Rhino-Primaris` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Sanguinary-Priest-With-Jump-Pack` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Scout-Bike-Squad` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Scout-Sniper-Squad` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Sergeant-Chronus` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Sergeant-Telion` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Sicaran-Arcus` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Sicaran-Battle-Tank` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Sicaran-Omega` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Sicaran-Punisher` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Sicaran-Venator` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Skyclaws` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Sokar-pattern-Stormbird` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Spartan` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Stalker` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Storm-Eagle-Gunship` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Stormfang-Gunship` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Stormwolf` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Tarantula-Air-Defence-Battery` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Tarantula-Sentry-Battery` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Techmarine-on-Bike` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Terminus-Ultra` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Terrax-pattern-Termite` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Thunderfire-Cannon` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Thunderhawk-Transporter` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Tycho-The-Lost` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Typhon` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Tyrannic-War-Veterans` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Vanguard-Veteran-Squad` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Venerable-Dreadnought` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Vindicator-Laser-Destroyer` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Whirlwind-Scorpius` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Wolf-Guard` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Wolf-Guard-Battle-Leader-In-Terminator-Armour` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Wolf-Guard-Battle-Leader-On-Thunderwolf` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Wolf-Guard-Pack-Leader` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Wolf-Guard-Pack-Leader-In-Terminator-Armour` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Wolf-Guard-Pack-Leader-With-Jump-Pack` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Wolf-Lord-on-Thunderwolf` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:space-marines:Xiphon-Interceptor` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:t-au-empire:Aun-shi` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:t-au-empire:Aun-va` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:t-au-empire:Barracuda` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:t-au-empire:Commander-In-Crisis-Battlesuit` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:t-au-empire:Crisis-Battlesuits` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:t-au-empire:Drone-Sentry-Turret` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:t-au-empire:Great-Knarloc` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:t-au-empire:Heavy-Gun-Drones` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:t-au-empire:Knarloc-Riders` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:t-au-empire:Longstrike` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:t-au-empire:Orca-Dropship` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:t-au-empire:R-varna-Battlesuit` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:t-au-empire:Remora-Stealth-Drones` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:t-au-empire:Remote-Sensor-Tower` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:t-au-empire:Shas-o-R-alai` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:t-au-empire:Tetras` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:t-au-empire:Tx42-Piranha` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:t-au-empire:Xv9-Hazard-Battlesuits` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:t-au-empire:Y-vahra-Battlesuit` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:thousand-sons:Cerberus` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:thousand-sons:Chaos-Lord-On-Disc-Of-Tzeentch` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:thousand-sons:Chaos-Thunderhawk` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:thousand-sons:Deredeo-Dreadnought` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:thousand-sons:Falchion` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:thousand-sons:Fellblade` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:thousand-sons:Fire-Raptor-Gunship` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:thousand-sons:Hell-Blade` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:thousand-sons:Hell-Talon` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:thousand-sons:Kratos` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:thousand-sons:Land-Raider-Achilles` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:thousand-sons:Land-Raider-Proteus` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:thousand-sons:Leviathan-Dreadnought` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:thousand-sons:Mastodon` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:thousand-sons:Rapier-Carrier` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:thousand-sons:Relic-Contemptor-Dreadnought` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:thousand-sons:Sicaran-Battle-Tank` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:thousand-sons:Sicaran-Punisher` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:thousand-sons:Sicaran-Venator` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:thousand-sons:Sokar-pattern-Stormbird` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:thousand-sons:Spartan` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:thousand-sons:Storm-Eagle-Gunship` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:thousand-sons:Terrax-pattern-Termite` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:thousand-sons:Typhon` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:thousand-sons:Whirlwind-Scorpius` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:thousand-sons:Xiphon-Interceptor` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:tyranids:Barbed-Hierodule` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:tyranids:Dimachaeron` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:tyranids:Malanthrope` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:tyranids:Scythed-Hierodule` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:tyranids:Sky-slasher-Swarms` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:world-eaters:Blood-Slaughterer` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:world-eaters:Cerberus` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:world-eaters:Chaos-Thunderhawk` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:world-eaters:Deredeo-Dreadnought` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:world-eaters:Falchion` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:world-eaters:Fellblade` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:world-eaters:Fire-Raptor-Gunship` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:world-eaters:Greater-Brass-Scorpion` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:world-eaters:Hell-Blade` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:world-eaters:Hell-Talon` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:world-eaters:Kratos` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:world-eaters:Kytan-Ravager` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:world-eaters:Land-Raider-Achilles` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:world-eaters:Land-Raider-Proteus` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:world-eaters:Leviathan-Dreadnought` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:world-eaters:Mastodon` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:world-eaters:Rapier-Carrier` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:world-eaters:Relic-Contemptor-Dreadnought` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:world-eaters:Sicaran-Battle-Tank` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:world-eaters:Sicaran-Punisher` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:world-eaters:Sicaran-Venator` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:world-eaters:Sokar-pattern-Stormbird` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:world-eaters:Spartan` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:world-eaters:Storm-Eagle-Gunship` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:world-eaters:Terrax-pattern-Termite` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:world-eaters:Typhon` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:world-eaters:Whirlwind-Scorpius` | — |
| `REC-UNMATCHED-DETAIL-ONLY` | advisory | `wahapedia:world-eaters:Xiphon-Interceptor` | — |
| `REC-UNMATCHED-POINTS-ONLY` | advisory | `mfm:aeldari/vyper` | — |
| `REC-UNMATCHED-POINTS-ONLY` | advisory | `mfm:chaos-titan-legions/chaos reaver titan` | — |
| `REC-UNMATCHED-POINTS-ONLY` | advisory | `mfm:chaos-titan-legions/chaos warbringer nemesis titan` | — |
| `REC-UNMATCHED-POINTS-ONLY` | advisory | `mfm:chaos-titan-legions/chaos warhound titan` | — |
| `REC-UNMATCHED-POINTS-ONLY` | advisory | `mfm:chaos-titan-legions/chaos warlord titan` | — |
| `REC-UNMATCHED-POINTS-ONLY` | advisory | `mfm:death-guard/myphitic blight haulers` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-aberrants` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-aberrants` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-abominant` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-acastus-knight-asterius` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-acastus-knight-porphyrion` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-accursed-cultists` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-accursed-cultists` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-achilles-ridgerunners` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-achilles-ridgerunners` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-aggressor-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-aggressor-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-aggressor-squad-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-aggressor-squad-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-aggressor-squad-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-aggressor-squad-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-aggressor-squad-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-aggressor-squad-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-aggressor-squad-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-aggressor-squad-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-aggressor-squad-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-aggressor-squad-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-anathema-psykana-rhino` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-ares-gunship` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-armiger-moirax` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-assault-intercessor-squad-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-assault-intercessors-with-jump-packs` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-assault-intercessors-with-jump-packs` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-assault-intercessors-with-jump-packs-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-assault-intercessors-with-jump-packs-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-assault-intercessors-with-jump-packs-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-assault-intercessors-with-jump-packs-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-assault-intercessors-with-jump-packs-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-assault-intercessors-with-jump-packs-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-assault-intercessors-with-jump-packs-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-assault-intercessors-with-jump-packs-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-assault-intercessors-with-jump-packs-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-assault-intercessors-with-jump-packs-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-assault-intercessors-with-jump-packs-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-assault-intercessors-with-jump-packs-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-astraeus` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-astraeus-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-astraeus-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-astraeus-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-astraeus-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-astraeus-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-atalan-jackals` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-atalan-jackals` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-atalan-jackals` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-attilan-rough-riders` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-attilan-rough-riders` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-ax-1-0-tiger-shark` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-baal-predator` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-ballistus-dreadnought` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-ballistus-dreadnought-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-ballistus-dreadnought-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-ballistus-dreadnought-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-ballistus-dreadnought-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-ballistus-dreadnought-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-baneblade` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-banehammer` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-banesword` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-basilisk` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-big-mek-with-shokk-attack-gun` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-blade-champion` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-bladeguard-veteran-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-bladeguard-veteran-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-bladeguard-veteran-squad-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-bladeguard-veteran-squad-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-bladeguard-veteran-squad-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-bladeguard-veteran-squad-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-bladeguard-veteran-squad-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-bladeguard-veteran-squad-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-bladeguard-veteran-squad-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-bladeguard-veteran-squad-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-bladeguard-veteran-squad-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-bladeguard-veteran-squad-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-bladeguard-veteran-squad-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-bladeguard-veteran-squad-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-bloodcrushers` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-bloodcrushers` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-bloodcrushers-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-bloodcrushers-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-bloodthirster` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-bloodthirster-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-boyz` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-boyz` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-breaka-boyz` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-broadside-battlesuits` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-broadside-battlesuits` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-broadside-battlesuits` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-brokhyr-thunderkyn` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-brokhyr-thunderkyn` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-brotherhood-librarian` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-brutalis-dreadnought` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-brutalis-dreadnought-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-brutalis-dreadnought-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-brutalis-dreadnought-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-brutalis-dreadnought-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-brutalis-dreadnought-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-bullgryn-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-bullgryn-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-caladius-grav-tank` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-canoptek-wraiths` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-canoptek-wraiths` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-captain-with-jump-pack-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-castigator` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-celestian-sacresants` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-celestian-sacresants` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-centaur-rsv` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-cerastus-knight-acheron` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-cerastus-knight-atrapos` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-cerastus-knight-castigator` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-cerastus-knight-lancer` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-chaos-acastus-knight-asterius` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-chaos-acastus-knight-porphyrion` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-chaos-cerastus-knight-acheron` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-chaos-cerastus-knight-atrapos` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-chaos-cerastus-knight-castigator` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-chaos-cerastus-knight-lancer` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-chaos-land-raider` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-chaos-land-raider-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-chaos-land-raider-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-chaos-land-raider-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-chaos-land-raider-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-chaos-predator-annihilator` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-chaos-predator-annihilator-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-chaos-predator-annihilator-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-chaos-predator-annihilator-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-chaos-predator-destructor` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-chaos-predator-destructor-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-chaos-predator-destructor-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-chaos-predator-destructor-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-chaos-questoris-knight-magaera` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-chaos-questoris-knight-styrix` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-chaos-rhino` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-chaos-rhino-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-chaos-rhino-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-chaos-rhino-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-chaos-rhino-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-chaos-terminators-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-chaos-terminators-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-chaos-vindicator` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-chaos-vindicator-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-chaplain-with-jump-pack-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-chimera` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-chosen` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-chosen` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-chronomancer` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-contemptor-achillus-dreadnought` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-contemptor-galatus-dreadnought` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-coronus-grav-carrier` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-crisis-fireknife-battlesuits` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-crisis-starscythe-battlesuits` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-crisis-sunforge-battlesuits` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-cultist-firebrand` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-custodian-guard` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-custodian-guard` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-custodian-guard-with-adrasite-and-pyrithite-spears` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-custodian-wardens` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-custodian-wardens` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-cyclops-demolition-vehicle` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-d-cannon-platform` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-daemon-prince-of-slaanesh` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-daemon-prince-of-slaanesh-with-wings` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-daemon-prince-of-tzeentch-with-wings` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-dark-commune` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-death-company-dreadnought` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-death-company-marines` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-death-company-marines` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-death-company-marines-with-bolt-rifles` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-death-company-marines-with-bolt-rifles` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-death-company-marines-with-jump-packs` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-death-company-marines-with-jump-packs` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-deathmarks` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-deathmarks` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-deathshroud-terminators` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-deathshroud-terminators` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-deathstrike` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-deathwing-knights` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-deff-dread` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-defiler` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-defiler-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-defiler-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-defiler-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-defiler-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-desolation-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-desolation-squad-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-desolation-squad-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-desolation-squad-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-desolation-squad-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-desolation-squad-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-devilfish` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-dominion-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-doomhammer` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-doomsday-ark` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-drop-pod` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-drop-pod-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-drop-pod-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-drop-pod-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-drop-pod-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-drop-pod-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-eightbound` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-eightbound` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-einhyr-hearthguard` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-einhyr-hearthguard` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-eradicator-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-eradicator-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-eradicator-squad-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-eradicator-squad-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-eradicator-squad-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-eradicator-squad-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-eradicator-squad-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-eradicator-squad-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-eradicator-squad-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-eradicator-squad-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-eradicator-squad-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-eradicator-squad-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-eversor-assassin` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-exaction-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-exalted-eightbound` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-exalted-eightbound` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-exocrine` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-exorcist` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-fenrisian-wolves` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-fenrisian-wolves` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-fire-dragons` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-fire-dragons` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-flash-gitz` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-flash-gitz` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-foetid-bloat-drone` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-foetid-bloat-drone-with-heavy-blight-launcher` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-forgefiend` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-forgefiend-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-forgefiend-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-fortis-kill-team` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-gargantuan-squiggoth` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-genestealers` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-genestealers` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-ghostkeel-battlesuit` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-gladiator-lancer` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-gladiator-lancer-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-gladiator-lancer-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-gladiator-lancer-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-gladiator-lancer-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-gladiator-lancer-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-gladiator-reaper` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-gladiator-reaper-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-gladiator-reaper-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-gladiator-reaper-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-gladiator-reaper-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-gladiator-reaper-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-gladiator-valiant` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-gladiator-valiant-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-gladiator-valiant-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-gladiator-valiant-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-gladiator-valiant-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-gladiator-valiant-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-goliath-rockgrinder` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-goliath-truck` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-gorkanaut` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-grand-master-in-nemesis-dreadknight` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-great-unclean-one` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-great-unclean-one-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-grey-knights-terminator-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-grey-knights-thunderhawk-gunship` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-hammerhead-gunship` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-harridan` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-haruspex` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-hastarii-exterminators` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-hastarii-fusiliers` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-havocs` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-hekaton-land-fortress` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-hellhammer` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-hellhound` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-hellions` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-hellions` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-hernkyn-pioneers` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-hernkyn-pioneers` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-hierophant` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-hive-guard` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-hive-guard` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-hospitaller` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-hybrid-metamorphs` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-hybrid-metamorphs` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-hyperadapted-raveners` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-immolator` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-imperial-rhino` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-imperial-rhino` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-impulsor` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-impulsor-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-impulsor-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-impulsor-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-impulsor-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-impulsor-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-inceptor-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-inceptor-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-inceptor-squad-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-inceptor-squad-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-inceptor-squad-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-inceptor-squad-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-inceptor-squad-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-inceptor-squad-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-inceptor-squad-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-inceptor-squad-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-inceptor-squad-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-inceptor-squad-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-incubi` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-incubi` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-incursor-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-incursor-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-incursor-squad-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-incursor-squad-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-incursor-squad-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-incursor-squad-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-incursor-squad-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-incursor-squad-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-incursor-squad-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-incursor-squad-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-incursor-squad-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-incursor-squad-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-indomitor-kill-team` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-infiltrator-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-infiltrator-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-infiltrator-squad-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-infiltrator-squad-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-infiltrator-squad-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-infiltrator-squad-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-infiltrator-squad-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-infiltrator-squad-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-infiltrator-squad-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-infiltrator-squad-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-infiltrator-squad-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-infiltrator-squad-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-inner-circle-companions` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-inner-circle-companions` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-inquisitor` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-inquisitor-coteaz` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-inquisitor-draxus` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-inquisitorial-agents` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-inquisitorial-agents` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-inquisitorial-chimera` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-inquisitorial-chimera` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-interceptor-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-interceptor-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-ironkin-steeljacks-with-heavy-volkanite-disintegrators` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-ironkin-steeljacks-with-heavy-volkanite-disintegrators` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-ironkin-steeljacks-with-melee-weapons` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-ironkin-steeljacks-with-melee-weapons` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-ironstrider-ballistarii` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-ironstrider-ballistarii` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-ironstrider-ballistarii` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-kapricus-carrier` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-kasrkin` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-kastelan-robots` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-kastelan-robots` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-keeper-of-secrets` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-keeper-of-secrets-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-khorne-lord-of-skulls` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-khorne-lord-of-skulls-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-killa-kans` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-killa-kans` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-knight-abominant` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-knight-castellan` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-knight-crusader` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-knight-defender` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-knight-desecrator` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-knight-despoiler` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-knight-destrier` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-knight-errant` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-knight-gallant` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-knight-paladin` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-knight-preceptor` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-knight-rampager` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-knight-ruinator` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-knight-tyrant` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-knight-valiant` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-knight-warden` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-krieg-combat-engineers` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-krieg-combat-engineers` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-kroot-farstalkers` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-krootox-rampagers` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-krootox-rampagers` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-land-raider` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-land-raider-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-land-raider-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-land-raider-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-land-raider-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-land-raider-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-land-raider-7` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-land-raider-crusader` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-land-raider-crusader-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-land-raider-crusader-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-land-raider-crusader-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-land-raider-crusader-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-land-raider-crusader-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-land-raider-crusader-7` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-land-raider-redeemer` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-land-raider-redeemer-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-land-raider-redeemer-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-land-raider-redeemer-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-land-raider-redeemer-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-land-raider-redeemer-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-land-raider-redeemer-7` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-land-speeder-vengeance` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-leman-russ-battle-tank` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-leman-russ-commander` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-leman-russ-demolisher` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-leman-russ-eradicator` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-leman-russ-executioner` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-leman-russ-exterminator` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-leman-russ-punisher` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-leman-russ-vanquisher` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-librarian` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-librarian-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-librarian-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-librarian-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-librarian-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-lokhust-destroyers` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-lokhust-destroyers` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-lokhust-destroyers` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-lokhust-destroyers` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-lokhust-heavy-destroyers` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-lokhust-heavy-destroyers` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-lokhust-heavy-destroyers` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-lootas` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-lootas` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-lord-exultant` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-lord-of-change` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-lord-of-change-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-maleceptor` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-mandrakes` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-mandrakes` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-manta` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-manticore` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-marshal` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-maulerfiend-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-maulerfiend-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-maulerfiend-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-meganobz` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-meganobz` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-meganobz` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-meganobz` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-mek-gunz` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-mek-gunz` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-mek-gunz` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-militarum-tempestus-command-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-monolith` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-morkanaut` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-mutalith-vortex-beast` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-mutilators` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-navigator` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-nemesis-dreadknight` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-neurolictor` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-night-spinner` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-nobz` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-nobz` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-noise-marines` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-norn-assimilator` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-norn-emissary` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-obelisk` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-obliterators` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-ophydian-destroyers` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-ophydian-destroyers` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-orion-assault-dropship` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-outrider-squad-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-paladin-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-paladin-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-paladin-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-paladin-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-paragon-warsuits` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-pathfinder-team` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-phantom-titan` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-piranhas` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-piranhas` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-piranhas` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-plagueburst-crawler` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-possessed` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-possessed` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-predator-annihilator` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-predator-annihilator-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-predator-annihilator-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-predator-annihilator-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-predator-annihilator-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-predator-annihilator-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-predator-destructor` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-predator-destructor-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-predator-destructor-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-predator-destructor-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-predator-destructor-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-predator-destructor-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-pteraxii-skystalkers` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-pteraxii-skystalkers` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-pteraxii-sterylizors` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-pteraxii-sterylizors` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-purestrain-genestealers` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-purestrain-genestealers` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-purgation-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-purgation-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-purifier-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-purifier-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-pyrovores` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-pyrovores` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-pyrovores` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-questoris-knight-magaera` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-questoris-knight-styrix` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-raider` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-raptors` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-raptors` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-raveners` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-ravenwing-command-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-razorback` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-razorback-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-razorback-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-razorback-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-razorback-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-razorback-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-razorback-7` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-reaver-titan` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-reavers` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-reavers` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-red-corsairs-raiders` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-red-corsairs-raiders` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-redemptor-dreadnought` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-redemptor-dreadnought-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-redemptor-dreadnought-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-redemptor-dreadnought-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-redemptor-dreadnought-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-redemptor-dreadnought-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-reductus-saboteur` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-rendmaster-on-blood-throne` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-repulsor` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-repulsor-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-repulsor-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-repulsor-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-repulsor-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-repulsor-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-repulsor-executioner` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-repulsor-executioner-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-repulsor-executioner-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-repulsor-executioner-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-repulsor-executioner-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-repulsor-executioner-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-repulsor-executioner-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-repulsor-executioner-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-repulsor-executioner-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-repulsor-executioner-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-retributor-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-revenant-titan` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-rhino` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-rhino-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-rhino-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-rhino-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-rhino-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-rhino-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-rhino-7` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-riptide-battlesuit` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-rogal-dorn-battle-tank` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-rogal-dorn-commander` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-rogue-trader-entourage` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-rubric-marines` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-rubric-marines` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-sagitaur` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-sanguinary-guard` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-sanguinary-guard` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-sanguinary-priest` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-scarab-occult-terminators` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-scarab-occult-terminators` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-scourges-with-heavy-weapons` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-scourges-with-shardcarbines` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-scout-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-scout-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-scout-squad-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-scout-squad-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-scout-squad-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-scout-squad-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-scout-squad-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-scout-squad-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-scout-squad-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-scout-squad-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-screamer-killer` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-sekhetar-robots` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-sekhetar-robots` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-seraphim-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-seraphim-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-seraptek-heavy-construct` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-shadowsword` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-sicarian-infiltrators` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-sicarian-infiltrators` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-sicarian-ruststalkers` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-sicarian-ruststalkers` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-sisters-of-battle-immolator` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-sisters-of-battle-immolator` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-sisters-of-battle-immolator` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-sisters-of-battle-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-skorpekh-destroyers` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-skorpekh-destroyers` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-skorpekh-lord` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-skorpius-dunerider` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-sorcerer-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-sorcerer-in-terminator-armour-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-sororitas-rhino` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-soul-grinder` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-spectrus-kill-team` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-starweaver` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-stealth-battlesuits` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-stompa` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-storm-speeder-hailstrike` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-storm-speeder-hailstrike-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-storm-speeder-hailstrike-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-storm-speeder-hailstrike-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-storm-speeder-hailstrike-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-storm-speeder-hailstrike-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-storm-speeder-hammerstrike` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-storm-speeder-hammerstrike-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-storm-speeder-hammerstrike-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-storm-speeder-hammerstrike-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-storm-speeder-hammerstrike-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-storm-speeder-hammerstrike-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-storm-speeder-thunderstrike` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-storm-speeder-thunderstrike-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-storm-speeder-thunderstrike-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-storm-speeder-thunderstrike-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-storm-speeder-thunderstrike-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-storm-speeder-thunderstrike-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-stormlord` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-stormraven-gunship` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-stormraven-gunship-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-stormraven-gunship-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-stormraven-gunship-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-stormraven-gunship-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-stormraven-gunship-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-stormraven-gunship-7` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-stormsurge` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-stormsword` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-subductor-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-swooping-hawks` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-swooping-hawks` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-sword-brethren-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-sword-brethren-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-sword-brethren-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-sword-brethren-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-talonstrike-kill-team` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-talos` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-talos` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-tankbustas` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-taunar-supremacy-armour` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-taurox` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-taurox-prime` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-technomancer` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-telemon-heavy-dreadnought` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-tempestus-scions` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-tempestus-scions` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-tesseract-vault` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-thunderwolf-cavalry` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-thunderwolf-cavalry` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-tiger-shark` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-tomb-blades` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-tomb-blades` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-transcendent-ctan` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-triarch-stalker` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-trukk` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-tyrannocyte` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-tyrannofex` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-valkyrie` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-vanguard-veteran-squad-with-jump-packs` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-vanguard-veteran-squad-with-jump-packs` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-vanguard-veteran-squad-with-jump-packs-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-vanguard-veteran-squad-with-jump-packs-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-vanguard-veteran-squad-with-jump-packs-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-vanguard-veteran-squad-with-jump-packs-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-vanguard-veteran-squad-with-jump-packs-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-vanguard-veteran-squad-with-jump-packs-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-vanguard-veteran-squad-with-jump-packs-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-vanguard-veteran-squad-with-jump-packs-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-vanguard-veteran-squad-with-jump-packs-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-vanguard-veteran-squad-with-jump-packs-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-vanguard-veteran-squad-with-jump-packs-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-vanguard-veteran-squad-with-jump-packs-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-venatari-custodians` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-venatari-custodians` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-venerable-contemptor-dreadnought` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-venerable-dreadnought` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-venerable-dreadnought-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-venerable-land-raider` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-venom` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-venomcrawler` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-victrix-honour-guard` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-victrix-honour-guard` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-vindicare-assassin` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-vindicator` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-vindicator-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-vindicator-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-vindicator-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-vindicator-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-vindicator-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-voidsmen-at-arms` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-war-dog-moirax` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-warbringer-nemesis-titan` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-warhound-titan` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-warlord-titan` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-warp-spiders` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-warp-spiders` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-warp-talons` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-warp-talons` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-wave-serpent` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-whirlwind` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-whirlwind-2` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-whirlwind-3` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-whirlwind-4` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-whirlwind-5` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-whirlwind-6` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-wolf-guard-headtakers` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-wolf-guard-headtakers` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-wolf-guard-headtakers` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-wolf-guard-headtakers` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-wolf-guard-headtakers` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-wolf-guard-terminators` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-wolf-guard-terminators` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-wraithknight` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-wraithknight-with-ghostglaive` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-wulfen` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-wulfen` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-wulfen-dreadnought` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-wulfen-with-storm-shields` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-wulfen-with-storm-shields` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-wyvern` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-ynnari-incubi` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-ynnari-incubi` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-ynnari-raider` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-ynnari-venom` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-zephyrim-squad` | — |
| `REC-VALUE-CONFLICT` | advisory | `ds-zephyrim-squad` | — |

</details>

<details><summary>summary (1348)</summary>

| code | severity | entities | resolved |
|---|---|---|---|
| `GLS-OUTSTANDING` | advisory | `glossary:abaddon the despoiler` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:aberrants` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:abhorrent` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:abominant` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:acanthrites` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:acastus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:accursed cultists` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:achilles ridgerunners` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:acolyte hybrids` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:acolyte hybrids with autopistols` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:acolyte hybrids with hand flamers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:acolyte iconward` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:adeptus arbites` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:adeptus astartes` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:adeptus titanicus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:adrax agatone` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:aegis defence line` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:aestred thurga` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:aetaos rau keres` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:aethon shaan` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:agamatus custodians` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:agathae dolan` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:agents of the imperium` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:aggressor squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ahriman` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:aleya` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:allarus custodians` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:amallyn shadowguide` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:an ggrath the unbound` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:anathema psykana` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ancient` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:angron` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:anhrathe` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:annihilation barge` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:anrakyr the traveller` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:anti monster vehicle` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:anti non monster vehicle` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:apothecary` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:aquila kill team` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:aquila lander` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:aquilon custodians` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:archaeopter fusilave` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:archaeopter stratoraptor` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:archaeopter transvector` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:archon` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:arco flagellants` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ares gunship` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:arjac rockfist` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:arkanyst evaluator` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:arkurian stormhammer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:armageddon pattern medusa` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:armiger` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:armoured sentinels` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:artillery` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:artillery team` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:arvus lighter` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:asmodai` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:aspect warrior` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:aspect warriors` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:assault intercessor squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:assault intercessors with jump packs` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:assault squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:assault squad with jump packs` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:astartes servitors` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:astorath` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:astraeus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:asurmen` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:asuryani` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:atalan jackals` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:atlas recovery vehicle` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:attack bike squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:attack fighta` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:attilan rough riders` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:aun shi` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:aun va` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:autarch` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:autarch skyrunner` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:autarch wayleaper` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:avatar of khaine` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:avenger strike fighter` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ax 1 0 tiger shark` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:azrael` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:baal predator` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:baharroth` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ballistus dreadnought` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:baneblade` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:banehammer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:banesword` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:bannernob` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:barbed hierodule` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:barbgaunts` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:barracuda` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:basilisk` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:battle leader` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:battle sanctum` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:battle sisters squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:battlesuit` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:battlewagon` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:be lakor` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:beast snagga` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:beast snagga boyz` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:beastboss` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:beastboss on squigosaur` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:beastmaster` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:beasts of nurgle` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:belial` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:belisarius cawl` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:bellatus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:benefictus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:berehk stornbröw` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:berzerkers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:beserks` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:big ed bossbunka` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:big gunz` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:big mek` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:big mek in mega armour` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:big mek on warbike` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:big mek with kustom force field` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:big mek with shokk attack gun` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:big trakk` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:bigboss` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:bike squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:biologis` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:biologus putrifier` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:biophagus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:biovores` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:bjorn the fell handed` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:blade champion` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:bladeguard ancient` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:bladeguard veteran squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:blades for hire` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:blightlord terminators` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:blitza bommer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:blood claws` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:blood legions` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:blood slaughterer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:bloodcrushers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:bloodletters` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:bloodmaster` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:bloodthirster` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:blue` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:bodyguard` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:bonesinger` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:boomdakka snazzwagon` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:boss snikrot` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:boss zagstruk` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:boyz` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:breacher team` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:breachers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:breaka boyz` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:brigand` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:brimstone` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:broadside` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:broodlord` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:brother captain` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:brother captain stern` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:brother corbulo` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:brotherhood champion` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:brotherhood chaplain` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:brotherhood librarian` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:brotherhood techmarine` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:brotherhood terminator squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:brutalis dreadnought` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:brôkhyr` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:bullgryn squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:buri aegnirssen` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:burna bommer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:burna boyz` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:burning chariot` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:burrower` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:burrowers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:c tan shard of the deceiver` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:c tan shard of the nightbringer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:c tan shard of the void dragon` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:caanok var` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:cadian` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:cadian castellan` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:cadian heavy weapons squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:cadian recon squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:cadian shock troops` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:cadre fireblade` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:caestus assault ram` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:caladius grav tank` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:callidus assassin` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:canis rex` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:canis wolfborn` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:canoness` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:canoptek` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:captain` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:carab culln the risen` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:carnifexes` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:carnivores` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:carnodon` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:carrier` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:castellan` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:castellan crowe` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:castigator` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:catachan` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:catachan heavy weapons squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:catachan jungle fighters` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:catacomb command barge` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:cato` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:celestian insidiants` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:celestian sacresant aveline` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:celestian sacresants` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:centaur light carrier` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:centaur rsv` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:centurion` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:centurion assault squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:centurion devastator squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:cerastus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:cerberus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:champion` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:changecaster` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:chaos` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:chaos bikers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:chaos lord` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:chaos lord in terminator armour` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:chaos lord on bike` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:chaos spawn` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:chaos terminator squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:chaos undivided` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:chaplain` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:chaplain cassius` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:chaplain grimaldus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:chaplain venerable dreadnought` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:chapter master` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:chief librarian mephiston` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:chief librarian tigurius` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:chimera` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:chinork warkopta` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:chosen` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:chronomancer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:clamavus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:cobra` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:colossus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:command squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:commander dante` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:commander farsight` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:commander in coldstar battlesuit` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:commander in crisis battlesuit` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:commander in enforcer battlesuit` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:commander shadowsun` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:commissar` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:commissar graves` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:commissar graves on foot` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:commissar yarrick` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:company champion` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:company heroes` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:company veterans` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:contemptor achillus dreadnought` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:contemptor galatus dreadnought` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:contorted epitome` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:convergence of dominion` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:coronus grav carrier` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:corpuscarii` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:corsair cloud dancer band` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:corsair reaver band` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:corsair skyreavers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:corsair voidreavers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:corsair voidscarred` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:corvus blackstar` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:coteaz` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:court of the archon` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:crassus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:crimson hunter` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:crisis` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:cronos` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:crusade ancient` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:crusader` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:crusader squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:crusaders` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:cryptek` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:cryptothralls` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:cthonian` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:culexus assassin` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:cult demagogue` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:cult mechanicus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:cultist firebrand` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:cultist mob` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:cultist mob with firearms` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:cultists` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:custodian guard` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:custodian guard with adrasite and pyrithite spears` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:custodian wardens` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:cybernetica datasmith` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:cyberwolf` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:cyclops demolition vehicle` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:cypher` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:d cannon platform` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:da red gobbo` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:daemon` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:daemon prince` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:daemon prince of chaos` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:daemon prince of chaos with wings` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:daemon prince with wings` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:daemonettes` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:daemonhost` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:daemonifuge` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:dakkajet` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:dakkarig` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:damned` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:damned legionnaires` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:dark apostle` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:dark commune` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:dark reapers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:dark talon` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:darkstrider` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:darnath lysander` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:dawneagle jetbike` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:death company` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:death company dreadnought` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:death company marines` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:death company marines with bolt rifles` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:death company marines with boltguns` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:death company marines with boltguns and jump packs` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:death company marines with jump packs` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:death cult assassins` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:death jester` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:death korps grenadier squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:death korps of krieg` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:death rider commissar` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:death riders` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:deathleaper` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:deathmarks` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:deathshroud terminators` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:deathstorm drop pod` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:deathstrike` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:deathwatch terminator squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:deathwatch veterans` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:deathwing` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:deathwing command squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:deathwing knights` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:deathwing strikemaster` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:deathwing terminator squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:decimator` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:decimus kill team` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:defenders` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:deff dread` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:deff rolla battle fortress` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:deffkilla wartrike` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:deffkoptas` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:deffkoptas with big shootas` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:defiler` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:deimos predator` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:deredeo dreadnought` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:desolation squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:destroyer cult` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:destroyers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:devastating wounds non monster vehicle` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:devastator squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:devilfish` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:dialogus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:dimachaeron` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:dire avengers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:disc of tzeentch` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:dogmata` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:dominion squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:dominus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:dominus armoured siege bombard` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:doom scythe` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:doomhammer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:doomsday ark` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:doomstalker` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:dragoons with radium jezzails` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:dragoons with taser lances` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:draxus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:drazhar` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:dreadclaw drop pod` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:dreadnought` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:dreadnought drop pod` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:drone sentry turret` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:drop pod` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:earthshaker carriage battery` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:earthshaker platform` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:earthshakers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:eightbound` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:einhyr champion` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:einhyr hearthguard` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:eisenhorn` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:eldrad ulthran` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:electro priests` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:eliminator squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:elysian drop sentinel` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:elysian sniper squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:emperor s champion` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:endless multitude` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:enginseer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:epidemius` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:eradicator squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:eradicator squad with heavy bolters` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ethereal` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:eversor assassin` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:exaction squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:exalted champion` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:exalted eightbound` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:exalted flamer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:exalted sorcerer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:execrator` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:executioner` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:exoarmour` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:exocrine` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:exodite` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:exoframe` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:exorcist` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:exterminators` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ezekiel` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:fabius bile` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:falchion` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:falcon` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:fallen` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:farseer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:farseer skyrunner` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:farstalkers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:fateskimmer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:feculent gnarlmaw` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:fellblade` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:fellgor beastmen` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:fenrisian wolves` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ferren areios` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:field ordnance battery` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:fiends` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:fighta bommer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:fire dragons` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:fire prism` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:fire raptor gunship` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:fire warrior` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:fireknife` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:firesight team` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:firestorm` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:firestrike servo turrets` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:flamers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:flash gitz` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:flawless blades` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:flayed ones` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:flesh hounds` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:flesh shaper` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:fluxmaster` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:foetid bloat drone` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:foetid bloat drone with heavy blight launcher` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:forgefiend` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:fortis kill team` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:foul blightspawn` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:frame` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:fuegan` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:fulgrim` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:fulgurite` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:furies` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:furioso dreadnought` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:fusiliers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:gabriel seth` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:gargantuan squiggoth` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:gargoyles` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:gaunt s ghosts` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:gauss pylon` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:gellerpox infected` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:genestealers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:geomancer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ghazghkull thraka` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ghost ark` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ghostkeel` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:giant chaos spawn` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:gladiator lancer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:gladiator reaper` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:gladiator valiant` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:goliath rockgrinder` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:goliath truck` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:goremongers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:gorgon heavy transport` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:gorkanaut` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:grand master` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:grand master in nemesis dreadknight` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:grand master voldus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:gravis` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:great devourer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:great knarloc` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:great unclean one` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:greater blight drone` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:greater brass scorpion` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:gretchin` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:grey hunters` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:grey knights terminator squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:greyfax` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:griffon mortar carrier` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:grimnyr` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:grot bomm launcha` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:grot mega tank` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:grot tanks` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:grotesques` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:grots` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:guardian defenders` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:guardians` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:haarken worldclaimer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:hades breaching drill` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:haemonculus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:haemonculus covens` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:hammerfall bunker` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:hammerhead gunship` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:hand of the archon` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:harald deathwolf` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:harlequins` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:harpy` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:harridan` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:haruspex` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:harvester` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:hastarii` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:havocs` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:headtakers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:hearthkyn warriors` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:heavy gun drones` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:heavy intercessor squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:heavy mortar team` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:heavy quad launcher team` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:hekaton land fortress` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:helbrute` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:heldrake` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:hell blade` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:hell s last` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:hell talon` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:hellblaster squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:hellflayer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:hellflayers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:hellhammer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:hellhound` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:hellions` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:helverin` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:hemlock wraithfighter` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:herald of slaanesh` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:heretic astartes` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:hernkyn` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:hexmark destroyer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:hierophant` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:high marshal helbrecht` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:hippogriff afv` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:hive crone` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:hive guard` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:hive tyrant` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:hormagaunts` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:hornet` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:horrors` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:horticulous slimux` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:hospitaller` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:hounds` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:hounds of morkai` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:howling banshees` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:hunta rig` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:hunter` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:hunting wolves` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:huntsman` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:huron blackheart` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:hybrid metamorphs` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:hydra` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:hydra platform` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:hyperadapted raveners` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:icon bearer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:illic nightspear` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:illuminor szeras` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:imagifier` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:immolator` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:immortals` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:imotekh the stormlord` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:imperial fists` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:imperial navy breachers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:imperial rhino` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:imperial space marine` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:imperium` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:impulsor` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:inceptor squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:incubi` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:incursor squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:indomitor kill team` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:infernal enrapturess` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:infernal master` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:infernus squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:infiltrator squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:infiltrators` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:infractors` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:inner circle companions` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:inquisitor` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:inquisitor ostromandeus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:inquisitorial agents` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:inquisitorial chimera` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:interceptor squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:intercessor squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:intranzia fraye` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:invader atv` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:invictor tactical warsuit` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:irillyth` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:iron father feirros` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:iron hand straken` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:iron hands` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:iron master` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:iron priest` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ironclad dreadnought` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ironkin steeljacks` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ironkin steeljacks with heavy volkanite disintegrators` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ironkin steeljacks with melee weapons` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ironstrider ballistarii` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:jackal alphus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:jain zar` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:jakhals` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:janus draik` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:javelin attack speeder` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:jokaero weaponsmith` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:judiciar` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:juggernaut` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:jump pack` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:jump packs` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:junith eruita` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:kabal` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:kabalite warriors` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:kairos fateweaver` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:kaldor draigo` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:kannonwagon` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:kapricus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:kaptin badrukk` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:karamazov` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:karanak` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:karandras` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:karnivore` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:kasrkin` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:kastelan robots` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:kataphron` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:kayvaan shrike` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:keeper of secrets` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:kelermorph` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:kharseth` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:kharybdis assault claw` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:khorne` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:khârn the betrayer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:kill krusha` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:kill rig` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:kill tank` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:kill team` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:kill team cassius` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:killa kans` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:knarloc riders` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:knight abominant` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:knight acheron` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:knight asterius` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:knight atrapos` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:knight castellan` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:knight castigator` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:knight centura` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:knight crusader` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:knight defender` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:knight desecrator` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:knight despoiler` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:knight destrier` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:knight errant` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:knight gallant` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:knight lancer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:knight magaera` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:knight paladin` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:knight porphyrion` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:knight preceptor` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:knight rampager` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:knight ruinator` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:knight styrix` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:knight tyrant` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:knight valiant` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:knight warden` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:kommandos` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:kor sarro khan` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:kratos` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:kravek morne` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:krieg` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:krieg combat engineers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:krieg heavy weapons squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:krom dragongaze` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:kroot` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:krootox rampagers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:krootox riders` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:kroyle` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:kustom boosta blasta` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:kytan ravager` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:kâhl` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:lady malys` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:land raider` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:land raider achilles` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:land raider crusader` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:land raider excelsior` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:land raider helios` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:land raider prometheus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:land raider proteus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:land raider redeemer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:land speeder` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:land speeder storm` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:land speeder tempest` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:land speeder tornado` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:land speeder typhoon` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:land speeder vengeance` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:lazarus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:legio cybernetica` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:legionaries` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:legiones daemonica` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:legions of excess` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:lelith hesperax` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:leman russ battle tank` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:leman russ commander` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:leman russ demolisher` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:leman russ eradicator` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:leman russ executioner` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:leman russ exterminator` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:leman russ punisher` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:leman russ vanquisher` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:lemartes` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:leviathan dreadnought` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:lhykhis` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:librarian` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:librarian dreadnought` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:lictor` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:lieutenant` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:lieutenant in reiver armour` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:lieutenant with combi weapon` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:lifta wagon` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:lion el jonson` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:locus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:logan grimnar` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:logan grimnar on stormrider` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:lokhust destroyers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:lokhust heavy destroyers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:lokhust lord` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:lone spear` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:long fangs` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:longstrike` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:lootas` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:lord` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:lord discordant` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:lord exultant` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:lord invocatus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:lord kakophonist` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:lord marshal dreir` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:lord of change` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:lord of contagion` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:lord of poxes` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:lord of skulls` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:lord of virulence` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:lord on juggernaut` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:lord solar leontus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:loyal protector` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:lucius the eternal` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:lukas the trickster` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:lychguard` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:lynx` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:macharius` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:macharius omega` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:macharius vanquisher` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:macharius vulcan` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:macrocytes` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:mad dok grotsnik` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:magnus the red` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:magus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:malanthrope` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:malcador` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:malcador annihilator` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:malcador defender` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:malcador infernus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:maleceptor` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:malignant plaguecaster` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:mandrakes` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:manipulus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:manta` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:manticore` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:manticore platform` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:marauder bomber` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:marauder destroyer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:markerlight` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:marneus calgar` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:marshal` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:master of executions` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:master of possession` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:masters of the maelstrom` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:mastodon` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:maugan ra` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:maulerfiend` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:mawloc` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:medusa carriage battery` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:mega armour` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:mega dread` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:meganobz` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:megatrakk scrapjet` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:mek` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:mek gunz` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:meka dread` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:mekboy workshop` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:memnyr strategist` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:miasmic malignifier` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:militarum tempestus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ministorum priest` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:minotaur` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:mob` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:mobile` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:moirax` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:monolith` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:morkanaut` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:mortarion` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:mortifiers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:mortis dreadnought` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:morvenn vahl` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:mounted` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:mozrog skragbad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:mucolid spores` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:mukaali riders` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:munitorum servitors` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:murderfang` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:mutalith vortex beast` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:mutant` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:mutilators` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:mutoid vermin` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:myphitic blight hauler` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:navigator` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:necron warriors` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:negavolt cultists` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:nekrosor ammentar` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:nemesis claw` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:nemesis dreadknight` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:nemesor zahndrekh` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:neophyte hybrids` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:nephilim jetfighter` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:neurogaunts` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:neurolictor` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:neurotyrant` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:nexos` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:neyam shai murad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:night scythe` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:night shroud` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:night spinner` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:nightwing` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:njal stormcaller` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:noble` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:nobz` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:nobz on warbikes` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:noctilith crown` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:noise marines` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:nork deddog` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:norn assimilator` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:norn emissary` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:noxious blightbringer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:nurgle` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:nurglings` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:obelisk` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:obliterators` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:officer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:officio assassinorum` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ogryn` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ogryn squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:old one eye` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:onager dunecrawler` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ophydian destroyers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:orca dropship` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ordo hereticus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ordo malleus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ordo xenos` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:orikan the diviner` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:orion assault dropship` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:outrider squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:overlord` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:overlord with translocation shroud` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:pack leader` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:painboss` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:painboy` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:painboy on warbike` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:paladin squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:palanquin of nurgle` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:palatine` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:pallas grav attack` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:paragon warsuits` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:parasite of mortrex` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:pathfinder team` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:patriarch` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:pedro kantor` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:penitent` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:penitent engines` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:phantom titan` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:phobos` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:phoenix` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:phoenix lord` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:pink` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:pioneers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:piranhas` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:plague drones` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:plague legions` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:plague marines` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:plague surgeon` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:plague toads` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:plaguebearers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:plagueburst crawler` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:plasmancer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:platoon` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:possessed` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:pox riders` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:poxbringer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:poxwalkers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:praetor` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:praetorians` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:predator annihilator` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:predator destructor` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:primarch` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:primaris company champion` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:primaris psyker` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:primus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:prince yriel` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:prosecutors` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:proteus kill team` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:provisionally prepared` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:psychomancer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:psychophage` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:pteraxii` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:purestrain genestealers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:purgation squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:purifier squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:pyrovores` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:quartermaster cadre squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:questoris` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:r varna` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ragnar blackmane` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:raider` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:rangers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:rapier carrier` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:rapier laser destroyer battery` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:raptors` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ratlings` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ravager` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:raven guard` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:raven strike fighter` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:raveners` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ravenwing` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ravenwing black knights` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ravenwing command squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ravenwing darkshroud` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ravenwing talonmaster` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:razorback` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:razorshark strike fighter` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:razorwing jetfighter` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:reanimator` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:reaper` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:reaver titan` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:reavers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:red corsairs raiders` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:red corsairs reave captain` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:redeemer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:redemptor dreadnought` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:reductus saboteur` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:regiment` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:regimental attachés` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:rein and raus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:reiver squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:relic contemptor dreadnought` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:relic razorback` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:relic terminator squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:remora stealth drones` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:remote sensor tower` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:rendmaster on blood throne` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:renegade enforcer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:renegade heavy weapons squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:renegade ogryn beast handler` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:renegade ogryn brutes` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:renegade plague ogryns` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:repentia squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:repressor` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:repulsor` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:repulsor executioner` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:requisitioned` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:retinue` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:retributor squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:revenant titan` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:rhino` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:rhino primaris` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ripper swarms` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:riptide` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:roboute guilliman` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:rogal dorn battle tank` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:rogal dorn commander` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:rogue psyker` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:rogue trader entourage` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:rotigus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:royal warden` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:rubric marines` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:rubricae` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:rukkatrukk squigbuggy` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ruststalkers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sabre weapons battery` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sagitaur` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sagittarum custodians` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:saint celestine` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:salamander command vehicle` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:salamander scout vehicle` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:salamanders` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sammael` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sanctifiers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sanctus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sanguinary guard` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sanguinary priest` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:scabeiathrax the bloated` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:scarab occult` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:scarab swarms` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:scintillating legions` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:scorpion` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:scourges` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:scourges with heavy weapons` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:scourges with shardcarbines` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:scout bike squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:scout sentinels` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:scout sniper squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:scout squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:screamer killer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:screamers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:scythed hierodule` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:secutarii hoplites` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:secutarii peltasts` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:seekers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sekhetar robots` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sentinel powerlifter` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sentry pylon` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:seraphim squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:seraptek heavy construct` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:serberys raiders` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:serberys sulphurhounds` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sergeant chronus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sergeant harker` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sergeant telion` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:servitor battleclade` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:servitors` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:shadow legion` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:shadow spectres` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:shadow weaver platform` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:shadowseer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:shadowsword` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:shalaxi helbane` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:shaper` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:shas o r alai` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:shield captain` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:shining spears` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:shokkjump dragsta` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:shroud runners` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sicaran arcus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sicaran battle tank` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sicaran omega` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sicaran punisher` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sicaran venator` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sicarian` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sicarius` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sisters novitiate squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sisters of battle squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:skarbrand` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:skathach wraithknight` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:skatros` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:skitarii` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:skorchas` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:skorpekh destroyers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:skorpekh lord` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:skorpius disintegrator` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:skorpius dunerider` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:skull altar` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:skull cannon` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:skullmaster` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:skulltaker` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sky ray gunship` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sky slasher swarms` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:skyclaws` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:skystalkers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:skyweavers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:slaanesh` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:slaughterbound` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sloppity bilepiper` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sly marbo` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sokar pattern stormbird` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:solitaire` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sorcerer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sorcerer in terminator armour` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sorcerer on bike` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sororitas rhino` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:soul grinder` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:spartan` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:spawn` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:spectrus kill team` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:speed freeks` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:spined chaos beast` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:spiritseer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:spoilpox scrivener` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:spore mines` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sporocyst` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:spyders` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:squadron` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:squiggoth` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:squighog boyz` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:stalker` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:starfangs` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:starscythe` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:starweaver` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:stealth` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:steed of slaanesh` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sternguard veteran squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sterylizors` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:stompa` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:storm chimera` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:storm eagle gunship` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:storm guardians` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:storm speeder hailstrike` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:storm speeder hammerstrike` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:storm speeder thunderstrike` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:stormblade` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:stormboyz` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:stormfang gunship` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:stormhawk interceptor` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:stormlord` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:stormraven gunship` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:stormsurge` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:stormsword` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:stormtalon gunship` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:stormwolf` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:strike squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:strike team` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:striking scorpions` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:stygies destroyer tank hunter` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:subductor squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:suboden khan` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:succubus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:summoned` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sun shark bomber` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sunforge` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:support weapon` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:suppressor squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:swooping hawks` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sword brethren squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:sydonian` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:syll esske` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:synapse` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ta unar supremacy armour` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tactical squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tacticus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tallyman` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:talonstrike kill team` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:talos` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tankbustas` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tantalus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tarantula air defence battery` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tarantula battery` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tarantula sentry battery` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tauros` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tauros assault vehicle` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tauros venator` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:taurox` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:taurox prime` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tech priest` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tech priest enginseer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:techmarine` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:technoarcheologist` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:technomancer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tectonic fragdrill` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:telemon heavy dreadnought` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tempestus aquilons` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tempestus scions` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:termagants` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:terminator` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:terminator assault squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:terminator squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:terminators` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:terminus ultra` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:terrax pattern termite` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tervigon` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tesseract ark` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tesseract vault` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tetras` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:the blue scribes` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:the changeling` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:the masque of slaanesh` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:the red terror` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:the sanguinor` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:the silent king` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:the swarmlord` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:the twin lance` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:the visarch` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:the yncarne` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:thulia ghuld` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:thunderfire cannon` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:thunderhawk` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:thunderhawk gunship` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:thunderhawk transporter` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:thunderkyn` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:thunderwolf cavalry` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tidewall droneport` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tidewall gunrig` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tidewall shieldline` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tiger shark` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:titus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tomb blades` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tomb citadel` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tomb crawlers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tomb sentinel` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tomb stalker` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tor garadon` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tormentbringer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tormentors` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:toxicrene` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:trail shaper` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:traitor enforcer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:traitor guardsmen squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:trajann valoris` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tranceweaver` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:transcendent c tan` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:trazyn the infinite` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:triarch` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:triumph of saint katherine` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:trojan support vehicle` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:troupe` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:troupe master` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:trukk` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:trygon` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tx42 piranha` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tycho` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tycho the lost` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:typhon` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:typhus` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tyranid prime with lash whip` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tyranid warriors with melee bio weapons` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tyranid warriors with ranged bio weapons` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tyrannic war veterans` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tyrannocyte` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tyrannofex` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tyrant guard` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tzaangor enlightened` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tzaangor enlightened with fatecaster greatbows` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tzaangor shaman` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tzaangors` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:tzeentch` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ufthak blackhawk` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ulrik the slayer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ultramarines` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:undivided` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ur` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:uriel ventris` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:urien rakarth` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ursula creed` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:valdor` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:valerian` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:valkyrie` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:valkyrie sky talon` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:vampire hunter` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:vampire raider` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:vanguard` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:vanguard invader` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:vanguard veteran squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:vanguard veteran squad with jump packs` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:vargard obyron` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:vashtorr the arkifane` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:venatari custodians` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:vendetta gunship` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:venerable` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:venerable contemptor dreadnought` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:venerable dreadnought` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:venerable land raider` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:venom` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:venomcrawler` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:venomthropes` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:vertus praetors` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:vespid stingwings` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:veteran bike squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:vibro cannon platform` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:victrix honour guard` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:vigilant squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:vigilators` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:vindicare assassin` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:vindicator` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:vindicator laser destroyer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:voidfarers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:voidraven bomber` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:voidsmen at arms` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:voidweaver` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:von ryan s leapers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:voss pattern lightning` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:vulkan he stan` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:vulture gunship` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:vypers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:war dog` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:war shaper` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:war walkers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:warbikers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:warboss` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:warboss in mega armour` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:warbringer nemesis titan` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:warbuggies` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:wardens of ultramar` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:warglaive` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:warhound titan` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:warlock` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:warlock conclave` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:warlock skyrunners` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:warlocks` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:warlord titan` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:warp hunter` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:warp spiders` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:warp talons` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:warpsmith` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:wartrakk` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:wasp assault walker` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:watch captain artemis` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:watch master` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:wave serpent` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:wazbom blastajet` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:wazdakka gutsmek` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:webway gate` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:weirdboy` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:whirlwind` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:whirlwind scorpius` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:white scars` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:windriders` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:winged hive tyrant` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:winged tyranid prime` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:witchseekers` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:wolf guard` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:wolf guard battle leader in terminator armour` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:wolf guard battle leader on thunderwolf` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:wolf guard pack leader` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:wolf guard pack leader in terminator armour` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:wolf guard pack leader with jump pack` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:wolf guard terminators` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:wolf lord on thunderwolf` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:wolf priest` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:wolf scouts` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:wracks` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:wraith construct` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:wraithblades` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:wraithguard` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:wraithknight` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:wraithknight with ghostglaive` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:wraithlord` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:wraiths` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:wraithseer` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:wulfen` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:wulfen with storm shields` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:wurrboy` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:wych cult` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:wyches` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:wyvern` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:x` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:xiphon interceptor` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:xv9 hazard` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:y vahra` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:yaegirs` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ynnari` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:yvraine` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:zarakynel` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:zephyrim squad` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:zoanthropes` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:zodgrod wortsnagga` | — |
| `GLS-OUTSTANDING` | advisory | `glossary:ûthar the destined` | — |

</details>

## Sub-reports

- [change_summary](change-summary.md)
- [edition_mismatch](edition-mismatch.md)
- [summary_coverage](summary-coverage.md)
- [trends](trends.md)
- [unverified_pricing](unverified-pricing.md)
