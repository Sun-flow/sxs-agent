# Dawnium plan: earning it and spending it

<!-- index: Read before spending Dawnium or when planning how to earn more: income sources, the spending ladder by budget, season timing, and hard limits -->

> **Summary:** Dawnium is the premium currency that the game also gives out for free. mae allows spending it
> (2026-11-18). Spend it every day from the top of one ladder: guild donations, discounted Vault tools, Daily
> Dungeon refreshes, Material Realm tools, Molly's Deals; put early-season surplus into the new relic pool. Income
> from daily play is small, so the big lever is selling dungeon shards and gear on the market once the account
> runs dungeons. Never spend real money, and never spend on the "never" list below.
> **Status:** the bot's rules still forbid almost all Dawnium spending (R-018, R-043). Until those rules are
> changed, this page is the plan to change them to: see [conflicts](../conflicts.md).
> **Applies:** all seasons
> **Related:** [Currencies](../systems/currencies.md#dawnium-income-and-spending), [Shops](../systems/shops.md),
> [Material Realms](../systems/material-realms.md), [Auction house](../systems/auction-house.md),
> data in [dawnium-daily-plan.json](../data/dawnium-daily-plan.json)

## Income

| Source | Size | Do | Source |
|---|---|---|---|
| Daily content (quests, dungeons, realms, guild, arena, event missions) | about 100+ a day ❓ | Finish the [daily routine](daily-routine.md) | [S-35] |
| Guild Conquest | pays Dawnium | 2 attempts a day | [R-112] |
| Story, achievements, feature unlocks | one-time lumps | Claim every red "!" | [R-063] |
| Mailbox and gift codes | 80 to 200 per code | Redeem the list in [Codes](../systems/codes.md); Claim All mail (never Delete Read) | [S-37][R-168] |
| Mall free gift boxes | small | Daily and weekly boxes only | [R-121] |
| Arena | per match and weekly rank ❓ | Reset-day climb | [S-01] |
| Wheel of Destiny | 2,888 as a low-priority choice | Take vouchers, keys and badges first | [S-01] |
| **Market sales** | the only source that scales | Sell spare dungeon shards and gear, white and black gems, recipes; sell shards before a season ends | [S-01][S-02] |

How the market income is built [S-01]:

1. Meet the newest dungeon's threshold.
2. Wear that kingdom's drop-bonus gear ("2x Rating Reward Rate", "Gear Drop Quality Ascension Rate") and display
   the Lucky Statue.
3. Run the highest difficulty you can enter, with a carry, every day, including the two paid runs.
4. Keep what upgrades you; list the rest in the Trading House (Commercium, Lv 40).

## The spending ladder

Buy from the top; stop when the day's budget is used. Prices: [Currencies](../systems/currencies.md#dawnium-income-and-spending).

| Step | Buy | Dawnium a day | Running total | Why this rank | Source |
|---|---|---|---|---|---|
| 1 | Guild donations 2 and 3 | 70 | 70 | Official tip calls it "highly recommended"; Guild Tokens buy Fantomon materials | [S-03][S-01] |
| 2 | Vault: discounted Material Realm tool bundles and discounted Stellatie | about 100 to 200, varies | about 250 | Bundles cost a fraction of the per-tool price at the realm | [R-120][S-03] |
| 3 | Daily Dungeon refresh x2 (once a dungeon is enterable) | 250 | about 500 | Top of every guide's list: gear, shards, and market income | [S-01] |
| 4 | Material Realm tools, 2 per realm (2222) | 480 | about 980 | The cheapest tools on each price ladder | [S-30] |
| 5 | Material Realm tools up to 4/2/4/4 (4244) | +600 | about 1,580 | The guide author's daily split | [S-01] |
| 6 | Molly's Deals (up to 10 a week) | varies, about 200 a deal | weekly | Discounted pulls and badges | [S-01] |
| 7 | Vault variable items up to 400 in total | +200 | about 1,800 | First thing to cut when short | [S-01] |
| 8 | Guild "Gold Tool" | 200 | 2,000 | Optional; cut first | [S-01] |
| 9 | Rolla realm up to 4 (4444), or 6446 when a threshold is at risk | +200 / +800 | | Only when Rolla is short or power is needed now | [S-01][S-02] |

Surplus above the ladder: relic gacha (Aeonic Gacha) early in a season while the pool is new, aiming at 70%
completion per region; later in the season more realm tools [S-01][S-02].

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
| Guild donations 4 and 5 | Guides stop at 3 | [S-01] |
| The NPC class swap for 10 Dawnium | Locks every skill; the class is mae's choice | R-054 |
| Skill pulls in the weeks before a new class tier | The new pool makes them obsolete | [S-01] |
| Gems from the market before prices fall | Gems scale badly | [S-02] |

## Open questions

- ❓ Real daily Dawnium income of this account: log the balance every day for two weeks.
- ❓ Dawnium price of an Aeonic Gacha x10 and of a Prayer x10.
- ❓ What the guild "Gold Tool" is.
- ❓ Market prices and fees on our server.

## Sources

- [S-01] Resource Economy and Exploration sections; [S-02] section VI; [S-03] Progression (guild donation tip);
  [S-30] price ladders; [S-35] income estimate; [S-37] codes
- Rules R-018, R-043, R-054, R-063, R-093, R-097, R-098, R-112, R-120, R-121, R-134, R-153, R-157, R-167, R-168
