# Status

> **Last updated**: 2026-11-04
> Where the work stands now. Past sessions: `log.md`. How a builder works: `playbook.md`.

## Game state (2026-11-04 11:40, rif-love-su)

- gromb2 on server Forgehall: Mage, Apprentice II, Lv 23/30, power 17.4K. Dawnium ~1.17K (never spent by the bot), Rolla ~33.6K, stamina ~122, Stellatie 0, Guild Tokens 760. Guild karsa_1515, gathering at the Forge.
- Explored and blessed: Originisle I–V; Verdantglade I, II; Moonveil Woods; Stone Ruins I; Highland Woods; Damp Woods. Verdantglade III (12K, 0%) has no entrance on foot from Moonveil Woods (R-084). Fantasia Ascent Moonveil Woods F1–5.
- Next rank (Apprentice III) needs Lv 30, 5 green leaf (have 9), 30 of an unnamed flower item, 10.5K Rolla (R-118).

## Works (all on main, PRs #1–#30)

- Hands and eyes: MaaFramework device layer, state detector, `python -m sxs` CLI (every loop runs as `python -m sxs <loop>`, contract in `sxs/core/loop.py`), offline detector check, smoke test (`docs/step2-hands-and-eyes.md`).
- Quest line and exploration: `sxs.loops.explore --chain`, `sxs.loops.tutorial`, `sxs.actions.goto`, `sxs.loops.fogwalk`, `sxs.vision.minimap`, `sxs.loops.roam` (Roam Loop), `sxs.loops.tower` (`docs/step3-explore.md`).
- Dailies: `sxs.loops.daily` runs sign-in, Cart, Growth Trial, Fantasia Ascent, Material Realms, quest claims, bed EXP, Mall gifts, Vendor free stamina, guild donate / Forge AFK / Conquest, gather, strengthen + Upgrade Loop (`docs/step4-dailies.md`).
- Upgrades and gathering: `sxs.loops.upgrade` follows character-screen badges (banded gear, Resonance, Quick Upgrade, ascension, class levels, rank; relic banding defined ahead); `sxs.loops.gather` `collect(target)` for ore, sand, essence, Rolla, Bellflower (`docs/step5-upgrades.md`).
- Pulls: `sxs.loops.pray` (handler-approved, x10 only). Shop survey: `scripts/shop_survey.py`, tables in `docs/shop-tables.md`.
- Game knowledge: `game/rules/` (by topic) and `game/nav-graph.json`.

## In progress

Format: `- what — branch, PR, environment (started)`. Remove the line when it merges or is dropped.

- Package restructure (mae's proposals 1–5): `sxs/` split into `core/ vision/ policy/ actions/ loops/`, shared helpers (screen coordinates, OCR, heal, reward/dialogue pass-through, watchdog, unstick), explore split, one loop contract and `python -m sxs <loop>` — `claude/project-thread-kb6hi9`, cloud (2026-11-04). Offline checks pass; untested live.
- Screenshot folders for `docs/screens/` and a bank of unlabelled screens for mae: plan posted, waiting for mae's go.

## Next (in order)

1. Conquest with tries left: watch it live after the 13:00Z reset.
2. Fog Walk pickup detection on screen (glowing items): the minimap barely shows pickups under the unexplored shadow (R-086).
3. Verdantglade III entrance: probably a quest unlock (R-084).
4. Grand Iron/Sand Mine special nodes: seen in chat, not located (R-109).
5. Older: test HP logic when HP drops below 70% while alive; minimap classifier per area palette; model supervisor for `unknown_*` stops.

## Waiting on mae

- Fill the Buy? column in `docs/shop-tables.md`; buy nothing until then.
- Show where the Home "collect all goals" control is (R-116).
- A blue-aura pickup crop, and the name of the Apprentice III flower item.
- Is co-op content in iteration 1? Hide chat channels in Settings → Game → Social Settings (cuts OCR noise; a settings change, so mae's call)?

## Known problems

- Minimap classifier was tuned in Verdantglade II; in Highland Woods it labels walkable explored tiles as walls.
- The island-map camera doesn't follow the player: locate the player first (the "gromb2" label or the player edge pointer).
- Quick Heal from the "badly wounded" dialog didn't seem to heal; Quick Heal from the portrait works.
- `equip_charms` taps the locked 4th charm slot and logs "loadout editor did not open" (harmless; skip locked slots).
- Untested live: Conquest with tries left; roam's statue walk (`bless_near`); the skills/class/rank passes inside the Upgrade Loop; the green-timer special-node detector.
- Docs say every loop logs a heartbeat; only `sxs/loops/explore.py` does.
- Post-rank tutorial overlays read as unknown; `nav.go_home` failed on one (R-036).
