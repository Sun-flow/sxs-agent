# Gacha and pull systems

<!-- index: Read before any pull or spin: which gacha uses which currency, known rates and pity, and when to pull or save -->

> **Summary:** Four pull systems matter: Prayer (skills; Stellatie, Covenite, Affection Tokens), the Aeonic
> Gacha (relics; Auroral Badges), the Fantomon summon (Bond Trinkets, Summon Crystals) and the Wheel of Destiny
> (Lucky Tickets). F2P plan: pull relics early in every season up to about 70% of the pool, stop pulling skills
> before a new class tier and save for it, and save Summon Crystals for a Mythic Fantomon plus its duplicate
> [S-01, S-02].
> **Applies:** all seasons
> **Related:** [Relics](relics.md), [Fantomons](fantomons.md), [Skills](skills.md), [Currencies](currencies.md),
> [Shops](shops.md), [Events](events.md), [Guild](guild.md), [Seasons](seasons.md),
> rules R-043, R-093, R-096, R-097, R-114, R-147, R-167

## Overview

| Gacha | Where | Gives | Currency (per pull) | Bot policy |
|---|---|---|---|---|
| Prayer: Standard | Goddess Statue furniture at Home | Skills (Techniques, Charms) and skill shards from the pool your current class can use (its own tier plus the lower tiers of its line) | Stellatie (1 per prayer, x10 = 10) | Only mae's pull script, x10 only (R-093) |
| Prayer: Affection | Same statue, banner selector | "Rewards", not itemised by any source ❓ [S-80] | Affection Tokens (x10 = 250) | Not used (R-093) |
| Prayer: Premium | Same statue, after clearing Verdantglade and the second-tier class change [S-85] | Skills of your current class only | Covenite | Not seen yet |
| Aeonic Gacha: Kingdom | Stone left of the Cart at Home | Relics of one kingdom pool | Auroral Badges of a tier (10 per draw, x10 = 100) | x10 whenever affordable with badges or tickets; never Dawnium (R-167) |
| Aeonic Gacha: Element | Same, Element tab | Relics of one chosen element | Auroral Elemental Badges (10 per draw) | Same rule |
| Fantomon summon | Arborisfatum (tree at Home), from Lv 51 (R-011; Lv 50 per [S-87][S-85]) | Fantomons, shards, ability food, Summon Crystals | Bond Trinkets | No rule yet |
| Wheel of Destiny (Lucky Wheel) | Lucky Wheel structures on the map | A prize from the wheel | First spin per wheel free; then Lucky Tickets | Only the free first spin (R-147) |
| Dawnstar Prelude | Thrilling Events > Featured | Gacha draws; contents unknown ❓ | ❓ | Never (R-096) |

Sources for the table: R-093, R-096, R-147, R-167, [S-25] (currency definitions), [S-03] (Arborisfatum).
Event-only draws also exist (e.g. launch "Prize Punch" using Overture Tickets [S-03]); see [Events](events.md).

## Prayer (skills)

### Screen and basics
- The Prayer screen has tabs Prayer / Exchange / Goals, a banner selector, a daily counter "Prayers Today
  n/10000", a "200 Prayers Bonus" and a pity counter (R-093).
- **200 Prayers Bonus:** after 200 prayers you choose a Legendary skill (R-093); S-20 describes it as a
  selectable Legendary T1 skill ❓.
- Goals tab ("Prayer Goals" [S-80]): "Total Standard Prayers" milestones at 10, 20 ... 60 are free claims; the
  10-prayer one paid 3 Iron Hammers (R-093). The milestone rewards change over time [S-80].
- What you can draw depends on your class [S-25]. The pool holds 238 player skills: 85 Legendary, 78 Epic,
  75 Rare, 47 of the Legendaries being attack skills [S-25][S-80] ❓. Other counts: 361 skills in eog's database
  (all classes and tiers) [S-85]; "300+" in the publisher's launch post [S-87]. Changing class before Lv 100 (before Aqualis) locks the old class's skills and forces
  re-pulling; "Class Rollback" exists to shrink the pool and re-pull low-tier skills [S-03]. See
  [Skills](skills.md) and [Classes overview](classes-overview.md).

### Banners

