# 2026-11-04 22:24 · Progress is recorded as per-day snapshots plus a run log, read only

- **Decision**: `python -m sxs progress` reads stats off a few screens into `logs/progress/<server day>.json` and writes a Markdown report beside it; the loop runner appends every run's readout to `logs/runs.jsonl`; other loops add readings they make anyway with `records.note`. Deltas compare the day's newest reading with the previous day's last; a failed read is "not read", never a change. Skills and gear are reported as 5-level bands, not per-skill levels (mae).
- **Rationale**: mae (2026-11-04) wants a session-by-session record of progress. Snapshots need no game knowledge beyond a few screens, cost no model calls, and survive misreads; notes avoid extra navigation (the Cart panel only opens when its loot bubble shows).
- **Alternatives considered**: deriving progress only from loop readouts (misses anything no loop reads, e.g. power, rank); one CSV row per run (nested gear/skill/area readings don't fit, and misreads would show as changes).
- **Status**: Accepted
