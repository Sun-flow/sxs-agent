# Research report to integrate: zeroluck

<!-- index: Working file for the integration pass; delete when folded in -->

## zeroluck.gg mining and kb_fetch.py extension: report

**Headline:** zeroluck.gg's Sword x Staff pages could not be downloaded. Every `https://zeroluck.gg/sword-x-staff/...` URL answers HTTP 404 to curl and to the script from this environment, and the site's sitemaps list only two other games (7dso, nte). robots.txt allows the section, so this is not a block. The same URLs do answer through WebFetch, so I read the section that way (about 50 calls). The notes and data are therefore a small model's reading of each page, not raw text or `__NEXT_DATA__`. Numbers agreed across two passes and across pages, but treat them as tier C.

### Files written
- `/home/user/sxs-agent/scripts/kb_fetch.py` (extended)
- `/home/user/sxs-agent/knowledge/sources/notes/zeroluck.md`
- `/home/user/sxs-agent/knowledge/sources/_register-zeroluck.md` (S-80 row; no fragment path was given, so I followed the wave-1 naming)
- `/home/user/sxs-agent/knowledge/data/gacha-rates.json` (13 banners)
- `/home/user/sxs-agent/knowledge/data/monsters.json` (37 named monsters)
- `/home/user/sxs-agent/knowledge/data/gear-tables.json` (21 records)
- `/home/user/sxs-agent/knowledge/data/combat-stats.json` (20 stats)
- `/home/user/sxs-agent/knowledge/data/life-skills.json` (18 records)

I did not write `items.json`: the item database page was not reachable. I did not write `skills-zeroluck.json`: all 72 class sample skills are already in `skills.json`.

`kb_check.py` reports S-80 as undefined (two lines) until the row is merged into `sources/README.md`. The other problems it lists are older broken links, not mine.

### kb_fetch.py
- **New mechanism:** a `SITES` table drives `fetch_site()`. Per site it reads robots.txt, takes section URLs from the sitemaps and from links on seed pages, and fetches each page with the delay. Output is `<slug>.txt`, plus `<slug>.next.json` when the page has `__NEXT_DATA__`, plus `manifest.json`.
- **robots handling:** uses `urllib.robotparser` and also parses `Content-Signal`. A site is refused if robots disallows our user agent, or if the signal says `ai-input=no` or `use=no`.
- **Bot check:** `get()` now turns an HTTP 403/429/503 carrying a Cloudflare challenge into `BotCheck`. Tested against a local stub; a plain 403 stays an `HTTPError`.
- **Kept working:** `all` and `status` cover all six sources; standard library only; docstring updated; `tests/check_repo.py` passes.

| Subcommand | Result of one run | Notes |
|---|---|---|
| `eog` | 18 pages, 0 skipped | robots: `search=yes, ai-train=no, use=reference`; `ClaudeBot` and other training crawlers disallowed (we are not one) |
| `official` | 18 pages, 0 skipped | home, 4 list pages, news 186 and 190-203 minus gaps; robots allows all but `/api/` |
| `zeroluck` | 0 pages, 15 seeds 404 | manifest records the 404s |
| `lootandwaifus` | 0 pages, 7 seeds 404 | no "sword" URL among the 636 in its sitemap; same pattern as zeroluck |

My files sit beside the other agent's in `raw/eog/` and `raw/official/` under different names (`games-sword-x-staff-guides-*.txt`, `news-203.txt`); nothing of theirs was overwritten or deleted.

### Key facts for the strategy guides (all [S-80])
1. **Standard and Premium Prayer rates:** shard 65.69%, Rare 24%, Epic 7.9%, Legendary 2.41%. Skill pool is 238 skills (85 Legendary, 78 Epic, 75 Rare; 47 Legendary attack skills).
2. **Relic gacha (Aeonic) rates:**
   - Rare: 73.55 Rare shard / 12.46 Rare / 11.03 Epic shard / 1.84 Legendary shard / 1 Epic / 0.12 Legendary.
   - Epic: 69.87 Epic shard / 13.79 Legendary shard / 12.46 Epic / 2.76 Mythic shard / 1 Legendary / 0.12 Mythic.
   - Legendary: 68.09 Legendary shard / 16.63 Legendary / 14.19 Mythic shard / 1.09 Mythic.
   - Mythic: 81.32 Mythic shard / 18.68 Mythic.
   - Elemental: 79.11 Epic / 16.63 Legendary / 4.26 Mythic.
   - Cost is 10 badges per capsule.
