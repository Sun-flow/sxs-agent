# Environments

> **Last updated**: 2026-11-05
> Where sessions run and the gotchas of each. Read before touching the emulator, a PC or the network.

## rif-love-su (current game PC, from 2026-11-04)

- mae's Windows PC. Repo at `C:\Users\jcmon\Github\sxs-agent`; venv `.venv\Scripts\python`.
- MuMu Player 12, instance 1, adb at **127.0.0.1:16416**. `sxs.core.device` falls back to the only adb device when the default is missing and `SXS_ADB_ADDRESS` is unset. On 2026-11-04 evening the fallback hung for over 2 minutes (more than one adb device listed?); `export SXS_ADB_ADDRESS=127.0.0.1:16416` before running fixed it. State detection takes 2-5 s per frame here.
- Display 1080×1920 @ 480 DPI: same 9:16 portrait, so the 720×1280 coordinates and templates still work. A state check takes ~4-7 s. If image matching misbehaves, switch MuMu to 720×1280 @ 240 first.
- No `gh` CLI: PRs are opened from the cloud. Git push works.
- Offline detector check (`tests/check_states_offline.py`, ~186 screens) takes ~10 min.
- Only one Remote Control session should drive the emulator at a time.

## maes2024 (retired, offline since 2026-11-04 ~10:00)

- Folder `C:\Users\jcmon\Desktop\sxs-player`, repo in `sxs-player\sxs-agent`, MuMu 720×1280 @ 240, adb 127.0.0.1:16384, Python 3.12.
- Plain `python` in Git Bash hits the Microsoft Store alias; use the venv or `py -3.12`.

## Cloud sessions

- Edit the repo, open PRs, maintain docs. No emulator.
- Can't reach APKPure or APKMirror (network policy). Pull the APK from the emulator instead: `adb shell pm path com.zjcs.android.us`, then `adb pull`.

## Emulator and toolkit gotchas

- The game is **portrait**: frames are 720 wide × 1280 tall even though MuMu's setting reads landscape. All coordinates use the portrait frame.
- MaaFramework batches OCR across a node's `next` list and misreads screens, so the detector runs nodes one by one (`sxs/core/state.py`). It has `And`/`Or` recognitions but no `Not`.
- OCR misses or misreads small white labels on dark badges ("+15" gear, "Lv. 10" skills, top-bar amounts) at real size; enlarged 3x onto a black canvas they read cleanly (`vision.ocr.zoomed_lines`, 2026-11-04). Cloud sessions can run the OCR checks: `pip install maafw==5.15.0 opencv-python-headless`, then `python3 scripts/fetch-ocr-models.py`.
- MaaFramework's MuMu plug-in prints `nemu_connect`/`product:` lines to stdout: take the last line for JSON. Its log is in the gitignored `.maa/debug` folder.
- After a restart the game resumes on the last screen, so a cold start can land on the world map instead of home.
- Home scene panning: fast swipes at mid-height often don't register; use slow (1 s) drags over the ground at y≈820 (`HOME_SWIPE_*` in `sxs/loops/strengthen.py`). Restart the game with `Device.stop_game()` / `start_game()` (about 40 s to the title).
- Typing into a game search field works with `adb shell input text` (MuMu's adb: `C:\Program Files\Netease\MuMuPlayer\nx_device\15.0\shell\adb.exe -s 127.0.0.1:<port>`). Never type in chat.
- The auto-mode classifier refuses helper scripts run from the session scratchpad; keep them in `scripts/`.
- mae doesn't want temp files piling up: `python scripts/clean.py` at the end of every session on the game PC (clears the gitignored captures and `.maa/debug`; it leaves the logs folder).
