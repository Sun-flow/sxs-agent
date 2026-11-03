# Step 3 (start): following quests without a model

_2026-11-03, built on maes2024 overnight while playing the opening quests (account Lv 2 → 10)._

## TL;DR

- `python -m sxs.explore --chain` plays the main quest line on its own: it follows the quest tracker's marker on the island map, fights, collects, opens cards, climbs mini-dungeon floors, heals, and claims each quest as it finishes, then starts the next one.
- `python -m sxs.tutorial` follows the game's own tutorial prompts: it taps through dialogue and taps whatever the yellow highlight frame or Akane's "Tap to..." bubble points at.
- Cards and dialogs go through a **decision step** (`sxs/decide.py`, rules in `resource/policy/cards.json`). It reads the card's title, text and buttons, then picks the option that fits the current goal: accept, a specific button, Cancel, or dismiss. It never presses Buy, Purchase, Refresh or Spend, or anything that mentions Dawnium. A card with no rule is dismissed, and after 3 of those the loop stops so a rule can be added.
- With this, Originisle II, III and IV and the Guardian Colossi boss were cleared with almost no manual taps. The manual work was strengthening the character between losses (gear, techniques, rank).

## How the explore loop decides (`sxs/explore.py`)

One detection per step, then by state:

| State | What it does |
|---|---|
| `world_map` | If the tracker shows n/n, tap it to claim. Else find the gold tracker ring (`Explore.Marker`: bright, dim and boss variants). At a screen edge, tap the ring to pan; otherwise tap ~100 px below it, where the target is. If the ring is under the HUD (`Explore.MarkerAnywhere`), drag the map. If progress hasn't moved for 4 map visits, first talk to an NPC with a red "!" (`Explore.NpcAlert`; quests can be gated behind them, as the Chief on Originisle V gated the loot row), skipping the "!" over our own name, then try attacking a monster with gold guard brackets (`Explore.GuardBracket`), then vary the tap offset under the ring. After 16 stalled visits, stop (`stuck_progress`). If there is no ring, make sure tracking is on (`Explore.TrackingIcon`, read by colour), then toggle it to re-centre. |
| `battle_prep` | Start Battle. |
| `battle`, `loading` | Wait. |
| `interact`, `dungeon_floor`, `confirm_dialog`, `quest_detail`, `defeated` | Decision step (below). `defeated` ends the run so the character can be strengthened. |
| `player_profile` | Quick Heal if HP < 80%, otherwise close it (tap above the popup). |
| `dialogue`, `dialogue_choice`, `reward_popup`, `tap_to_continue` | Advance or close. For a reply choice, take the lowest option. |
| `home` | Read the tracker panel by OCR: claim a finished quest, or open the quest and Go. |
| anything else | Tap outside; stop after 5 in a row or 20 in total. |

Guards: the same card title chosen 4 times in a row stops the run (`repeating_card`), as do 3 cards with no rule (`unknown_card`).

## Decision rules (`resource/policy/cards.json`)

The goal is one of `explore`, `daily` or `idle`; `hp_ok` is a flag. Rules are tried in order:

| Card | Explore goal | Otherwise |
|---|---|---|
| Defeated ("incapacitated") | OK (go home) | same |
| Badly wounded | Quick Heal (cooked dishes) | Return to Home |
| Quest detail | Go / Track | dismiss |
| Travel ("Travel to X now?", "Destination: X. Head there now?") | OK | Cancel |
| Portal | Activate | same |
| Mini-dungeon (Temple Ruins, …) | Explore when HP ok | dismiss |
| Dungeon floor ("…: Floor n") | Next Floor when HP ok | back arrow (leave) |
| anything else | dismiss and count as unknown | same |

Add a rule whenever the log shows `no rule for card '...'`.

## Tutorial follower (`sxs/tutorial.py`)

`find_highlight()` looks for a bright yellow rounded-rectangle outline by colour (HSV). It accepts the shape only if the yellow runs along the edges and into the corners and the inside is mostly not yellow, which rules out lime buttons and round icons. When the highlight wraps a yellow button and can't be separated from it, the bubble "Tap to unlock / speed up" (`Tutorial.Hint`) is used instead, with the button ~100 px below. Pale or white highlights (the Skill button) are not detected yet.

## New screens and states

`interact`, `dungeon_floor`, `quest_detail`, `player_profile`, `defeated`, `dialogue_choice`, `tap_to_continue`, `cart`; `reward_popup` now also covers "Cooked". References are in `docs/screens/`, and `tests/check_states_offline.py` covers them.

## Known gaps

- Strengthening (equip new gear, enhance gear, upgrade techniques, rank up, cook dishes) is still done by hand. `scripts/enhance_all.py` covers gear enhancing.
- Quick Heal from the "badly wounded" dialog didn't seem to take effect; from the profile popup it works.
- Pale tutorial highlights, and highlights around yellow buttons that have no hint bubble.
- Loot left on the map after a boss (chests by the Originisle V pillar) isn't picked up unless the tracker points at it.
