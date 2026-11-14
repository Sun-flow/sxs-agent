# Memory Bank: Generation and Maintenance Prompt (v2, draft)

> **What this is**: a project-agnostic prompt for any AI coding agent. Point an agent at it to **create** a memory
> bank in a repo, to **reconcile** one that has drifted, or as the standing rules for **maintaining** one. To use it
> in a new repo, copy this file to `.agents/prompts/memory-bank.md` and `bank.py` to `scripts/bank.py`, then tell the
> agent: "Read `.agents/prompts/memory-bank.md` and set up a memory bank for this repo." Both files work unchanged;
> everything project-specific goes in the bank itself (and, if needed, `memory-bank/bank.json`).
>
> **What changed from v1**: v1 assumed one agent working at a time. v2 assumes several sessions may work on the
> same repo at once, on separate branches merged in any order, and that some memory lives outside the repo (an
> agent platform's own notes). Measured in a repo that ran that way, about half of all merges hit conflicts, almost
> all of them in shared memory files; status went stale on the default branch; ID counters collided; and a merged
> PR's code never reached the default branch without anything noticing. Every v2 rule below answers one of those.

---

## Why a memory bank exists

Your memory resets between sessions, and the next session may be a different agent, model or tool, in a different
environment, with no chat history. The memory bank is a small folder of Markdown files that carries what you'd
otherwise lose: what the project is, what works, what was just done, and what the people you work with expect. It
is written so the next session can orient itself in a couple of minutes without asking questions already answered.

It is **memory, not a standard**. The repo's own docs (a spec, a decision log, a README, the code) are the sources
of truth. The bank points to them and never copies their content.

## Order of truth

When two sources disagree, the higher one wins. Fix the lower one in the same session.

1. The code, tests and manifests, as they are now.
2. The repo's binding docs: spec, decision log, README (whatever the repo actually has).
3. The memory bank.
4. Memory kept outside the repo (an agent platform's notes): it wins only for **live state** (below).
5. Anything in an archive. That is history, not instructions.

---

## Two design rules that shape everything else

**1. A file that every session edits is a merge conflict waiting to happen.** So the bank has two kinds of file:

- **Singletons**, edited rarely: `README.md`, `context.md`, `notes.md`, `status.md`. Most sessions don't touch them.
- **Entry folders**, one file per entry, never edited by two sessions: `log/`, `decisions/`, `work/`, and any list
  that grows (`stuck/`, `questions/`, `inbox/`). Their indexes are printed by `scripts/bank.py`, never committed.

**2. Live state is not memory.** Who is running what right now, which machine is busy, what waits on a person, and
runtime readings (scores, levels, counts, account state) change hourly. Git lands them only when a branch merges,
so on the default branch they are always stale, and every branch edits them, so they always conflict. Keep live
state where it updates live: the agent platform's own notes, an issue, a dashboard, or a report the program prints
from its own logs. The bank keeps a pointer to it, not a copy.

The test: **if a value would change during a normal day's work, it doesn't go in a committed file that every branch
edits.**

---

## The file set

Create `memory-bank/` at the repo root:

| Path | Holds | Changes | Budget |
|---|---|---|---|
| `README.md` | The map of files and folders (what each is for, when to read it, when to update it), the sources of truth, **which store owns which kind of fact** (including memory outside the repo), and the maintenance rules. | When a file or folder is added or repurposed. | 120 lines, 8 KB |
| `context.md` | What the project is and isn't, who it's for, the stack and exact commands, the architecture in a few lines, and where each kind of fact lives. | When scope, stack, commands or layout change. | 100 lines, 6 KB |
| `status.md` | **Durable state only**: Works / Next (in order) / Known defects. Every bullet ends with a `(YYYY-MM-DD)` date. No live state. | At milestones. Most sessions don't touch it. | 60 lines, 6 KB |
| `notes.md` | The people's working preferences, environment and tool gotchas, conventions the code relies on that aren't written elsewhere. | When learned. | 100 lines, 8 KB |
| `log/` | One file per session, `YYYY-MM-DD-HHMM-slug.md`: where it ran, what changed (PR or commit), what's open. | Every session that changed something. | 15 lines each |
| `decisions/` | One file per decision: decision, why, what was rejected, status. Use the repo's ADR folder instead if it has one. | When a decision is made or superseded. | Never delete; supersede |
| `work/` | One file per branch in progress: title, `Branch:`, PR, where it runs, notes. Only its own branch edits it. | Created when work starts; deleted in the PR that finishes it. | 20 lines |
| `stuck/` | One file per recurring problem, with `seen: N`, first/last dates, status, owner. | A session that hits it bumps the count (`bank.py seen stuck SLUG`). | 25 lines |
| `questions/` | One file per question waiting on a person. | Deleted in the PR that acts on the answer. | 15 lines |
| `inbox/` | One file per rule or preference a person stated, in their words, not yet filed in its proper place. | Written the turn it's said; deleted when filed. | 15 lines |
| `retired.txt` | Terms that must no longer appear: scrapped features, removed modules, retired IDs. One per line. | When something is retired. | — |

Create entry folders when first needed, not up front. Add other singletons only when a real need appears, add them
to the map and to `bank.json`'s `singletons`, and give them budgets.

Budgets are **lines and bytes**, and no line may exceed 300 characters. A paragraph written on one line is still a
paragraph; byte budgets stop a file from meeting a line budget by packing.

**Never keep a rolling log with an archive.** Moving the oldest entry out makes every session edit two shared files.
With one file per entry there is nothing to roll over.

**Adopt, don't duplicate.** If the repo already has a file doing one of these jobs (a status doc, a changelog, an
ADR folder), move it into the bank or point to it from the map. Never keep two.

---

## Working in parallel

These rules apply from the first commit, even if only one session works on the repo today.

- **Indexes are printed, not edited.** Each doc carries its own index line under its title:
  `<!-- index: when to read this -->`. `python3 scripts/bank.py index docs` prints the table. Adding a file never
  means adding a row to a shared README table. Apply the same pattern to any folder whose README lists its files
  (scripts, modules, tests): the listing comes from metadata inside each file.
- **No shared counters.** Never store "next free ID" anywhere: not in a README, not in outside memory. On a branch,
  a new numbered item gets a provisional ID (`R-new-portal-teleport`) that code and docs may cite. After merging,
  on the default branch, `python3 scripts/bank.py ids --assign` numbers every provisional ID and rewrites its
  citations; the check fails on the default branch while any remain. The same applies to any numbered list several
  branches extend (class IDs, error codes, migrations): key by name on branches, number on the default branch.
- **Confirm work landed.** A PR targets the default branch. If you stack a branch on another, retarget its PR the
  moment the base merges. The check lists PRs merged into a branch other than the default (their code is not on the
  default branch yet) and merged branches that gained more commits afterwards. Work is done when its commits are on
  the default branch, not when its PR says merged.
- **Capture rules the turn they're stated.** When a person states a rule, a preference or a correction, write it
  that turn as an `inbox/` file on your branch, in their words. Don't leave it only in chat or in outside memory: the
  sessions that write code read the repo, not the chat.
- **Ledgers count, they don't grow.** A recurring problem is one `stuck/` file whose count goes up, not another
  bullet. `bank.py index stuck` prints them by count; the top of that list is the priority. "Seen twice" means it
  is a defect to fix, not a case to work around.
- **Only your own files.** A session edits its own `work/` file and entries it created. It corrects another
  session's entry only to fix a mistake, never to add news: news is a new entry.

---

## Memory outside the repo

Agent platforms often keep their own notes (a coordinator's memory, a project memory, a team wiki). Decide in
`memory-bank/README.md` which store owns which kind of fact, and write it down as a table:

| Kind of fact | Owner | Others |
|---|---|---|
| Rules, preferences, how to run, durable status, decisions, ledgers | the repo | point by ID or path |
| Live coordination: who runs what, which machine is busy, who waits on whom | outside memory | the repo doesn't hold it |
| Deliverables for people (reports, exports) | wherever people read them | the repo links them |

Outside memory names rule IDs and files; it never restates a rule. When it learns a durable fact, the fact goes to
the repo (an `inbox/` file is enough) the same turn.

---

## Entry point

Every agent tool reads a different file first. Make them all lead to the same place:

- `AGENTS.md` at the root is the entry point. Near the top: run `python3 scripts/bank.py`, then read
  `memory-bank/README.md` and what it lists, before doing anything else; and at the end of the session, update the
  bank as the README describes.
- `CLAUDE.md` holds one line, `@AGENTS.md`, so Claude Code loads the same instructions.
- Add a one-line pointer for any other tool the people use: `.github/copilot-instructions.md`, `.cursor/rules/`,
  `.clinerules`. Ask which tools they use rather than guessing. Keep the instructions themselves in `AGENTS.md`.

---

## Session protocol

**Start**: `git fetch`, then run `python3 scripts/bank.py`. It prints, in order: problems to fix, work that didn't
land, dated items older than 7 days to re-verify or close, merged PRs no log entry mentions, and the newest three log
entries. Then read `context.md` and `status.md`, and only what your task needs. Read `notes.md` before anything
touching the people's preferences or the environment. If anything contradicts the code, the code wins: fix the
bank in this session.

**During**: write things down the turn you learn them. A stated rule goes to `inbox/`; a decision to `decisions/`
(`bank.py new decisions "Title"`); a problem you hit for the second time gets `bank.py seen stuck SLUG` or a new
`stuck/` file. Sessions end without warning.

**End** (or before you hand work back):

1. Add your log entry: `python3 scripts/bank.py new log "Title (who, where)"`, then fill it in.
2. Update your `work/` file, or delete it if the work merged or was dropped.
3. Edit `status.md` only if a milestone changed. Never put live state there.
4. If you changed the stack, commands or layout, update `context.md`.
5. **Reconcile, don't just append**: close or re-date any item the check listed as old that your session can
   verify. An item nobody can verify gets ❓ and a line saying what would confirm it.
6. Run `python3 scripts/bank.py check` and commit memory changes with the work they describe.

When someone says "update the memory bank", reconcile every file against the repo, not just the latest diff.

---

## Writing rules

1. **Point, don't copy.** Name the file and section that holds a fact instead of restating it. Copies drift.
2. **Paths and sections, never line numbers.**
3. **Verify before you write.** Every claim comes from a file, a command's output or git history. Mark what you
   couldn't check with ❓ and say what would confirm it.
4. **Write the why.** A decision without its reason gets undone. Say what was tried and rejected.
5. **Date what changes.** Status bullets and ledger entries carry `YYYY-MM-DD`; undated items can't be found stale.
6. **Budgets are bytes and lines; lines stay under 300 characters.** When a file outgrows its budget, cut what's
   stale or split the detail into entry files.
7. **Don't store what git already has.** Link commits and PRs; don't repeat diffs.
8. **Procedures are scripts.** If doing something takes more than one step, commit a script and let memory name
   the command. A remembered procedure gets rebuilt slightly differently each time.
9. **Rules point to code.** A rule or procedure says which code implements it, or `code: none`. The `code: none`
   list is the honest list of what still needs a person, and the backlog for turning manual steps into code.
10. **Retire, then flag.** When something is scrapped, add its name to `retired.txt` and move its docs to the
    archive with a pointer to the replacement. The check flags every remaining mention.
11. **Never store secrets**, tokens, personal contact details or anything private you wouldn't put in the repo.
12. **Write for a stranger.** Plain sentences, full paths, no "as discussed".

---

## Init workflow ("set up a memory bank")

1. **Survey** the repo: tree, manifests, CI, existing docs, the README, the last ~30 commits, open PRs and branches.
2. **Find the sources of truth** that already exist; decide what the bank adopts and what it points to. Ask whether
   the people's agent platform keeps memory outside the repo, and fill in the ownership table.
3. **Create** `memory-bank/` with the four singletons and `log/`, filled only from what you verified. Use ❓ for the
   rest. Create the other entry folders when first needed.
4. **Wire** `AGENTS.md`, `CLAUDE.md` and any other tool pointers.
5. **Add the tool.** Copy `bank.py` to `scripts/bank.py` (Python 3.8+, standard library only). If the repo's layout
   needs it, add `memory-bank/bank.json` (budgets, extra singletons, path bases, ID prefixes, the default branch).
   Run `python3 scripts/bank.py` and fix what it reports. If the repo has CI or a test runner, run
   `python3 scripts/bank.py check --quiet` there.
6. **Convert shared tables.** Any README that lists files by hand gets replaced by a printed index (the
   `<!-- index: -->` line, or a docstring field read by a small script). Any stored "next ID" goes away.
7. **Read it cold.** Have a fresh session (or a subagent with no context) read only the entry point and the bank,
   and ask: what is this project, what works, what's next, how do I run it, and what is in progress right now and
   where would I see it? Fix whatever it gets wrong.

## Migrating a v1 bank

1. Split `log.md` and its archive into `log/` files (one per entry, named by date); split `decisions.md` likewise.
2. Move status's "In progress" items to `work/` files and its live sections (who runs what, account readings,
   waiting on people) out of git, leaving a pointer.
3. Move status's long lists (open problems, untested items, questions) to `stuck/` and `questions/` files.
4. Replace hand-edited index tables and "next free" lines as in init step 6.
5. Run the check; long lines and stale items it lists are the reconciliation to do.

## Definition of done

- [ ] The singletons exist, each with a `Last updated` date, inside their line and byte budgets.
- [ ] No file in the bank is one that every session must edit; `status.md` holds milestones only, every bullet dated.
- [ ] No "next free" counter is stored anywhere; provisional IDs are numbered by the tool.
- [ ] Every index is printed from metadata in the files; no README table lists files by hand.
- [ ] The README names the owner of each kind of fact, including stores outside the repo.
- [ ] `AGENTS.md` sends agents to `scripts/bank.py` and the bank first; `CLAUDE.md` points to `AGENTS.md`.
- [ ] `python3 scripts/bank.py check` passes.
- [ ] A cold read answers: what this is, what works, what's next, how to run it, where live state is.
