# Memory bank retrospective (2026-11-12)

<!-- index: What the memory bank prompt got wrong for a repo with many parallel threads, measured from git history, the fixes proposed in priority order, and a revised prompt for the next repo -->

mae asked (2026-11-12): using what happened in this repo, how would we improve the memory bank generator
(`.agents/prompts/memory-bank.md` plus `scripts/check-memory.py`), how would we change the prompt so a new repo gets
the improvements from day one, and where were the consistent stress points and gaps in how the bank was used?

Evidence is from `main` at `3fee45d` (after #61) and the open PR #70 branch. Commands used are listed at the end so
the numbers can be re-run. `entries.py` and `index.py` below are the `scripts/` helpers #70 adds; `landed.py` is
proposed here and doesn't exist yet. This doc changes no memory files on purpose (it would conflict with #70); the
decisions it leads to get their own entries once mae picks.

## The short version

The prompt was written for **one agent working serially**: one session reads the bank, works, updates five files,
hands off. This repo ran **many threads at once on one repo**, each on its own branch, merged by mae in any order,
with a coordinator holding its own memory outside git. Almost every problem below follows from that mismatch.

1. **Shared, hand-edited files are where merges break.** Of the last 80 merge commits, 38 had files changed on both
   sides. The top three were all memory files: `memory-bank/log.md` (31), `memory-bank/status.md` (26),
   `docs/archive/memory-bank-log.md` (25). The most-conflicted *code* file appeared 4 times. PR #70 fixes the log,
   decisions and in-progress list; the rest of the pattern (status, counters, README tables) is still open.
2. **Live state doesn't belong in git.** `status.md` mixes durable facts with hourly state (who is running what,
   the game account's level, what waits on mae). Git only lands it when a PR merges, so on `main` it is always
   behind, and every branch edits it, so it always conflicts. The coordinator ended up keeping a second, fresher
   status in project memory.
3. **Shared counters collide.** Rule IDs (`next free: R-175` is a hand-edited line in `game/rules/README.md`) and
   detector class IDs (#67 and #69 both took class 44) are the same bug: two branches read the same "next" number.
4. **The checks are structural, not semantic.** `check-memory.py` passes today on a `status.md` that is 80 lines
   but 17.7 KB, with a 1,953-character line, a "Game state (2026-11-05)" heading over 2026-11-11 facts, and items
   from 2026-11-04 that are stale. Nothing checked that a PR's code reached `main` (#62).
5. **The bank was written much more than it was read or reconciled.** 205 of 504 commits touch `log.md`, 101 touch
   `status.md`, but open items accumulate instead of being closed, and new rules from mae lived in chat and project
   memory for hours before reaching the repo.

The proposals, in priority order, are in [Proposals](#proposals). The revised prompt is in
[A revised prompt for the next repo](#a-revised-prompt-for-the-next-repo).

---

## Findings

### F1. Merge conflicts came almost entirely from memory and index files

Files changed on both sides of a merge, over the last 80 merge commits (`git log --merges`, merge-base diff):

| File | Merges where both sides changed it |
|---|---|
| `memory-bank/log.md` | 31 |
| `memory-bank/status.md` | 26 |
| `docs/archive/memory-bank-log.md` | 25 |
| `docs/README.md` | 7 |
| `sxs/README.md` | 6 |
| `scripts/README.md` | 5 |
| `fogwalk.py` in `sxs/loops/` (top code file, since removed) | 4 |
| `memory-bank/decisions.md`, `memory-bank/game/rules/overworld.md` | 4 each |
| `memory-bank/game/rules/README.md`, `resource/items/items.json`, `memory-bank/notes.md` | 3 each |

Notes:

- The log archive conflicted almost as often as the log itself. The prompt's rule "keep ~15 entries, move the oldest
  to an archive" means **every** session edits two shared files, and two sessions always move the same oldest entry.
- There are 133 merge commits for about 66 PRs; 80 of them are not "Merge pull request" but syncs ("Merge main
  (#66) into the big-map branch", "Merge npg43i into the strengthen build"). Threads spent a merge commit per PR,
  on average, just keeping memory files in step. Recorded conflict notes show the same thing:
  `# Conflicts: docs/archive/memory-bank-log.md, memory-bank/log.md` on #45 and #47; "memory-bank/log.md (both
  entries kept, oldest moved to the archive)" on #55.
- `fogwalk.py` is the only code file near the top, which says code ownership by thread worked; shared prose did not.

PR #70 (proposals 1 and 2) moves log, decisions and in-progress work to one file per entry and prints the docs,
tests and rules indexes from file metadata. That removes rows 1, 3, 4 and most of row 7. Still shared and
hand-edited after #70: `status.md`, `sxs/README.md`, `scripts/README.md`, `notes.md`, the rule topic files, the
rules README's situation table, `resource/items/items.json`, and `resource/detect/classes.json`.

### F2. status.md is a live dashboard stored in git

What `memory-bank/status.md` on `main` holds today:

- 80 lines (inside the 80-line budget) but **17.7 KB**: the longest line is 1,953 characters. The line budget is
  met by writing paragraphs on one line. The same is true of `decisions.md` (19 KB, no budget) and `log.md`
  (20 KB for 15 entries).
- `## Game state (2026-11-05 05:05Z, mae's PC)` heading, with bullets from 2026-11-11 under it, and an "(older)"
  bullet saying Lv 30 next to the newer Lv 37.
- `## Works (all on main, PRs #1–#30)` while main is at #66.
- "In progress" still lists a branch marked "(merged)" and branches with "no PR yet" whose PRs have merged.
- "Next" item 2 is "Fog Walk pickup detection", and a Known problem is "the fog walk's zone check", both written
  2026-11-04; the Fog Walk was scrapped 2026-11-10 (`docs/fogwalk-postmortem.md`).
- Known problems added 2026-11-04 and still there: "Untested live: Conquest with tries left ...", "Docs say every
  loop logs a heartbeat; only `sxs/loops/explore.py` does", "Minimap classifier was tuned in Verdantglade II".

Meanwhile the coordinator's project memory has a `STATE` block, timestamped to the minute, with the emulator owner,
each thread's PR and what waits on mae. That is the status people actually used. The repo copy lags because it only
reaches `main` when a PR merges, and every thread that changes anything edits it.

**Root cause:** status mixes three kinds of fact with different lifetimes:

| Kind | Example | Changes | Where it should live |
|---|---|---|---|
| Live coordination | who has the emulator, which thread runs what, waiting on mae | hourly | outside git (project memory or a live page) |
| Runtime readings | account level, power, stamina, zones blessed | every run | generated from the bot's own logs (`python -m sxs report`) |
| Durable state | what works, what is planned, known defects | at milestones | git, one file per item |

### F3. Shared counters

- `game/rules/README.md` carries `New rule: next free ID (**next free: R-175**)`, a line every rule-adding branch
  edits. Project memory carried the same counter separately and went stale: the stamina-loop memory says "next free
  R-175+" while the portals PR (#69) had already taken R-175; an older memory says "next free R-093".
- #67 and #69 both gave a new detector class ID 44 in the class list.
- PR #70 adds `check-rules.py --next` (reads the highest ID on disk). That stops hand-editing the counter line but
  not the race: two branches that fetch before either merges still get the same number. #70's answer is "the second
  branch renumbers", which is correct but manual.

### F4. Nothing checked that work actually landed

#62 was merged into its base branch eleven seconds after that branch had itself merged into `main` (#59), so the
gacha, relics, rank-first and swipe-fallback code never reached `main`. It was caught by a person reading the
result, not by a check. The lesson is recorded in one log entry and in project memory ("always confirm code reached
main"), but there is no command that does the confirming, and nothing in `memory-bank/notes.md` or `AGENTS.md`.

### F5. The staleness signal in check-memory.py is dead

`check-memory.py` lists "commits after the last change to `memory-bank/`" so a new session knows what memory might
be stale. In this repo nearly every commit touches `memory-bank/`, so the list is always empty (it is empty today).
The check passes, and tells the reader nothing.

The other checks (paths exist, files are mapped, `Last updated` present, line budgets) all pass while F2's problems
stand. They catch broken references; they don't catch stale ones. `context.md` says `Last updated: 2026-11-04`; its
Plan still lists step 6 as "a supervisor that calls a model", while `docs/step6-clear-zone.md` is Clear Zone.

### F6. Rules from mae reached the repo late, or not at all

mae's standing rules arrive in chat. The path into the repo is: thread hears it, tells the coordinator, coordinator
saves to project memory and later asks the docs thread, docs thread files a rule in a PR, mae merges. Two rules mae stated on
2026-11-11 are in no rule file on `main` or on the #67, #69 and capture branches: "monsters at a zone entrance
block the walk in; fight them first" (21:48, mentioned only in the capture branch's log entry) and "misc collectible
class for infrequent recipe resources" (22:58). Their full text lives in project memory.

This works against mae's own goal, "every manual step becomes rule + code": the rule exists before the code, but
only in a place the code-writing threads don't read.

There is also no link from a rule to the code that implements it. The rule format allows "which code or template"
in prose, but nothing lists rules that are still manual, so "manual step backlog" can't be printed.

### F7. Lists that only grow

mae's rule is "a repeated stuck point is a defect". The bank has no place where a stuck point is one item with a
count. Instead:

- status.md's "Open stuck points" bullet grew to ~660 characters of semicolon-joined cases (first written 2026-11-09).
- project memory's "Open stuck points" line holds 13 cases.
- `docs/function-check.md` has a "Ran live before?" column; status.md has "Untested live"; project memory has
  "NEVER RUN LIVE" items. Three ledgers of the same fact, none generated from the run logs.

Items are added by the thread that hits them and rarely removed, because removing means checking, and no thread
owns the list.

### F8. The same facts live in three places

| Fact | memory-bank | docs/ | project memory |
|---|---|---|---|
| Never-do list | `game/rules/policy.md` | | "Never-dos" paragraph |
| Live-test status | status.md Known problems | `function-check.md` column | "NEVER RUN LIVE", "UNTESTED LIVE" |
| Game account state | status.md Game state | | STATE, Game paragraph |
| Readout rule | `playbook.md`, `notes.md` | | READOUT RULE |
| Thread and PR list | status.md In progress | | Threads, PRs |
| Design docs | | `docs/big-map-survey.md`, `shop-tables.md`, `function-check.md`, labeler docs | copies in the project's shared files folder |

The prompt's "point, don't copy" rule was followed inside the repo, mostly. It had nothing to say about memory
outside the repo, and the coordinator's memory (about 15 KB in one index file) became a full parallel bank. When
they disagree, nothing says which wins.

### F9. Signs of how the bank was read

Direct evidence of reading is thin (sessions don't log what they read), so these are inferences:

- Threads were reliably given their rules in the coordinator's spawn message (readout rule, "put in every builder
  thread's instructions"), not left to find them in the bank. That is the coordinator compensating for a bank it
  didn't trust to be read.
- Stale items survive 100 edits of status.md. Sessions append their own news but don't reconcile the rest, which
  the prompt asks for only when someone says "update the memory bank".
- The playbook's first section is bold "this was agreed before but builders have not kept to it": rules written in
  prose were not followed until repeated in the thread prompt.

What did work: the game rules split by situation (`game/rules/README.md` situation table), the never-do file, and
`check-rules.py`. Rules are short, ID'd, cited from code and checked. They are the part of the bank that behaves
like code, and they are the part that held up.

---

## Proposals

Ordered by value for effort. P1 and P2 are #70 (already proposed, waiting to merge); they are listed so the rest
reads in context.

| # | Proposal | Fixes | Effort |
|---|---|---|---|
| P1 | One file per appended entry: log, decisions, work (#70) | F1 | done in #70 |
| P2 | Indexes printed from file metadata: docs, tests, rules, work (#70) | F1 | done in #70 |
| P3 | Split status by lifetime: live state out of git, readings generated, durable items one file each | F2, F8 | medium |
| P4 | No shared counters: provisional IDs on branches, numbers assigned on main | F3 | small |
| P5 | Landing check at session start: commits of finished work that aren't on main | F4 | small |
| P6 | Semantic checks: byte budgets, dated items, retired terms, merged branches still "in progress" | F2, F5 | small |
| P7 | Rule inbox: a stated rule lands in the repo the same turn, as its own file | F6 | small |
| P8 | Ledgers as one file per item with a count: stuck points, live-test status, questions for mae | F7 | medium |
| P9 | Rules carry a `code:` field; print the manual-step backlog | F6 | small |
| P10 | One owner per fact across repo and project memory; project memory points, never copies | F8 | small |
| P11 | Extend P2 to `sxs/README.md` and `scripts/README.md` (module docstrings) | F1 rows 5, 6 | small |

### P3. Split status by lifetime

- **Live coordination** (who runs what, emulator owner, waiting on mae, thread list) moves out of git. The
  coordinator's project memory already does this job; make it official and remove those sections from `status.md`.
  If a repo has no coordinator, a `work/` file per branch (P1) covers "in progress", and "waiting on mae" becomes
  `questions/` files (P8).
- **Runtime readings** (level, power, stamina, zones blessed) are printed by `python -m sxs report` from the
  progress snapshots the bot already writes. A log entry may quote the reading at the end of a session (dated, one
  file, no conflict); `status.md` never holds it.
- **Durable state** stays: a short `status.md` of milestones (what works, what's next in order, known defects),
  changed only when a milestone changes. Most sessions should not touch it at all.

The test: if a field would change during a normal day's run, it doesn't go in a committed file that every branch edits.

### P4. No shared counters

- On a branch, a new rule is written with a provisional ID: `### R-new-portal-teleport · ...`. Code and rules may
  cite it.
- `scripts/check-rules.py --assign` (run on `main` after a merge, by whoever merges next or the docs thread)
  replaces each `R-new-*` with the next number and rewrites citations. `check-rules.py` warns on `R-new-*` on a
  branch and fails on `main`.
- The same pattern for `resource/detect/classes.json`: branches add a class by name with `"id": null`; the dataset
  export assigns IDs from `main`'s order and refuses `null` on `main`. Names are the key; numbers come last.
- Delete the `next free:` line from the rules README (#70 already moves to `--next`).

This replaces "the second branch renumbers by hand" with a single mechanical step in one place.

### P5. Landing check

`landed.py`, run by the session-start check:

- For each `work/` file and each branch named in the last N log entries: `git cherry origin/main origin/<branch>`;
  print branches whose PR is merged but which still have commits not on `main` (the #62 case).
- Print open PRs whose base is not `main` (the setup that caused #62).
- Add one line to `AGENTS.md`: a PR targets `main`; if you stack on another branch, retarget it the moment that
  branch merges.

### P6. Checks that catch staleness, not just broken paths

Add to `check-memory.py`:

- **Byte budgets** alongside line budgets, and a maximum line length (say 300 characters) for memory files. A
  1,953-character line is a paragraph pretending to be a bullet.
- **Dated items**: every bullet in `status.md` (and every ledger file, P8) carries `(YYYY-MM-DD)`. Items older than
  7 days are printed as "re-verify or close" at session start. That turns "reconcile every file" from a ritual
  into a short list.
- **Retired terms**: a `memory-bank/retired.txt` (one term per line: "Fog Walk", "fogwalk.py", retired rule IDs).
  Any mention outside archives, the post-mortem and the retired table is flagged.
- **In progress vs git**: a `work/` file whose branch is merged into `main` is flagged for deletion.
- **Replace the dead signal** (F5): instead of "commits since memory last changed", list merged PRs since the
  newest log entry's date that no log entry mentions by number. That still works when every commit touches memory.

### P7. Rule inbox

Whichever thread hears mae state a rule writes `memory-bank/game/rules/inbox/<date>-<slug>.md` (her words, the time,
the situation) in the same turn, on its own branch, and mentions it in its PR. The docs thread later files it as a
proper rule and deletes the inbox file. It's one file per rule, so it never conflicts, and the rule reaches every
thread at the next merge instead of waiting for the docs thread's batch. Project memory can still keep a one-line
pointer while the PR is open.

### P8. Ledgers as files with counts

- `memory-bank/stuck/<slug>.md`: what happens, where (loop, zone, screen), first seen, `seen: N` with dates, owner,
  status (open / fix on branch X / fixed in #N). A thread that hits a known stuck point bumps the count instead of
  adding a bullet. `index.py stuck` prints them sorted by count: the top of that list is mae's "repeated
  stuck point = defect" queue.
- Live-test status: one line per loop in the loop's own module docstring (`Live: yes 2026-11-10 (Damp Woods)` /
  `Live: never`), printed by `index.py live`. `docs/function-check.md`'s column and status.md's "Untested
  live" go away.
- `memory-bank/questions/<slug>.md` for things waiting on mae, closed by deleting the file in the PR that acts on
  the answer.

### P9. Rule → code link

Extend the rule meta line with `code: sxs/loops/clear.py` or `code: none`. `index.py rules --manual` prints
rules with `code: none`: the backlog of manual steps mae wants turned into code, and the honest list of what the
bot can't yet do alone.

### P10. One owner per fact

Write down, in `memory-bank/README.md`, which store owns each kind of fact, including project memory:

- repo owns anything a code-writing session needs (rules, never-dos, how to run, durable status, ledgers);
- project memory owns live coordination (threads, emulator owner, who is waiting on whom) and pointers into the
  repo; it never restates a rule, it names the rule ID or file;
- the project's shared files folder holds deliverables for mae; repo docs are not copied there, they're linked.

When the two disagree, the repo wins for durable facts and project memory wins for live state.

### P11. Finish the job #70 started

`sxs/README.md` and `scripts/README.md` are the remaining hand-edited index tables (6 and 5 conflicts). Print them
from module docstrings the same way #70 prints the tests index.

### Not proposed again

mae declined a union merge driver and a "keep PR edits narrow" convention (2026-11-11) and wants to see how P1 and
P2 perform first. Nothing here depends on either. If P1 and P2 hold up, the measurement to repeat is F1's table
over the next 40 merges.

---

## A revised prompt for the next repo

The current prompt is good on content (point don't copy, verify, write the why, procedures are scripts) and should
keep all of that. What it lacks is a concurrency model and a way to tell live state from memory. Below are the
sections to add or replace, written so they can be pasted into `.agents/prompts/memory-bank.md`.

### Replace "The file set" with this

```markdown
## The file set

Many sessions may write to this repo at once, each on its own branch, merged in any order. Design for that from the
first commit: **a file that every session edits is a merge conflict waiting to happen.** So the bank has two kinds of
file:

- **Singletons**, edited rarely and by one session at a time: README.md, context.md, notes.md, status.md.
- **Entry folders**, one file per entry, never edited by two sessions: log/, decisions/, work/, and any list that
  grows (stuck points, open questions, a ledger). Indexes over them are printed by a script, never committed.

| Path | Holds | Changes | Budget |
|---|---|---|---|
| `README.md` | The map, the sources of truth, which store owns which fact (including memory outside the repo), the maintenance rules. | When a file or folder is added or repurposed. | 120 lines, 8 KB |
| `context.md` | What the project is and isn't, stack, exact commands, architecture in a few lines, where each kind of fact lives. | When scope, stack, commands or layout change. | 100 lines, 6 KB |
| `status.md` | Durable state only: what works, what's next in order, known defects. Each bullet dated. No live state (see below). | At milestones. Most sessions don't touch it. | 60 lines, 6 KB |
| `notes.md` | The people's working preferences, environment gotchas, conventions not written elsewhere. | When learned. | 100 lines, 8 KB |
| `log/` | One file per session: `YYYY-MM-DD-HHMM-slug.md`. Date, where it ran, what changed (PR or commit), what's open. | Every session that changed something. | 15 lines each |
| `decisions/` | One file per decision: decision, why, alternatives rejected, status. (Use the repo's ADR folder if it has one.) | When a decision is made or superseded. | Never delete |
| `work/` | One file per branch in progress: title, branch, PR, where it runs, notes. Deleted in the PR that finishes it. | Created when work starts; only its own branch edits it. | 20 lines |

Never keep a rolling log with an archive: moving the oldest entry makes every session edit two shared files.

### Live state is not memory

Who is running what right now, which machine is busy, what waits on a person, and runtime readings (scores, levels,
counts) change hourly. Git lands them only when a branch merges, so on the default branch they are always stale and
always conflicting. Keep live state where it updates live (the coordinator's notes, an issue, a dashboard, or a
report the program prints from its own logs) and keep only a pointer to it in the bank.

The test: if a value would change during a normal day's work, it doesn't go in a committed file that every branch
edits.
```

### Add a section "Working in parallel"

```markdown
## Working in parallel

- **Indexes are printed, not edited.** Each doc, test and rule carries its own index line (a comment under the
  title, a docstring field, a heading). `index.py <folder>` prints the table. Adding a file never means
  adding a row to a shared table.
- **No shared counters.** Never store "next free ID" in a file. A branch gives a new numbered item a provisional
  ID (`R-new-<slug>`, `"id": null`); a script assigns real numbers on the default branch after merge, and the check
  fails on the default branch while any provisional ID remains. Where numbers don't matter, key by name.
- **Confirm work landed.** A PR targets the default branch. If you stack a branch on another, retarget the PR as
  soon as its base merges. At session start, `landed.py` lists merged branches with commits missing from
  the default branch.
- **Capture rules the moment they're stated.** When a person states a rule or preference, write it the same turn as
  its own file (an inbox file is fine) on your branch. Don't leave it only in chat or in memory outside the repo.
- **Ledgers are files with counts.** A recurring problem is one file with `seen: N` and dates, not a new bullet each
  time. Print ledgers sorted by count; the top is the priority.
```

### Replace "Session protocol" Start and End with this

```markdown
**Start**: run `python3 scripts/check-memory.py`. It prints, in order: problems to fix, work that didn't land,
items older than 7 days to re-verify or close, merged PRs no log entry mentions, and the newest three log entries.
Then read context.md and status.md, and only what your task needs. If anything contradicts the code, the code wins:
fix the bank in this session.

**End**:
1. Add your log entry (`entries.py new log "Title"`).
2. Update or delete your own `work/` file. Edit `status.md` only if a milestone changed.
3. Bump or close ledger items you touched; add decisions and rules as their own files.
4. Run the check and commit memory with the work it describes.

**Reconcile, don't just append.** Before ending, close or re-date any item the check listed as old that your
session can verify. An item nobody can verify gets ❓ and a line saying what would confirm it.
```

### Replace the check description in "Init workflow" step 5 with this

```markdown
5. **Add the checks.** Copy `scripts/check-memory.py`, `entries.py`, `index.py` and
   `landed.py` if they came with this prompt. The memory check must fail on: a path the bank names that
   doesn't exist; a memory file missing from the map; a file over its line **or byte** budget; a line over 300
   characters; a `§` reference to a missing section; a mention of a term in `memory-bank/retired.txt`; a `work/`
   file whose branch has merged; a provisional ID on the default branch. It must list, as warnings: dated items
   older than 7 days, merged PRs no log entry mentions, and merged branches with commits not on the default
   branch. Structural checks catch broken references; only dated items catch stale ones.
```

### Add to "Writing rules"

```markdown
12. **Budgets are bytes, not lines.** A long paragraph on one line is still a long paragraph.
13. **Date every status item and ledger entry.** Undated items can't be found stale.
14. **One owner per fact, inside and outside the repo.** The README says which store owns each kind of fact,
    including memory the agent platform keeps outside git. Other stores point; they never restate.
15. **Rules point to code.** A rule or procedure says which code implements it, or `code: none`. The list of
    `code: none` items is the honest list of what still needs a person.
```

### Add to "Definition of done"

```markdown
- [ ] No file in the bank is one that every session must edit (status.md is milestones only).
- [ ] No "next free" counter is stored anywhere.
- [ ] The start-of-session check prints stale items, unlanded work and unlogged PRs.
- [ ] The README names the owner of each kind of fact, including stores outside the repo.
```

### Ship the scripts with the prompt

The prompt today ships one script. The next repo should get, from day one: `check-memory.py` (with P6),
`entries.py` and `index.py` (from #70), `landed.py` (P5), and `check-rules.py --assign` generalised as
`ids.py assign` for any provisional-ID file. A new repo should never have a shared log, a hand-edited index or a
stored counter to migrate away from.

---

## Suggested order for this repo

1. Merge #70 (P1, P2).
2. P5 landing check and P6 staleness checks: small, and they make the bank's own drift visible.
3. P4 provisional IDs for rules and detector classes, before the next round of parallel rule PRs.
4. P3 status split and P8 ledgers together: they remove the last file every session edits.
5. P7, P9, P10, P11 as the docs thread's next batch.
6. Fold the agreed changes back into `.agents/prompts/memory-bank.md` (and into the TrackFlow source it came from).

## How the numbers were measured

```bash
git log --oneline | wc -l                                   # 504 commits on main
git log --oneline -- memory-bank/log.md | wc -l             # 205
git log --oneline -- memory-bank/status.md | wc -l          # 101
git log --merges --oneline | wc -l                          # 133 merges; 80 not "Merge pull request"
# files changed on both sides of each of the last 80 merges:
for m in $(git log --merges --format=%h | head -80); do
  set -- $(git log -1 --format=%P $m); b=$(git merge-base $1 $2)
  (git diff --name-only $b $1; git diff --name-only $b $2) | sort | uniq -d
done | sort | uniq -c | sort -rn
wc -c memory-bank/*.md                                      # status 17.7 KB, decisions 19 KB, log 20 KB
git log --reverse --format=%ad --date=short -S"Untested live" -- memory-bank/status.md | head -1   # 2026-11-04
```
