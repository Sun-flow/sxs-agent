# Dawnium plan: earning it and spending it

<!-- index: Read before spending Dawnium or when planning how to earn more: income sources, the spending ladder by budget, season timing, and hard limits -->

> **Summary:** Dawnium is the premium currency that the game also gives out for free. mae allows spending it
> (2026-11-18). It is generated mostly by daily play and, at scale, by market sales. Spend it every day from the top of one ladder: guild donations, discounted Vault tools, Daily
> Dungeon refreshes, Material Realm tools, Molly's Deals; put early-season surplus into the new relic pool. Income
> from daily play is small, so the big lever is selling dungeon shards and gear on the market once the account
> runs dungeons. Never spend real money, and never spend on the "never" list below.
> **Status:** the bot's rules still forbid almost all Dawnium spending (R-018, R-043). Until those rules are
> changed, this page is the plan to change them to: see [conflicts](../conflicts.md).
> **Applies:** all seasons
> **Related:** [Currencies](../systems/currencies.md#dawnium-income-and-spending), [Shops](../systems/shops.md),
> [Material Realms](../systems/material-realms.md), [Auction house](../systems/auction-house.md),
> data in [dawnium-daily-plan.json](../data/dawnium-daily-plan.json)

## How Dawnium is generated

Free sources, largest and most reliable first. Sizes marked ❓ are estimates; the account's own daily log is the
only way to firm them up.

| # | Source | Size | How often | Do | Source |
|---|---|---|---|---|---|
| 1 | **Market sales** (Trading House, Lv 40) | The only source that scales; no fixed figure | daily once dungeons are run | Sell spare dungeon shards and gear, white and black gems, recipes; sell shards before a season ends, because they lose sell value at the rollover | [S-01][S-02][S-85] |
| 2 | Daily content: daily quests, dungeons, realms, guild, arena, event missions | about 100+ a day ❓ | daily | Finish the [daily routine](daily-routine.md) | [S-35] |
| 3 | Guild Conquest | pays Dawnium, amount not recorded | 2 attempts a day | Do both | [R-112] |
| 4 | Story, achievements, feature unlocks | one-time lumps | once each | Claim every red "!" | [R-063] |
| 5 | Mailbox and gift codes | 80 to 200 per code; 16 codes were listed as working in mid-2026, none checked by us | when a code appears | Redeem at Home > Main Menu > User Center > Gift Code; Claim All mail (never Delete Read) | [S-37][S-85][R-168] |
| 6 | Mall free gift boxes | small | daily and weekly | Free boxes only | [R-121] |
| 7 | Grand Arena | per match and weekly rank ❓ | daily tickets, weekly reset | Spend saved tickets right after the reset | [S-01][S-87] |
| 8 | Wheel of Destiny | 2,888 as one reward choice | per Lucky Ticket | Low priority: take vouchers, keys and badges first | [S-01] |
| 9 | Events and login campaigns | varies | per event | Claim the free lanes | [S-03] |

Not used: Luminium converts to Dawnium 1:1 but is bought with real money [S-80][S-85][R-121]; a battle pass tier
skip costs 100 Dawnium and is never bought [S-80].

How the market income is built [S-01]:

1. Meet the newest dungeon's threshold.
2. Wear that kingdom's drop-bonus gear ("2x Rating Reward Rate", "Gear Drop Quality Ascension Rate") and display
   the Lucky Statue (dungeon double-reward chance 10%, rising to 60% as it is upgraded [S-85]).
3. Run the highest difficulty you can enter, with a carry, every day, including the two paid runs.
4. Keep what upgrades you; list the rest in the Trading House (Commercium, Lv 40).

## What a Dawnium buys (planning values)

eog.gg prices every item in Dawnium [S-85]. These are that site's valuations, not shop prices, but they show which
offers are cheap. Full table: [item-values.json](../data/item-values.json).

| Item | eog value | What it tells us |
|---|---|---|
| 1 Stamina | 4.8 | The free 30 stamina in the Vault is worth about 144 a day; never skip it |
| Material Realm tool | 20 | A Vault bundle (5 Gold Pickaxes for 60, 5 Worn Knuckles for 40 [R-120]) is 8 to 12 a tool; the realm's own ladder starts at 60. Bundles first |
| Stellatie | 100 | A Standard Prayer x10 is worth about 1,000; buy Stellatie only at a discount |
| Covenite | 1,000 | Never skip a Covenite in Molly's Deals or the Arena Shop (500 coins) |
| Quest Scroll | 120 | Buying scrolls with Rolla at the Vendor Booth is good value [S-87] |
| Bond Trinket / Summon Crystal | 160 / 1,600 | A Mythic Fantomon (60 crystals) is far beyond a free budget; take crystals as they drop |
| Auroral Badge: Rare / Epic / Legendary / Mythic | 8 / 15 / 56 / 74 | One relic capsule is 10 badges [S-80]: about 80, 150, 560 or 740 a pull |
| Destiny Fruit / Lucky Ticket | 60 / 360 | - |

## The spending ladder

Buy from the top; stop when the day's budget is used. Unit prices: daily dungeon refreshes 100 then 150
[S-01][S-85]; realm tools per realm per day 60, 60, 100, 100, 150, 150, 200, 200, 250, 300 [S-30]; donations
free, 20, 50 [R-103]. More: [Currencies](../systems/currencies.md#dawnium-income-and-spending).

| Step | Buy | Dawnium a day | Running total | Why this rank | Source |
|---|---|---|---|---|---|
| 1 | Guild donations 2 and 3 (20 + 50) | 70 | 70 | The publisher's handbook recommends exactly this: 70 Dawnium for two more donations; Guild Tokens buy Fantomon materials | [S-87][S-01] |
| 2 | Vault: discounted Material Realm tool bundles and discounted Stellatie | about 100 to 200, varies | about 250 | A bundled tool costs 8 to 12 against 60 or more at the realm | [R-120][S-87] |
| 3 | Daily Dungeon refresh x2 (100 + 150), once a dungeon is enterable | 250 | about 500 | Top of every guide's list: gear, shards, and market income | [S-01][S-85] |
| 4 | Material Realm tools, 2 per realm (2222): 4 x 120 | 480 | about 980 | The cheapest tools on each price ladder; eog's free-player split | [S-30][S-85] |
| 5 | Material Realm tools up to 4/2/4/4 (4244): 320 + 120 + 320 + 320 = 1,080 | +600 | about 1,580 | SOF's daily split for a free player | [S-01] |
| 6 | Molly's Deals (up to 10 a week) | varies, about 200 a deal | weekly | Discounted pulls, Covenite and badges | [S-01] |
| 7 | Vault variable items up to 400 in total | +200 | about 1,800 | First thing to cut when short | [S-01] |
| 8 | Guild "Gold Tool" (a guild item, probably a 24-hour gathering boost ❓; not the Gold Pickaxe) | 200 | 2,000 | Optional; cut first | [S-01] |
| 9 | Rolla realm up to 4 (4444), or 6446 when a threshold is at risk | +200 / +800 | | Only when Rolla is short or power is needed now | [S-01][S-02] |

Surplus above the ladder: relic gacha (Aeonic Gacha) early in a season while the pool is new, aiming at 70%
completion per region, then Destiny Fruits for the rest; later in the season more realm tools [S-01][S-02][S-85].

Where a lower-tier source disagrees, this page keeps SOF:

- eog calls 2222 the free-player split and 4244 a mid-spender split [S-85]; SOF spends 4244 as a free player
  [S-01]. The ladder has both, 2222 first.
- eog advises refreshing the Vendor Booth once a day and buying it out before Aqualis, twice a day in Loong Haven,
  later only the 80%-off items [S-85]. SOF treats refreshes as an optional "Rolla strategy"; rule R-120 forbids
  Refresh today. Not on the ladder.
- eog says free players get 3 donations a day [S-85]; the publisher says up to 5 with 1 free [S-87]. SOF's "3 only"
  stands either way.

## The daily budget rule (our proposal)

The guides assume an account that earns enough to spend 2,000 a day. A new account does not. So the bot needs a
rule that never empties the wallet ❓ (our design, not from a source):

- `reserve` = 1,000 Dawnium, kept for Molly's Deals and surprises.
- `budget_today` = min(2,000, average daily income over the last 7 days + (balance - reserve) / 14), never below 0.
- Walk the ladder from step 1 and stop at the last step that fits inside `budget_today`.
- A step is bought whole or not at all (a half-bought split wastes the cheap first tools of the other realms: the
  first two tools of every realm cost 60 each and come before any third tool).
- The progress tracker already reads the Dawnium balance, so the 7-day income is a log question.

Worked example: balance 3,000, income 120 a day gives 120 + 2,000 / 14 = about 263: steps 1 and 2. With market
income of 800 a day and a balance of 6,000 the budget is about 1,157: steps 1 to 4.

## Timing inside a season

| Phase | Extra Dawnium goes to | Source |
|---|---|---|
| Pre-season and first weeks | Relic pool 1 of the new kingdom; hold realm tools until the top rank if no threshold is at risk | [S-02] |
| Top rank reached to mid-season | Realm tools: sand first, then ore as gear catches up | [S-01][S-02] |
| Mid-season | Realm tools (ore); pool 2 is filled slowly with saved tickets, not Dawnium | [S-02] |
| Last two weeks | Ore and gear enhancement for Primostars; no skill pulls | [S-01] |

## Never

| Never | Why | Rule |
|---|---|---|
| Real-money buttons: Mall packs, Top Up, Timed Packs, Monthly Pass, Luminium, Vouchers | mae's hard limit | R-121, R-157 |
| Sign-in "Catch Up", Advanced Trial | Poor value | R-097, R-098 |
| Golden Beetle, Shapeshifting Mirror, Rename Card | No power | R-153, R-134 |
| Draw x1 or short draws; pulls below a full x10 | Pity and bonus logic is built on x10 | R-093, R-167 |
| Battle pass tier skips (100 each) | No power per Dawnium | [S-80] |
| Guild donations 4 and 5 | Guides stop at 3; the publisher's own tip also stops at 3 | [S-01][S-87] |
| The NPC class swap for 10 Dawnium | Locks every skill; the class is mae's choice | R-054 |
| Skill pulls in the weeks before a new class tier | The new pool makes them obsolete | [S-01] |
| Gems from the market before prices fall | Gems scale badly | [S-02] |

## Open questions

- ❓ Real daily Dawnium income of this account: log the balance every day for two weeks.
- ❓ Dawnium price of an Aeonic Gacha x10 and of a Prayer x10: no source has shop prices, only eog's valuations.
- ❓ What the guild "Gold Tool" is (best reading: a 24-hour guild gathering boost): open the guild facility screen.
- ❓ Dawnium paid by Conquest, Arena and the daily quests, one by one.
- ❓ Market prices and fees on our server.

## Sources

- [S-01] Resource Economy and Exploration sections; [S-02] section VI; [S-03] Progression (guild donation tip);
  [S-30] price ladders; [S-35] income estimate; [S-37] codes; [S-80] battle pass, Luminium, capsule cost;
  [S-85] item values, codes, refresh prices, splits; [S-87] official handbook (donations, Vendor Booth)
- Rules R-018, R-043, R-054, R-063, R-093, R-097, R-098, R-112, R-120, R-121, R-134, R-153, R-157, R-167, R-168
