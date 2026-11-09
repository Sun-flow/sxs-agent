# Overworld rules

Read when on the island map: exploring, reading the minimap or area map, travelling, fog, statues, gates, puzzles, or a target you can't reach.

## Exploring an area

### R-002 · Full exploration = every green dot cleared and all mist revealed
Walk to each green minimap dot and interact with what it marks, beat roaming monsters, and walk into all the area's fog. "Explore <area>" quests are done this way. Full exploration unlocks the area's statue (R-070). Exploring also pays Dawnium and Rolla.
*told, observed* · R-021, R-066, R-070, R-131

### R-131 · Save a reference of every collectible and monster met while exploring
- Each time exploration collects an interactable or fights a monster, save a reference crop of it, tagged "exploration collectibles" (mae). Explore then watches for things it recognises it needs to collect or fight.
- Store: `resource/image/explore/collectibles/`, one crop per object plus a row in a manifest.json there (name, kind: collectible / interactable / monster, area, date, stamina cost if any). Builder designs the code ❓.
- Use the crops in unexplored areas to spot monsters and interactables that must be fought or collected (free there). In explored, blessed areas the same things cost stamina: a crop match there must not trigger a tap unless a loop is deliberately farming (R-065).
*told* · R-002, R-065, R-066, R-107

### R-132 · Dotted lines mark zone borders: finish the zone you're in first
- A dotted line is the border between two zones such as Verdantglade III and IV (mae). On the minimap it shows as light dashes. In the world it shows as dark dashes, usually labelled with the zone name: "Troll Lair" with its power "17K" in a horizontal label at a corner of a line, or "Zephyr Vale" written sideways along a vertical line with no power shown.
- Use it to tell which zone the character is in, and finish that zone to 100% (R-065) before crossing into the next. Seen: the fog walk crossed into Verdantglade IV with III at about 91%.
- A zone across the line still needs the 1.25x power check (R-127).
- Code: `border_mask` / `border_tiles` in `sxs/vision/minimap.py` find the minimap line: light grey, 1–2 px wide, S < 40, V 105–200, straight runs of 12+ px with green on both sides (measured on `world/explore_bellflower_picked.png`). The fog walk treats border tiles as walls unless roam is walking into the target zone.
- Auroradrasil is its own zone, not part of Verdantglade V (mae), even though it sits inside V on the map; it has its own Lost Goddess Statue (R-070). Travelling to finish a zone must land on that zone's own ground, not on a neighbour inside it.
*told, observed* · `world/zone_boundary_troll_lair_mae.png`, `world/zone_boundary_zephyr_vale_mae.png`, `minimap/legend_zone_boundary_mae.png` · R-065, R-066, R-127, R-130

### R-065 · When stuck or between quests, walk the fog edge
Exploration comes in two kinds (mae), and loops should handle both: **quest-progression** (follow the tracker's Explore and unlock quests, R-044) and **fog-walking** (clear side areas that aren't tied to progression but are within our CP range, e.g. Damp Woods). Side areas have no quest but give resources and levels; walking into the fog edge reveals new areas. **Explore outward from the connected area the character is in; never jump back across the map** (mae). Code: `python -m sxs roam` (`--area`, `--minutes`, `--max-areas`). It picks an unexplored area with recommended power up to 1.25x ours (R-127, R-084), enters from a connected explored neighbour (R-067), explores it with the Fog Walk (`sxs/loops/fogwalk.py`; stays in its current area when that borders the target) and blesses the statue (R-070). **Fog-walk goal** (mae): at all times aim for 100% exploration of the unexplored area: collect every green dot, fight or interact with every orange dot, complete every yellow structure or mini-dungeon (R-071). Only then does the Goddess Statue or Lost Goddess Statue become available to bless the area (R-070). Exploring itself never spends stamina (mae). In unexplored areas, monsters and interactables are free: fight and collect them. In explored, blessed areas, monsters respawn and they and most interactables cost stamina: skip them unless a loop is deliberately farming (battle essence for skills, gathering, R-107).
*told, observed* · R-044, R-066, R-067, R-070, R-071, R-084, R-127, R-130, R-131

