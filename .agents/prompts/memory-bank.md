# Memory Bank: Generation and Maintenance Prompt

> **What this is**: a project-agnostic prompt for any AI coding agent. Point an agent at it to **create** a memory bank in a repo, to **reconcile** one that has drifted, or as the standing rules for **maintaining** one. To use it in a new repo, copy this file to `.agents/prompts/memory-bank.md` and `scripts/check-memory.py` beside it, then tell the agent: "Read `.agents/prompts/memory-bank.md` and set up a memory bank for this repo." Both files work unchanged; everything project-specific goes in the bank itself.

---

## Why a memory bank exists

Your memory resets between sessions, and the next session may be a different agent, model or tool, in a different environment, with no chat history. The memory bank is a small folder of Markdown files that carries what you'd otherwise lose: what the project is, where things stand, what was just done, and what the people you work with expect. It is written so the next session can orient itself in a couple of minutes and pick up the work without asking questions that were already answered.

It is **memory, not a standard**. The repo's own docs (a spec, a decision log, a README, the code) are the sources of truth. The bank points to them and never copies their content.

## Order of truth

When two sources disagree, the higher one wins. Fix the lower one in the same session.

1. The code, tests and manifests, as they are now.
2. The repo's binding docs: spec, decision log, README (whatever the repo actually has).
3. The memory bank.
4. Anything in an archive. That is history, not instructions.

---

## The file set

Create `memory-bank/` at the repo root with these five files. Don't add more until a file passes its size budget and needs to be split, and then record the new file in the map.

| File | Holds | Changes | Budget |
|---|---|---|---|
| `README.md` | How this memory works: the map of files (what each is for, when to read it, when to update it), the sources of truth for this repo, and the maintenance rules. | Rarely. When a file is added, removed or repurposed. | ~120 lines |
| `context.md` | Orientation. What the project is and isn't, who it's for, the stack and the exact commands to run, build and check it, the architecture in a few lines, and **where each kind of fact lives**. | When scope, stack, commands or doc layout change. | ~100 lines |
| `status.md` | Current state, under the headings Works / In progress / Next / Open questions / Known problems. Each "In progress" item names its branch, PR and the environment working on it, so two sessions don't pick up the same work. | Every session that changes the state of the work. | ~80 lines |
| `log.md` | Session handoffs, newest first. One short entry per session: date, where it ran, what changed (link the PR or commit), and what was left open. | At the end of every session that changed something. | Last ~15 entries; older ones move to an archive file |
| `notes.md` | Things learned the hard way. The people's working preferences, environment and tool gotchas, and conventions the code relies on that aren't written anywhere else. | Whenever you learn something the next session would otherwise rediscover. | ~100 lines |

**Decisions**: if the repo already has a decision log or ADR folder, use it and point to it from `context.md`. Only if it has none, add `memory-bank/decisions.md` with entries of the form: date and title, decision, rationale, alternatives considered, status.

**Adopt, don't duplicate.** If the repo already has a file doing one of these jobs (a status doc, a changelog, an architecture doc), either move it into the bank or point to it from the map. Never keep two.

---

## Entry point

Every agent tool reads a different file first. Make them all lead to the same place:

- `AGENTS.md` at the root is the entry point. Near the top it says: read `memory-bank/README.md` and then the files it lists, before doing anything else; and at the end of the session, update the bank as the README describes.
- `CLAUDE.md` holds one line, `@AGENTS.md`, so Claude Code loads the same instructions.
- Add a one-line pointer for any other tool the people use: `.github/copilot-instructions.md` for GitHub Copilot, `.cursor/rules/` for Cursor, `.clinerules` for Cline. Ask which tools they use rather than guessing. Keep the instructions themselves in `AGENTS.md` only.

---

## Session protocol

