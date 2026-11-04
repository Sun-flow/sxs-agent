# Step 5: upgrade systems and gathering

Two composable loops, both also run from `sxs.daily` (steps `gather` and `strengthen`).

## Upgrade Loop: `python -m sxs.upgrade [--only skills,gear,class_levels,rank,relics]`

mae, 2026-11-04: any red "!" on the Character screen means an upgrade is ready; always check and apply it (R-080).
`sxs/badges.py` finds the "!" badges by colour (red disc, thin white mark; badges pulse, so two frames are merged).
The loop reads the Character screen's badges and runs the pass behind each one:

| Badge | Pass | What it does | Screens |
|---|---|---|---|
| Gear slot | `gear` | Banded enhancement (5 levels, all pieces, `GEAR_PRIORITY`), then Gear Resonance: Activate each bonus earned (all 4 pieces at +5, +10, ...), then the Enhancement Goals tab. | `gear_resonance`, `gear_goals` |
| Skill | `skills` | Quick Upgrade (one tap levels every skill with Battle Essence; the button disappears when nothing is affordable), Ascend each technique with "!" (Enhance > Ascend tab, 10 of its own shards), fill empty charm slots from the Charm tab, claim Skill Goals (Level, Quality). | `skill_page`, `skill_page_after_quick_upgrade`, `technique_upgrade`, `technique_ascend`, `skill_goals_quality` |
| Class | `class_levels` | Class Hierarchy: tap each class card with "!" (claims its Class Badges), level it on the Upgrade tab (10 badges a level), claim Total Class Level goals. **Never Change Class.** | `class_page`, `class_hierarchy`, `class_badge_received`, `class_info`, `class_upgrade`, `class_goals` |
| Apprentice (rank) | `rank` | Claim Level and Power goals; Advance only when the Advance button itself carries "!". | `rank_advancement`, `rank_level_goals`, `rank_power_goals`, `item_bellflower` |
| (relics) | `relics` | Not unlocked yet. `relic_plan()` already encodes the rule: steps of 1, one element's 4 relics as a band, elements by affinity (highest first), all elements level before the next step. | none yet |

Every button is tapped only while its own "!" stays (the game shows it only while affordable), with a tap budget,
and never when a spend word (`claims.SPEND`) is on the same row.

## Gather Loop: `python -m sxs.gather [--material ore|sand|essence|rolla] [--check]`

Route: Journal (bottom bar, 2nd icon) > Map Exploration > Resource Hunt: pick the material, Go, OK on "Enter
Verdantglade to explore?". The game drops the character near the material with a tracking ring over the nearest
pickup. The loop then repeats: green special-node timer circle first (free, R-109), else the nearest "bolt 5" cost
label (template `Gather.StaminaCost`, pickups close to the character), else the tracking ring on the map, else the
ring at a screen edge (tap pans the camera), else the ring on the minimap (walk toward it). Stamina is read at the
top right after each tap; it stops at the reserve.

Policy: `resource/policy/gather.json` (`priority`: first entry is gathered, `keep_stamina`: 70). Switch ore to sand
there when mae says so.

First live run (2026-11-04): 171 stamina, 20 ore pickups, about one every 6 to 7 seconds, about +178 Raw Ore each.

Not seen yet: a special node (its detector is a guess: a green circle, radius 14 to 36 px); the daily cap per
material type; guarded pickups (the loop backs out of battle prep and stops).

## Tests

`python tests/check_upgrade_logic.py` (relic banding, stamina budget, badge counts on reference screens) and
`python tests/check_states_offline.py` (the new `State.*` screens).
