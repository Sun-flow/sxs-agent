# zeroluck.gg notes (Sword x Staff section)

<!-- index: Page-by-page facts from zeroluck.gg's Sword x Staff section (classes, banner rates, gear costs, bestiary, stats, life skills, codes) and which knowledge page each one fills -->

> **Summary:** zeroluck.gg is a database-style site that says its numbers come from the game's own data. Its 14 Sword x Staff pages give exact banner rate tables, class base-stat weights and promotion gates, a gear quality ladder with enhancement costs up to +250, the game's monster taxonomy (275 entries), the list of 20 combat stats, guild facility yields and a 16-code list. It has counts but almost no per-item rows (no relic, gem, set, recipe or pet tables), no unlock levels and no costs per pull.
> **Applies:** all seasons (base data tables; not a snapshot of any live banner or season)
> **Related:** [gacha](../../systems/gacha.md), [skills](../../systems/skills.md), [gear](../../systems/gear.md), [relics](../../systems/relics.md), [fantomons](../../systems/fantomons.md), [monsters](../../systems/monsters.md), [guild](../../systems/guild.md), [cooking](../../systems/cooking-and-dishes.md), [classes overview](../../systems/classes-overview.md), [codes](../../systems/codes.md), [provenance](../provenance.md)

All facts on this page carry [S-80] (zeroluck.gg as a whole) unless another tag is shown. Earlier pages cite single
zeroluck pages as S-10, S-25, S-38 and S-46: same site, same tier.

## How this was read (important for trust)

- Read on 2026-11-18. robots.txt allows `/sword-x-staff/` for general user agents (it blocks only five named SEO
  crawlers and some account paths) and has no Content-Signal line.
- **Direct download failed.** From this environment every `https://zeroluck.gg/sword-x-staff/...` URL answered
  HTTP 404 to curl and to `scripts/kb_fetch.py zeroluck`, and the site's sitemaps list only two other games. No raw
  page or `__NEXT_DATA__` JSON could be cached; `sources/raw/zeroluck/` holds only a manifest of the 404s.
- The same URLs did answer through the WebFetch tool, which returns a small model's reading of the page, not the
  page. Every page below was read that way, most of them twice with different questions; the numbers agreed
  between passes and between pages (for example the Skill Prayer rates on the summoning and reroll pages).
  A reader model can still drop or garble a row, so treat single numbers as tier C and check against the game.
