# Research report to integrate: eog-official

<!-- index: Working file for the integration pass; delete when folded in -->

REPORT: eog.gg / lootandwaifus.com / official site (tags S-85, S-86, S-87; S-88 and S-89 unused)

Outcome: eog.gg and the official site are fully mined. lootandwaifus.com gave nothing: its Sword x Staff section is gone (404), so relic and ingredient drop chances are still missing.

## Files written

Notes (in /home/user/sxs-agent/knowledge/sources/notes/):
- eog.md (627 lines: hub, 10 guides, 6 tools, roadmap, tier list, gems, gear sets, relic pools, Mage-line skill tables, gap table, conflicts)
- lootandwaifus.md (what was checked, what is missing)
- official-site.md (post-by-post notes, gap table, conflicts)

Data (in /home/user/sxs-agent/knowledge/data/, all new names, all sourced S-85, all parse):
astral-pact-scoring.json (28 records), relic-database.json (1128), recipe-database.json (87), ingredients.json (88; drop_sources and drop_chance are null), skill-database.json (432), server-day-roadmap.json (89), gathering-yields.json (24), gem-tiers.json (29), dungeon-gear-sets.json (102), map-points.json (1468), item-values.json (48), class-tier-list.json (131), monster-list.json (215), equipment-affixes.json (140), companion-loadouts.json (35), fantomon-skills.json (13), combat-terms.json (104).

No existing file was edited; scripts/ untouched; no git. Raw caches are in knowledge/sources/raw/{eog,official,lootandwaifus}/.

`python3 scripts/kb_check.py` reports only one kind of problem for my three notes files: S-85, S-86, S-87 are not defined in knowledge/sources/README.md. Rows to add:

| Tag | Title | URL | Tier | Date seen/published | Notes on reliability |
|---|---|---|---|---|---|
| S-85 | eog.gg Sword x Staff section as a whole (hub, 10 guides, 6 tools, data bundle) | https://eog.gg/swordxstaff | C | seen 2026-11-18 / guides published 2026-05-22 to 2026-07-06 | Fan site, "EOG Analyst Team". Future seasons read from the CN server. Own translations for relic, dungeon, monster and food names. Fantomon and companion rows say they come from Prydwen. robots: allowed, Content-Signal use=reference. |
| S-86 | lootandwaifus.com Sword x Staff section | https://lootandwaifus.com/ | C | seen 2026-11-18 | Section removed: all pages 404, not in sitemap. No facts taken. pages.dev mirror blocked by proxy 403 and skipped. |
| S-87 | Official site news posts 186, 190-200, 203 | https://swordxstaff.boltray.com/ | A | seen 2026-11-18 / published 2026-04-10 to 2026-06-05 | Publisher. Handbook Vol. 1 and 2 and Tips posts are firm; player and skill counts are marketing. /api/ is disallowed and was not requested. |

## Things to know before using the data

- eog names are eog's translations, not the global client's ("Lucky Idol" = Lucky Statue, "Primordial Gem" = Primal Gem, "Forest Wolf" = Sylvanwolf). The example set in eog's own Destiny Fruit guide (Faint Ember Glow: Quake Pick, Pyrecrown, Ignic Loop, Blade Saw) is not findable by those names in eog's relic database.
- The dungeon name matches between eog's gear-set list and its roadmap list (World Tree = Auroradrasil, General's Tomb = Warlord's Rest, and so on) are my inference, marked ❓ in eog.md.
- eog's Fantomon and companion rows carry a source field naming Prydwen. I did not visit Prydwen; the rows were read from eog. Your call whether to keep them.
- Everything after Season 2 in server-day-roadmap.json is the CN schedule projected onto global.
- Star and stamina calculator "defaults" (EXP 730,000 for Lv 100 to 101, Raw Ore 11,100 per gear level at 120) are tool defaults, not confirmed game tables.
- The skill tables in eog.md and skill-database.json carry shortened in-game effect text as eog shows it.
- eog.md cites [S-25] (zeroluck summoning) and [S-55] (the gem-fusion source already used in systems/gems.md) in its Conflicts section.

## Most important facts and takeaways