### R-135 · Non-quest exploration order: lowest-CP unblessed zone first
The non-quest exploration loop (mae; the quest-progression loop is settled):
1. Pick the lowest-CP zone not yet blessed (within the fight limit, R-127).
2. Explore it until its statue is blessed (R-065 goal, R-070).
3. Repeat until no unblessed zone remains.
4. Then look for any fog-walk ground not yet explored (R-130). Explore it if there is some; otherwise exploration is concluded for now.
Next by this order (2026-11-05): Jungle Camp (12.6K); walking in from Drasilgard's south edge gained no %, so its entry point is unknown ❓.
Code: `python -m sxs roam` picks the zone with `Tree.next_zone` from the location tree (`resource/world/zones.json`, `sxs/policy/zones.py`, `python -m sxs zones`; zones with no power line read go last). The tree holds each zone's kingdom, CP, %, blessed, map point and way in, and records Jungle Camp's missing entry as an open question. Roam blesses a statue when its area-map "!" lights (R-070), and ends with `exploration_concluded`.
*told* · R-065, R-070, R-076, R-127, R-130, R-132

## Walking and the camera

### R-025 · Tap to walk, swipe to pan; the camera doesn't follow
Tap a spot to walk; swipe to pan. A tap inside fog doesn't move the character: tap tiles at its edge. The camera stays put after walking, so re-centre (drag the map or tap an edge pointer, R-074) before the next tap.
*observed* · `world/world_map.png` · R-067, R-074

### R-074 · Edge pointers: tap one to pan the camera to its target
Templates in `resource/image/explore/`:
- gold quest ring (R-022): `resource/image/explore/marker.png`, `resource/image/explore/marker_dim.png`;
- boss: white ring, boss portrait, speech-bubble tail: `resource/image/explore/marker_boss.png`;
- Goddess Statue (R-070): `resource/image/explore/pointer_statue.png`;
- "Unlock <area>": blue orb, `resource/image/explore/pointer_unlock.png`;
- the player's own face in a white ring, when the camera drifted off them: `resource/image/explore/player_pointer.png`; tapping it re-centres on the player. Ignore the match on the top-left HUD avatar.
*observed* · `world/world_map_player_pointer.png` · R-022, R-025

## Reading the minimap

### R-004 · Minimap and coordinates give relative positions
The minimap shows items, interactables and enemies around the character; use it to choose a direction. Tile coordinates show as "(x, y)" under it ("Originisle I (24,23)"), read by OCR. x grows east (screen right), y shrinks south (screen down), as `sxs/actions/goto.py` uses them. OCR sometimes reads the comma as a period ("(134.93)"); accept both.
*told, observed* · node `world_map` · R-066, R-068