- The reader could not see link targets, so pages that hold the per-item rows (a "Pets database", a "Monsters
  database", an "Items database" with 7,952 items, an interactive map) were named but their URLs are unknown.
- The site uses its own labels in places: "Gear Prayer" for the relic gacha (Aeonic Gacha, paid with Auroral
  Badges), "Pet" and "Companion" for Fantomon, "Treasure" for relic, "Friend Prayer" for the Affection banner,
  "Legend" for Tier 5. This page keeps our terms and gives the site's label once.

## Section map

| Page | URL path under `/sword-x-staff/` | What it holds | Read |
|---|---|---|---|
| Guides index | `guides/` | 13 guide cards in groups Characters, Systems, Gacha, More; tagline says every guide is verified in game | yes |
| Classes | `classes/` | 18 classes, stat weights, promotion gates, 4 sample skills each | yes |
| Companions | `companions/` | Fantomon counts by role and rarity, evolution, Treats | yes (roster rows not visible) |
| Bestiary | `bestiary/` | Monster taxonomy and 37 named monsters | yes |
| Friendship | unknown | NPC friendship tiers, liked gifts, journals, roster (per the index card) | no: URL not found (7 guesses answered 404) |
| Gear | `gear/` | Slots, quality ladder, enhancement costs, Resonance, FAQ | yes |
| Combat stats | `combat-stats/` | 20 stats in four groups | yes |
| Game modes | `game-modes/` | Empty: the page itself says it lists 0 modes | yes |
| Currencies | `currencies/` | 4 wallet currencies, 9 summon currencies, material categories | yes |
| Life skills | `life-skills/` | Guild facilities, yields, cooking counts | yes |
| Reroll | `reroll/` | Reroll verdict and loop | yes |
| Relics | `relics/` | Relic pool counts by stat, relic banners | yes |
| Battle Pass | `battle-pass/` | Pass structure | yes (no per-tier rows visible) |
| Banners | `summoning/` | 13 banners with rate tables | yes |
| Codes | `codes/` | 16 codes, redeem steps | yes |
| Section hub, map | `/sword-x-staff/`, `map/` | - | no: 404 for both readers |

## Classes page

Data is also in [classes.json](../../data/classes.json) (cited there as S-10).

- 18 classes: 2 base classes and 4 lines of 4 promoted classes. The Tier 2 choice fixes the line up to Tier 5.
- Promotion gates. Each class has its own level track; a promotion needs a level in the current class and a
  total of levels across all classes:

| Promotion | Class level | Total level over all classes |
|---|---|---|
| Tier 1 -> Tier 2 | 18 | 20 |
| Tier 2 -> Tier 3 | 16 | 48 |
| Tier 3 -> Tier 4 | 19 | 89 |
| Tier 4 -> Tier 5 | 40 | 180 |

- Stat weights are the game's relative base rates per class, not final values:

| Class | Tier | Line (site's role label) | HP | ATK | DEF | SPD | Class trait | Four sample skills |
|---|---|---|---|---|---|---|---|---|
| Warrior | 1 | - | 900 | 600 | 900 | 600 | - | Edge Strike, Heavy Impact, Lion Combo, Wind Blade Slash |
| Knight | 2 | Guardian line (tank) | 1500 | 900 | 1500 | 1100 | Block | Stunning Strike, Frostbite Blossom, Guardian Ring, Ricocheting Shield |
| Paladin | 3 | Guardian line | 2400 | 1600 | 2400 | 1800 | Block | Lunarwater Threads, Desperate Protection, Star Shattering Slash, Forceful Charge |
| Guardian | 4 | Guardian line | 3400 | 2600 | 3400 | 2800 | Block | Seismic Tide, Swirling Blade, Light Sword Array, Hamper Strike |
| Templar | 5 | Guardian line | 4400 | 3600 | 4900 | 3800 | Block | Last Stand, First Light, Dawnburst, Sacred Shine |
| Duelist | 2 | Berserker line (crit bruiser) | 1000 | 1500 | 1000 | 1500 | Crit Rate | Flash Dash, Fire Slash, Shattering Sigil, Sunset Sword |
| Berserker | 3 | Berserker line | 1700 | 2400 | 1700 | 2400 | Crit Rate | Asura's Grasp, Eclipse Slash, Doom Blade, Hunter's Judgment |
| Conqueror | 4 | Berserker line | 2650 | 3450 | 2700 | 3400 | Crit Rate | Hellfire Requiem, Blade Storm, Soul Piercer, Flickering Blade |
| Ravager | 5 | Berserker line | 3700 | 4400 | 3700 | 4900 | Crit Rate | Air Break, Night Curse, Shattering Dance, Solaris Storm |
| Mage | 1 | - | 500 | 1400 | 500 | 600 | - | Water Shot, Tempest Sphere, Water Assault, Iron Thorn |
| Sorcerer | 2 | Archmage line (burst caster) | 1000 | 1900 | 900 | 1200 | Block Penetration | Flickering Stars, Lightning Chain, Fiery Star Trail, Frosty Nova |
| Archmage | 3 | Archmage line | 1650 | 2950 | 1600 | 2000 | Block Penetration | Divine Wrath, Howling Hurricane, Aqua Vortex, Meteoric Flames |
| Destroyer | 4 | Archmage line | 2700 | 3900 | 2600 | 3000 | Block Penetration | Starlight Burst, Flowing Doom, Wind Blade Spiral, Formation Breaker |
| Magister | 5 | Archmage line | 3700 | 5400 | 3600 | 4000 | Block Penetration | Blast Spirit, Frost Thorn, Crimson Whirl, Storm Rhapsody |
| Sage | 2 | Arcanist line (support, summoner) | 1250 | 1250 | 1250 | 1250 | Crit Avoid, Healing | Radiant Restoration, Treantling Summon, Weakening Hex, Flame Wolf Summon |
| Arcanist | 3 | Arcanist line | 2050 | 2050 | 2050 | 2050 | Crit Avoid, Healing | Abyssal Hand, Mana Blast, Waterling Summon, Shadow of Termination |
| Dominator | 4 | Arcanist line | 3050 | 3050 | 3050 | 3050 | Crit Avoid, Healing | Chaos Rune, Spirit Aegis, Rock Rex Summon, Rejuvenating Rain |
| Prophet | 5 | Arcanist line | 4550 | 4050 | 4050 | 4050 | Crit Avoid, Healing | Thalasson Summon, Soul Reap, Hexed Blast, Desperate Shadow |

- One-line class descriptions: Knight guards allies with shield and block; Paladin adds holy light to defence;
  Guardian fights with ice; Templar is a holy-light wall. Duelist is a fast burst fighter; Berserker turns
  attack into defence; Conqueror runs on battle fury; Ravager is fire spirit. Sorcerer is the area-damage
  specialist; Archmage throws raw elements; Destroyer "creation and destruction"; Magister burns everything.
  Sage heals, controls and summons; Arcanist controls with summons and charms; Dominator leads many summons;
  Prophet is the fate-themed top of the line.
- Not on the page: skill effects, elements, weapons, unlock character levels, a tier list.
- Mage-line reading (ours, from the weights): the Sorcerer line has the highest ATK weight of all lines at every
  tier (5400 at Tier 5) and the lowest DEF; the Sage line is flat across all four stats, with extra HP at Tier 5.

## Banners page (the site's "Summoning")

Data: [gacha-rates.json](../../data/gacha-rates.json).

- 13 banners in four families. The rates are the base per-pull tables; the site warns that featured pools and
  the "Prayer Goals" milestone rewards change over time and are not covered.

| Banner (our name; site label) | Currency | Notes |
|---|---|---|
| Standard Prayer ("Skill Prayer, Standard") | Stellatie | Skills; the pool depends on your class |
| Affection banner ("Friend Prayer") | Affection Token | No rate table on the site |
| Premium Prayer ("Skill Prayer, Premium") | Covenite | Same base rates as Standard, featured pool |
| Fantomon summon ("Pet Prayer") | Bond Trinket | Fantomons, shards and aptitude food |
| Aeonic Gacha Rare / Epic / Legendary / Mythic ("Gear Prayer") | The matching Auroral Badge | Each higher tier raises the lowest rarity it can give |
| Aeonic Gacha Fire / Water / Wind / Light / Dark ("Elemental Gear") | Auroral Elemental Badge (one badge for all five) | Relics of the chosen element |

| Banner | Result | Chance % |
|---|---|---|
| Standard and Premium Prayer | Common skill shard | 65.69 |
| | Rare skill | 24 |
| | Epic skill | 7.9 |
| | Legendary skill | 2.41 |
| Fantomon summon | Rare aptitude food | 44.24 |
| | Epic aptitude food | 14.16 |
| | Legendary Fantomon shard | 13.27 |
| | Legendary "other" (not explained) | 12.04 |
| | Epic Fantomon shard | 7.96 |
| | Epic Fantomon | 6.37 |
| | Legendary Fantomon | 1.96 |
| Aeonic Gacha, Rare | Rare relic shard | 73.55 |
| | Rare relic | 12.46 |
| | Epic relic shard | 11.03 |
| | Legendary relic shard | 1.84 |
| | Epic relic | 1 |
| | Legendary relic | 0.12 |
| Aeonic Gacha, Epic | Epic relic shard | 69.87 |
| | Legendary relic shard | 13.79 |
| | Epic relic | 12.46 |
| | Mythic relic shard | 2.76 |
| | Legendary relic | 1 |
| | Mythic relic | 0.12 |
| Aeonic Gacha, Legendary | Legendary relic shard | 68.09 |
| | Legendary relic | 16.63 |
| | Mythic relic shard | 14.19 |
| | Mythic relic | 1.09 |
| Aeonic Gacha, Mythic | Mythic relic shard | 81.32 |
| | Mythic relic | 18.68 |
| Aeonic Gacha, each element | Epic relic | 79.11 |
| | Legendary relic | 16.63 |
| | Mythic relic | 4.26 |

Every table sums to 100.

- Skill pool: 238 player skills, 85 Legendary, 78 Epic, 75 Rare; 47 of the Legendaries are attack skills.
- Twelve Legendary skills named as examples: Water Assault, Heavy Impact, Lion Combo, Whirlwind Slash, Treantling
  Summon, Blazing Fire Ring, Fiery Star Trail, Wind's Delight, Divine Wrath, Star Shattering Slash, Ricocheting
  Shield, Mountain Collapse.
- Most Prayer pulls give skill shards, which merge into whole skills. Shards per skill: not stated.
- Not on the page: cost per pull, pity or guarantee rules, Prayer Goals contents, unlock conditions, dates.

## Reroll page

- Verdict: optional. Classes are chosen freely, so a reroll only buys a faster start through a good Legendary
  attack skill for the intended line (2.41% per pull).
- Loop: play as a guest or unbound account; clear the tutorial (this opens the Prayer and the mail); claim launch
  mail and codes for free Stellatie and badges; pull; bind the account only when keeping it, otherwise wipe and
  repeat. No pull count or time per loop is given.
- Not relevant to our account (already bound and progressing); recorded for completeness.

## Currencies page

| Currency | Rarity colour per the site | Use per the site |
|---|---|---|
| Rolla | Common | Gear enhancement, ascension, shop purchases |
| Luminium | Legendary | Converted to Dawnium 1:1, or spent directly |
| Dawnium | Epic | Shop purchases; obtained by exchanging Luminium |
| Voucher | Mythic | In-game purchases |
| Stellatie | Legendary | Goddess Prayer, for skills |
| Affection Token | Epic | Affection Prayer at the Goddess Statue, for rewards |
| Covenite | Legendary | Goddess Prayer, for skills of the current class |
| Bond Trinket | Legendary | Summoning Fantomons at Arborisfatum |
| Rare / Epic / Legendary / Mythic Auroral Badge | Rare / Epic / Legendary / Mythic | 10 badges = one capsule from the Aeonic Gacha of that tier |
| Auroral Elemental Badge | Legendary | 10 badges = one capsule of a chosen element |

- Material categories with counts where shown: gear enhancement materials 12 (ore, stones, rank-up plants);
  gems 360; relic materials (universal shards, pieces for ascending and awakening); cooking (ingredients,
  recipes, dishes for the "Alchemy Pot"); Fantomon food (Treats, and essences that activate aptitudes); skill
  materials (Battle Essence, skill shards); guild construction (steel, cells, mana clusters, garden plants);
  monster and sweep drops; furniture materials 2 (stone, wood).
- The item database behind the page holds 7,952 items, 1,868 of them upgrade or crafting materials, and may
  include items not live in every region.
- Not on the page: how any currency is earned, amounts, caps.

## Gear page

Data: [gear-tables.json](../../data/gear-tables.json).

- Counts: 629 equipment pieces, 5 slots, 6 qualities, 28 sets (each with a 2-piece and a 4-piece bonus), 8 gem
  types (the data calls them "Ziwei stars"), 360 gems, 240 Resonance steps. Set and gem names and values are not
  given ("not yet translated").
- Slots: Weapon (Sword or Wand), Helmet, Armor, Boots, Off-hand (Shield, Glove, Book or Ball).
- Quality ladder: quality fixes how many substat lines a piece has and how high each line can roll, as a
  multiplier of the line's base value:

| Quality colour | Example weapon | Substat lines | Roll multiplier |
|---|---|---|---|
| White | Novice's Longsword | 0 | 0.7 to 0.8 |
| Blue | Explorer's Blade | 1-2 | 0.7 to 0.9 |
| Purple | Beastfang Sword | 3 | 0.8 to 1.0 |
| Orange | Stone Blade | 4 | 0.8 to 1.15 |
| Gold | Lavaborn Mech Saber | 4 | 0.8 to 1.25 |
| Red | Soulflare Blade | 4 | 0.8 to 1.25 |

  The site uses colours only. Matching them to the game's rarity names (Epic, Legendary, Mythic, Divine...) is
  not stated; purple = Epic and orange = Legendary would fit the usual scheme (guess).
- Enhancement cost of single levels (per piece), with a data maximum of +250:

| Level | Rolla | Raw Ore | Refined Ore |
|---|---|---|---|
| +1 | 70 | 35 | 0 |
| +5 | 110 | 55 | 10 |
| +10 | 160 | 80 | 30 |
| +20 | 1,160 | 580 | 170 |
| +30 | 2,560 | 1,280 | 310 |
| +40 | 4,160 | 2,080 | 330 |
| +250 | 200,000 | 100,000 | 550 |
| Total +0 to +250 | 17,402,400 | 8,701,200 | 22,280 |

  Rolla is always twice the Raw Ore. Levels between the listed ones are not given.
- Resonance: every 5 gear levels adds a step that gives a flat +20% to one stat, cycling HP, ATK, DEF, SPD
  (level 5 HP, 10 ATK, 15 DEF, 20 SPD, 25 HP ...), 240 steps in the data. The page does not say what the 20% is
  a share of, nor whether all five pieces must reach the level; it only advises levelling all slots evenly.
  Our own observation is a small bonus per band (R-092, [gear](../../systems/gear.md)), so read "+20%" with care ❓.
- Advice in its FAQ: enhance white and blue pieces only as a stopgap; aim for orange or better (4 lines); a
  4-piece set usually beats five unmatched stronger pieces; +250 is an endgame goal.

## Combat stats page

Data: [combat-stats.json](../../data/combat-stats.json). 20 stats, with the game's English labels:

| Group | Stat | What it does |
|---|---|---|
| Core | HP | Health; set by class, raised by gear and Fantomons |
| Core | ATK | Base damage before crit, element and damage-boost multipliers |
| Core | DEF | Lowers damage taken |
| Core | SPD | Turn order and how often a unit acts |
| Offence | Crit Rate | Chance to crit |
| Offence | Crit DMG | Extra damage of a crit |
| Offence | DMG Boost | Percentage increase to all damage dealt |
| Offence | Effect Hit Rate (data name "Base Effect Hit Rate") | Chance that debuffs and status effects land |
| Offence | PvP Bonus DMG | Extra damage against players |
| Offence | PvE Bonus DMG | Extra damage against monsters |
| Defence | Block Rate | Chance to block a hit and reduce it |
| Defence | Block Efficiency | How much a block removes |
| Defence | Crit RES | Lowers the enemy's chance to crit you |
| Defence | DMG RES | Percentage reduction of all damage taken |
| Defence | Resilience | Described as companion sturdiness against burst and control |
| Defence | Effect RES (data name "Base Effect RES") | Resists debuffs and status effects |
| Defence | PvP DMG RES | Less damage from players |
| Defence | PvE DMG RES | Less damage from monsters |
| Utility | Accuracy | Counters the enemy's Block Rate |
| Utility | Healing Boost | Stronger heals; has no icon in game |

- The page says the power-rating formula is not public, and gives no formulas, caps or element chart.

## Bestiary page

Data: [monsters.json](../../data/monsters.json).

- 275 entries in the game's monster data, including player-side units (14 player summons, 12 player Fantomons).
- The game's own type labels:

| Type label | Count | Meaning |
|---|---|---|
| Minion Monster | 159 | Common field monsters |
| Elite Monster | 67 | Tougher named field monsters |
| Boss | 39 | Stage and zone bosses |
| Hieromon | 9 | The sacred-beast bosses of the Crucible of Hieromon |
| Boss (own type) | 1 | Chaos Tyrant |

| Attack profile (data label) | Range | Count |
|---|---|---|
| Near Weak | Melee | 78 |
| Near Strong | Melee | 70 |
| Far Weak | Ranged | 81 |
| Far Strong | Ranged | 46 |

| AI behaviour | Count |
|---|---|
| Standard hostile | 217 |
| Summoned by an enemy during a fight | 20 |
| Triggered by the player coming close | 12 |
| Player summon | 14 |
| Player Fantomon | 12 |

- Named monsters (a sample per type, each with its range):
  - Minion Monster: Wind Slime (melee), Fire Slime (melee), Water Slime (ranged), Light Slime (ranged), Dark
    Slime (melee), Sylvanwolf Bruiser (melee), Sylvanwolf Flinger (ranged), Boar (melee), Stink Bomb (ranged),
    Waterflow Spider (ranged), Saber Rabbit (melee), Sickle Mantis (melee).
  - Elite Monster: Sylvanwolf Rider (ranged), Shielded Sylvanwolf Warrior (melee), Sylvanwolf Shaman (ranged),
    Water Slime King (melee), Fire Slime King (melee), Wind Slime King (ranged), Two-Headed Troll (melee),
    Colossal Waterflow Spider (melee), Bear Warrior (melee), Boar King (melee).
  - Boss: Golem (melee), Sylvanwolf Chieftain (melee), Corrupted Guardian (melee), Spider Queen (melee),
    Dimensional Golem (ranged), Polyhedral Sun (ranged), Bovine Titan (ranged), Cyclopean Geocrusher (ranged).
  - Hieromon (6 of 9 named): Storm Griffin (melee), Flamoenix (ranged), Yamata no Orochi (ranged), Primordial
    Loong (ranged), Lord of Decay (ranged), Lord of Ruin (melee).
  - Chaos Tyrant (melee).
- "Light" and "heavy" for Weak and Strong is the site's reading, not a game rating. The data has no element,
  level, stats, location or drops, so nothing here says which monster is strongest.

## Companions page (Fantomons)

- 13 Fantomons: 4 Attacker, 4 Tank, 5 Support (the role labels are the game's). 6 are Legendary and 4 Epic; the
  rarity of the other 3 is not stated. 12 of 13 evolve from Childhood to Adulthood, which upgrades the model,
  stats and skill quality. The player-Fantomon count in the bestiary is 12.
- Each has an ability tree whose nodes open as it levels. EXP comes from Treats in three grades: Basic, Premium,
  Deluxe. Fantomons come from the Bond Trinket summon.
- Not readable: the roster itself (names, role and rarity per Fantomon), EXP values, evolution level.

## Relics page

- 855 relic pieces across 6 regions (regions not named); relic level and star both max at 6. Levelling grows one
  main stat; starring grows an elemental line, either Affinity (damage dealt with that element) or Aegis
  (resistance to it).
- Relics per main (level) stat: SPD 66, ATK 65, DEF 65, HP 65, DMG RES 20, DMG Boost 19, Crit Rate 15, Crit RES 14.
- Relics per star stat (top eight shown): Water Affinity 87, Light Aegis 86, Dark Affinity 86, Wind Affinity 86,
  Fire Affinity 86, Light Affinity 85, Wind Aegis 85, Water Aegis 85. The first list sums to 329, so most of the
  855 pieces are not in it (perhaps other stats, perhaps shards or variants: not explained) ❓.
- 75 relics carry an extra bonus that grows as a gameplay task is completed; many of them name a gear slot:
  Boots 9, Weapon 9, Helmet 6, Armor 5, Off-hand 2. The tasks are not listed.
- Nine relic banners: four rarity tiers and five elements (see the banners section).
- No relic names: the site says the names are still in the source language.

## Battle Pass page

- A pass has 70 tiers with a free and a premium reward on each. Pilgrimage Points from normal play move the pass
  forward; one tier can be bought for 100 Dawnium. Buying the premium lane later pays out every premium reward
  already passed.
- The data holds 16 permanent "Normal" passes and 4 rotating "Season" passes, plus limited event passes the site
  leaves out (one of them an unreleased crossover).
- Headline rewards: a Legendary Relic on Normal passes; on Season passes a Legendary Fantomon of the player's
  choice. The site calls the premium lane good value for a daily player (real money: not for our account).
- Not readable: per-tier rewards, points per tier, pass length in days, prices.

## Life skills page (guild facilities and cooking)

Data: [life-skills.json](../../data/life-skills.json).

- Seven activities: Garden, Sheepfold, Roost, Forge, Power Station, Mana Vein (all on the Guild Map) and Cooking.
  There is no fishing, logging or mining profession. Each facility runs "AFK Sessions" on a timer, has its own
  slot count and proficiency level, and has tools that raise output.
- Planting and breeding (5 tool tiers each). All three have the same three session tiers:

| Facility | Aptitude material | Tier 1 (6 min) | Tier 2 (9 min) | Tier 3 (12 min) |
|---|---|---|---|---|
| Garden | Oil | 60 Basic Treats + 6 random oil materials | 20 Premium Treats + 12 | 60 Premium Treats + 24 |
| Sheepfold | Wool | 60 Basic Treats + 6 random wool materials | 20 Premium Treats + 12 | 60 Premium Treats + 24 |
| Roost | Eggs | 60 Basic Treats + 6 random egg materials | 20 Premium Treats + 12 | 60 Premium Treats + 24 |

  Oil, wool and eggs activate Fantomon aptitudes; Treats are Fantomon EXP.
- Gathering (3 tool tiers each; no Treats, no aptitude materials; amounts not given):

| Facility | Gives | Used for |
|---|---|---|
| Forge | Steel | Guild building projects |
| Power Station | Kanstein Cell | Fuel for Glyph Research |
| Mana Vein | Mana Cluster | Many guild projects |

- Cooking: 67 recipes, 5 recovery dishes and 62 buff dishes (HP, ATK, DEF or SPD). Proficiency per dish goes to
  Lv 5 and a buff dish gets stronger the more it is cooked.
  - Recovery dishes: Green Rice Ball, Chargrilled Mushroom, Verdant Dew, Shepherd's Purse Pancake (restore HP);
    Starlight Bread (restores Stamina, although filed under recovery).
  - Buff dishes named: Stir-Fried Cabbage, Adventurer's Special Platter, Wonder Skewers (ATK); Wonder Hotpot
    (DEF); Jelly Bean Pals and Cheerful Greens (buff, stat not shown).
  - No ingredients are listed.

## Game modes page

Empty on the day it was read: the text says the game has "0" modes beyond the campaign and names none. It only
states that the site leaves out rewards, schedules and rotations because the data does not hold them reliably.

## Codes page

- 16 codes, all shown as active "as of 2026-06-14", no expiry dates. Redeem: Home (cube) icon > User Center >
  Gift Code; codes are case-sensitive capitals; rewards come by in-game mail.

| Code | Reward per the site |
|---|---|
| THEGAMETHEORIST, SXSCREATOR, SXSAMBASSADOR, SXSPARTNER, VANOSSTEAM, CARBOTANIMATIONS | 20 Rare Auroral Badges, 1 Destiny Fruit, 1 Stellatie each |
| SXSDCTHANKS, SXSFBTHANKS | 40 Rare Auroral Badges, 3 Destiny Fruits, 180 Dawnium each |
| SXSREDDIT | 180 Dawnium |
| ZJ999 | 2 Jelly Bean Pals, 3 Honeyed Roast, 50 Green Rice Balls |
| ZJ888 | 2 Legendary, 10 Epic and 20 Rare Auroral Badges |
| ZJ777 | 200 Dawnium, 2 Stellatie |
| SS000 | 100 Stone, 300 Raw Ore, 300 Chrono Sand, 1,000 Battle Essence |
| SS888 | 100 Abundance Leaf, 1 Destiny Fruit, 25 Stamina |
| SS777 | 3 Golden Leaf, 5 Iris, 5 Sunflower |
| SS999 | 3 Brown Eggs, 5 Basic Treats, 2 Bond Trinkets |

Redeeming is an account action for mae to approve; see [codes](../../systems/codes.md).

## Where each fact belongs (gaps this source fills)

| Gap or open question | What zeroluck says | Target page |
|---|---|---|
| Substat lines per gear rarity | 0 / 1-2 / 3 / 4 / 4 / 4 from white to red, with roll ranges | [gear](../../systems/gear.md) |
| Enhancement cap | Data maximum +250; cost points and the +250 total | [gear](../../systems/gear.md) |
| Off-hand types | Shield, Glove, Book, Ball; weapons Sword, Wand | [gear](../../systems/gear.md) |
| Gem structure | 8 gem types, 360 gems, merge upward (no names or values) | [gems](../../systems/gems.md) |
| Relic gacha rates per tier | Six rate tables | [gacha](../../systems/gacha.md), [relics](../../systems/relics.md) |
| Relic level and star caps, what each grows | Both cap at 6; level = main stat, star = Affinity or Aegis line | [relics](../../systems/relics.md) |
| Standard Prayer rates | 65.69 / 24 / 7.9 / 2.41, same on the Premium banner | [skills](../../systems/skills.md), [gacha](../../systems/gacha.md) |
| What the Fantomon summon gives | Seven-row rate table | [fantomons](../../systems/fantomons.md), [gacha](../../systems/gacha.md) |
| Fantomon roster shape | 13 total; 4 Attacker, 4 Tank, 5 Support; 6 Legendary, 4 Epic; 12 evolve | [fantomons](../../systems/fantomons.md) |
| Which guild building makes which aptitude material | Garden oil, Sheepfold wool, Roost eggs; session tiers and yields | [fantomons](../../systems/fantomons.md), [guild](../../systems/guild.md) |
| What the guild gathering buildings give | Forge steel, Power Station Kanstein Cell (Glyph Research), Mana Vein Mana Cluster | [guild](../../systems/guild.md) |
| The game's own monster tiers | Minion Monster, Elite Monster, Boss, Hieromon; counts; 37 names | [monsters](../../systems/monsters.md) |
| Hieromon list | 9 exist; two more names: Lord of Decay, Lord of Ruin | [monsters](../../systems/monsters.md) |
| Which dishes heal and which buff | 5 recovery dishes named; Jelly Bean Pals and Cheerful Greens are buff dishes; 67 recipes; proficiency Lv 5 | [cooking](../../systems/cooking-and-dishes.md) |
| Stat list and what counters what | 20 stats; Accuracy vs Block Rate, Crit RES vs Crit Rate, Effect RES vs Effect Hit Rate | [glossary](../../glossary.md), [classes overview](../../systems/classes-overview.md) |
| Class-level promotion gates | 18 / 16 / 19 / 40 with totals 20 / 48 / 89 / 180 (still this one source) | [classes overview](../../systems/classes-overview.md) |
| Luminium and Dawnium | 1 Luminium = 1 Dawnium; badges are spent 10 per capsule | [currencies](../../systems/currencies.md) |
| Battle pass structure | 70 tiers, 16 Normal + 4 Season passes, premium is paid out retroactively | [events](../../systems/events.md) |
| Codes | 16 codes as of 2026-06-14 | [codes](../../systems/codes.md) |

## Open questions

- ❓ Why the section answers 404 to direct requests from this environment while a second reader gets pages. Until
  that changes, `scripts/kb_fetch.py zeroluck` caches nothing and these notes cannot be diffed against raw text.
- ❓ The Friendship page and the database pages (pets, monsters, items, map): URLs unknown, content unread.
- ❓ What "Legendary other" (12.04%) is on the Fantomon summon.
- ❓ What Resonance's "+20%" applies to; our rule R-092 shows a small bonus per band.
- ❓ How the gear quality colours map to the game's rarity names, and where Divine and Immortal gear sit.
- ❓ Whether +250 enhancement, 16 passes and Tier 5 classes are live on the global server or only present in data.
- ❓ The three unnamed Hieromon; the rarity of the three Fantomons that are neither Legendary nor Epic.

## Sources

- [S-80] zeroluck.gg Sword x Staff section, pages listed in the section map, read 2026-11-18 through WebFetch
  (two passes on classes, summoning, relics, gear, bestiary, companions, battle pass).
