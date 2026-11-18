# World and kingdoms

<!-- index: Read to know which kingdom comes when, what each one holds (town, currency, tool, dungeons) and how the next one opens -->

> **Summary:** The world of Kanstein is played kingdom by kingdom: Originisle (tutorial), Verdantglade, Cinder Ridge,
> Aqualis (all Season 1), then Loong Haven (Season 2) and Aethyris (Season 3). Each kingdom has its own town, Kingdom
> Shop currency, exploration tool, relic pool and daily dungeons, and its dungeons open on fixed server days.
> Buy each kingdom's tool first: every tool opens extra ground with at least one more statue.
> **Applies:** all seasons
> **Related:** [Exploration](exploration.md), [Goddess Statues](goddess-statues.md), [Kingdom Rank](kingdom-rank.md),
> [Levels and unlocks](levels-and-unlocks.md), [Seasons](seasons.md), [Dungeons](dungeons.md), [Shops](shops.md),
> [Currencies](currencies.md), data in [kingdoms.json](../data/kingdoms.json); rules R-006, R-069, R-134, R-145

## The world in one table

| # | Kingdom | Season | Character level while there | Town / hub | Kingdom currency | Kingdom tool (bought in its Kingdom Shop) | Daily dungeons (in order) |
|---|---|---|---|---|---|---|---|
| 0 | Originisle | 1 (tutorial) | 1 to about 10 ❓ | none seen | none | none | none |
| 1 | Verdantglade | 1 | about 10 to 40-44 | Drasilgard [S-03][R-134] | Abundance Leaf [S-01][R-134] | Withering Potion [S-01] | Auroradrasil [S-03] |
| 2 | Cinder Ridge | 1 | about 40-44 to ❓ | Fortburg [S-03] | ❓ | Magic Drill [S-01] | Mecha Summit [S-03] |
| 3 | Aqualis | 1 | ❓ to 100, then the Season 1 cap (about 124) | ❓ | ❓ | Water Mine [S-01] | Ocean Palace Ruins, Aquorigin Shrine, Hellhold [S-03] |
| 4 | Loong Haven | 2 | 100 to 120 and beyond | "Unrakumotogo" is named as the place of the 4th class change [S-03] | ❓ | "New Season Item" (name not given) [S-53] | Demonseal Gorge, Warlord's Rest, Cloudcrest Temple, Bladeshire, Celestship [S-02] |
| 5 | Aethyris | 3 | ❓ | ❓ | ❓ | ❓ | ❓ |

- The order Originisle, Verdantglade, Cinder Ridge, Aqualis, Loong Haven is confirmed by our own area map
  buttons and by the guides [R-006][S-01][S-03].
- The Gateway Key is a tool that works in every kingdom ("All - Gateway Key") [S-01].
- The lore names a fifth continent, Aethyris, home of the vanished Aethyrine [S-03]. The Season 2 calendar ends with
  "Season 3 Aethyris" [S-02].
- A map tool lists two more kingdom names as empty filters, Harpadia and Ignis: possible later seasons ❓ [S-50].
- Level ranges are pieced together from single facts and are approximate: the second class change happens at
  Lv 44 in Cinder Ridge [S-03][S-54]; Fantomons unlock at Lv 50, in Cinder Ridge [S-52]; players are Lv 100 when
  the Aquorigin Shrine opens in Aqualis [S-03]; the 4th class change is at Lv 106 in Loong Haven [S-02][S-03].

## Originisle

- The starting island: tutorial ground where the first Goddess Statue raises Blessing Level to 2 [R-070].
- Leave it through the Voyage Obelisk, "your pathway to the next kingdom" [R-069]. Verdantglade's own Voyage
  Obelisk is one marker on the map tool, in the far zone group around Verdantglade XVII [S-50].
- Originisle is fully explored and blessed on our account [R-070]; it is not yet in `resource/world/zones.json`.

## Verdantglade

- Lore: forest land of the Dryason, with the world tree Auroradrasil; the village Drasilgard sits at its foot
  [S-03].
- **Town: Drasilgard.** NPCs: the Village Chief Narss (story), Hermes the merchant-alchemist (Kingdom Shop for
  Abundance Leaves), Carol the Black Cat (appearance change); a Portal [R-134][S-03].
