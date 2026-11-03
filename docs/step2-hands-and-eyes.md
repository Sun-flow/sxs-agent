# Step 2: hands and eyes

_2026-11-03, built and tested on maes2024._

## TL;DR

- **MaaFramework works on this setup.** `maafw` 5.15 (pip) finds MuMu at `127.0.0.1:16384` and uses MuMu's IPC screenshot path: about **7 ms per frame**. No fallback to plain adb was needed.
- **The game runs in portrait.** Every frame is **720 wide × 1280 tall** even though MuMu is set to 1280×720. All coordinates in this repo are in that portrait frame.
- **No model calls at runtime.** Screens are recognised by OCR (PaddleOCR v4 through MaaFramework) and template matching.
- **State detector**: 14 screens, about 0.1 to 0.8 s per check (the cost is OCR). It passes on all 25 reference screenshots offline (`tests/check_states_offline.py`).
- **Smoke test** (`tests/smoke_test.py`): kill the game, cold-start it, get to home (about 60 s, mostly the game's own loading), then go home → menu → home → World → home → Character → home. Passes.

## Layout

| Path | What |
|---|---|
| `sxs/device.py` | `Device`: connect, `screenshot()`, `tap`, `swipe`, `back`, `start_game`, `stop_game`, `foreground_package`. |
| `sxs/state.py` | `StateDetector.detect()` returns a `Detection` (state id, node, box, OCR text, timing). |
| `sxs/nav.py` | `Navigator.go_home()` (from anywhere, including a cold start) and `tap_and_expect()`. Tap coordinates for the nav bar and common buttons. |
| `sxs/replay.py` | `ImageDevice`: feeds saved PNGs to the detector so it can be tested without the emulator. |
| `sxs/cli.py` | `python -m sxs ...` (below). |
| `resource/` | The MaaFramework bundle. `pipeline/state.json` holds one `State.*` node per screen; `image/` holds templates (paths in pipelines are relative to `image/`); `model/ocr/` holds the OCR models. |
| `docs/screens/` | Reference screenshots, full 720×1280, saved as 256-colour PNGs (~200 KB each). |
| `scripts/fetch-ocr-models.py` | Downloads the OCR models (gitignored, ~12 MB). |
| `scripts/explore.py`, `advance.py`, `record.py`, `ocr.py`, `crop.py`, `sheet.py`, `grid.py` | Tools for exploring new screens by hand (see "Adding a screen"). Their output goes to `captures/` (gitignored). |
| `scripts/clean.py` | Deletes working files (`captures/`, `.maa/debug/`). Run at the end of a session. |
| `tests/` | `check_states_offline.py` (no emulator) and `smoke_test.py` (live). |

## Setup on a fresh clone

```bash
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python scripts\fetch-ocr-models.py
.venv\Scripts\python tests\check_states_offline.py
```

MuMu must be running for anything live. `SXS_ADB_ADDRESS` overrides the default `127.0.0.1:16384`.

## CLI

```bash
python -m sxs state              # {"state": "home", "node": "State.Home", "text": "Home", "elapsed_ms": 560, ...}
python -m sxs state --save DIR   # also save the frame
python -m sxs watch              # print the state whenever it changes
python -m sxs screenshot [out.png]
python -m sxs tap X Y
python -m sxs swipe X1 Y1 X2 Y2 [--ms 300]
python -m sxs back               # Android back key; the game mostly ignores it (see below)
python -m sxs start | stop       # launch or kill the game
python -m sxs capture NAME       # save docs/screens/NAME.png
```

MaaFramework's MuMu plug-in prints a few lines (`nemu_connect ...`, `product: ...`) to stdout; for JSON output, read the last line.

## How the detector works

`State.Detect` in `resource/pipeline/state.json` lists the `State.*` nodes in priority order (`custom_action_param.order`). `detect()` takes one screenshot and the `DetectState` custom action tries each node on that frame, stopping at the first hit. Popups and overlays come first, because they sit on top of other screens. The state id is the node name in snake_case (`State.MainMenu` → `main_menu`); variants share a state (`State.Loading.Title` → `loading`). If the game isn't the focused app, the state is `not_running`.

Why not a plain MaaFramework `next` list: MaaFramework batches OCR across the nodes of a `next` list, and the batched results misread several screens (no "Tap to Play", no "Loading"). Running each node on its own fixed that. Using `only_rec` (skip text detection) made checks about 40% faster but broke five screens, so it is off.

| State | How it is recognised | Reference |
|---|---|---|
| `agreement` | OCR "accept the User Agreement" (first launch only; needs a human) | (not committed) |
| `loading` | OCR "Load" bottom right, "Logging in" mid-screen, or the build string `..._R156699_...` top left while the title initialises | `loading.png`, `logging_in.png`, `title_loading.png` |
| `title` | OCR "Tap to Play" at (360, 1056) | `title.png` |
| `reward_popup` | OCR "YOU RECEIVED" | `reward_popup.png` |
| `confirm_dialog` | OCR "Confirm" title | `confirm_dialog.png` |
| `dialogue` | Template `state/dialogue_arrow.png` (the ▼ at the bottom of the story box) | `dialogue.png`, `dialogue_loadout.png` |
| `battle_prep` | OCR "Start Battle" | `battle_prep.png` |
| `battle` | OCR "Round n/15" top centre | `battle.png` |
| `home` | OCR "Home" under the centre house of the nav bar | `home.png`, `home_cart.png` |
| `world_overview` | OCR "World" under the right nav button | `world_overview.png` |
| `world_map` | OCR of the "x, y" coordinates under the minimap | `world_map*.png` |
| `character` | OCR "Character" under the left nav button | `character.png` |
| `main_menu` | OCR "User Center" | `main_menu.png` |
| `quests` | OCR "Guidance Quest" or "Achievement Quest" | `quest_list.png`, `achievement_quest.png` |
| `unknown` | Nothing matched | `loadout_edit.png`, `player_profile.png`, `quest_detail.png`, `splash.png` |

## Interface catalogue (account Lv 2, server Forgehall)

Coordinates are (x, y) in the 720×1280 frame.

**Boot.** Android splash → BOLTRAY / studio logos (~10 s) → title art with "Initializing resources / Loading patch / Initializing" bar (~25 s) → title with "Tap to Play" (360, 1056) and side buttons (Servers, Settings, Follow Us, Customer Service, Notice, User Center, Repair Client, Submit Logs) → "Logging in..." → loading screen → **the game resumes on the last screen** (the world map, if that is where it was closed), not always home.

**Bottom nav** (y = 1240), on home, Character and World:

| x | Button | Notes |
|---|---|---|
| 80 | Character | Gear slots, stats, Skill, Class, Level, Rank |
| 210 | Travel Journal | Locked: "Unlock any mode to unlock Travel Journal" |
| 360 | Home | The house |
| 500 | Guild | Locked: "Guild unlocks at Character Lv. 15" |
| 640 | World | Island picker |

**Home.** Top bar: avatar and level (top left), Rolla (gold coin), Dawnium (orange gem), stamina (lightning, n/300). The scene scrolls sideways; the Cart (AFK income) sits on the left part with a coin bubble to tap, which gives a `reward_popup` (Rolla, Stone, Wood). Quest tracker panel at (296, 994): tapping it offers to travel to the quest's island (`confirm_dialog`, OK at (490, 735)). Box button at (664, 1006) opens `main_menu`. The chat strip (y ≈ 1040–1150) opens Server Chat if tapped; close it with the arrow at (40, 1226). Never type there.

**Main menu** (`main_menu`): Quest card (200, 958); "Coming soon" card; Photo (100, 1090), Notice (260, 1090), User Center (360, 1090), Settings (480, 1090); server clock bottom right (**server time is UTC-5**). Back arrow (60, 1216).

**Quests** (`quests`): Guidance Quest tab (290, 1216) with a "Go »" button per quest that jumps to the right screen; Achievement tab (560, 1216). Achievement quests refresh Mondays 08:00 UTC-5.

**World** (`world_overview`): islands on a sea map; Originisle at (360, 540). Tapping an island opens its `world_map`.

**Island map** (`world_map`): minimap and coordinates top right; tap the ground to walk; swipe to pan; thick fog blocks walking. Pick-ups (gold piles, plants, chests) are collected by walking onto them. Monsters: tap → `battle_prep` → "Start Battle" (360, 956) → `battle` (auto, "Round n/15") → back to the map, with no result screen seen for an easy win. Quest tracker panel bottom left; its target icon toggles tracking, and a gold ring marks the next target (at the screen edge when off screen; tap it to pan). Back arrow (60, 1216) returns home. Tapping your own character opens the player profile (power, gear, techniques, Dish, Quick Heal); close by tapping outside.

**Character → gear.** Tap a gear slot → item card (Replace / Enhance) → Enhance Gear (costs Raw Ore, Refined Ore, Rolla; "Insufficient materials to enhance." when short). Back arrow (76, 1216).

**Android back key**: did nothing on the player profile popup. Treat it as unreliable and use on-screen back arrows.

## Where screenshots go, and cleanup

| Where | What | Grows? |
|---|---|---|
| `docs/screens/` (committed) | Reference screenshots, ~200 KB each (25 files, ~4.7 MB) | Only when someone runs `capture`; keep it to one shot per screen |
| `captures/` (gitignored) | Exploration frames (`explore/`, newest 40 kept), `record/` (cleared each run), previews, `smoke-failure.png` | Bounded, but clear it anyway |
| `.maa/debug/maafw.log` (gitignored) | MaaFramework's log, ~2 MB per hour of exploring | Yes |
| wherever you point `screenshot OUT` or `state --save DIR` | One frame per call | Only if you ask |

`python -m sxs state`, `watch`, `tap` and the smoke test save nothing (except a frame on smoke-test failure). **At the end of a session, run `python scripts/clean.py`** (use `--dry-run` to see sizes first). It deletes `captures/` and `.maa/debug/`.

## Adding a screen

1. Get to it and run `python scripts/explore.py none` (or `python -m sxs capture NAME`).
2. Find stable text with `python scripts/ocr.py captures/explore/NNN.png [X Y W H]`, or crop a template with `python scripts/crop.py SRC X Y W H resource/image/state/NAME.png`.
3. Add a `State.Name` node to `resource/pipeline/state.json` and put it in `State.Detect`'s order (overlays before full screens).
4. Save a reference with `python -m sxs capture name`, add it to `EXPECTED` in `tests/check_states_offline.py`, and run it.

## Not done yet

- Daily-content screens (shop, dungeons, mail, arena, guild, vendor) are not reachable or not unlocked at Lv 2.
- No `battle_result` screen yet: the one easy fight returned straight to the map.
- Currency icon templates are not cropped yet.
- `title` was reached without a tap once during capture; the smoke test taps "Tap to Play" anyway.
