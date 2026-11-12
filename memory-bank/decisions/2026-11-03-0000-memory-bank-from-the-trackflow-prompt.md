# 2026-11-03 · Memory bank from the TrackFlow prompt

- **Decision**: Agent memory lives in `memory-bank/`, built and maintained by `.agents/prompts/memory-bank.md` and checked by `scripts/check-memory.py`, both copied from mae's TrackFlow-Company-Overhaul repo. Decisions live in this file because the repo has no other decision log.
- **Rationale**: mae asked for it. Sessions run in different places (cloud, maes2024) with no shared chat history, so the repo has to carry the context.
- **Alternatives considered**: relying on the Claude project's own memory (not visible to agents outside the project, such as a local session on maes2024).
- **Status**: Accepted
