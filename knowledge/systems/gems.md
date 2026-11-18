# Gems

<!-- index: Read before socketing, combining, buying or selling gems, or deciding how much to invest in them -->

> **Summary:** Gems are socketed into gear for flat percentage stats: one socket per piece in Season 1, two in
> Season 2 (10 gems). Eight colours, each allowed only in certain slots. They are a quick early boost that falls
> behind as the season goes on, so do not invest heavily: socket what drops, sell black and white gems to
> spenders, build combine pity with cheap gems, and buy only after the market price crashes.
> **Applies:** late Season 1 onward; main sources open in Season 2 (Loong Haven)
> **Related:** [Gear](gear.md), [Towers](towers.md), [Auction House](auction-house.md),
> [Astral Pact](astral-pact.md), [Seasons](seasons.md), data in [gems.json](../data/gems.json)

## Colours, stats and slots

| Colour | Name | Stats | Kind | Weapon | Offhand | Helmet | Armor | Boots |
|---|---|---|---|---|---|---|---|---|
| Red | Ruby [S-52] | ATK% | normal | yes | yes | - | - | yes |
| Purple | Amethyst [S-85] | SPD% + Crit Rate | normal | yes | yes | - | - | yes |
| Yellow | Citrine [S-85] | SPD% | normal | - | yes | yes | - | yes |
| Green | Beryl [S-52][S-85] | HP% | normal | - | yes | yes | yes | - |
| Blue | Sapphire [S-85] | DEF% | normal | - | yes | yes | yes | - |
| Orange | Amber [S-52] | HP% + Healing Boost | normal | - | yes | yes | - | yes |
| Black | Obsidian [S-52] | ATK% + DMG Boost | special | yes | yes | - | - | - |
| White | Moonstone [S-52] | DEF% + DMG RES | special | - | yes | - | yes | - |

- Colours, stats and slot rules are from the F2P guide [S-01]. The offhand takes every colour [S-01].
- The gem names are eog's (its own translations, not checked against the global client ❓): four pairs, Ruby and
  Obsidian (ATK), Sapphire and Moonstone (DEF), Beryl and Amber (HP), Citrine and Amethyst (SPD); the first of
  each pair is the single-stat gem [S-52][S-85]. eog's slot fits for all eight match the F2P guide's table above.
- Structure: four base stats (ATK, DEF, HP, SPD), each with a plain gem and a dual-stat gem [S-52]. A database
  site counts 8 gem types and 360 gem items, and calls the types "Ziwei stars" [S-80].

## Sockets

| Season | Sockets per gear piece | Total gems |
|---|---|---|
| 1 | 1 | 5 |
| 2 | 2 | 10 |
| later | +1 per new season | 15, 20 ... |

Source: [S-01][S-02]. With two sockets, a slot can hold two different allowed colours. eog agrees and adds
detail: sockets open with the piece's level (2 per piece on level-130 gear in Season 2), one more per season, at
most 4 [S-85].

## Tiers and combining

- Tiers run T1 to T15; each tier is worth about 1.5 times the one before [S-52][S-85]. The practical ceiling is
  T12; T13 to T15 exist as items but were not seen live [S-85].
- Value per tier, as a percent of the **base** attribute, not the final stat [S-85]:

| Tier | 1 | 2 | 3 | 4 | 5 | 6 | 8 | 10 | 12 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|
| Single-stat gem % | 1.5 | 3 | 6 | 12 | 18 | 27 | 60.7 | 136.6 | 307.5 | 1037.9 |
| Dual-stat gem, main stat % | 1 | 2 | 4.5 | 10 | 15.5 | 24 | 56.7 | 131.6 | 301.5 | 1030.4 |

  Every tier: [data/gem-tiers.json](../data/gem-tiers.json). This explains the "+301.5%" (T12 Obsidian) and
  "+307.5%" (T12 Ruby) figures: they are percent of base ATK. One player measurement: a T4 Amber gave about
  5,700 HP on a 680,000 HP character [S-85].
- Secondary stats grow slowly, per tier: DMG Boost or DMG RES 0.1%, Crit Rate 0.2%, Healing Boost 0.4% (a T12
  Obsidian carries +1.2% DMG Boost) [S-52][S-85]. A higher tier matters more than which gem of a pair [S-85].
