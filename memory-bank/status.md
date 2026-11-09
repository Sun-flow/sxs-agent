# Status

> **Last updated**: 2026-11-09
> Where the work stands now. Past sessions: `log.md`. How a builder works: `playbook.md`.

## Game state (2026-11-05 05:05Z, mae's PC)

- gromb2: Mage, Apprentice II, Lv 24/30, power 22.4K (skills Lv 17-18 after Quick Upgrade; Cart Stone and Wood Lv 5). Rolla ~72.7K, Dawnium ~1.85K (never spent by the bot), stamina ~234/300, Abundance Leaves 450, 1 Shapeshifting Mirror (unused).
- Explored and blessed: Originisle; Verdantglade I-IV area quests done; Verdantglade III 100%; Auroradrasil 100% and blessed (Lost Goddess Statue, 2026-11-05). Drasilgard town visited (Chief, Hermes, Carol). Verdantglade V 78% (quest "Explore Verdantglade V"). Unexplored: Jungle Camp 12.6K, Zephyr Vale, Monolith Ruins I, Troll Lair 17K, Verdantglade VI, Wildbloom Coast 20.4K.
- Rank: Apprentice III needs Lv 30, leaves 16/5, Bellflower 4/30 (source: Verdantglade Flower Harvest in Moonveil Woods; the plants in Drasilgard are decoration), Rolla 10.5K. Blocked on Lv 30.
- Fantasia Ascent Moonveil Woods: Auto Challenge climbed to F24+ in the background (2026-11-04).
- Social features open (R-057): NPC companions Akane, Qin, Killian were invited for Auroradrasil (rank B).

## Strengthening and the Cart (2026-11-05 early morning)

