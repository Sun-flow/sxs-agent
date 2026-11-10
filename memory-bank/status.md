# Status

> **Last updated**: 2026-11-09
> Where the work stands now. Past sessions: `log.md`. How a builder works: `playbook.md`.

## Game state (2026-11-05 05:05Z, mae's PC)

- gromb2: Mage, Apprentice II, Lv 30/30 (cap; bed EXP claim took Lv 24 to 30), power about 28.4K (2026-11-10: gear swap and enhance, boots 2050 to 2110; rank Goals claimed; skills Lv 17-18; Cart Stone and Wood Lv 5). Rolla ~72.7K, Dawnium ~1.85K (never spent by the bot), stamina ~234/300, Abundance Leaves 450, 1 Shapeshifting Mirror (unused).
- Explored and blessed: Originisle; Verdantglade I-IV area quests done; Verdantglade III 100%; Auroradrasil 100% and blessed (Lost Goddess Statue, 2026-11-05). Drasilgard town visited (Chief, Hermes, Carol). Verdantglade V 100% and blessed (2026-11-10: its Goddess Statue near the north-east edge, R-070; Blessing Level 5 → 6, AFK EXP 592 → 608). Sealed Stone Gate on V's north edge (135, 126) is the way into Verdantglade VI: rank-gated (Apprentice II), unlocked free by run 10 at about 03:32 (R-145); runs 11–17 took VI to 87%. Zones at 100%: Originisle I–V, Verdantglade I–III and V, Moonveil Woods, Stone Ruins I, Highland Woods, Damp Woods (❓ recheck: the tree's 100% came from three readings with no %), Auroradrasil, Jungle Camp, Wildbloom Coast (0 → 100% and blessed by the bot on its own, 2026-11-10 03:20). Jungle Camp 12.6K 100% and blessed (2026-11-10: Lost Goddess Statue, Home EXP +1%, Raw Ore +1%; the free Lucky Wheel spin was the last object, R-147; ways in from Verdantglade III (142, 84) and Drasilgard (138, 84)). Hidden Camp: inaccessible until we have a Magic Drill for its Boulder Blockade; not explored for now, and roam skips it (mae, R-151); behind the blockade: pickups (coins, apple, chests) and a Lost Goddess Statue. Verdantglade VI 87% (run 18 going for 100%). Unexplored: Zephyr Vale, Monolith Ruins I, Troll Lair 17K.
- Rank: Apprentice III now only needs Bellflowers, 4/30 (source: Verdantglade Flower Harvest in Moonveil Woods; the plants in Drasilgard are decoration). Lv 30, leaves 16/5 and Rolla 10.5K are met.
- Fantasia Ascent Moonveil Woods: Auto Challenge climbed to F24+ in the background (2026-11-04).
- Social features open (R-057): NPC companions Akane, Qin, Killian were invited for Auroradrasil (rank B).

## Strengthening and the Cart (2026-11-05 early morning)

