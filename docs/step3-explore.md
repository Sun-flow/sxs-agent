# Step 3: exploring and following quests without a model

_Started 2026-11-03 on maes2024 (account Lv 2 → 10, Originisle II–IV and the Guardian Colossi cleared)._

## Commands

| Command | What it does |
|---|---|
| `python -m sxs explore [--chain] [--minutes 20] [--choose REGEX]` | Follows the quest tracker on the island map: fights, collects, opens cards, climbs mini-dungeon floors, heals, claims finished quests. `--chain` starts the next quest. `--choose` passes a decision a human made (e.g. `'^Ascend to Mage$'`). |
| `python -m sxs tutorial [--steps 40]` | Follows tutorial prompts: taps through dialogue and taps what the yellow highlight or "Tap to..." bubble points at (R-036). |
| `python -m sxs goto "Stone Ruins I"` or `goto X Y` | Walks to an area label (OCR'd) or point on the area map. |
| `python -m sxs fogwalk [--minutes 10] [--area NAME]` | Explores areas with no quest marker: minimap's unexplored tiles, then the fog edge. |
| `python -m sxs roam [--minutes 30] [--area NAME] [--max-areas 2] [--walk-minutes 10]` | Picks unfinished areas from the area map (R-076), walks there, fog-walks them, unlocks their statue (R-070). Stops at the first power wall (R-084). |
| `python -m sxs tower [--tower NAME] [--to N] [--floors 110] [--minutes 15]` | Fantasia Ascent climb (R-079): Auto Challenge on, no retries. |
| `python -m sxs see minimap [FRAME.png]` | Classifies minimap tiles (R-066); writes `captures/minimap.png`. |

## Loop conventions (bind every loop)

From mae, 2026-11-04; see `memory-bank/decisions.md` ("Loops are watched and hand off to each other").

- **Banner** at start via `device.banner()`: `[Running X Loop]` / `[Goal: ...]` / `[End condition: ...]`. Post it to mae when starting a loop.
- **Stuck checks**: periodic heartbeat log line; end early with a named reason, never idle. Explore's reasons: `complete`, `defeated`, `no_marker`, `no_tracker`, `unknown_card`, `repeating_card`, `needs_decision`, `stuck_home`, `stuck_progress`, `stuck_self`, `low_hp`, `unknown_screen`, `timeout`. A loop that gets stuck repeatedly needs fixing, not restarting.
- **Unknown screens**: a bounded known recovery (back arrow, close, tap outside), then `device.save_unknown()` (frame to `captures/unknown/`) and stop.
- **Composable**: loops call each other and resume (explore hands Fantasia Ascent screens to `sxs.loops.tower`; roam uses goto and fogwalk).
- **Heal before fights**: never fight under 70% HP (R-061); `sxs/actions/heal.py` for loops outside explore.

## Explore loop (`sxs/loops/explore.py`)

One detection per step, then by state:

| State | Action |
|---|---|
| `world_map` | Tracker shows n/n → tap it to claim. Else find the gold ring (`Explore.Marker`, bright/dim/boss): at a screen edge tap it to pan, else tap ~100 px below it. Ring under the HUD (`Explore.MarkerAnywhere`) → drag the map. No ring → ensure tracking is on (`Explore.TrackingIcon`, by colour) and toggle to re-centre. |
| `battle_prep` | Start Battle (after the HP check). |
| `battle`, `loading` | Wait. |
| `interact`, `dungeon_floor`, `confirm_dialog`, `quest_detail`, `defeated` | Decision step. `defeated` ends the run (R-031). |
| `player_profile` | Quick Heal if HP < 80%, else close (tap above the popup, R-060). |
| `dialogue`, `dialogue_choice`, `reward_popup`, `tap_to_continue` | Advance or close; reply choices take the lowest option. |
| `home` | OCR the tracker panel: claim a finished quest, or open it and Go. |
| other | Tap outside; stop after 5 in a row or 20 total. |

**Stall handling**: if progress hasn't moved for 4 map visits, rotate: talk to an NPC with a red "!" (`Explore.NpcAlert`, R-062; skip the "!" over our own name), attack a guard with gold brackets (`Explore.GuardBracket`, R-041), vary the tap offset. 16 stalled visits → `stuck_progress`. Same card title 4 times in a row → `repeating_card`; 3 cards with no rule → `unknown_card`.

## Decision step (`sxs/policy/decide.py`, `resource/policy/cards.json`)

- Read the card's title, text and buttons; match ordered rules on `kind`/`match`, filtered by `when` (`goal`: `explore`, `daily`, `idle`; `hp_ok`). A rule chooses a button regex, `cancel` or `dismiss`. Rule semantics: R-042.
- Never presses spend buttons (R-043). Lasting choices (class) stop with `needs_decision` (R-054).
- No rule → dismiss and count as unknown. When the log shows `no rule for card '...'`, add a rule to `cards.json`, not code.

## Tutorial follower (`sxs/loops/tutorial.py`)

`find_highlight()` finds a bright yellow rounded-rectangle outline by HSV: yellow must run along the edges into the corners with a mostly non-yellow inside (rejects lime buttons and round icons). If the highlight wraps a yellow button, it falls back to the hint bubble (`Tutorial.Hint`) and taps ~100 px below it.

## Open

- Pale/white tutorial highlights (the Skill button) are not detected, nor highlights on yellow buttons with no hint bubble.
- Quick Heal from the "badly wounded" card didn't seem to take; from the profile it works (R-078).
- Loot off the tracker's path (e.g. after a boss) isn't picked up unless fogwalk/roam reaches it.
- `sxs/loops/explore.py` keeps its own inline copy of the heal logic instead of `sxs/actions/heal.py`.
