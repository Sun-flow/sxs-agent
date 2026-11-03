# Game rules

> **Last updated**: 2026-11-03
> Screen captures named below are in `docs/screens/`; captures from batches 4 onward (R-029 onward, plus `cart.png`) and the marker templates are on branch step3-explore until it merges.
> One entry per rule of the world that an agent acting in the game needs. Format and confidence levels: `memory-bank/game/README.md`. IDs are permanent; add new ones at the end of their topic with the next free number (next free: R-069).

Entry format:

```
### R-NNN · short title
- **Rule**: one or two sentences, stated so a script could act on it.
- **Confidence**: observed | told | reported. **Source**: who or what, and date.
- **Images**: repo paths, or "none yet".
- **Related**: other rule IDs or nav-graph node ids.
```

## Combat

### R-001 · All battles are automatic
- **Rule**: Every battle, PvE and PvP, plays itself. The bot never controls combat; it only starts battles and handles the screens before and after. On the map: tap a monster, then Start Battle on the prep screen; the battle runs up to 15 rounds ("Round n/15") and a win returns to the map within about 4 s, with no result screen.
- **Confidence**: observed (2026-11-03). **Source**: step 1 doc section 3; builder thread batch 1.
- **Images**: `docs/screens/battle_prep.png`, `docs/screens/battle.png`.
- **Related**: nodes `battle_prep`, `battle`. What a loss looks like is not known yet ❓.

## Exploration and the world map

### R-002 · Exploring an area means clearing green dots and mist
- **Rule**: An area is fully explored when every green dot on the minimap has been cleared, by walking to it and interacting with the thing it marks, and all the mist (fog of war) on that area's map is revealed.
- **Confidence**: told; partly observed (collecting pickups, beating monsters and walking into fog took Originisle I from 43 to 100, R-021). **Source**: mae, 2026-11-03; builder batch 2.
- **Images**: none yet (want: minimap with green dots; area with mist).
- **Related**: R-003, R-004, R-006.

### R-003 · A fully explored area unlocks a blessing statue
- **Rule**: Once R-002 is met for an area, a statue unlocks in it; interact with the statue to "bless" the area.
- **Confidence**: told; not yet seen in game, even after Originisle I reached 100 ❓. **Source**: mae, 2026-11-03.
- **Images**: none yet.
- **Related**: R-002, R-014.

### R-004 · Use the minimap for relative positions
- **Rule**: The minimap shows where items, interactables and enemies are relative to the character. Use it to choose which way to move to reach the next item or enemy. The island map also shows the player's tile coordinates as "(x, y)" under the minimap (for example "Originisle I (24,23)"), which the state detector reads by OCR; step 3 plans to combine minimap dots with these coordinates to plan walks.
- **Confidence**: told (minimap use); observed (coordinates). **Source**: mae, 2026-11-03; builder batch 3.
- **Images**: none yet (want: minimap crop with its icon types labelled).
- **Related**: R-002, node `world_map`.

### R-005 · Areas show an exploration percentage
- **Rule**: Each area tracks exploration as a percentage (Originisle was at 62% after the first part of the tutorial). 100% presumably means R-002 is met ❓. The Explore quest counter (R-021) is a separate n/100 count.
- **Confidence**: observed (the percentage); the link to R-002 is a guess. **Source**: builder thread, 2026-11-03.
- **Images**: none yet.
- **Related**: R-002.

### R-006 · The world has named regions
- **Rule**: Known regions: Originisle (starting area), Verdantglade, Cinder Ridge, Aqualis, Loong Haven.
- **Confidence**: observed for Originisle; reported for the rest. **Source**: builder thread; step 1 doc section 3.
- **Images**: none yet.
- **Related**: node `world_map`.

## Quests

### R-007 · Follow the quest guide to finish the tutorial
- **Rule**: The tutorial is driven by the quest guide; doing each quest it shows in order completes the tutorial.
- **Confidence**: told. **Source**: mae, 2026-11-03.
- **Images**: none yet.
- **Related**: R-008, R-009, node `quests`.

### R-008 · "Explore" quests need every item in the area
- **Rule**: A quest that says "Explore" an area is done by going to the overworld map and collecting all the items in that area, which means clearing its green dots and interacting with every interactable (R-002).
- **Confidence**: told. **Source**: mae, 2026-11-03.
- **Images**: none yet.
- **Related**: R-002, R-009, R-021 (observed detail).

### R-009 · Track a quest to get map markers
- **Rule**: A quest can be tracked. While tracked, the map squares that matter to it carry a quest marker symbol; tap those squares to progress the quest.
- **Confidence**: told. **Source**: mae, 2026-11-03.
- **Images**: none yet (want: the track button and the quest marker icon).
- **Related**: R-007, R-022 (observed detail), nodes `quests`, `world_map`.

## Unlocks and progression