**Start**: read `AGENTS.md`, then `memory-bank/README.md`. Run the check if there is one: it also lists commits that changed the repo after the bank was last updated, which tells you what memory might be stale. Then read `context.md`, `status.md`, and the top few entries of `log.md`. Read `notes.md` before doing anything that touches the people's preferences or the environment. Then read the repo docs and code your task needs. If anything you read contradicts the code, the code wins: note it and fix the bank.

**During**: when you learn something the next session will need, such as a preference, a gotcha or a decision, write it down in the same turn. Don't save it for the end; sessions end without warning.

**End** (or before you hand work back):

1. `status.md`: move what you finished to "Works", update "Next" and "Open questions".
2. `log.md`: add one entry at the top.
3. `notes.md`: add anything learned the hard way.
4. If you changed the stack, commands or doc layout, update `context.md`.
5. Run the check (below) if the repo has one.
6. Commit the bank changes in the same commit as the work they describe. That keeps memory and code in step, and it is how the check spots commits the memory hasn't caught up with.

When someone says "update the memory bank", reconcile **every** file against the repo, not just the latest diff.

---

## Writing rules

1. **Point, don't copy.** Name the file and section that holds a fact (`docs/spec.md` §3) instead of restating it. Copies drift, and the same standard written in several places ends up contradicting itself.
2. **Paths and sections, never line numbers.** Line numbers go stale with every edit. If the bank cites one document by section number (`§3`), name it in the README with a line of the form ``Section references (§N) point to `path/to/doc.md`.`` so the check can confirm the sections exist.
3. **Verify before you write.** Every claim about the repo comes from a file, a command's output or git history. If you can't check something, mark it ❓ and say what would confirm it.
4. **Write the why.** A decision without its reason gets undone by the next session. Say what was tried and rejected.
5. **Date what changes.** Each file has a `Last updated` line; log entries and status items carry ISO dates.
6. **Stay inside the budgets.** When a file grows past its budget, cut what's stale or split it and add the new file to the map.
7. **Don't store what git already has.** The log links to commits and PRs; it doesn't repeat diffs.
8. **Procedures are scripts.** If doing something takes more than one step (screenshots, a release, regenerating data), commit a script and let the memory name the command. A script can be run and checked; a remembered procedure gets rebuilt slightly differently each time.
9. **Never store secrets**, tokens, personal contact details or anything private you wouldn't put in the repo.
10. **Archive, don't delete.** Superseded files go to the repo's archive with a one-line note pointing to their replacement.
11. **Write for a stranger.** Plain sentences, full paths, no "as discussed". The next reader may be a different model with none of your context.

---

## Init workflow ("set up a memory bank")

1. **Survey** the repo: tree, manifests, lockfiles, CI, existing docs, the README, the last ~30 commits.
2. **Find the sources of truth** that already exist and decide what the bank will adopt and what it will point to.
3. **Create** `memory-bank/` with the five files, filled only from what you verified. Use ❓ for the rest.
4. **Wire** `AGENTS.md`, `CLAUDE.md` and any other tool pointers.
5. **Add the check.** If `scripts/check-memory.py` came with this prompt, keep it and run it (it needs only Python 3). If not, and the repo can run one, write a small script that fails on any path the bank or `AGENTS.md` mentions that doesn't exist, on any `memory-bank/` file missing from the map, on files over budget and on `§` references to sections that don't exist, and that lists the commits made after the last change to `memory-bank/`. Mechanical checks catch drift better than review rituals.
6. **Read it cold.** Start a fresh session (or a subagent with no context), have it read only the entry point and the bank, and ask it: what is this project, what works, what's next, and how do I run it? Fix whatever it gets wrong or can't answer.

## Definition of done

- [ ] The five files exist, each with a `Last updated` date, inside its budget.
- [ ] Every claim is verified or marked ❓; nothing restates the binding docs.
- [ ] `AGENTS.md` sends agents to the bank first and says how to maintain it; `CLAUDE.md` points to `AGENTS.md`.
- [ ] The check passes, if there is one.
- [ ] A cold read answers: what this is, what works, what's next, how to run it.
