# 2026-11-04 21:49 · Screenshots in folders by situation, unlabelled screens banked for mae

- **Decision**: `docs/screens/` holds one folder per situation (home, character, world, battle, dailies, guild, shops, dialogs, system, icons, minimap); the folder comes from the name's prefix (`sxs/core/screens.py`). Expected detector states live in `docs/screens/expected.json`. Unfamiliar screens go to `docs/screens/unlabeled/` with a table mae fills in; `python -m sxs label` files them.
- **Rationale**: mae (2026-11-04): "We should have a bank of unfamiliar/undefined screens that I can manually label and build context on"; 190 flat files were slow to browse.
- **Alternatives considered**: keep the flat folder until ~300 screens (my earlier suggestion); delete unreferenced screens (mae: keep them).
- **Status**: Accepted