### R-066 · Minimap legend: it shows the true tiles
Code: `sxs/vision/minimap.py`. About 8 px per tile; player at the centre (0.856, 0.138); usable radius about 86 px. Tiles (OpenCV HSV):
- **green dots**: collectibles. Walk to them and interact for now; they'll be auto-collected once Fantomon unlock (mae). Under shadow they look pale (about 39/81/213). Highland Woods dots are paler (S about 128 vs 150+).
- **light green**: explored walkable, S<95, V>=115.
- **Stripes mean unexplored** (mae); the colour under them still shows the terrain as fog clears.
- **light green, shaded about 0.55x, striped** (about 42/79/81): unexplored walkable. If connected to explored ground, it's an exploration target (R-065).
- **dark green**: wall. Explored: unlined (about 54/117/109, S>=95, V>=85). Unexplored: very dark, striped (about 54/130/58, V<85).
- Explored walkable light green is about 41/72/148. Once an area is blessed (100% plus statue, R-070) its colours brighten.
- **black / cross-hatch, no colour**: fog the player hasn't come near (grey, S<35, V about 35). Coming close reveals the terrain under it and the dots around it.
- **gold buildings**: interactables; the biggest are dungeons (daily challenges after the first clear), smaller ones mini-dungeons such as mines (R-071).
- **orange** (about 18/116/187): monsters or interactables (also gold buildings under shadow). They must be dealt with to explore the area: fight monsters, interact with the rest (mae), within the HP rules (R-061, R-078).
Other types aren't catalogued ❓. Highland Woods (9.6K): entered past a bracketed wolf-boss pack (R-041, beaten at 10K); its ground pickups by a cooking pot alone finish it.
*told, observed* · `minimap/minimap_verdantglade2.png`, `minimap/minimap_classified.png`, `minimap/tile_walk_explored.png`, `minimap/tile_walk_unexplored.png`, `minimap/tile_wall_explored.png`, `minimap/tile_wall_unexplored.png`, `minimap/tile_unspotted.png`, `minimap/minimap_highland_items.png`, `minimap/legend_boundary_mae.png`, `minimap/legend_fog_edge_mae.png`, `minimap/legend_walk_explored.png`, `minimap/legend_walk_unexplored_striped.png`, `minimap/legend_wall_explored.png`, `minimap/legend_wall_unexplored_striped.png`, `minimap/legend_dots_fog_mae.png` · R-004, R-065, R-070, R-071, R-130

### R-130 · Fog-walk and pathfind toward the light-green to striped-green edge
When fog-walking (R-065) or finding a way to an out-of-the-way spot, look on the minimap for where explored light green meets striped dark green (unexplored walkable). That edge is where to walk: it is open ground into the fog. Where passable (light green, explored or striped) terrain runs into black fog, follow it in: walking near the fog reveals the terrain and the dots around it. Exposing fog is the one case that needs player-oriented movement (locating the character, stepping toward the edge), because there is no visible endpoint to tap; everything else travels by endpoint (R-068). Unlined darker green and very dark striped green are walls or impassable terrain; don't path into them (mae). Colours and crops: R-066.
*told* · `minimap/legend_boundary_mae.png`, `minimap/legend_fog_edge_mae.png`, `minimap/legend_dots_fog_mae.png` · R-065, R-066, R-067

## Getting somewhere