- Strengthening, live-validated (2026-11-09/10): gear swap weapon 1490 to 1960, head 1170 to 1820; enhance weapon +21 to +24, head +18 to +23, chest +15 to +21, boots +15 to +20; power 22.4K to about 24.5K. `python -m sxs upgrade` always opens the Skill page; the gear pass finds blue enhance pips and leaves out pieces short of their own material (the weapon's +25 needs red ore; enough is now in hand). To do: enhance lower-level pieces first (mae, R-092).
- Cart: `python -m sxs cart` (also daily step `cart_upgrade`) raises Stone and Wood evenly (R-136). Both are Lv 6 (2026-11-10); Lv 7 needs Blessing Lv 7. Costs are Wood + Stone + Rolla only. Blessing Level rises when a zone's Goddess Statue is unlocked (R-035, R-070). Chrono Sand unlocked live (free, R-137).

## Works (all on main, PRs #1–#30)

- Hands and eyes: MaaFramework device layer, state detector, `python -m sxs` CLI (every loop runs as `python -m sxs <loop>`, contract in `sxs/core/loop.py`), offline detector check, smoke test (`docs/step2-hands-and-eyes.md`).
- Quest line and exploration: `sxs.loops.explore --chain`, `sxs.loops.tutorial`, `sxs.actions.goto`, `sxs.loops.fogwalk`, `sxs.vision.minimap`, `sxs.loops.roam` (Roam Loop), `sxs.loops.tower` (`docs/step3-explore.md`).
- Dailies: `sxs.loops.daily` runs sign-in, Cart, Growth Trial, Fantasia Ascent, Material Realms, quest claims, bed EXP, Mall gifts, Vendor free stamina, guild donate / Forge AFK / Conquest, gather, strengthen + Upgrade Loop (`docs/step4-dailies.md`).
- Upgrades and gathering: `sxs.loops.upgrade` follows character-screen badges (banded gear, Resonance, Quick Upgrade, ascension, class levels, rank; relic banding defined ahead); `sxs.loops.gather` `collect(target)` for ore, sand, essence, Rolla, Bellflower (`docs/step5-upgrades.md`).
- Pulls: `sxs.loops.pray` (handler-approved, x10 only). Shop survey: `scripts/shop_survey.py`, tables in `docs/shop-tables.md`.
- Game knowledge: `game/rules/` (by topic) and `game/nav-graph.json`.
- Screen labeler (2026-11-09, branch `claude/project-thread-genq9f`): `python -m sxs labeler` web page where mae names screens and boxes buttons, text, icons; boxes in `docs/screens/labels.json`, template crops in `resource/image/labels/`, matched by `sxs/vision/labels.py`. No boxes drawn yet: mae's first pass over the bank is next.

## In progress

Format: `- what — branch, PR, environment (started)`. Remove the line when it merges or is dropped.

- Exploration drivers per mae (2026-11-05): roam picks the lowest-CP unblessed zone, blesses statues whose area-map "!" is lit, ends with a fog walk; fog walk reaches objects through the big map, follows passable ground into fog, keeps to its zone (R-132), free pickups and fights only in unexplored areas (R-065), collectibles store (R-131) — `claude/project-thread-ieaqnz` (latest commits beyond #41), mae's PC. Open: (1) at the zoomed-out area map OCR merges neighbouring labels and loses percentages (closer zoom with pans written on `claude/project-thread-sesbe9`, not yet live); (2) Jungle Camp run (2026-11-05): approach from Drasilgard, big-map walks mostly "no_move", no % gained; the walk into Jungle Camp needs a better entry point; (3) progress readings with OCR noise in coordinates count as movement, so a stuck run can be extended; (4) the tutorial glow on the Companions "Invite" isn't found by the highlight finder (interrupt layer PR #40).

- Zone borders, location tree, closer-zoom survey, Cart unlock (mae, 2026-11-09) — `claude/project-thread-sesbe9`, in #43 and #46; live in Verdantglade V (78 to 100%) and the Cart unlock. Commit `resource/world/zones.json` after live runs: it is the bot's map.

- Loop diagrams (mae, 2026-11-09): `docs/loops/` has a Mermaid page per loop, a screen-by-screen table and `docs/loops/open-questions.md` (15 places where code, rules and mae's asks disagree; mae's 2026-11-09 answers applied: blue-pip gear enhance trigger, gather fights guards, `get_stronger` for explore, one tower climb a day from any loop, tutorial stops on class choices; none run live yet) — `claude/project-thread-aqcucg`, PR pending, cloud. Follow-up proposed in `docs/loops/README.md`: per-loop flow specs the loops read, so the diagrams become the source of truth.

- Roam (2026-11-10): runs 1–4 gained nothing (label reads, Auroradrasil trap, Rankings card; all fixed). Runs 5–7 ended early on joined labels (fixed: the tree decides). Wildbloom Coast done 0 → 100%. Open stuck point: Monolith Ruins I (a monster tapped twice, no fight started; its label unread). Run 9 targeted Zephyr Vale, Monolith Ruins I, Verdantglade VI, Troll Lair. Run 10 unlocked the Sealed Stone Gate into Verdantglade VI (R-145); runs 11–17 explored VI to 87%, fixing the profile popup (ring over our own character, R-142), Class page taps (HUD ring, back arrow on gear and class cards, R-030), clipped labels in the per-step zone check (R-140) and the portal under VI's label (R-152); each zone now records its `objectives`. Run 18 going for VI 100%.
- Jungle Camp blessed (2026-11-10): the last 7% was the Lucky Wheel's free first spin (blue "!", mae); Lost Goddess Statue unlocked.

## Next (in order)

- From mae's rules (2026-11-09), code to do: gather fights a monster guarding a pickup, then resumes it (R-139); a separate bed free speed-up task, called after the day's exploration, not in dailies (R-035); the gear pass treats a blue arrow pip on a slot as "enhance" (R-088); pickup reference crops for the fog walk (R-131).

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

- Auroradrasil sits inside Verdantglade V on the map, so the fog walk's zone check (R-132) bounces the bot out when a walk lands there. mae (03:10): Auroradrasil is its own zone, so the goto for Verdantglade V must land on V's own ground (R-132). Verdantglade V reached 100% on 2026-11-09.
- Minimap classifier was tuned in Verdantglade II; in Highland Woods it labels walkable explored tiles as walls.
- The island-map camera doesn't follow the player: locate the player first (the "gromb2" label or the player edge pointer).
- Quick Heal from the "badly wounded" dialog didn't seem to heal; Quick Heal from the portrait works.
- `equip_charms` taps the locked 4th charm slot and logs "loadout editor did not open" (harmless; skip locked slots).
- Untested live: Conquest with tries left; roam's statue walk (`bless_near`); the skills/class/rank passes inside the Upgrade Loop; the green-timer special-node detector.
- Docs say every loop logs a heartbeat; only `sxs/loops/explore.py` does.
- Post-rank tutorial overlays read as unknown; `nav.go_home` failed on one (R-036).
