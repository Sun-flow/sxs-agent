# Decision Log

> **Last updated**: 2026-11-09
> Decisions with lasting consequences (tech choices, structure, conventions, scope calls) and why they were made, so later sessions don't undo them by accident. One entry per decision, newest first; update `Status` when superseded; never delete an entry. Details and sources for the 2026-11-02 entries are in `docs/step1-emulator-and-game.md`.

Entry format:

```
### [YYYY-MM-DD] Title
- **Decision**: one line
- **Rationale**: why
- **Alternatives considered**: what we didn't pick and why
- **Status**: Accepted / Superseded by [title]
```

---

### [2026-11-09] The location tree is committed data the bot writes: `resource/world/zones.json`
- **Decision**: zones, their CP, exploration %, blessed flag, links (walked / map_adjacent / inside) and known ways in live in one JSON file under `resource/world/`, read and written by `sxs/policy/zones.py`. Roam surveys and fog-walk zone changes update it at runtime; builders commit it with their session. Roam picks targets and entry neighbours from it, not from one area-map reading.
- **Rationale**: mae (2026-11-09): the system should build a map of locations and explorations. One area-map reading misses zones off screen and loses % lines; per-run state in `logs/roam.json` was gitignored and forgot every way in. Committed data survives sessions and machines and shows its gaps (`python -m sxs zones`).
- **Alternatives considered**: keeping it under `memory-bank/game/` beside nav-graph.json (that folder is maintained by the docs thread through rules batches; runtime writes there would collide); gitignored `logs/` (loses the map between machines); folding it into nav-graph.json (menus, not geography).
- **Status**: Accepted (live check pending)

### [2026-11-05] Interrupts: one table pauses any loop for tutorials, reward choices and popups
- **Decision**: the runner wraps the state detector (`sxs/core/interrupts.py`); after every screen check one priority table (`sxs/actions/interrupts.py`) can pause the running loop, run a short handler (tutorial highlight on the island map or home, Choose Your Reward, rating popup, chat), and hand the loop the fresh detection. Handlers have their own budget, can mute themselves, and end the run with a named status (`LoopStop`) when mae must decide. Loops opt out per row (`Loop.owns`) and can register a resume step (`resume_with`). Unknown stays explicit.
- **Rationale**: mae (2026-11-05 01:56): move between tasks such as explore and tutorial when the detector sees the state change. Fog Walk kept tapping under a tutorial highlight and had to be stopped by hand. One place for these screens instead of a branch per loop; pausing inside `detect()` keeps the loop's goal intact without serialising it.
- **Alternatives considered**: a scheduler that stops a loop and starts another (loses the loop's in-memory goal, needs every loop to be resumable from saved state); per-loop branches (what we had: explore handled the reward choice, Fog Walk didn't); firing the tutorial row on every state (the highlight finder matches 18 ordinary reference screens).
- **Status**: Accepted (proposed to mae 2026-11-05; live check pending)

