# Memory Bank

> Built from the project-agnostic prompt in `.agents/prompts/memory-bank.md`. That file has the full rules and the reasoning behind them; this one is the short version for this repo.

Agents forget everything between sessions, and the next session may be a different agent or tool in a different environment (a cloud session, or a session on mae's Windows PC). These files carry what would otherwise be lost. They are **memory, not standards**: the binding docs are listed below, and this folder points to them instead of copying them.

## Read at the start of every session

1. Run `python3 scripts/check-memory.py`. It also lists commits that changed the repo after the bank was last updated; skim them so you know which memory might be stale.
2. `context.md`: what the project is, the plan, the stack, and where each kind of fact lives.
3. `status.md`: game state, what works, what's next, what waits on mae; `python3 scripts/index.py work` for the
   workstreams in progress.
4. `python3 scripts/entries.py log`: the newest three session entries.
5. Then only what your task needs: `playbook.md` if you play the game; `game/rules/README.md` to find the rules for your situation (always `game/rules/policy.md` before pressing anything that might spend or is social); `notes.md` before anything touching mae's preferences or loop design; `environments.md` before touching a PC, the emulator or the network; `python3 scripts/entries.py decisions --titles` before changing the emulator, toolkit, OS or model strategy.

## The files

| File | For | Update when | Budget |
|---|---|---|---|
| `README.md` | This map and the maintenance rules. | A memory file is added, removed or repurposed. | ~120 lines |
| `context.md` | Orientation: purpose, plan, stack, where facts live. | Scope, stack or doc layout change. | ~100 lines |
| `status.md` | Game state, Works / Next / Waiting on mae / Known problems, live run notes. In progress lives in `work/`. | Any session that changes the state of the work or the account. | ~80 lines |
| `log/` | Session handoffs, one file per entry (`log/README.md`); read with `python3 scripts/entries.py log`. Older history: `docs/archive/memory-bank-log.md`. | End of every session that changed something: `python3 scripts/entries.py new log "Title"`. | None: one file each |
| `work/` | Workstreams in progress, one file per branch or thread, named by the branch slug (title, then `Branch: ... · PR: ... · Where: ...`, then notes); list with `python3 scripts/index.py work`. | Create it when work starts; only its own thread edits it; delete it in the PR that finishes or drops the work. | ~20 lines each |
| `playbook.md` | How a game-playing (builder) session works: the loop, commands, context resets. | The process changes. | ~60 lines |
| `notes.md` | mae's preferences and the rules every loop follows. | As soon as mae states a preference or working rule. | ~100 lines |
| `environments.md` | Machines (current game PC, retired ones, cloud), emulator and toolkit gotchas. | A machine, port or tool quirk changes. | ~60 lines |
| `game/` | Game knowledge: rules by topic (`game/rules/`, situation table in `game/rules/README.md`, ID index from `python3 scripts/index.py rules`) and the menu graph (`game/nav-graph.json`). Its own README explains the formats. | A session learns a rule or a route. | Rules checked by `scripts/check-rules.py`; graph by `scripts/nav-graph.py` |
| `decisions/` | Decisions with lasting consequences, why, and what was rejected; one file per decision (`decisions/README.md`). | A decision is made (`python3 scripts/entries.py new decisions "Title"`) or superseded (edit its Status line). | Never delete an entry |

## Sources of truth (higher wins)

1. The code, as it is now.
2. The design notes in `docs/` (steps 1 to 5) and the policy files in `resource/policy/`.
3. `decisions/` in this folder: why each decision was made.
4. The rest of this folder.
5. Anything in an archive: history only, never instructions.

If something here disagrees with a higher source, fix this folder in the same session.

## How to maintain it

At the end of a session (or before handing work back):

1. Update `status.md` and your own `work/` file (delete it if the work merged or was dropped), add a log entry
   (`python3 scripts/entries.py new log "Title (who, where)"`), and add anything learned to `notes.md`.
2. Add decisions with `python3 scripts/entries.py new decisions "Title"`; update `context.md` if the stack, commands or doc layout changed.
3. Run `python3 scripts/check-memory.py` and fix what it reports. Commit the memory changes in the same commit as the work, so the check can tell when memory falls behind.

Rules that keep it useful:

- **Point, don't copy.** Name the file and section that holds a fact. Use paths and headings, never line numbers.
- **Verify before writing.** Mark anything you couldn't check with ❓ and say what would confirm it.
- **Write the why**, date what changes, and stay inside the budgets.
- **Procedures are scripts.** If doing something takes more than one step (starting the emulator, pulling the APK, running the daily loop), it lives in `scripts/` and the memory names the command.
- **No secrets** or private details (no account credentials, no game login). Don't repeat what git already records; link the commit or PR.

## Merge-proof by design

Many branches write memory at once, and mae merges them in any order. Shared lines conflict; separate files don't.

- **Anything appended per session is its own file**: a log entry, a decision, a workstream. Never append to a
  shared list for these.
- **Indexes are built, never edited.** The docs list, the tests list and the rule ID index come from metadata in
  each file (`python3 scripts/index.py docs|tests|rules|work`). Adding a doc, test or rule means giving the new file
  its metadata line, not adding a table row. No generated index is committed, so there is nothing to regenerate
  after a merge.
- **New rule IDs** come from `python3 scripts/check-rules.py --next` after `git fetch`; if two branches still take
  the same ID, `scripts/check-rules.py` fails on main and the second branch renumbers.
- This repo departs from `.agents/prompts/memory-bank.md` here: that prompt describes a single log file and a
  single decisions file.

When mae says "update the memory bank", reconcile every file against the repo, not just the latest change.