3. **Fantomon summon rates:** 44.24 Rare aptitude food, 14.16 Epic food, 13.27 Legendary shard, 12.04 "Legendary other", 7.96 Epic shard, 6.37 Epic Fantomon, 1.96 Legendary Fantomon.
4. **Gear quality:** substat lines are white 0, blue 1-2, purple 3, orange/gold/red 4. Roll multipliers run 0.7-0.8 up to 0.8-1.25. Quality beats enhancement.
5. **Enhancement cost per level (Rolla / Raw Ore / Refined Ore):** +1 70/35/0; +10 160/80/30; +20 1,160/580/170; +40 4,160/2,080/330; +250 200,000/100,000/550. Total to +250 is 17.4M Rolla, 8.7M Raw Ore, 22,280 Refined Ore. Rolla is always twice the Raw Ore.
6. **Resonance:** a step every 5 gear levels, cycling HP, ATK, DEF, SPD, 240 steps; the site says "+20% flat".
7. **Gear counts:** 629 pieces, 28 sets (2- and 4-piece bonuses), 8 gem types, 360 gems. Off-hand types are Shield, Glove, Book, Ball.
8. **Class gates (class level / total level):** 18/20, 16/48, 19/89, 40/180.
9. **Mage line weights:** Sorcerer line has the top ATK weight at every tier (1900, 2950, 3900, 5400) with a Block Penetration trait. Sage line is flat (1250, 2050, 3050, then 4550 HP / 4050 others) with Crit Avoid and Healing.
10. **Combat stats:** 20 stats. Accuracy counters Block Rate, Crit RES counters Crit Rate, Effect RES counters Effect Hit Rate. Separate PvE and PvP damage and resistance stats exist.
11. **Guild planting and breeding:** Garden gives oil, Sheepfold wool, Roost eggs (Fantomon aptitude materials). Sessions are 6 / 9 / 12 minutes, giving 60 Basic / 20 Premium / 60 Premium Treats plus 6 / 12 / 24 materials.
12. **Guild gathering:** Forge gives Steel, Power Station gives Kanstein Cell (Glyph Research fuel), Mana Vein gives Mana Cluster.
13. **Fantomons:** 13 total; 4 Attacker, 4 Tank, 5 Support; 6 Legendary, 4 Epic; 12 evolve from Childhood to Adulthood. Treats come in Basic, Premium and Deluxe.
14. **Relics:** 855 pieces over 6 regions; level and star both cap at 6. Level grows one main stat, star grows an element Affinity (damage) or Aegis (resistance). 75 relics have a task-based bonus.
15. **Monsters:** game labels are Minion Monster (159), Elite Monster (67), Boss (39), Hieromon (9), plus Chaos Tyrant. Hieromon named: Storm Griffin, Flamoenix, Yamata no Orochi, Primordial Loong, Lord of Decay, Lord of Ruin.
16. **Cooking:** 67 recipes (5 recovery, 62 buff), proficiency to Lv 5 per dish. Starlight Bread restores Stamina.
17. **Battle pass:** 70 tiers, 100 Dawnium per tier skip, 16 Normal and 4 Season passes. Buying premium later pays out earlier tiers. Season pass headline is a chosen Legendary Fantomon.
18. **Currencies:** Luminium converts to Dawnium 1:1.
19. **Codes:** 16 codes listed as active on 2026-06-14 (table in the notes).

### Answers to open gaps (gap -> answer -> target page)
- Affix lines per gear rarity -> 0 / 1-2 / 3 / 4 / 4 / 4 from white to red, with roll ranges -> `systems/gear.md`
- Enhancement cap -> data maximum is +250, with cost points and total -> `systems/gear.md`
- Off-hand and weapon types -> Shield, Glove, Book, Ball; Sword, Wand (unlock level still unknown) -> `systems/gear.md`
- Gem structure -> 8 types, 360 gems, merge upward; no names or values -> `systems/gems.md`
- Live relic gacha rates per tier -> six tables above; no pity stated -> `systems/relics.md`, `systems/gacha.md`
- Relic level and star caps -> both 6; level = main stat, star = Affinity or Aegis -> `systems/relics.md`
- True Standard Prayer rates -> 65.69 / 24 / 7.9 / 2.41, Premium identical; still disagrees with EOG -> `systems/skills.md`, `systems/gacha.md`
- What the Affection banner is -> Affection Token spent at the Goddess Statue "for rewards"; no rate table -> `systems/gacha.md`
- Which guild building makes which aptitude material -> Garden oil, Sheepfold wool, Roost eggs -> `systems/fantomons.md`
- Guild Farm workings -> timed AFK sessions with the yields above; tool tiers 5 (planting/breeding) and 3 (gathering) -> `systems/guild.md`
- Fantomon types and rarities -> totals only (4/4/5; 6 Legendary, 4 Epic); per-Fantomon rows unread -> `systems/fantomons.md`
- The game's own monster tiers -> Minion Monster, Elite Monster, Boss, Hieromon -> `systems/monsters.md`
- Hieromon roster -> 9 exist; adds Lord of Decay and Lord of Ruin; 3 unnamed -> `systems/monsters.md`
- Which dishes heal or buff -> recovery: Green Rice Ball, Chargrilled Mushroom, Verdant Dew, Shepherd's Purse Pancake, Starlight Bread; Jelly Bean Pals and Cheerful Greens are buff dishes -> `systems/cooking-and-dishes.md`
- Pilgrimage pass structure -> 16 Normal + 4 Season passes, retroactive premium; free-lane list and length still unknown -> `systems/events.md`
- Dawnium price of a pull -> not on the site; only 10 badges per capsule -> `systems/currencies.md`
- Class-level gates -> same numbers, still this single source -> `systems/classes-overview.md`

