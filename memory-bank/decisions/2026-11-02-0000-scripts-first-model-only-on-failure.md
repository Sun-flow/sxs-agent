# 2026-11-02 · Scripts first, model only on failure

- **Decision**: Deterministic pipelines do the daily work; a supervisor calls a model only on an unknown screen or a timeout, and writes the fix back as a pipeline.
- **Rationale**: mae's budget rules out a model call per action; each solved situation then costs nothing next time.
- **Alternatives considered**: a model-in-the-loop agent that looks at every screen (too costly to run daily).
- **Status**: Accepted
