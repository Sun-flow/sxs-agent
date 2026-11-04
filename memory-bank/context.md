# Context

> **Last updated**: 2026-11-04

## What this is

An automated agent that plays **Sword x Staff** (BOLTRAY GAMES, Play Store id `com.zjcs.android.us`, portrait 720×1280) on an Android emulator on a Windows PC. Deterministic scripts drive the content; a model is called only when a script gets stuck. All combat is auto-battle, so the bot is a menu navigator and decision-maker, not a fighter. mae's project for learning to build automated systems; the account is a test account.

**Iteration 1 is done when** the bot completes the daily content unattended. Later: an "entertainment agent" that narrates to a stream and chats in game, then a fully self-running system. **Not in scope yet**: Linux/headless hosting (Redroid is the noted later path), network-protocol automation, Guild War and other content step 1 defers to iteration 2.

## Plan

1. Emulator choice and game survey: `docs/step1-emulator-and-game.md`. Done.
2. Hands and eyes (device layer, state detector, CLI): `docs/step2-hands-and-eyes.md`. Done.
3. Quest following and exploration: `docs/step3-explore.md`. Done; Roam Loop added later.
4. Dailies loop: `docs/step4-dailies.md`. Done.
5. Upgrades and gathering: `docs/step5-upgrades.md`. Done.
6. Next: a supervisor that calls a model only on a failure or unknown screen and writes the fix back as a pipeline or policy rule; then the entertainment agent reading the same event log.

## Stack

- **Emulator**: MuMu Player 12 on Windows (fallback BlueStacks 5). Machines and ports: `environments.md`. Why: `decisions.md`.
- **Toolkit**: MaaFramework (JSON pipelines, template matching, OCR) with Python custom logic; MaaMCP so Claude can drive the device.
- **Models**: Claude now, a local model later; called only when stuck or planning.
- **Code**: Python 3.12 in a repo-local `.venv`; package `sxs/`, MaaFramework bundle `resource/`, checks in `tests/`.
- **Screen**: all coordinates use the 720×1280 portrait frame.
- **Repo**: https://github.com/Sun-flow/sxs-agent, default branch `main`.

## Commands

Module commands: `sxs/README.md`. Helper scripts: `scripts/README.md`. Repo checks:

```bash
python3 scripts/check-memory.py                         # memory bank drift; lists commits since it was last updated
python3 scripts/check-rules.py                          # every cited R-ID resolves; rule image paths exist
python3 scripts/nav-graph.py check|render|path FROM TO  # menu graph
```

## Where facts live

| Kind of fact | File |
|---|---|
| Never-do rules and their exceptions (spending, pulls, social, class) | `game/rules/policy.md` |
| Game rules by situation (home, overworld, combat, upgrades, ...) and the ID index | `game/rules/README.md` |
| How screens connect, and the taps between them | `game/nav-graph.json` (diagram `game/nav-graph.md`) |
| Card and dialog decisions; gather priorities | `resource/policy/cards.json`, `resource/policy/gather.json` |
| What each step built, its design and limits | `docs/step1-emulator-and-game.md` … `docs/step5-upgrades.md`; index `docs/README.md` |
| Shop stock and mae's Buy? marks | `docs/shop-tables.md` |
| Reference screenshots | `docs/screens/` |
| Modules and their commands | `sxs/README.md` |
| Where the work and the game account stand | `status.md` |
| How a game-playing session works | `playbook.md` |
| mae's preferences and the loop rules | `notes.md` |
| Machines, emulator and tool gotchas | `environments.md` |
| Why a decision was made | `decisions.md` |
| Past sessions | `log.md`, then `docs/archive/memory-bank-log.md` |
| How agents work here | `AGENTS.md` |