1. Astral Pact scoring per season [S-85]: S1 is 100 points per star (gear 38 per level per piece, character 100 per level above Lv 100, skill 13 per slot, relic 57 per slot, Fantomon 14 per slot); S2 is 27 per star; S3 is 13 per star. S1 milestones at 10, 20, 30, 40, 56, 72, 88, 104, 128, 152, 176, 200, 230, 260, 290, 320 stars.
2. Job changes [S-85]: 2nd Lv 44, 3rd Lv 82, 4th Lv 106, 5th Lv 136, 6th Lv 172, 7th Lv 198, each with class-level gates (20, 48, 89, 180, 280, 380).
3. Server-day roadmap [S-85]: Cinder Ridge day 4, Aqualis 12, Loong Haven 47 (S2), Aethyris 114 (S3), Harpadia 226 (S4), Ignis 335 (S5). Global day 1 is 2026-05-19.
4. Official unlock levels [S-87]: Dismantle 12, Guild 15, Vendor Booth 20, Grand Arena and Commercium 40, Fantomons 50; Off-hand slot after Class II. eog adds Skill Test at 40 and Demonbind Tower at 116.
5. Enhancement belongs to the gear slot, not the item; every 5 levels across all slots gives a Resonance step, so upgrade evenly [S-87].
6. Cart [S-87][S-85]: raise all resources to Lv 10, then Wood and Stone; a focused resource yields 20 to 30% more. Idle rewards cap at 36 hours; a Temporal Crystal is 2 hours of Bed and Cart.
7. Guild donations [S-87]: up to 5 a day, 1 free; the publisher recommends 70 Dawnium for two more.
8. Material Realm rewards scale with Kingdom Rank [S-87]; eog gives Rolla per 5 stamina from 1,920 (Black Iron) to 54,000 (Legend); iron is 1/10, Chrono Sand 1/12, Battle Essence 1/8 of that.
9. Gems [S-85]: tiers 1 to 15, single-stat curve 1.5% up to 1037.9% (tier 12 = 307.5%); fusion 3 into 1 for the first two steps, then 2 into 1; 2 sockets on Lv 130 gear in S2, max 4; practical ceiling tier 12.
10. Daily dungeons [S-85]: 2 free runs, refreshes 100 then 150 Dawnium, runs bank up to 6. Gates: Aquorigin Shrine Lv 100, Warlord's Rest Lv 130.
11. Season 2 prep [S-85]: stop claiming Bed EXP 36 hours before, bank dungeon attempts, spend all Primo Stars on launch morning, speed-up milestones Lv 106, 108, 116, 130; stockpile Gateway Key x5, Water Mine x2, Magic Drill x1, Withering Potion x1, Cloud Jade x7.
12. Grand Treasure Hunt [S-85]: currency Aurodrasil Energy, about 3,240 clears stages 1 to 5; first on day 8, weekly; free players skip hunts 1 and 3 and take 2 and 5; floor 5 left item first.
13. Fantomons [S-85][S-87]: main slot 100%, three sub slots 50%, rest of collection 20%; resonance is the lowest of the 4 deployed; a Mythic costs 60 Summon Crystals, crystals drop 4.2% per pull, evolution needs 120 shards.
14. Permanent food [S-85]: per recipe, meals 1 to 10 give 100%, 11 to 30 give 50%, 31 to 50 give 20%, later 5%; the counter is per recipe, so spread across recipes.
15. Void Rifts [S-85]: every other Sunday alternating with Chaos Invasion, 10 attempts in 24 hours.
16. Tier list [S-85]: Sorcerer line grades A, A, A, A, S, A for tiers 3 to 8; eog flags Ravager (tier 5 Duelist) and Oracle (tier 6 Sage) as tiers to avoid.
17. Damage test [S-85]: 40 Elemental or Physical Mastery is +1% damage; Wind's Delight tested best for Sorcerer.
18. Exploration items per kingdom [S-85]: Verdantglade Key 3, Potion 5, Drill 3; Cinder Ridge 4/3/5 plus Water Mine 3; Aqualis 5/2/3 plus Water Mine 6; Loong Haven 5/1/1 plus Water Mine 2 and Cloud Jade 7.
19. Daily reset is 13:00 UTC [S-85]; the Voice of Kanstein launch event used the same hour [S-87].
20. 16 gift codes listed on eog, said to work as of August 2026; none checked by us [S-85].

## Conflicts

