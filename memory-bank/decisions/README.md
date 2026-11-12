# Decisions

Decisions with lasting consequences (tech choices, structure, conventions, scope calls) and why they were made, so
later sessions don't undo them by accident. One file per decision, so branches never edit the same lines. Details
and sources for the 2026-11-02 entries are in `docs/step1-emulator-and-game.md`.

Read them with `python3 scripts/entries.py decisions --titles` (one line each, newest first), then open the file, or
`python3 scripts/entries.py decisions --grep WORD`.

## Adding a decision

    python3 scripts/entries.py new decisions "Title as the decision itself (mae, HH:MM)"

That writes `decisions/YYYY-MM-DD-HHMM-slug.md` (UTC now) with this shape:

```
# 2026-11-11 21:40 · Title
- **Decision**: one line
- **Rationale**: why
- **Alternatives considered**: what we didn't pick and why
- **Status**: Accepted / Superseded by [title]
```

- Never delete an entry. When a decision is superseded, change its `Status` line to name the new one; that one-line
  edit is the only change to an old entry.
- Entries from 2026-11-02 and 2026-11-03 carry no time (it wasn't recorded); their files use `0000`.