### R-010 · Menus unlock with tutorial progress
- **Rule**: Some menus are locked until the tutorial reaches a certain point. The game makes it clear when one becomes usable, so the bot should treat a locked menu as "not yet", not as an error.
- **Confidence**: told. **Source**: mae, 2026-11-03.
- **Images**: none yet (want: a locked menu button and the unlock announcement).
- **Related**: `unlock` field of each node in `nav-graph.json`.

### R-011 · Some features unlock by account level
- **Rule**: Guilds unlock at account level 15, the Vendor Booth at 18, Fantomons at 51. In game the locked Guild tab says "Guild unlocks at Character Lv. 15", and the Travel Journal tab says "Unlock any mode to unlock Travel Journal".
- **Confidence**: observed for Guild and Travel Journal (builder, 2026-11-03); reported for the rest. **Source**: step 1 doc sections 4 and 5.
- **Images**: none.
- **Related**: R-010, nodes `guild`, `vendor`.

### R-012 · Seasons partly reset levels
- **Rule**: Seasons (the first about a month, later two to three months) partly reset levels, so level-based unlocks (R-011) must be re-checked each season.
- **Confidence**: reported. **Source**: step 1 doc section 3.
- **Images**: none.
- **Related**: R-011.

### R-013 · Servers cap at 5,000 players and merge
- **Rule**: A server holds up to 5,000 players and later merges with others; guilds are per server. Our test account is on server Forgehall.
- **Confidence**: reported. **Source**: step 1 doc section 3.
- **Images**: none.

## Daily content

### R-014 · Statues give one interaction a day
- **Rule**: Goddess, Witch and Hero statues on the map can each be interacted with once a day.
- **Confidence**: reported. **Source**: step 1 doc section 4. Unclear whether these are the same as the blessing statues of R-003 ❓.
- **Images**: none yet.
- **Related**: R-003.

### R-015 · Material dungeons have two free attempts each
- **Rule**: Each material dungeon has 2 free attempts a day; more attempts cost Dawnium.
- **Confidence**: reported. **Source**: step 1 doc section 4.
- **Images**: none yet.
- **Related**: R-018, node `dungeons`.

### R-016 · Guild donations: three basic a day
- **Rule**: A guild member can make 3 basic donations a day; the Guild Farm can be planted and harvested once a day.
- **Confidence**: reported. **Source**: step 1 doc section 4.
- **Images**: none yet.
- **Related**: R-011, node `guild`.

## Currencies and resources

### R-017 · Stamina caps at 300
- **Rule**: Stamina is spent on map nodes and caps at 300; stamina gained over the cap is wasted, so spend it before it fills. A free stamina pack is available daily in the Shop.
- **Confidence**: cap observed (top bar shows e.g. 52/300, lightning icon); the rest reported. **Source**: builder batch 1; step 1 doc section 4.
- **Images**: none yet `resource/image/currency/stamina.png` (step 3).
- **Related**: node `shop`.

### R-018 · Dawnium is the premium currency
- **Rule**: Dawnium buys extra dungeon attempts and items in the Shop's Vault. The bot should not spend it without a rule saying so.
- **Confidence**: the currency and its icon observed (orange diamond in the top bar); its uses reported. **Source**: builder batch 1; step 1 doc section 4.
- **Images**: none yet `resource/image/currency/dawnium.png` (step 3).
- **Related**: R-015.

### R-019 · Rolla is the common currency
- **Rule**: Rolla (gold coin icon, shown like "1.38K" in the top bar) pays for gear enhancement (R-023) and Daily Shop refreshes; early on it is the priority use of stamina. On the world map the top bar shows a fruit counter in its place.
- **Confidence**: icon and gear use observed; shop and stamina uses reported. **Source**: builder batch 1; step 1 doc section 4.
- **Images**: none yet `resource/image/currency/rolla.png` (step 3).
- **Related**: R-017.

### R-020 · The Cart collects AFK rewards
- **Rule**: The Cart accumulates rewards while offline, up to a cap; collect it at least once per cap period. It sits on the left of the Home scene (scroll the scene left); tap its coin bubble to collect, which opens a reward popup (Rolla, Stone, Wood).
- **Confidence**: observed (collecting); the cap is reported. **Source**: builder batch 1; step 1 doc sections 3 and 4.
- **Detail**: Tapping the cart itself opens a panel of hourly income, each line with a level and an upgrade arrow: Rolla +1000/h, Wood +50/h, Stone +50/h, Raw Ore +100/h and Battle Essence +125/h (the last two unlocked free in the tutorial at Lv 3); Gear "Unlocks at Lv. 15". "Claim All" (0.5, 0.86) collects; tap outside (0.5, 0.95) to close. Observed, builder batch 5.
- **Images**: `docs/screens/home_cart.png`, `docs/screens/cart.png`, `docs/screens/reward_popup.png`.
- **Related**: node `home`.

