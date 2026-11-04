# Handoff: game-playing and screen-mapping session on maes2024

> **Last updated**: 2026-11-04

> Written 2026-11-03 by the session that built steps 2 and 3; updated 2026-11-04 by the dailies-and-upgrades session (step 4). You're taking over the same job. Read `AGENTS.md` and `memory-bank/README.md` first (the start-of-session steps), then this file.

## Your job

Keep the Sword x Staff test account progressing through the game on maes2024, and turn everything you learn into **deterministic code and data, not model calls**. Each new screen gets a detector state; each new card or dialog gets a decision rule; each recurring chore gets a script. The long-run goal is a bot that does the dailies unattended and calls a model only when stuck. You are building that bot by playing.

You run as a Remote Control session on mae's PC, in `C:\Users\jcmon\Desktop\sxs-player\sxs-agent`. You talk to mae only through the thread tools. A coordinator Claude relays project context; send it rule batches with `send_message` (`session_id: "@parent"`, `visibility: "sent_to_shared_agent"`), and it forwards them to the docs thread that maintains `memory-bank/game/rules.md` and `memory-bank/game/nav-graph.json`.

## How the previous session worked (keep doing this)

1. **Let the loop play; step in when it stops.** Run `python -m sxs.explore --chain --minutes N`, usually in the background with output to a log. It returns a reason when it can't go on (`unknown_card`, `stuck_progress`, `needs_decision`, `defeated`, `needs_help`, ...).
2. **When it stops, look once and fix it generally.** Take a screenshot (`python scripts/explore.py none 0`, then view captures/latest.jpg). Work out what the game wants. Then add the smallest general fix: a `State.*` node in `resource/pipeline/state.json`, a rule in `resource/policy/cards.json`, a template in `resource/image/`, or a handler in `sxs/explore.py`. Avoid one-off taps baked into code. Prefer "given the goal and circumstances, choose the option" over "press the big button" (mae's design rule).
3. **Save a reference screenshot** for every new screen: `python -m sxs capture NAME` writes NAME.png into `docs/screens/`. Add it to `EXPECTED` in `tests/check_states_offline.py`, then run `python tests/check_states_offline.py`, which must say "all good".
4. **Send rule batches** to the coordinator whenever you learn something: what a screen is for, how to detect it, where to tap (as fractions of 720×1280), what a currency or item does, how a quest works. Include `docs/screens/...` paths. Don't resend what the coordinator says it already forwarded.
5. **Post short status updates** to mae at milestones (an area done, a blocker, a question), with a screenshot when it helps (`SendUserFile`, then attach the `/mnt/project-files/...` path it returns). mae sometimes asks for an update every ~5 minutes; then run the loop in 5-minute chunks.
6. **Commit and push often** on your own branch cut from main (`git pull --no-rebase` first: the docs thread sometimes merges main into it). There's no `gh` here, so ask the coordinator to open the PR. Watch for PowerShell `Set-Content -Encoding utf8`: it adds a BOM; prefer Python or the Edit tool for file edits.
7. **End of session**: update the memory bank (`status.md`, `log.md`, `notes.md`, `decisions.md`), run `python scripts/check-memory.py`, then `python scripts/clean.py` (mae wants temp files cleared).

## Rules from mae (don't break these)

- **Never spend Dawnium** (orange gem) or press Buy / Purchase / Refresh / Spend / Pray / Recharge. Exception: skill pulls at the Goddess Statue when mae (the handler) triggers them, only through `python -m sxs.pray --pulls N --handler-approved` (Standard banner, Stellatie tickets, never "+"). Never pull from a loop. Rolla (gold coin), ores and Battle Essence are fine for upgrades. Healing food (Green Riceball: cooked, or bought for Rolla) is fine. Conserve stat-boost dishes.
- **Heal and retry a lost fight at most 2 times**; then go home and get stronger (`sxs.strengthen`); if it still loses, ask mae. This is built into `sxs/explore.py` (`RETRIES`).
- **No lasting choices without mae**: class choices (mae picked Mage; `--choose "^Ascend to Mage$"` applies a choice mae made), and anything account- or agreement-related.
- **Social stays untouched**: friend, team-up and challenge requests, chat (never type), the Team panel.
- **Verdantglade cap**: clear only the first 4 to 7 Verdantglade areas, or stop at a natural wall. 5 done (I, II, Moonveil Woods, Stone Ruins I, Highland Woods).
- Map "!" over an NPC means talk to them (quests can be gated behind it). A red "!" badge on a menu or button means something to claim. Badged menus change as event banners roll over, so don't hard-code the list.
- Some quests are explained only in dialogue. Read `logs/dialogue.log` when stuck.
- **Loops (mae, 2026-11-04)**: every loop checks regularly whether it's stuck and ends early with a reason; a loop that gets stuck regularly needs fixing, not restarting. Unfamiliar screens are flagged (frame in `captures/unknown/`) and end the loop. Loops call each other (explore → tower → back). **Post mae a banner in the thread whenever you start a loop**: `[Running X Loop]` / `[Goal: ...]` / `[End condition: ...]`.
- **Fantasia Ascent**: Auto Challenge always on, no retries, one run a day (a daily).
- A red "!" over the player can mean empty charm slots or better gear, not only low HP; heal by the HP bar.
- **Gear**: enhance in 5-level bands, all pieces together, priority weapon > offhand > headpiece > chest > boots (`Strengthener.enhance_gear`, `GEAR_PRIORITY`).
- **Bed XP (mae, 2026-11-04)**: an icon over the bed in the house shows when there is AFK XP to collect. XP builds slowly, so collect it once a day (more often only when close to a level-up). It is a daily chore, not part of the upgrade pass. mae will send a screenshot of the icon; not automated yet.
- **Don't use Rcmd Loadouts.** Defeat in a mini-dungeon resets the run.
- **Mall**: stay out until mae says whether free items there (daily stamina pack) may be claimed (asked 2026-11-04, no answer yet).

## State right now (2026-11-04, end of the dailies thread)

- **Game**: gromb2 on Forgehall, **Lv 20** (mae collected bed XP), Mage, power ~13.1K, Rolla ~43K, Dawnium ~1.09K (never spent), Stellatie 20 (prayer tickets). Home shows the house view. Tracker: "Path to Upgrade: Reach Lv. 20" (claimable). Gear: staff +21, hat +12, chest +10, boots +7; Raw Ore is the bottleneck.
- **New at Lv 20: the Guild.** The bottom bar's 4th icon (crest, between Home and World, about (0.68, 0.97)) is unlocked and highlighted by a tutorial (`docs/screens/home_guild_tutorial.png`). Nobody has opened it yet. **Your first job is mapping it** (see Next steps).
- **Verdantglade III** needs ~12K: now reachable on power (13.1K), untested.
- **Today's dailies** (server day 2026-11-03, `logs/daily.json`): sign-in, Fantasia Ascent (F6 reached), Cart, Ironvein Pit (3 hammers), quests, strengthen.
- **Open questions to mae**: may `sxs.pray` run 20 Standard pulls now (all 20 Stellatie)? May the bot claim free items in Mall?
- **Code**: everything through PR #14 (`dailies-upgrades`) is merged into main. This handoff is on branch `dailies-wrapup`.

### Tested vs untested (2026-11-04)

| Piece | Status |
|---|---|
| `sxs.daily` (sign_in, cart, growth_trial, fantasia_ascent, material_realms, quests, strengthen) | All steps ran live and returned home. Sign-in and Growth Trial claims tested only with nothing left to claim (sign-in was claimed by hand first). `fantasia_ascent` via the Journal tab: entry tested, the climb itself not since (already done that day). |
| `sxs.claims.claim_all` | Tested on the Prayer Goals tab (claimed 1). |
| Banded gear enhancement | Tested with ore: boots 2 to 5, then chest 9 to 10 and boots 5 to 7, stopping when short. Correct band order. |
| Ironvein Pit | Tested: 3 hammers used, about +115 Raw Ore each; Goals claimed. |
| `sxs.pray` | `--check` tested (opens Prayer, reads 20 tickets and Dawnium). Refusal without flags tested. **No pull run yet.** The result-screen flow (animation skip, back) is untested. |
| Tower heal on battle prep (`sxs/heal.py`) | Untested live. |
| `equip_charms` | Taps the locked 4th charm slot and logs "loadout editor did not open": harmless noise, fix by skipping locked slots. |

The step 3 pieces (goto, explore, tower hand-over, loss counting, HUD HP, mini-dungeons) are listed in the same table of the previous handoff: `git show 30339d2:memory-bank/handoff.md`.

### Gotchas

- **Home stuck on sky**: after a long session the home scene can show only sky; swipes don't move it, so the Cart bubble and the Goddess Statue can't be found. Restarting the game (`Device.stop_game()`, then `go_home`) fixes it. Worth an automatic check.
- The Goddess Statue tap point (`sxs/pray.py` `HOME_STATUE`) assumes the default home camera after a fresh start.

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
.venv\Scripts\python -m sxs.daily [--only a,b] [--force]  # all dailies + upgrade passes (docs/step4-dailies.md)
.venv\Scripts\python -m sxs.pray --check                 # Prayer ticket count; pulls need --pulls N --handler-approved
.venv\Scripts\python scripts\advance.py 20              # tap through dialogue and popups
.venv\Scripts\python scripts\ocr.py IMG X Y W H         # what text MaaFramework sees in a region
.venv\Scripts\python scripts\crop.py IMG X Y W H OUT    # make a template
.venv\Scripts\python tests\check_states_offline.py      # detector regression on docs\screens
```

Filter MaaFramework's chatter when reading logs: `grep -v -i "nemu\|product:\|same day\|^x:\|after convert"`. Run the Python helpers from `scripts/`, not the scratchpad (the auto-mode classifier blocked scratchpad scripts). The game is portrait: coordinates are in a 720×1280 frame.

Code map: `docs/step2-hands-and-eyes.md` (device, detector, CLI) and `docs/step3-explore.md` (explore loop, decisions, tutorial follower). The game knowledge lives in `memory-bank/game/` (maintained by the docs thread).

## Update 2026-11-04 (night, guild thread)

- **Guild done**: gromb2 is in karsa_1515 (mae's OK) and gathers at the Forge. `python -m sxs.guild` (also steps guild_donate, guild_afk, guild_conquest in `sxs.daily`): donations up to 2 a day (Free, then 20 Dawnium: mae-approved; never the 50 one), Forge AFK, Conquest's 2 daily attempts sent to the background, Conquest goals claimed. Screens `docs/screens/guild_*`; rules sent to the coordinator. Untested live: Conquest with attempts left (do it next server day and watch).
- **Bed step** added to `sxs.daily` (template `resource/image/home/bed_xp_bubble.png`), once a day; untested live (mae had collected).
- Not touched: guild Shop (spends Guild Tokens: ask mae), Guildmates, chat, Guild Clash (unlocks ~2026-11-12).
- **Next job (mae, 2026-11-04)**: scripts and rules for upgrade systems, including ones not unlocked yet: skill quick upgrade (tap a skill, "quick upgrade" beside the lower-right charm); relic banding (step 1, per element as one band, all elements level together, element priority by affinity, highest first); materials (ore: armor, sand: relics, battle essence: skills, rolla: coins); stamina gathering via Journal > Map Exploration > material > Go, 5 stamina per pickup, keep 70 stamina for daily commissions, ore first then sand; always tap special nodes with a green timer circle (e.g. Grand Mine, free); always check "!" on the character screen.

## Next steps, in order

1. **Map the Guild** (unlocked at Lv 20). Follow its tutorial (`python -m sxs.tutorial --steps 40`, which follows the yellow highlight and never presses spend-looking buttons; step in by hand where it stalls). For every new screen: a `State.*` node, a reference screenshot in `docs/screens/` plus an `EXPECTED` entry, and a rule batch to the coordinator. Expected guild dailies (step 1 doc §4, R-016): 3 basic donations a day, Guild Farm (plant and harvest), guild boss. Joining or creating a guild, applying, or anything social (chat, requests) is mae's decision: ask before any of it. Donations that cost Dawnium are never made.
2. **Guild dailies into `sxs.daily`** as new steps once mapped (each with a route, a time budget and a done-today mark).
3. **Bed XP step**: once mae sends the icon screenshot, add a once-a-day `bed` step to `sxs.daily` (home → scroll up to the house → bed → claim; R-035), plus "Today's Free Speedup".
4. **Pulls**: when mae says go, `python -m sxs.pray --pulls N --handler-approved`, then equip the new techniques and level them (`Strengthener.upgrade_techniques`). Watch the first run closely: the result-screen flow is untested.
5. **Back to Verdantglade III** at 13K (`sxs.explore --chain`).
6. **Home-stuck check**: restart the game when home shows no Cart bubble and no statue.
7. Older items still open: test the HP logic when HP drops below 70% while alive; minimap classifier per area palette; badge sweep; model supervisor for `unknown_*` stops.
