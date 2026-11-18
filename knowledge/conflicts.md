# Conflicts: guides against our rules, and sources against each other

<!-- index: Read before changing a rule or trusting a contested fact: every place where a guide disagrees with memory-bank/game/rules/ or with another source, with a recommendation -->

> **Summary:** the knowledge base never edits a rule. Where the player guides recommend something a rule forbids
> or shapes differently, it is listed in part 1 with a recommended decision for mae. Part 2 lists facts our rules
> report differently from the sources (to verify in game). Part 3 lists disagreements between sources and which
> one the pages follow.
> **Applies:** all seasons
> **Related:** `memory-bank/game/rules/policy.md`, [Dawnium plan](strategy/dawnium-plan.md), [Sources](sources/README.md)

## Part 1: advice that goes further than a rule (decisions for mae)

mae said on 2026-11-18 that spending Dawnium is allowed and asked for clear plans. The rules below still say
otherwise, so the bot behaves as before until they are changed. The docs thread owns rule edits.

| # | Topic | Rule today | Guides say | Recommended decision |
|---|---|---|---|---|
| C-01 | Spending Dawnium at all | Never, except the 2nd guild donation [R-018][R-043] | Spend daily from a priority list, about 2,000 a day for an established account [S-01] | Replace "never spend Dawnium" with an allow-list (C-02 to C-08) and a daily budget rule ([Dawnium plan](strategy/dawnium-plan.md)); keep "never real money" |
| C-02 | Guild donations | At most 2 a day; never the 50-Dawnium one [R-103] | 3 a day: free, 20, 50 (official tip: "highly recommended") [S-03][S-01] | Allow the 3rd donation |
| C-03 | Daily Dungeon paid runs | Never buy extra attempts [R-015] | Two refreshes a day (100, 150) are the top Dawnium priority [S-01] | Allow once a Daily Dungeon loop exists |
| C-04 | Material Realm tools | Never buy hammers or tools [R-095][R-043] | 4244 or 4444 extra tools a day; 2222 as a light plan [S-01][S-30] | Allow inside the daily budget; prefer Vault bundles |
| C-05 | Vendor Booth | Never Refresh; buy nothing until Buy? is filled [R-120] | Buy Wood, Stone, Quest Scrolls for Rolla; discounted Stellatie and tools in the Vault [S-03][S-01] | Fill Buy? in `docs/shop-tables.md` from [Shops](systems/shops.md); it also completes the daily quest "2 Vendor purchases" [R-128] |
| C-06 | Kingdom Shop | Buy nothing from Hermes yet [R-134] | Kingdom tools are the top purchase: each opens a statue area [S-01] | Allow Withering Potion and Gateway Key with Abundance Leaves |
| C-07 | Guild Shop | Buy nothing yet [R-114] | Fantomon aptitude materials and summon tokens weekly [S-01] | Allow those items once Fantomons unlock (Lv 50) |
| C-08 | Relic gacha with Dawnium | Never Dawnium; badges and tickets only [R-167] | Early-season Dawnium to the relic gacha; 70% completion per region [S-01][S-02] | Keep the rule until the price per pull is read; then allow as "surplus" in the budget |
| C-09 | Relic "Replace" | Never Replace a relic [R-172] | Display priority: unique relic, special stat, flat, percent; Lucky Statue must be displayed [S-01] | Allow Replace when the new relic ranks higher in that order |
| C-10 | Relic enhance order | Band all elements evenly, by character affinity [R-105] | Class element first, then all five [S-01] | Class (loadout) element one band ahead, others follow |
| C-11 | Wheel of Destiny | Only the free first spin [R-147] | Spend Lucky Tickets; choose by the priority list [S-01] | Allow ticket spins (no Dawnium) with the reward order from [Weekly routine](strategy/weekly-routine.md) |
| C-12 | Cart rows | Only Stone and Wood [R-136] | All rows to Lv 10 first (official tip), then Wood and Stone, then Rolla, Ore/Sand, Essence, Treats [S-03][S-01] | Keep Stone and Wood first; add the later rows as the order when both are capped |
| C-13 | Material Realm attempts | Use the 2 free attempts daily [R-015] | Save attempts and tools for the top rank; only Rolla runs for the daily quest [S-01][S-02][S-03] | Below Lv 100 keep using free attempts; save bought tools. Revisit at Lv 100 |
| C-14 | Stamina target | Ore by default [R-107] | Commissions first; sand at season start, ore from mid-season [S-01] | Follow [Stamina plan](strategy/stamina-and-realms.md) once commissions are coded |
| C-15 | Skill banners | Standard banner only; Affection banner unused [R-093] | Covenite (Premium) banner pulls for the class later; save pulls before a new tier [S-01] | No change now; add a "save before a tier" switch to the pull script later |
| C-16 | Golden Beetles | Never spend [R-153] | No guide disagrees | No change |
| C-17 | Class choice at Lv 44 | mae's decision [R-054] | Sorcerer recommended for a solo account; reversible for free at Lv 100 [S-03] | mae to choose before the account reaches Lv 44 |
| C-18 | Skill levels | Techniques are levelled one by one; new ones start at Lv 1 [R-037] | One blog says levels belong to the slot [S-11] | Keep the rule (observed) |
| C-19 | Guild donations, third one | At most 2 a day [R-103] | The publisher's handbook: up to 5 a day, 1 free, and it recommends paying 70 Dawnium for two more [S-87] | Same as C-02, now backed by the publisher: allow the 3rd donation |
| C-20 | Vendor Booth Refresh | Never Refresh [R-120] | Refresh once a day and buy out before Aqualis, twice in Loong Haven, later only 80%-off items [S-85]; SOF treats refreshes as optional [S-01] | Keep the rule; SOF does not ask for it |
| C-21 | Dawnium for Daily Dungeon runs: price now known | Never buy extra attempts [R-015] | 100 then 150 Dawnium, confirmed by a second source; unused runs bank to 6 [S-85] | Same as C-03; the cost side is settled |
| C-22 | Speed-ups in a new season | No rule on timing (speed-up not coded) | Hold the free speed-up and Temporal Crystals for Lv 106, 108, 116, 130, or to the season's end [S-85]; SOF: after the new statues are lit [S-02] | When coded, follow SOF (statues first), then eog's milestones |
| C-23 | Relic gacha stop point | Badges and tickets only, no stop rule [R-167] | Pull to 50 to 70% of a pool, then switch to Destiny Fruits [S-85][S-01] | Add a completion check to the gacha loop before more x10 pulls |
| C-24 | Fantomon levelling | Not coded | Level only the four deployed; resonance is the lowest of them [S-87][S-85] | Write the rule this way when Fantomons are coded |

