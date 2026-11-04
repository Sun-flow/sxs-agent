# Session Log

> **Last updated**: 2026-11-04
> Newest first. One entry per session: date, where it ran, what changed (link the PR or commit), what was left open. Keep about 15 entries. When there are more, move the oldest to `docs/archive/memory-bank-log.md` (create it the first time). Entries before this file existed were rebuilt from git history and the project's chat.

### 2026-11-04 (late night) · Upgrade systems and gathering (Claude Code, maes2024 via Remote Control)
- Branch `upgrade-systems` from `guild-tutorial`. New `sxs/badges.py` (red "!" finder), `sxs/upgrade.py` (Upgrade Loop: gear, skills, class_levels, rank, relics), `sxs/gather.py` (Gather Loop, policy `resource/policy/gather.json`), 7 new states, `docs/step5-upgrades.md`, `tests/check_upgrade_logic.py`; `gather` step and the Upgrade Loop inside `strengthen` in `sxs.daily`.
- Live: Quick Upgrade (1.6K essence, charms Lv 1 to 8/9), Ice Spike ascended, a charm equipped, class Mage 1 to 3 and Warrior 1 to 2 (Total 5), many unclaimed Goals tabs claimed; gather 20 ore pickups (stamina 171 to 71, ~+178 ore each); upgrade loop took gear to staff +21, hat +15, chest +15, boots +14, two Resonance tiers. Power 13.1K to ~13.6K+.
- Fixed: the Enhance Gear level reader took "+10" from "+9 -> +10" (OCR order); chest was stuck at +9.
- Rules batch sent (docs PR #18: R-080, R-104, R-108 updated, R-115 to R-119 new). Open: Bellflowers for Rank Advancement (Lv cap 20); special nodes not seen yet.

### 2026-11-04 (night) ? Guild mapping (Claude Code, maes2024 via Remote Control)
- Branch `guild-tutorial` from main. Guild tutorial is only dialogue, then Join/Create. mae: join a big, high-power guild; joined karsa_1515 (ID 700460600036) by searching its name.
- Mapped: island (Lobby, Gate of Expedition, Power Station, Forge, Warehouse, Shop), Lobby tabs, Donation (1 free, then 20, 50 Dawnium; mae: 2 a day max, Dawnium approved for those), gather slots (one slot per character, Forge per mae), Guild Events / Conquest (2 attempts a day, background fights per mae), Conquest goals and rankings. ~30 screens in `docs/screens/guild_*`; states guild, guild_panel, guild_donation, guild_conquest, guild_no_guild, guild_join_list, background_fight; guild nodes run before Interact (Conquest's "Challenge" fooled it).
- New `sxs/guild.py`, steps guild_donate / guild_afk / guild_conquest and bed (template `resource/image/home/bed_xp_bubble.png`) in `sxs.daily`. Live: donate and afk "nothing" correctly; conquest navigates (0 attempts left). Today's bed, donations and conquest marked done in `logs/daily.json`.
- Open: may the bot buy in the guild Shop (Guild Tokens)? Pulls and Mall questions still open. Next job: mae's upgrade-systems list (R-104 to R-109).

### 2026-11-04 (morning, later) · Game docs: guild (Claude Code, cloud)
- PRs #15 and #16 merged. Guild thread: tutorial ends at Join / Create; mae chose to join a random open guild; never create (R-102).
- mae: donate to the guild at most twice a day; those two may use Dawnium (R-103, R-043, R-016). Joined karsa_1515.
- mae's upgrades and materials rules: Quick Upgrade for skills (R-104), relic banding by element (R-105, not unlocked yet), the four materials (R-106), keep 70 stamina and gather ore (R-107), material tracking (R-108), special nodes (R-109), any character "!" means an upgrade (R-080). Guild thread: one gathering slot (R-110), Gate of Expedition (R-111), third donation costs 50 (R-103).
- PR #17 merged. mae: fights with the background symbol run unattended, so start them and move on (R-112, icon crop in `docs/screens/icons/`); Conquest has 2 free tries a day (R-111).
- Guild batch 1: tutorial and join list (R-102), donation screen (R-103), gathering facilities and mae's Forge choice (R-110), Conquest flow and the guild script (R-111), island and Lobby (R-113), Warehouse and Shop (R-114), bed EXP bubble (R-101). Eight guild screens in the nav graph. Images are on the builder's guild-tutorial branch until it merges.
- Guild addendum: Conquest OCR quirk and the Done chip (R-111), the hidden Gate label and remembered camera pan (R-113). Opened PR #19 for `guild-tutorial`.
- Upgrade-systems batch 1 (builder numbered from R-112; renumbered here): builder R-112 folded into R-080, R-113 into R-104, R-119 into R-108; new R-115 technique ascension, R-116 Goals tabs, R-117 class badges, R-118 rank cap and Bellflowers, R-119 gear resonance.
- mae: skill pulls only in groups of ten, never Pray x1 (R-093 amended). Rating popups: dismiss with "Later" (R-060). The Vendor Booth unlocked on home (R-120). Mall: claim the free gift boxes, never the paid packs (R-121). mae's shop policy: map each shop's stock into a table, mae marks buys, buy nothing without a buy list (R-120, R-114).
- PRs #18 to #21 merged. Bellflower field in Verdantglade, no stamina cost, tap the plants themselves; Bellflowers and Rank Advancement come before the shops (R-118). Blue-aura pickups are rarer, so prefer them (R-122).

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
