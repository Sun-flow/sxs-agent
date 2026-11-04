# Step 2: hands and eyes

_2026-11-03, built and tested on maes2024._

## What it is

- `maafw` (pip) connects to MuMu at `127.0.0.1:16384` over its IPC screenshot path (~7 ms a frame). `SXS_ADB_ADDRESS` overrides the address; with one emulator running and no override, `sxs/core/device.py` uses it.
- **Frames are portrait, 720 wide × 1280 tall**, though MuMu is set to 1280×720. All coordinates in this repo are in that frame.
- **No model calls at runtime.** Screens are recognised by OCR (PaddleOCR v4 via MaaFramework) and templates. A check takes ~0.1–0.8 s, mostly OCR.

## Files

| Path | What |
|---|---|
| `sxs/core/device.py` | `Device`: connect, `screenshot()`, `tap`, `swipe`, `back`, `start_game`, `stop_game`, `foreground_package`; also `server_day()` and `banner()`. |
| `sxs/core/state.py` | `StateDetector.detect()` → `Detection` (state id, node, box, OCR text, timing). |
| `sxs/core/nav.py` | `Navigator.go_home()` (from anywhere, including a cold start), `tap_and_expect()`, common tap points. |
| `sxs/core/replay.py` | `ImageDevice`: feeds saved PNGs to the detector for offline tests. |
| `sxs/cli.py` | `python -m sxs ...` (below). |
| `resource/pipeline/state.json` | One `State.*` node per screen plus `State.Detect` (the order). |
| `resource/image/` | Templates; pipeline image paths are relative to it. |
| `resource/model/ocr/` | OCR models (gitignored, ~12 MB): `scripts/fetch-ocr-models.py`. |
| `docs/screens/` | Reference screenshots, full 720×1280, 256-colour PNG (~200 KB). One per screen. |
| `scripts/probe.py`, `advance.py`, `record.py`, `ocr.py`, `crop.py`, `grid.py` | Hand tools for new screens; output in `captures/` (gitignored). |
| `scripts/clean.py` | Deletes `captures/` and `.maa/debug/` (not `logs/`). `--dry-run` shows sizes. Run at session end. |
| `tests/check_states_offline.py` | Detector vs every reference screenshot (no emulator). |
| `tests/smoke_test.py` | Live: kill, cold-start (~60 s), reach home, visit menu / World / Character and back. Saves `captures/smoke-failure.png` on failure. |

## Setup (Windows)

```bash
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python scripts\fetch-ocr-models.py
.venv\Scripts\python tests\check_states_offline.py
```

MuMu must be running for anything live.

## CLI

```bash
python -m sxs state [--save DIR]      # JSON: state, node, text, elapsed_ms
python -m sxs watch [--interval 2]    # print the state when it changes
python -m sxs screenshot [out.png]
python -m sxs tap X Y
python -m sxs swipe X1 Y1 X2 Y2 [--ms 300]
python -m sxs back                    # Android back; unreliable in-game (R-026)
python -m sxs start | stop
python -m sxs capture NAME            # save docs/screens/NAME.png
```

The MuMu plug-in prints a few lines (`nemu_connect ...`) to stdout first; parse the last line as JSON. `state`, `watch` and `tap` save nothing.

## Detector design

- `State.Detect` lists `State.*` nodes in priority order (`custom_action_param.order`). `detect()` takes one screenshot and the `DetectState` custom action tries each node on it, first hit wins. **Popups and overlays go first**, since they cover other screens.
- State id = node name in snake_case (`State.MainMenu` → `main_menu`); variants share an id (`State.Loading.Title` → `loading`). Game not focused → `not_running`. Nothing matched → `unknown`, which every loop must handle.
- Nodes run one at a time, not as a MaaFramework `next` list: batched `next` OCR misread several screens. `only_rec` OCR is off: 40% faster but broke five screens.
- Prefer OCR of fixed UI text; use a template only where there is no text.

Screen-by-screen recognition and tap points: `resource/pipeline/state.json` and `memory-bank/game/nav-graph.md`. Game behaviour (back key, chat strip, server clock, boot resuming on the last screen): `memory-bank/game/rules/ui.md` and `home.md`.

## Adding a screen

1. Reach it; `python scripts/probe.py none` (or `python -m sxs capture NAME`).
2. Find stable text: `python scripts/ocr.py captures/explore/NNN.png [X Y W H]`, or crop a template: `python scripts/crop.py SRC X Y W H resource/image/state/NAME.png`.
3. Add `State.Name` to `resource/pipeline/state.json` and to `State.Detect`'s order (overlays before full screens).
4. `python -m sxs capture name`, add it to `EXPECTED` in `tests/check_states_offline.py`, run the test.

## Working files

| Where | Grows? |
|---|---|
| `docs/screens/` (committed) | Only via `capture`; keep one shot per screen |
| `captures/` (gitignored): `explore/` (newest 40), `record/` (cleared each run), `unknown/`, previews | Bounded; `clean.py` |
| `.maa/debug/maafw.log` (gitignored) | ~2 MB per hour of exploring; `clean.py` |

## Open

- No `battle_result` screen seen (easy wins return straight to the map).
- Currency icon templates not cropped.
- `title` sometimes appears without a tap; the smoke test taps "Tap to Play" anyway.