## Part 2: facts to verify in game

| # | Fact | Our rule | Sources | Check |
|---|---|---|---|---|
| V-01 | Fantomon unlock level | Lv 51, reported [R-011] | Lv 50: official post, Fandom, eog [S-40][S-03][S-54] | Note the level when the tutorial fires |
| V-02 | Vendor Booth unlock | Lv 18, reported [R-011] | Lv 20 [S-03] | Already unlocked on our account; low value |
| V-03 | Guild unlock | Lit at Lv 20 [R-011] | Lv 15 (tab text, Fandom) [S-03] | Low value |
| V-04 | Cart Gear row unlock | Lv 15, observed [R-020] | Lv 10 [S-35] | Keep ours |
| V-05 | Stamina regeneration | 5 an hour, observed [R-107] | "every minute" [S-04] | Keep ours; the tier D claim is wrong |
| V-06 | Stamina cap | 300 passive; items up to 1,200 (shop text) | "max 300" [S-04]; "bank 300" [S-02] | Read the stamina card |
| V-07 | Our server's day 1 | unknown | Schedules run on server days [S-02] | Read a calendar or event page: turns the schedule into dates |
| V-08 | Statue of the Brave / Statue of Witch | "Statue of <name>" Visit: one-time permanent stat boost and full heal [R-144] | A daily visit for Stellatie or stamina [S-40]; "a daily buff or curse" [S-04] | Visit the same statue on two days |
| V-09 | Daily reset hour | 8:00 server time, UTC-5 [R-024] | 13:00 UTC [S-85] | The two agree; nothing to do |
| V-10 | Off-hand slot | Not unlocked at Lv 37 [R-023] | Opens after the Class II change [S-87] | Look at the slot after Lv 44 |
| V-11 | Dismantle unlock | Alchemy Pot slot at Lv 7 [R-035] | Dismantle at Lv 12 [S-87] | Low value; already past |
| V-12 | Gear Resonance size | Small bonus per band, for example HP +2% [R-092] | "+20% flat" per step [S-80] | Keep ours; the site's unit is unclear |