- **Kingdom Shop (Hermes).** Four shop levels; level 1 already sells the Withering Potion (1.8K leaves discounted,
  3K full price), Stellatie, Refined Ore, recipes and gifts. The full table is in `docs/shop-tables.md` [R-134].
  A guide quotes "3k leaves to buy a key/potion" [S-01].
- **Currency: Abundance Leaf.** Sources: map chests (60 from one chest) [R-076], commission rewards (pick the
  kingdom-currency reward when a tool is close) [S-01], map clearing ❓ [S-04].
- **Tool: Withering Potion**, clears a Vine Blockade [S-01][R-134]. Verdantglade's map needs 5 Withering Potions,
  3 Magic Drills and 3 Gateway Keys in total (11 gated spots) [S-50].
- **Zones.** Seventeen numbered main zones (Verdantglade I to XVII) and about fifty named side zones [S-50]. Our
  observed zones, recommended power and links are in `resource/world/zones.json`; the main line seen so far runs
  from 9.6K (Highland Woods) to 37K (Verdantglade XI) and 44K (Amber Gorge) [R-076][R-145].
- **Map contents** (marker counts): 17 Goddess Statues, 49 Lost Goddess Statues, 25 Portals, 4 Hero Statues,
  2 Witch Statues, 1 Voyage Obelisk, 4 Power Gates, 4 Elemental Gates, 2 Rank Gates, 3 Sealed Pillars,
  6 Challenge Steles, 4 Trait Steles, 2 Lucky Roulettes, and 19 mini-dungeons (3 Ancient Keeps, 3 Temple Ruins,
  3 Monster Caves, 3 Gold Caves, 3 Iron Mines, 2 Sand Mines, Auroradrasil, "Moonshadow Forest") [S-50].
- **Rank gates.** Verdantglade V to VI needs Apprentice II; XI to XII needs Apprentice III [R-145].
- **Daily dungeon: Auroradrasil.** Normal from server day 1 with no power requirement; Hard needs 36K power
  [S-03] and an S rating on Normal ❓ [S-04]. The story version is a free 4-player dungeon [R-133].
- **Rank material:** Bellflowers from the free Verdantglade Flower Harvest [R-123]; see [Kingdom Rank](kingdom-rank.md).

## Cinder Ridge

- Lore: peaks and desert, ruined magitech; Fortburg is the only town left [S-03].
- **Town: Fortburg.** NPC names are not known ❓. The tier D site's Fortburg page lists resources ("Crystal
  Shards", "Scavenged Magitech", "Desert Herbs") that no other source knows ❓ [S-04].
- **Tool: Magic Drill**, smashes a Boulder Blockade [S-01][R-151]. It is sold in the Cinder Ridge Kingdom Shop,
  yet three drill spots are back in Verdantglade [S-50], so expect to return to earlier kingdoms with later tools.
- **What unlocks here:** second class change at Lv 44 [S-03][S-54]; the Grand Arena (Lv 40 plus Rank
  Advancement) [S-03]; Fantomons at Lv 50 [S-52]; the premium skill banner and the Auction House [S-54].
- **Daily dungeon: Mecha Summit.** Normal from server day 4; Hard needs 180K power [S-03].
- Currency name, shop NPC, ranks and zone list: ❓.

## Aqualis

- Lore: the ocean realm, home of the Merean, full of yokai tales [S-03].
- **Tool: Water Mine** [S-01]. The obstacle it clears is not named in any source ❓.
- **What unlocks here:** Lv 100 lossless class change [S-03]; from Lv 100 everything gained is seasonal
  ([Seasons](seasons.md)).
- **Daily dungeons** [S-03][S-01]:

| Dungeon | Opens (server day) | Normal | Hard | Nightmare | Purgatory |
|---|---|---|---|---|---|
| Ocean Palace Ruins | 12 | none | 580K | - | - |
| Aquorigin Shrine | 24, and Lv 100 | 930K | 1.45M | 2.05M | - |
| Hellhold | 33 | 2.25M | 2.75M | 3.9M | 6.2M |

