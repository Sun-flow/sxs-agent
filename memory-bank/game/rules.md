# Game rules

> **Last updated**: 2026-11-03
> One entry per rule of the world that an agent acting in the game needs. Format and confidence levels: `memory-bank/game/README.md`. IDs are permanent; add new ones at the end of their topic with the next free number (next free: R-021).

Entry format:

```
### R-NNN · short title
- **Rule**: one or two sentences, stated so a script could act on it.
- **Confidence**: observed | told | reported. **Source**: who or what, and date.
- **Images**: repo paths, or "none yet".
- **Related**: other rule IDs or nav-graph node ids.
```

## Combat

### R-001 · All battles are automatic
- **Rule**: Every battle, PvE and PvP, plays itself. The bot never controls combat; it only starts battles and handles the screens before and after.
- **Confidence**: observed (won the first tutorial battle with no input, 2026-11-03). **Source**: step 1 doc section 3; builder thread.
- **Images**: none yet.
- **Related**: nodes `battle`, `battle_result`.

## Exploration and the world map

### R-002 · Exploring an area means clearing green dots and mist
- **Rule**: An area is fully explored when every green dot on the minimap has been cleared, by walking to it and interacting with the thing it marks, and all the mist (fog of war) on that area's map is revealed.
- **Confidence**: told. **Source**: mae, 2026-11-03.
- **Images**: none yet (want: minimap with green dots; area with mist).
- **Related**: R-003, R-004, R-006.

### R-003 · A fully explored area unlocks a blessing statue
- **Rule**: Once R-002 is met for an area, a statue unlocks in it; interact with the statue to "bless" the area.
- **Confidence**: told. **Source**: mae, 2026-11-03.
- **Images**: none yet.
- **Related**: R-002, R-014.

### R-004 · Use the minimap for relative positions
- **Rule**: The minimap shows where items, interactables and enemies are relative to the character. Use it to choose which way to move to reach the next item or enemy.
- **Confidence**: told. **Source**: mae, 2026-11-03.
- **Images**: none yet (want: minimap crop with its icon types labelled).
- **Related**: R-002, node `world_map`.

### R-005 · Areas show an exploration percentage
- **Rule**: Each area tracks exploration as a percentage (Originisle was at 62% after the first part of the tutorial). 100% presumably means R-002 is met ❓.
- **Confidence**: observed (the percentage); the link to R-002 is a guess. **Source**: builder thread, 2026-11-03.
- **Images**: none yet.
- **Related**: R-002.

### R-006 · The world has named regions
- **Rule**: Known regions: Originisle (starting area), Verdantglade, Cinder Ridge, Aqualis, Loong Haven.
- **Confidence**: observed for Originisle; reported for the rest. **Source**: builder thread; step 1 doc section 3.
- **Images**: none yet.
- **Related**: node `world_map`.

## Quests

### R-007 · Follow the quest guide to finish the tutorial
- **Rule**: The tutorial is driven by the quest guide; doing each quest it shows in order completes the tutorial.
- **Confidence**: told. **Source**: mae, 2026-11-03.
- **Images**: none yet.
- **Related**: R-008, R-009, node `quests`.

### R-008 · "Explore" quests need every item in the area
- **Rule**: A quest that says "Explore" an area is done by going to the overworld map and collecting all the items in that area, which means clearing its green dots and interacting with every interactable (R-002).
- **Confidence**: told. **Source**: mae, 2026-11-03.
- **Images**: none yet.
- **Related**: R-002, R-009.

### R-009 · Track a quest to get map markers
- **Rule**: A quest can be tracked. While tracked, the map squares that matter to it carry a quest marker symbol; tap those squares to progress the quest.
- **Confidence**: told. **Source**: mae, 2026-11-03.
- **Images**: none yet (want: the track button and the quest marker icon).
- **Related**: R-007, nodes `quests`, `world_map`.

## Unlocks and progression

### R-010 · Menus unlock with tutorial progress
- **Rule**: Some menus are locked until the tutorial reaches a certain point. The game makes it clear when one becomes usable, so the bot should treat a locked menu as "not yet", not as an error.
- **Confidence**: told. **Source**: mae, 2026-11-03.
- **Images**: none yet (want: a locked menu button and the unlock announcement).
- **Related**: `unlock` field of each node in `nav-graph.json`.

### R-011 · Some features unlock by account level
- **Rule**: Guilds unlock at account level 15, the Vendor Booth at 18, Fantomons at 51.
- **Confidence**: reported. **Source**: step 1 doc sections 4 and 5.
- **Images**: none.
- **Related**: R-010, nodes `guild`, `vendor`.

### R-012 · Seasons partly reset levels
- **Rule**: Seasons (the first about a month, later two to three months) partly reset levels, so level-based unlocks (R-011) must be re-checked each season.
- **Confidence**: reported. **Source**: step 1 doc section 3.
- **Images**: none.
- **Related**: R-011.

### R-013 · Servers cap at 5,000 players and merge
- **Rule**: A server holds up to 5,000 players and later merges with others; guilds are per server.
- **Confidence**: reported. **Source**: step 1 doc section 3.
- **Images**: none.

## Daily content

### R-014 · Statues give one interaction a day
- **Rule**: Goddess, Witch and Hero statues on the map can each be interacted with once a day.
- **Confidence**: reported. **Source**: step 1 doc section 4. Unclear whether these are the same as the blessing statues of R-003 ❓.
- **Images**: none yet.
- **Related**: R-003.

### R-015 · Material dungeons have two free attempts each
- **Rule**: Each material dungeon has 2 free attempts a day; more attempts cost Dawnium.
- **Confidence**: reported. **Source**: step 1 doc section 4.
- **Images**: none yet.
- **Related**: R-018, node `dungeons`.

### R-016 · Guild donations: three basic a day
- **Rule**: A guild member can make 3 basic donations a day; the Guild Farm can be planted and harvested once a day.
- **Confidence**: reported. **Source**: step 1 doc section 4.
- **Images**: none yet.
- **Related**: R-011, node `guild`.

## Currencies and resources

### R-017 · Stamina caps at 300
- **Rule**: Stamina is spent on map nodes and caps at 300; stamina gained over the cap is wasted, so spend it before it fills. A free stamina pack is available daily in the Shop.
- **Confidence**: reported. **Source**: step 1 doc section 4.
- **Images**: none yet (want: stamina icon).
- **Related**: node `shop`.

### R-018 · Dawnium is the premium currency
- **Rule**: Dawnium buys extra dungeon attempts and items in the Shop's Vault. The bot should not spend it without a rule saying so.
- **Confidence**: reported. **Source**: step 1 doc section 4.
- **Images**: none yet (want: Dawnium icon).
- **Related**: R-015.

### R-019 · Rolla is the common currency
- **Rule**: Rolla pays for Daily Shop refreshes; early on it is the priority use of stamina.
- **Confidence**: reported. **Source**: step 1 doc section 4.
- **Images**: none yet (want: Rolla icon).
- **Related**: R-017.

### R-020 · The Cart collects AFK rewards
- **Rule**: The Cart accumulates rewards while offline, up to a cap; collect it at least once per cap period.
- **Confidence**: reported. **Source**: step 1 doc sections 3 and 4.
- **Images**: none yet.
- **Related**: node `home`.