- Combining (fusion) makes one gem of the next tier: **3 into 1 for the T1 and T2 steps, then 2 into 1 from T3
  up** [S-85] (tier C). A tier D site says "3 into 1" with no tier limit [S-55]; this page follows [S-85].
- T1 to T5 fuse from the inventory; from the T5 to T6 step fusion is done at the blacksmith NPC in Cinder Ridge
  [S-85] ❓.
- Success rates listed per band: 100% / 36% / 18% / 8% / 4%; which tier steps each band covers is not clear
  ❓ [S-85].
- Up to tier 5, combining always works. Beyond tier 5 it can fail; each failure fills a pity meter, which ends at
  a 100% success rate, and each success resets it [S-02]. eog describes the same meter: a failure does not raise
  the odds, it fills a per-tier charge that guarantees a later attempt [S-85].
- **Pity trick:** all gems of the same tier share one success rate and pity. Fail on cheap, unwanted gems of that
  tier until pity reaches 100%, then combine the expensive gems for a guaranteed success [S-02].

## Sources of gems

| Source | From | Notes | Source |
|---|---|---|---|
| Open world pickups | Loong Haven (Season 2) | Found lying around like cooking ingredients | [S-02] |
| Demonbind Tower | Lv 116, Loong Haven | The Season 2 tower ("Gem Tower"); rankings are pushed with class swaps | [S-02][S-03] |
| Market (Commercium) | any time | Prices fall as players saturate; wait for the crash before buying | [S-02] |
| Astral Pact "Gem Drop Rate +5%" nodes | Primostar levels 20 (Season 1 track), 800 and 1060 (Season 2 targets) | Permanent drop bonus | [S-01][S-02] |
| Primal Gem (eog: "Primordial Gem") | Grand Treasure Hunt reward | Raises gem acquisition from 10% to 60% ❓; see [Events](events.md) | [S-85] |
| Launch of the system | late Season 1 | Introduced a few days after the F2P guide was written | [S-01] |

## Recommended gems

| Class | Gems | Source |
|---|---|---|
| Duelist | Red or Purple (weapon, boots), Yellow, Green | [S-01] |
| Knight | Red or Purple, Blue | [S-01] |
| Sorcerer | Red or Purple, Yellow, Green | [S-01] |
| Sage | Red or Purple, Orange or Green (Orange for healers) | [S-01] |
| Any F2P | Sell White and Black gems to spenders | [S-01] |

For the Mage line (Sorcerer, Sage): Red or Purple in weapon and boots, Yellow or Green in helmet, Green in armor,
and the best spare in the offhand; a healer Sage swaps Green for Orange where the slot allows (helmet, boots,
offhand) [S-01]. Non-healers use the plain HP gem instead of Amber [S-52].

## Why not to over-invest

- Gems are "good, but not great": front-loaded, a real share of power early, a very small share later as the
  character grows [S-02][S-01].
- Season 2 adds many free sources, so supply rises [S-02].
- As players saturate and notice the low return, prices "will plummet": that is the time to buy high-tier gems, not
  before [S-02].
- Invest only for an immediate, temporary power boost, for example to make a dungeon threshold [S-02].
- Removing a socketed gem may cost a special item ❓ [S-55].

## Open questions

- ❓ Which fusion steps the 36 / 18 / 8 / 4% success rates apply to.
- ❓ Whether the global client uses eog's gem names (Sapphire, Citrine, Amethyst) and tier values; read a gem's info card.
- ❓ Whether gems and their tiers persist across seasons (the guides call them a permanent power source "at first").
- ❓ Whether the Season 1 gem source was an event or a tower.

## Sources

- [S-01] section 5 (Gems)
- [S-02] section VI (Gems, upgrade trick), section IV (Demonbind Tower)
- [S-03] Everything about Class Change ("Gem Tower")
- [S-52] gem names, tiers; [S-55] combine count (lead only)
- [S-85] eog.gg gems tab: values per tier, pairs, fusion, sockets ([notes](../sources/notes/eog.md)); [S-80] zeroluck.gg counts
