# Status

> **Last updated**: 2026-11-03

**Current step**: step 3. The bot plays the quest line by itself (`python -m sxs.explore --chain`) and has reached Verdantglade. It's blocked on "Moonveil Woods I: Unlock Moonveil Woods", where the way in seems to run through unexplored ground that only the minimap shows. The thread is being handed off: read `memory-bank/handoff.md` first.

## Works

- Step 1 design doc: emulator choice (MuMu Player 12), toolkit (MaaFramework + MaaMCP), game survey and daily-content catalogue with a suggested iteration 1 scope. `docs/step1-emulator-and-game.md`, merged in PR #1.
- Agent setup: `AGENTS.md` entry point, `CLAUDE.md`, this memory bank and `scripts/check-memory.py` (2026-11-03, PR #2).
- Hands-and-eyes layer: MaaFramework device control over MuMu IPC (~7 ms screenshots), the `python -m sxs` CLI, the state detector, `Navigator.go_home()` from a cold start, the offline detector check and a live smoke test. `docs/step2-hands-and-eyes.md`, merged in PR #5 (2026-11-03).
- Quest following (2026-11-03): `sxs/explore.py` follows the tracker marker and edge pointers (boss, statue, unlock). It fights; opens cards through the decision rules (`sxs/decide.py`, `resource/policy/cards.json`); climbs mini-dungeons; heals and retries per mae's rule; claims quests via the tracker gift; and gets unstuck by talking to NPCs with a red "!", fighting path blockers and guards, and panning the camera. `sxs/tutorial.py` follows the tutorial (yellow highlight, Akane hints; never spend-looking buttons). `sxs/strengthen.py` claims the Cart, enhances gear and upgrades techniques. `sxs/minimap.py` reads minimap tiles and finds a path to unexplored ground; `sxs/fogwalk.py` uses it for side areas (experimental). Story text is logged to the gitignored `logs/dialogue.log`. `docs/step3-explore.md`.
- maes2024 game state: account gromb2 on Forgehall, Lv 12, Mage, rank Apprentice I, power ~7.7K. Originisle is done (I–V, the Guardian Colossi boss, Voyage Obelisk). Verdantglade I and II are 100% explored and blessed (Blessing Level 3). Dawnium ~789 is untouched by the bot; the 10 free tutorial prayer tickets were used.

## In progress

Format: `- what — branch, PR, environment (started date)`. Remove the line when it merges or is dropped.

- Step 3 exploration continues from `memory-bank/handoff.md` (PR #7 merged), maes2024 via Remote Control (2026-11-03).
- Game rules and menu navigation graph (`memory-bank/game/`), filled in from rule batches the builder sends — branch `claude/project-thread-npg43i`, PRs #3, #4 and #6 merged; R-068 to R-077 in PR #8, cloud (2026-11-03).

## Next

See `memory-bank/handoff.md` → "Next steps". In short: get into Moonveil Woods with the minimap walker (it needs the player's screen position, and the camera doesn't follow the player); explore the Verdantglade side areas (Stone Ruins I, Damp Woods), stopping at 4 to 7 Verdantglade areas in total; automate the rest of strengthening and a "claim the red badges" sweep; then the daily-content pipelines and the model supervisor.

## Open questions

- How to unlock Moonveil Woods (asked mae 2026-11-03 with a screenshot; mae's hint: the minimap shows a connected route south of the cliff).
- Daily reset time. The server clock is UTC-5 (shown on the main menu) and weekly achievement quests refresh Monday 08:00 UTC-5, but the daily reset hour is unknown. (`memory-bank/game/rules.md`, R-024)
- Is co-op content in iteration 1?
- Should chat channels on home be hidden in Settings → Game → Social Settings? It would cut OCR noise and stray taps, but it's a settings change, so it's left for mae.

## Known problems

- Cloud sessions can't download the APK (network policy blocks APK mirrors); it has to come from the emulator on maes2024.
- maes2024 has no `gh` CLI, so PRs are opened from the cloud by the coordinator. Git push works.
- The island-map camera doesn't follow the player, so screen-relative planning (minimap walker, blocker taps) needs the player located first: by the "gromb2" label, or by tapping the player edge pointer.
- Quick Heal from the "badly wounded" dialog didn't seem to heal; Quick Heal from the player profile works.
