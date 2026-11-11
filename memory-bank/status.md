# Status

> **Last updated**: 2026-11-11 (Clear Zone live-tested)
> Where the work stands now. Past sessions: `log.md`. How a builder works: `playbook.md`.

## Game state (2026-11-05 05:05Z, mae's PC)

- gromb2: Mage, Apprentice II, Lv 30/30 (cap; bed EXP claim took Lv 24 to 30), power about 28.4K (2026-11-10: gear swap and enhance, boots 2050 to 2110; rank Goals claimed; skills Lv 17-18; Cart Stone and Wood Lv 5). Rolla ~72.7K, Dawnium ~1.85K (never spent by the bot), stamina ~234/300, Abundance Leaves 450, 1 Shapeshifting Mirror (unused).
- Explored and blessed: Originisle; Verdantglade I-IV area quests done; Verdantglade III 100%; Auroradrasil 100% and blessed (Lost Goddess Statue, 2026-11-05). Drasilgard town visited (Chief, Hermes, Carol). Verdantglade V 100% and blessed (2026-11-10: its Goddess Statue near the north-east edge, R-070; Blessing Level 5 → 6, AFK EXP 592 → 608). Sealed Stone Gate on V's north edge (135, 126) is the way into Verdantglade VI: rank-gated (Apprentice II), unlocked free by run 10 at about 03:32 (R-145); runs 11–18 explored VI to 100%; its Goddess Statue blessed (Blessing Level 6 → 7, Cart max 7, AFK EXP 620 → 636; 2026-11-10). Explore Verdantglade VI gave a quest gift; next quest Explore Verdantglade VII (already 60%). Zones at 100%: Originisle I–V, Verdantglade I–III and V, Moonveil Woods, Stone Ruins I, Highland Woods, Damp Woods (❓ recheck: the tree's 100% came from three readings with no %), Auroradrasil, Jungle Camp, Wildbloom Coast (0 → 100% and blessed by the bot on its own, 2026-11-10 03:20). Jungle Camp 12.6K 100% and blessed (2026-11-10: Lost Goddess Statue, Home EXP +1%, Raw Ore +1%; the free Lucky Wheel spin was the last object, R-147; ways in from Verdantglade III (142, 84) and Drasilgard (138, 84)). Hidden Camp: inaccessible until we have a Magic Drill for its Boulder Blockade; not explored for now, and roam skips it (mae, R-151); behind the blockade: pickups (coins, apple, chests) and a Lost Goddess Statue. Verdantglade VI 100% and blessed. In progress: Verdantglade VII 60% (main quest), Troll Lair 42% (17K). Unexplored (0%): Zephyr Vale, Monolith Ruins I, Grotto Peninsula 23K, Rabbit Vault, Stagnant Jungle; Sunrise Isle never read on the big map.
- Rank: Apprentice III now only needs Bellflowers, 4/30 (source: Verdantglade Flower Harvest in Moonveil Woods; the plants in Drasilgard are decoration). Lv 30, leaves 16/5 and Rolla 10.5K are met.
- Fantasia Ascent Moonveil Woods: Auto Challenge climbed to F24+ in the background (2026-11-04).
- Social features open (R-057): NPC companions Akane, Qin, Killian were invited for Auroradrasil (rank B).

## Strengthening and the Cart (2026-11-05 early morning)