- Strengthening done: power 22.4K. `python -m sxs upgrade` now always opens the Skill page (Quick Upgrade shows blue arrows, not a red "!"). At the end the Character screen's weapon slot showed a red "!" and chest/boots blue arrows: recheck with `gearswap` and the gear pass.
- Cart: `python -m sxs cart` (also daily step `cart_upgrade`) raises Stone and Wood evenly (R-136). Both are Lv 5, capped: Lv 6 needs Blessing Lv 6 (the bed's Blessing Level). Costs are Wood + Stone + Rolla only. ❓ How the Blessing Level rises (blessing statues? R-035, R-070).

## Works (all on main, PRs #1–#30)

- Hands and eyes: MaaFramework device layer, state detector, `python -m sxs` CLI (every loop runs as `python -m sxs <loop>`, contract in `sxs/core/loop.py`), offline detector check, smoke test (`docs/step2-hands-and-eyes.md`).
- Quest line and exploration: `sxs.loops.explore --chain`, `sxs.loops.tutorial`, `sxs.actions.goto`, `sxs.loops.fogwalk`, `sxs.vision.minimap`, `sxs.loops.roam` (Roam Loop), `sxs.loops.tower` (`docs/step3-explore.md`).
- Dailies: `sxs.loops.daily` runs sign-in, Cart, Growth Trial, Fantasia Ascent, Material Realms, quest claims, bed EXP, Mall gifts, Vendor free stamina, guild donate / Forge AFK / Conquest, gather, strengthen + Upgrade Loop (`docs/step4-dailies.md`).
- Upgrades and gathering: `sxs.loops.upgrade` follows character-screen badges (banded gear, Resonance, Quick Upgrade, ascension, class levels, rank; relic banding defined ahead); `sxs.loops.gather` `collect(target)` for ore, sand, essence, Rolla, Bellflower (`docs/step5-upgrades.md`).
- Pulls: `sxs.loops.pray` (handler-approved, x10 only). Shop survey: `scripts/shop_survey.py`, tables in `docs/shop-tables.md`.
- Game knowledge: `game/rules/` (by topic) and `game/nav-graph.json`.

## In progress

Format: `- what — branch, PR, environment (started)`. Remove the line when it merges or is dropped.

- Exploration drivers per mae (2026-11-05): roam picks the lowest-CP unblessed zone, blesses statues whose area-map "!" is lit, ends with a fog walk; fog walk reaches objects through the big map, follows passable ground into fog, keeps to its zone (R-132), free pickups and fights only in unexplored areas (R-065), collectibles store (R-131) — `claude/project-thread-ieaqnz` (latest commits beyond #41), mae's PC. Open: (1) at the zoomed-out area map OCR merges neighbouring labels and loses percentages (read at a closer zoom with pans instead); (2) Jungle Camp run (2026-11-05): approach from Drasilgard, big-map walks mostly "no_move", no % gained; the walk into Jungle Camp needs a better entry point; (3) progress readings with OCR noise in coordinates count as movement, so a stuck run can be extended; (4) the tutorial glow on the Companions "Invite" isn't found by the highlight finder (interrupt layer PR #40).

- Loop diagrams (mae, 2026-11-09): `docs/loops/` has a Mermaid page per loop, a screen-by-screen table and `docs/loops/open-questions.md` (15 places where code, rules and mae's asks disagree; mae's 2026-11-09 answers applied: blue-pip gear enhance trigger, gather fights guards, `get_stronger` for explore, one tower climb a day from any loop, tutorial stops on class choices; none run live yet) — `claude/project-thread-aqcucg`, PR pending, cloud. Follow-up proposed in `docs/loops/README.md`: per-loop flow specs the loops read, so the diagrams become the source of truth.

## Next (in order)

- Interrupt layer (`docs/interrupts.md`): ran under all 8 live runs of the strengthening session (2026-11-05) with no false trigger; still to watch live: the tutorial pause/resume path. Live check that a tutorial highlight on the island map pauses Fog Walk and resumes it; capture frames of tutorials on unknown overlays so the row can learn them. Companions invite is followed (mae 02:23: inviting is fine).

0. Progress tracker live check: run `python -m sxs progress` on rif-love-su, confirm the profile/Journal/guild/area readings, then the daily run's report. Routes still missing: the bag (Lumium, Material Realm tools), relics (not unlocked).

1. Conquest with tries left: watch it live after the 13:00Z reset.
2. Fog Walk pickup detection on screen (glowing items): the minimap barely shows pickups under the unexplored shadow (R-086).
3. Verdantglade III entrance: probably a quest unlock (R-084).
4. Grand Iron/Sand Mine special nodes: seen in chat, not located (R-109). Lead: a gold-ore icon with a red "!" on the area map in Verdantglade V, possibly a mine.
5. Older: test HP logic when HP drops below 70% while alive; minimap classifier per area palette; model supervisor for `unknown_*` stops.

## Waiting on mae

- Remaining questions in `docs/loops/open-questions.md`: Forge-full fallback (Q6), Notice sign-ins and Exploration Goals in the daily loop (Q7), Cart tie-break (Q8). Settled 2026-11-09: Q3, Q4, Q5, Q9, Q10, Q11, bed speed-up timing.

- Label the 9 screens in `docs/screens/unlabeled/README.md` (and any new ones `python -m sxs bank` adds), then `python -m sxs label`.

- Fill the Buy? column in `docs/shop-tables.md`; buy nothing until then.
- (R-116 changed 22:17: mae retracted the Home collect-all; Goals tabs are claimed per tab by a claim-goals task, builder to build.)
- A blue-aura pickup crop, and the name of the Apprentice III flower item.
- Is co-op content in iteration 1? Hide chat channels in Settings → Game → Social Settings (cuts OCR noise; a settings change, so mae's call)?

## Known problems

- Auroradrasil sits inside Verdantglade V on the map, so the fog walk's zone check (R-132) bounces the bot out when a walk lands there. mae (03:10): Auroradrasil is its own zone, so the goto for Verdantglade V must land on V's own ground (R-132). Verdantglade V is at 78%.
- Minimap classifier was tuned in Verdantglade II; in Highland Woods it labels walkable explored tiles as walls.
- The island-map camera doesn't follow the player: locate the player first (the "gromb2" label or the player edge pointer).
- Quick Heal from the "badly wounded" dialog didn't seem to heal; Quick Heal from the portrait works.
- `equip_charms` taps the locked 4th charm slot and logs "loadout editor did not open" (harmless; skip locked slots).
- Untested live: Conquest with tries left; roam's statue walk (`bless_near`); the skills/class/rank passes inside the Upgrade Loop; the green-timer special-node detector.
- Docs say every loop logs a heartbeat; only `sxs/loops/explore.py` does.
- Post-rank tutorial overlays read as unknown; `nav.go_home` failed on one (R-036).
