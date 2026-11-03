# Notes

> **Last updated**: 2026-11-03
> Things learned the hard way. Add to this as soon as you learn something the next session would otherwise rediscover. Keep each note to a line or two, keep only what is highly relevant, and remove notes that stop being true.

## Working with mae

- mae wants the system split into components that run scripts without constant model calls; the model is for being stuck or planning. mae likes the "agent writes its own scripts" pattern: when a model solves something, save it as a script so it costs nothing next time.
- Budget: a Claude subscription now, a local model later. Don't design anything that needs a model call per action.
- Windows first; Linux is fine where it is easier.
- It is a test account and a learning project; the game's terms of service are not a concern. Decompiling the APK is allowed.
- The game is "Sword x Staff". Older notes and the project name say "Sword x Shield" or "SxS"; they mean the same game.

## Environment and tools

- maes2024 is the Windows PC that runs the emulator; work there goes through `C:\Users\jcmon\Desktop\sxs-player`. Only one Remote Control session should drive it at a time.
- Cloud sessions can't reach APKPure or APKMirror (network policy). Pull the APK from the emulator with `adb shell pm path com.zjcs.android.us` and `adb pull` instead.
- Step 2 keeps working screenshots in a gitignored scratch folder (newest 40 frames) and its clean.py script clears them at session end (step 2 branch step2-hands-and-eyes, not merged yet ❓).
- Seasons partly reset levels, so unlock-level assumptions need re-checking each season (step 1 doc, section 3).
