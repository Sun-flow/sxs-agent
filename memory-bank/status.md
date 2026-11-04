# Status

> **Last updated**: 2026-11-04

**Current step**: step 3. The bot plays the quest line by itself (`python -m sxs.explore --chain`). Verdantglade is done up to its power walls: 5 areas cleared (I, II, Moonveil Woods, Stone Ruins I, Highland Woods). The main quest "Explore Verdantglade III" needs ~12K power (have 10K); Damp Woods needs 15.5K. Read `memory-bank/handoff.md` first.

## Works

- Step 1 design doc: emulator choice (MuMu Player 12), toolkit (MaaFramework + MaaMCP), game survey and daily-content catalogue with a suggested iteration 1 scope. `docs/step1-emulator-and-game.md`, merged in PR #1.
- Agent setup: `AGENTS.md` entry point, `CLAUDE.md`, this memory bank and `scripts/check-memory.py` (2026-11-03, PR #2).
- Hands-and-eyes layer: MaaFramework device control over MuMu IPC (~7 ms screenshots), the `python -m sxs` CLI, the state detector, `Navigator.go_home()` from a cold start, the offline detector check and a live smoke test. `docs/step2-hands-and-eyes.md`, merged in PR #5 (2026-11-03).
- Quest following (2026-11-03): `sxs/explore.py` follows the tracker marker and edge pointers (boss, statue, unlock). It fights; opens cards through the decision rules (`sxs/decide.py`, `resource/policy/cards.json`); climbs mini-dungeons; heals and retries per mae's rule; claims quests via the tracker gift; and gets unstuck by talking to NPCs with a red "!", fighting path blockers and guards, and panning the camera. `sxs/tutorial.py` follows the tutorial (yellow highlight, Akane hints; never spend-looking buttons). `sxs/strengthen.py` claims the Cart, enhances gear and upgrades techniques. `sxs/minimap.py` reads minimap tiles and finds a path to unexplored ground; `sxs/fogwalk.py` uses it for side areas (experimental). Story text is logged to the gitignored `logs/dialogue.log`. `docs/step3-explore.md`.
- maes2024 game state (2026-11-04): account gromb2 on Forgehall, Lv 13, Mage, Apprentice I, power ~10K, Dawnium ~1.03K untouched by the bot. Originisle done; Verdantglade I, II, Moonveil Woods, Stone Ruins I and Highland Woods explored, statues blessed (Moonveil, Highland). Fantasia Ascent Moonveil Woods F5 cleared (today's run used). 3 of 4 charm slots filled.
- Step 3 additions (2026-11-04): `sxs/goto.py` (walk via the area map), `sxs/tower.py` (Fantasia Ascent daily), charm and gear equipping in `sxs/strengthen.py`, loop banners, heartbeats, watchdogs and unknown-screen saves in all loops.

## In progress

Format: `- what — branch, PR, environment (started date)`. Remove the line when it merges or is dropped.

- Step 3 exploration continues from `memory-bank/handoff.md` (PR #7 merged), maes2024 via Remote Control (2026-11-03).
- Game rules and menu navigation graph (`memory-bank/game/`), filled in from rule batches the builder sends — branch `claude/project-thread-npg43i`, PRs #3, #4 and #6 merged; R-068 to R-077 in PR #8, cloud (2026-11-03).

## Next

See `memory-bank/handoff.md` → "Next steps". In short: get stronger toward 12K (rank up, cook, daily Fantasia Ascent, Cart) and retry Verdantglade III; count "badly wounded" respawns as losses; badge sweep; daily pipelines; model supervisor.

## Open questions

- Daily reset time. The server clock is UTC-5 (shown on the main menu) and weekly achievement quests refresh Monday 08:00 UTC-5, but the daily reset hour is unknown. (`memory-bank/game/rules.md`, R-024)
- Is co-op content in iteration 1?
- Should chat channels on home be hidden in Settings → Game → Social Settings? It would cut OCR noise and stray taps, but it's a settings change, so it's left for mae.

## Known problems

- The minimap classifier was tuned in Verdantglade II; in Highland Woods it labels walkable explored tiles as walls, so the fog walk plans poorly there.

- Cloud sessions can't download the APK (network policy blocks APK mirrors); it has to come from the emulator on maes2024.
- maes2024 has no `gh` CLI, so PRs are opened from the cloud by the coordinator. Git push works.
- The island-map camera doesn't follow the player, so screen-relative planning (minimap walker, blocker taps) needs the player located first: by the "gromb2" label, or by tapping the player edge pointer.
- Quick Heal from the "badly wounded" dialog didn't seem to heal; Quick Heal from the player profile works.
