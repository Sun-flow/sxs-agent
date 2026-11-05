# Overworld rules

Read when on the island map: exploring, reading the minimap or area map, travelling, fog, statues, gates, puzzles, or a target you can't reach.

## Exploring an area

### R-002 · Full exploration = every green dot cleared and all mist revealed
Walk to each green minimap dot and interact with what it marks, beat roaming monsters, and walk into all the area's fog. "Explore <area>" quests are done this way. Full exploration unlocks the area's statue (R-070). Exploring also pays Dawnium and Rolla.
*told, observed* · R-021, R-066, R-070

### R-065 · When stuck or between quests, walk the fog edge
Exploration comes in two kinds (mae), and loops should handle both: **quest-progression** (follow the tracker's Explore and unlock quests, R-044) and **fog-walking** (clear side areas that aren't tied to progression but are within our CP range, e.g. Damp Woods). Side areas have no quest but give resources and levels; walking into the fog edge reveals new areas. **Explore outward from the connected area the character is in; never jump back across the map** (mae). Code: `python -m sxs roam` (`--area`, `--minutes`, `--max-areas`). It picks an unexplored area with recommended power up to 1.25x ours (R-127, R-084), enters from a connected explored neighbour (R-067), explores it with the Fog Walk (`sxs/loops/fogwalk.py`; stays in its current area when that borders the target) and blesses the statue (R-070). It takes 5-stamina pickups only while stamina stays ≥70 (R-107).
*told, observed* · R-044, R-066, R-067, R-070, R-084, R-127, R-130

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
The minimap shows items, interactables and enemies around the character; use it to choose a direction. Tile coordinates show as "(x, y)" under it ("Originisle I (24,23)"), read by OCR. x grows east (screen right), y shrinks south (screen down), as `sxs/actions/goto.py` uses them.
*told, observed* · node `world_map` · R-066, R-068

### R-066 · Minimap legend: it shows the true tiles
Code: `sxs/vision/minimap.py`. About 8 px per tile; player at the centre (0.856, 0.138); usable radius about 86 px. Tiles (OpenCV HSV):
- **green dots**: pickups/POIs. Under shadow they look pale (about 39/81/213). Highland Woods dots are paler (S about 128 vs 150+).
- **light green**: explored walkable, S<95, V>=115.
- **Stripes mean unexplored** (mae); the colour under them still shows the terrain as fog clears.
- **light green, shaded about 0.55x, striped** (about 42/79/81): unexplored walkable. If connected to explored ground, it's an exploration target (R-065).
- **dark green**: wall. Explored: unlined (about 54/117/109, S>=95, V>=85). Unexplored: very dark, striped (about 54/130/58, V<85).
- Explored walkable light green is about 41/72/148. Once an area is blessed (100% plus statue, R-070) its colours brighten.
- **cross-hatch, no colour**: unspotted (grey, S<35, V about 35); resolves when the player gets close.
- **gold buildings**: interactables; the biggest are dungeons (daily challenges after the first clear), smaller ones mini-dungeons such as mines (R-071).
- **orange** (about 18/116/187): monsters, and gold buildings under shadow. Fight monsters (mae), within the HP rules (R-061, R-078).
Other types aren't catalogued ❓. Highland Woods (9.6K): entered past a bracketed wolf-boss pack (R-041, beaten at 10K); its ground pickups by a cooking pot alone finish it.
*told, observed* · `minimap/minimap_verdantglade2.png`, `minimap/minimap_classified.png`, `minimap/tile_walk_explored.png`, `minimap/tile_walk_unexplored.png`, `minimap/tile_wall_explored.png`, `minimap/tile_wall_unexplored.png`, `minimap/tile_unspotted.png`, `minimap/minimap_highland_items.png`, `minimap/legend_boundary_mae.png`, `minimap/legend_fog_edge_mae.png`, `minimap/legend_walk_explored.png`, `minimap/legend_walk_unexplored_striped.png`, `minimap/legend_wall_explored.png`, `minimap/legend_wall_unexplored_striped.png` · R-004, R-065, R-070, R-071, R-130

### R-130 · Fog-walk and pathfind toward the light-green to striped-green edge
When fog-walking (R-065) or finding a way to an out-of-the-way spot, look on the minimap for where explored light green meets striped dark green (unexplored walkable). That edge is where to walk: it is open ground into the fog. Unlined darker green and very dark striped green are walls or impassable terrain; don't path into them (mae). Colours and crops: R-066.
*told* · `minimap/legend_boundary_mae.png`, `minimap/legend_fog_edge_mae.png` · R-065, R-066, R-067

## Getting somewhere

### R-067 · Areas join by land bridges: head for the connection, not the straight line
Connections can be far off the straight line (Verdantglade II to Moonveil Woods is a land bridge at the minimap's bottom). Straight walks hit walls and water: path-find over walkable minimap tiles (R-066) to the connection, or travel via the area map (R-068), whose taps auto-path.
*told* · R-066, R-068

### R-068 · Travel far or into unexplored ground through the area map
1. Tap the minimap to open the area map (the white box is the camera viewport).
2. Tap the destination; the camera centres there.
3. Close the map and tap the ground: the player auto-paths, around walls and through land bridges and unseen gaps.
Zoom differs each opening: pick places by OCR'd label, never fixed positions. Match labels exactly, trailing numerals included ("Verdantglade III" is not "Verdantglade I"). A label in fog can't be reached this way (`no_move`): travel from home (R-089). Code: `python -m sxs goto "Area Name"` or `python -m sxs goto X Y`.
*told, observed* · `world/world_area_map.png`, `world/world_map_moonveil_entry.png`, `world/world_area_map_stone_ruins.png` · node `area_map` · R-067, R-076, R-089

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
- Match both with `^(Lost )?Goddess Statue$`.
- **Already blessed**: "A starlit statue silently guards this Blessed Land", Regional Relics, no button. Dismiss and walk around it (kind `blessed_statue`).
- Goddess, Witch and Hero statues can each be used once a day; whether these are the blessing statues is unknown ❓.
*observed, reported* · `world/interact_goddess_statue.png`, `world/interact_goddess_statue_blessed.png`, `world/blessing_level.png`, `world/lost_goddess_statue.png` · R-002, R-074

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
