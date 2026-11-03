# Status

> **Last updated**: 2026-11-03

**Current step**: step 2 (hands and eyes) is built and smoke-tested on maes2024, and its PR is pending. Next is step 3, the daily loop.

## Works

- Step 1 design doc: emulator choice (MuMu Player 12), toolkit (MaaFramework + MaaMCP), game survey and daily-content catalogue with a suggested iteration 1 scope. `docs/step1-emulator-and-game.md`, merged in PR #1.
- Agent setup: `AGENTS.md` entry point, `CLAUDE.md`, this memory bank and `scripts/check-memory.py` (2026-11-03, PR #2).
- Hands-and-eyes layer (2026-11-03): MaaFramework device control over MuMu IPC (~7 ms screenshots), the `python -m sxs` CLI, a 14-screen state detector (OCR and templates, no model), `Navigator.go_home()` from a cold start, an offline detector check, a live smoke test (passed twice, ~60 s) and 25 reference screenshots. `docs/step2-hands-and-eyes.md`.
- maes2024: MuMu Player 12 with the game installed and signed in (account gromb2, server Forgehall, Lv 2). Tutorial prompts are done and Wild Isle Trek I is finished.

## In progress

Format: `- what — branch, PR, environment (started date)`. Remove the line when it merges or is dropped.

- Step 2 hands-and-eyes layer — branch `step2-hands-and-eyes`, PR #5, maes2024 via Remote Control (2026-11-03).
- Game rules and menu navigation graph (`memory-bank/game/`), filled in as the step 2 work reports what it learns — branch `claude/project-thread-npg43i`, PR #3 merged, later batches in PR #4, cloud (2026-11-03).

## Next

1. Merge step 2.
2. Level the account so dailies unlock (Guild at Lv 15, Vendor at 18). Map the shop, dungeon, mail and arena screens as they appear, and add `State.*` nodes for them.
3. Step 3: one pipeline per iteration 1 daily, plus the supervisor that calls a model only on `unknown` or a timeout.
4. Check the APK's engine (Unity/Il2Cpp or Cocos). The split APK is in the `apk` folder next to the repo on maes2024, not in the repo.

## Open questions

- Daily reset time. The server clock is UTC-5 (shown on the main menu) and weekly achievement quests refresh Monday 08:00 UTC-5, but the daily reset hour is unknown. (`memory-bank/game/rules.md`, R-024)
- Is co-op content in iteration 1?

## Known problems

- Cloud sessions can't download the APK (network policy blocks APK mirrors); it has to come from the emulator on maes2024.
- Git on maes2024 has no GitHub credentials yet, so Remote Control sessions can't push until mae signs in once.
- No `battle_result` screen has been seen; an easy map fight returns straight to the map.