### R-067 · Areas join by land bridges: head for the connection, not the straight line
Connections can be far off the straight line (Verdantglade II to Moonveil Woods is a land bridge at the minimap's bottom). Straight walks hit walls and water: path-find over walkable minimap tiles (R-066) to the connection, or travel via the area map (R-068), whose taps auto-path.
*told* · R-066, R-068

### R-068 · Travel far or into unexplored ground through the area map
1. Tap the minimap to open the area map (the white box is the camera viewport).
2. Tap the destination; the camera centres there.
3. Close the map and tap the ground: the player auto-paths, around walls and through land bridges and unseen gaps.
The same route reaches any target, not just areas (mae): find it on the area map (a dot, a structure), tap it there to centre the camera on it, close the map, then tap the now-visible element on screen to walk to it. No player-relative pathfinding is needed: the character auto-paths to any tapped spot even when it is off screen, so the bot finds endpoints and never manages the route (mae). The camera only has to see the thing to tap it. With several targets in view, tap each on screen in turn without reopening the map; reopen it only when nothing targetable is left in view (mae).
Zoom differs each opening: pick places by OCR'd label, never fixed positions. Match labels exactly, trailing numerals included ("Verdantglade III" is not "Verdantglade I"; a V/VI mix-up once landed the bot in Auroradrasil). At full zoom-out OCR merges neighbouring labels ("Wildbloom Coahlidden Camp", "14.8K Monolith Ruins") and drops percentages: zoom out one step at most when reading zones. A label in fog can't be reached this way (`no_move`): travel from home (R-089). Code: `python -m sxs goto "Area Name"` or `python -m sxs goto X Y`.
*told, observed* · `world/world_area_map.png`, `world/world_map_moonveil_entry.png`, `world/world_area_map_stone_ruins.png` · node `area_map` · R-065, R-067, R-076, R-089, R-130

### R-089 · Travel from home through the quest tracker
At home, tapping the tracker for a quest elsewhere asks "Travel to <Area> now?"; OK is free. Use it for areas whose area-map label is in fog.
*observed* · `dialogs/confirm_dialog.png` · node `confirm_dialog` · R-044, R-068

### R-069 · The Voyage Obelisk travels to the next kingdom
"Your pathway to the next kingdom." Tap the obelisk once to select it, again to open its card, then Activate (Originisle to Verdantglade).
*observed* · `world/interact_obelisk.png` · R-030

## Reading the area map

### R-076 · The area map shows resources, progress and power gates
- Legend: Portal, Lost Statue, Gold Ore, Steel Ore, Sandstone. Ore nodes cost 5 stamina each.
- Unfinished areas show "Exploration: N%" and any power gate ("12K") under the label; finished ones show only the name. Gates seen: Highland Woods 9.6K, Verdantglade III 12K. Skip areas gated above your power (R-084).
- Lost Statue icon: `resource/image/areamap/lost_statue.png` at 0.8.
- Edge labels are clipped on the left ("tglade III"); `sxs/loops/roam.py` accepts a 6+ letter suffix with matching numerals.
- Survey (code: `sxs/loops/roam.py`): zoom out fully, then tap "+" at (682, 795) once (at full zoom-out OCR merges labels and drops %), and read a 3×3 grid of slow 300 px pans, merging readings by name. The "+" position and pan size come from one reference screen ❓ (not yet watched live).
- A 100% area with a red "!" probably has its statue waiting ❓. Sunrise Isle is at the bottom right of the Verdantglade map; its % isn't read ❓.
*observed* · `world/world_area_map.png`, `world/area_map_lv22.png` · node `area_map` · R-068, R-070, R-084, R-086

## Power walls and gates

### R-084 · A recommended power far above yours is a wall: stop exploring there
Where recommended power is well above yours and fights end in losses (R-031), stop exploring; don't retry. Verdantglade cap (mae): clear only the first 4 to 7 Verdantglade areas, or stop at a natural wall; `sxs/loops/roam.py` stops at the first power wall and caps areas with `--max-areas`. Get stronger first: gear, charms, techniques, tower clears. Verdantglade III (12K) lost every fight at 8.1K and 10K. Enter it with the quest's Go travel (R-089): that took it from 0 to 73/100. On foot from Moonveil Woods the fog edge south of about (168, 94) never moves. OCR mixes II and III on the area map, so check the trailing numeral (R-068).
*observed* · R-031, R-061, R-076, R-086

### R-086 · Gate of Power: a wall until power meets it, then press Open
A stone pillar card "Gate of Power": "Requires: Power reaches 15.5K (Current: 8.1K)". Short of power there's no button: dismiss (policy kind `power_gate`); the fog walk stops there. With enough power a free "Open" shows at about (0.5, 0.74): press it (kind `power_gate_open`) and the pillar sinks.
- Damp Woods: an area-map walk to its label from Verdantglade II lands at about (184, 86), a fogged pocket with a stone mini-dungeon, ore baskets, a statue and the 15.5K gate. Behind it: ore baskets, a glowing crystal and a duck-shaped item, free to tap; they finish Damp Woods. The minimap barely shows them under shadow, so the bot can't find them from it yet ❓.
*observed* · `world/gate_of_power.png`, `world/gate_of_power_open.png` · R-065, R-070, R-084

## Map objects and statues

### R-030 · Map objects open a card with one action
Tapping a map object (e.g. a Portal) opens a card with one button at (0.5, 0.70), e.g. "Activate"; using it adds Explore progress. Press only safe verbs: Activate, Collect, Claim, Open, Interact, Bless, Pray, Gather, Harvest, Mine, Examine, Read. **This never covers the Prayer gacha's Pray (R-093) or any spend button (R-043).** Card choices: R-042.
*observed* · `world/interact_portal.png` · node `interact` · R-042, R-043

### R-070 · Goddess Statues bless a fully explored area
- **Goddess Statue**: needs "Reach 100% exploration in <area>"; Unlock gives Blessing Level +1 (level 2 raised Max Cart Level 1→2 and AFK EXP 50→500): bless every area. "The Goddess's Grace I/II" follows each Explore quest; reach it via the statue pointer (R-074).
- **Lost Goddess Statue** ("Activate this dim statue..."): same requirement; Unlock at (0.5, 0.81); gives +1% Home EXP and +1% of one home yield (Highland Woods Wood, Moonveil Woods Rolla, Damp Woods Stone), then Tap to Continue.
- Two sizes, both bless the area (mae): the large Goddess Statue gives greater rewards than the smaller Lost Goddess Statue. Non-progression side areas often hold a Lost Goddess Statue, usable once the zone is explored. A red "!" over a statue means it can be blessed now: go and unlock it. The "!" also shows on the area map (about 17 px, smaller than menu badges; a gold-ore icon can carry the same "!", told apart by its big yellow block, and that is not a statue): tap it there, close the map, tap the screen centre, and the statue's card opens (R-068). Auroradrasil's Lost Goddess Statue ("Reach 100% exploration in Auroradrasil") gave Home EXP Yield Boost +1% and Home Stone Yield Boost +1%, then "Divine Power Awakens Your Potential", Tap to Continue.
- Match both with `^(Lost )?Goddess Statue$`.
- **Already blessed**: "A starlit statue silently guards this Blessed Land", Regional Relics, no button. Dismiss and walk around it (kind `blessed_statue`).
- Goddess, Witch and Hero statues can each be used once a day; whether these are the blessing statues is unknown ❓.
*observed, reported* · `world/interact_goddess_statue.png`, `world/interact_goddess_statue_blessed.png`, `world/blessing_level.png`, `world/lost_goddess_statue.png`, `world/lost_goddess_statue_auroradrasil_mae.png`, `unlabeled/lost_goddess_statue_auroradrasil.png`, `unlabeled/lost_goddess_statue_blessed.png`, `unlabeled/area_map_statue_badge_auroradrasil.png` · R-002, R-065, R-074

### R-085 · Stone tile floor puzzle: step on every tile for chests
Stone Ruins I: a 2x2 floor of stone tiles; each lights cyan when stepped on. All 4 lit spawns two chests (about 60 Dawnium each, plus Rolla, ore, gear, Abundance Leaf). Each chest pops a gear-swap prompt (swap button bottom right) that closes with the reward popup.
*observed* · `world/world_map_tile_puzzle_chests.png`, `character/gear_swap_prompt.png` · node `gear_swap_prompt`

### R-072 · Energy Circuits puzzle: not automated
Ancient Fortress, "Energy Circuits": 3 slabs in a row; tap two to swap until all nodes link (swapping the end slabs solved the one seen). Reset is top right. The bot doesn't solve these yet.
*observed* · `world/puzzle_energy_circuits.png` · node `puzzle_energy_circuits`

## Target unreachable or quest not moving

### R-062 · Talk to red "!" NPCs first; they gate what's around them
An NPC with a red "!" overhead gives instructions, then disappears and unlocks the objects around it. If the tracker points at something unreachable, find a red "!" NPC nearby and tap it. Template `resource/image/explore/npc_alert.png`; skip the "!" over the player (R-080). Example: the loot row by the Chief at the Originisle V pillar sits on a ledge (taps only walk to the grass below) until you talk to the Chief.
*told, observed* · `world/world_map_loot_ledge.png` · R-064, R-080, R-082

### R-064 · If the marker leads nowhere, follow NPC instructions
Some quests rely on NPC dialogue, not the marker ("Unlock Moonveil Woods" pointed into fog). If tapping does nothing, open the area map (tap the minimap) and look for a "!" NPC (R-062). Log NPC dialogue text so missed directions can be read later.
*told* · R-062, R-082
