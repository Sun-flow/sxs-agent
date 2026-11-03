# Status

> **Last updated**: 2026-11-03

**Current step**: step 3 has started. The bot plays the opening quest line by itself (`python -m sxs.explore --chain`) and is paused at the class choice, which waits on mae.

## Works

- Step 1 design doc: emulator choice (MuMu Player 12), toolkit (MaaFramework + MaaMCP), game survey and daily-content catalogue with a suggested iteration 1 scope. `docs/step1-emulator-and-game.md`, merged in PR #1.
- Agent setup: `AGENTS.md` entry point, `CLAUDE.md`, this memory bank and `scripts/check-memory.py` (2026-11-03, PR #2).
- Hands-and-eyes layer: MaaFramework device control over MuMu IPC (~7 ms screenshots), the `python -m sxs` CLI, the state detector, `Navigator.go_home()` from a cold start, the offline detector check and a live smoke test. `docs/step2-hands-and-eyes.md`, merged in PR #5 (2026-11-03).
- Quest following (2026-11-03): an explore loop that follows the tracker marker, fights, opens cards, climbs mini-dungeons, heals and claims quests in a chain; a tutorial follower (yellow highlight and Akane hint bubble); a decision step for cards and dialogs driven by `resource/policy/cards.json`. The detector now knows 25 states, checked against 62 reference screenshots. `docs/step3-explore.md`.
- maes2024 game state: account gromb2 on Forgehall, Lv 10, rank Apprentice I, power ~5.2K. Originisle I to V are done (82% of Originisle overall) and the Guardian Colossi boss is beaten. Dawnium (518) is untouched.

## In progress

Format: `- what — branch, PR, environment (started date)`. Remove the line when it merges or is dropped.

- Step 3 quest following — branch `step3-explore`, no PR yet, maes2024 via Remote Control (2026-11-03).
- Game rules and menu navigation graph (`memory-bank/game/`), filled in from rule batches the builder thread sends — branch `claude/project-thread-npg43i`, PR #3 merged, later batches in PR #4, cloud (2026-11-03).

## Next

1. mae picks the class at the Chief on Originisle V ("Ascend to Mage", "Change Class", "Leave"). The bot always leaves this choice and stops with `needs_decision`.
2. Automate strengthening between losses: equip new gear, enhance gear (`scripts/enhance_all.py`), upgrade techniques, rank up, cook dishes, claim the Cart, and use the Bed's free daily speed-up.
3. Continue the quest line into Verdantglade, stopping after 4 to 7 areas or at a natural wall (mae, 2026-11-03).
4. Step 3 proper: one pipeline per iteration 1 daily, plus the supervisor that calls a model only on `unknown`, `unknown_card` or a timeout.
5. Check the APK's engine (Unity/Il2Cpp or Cocos). The split APK is in the `apk` folder next to the repo on maes2024, not in the repo.

## Open questions

- Which class? (asked in the step 2 thread, 2026-11-03)
- Daily reset time. The server clock is UTC-5 (shown on the main menu) and weekly achievement quests refresh Monday 08:00 UTC-5, but the daily reset hour is unknown. (`memory-bank/game/rules.md`, R-024)
- Is co-op content in iteration 1?
- Should chat channels on home be hidden in Settings → Game → Social Settings? It would cut OCR noise and stray taps, but it's a settings change, so it's left for mae.

## Known problems

- Cloud sessions can't download the APK (network policy blocks APK mirrors); it has to come from the emulator on maes2024.
- maes2024 has no `gh` CLI, so PRs are opened from the cloud. Git push works now that mae has signed in.
- No `battle_result` screen has been seen; won fights return straight to the map.
- Quick Heal from the "badly wounded" dialog didn't seem to heal; Quick Heal from the player profile works.