- Strengthening, live-validated (2026-11-09/10): gear swap weapon 1490 to 1960, head 1170 to 1820; enhance weapon +21 to +24, head +18 to +23, chest +15 to +21, boots +15 to +20; power 22.4K to about 24.5K. `python -m sxs upgrade` always opens the Skill page; the gear pass finds blue enhance pips and leaves out pieces short of their own material (the weapon's +25 needs red ore; enough is now in hand). To do: enhance lower-level pieces first (mae, R-092).
- Cart: `python -m sxs cart` (also daily step `cart_upgrade`) raises Stone and Wood evenly (R-136). Both are Lv 6 (2026-11-10); Lv 7 needs Blessing Lv 7. Costs are Wood + Stone + Rolla only. Blessing Level rises when a zone's Goddess Statue is unlocked (R-035, R-070). Chrono Sand unlocked live (free, R-137).

## Works (all on main, PRs #1–#30)

- Hands and eyes: MaaFramework device layer, state detector, `python -m sxs` CLI (every loop runs as `python -m sxs <loop>`, contract in `sxs/core/loop.py`), offline detector check, smoke test (`docs/step2-hands-and-eyes.md`).
- Quest line and exploration: `sxs.loops.explore --chain`, `sxs.loops.tutorial`, `sxs.actions.goto`, `sxs.loops.clear` (Clear Zone, replaced the Fog Walk 2026-11-10; `docs/step6-clear-zone.md`), `sxs.vision.minimap`, `sxs.loops.roam` (Roam Loop), `sxs.loops.tower` (`docs/step3-explore.md`).
- Dailies: `sxs.loops.daily` runs sign-in, Cart, Growth Trial, Fantasia Ascent, Material Realms, quest claims, bed EXP, Mall gifts, Vendor free stamina, guild donate / Forge AFK / Conquest, gather, strengthen + Upgrade Loop (`docs/step4-dailies.md`).
- Upgrades and gathering: `sxs.loops.upgrade` follows character-screen badges (banded gear, Resonance, Quick Upgrade, ascension, class levels, rank; relic banding defined ahead); `sxs.loops.gather` `collect(target)` for ore, sand, essence, Rolla, Bellflower (`docs/step5-upgrades.md`).
- Pulls: `sxs.loops.pray` (handler-approved, x10 only). Shop survey: `scripts/shop_survey.py`, tables in `docs/shop-tables.md`.
- Game knowledge: `game/rules/` (by topic) and `game/nav-graph.json`.
- Screen labeler (2026-11-09, branch `claude/project-thread-genq9f`): `python -m sxs labeler` web page where mae names screens and boxes buttons, text, icons; boxes in `docs/screens/labels.json`, template crops in `resource/image/labels/`, matched by `sxs/vision/labels.py`. No boxes drawn yet: mae's first pass over the bank is next.

## In progress

Format: `- what — branch, PR, environment (started)`. Remove the line when it merges or is dropped.

- **Clear Zone replaces the Fog Walk** (mae, 2026-11-10 23:48: "scrap it") — `claude/project-thread-e1kt6z`, cloud, PR to merge; includes the vj9wvt exploration commits. `python -m sxs clear --area NAME`; roam calls it per zone. Every leg has a named objective (quest ring, known object, minimap object, big-map object, fog frontier); progress = % or an object cleared; stops `no_objective` / `no_progress` (4 legs without gain). Offline check `tests/check_clear.py`. **Live-tested 2026-11-11 (runs 15-29)**: IX, X and Bubble Lake to 100%; quest ring, minimap and big-map legs, item re-taps, the guard-group leg (XI entrance), auto-bless (Bubble Lake's Lost Goddess Statue), puzzle/lore/blocker stops. Not yet live: the frontier source (fog-shrink check, `player_dot` fallback), one-option dialogues, `resource/policy/dialogue_choices.json`.

- Exploration builder (2026-11-10 evening) — `claude/project-thread-vj9wvt` (off main after #53), mae's PC, no PR yet (coordinator opens it). Game state ~23:40Z: Lv 30, power 28.5K, stamina 300, **Blessing Lv 9**, **Cart Stone and Wood Lv 9** (Lv 10 needs Blessing 10). **Verdantglade VIII 0 → 100% and blessed** (way in: VII's south edge at (102,110), a monster group on the line; the Drasilgard side is cliffs). Main quest now **Explore Verdantglade IX** (30K, south of VIII). **Troll Lair** was really 100% (label hidden under Verdantglade IV's; OCR "rolLall"): Lost Goddess Statue unlocked. **Zephyr Vale 0 → 100% and blessed** through a **Gate of Wind** (opened with companion Akane, R-159 proposed). **Monolith Ruins I**: way in from V at (151,122) → (155,119); only a 3-pedestal light puzzle there (skipped, R-153). **Bubble Lake** (new zone, 0%) is behind a 30.5K Gate of Power on VIII's west edge (109,83). Leafy Corridor and Verdantglade IV recheck: see log.
- Exploration builder (2026-11-10 morning) — `claude/project-thread-dloc9z` (merged). **Handed off 2026-11-10 ~06:30Z** (mae: the emulator goes to a new thread mapping currency/material/item symbols). Game state then: Lv 30, power 28.5K, **Blessing Lv 8** (Cart max 8; Stone/Wood still at 6), stamina ~291. Verdantglade VII 60 → 100%, Goddess Statue unlocked (by hand: the statue walk failed, now fixed). Quest now "Explore Verdantglade VIII" 0/100 (27K; reached from the Drasilgard side near map (129,100); its quest ring pointed into fog west of (129,94) that the walk couldn't enter). New zones in the tree: Verdantglade VIII 27K, Leafy Corridor 25.5K, Monolith Ruins II. **Monolith Ruins II is blocked** by Fonik's box puzzle at about (88,104) ("Present a Golden Beetle"; Akane's tutorial gave one): mae (06:25): **never spend Golden Beetles**; ignore puzzle areas for now (solving puzzles in code is a later task); the walk takes Leave. Monolith Ruins I: still no known way in (VII borders Monolith Ruins II, not I). Zephyr Vale, Troll Lair (42%), Verdantglade IV recheck not reached.
- Run setup: `$env:SXS_ADB_ADDRESS='127.0.0.1:16416'; $env:SXS_INFERENCE='directml'` (mae approved the GPU 06:12; `setx` was blocked for the builder, mae can run `setx SXS_INFERENCE directml` once). Trace runs: `scripts/tap_trace.py roam AREA MIN`.
- Open stuck points: survey OCR still reads one zone's % line under a neighbour's name (VIII's 27K/0% under VII; the blessed guard protects explored zones only); minimap names lose a trailing I (Monolith Ruins II → "I ."; handled only for the zone being explored); the big-map picker once picked a dark point far outside the zone (VIII run 8); tapping an explored-zone monster starts a stamina fight (5 stamina, by hand); Troll Lair label flip; Sunrise Isle never read.
- Roam (2026-11-10): runs 1–4 gained nothing (label reads, Auroradrasil trap, Rankings card; all fixed). Runs 5–7 ended early on joined labels (fixed: the tree decides). Wildbloom Coast done 0 → 100%. Open stuck point: Monolith Ruins I (a monster tapped twice, no fight started; its label unread). Run 9 targeted Zephyr Vale, Monolith Ruins I, Verdantglade VI, Troll Lair. Run 10 unlocked the Sealed Stone Gate into Verdantglade VI (R-145); runs 11–17 explored VI to 87%, fixing the profile popup (ring over our own character, R-142), Class page taps (HUD ring, back arrow on gear and class cards, R-030), clipped labels in the per-step zone check (R-140) and the portal under VI's label (R-152); each zone now records its `objectives`. Run 18 finished VI; blessed (Blessing Lv 7).

- Item symbol survey (mae, 2026-11-10) — `claude/project-thread-6juae0`, mae's PC, no PR yet (hand to the docs thread). 78 catalogue items read from their cards; survey notes `docs/screens/items/README.md`. Left: `unknown_1` name from mae, skill shards, Carnival Sign-In, Kingdom shop, Mall, mail.
- UI detector (mae, 2026-11-10): screen-check speed-ups merged (#48; mae's PC 6.4 s -> 1.3 s median, 1.0 s with `SXS_INFERENCE=directml`). Step 1 built: detector classes, labeler class menu + drafts, `python -m sxs prelabel` (365 drafts committed), `python -m sxs dataset` — `claude/project-thread-wuht8i`, new PR, cloud. Waiting on mae: check drafts in the labeler, Roboflow account. Plan: `docs/detector-design.md`.
- Item and currency symbol catalogue (mae, 2026-11-10): `resource/items/` + `python -m sxs items`, class `item_icon`, `prelabel --items`, `dataset --items each|one` — `claude/project-thread-wuht8i`, cloud. The RC thread "Map item and currency symbols" fills it from popups on the emulator. Standing rule: any unrecognised material or currency symbol gets identified (tap it, read the popup) and added.

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