| Banner | Currency | Pool | Unlock | Sources |
|---|---|---|---|---|
| Standard | Stellatie | Skills your current class can use: its own tier plus the lower tiers of its line (a Class Rollback shrinks it) | From the start | R-093, [S-25], [S-03] |
| Affection ("Friend Prayer") | Affection Token (red token) | "Rewards" ❓; no rate table published | Visible from the start | R-093, [S-25], [S-80] |
| Premium | Covenite | Skills of your **current class** only ("featured pool" [S-80]; each new class has its own premium pool, selectable [S-85]) | After clearing Verdantglade **and** making the second-tier class change (Lv 44 [S-85]), which puts you in Cinder Ridge ❓ | [S-25], [S-20], [S-85] |

- Affection Token income, two readings, both tier C and not exclusive ❓: Affection gained from praying
  ("summons") is capped at 1,000 per week [S-24][S-85]; partying in daily events pays tokens, more with friends
  or guildmates [S-42] (see [Guild](guild.md)). At 250 tokens per x10 (R-093) the cap would be 40 Affection
  prayers a week ❓.
- **Covenite** is the skill selection ticket that pays for the Premium banner: "Goddess Prayer, for skills of
  your current class" [S-25]. It comes from Molly's Deals, Wheel of Destiny prizes [S-01], Chaos Invasion
  rewards [S-03] and the Arena Shop (500 Arena coins, limit 1) [S-42]. Other reading: eog calls it a currency
  earned from Standard pulls that cannot be bought with Dawnium [S-20][S-85]; SOF (tier B) outranks eog
  (tier C/D), so this page follows [S-01].

### Rates and pity

| | Legendary | Epic | Rare | Common shard | Source |
|---|---|---|---|---|---|
| Per-pull rates, version A | 1% | 7% | 22% | (rest) | [S-20][S-85] ❓ |
| Per-pull rates, version B (Standard and Premium share them) | 2.41% | 7.9% | 24% | 65.69% | [S-25][S-80] ❓ |
| Pity | 70 pulls | 30 pulls | 10 pulls | | [S-20][S-85] ❓ |

The two rate tables disagree (version B may include pity); both are tier C, a second reading of each site
gave the same numbers, and neither is confirmed in game. zeroluck states no pity or cost per pull [S-80]. All
banner tables: [data/gacha-rates.json](../data/gacha-rates.json). The pity counter is
said to be account-wide and to survive a class change ❓ [S-20].

### Where Stellatie comes from

| Source | Amount / price | Reference |
|---|---|---|
| Daily Sign-in | 10 a day | R-093, R-097 |
| Vendor Booth, General tab | 1 for 3.15K Rolla (discount badge) | `docs/shop-tables.md` |
| Vendor Booth, Vault tab | x2 for 100 Dawnium (50% badge), limit 1 | `docs/shop-tables.md`; "check the Vault for discounted Stellaties" [S-03] |
| Guild Shop | 500 Guild Tokens each, limit 3 a week | R-114 |
| Kingdom Shop (Hermes, Drasilgard) | 100 Leaves (limit 1) and 600 Leaves (limit 2) | `docs/shop-tables.md` |
| Molly's Deals | Discounted; up to 10 deals a week across friends' homes | [S-01] |
| Quests, chests, wheels, mail | E.g. "Reach Lv. 20" quest, map chests (x2), free Lucky Wheel spin (x5), Mailbox (x10) | R-147, R-168 |
| Extra Vendor Booth refreshes | More Stellatie and Bond Trinkets per refresh (the "Rolla strategy") | [S-01] |
| Gift codes | Small amounts ❓ | [S-04] |

Covenite sources: Molly's Deals, Wheel of Destiny (third priority prize) [S-01]; Chaos Invasion ranking
rewards [S-03]; Arena Shop [S-42]. Affection Tokens: from praying ❓ [S-24][S-85] and from partying ❓ [S-42].

### Skill Shard Vouchers
- Not a pull, but the companion item to Prayer: vouchers convert into shards of a chosen skill. SOF calls them
  "one of the most important items in the game" and the **top Wheel of Destiny prize** [S-01].
- Spend them only on skills that stay in your kit across class tiers (some Techniques and Charms persist),
  never on skills that the next tier replaces [S-01]. Hold early vouchers for third tier and beyond ❓ [S-20].

## Aeonic Gacha (relics)