### Conflicts
- **Standard Prayer rates:** zeroluck 2.41 / 7.9 / 24 / 65.69 [S-80] vs EOG.GG 1 / 7 / 22 [S-15]. Already noted in `skills.md`, unresolved.
- **Resonance size:** zeroluck says "+20% flat" per step [S-80]; `gear.md` and R-092 show a small bonus per band (e.g. HP +2%). Units are unclear on the site.
- **Enhancement cap:** zeroluck data maximum +250 [S-80] vs +100 base with seasonal +160 to +180 [S-03][S-02]. Probably data ceiling vs live cap.
- **Gear rarity names:** zeroluck uses six colours, white to red [S-80]; our pages use Mythic/Divine names. Mapping is not stated.
- **Relic cap:** zeroluck "maxes at 6" for level and star [S-80]; `relics.md` discusses enhance costs "beyond +4" and resonance +10. Check that these are the same scales.
- **Starlight Bread:** filed under "Restore HP" but described as restoring Stamina, on the same page.
- **Life skills page:** its summary says six facilities give Treats; its detail says only three do. Notes follow the detail.
- **Site contradicts itself across readers:** pages exist for WebFetch, 404 for curl. Cause unknown.

### Gaps
- No raw cache or `__NEXT_DATA__` for zeroluck.
- Friendship page URL not found (7 guesses returned 404).
- Database pages (pets, monsters, items with 7,952 entries, interactive map) and the section hub are unreachable or their URLs are unknown.
- Game modes page is empty on the site itself ("0 modes").
- The site has none of: unlock levels, cost per pull, pity, per-tier pass rewards, relic/set/gem/recipe names, skill effects, element chart, drop tables.
- "Legendary other" (12.04%) on the Fantomon summon is unexplained.
- Loot & Waifus's Sword x Staff pages also return 404 here, so its JSON dumps were not fetched.

### New glossary terms
- Minion Monster / Elite Monster / Hieromon: the game's monster type labels -> `systems/monsters.md`
- Near Weak / Near Strong / Far Weak / Far Strong: data attack profiles (melee or ranged, light or heavy) -> `systems/monsters.md`
- Lord of Decay, Lord of Ruin: Hieromon named in game data -> `systems/monsters.md`
- Affinity / Aegis: relic star stat lines; element damage dealt / element resistance -> `systems/relics.md`
- Resonance (gear): bonus step every 5 enhancement levels, cycling HP, ATK, DEF, SPD -> `systems/gear.md`
- Block Efficiency: how much damage a block removes -> `data/combat-stats.json`
- Effect Hit Rate / Effect RES: chance to land / resist debuffs -> `data/combat-stats.json`
- Resilience: defensive stat described as companion sturdiness -> `data/combat-stats.json`
- Healing Boost: heal strength stat with no icon -> `data/combat-stats.json`
- PvE / PvP Bonus DMG and DMG RES: mode-specific damage stats -> `data/combat-stats.json`
- AFK Session: a timed guild facility run -> `systems/guild.md`
- Kanstein Cell: Power Station output, fuel for Glyph Research -> `systems/guild.md`
- Mana Cluster / Steel: Mana Vein / Forge outputs for guild projects -> `systems/guild.md`
- Treats (Basic, Premium, Deluxe): Fantomon EXP food -> `systems/fantomons.md`
- Childhood / Adulthood: Fantomon evolution stages -> `systems/fantomons.md`
- Voucher: Mythic-coloured wallet currency for in-game purchases -> `systems/currencies.md`
- Prayer Goals: milestone rewards on Prayer banners -> `systems/gacha.md`
- Aliases used by zeroluck: "Gear Prayer" = Aeonic Gacha, "Pet Prayer" = Fantomon summon, "Friend Prayer" = Affection banner, "Legend rank" = Tier 5, "Alchemy Pot" = cooking pot, "Ziwei stars" = gem types -> `glossary.md`
