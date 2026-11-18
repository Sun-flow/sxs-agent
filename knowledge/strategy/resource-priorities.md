# Resource priorities: where each resource goes

<!-- index: Read when holding a resource and deciding what to spend it on: one row per currency or material, with the order of uses and what never to use it for -->

> **Summary:** one table. Find the resource, read its uses left to right, stop at the first one that is
> available. The last column lists what to keep away from.
> **Applies:** all seasons
> **Related:** [Currencies](../systems/currencies.md), [Shops](../systems/shops.md), [Dawnium plan](dawnium-plan.md),
> [Stamina and Material Realms](stamina-and-realms.md), data in [currencies.json](../data/currencies.json)

| Resource | First use | Then | Then | Avoid | Source |
|---|---|---|---|---|---|
| Dawnium | Guild donations 2 and 3; discounted Vault tools | Daily Dungeon refreshes; realm tools (2222, then 4244) | Molly's Deals; relic gacha early in a season | Real-money items, Catch Up, cosmetics, donations 4 and 5 | [Dawnium plan](dawnium-plan.md) |
| Rolla | Rank Advancement | Gear enhancement; Cart upgrades | Vendor Booth General: Wood, Stone, Quest Scrolls, discounted Stellatie | Refresh spam unless following the "Rolla strategy" | [R-118][S-03][S-01] |
| Stamina | Commissions | Sand (season start) or ore (later) | Battle Essence | Sitting at the cap | [Stamina plan](stamina-and-realms.md) |
| Raw Ore, Refined Ore | Gear bands, lowest piece first | Gear Resonance tiers | - | One piece far ahead of the others | [R-092] |
| Battle Essence | Quick Upgrade of the equipped loadout | Skills of the second element loadout | - | Skills you will not equip | [R-104] |
| Chrono Sand | Resonance of the class element | All five elements to the season cap | - | Levels above the cap late in a season (they reset) | [S-01] |
| Wood, Stone | Cart: every row to Lv 10 [S-87], then the Stone and Wood rows | Other rows, then furniture | Store for next season's new Cart levels once capped | - | [S-01][R-136] |
| Stellatie | Standard Prayer x10 | Save in the weeks before a new class tier | - | x1 pulls | [R-093][S-01] |
| Covenite (skill selection ticket) | Premium Prayer for the current class | Save before a new tier | - | Pulls just before a tier change | [S-01] |
| Skill Shard Vouchers | Skills that survive class tiers, up to a quality step | - | - | Tier 1 and Tier 2 skills | [S-01] |
| Auroral Badges, Elemental Badges (10 per capsule [S-80]) | Aeonic Gacha x10 in the newest pool, to about 70% of it | The class element with Elemental Badges | Destiny Fruits for the missing relics | Draws below x10 | [R-167][S-02][S-85] |
| Destiny Fruits | Destiny Exploration in the current region | - | - | - | [Relics](../systems/relics.md) |
| Kingdom currency (Abundance Leaves ...) | Kingdom tools that open statue areas | Gateway Keys | Other stock | Anything before the tools | [S-01] |
| Guild Tokens | Fantomon aptitude materials, summon tokens | Lucky Ticket ❓ | Other stock | - | [S-01] |
| Arena coins | Fantomon shards | Covenite (500, limit 1) | Bond Treat, Rare Auroral Badges | - | [Arena and PvP](../systems/arena-and-pvp.md) |
| Summon Crystals | One duplicate to make the Main Fantomon Adult (Lv 108) | Save for Pandarial | - | Buying a second Mythic from scratch | [S-02] |
| Bond Trinkets | Fantomon summons | - | - | - | [Fantomons](../systems/fantomons.md) |
| Fantomon aptitude materials | The Main Fantomon | The two Subs of other types | - | The Sub that shares the Main's type | [S-01] |
| Companion gifts | The companion that favours that gift, in the order all-to-20, class-match-to-50, all-to-50 | - | - | Non-favoured gifts | [S-01] |
| Aurodrasil Energy (Treasure Hunt) | Lucky Statue and Primal Gem on MUST BUY weeks: the Level 5 left item | Level 5 far right, then middle | Level 4 Legendary Auroral Badges or Bond Trinkets | Spending on SAVE weeks; Stellatie | [S-01][S-85] |
| Chaos Crystals (Chaos Invasion) | Primal Forge, every event until Immortal | - | - | Everything else in that shop | [S-01][S-85] |
| Lucky Tickets (Wheel of Destiny) | Spin; choose vouchers, keys, elemental badges | - | - | - | [S-01] |
| Temporal Crystals, free speed-up (2 hours of Bed and Cart each) | After new statues are lit; in a new season at the Lv 106, 108, 116, 130 milestones | - | - | Before the statues; before a season change | [S-02][S-87][S-85] |
| Material Realm tools | See the use-or-save table | - | - | Using a stockpile below the top rank without need | [Stamina plan](stamina-and-realms.md) |
| Kingdom tools (Withering Potion, Magic Drill, Water Mine, Gateway Key) | The blockade hiding the most statues (the two-statue Magic Drill spot in Verdantglade first) | - | - | - | [S-01] |
| Divinecraft Stones (Season 2+) | Re-roll Mythic or Divine gear of a seasonal dungeon for 1 or 2 good lines | - | - | Chasing 3 or 4 lines | [S-02] |
| Gems | Slot the recommended colours | Sell white and black | Combine with the pity trick above tier 5 | Buying before prices fall | [S-01][S-02] |
| Spare dungeon shards and gear | Keep pieces with drop-bonus lines or top affixes | Sell on the market | Dismantle (stones, ore) | Holding shards across a season end | [S-01][S-02] |
| Permanent dishes | Eat up to 10 of each recipe (full value); the count is per recipe, so spread | 11 to 30 at half value | 31 to 50 at 20%; sell the rest | Eating 50+ of one dish (5%) | [S-31][S-85] |
| Golden Beetle | Keep (puzzles are skipped) | - | - | Spending | [R-153] |
| Luminium, Vouchers | Never bought | - | - | Real money | [R-121] |

