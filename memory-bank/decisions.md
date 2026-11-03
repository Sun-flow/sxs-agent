# Decision Log

> **Last updated**: 2026-11-03
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
