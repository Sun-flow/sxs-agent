# 2026-11-10 06:33 · Item and currency symbol catalogue (Claude Code, cloud)

- mae wants the detector to name item, material and currency symbols, each read from its own popup, and set a standing rule: any unrecognised material or currency symbol gets identified and catalogued. A new RC thread "Map item and currency symbols" collects them on the emulator.
- Built: `resource/items/` (`items.json` + `icons/`, 15 items seeded from the Vendor Booth screens, names from shop rows, popups still to read), `python -m sxs items [add|find]`, detector class `item_icon` with an `item` id on labeler boxes ("which item?" menu), `prelabel --items` auto-drafts by multi-scale template matching, `dataset --items each|one`. Checks in `tests/check_detect_data.py`.
- Open: popup reads for every item; `prelabel --items` on mae's labels worktree once she has confirmed the current drafts (to avoid a labels.json conflict).
