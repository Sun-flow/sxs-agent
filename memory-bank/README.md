# Memory Bank

> **Last updated**: 2026-11-03
> Built from the project-agnostic prompt in `.agents/prompts/memory-bank.md`. That file has the full rules and the reasoning behind them; this one is the short version for this repo.

Agents forget everything between sessions, and the next session may be a different agent or tool in a different environment (a cloud session, or a session on mae's Windows PC). These files carry what would otherwise be lost. They are **memory, not standards**: the binding docs are listed below, and this folder points to them instead of copying them.

## Read at the start of every session

1. Run `python3 scripts/check-memory.py`. Besides checking the bank, it lists any commits that changed the repo after the bank was last updated; skim those so you know which memory might be stale.
2. `context.md`: what the project is, the plan's steps, how to run things, and where each kind of fact lives.
3. `status.md`: what works, what's in progress, what's next, open questions.
4. `log.md`: the top three or so entries, to see what the last sessions did and left open.
5. `notes.md`: before anything that touches mae's preferences or the environment (emulator, PC, network).
6. `decisions.md`: before changing the emulator, toolkit, OS or model strategy.

Then read the docs and code your task needs.

## The files

| File | For | Update when | Budget |
|---|---|---|---|
| `README.md` | This map and the maintenance rules. | A memory file is added, removed or repurposed. | ~120 lines |
| `context.md` | Orientation: purpose, plan, stack, commands, where facts live. | Scope, stack, commands or doc layout change. | ~100 lines |
| `status.md` | Works / In progress / Next / Open questions / Known problems. Each "In progress" item names its branch, PR and environment. | Any session that changes the state of the work. | ~80 lines |
| `log.md` | Session handoffs, newest first. | End of every session that changed something. | ~15 entries, then move the oldest to `docs/archive/memory-bank-log.md` (create it the first time) |
| `notes.md` | mae's preferences, environment and tool gotchas, unwritten conventions. | As soon as you learn something the next session would rediscover. | ~100 lines |
| `decisions.md` | Decisions with lasting consequences, why, and what was rejected. The repo has no other decision log. | A decision is made or superseded. | Newest first; never delete an entry |

## Sources of truth (higher wins)

1. The code, as it is now.
2. The design notes in `docs/` (step 1: emulator choice and the daily-content catalogue).
3. `decisions.md` in this folder: why each decision was made.
4. The rest of this folder.
5. Anything in an archive: history only, never instructions.

If something here disagrees with a higher source, fix this folder in the same session.

## How to maintain it

At the end of a session (or before handing work back):

1. Update `status.md`, add a `log.md` entry, and add anything learned to `notes.md`.
2. Log decisions in `decisions.md`; update `context.md` if the stack, commands or doc layout changed.
3. Run `python3 scripts/check-memory.py` and fix what it reports. Commit the memory changes in the same commit as the work, so the check can tell when memory falls behind.

Rules that keep it useful:

- **Point, don't copy.** Name the file and section that holds a fact. Use paths and headings, never line numbers.
- **Verify before writing.** Mark anything you couldn't check with ❓ and say what would confirm it.
- **Write the why**, date what changes, and stay inside the budgets.
- **Procedures are scripts.** If doing something takes more than one step (starting the emulator, pulling the APK, running the daily loop), it lives in `scripts/` and the memory names the command.
- **No secrets** or private details (no account credentials, no game login). Don't repeat what git already records; link the commit or PR.

When mae says "update the memory bank", reconcile every file against the repo, not just the latest change.
