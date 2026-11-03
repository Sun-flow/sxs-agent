# Session Log

> **Last updated**: 2026-11-03
> Newest first. One entry per session: date, where it ran, what changed (link the PR or commit), what was left open. Keep about 15 entries. When there are more, move the oldest to `docs/archive/memory-bank-log.md` (create it the first time). Entries before this file existed were rebuilt from git history and the project's chat.

### 2026-11-03 · Game docs batch 4 (Claude Code, cloud)
- Builder batch 4 (step 3 explore loop): added `interact` and `defeated` screens and their taps to `memory-bank/game/nav-graph.json`; rules R-029 to R-034 (Trek quest chain, map object cards, defeat, camera, stamina regen, exploration rewards) and the quest-ring offset in R-022. Branch `claude/project-thread-npg43i` fast-forwarded to main after PR #4.
- Batch 5 added to the same PR: cart, house, bed, unlock result and skill/technique screens; rules R-035 to R-039; Cart income in R-020.
- Open: captures for batches 4 and 5 live on branch step3-explore until it merges.

### 2026-11-03 · Game docs batch 2 (Claude Code, cloud)
- Builder batch 2: added the `title` screen and login waits to `memory-bank/game/nav-graph.json`, confirmed Explore progress (R-002, R-021), noted the blessing statue is still unseen (R-003). Branch `claude/project-thread-npg43i` fast-forwarded to main after PR #3 merged.
- Also folded in the step 2 doc's screen catalogue (boot taps, resume on last screen), merged main after PR #5, PR #4.

### 2026-11-03 · Step 2: hands and eyes (Claude Code, maes2024 via Remote Control)
- Installed MaaFramework 5.15 in `.venv`; it uses MuMu's IPC screenshots. Built `sxs/` (device, state detector, navigator, CLI, offline replay), `resource/` (state pipeline, dialogue template, OCR models via `scripts/fetch-ocr-models.py`), `tests/` and `docs/step2-hands-and-eyes.md`. Branch `step2-hands-and-eyes`.
- mae accepted the agreement and signed in. I played the rest of the tutorial prompts (enhanced the staff, equipped the cap, finished Wild Isle Trek I) and captured 25 screens. I sent game rules to the docs thread (PR #3) through the coordinator.
- The smoke test passed twice. Open: push and PR (Git on maes2024 needs mae's GitHub sign-in). Daily-content screens are still locked at Lv 2.

### 2026-11-03 · Game rules and menu graph started (Claude Code, cloud)
- mae asked for documentation of the game's rules and a traversable map of menus, fed by the step 2 builder thread. Added `memory-bank/game/` (README, `memory-bank/game/rules.md` with R-001 to R-020 from mae and the step 1 doc, `memory-bank/game/nav-graph.json` with 15 screens) and `scripts/nav-graph.py` (check, render, shortest path). Branch `claude/project-thread-npg43i`, PR #3.
- Batch 1 from the builder (via the coordinator): graph now 25 screens and 29 actions with OCR detection and tap positions; rules R-021 to R-028 added, currency, Cart and unlock rules promoted to observed.
- Open: shop, dungeons, mail, arena and vendor entry points; currency icon crops; battle loss path. Earlier: most edges lacked tap positions and most screens lack detection hints and captures; the builder thread sends them as it plays.

### 2026-11-03 · Memory bank set up (Claude Code, cloud)
- mae asked to bring the memory bank generation prompt from the TrackFlow-Company-Overhaul repo into this one and instantiate it. Copied `.agents/prompts/memory-bank.md` and `scripts/check-memory.py` unchanged. PR #2. Wrote `AGENTS.md`, `CLAUDE.md` and the six memory files. Branch `claude/project-thread-4u6oai`.
- Open: mae reviews and merges PR #2.

### 2026-11-02 · Step 1: emulator choice and game survey (Claude Code, cloud)
- Compared emulators and automation toolkits and catalogued the game's daily content; picked MuMu Player 12 and MaaFramework (`decisions.md`). mae confirmed the game is Sword x Staff. PR #1, branch `docs/step1-emulator-and-game`.
- PR #1 merged 2026-11-03. Open: maes2024 setup.
