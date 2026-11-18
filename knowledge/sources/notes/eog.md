# eog.gg Sword x Staff section: page-by-page notes

<!-- index: Everything eog.gg publishes on Sword x Staff (hub, 10 guides, 6 tools, database, roadmap, tier list), in our words, with the page each fact belongs in -->

> **Summary:** eog.gg runs the largest English fan hub for the game: ten guides, six calculators and a database that reaches five seasons ahead by reading the Chinese server. This file records every fact found there on 2026-11-18, tagged [S-85], and says which knowledge page each gap-filling fact belongs in. Seventeen data files in `../../data/` hold the tables.
> **Applies:** all seasons (future-season rows come from the CN server and may change for global)
> **Related:** [Source register](../README.md), [lootandwaifus notes](lootandwaifus.md), [official site notes](official-site.md), [Conventions](../../CONVENTIONS.md)

## How this source was read

- robots.txt allows all crawlers; its Content-Signal line is `search=yes, ai-train=no, use=reference`. We use the pages as a reference only, which the line permits. [S-85]
- URLs came from the sitemap and the hub page. Fetched with curl at about one request per second. Raw copies are in `knowledge/sources/raw/eog/` (gitignored).
- The site is a single-page app. Guide text is in the HTML; hub, database and tool data sit in JavaScript bundles under `/assets/`. The data was read out of the bundle text with a literal parser; no site code was run.
- Tier: C (fan site, signed "EOG Analyst Team"; it credits the video maker QY Maple, and a contributor named Keripo for the damage test). Future-season data is read from the Chinese server, so dates for global are projections.
- ❓ Names: eog uses its own translations for many relics, dungeons, monsters, foods and gear sets. They often differ from the global client ("Lucky Idol" is the client's Lucky Statue, "Primordial Gem" is Primal Gem, "Forest Wolf" is Sylvanwolf). Match by position and stats, not by name.
- ❓ The Fantomon and companion rows in the eog database carry a source field naming Prydwen. We did not visit Prydwen; the rows were read from eog. Treat them as second-hand.
- Earlier single eog pages were already registered as S-20, S-50, S-51, S-52 and S-69. S-85 covers the site as a whole as seen on 2026-11-18.

## Data files built from this source

| File in `knowledge/data/` | Records | Holds |
|---|---|---|
| `astral-pact-scoring.json` | 28 | Star calculator: points per source per season, milestones, defaults |
| `relic-database.json` | 1128 | Every relic: pool, rarity, element, stats, set |
| `recipe-database.json` | 87 | Recipes with ingredients and effects |
| `ingredients.json` | 88 | Ingredients, derived from the recipes (drop sources unknown, null) |
| `skill-database.json` | 432 | 361 skills, 70 keywords, the quality ladder |
| `server-day-roadmap.json` | 89 | What unlocks on which server day, five seasons |
| `gathering-yields.json` | 24 | Stamina calculator: yields per rank, mine targets |
| `gem-tiers.json` | 29 | Gem values per tier, fusion rules |
| `dungeon-gear-sets.json` | 102 | Dungeon gear sets, effects, dungeon list by rank band |
| `map-points.json` | 1468 | Map markers for seven kingdoms |
| `item-values.json` | 48 | Dawnium-equivalent value per item |
| `class-tier-list.json` | 131 | Grades per class tier, builds |
| `monster-list.json` | 215 | Monsters by type and kingdom |
| `equipment-affixes.json` | 140 | Gear affixes |
| `companion-loadouts.json` | 35 | Companions and their class per rank band |
| `fantomon-skills.json` | 13 | Fantomons, rarity, skills |
| `combat-terms.json` | 104 | Status and combat keywords |

## Hub page (/swordxstaff)

- Daily reset is 13:00 UTC. [S-85]
- Base critical damage is 150%. A block halves the hit and cancels a critical. A unit with twice the enemy's Speed takes two turns. [S-85]
- Class traits: Sorcerer Accuracy, Duelist Crit Rate, Knight Block Rate, Sage all base attributes. [S-85]
- Changing class at Aqualis swaps skills like for like. [S-85]
- Luminium is described as converting to Dawnium one to one. ❓ single source. [S-85]
- Guild donations: three a day for free players, five for spenders. Conflicts with the official handbook ("up to 5, 1 free") [S-87]. [S-85]
- Second KonoSuba arc dated 2026-07-29. [S-85]
- Gift codes listed (16), said to work as of August 2026: SS000, SS888, ZJ888, ZJ999, ZJ777, SS999, SXSPARTNER, VANOSSTEAM, CARBOTANIMATIONS, SS777, SXSCREATOR, SXSAMBASSADOR, SXSREDDIT, SXSFBTHANKS, SXSDCTHANKS, THEGAMETHEORIST. Redeem at Home > Main Menu > User Center > Gift Code. ❓ none checked by us; codes expire. [S-85]

## Guide: Reroll (30 May)

- A reroll run takes 15 to 20 minutes and gives about 45 free pulls plus the 10 tutorial pulls. [S-85]
- Mage targets: Water Assault, Gale Shield, Water to Ice, Mana Surge. Warrior target: Heavy Impact and similar. [S-85]
- Second class at Lv 44 in Cinder Ridge. Join a guild at Lv 15. [S-85]

## Guide: Important tips (30 May)

- Sage has one viable build, Dark. Free players should commit to one element; relics give a 10 to 15% boost to it. [S-85]
- Class elements: Duelist Fire or Dark, Knight Water or Light, Sorcerer Light or Fire, Sage Dark. [S-85]
- Cart priority: Wood and Stone, then Chrono Sand and Raw Ore, then Rolla (only with 3 or more refreshes a day), then Battle Essence and Basic Treats. A focused resource yields 20 to 30% more. [S-85]
- Fantomons: main slot counts 100% of its stats, the three sub slots 50%, the rest of the collection 20%. Resonance level is the lowest level among the four deployed. [S-85]
- Mythic Fantomons Aegiswing and Nyxarchon cost 60 Summon Crystals each. Crystals drop at 4.2% per pull with at least one per 10-pull. Evolution needs 120 shards, which is one duplicate, so 120 crystals in total. [S-85]
- Fantomons by role: Knight Boaro or Armopi; area damage Falko or Zeioletus; Sage Mandragora or Herbote; Kels dispels. [S-85]
- A free player ends with about 70% of the Verdantglade relic pool. Selectable Mythic relic: Crit Rate for damage classes and Sage, Block Rate for Knight. [S-85]
- Relic resonance needs 4 relics of one element. The paid Hero's Guide relic (Stellaris Path) adds EXP and 20% resonance. [S-85]
- Gems: 8 gem types over 4 stats; tiers 1 to 15; each tier about 1.5 times the last; values are percent of the base attribute. Obsidian fits only Weapon and Off-hand, Moonstone only Armor and Off-hand. Tier 12 Obsidian gives +301.5% ATK and +1.2% DMG Boost; tier 12 Ruby +307.5% ATK. Amber adds 0.4% Healing Boost per tier. [S-85]
- Daily dungeons: 2 free runs, paid refreshes cost 100 then 150 Dawnium, unused runs bank up to 6, ranking is by how far you get. Dismantle old dungeon shards when a new dungeon opens. [S-85]
- Material dungeon refresh ladder: free player 2/2/2/2, mid spender 4/2/4/4. [S-85]
- Shop refresh: before Aqualis refresh once a day and buy out; during Loong Haven twice; afterwards buy only the 80%-off items, up to 3 refreshes. [S-85]
- The Mysterious NPC appears the day after Chaos Invasion: buy only Primal Forge with Chaos Crystals and upgrade it to Immortal. [S-85]
- Arena: the weekly reset is the time to spend 20 saved tickets on day one. [S-85]
- Spending order: Monthly card, Month Fund, Weekly Card, pop-up offers. [S-85]
- Affection from summons caps at 1000 a week. Each new job has its own premium skill pool. [S-85]

## Guide: Gacha and pity (30 May)

- Standard banner (blue orb): 1% Legendary, 7% Epic, 22% Rare; pity at 70, 30 and 10 pulls; at 200 pulls choose a Legendary tier-1 skill. Pity is account-wide and survives a class change. Conflicts with the rate set in [S-25] (see Conflicts). [S-85]
- Premium banner (pink orb) uses Covenite, earned from Standard pulls and not sold for Dawnium. It unlocks after Verdantglade and the second-tier advancement; the class pool is selectable. [S-85]
- Hold Skill Shard Vouchers for tier 3 and later. [S-85]
- Relic banner: pull until 50 to 70% of the collection, then use Destiny Exploration. [S-85]
- Fantomon banner: 0.8% top rate, Legendary pity 80; the Summon Shop sells a Mythic for 60 and a rotating Legendary for 18. Evolution needs Lv 108 and Nimbuville. [S-85]
- Bond Trinkets come from Delegate Tasks, the Guild shop, the Arena shop and Grand Treasure Hunt level 4. [S-85]

## Guide: Grand Treasure Hunt (30 May)

- Currency is Aurodrasil Energy. About 3,240 Energy clears stages 1 to 5. [S-85]
- Free cadence: join every 2 weeks (about 4,440 Energy, 2 level-5 items) or every 3 weeks (about 5,640, all level-5 items). Two 500-Energy packs are sold per cycle. [S-85]
- Floor 5 priority: left (the unique relic), then far right, then middle. [S-85]
- Phases: 1 Cinder Ridge Mythic relic select; 2 Lucky Statue (dungeon chest double chance 10% rising to 60%); 3 third-class skill shards x180; 4 Primal Gem (gem acquisition 10% rising to 60%); 5 Aqualis Mythic select; 6 Lucky Statue. [S-85]
- Before Loong Haven a free player skips hunts 1 and 3 and takes 2 and 5. [S-85]
- Lower floors: L1 Basic Treats, L2 Companion Gifts, L3 Wood and Stone, L4 Legendary Auroral Badges or Bond Trinkets. Skip Stellatie. [S-85]

## Guide: Destiny Fruit (30 May)

- A Destiny Exploration is run at the place named on a relic's source list, shown as "<Kingdom> <Area> Destiny Exploration". [S-85]
- The gallery has tabs Verdantglade, Cinder Ridge, Aqualis, Loong Haven and Other. Sets activate at 2, 3 and 4 pieces; the example set Faint Ember Glow is Quake Pick, Pyrecrown, Ignic Loop and Blade Saw. ❓ these four names were not found in the eog relic database, which uses other translations. [S-85]
- Switch from the banner to Destiny Fruit at about 70% of a pool. The fruit cost varies and is shown in the dialog. [S-85]

## Guide: DPS dummy test (30 May)

- Skill Test unlocks at Lv 40: Home > Character > Skills > Test. The dummy is a Boss with unlimited HP, 50 rounds, no element. [S-85]
- 40 Elemental Mastery (or Physical Mastery) is +1% damage. A Gold-tier Elemental Mastery charm at 1,270 gives +31.75%. [S-85]
- Sorcerer results: Wind's Delight best, then Water Assault; Water Shot has no cooldown; Stonechief Summon worst. [S-85]
- A loadout cannot be named "Test". [S-85]

## Guide: Void Rifts (30 May)

- Every other Sunday, alternating with Chaos Invasion. 10 attempts within 24 hours; each run has 1 to 5 floors by chance; relic pulls reach Mythic. [S-85]
- Suggested group: 1 healer, 1 frontliner, 2 damage. [S-85]

## Guide: Companion upgrade (22 May)

- Stat nodes at companion level 20, 50, 70 and 100; level 70 repeats the level-20 stat and level 100 repeats the level-50 stat. Healing Boost appears only at 100. [S-85]
- Level 20: DMG Boost for offensive companions, DMG Reduce for defensive. Level 50: Crit Rate or Accuracy, or Block or Crit Resist. Skins at level 60. [S-85]
- Order: everyone to 20, then companions matching your class to 50. The "!" mark shows preferred gifts. [S-85]

## Guide: Season 2 prep (1 Jul)

- Before rollover: save Material Realm tools; sell spare shards (they lose sell value); reach Champion I before spending stamina. [S-85]
- 36 hours before launch stop claiming Bed EXP and turn off Quick Claim. One day before, stop claiming dungeon rewards and bank 2 extra attempts (they stack to 6). [S-85]
- Launch morning: claim seasonal rewards, spend all Primo Stars in Astral Pact, push progression before using Speed-Ups and Temporal Crystals, then do relic pulls. [S-85]
- Speed-up milestones: Lv 106 (tier 4), Lv 108 (Adult Fantomon), Lv 116 (Tower, gem drops), Lv 130 (second dungeon, first seasonal gear). An alternative is to hold speed-ups to season end. [S-85]
- Stockpile for the new map: Gateway Key x5, Water Mine x2, Magic Drill x1, Withering Potion x1, new season item x7 (the map data shows this is Cloud Jade). [S-85]

## Guide: Food (6 Jul)

- Three food systems. Buff food lasts a number of battles, not a time. Permanent food raises HP, ATK, DEF or SPD. [S-85]
- Permanent food has brackets per recipe: meals 1 to 10 give 100%, 11 to 30 give 50%, 31 to 50 give 20%, 51 and later 5%. The counter is per recipe, not per stat, so spreading over recipes is better. [S-85]
- Recipes come from Commissions and the Auction House. Food has no inventory cap and does not expire. [S-85]
- Full recipe list: `recipe-database.json`.

## Tool: Star calculator (Astral Pact)

| Season | Points per star | Flat | Level floor | Relic floor | Gear per level per piece | Character per level | Skill per slot (8) | Relic per slot (20) | Fantomon per slot (4) |
|---|---|---|---|---|---|---|---|---|---|
| S1 | 100 | 10 | 100 | +10 | 38 | 100 | 13 | 57 | 14 |
| S2 | 27 | 45 | 130 | 13 | 18 | 100 | 7 | 33 | 8 |
| S3 | 13 | 65 | 160 | 16 | 14 | 100 | 5 | 26 | 6 |

- Points count levels above the season floor. Example: character Lv 124 in S1 scores 2,400 from level alone. [S-85]
- S1 milestones at 10, 20, 30, 40, 56, 72, 88, 104, 128, 152, 176, 200, 230, 260, 290 and 320 stars, cycling four bonuses: Ascension drop +3%, Gem acquisition +5%, Dungeon evaluation double reward +2%, EXP gain +2%. [S-85]
- Tool defaults: EXP for 100 to 101 is 730,000 and rises 50,000 a level; Raw Ore per gear level is 11,100 at Lv 120 and rises 90 a level; relic cap is floor +3, Fantomon cap floor +30. ❓ these are calculator defaults, not confirmed game tables. [S-85]

## Tool: Stamina calculator

| Kingdom Rank band | Rolla per 5 stamina (three sub-ranks) |
|---|---|
| Black Iron | 1920 / 2520 / 3180 |
| Bronze | 4020 / 4980 / 5940 |
| Silver | 6900 / 7980 / 9240 |
| Gold | 12000 / 12960 / 14160 |
| Sanctuary | 22800 / 23400 / 24000 |
| Legend | 48000 / 51000 / 54000 |

- Iron yield is one tenth of the Rolla figure, Chrono Sand one twelfth, Battle Essence one eighth. [S-85]
- A big mine has a 5% chance and pays double; one is guaranteed within 75 attempts. The realm rank multiplier is the Rolla figure divided by 1200. [S-85]
- A tool swing deals 10 damage 80% of the time and 15 damage 20% of the time. [S-85]
- Realms: Iron Mine, Gold Mine, Monster Cave (tool Worn Gauntlet), Sand Mine (tool Sand Shovel, gives Chrono Sand). Target weights are in `gathering-yields.json`. [S-85]

## Tools: Statue, Roulette, Map, Kingdom Map

### POI counts per kingdom

| Type | Verdantglade | Cinder Ridge | Aqualis | Loong Haven | Aethyris | Harpadia | Ignis |
|---|---|---|---|---|---|---|---|
| Goddess Statue | 17 | 18 | 18 | 18 | 18 | 18 | 18 |
| Lost Goddess Statue | 49 | 68 | 74 | 79 | 78 | 82 | 81 |
| Portal | 25 | 32 | 32 | 46 | 54 | 46 | - |
| Warp Gate | - | - | - | - | - | - | 59 |
| Voyage Obelisk | 1 | 1 | 1 | - | - | - | - |
| Hero Statue | 4 | 6 | 6 | 6 | 6 | - | 5 |
| Witch Statue | 2 | 3 | 4 | 4 | - | - | - |
| Challenge Stele | 6 | 7 | 8 | 8 | 9 | 9 | 9 |
| Trait Stele | 4 | 6 | 6 | 5 | 7 | - | - |
| Courage Stele | - | - | - | - | - | - | 5 |
| Power Gate | 4 | 6 | 4 | 4 | 1 | 2 | 3 |
| Elemental Gate | 4 | 5 | 5 | 5 | 5 | - | - |
| Rank Gate | 2 | 2 | - | 2 | 2 | - | - |
| Sealed Pillar | 3 | 4 | 5 | 5 | 5 | 5 | 5 |
| Frost Ice | - | - | - | - | - | - | 3 |
| Lava Boulder | - | - | - | - | - | - | 3 |
| Lucky Roulette | 2 | 3 | 3 | 4 | 4 | 4 | 4 |
| Ancient Keep | 3 | 3 | 3 | 3 | - | - | - |
| Temple Ruins | 3 | 3 | 3 | 3 | - | - | - |
| Monster Cave | 3 | 3 | 3 | 3 | - | - | - |
| Gold Cave | 3 | 3 | 3 | 3 | - | - | - |
| Iron Mine | 3 | 3 | 3 | 3 | - | - | - |
| Sand Mine | 2 | 3 | 3 | 3 | - | - | - |
| Gold Ore | 20 | 26 | 23 | 25 | 18 | 62 | - |
| Iron Ore | 28 | 25 | 47 | 33 | 19 | 52 | - |
| Sand Ore | 26 | 26 | 23 | 30 | 20 | 74 | - |
| Food | 28 | 39 | 51 | 32 | 36 | 75 | - |
| Bellflower | 34 | - | - | - | - | - | - |

Named dungeons / landmarks per kingdom (one marker each):

- **Verdantglade** (19 major sectors, 58 named areas): Auroradrasil, Moonshadow Forest [S-85]
- **Cinder Ridge** (20 major sectors, 79 named areas): Mecha Summit, Demonic Abyss [S-85]
- **Aqualis** (20 major sectors, 86 named areas): Cloudstream Vortex, Ocean Palace Ruins, Aquaorigin Shrine, Hellhold [S-85]
- **Loong Haven** (20 major sectors, 91 named areas): Celestial Cloudship, Bladeshire, Demonseal Gorge, Warlord's Rest, Demon-Sealing Tower, Cloudcrest Temple [S-85]
- **Aethyris** (18 major sectors, 94 named areas): Purification Garden, Sovereign's Nest, Battle Abyss Fortress, Eternal Flower Garden, Blazing Sun Spire, Order Temple, Crystal Spiral Tree [S-85]
- **Harpadia** (18 major sectors, 94 named areas): Paradise Corsair, Cogwork Bastion, Astral Observatory, Clockwork Belfry, Starfall City, Titan's Ascent, Emperor's Nautilus [S-85]
- **Ignis** (18 major sectors, 92 named areas): Rimespire, Blackrock Ruins, Everfrost Castle, Emberthrone, Lunar Palace, Crimson Keystone, Origin Gate [S-85]

### Unlock items needed per kingdom

| Kingdom | Gateway Key | Withering Potion | Magic Drill | Water Mine | Cloud Jade | Purifying Hammer | Brick Switch | Flame Hammer | Frost Hammer | Total |
|---|---|---|---|---|---|---|---|---|---|---|
| Verdantglade | 3 | 5 | 3 | - | - | - | - | - | - | 11 |
| Cinder Ridge | 4 | 3 | 5 | 3 | - | - | - | - | - | 15 |
| Aqualis | 5 | 2 | 3 | 6 | - | - | - | - | - | 16 |
| Loong Haven | 5 | 1 | 1 | 2 | 7 | - | - | - | - | 16 |
| Aethyris | 5 | - | 2 | 2 | 2 | 5 | - | - | - | 16 |
| Harpadia | 5 | - | 2 | 2 | - | - | 5 | - | - | 14 |
| Ignis | 5 | - | - | - | - | - | - | 3 | 3 | 11 |

Where each unlock item sits (nearest named area on the eog map; approximate):

- **Verdantglade**: Gateway Key: Rabbit Vault, Gorge Depths, Owl Vault; Withering Potion: Jungle Vault, Monolith Ruins V, Stagnant Jungle, Sunken Forest, Sunrise Isle; Magic Drill: Vine Peninsula, Hidden Camp, Hideout [S-85]
- **Cinder Ridge**: Gateway Key: Cliff Trove, Riskland Trove, Vale Trove, Lava Trove; Withering Potion: Ruin Cluster, Wild Vale, Vulture Cliff; Magic Drill: Stormcliff, Boulder Plain, Volcano Rift, Wild Vale, Lizard Isle; Water Mine: Nimbus Isle, Crate Ruins V, Oasis Throne [S-85]
- **Aqualis**: Gateway Key: Key Vault I, Key Vault II, Key Vault III, Key Vault IV, Key Vault V; Withering Potion: Vine Woods, Sulfur Woods; Magic Drill: Boulder Cliff, Boulder Grove, Swamp Haven; Water Mine: Sweetfin Isle, Merean Isle, Mangrove Isle, Anemone Isle, Raccoon Isle, Beetle Isle [S-85]
- **Loong Haven**: Cloud Jade: Emerald Corner, Breeze Cliff, Autumnal Plain, Golden Cliff, Dawn Vale, Fairy Greens, Dying Sun; Gateway Key: Iron Latch, Keyland, Ironpeak, Frontier Vault, Frozen Vault; Water Mine: Jadetoad Isle, Torn Hills; Withering Potion: Cosmic Ridge; Magic Drill: Seal Stone [S-85]
- **Aethyris**: Gateway Key: Treasure of Redemption, Treasure of Decay, Celestial Temple, Sanctum of Rites, Keystone Altar; Cloud Jade: Aerial Vault, Healer's Ruins; Water Mine: Mourning Sea, Lifeless Vault; Magic Drill: Paleveil Woods, The Sundered End; Purifying Hammer: Starward Court, Relic of Rebirth, Isle of Plenty, City of the Void, Guardian's Ground [S-85]
- **Harpadia**: Brick Switch: Dreamfall Isle, Phantom Sea, Fantasy Maze, Prism Terrace, Drift of Delight; Water Mine: Fool's Flats, Singing Flats; Gateway Key: Glee Vault, Curio Heights, Nebula Vault, Treasure Works, Glee Vault; Magic Drill: Secret Factory, House of Giggles [S-85]
- **Ignis**: Gateway Key: Snow Capsized Treasure Vault, Scorched Flame Treasure Vault, Bitter Winter Treasure Vault, Void Order Treasure Vault, Forgotten Lost Treasure Vault; Flame Hammer: Eternal Winter Ice Cliff, Still Stagnant Falls, Harsh Cold Holy Site; Frost Hammer: Wyrm Lull Vital Land, Charred Bone Vital Land, Ash Cinder Court [S-85]

### Prayer statues

- **Verdantglade** (6): Witch: Bubble Lake, Spider Queen Lair; Nameless Hero: Hurricane Heights; Rock Fighter: Verdantglade XVII; Wise Mage: Guardian Vale; Moon Lord: Hidden Camp [S-85]
- **Cinder Ridge** (9): Witch: Cliff Camp, Enigma Gorge, Shadow Gorge; Nameless Hero: Cinder Ridge III; Rock Fighter: Jagged Gorge; Iron Knight: Lumiriver; Flying Warrior: Titan Mine; Wise Mage: Undercliff Gravel Beach; Moon Lord: Obsidian Guard [S-85]
- **Aqualis** (10): Witch: Pier of Yore, Woodside Settlement, Toxic Jungle III, Hellhollow River; Nameless Hero: Glittering Vale; Rock Fighter: Toxic Jungle I; Iron Knight: Cursed Woods; Flying Warrior: Budokan; Wise Mage: Beetle Samurai Order; Moon Lord: Salamander Coast [S-85]
- **Loong Haven** (10): Witch: Enchanted Garden, Old Trail, Frostrealm, Torn Hills; Nameless Hero: Evergreen Trail; Rock Fighter: Swordsmith Pavilion; Iron Knight: Eaglegrim Ridge; Flying Warrior: Reed Marsh; Wise Mage: Forsaken Lotus Pond; Moon Lord: Frigid Land [S-85]
- **Aethyris** (6): Nameless Hero: Sanctum Ruins; Rock Fighter: The Final Brink; Iron Knight: Contemplation Court; Flying Warrior: Cataclysmic Sanctum; Wise Mage: Flame of the Fallen God; Moon Lord: Valor Plaza [S-85]
- **Harpadia** (0): none recorded [S-85]
- **Ignis** (5): Frost Maiden: Scorched Searing Open Road; Ice Soul Hero: Charred Earth Flats; Ember Maiden: II; Flamewing Hero: I, Pale Mirror [S-85]

### Lucky Roulettes

- **Verdantglade**: Relic Roulette: Jungle Camp; Skill Roulette: Damp Cliff [S-85]
- **Cinder Ridge**: Star-Up Roulette: Boulder Settlement; Beast Material Roulette: Mount Chestnut; Relic Roulette: Stormcliff [S-85]
- **Aqualis**: Skill Roulette: Coral Settlement; Star-Up Roulette: Vine Jungle; Beast Material Roulette: Tidal Peninsula [S-85]
- **Loong Haven**: Relic Roulette: Hush Yard; Skill Roulette: Coastal Plain; Star-Up Roulette: Dawn Woods; Beast Material Roulette: Crystalheart Lake [S-85]
- **Aethyris**: Relic Roulette: Ancestor Woods; Skill Roulette: Purge Cliffs; Star-Up Roulette: Ashen Hoop; Beast Material Roulette: Healer's Ruins [S-85]
- **Harpadia**: Relic Roulette: Dreammaze; Skill Roulette: Bulwark Bay; Star-Up Roulette: Prism Forge; Beast Material Roulette: Sweetdream Isle [S-85]
- **Ignis**: Relic Roulette: Ice Rift Lost Palace; Skill Roulette: Blood Dancing Dissolve Rock Lake; Star-Up Roulette: Still Snow Corridor; Beast Material Roulette: Whisper Corridor [S-85]

### Verdantglade gates, steles and dungeons by nearest area

- Challenge Stele: Drasilgard, Gnoll Vale, Verdantglade VIII, Amber Gorge, Dark Woods, Verdantglade XVII [S-85]
- Voyage Obelisk: Voyage Obelisk [S-85]
- Ancient Keep: Verdantglade I, Grotto Peninsula, Blooming Jungle [S-85]
- Temple Ruins: Verdantglade III, Verdantglade XI, Dream Sea [S-85]
- Monster Cave: Troll Lair, Verdantglade VIII, Verdantglade XV [S-85]
- Gold Cave: Monolith Ruins I, Verdantglade VI, Verdantglade XVI [S-85]
- Iron Mine: Stone Ruins I, Verdantglade VII, Verdantglade XIII [S-85]
- Sand Mine: Verdantglade X, Verdantglade XII [S-85]
- Rank Gate: Verdantglade V, Amber Gorge [S-85]
- Power Gate: Damp Woods, Bubble Lake, Windless Cliff, Stone Ruins III [S-85]
- Sealed Pillar: Rabbit Vault, Gorge Depths, Owl Vault [S-85]
- Elemental Gate: Zephyr Vale, Damp Coast, Dark Woods, Light Woods [S-85]
- Auroradrasil: Auroradrasil [S-85]
- Lucky Roulette: Jungle Camp, Damp Cliff [S-85]
- Trait Stele: Amber Gorge, Gnoll Basecamp, Dream Sea, Light Woods [S-85]
- Witch Statue: Bubble Lake, Spider Queen Lair [S-85]
- Hero Statue: Hidden Camp, Guardian Vale, Hurricane Heights, Verdantglade XVII [S-85]
- Moonshadow Forest: Moonveil Woods [S-85]

Verdantglade major sectors: Verdantglade I, Verdantglade II, Verdantglade III, Verdantglade IV, Drasilgard, Verdantglade V, Verdantglade VI, Verdantglade VII, Verdantglade VIII, Verdantglade IX, Verdantglade X, Verdantglade XI, Verdantglade XII, Verdantglade XIII, Verdantglade XIV, Verdantglade XV, Verdantglade XVI, Verdantglade XVII, Voyage Obelisk


## Hub tab: Roadmap (server days)

- Global day 1 is 2026-05-19. [S-85]
- Regions: day 1 Verdantglade, 4 Cinder Ridge, 12 Aqualis (Season 1), 47 Loong Haven (Season 2), 114 Aethyris (Season 3), 226 Harpadia (Season 4), 335 Ignis (Season 5), 444 Shining Bond (Season 6, CN only so far). [S-85]
- Job changes:

| Job | Character level | Class level | Previous job level |
|---|---|---|---|
| 2nd | 44 | 20 | 18 |
| 3rd | 82 | 48 | 16 |
| 4th | 106 | 89 | 19 |
| 5th | 136 | 180 | 40 |
| 6th | 172 | 280 | 50 |
| 7th | 198 | 380 | 55 |

- Dungeons: Aquorigin Shrine day 24 (needs Lv 100), Hellhold day 33, Demonseal Gorge day 47, Warlord's Rest day 60 (needs Lv 130), Cloudcrest Temple day 73, Bladeshire day 86, Celestship day 99; Season 3 dungeons days 114 to 203; Season 4 days 226 to 309; Season 5 days 335 to 418, last power wall 1.8 billion. Power per difficulty is in `server-day-roadmap.json`. [S-85]
- Fantomon Manifestation at Lv 108; Demonbind Tower at Lv 116; Fantomon Bond at Lv 180; companion Dora at Lv 186. [S-85]
- Seasonal maps: Whaleback Island (day 26), Acme Nexus (day 71, Lv 130), Astral Odyssey (day 128), Grotesque Fairground (day 240), Frostfire Voyage (day 349). [S-85]
- Mythic Fantomons: Pandarial day 92, Prismatic Astralite day 160. [S-85]
- Grand Treasure Hunt: first on day 8, then every 7 days; reward cycle of four (Mythic Relic Box, special A such as Lucky Idol, skill shards x180, special B such as Primordial Gem). Mini-games: Bingo Draw, Lucky Scratch, Feneck's Puzzle. [S-85]

## Hub tab: Tier list and builds

Class names by tier (Duelist / Knight / Sorcerer / Sage line):

| Tier | Duelist line | Knight line | Sorcerer line | Sage line | Grades (same order) |
|---|---|---|---|---|---|
| 3 | Berserker | Paladin | Archmage | Arcanist | A / B / A / B |
| 4 | Conqueror | Guardian | Destroyer | Dominator | S / A / A / B |
| 5 | Ravager | Templar | Magister | Prophet | C / A / A / S |
| 6 | Reaver | Empyrean | Cataclyst | Oracle | S / B / A / C |
| 7 | Annihilator | Seraph | Voidcaller | Ascendant | B / S / S / B |
| 8 | Hellblade | Paragon | Obliterator | Fateweaver | S / C / A / B |

- eog flags Ravager (tier 5 Duelist) and Oracle (tier 6 Sage) as tiers to avoid. [S-85]
- Sorcerer boss build: Water Assault, Flame Jet, Light of Dawn, Wind's Delight with charms Unstable Aura, Elemental Harmony, Mana Surge, Lightning Mystery. [S-85]
- Archmage "Elemental Harmony" build: Aqua Vortex, Divine Wrath, Meteoric Flames, Wind's Delight with Elemental Harmony, Radiant Sear, Rapid Cast, Mana Surge. [S-85]
- Named builds also exist for Destroyer (Radiant Judgment), Dominator (Dark Starburst Nuke) and Sage (Generalist, Summon Erosion, Healing). All 22 builds: `class-tier-list.json`. [S-85]

## Hub tab: Gems

| Tier | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Single-stat gem % | 1.5 | 3 | 6 | 12 | 18 | 27 | 40.5 | 60.7 | 91.1 | 136.6 | 205 | 307.5 | 461.2 | 691.9 | 1037.9 |
| Dual-stat gem % | 1 | 2 | 4.5 | 10 | 15.5 | 24 | 37 | 56.7 | 86.6 | 131.6 | 199.5 | 301.5 | 454.7 | 684.9 | 1030.4 |

- Pairs: Ruby and Obsidian (ATK), Sapphire and Moonstone (DEF), Beryl and Amber (HP), Citrine and Amethyst (SPD and Crit Rate). The first of each pair is the single-stat gem. [S-85]
- Fusion: 3 into 1 for the first two steps (tier 1 and tier 2), then 2 into 1. Success rates listed: 100%, 36%, 18%, 8%, 4%. ❓ which tier step each rate applies to was not clear from the bundle. [S-85]
- Tier 5 to tier 6 and above is done at the blacksmith NPC in Cinder Ridge. [S-85]
- Sockets: 2 per piece on level-130 gear in Season 2, at most 4. Practical ceiling is tier 12. [S-85]

## Hub tab: Dungeon gear sets

- 30 sets over Seasons 1 to 5 with their trigger texts, and the dungeon list by rank band (Blackiron, Bronze, Silver, Gold, Saint, Legend, Angel): `dungeon-gear-sets.json`. [S-85]
- ❓ Inferred name matches between the eog set list and the roadmap list (ours, not stated by eog): World Tree = Auroradrasil; Machine God Mountain = Mecha Summit; Sea Palace Ruins = Ocean Palace Ruins; Wellspring Grand Shrine = Aquorigin Shrine; Yomi or Netherworld Pavilion = Hellhold; General's Tomb = Warlord's Rest; Azure Cloud Temple = Cloudcrest Temple; Ancient Sword City = Bladeshire; Celestial Sea Skyship = Celestship.

## Hub tab: Item values

- eog prices items in Dawnium: Stellatie 100, Covenite 1000, Bond Trinket 160, Summon Crystal 1600, Destiny Fruit 60, Quest Scroll 120, Lucky Ticket 360, 1 Stamina 4.8, realm tools 20, Auroral Badges Rare 8, Epic 15, Legendary 56, Mythic 74. Full list: `item-values.json`. ❓ these are eog's valuations, not shop prices. [S-85]

## Hub tab: Fantomons and companions

- Mythic: Aegiswing, Nyxarchon, Pandarial. Legendary: Armopi, Herbote, Kels, Sylvaerie, Terragon, Zeioletus. Epic: Boaro, Chomusuke, Falko, Mandragora. [S-85]
- 35 companions, each with a class that advances by rank band (Akane: Mage, Sorcerer, Archmage, Destroyer, Magister): `companion-loadouts.json`. [S-85]

## Hub tab: Relics

| Pool (eog name) | Kingdom | Rare | Epic | Legendary | Mythic | Total | Sets | Elements |
|---|---|---|---|---|---|---|---|---|
| Forest | Verdantglade | 20 | 20 | 20 | 10 | 70 | 20 | Dark 14, Fire 14, Light 14, Water 14, Wind 14 |
| Mountain | Cinder Ridge | 20 | 20 | 20 | 10 | 70 | 20 | Dark 14, Fire 14, Light 14, Water 14, Wind 14 |
| Marsh | Aqualis | 20 | 20 | 20 | 10 | 70 | 20 | Dark 14, Fire 14, Light 14, Water 14, Wind 14 |
| Dragon I | Loong Haven | 20 | 20 | 20 | 20 | 80 | 22 | Dark 16, Fire 16, Light 16, Water 16, Wind 16 |
| Dragon II | Loong Haven | 20 | 20 | 20 | 20 | 80 | 20 | Dark 16, Fire 16, Light 16, Water 16, Wind 16 |
| Feather I | Aethyris | 20 | 20 | 20 | 20 | 80 | 20 | Dark 16, Fire 16, Light 16, Water 16, Wind 16 |
| Feather II | Aethyris | 20 | 20 | 20 | 20 | 80 | 20 | Dark 16, Fire 16, Light 16, Water 16, Wind 16 |
| Feather III | Aethyris | 20 | 20 | 20 | 20 | 80 | 20 | Dark 16, Fire 16, Light 16, Water 16, Wind 16 |
| Harpadia I | Harpadia | 20 | 20 | 20 | 20 | 80 | 20 | Dark 16, Fire 16, Light 16, Water 16, Wind 16 |
| Harpadia II | Harpadia | 20 | 20 | 20 | 20 | 80 | 20 | Dark 16, Fire 16, Light 16, Water 16, Wind 16 |
| Harpadia III | Harpadia | 20 | 20 | 20 | 20 | 80 | 20 | Dark 16, Fire 16, Light 16, Water 16, Wind 16 |
| Other | - | 60 | 62 | 78 | 78 | 278 | 61 | Dark 52, Fire 55, Light 59, Water 56, Wind 56 |

Special main stats by pool (count of Legendary / Mythic relics carrying it; plain ATK, DEF, HP, SPD relics not listed):

- **Forest**: ATK (%) 0/1 (+1 lower); CRIT Rate (%) 0/1; CRIT Resistance (%) 0/1; DEF (%) 0/0 (+1 lower); Damage Bonus (%) 1/1; Damage Resistance (%) 1/0; Effect Hit 1/0; Elemental Resistance 1/0; HP (%) 1/1 (+1 lower); Physical Mastery 1/0 (+1 lower); Physical Resistance 1/0 (+1 lower); SPD (%) 1/1 (+1 lower) [S-85]
- **Mountain**: ATK (%) 0/0 (+1 lower); Accuracy (%) 1/0; Block Rate (%) 1/1; CRIT DMG (%) 0/1; CRIT Rate (%) 1/0; CRIT Resistance (%) 1/0; DEF (%) 0/2 (+1 lower); Effect Hit 1/0; Effect Resistance 1/0; Elemental Mastery 3/0 (+1 lower); Elemental Resistance 2/0 (+1 lower); HP (%) 0/1 (+1 lower); Physical Mastery 1/0; Physical Resistance 2/0; SPD (%) 0/0 (+1 lower) [S-85]
- **Marsh**: ATK (%) 2/1; Accuracy (%) 0/1; DEF (%) 2/0; Damage Bonus (%) 0/0 (+1 lower); Damage Resistance (%) 0/0 (+1 lower); Effect Hit 1/0 (+1 lower); Effect Resistance 2/0 (+1 lower); HP (%) 1/0; Physical Mastery 1/0; SPD (%) 1/1 [S-85]
- **Dragon I**: ATK (%) 3/2 (+3 lower); Accuracy (%) 1/1; Block Rate (%) 1/1; CRIT Rate (%) 1/1; CRIT Resistance (%) 1/2; DEF (%) 3/2 (+3 lower); Damage Bonus (%) 1/1; Damage Resistance (%) 1/2; HP (%) 3/2 (+3 lower); Physical Mastery 1/0; Physical Resistance 1/0; SPD (%) 3/2 (+3 lower) [S-85]
- **Dragon II**: ATK (%) 1/3 (+1 lower); Accuracy (%) 1/1; Block Rate (%) 1/1; CRIT DMG (%) 0/2; CRIT Rate (%) 1/0; CRIT Resistance (%) 1/2; DEF (%) 1/3 (+1 lower); Damage Bonus (%) 0/1; Damage Resistance (%) 0/1; Effect Hit 1/0; Effect Resistance 1/0; Elemental Mastery 1/0; Elemental Resistance 1/0; HP (%) 1/3 (+1 lower); Physical Mastery 1/0; Physical Resistance 1/0; SPD (%) 1/3 (+1 lower) [S-85]
- **Feather I**: Accuracy (%) 0/1; Block Rate (%) 0/1; CRIT DMG (%) 0/2; CRIT Rate (%) 0/2; CRIT Resistance (%) 2/1; Damage Bonus (%) 1/0 (+1 lower); Effect Hit 1/0; Effect Resistance 1/0 (+1 lower); Elemental Resistance 1/0; Physical Resistance 2/0 [S-85]
- **Feather II**: Accuracy (%) 1/0; Block Rate (%) 0/2; CRIT DMG (%) 0/1; CRIT Rate (%) 1/1; Damage Bonus (%) 1/2; Damage Resistance (%) 0/0 (+1 lower); Effect Resistance 1/0; Elemental Mastery 2/0 (+1 lower); Elemental Resistance 2/0 (+1 lower); Physical Mastery 1/0 [S-85]
- **Feather III**: Accuracy (%) 0/2; Block Rate (%) 1/0; CRIT Rate (%) 1/1; Damage Bonus (%) 0/1; Damage Resistance (%) 2/3; Effect Hit 2/0 (+1 lower); Effect Resistance 1/0; Elemental Mastery 1/0; Physical Mastery 1/0 (+1 lower); Physical Resistance 0/0 (+1 lower) [S-85]
- **Harpadia I**: ATK (%) 0/2; Accuracy (%) 0/1; Block Damage Resistance (%) 0/1; Block Rate (%) 1/0; CRIT Rate (%) 1/1; CRIT Resistance (%) 0/1; DEF (%) 1/1; Damage Bonus (%) 2/1 (+1 lower); Damage Resistance (%) 2/2; Effect Hit 2/0; Effect Resistance 1/0; Elemental Mastery 3/0 (+1 lower); Elemental Resistance 1/0 (+1 lower); HP (%) 1/0 (+1 lower); Physical Mastery 2/0 (+1 lower); Physical Resistance 0/0 (+1 lower); SPD (%) 0/2 (+1 lower) [S-85]
- **Harpadia II**: ATK (%) 2/1 (+1 lower); Accuracy (%) 0/1; Block Damage Resistance (%) 0/1; Block Rate (%) 1/1; CRIT Rate (%) 1/0; CRIT Resistance (%) 1/1; DEF (%) 1/2 (+1 lower); Damage Bonus (%) 0/1; Damage Resistance (%) 0/1; Effect Resistance 2/0 (+1 lower); Elemental Resistance 2/0; HP (%) 1/0; Physical Mastery 1/0; Physical Resistance 1/0; SPD (%) 1/0 (+1 lower) [S-85]
- **Harpadia III**: ATK (%) 0/0 (+1 lower); Accuracy (%) 1/1; Block Damage Resistance (%) 1/0; Block Rate (%) 0/1; CRIT DMG (%) 1/1; CRIT Rate (%) 0/1; CRIT Resistance (%) 0/1; DEF (%) 0/0 (+1 lower); Damage Bonus (%) 0/1; Damage Resistance (%) 0/1 (+1 lower); Effect Hit 2/0 (+1 lower); Effect Resistance 1/0; Elemental Mastery 1/0; Elemental Resistance 1/0; HP (%) 0/3 (+1 lower); Physical Mastery 1/0; Physical Resistance 3/0; SPD (%) 1/1 [S-85]
- **Other**: ATK (%) 1/0; Accuracy (%) 1/2; Base ATK (%) 2/3 (+2 lower); Base DEF (%) 2/3 (+2 lower); Base Dispatch Reward (%) 0/1; Base HP (%) 2/3 (+2 lower); Base SPD (%) 2/3 (+2 lower); Block Damage Resistance (%) 1/2; Block Rate (%) 1/3; CRIT DMG (%) 1/1; CRIT Rate (%) 2/3; CRIT Resistance (%) 3/2; DEF (%) 1/0; DMG from Monsters Resist (%) 2/0; DMG from Players Resist (%) 2/0; DMG to Flame Phoenix Increase (%) 1/0; DMG to Hurricane Griffin Increase (%) 1/0; DMG to Monsters Increase (%) 4/0; DMG to Orochi Increase (%) 1/0; DMG to Players Increase (%) 3/0; DMG to Progenitor Dragon God Increase (%) 1/0; Damage Bonus (%) 2/4 (+1 lower); Damage Resistance (%) 2/5 (+1 lower); Destiny Fruit Growth Speed (%) 0/1; Dungeon Rating Reward Double Chance (%) 0/1; EXP Gain Bonus (%) 0/1; Effect Hit 3/0 (+1 lower); Effect Resistance 4/0 (+1 lower); Elemental Mastery 4/0 (+1 lower); Elemental Resistance 4/0 (+1 lower); Gem Acquisition Rate (%) 0/1; HP (%) 0/0 (+1 lower); Homestead Battle Essence Output Bonus (%) 0/1; Homestead Chrono Sand Output Bonus (%) 0/1; Homestead Equipment Output Speed (%) 0/1; Homestead Lola Output Bonus (%) 0/1; Homestead Rough Stone Output Bonus (%) 0/1; Homestead Stamina Recovery Speed (%) 0/1; Homestead Stone Output Bonus (%) 0/1; Homestead Wood Output Bonus (%) 0/1; Physical Mastery 4/0 (+1 lower); Physical Resistance 4/0 (+1 lower); SPD (%) 1/2; Wonder Initial Great Success (%) 0/1 [S-85]

Verdantglade (Forest) Mythic relics as eog names them: Horn of Abundance (Light, Damage Bonus (%)), Fruit of Wisdom (Light, DEF), Stormsong Lyre (Wind, ATK (%)), Moon Goddess Hunting Bow (Wind, DEF), Lady of the Lake Hilt (Water, CRIT Rate (%)), Box of Calamity (Dark, SPD (%)), Jade Aquatic Cradle (Water, CRIT Resistance (%)), Pot of Endless Greed (Dark, DEF), Hellflame Blossom (Fire, SPD), Dragonheart Flame Crystal (Fire, HP (%)) [S-85]

Cinder Ridge (Mountain) Mythic relics: Bionic Source Dew (Water, Block Rate (%)), Summit of Light (Light, CRIT DMG (%)), Machine God's Flame Eye (Fire, DEF (%)), Machine God's Mana Key (Dark, HP (%)), Scales of Order (Wind, HP), Perpetual Headwind Wheel (Wind, DEF (%)), Sandfall Funeral Coffin (Water, DEF), Doomsday Dark Clock (Dark, SPD), Everburning Flame Throne (Fire, ATK), Power Source Zero (Light, ATK) [S-85]

Aqualis (Marsh) Mythic relics: Yata Mirror of Light (Light, SPD), Ancient Divine Turtle Charm (Water, HP), Sky Gale Tailfeather Spread (Wind, SPD), Phantom Soul-Burial Armor (Dark, ATK), Otherworld Prince Wind Bag (Wind, ATK), Dark Fang Yomi Port (Dark, HP), Heart of the Surging Sea (Water, Accuracy (%)), Blazing Sky Seven-Branched Sword (Fire, ATK (%)), Inferno Reincarnation Seal (Fire, SPD (%)), Divine Law Amulet Gold Chest (Light, HP) [S-85]

"Other" pool relics with no set (34; event, shop and unique relics): Legend of the Sword (Epic Light, HP (%)), Portable Air Thermostat Mk.I (Epic Water, SPD), Warm Winter Surprise (Legendary Fire, DEF (%)), Divine Codex Charm (Legendary Water, DMG to Monsters Increase (%)), Divine Sword Charm (Legendary Light, DMG to Monsters Increase (%)), Divine Staff Charm (Legendary Wind, DMG to Monsters Increase (%)), Divine Armor Charm (Legendary Water, DMG from Monsters Resist (%)), Divine Shield Charm (Legendary Light, DMG from Monsters Resist (%)), Auspicious Cloud Pouch (Legendary Wind, DMG to Monsters Increase (%)), Berry Doll (Legendary Light, ATK (%)), Wind Legend Limited Ancient Relic (Legendary Wind, SPD (%)), Grimoire Charm (Legendary Wind, DMG to Players Increase (%)), Demon Sword Charm (Legendary Dark, DMG to Players Increase (%)), Demon Staff Charm (Legendary Fire, DMG to Players Increase (%)), Demon Shield Charm (Legendary Fire, DMG from Players Resist (%)), Demon Armor Charm (Legendary Dark, DMG from Players Resist (%)), Proud Snow Bronze Mirror (Mythic Water, Damage Resistance (%)), Primordial Gem (Mythic Light, Gem Acquisition Rate (%)), Lucky Idol (Mythic Light, Dungeon Rating Reward Double Chance (%)), Fortune Cat Idol (Mythic Light, Homestead Lola Output Bonus (%)), Travel Pack (Mythic Wind, Base Dispatch Reward (%)), Endless Hourglass (Mythic Dark, Homestead Chrono Sand Output Bonus (%)), Star Wish Echo (Mythic Light, SPD (%)), Cosmic Song Journey (Mythic Water, Damage Resistance (%)), Vital Divine Water (Mythic Water, Homestead Stamina Recovery Speed (%)), Floating Falls Lantern (Mythic Fire, SPD (%)), Consecrated Spirit Liquid (Mythic Wind, Destiny Fruit Growth Speed (%)), Divine Forging Anvil (Mythic Fire, Homestead Equipment Output Speed (%)), Treasure Detector (Mythic Light, Wonder Initial Great Success (%)), Essence Refining Flask (Mythic Dark, Homestead Battle Essence Output Bonus (%)), Hero's Guide (Mythic Wind, EXP Gain Bonus (%)), Philosopher's Stone (Mythic Water, Homestead Stone Output Bonus (%)), Ancient Furnace (Mythic Fire, Homestead Rough Stone Output Bonus (%)), Golden Sacred Tree (Mythic Light, Homestead Wood Output Bonus (%)) [S-85]

## Hub tab: Skills

- Quality steps: Rare 2, Epic 3, Legendary 4, Mythic 6, Divine 8, Immortal 11 (34 in all). [S-85]
- Doom DMG deals +100% to shields and summons. Erosion is a Dark damage-over-time lasting 3 turns. Heals scale with max HP. [S-85]
- Water to Ice: 50% chance of Condensation (extra Water damage) and 30% chance to freeze. Mana Surge raises Crit Rate. Frostbite Blossom deals Water damage once in a 1-grid square. [S-85]
- Frenzy Totem and Summoner's Frenzy belong to Arcanist (tier 3). Divine Wrath is an Archmage skill: 16 Light hits, cooldown 2. [S-85]

### Mage-line skills


**Mage**

| Skill | Type | CD | Dmg % Rare / Legendary / Immortal | Effect (in-game text, shortened) |
|---|---|---|---|---|
| Blazing Fire Ring | T | 1 | 48.16 / 68.8 / 137.59 | Deals Fire DMG once to all enemies within 2 grids of the caster. |
| Curse Resonance | C | - | - | For each ailment or debuff the target carries, Technique DMG dealt by the caster to that target increases. Stacks up to 3 times. |
| Cyclone | T | 1 | 26.75 / 38.22 / 76.44 | Selects a grid within 6 grids of the caster. Deals Wind DMG once to all enemies within 2 grids of the target grid, knocking them airborne and pulling them to the target grid. |
| Dew's Blessing | C | - | - | Increases the caster's Water DMG. |
| Elemental Body | C | - | - | Increases the caster's Elemental RES. |
| Elemental Mystery | C | - | - | Increases the caster's Elemental Mastery. |
| Fireball | T | 1 | 45.08 / 64.4 / 128.8 | Selects a grid within 5 grids of the caster. Deals Fire DMG once to all enemies within a 1-grid square area of the target grid. |
| Flame Jet | T | 1 | 23.84 / 34.06 / 68.11 | Deals Fire DMG 3 times to all enemies in a 1x3 grid area in front of the caster. |
| Flaming Path | C | - | 29.4 / 42 / 84 | When the caster starts to move in their turn, there is a 30% chance to inflict Burn to grids within 1 grid of the caster. |
| Gale Shield | C | - | 19.6 / 28 / 56 | Grants a shield based on the caster's max HP at the start of battle. When the shield disappears, deals Wind DMG once to all enemies within a 1-grid square area of the caster, with a 100% base chance to knock them back by 1 grid. |
| Healing Touch | T | 1 | - | Heals 1 ally within 5 grids of the caster once and dispels 1 random ailment or debuff from them. |
| Heart of Flame | C | - | - | Increases the caster's Fire DMG. |
| Ice Spike | T | 1 | 47.87 / 68.39 / 136.78 | Deals Water DMG once to all enemies in a 1x5 grid area in front of the caster, with a 40% base chance to inflict Frozen for 1 turn. |
| Insight | C | - | - | Increases the caster's Effect Hit Rate. |
| Iron Thorn | T | 1 | 51.45 / 73.5 / 147 | Selects a grid within 3 grids of the caster. Deals Wind DMG once to all enemies within 1 grid of the target grid, with a 30% base chance to inflict Immobilize for 1 turn. |
| Mana Surge | C | - | - | Increases the caster's Crit Rate. |
| Stonechief Summon | T | 5 | - | Summons a Stonechief in front of the caster that immediately acts. The summon inherits a percentage of the caster's stats and remains for up to 5 turns. (Zero Initial CD) |
| Tempest Sphere | T | 1 | 15.04 / 21.48 / 42.97 | Deals Wind DMG 5 times to 1 enemy within 3 to 5 grids of the caster. |
| Tough Soul | C | - | - | Increases the caster's HP. |
| Unstable Aura | C | - | 22.05 / 31.5 / 63 | When the caster's Technique deals DMG to an enemy, there's a 25% chance to trigger Aura, dealing additional Wind DMG once, with a 60% base chance to knock them back by 1 grid. |
| Void Blessing | T | 2 | - | Selects a grid within 4 grids of the caster. Increases max HP of all allied characters within 2 grids of the target grid by a percentage of the caster's Max HP for 3 turns. This effect is unique. If the target's HP is below 30%, a |
| Water Assault | T | 1 | 31.57 / 45.09 / 90.19 | Deals Water DMG once to all enemies in a 3x4 grid area in front of the caster. DMG decreases by 25% for each subsequent hit on the same target. (Large targets may take multiple hits.) |
| Water Shot | T | - | 43.61 / 62.29 / 124.59 | Deals Water DMG once to 1 enemy within 4 grids of the caster. |
| Water to Ice | C | - | 19.11 / 27.3 / 54.6 | When the caster's Technique deals Water DMG to an enemy, there's a 50% chance to trigger Condensation, dealing additional Water DMG once, with a 30% base chance to inflict Frozen for 1 turn. |
| Wind's Delight | T | 1 | 22.64 / 32.34 / 64.68 | Selects a grid within 6 grids of the caster. Launches 7 waves of wind blades at the target grid and random enemies within 1 grid to the target grid's left and right. Each wave deals Wind DMG once to all enemies within 1 grid of th |
| Wind's Whisper | C | - | - | Increases the caster's Wind DMG. |

**Sorcerer**

| Skill | Type | CD | Dmg % Rare / Legendary / Immortal | Effect (in-game text, shortened) |
|---|---|---|---|---|
| Elemental Harmony | C | - | - | For each element among equipped Techniques that deal DMG, increases the caster's Elemental Mastery. Stacks up to 4 times. |
| Energy Burst | T | 1 | - | Your next damaging Technique gains increased Accuracy and deals 50% more DMG. |
| Fiery Star Trail | T | 1 | 24.13 / 34.47 / 68.94 | Deals Fire Doom DMG twice to all enemies within a 3-grid circular area of the caster. |
| Flickering Stars | T | 1 | 69.83 / 99.75 / 199.5 | Selects a grid within 6 grids of the caster. Deals Light DMG once to all enemies within 1 grid of the target grid and dispels 1 random buff from them. |
| Frosty Nova | T | 1 | 48.22 / 68.88 / 137.76 | Selects a grid within 3 grids of the caster. Deals Water DMG once to all enemies within a 1-grid square area of the target grid, with a 30% base chance to inflict Frozen for 1 turn. |
| Light of Dawn | T | 1 | 41.9 / 59.85 / 119.7 | Deals Light Doom DMG twice to all enemies in a 1x8 grid area in front of the caster. |
| Lightning Chain | T | - | 23.71 / 33.87 / 67.73 | Deals Light DMG once to 1 enemy within 4 grids of the caster. The effect then chains to 1 random enemy within 4 grids of the target, up to 9 times. Each enemy can only be hit once by the chain effect. |
| Lightning Mystery | C | - | 31.97 / 45.68 / 91.35 | Each time the caster's Technique deals DMG to an enemy, there's a 30% chance to trigger Thunder Strike that deals additional Light DMG once. |
| Raging Wildfire | C | - | 21.71 / 31.01 / 62.02 | Has a 20% chance to inflict Burn to grids within range when casting a Fire Technique. |
| Void Bubble | C | - | - | When the caster's HP drops below 50% for the first time in a battle, grants a shield to the caster based on max HP for 2 turns and Dodge for 2 turns (cannot be dispelled). |
| Wind's Shadow | C | - | 16.76 / 23.94 / 47.88 | Has a 30% chance to deal additional Wind DMG once and a 50% base chance to delay the target's action by 20% after dealing Wind DMG 3 times to an enemy with Techniques. |

**Sage**

| Skill | Type | CD | Dmg % Rare / Legendary / Immortal | Effect (in-game text, shortened) |
|---|---|---|---|---|
| Dark Bullet | T | - | 41.93 / 59.9 / 119.8 | Attacks 1 enemy within 4 grids of the caster, dealing Dark DMG once, with a 50% base chance to inflict Erosion. |
| Flame Wolf Summon | T | 2 | - | Summons 2 Flame Wolves in front of the caster that immediately acts. The summons inherit a percentage of the caster's stats, but cannot be the primary target of attacks or healing. They remain for up to 2 turns. (Zero Initial CD) |
| Healing Mastery | C | - | - | Enhances the caster's healing effects. |
| Radiant Restoration | T | 2 | - | Heals all allies within 4 grids of the caster once. |
| Resurrection | C | - | - | When an allied adventurer dies, immediately revives and heals them once, granting Revitalization for 2 turns (cannot be dispelled). This Charm can only trigger once per battle. At the start of battle, if multiple allied adventurer |
| Shadow Erosion | C | - | 22.86 / 32.66 / 65.31 | Each time the caster's Technique deals Dark DMG to an enemy, there is a 40% base chance to inflict Erosion. |
| Shadow Impact | T | 1 | 43.06 / 61.51 / 123.02 | Selects a grid within 3 grids of the caster. Deals Dark DMG once to all enemies within 2 grids of that target grid. If the enemy target carries Erosion, triggers Erosion effect twice immediately. |
| Soul Impact | C | - | 36.75 / 52.5 / 105 | When the caster's summon dies or expires, deals Dark DMG once to all enemies within 2 grids of it. |
| Soul Spark | C | - | - | Increases the ATK of the caster's summons but reduces their duration by 2 turns. (Summons last at least 1 turn; this Charm does not affect summons without a turn limit.) |
| Treantling Summon | T | 3 | - | Summons a Treantling behind the caster that immediately acts. The summon inherits a percentage of the caster's stats, but cannot be the primary target of attacks or healing. It remains for up to 5 turns. (Zero Initial CD) |
| Weakening Hex | T | 1 | 39.27 / 56.11 / 112.21 | Selects a grid within 3 grids of the caster. Deals Dark DMG once to all enemies within 2 grids of the target grid, with a 50% base chance to inflict Weakened 1 for 2 turns. |

**Archmage**

| Skill | Type | CD | Dmg % Rare / Legendary / Immortal | Effect (in-game text, shortened) |
|---|---|---|---|---|
| Aqua Vortex | T | 1 | 38.37 / 54.81 / 109.62 | Creates a vortex at a selected grid within 4 grids of the caster. The vortex deals Water DMG once to all enemies within 2 grids and pulls them to its center, with a 40% base chance to inflict Wet for 2 turns. |
| Divine Wrath | T | 2 | 92.33 / 131.9 / 263.8 | Selects a target within 4 grids of the caster. Randomly deals Light DMG 16 times within 3 grids of the target, hitting at least 3 times. DMG decreases by 40% for each subsequent hit on the same target. (Prioritizes the skill range |
| Fire Blast | T | - | 66.15 / 94.5 / 189 | Deals Fire DMG once to 1 enemy within 5 grids of the caster. |
| Frost Guard | C | - | - | At the end of the caster's turn, if no Technique was cast this turn, the caster enters the Icebound status, which reduces DMG taken and lasts until the start of the caster's next turn. This status heals the caster once before it e |
| Howling Hurricane | T | 2 | 24.5 / 35 / 70 | Selects a grid within 5 grids of the caster. Deals Wind DMG 5 times to all enemies within 2 grids of the target grid, knocking them airborne. |
| Incarnation of Light | C | - | - | Increases the caster's Light DMG. |
| Meteoric Flames | T | 1 | 79.89 / 114.14 / 228.27 | Selects a grid within 5 grids of the caster. Deals Fire DMG once to all enemies within a 1-grid square area of the target grid, with a 60% chance to inflict Burn on grids within range. (Prioritizes large targets) |
| Radiant Sear | C | - | 30.38 / 43.4 / 86.8 | Each time the caster's Technique deals DMG to an enemy, there's a 50% chance to deal additional Light DMG once, with a 30% base chance to inflict Blind. |
| Rapid Cast | C | - | - | Increases the caster's Elemental Mastery. At the start of battle, reduces the CD of all Techniques by 1 turn. (Techniques already off cooldown are not affected.) |
| Repelling Wind | C | - | 36.75 / 52.5 / 105 | Has a 75% chance to trigger Repelling Wind when an enemy actively enters within 2 grids of the caster, dealing Wind DMG once, with a 100% base chance to knock them back 2 grids. (Triggers again if they approach repeatedly) |

**Arcanist**

| Skill | Type | CD | Dmg % Rare / Legendary / Immortal | Effect (in-game text, shortened) |
|---|---|---|---|---|
| Abyssal Hand | T | 1 | 52.59 / 75.12 / 150.25 | Selects a grid within 3 grids of the caster. Deals Dark DMG once to all enemies within 2 grids of the target grid, with a 50% base chance to inflict Slow 1 for 2 turns. |
| Frenzy Totem | T | 4 | - | Summons a Totem in front of the caster that immediately acts. The summon inherits a percentage of the caster's stats, but cannot be the primary target of attacks or healing. It remains for up to 5 turns. (Zero Initial CD) |
| Linked Misfortune | C | - | 28.58 / 40.82 / 81.65 | Each time the caster inflicts Erosion on an enemy, there's a 60% chance to inflict Erosion again. |
| Mana Blast | T | 1 | 48.58 / 69.4 / 138.8 | Selects a grid within 3 grids of the caster. Deals Dark DMG once to all enemies within 2 grids of the target grid with a 50% base chance to inflict Erosion. |
| Night's Blessing | C | - | - | Increases the caster's Dark DMG. |
| Overhealing | C | - | - | Has a 30% chance to additionally heal all allies within 1 grid of the target each time the caster heals allies with a Technique. |
| Shadow of Termination | T | 2 | 126.61 / 180.87 / 361.75 | Deals Dark DMG once to 1 enemy within 3 grids of the caster. If the target carries Erosion, triggers all Erosion stacks immediately. (Prioritizes large targets) |
| Shadow Vengeance | C | - | - | Upon taking lethal DMG for the first time, the caster survives with 1 HP and enters Shadow Form, lasting until the end of the caster's turn (cannot be dispelled). In this form, the caster is immune to all DMG, can't be healed, won |
| Summoner's Frenzy | C | - | - | Increases the ATK of summons. |
| Waterling Summon | T | 3 | - | Summons a Waterling behind the caster that immediately acts. The summon inherits a percentage of the caster's stats, but cannot be the primary target of attacks or healing. It remains for up to 5 turns. (Zero Initial CD) |

**Destroyer**

| Skill | Type | CD | Dmg % Rare / Legendary / Immortal | Effect (in-game text, shortened) |
|---|---|---|---|---|
| Cyclone Lament | C | - | 14.7 / 21 / 42 | Increases the caster's Wind DMG. Each time the caster's Technique deals Wind DMG to an enemy, there is a 35% base chance to inflict Laceration for 1 turn. |
| Explosive Spirit | C | - | - | For every Fire Technique cast, increases the caster's Crit Rate for 2 turns. Stacks up to 8 times. |
| Fiery Burst | C | - | 19.66 / 28.09 / 56.18 | Each time the caster's Technique deals Fire Crit DMG to an enemy, deals additional Fire DMG once to all enemies within 2 grids of the target. |
| Fiery Rejuvenation | C | - | - | At the end of the caster's turn, if there are grounds inflicted with Burn within 2 grids of the caster, heals the caster once. Increases the healing power by 10% for each additional Burning grid in the area. Stacks up to 5 times. |
| Flowing Doom | T | 2 | 41.65 / 59.5 / 119 | Deals Water DMG 3 times to all enemies in a 3x5 grid area in front of the caster, with a 50% base chance to knock them back by 1 grid. |
| Formation Breaker | T | 2 | - | Increases ATK for all allied characters within 3 grids of the caster by a percentage of the caster's ATK for 2 turns. This effect is unique. Also there's a 50% chance to advance the action bar of allied characters by 20%. (Zero In |
| Overload Protection | C | - | - | Within a single turn, each time the caster loses over 15% of max HP, grants the caster a shield based on their max HP for 2 turns. |
| Protective Rune | T | 4 | - | Reduces direct DMG the caster takes from Techniques. Also boosts the caster's other DMG Reduction effects by an extra 20%. Lasts 3 turns. (Zero Initial CD) |
| Shattering Ice | C | - | 112.7 / 161 / 322 | When a target frozen by the caster removes the Frozen state, additionally deals Water DMG once. |
| Starlight Burst | T | 1 | 63.7 / 91 / 182 | Selects a grid within 5 grids of the caster. Deals Light DMG once to all enemies within 2 grids of the target grid, with a 30% base chance to inflict Blind. |
| Thunder of Judgment | T | 1 | 42.26 / 60.37 / 120.74 | Deals Light DMG 3 times to 1 enemy within 5 grids of the caster. (Prioritizes large targets) |
| Wind Blade Spiral | T | 1 | 36.75 / 52.5 / 105 | Selects a grid within 3 grids of the caster. Deals Wind DMG 3 times to all enemies within a 1-grid square area of the target grid, with a 40% base chance to inflict Laceration for 1 turn. |

**Dominator**

| Skill | Type | CD | Dmg % Rare / Legendary / Immortal | Effect (in-game text, shortened) |
|---|---|---|---|---|
| Aberrancy | C | - | - | When taking DMG, if the attacker is affected by ailment or debuff, reduces DMG taken by the caster. |
| Chaos Rune | T | 2 | 159.29 / 227.56 / 455.13 | Attacks 1 enemy within 3 grids of the caster, dealing Dark DMG once, with a 40% base chance to inflict Frenzy for 1 turn. |
| Dark Starburst | T | 1 | 42.88 / 61.25 / 122.5 | Deals Dark DMG 3 times to 1 enemy within 4 grids of the caster. |
| Decoy Clone | T | 3 | - | Summons a Clone in front of the caster and connects it with 1 enemy. When the Clone's HP decreases, the connected target loses an equal amount of HP. The Clone lasts for 3 turns, inherits 60% of the target's DEF and a percentage o |
| Falling Dark Star | C | - | - | At the start of the caster's turn, the caster gains 1 random buff that lasts until the start of the caster's next turn. |
| Mantra of Blessings | C | - | - | At the start of the caster's turn, grants Blessing to the allied character with the highest ATK, increasing their DMG. This effect lasts until the start of the caster's next turn and cannot be dispelled. |
| Phantom Light | C | - | - | Increases the caster's healing effects. When a Technique's healing overflows, converts 100% of the overheal into a shield for the target, lasting 2 turns. |
| Rejuvenating Rain | T | - | - | Heals 1 ally within 5 grids of the caster once. If the target's HP is below 50%, this healing effect is increased by 20%. |
| Rock Rex Summon | T | - | - | Summons 1 Rock Rex in front of the caster. The summon inherits a percentage of the caster's stats. (The Technique can only trigger once per battle.) |
| Soul Pact Resonance | C | - | - | Grants an ATK boost when the caster has a summon on the battlefield. |
| Soulbond Restoration | C | - | - | When the caster's summon dies or expires, heals the caster once. |
| Spirit Aegis | T | 1 | - | Grants Spirit Mark to the allied character with the lowest HP within 5 grids of the caster. |

**Magister**

| Skill | Type | CD | Dmg % Rare / Legendary / Immortal | Effect (in-game text, shortened) |
|---|---|---|---|---|
| Blast Spirit | T | 2 | 107.8 / 154 / 308 | Places 2 Blast Spirits in front of the caster. They remain on the battlefield for up to 3 turns. (Zero Initial CD) |
| Crimson Whirl | T | 2 | 53.96 / 77.09 / 154.18 | Deals Fire Doom DMG 3 times to all enemies in a 3x3 grid area in front of the caster. |
| Ember Flare | C | - | 107.8 / 154 / 308 | Increases the caster's Fire DMG. Killing an enemy has a 30% chance to place 1 Blast Spirit on the spot. |
| Frost Thorn | T | 1 | 46.92 / 67.03 / 134.06 | Deals Water DMG twice to all enemies in a 3x3 grid area in front of the caster, with a 30% base chance to inflict Frozen for 1 turn. |
| Frostsoul Ward | C | - | - | Increases the caster's Water DMG. When attacked, there's a 70% base chance to inflict Wet on the attacker for 2 turns. |
| Light Burst | T | 1 | 88.2 / 126 / 252 | Deals Light DMG once to 1 enemy within 4 grids of the caster. Each instance of damage can chain to 2 random enemies within 4 grids of the target, up to 2 times. Each enemy can only be hit once by the same chain. |
| Radiant Warp | C | - | - | Increases the caster's DMG RES. When taking Technique DMG, there's a 50% chance to teleport to any empty grid within 4 grids of the caster. Can trigger only once per turn. |
| Storm Rhapsody | T | 1 | 30.58 / 43.68 / 87.36 | Selects a grid within 5 grids of the caster. Deals Wind DMG 3 times to all enemies within 3 grids of the target grid with a 35% base chance to knock them back by 1 grid towards the center of the battlefield. |
| Thunder Judgment | C | - | 49 / 70 / 140 | When an enemy within 5 grids of the caster casts a Technique, there's a 30% chance to trigger Thunder Strike, dealing Light DMG once. The chance increases to 90% if the target is inflicted with Electro or Wet. |
| Thunderbolt Mark | C | - | 25.97 / 37.1 / 74.2 | Each time the caster's Technique deals Light DMG to an enemy, there is a 65% base chance to inflict Electro. |
| Twin Gale | T | - | 39.2 / 56 / 112 | Deals Wind DMG twice to 1 enemy within 3 to 5 grids of the caster. |
| Vital Rhythm | C | - | - | At the start of the caster's turn, gains 1 stack of Rhythm if the caster's HP is above 30%. This effect stacks up to 5 times and cannot be dispelled. |

**Prophet**

| Skill | Type | CD | Dmg % Rare / Legendary / Immortal | Effect (in-game text, shortened) |
|---|---|---|---|---|
| Cursed Armor | C | - | 20.58 / 29.4 / 58.8 | Each time the caster takes Technique DMG, there's a 50% base chance to inflict Erosion on the attacker. |
| Desperate Shadow | T | 1 | 111.05 / 158.65 / 317.3 | Deals Dark DMG once to all enemies within a 1x4 grid area in front of the caster, with a 70% base chance to inflict 1 random debuff (Weakened 2, Armor Break 2, or Slow 2) for 2 turns. |
| Hexed Blast | T | 1 | 71.13 / 101.61 / 203.22 | Selects a grid within 3 grids of the caster. Deals Dark DMG once to all enemies within 2 grids of the target grid. For each type of debuff the target carries, deals additional Dark DMG once, up to 3 times. |
| Radiant Rhythm | T | 1 | - | Heals 1 ally within 4 grids of the caster once. The effect then chains to 1 random ally within 4 grids of the target, up to 5 times. Repeated healing on the same target is diminished by 35% per instance. |
| Rejuvenating Elixir | C | - | - | Carries 3 potions at the start of battle. When an allied character's HP falls below 50%, uses a potion to heal them. Produces 1 potion every 3 turns, holding up to 3 at a time. |
| Ring of Omen | C | - | - | At the start of the caster's turn, reduces Effect RES of all enemies within 5 grids of the caster. This effect is unique. Also there's a 50% base chance to inflict Vulnerability for 1 turn. |
| Shadowy Current | C | - | 39.2 / 56 / 112 | Increases the caster's Dark DMG. Killing an enemy deals additional Dark DMG once to all enemies within 1 grid of the target. |
| Soul Reap | T | 2 | 109.82 / 156.89 / 313.78 | Deals Dark DMG twice to 1 enemy within 3 grids of the caster. For every 5% HP lost by the target, this skill deals 5% more DMG, up to a max of 50% increase. (Prioritizes large targets) |
| Soulweave | C | - | - | When 3 of the caster's summons die or disappear, summons 1 Infernal Fiend in front of the caster that immediately acts. The summon inherits a percentage of the caster's stats. (The Charm can only trigger once per battle.) |
| Summoning Pact | C | - | - | Summoning consumes 2% of the caster's max HP to increase the summon's HP. Restores all HP consumed by this Charm if the caster survives until victory. |
| Thalasson Summon | T | - | - | Summons 1 Thalasson next to the caster that immediately acts. The summon inherits a percentage of the caster's stats. (The Technique can only trigger once per battle.) |
| Void Chant | T | 2 | 39.2 / 56 / 112 | Creates a magic rune that lasts 2 turns. When an enemy within 5 grids casts a Technique, the rune deals Dark DMG once to them. If the target carries Erosion, triggers the Erosion effect once. (Zero Initial CD) |

### Skill counts per class

| Class | Techniques | Charms |
|---|---|---|
| Warrior | 13 | 13 |
| Mage | 13 | 13 |
| Duelist | 6 | 5 |
| Knight | 6 | 5 |
| Sorcerer | 6 | 5 |
| Sage | 6 | 5 |
| Berserker | 5 | 5 |
| Paladin | 5 | 5 |
| Archmage | 5 | 5 |
| Arcanist | 5 | 5 |
| Conqueror | 6 | 6 |
| Guardian | 7 | 6 |
| Destroyer | 6 | 6 |
| Dominator | 6 | 6 |
| Ravager | 6 | 6 |
| Templar | 6 | 6 |
| Magister | 6 | 6 |
| Prophet | 6 | 6 |
| Reaver | 6 | 6 |
| Empyrean | 6 | 6 |
| Cataclyst | 6 | 6 |
| Oracle | 6 | 6 |
| Annihilator | 6 | 6 |
| Seraph | 6 | 6 |
| Voidcaller | 6 | 6 |
| Ascendant | 6 | 6 |
| Monster | 25 | 7 |

## Where gap-filling facts belong

| Gap in an existing page | Answer from eog | Target page |
|---|---|---|
| Astral Pact points beyond the known total; other seasons | Per-source point table, S2 and S3 conversion, 16 milestones | `systems/astral-pact.md` |
| Class tier levels and names past tier 4 | Job table (44, 82, 106, 136, 172, 198 with class-level gates), tier 5 to 8 names | `systems/classes-overview.md` |
| When later kingdoms open | Harpadia day 226 (S4), Ignis day 335 (S5); Whaleback Island and Acme Nexus are seasonal maps | `systems/seasons.md`, `systems/world-and-kingdoms.md` |
| Dungeon level gates | Aquorigin Shrine Lv 100, Warlord's Rest Lv 130, S3 names and power walls | `systems/dungeons.md` |
| Where exploration tools are found | Verdantglade key, potion and drill areas; counts per kingdom; Loong Haven item is Cloud Jade | `systems/goddess-statues.md`, `systems/exploration.md` |
| Gem values and fusion | Value per tier, pairs, slot fits, fusion counts, success rates | `systems/gems.md` |
| Sand realm and rank scaling | Sand Mine with Sand Shovel; yield table per Kingdom Rank | `systems/material-realms.md`, `systems/stamina.md` |
| Gear sockets | 2 sockets on Lv 130 gear in S2, max 4 | `systems/gear.md` |
| Fantomon rarities and slot weights | Rarity list, 100/50/20%, crystal rate 4.2%, 120 shards | `systems/fantomons.md` |
| Companion stat nodes | 20/50/70/100, skins at 60 | `systems/companions.md` |
| Cooking numbers | Recipe list, per-recipe brackets | `systems/cooking-and-dishes.md` |
| Grand Treasure Hunt costs | Aurodrasil Energy, about 3,240 for stages 1 to 5, mini-game names | `systems/events.md` |
| Void Rift schedule | Alternates with Chaos Invasion on Sundays, 10 attempts | `systems/events.md` |
| Skill cooldowns and texts | Skill database, keywords, quality steps | `systems/skills.md`, class pages |
| Value of a Quest Scroll | 120 Dawnium equivalent | `systems/shops.md` |
| Monster types | 215 monsters by type | `systems/monsters.md` |
| Tower unlock | Demonbind Tower Lv 116 | `systems/towers.md` |
| Arena ticket timing | Spend 20 saved tickets at weekly reset | `systems/arena-and-pvp.md` |
| Skill Test unlock | Lv 40 | `systems/levels-and-unlocks.md` |

## Conflicts

- Gacha rates: eog gives 1% / 7% / 22% with pity 70 / 30 / 10 [S-85]; [S-25] gives a different set. Not resolved.
- Guild donations: eog says 3 a day free and 5 for spenders [S-85]; the official handbook says up to 5 a day with 1 free and recommends 70 Dawnium for two more [S-87].
- Gem fusion: eog says 3 into 1 only for the first two steps, then 2 into 1 [S-85]; the existing gems page has 3 into 1 from a tier D site only [S-55], with no tier limit.
- Fantomon unlock: eog and the official site say Lv 50 [S-85][S-87]; rule R-011 records 51.

## Open questions

- ❓ Relic drop chances and exact drop places per relic: not on eog. The site that had them (lootandwaifus) is offline.
- ❓ Grand Treasure Hunt price per floor item: only totals are given.
- ❓ Real EXP table and Raw Ore table: only calculator defaults.
- ❓ Kingdom Rank requirements, Arena reward tables, skill shard costs per quality: not found.
- ❓ Which fusion step each success rate (100/36/18/8/4%) belongs to.
- ❓ Whether global follows the CN server-day schedule after Season 2.
- ❓ Mapping of eog relic and dungeon names to global client names; confirm in game.

## Sources

- [S-85] eog.gg Sword x Staff section as a whole, seen 2026-11-18: hub `/swordxstaff`, guides (reroll, important-tips, gacha-and-pity, grand-treasure-hunt, destiny-fruit, dps-dummy-test, void-rifts, companion-upgrade, season-2-prep, food-guide), tools (star, stamina, statue, roulette, map, kingdom map) and the hub data bundle. Not yet in the register; row proposed to the lead.
- [S-87] Official site handbook posts, see [official-site.md](official-site.md).
- [S-25] zeroluck.gg summoning page (other rate set), see the [register](../README.md).
- [S-55] Tier D gem-fusion statement cited by `systems/gems.md`, see the [register](../README.md).
