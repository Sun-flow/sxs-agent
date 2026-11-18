# Stamina and Material Realms plan

<!-- index: Read to decide what stamina is spent on today and whether Material Realm tools are used or saved -->

> **Summary:** stamina (5 an hour, 300 passive cap) and Material Realm attempts are the two daily taps for upgrade
> materials. What both pay grows steeply with Kingdom Rank (about 28 times from the lowest to the highest band). Commissions come first for stamina; the rest follows the season phase: Chrono Sand at the start of a
> season, ore from the middle to the end. Free realm attempts are used daily; bought and stored tools are worth
> saving until the kingdom's top rank, unless a dungeon threshold is at risk.
> **Applies:** all seasons
> **Related:** [Stamina](../systems/stamina.md), [Material Realms](../systems/material-realms.md),
> [Kingdom Rank](../systems/kingdom-rank.md), [Dawnium plan](dawnium-plan.md), rules R-107, R-108

## Stamina: the order

| Priority | Use | Condition | Source |
|---|---|---|---|
| 1 | Keep a reserve of 70 for the day's commissions | always | [R-107] |
| 2 | Commissions that cost stamina, Premium ones first | always: "complete commissions aggressively" | [S-01] |
| 3 | The material the next upgrade is short of, when a dungeon or zone threshold is within reach | threshold at risk | [S-01] |
| 4 | Chrono Sand | season start, until relic resonance is at the season cap | [S-01][S-02] |
| 5 | Ore | mid-season to the end | [S-01][S-02] |
| 6 | Battle Essence | when skills lag the character level | [R-106] |
| 7 | Rolla | only when Rolla blocks an upgrade | [R-108] |

- Never let stamina sit at the cap: above 150 spending is a side objective every day (mae).
- Before a season change, bank up to 300 [S-02].
- One stamina is valued at 4.8 Dawnium by eog [S-85]: a full 300 bar is about 1,440 Dawnium of materials, so a
  capped bar is the most expensive waste in the daily routine.
- In the first season of an account (below Lv 100) "season start" means the first weeks: relics are not unlocked
  at the very beginning, so ore comes first until the Workbench opens ❓ (our reading).

## Material Realms: use or save

| Situation | Free daily attempts | Bought or stored tools | Source |
|---|---|---|---|
| A zone or dungeon threshold is within reach and needs the materials | Use | Use | [S-01] |
| Below the kingdom's top rank, no threshold pressure | Use the Rolla realm (10 runs cover the daily quest, "0/10/0/0") | Save in the bag | [S-01][S-02][S-03] |
| At the top rank (Champion III at Lv 120 in Season 2) | Use all | Use the stockpile | [S-02] |
| Just before a season rollover | Use | Keep: the new kingdom's ranks pay more | [S-02][S-85] |
| Last two weeks of a season | Use all, ore | Use all, ore | [S-01] |

Which realm gets extra tools: sand at the start of a season, ore from the middle; the standard splits are 4244
and 4444 (ore / Rolla / essence / sand) [S-01]. eog calls 2222 the free-player split and 4244 a mid-spender one
[S-85]; this page keeps SOF's 4244 as the target and 2222 as the floor. Vault tool bundles are cheaper than tools
bought at the realm [R-120].

## What a run pays, by rank

The publisher confirms that Material Realm rewards scale with Kingdom Rank [S-87]. eog's stamina calculator gives
the size [S-85] (data: [gathering-yields.json](../data/gathering-yields.json)):

| Rank band (eog's names) | Rolla per 5 stamina, three sub-ranks | Realm reward multiplier |
|---|---|---|
| Black Iron | 1,920 / 2,520 / 3,180 | 1.6 to 2.65 |
| Bronze | 4,020 / 4,980 / 5,940 | 3.35 to 4.95 |
| Silver | 6,900 / 7,980 / 9,240 | 5.75 to 7.7 |
| Gold | 12,000 / 12,960 / 14,160 | 10 to 11.8 |
| Sanctuary | 22,800 / 23,400 / 24,000 | 19 to 20 |
| Legend | 48,000 / 51,000 / 54,000 | 40 to 45 |

- The same 5 stamina gives Raw Ore at one tenth of the Rolla figure, Battle Essence at one eighth, Chrono Sand at
  one twelfth [S-85].
- A "big mine" pays double: 5% chance, guaranteed within 75 attempts [S-85].
- What this means: the jump between bands (Silver to Gold +30%, Gold to Sanctuary +61%, Sanctuary to Legend
  +100%) is far larger than the steps inside a band. Saving bought tools pays when the next **band** is close;
  inside a band, waiting gains little. This sharpens the SOF advice, it does not replace it.
- ❓ How eog's band names map onto the in-game rank names (Apprentice I to III ... Champion I to III) is not
  stated.

For an account below Lv 100 the saving trick matters less: ranks pass quickly and every level is permanent. Our
default: use free attempts daily, save bought tools only when the next rank is less than a week away ❓ (our
judgement; the official tip only says to save "unless materials are needed immediately" [S-03]).

## Open questions

- ❓ Which in-game rank is which eog band (the yield table above is keyed by eog's names).
- ❓ The sand realm is the Sand Mine with the Sand Shovel per eog [S-85]; in-game spelling and free attempts per
  realm per day are not yet read.

## Sources

- [S-01] Material Realms, permanent vs seasonal tips; [S-02] sections IV and VI; [S-03] Material Realm tip;
  [S-85] stamina calculator, splits, item values; [S-87] official handbook (rank scaling)
- Rules R-106, R-107, R-108, R-120