## Pull odds behind the pull rows

Published rate tables, all from one database site [S-80] unless tagged; none confirmed in game. Data:
[gacha-rates.json](../data/gacha-rates.json).

| Banner | Best result | Next | Rest | Advice it supports |
|---|---|---|---|---|
| Standard and Premium Prayer | Legendary skill 2.41% (eog: 1%, pity 70 [S-85]) | Epic 7.9%, Rare 24% | shards 65.69% | x10 only; save for the pool you want |
| Aeonic Gacha, Rare badges | Legendary relic 0.12% | Epic relic 1%, Rare relic 12.46% | shards | Cheap completion of the low tiers |
| Aeonic Gacha, Epic badges | Mythic relic 0.12% | Legendary 1%, Epic 12.46% | shards | - |
| Aeonic Gacha, Legendary badges | Mythic relic 1.09% | Legendary 16.63% | shards | The badge to hunt for in shops and wheels |
| Aeonic Gacha, Mythic badges | Mythic relic 18.68% | - | Mythic shards 81.32% | - |
| Aeonic Gacha, Elemental badges | Mythic 4.26% | Legendary 16.63%, Epic 79.11% | none | Every pull is a whole relic of the chosen element: best badge for the class element |
| Fantomon summon | Legendary Fantomon 1.96% (eog: top rate 0.8%, Legendary pity 80 [S-85]) | Epic Fantomon 6.37% | aptitude food and shards | Summon Crystals drop at 4.2% a pull, at least 1 per x10 [S-85] |

No source states a relic pity. SOF's rule stands: pull to about 70% of a pool, then stop [S-01].

## Sources

- [S-80] rate tables, capsule cost; [S-85] Treasure Hunt order, food brackets, speed-up milestones; [S-87] official
  handbook
- [S-01], [S-02], [S-03], [S-31]; rules R-092, R-093, R-104, R-118, R-121, R-136, R-153, R-167
