# Session Log Archive

Older entries moved from `memory-bank/log.md`, newest first.

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
