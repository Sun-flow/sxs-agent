# Shops

<!-- index: Read before buying anything: every shop, its currency, stock, refresh, what to buy first and what to skip -->

> **Summary:** Kingdom Shop: kingdom tools first. Guild Shop: Fantomon aptitude materials and summon tokens first. Vendor Booth: free stamina daily, Wood, Stone and Quest Scrolls for Rolla, discounted Stellatie and realm tools in the Vault. Mysterious Merchant: only the Primal Forge. Molly's Deals: up to 10 a week, usually worth it. Mall: real money, never.
> **Applies:** all seasons
> **Related:** [Currencies](currencies.md), [Material Realms](material-realms.md), [Auction house](auction-house.md), [Events](events.md), [Guild](guild.md), machine-readable copy in [data/shops.json](../data/shops.json); rules R-043, R-114, R-120, R-121, R-125, R-134, R-157

The stock we have actually read in our own game is in [docs/shop-tables.md](../../docs/shop-tables.md) (tier A). The
bot buys nothing until mae fills that file's Buy? column [R-120][R-114]; the priorities below are what the guides
recommend, to help fill it. Read any item through its info card, never its price button [R-125].

## Overview

| Shop | Where | Currency | Refresh | First buys |
|---|---|---|---|---|
| Vendor Booth: General | Home, Molly's wagon | Rolla | daily; paid refresh 4K Rolla | Wood, Stone, Quest Scrolls |
| Vendor Booth: Vault | same | Dawnium | daily | free Stamina, discounted Stellatie and realm tools |
| Vendor Booth: Goals | same | Vendor Booth Pts | milestones | free claims |
| Molly's Deals | friends' homes, via the Home gate | Dawnium ❓ | 10 purchases a week | Stellatie, Covenite, relic badges |
| Kingdom Shop | each kingdom's town (Hermes in Drasilgard) | kingdom currency | ❓ | kingdom tools |
| Guild Shop | guild island, east | Guild Tokens | weekly | Fantomon aptitude materials, summon tokens |
| Arena Shop | Grand Arena | Arena coins (blog's name ❓) | ❓ | Fantomon shards, Bond Trinkets, then Covenite and Stellatie |
| Mysterious Merchant | Home, the day after Chaos Invasion; can also be summoned by a Destiny Exploration | Chaos Crystals | per event | Primal Forge only |
| Grand Treasure Hunt | event | Aurodrasil Energy | weekly event | Level 5 unique relics |
| Prayer / Fantomon exchange | Goddess Statue, Arborisfatum | pull by-products | ❓ | Mythic Fantomon duplicate |
| Commercium | airship from Home, Lv 40 | Dawnium, Luminium | player-driven | see [Auction house](auction-house.md) |
| Mall, Starter Pack, Timed Packs | Home menu and popups | real money | - | nothing, ever |

## Vendor Booth (Molly)

- Unlock: Lv 18 on our account, where the tutorial that the Bellflower harvest plays opened it early
  [R-011][R-120] (tier A, the figure this knowledge base uses). The publisher and Fandom say character Lv 20
  [S-87][S-03].
- Three tabs: General (Rolla), Vault (Dawnium), Goals (Vendor Booth Pts) [R-120].
- Stock refreshes daily; a paid refresh of the General tab costs 4K Rolla, with 10 available when we looked
  [R-120]. Buying two things here is a Daily Quest [R-128].

### General tab (Rolla)

| Priority | Item | Seen price | Why |
|---|---|---|---|
| 1 | Wood | 150 for 3K | Cart upgrades; "always in short supply" [S-03] |
| 1 | Stone | 150 for 2.4K (20% badge) | Cart upgrades; the tighter of the two [S-01] |
| 1 | Quest Scrolls | ❓ | named a first buy, with Wood and Stone, by the publisher [S-87][S-03]; eog values one at 120 Dawnium (its valuation, not a price) [S-85] ❓; not seen in our stock yet |
| 2 | Stellatie | 1 for 3.15K (70% badge) | skill pulls; extra refreshes add up to "quite a lot" of Stellatie and Bond Trinkets [S-01] |
| 3 | Raw Ore, Battle Essence | 350 for 2.1K; 250 to 300 for 1.6K to 2.4K | fill a bottleneck; "adjust other purchases based on your needs" [S-03] |
| 4 | Water | 500 | cooking ingredient; buy only for a recipe |

Refreshing:

- SOF does not favour the "Rolla strategy" (many refreshes to buy Wood and Stone), because the amount per refresh
  is limited [S-01]. See [Cart and home](cart-and-home.md#the-rolla-strategy).
- One guide site gives a schedule: one refresh a day and buy out before Aqualis; two during Loong Haven; later only
  items at 80% off, up to three refreshes ❓ [S-32]. Another says at least three a day ❓ [S-35].
- Our rule today: never press Refresh [R-120].

### Vault tab (Dawnium)

| Priority | Item | Seen price | Verdict |
|---|---|---|---|
| 1 | Stamina x30 | Free, once a day | Always claim [R-120] |
| 2 | Gold Pickaxe x5 | 60 (40% badge) | Buy: 12 Dawnium a tool against 60+ at the realm [S-03][S-30] |
| 2 | Worn Knuckles x5 | 40 (60% badge) | Buy: 8 Dawnium a tool [S-03] |
| 2 | Iron Hammers | not in our stock that day | Buy when offered at a discount; the publisher lists them in the Vault [S-87][S-03] |
| 3 | Stellatie x2 | 100 (50% badge) | Buy when discounted [S-03] |
| 3 | Epic Auroral Badges | ❓ | named an essential by one site ❓ [S-35] |
| skip | Refined Ore x180 | 180 | too expensive for F2P ❓ [S-04] |
| skip | Golden Beetle, Shapeshifting Mirror, Rename Card | 50, 100, 500 | no power [R-153] |

SOF budgets about 400 Dawnium a day for the Vault, as the variable last item of the daily plan [S-01].

### Goals tab

Milestones at 5K, 10K, 15K, 20K and 25K Vendor Booth Pts, each paying a ticket item; points likely come from buying
[R-120]. Free to claim [R-116].

## Molly's Deals

- At the gate on Home; it opens the friends list. A friend showing an orange house symbol has a special Molly's
  Deal at their home [S-01].
- Weekly purchase limit: 10 deals [S-01]. The guide's screenshot shows "Weekly Purchase Limit: 2/10" and a card
  priced 225 for an item x10 [S-01].
- Stock: Stellatie, Covenite, relic gacha badges and more, at a discount; "usually very good deals" [S-01].
- Check the gate several times through the week [S-01]. Needs friends: see [Guild](guild.md) for social rules; the
  bot may team up freely [R-057].

## Kingdom Shops

- One per kingdom, paid in that kingdom's currency. Verdantglade's is run by Hermes, the "Smiling Merchant", at the
  mushroom-roof shop on the east side of Drasilgard; the first talk gives a free welcome gift [R-134].
- Shop Level 1 of 4 with a progress bar (0/3500 to Lv 2); tabs Lv 1 to Lv 4, higher ones locked [R-134]. What
  raises the level is unknown ❓ (leaves spent is the likely answer).

| Priority | Item | Seen price (Abundance Leaves) | Why |
|---|---|---|---|
| 1 | Withering Potion | 1.8K (40% badge, limit 1), then 3K (limit 1) | opens a vine blockade with a statue behind it [S-01] |
| 1 | Gateway Key | about 3K ("3k leaves to buy a key/potion") | same, for gateways; not in our Lv 1 tab [S-01] |
| 2 | Stellatie at 90% off | 100 (limit 1) | cheapest pull ticket in the game |
| 2 | Refined Ore at 90% off | 100 for 100 (limit 1) | cheap |
| 3 | Stellatie, Refined Ore at 40% off | 600 (limit 2) | only when no tool is within reach |
| 3 | Recipes (Cheerful Greens, Stewed Meat and Potatoes) | 600 each | buff dishes, see [Cooking](cooking-and-dishes.md) |
| 4 | Flour, Potato; Iris, Jungle Fables | 50 each; 300 each | ingredients and companion gifts, as needed |

- Kingdom tools are "extremely important to buy from the kingdom shops, the top priority" [S-01].
- Tools by kingdom: Verdantglade Withering Potion, Cinder Ridge Magic Drill, Aqualis Water Mine, all kingdoms
  Gateway Key [S-01]. A Magic Drill is also needed inside Verdantglade (Hidden Camp, [R-151]); one Verdantglade area
  has two statues behind one drill [S-01].
- Fund them through commissions that pay kingdom currency [S-01]. See [Commissions](commissions.md).
- One site lists, for the Season 2 changeover, Gateway Key x5, Water Mine x2, Magic Drill x1, Withering Potion x1
  and seven of the new season's item ❓ [S-34]; it does not say whether that is stock to buy or a total needed.

## Guild Shop

- Guild island, east side; pays Guild Tokens; refreshes weekly; stock unlocks with the guild's Shop level (1 to 6)
  [R-114].

| Priority | Item | Seen price (Tokens) | Notes |
|---|---|---|---|
| 1 | Fantomon aptitude materials | ❓ | "highest priority Guild shop purchases every week" [S-01] |
| 1 | Bond Trinket (summon token) | 400 at 50% off, limit 2, shop Lv 3 | same [S-01] |
| 2 | Discounted items in general | | "Prioritize discounted items and Fantomon growth materials" [S-03] |
| 2 | Stellatie | 500, limit 3 | buyable at shop Lv 1 |
| 3 | Rare Auroral Badge x10 | 400, limit 3, shop Lv 2 | one Rare capsule |
| 3 | Lucky Ticket | 1.5K, limit 1 | a Wheel of Destiny spin |
| 4 | Garden plants and livestock (Resilient Sprout, Stone Sheep, Steely Chicken ...) | 640 to 4.2K | feed the guild garden and pens, which produce Fantomon materials; see [Guild](guild.md) |

Token income: 300 per donation, 120 an hour from guild AFK [R-103][R-110].

## Arena shop

- Paid with **Arena coins**, 100 per won attack; "Arena coins" is a player blog's name, the in-game name is not
  confirmed ❓ [S-42]. It also sells permanent-stat food [S-31].
- Stock reported by one Season 1 player [S-42]: Fantomon Shards x10 2.1K (limit 2), Bond Treat 1.6K (2),
  Stellatie 1K (3), Rare Auroral Badge x10 800 (5), Covenite 500 (1). The publisher confirms it sells Fantomon
  shards [S-87]. Full table and buy order: [Arena and PvP](arena-and-pvp.md#arena-shop).

## Mysterious Merchant (after Chaos Invasion)

- After a Chaos Invasion event ends (the day after, per eog [S-85]), the Mysterious Merchant appears on Home and
  sells for the event currency (Chaos Crystals [S-32]) [S-01]. That is his scheduled visit. A Destiny
  Exploration can also summon him, or Molly, to Home with discounted goods [S-03]; see
  [Relics](relics.md#destiny-fruits).
- **Buy only the Primal Forge; skip everything else; keep buying it until it is maxed** [S-01].
- If you cannot afford it, dismiss him and save the currency for the next Chaos Invasion [S-01].
- He can also sell recipes for permanent food [S-31]; SOF's rule above still says skip them.
- The Primal Forge raises the Cart's Raw Ore output [S-03] and is upgraded up to Immortal rarity [S-85][S-03].
  Its price per level is not in our sources ❓. See [Events](events.md).

## Grand Treasure Hunt

- Weekly event (first on server day 8, then every 7 days) paid in Aurodrasil Energy; reward Levels 1 to 5
  (guides also say floors or stages), with a unique relic on Level 5 [S-33][S-85].
- SOF: save the currency every other week so you can afford the Lucky Statue and Primal Gem relics [S-01].
- Lucky Statue: 10% to 60% chance to double dungeon chest drops as it ascends; Primal Gem: 10% to 60% more gems
  [S-33]. Keep the Lucky Statue in the main relic line for the 20% resonance bonus [S-01].
- Clearing Levels 1 to 5 costs about 3,240 Energy; do not spend in a week you cannot reach Level 5 ❓
  [S-33][S-85]. Prices per item are not published, only this total.
- Lower Levels hold Treats, companion gifts, Wood and Stone, Legendary Auroral Badges, Bond Trinkets; Stellatie
  there is a skip ❓ [S-33]. See [Events](events.md) and [Relics](relics.md).

## Wheel of Destiny rewards

Not a shop, but a choice of rewards. SOF's order [S-01]:

1. Skill Shard Vouchers
2. Gateway Keys and Auroral Elemental Badges
3. Legendary Auroral Badges, Covenite, Bond Trinkets
4. Legendary Fantomon resources (wool, egg, essence), 2,888 Dawnium, extra Lucky Tickets

The first spin on each map wheel is free while its zone is unexplored [R-147].

## Exchange shops

- The Prayer screen has an Exchange tab [R-093]; stock unknown ❓. See [Gacha](gacha.md).
- The Fantomon exchange shop sells duplicates of Nyxarchon and Aegiswing; one duplicate is what an Adult evolution
  needs [S-02]. Price reported as 60 Summon Crystals a copy ❓ [S-32]. See [Fantomons](fantomons.md).
- The launch event had an Overture Shop (emoticons) paid in Overture Badges [S-03].

## Mall and paid packs: never

- Every Mall pack costs real money; only the free gift box on each pack page is claimed [R-121].
- Starter Pack on Home and Timed Packs popups ("Exploration Kit", "Gacha Bonus Pack", $0.99) are paid: dismiss
  [R-157][R-167].
- For reference only, one site ranks paid offers as monthly card, month fund, weekly card, pop-up packs ❓ [S-32].
  The Monthly Pass also boosts Cart production [S-03].

## Open questions
- ❓ Kingdom Shop tabs Lv 2 to 4: stock, and what raises the shop level.
- ❓ Kingdom shops and merchants of Cinder Ridge, Aqualis and Loong Haven.
- ❓ Molly's Deals currency (the screenshot icon is not readable) and whether deals differ per friend.
- ❓ Arena Shop: in-game currency name and refresh; Prayer Exchange stock; Mysterious Merchant stock and the
  Primal Forge's price per level.
- ❓ Quest Scrolls: what they do and their Rolla price (eog values one at 120 Dawnium [S-85]).

## Sources
- [S-01] Exploration, Fantomons, Additional Tips (Molly's Deals, Chaos Invasion, Wheel of Destiny)
- [S-02] Section V (exchange shop)
- [S-03] vendor-booth, progression, journey-overture
- [S-04] covenite page (lead)
- [S-30], [S-32], [S-35] refresh and Vault advice
- [S-31] food sources
- [S-33] Grand Treasure Hunt
- [S-34] area item checklist
- [S-42] player blog (Arena Shop stock); [S-85] eog.gg (Treasure Hunt, merchant timing, item values: [data/item-values.json](../data/item-values.json)); [S-87] official Handbook Vol. 2 (Vendor Booth)
- Rules R-011, R-057, R-093, R-103, R-110, R-114, R-116, R-120, R-121, R-125, R-128, R-134, R-147, R-151, R-153, R-157, R-167; observed stock in [docs/shop-tables.md](../../docs/shop-tables.md)
