# UI rules

Read when a menu, popup, overlay, tutorial highlight or red badge is on screen, or when reading a shop.

## Dialogue and tutorial overlays

### R-028 · Tap through story dialogue, then carry on
Story dialogue (Akane, ▼ at the bottom) can overlay any screen. Tap (0.5, 0.9) until it's gone, then resume.
*observed* · `dialogs/dialogue.png`, `dialogs/dialogue_loadout.png` · node `dialogue` · R-036

### R-164 · Story dialogue with choices and no Leave: stop, save the screen, ask mae
- When story dialogue offers **two or more** answer choices and no Leave (e.g. Akane and Qin in Verdantglade VIII), the bot does not pick: it stops with `needs_decision`, saves a reference screenshot of the dialogue, and asks mae (mae, 2026-11-11 04:10).
- This holds for the next few instances. Most choices are flavour only, but some may matter; once mae has seen enough of them she may let the bot answer some itself.
- Save each capture under `docs/screens/dialogs/` with a name for the scene, and record which choice mae picked.
- One option only: press it, no stop (R-171).
- Not covered: a choice with a Leave option (class choice, puzzles) keeps its own rule (R-054, R-153); plain dialogue without choices is tapped through (R-028).
*told* · node `dialogue` · R-028, R-042, R-054, R-153

### R-171 · Story dialogue with a single option: always press it
- If story dialogue offers only one option, it is always safe to press: press it and carry on (mae, 2026-11-11 05:37). Only two or more choices with no Leave stop the bot (R-164).
*told* · node `dialogue` · R-028, R-164

