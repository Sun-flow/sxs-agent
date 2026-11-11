# UI detector step 1 and item catalogue (mae, 2026-11-10)

Branch: `claude/project-thread-wuht8i` · PR: new PR · Where: cloud

- UI detector (mae, 2026-11-10): screen-check speed-ups merged (#48; mae's PC 6.4 s -> 1.3 s median, 1.0 s with `SXS_INFERENCE=directml`). Step 1 built: detector classes, labeler class menu + drafts, `python -m sxs prelabel` (365 drafts committed), `python -m sxs dataset` — `claude/project-thread-wuht8i`, new PR, cloud. Waiting on mae: check drafts in the labeler, Roboflow account. Plan: `docs/detector-design.md`.
- Item and currency symbol catalogue (mae, 2026-11-10): `resource/items/` + `python -m sxs items`, class `item_icon`, `prelabel --items`, `dataset --items each|one` — `claude/project-thread-wuht8i`, cloud. The RC thread "Map item and currency symbols" fills it from popups on the emulator. Standing rule: any unrecognised material or currency symbol gets identified (tap it, read the popup) and added.