- Gacha rates: eog 1% / 7% / 22% with pity 70 / 30 / 10 [S-85] against the other rate set from zeroluck [S-25].
- Guild donations: eog "3 a day free, 5 for spenders" [S-85] against official "up to 5, 1 free" [S-87].
- Fantomon unlock: Lv 50 [S-85][S-87] against 51 in rule R-011.
- Vendor Booth: Lv 20 [S-87] against 18 in rule R-011 (our account met it early through the Bellflower tutorial).
- Gem fusion: eog says 3 into 1 only for the first two steps, then 2 into 1 [S-85]; systems/gems.md has 3 into 1 from a tier D site [S-55] with no tier limit.
- Skill count: official "over 200" (April) then "300+" (launch) [S-87]; eog's database has 361 [S-85].
- Luminium: eog says it converts to Dawnium 1:1 [S-85]; single source, check against systems/currencies.md.

## Gaps (not found)

- Relic drop chance and drop place per relic; ingredient drop sources and chances (lootandwaifus offline).
- Grand Treasure Hunt price per floor item (only totals).
- Real EXP-per-level and Raw Ore tables.
- Kingdom Rank requirement table, Arena reward tables, skill shard cost per quality, base rarity per skill.
- Which fusion step each success rate (100 / 36 / 18 / 8 / 4%) applies to.
- Dawnium ladder for guild donations 2 to 5.
- Official gift-code page (on webcp01.boltray.com, not fetched); official site has no FAQ or patch notes and no post after 2026-06-05.
- Whether global keeps the CN day schedule after Season 2.

## New glossary terms

- Aurodrasil Energy: currency spent in the Grand Treasure Hunt -> systems/events.md
- Cloud Jade: exploration item needed on the Loong Haven map (7 needed) -> systems/exploration.md
- Purifying Hammer / Brick Switch / Flame Hammer / Frost Hammer: exploration items for Aethyris, Harpadia and Ignis -> systems/exploration.md
- Sand Mine: material realm that gives Chrono Sand, tool Sand Shovel -> systems/material-realms.md
- Worn Gauntlet (official: Worn Knuckles): tool for the Monster Cave realm -> systems/material-realms.md
- Skill Test: damage dummy at Home > Character > Skills > Test, from Lv 40 -> systems/skills.md
- Resonance (gear): percent boost to base stats, one step per 5 enhancement levels across all slots -> systems/gear.md
- Alchemy Pot: Home object that dismantles gear into Refined Ores and Raw Ores, Lv 12 -> systems/cart-and-home.md
- Commercium: trading hub with Trading House and Auction House, Lv 40, by airship from Home -> systems/auction-house.md
- Arborisfatum: the tree at Home where Fantomons are summoned and Destiny Fruit grows -> systems/fantomons.md
- Hieromon: guardian beast of a kingdom (Storm Griffin, Flamoenix, Yamata no Orochi, Primordial Loong) -> systems/world-and-kingdoms.md
- Covenite: premium-banner currency earned from Standard pulls -> systems/gacha.md
- Primal Forge: item bought with Chaos Crystals from the Mysterious NPC after Chaos Invasion -> systems/events.md
- Lucky Statue (eog: Lucky Idol): Treasure Hunt reward raising dungeon chest double chance from 10% to 60% -> systems/events.md
- Primal Gem (eog: Primordial Gem): Treasure Hunt reward raising gem acquisition from 10% to 60% -> systems/gems.md
- Doom DMG: damage type dealing +100% to shields and summons -> systems/skills.md
- Erosion: Dark damage over time for 3 turns -> systems/skills.md
- Demonbind Tower: tower mode opening at Lv 116 -> systems/towers.md
- Fantomon Manifestation: Adult evolution at Lv 108 -> systems/fantomons.md
- Whaleback Island / Acme Nexus / Astral Odyssey / Grotesque Fairground / Frostfire Voyage: seasonal maps (days 26, 71, 128, 240, 349) -> systems/seasons.md
- Tier 5 to 8 class names (Ravager/Templar/Magister/Prophet; Reaver/Empyrean/Cataclyst/Oracle; Annihilator/Seraph/Voidcaller/Ascendant; Hellblade/Paragon/Obliterator/Fateweaver) -> systems/classes-overview.md
- Visage: cosmetic appearance (KonoSuba collab: Otherworldly Adventurer, Crusader) -> systems/events.md

## Answers to open gaps (gap -> answer -> target page)

