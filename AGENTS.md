# AGENTS.md — Agent Entry Point

> **For AI coding agents.** Start here every session, whatever tool or environment you run in. `CLAUDE.md` points here; keep instructions in this file only.

## Project: sxs-agent

An automated agent that plays the Android game Sword x Staff (BOLTRAY GAMES) on a PC emulator: deterministic scripts drive the daily content, and a model is called only when a script gets stuck. See `memory-bank/context.md` for the full picture.

## Start of every session

Your memory doesn't carry over between sessions, so this repo keeps it for you in `memory-bank/`.

1. Open `memory-bank/README.md` and follow its start-of-session steps. They tell you what the project is, how to run things, where things stand and what the last session left open.
2. Then read the docs and code your task needs.

## End of every session

Before you finish or hand work back, update the memory bank as `memory-bank/README.md` describes: `status.md`, a new entry at the top of `log.md`, anything learned in `notes.md`, decisions in `memory-bank/decisions.md`. Then run `python3 scripts/check-memory.py` and commit the memory changes with the work. Write things down as you learn them; sessions can end without warning.

## Where things go

| Path | Purpose |
|---|---|
| `README.md` | One-paragraph description of the repo. |
| `docs/` | Design notes, one file per step of the plan. |
| `memory-bank/` | Agent memory: context, status, session log, notes, decisions. |
| `scripts/check-memory.py` | Checks the memory bank and lists commits it hasn't caught up with. |
| `sxs/`, `resource/`, `tests/` | Step 2 hands-and-eyes code, MaaFramework bundle and tests; see `docs/step2-hands-and-eyes.md`. |
| `.agents/prompts/memory-bank.md` | The project-agnostic prompt that builds and maintains `memory-bank/` (copied from mae's TrackFlow-Company-Overhaul repo). |
