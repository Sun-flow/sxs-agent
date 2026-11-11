# 2026-11-11 21:23 · Memory is written one file per entry and indexes are built, never edited (mae, 21:16)

- **Decision**: Session log entries, decisions and in-progress workstreams are one file each (`memory-bank/log/`, `memory-bank/decisions/`, `memory-bank/work/`). The docs list, tests list and rule ID index are printed by `scripts/index.py` from metadata in each file and are not committed. Shared files that remain get narrow edits only.
- **Rationale**: nearly every PR conflicted on log.md, status.md, docs/README.md and tests/README.md because branches appended at the same spot; mae merges on GitHub in any order. New files never conflict.
- **Alternatives considered**: a `merge=union` driver in .gitattributes (likely ignored by GitHub's merge button; silently keeps stale lines); committed generated indexes regenerated on main (still conflict whenever a branch regenerates, and need CI or a manual step); a GitHub Action to regenerate on main (no CI in this repo yet).
- **Status**: Accepted