### [2026-11-04] Progress is recorded as per-day snapshots plus a run log, read only
- **Decision**: `python -m sxs progress` reads stats off a few screens into `logs/progress/<server day>.json` and writes a Markdown report beside it; the loop runner appends every run's readout to `logs/runs.jsonl`; other loops add readings they make anyway with `records.note`. Deltas compare the day's newest reading with the previous day's last; a failed read is "not read", never a change. Skills and gear are reported as 5-level bands, not per-skill levels (mae).
- **Rationale**: mae (2026-11-04) wants a session-by-session record of progress. Snapshots need no game knowledge beyond a few screens, cost no model calls, and survive misreads; notes avoid extra navigation (the Cart panel only opens when its loot bubble shows).
- **Alternatives considered**: deriving progress only from loop readouts (misses anything no loop reads, e.g. power, rank); one CSV row per run (nested gear/skill/area readings don't fit, and misreads would show as changes).
- **Status**: Accepted

### [2026-11-04] Screenshots in folders by situation, unlabelled screens banked for mae
- **Decision**: `docs/screens/` holds one folder per situation (home, character, world, battle, dailies, guild, shops, dialogs, system, icons, minimap); the folder comes from the name's prefix (`sxs/core/screens.py`). Expected detector states live in `docs/screens/expected.json`. Unfamiliar screens go to `docs/screens/unlabeled/` with a table mae fills in; `python -m sxs label` files them.
- **Rationale**: mae (2026-11-04): "We should have a bank of unfamiliar/undefined screens that I can manually label and build context on"; 190 flat files were slow to browse.
- **Alternatives considered**: keep the flat folder until ~300 screens (my earlier suggestion); delete unreferenced screens (mae: keep them).
- **Status**: Accepted

### [2026-11-04] Layered package and one loop contract
- **Decision**: `sxs/` is split into `sxs/core/`, `sxs/vision/` (never taps), `sxs/policy/`, `sxs/actions/` and `sxs/loops/`. Every loop is a `Loop` spec (`sxs/core/loop.py`) run by one runner: same inputs (`ctx` with device, detector, navigator, plus its own options), same output (`Result(status, ok, data)`), same readouts (banner at start, `[Result X]` log line and one JSON line at the end, exit 0/1/2). Commands are `python -m sxs <loop>`. Runs are short: a 120 s budget per loop and per daily step, and a stall stop after 60 s without progress (mae, 2026-11-04 21:45: "1-2 min max", exit shortly after a task stops moving). Code used in two places becomes one helper (`sxs/core/ui.py` coordinates, `sxs/vision/ocr.py`, `sxs/actions/heal.py`, `sxs/actions/common.py`).
- **Rationale**: mae (2026-11-04 21:25): "clear inputs, outputs, and readouts, that are consistent and operationalizable", used "structurally as often as possible"; duplicated code becomes functions; smaller modules so an agent reads less context per task.
- **Alternatives considered**: keep flat modules with per-module `main()` (each printed its own format and exit code); drop MaaFramework (mae: keep Maa).
- **Status**: Accepted

### [2026-11-04] Rules split by situation, memory bank slimmed
- **Decision**: The single rules file (memory-bank/game/rules.md) became `memory-bank/game/rules/`: one file per situation (policy, ui, home, world, overworld, quests, combat, dailies, guild, gathering, upgrades, economy) plus a README index. Rules were rewritten to what an acting agent needs (no sources, dates, batch history or account snapshots). IDs are kept; merged duplicates are listed as retired IDs in the index, and `scripts/check-rules.py` checks every cited ID resolves. The handoff file was split into `playbook.md` (stable process) and `status.md` (state and next steps); machine facts moved from `notes.md` to `environments.md`.
- **Rationale**: mae (2026-11-04): context had grown bloated; organise rules by content type so an agent in one environment reads one file. The 101 KB rules file and a 22 KB handoff with seven appended updates cost every session ~8.6K tokens, about half duplicated.
- **Alternatives considered**: renumbering rules per file (breaks the R-IDs cited in code, policy files and the nav graph); keeping one file with better headings (still loads everything for every situation).
- **Status**: Accepted

### [2026-11-04] Loops are watched and hand off to each other
- **Decision**: Each loop (`sxs.loops.explore`, `sxs.loops.tower`, `sxs.loops.fogwalk`, `sxs.actions.goto`) logs a banner at start, a heartbeat every 30 s, and ends early with a named reason (stuck_progress, stuck_self, stuck, unknown_screen with a saved frame, power_gate, repeating_card) instead of idling. Stalls rotate through unstick strategies (walk to the quest's area, talk to a red "!", fight a blocker or guard, pan). The explore loop calls the tower loop on Fantasia Ascent screens and resumes after.
- **Rationale**: mae (2026-11-04): loops must notice being stuck, report unfamiliar screens, and call each other; a stuck loop is a robustness bug to fix, not a restart.
- **Alternatives considered**: one 5-minute give-up timer (what we had; it idled silently on a counterless quest).
- **Status**: Accepted

### [2026-11-03] Goal-based decisions on cards, rules in a data file
- **Decision**: Every popup or card is read (title, text, buttons) and matched against ordered rules in `resource/policy/cards.json`, keyed on the current goal (explore, daily, idle) and circumstances (HP). A rule picks a button, Cancel, or dismiss. A card with no rule is dismissed and stops the run after 3, so a rule gets added once. Lasting choices (class) always stop with `needs_decision`.
- **Rationale**: mae asked for "select the correct option given goals and circumstances" rather than menu-advancing scripts. Rules as data let the supervisor (a model, later) add one rule per new card instead of editing code, so each new card costs model tokens once.
- **Alternatives considered**: always pressing the main button (walks into purchases and wrong dungeons); hard-coding per-screen handlers in Python (every new card needs a code change).
- **Status**: Accepted

### [2026-11-03] OCR-first state detection, one node at a time
- **Decision**: Detect screens with MaaFramework OCR on fixed UI text (nav labels, titles, buttons), using templates only where there is no text. Run the `State.*` nodes one by one on a single screenshot (custom action `DetectState`) instead of through a `next` list. Commit reference screenshots as 256-colour PNGs in `docs/screens/` and check the detector against them offline.
- **Rationale**: OCR on UI text holds up better than image templates when art or colours change, and the game's English UI is clean. MaaFramework's batched OCR for `next` lists misread several screens. 256-colour PNGs are ~200 KB instead of ~550 KB and give the same detector results.
- **Alternatives considered**: a plain `next` list (fast but wrong); `only_rec` OCR (40% faster, but broke five screens); plain adb + OpenCV (not needed, since MaaFramework works).
- **Status**: Accepted

### [2026-11-03] Memory bank from the TrackFlow prompt
- **Decision**: Agent memory lives in `memory-bank/`, built and maintained by `.agents/prompts/memory-bank.md` and checked by `scripts/check-memory.py`, both copied from mae's TrackFlow-Company-Overhaul repo. Decisions live in this file because the repo has no other decision log.
- **Rationale**: mae asked for it. Sessions run in different places (cloud, maes2024) with no shared chat history, so the repo has to carry the context.
- **Alternatives considered**: relying on the Claude project's own memory (not visible to agents outside the project, such as a local session on maes2024).
- **Status**: Accepted

### [2026-11-02] Scripts first, model only on failure
- **Decision**: Deterministic pipelines do the daily work; a supervisor calls a model only on an unknown screen or a timeout, and writes the fix back as a pipeline.
- **Rationale**: mae's budget rules out a model call per action; each solved situation then costs nothing next time.
- **Alternatives considered**: a model-in-the-loop agent that looks at every screen (too costly to run daily).
- **Status**: Accepted

### [2026-11-02] MaaFramework + MaaMCP for the hands-and-eyes layer
- **Decision**: Build device control, recognition and flows on MaaFramework JSON pipelines with Python custom logic; use MaaMCP for Claude to drive the device and save pipelines.
- **Rationale**: open source and proven in game bots; built-in template matching and OCR; supports MuMu's fast screenshot path; MaaMCP fits the "agent writes its own scripts" pattern.
- **Alternatives considered**: plain Python (`adbutils` + OpenCV + RapidOCR), kept as the fallback if MaaFramework proves too opinionated.
- **Status**: Accepted

### [2026-11-02] MuMu Player 12 on Windows at 1280×720
- **Decision**: Run the game on MuMu Player 12 on maes2024, one instance per account, 1280×720 at 240 dpi.
- **Rationale**: fastest screenshot path (~10 ms IPC vs ~100 ms `adb screencap`), a CLI for instance control, per-instance ADB ports, wide use in bot communities. 1280×720 is what most bot assets assume.
- **Alternatives considered**: BlueStacks 5 (fallback; slower screenshots, little CLI); LDPlayer 9 (dropped by MAA for unstable screenshots); Android Studio AVD (ARM games run poorly on x86); Redroid on Linux (best for headless later, not worth it for iteration 1).
- **Status**: Accepted