## Added from builder batch 1 (2026-11-03)

### R-021 · How the Explore quest counter rises
- **Rule**: An Explore quest ("Wild Isle Trek I: Explore Originisle I n/100") gains progress from walking into fog, collecting pickups (gold piles, plants, chests) and winning fights against roaming monsters. At 100/100 claim it with the gift icon on the quest tracker panel (0.42, 0.77). The next one is Wild Isle Trek II on Originisle II.
- **Confidence**: observed twice (Originisle I went from 43 to 100 this way). **Source**: builder batches 1 and 2, 2026-11-03.
- **Images**: `docs/screens/world_map_explore.png`, `docs/screens/world_map_quest_complete.png`.
- **Related**: R-002, R-008, node `world_map`.

### R-022 · Quest tracking puts a gold ring on the next target
- **Rule**: The target icon on the quest tracker panel (0.40, 0.79) toggles tracking. While on, a gold ring marks the next target; if the target is off screen the ring sits at the screen edge pointing to it. Tap the edge ring to pan the camera, then tap the item. The ring floats about 100 px (0.08 of the screen height) above its target, so tap below it. It can hide under the top-left avatar and level badge; dragging the map brings it back. Templates: `resource/image/explore/marker.png` (lit) and `resource/image/explore/marker_dim.png` (shadowed).
- **Confidence**: observed. **Source**: builder batches 1 and 4.
- **Images**: none yet (want: tracking ring on screen and at the edge).
- **Related**: R-009.

### R-023 · Gear enhancement costs ore and Rolla
- **Rule**: Character, then a gear slot, then the item card (Replace / Enhance), then Enhance Gear. Enhancing costs Raw Ore (blue crystal), Refined Ore (red crystal) and Rolla. Without enough, a toast says "Insufficient materials to enhance."
- **Confidence**: observed. **Source**: builder batch 1.
- **Images**: none yet (want: ore icon crops, Enhance Gear screen).
- **Related**: R-019, node `character`.

### R-024 · Server time is UTC-5; achievements refresh Mondays
- **Rule**: The server clock is UTC-5 and is shown on the menu screen. Achievement quests refresh on Mondays at 8:00 server time. Daily reset time is still unknown ❓.
- **Confidence**: observed. **Source**: builder batch 1.
- **Images**: `docs/screens/main_menu.png`.
- **Related**: node `main_menu`.

### R-025 · Moving on the island map
- **Rule**: Tap a spot to walk there; swipe to pan the camera. The character can't walk into thick fog.
- **Confidence**: observed. **Source**: builder batch 1.
- **Images**: `docs/screens/world_map.png`.
- **Related**: R-002, R-004.

### R-026 · Don't rely on the Android back key
- **Rule**: The Android back key does nothing on some screens (player profile). Use the on-screen back arrow (bottom left, 0.08, 0.95) or tap outside a popup instead.
- **Confidence**: observed. **Source**: builder batch 1.
- **Images**: `docs/screens/player_profile.png`.
- **Related**: nav-graph edge from `*`.

### R-027 · Keep away from the chat strip
- **Rule**: The chat strip on Home (y 0.82 to 0.90) opens Server Chat when tapped. If it opens, close it with the down arrow (0.06, 0.96) and never type there.
- **Confidence**: observed. **Source**: builder, 2026-11-03.
- **Images**: none yet.
- **Related**: node `server_chat`.

### R-028 · Story dialogue can appear over any screen
- **Rule**: Tutorial and story dialogue (Akane) overlays the current screen with a ▼ arrow at the bottom. Tap (0.5, 0.9) until it is gone, then carry on with what you were doing.
- **Confidence**: observed. **Source**: builder batch 1.
- **Images**: `docs/screens/dialogue.png`, `docs/screens/dialogue_loadout.png`.
- **Related**: node `dialogue`.

## Added from builder batch 4 (2026-11-03)

### R-029 · The first quest chain is Wild Isle Trek I to III
- **Rule**: Wild Isle Trek I (Originisle I), II (Originisle II) and III (Originisle III) follow each other. Reaching 100 on one moved the tracker to the next on its own (no claim screen was seen for Trek II). A story dialogue with Akane about a "Chaosborn" creature plays on Originisle II. The account reached Lv 3 after Originisle II.
- **Confidence**: observed. **Source**: builder batch 4.
- **Images**: none yet.
- **Related**: R-021, R-028, R-044 (what follows Trek III).

### R-030 · Map objects open a card with one action
- **Rule**: Tapping a map object (for example a Portal, "An ancient gateway that whisks you across space when activated") opens a card with one button at (0.5, 0.70), such as "Activate". Using it counts toward Explore progress. The bot only presses buttons with safe verbs: Activate, Collect, Claim, Open, Interact, Bless, Pray, Gather, Harvest, Mine, Examine, Read.
- **Confidence**: observed. **Source**: builder batch 4.
- **Images**: `docs/screens/interact_portal.png`.
- **Related**: R-002, R-021, node `interact`. See R-042 for which buttons the bot presses.

