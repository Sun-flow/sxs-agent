# Combat rules

Read before any fight, when HP is low, after a loss, or inside a mini-dungeon or Fantasia Ascent.

## Before a fight: HP and healing

### R-061 · Heal to 70% before any fight; retry a lost fight at most twice
- **HP must be at least 70% before any fight** (mae). Judge HP from the HUD bar only (R-078); a red "!" over the player is not a heal signal (R-080). `sxs/explore.py` heals below 80%; `sxs/heal.py` is the shared check.
- Healing food (Alchemy Pot, or bought with Rolla) is cheap: use freely. Player portrait, then "Recover" (or similar) on the right.
- **Dishes** are rare temporary stat boosts: conserve them.
- Same fight lost twice in a row after healing: stop (mae). Contact mae or go home to get stronger (gear, techniques, rank).
*told* · node `player_profile`, `wounded`, `alchemy_pot` · R-078, R-031, R-080

### R-078 · Read HP on the HUD bar; heal via the HUD portrait
- HP bar: top-left of the map HUD, x 116-268, y 52-64 (720x1280 px).
- Tap the top-left portrait for Quick Heal. Works on any screen that shows it (map, battle prep, dungeon floor cards); no need to back out (mae).
- Not the player sprite: on a shared tile it opens a pick-one menu and re-taps loop. If that menu opens, pick the character's name.
*told* · node `player_profile` · R-061, R-091

### R-046 · "Badly wounded" dialog
- Starting a fight badly hurt shows "The character is badly wounded. Use dishes to heal?": Return to Home / Quick Heal (costs dishes, e.g. 2; count top right; cooked in the Alchemy Pot, R-047).
- Repeated Quick Heal sometimes didn't clear it, then only Return to Home was offered ❓ (heal too small, or dishes ran out). "Dishes" may mean healing food here ❓.
*observed* · `wounded.png` · node `wounded` · R-061, R-031, R-047

## Starting and running fights

### R-001 · All battles are automatic
- The bot only starts battles and handles the screens around them.
- Map fight: tap the monster, Start Battle on prep. Up to 15 rounds ("Round n/15"). A win returns to the map in about 4 s, no result screen.
*observed* · `battle_prep.png`, `battle.png` · node `battle_prep`, `battle` · R-031

### R-073 · Fight monsters that block the path
- Fight a roaming monster standing between the player and a pickup first. Spear wolves (Verdantglade): `resource/image/monsters/wolf_spear*.png`.
*observed* · R-001, R-041, R-066

### R-127 · Take fights against up to 25% more CP than ours
When weighing a fight or challenge, accept monsters with up to 25% more CP (power) than the character (mae). Monsters usually out-power us on CP, but skills and gear win when the character is well equipped. Above 25% treat it as a wall (R-084). HP rules still apply first (R-061).
*told* · R-061, R-073, R-084

### R-112 · Background fights: start, minimise, move on
- A fight with the "run in background" icon (square, arrow into its lower-left corner) needs no watching. On Conquest it's at (0.10, 0.95); tap to minimise, do other things, come back for the result. Template `resource/image/state/background_fight.png`.
- Fantasia Ascent's Auto Challenge also runs in the background (R-079).
*told* · `icons/background_battle.png` · R-079, R-111

## After a loss

### R-031 · "Incapacitated" and "badly wounded" are both losses
- "Your character is incapacitated. Return to Home now?": Cancel (0.32, 0.65), OK (0.68, 0.65) goes home; the explore loop stops.
- A loss can instead show "badly wounded" (R-046) and move the character back (Verdantglade III: entrance (178, 88) or Verdantglade II).
- Count either toward the retry limit (R-061) and power wall (R-084).
*observed* · `defeated.png`, `wounded.png` · node `defeated` · R-061, R-046, R-084

## Mini-dungeons

### R-040 · Temple Ruins: multi-floor mini-dungeon
- Card "Temple Ruins" (Originisle III): Explore, 6-enemy prep, auto battle, then floor card "Temple Ruins: Floor n" with Next Floor (0.5, 0.64) and a back arrow to leave.
- Floor count unknown; summit "legacy skill" reward ❓. Enter only when exploring with HP fine (R-042).
*observed* · `interact_temple.png`, `dungeon_floor.png` · node `interact`, `dungeon_floor` · R-091, R-071, R-042

### R-071 · Mines: mini-dungeons with first-clear rewards
- Mine cards (e.g. "Ironvein Pit") show First Clear Rewards (Refined Ore 100, Raw Ore 640) and Explore at (0.5, 0.80). Battles up to 25 rounds.
- Card policy: a mini-dungeon is any card named *Ruins, Cave, Tower, Dungeon, Pit, Mine, Lair, Den or Fortress, or showing "First Clear Rewards".
*observed* · `interact_ironvein_pit.png` · R-040, R-042

### R-091 · Heal between floors; a defeat ends the run
- Low HP is no reason to leave (mae): heal from the portrait on the floor card or prep (R-078), then Next Floor.
- Prep HP bar under the character model: x 314-406, y 866-876 (720x1280 px), yellow-green when full. Apply the 70% check; prep can be backed out of.
- A lost fight inside (then "badly wounded" or forced heal) resets the dungeon: count a loss (R-031), don't continue.
*told* · `dungeon_floor.png` · node `dungeon_floor` · R-061, R-078, R-031

## Fantasia Ascent (tower)

### R-079 · Fantasia Ascent: one climb a day, Auto Challenge on, never Retry
- Daily step `fantasia_ascent` (`sxs/tower.py`, run date in `logs/daily.json`); the explore loop can call it too and gets control back. One climb a day; **never retry a tower loss** (mae).
- Route: Journal, Fantasia Ascent (R-094). Or quest "Into the Moon's Shadow I" Go, then OK (0.68, 0.57) on "Return to Home to challenge the Fantasia Ascent?".
- `tower_list` (cards "Current: Fn/110") -> `tower_floors` (F1 at bottom; Goals tab may be badged, R-063; recommended power, Challenge (0.85, 0.86)) -> prep (15 rounds) -> `tower_result`.
- VICTORY: Clear Rewards (ores, Worn Knuckles), Continue (0.77, 0.95) goes to the next floor's prep. DEFEAT: Retry in the same spot: **never press it**.
- Before F3 is cleared, climb floor by floor (Continue). Auto Challenge then unlocks: its checkbox (0.66, 0.90) appears only on the result screen, so tick it after each win; Continue then counts down "(3s)". A loss unticks it; leave it off (ticking on DEFEAT starts a retry).
*told, observed* · `confirm_fantasia_home.png`, `fantasia_ascent.png`, `fantasia_floors.png`, `fantasia_victory.png`, `fantasia_defeat.png` · node `fantasia_ascent`, `fantasia_floors`, `fantasia_result` · R-094, R-112