- "Whaleback Island" appears on the Season 1 calendar on server day 26, in a different colour from dungeons:
  probably a new map area or event ❓ [S-01].
- Town, currency, shop NPC, ranks: ❓.

## Loong Haven (Season 2)

- Lore: ancient land of snow peaks, waterfalls, bamboo groves and maple forests; the Loongborn live here [S-03].
- Opens on server day 47, the first day of Season 2; the first two weeks are a pre-season [S-02]. See
  [Seasons](seasons.md).
- **What unlocks here:** T4 class at Lv 106, Adult Fantomon at Lv 108, Demonbind Tower (gems) at Lv 116, top rank
  Champion III at Lv 120, second dungeon at Lv 130 [S-02][S-53].
- New companions: Wuji, Ming, Hui, Jiangwang, Suimo [S-02]. Two relic pools (the second opens one month in) [S-02].
- Gems start dropping here; new gear affixes Dodge and Flash appear from here [S-02][S-52].
- **Daily dungeons** [S-02]:

| Dungeon | Opens (server day) | Gear level | Normal | Hard | Nightmare | Purgatory |
|---|---|---|---|---|---|---|
| Demonseal Gorge (pre-season, Mythic only) | 47 | 130 | none | 2.35M | not available | - |
| Warlord's Rest (needs Lv 130) | 60 | 165 | 3.55M | 5M | 6M | - |
| Cloudcrest Temple | 73 | 195 | 6.2M | 7.7M | 9.8M | - |
| Bladeshire | 86 | 225 | 10M | 12.5M | 15.8M | - |
| Celestship | 99 | 250 | 16.5M | 20M | 24.5M | 40M |

## Aethyris (Season 3)

Starts on server day 114 on the guide author's server (29 November 2026 there) [S-02]. Nothing else is known ❓.

## How the next kingdom opens

1. **Inside Season 1** the kingdoms are joined by the story: finish the main Explore quests, then use the Voyage
   Obelisk [R-069]. Progress is also held back by rank gates (Sealed Stone Gates need a Kingdom Rank [R-145]) and by
   recommended power [R-084].
2. **Dungeons open by server day**, counted from the server's launch, not by your progress [S-03][S-02]. Meeting
   each new dungeon's power threshold on its opening day is the main schedule target [S-01].
3. **A new kingdom after Aqualis opens with a new season** on a fixed server day for everybody [S-02].

## Servers and merges

- A server holds up to 5,000 players and servers merge later; guilds are per server. Our account is on
  Forgehall [R-006].
- Server time is UTC-5; the daily reset is 8:00 [R-024].
- The global launch was 19 May 2026, 8:30 (UTC-5), mainly for North America and Europe [S-03]. Servers launched
  later run the same calendar shifted by their launch date: the guides' own server reached day 47 on
  23 September 2026, so it opened on 8 August 2026 [S-02].
- Calendar for our server: find the server's launch day once (❓ not yet read), then every "server day" in this
  page turns into a date.

## Open questions

- ❓ Kingdom currency names, shop NPCs and town names for Cinder Ridge (beyond Fortburg), Aqualis and Loong Haven.
  Confirm from the Kingdom Shop screen in each town.
- ❓ What the Water Mine clears, and the name of Loong Haven's tool. Confirm from the first blockade card there.
- ❓ Exact level at which each kingdom is entered. Confirm from our own level when the Voyage Obelisk is used.
- ❓ Forgehall's launch date (server day 1) and whether it has merged.
- ❓ Whether Harpadia and Ignis are real future kingdoms.

## Sources

- [S-01] sections 1 (calendar), 2 (kingdom tools, commissions)
- [S-02] section II calendars and "Season 2 gear power comparison", sections IV-VI
- [S-03] Fandom: Maps, Daily Dungeons, Class Selection, Classes Overview, Arena, Companions, Launch FAQ
- [S-04] sxswiki map, Fortburg, Withering Potion pages (leads only)
- [S-50] Verdantglade marker and tool counts; [S-52] Fantomons, gems; [S-53] milestones; [S-54] unlock levels
- Rules R-006, R-024, R-069, R-070, R-076, R-084, R-123, R-133, R-134, R-145, R-151; `resource/world/zones.json`;
  `docs/shop-tables.md`