- Astral Pact points beyond the known total and in later seasons -> per-source point table for S1, S2, S3 plus 16 S1 milestones [S-85] -> systems/astral-pact.md
- Class tier levels and names past tier 4 -> job table 44 / 82 / 106 / 136 / 172 / 198 with class-level gates; tier 5 to 8 names [S-85] -> systems/classes-overview.md
- When later kingdoms open -> Harpadia day 226 (S4), Ignis day 335 (S5) [S-85] -> systems/seasons.md, systems/world-and-kingdoms.md
- What Whaleback Island and Acme Nexus are -> seasonal maps, days 26 and 71 (Acme Nexus needs Lv 130) [S-85] -> systems/seasons.md
- Dungeon level gates -> Aquorigin Shrine Lv 100 (day 24), Warlord's Rest Lv 130 (day 60); S3 to S5 names and power walls [S-85] -> systems/dungeons.md
- Where Verdantglade exploration tools are -> Keys: Rabbit Vault, Gorge Depths, Owl Vault; Potions: Jungle Vault, Monolith Ruins V, Stagnant Jungle, Sunken Forest, Sunrise Isle; Drills: Vine Peninsula, Hidden Camp, Hideout [S-85] -> systems/goddess-statues.md, systems/exploration.md
- Loong Haven season item -> Cloud Jade, 7 needed [S-85] -> systems/exploration.md
- Statue counts -> Goddess Statues 17 (Verdantglade) or 18; Lost Goddess Statues 49 / 68 / 74 / 79 / 78 / 82 / 81 [S-85] -> systems/goddess-statues.md
- Gem values, names, fusion -> value per tier, four gem pairs with slot fits, 3 into 1 then 2 into 1, success rates [S-85] -> systems/gems.md
- Sand realm and rank scaling -> Sand Mine with Sand Shovel; yield table per Kingdom Rank; multiplier = Rolla figure / 1200 [S-85]; rewards scale with Rank [S-87] -> systems/material-realms.md, systems/stamina.md
- Gear sockets and Off-hand -> 2 sockets on Lv 130 gear in S2, max 4 [S-85]; Off-hand after Class II [S-87] -> systems/gear.md
- Guild 15 or 20 -> 15 [S-87] -> systems/levels-and-unlocks.md, systems/guild.md
- Vendor Booth 18 or 20 -> 20 [S-87] -> systems/levels-and-unlocks.md
- Fantomons 50 or 51 -> 50 [S-87][S-85] -> systems/levels-and-unlocks.md
- Dismantle, Arena, Commercium, Skill Test levels -> 12, 40, 40, 40 [S-87][S-85] -> systems/levels-and-unlocks.md
- Donations per day -> up to 5, 1 free, 70 Dawnium for two more [S-87] -> systems/guild.md
- Fantomon rarities and slot weights -> Mythic Aegiswing, Nyxarchon, Pandarial; six Legendary; four Epic; 100 / 50 / 20% [S-85] -> systems/fantomons.md
- Companion stat nodes -> levels 20, 50, 70, 100 (70 repeats 20, 100 repeats 50), skins at 60 [S-85] -> systems/companions.md
- Cooking numbers -> 87 recipes, per-recipe brackets 100 / 50 / 20 / 5% [S-85] -> systems/cooking-and-dishes.md
- Treasure Hunt currency and cost -> Aurodrasil Energy, about 3,240 for stages 1 to 5; mini-games Bingo Draw, Lucky Scratch, Feneck's Puzzle [S-85] -> systems/events.md
- Void Rift schedule -> alternates with Chaos Invasion on Sundays, 10 attempts in 24 hours [S-85] -> systems/events.md
- Skill cooldowns and effect texts -> 361 skills with cooldowns and damage by quality; quality steps Rare 2, Epic 3, Legendary 4, Mythic 6, Divine 8, Immortal 11 [S-85] -> systems/skills.md and class pages
- Value of a Quest Scroll -> 120 Dawnium equivalent (eog's valuation) [S-85] -> systems/shops.md
- Monster types -> 215 monsters by type and kingdom [S-85] -> systems/monsters.md
- Tower unlock -> Demonbind Tower Lv 116 [S-85] -> systems/towers.md
- Arena ticket timing -> save tickets before the weekly reset, spend early in the new season [S-87]; eog says 20 on day one [S-85] -> systems/arena-and-pvp.md
- Idle cap and Temporal Crystal -> 36 hours; 2 hours of Bed and Cart [S-87] -> systems/cart-and-home.md, systems/currencies.md
- Gift codes -> 16 codes with redeem path Home > Main Menu > User Center > Gift Code [S-85] -> systems/codes.md
