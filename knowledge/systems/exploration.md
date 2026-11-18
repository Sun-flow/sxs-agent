# Exploration

<!-- index: Read to understand why map exploration is the main growth engine, what blocks a zone and which tool or stat removes each block -->

> **Summary:** Exploring a zone to 100% lets you activate its statue; statues raise bed EXP and Cart output, which
> raise level and power, which open the next zones. Push the map before anything else, buy every kingdom tool
> (each one hides at least one more statue), and use speed-ups only after the newest statues are lit.
> **Applies:** all seasons (every new kingdom restarts the loop)
> **Related:** [Goddess Statues](goddess-statues.md), [World and kingdoms](world-and-kingdoms.md),
> [Kingdom Rank](kingdom-rank.md), [Cart and home](cart-and-home.md), [Commissions](commissions.md),
> [Stamina](stamina.md); rules R-002, R-065, R-070, R-084, R-130, R-135, R-145, R-151, R-153, R-159, R-175

## The loop

```
explore zone to 100%  ->  activate its Goddess Statue / Lost Goddess Statue
        ^                              |
        |                              v
  more power and level   <-   more bed EXP per hour, higher Cart caps and yields
```

- "The faster you explore, the more Lost Goddess Statues you unlock, the more passive EXP you gain, the stronger
  you become" [S-01].
- Three things move the map forward [S-01]:
  1. **Combat power**: more zones can be cleared.
  2. **Kingdom tools**: each opens extra ground that always holds at least one more statue; they are the top
     priority purchase in every Kingdom Shop.
  3. **Daily commissions**: they pay kingdom currency (for tools) and Premium Commissions; do them aggressively,
     even when they cost stamina.
- Side zones matter as much as the story line: they are small, quick, and most Lost Goddess Statues are in them
  [R-070]; tier D guides say the same ("clear side zones first") ❓ [S-04].

## Zones

- A kingdom's map is split into numbered main zones (Verdantglade I to XVII) and named side zones; dotted lines
  mark zone borders [R-132][S-50].
- Each unfinished zone shows "Exploration: N%" and, when gated, a recommended power under its name on the area
  map [R-076]. A recommended power well above yours is a wall: stop there and get stronger [R-084]. Our bot takes
  fights up to 25% above its own power [R-127].
- Exploration % rises with fog revealed, pickups, fights and map objects [R-021][R-002]. In a zone that is not yet
  blessed the whole minimap stays shaded and the % comes from objects [R-143].
- Fog: revealed by walking to the zone's own edge, never by tapping fog [R-130][R-146].
- 100% means every objective cleared and all mist revealed [R-002]. The zone's own Explore quest lists what is
  left [R-142]. Exploration Goals pay milestone rewards [R-052].
- Order used by our bot outside quests: lowest-power unblessed zone first [R-135].
- Portals: each main zone has fast-travel Portals (25 in Verdantglade [S-50]); teleport into the zone you are
  heading to [R-175][R-152]. Kingdom to kingdom travel is by Voyage Obelisk [R-069].

## Obstacles and what opens each

