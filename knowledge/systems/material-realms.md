# Material Realms

<!-- index: Read when deciding how many Material Realm attempts to run or buy, which realm to favour, or whether to save tools -->

> **Summary:** Four realms (Ironvein Pit, Gilded Depths, Dread Hollow and the Sand Mine) turn tools into ore, Rolla, Battle Essence and Chrono Sand. Extra tools are the main Dawnium sink: SOF buys 4 ore / 2 Rolla / 4 essence / 4 sand a day (1,080 Dawnium). Rewards scale with Kingdom Rank, so unused tools can be saved for the top rank, running only the Rolla realm for the daily quest meanwhile, as long as that does not cost you a progression threshold.
> **Applies:** all seasons
> **Related:** [Currencies](currencies.md), [Kingdom rank](kingdom-rank.md), [Stamina](stamina.md), [Seasons](seasons.md), [Shops](shops.md), rules R-015, R-095, R-128

## The realms

Reached from Journal > Material Realms [R-094]. Each realm has its own tab set: the realm, Rankings, Goals [R-095].

| Realm | Tool | Gives | Unlock | Source |
|---|---|---|---|---|
| Ironvein Pit | Iron Hammer | Raw Ore and Refined Ore | first realm; after Verdantglade II ❓ | [R-095][S-35] |
| Gilded Depths | Gold Pickaxe | Rolla | ❓ | [R-125][S-35] |
| Dread Hollow | Worn Knuckles (eog: "Worn Gauntlet") | Battle Essence (fights monsters) | after Verdantglade IV ❓ | [R-125][S-35][S-87] |
| Sand Mine ❓ (eog's name; in-game name not seen) | Sand Shovel [S-85] ("a shovel" [S-04]) | Chrono Sand | ❓ | [S-85][S-01] |

eog calls the first three Iron Mine, Gold Mine and Monster Cave [S-85]; this page keeps the names seen in game.

- One tool is one attempt. In Ironvein Pit, one Iron Hammer mined about +115 Raw Ore at our rank (Apprentice)
  [R-095].
- eog's model of a run [S-85] ❓: each tool use (swing) deals 10 damage (80%) or 15 (20%) to the current target;
  a target pays on every hit and again when it breaks, then a new one is rolled by weight. Targets, weights and
  rewards: [data/gathering-yields.json](../data/gathering-yields.json).
- The realm's Goals tab pays for totals mined (Iron Mined 5 to 25 goals) [R-095].
- "Material Realms x5" is a Daily Quest [R-128].

## Where tools come from

| Source | Detail | Source |
|---|---|---|
| Goals tabs | e.g. 10 Standard Prayers paid 3 Iron Hammers | [R-093][R-095] |
| Daily quests | "a set amount of Iron Hammers daily" ❓ | [S-04] |
| Commissions ("Delegate Tasks") | Iron Hammers and Gold Pickaxes ❓ | [S-36] |
| Vendor Booth Vault | bundles at a discount: 5 Gold Pickaxes for 60 Dawnium, 5 Worn Knuckles for 40; the publisher also lists Iron Hammers there | [R-120][S-03][S-87] |
| Buying at the realm | button opens "Purchase Iron Hammer" at 0 tools; first price 60 Dawnium, limit 20 a day | [R-095] |

How many attempts are free each day is not stated exactly in any good source: our early note says two free attempts
per material dungeon (reported) [R-015], and guide sites speak of "extra attempts" on top of a daily allowance
[S-30][S-32] ❓.

## Buying extra tools with Dawnium

Price of each extra tool, per realm, per day [S-30][S-35]:

| Extra tool number | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Price | 60 | 60 | 100 | 100 | 150 | 150 | 200 | 200 | 250 | 300 |
| Running total | 60 | 120 | 220 | 320 | 470 | 620 | 820 | 1,020 | 1,270 | 1,570 |

The first price matches what we saw in game (60) [R-095]; the rest of the ladder comes from guide sites and fits
the SOF total exactly (see below).

Splits are written as four digits in the order **ore / Rolla / Battle Essence / sand** [S-01]:

| Split | Who recommends it | Dawnium a day |
|---|---|---|
| 2222 | F2P baseline on guide sites [S-30][S-32][S-35] | 480 |
| 3233 | "normal spenders" on one site ❓ [S-39] | 780 |
| 4244 | SOF's own F2P pick: less Rolla if the Cart's Rolla row is well levelled [S-01] | 1,080 |
| 4444 | the most popular choice [S-01][S-02] | 1,280 |
| 6446 | "fine too if you are desperate for power" [S-02] | 1,880 |
| 6666 / 8888 / 10-10-10-10 | heavy spenders ❓ [S-32] | 2,480 / 4,080 / 6,280 |

- 4244 or 4444 depends on your Rolla needs: if Rolla was your third or fourth Cart priority after Wood and Stone,
  you can put less Dawnium into the Rolla realm [S-01].
- "The Material Realm is extremely important for seasonal power: you cannot neglect it" [S-01].
- Check the Vault first: its discounted tool bundles cost far less per tool than the ladder [R-120].
- SOF and the lighter guides disagree on the F2P amount (4244 against 2222). This page follows SOF (tier B) when
  the Dawnium is there, and 2222 as the floor when it is not.

## Rewards scale with Kingdom Rank

- "Material Realm rewards scale with your Rank. Unless materials are needed immediately, save your attempts for
  higher Ranks to maximize drops" [S-03][S-87].
- From Season 2 every kingdom has only three ranks, so waiting for the top rank is a short wait [S-01].
- Loong Haven's top rank is Champion III, reached at about level 120 [S-02]. One site says the jump already comes at
  Champion I, and applies to stamina rewards too ❓ [S-34].
- Size of the bonus, from eog's calculator (tier C, not checked in game ❓) [S-85]: a realm rank multiplier that
  runs from 1.6 at the lowest rank to 45 at the highest, equal to the Rolla-per-5-stamina figure divided by 1,200.

| Rank band (eog's names) | Rolla per 5 stamina, three sub-ranks | Realm multiplier |
|---|---|---|
| Black Iron | 1,920 / 2,520 / 3,180 | 1.6 / 2.1 / 2.65 |
| Bronze | 4,020 / 4,980 / 5,940 | 3.35 / 4.15 / 4.95 |
| Silver | 6,900 / 7,980 / 9,240 | 5.75 / 6.65 / 7.7 |
| Gold | 12,000 / 12,960 / 14,160 | 10 / 10.8 / 11.8 |
| Sanctuary | 22,800 / 23,400 / 24,000 | 19 / 19.5 / 20 |
| Legend | 48,000 / 51,000 / 54,000 | 40 / 42.5 / 45 |

- Raw Ore is one tenth of the Rolla figure, Chrono Sand one twelfth, Battle Essence one eighth [S-85]. The band
  names are eog's translations; how they map to Apprentice ... Champion is not stated ❓. Our one data point fits
  the lowest band: an ore rock gave about +178 Raw Ore at Apprentice [R-108] against eog's 192.
- The jump between bands is large (Gold to Sanctuary nearly doubles), which is the case for saving tools. See
  [Kingdom rank](kingdom-rank.md).

## The save-attempts strategy

1. Keep every consumable tool in the bag; they do not expire and carry into the next season [S-02].
2. Each day run only the Rolla realm, enough to finish the daily quest: SOF writes it as 0/10/0/0, ten Rolla runs
   [S-01].
3. When you reach the kingdom's top rank (Champion III in Loong Haven), spend the stockpile [S-02].

Limits:

- It is an optimisation, not a requirement. "Do not hoard attempts if doing so will prevent you from reaching
  important CP/progression thresholds" [S-01].
- SOF does not guarantee it is better; it is the widely circulated community strategy [S-01]. "Almost every veteran
  player" recommends waiting at a season start, which is low pressure anyway [S-02].

## Which realm when

| Season phase | Favour | Why | Source |
|---|---|---|---|
| Start | Sand | Relic Resonance gives the most seasonal power early | [S-01][S-02] |
| Middle | Ore | gear catches up with relics in power | [S-01][S-02] |
| Last weeks | Ore | gear level weighs most in the Primostar rating | [S-01] |
| Any time | Rolla only as needed | the Cart covers it if its Rolla row is levelled | [S-01] |

The same order applies to stamina spending [S-01]. See [Stamina](stamina.md).

## Daily rankings

- Each realm has a Rankings tab [R-095]. One site says the rankings pay extra rewards by amount mined or monsters
  beaten ❓ [S-04]; no reliable source lists the rewards.
- SOF mentions "many advanced strategies designed around the material realm" without describing them [S-01];
  saving a stockpile and spending it in one day to top a ranking is a plausible one ❓.

## Open questions
- ❓ In-game name of the sand realm (eog: Sand Mine, tool Sand Shovel); unlock conditions of realms 2 to 4.
- ❓ Free attempts or free tools per day, per realm.
- ❓ Whether the price ladder resets daily and continues past 10 (our game showed a limit of 20 a day).
- ❓ Check eog's rank multipliers in game (compare one hammer's yield before and after a rank-up) and map its
  rank band names to the game's rank names.
- ❓ Ranking rewards and when rankings settle.

## Sources
- [S-01] Material Realms section, Additional Tips 7
- [S-02] Sections IV and VI
- [S-03] material-realm, progression
- [S-04] material realms and covenite pages (leads)
- [S-85] eog.gg stamina and gathering calculator ([notes](../sources/notes/eog.md)); [S-87] official Handbook Vol. 2
- [S-30], [S-35] price ladder; [S-32] refresh ladder by spender tier; [S-34] rank note; [S-36] tool sources; [S-39] 3233 split
- Rules R-015, R-093, R-094, R-095, R-108, R-120, R-125, R-128
