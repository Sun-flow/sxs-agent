# Session Log Archive

Older entries moved from `memory-bank/log.md`, newest first.

### 2026-11-04 (evening) · Game docs: fight odds, exploration kinds, gear replace, short loops (Claude Code, cloud)
- mae: take fights against up to 25% more CP (new R-127); two exploration kinds, quest-progression and fog-walking (R-065); a gear "!" means replace, as its own task (R-088); loops run 1-2 min with progress-based exits (`memory-bank/notes.md`). Merged main after the restructure (#30).

### 2026-11-04 (evening) · Package restructure and loop contract (Claude Code, cloud)
- mae approved structural proposals 1–5 (21:25). Branch `claude/project-thread-kb6hi9` from main: `sxs/` is now `core/` (device, state, nav, replay, marks, paths, `ui.py` coordinates, `loop.py` contract), `vision/` (ocr, hp, hud, player, tracker, pickups, gift, badges, minimap), `policy/` (decide, claims), `actions/` (heal, rewards, goto, common pass-through, watchdog, unstick, camera), `loops/` (one module per loop, REGISTRY in `__init__.py`). `explore.py` became an `Explorer` class with one method per screen. Every loop exposes `LOOP` and runs as `python -m sxs <loop>`, logs `[Result X] status` and prints one JSON readout. `scripts/explore.py` renamed `scripts/probe.py`. New `tests/check_loops.py`; `tests/check_repo.py` flags the old `python -m sxs.X` form. Bellflower reference moved to `docs/screens/icons/`. Spending safeguards unchanged (pray gates now return `refused: ...`, exit 2).
- mae's go on screenshots (21:42): `docs/screens/` split into home, character, world, battle, dailies, guild, shops, dialogs, system (plus icons, minimap); the detector test's EXPECTED moved to `docs/screens/expected.json`; new `sxs/core/screens.py`; `python -m sxs bank` copies `captures/unknown/` into `docs/screens/unlabeled/` with a row each, and `python -m sxs label` files the rows mae fills in. The 9 unreferenced screens start the bank. About 200 references rewritten; `tests/check_repo.py` fails on a screen left at the top level or a missing `docs/screens/...png`.
- mae's short-run rule (21:45): the runner now stops every loop at its budget (120 s default, `--budget`) and on 60 s without progress (`--stall`, fed by `progress()` from the Heartbeat and the collector); daily gives each step its own 120 s `task()`. `--minutes` defaults lowered to 2 in explore, fogwalk, roam, tower and gather.
- Open: live shakedown (thread "Test the restructured bot live"); mae labels the bank.

### 2026-11-04 (noon) · Stuck-point review and fixes (Claude Code, cloud)
- Branch `claude/project-thread-16r1uh` (PR #29), rebased on the audit branch. Run logs on rif-love-su were out of reach, so the review used the memory bank and code (report: Claude Doc "Stuck points in today's runs"). New `sxs/rewards.py`: Fog Walk (and so the Roam Loop) claims a finished tracker quest when the gift box and its "!" show (mae's crop `docs/screens/icons/reward_gift_box_mae.png`; check `tests/check_rewards_offline.py`). Fog Walk remembers card-opening spots in map coordinates (screen points went stale when the camera moved: the blessed-statue bumps). Roam keeps areas it gave up on for the server day (Verdantglade III no longer eats every run). The collector finds the character low on screen. `cards.json` never list covers Pray, Recharge, Top up, Catch Up, Advanced Trial, Create Guild, Change Class, USD, hammers.

### 2026-11-04 (midday) · Repo structure audit (Claude Code, cloud)
- Branch `claude/project-thread-kb6hi9`, stacked on the rules/docs branch. Three audit passes (code, scripts/resources, docs/memory). Added README indexes in `sxs/`, `scripts/`, `tests/`, `resource/`, `docs/` and a map table in `AGENTS.md`; new `tests/check_repo.py` (pipelines, templates, State.Detect order, module/script names in docs, compile). Deleted `scripts/enhance_all.py` and `scripts/sheet.py`; mae's bellflower picture moved to `docs/screens/explore_bellflower_mae.png`. New `sxs/marks.py` (daily and tower shared the same done-marks code); explore/fogwalk take heal constants from `sxs/heal.py` and the area name from `sxs/goto.py`; unused constants and imports removed. check-memory skips paths in log.md (history). Spending code untouched.
- Offline checks: check_repo, check-memory, check-rules and check_upgrade_logic pass in the cloud (maafw installs on Linux). Open: the larger proposals in the PR (package split, docs/screens subfolders, heal-sequence dedupe, lazy maa import, loop runner).

### 2026-11-04 (midday) · Rules and docs consolidation (Claude Code, cloud)
- mae asked for concise rules organised by situation. The single rules file (101 KB) became `game/rules/` (12 situation files + index): 99 rules kept with their IDs, 27 merged (retired table in the index), ~40% fewer words, two independent fidelity passes against the original. New `scripts/check-rules.py`. Merged IDs remapped in the nav graph and code comments.
- Memory bank: the handoff file split into `playbook.md` (process) and `status.md` (state, next, waiting on mae); `environments.md` split out of `notes.md`; game facts removed from notes (they're rules); 9 log entries archived. Step 1-5 docs rewritten against the code (step 4's step table was 8 steps behind). Branch `claude/project-thread-qq78yt`.
- The `cards.json` never list was widened in PR #29. Sibling PR (repo audit) adds the sxs, scripts and docs README indexes that context.md and playbook.md point at, and moves bellflower_mae.png to docs/screens.

### 2026-11-04 (late morning) · Bed, pathfinding, Roam Loop, Damp Woods (Claude Code, rif-love-su via Remote Control)
- Same branch. Bed pan fix (Lv 22). New `sxs/roam.py`; Fog Walk: monsters, stamina reserve, bumped-card step-aside, neighbour areas; minimap shaded thresholds; goto takes (from, to, fraction); rules `blessed_statue`, `power_gate_open`. Damp Woods explored and blessed (Lv 23, 17.4K). Verdantglade III not enterable from Moonveil. Rules batch sent (folded into docs PR #24). Details in handoff.md.

### 2026-11-04 · Setup on rif-love-su (Claude Code, rif-love-su via Remote Control)
- Branch `claude/project-thread-5s0w12` = `upgrade-systems` (4 commits not yet in main) + main. venv, requirements, OCR models; offline detector check all good. MuMu found at 127.0.0.1:16416; `sxs.device` now falls back to the single adb device. Live screenshot: home, gromb2 Lv 21, power 16.3K. Game not touched beyond the screenshot.

### 2026-11-04 (morning) · Pulls, Mall gifts, Bellflower hunt start (Claude Code, maes2024 via Remote Control)
- Same branch `upgrade-systems`, main merged in. 20 handler-approved pulls (10 singles by mistake; `sxs.pray` now x10 only). Rating popup: Later. `sxs/mall.py` + daily step `mall_gifts` (4 free gift boxes). Vendor Booth unlocked by tutorial.
- Bellflower Flower Harvest found (free picks in Moonveil Woods, 2/20); `gather --harvest` needs a better plant detector. Paused by mae to swap computers. Details in handoff.md.

### 2026-11-04 (late night) · Upgrade systems and gathering (Claude Code, maes2024 via Remote Control)
- Branch `upgrade-systems` from `guild-tutorial`. New `sxs/badges.py` (red "!" finder), `sxs/upgrade.py` (Upgrade Loop: gear, skills, class_levels, rank, relics), `sxs/gather.py` (Gather Loop, policy `resource/policy/gather.json`), 7 new states, `docs/step5-upgrades.md`, `tests/check_upgrade_logic.py`; `gather` step and the Upgrade Loop inside `strengthen` in `sxs.daily`.
- Live: Quick Upgrade (1.6K essence, charms Lv 1 to 8/9), Ice Spike ascended, a charm equipped, class Mage 1 to 3 and Warrior 1 to 2 (Total 5), many unclaimed Goals tabs claimed; gather 20 ore pickups (stamina 171 to 71, ~+178 ore each); upgrade loop took gear to staff +21, hat +15, chest +15, boots +14, two Resonance tiers. Power 13.1K to ~13.6K+.
- Fixed: the Enhance Gear level reader took "+10" from "+9 -> +10" (OCR order); chest was stuck at +9.
- Rules batch sent (docs PR #18: R-080, R-104, R-108 updated, R-115 to R-119 new). Open: Bellflowers for Rank Advancement (Lv cap 20); special nodes not seen yet.

### 2026-11-04 (night) · Guild mapping (Claude Code, maes2024 via Remote Control)
- Branch `guild-tutorial` from main. Guild tutorial is only dialogue, then Join/Create. mae: join a big, high-power guild; joined karsa_1515 (ID 700460600036) by searching its name.
- Mapped: island (Lobby, Gate of Expedition, Power Station, Forge, Warehouse, Shop), Lobby tabs, Donation (1 free, then 20, 50 Dawnium; mae: 2 a day max, Dawnium approved for those), gather slots (one slot per character, Forge per mae), Guild Events / Conquest (2 attempts a day, background fights per mae), Conquest goals and rankings. ~30 screens in `docs/screens/guild_*`; states guild, guild_panel, guild_donation, guild_conquest, guild_no_guild, guild_join_list, background_fight; guild nodes run before Interact (Conquest's "Challenge" fooled it).
- New `sxs/guild.py`, steps guild_donate / guild_afk / guild_conquest and bed (template `resource/image/home/bed_xp_bubble.png`) in `sxs.daily`. Live: donate and afk "nothing" correctly; conquest navigates (0 attempts left). Today's bed, donations and conquest marked done in `logs/daily.json`.
- Open: may the bot buy in the guild Shop (Guild Tokens)? Pulls and Mall questions still open. Next job: mae's upgrade-systems list (R-104 to R-109).

### 2026-11-04 (morning, later) · Game docs: guild, upgrades, shops, exploration (Claude Code, cloud)
- Docs thread folded the builders' batches into rules R-102 to R-126 (guild, upgrades and materials, background fights, pull x10-only, rating popup Later, Vendor Booth and free Vault stamina, Mall gift boxes, shop policy, Bellflowers and Rank II, collector order, home layout, Roam Loop, Gates of Power, orange minimap monsters). PRs #15 to #24 and #27. Full entry: `git show cc7de5a:memory-bank/log.md`.

### 2026-11-04 (morning) · Game docs: bed EXP (Claude Code, cloud)
- PR #13 merged. mae: collect bed EXP daily, not in every upgrade pass, and sooner near a level-up (R-101); the guild unlocked at Lv 20 (R-011). Next: rule batches from the guild-mapping thread.
- Dailies builder's final batch: guild crest icon at Lv 20 (R-011), bed EXP took Lv 13 to 20 (R-101), "Path to Upgrade: Reach Lv. 20" after Verdant Wonders III (R-084). Opened PR #16 for `dailies-wrapup` (handoff for the guild thread).

### 2026-11-04 (late) · Game docs: final step 3 batch (Claude Code, cloud)
- PRs #10 and #11 merged. Opened PR #12 for the builder's `step3-wrapup` branch (banded gear enhancement, handoff).
- Final step 3 batch: the Enhance Gear screen and the `enhance_gear` node (R-023), HP bar positions on the map and battle prep (R-078, R-091), both loss dialogs and where a loss puts you (R-090), and exact area-label matching (R-068).
- mae: skill pulls get a dedicated script that only the handler starts (R-093; R-055 updated).
- Opened PR #14 for the dailies builder (`dailies-upgrades`). Dailies batch 1: R-094 to R-099 (Journal route to the tower, Material Realms and hammers, Thrilling Events, Daily Sign-in, Growth Trial, Guidance quests for ore); daily reset 8:00 UTC-5 (R-024); more never-press buttons (R-043); Notice board badges are unread posts (R-063). New screens `material_realms`, `ironvein_pit`, `purchase_iron_hammer`, `featured`, `daily_signin`, `growth_trial`. Images are on `dailies-upgrades` until PR #14 merges.
- Dailies addendum: free Iron Hammers from Prayer Goals, ~115 Raw Ore each (R-095); pulls cost Stellatie and `sxs.pray` needs `--handler-approved` (R-093); banded enhancement confirmed live (R-092).
- Dailies batch 2: Prayer banners and costs, Goals milestones paying hammers (R-093, R-095), home stuck on sky means restart (R-100), Friend Request toasts left alone (R-057).
- PRs #12 and #14 merged; merged main into this branch, so the dailies screenshots now resolve.

### 2026-11-04 · Dailies and upgrades (Claude Code, maes2024 via Remote Control)
- Wrap-up: PR #14 merged. Also built `sxs/pray.py` (handler-triggered Standard pulls; not run yet, waiting on mae) and the Ironvein Pit daily step (hammers from prayer goals, ~115 Raw Ore each). mae collected bed XP by hand: Lv 20, power 13.1K, Guild unlocked with a tutorial. Handoff rewritten for the guild-mapping thread (branch `dailies-wrapup`). Open: mae's answer on pulls and on Mall free items; bed XP step waits for mae's icon screenshot.
- Branch `dailies-upgrades` from `step3-wrapup`: `python -m sxs.daily` runs sign-in, Cart, Growth Trial, Fantasia Ascent (Journal tab entry, heal on prep, server-day marks), guidance quest claims and two strengthen passes. Safe claim helper `sxs/claims.py`. New states: enhance_gear, featured, daily_signin, growth_trial, journal, material_realms, notice; main_menu ROI widened. Live: all steps ran; gear enhancement is ore-bound (7 Raw Ore).
- Found: Journal tab (Fantasia Ascent, Map Exploration, Material Realms, Weekly Events); Ironvein Pit needs Iron Hammers (bought only with Dawnium: never). Notice badges mean unread posts.

### 2026-11-04 · Game docs: Fantasia Ascent (Claude Code, cloud)
- PR #9 merged (memory check fix, healing rules, gold buildings, loop design rules). Added R-079 (Auto Challenge in Fantasia Ascent) and the `fantasia_ascent` screen.
- R-079 addendum from the builder: a tower floor loss turns Auto Challenge off; re-enable it next time. mae: tower losses are not retried; one challenge per day as a daily mission. Branch `claude/project-thread-npg43i` fast-forwarded to main.
- mae's design rule in `memory-bank/notes.md`: loops flag the unknown state and recover or end early with a report, instead of spinning.
- mae's reporting rule in `memory-bank/notes.md`: each loop prints `[Running XXX Loop]`, `[Goal: ...]` and `[End condition: ...]` when it starts.
- mae's correction: a red "!" over the player is not a heal signal (it can mean charms to equip). R-061 amended; new R-080 (check the character panel; heal only from the HP bar; red panel badge = empty Charm slot, blue = gear upgrade; marker next to the player can cause mis-taps).
- Builder batch 11: R-081 to R-085 (map coordinates, counterless unlock quests, tracker gift claim, power wall at Verdantglade III, stone tile puzzle); R-068, R-074, R-076, R-079 and R-080 extended with goto, the player pointer, the tower flow and the charm loadout steps. New screens `fantasia_floors`, `fantasia_result`, `charm_detail`, `rcmd_loadouts`, `gear_swap_prompt`. Images are on the step 3 branch. All in PR #10.
- Builder batch 12: R-086 to R-090 (Gate of Power, Highland Woods, replacing gear, travel from home, "badly wounded" as a loss); R-022, R-068, R-070, R-083 and R-084 extended (ring hiding the area name, map zoom and OCR labels, Lost Goddess Statue, gift claims for counter quests). New screens `replace_gear`, `gear_compare`. Same PR #10.
- mae: heal mid-run in mini-dungeons instead of leaving (R-091). Auto Challenge timing refined in R-079. Opened PR #11 for the builder's `step3-explore` work and merged main into it.
- mae: Quick Heal from the portrait on any screen (R-078); a defeat in a mini-dungeon resets the run (R-091); enhance gear evenly in 5-level bands with a priority order (R-092).
- PR #11 (builder's step 3b code) merged; merged main back into this branch.

### 2026-11-04 · Moonveil Woods, Fantasia Ascent, side areas, loop robustness (Claude Code, maes2024 via Remote Control)
- Got into Moonveil Woods with mae's area-map procedure (now `sxs/goto.py`), talked to Molly, won the gate fight, climbed the Moonveil tower to F5 (new `sxs/tower.py`; lost F6). Explored Stone Ruins I (tile puzzle, two chests) and Highland Woods, blessed the Highland and Moonveil statues. Damp Woods is behind a 15.5K Gate of Power; Verdantglade III (12K) fights are lost at 10K. 5 Verdantglade areas done. Lv 13, power 10K (new gear via `equip_better_gear`, charms via `equip_charms`).
- Loop robustness per mae: heartbeat lines, rotating unstick rounds, counterless-quest progress, own-profile watchdog, unknown screens saved to `captures/unknown/` before stopping, loop banners, fog walk stays in its area and stops when no new tile is reached. Branch `step3-explore`, PR #11.
- Later the same day, from mae's notes: "badly wounded" counts as a loss, HP read from the HUD bar and the battle-prep bar with healing below 70% via the top-left portrait, mini-dungeons heal mid-run, gold-building POIs on the minimap, banded gear enhancement (branch `step3-wrapup`). PR #11 merged step3-explore.
- Open: Verdantglade III needs about 12K power; the low-HP paths and banded enhancement need live tests; the minimap classifier mislabels Highland Woods' darker walkable tiles. Next thread: dailies and upgrades.

### 2026-11-03 (late) · Game docs after PR #6 (Claude Code, cloud)
- PR #6 merged batches 4 to 9 and mae's rules up to R-067. Added R-068 (travel through the full area map) and the `area_map` screen; branch `claude/project-thread-npg43i` fast-forwarded to main.
- Builder batch 10 (handoff): R-069 to R-077 (obelisk, Goddess Statue blessing, mines, puzzle, path blockers, edge pointers, home events, area map, team panel); minimap crops and HSV thresholds linked to R-066; `puzzle_energy_circuits`, `team` and `blessing_level` screens. Same PR #8.
- Merged main after PR #7, so the images from batches 4 to 10 now resolve on main.

### 2026-11-03 (late) · Verdantglade I–II, minimap reader, handoff (Claude Code, maes2024 via Remote Control)
- Talked to the Chief to open the Originisle V loot (NPC "!" gating), activated the Voyage Obelisk, then cleared and blessed Verdantglade I and II (Lv 12, 7.7K power). Added: talk to NPC "!" when stuck, fight path blockers (wolf templates), edge pointers (boss, statue, unlock), the tracker gift claim, rules for the obelisk, goddess statue and mines, mae's heal-and-retry rule, dialogue logging, `sxs/minimap.py` and `sxs/fogwalk.py`. Branch `step3-explore`, PR #7.
- Open: Moonveil Woods route (blocker); handed off in `memory-bank/handoff.md` at mae's request.

### 2026-11-03 (evening) · Mage, prayer, strengthen routine (Claude Code, maes2024 via Remote Control)
- mae chose Mage, and the character ascended. The tutorial unlocked the Statue and Prayer (10 free tickets used), and Cyclone and Flame Jet are equipped. Added `--choose` to `sxs.explore`, stall guards (vary tap offset, give up), unknown screens through the decider, a spend guard in the tutorial follower, and `sxs/strengthen.py`. Rule batch 9 went to the docs thread. Branch `step3-explore`, PR #7.
- Open: the unreachable loot on Originisle V blocks Wild Isle Trek V.

### 2026-11-03 (night) · Step 3 start: quest following (Claude Code, maes2024 via Remote Control)
- mae asked me to keep playing the tutorial overnight and map screens. Built `sxs/explore.py` (tracker-marker loop with chaining), `sxs/tutorial.py` (highlight and hint follower), `sxs/decide.py` with `resource/policy/cards.json` (goal-based card decisions, per mae's design note), `scripts/enhance_all.py` and `docs/step3-explore.md`. Branch `step3-explore`.
- Account went from Lv 2 to Lv 10: Originisle I–V, Temple Ruins floor 1, the Guardian Colossi boss, rank Apprentice I. Rule batches 4–7 went to the docs thread through the coordinator.
- Open: class choice (mae), automating strengthening, a PR for `step3-explore`.

### 2026-11-03 · Game docs batch 4 (Claude Code, cloud)
- Builder batch 4 (step 3 explore loop): added `interact` and `defeated` screens and their taps to `memory-bank/game/nav-graph.json`; rules R-029 to R-034 (Trek quest chain, map object cards, defeat, camera, stamina regen, exploration rewards) and the quest-ring offset in R-022. Branch `claude/project-thread-npg43i` fast-forwarded to main after PR #4.
- Batch 5 added to the same PR: cart, house, bed, unlock result and skill/technique screens; rules R-035 to R-039; Cart income in R-020.
- Batch 6: exploration cards, Temple Ruins mini-dungeon (`dungeon_floor` screen), guarded targets, the goal-dependent card policy (R-040 to R-043). The graph format gained an optional `when` condition on edges; `scripts/nav-graph.py` shows it.
- Batch 7: quest chain to the Guardian Colossi boss, claiming from the tracker, boss pointer, low-HP dialog, Alchemy Pot dishes, rank advancement (R-044 to R-049; screens `wounded`, `alchemy_pot`, `rank_advancement`).
- Batch 8: class choice, Notice board events, Exploration Goals, Lv 10 menu layout, Friends and Settings (R-050 to R-053); currency icon crops linked. Opened the step 3 PR (#7) for the builder and merged main into its branch.
- Batch 9: mae chose Mage; class ascend, Prayer gacha (never pray), technique equipping, social requests left alone, unreachable ledge loot, popups close above (R-054 to R-060).
- mae's heal-and-retry policy added as R-061 (healing food fine to spend, conserve stat-boost dishes, retry a lost fight at most twice).
- Open: captures for batches 4 to 9 live on branch step3-explore (PR #7) until it merges; ledge loot resolved by mae (talk to red "!" NPCs first, R-062); why Quick Heal sometimes doesn't clear the wounded dialog.

### 2026-11-03 · Game docs batch 2 (Claude Code, cloud)
- Builder batch 2: added the `title` screen and login waits to `memory-bank/game/nav-graph.json`, confirmed Explore progress (R-002, R-021), noted the blessing statue is still unseen (R-003). Branch `claude/project-thread-npg43i` fast-forwarded to main after PR #3 merged.
- Also folded in the step 2 doc's screen catalogue (boot taps, resume on last screen), merged main after PR #5, PR #4.

### 2026-11-03 · Step 2: hands and eyes (Claude Code, maes2024 via Remote Control)
- Installed MaaFramework 5.15 in `.venv`; it uses MuMu's IPC screenshots. Built `sxs/` (device, state detector, navigator, CLI, offline replay), `resource/` (state pipeline, dialogue template, OCR models via `scripts/fetch-ocr-models.py`), `tests/` and `docs/step2-hands-and-eyes.md`. Branch `step2-hands-and-eyes`.
- mae accepted the agreement and signed in. I played the rest of the tutorial prompts (enhanced the staff, equipped the cap, finished Wild Isle Trek I) and captured 25 screens. I sent game rules to the docs thread (PR #3) through the coordinator.
- The smoke test passed twice. Open: push and PR (Git on maes2024 needs mae's GitHub sign-in). Daily-content screens are still locked at Lv 2.

### 2026-11-03 · Game rules and menu graph started (Claude Code, cloud)
- mae asked for documentation of the game's rules and a traversable map of menus, fed by the step 2 builder thread. Added `memory-bank/game/` (README, `memory-bank/game/rules.md` with R-001 to R-020 from mae and the step 1 doc, `memory-bank/game/nav-graph.json` with 15 screens) and `scripts/nav-graph.py` (check, render, shortest path). Branch `claude/project-thread-npg43i`, PR #3.
- Batch 1 from the builder (via the coordinator): graph now 25 screens and 29 actions with OCR detection and tap positions; rules R-021 to R-028 added, currency, Cart and unlock rules promoted to observed.
- Open: shop, dungeons, mail, arena and vendor entry points; currency icon crops; battle loss path. Earlier: most edges lacked tap positions and most screens lack detection hints and captures; the builder thread sends them as it plays.

### 2026-11-03 · Memory bank set up (Claude Code, cloud)
- mae asked to bring the memory bank generation prompt from the TrackFlow-Company-Overhaul repo into this one and instantiate it. Copied `.agents/prompts/memory-bank.md` and `scripts/check-memory.py` unchanged. PR #2. Wrote `AGENTS.md`, `CLAUDE.md` and the six memory files. Branch `claude/project-thread-4u6oai`.
- Open: mae reviews and merges PR #2.

### 2026-11-02 · Step 1: emulator choice and game survey (Claude Code, cloud)
- Compared emulators and automation toolkits and catalogued the game's daily content; picked MuMu Player 12 and MaaFramework (`decisions.md`). mae confirmed the game is Sword x Staff. PR #1, branch `docs/step1-emulator-and-game`.
- PR #1 merged 2026-11-03. Open: maes2024 setup.
