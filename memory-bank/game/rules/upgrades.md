# Upgrade rules

Read when raising character power: the character-screen "!", gear, skills, charms, class, rank or relics.

## The character screen "!"

### R-080 · A "!" on the player or the character screen means an upgrade is waiting: take it
- A red "!" over the player on the overworld means "something for your character" (charms or gear to equip, maybe low HP). It is **not** a heal signal: heal only from the HP bar (R-061, R-078), and never block fights on the "!".
- The "!" is not one signal (mae). It can mean gear enhance (R-092), gear replace (R-088), charms, skill upgrade (R-104; skill icons show a blue arrow instead of a "!") or ascend (R-115), class (R-117), rank (R-118) or relics (R-105). Each is its own upgrade task with its own check for whether it is needed; follow the badge to the exact tab or button to tell which, and never assume it means gear. A lit Goals tab is claimed first (R-116).
- Open the character panel (HUD portrait or your own character). Badges sit on gear slots, Skill, Class and the rank badge, and inside each screen on the exact tab or button. Red badges: empty charm slots (row y≈0.71). On a gear slot, red "!" = a better piece to swap, blue arrow pip = can be enhanced (R-088, R-092). Always follow a badge and take the upgrade, within the spending rules (mae). Badges pulse: check 2 frames.
- Fill a charm slot: tap it to open "Edit" (charm slots at x≈0.87, y≈0.21 / 0.30 / 0.39 / 0.48), Charm tab (0.56, 0.62), a charm card, Equip (0.5, 0.70), then a pulsing empty slot. A filled slot's button reads Replace. The 4th slot was still locked at Lv 13 ❓.
- **Never use Rcmd ("Rcmd Loadouts" / Apply).**
- Opened by accident when a marker sits beside the player: R-022.
- One function per type. `python -m sxs upgrade` runs passes `goals`, `skills`, `gear`, `class_levels`, `rank` (and `relics` once unlocked), each up to 90 s, only where a badge shows (`--only` picks passes). Charms are filled only when the profile's Charm row is badged. Gear replace is its own loop (R-088). Badge finder: `sxs/vision/badges.py`.
*told, observed* · `character/player_profile_charm_badges.png`, `character/loadout_edit_charms.png`, `character/charm_detail.png`, `character/rcmd_loadouts.png` · nodes `player_profile`, `loadout_edit`, `charm_detail`, `rcmd_loadouts` · R-063, R-088, R-092, R-104, R-105, R-115, R-116, R-117, R-118

## Gear

### R-023 · Enhancing gear costs ore and Rolla
- Character, a gear slot, the item card (Replace / Enhance), Enhance Gear.
- Cost: Raw Ore (blue crystal) and Rolla, shown have/need ("Raw Ore 7/720"); higher steps add Refined Ore (red crystal): the weapon's +24 → +25 needs 300. Short: a banner "Insufficient materials to enhance." Wait for it to clear (about 2.5 s) before the next piece, or that piece reads the old banner as its own failure.
- 4 tabs on top, one per piece (weapon, head, chest, boots; no offhand yet), each "+N". The selected piece shows "+21 → +22" at y≈0.42, stat deltas, cost, Enhance (0.5, 0.85), Resonance (R-119), Goals (R-116).
- Detector state `enhance_gear`.
- Raw Ore is the limit on enhancing: after about 10K spent on 2026-11-11, 348 were left and the weapon's next level needs 1.14K. Dismantle (R-165) and Raw Ore Caskets (R-169) are the free sources.
*observed* · `character/enhance_gear.png` · nodes `character`, `enhance_gear` · R-092, R-119

