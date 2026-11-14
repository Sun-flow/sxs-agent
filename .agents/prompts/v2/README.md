# Memory bank prompt v2 (draft for review)

Drafts from the memory bank retrospective (`docs/memory-bank-retro.md`). Not in use in this repo yet.

- `memory-bank.md`: the revised project-agnostic prompt (replaces `../memory-bank.md` once agreed).
- `bank.py`: one standard-library tool that replaces `check-memory.py` and adds entry files, printed indexes,
  ledgers with counts, the landing check and provisional-ID assignment. Copy it to `scripts/bank.py` to use it.

Tested against PR #70's layout (finds this repo's long lines, stale status items, unlogged PRs and the branch with
commits after its PR merged) and against a throwaway repo reproducing the #62 case (PR merged into a branch that
had already merged).
