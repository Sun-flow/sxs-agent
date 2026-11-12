# 2026-11-11 18:38 · Stamina Spend loop designed (Claude Code, cloud)

- mae (item 8 in the capture thread): stamina regenerates and must be spent; above 150, spending is an important side objective; one daily quest needs it; report unplanned stamina drops with a pre-roll capture.
- Draft `docs/loops/stamina.md` (offline, nothing built): three trigger levels (urgent 250+, side above 150, daily "consume 30"), 70 floor kept, one material per run picked by need (rank first at cap, then what strengthen ran short of, else policy), `spend` wraps `Gatherer.collect`, moves before the daily quest claim, exploration hands off at safe points and never taps stamina objects itself, unplanned-drop log.
- Open: six questions for mae at the bottom of the page; rules filed by the docs thread after her edit.