## Part 3: sources against each other

| # | Topic | Version A | Version B | Pages follow |
|---|---|---|---|---|
| X-01 | Season number of Loong Haven | "Season 3" on one calendar image [S-01] | Season 2 everywhere else [S-02] | Season 2 |
| X-02 | Free-player realm split | 4244 [S-01] | 2222 [S-30][S-32] | 4244 as the target, 2222 as the floor |
| X-03 | Rank to wait for before using saved tools | Champion III [S-02] | Champion I [S-34] | Champion III |
| X-04 | Standard Prayer rates | Legendary 2.41%, Epic 7.9%, Rare 24%, shard 65.69%; no pity stated [S-10][S-80] | 1%, 7%, 22% with pity at 70, 30, 10 [S-15][S-85] | Both shown, unverified; plans use the lower set |
| X-05 | What Covenite is | Premium (class) Prayer ticket, a skill selection ticket from Molly's Deals, the Wheel of Destiny, Chaos Invasion and the Arena Shop [S-25][S-01][S-42] | A currency earned from Standard pulls, not sold for Dawnium [S-20][S-85] | Premium ticket |
| X-06 | Tank Fantomon aptitude stats | Block and Crit Res [S-01] | Block and Block Efficiency [S-02] | Both listed |
| X-07 | Relic pool 2 Legendary stats | Four stats in the text [S-02] | One in the table image [S-02] | The text |
| X-08 | Who can become Adult | Only Mythic Fantomons [S-04][S-26] | Fillers such as Armopi can [S-02] | The guide [S-02] |
| X-09 | Tier 2 class unlock | Lv 44 [S-03][S-11] | "level 18" and others [S-04] (18 is the class level) | Lv 44 |
| X-10 | Tier 4 skill names | Fandom names [S-03] | zeroluck names [S-10] | Both recorded; in-game names to confirm |
| X-11 | Arena extra-ticket prices | 10, 25, 45, 75 ... [S-42] | 10, 15, 20, 30 ... [S-45][S-30] | Second, as it matches a third source |
| X-12 | Dungeon name | Aquaorigin [S-01][S-02] | Aquorigin Shrine [S-03][S-85] | Aquorigin Shrine as the main spelling, Aquaorigin as an alias |
| X-13 | Hellhold Purgatory threshold | 6.2M [S-03] | Image unclear, could be 5.2M [S-01] | 6.2M |
| X-14 | Relic resonance cap in Season 1 | +10 [S-01][S-03] | Calculator scores to +13 [S-51] | +10 permanent, +11 to +13 seasonal |
| X-15 | Cart second priority | Rolla [S-01] | Ore and Sand [S-32][S-39] | The guide [S-01]; both orders are given there as valid |
| X-16 | Companion unlocking | Journals from Premium Commissions [S-01] | "Draws from level 38" [S-27] | The guide [S-01] |
| X-17 | Global launch date | 2026-05-19 [S-61] | 2024-12-20 [S-72] | 2026-05-19; S-72 is fabricated |
| X-18 | Fandom data quality | Tier 3 class pages are copies of the Duelist tables; Warrior charm texts copy the Mage's [S-03] | - | Those tables are not used |
| X-19 | Guild donations per day | Up to 5, 1 free; pay 70 for two more [S-87] | 3 a day for free players, 5 for spenders [S-85] | The publisher [S-87]; the advice (stop at 3) is the same |
| X-20 | Free-player Treasure Hunt picks before Loong Haven | Lucky Statue and Primal Gem are both MUST BUY [S-01][S-02] | Skip hunts 1 and 3, take 2 and 5: Lucky Statue and the Aqualis Mythic choice, not the Primal Gem [S-85] | SOF |
| X-21 | Fantomon summon top rate | Legendary Fantomon 1.96%, Epic 6.37% [S-80] | Top rate 0.8%, Legendary pity 80 [S-85] | Both shown, unverified |
| X-22 | Gem fusion | 3 into 1 at every step [S-55] | 3 into 1 for the first two steps, then 2 into 1 [S-85] | eog (tier C over tier D) |
| X-23 | Gear enhancement cap | +100 permanent, about +160 to +180 in a season [S-03][S-02] | Data maximum +250 [S-80] | The guides; +250 is read as the data ceiling |
| X-24 | Number of player skills | "Over 200", then "300+" [S-87] | 238 [S-80]; 361 [S-85] | Not used for any decision |
| X-25 | Sorcerer class trait name | Accuracy [S-03][S-85] | Block Penetration [S-80] | Accuracy; the other is an alias |
| X-26 | Tier 3 class-level gate | Class level 16 in the Tier 2 class, total 48 [S-80][S-85] | Job level 18 [S-03] (that is the Tier 2 gate) | 16 and 48 |
| X-27 | Sand realm and its tool | Sand Mine, Sand Shovel [S-85] | "Crystal Shovel", "a shovel" [S-04] | eog; in-game name still to read |
| X-28 | Free-player split and the rank to wait for | 4244; wait for Champion III [S-01][S-02] | 2222 for free players, 4244 for mid spenders; reach Champion I before spending stamina [S-85] | SOF (see X-02, X-03) |
| X-29 | Cart order after Wood and Stone | Rolla next [S-01] | Chrono Sand and Raw Ore next; Rolla only with 3 or more shop refreshes a day [S-85]; the publisher only says all rows to Lv 10, then Wood and Stone [S-87] | SOF (see X-15) |
| X-30 | One element or all | Class element first, then all five [S-01] | Free players commit to one element [S-85] | SOF |
| X-31 | Where Affection Tokens come from | Praying, capped at 1,000 a week [S-85] | Partying in daily events with friends or guildmates [S-42] | Praying; the other is noted as unconfirmed |
| X-32 | When the Mysterious Merchant appears | The day after Chaos Invasion [S-01][S-03][S-85] | Also after a Destiny Exploration (two of our pages, no clear source) | After Chaos Invasion |
| X-33 | Relic level cap | Level and star both max at 6 [S-80] | Enhance costs "beyond +4", resonance to +10 and +13 [S-01][S-03] | Different scales (per-relic level against per-element resonance); both kept |
| X-34 | Starlight Bread | Filed under "Restore HP" [S-80] | Described as restoring Stamina, same page [S-80] | Unresolved; test one |
| X-35 | Server calendar after Season 2 | SOF's calendar ends at Season 3's start [S-02] | Harpadia day 226, Ignis day 335, from the Chinese schedule [S-85] | Forecast only |
| X-36 | Recipe count | 67 recipes (5 recovery, 62 buff) [S-80] | 87 dishes over all kingdoms [S-85] | Unresolved; eog probably counts later kingdoms. See [cooking](systems/cooking-and-dishes.md) |
| X-37 | Sage line at Tier 4 (Dominator) | Grade B on eog's relayed tier list [S-85] | Rated top for PvE support by other guides, see [Tier 4 classes](classes/tier-4.md) | Unresolved; one grade for all modes hides the role. SOF's advice stays the guide for our Mage |

## Sources

- [S-01], [S-02]: the SOF guides; [S-03]: Fandom; [S-80]: zeroluck.gg; [S-85]: eog.gg; [S-87]: the publisher's
  news posts; others as tagged; rules cited by ID