Also written "Aeonique" on French-derived pages [S-04]. Full relic rules: [Relics](relics.md).

- A "time-frozen gacha machine" at Home that draws relics with **Auroral Badges**; unlocking it is free and its
  first quest pays 50 badges (R-167).
- Tabs Kingdom / Element / Goals. Verdantglade's kingdom banner is "Sylvan Relics". Draw x1 = 10 badges, Draw
  x10 = 100 badges; "Gacha Draws Today n/10000"; guaranteed Rare in 10 on the Rare tier (R-167).
- Duplicates arrive as 3-shard bundles; new relics need Activate at the Workbench (R-167, R-172).
- Goals tab: "Kingdom Gacha Draws" rows at 10/20/30 with free claims (R-167).
- Loong Haven has two pools (Celestial Crafts from day 1, Ethereal Oracle about a month later) [S-02].

### Badge types

| Badge | Draws | Sources |
|---|---|---|
| Rare Auroral Badge | 10 = one capsule from the Rare Aeonic Gacha | [S-25], R-167 |
| Epic Auroral Badge | 10 = one capsule from the Epic tier | [S-25], R-167 |
| Legendary Auroral Badge | 10 = one capsule from the Legendary tier | [S-25] |
| Mythic Auroral Badge | 10 = one capsule from the Mythic tier | [S-25] |
| Auroral Elemental Badge | 10 = one capsule of your chosen element (Fire, Water, Wind, Light, Dark) | [S-25] |
| Pull tickets | Counted on the gacha screen's ticket counter; usable instead of badges | R-167; "tickets saved" for pool 2 [S-02] |

### Base rates per tier (database table, read twice with the same numbers; not checked in game) ❓ [S-25][S-80]

| Tier | Relic of tier | Relic one tier up | Shards |
|---|---|---|---|
| Rare | Rare relic 12.46% | Epic relic 1%, Legendary relic 0.12% | Rare shard 73.55%, Epic shard 11.03%, Legendary shard 1.84% |
| Epic | Epic relic 12.46% | Legendary relic 1%, Mythic relic 0.12% | Epic shard 69.87%, Legendary shard 13.79%, Mythic shard 2.76% |
| Legendary | Legendary relic 16.63% | Mythic relic 1.09% | Legendary shard 68.09%, Mythic shard 14.19% |
| Mythic | Mythic relic 18.68% | | Mythic shard 81.32% |
| Elemental (any element) | Epic 79.11%, Legendary 16.63%, Mythic 4.26% | | |

Every tier costs 10 badges per capsule; the site states no pity [S-80]. Machine-readable copy:
[data/gacha-rates.json](../data/gacha-rates.json). Higher tiers guarantee a higher minimum rarity [S-25]. The Elemental tier never gives Rare results, which is
why SOF ranks "auroral elemental badges" above "Legendary auroral badges" on the Wheel of Destiny [S-01].

### Where badges come from

| Source | Reference |
|---|---|
| Gacha unlock quest (50), Mailbox (50 Rare), gacha Goals | R-167, R-168 |
| Guild Shop: Rare Auroral Badge x10 for 400 tokens, limit 3 a week (guild Shop Lv 2) | R-114 |
| Molly's Deals: "relic gacha badges" at a discount | [S-01] |
| Wheel of Destiny: elemental badges (2nd priority), Legendary badges (3rd) | [S-01] |
| Grand Treasure Hunt Level 4: Legendary Auroral Badges (default pick) ❓ | [S-23] |
| Chaos Invasion ranking rewards: Legendary Auroral Badges | [S-03] |
| Gift codes (Legendary, Epic and Rare badges) ❓ | [S-04] |
| Dawnium (the "relic gamba" SOF invests in for long-term strength) | [S-01]; forbidden to the bot by R-167 |

## Fantomon summon (Arborisfatum)

Full Fantomon rules: [Fantomons](fantomons.md).

