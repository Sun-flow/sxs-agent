# Notes

> **Last updated**: 2026-11-04
> Things learned the hard way. Add to this as soon as you learn something the next session would otherwise rediscover. Keep each note to a line or two, keep only what is highly relevant, and remove notes that stop being true.

## Working with mae

- mae wants the system split into components that run scripts without constant model calls; the model is for being stuck or planning. mae likes the "agent writes its own scripts" pattern: when a model solves something, save it as a script so it costs nothing next time.
- Loops must check semi-regularly whether they are stuck, even during automated runs (no progress, same screen or card repeating), and stop or recover. A stuck case that keeps recurring means the loop needs to be made more robust, not just restarted (mae, 2026-11-04).
- Loops must be composable: one loop can call another and then resume, for example the area exploration loop runs the multi-floor dungeon loop when it meets a dungeon, then carries on exploring (mae, 2026-11-04).
- Budget: a Claude subscription now, a local model later. Don't design anything that needs a model call per action.
- Windows first; Linux is fine where it is easier.
- It is a test account and a learning project; the game's terms of service are not a concern. Decompiling the APK is allowed.
- The game is "Sword x Staff". Older notes and the project name say "Sword x Shield" or "SxS"; they mean the same game.

## Environment and tools

- maes2024 is the Windows PC that runs the emulator; work there goes through `C:\Users\jcmon\Desktop\sxs-player`. Only one Remote Control session should drive it at a time.
- Cloud sessions can't reach APKPure or APKMirror (network policy). Pull the APK from the emulator with `adb shell pm path com.zjcs.android.us` and `adb pull` instead.
- The game is **portrait**: frames are 720 wide × 1280 tall, although MuMu is set to 1280×720. All tap coordinates use the portrait frame.
- Use the venv: `.venv\Scripts\python`. Plain `python` in Git Bash on maes2024 hits the Microsoft Store alias; the real interpreter is `py -3.12`.
- MaaFramework batches OCR across a node's `next` list, and the batched results misread screens, so the detector runs nodes one by one instead (`sxs/state.py`). MaaFramework has `And`/`Or` recognitions but no `Not`.
- MaaFramework's MuMu plug-in prints `nemu_connect`/`product:` lines to stdout, so take the last line for JSON. Its log is in the gitignored .maa/debug folder.
- The game mostly ignores the Android back key; use the on-screen back arrows. Tapping the home chat strip (y ≈ 1040–1150) opens Server Chat.
- mae doesn't want temp files piling up: run `python scripts/clean.py` at the end of every session on maes2024 (it clears the gitignored captures and .maa/debug folders).
- mae's design rule for game logic: write "given the goal and circumstances, pick the right option (which may be declining)" functions, not "advance through the menu" scripts. Cards go through `sxs/decide.py`.
- Overnight rules from mae (2026-11-03): don't spend Dawnium, delete or dismantle items, type in chat, or accept agreements or account prompts. Leave lasting choices (class) to mae.
- Healing rule from mae (2026-11-03): healing food (Green Riceball, bought for Rolla or cooked from ingredients) is cheap, so heal freely while fights are being won. Recover from the player portrait's right-hand button. Retry a lost fight at most 2 times; after that, go home and get stronger, or ask mae. Stat-boost "dishes" are rarer: conserve them. Implemented in `sxs/explore.py` (`RETRIES`).
- Popups close on a tap above them (360, 60); a tap below them sometimes does nothing.
- After a restart the game resumes on the last screen, so a cold start can land on the world map instead of home.
- The auto-mode classifier refused running a helper script from the session scratchpad; keep helper scripts in `scripts/`.
- Seasons partly reset levels, so unlock-level assumptions need re-checking each season (step 1 doc, section 3).
