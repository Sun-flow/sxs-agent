# AGENTS.md — Agent Entry Point

> **For AI coding agents.** Start here every session, whatever tool or environment you run in. `CLAUDE.md` points here; keep instructions in this file only.

## Project: sxs-agent

An automated agent that plays the Android game Sword x Staff (BOLTRAY GAMES) on a PC emulator: deterministic scripts drive the daily content, and a model is called only when a script gets stuck. See `memory-bank/context.md` for the full picture.

## Start of every session

Your memory doesn't carry over between sessions, so this repo keeps it for you in `memory-bank/`.

1. Run `python3 scripts/check-memory.py`; skim the commits it lists.
2. Open `memory-bank/README.md` and follow its start-of-session steps (status, recent log, and the rest on demand).
3. Then use the map below to read only what your task needs. Every folder has a README index: read the index, then the one file it points to.

## Map: read top-down, stop when you have what you need

| Need | Index | Leaves |
|---|---|---|
| Where the work stands, what's next | `memory-bank/README.md` | `status.md`, top of `log.md` |
| mae's preferences, environments, decisions | `memory-bank/README.md` | the bank file it names |
| Game facts: rules of the world, menus, routes | `memory-bank/game/README.md` | one topic file of the rules; `memory-bank/game/nav-graph.json` |
| Running or changing the bot (modules, commands) | `sxs/README.md` | one module |
| Screens the bot can detect, templates, policies | `resource/README.md` | `resource/pipeline/state.json`, the policy files |
| Why a step is designed the way it is | `docs/README.md` | one `docs/stepN-*.md` |
| Helper scripts and checks | `scripts/README.md` | one script |
| Tests and what each needs | `tests/README.md` | one test |

## End of every session

Before you finish or hand work back, update the memory bank as `memory-bank/README.md` describes: `status.md`, a new entry at the top of `log.md`, anything learned in `notes.md`, decisions in `memory-bank/decisions.md`. Then run `python3 scripts/check-memory.py` and `python3 tests/check_repo.py`, and commit the memory changes with the work. Write things down as you learn them; sessions can end without warning.

## Where things go

| Path | Purpose |
|---|---|
| `README.md` | One-paragraph description of the repo. |
| `sxs/` | The bot: device layer, state detector, loops (`python -m sxs.<loop>`). |
| `resource/` | MaaFramework bundle: pipelines, templates, OCR models, decision policies. |
| `tests/` | Offline checks and the live smoke test. |
| `scripts/` | Dev helpers and repo checks. |
| `docs/` | Design notes (one per plan step), shop tables, reference screenshots in `docs/screens/`. |
| `memory-bank/` | Agent memory: context, status, log, notes, decisions; `game/` holds game knowledge. |
| `.agents/prompts/memory-bank.md` | The project-agnostic prompt that builds and maintains `memory-bank/` (copied from mae's TrackFlow-Company-Overhaul repo). |
| captures/, logs/, .maa/ | Runtime output, gitignored. `scripts/clean.py` empties captures/. |

New file? Put it in the folder above that fits and add a line to that folder's README. A new top-level folder needs a row here.
