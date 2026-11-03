# Handoff: game-playing and screen-mapping session on maes2024

> **Last updated**: 2026-11-03

> Written 2026-11-03 by the session that built steps 2 and 3. You're taking over the same job. Read `AGENTS.md` and `memory-bank/README.md` first (the start-of-session steps), then this file.

## Your job

Keep the Sword x Staff test account progressing through the game on maes2024, and turn everything you learn into **deterministic code and data, not model calls**. Each new screen gets a detector state; each new card or dialog gets a decision rule; each recurring chore gets a script. The long-run goal is a bot that does the dailies unattended and calls a model only when stuck. You are building that bot by playing.

You run as a Remote Control session on mae's PC, in `C:\Users\jcmon\Desktop\sxs-player\sxs-agent`. You talk to mae only through the thread tools. A coordinator Claude relays project context; send it rule batches with `send_message` (`session_id: "@parent"`, `visibility: "sent_to_shared_agent"`), and it forwards them to the docs thread that maintains `memory-bank/game/rules.md` and `memory-bank/game/nav-graph.json`.

## How the previous session worked (keep doing this)

1. **Let the loop play; step in when it stops.** Run `python -m sxs.explore --chain --minutes N`, usually in the background with output to a log. It returns a reason when it can't go on (`unknown_card`, `stuck_progress`, `needs_decision`, `defeated`, `needs_help`, ...).
2. **When it stops, look once and fix it generally.** Take a screenshot (`python scripts/explore.py none 0`, then view captures/latest.jpg). Work out what the game wants. Then add the smallest general fix: a `State.*` node in `resource/pipeline/state.json`, a rule in `resource/policy/cards.json`, a template in `resource/image/`, or a handler in `sxs/explore.py`. Avoid one-off taps baked into code. Prefer "given the goal and circumstances, choose the option" over "press the big button" (mae's design rule).
3. **Save a reference screenshot** for every new screen: `python -m sxs capture NAME` writes NAME.png into `docs/screens/`. Add it to `EXPECTED` in `tests/check_states_offline.py`, then run `python tests/check_states_offline.py`, which must say "all good".
4. **Send rule batches** to the coordinator whenever you learn something: what a screen is for, how to detect it, where to tap (as fractions of 720×1280), what a currency or item does, how a quest works. Include `docs/screens/...` paths. Don't resend what the coordinator says it already forwarded.
5. **Post short status updates** to mae at milestones (an area done, a blocker, a question), with a screenshot when it helps (`SendUserFile`, then attach the `/mnt/project-files/...` path it returns). mae sometimes asks for an update every ~5 minutes; then run the loop in 5-minute chunks.
6. **Commit and push often** on `step3-explore` (`git pull --no-rebase` first: the docs thread sometimes merges main into this branch). PR #7 is open. There's no `gh` here, so ask the coordinator if a new PR is needed.
7. **End of session**: update the memory bank (`status.md`, `log.md`, `notes.md`, `decisions.md`), run `python scripts/check-memory.py`, then `python scripts/clean.py` (mae wants temp files cleared).

## Rules from mae (don't break these)

- **Never spend Dawnium** (orange gem) or press Buy / Purchase / Refresh / Spend / Pray / Recharge. Rolla (gold coin), ores and Battle Essence are fine for upgrades. Healing food (Green Riceball: cooked, or bought for Rolla) is fine. Conserve stat-boost dishes.
- **Heal and retry a lost fight at most 2 times**; then go home and get stronger (`sxs.strengthen`); if it still loses, ask mae. This is built into `sxs/explore.py` (`RETRIES`).
- **No lasting choices without mae**: class choices (mae picked Mage; `--choose "^Ascend to Mage$"` applies a choice mae made), and anything account- or agreement-related.
- **Social stays untouched**: friend, team-up and challenge requests, chat (never type), the Team panel.
- **Verdantglade cap**: clear only the first 4 to 7 Verdantglade areas, or stop at a natural wall. Done so far: Verdantglade I and II. Moonveil Woods would be the 3rd.
- Map "!" over an NPC means talk to them (quests can be gated behind it). A red "!" badge on a menu or button means something to claim. Badged menus change as event banners roll over, so don't hard-code the list.
- Some quests are explained only in dialogue. Read `logs/dialogue.log` when stuck.

## State right now (2026-11-03 evening)

- **Game**: gromb2 on server Forgehall, Lv 12, Mage, Apprentice I, power ~7.7K, Rolla ~41K, Dawnium ~789. Standing in Verdantglade II at about (173, 104), near its west cliff. Tracker: "Moonveil Woods I: Unlock Moonveil Woods" (no counter, no Go button). The tracker's blue-orb edge pointer sits inside the fog west of the cliff.
- **Blocker**: the route into Moonveil Woods. mae marked a connected strip of unexplored walkable tiles on the minimap, south-west of the player (`docs/screens/minimap/minimap_verdantglade2.png`, classified in `docs/screens/minimap/minimap_classified.png`). The area map (tap the minimap; `docs/screens/world_area_map.png`) shows Moonveil Woods, Stone Ruins I and Damp Woods at 0%, Highland Woods needing 9.6K power and Verdantglade III needing 12K.
- **Code**: everything is pushed on `step3-explore`. The detector knows 24 screen nodes (plus unknown and not_running), checked against 76 reference screenshots.

## How to run things

```bash
.venv\Scripts\python -m sxs state                       # what screen is this (JSON)
.venv\Scripts\python scripts\explore.py none 0          # screenshot -> captures\latest.jpg (half size) to look at
.venv\Scripts\python scripts\explore.py tap X Y 3       # tap, wait 3 s, screenshot
.venv\Scripts\python -m sxs.explore --chain --minutes 10 > captures\explore.log 2>&1
.venv\Scripts\python -m sxs.tutorial --steps 40         # follow tutorial highlights
.venv\Scripts\python -m sxs.strengthen                  # Cart, gear, techniques
.venv\Scripts\python -m sxs.minimap [frame.png]         # classify minimap -> captures\minimap.png
.venv\Scripts\python -m sxs.fogwalk --minutes 5         # experimental: walk to unexplored ground
.venv\Scripts\python scripts\advance.py 20              # tap through dialogue and popups
.venv\Scripts\python scripts\ocr.py IMG X Y W H         # what text MaaFramework sees in a region
.venv\Scripts\python scripts\crop.py IMG X Y W H OUT    # make a template
.venv\Scripts\python tests\check_states_offline.py      # detector regression on docs\screens
```

Filter MaaFramework's chatter when reading logs: `grep -v -i "nemu\|product:\|same day\|^x:\|after convert"`. Run the Python helpers from `scripts/`, not the scratchpad (the auto-mode classifier blocked scratchpad scripts). The game is portrait: coordinates are in a 720×1280 frame.

Code map: `docs/step2-hands-and-eyes.md` (device, detector, CLI) and `docs/step3-explore.md` (explore loop, decisions, tutorial follower). The game knowledge lives in `memory-bank/game/` (maintained by the docs thread).

## Next steps, in order

0. **Build map-based navigation (mae, 2026-11-03)**, used by everything below. Open the area map by tapping the minimap (docs/screens/world_area_map.png). Search it for unexplored areas: 0% labels, shadowed or unspotted ground, pickups. Then go there: tap that spot on the map so the camera centres over it, close the map (back arrow; the camera now looks at that spot), and tap the ground where you want to go, and the game auto-paths the character there. Wrap it as `sxs/navigate.py` with `find_unexplored()` (read the area map like the minimap) and `go_to(map_point)`, and use it instead of straight-line taps.

1. **Get into Moonveil Woods.** First try mae's navigation procedure (2026-11-03): open the area map (tap the minimap), tap the spot you want so the camera centres there, close the map, then tap the ground at that spot and the game auto-paths the character. Turn it into a reusable `go_to(area_map_point)` helper. Finish the minimap walker in `sxs/fogwalk.py` → `minimap_target()`. It already classifies tiles and finds a BFS path to the nearest `walk_unexplored` or `item` tile. It still needs the player's screen position, and the camera doesn't follow the player: tap the player's edge pointer (a white ring with the player's face) to re-centre, or OCR the "gromb2" label. Calibrate `SCREEN_TILE` (~104 px per tile) by tapping and reading the coordinates under the minimap. Check after each tap that the coordinates changed, and if not, try another tile. Then walk the strip mae pointed out. If it's still blocked, ask mae.
2. **Explore the Verdantglade side areas** (Stone Ruins I, Damp Woods) with the same walker, blessing each area's statue at 100%. Keep a count: stop at 4 to 7 Verdantglade areas in total.
3. **Strengthening, finish it**: equip new gear and techniques (red-dot slots), rank up when the requirements are met (Character → Rank badge), cook Green Riceballs in the Alchemy Pot when they run low, and use the Bed's "Today's Free Speedup" once a day.
4. **Badge sweep**: a routine that finds red "!" badges on menus and buttons (not on the map), opens each one, and claims through the card rules. It must be generic, because events rotate.
5. **Dailies** (`docs/step1-emulator-and-game.md` §4 iteration 1 list): one pipeline each, as they unlock (Guild at Lv 15, Vendor at 18).
6. **Supervisor**: when a loop returns `unknown_card`, `stuck_progress` or `unknown_screen`, hand the screenshot and recent log to a model once, and save its answer as a rule, template or state, so the same situation costs nothing next time.
