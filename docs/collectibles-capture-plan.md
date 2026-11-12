# World collectibles: training-data capture plan (2026-11-11)

<!-- index: Training data for world collectibles: what they are, class options, burst capture of approach sequences, session plan, pre-roll buffer -->

mae (2026-11-11): the detector needs a lot of training data for map items, and it should include collectible items
in the world, with reference images leading up to collection, so the Roboflow model can spot them. This is the plan.
It needs emulator time, so nothing here runs until mae approves a time; the builder thread runs it. No Roboflow
upload until mae says go.

## What counts as a world collectible

From the rules (R-002, R-066, R-106, R-108, R-109, R-122, R-124, R-131) and the reference screens:

| Collectible | Where it shows | Cost | Reference now |
|---|---|---|---|
| Ground pickup (green minimap / area-map dot) | Island map, every zone | free while exploring, 5 stamina in blessed zones | none on the island map; dots only |
| Ore rock (grey rock, blue crystals, "⚡5") | Verdantglade II mine, other zones | 5 stamina | `world/explore_ore_rocks*.png`, `world/explore_ore_mined.png` |
| Sand, Battle Essence, Rolla nodes | Resource Hunt targets | 5 stamina | none |
| Bellflower (and other Flower Harvest plants) | Verdantglade Flower Harvest | free picks | `world/explore_bellflower_*.png`, `world/item_bellflower.png` |
| Blue-aura rare pickup (R-122) | any zone | as above | none |
| Green-timer special node (R-109) | gather fields | as above | none |
| Chest (walk onto it) | zones, puzzle rewards | free | `world/world_map_tile_puzzle_chests.png`, `icons/area_map_chest.png` |
| Boar with "⚡5" | ore field | 5 stamina, gives ❓ | `world/explore_stamina_boar.png` |

Never touched for this: Golden Beetles, anything with a spend button (policy.md never-do list).

## Classes: a proposal for mae

`resource/detect/classes.json` has no class for a collectible on the island map (only `monster`, `npc_alert`,
`player_character`, `tracker_box` in group world, and `badge_gold_ring` for the tracking ring). Two options, both
append-only:

1. **One class, catalogue field (recommended).** Append `world_collectible` (group world, kind region). A box
   carries `collectible`, an id from a new `resource/world/collectibles.json` (id, name, look, cost, where seen),
   the same way `item_icon` carries `item`. The export can then train one class per collectible, per group (ore,
   plant, pickup, chest), or one class for all, as `--items` does today. New kinds never need a class change.
2. **One class per kind.** Append `world_ore_node`, `world_plant_node`, `world_pickup`, `world_chest`. Simpler to
   read, but every new kind is a new class.

Nothing is appended until mae picks.

## How a sequence is captured

New command (this PR): `python -m sxs capture NAME --burst N --every S` saves N frames S seconds apart into
`captures/sequences/NAME/01.png ...` with `frames.json` (time of each). The folder is gitignored; frames move into
`docs/screens/` only after picking.

One sequence per collectible met:

1. Before walking: one area-map frame with the target's dot (map classes get data too), then close the map.
2. Start the burst (`--burst 16 --every 0.5`, 8 s) when the collectible first shows on screen or at the minimap edge.
3. Walk to it with the normal tap (the loop's own walk), let it collect, keep the burst running through the reward
   popup.
4. Name: `seq_<kind>_<zone>_<n>`, e.g. `seq_ore_verdantglade_ii_1`.

Pick about 5 frames per sequence: far (first sight), middle, near, the tap or collect moment, and the reward. Keep
every frame of one sequence in the same train/valid/test split (near-duplicates in two splits inflate the scores);
to build before the first export with sequences: `sxs/detect/dataset.py` hashes the sequence name, not the file
name, for `seq_` screens (today it hashes each file, and `balanced_splits` moves single screens).

## Session plan (needs mae's approved time, about 40 minutes)

| Step | What | Sequences | Stamina |
|---|---|---|---|
| 1 | Island map frames of the current zone (Verdantglade XI, being explored): minimap and area map at each stop | area-map and minimap frames, about 15 | 0 |
| 2 | Green-dot pickups while exploring an unexplored zone (free there) | 10 | 0 |
| 3 | Flower Harvest bellflowers (free picks) | 4 | 0 |
| 4 | Resource Hunt ore (Verdantglade II mine), above the 70 keep line only (R-107) | 4 | 20 |
| 5 | Any chest, blue-aura or green-timer node met on the way | as met | 0 |

That is about 20 sequences, about 100 picked frames, and at least 3 sequences per kind across 2 zones. The target for
a first training is 50 boxes on 20 screens per class, so ore, plant and pickup each need about 2 sessions; later
sessions add other zones and lighting (shadow, and blessed zones, whose colours brighten).

Live-run rules: the readout rule (post command, goal, target and stop condition before, readouts about every 2
minutes, a [Result] at the end), never spend Dawnium, never tap Golden Beetles, keep 70 stamina.

## Making it automatic (the system, not a person)

Hand-run bursts are only the first batch. The loops already take a frame every step, so the lasting fix is a
pre-roll buffer: the fog walk and the gather collector keep their last 12 frames, and when a pickup or reward popup
appears they save the buffer as a `seq_` sequence (R-131 already asks for a reference of every collectible met).
Every exploration run then adds training data with no extra emulator time. Build offline next; live test at an
approved time.

## Labeling sequences

The pre-labeller cannot draft collectibles yet (no detector for them). Plan: mae boxes the collectible on the
nearest frame of a sequence; a sequence drafter (`prelabel --sequence NAME`, to build) follows the box backwards
frame by frame by template matching in a small window (scale 0.9 to 1.1) and drafts it on the earlier frames; mae
checks them in the review grid (one category, keep or reject). Ore rocks get a head start from the existing "⚡5"
template (`resource/image/explore/stamina_cost_5.png`) and the tracking ring finder.

## What mae decides

1. Option 1 or 2 for the classes.
2. A time for the 40-minute capture session (the builder thread runs it; the coordinator asks).
3. Whether to build the pre-roll buffer next.