- Unlocks with the Fantomon system: Lv 51 on our account (R-011, tier A); the publisher and eog say Lv 50
  [S-87][S-85][S-03]. Currency: **Bond Trinket** ("summoning Fantomons at
  Arborisfatum") [S-25].
- Each pull can drop a **Summon Crystal**: about 4.2% per pull [S-85], at least one guaranteed per 10-pull ❓ [S-20, S-24].
- Summon Crystal exchange shop: a Mythic costs 60 [S-85] (Summon Crystals buy Mythics [S-87]): Nyxarchon 60,
  Aegiswing 60, a rotating Legendary (Sylvaerie) 18 ❓ [S-20, S-26]; evolution needs 120 shards [S-85];
  the exchange shop sells the duplicate needed for Adult evolution [S-02]; Pandarial joins on day 46 of
  Season 2 [S-02].
- Budget for one Adult Mythic: 2 copies = 120 Summon Crystals, at most about 600 pulls for the first 60 ❓ [S-20].

| Published rates | Top rarity | Next | Rest | Source |
|---|---|---|---|---|
| Version A | "SSR" 0.8% | "SR" 5% | 94.2% | [S-04] ❓ |
| Version B | Mythic 0.8% | Legendary 5% | Epic 30%, Rare 64.2% | [S-26] ❓ |
| Version C (item table) | Legendary Fantomon 1.96% | Epic Fantomon 6.37% | Legendary shard 13.27%, Epic shard 7.96%, "Legendary other" 12.04% (unexplained), Epic ability food 14.16%, Rare ability food 44.24% | [S-25][S-80] ❓ |
| Pity | Legendary at 80 pulls | | | [S-20] ❓ |

The three tables disagree on names and numbers; all agree the best direct drop is rare (about 1-2%) and that
Summon Crystals are the reliable route to a Mythic.

Bond Trinket sources: Guild Shop (400 tokens, limit 2 a week, guild Shop Lv 3; R-114), Vendor Booth [S-01],
Wheel of Destiny (3rd priority) [S-01], Mailbox (R-168), Grand Treasure Hunt Level 4 option ❓ [S-23],
Delegate Tasks and Arena shop ❓ [S-20], gift codes ❓ [S-04].

## Wheel of Destiny (Lucky Wheel)

- Lucky Wheel structures on the map open "Wheel of Destiny". The first spin on each wheel is free while its
  zone is below 100%; later spins cost **Lucky Tickets** (R-147). A free spin gave Stellatie x5 and counted
  toward the zone's exploration (R-147).
- Lucky Ticket source: Guild Shop, 1.5K Guild Tokens, limit 1 a week (R-114); extra tickets are also a wheel
  prize [S-01].
- Prize priority when choosing what to go for [S-01]:

| Priority | Prizes |
|---|---|
| 1 | Skill Shard Vouchers |
| 2 | Gateway Keys, Auroral Elemental Badges |
| 3 | Legendary Auroral Badges, Covenite, Bond Trinkets |
| 4 | Legendary Fantomon resources (wool, egg, essence), 2888 Dawnium, additional Lucky Tickets |

- How prizes are selected on the wheel (fixed list, pick-your-pool, or per-wheel) is not described ❓.
- Tier D pages use "Wheel of Destiny" for Destiny Fruit exploration; that is a different thing
  ([Relics](relics.md#destiny-fruits)) [S-04].

## Dawnstar Prelude

- A card in Thrilling Events > Featured that offers gacha draws (R-096). The bot never touches it (R-096,
  R-043). No guide or wiki we could read describes its pool, currency or rates ❓.

## Rates and pity at a glance

| System | Known guarantee | Confidence |
|---|---|---|
| Prayer | Rare within 10, Epic within 30, Legendary within 70; Legendary of choice at 200 prayers | 200 bonus: R-093; pity numbers ❓ [S-20] |
| Aeonic Gacha | Rare-tier: a Rare relic within 10 draws; higher tiers raise the minimum rarity | R-167; [S-25] ❓ |
| Fantomon summon | 1+ Summon Crystal per 10-pull; Legendary within 80 | ❓ [S-20] |
| Wheel of Destiny | None known | |

## F2P pulling advice

### When to pull, when to save

| Resource | Rule | Why | Source |
|---|---|---|---|
| Auroral Badges, relic tickets | **Pull early in each season**, in the new kingdom's pool, until about 70% completion; then slow down | A fresh pool gives a new relic on most pulls; relics are permanent and resonance is the biggest early-season power | [S-01], [S-02] |
| Relic pulls for Loong Haven pool 2 | Save tickets for its opening about a month in; fill it slowly | By mid-season Dawnium should go to Material Realms instead | [S-02] |
| Stellatie, Covenite | **Stop pulling skills before a new class tier; save for it** (SOF: "Stop pulling skills, save pull resources for T4"; T4 unlocks at Lv 106) | Most skills become obsolete at a new class tier | [S-01], [S-02] |
| Stellatie early game | Use the free daily Stellatie; aim pulls at the 200-prayer Legendary pick rather than buying extra | The 200 bonus is the only guaranteed Legendary of choice | R-093; [S-20] ❓ |
| Skill Shard Vouchers | Hold for skills that persist across tiers | Same reason | [S-01] |
| Bond Trinkets | Buy weekly from the Guild Shop; pull to collect Summon Crystals | Crystals buy the Mythic and its duplicate | [S-01]; [S-20] ❓ |
| Summon Crystals | Save 60 for your role's Mythic, 60 more for the duplicate (Adult at Lv 108); in Season 2 buy one duplicate, then save for Pandarial | Adult evolution is a large power jump | [S-02] |
| Lucky Tickets | Spin for the priority list above | | [S-01] |

- Tier D extras ❓: pull T1 skills only until class level 17, then save for T2 [S-04]; do not start Fantomon
  pulls before Lv 50 [S-04]; do not spend Summon Crystals on the 18-crystal Legendary [S-20].

### Dawnium and gacha
- Spending free Dawnium is allowed in our strategy; real money is not.
- SOF's two basic uses of F2P Dawnium: (a) extra Material Realm tools for power this season, (b) the relic
  gacha ("relic gamba") for long-term account strength; balance the two [S-01].
- SOF's ideal daily plan of 2,000 Dawnium (in priority order) has **no gacha line**: Daily Dungeon refresh x2
  (250), Material Realms 4/2/4/4 (1,080), Guild donations 3 times plus Gold Tool (270), Vault (400) [S-01].
  Gacha Dawnium is on top of that or replaces lower lines. The Vault line can be discounted Stellatie.
- Season rhythm [S-02]: early season -> Dawnium into the relic gacha; as the pool saturates and mid-season
  approaches -> heavy Material Realm priority.
- End of Season 1 advice: "Invest in Relic Gacha (ideally 70% completion in each region)" and stop pulling
  skills [S-01].
- Never buy Dawnstar Prelude draws, Prayer "+" tickets or Aeonic draws with Dawnium unless mae changes
  R-043/R-093/R-167; the guide-versus-rule gap is recorded in [conflicts](../conflicts.md).

## Open questions
- ❓ Dawnstar Prelude: what it draws, its currency, whether any part is free.
- ❓ Live rates and pity for all three main gachas (in-game "details" pages would settle the disagreements
  above; zeroluck and eog each repeat their own set).
- ❓ What the Affection banner's "rewards" are, and which Affection Token income (praying cap or partying) is real.
- ❓ Premium (Covenite) banner: cost per pull; confirm the unlock (Verdantglade cleared plus second-tier class) in game.
- ❓ Bond Trinket cost per summon; Dawnium prices of Stellatie, badges and Bond Trinkets outside discounts.
- ❓ How the Wheel of Destiny prize list is chosen and its odds.

## Sources
- [S-01] Permanent vs Seasonal recommendations; Dawnium page (daily spend infographic); Additional Tips (Molly's Deals, Skill Vouchers, Wheel of Destiny)
- [S-02] Sections IV to VI (T4 at Lv 106, relic pools, Fantomon exchange shop, Dawnium rhythm)
- [S-03] Fandom "Fantomon", "Vendor Booth", "Everything About Class Change", "Journey Overture", Chaos Invasion guide
- [S-04] sword-x-staff.wiki gacha, Fantomon, voucher and Wheel of Destiny pages (leads only)
- [S-20] [S-23] [S-24] EOG.GG pages; [S-25] zeroluck.gg summoning and currencies; [S-26] BlueStacks Fantomon guide
- [S-80] zeroluck.gg second reading (rates, Prayer Goals, badge cost): [notes](../sources/notes/zeroluck.md); [S-85] eog.gg section: [notes](../sources/notes/eog.md); [S-87] official site posts; [S-42] player blog (Arena Shop, Affection)
- Rules R-043, R-093, R-096, R-097, R-114, R-147, R-167, R-168, R-172; `docs/shop-tables.md`
