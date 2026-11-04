# Session Log

> **Last updated**: 2026-11-04
> Newest first. One entry per session: date, where it ran, what changed (link the PR or commit), what was left open. Keep about 15 entries. When there are more, move the oldest to `docs/archive/memory-bank-log.md` (create it the first time). Entries before this file existed were rebuilt from git history and the project's chat.

### 2026-11-04 (midday) · Rules and docs consolidation (Claude Code, cloud)
- mae asked for concise rules organised by situation. The single rules file (101 KB) became `game/rules/` (12 situation files + index): 99 rules kept with their IDs, 27 merged (retired table in the index), ~40% fewer words, two independent fidelity passes against the original. New `scripts/check-rules.py`. Merged IDs remapped in the nav graph and code comments.
- Memory bank: the handoff file split into `playbook.md` (process) and `status.md` (state, next, waiting on mae); `environments.md` split out of `notes.md`; game facts removed from notes (they're rules); 9 log entries archived. Step 1-5 docs rewritten against the code (step 4's step table was 8 steps behind). Branch `claude/project-thread-qq78yt`.
- Open: `resource/policy/cards.json` safe-verb list includes Pray (status.md, Known problems). Sibling PR (repo audit) adds the sxs, scripts and docs README indexes that context.md and playbook.md point at, and moves bellflower_mae.png to docs/screens.

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
