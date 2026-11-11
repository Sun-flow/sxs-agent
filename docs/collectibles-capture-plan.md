# World collectibles: training-data capture plan (2026-11-11)

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

## Classes: two tiers (mae, 2026-11-11 18:35)

mae wants one broad class for exploration ("is it collectible?") and the exact kind when farming ("where is the
ore?"), with stamina-costing objects told apart from free ones.

**Roboflow constraint.** An object-detection box has exactly one class; Roboflow has no nested classes, and its tags
are per image, not per box. But a dataset version can merge or drop classes when it is generated ("Modify Classes"),
and our own export already does the same (`--items each|group|one`). So two tiers are possible: **label the fine
kind once, train the fine classes, and let the bot (or a merged dataset version) roll them up.** "Any collectible" is
then just "any box whose class is in the collectible table": no second model, no extra labeling.

**Design (proposed, append-only):**

1. `resource/detect/classes.json`: append `world_collectible` (group world, kind region), and the statue objects
   (below). A box of class `world_collectible` carries `collectible`, an id from a new catalogue
   `resource/world/collectibles.json`, the way `item_icon` carries `item`.
2. `collectibles.json`, one entry per kind: `{id, name, family, cost, look, seen}`.
   - `family`: `ore`, `sand`, `essence`, `rolla`, `plant`, `pickup`, `chest`, `special`.
   - `cost`: `free` or `stamina`. The same art can be both (ore rocks are free in an unexplored zone, 5 stamina in
     a blessed one), so `cost` is set per box when it differs, from what the frame shows.
3. The stamina label. Stamina-costing objects show a "⚡5" label over them (`resource/image/explore/stamina_cost_5.png`,
   R-108). Append a class `stamina_cost` for that label. This is what tells "costs stamina" apart from "free" for every
   kind, including essence: an essence fight is a monster with a stamina label (to confirm on a blessed zone's
   monster), so the model does not need to learn every monster type as "essence". Essence = `monster` box +
   `stamina_cost` box above it; ore for stamina = `world_collectible/ore` + `stamina_cost` above it.
4. Export modes (`python -m sxs dataset --collectibles each|family|one`, built): `each` trains one class per kind
   (`wc_ore_rock`, ...), `family` one per family, `one` a single `world_collectible`. First training: `family`, since
   each class needs about 50 boxes on 20 screens and families get there first; switch to `each` once kinds have the
   data.
5. Runtime: exploration asks for any box in the collectible table (any family, any cost) and skips those with a
   `stamina_cost` box over them in blessed zones (R-065); the stamina loop asks for family `ore` (or `sand`,
   `rolla`, essence monsters) *with* a `stamina_cost` box.

**Statues (mae: very important).** Coverage today: 0 boxes on any statue. Only 2 `map_statue_bang` boxes (the blue
"!" badge on the area map), 0 `card_goddess_statue`, and no class for the statue itself on the island map. Reference
screens that show one: 6 statue cards (now drafted as `card_goddess_statue`, for mae to confirm), 1 Lost Goddess
Statue on the island map (`world/lost_goddess_statue_auroradrasil_mae.png`), 2 area maps with statue icons, 1
blessing popup. Proposed: append `world_goddess_statue` and `world_lost_statue` (group world, kind region): the
large and the small statue look different and give different rewards (R-070), so they get separate classes; the
blessed and unblessed looks stay one class each. The capture session adds statues (below).

**Built (mae said yes, 2026-11-11 22:58).** The four classes are appended to classes.json; the catalogue is
`resource/world/collectibles.json` (`sxs/detect/collectibles.py`) with families `resource_hunt` (ore rock, sand
node, Rolla node: the Journal Resource Hunt targets), `misc` (Bellflower now; mae: recipe resources that crop up now
and then, many more to come as we explore), `chest`, `pickup`. Essence is not a collectible kind: mae confirmed the
"stamina 5" board is a monster fight, which any monster can give once its zone is blessed, so it is boxed as
`monster` plus `stamina_cost`. The labeler shows a "which collectible?" menu and a cost menu on `world_collectible`
boxes, and the Category menu filters by collectible kind or family. `python -m sxs dataset --collectibles
family|each|one` (default family).

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
| 6 | Statues: walk to each Goddess and Lost Goddess Statue in reach (blessed ones in done zones, an unblessed one when a zone is at 100%), burst the approach and the card | 6+ (3 of each kind) | 0 |
| 7 | Stamina-costing forms, in blessed zones, while above 150 stamina and never below 70: ore, sand, Rolla nodes, and a monster fight for essence; one burst each, frames show the "⚡5" label | 8 (2 per resource) | about 40 |

That is about 20 sequences, about 100 picked frames, and at least 3 sequences per kind across 2 zones. The target for
a first training is 50 boxes on 20 screens per class, so ore, plant and pickup each need about 2 sessions; later
sessions add other zones and lighting (shadow, and blessed zones, whose colours brighten).

Live-run rules: the readout rule (post command, goal, target and stop condition before, readouts about every 2
minutes, a [Result] at the end), never spend Dawnium, never tap Golden Beetles, keep 70 stamina.

## Making it automatic (built 2026-11-11)

Hand-run bursts are only the first batch. The loops already take a frame every step, so the lasting fix is a
pre-roll buffer: the fog walk and the gather collector keep their last 12 frames, and when a pickup or reward popup
appears they save the buffer as a `seq_` sequence (R-131 already asks for a reference of every collectible met).
Every exploration run then adds training data with no extra emulator time.

Built as `sxs/core/preroll.py`: every screenshot goes into a 12-frame buffer (`SXS_PREROLL`, 0 turns it off); the
R-131 moments (`sxs/vision/collectibles.save`: a monster fight starting, an interactable's card in Clear Zone) and
each gather pickup save it to `captures/sequences/seq_<kind>_<what>_<area>_<time>/` (one per event per 20 s), and
writing stops at `SXS_PREROLL_MAX_MB` (500 MB) so a long run cannot fill the disk. Not run live yet: the first
approved run shows how big the sequences get. Not covered yet: a stamina drop with no fight or pickup (mae: report
it with a pre-roll of the cause); that needs a stamina read in Clear Zone, which belongs to that thread.

## Labeling sequences

The pre-labeller cannot draft collectibles yet (no detector for them). Plan: mae boxes the collectible on the
nearest frame of a sequence; a sequence drafter (`prelabel --sequence NAME`, to build) follows the box backwards
frame by frame by template matching in a small window (scale 0.9 to 1.1) and drafts it on the earlier frames; mae
checks them in the review grid (one category, keep or reject). Ore rocks get a head start from the existing "⚡5"
template (`resource/image/explore/stamina_cost_5.png`) and the tracking ring finder.

## What mae decides

1. ~~Classes~~: two tiers, `world_collectible` + kind (mae, 18:35); the four class names approved (22:58).
2. A time for the capture session (the builder thread runs it; the coordinator asks).
3. ~~Pre-roll buffer~~: yes (mae, 18:35), built; shorten it (`SXS_PREROLL`) if the frames bloat.