### R-031 · Losing a map fight sends you home
- **Rule**: After a lost fight a dialog says "Your character is incapacitated. Return to Home now?" with Cancel (0.32, 0.65) and OK (0.68, 0.65); OK goes home. The explore loop stops there. Lost at Lv 3 on Originisle III, so later islands may need stronger gear or levels first ❓.
- **Confidence**: observed. **Source**: builder batch 4.
- **Images**: `docs/screens/defeated.png`.
- **Related**: R-001, node `defeated`.

### R-032 · The camera doesn't follow the player
- **Rule**: After walking, the camera stays where it was, so the player and the target can drift to the screen edge. Re-centre by dragging the map or tapping the edge ring before the next tap.
- **Confidence**: observed. **Source**: builder batch 4.
- **Images**: none yet.
- **Related**: R-022, R-025.

### R-033 · Stamina regenerates slowly
- **Rule**: Stamina went from 51 to 55 in about 40 minutes, roughly 1 every 10 minutes ❓ (one sample).
- **Confidence**: observed once. **Source**: builder batch 4.
- **Images**: none.
- **Related**: R-017.

### R-034 · Exploring pays Dawnium and Rolla
- **Rule**: Exploring Originisle I to III raised Dawnium from 145 to 175 and Rolla to 3.76K, so exploration is a source of the premium currency.
- **Confidence**: observed. **Source**: builder batch 4.
- **Images**: none.
- **Related**: R-018, R-019, R-021.

## Added from builder batch 5 (2026-11-03)

