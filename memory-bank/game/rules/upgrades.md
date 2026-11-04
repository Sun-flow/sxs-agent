# Upgrade rules

Read when raising character power: the character-screen "!", gear, skills, charms, class, rank or relics.

## The character screen "!"

### R-080 · A "!" on the player or the character screen means an upgrade is waiting: take it
- A red "!" over the player on the overworld means "something for your character" (charms or gear to equip, maybe low HP). It is **not** a heal signal: heal only from the HP bar (R-061, R-078), and never block fights on the "!".
- Open the character panel (HUD portrait or your own character). Badges sit on gear slots, Skill, Class and the rank badge, and inside each screen on the exact tab or button. Red badges: empty charm slots (row y≈0.71). Blue badges on Equip: better gear (R-088). Always follow a badge and take the upgrade, within the spending rules (mae). Badges pulse: check 2 frames.
- Fill a charm slot: tap it to open "Edit" (charm slots at x≈0.87, y≈0.21 / 0.30 / 0.39 / 0.48), Charm tab (0.56, 0.62), a charm card, Equip (0.5, 0.70), then a pulsing empty slot. A filled slot's button reads Replace. The 4th slot was still locked at Lv 13 ❓.
- **Never use Rcmd ("Rcmd Loadouts" / Apply).**
- Opened by accident when a marker sits beside the player: R-022.
- Code: `python -m sxs.upgrade` (`--only skills,gear,class_levels,rank,relics`), `sxs/badges.py`.
*told, observed* · `player_profile_charm_badges.png`, `loadout_edit_charms.png`, `charm_detail.png`, `rcmd_loadouts.png` · nodes `player_profile`, `loadout_edit`, `charm_detail`, `rcmd_loadouts` · R-063, R-104, R-116

## Gear

### R-023 · Enhancing gear costs ore and Rolla
- Character, a gear slot, the item card (Replace / Enhance), Enhance Gear.
- Cost: Raw Ore (blue crystal), Refined Ore (red crystal), Rolla, shown have/need ("Raw Ore 7/720"). Short: toast "Insufficient materials to enhance."
- 4 tabs on top, one per piece (weapon, head, chest, boots; no offhand yet), each "+N". The selected piece shows "+21 → +22" at y≈0.42, stat deltas, cost, Enhance (0.5, 0.85), Resonance (R-119), Goals (R-116).
- Not a detector state yet: `go_home` gets stuck there.
*observed* · `enhance_gear.png` · nodes `character`, `enhance_gear` · R-092, R-119

### R-092 · Enhance all gear evenly, in 5-level bands
- All equipped pieces to +5, then all to +10, then +15... A piece passes a band only when every other piece has reached it.
- Inside a band, priority: weapon, offhand (not unlocked), headpiece, chest, boots. Code: `Strengthener.enhance_gear` in `sxs/strengthen.py` (`GEAR_BAND`, `GEAR_PRIORITY`; insert the offhand after the weapon when its tab appears).
- Ore is the bottleneck. Sources: Cart (+100 Raw Ore/h, R-020), gathering (R-107), Guidance quests (R-099), Ironvein Pit (R-095).
*told, observed* · R-023, R-106, R-119

### R-119 · Activate Gear Resonance each time a band completes
Enhance Gear > Resonance (0.86, 0.20). Tiers read "Enhance Gear x4 to +N" (N = 5, 10 ... 35+; e.g. HP +2%) and show Activate once all 4 pieces reach +N: activate as soon as an R-092 band completes. OCR quirk: text isn't returned left to right, so the current level is the leftmost number in "+9 → +10".
*observed* · `gear_resonance.png` · node `enhance_gear` · R-023, R-092

### R-088 · Replace gear with better items from the profile
A red "!" over a gear piece's picture means a better piece is available for that slot. Replace it whenever one drops. This is its own task, independent of enhancing (R-092), and the bot should do it on its own (mae). Profile, an Equip slot, Replace. The list puts the best first, green up arrow on upgrades. Tap one for a compare (equipped left, new right, with power); Replace is under the new item. Enhancement levels carry over, so replacing loses nothing.
*observed, told* · `replace_gear.png`, `gear_compare.png` · nodes `replace_gear`, `gear_compare` · R-080, R-092

## Skills and charms

### R-037 · Techniques level with Battle Essence, capped by character level
- Character > Skill (0.41, 0.59): the loadout, 4 technique slots left, 4 charm slots right.
- Equip: Technique tab, card, Equip, an empty slot. New techniques start at Lv 1.
- Level: tap it, Enhance, upgrade (0.5, 0.85). Prefer Quick Upgrade (R-104); Ascend: R-115.
- Battle Essence (purple orb, top right) is the skill currency; Cart +125/h (R-020); Lv 1 to 10 ≈ 490.
- Capped by character level ("Unlocks at Character Lv. 6").
*observed* · `skill_loadout.png`, `technique_card.png`, `technique_upgrade.png` · nodes `skill_loadout`, `technique_upgrade` · R-104, R-106

### R-104 · Level everything at once with Quick Upgrade
Skill page, Quick Upgrade icon at about (0.73, 0.47), captioned "Upgrade". No selection needed: one tap levels everything Battle Essence can afford, charms included. It disappears when nothing is affordable.
*told, observed* · `skill_page.png`, `skill_page_after_quick_upgrade.png` · node `skill_loadout` · R-037, R-106

### R-115 · Ascend a technique with its own shards
A "!" on a technique means it can ascend: tap it, Enhance (0.68, 0.74), Ascend tab (bottom right), Ascend (0.50, 0.85). Each step costs 10 of its own shards (Rare → Rare 1★ → Epic). No Dawnium.
*observed* · `technique_upgrade.png`, `technique_ascend.png` · nodes `technique_card`, `technique_upgrade` · R-037, R-080

## Class

### R-117 · Level classes with Class Badges; never Change Class
- Class > Class Hierarchy: tap a class card with "!" for "Class Badge Received" (+2 per owned skill of that class), OK (0.50, 0.72).
- That class's Upgrade tab: 10 badges per level (+HP, ATK, DEF, SPD). Levelling any class raises Total Class Level without changing class.
- **Never tap "Change Class"** (locked until Lv 100; also a button on the Warrior page). Class choice is mae's (R-054).
*observed* · `class_page.png`, `class_hierarchy.png`, `class_badge_received.png`, `class_info.png`, `class_upgrade.png` · node `class_ascend` · R-054, R-116

## Rank

### R-118 · Rank Advancement raises the level cap
- Character > rank badge ("Apprentice I", (0.82, 0.72)). Needs max level plus materials; at the cap, levelling stops until you rank up.
- Advance only when the Advance button shows "!", with free materials (**no Dawnium**). Tap through "RANK UP"; stored XP applies at once. Then claim the rank Goals (R-116).
- Apprentice I → II (done): Lv 20, 5 grey stones, 20 Bellflowers (R-123), 5.5K Rolla; cap 30.
- Apprentice II → III: Lv 30, 5 green leaf items, 30 of a new flower ❓ (name unknown; probably another Flower Harvest), 10.5K Rolla; cap 40.
*observed* · `rank_advancement.png`, `rank_up_result.png` · node `rank_advancement` · R-101, R-116, R-123

## Relics

### R-105 · Enhance relics in bands of 1, element by element (not unlocked yet)
Relics come in elements of 4. Raise one element's 4 relics together by 1 level; bring every element level before any goes higher. Element order: the character's affinity, highest first. Cost: sand (R-106). Code: `relic_plan` in `sxs/upgrade.py`.
*told* · R-092, R-106
