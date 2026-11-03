# Context

> **Last updated**: 2026-11-03

## What this is

An automated agent that plays **Sword x Staff** (BOLTRAY GAMES, Play Store id `com.zjcs.android.us`) on an Android emulator on a Windows PC. It should complete missions, dailies and collaborative (guild, co-op) content without guidance and without spending model credits on every step. It is mae's project for learning to build automated systems; the game account is a test account.

All combat in the game is auto-battle, so the bot is mostly a menu navigator and decision-maker, not a fighter.

**Iteration 1 is done when** the bot completes the daily content unattended. Later goals: an "entertainment agent" that narrates what the bot does to a stream or audience and chats with other players in game, and eventually a fully self-running system.

**Not in scope yet**: Linux or headless hosting (Redroid is the noted later path), network-protocol automation (vision first), Guild War and other content the step 1 doc defers to iteration 2.

## Plan

1. Choose the emulator and survey the game. Done: `docs/step1-emulator-and-game.md` (PR #1).
2. Hands-and-eyes layer: MaaFramework over MuMu Player 12, state detector, CLI, smoke test. `docs/step2-hands-and-eyes.md` (branch `step2-hands-and-eyes`).
3. Script the daily loop, with a supervisor that calls a model only on a failure or unknown screen and writes the fix back as a new or patched pipeline.
4. Later: the entertainment agent, reading the same event log.

## Stack

- **Emulator**: MuMu Player 12 on Windows, one instance per account at 1280×720, 240 dpi. Fallback BlueStacks 5. Why: `decisions.md`.
- **Automation toolkit**: MaaFramework (JSON pipelines plus Python custom logic, template matching and OCR), with MaaMCP so Claude can drive the device and save what it did as a pipeline.
- **Models**: Claude to start, a local model later. Called only when stuck or planning.
- **Language**: Python 3.12 in a repo-local `.venv`; package `sxs/`, MaaFramework bundle `resource/`.
- **Screen**: the game is portrait, frames are 720 wide × 1280 tall; all coordinates use that frame.
- **Machines**: maes2024, mae's Windows PC that runs the emulator, project folder `C:\Users\jcmon\Desktop\sxs-player`. Cloud Claude Code sessions edit the repo; device work happens on maes2024.

## Commands

```bash
python3 scripts/check-memory.py   # check the memory bank; lists commits since it was last updated
python3 scripts/nav-graph.py check|render|path FROM TO   # menu graph: validate, regenerate the diagram, find a route
```

Setup, CLI and how to add a screen: `docs/step2-hands-and-eyes.md`. Run from the repo root on maes2024 (Windows paths):

```bash
.venv\Scripts\python -m sxs state               # where is the game right now (JSON)
.venv\Scripts\python tests\check_states_offline.py   # detector vs docs/screens, no emulator
.venv\Scripts\python tests\smoke_test.py           # live: cold start -> home -> menus -> home
```

## Repo facts

- Default branch `main`; pull requests target it.
- Remote: https://github.com/Sun-flow/sxs-agent

## Where facts live

| Kind of fact | File |
|---|---|
| Emulator comparison, architecture, game notes, daily-content catalogue, iteration 1 scope | `docs/step1-emulator-and-game.md` |
| Device layer, state detector, screen catalogue with tap coordinates | `docs/step2-hands-and-eyes.md` |
| Reference screenshots | `docs/screens/` |
| Rules of the world (currencies, quests, exploration, unlocks) | `memory-bank/game/rules.md` |
| How screens connect, and the taps between them | `memory-bank/game/nav-graph.json` (diagram in `memory-bank/game/nav-graph.md`) |
| Why a decision was made, and what was rejected | `memory-bank/decisions.md` |
| Where the work stands | `memory-bank/status.md` |
| mae's preferences, environment gotchas | `memory-bank/notes.md` |
| How agents should work here | `AGENTS.md` (entry point; `CLAUDE.md` points to it) |
| How to build or rebuild this memory bank | `.agents/prompts/memory-bank.md` |