### R-035 · The house bed gives AFK EXP and a free daily speed-up
- **Rule**: Scroll the home scene up to reach the house. Its bed ("Sleep to earn AFK EXP and speed up AFK resource collection", unlocked free) shows Blessing Level, Activated Lost Goddess Statues, Base EXP Yield, Production Bonus, EXP/Hr (50), EXP Reserve and Yield Progress. "Today's Free Speedup" is a **daily task**: one free speed-up per day. Using it took the account from Lv 3 to Lv 5. Other furniture slots unlock by level (one at Lv 7).
- **Confidence**: observed. **Source**: builder batch 5.
- **Images**: `docs/screens/home_house.png`, `docs/screens/bed.png`, `docs/screens/furniture_unlock.png`, `docs/screens/unlocked.png`.
- **Related**: R-003 (blessed statues likely raise the bed's Blessing Level ❓), R-020, nodes `home_house`, `bed`.

### R-036 · How the tutorial points at the next tap
- **Rule**: The tutorial marks what to tap with (a) a bright yellow pulsing rounded frame around it, (b) a small Akane chibi bubble ("Tap to unlock", "Tap to speed up", "Upgrade skill to Lv. 5") about 0.08 of the screen height above the button, or sometimes (c) a white or pale frame instead of yellow. Step 3's tutorial follower handles (a) and (b). Unlock results show a full-screen "UNLOCKED ..." card; tap to continue.
- **Confidence**: observed. **Source**: builder batch 5.
- **Images**: `docs/screens/tutorial_highlight.png`, `docs/screens/tutorial_highlight_dim.png`, `docs/screens/unlocked.png`.
- **Related**: R-007, R-028, node `tap_to_continue`.

### R-037 · Techniques are upgraded with Battle Essence, capped by level
- **Rule**: Character, then Skill (0.41, 0.59), opens the loadout (4 technique slots, 4 charm slots). Tap a technique, then Enhance, to reach the Upgrade screen; the upgrade button is at (0.5, 0.85) and costs Battle Essence. A technique's level can't exceed what the character level allows ("Unlocks at Character Lv. 6" at Lv 5). An Ascend tab exists but is unexplored.
- **Confidence**: observed. **Source**: builder batch 5.
- **Images**: `docs/screens/skill_loadout.png`, `docs/screens/technique_card.png`, `docs/screens/technique_upgrade.png`.
- **Related**: R-039, nodes `skill_loadout`, `technique_upgrade`.

### R-038 · Charms are equipped into one of four slots
- **Rule**: On the Charm tab, open a charm card (e.g. "Unstable Aura", Rare: 25% chance on technique hit to deal extra Wind DMG and knock back 1 grid), tap Equip, then tap one of the four pulsing right-hand slots.
- **Confidence**: observed. **Source**: builder batch 5.
- **Images**: none yet.
- **Related**: R-037.

### R-039 · Battle Essence is the skill currency
- **Rule**: Battle Essence (purple orb, shown top right on the upgrade screen) pays for technique upgrades; the Cart produces it at +125/h. So far it is the only soft currency the bot has spent (788 down to 448 for a few upgrades). Account at Lv 5, power 1.3K to 2.3K after these upgrades.
- **Confidence**: observed. **Source**: builder batch 5.
- **Images**: none yet (want: icon crop).
- **Related**: R-020, R-037.

## Added from builder batch 6 (2026-11-03)

### R-040 · Temple Ruins is a multi-floor mini-dungeon
- **Rule**: The "Temple Ruins" exploration card ("Crumbling sanctum of a forgotten temple. Time for some treasure hunts...") has an Explore button. Explore leads to a 6-enemy battle prep, an auto battle, then a floor card ("Temple Ruins: Floor 1 ... A faint echo of a legacy skill calls from its summit.") with Next Floor (0.5, 0.64) and a back arrow to leave. The number of floors is unknown; the summit seems to hold a "legacy skill" reward ❓. Found on Originisle III at 70% explored, account Lv 7, power 2.63K.
- **Confidence**: observed. **Source**: builder batch 6.
- **Images**: `docs/screens/interact_temple.png`, `docs/screens/dungeon_floor.png`.
- **Related**: R-030, nodes `interact`, `dungeon_floor`.

### R-041 · Guarded quest targets need their guards beaten first
- **Rule**: Some quest targets (the Pink Bird on Originisle III) are ringed by monsters drawn with gold corner brackets. The target only repeats a line ("Chirp! Chirp!") until all bracketed monsters are beaten (6 Chaosborn, won at Lv 6). Dialogue can also offer reply options, drawn as a white pill with a black arrow.
- **Confidence**: observed. **Source**: builder batch 6.
- **Images**: `docs/screens/dialogue_choice.png`.
- **Related**: R-022, R-028.

### R-042 · Card policy: what the bot presses depends on its goal
- **Rule**: Cards and dialogs are answered by a goal-dependent policy (`resource/policy/cards.json` and `sxs/decide.py` on the step 3 branch), not a fixed tap: defeated → OK (home); travel prompt → OK when exploring or doing dailies, Cancel when only going home; Portal → Activate; mini-dungeon card → Explore only when the goal is explore and HP is fine, else dismiss; dungeon floor → Next Floor when HP is fine, else the back arrow; unknown cards → dismiss and log. The nav graph's `when` field on edges records the same conditions.
- **Confidence**: told (mae's design principle), implemented by the builder. **Source**: builder batch 6.
- **Images**: none.
- **Related**: R-018, R-043, `memory-bank/game/README.md` (the `when` field).

### R-043 · Never press spending buttons
- **Rule**: The bot never presses Buy, Purchase, Refresh, Spend, Pray, Recharge or Top up, or any button mentioning Dawnium, unless a later policy rule explicitly allows it. Exception (R-061): buying or cooking healing food with Rolla or ingredients is allowed.
- **Confidence**: told (policy). **Source**: builder batch 6, following mae's budget rules.
- **Images**: none.
- **Related**: R-018, R-042.

## Added from builder batch 7 (2026-11-03)

### R-044 · Quest chain, side quests and claiming from the tracker
- **Rule**: After Trek III comes Wild Isle Trek IV (Originisle IV), then the boss quest "Fight the Guardian Colossi! Defeat Guardian Colossi 0/1". Side quests also show on the tracker ("Well Armed: Equip Gear x4", "Perfected Craft: Enhance Gear x1 to +10"). On Home, when the tracked quest shows a/b with a = b, tapping the tracker claims it; tapping an unfinished quest's title opens its detail card (Details, Goal, Rewards, and Go or Track); the ">" arrow on the tracker offers travel to its island.
- **Confidence**: observed. **Source**: builder batch 7.
- **Images**: `docs/screens/quest_detail_go.png`.
- **Related**: R-009, R-022, R-029, node `quest_detail`.

### R-045 · The tracker panel moves; bosses have their own pointer
- **Rule**: On the map the tracker panel's height and its tracking icon's x position change with the quest title's length (icon at x ≈ 287 px for "Wild Isle Trek III", ≈ 352 px for "Fight the Guardian Colossi!"), so find the icon by template, not a fixed spot. A boss target's off-screen pointer is a white ring with the boss portrait and a speech-bubble tail (template `resource/image/explore/marker_boss.png`), not the gold ring.
- **Confidence**: observed. **Source**: builder batch 7.
- **Images**: none yet.
- **Related**: R-022.

### R-046 · Low HP blocks fights until you heal
- **Rule**: Starting a fight while badly hurt shows "The character is badly wounded. Use dishes to heal?" with Return to Home and Quick Heal (costs dishes, e.g. 2; the dish count is top right). Repeated Quick Heal did not always clear it, and it eventually offered only Return to Home: perhaps the heal wasn't enough for the boss or dishes ran out ❓. Dishes come from the Alchemy Pot (R-047). See R-061 for mae's heal-and-retry policy; the dialog's word "dishes" may mean healing food here, not the rarer stat-boost dishes ❓.
- **Confidence**: observed; the cause of the stuck heal is unknown. **Source**: builder batch 7.
- **Images**: `docs/screens/wounded.png`.
- **Related**: R-031, R-047, node `wounded`.

### R-047 · The Alchemy Pot cooks healing dishes
- **Rule**: House furniture unlocked at Lv 7 that "melts down gear and even whips up tasty treats". On its Dish tab, Green Riceball restores 8% + 1000 HP and costs ingredients shown at the top (blue potion 10/2, green herb 5/4); Cook shows a "Cooked" banner. Jelly Bean Pals is a second recipe. Green Riceball looks like the cheap healing food of R-061 ❓; keeping it stocked keeps the explore loop going (R-046).
- **Confidence**: observed. **Source**: builder batch 7.
- **Images**: `docs/screens/furniture_alchemy_pot.png`, `docs/screens/alchemy_pot.png`, `docs/screens/cooked.png`.
- **Related**: R-035, R-046, node `alchemy_pot`.

### R-048 · Rank advancement raises base stats
- **Rule**: Character, then the Rank badge (bottom right), opens Rank Advancement. Apprentice I to II needs max level (20) and materials: Stone 5, a blue flower item 20 and Rolla 5.5K. Ranking up raised power from 4.15K to 5.21K at Apprentice I.
- **Confidence**: observed. **Source**: builder batch 7.
- **Images**: `docs/screens/rank_advancement.png`.
- **Related**: R-019, node `rank_advancement`.

### R-049 · What limits growth
- **Rule**: Technique level is capped at character level (R-037); gear enhancement is limited by Raw Ore, which the Cart makes at +100/h (R-020). The weapon reached +13. At this point the account was Lv 10, power about 5.3K, Rolla 9.7K and Dawnium 518, untouched per R-043.
- **Confidence**: observed. **Source**: builder batch 7.
- **Images**: none.
- **Related**: R-020, R-023, R-037, R-043.

## Added from builder batch 8 (2026-11-03)

### R-050 · The class choice comes after the Guardian Colossi
- **Rule**: After the boss, "Crossroads of Classes: Talk to the Mysterious Elder" leads to the Chief at the Originisle V pillar. Its dialogue offers "Ascend to Mage", "Change Class" or "Leave". This is a decision for mae, not the bot: the bot picks Leave and stops with `needs_decision`. mae chose **Mage** on 2026-11-03 (the class can be changed later; R-054). Boss loot (chests, an orb, an ore pile) lies around the pillar.
- **Confidence**: observed. **Source**: builder batch 8.
- **Images**: `docs/screens/class_choice.png`.
- **Related**: R-041 (dialogue choices), R-042, node `class_choice`.

### R-051 · Events and their daily sign-ins are on the Notice board
- **Rule**: The Notice board (tabs Notice / System / News) lists events. A Halloween event, "Haunted Carnival", runs 25 October to 14 November with a daily Carnival Sign-In: a **daily task** while it runs. Event names and dates change, so read them each time rather than hard-coding them.
- **Confidence**: observed. **Source**: builder batch 8.
- **Images**: `docs/screens/notice.png`.
- **Related**: node `notice`; step 1 doc's "Mail, event check-ins, codes".

### R-052 · Exploration Goals reward exploration milestones
- **Rule**: The World tab's bottom-left button opens Exploration Goals. Its Progress tab lists per-region milestones with rewards (Originisle Exploration 82/100; Verdantglade Exploration 0/5, 0/10, 0/15, 0/20), and its Explore tab lists Destiny Exploration Goals (0/20 up to 0/100). The world overview shows each island's score and rank ("Originisle 82, Ahead of 59.7% of Players"). Claiming milestones is likely worth adding to the daily loop ❓.
- **Confidence**: observed. **Source**: builder batch 8.
- **Images**: `docs/screens/exploration_goals.png`, `docs/screens/destiny_exploration_goals.png`.
- **Related**: R-002, R-005, node `exploration_goals`.

### R-053 · Menu buttons move as features unlock
- **Rule**: At Lv 10 the menu gains Friends and the bottom row shifts (Friends 0.14, Photo 0.32, Notice 0.49, User Center 0.67, Settings 0.85, all at y 0.85). Find menu buttons by their label, not a fixed position. Friends holds 60; tabs Friends / Add Friends / Requests / Blocklist. Settings has Game, Graphics, Sound, Alerts and Other tabs.
- **Confidence**: observed. **Source**: builder batch 8.
- **Images**: `docs/screens/main_menu_lv10.png`, `docs/screens/friends.png`.
- **Related**: R-010, nodes `main_menu`, `friends`, `settings`.

## Added from builder batch 9 (2026-11-03)

### R-054 · Ascending to a class
- **Rule**: Choosing "Ascend to Mage" at the Chief opens the class screen: Mage trait Base HP +5%, ATK +14%, DEF +5%, SPD +6%, a grid of class skills ("Prayer will feature the class skills") and Ascend at (0.5, 0.86). Power went from 5.24K to 5.73K. The next quest is Wild Isle Trek V (Explore Originisle V, already 50% after the boss). The bot never makes a class choice itself; `python -m sxs.explore --choose "<regex>"` applies a human's choice.
- **Confidence**: observed. **Source**: builder batch 9; mae's choice.
- **Images**: `docs/screens/class_choice.png`, `docs/screens/class_ascend.png`.
- **Related**: R-050, node `class_ascend`.

### R-055 · Prayer is the skill gacha; the bot never prays
- **Rule**: The Statue furniture ("Pray to the goddess and embrace her divine power") on home, next to the "Class to Unlock" stone, opens Prayer: Pray x1 / Pray x10 cost blue prayer tickets (counter top right, with "+" to buy more), Prayers Today n/10000, "200 Prayers Bonus: a Legendary skill of your choice", a pity counter ("Prayer x70 away from a guaranteed Legendary skill"), a banner selector (Mage) and tabs Prayer / Exchange / Goals. The tutorial gives 10 free tickets; one x10 pull gave Cyclone (Epic wind: pick a grid within 6, knock up and pull), Flame Jet (Rare fire, 3 hits in a 1x3 area), Heart of Flame, Dew's Blessing and shards (Tough Soul, Flame Jet, Insight); power rose to 6.79K once equipped. **The bot never taps Pray or any spend-looking button (Pray, Buy, Purchase, Refresh, Spend, Dawnium, Recharge, Top up) on its own.**
- **Confidence**: observed. **Source**: builder batch 9.
- **Images**: `docs/screens/furniture_statue.png`, `docs/screens/prayer.png`, `docs/screens/prayer_result.png`.
- **Related**: R-043 (now with Pray, Recharge and Top up added), nodes `prayer`, `prayer_result`.

### R-056 · Equipping and levelling techniques
- **Rule**: Each loadout has 4 technique slots on the left. Equip from the Technique tab: card, Equip, then tap an empty slot. New techniques start at Lv 1; levelling Cyclone from 1 to 10 cost about 490 Battle Essence.
- **Confidence**: observed. **Source**: builder batch 9.
- **Images**: `docs/screens/skill_loadout.png`.
- **Related**: R-037, R-039.

### R-057 · Social requests are left alone
- **Rule**: A person icon with a badge on the map's left edge (0.06, 0.6) opens "Apply": tabs Friends / Team Up / Challenge / Room, incoming friend requests with x and check, Decline All and Agree All. The bot doesn't touch these; accepting or declining is mae's call.
- **Confidence**: observed. **Source**: builder batch 9.
- **Images**: `docs/screens/apply_requests.png`.
- **Related**: R-053, node `apply_requests`.

### R-058 · Loot behind the Chief is out of reach until you talk to him
- **Rule**: After the boss, the loot row next to the Chief (ore pile, blue orb, chest, red chest) sits on a ledge. Tapping it only walks the player to the grass below, and the tracker keeps pointing there, so the explore loop can get stuck on it. Resolved by mae: talk to the Chief first; he gives instructions and disappears, which opens the ledge (R-062).
- **Confidence**: observed (the problem); told (the fix). **Source**: builder batch 9.
- **Images**: `docs/screens/world_map_loot_ledge.png`.
- **Related**: R-022, R-025.

### R-059 · Home scene labels can be misread as the tracker
- **Rule**: On home, the scene's own labels (for example the stone's "Class to Unlock") overlap the quest tracker's region, so OCR of the tracker must filter them out.
- **Confidence**: observed. **Source**: builder batch 9.
- **Images**: none.
- **Related**: R-044.

### R-060 · Close popups by tapping above them
- **Rule**: Popups close on a tap above them, at (0.5, 0.05), not below.
- **Confidence**: observed. **Source**: builder batch 9. Earlier, (0.5, 0.95) closed the player profile, so either may work there.
- **Images**: none.
- **Related**: nodes `cart`, `player_profile`, `apply_requests`.

## Added from mae (2026-11-03, evening)

### R-061 · Heal and retry a lost fight at most twice
- **Rule**: Healing food (cooked from ingredients in the Alchemy Pot, or bought with Rolla) is cheap and fine to spend: eat it from the player portrait, then the button on the right ("Recover" or similar). While fights are being won, heal as freely as needed; Rolla is abundant early. **Dishes** are different: rarer items that give temporary stat boosts for a fight, so conserve them. If the same fight is lost twice in a row after healing, stop retrying: contact mae or go back to base to get stronger (gear, techniques, rank) first.
- **Confidence**: told. **Source**: mae, 2026-11-03.
- **Images**: none yet (want: the profile's Recover button).
- **Related**: R-031, R-043, R-046, R-047, nodes `player_profile`, `wounded`, `alchemy_pot`.

### R-062 · NPCs with a red "!" gate progress
- **Rule**: Quests can be locked behind NPC interactions. An NPC with a red exclamation mark above its head on the world map or overworld (Originisle, Verdantglade...) must be talked to first; it gives instructions on how to progress and then disappears, unlocking the objects around it (for example the Chief at the Originisle V pillar guards the boss loot row). When the tracker points at something that can't be reached, look for a red "!" NPC nearby and tap it first.
- **Confidence**: told. **Source**: mae, 2026-11-03.
- **Images**: none yet (want: an NPC with the red "!").
- **Related**: R-041, R-058, R-063 (the other kind of "!").

### R-063 · A red "!" in a UI menu means something to claim
- **Rule**: A red "!" badge on a menu button or tab (not above an NPC in the world) means there is something to claim inside. Follow the badges down to the claim button. Treat it differently from the NPC "!" of R-062, which means talk to them. Which menus carry badges changes over time as event banners roll over, so a claim sweep must find badges on screen each run (template or colour), not walk a fixed list of menus.
- **Confidence**: told. **Source**: mae, 2026-11-03.
- **Images**: none yet (want: a menu badge).
- **Related**: R-062, R-044 (claiming quests).

### R-064 · Some quests progress by NPC instructions, not the marker
- **Rule**: Some quests aren't tracked well by their objective marker and rely on narrative instructions from NPC dialogue. When the tracker points somewhere unreachable or tapping does nothing (for example "Unlock Moonveil Woods" pointing into fog), open the full map by tapping the minimap and look for any "!" NPC to speak to; an NPC probably gave directions that were missed. So the bot should capture and log NPC dialogue text, so instructions aren't lost and a later step (or a model) can read them.
- **Confidence**: told. **Source**: mae, 2026-11-03.
- **Images**: none yet.
- **Related**: R-028, R-058, R-062.

### R-065 · Side areas: walk the fog edge when stuck or between quests
- **Rule**: Many "side areas" have no quest attached but give resources and levels. When stuck, or between quests, walk along the fog edge of the current region (for example Verdantglade) and explore anything unexplored; walking into the fog edge also reveals and unlocks new areas.
- **Confidence**: told. **Source**: mae, 2026-11-03.
- **Images**: none.
- **Related**: R-002, R-021, R-025, R-064.

## Map reading

### R-066 · Minimap legend: it shows the true tiles
- **Rule**: The minimap (circle at the top right of the island map, region name and "(x, y)" below it) shows the game's true tiles, so it can be read as a grid map. Known tile types:
  - **green dots**: items or POIs to pick up;
  - **light green**: explored walkable terrain;
  - **light green under a shadow**: walkable terrain not yet explored;
  - **dark green**: walls (lighter when explored, darker when not);
  - **transparent cross-hatch with no colour beneath**: unspotted terrain, which turns into one of the known types once the player gets close.
  Other types exist and aren't catalogued yet. Shadowed walkable areas that connect to explored ground are reachable targets for exploration (R-065). mae asked the builder for a minimap reader that classifies these tiles and marks POIs, to plan walks with the coordinates (R-004).
- **Confidence**: told. **Source**: mae, 2026-11-03, with a marked-up screenshot of Verdantglade II (173, 104) circling a shadowed area joined to explored ground (not committed: it shows other players' chat). A clean capture from the builder is wanted.
- **Images**: none yet.
- **Related**: R-002, R-004, R-025, R-065.

### R-067 · Areas connect by land bridges: path-find, don't walk straight
- **Rule**: Areas join through land connections that can be far from the straight line to a target; for example, the way from Verdantglade II into Moonveil Woods is a land bridge at the bottom of the minimap. Straight-line walking will often hit walls or water, so the bot needs path-finding over the walkable tiles read from the minimap (R-066), heading for the connection first.
- **Confidence**: told. **Source**: mae, 2026-11-03.
- **Images**: none yet.
- **Related**: R-025, R-064, R-066.

### R-068 · Travel to a far or unexplored area through the full map
- **Rule**: To move somewhere distant or unexplored: tap the minimap to open the full area map; look for unexplored areas on it; tap the spot you want the camera over (this centres the camera there); close the map, and the camera now shows that spot; then tap the ground where you want to go and the player auto-paths there, around walls and through land bridges (R-067). This is the intended way to reach unexplored areas found on the map.
- **Confidence**: told. **Source**: mae, 2026-11-03.
- **Images**: `docs/screens/world_area_map.png` (step 3 branch).
- **Related**: R-025, R-032, R-065, R-066, R-067, node `area_map`.
