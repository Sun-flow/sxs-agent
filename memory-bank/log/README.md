# Session log

One file per session handoff, so two branches never edit the same lines. Read the newest with
`python3 scripts/entries.py log` (`-n 10`, `--all`, `--grep WORD`). Entries from before this folder existed (up to
2026-11-10 morning) are frozen in `docs/archive/memory-bank-log.md`.

## Adding an entry

    python3 scripts/entries.py new log "What you did (Claude Code, cloud)"

That writes `log/YYYY-MM-DD-HHMM-slug.md` (UTC now) with this shape; fill it in and commit it with the work:

```
# 2026-11-11 21:40 · What you did (Claude Code, cloud)

- What changed, linking the PR or commit; what mae decided, with her time.
- Open: what's left and who it waits on.
```

- One entry per session (a long session may add one per PR). Write a new entry for news; don't append to someone
  else's. Fixing a wrong fact in an entry is fine.
- No budget and no archiving: old entries stay where they are, and the views only show the newest.
- `python3 scripts/check-memory.py` checks names and headings (through `scripts/entries.py check`).
