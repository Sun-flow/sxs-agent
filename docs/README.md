# docs

Design notes, one per plan step or design question. The code is the source of truth; these explain how and why.

## Which doc

The list is built from the docs themselves, so no branch ever edits a shared table:

```
python3 scripts/index.py docs     # | File | Read when |, one row per docs/*.md and per subfolder
```

The design notes for the plan steps are `step1-emulator-and-game.md` to `step6-clear-zone.md`. Subfolders: `loops/`
(a diagram of every loop, index `loops/README.md`), `screens/` (reference screenshots, index `screens/README.md`),
`archive/` (history only, never instructions).

## Adding a doc

Put one line under the doc's `#` title saying when to read it; that line is its index entry:

```
# Portals: teleporting on the big map

<!-- index: How portals are found, when the bot teleports, and what it does with a portal it opened by accident -->
```

A new subfolder gets a `README.md` with the same line. `python3 tests/check_repo.py` fails on a doc without one.
