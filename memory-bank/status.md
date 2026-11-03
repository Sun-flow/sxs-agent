# Status

> **Last updated**: 2026-11-03

**Current step**: step 2 setup. The step 1 decision doc is written; maes2024 is being set up so the hands-and-eyes layer can be built.

## Works

- Step 1 design doc: emulator choice (MuMu Player 12), toolkit (MaaFramework + MaaMCP), game survey and daily-content catalogue with a suggested iteration 1 scope. `docs/step1-emulator-and-game.md`, merged in PR #1.
- Agent setup: `AGENTS.md` entry point, `CLAUDE.md`, this memory bank and `scripts/check-memory.py` (2026-11-03, PR #2).

## In progress

Format: `- what — branch, PR, environment (started date)`. Remove the line when it merges or is dropped.

- Set up MuMu Player 12 and Python on maes2024 — no branch, maes2024 via Remote Control (2026-11-03).
- Game rules and menu navigation graph (`memory-bank/game/`), filled in as the step 2 builder thread reports what it learns — branch `claude/project-thread-npg43i`, cloud (2026-11-03).

## Next

1. Finish maes2024 setup: virtualization on, MuMu Player 12 at 1280×720, test account signed in, game installed and tutorial done, Python 3.12 and `adb` (step 1 doc, "Getting maes2024 ready").
2. Pull the APK from the emulator and check the engine (Unity/Il2Cpp or Cocos) and any emulator detection.
3. Step 2: MaaFramework controller over MuMu, a "where am I" state detector, and the first pipelines for the iteration 1 dailies.

## Open questions

- Test account level and server (guilds unlock at 15, vendor at 18).
- Daily reset time on the server.
- Is co-op content in iteration 1?

## Known problems

- Cloud sessions can't download the APK (network policy blocks APK mirrors); it has to come from the emulator on maes2024.