### R-173 · Lore pages: swipe to the end, then Close
- A minimap "building" object can open a lore page (e.g. "Tale of the Blight Witch I"): title top left, long story text, a down chevron at the bottom, no back arrow (builder, 2026-11-11).
- Swipe up to the end of the text; a "Close" button appears at about (360, 1104). Close is safe, and reading the page counts as clearing the object.
- A Blight Witch lore page is followed by a curse (R-174).
- Code: a `lore_page` state is being added with Clear Zone (#60).
*observed* · `dialogs/dialogue_lore_tale_of_the_blight_witch.png`, `dialogs/dialogue_lore_page_close.png` · R-028, R-030

### R-036 · Tap what the tutorial highlights
- Highlights: (a) a bright yellow pulsing frame, (b) an Akane chibi bubble ("Tap to unlock", "Tap to speed up", "Upgrade skill to Lv. 5") about 0.08 screen height above the button, (c) sometimes a white or pale frame. Step 3's tutorial follower handles (a) and (b).
- "UNLOCKED ..." full-screen card: tap to continue.
- The detector reads a highlight overlay as unknown and `nav.go_home` can fail on it: tap the highlighted control (e.g. Character, rank badge, Advance after the Bellflower harvest, R-123).
- Never follow a tutorial into a class choice: on dialogue options "Ascend to …" or "Change Class", take Leave and stop with needs_decision (R-054; the tutorial loop does this, PR #45).
*observed* · `dialogs/tutorial_highlight.png`, `dialogs/tutorial_highlight_dim.png`, `dialogs/unlocked.png` · node `tap_to_continue` · R-028, R-118

## Popups

### R-060 · Close popups by tapping above them; rating popups get Later
- Tap (0.5, 0.05), above the popup. (0.5, 0.95) also closed the player profile.
- **Rating/feedback popups: always Later; never rate or open the store** (mae). Seen after skill pulls: "...do you satisfy with your experience in Kanstein?" with Very Satisfied (0.50, 0.55), Dissatisfied (0.50, 0.62), Later (0.50, 0.69). Detector state `RatingPopup`; the toward-home step taps Later.
*observed, told* · `dialogs/rating_popup.png` · node `cart`, `player_profile`, `apply_requests` · R-043

## Moving between screens

### R-026 · Use the on-screen back arrow, not the Android back key
The back key does nothing on some screens (player profile). Use the back arrow (0.08, 0.95) or tap outside the popup.
*observed* · `character/player_profile.png` · R-060

### R-027 · Keep away from the chat strip
Home's chat strip (y 0.82-0.90) opens Server Chat; a stray tap on the strip opens the chat panel (Server | Guild | Private) from any screen, even mid-fight. **Never type there.** Close it with the down chevron (42, 1226), about (0.06, 0.96). Detector state `chat`.
*observed* · `system/chat.png` · node `server_chat` · R-057

### R-053 · Find menu buttons by label; they move as features unlock
- Home menu buttons shift with unlocks (at Lv 10: Friends 0.14, Photo 0.32, Notice 0.49, User Center 0.67, Settings 0.85, y 0.85; later a second row plus Quest and Mall cards). Match labels.
- **The menu's event banner opens paid packs: never tap it** (R-043).
- Friends (social, R-057): Friends / Add Friends / Requests / Blocklist. Settings: Game, Graphics, Sound, Alerts, Other.
*observed* · `home/main_menu_lv10.png`, `home/friends.png` · node `main_menu`, `friends`, `settings` · R-010

### R-010 · A locked menu means "not yet", not an error
Menus unlock with tutorial progress and the game announces it. Each node's `unlock` field in `memory-bank/game/nav-graph.json` records the gate.
*told* · R-011, R-036

## Badges and claiming

### R-063 · A red "!" on a menu button or tab means something to claim
- Follow badges down to the claim button. Not the NPC "!" (talk, R-062) or the player "!" (R-080).
- Badged menus change with events: find badges on screen each run (template or colour), never a fixed menu list.
- Exception: Notice board tab badges mean unread posts.
*told* · `home/notice_board.png` · R-062, R-080, R-116, R-044

### R-116 · Claim every lit Goals tab with the claim-goals task
- Menus have milestone Goals tabs at the bottom. Whenever a Goals tab shows "!", claim it with the dedicated claim-goals task (mae). It's free, and an unclaimed "!" confuses the screen-state and upgrade readers (R-080), so clear it before reading the menu. It runs as its own pass, first in the upgrade loop (`goals`, R-080).
- Known tabs (free, shown with "!"): Skill (incl. "Battle Essence Used" milestones 8.8K, 13.1K, …), Enhance Gear, Rank, Class, Prayer (R-093), Vendor Booth Pts (R-120). Quest-like goals (tasks, not milestone rewards) follow their own rules.
*observed, told* · `character/skill_goals_quality.png`, `character/gear_goals.png`, `character/rank_level_goals.png`, `character/rank_power_goals.png`, `character/class_goals.png` · R-063

### R-129 · "Choose Your Reward": take the class match, else ask mae
- Some clears offer a choice of rewards ("Choose Your Reward", seen after clearing the Temple Ruins mini-dungeon, R-040). The detector can misread it as the Class page.
- If exactly one choice is marked "Class Mismatch", take the other, class-matched one (on by default, mae).
- If both choices are valid (or both mismatch), stop and ask mae.
- Code: detector state `choose_reward`, `sxs/actions/choose_reward.py` (class-match pick, `AUTO_PICK` on), called from explore.
*told, observed* · `dialogs/choose_reward_skill.png` · R-040, R-054

## Reading shops and items

### R-125 · Read items through their info cards, never the price button
- Tap an item's **icon**, not its price button (about 100 px lower), for a read-only card (name, type, owned, use, source); tap outside to close. `scripts/shop_survey.py` does a whole grid, icons only.
- Uses: Wood, Stone: furniture upgrades. Gold Pickaxe: Realm Gilded Depths. Worn Knuckles: Realm Dread Hollow. Refined Ore: gear enhancement (from dismantling advanced gear, Fantasia Ascent). Golden Beetle: skips a puzzle. Lucky Ticket: Wheel of Destiny. Water: cooking.
*observed* · `shops/vendor_booth_general.png` · R-043, R-120, R-114

### R-154 · Identify every unrecognized item or currency symbol
- Whenever you see a material, currency or item symbol you don't already recognize, find out what it is: tap the symbol for its read-only info card (name and description, R-125), then add it to the items and currency database, `resource/items/items.json` with icon crops in `resource/items/icons/`, always through `python -m sxs items add`, never by hand (full command: playbook.md, "Item and currency symbols"). Look-alike usage badges in Material Realms are kind `usage` under their own id. A symbol nobody can name yet gets the id "unknown" (stored as unknown_N) for mae to name (mae, 2026-11-10 06:24).
- It applies to every session, builders and the item-map work alike. Most symbols don't matter to the bot's decisions, but every one is a class for the Roboflow detector's training data.
- Tap only the icon, never a price or spend button (R-043).
*told* · R-018, R-019, R-043, R-125, R-131

### R-158 · Walk taps keep out of the HUD; stray taps open cards to close
- Island-map walk taps stay out of the HUD areas (720x1280 px): portrait, name and power (0–330, 0–200); flag (0–110, 200–260); minimap, zone name and Timed Packs (500–720, 0–450); Team button (0–90, 700–820); tracker, chat and the bottom bar (y > 950) (builder, 2026-11-10).
- A stray tap on the character opens our own profile popup; its charm row opens a charm card (e.g. "Heart of Flame", Rare, Lv 23, button Replace). **Never press Replace**: close it with the back arrow.
- Stray taps that opened the Class page and Timed Packs: R-076, R-157.
*observed* · node `player_profile` · R-030, R-076, R-142, R-157
