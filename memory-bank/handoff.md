# Handoff: game-playing and screen-mapping session on maes2024

> **Last updated**: 2026-11-04

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
- **Loops (mae, 2026-11-04)**: every loop checks regularly whether it's stuck and ends early with a reason; a loop that gets stuck regularly needs fixing, not restarting. Unfamiliar screens are flagged (frame in `captures/unknown/`) and end the loop. Loops call each other (explore → tower → back). **Post mae a banner in the thread whenever you start a loop**: `[Running X Loop]` / `[Goal: ...]` / `[End condition: ...]`.
- **Fantasia Ascent**: Auto Challenge always on, no retries, one run a day (a daily).
- A red "!" over the player can mean empty charm slots or better gear, not only low HP; heal by the HP bar.

## State right now (2026-11-04, end of the exploration thread)

- **Game**: gromb2 on Forgehall, Lv 13, Mage, Apprentice I, power ~10K, Rolla ~43K, Dawnium ~1.03K (never spent). On the Verdantglade III map after losses. Tracker: "Verdant Wonders III: Explore Verdantglade III 0/100" (Rcmd 12K). Gear: Seeker's Staff +21, Adventurer's Leather Hat +12, armour +9, Starter's Boots +2; ore is short (7/720), which caps enhancement now. 3 of 4 charm slots filled (4th locked).
- **Verdantglade**: 5 of the 4 to 7 cap done (I, II, Moonveil Woods, Stone Ruins I, Highland Woods); Moonveil and Highland statues blessed. Walls: Verdantglade III (12K; guard fights lost at 10K), Damp Woods (Gate of Power, 15.5K). Sunrise Isle is on the area map, unvisited. Exploration is finished for now; the next thread works on dailies and upgrades.
- **Today's dailies done**: Fantasia Ascent Moonveil Woods (F1→F5, lost F6; `logs/daily.json`).
- **Code**: PR #11 (`step3-explore`) is merged into main. Later work is on branch `step3-wrapup` (from main): the banded gear enhancement below and this handoff. It needs a PR.

### Tested vs untested (2026-11-04)

| Piece | Status |
|---|---|
| `sxs.goto` area-map walking | Tested (Moonveil, Stone Ruins I, Damp Woods, Highland Woods). Fails on labels inside fog; explore then travels from home via the tracker (tested). |
| `sxs.tower` (Auto Challenge on, no retries, daily marker) | Tested F1–F6. Auto Challenge only appears on the result screen, so the first fight of a run starts without it. |
| Explore → tower hand-over and resume | Tested. Fog walk → tower hand-over: untested. |
| Loss counting ("badly wounded" = lost fight) | Tested: losses counted, retry rule → strengthen ran. A loss dialog seen while the detector says "unknown" is now also counted (untested). |
| HP from the HUD bar (`explore.hud_hp`, x 116-268 y 52-64) | Tested at full HP only (reads 99%). Low-HP reading untested. |
| Heal before fights (< 70%) on the map and on battle prep (`PREP_HP_BAR`, x 314-406 y 866-876) via the top-left portrait | Untested live: no low-HP-while-alive case came up. Prep bar reads 97% on the reference screenshot. Whether battle prep has a tappable portrait is unknown; the code backs out and retries if the portrait doesn't open the profile. |
| Charm filling and better-gear swaps from the profile | Tested. |
| Banded gear enhancement (spec below) | Tested once: read levels {21, 12, 9, 2}, stopped after 1 tap because ore is short. The band logic itself still needs a run with materials. |
| Gold-building POIs on the minimap, fog walk visiting them | Detection tested on one frame; walking to them untested. |
| Mini-dungeon floors: always Next Floor, heal mid-run | Rule changed; untested in a dungeon. |

### Gear enhancement spec (mae, 2026-11-04)

Enhance in **5-level bands with all pieces levelled together**: the target is the next multiple of 5 above the lowest piece; raise every piece below it, in priority order **weapon > offhand > headpiece > chest > boots**, then move to the next band, until materials run short. The order is configurable (`GEAR_PRIORITY` in `sxs/strengthen.py`, indexes into the Enhance Gear tabs; today the tabs are weapon, head, chest, boots, with no offhand yet, so add its index after the weapon when it appears). Implemented in `Strengthener.enhance_gear` (branch `step3-wrapup`). The Enhance Gear screen isn't a detector state yet, so `go_home` can't leave it on its own: add a state for it.

## How to run things

```bash
.venv\Scripts\python -m sxs state                       # what screen is this (JSON)
.venv\Scripts\python scripts\explore.py none 0          # screenshot -> captures\latest.jpg (half size) to look at
.venv\Scripts\python scripts\explore.py tap X Y 3       # tap, wait 3 s, screenshot
.venv\Scripts\python -m sxs.explore --chain --minutes 10 > captures\explore.log 2>&1
.venv\Scripts\python -m sxs.tutorial --steps 40         # follow tutorial highlights
.venv\Scripts\python -m sxs.strengthen                  # Cart, gear, techniques
.venv\Scripts\python -m sxs.minimap [frame.png]         # classify minimap -> captures\minimap.png
.venv\Scripts\python -m sxs.fogwalk --area "Stone Ruins I" --minutes 5   # explore a side area (walks there first)
.venv\Scripts\python -m sxs.goto "Highland Woods"      # walk somewhere via the area map
.venv\Scripts\python -m sxs.tower --tower "Moonveil Woods"   # daily Fantasia Ascent climb
.venv\Scripts\python scripts\advance.py 20              # tap through dialogue and popups
.venv\Scripts\python scripts\ocr.py IMG X Y W H         # what text MaaFramework sees in a region
.venv\Scripts\python scripts\crop.py IMG X Y W H OUT    # make a template
.venv\Scripts\python tests\check_states_offline.py      # detector regression on docs\screens
```

Filter MaaFramework's chatter when reading logs: `grep -v -i "nemu\|product:\|same day\|^x:\|after convert"`. Run the Python helpers from `scripts/`, not the scratchpad (the auto-mode classifier blocked scratchpad scripts). The game is portrait: coordinates are in a 720×1280 frame.

Code map: `docs/step2-hands-and-eyes.md` (device, detector, CLI) and `docs/step3-explore.md` (explore loop, decisions, tutorial follower). The game knowledge lives in `memory-bank/game/` (maintained by the docs thread).

## Next steps, in order

1. **Dailies and upgrades** (the next thread): a daily runner that calls the chores in turn (Fantasia Ascent via `sxs.tower`, Cart, the Bed's free speedup, others as they unlock: `docs/step1-emulator-and-game.md` §4), each with its banner and stop reasons, recording runs in `logs/daily.json`.
2. **Upgrades**: test the banded enhancement with materials; add detector states for Enhance Gear and the technique upgrade screen; rank up when the requirements are met; cook Green Riceballs when low.
3. **Badge sweep**: claim red "!" badges on menus (the Fantasia Ascent Goals tab had one), generic because events rotate.
4. **Test the HP logic** the first time HP drops below 70% while alive (map and battle prep), and watch the retry rule (2 retries, strengthen, ask mae).
5. **Minimap classifier per area palette**: Highland Woods' explored walkable tiles read as walls. Calibrate from tiles the player has stood on.
6. **Back to Verdantglade III** at ~12K power (`sxs.explore --chain`).
7. **Supervisor**: when a loop returns `unknown_card`, `unknown_screen` or a stuck reason, hand the saved frame and recent log to a model once and save its answer as a rule, template or state.