### R-092 · Enhance all gear evenly, in 5-level bands
- All equipped pieces to +5, then all to +10, then +15... A piece passes a band only when every other piece has reached it.
- A piece short of its own material, or at its cap, is left out and the other pieces keep banding (live 2026-11-09: the weapon's red ore stopped the whole pass before this fix).
- Enhance the lower-level pieces first: the highest piece costs the most (mae, 2026-11-10 00:07). The band target comes from the lowest piece, so pieces already at it are skipped until the rest catch up. Among pieces below the target, priority: weapon, offhand (not unlocked), headpiece, chest, boots.
- Enhance only pieces whose tab on the Enhance screen shows a blue pip (R-088); a tab without one is skipped, not tried. Code reads the tab row with `tabs_with_pip`. Covered by a screenshot test; live proof waits for the next materials. Code: `Strengthener.enhance_gear` in `sxs/loops/strengthen.py` (`GEAR_BAND`, `GEAR_PRIORITY`; insert the offhand after the weapon when its tab appears).
- Ore is the bottleneck. Sources: Cart (+100 Raw Ore/h, R-020), gathering (R-107), Guidance quests (R-099), Ironvein Pit (R-095).
*told, observed* · R-023, R-106, R-119

### R-119 · Activate Gear Resonance each time a band completes
Enhance Gear > Resonance (0.86, 0.20). Tiers read "Enhance Gear x4 to +N" (N = 5, 10 ... 35+; e.g. HP +2%) and show Activate once all 4 pieces reach +N: activate as soon as an R-092 band completes. OCR quirk: text isn't returned left to right, so the current level is the leftmost number in "+9 → +10".
*observed* · `character/gear_resonance.png` · node `enhance_gear` · R-023, R-092

### R-088 · Replace gear with better items from the profile
A red "!" over a gear piece's picture means a better piece is available for that slot: swap it. A **blue upgrade-arrow pip** in the same spot means the piece can be enhanced instead (R-092), not swapped (mae, 2026-11-09). Live pips are bluer than the first crop (H 98–114, S up to about 175), and next to the chest slot the pip merges with the slot rim (reference `character/character_pips_all4.png`). Replace it whenever one drops. Code (PR #45): the blue pip is found by `find_up_pips` in `sxs/vision/badges.py`, and the Upgrade loop's gear pass runs on it. This is its own task, independent of enhancing (R-092), and the bot should do it on its own (mae). Profile, an Equip slot, Replace. The list puts the best first, green up arrow on upgrades. Tap one for a compare (equipped left, new right, with power); Replace is under the new item. Enhancement levels carry over, so replacing loses nothing.
- Code: its own loop `python -m sxs gearswap`, also daily step `gear_swap`. The slot badge says to look; the power compare decides whether to Replace. First live run worked: head 1100 to 1170, chest 889 to 1900, boots 143 to 1860 power. 2026-11-09: weapon 1490 to 1960, head 1170 to 1820.
*observed, told* · `character/replace_gear.png`, `character/gear_compare.png`, `character/character_pips_all4.png` · nodes `replace_gear`, `gear_compare` · R-080, R-092

## Skills and charms

### R-037 · Techniques level with Battle Essence, capped by character level
- Character > Skill (0.41, 0.59): the loadout, 4 technique slots left, 4 charm slots right.
- Equip: Technique tab, card, Equip, an empty slot. New techniques start at Lv 1.
- Level: tap it, Enhance, upgrade (0.5, 0.85). Prefer Quick Upgrade (R-104); Ascend: R-115.
- Battle Essence (purple orb, top right) is the skill currency; Cart +125/h (R-020); Lv 1 to 10 ≈ 490.
- Capped by character level ("Unlocks at Character Lv. 6").
*observed* · `character/skill_loadout.png`, `character/technique_card.png`, `character/technique_upgrade.png` · nodes `skill_loadout`, `technique_upgrade` · R-104, R-106

### R-104 · Level everything at once with Quick Upgrade
Skill page, Quick Upgrade icon at about (0.73, 0.47), captioned "Upgrade". No selection needed: one tap levels everything Battle Essence can afford, charms included. It disappears when nothing is affordable.
- Upgradable skill icons show a **blue arrow**, not a red "!" (the "!" means ascend, R-115), and the Character screen's Skill button shows no "!" for them. Quick Upgrade appears anyway: always open the Skill page and press it whenever any skill icon carries a blue arrow. The `upgrade` loop now always opens the Skill page.
- Live 04:37: one press raised every skill 2–4 levels for about 3K Battle Essence; power 22.2K to 22.4K.
*told, observed* · `character/skill_page.png`, `character/skill_page_after_quick_upgrade.png` · node `skill_loadout` · R-037, R-106

### R-115 · Ascend a badged skill with its own shards
- A "!" on any skill icon, equipped or in the Technique or Charm bag, means it can ascend (10/10 of its own shards). Ascend it. Each step costs 10 of its own shards (Rare → Rare 1★ → Epic). No Dawnium.
- Technique card: Enhance (0.68, 0.74) opens Ascension directly; Ascend (0.50, 0.85). Charm card: Enhance opens Upgrade, then the Ascend tab (bottom right), then Ascend.
- Seen: Ice Spike Rare to Epic, Elemental Mystery. Code: the `skills` pass of `python -m sxs upgrade`.
*observed* · `character/technique_upgrade.png`, `character/technique_ascend.png` · nodes `technique_card`, `technique_upgrade` · R-037, R-080

## Class

### R-117 · Level classes with Class Badges; never Change Class
- Class > Class Hierarchy: tap a class card with "!" for "Class Badge Received" (+2 per owned skill of that class), OK (0.50, 0.72).
- That class's Upgrade tab: 10 badges per level (+HP, ATK, DEF, SPD). Levelling any class raises Total Class Level without changing class.
- **Never tap "Change Class"** (locked until Lv 100; also a button on the Warrior page). Class choice is mae's (R-054).
*observed* · `character/class_page.png`, `character/class_hierarchy.png`, `character/class_badge_received.png`, `character/class_info.png`, `character/class_upgrade.png` · node `class_ascend` · R-054, R-116

## Rank

### R-118 · Rank Advancement raises the level cap; at the cap it comes first (mae)
- Character > rank badge ("Apprentice I", (0.82, 0.72)). Needs max level plus materials; at the cap, levelling stops until you rank up.
- **Rank advancement is one of the highest-priority strengthening tasks: whenever the level hits the cap, go for the next rank at once** (mae, 2026-11-11 05:20). It is a huge power boost: Apprentice III applied the banked bed EXP, Lv 30 → 37, power 30.6K → 35.9K. Gather any free material it is short of (Bellflowers, R-123) before other strengthening. Flowchart: `docs/loops/upgrade.md` (Get stronger).
- Advance only when the Advance button shows "!", with free materials (**no Dawnium**). Tap through "RANK UP"; stored XP applies at once. Then claim the rank Goals (R-116).
- Apprentice I → II (done): Lv 20, 5 grey stones, 20 Bellflowers (R-123), 5.5K Rolla; cap 30.
- Apprentice II → III: Lv 30 (met), 5 green leaves (18/5, met), 30 Bellflowers (14/30 on 2026-11-11; the cost card names "Verdantglade Flower Harvest" as the source and shows an "Available" tag; picks are free, R-123), 10.5K Rolla (met); cap 40. Raising Player Rank is required to keep progressing (mae, 2026-11-11).
- While a material is short the Advance button shows a **blue pip**, not "!"; the Rank Goals tab carries the "!" (claim it, R-116).
- Collect the Bellflowers with `python -m sxs gather --harvest bellflower --enter` (enters the Flower Harvest field itself).
- Apprentice III reached 2026-11-11 (strengthening pass): the banked bed EXP applied on rank-up, Lv 30 → 37 (cap 40). The next rank's needs are not read yet ❓.
- Code: rank-first is built (Upgrader.rank_first, PR #62); the flowchart in `docs/loops/upgrade.md` shows it as a solid branch.
*observed, told* · `character/rank_advancement.png`, `character/rank_up_result.png`, `character/rank_advancement_apprentice3.png` · node `rank_advancement` · R-101, R-116, R-123

## Relics

### R-105 · Enhance relics in bands of 1, element by element
Relics come in elements of 4. Raise one element's 4 relics together by 1 level; bring every element level before any goes higher. Element order: the character's affinity, highest first. Cost: sand (R-106). Relics are unlocked (R-172). Code: `relic_plan` in `sxs/loops/upgrade.py`, used by the relic step (PR #62).
*told* · R-092, R-106
