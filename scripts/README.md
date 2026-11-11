# scripts: helpers and checks

Run from the repo root (`.venv\Scripts\python scripts\X.py` on Windows, `python3 scripts/X.py` in the cloud). Output goes to `captures/` (gitignored).

## Checks (run before committing)

| Script | Does |
|---|---|
| `check-memory.py` | Memory-bank drift: broken paths, unmapped files, dates, budgets; lists commits since the bank was updated |
| `check-rules.py` | Every cited R-ID resolves to a live rule; image paths in rules exist |
| `nav-graph.py check\|render\|path FROM TO` | Validate, re-render or query `memory-bank/game/nav-graph.json` |
| `../tests/check_repo.py` | Repo structure: pipelines, templates, policies, module references in docs (no emulator, no MaaFramework) |

## Device helpers (need the emulator)

| Script | Does |
|---|---|
| `probe.py none 0` / `tap X Y 3` / `swipe ...` / `back` | One action, wait, save `captures/explore/NNN.png` + `captures/latest.jpg` (half size) |
| `drag.py X1 Y1 X2 Y2 [MS] [WAIT]` | Slow drag (default 1000 ms; Home only pans on slow drags, R-126), then save a frame like probe.py |
| `advance.py [MAX_TAPS]` | Tap through dialogue and reward popups, then save the frame |
| `record.py` | Save a frame every N seconds (short-lived screens) |
| `shop_survey.py NAME [rows]` | Read a shop's item cards without buying (taps icons, never prices) |

## Image helpers (offline)

| Script | Does |
|---|---|
| `ocr.py IMG [X Y W H]` | Every OCR result MaaFramework finds in a region |
| `crop.py SRC X Y W H OUT` | Crop a template |
| `grid.py FOLDER i j ...` | Tile frames from a `captures/` subfolder into `captures/grid.jpg` |

## Setup and housekeeping

| Script | Does |
|---|---|
| `fetch-ocr-models.py` | Download the OCR models into `resource/model/ocr/` (once per clone) |
| `clean.py [--dry-run]` | Delete `captures/` and `.maa/debug/` (not `logs/`) at the end of a session |
| `tap_trace.py` | Run Clear Zone or roam with every tap logged (point, calling line) and the frame saved to `captures/taps/`; for finding which tap causes a stuck point |
