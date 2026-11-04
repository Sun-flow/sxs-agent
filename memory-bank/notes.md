# Notes

> **Last updated**: 2026-11-04
> mae's preferences and the working rules that bind every loop. Game rules live in `game/rules/`; machine and tool gotchas in `environments.md`. Keep each note to a line or two; remove notes that stop being true.

## mae

- Learning project, test account: the game's terms of service are not a concern; decompiling the APK is allowed.
- The game is "Sword x Staff". The project name and older notes say "Sword x Shield" or "SxS"; same game.
- Budget: a Claude subscription now, a local model later. Scripts run without model calls; the model is for being stuck or planning. When a model solves something, save it as a script so it costs nothing next time. Credits are fine during build-out; the final bot must be token-efficient.
- Windows first; Linux where easier.
- mae guides from phone or PC and likes Claude playing the game itself. Ask before touching the game after a pause.
- Lasting or account choices are mae's: class, social (friends, team, guild choice), agreements, account prompts. Never delete or dismantle items, never type in chat. Full list: `game/rules/policy.md`.

## How loops must behave (mae, 2026-11-04)

- **Goal-driven**: "given the goal and circumstances, pick the right option (which may be declining)", not "advance through the menu". Cards go through `sxs/policy/decide.py` and `resource/policy/cards.json`.
- **Stuck checks**: every loop checks regularly whether it's stuck (no progress, same screen or card repeating: heartbeat, watchdogs) and ends early with a named reason. A stuck case that recurs means make the loop more robust, not restart it.
- **Unknown state**: unfamiliar screens are an explicit `UNKNOWN` (`sxs/core/state.py`). Try a known recovery (back arrow, close, tap the HUD) a bounded number of times, otherwise end early and report, with the frame saved to `captures/unknown/`.
- **Composable**: loops call each other and resume (explore hands Fantasia Ascent screens to `sxs.loops.tower`, then carries on).
- **Banner**: every loop logs this when it starts, and the builder posts it to mae:
  ```
  [Running XXX Loop]
  [Goal: reason for running this loop]
  [End condition: when this loop ends]
  ```