| Obstacle | What it needs | Where the key comes from | Rule / source |
|---|---|---|---|
| Recommended power on a zone | Power near the number | Gear, relics, skills, level | [R-084] |
| Gate of Power (stone pillar) | Power at or above the gate's number; then a free Open | same | [R-086]; 4 in Verdantglade [S-50] |
| Sealed Stone Gate ("Rank Gate") | A Kingdom Rank (Apprentice II, Apprentice III ...); then a free Unlock | [Kingdom Rank](kingdom-rank.md) | [R-145]; 2 in Verdantglade [S-50] |
| Vine Blockade | 1 Withering Potion | Verdantglade Kingdom Shop (Abundance Leaves) | [S-01][R-134]; 5 in Verdantglade [S-50] |
| Boulder Blockade (e.g. Hidden Camp) | 1 Magic Drill | Cinder Ridge Kingdom Shop | [R-151][S-01]; 3 in Verdantglade [S-50] |
| Water obstacle (name ❓) | Water Mine | Aqualis Kingdom Shop | [S-01] |
| Gateway (name of the object ❓) | 1 Gateway Key, usable in every kingdom | Kingdom Shops; also a Wheel of Destiny prize | [S-01]; 3 in Verdantglade [S-50] |
| Sealing Pillar ("Sealed Pillar") | ❓ (not seen by us) | ❓ | 3 in Verdantglade [S-50] |
| Gate of Elements (Gate of Wind ...) | Total affinity of one element; relics or up to 3 helpers supply it | Relics; NPC companions carry 101 each | [R-159]; 4 in Verdantglade [S-50] |
| Puzzle (Fonik's boxes, Energy Circuits, tile floor) | Solve it, or spend 1 Golden Beetle to skip | Golden Beetle: Vault, 50 Dawnium | [R-153][R-072][R-085] |
| Red "!" NPC | Talk first; it gates what is around it | - | [R-062] |
| Bracketed guards | Beat the guards before the target responds | - | [R-041] |
| Challenge Stele, Trait Stele | ❓ (not seen by us) | ❓ | 6 and 4 in Verdantglade [S-50] |

Tool stock to carry into a new season, from a preparation checklist: Gateway Key x5, Water Mine x2, Magic Drill
x1, Withering Potion x1, plus 7 of the new season's own tool [S-53][S-85]. For Loong Haven that tool is **Cloud
Jade** (7 needed) [S-85]. New kingdoms keep using old tools.

### Tools needed per kingdom

Counts from eog's map data (tier C) [S-85]; the Verdantglade row matches the marker counts of [S-50].

| Kingdom | Gateway Key | Withering Potion | Magic Drill | Water Mine | Season item |
|---|---|---|---|---|---|
| Verdantglade | 3 | 5 | 3 | - | - |
| Cinder Ridge | 4 | 3 | 5 | 3 | - |
| Aqualis | 5 | 2 | 3 | 6 | - |
| Loong Haven | 5 | 1 | 1 | 2 | Cloud Jade 7 |

- Where each is used in Verdantglade [S-85]: Gateway Keys at Rabbit Vault, Gorge Depths, Owl Vault; Withering
  Potions at Jungle Vault, Monolith Ruins V, Stagnant Jungle, Sunken Forest, Sunrise Isle; Magic Drills at Vine
  Peninsula, Hidden Camp, Hideout. Hidden Camp agrees with our own boulder there [R-151].
- Later kingdoms add their own items ❓ (Chinese-server data, eog's names): Purifying Hammer (Aethyris), Brick
  Switch (Harpadia), Flame Hammer and Frost Hammer (Ignis) [S-85].
- Spots for the other kingdoms: [eog notes](../sources/notes/eog.md); every marker with coordinates:
  [map-points.json](../data/map-points.json).
- Exploration items are sold in the Kingdom Shops [S-87].

## Things found while exploring

| Object | What it gives | Rule / source |
|---|---|---|
| Goddess Statue, Lost Goddess Statue | Blessing Level, bed EXP, Cart yields | [Goddess Statues](goddess-statues.md), [R-070] |
| Hero Statue, Witch Statue (cards read "Statue of <name>"; the publisher calls them Statue of the Brave and Statue of Witch) | Press Visit: a permanent stat boost (e.g. HP +170) and a full heal; the card shows daily visit attempts [R-144]. The publisher adds that each can be used once a day and may give a Stellatie or stamina ("a lightning bolt") [S-87][S-40]. Blight Witch lore statues instead give a one-battle curse [R-174]; "a daily buff or curse" is the tier D wording [S-04] | [R-144][R-174][S-87]; 4 and 2 in Verdantglade [S-50] |
| Chests | Kingdom currency, Rolla, Stellatie, ore, gear | [R-076] |
| Lucky Wheel ("Wheel of Destiny", "Lucky Roulette") | One free spin per wheel while its zone is unexplored; later spins cost Lucky Tickets | [R-147]; 2 in Verdantglade [S-50] |
| Ore nodes (Gold Ore, Steel Ore, Sandstone) and material pickups | Rolla, Raw Ore, Chrono Sand, Battle Essence for 5 stamina a pickup | [R-076][R-106] |
| Mini-dungeons: Temple Ruins, mines, caves, Ancient Keep | First-clear rewards | [R-040][R-071]; 19 in Verdantglade [S-50] |
| Cooking ingredients, and from Season 2 gems, lying in the open world | Dishes; gems | [S-02] |
| Lore objects, stone tablets | Small rewards, lore | [R-173][R-174] |
| Collectibles and monsters | Our bot saves a reference of each new one | [R-131] |

## Priorities

1. Follow the main Explore quest until a wall (power, rank, tool), then clear every reachable side zone and light
   its statue [R-135][S-01].
2. Whenever a kingdom tool is affordable, buy it and use it on the spot with the most statues behind it. In
   Verdantglade the first Magic Drill goes to the Mushroom Woods / Mushroom Cluster area: two Lost Goddess Statues
   behind one drill [S-01].
3. Choose commission rewards for the kingdom currency you are short of for the next tool (the example given is
   3K Abundance Leaves for a key or potion) [S-01].
4. Hold the free daily bed speed-up and Temporal Crystals until the day's new statues are lit [S-02][S-03][R-035].
5. Wheel of Destiny prizes worth taking for exploration: Gateway Keys are second priority, after Skill Shard
   Vouchers [S-01].

## Open questions

- ❓ What a Sealing Pillar, Challenge Stele and Trait Stele ask for. Confirm from the first card of each.
- ❓ Which obstacle the Water Mine and the Gateway Key remove, by in-game name.
- ❓ Whether the daily Stellatie or stamina from a Hero / Witch statue [S-87] comes on top of the permanent stat of the first Visit [R-144]: watch a second-day visit.
- ❓ Exact weight of fog, pickups and fights in the exploration %.

## Sources

- [S-01] section 2 (exploration, kingdom tools, bonus tip with map screenshot), section 7 (Wheel of Destiny)
- [S-02] sections I, VI (speed-ups, gems in the open world)
- [S-03] Goddess Statues, Progression
- [S-04] beginner, day-1 and starter guides (leads only)
- [S-50] Verdantglade marker counts and tool totals; [S-53] area unlock stockpile
- [S-85] eog map data: tools per kingdom, tool spots, Cloud Jade ([map-points.json](../data/map-points.json)); [S-87], [S-40] official posts (daily statues, Kingdom Shops)
- Rules listed inline; `resource/world/zones.json` for our observed zones, power and links
