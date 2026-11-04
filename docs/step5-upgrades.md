# Step 5: upgrade systems and gathering

Two composable loops, also run from `sxs.loops.daily` (steps `strengthen` and `gather`).

## Upgrade Loop (`sxs/loops/upgrade.py`)

```bash
python -m sxs upgrade [--only skills,gear,class_levels,rank,relics]
python -m sxs strengthen     # Cart, gear, techniques only (older pass; soft resources)
```

Any red "!" on the Character screen means an upgrade is ready: always check and apply it (R-080). `sxs/vision/badges.py` finds the badges by colour (red disc, thin white mark); badges pulse, so two frames are merged. Each badge runs one pass:

| Badge | Pass | Does | Rules |
|---|---|---|---|
| Gear slot | `gear` | Banded enhancement (all pieces to the next multiple of 5, `GEAR_PRIORITY` order), then Gear Resonance Activate, then Enhancement Goals | R-092, R-119 |
| Skill | `skills` | Quick Upgrade (gone when nothing is affordable), Ascend techniques with "!" (10 own shards), fill empty charm slots, claim Skill Goals | R-104, R-115, R-037 |
| Class | `class_levels` | Tap class cards with "!" (badges), level on the Upgrade tab, claim Total Class Level goals. **Never Change Class.** | R-117 |
| Apprentice | `rank` | Claim Level and Power goals; Advance only when the Advance button itself has "!" | R-118 |
| (relics) | `relics` | Not unlocked. `relic_plan()` encodes the banding | R-105 |

Every button is tapped only while its own "!" stays (the game shows it only while affordable), within a tap budget, each tap checked for an effect, never with a `claims.SPEND` word on its row. Spends only Rolla, ore, Battle Essence, shards, class badges (later sand); never Dawnium or Rcmd Loadouts. Reference screens (`docs/screens/`): `gear_resonance`, `gear_goals`, `skill_page`, `technique_upgrade`, `technique_ascend`, `class_hierarchy`, `class_upgrade`, `class_goals`, `rank_advancement`, `rank_level_goals`, `rank_power_goals`, and more.

## Gather Loop (`sxs/loops/gather.py`)

```bash
python -m sxs gather                          # priority material from resource/policy/gather.json
python -m sxs gather --material ore|sand|essence|rolla
python -m sxs gather --check                  # read stamina and the plan, tap nothing
python -m sxs gather --harvest [bellflower]   # already on the map with an item tracker: collect until full
```

- One entry point, `Gatherer.collect(target)`. A `Target` says how the material's objects are found, how progress shows (stamina drop or tracker "a/b") and the cost per pickup.
- Route: Journal → Map Exploration → Resource Hunt → material → Go → OK (R-108).
- Tap order: R-124 (special-node green timer first, R-109; blue aura first, R-122; then "bolt 5" cost labels `Gather.StaminaCost`, then tracking ring, edge ring, minimap ring). Tap the objects themselves, never the tracker icon over the character.
- Policy `resource/policy/gather.json`: `priority` (first entry is gathered; mae switches ore → sand), `keep_stamina` 70 (R-107). Stamina is read after each tap.
- Stuck checks: progress within `STALE_ACTIONS` taps, at most 3 taps on ourselves; unknown screen → back arrow twice, then stop with the frame saved. Guarded pickups: backs out of battle prep and stops.
- Measured: ~one ore pickup per 6–7 s, ~+178 Raw Ore each.

Open: special-node detector is a guess (green circle, radius 14–36 px, not yet seen); daily cap per material unknown.

## Tests

`python tests/check_upgrade_logic.py` (relic banding, stamina budget, badge counts on reference screens) and `python tests/check_states_offline.py`.
