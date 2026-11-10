# Gathering rules

Read when spending stamina, gathering materials on the overworld, or picking up items in a field.

## Stamina budget

### R-107 · Keep 70 stamina for daily commissions; spend the rest on the priority material
- Stamina (lightning icon, top bar "52/300") pays for map nodes and pickups. It regenerates 5 an hour; passive regen stops at 300 and overflow is wasted, so spend before it fills. Items can push it up to 1,200.
- **Always keep at least 70 stamina for the daily commissions.** Spend the rest gathering the priority material, currently **ore** (mae will switch it to sand).
- Policy: `resource/policy/gather.json` (`priority`, first entry is gathered; `keep_stamina`). Route: R-108.
- Free +30 a day from the Vendor Booth Vault (R-120).
*told, observed* · `resource/image/currency/stamina.png` · node `shop` · R-106, R-108, R-120

### R-106 · Four upgrade materials, each gathered for 5 stamina a pickup
**Ore** pays for gear (R-023), **sand** for relics (R-105), **battle essence** for skills (R-037, R-104), **rolla** is general coin (R-019). All lie on the overworld at 5 stamina per pickup; most days offer resources of each type. Other sources: mining (R-095), Guidance quests for ore (R-099).
*told* · R-076, R-095, R-107, R-108

## Getting to a material

### R-108 · Track a material through Journal > Map Exploration > Resource Hunt
- Home bottom bar, second icon (Journal, R-094), Map Exploration (0.29, 0.47): the Resource Hunt card, showing stamina ("175/300"). Material icons at y 0.24: Rolla x 0.08, ore 0.18, sand 0.29, Battle Essence 0.39. Then Go (0.84, 0.28), then OK (0.68, 0.57) on "Enter Verdantglade to explore?".
- The tracked object sits in a yellow and white ring, also on the minimap and as an edge ring (tap it to pan there).
- Ore: a mine in Verdantglade II near map (187, 97), grey rocks with blue crystals. Pickups show a "lightning 5" label; one tap on a rock walks there and mines it (5 stamina, about +178 Raw Ore). Stop at the R-107 budget.
- Boars with a "lightning 5" label also appear there ❓ (what they give is unknown).
- Code: `python -m sxs gather` (priority material), `--material sand` (override), `--check` (read stamina and plan only).
*told, observed* · `home/journal.png`, `world/map_exploration.png`, `dialogs/confirm_enter_explore.png`, `world/explore_ore_rocks.png`, `world/explore_ore_mined.png`, `world/explore_stamina_boar.png`, `resource/image/explore/stamina_cost_5.png` · node `travel_journal` · R-094, R-107, R-124

## On the field: what to tap

### R-124 · The collector's tap order
`Gatherer.collect(target)` in `sxs/loops/gather.py` handles ore, sand, essence, Rolla and Bellflowers. Each pass it taps the first it sees of:
1. a green-timer special node (R-109);
2. material objects on the ground (template or the "5" stamina label), blue-aura first (R-122);
3. the tracking ring, only if more than 70 px from the character;
4. the edge ring;
5. a walk toward the minimap ring.

Never the ring or icon over the character (R-123). Bellflower template: mae's picture at 1.3x, threshold 0.6 (no false hits on ore, boars, tracker or world map).
*observed* · `world/explore_bellflower_field_wide.png`, `icons/bellflower_mae.png`, `resource/image/explore/bellflower.png` · R-108, R-109, R-122, R-123

### R-122 · Prefer pickups with a blue aura
Blue-aura pickups are rarer and give bonus ingredients. Take them before plain ones in reach.
*told* · R-124

### R-139 · A monster guarding a pickup: fight it, then resume the pickup
When a monster blocks or guards a pickup, fight it first, then go back to the same pickup and collect it (mae, 2026-11-09). This holds in every loop that explores (quest, roam, fog walk, gather). A guard shows a red horned-skull marker over it (`resource/image/explore/guard_marker.png`); code: `unstick.attack_guard` and the shared `start_fight` in `sxs/actions/common.py` (R-073). The fight follows the usual checks: HP at 70% (R-061), the power limit (R-127), at most two retries.
*told* · R-061, R-073, R-124, R-127

### R-109 · Always tap special nodes with a green timer circle
Special nodes or encounters carry a green timer circle at their upper right and are high value: always tap them. A Grand Mine gives one free material collection. Chat announces "Grand Iron Mine" / "Grand Sand Mine" spawns in Verdantglade ❓ (where they appear is unknown).
*told* · R-108, R-124

## Bellflowers

### R-123 · Bellflowers come from the free Verdantglade Flower Harvest
- Route: Character (0.11, 0.97), rank badge (0.82, 0.72), the middle cost icon on Rank Advancement (0.50, 0.74), the item card's Source row "Verdantglade Flower Harvest »" (0.82, 0.59), OK (0.68, 0.57). Lands in Verdantglade II near minimap (181, 90) with a tracker "a/20" on the left panel and an edge ring toward the field. Code: `Gatherer.enter_bellflower_field()`; `python -m sxs gather --harvest bellflower` collects once on the map.
- The look-alike plants in Drasilgard don't count (R-134).
- Field: Moonveil Woods, minimap (169, 94-95), the clearing south of the big hollow-tree arch, stone statue on its west side. About 8 white-bell plants respawn.
- **Tap the plants themselves, never the tracker ring over the character or the Bellflower icon** (mae). Picks are free, +2 each; blue-aura first (R-122). **Never tap other players in the field** (R-057).
- At 20/20 Akane's dialogue says "Go for that rank advancement!" (tap on); home then shows a tutorial overlay on Character, rank badge, Advance (R-036).
- The first visit also plays the tutorial that unlocks the Vendor Booth (R-120). Bellflowers and Rank Advancement come before mapping shops (mae).
*observed, told* · `world/item_bellflower.png`, `world/explore_bellflower_tracker.png`, `world/explore_bellflower_field.png`, `world/explore_bellflower_field_wide.png`, `world/explore_bellflower_picked.png`, `world/explore_bellflower_done_dialogue.png`, `icons/bellflower_mae.png`, `resource/image/explore/bellflower.png` · R-118, R-122, R-124
