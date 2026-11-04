# Builder playbook

> **Last updated**: 2026-11-04
> How a game-playing ("builder") session works. Read after `status.md`. Where things stand and what's next is in `status.md`; never-do rules are in `game/rules/policy.md`.

## The job

Keep the Sword x Staff test account progressing and turn everything learned into **deterministic code and data, not model calls**: each new screen gets a detector state, each new card or dialog a decision rule, each recurring chore a script. Goal: the bot does the dailies unattended and calls a model only when stuck.

The builder runs as a Remote Control session on mae's PC (machine details: `environments.md`). It talks to mae only through the thread tools and sends rule facts to the coordinator, which forwards them to whoever maintains `game/rules/` and `game/nav-graph.json`.

## Loop

1. **Let the loop play; step in when it stops.** Run the loop (e.g. `python -m sxs explore --chain --minutes N`, `python -m sxs roam`, `python -m sxs daily`) in the background with output to a log. It returns a reason when it can't go on (`unknown_card`, `stuck_progress`, `needs_decision`, `defeated`, `needs_help`, ...).
2. **Look once, fix generally.** Screenshot (`python scripts/probe.py none 0`, view `captures/latest.jpg`), work out what the game wants, add the smallest general fix: a `State.*` node in `resource/pipeline/state.json`, a rule in `resource/policy/cards.json`, a template in `resource/image/`, or a handler in the loop. No one-off taps baked into code; write "given the goal and circumstances, pick the option" functions (`sxs/policy/decide.py`).
3. **Reference screenshot for every new screen**: `python -m sxs capture NAME` writes NAME.png into its folder under `docs/screens/` (by prefix); add its state to `docs/screens/expected.json`; that check must say "all good".
4. **Send rule batches** to the coordinator as you learn: what a screen is for, how to detect it, where to tap (fractions of 720×1280), what an item does, with `docs/screens/...` paths. Don't resend what's already forwarded.
5. **Post short updates** to mae at milestones (area done, blocker, question) with a screenshot when it helps. Post the loop banner whenever a loop starts (format in `notes.md`).
6. **Commit and push often** on your own branch cut from main (`git pull --no-rebase` first). No `gh` on mae's PCs: ask the coordinator to open the PR. PowerShell `Set-Content -Encoding utf8` adds a BOM; edit files with Python or the Edit tool.
7. **Before touching the game after a pause, ask mae whether it's free.**
8. **End of session**: update the memory bank (`README.md` says how), run `python scripts/check-memory.py`, then `python scripts/clean.py`.

## Commands

Module and helper commands: `sxs/README.md` and `scripts/README.md`. The ones used every session:

```bash
.venv\Scripts\python -m sxs state                 # what screen is this (JSON)
.venv\Scripts\python scripts\probe.py none 0    # screenshot -> captures\latest.jpg
.venv\Scripts\python -m sxs daily [--only a,b] [--force]
.venv\Scripts\python tests\check_states_offline.py
```

Filter MaaFramework chatter in logs: `grep -v -i "nemu\|product:\|same day\|^x:\|after convert"`. Run helpers from `scripts/`, not the scratchpad (the auto-mode classifier blocks scratchpad scripts).

## Context resets

When a builder thread gets long: finish the task, send the final rules batch, update `status.md` (state + next steps) and `log.md`, push, and let the coordinator start a fresh builder from this file.
