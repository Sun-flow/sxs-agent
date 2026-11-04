# Game rules

> **Last updated**: 2026-11-03
> Screen captures named below are in `docs/screens/`; templates in `resource/image/`.
> One entry per rule of the world that an agent acting in the game needs. Format and confidence levels: `memory-bank/game/README.md`. IDs are permanent; add new ones at the end of their topic with the next free number (next free: R-123).

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
- **Confidence**: told; observed as the Goddess Statue (R-070). **Source**: mae, 2026-11-03.
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
- **Rule**: Guilds unlock at account level 15, the Vendor Booth at 18, Fantomons at 51. In game the locked Guild tab says "Guild unlocks at Character Lv. 15", and the Travel Journal tab says "Unlock any mode to unlock Travel Journal". In practice the Guild unlocked at Lv 20 (2026-11-04): the bottom bar's 4th icon (a crest, about (0.68, 0.97)) lit up with a tutorial highlight. So the Lv 15 label isn't the real gate ❓.
- **Confidence**: observed for Guild and Travel Journal (builder, 2026-11-03); reported for the rest. **Source**: step 1 doc sections 4 and 5.
- **Images**: `docs/screens/home_guild_tutorial.png` (guild tutorial at Lv 20).
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
- **Rule**: A guild member can make 3 basic donations a day; the Guild Farm can be planted and harvested once a day. The bot donates at most twice a day (mae's rule, R-103).
- **Confidence**: reported. **Source**: step 1 doc section 4.
- **Images**: none yet.
- **Related**: R-011, R-103, node `guild`.

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
- **Rule**: The target icon on the quest tracker panel (0.40, 0.79) toggles tracking. While on, a gold ring marks the next target; if the target is off screen the ring sits at the screen edge pointing to it. Tap the edge ring to pan the camera, then tap the item. The ring floats about 100 px (0.08 of the screen height) above its target, so tap below it. It can hide under the top-left avatar and level badge; dragging the map brings it back. It can also sit on the area name and coordinates under the minimap, which breaks `world_map` detection; nudge the camera to uncover them (builder batch 12). Templates: `resource/image/explore/marker.png` (lit) and `resource/image/explore/marker_dim.png` (shadowed).
- **Confidence**: observed. **Source**: builder batches 1, 4 and 12.
- **Images**: none yet (want: tracking ring on screen and at the edge).
- **Related**: R-009.

### R-023 · Gear enhancement costs ore and Rolla
- **Rule**: Character, then a gear slot, then the item card (Replace / Enhance), then Enhance Gear. Enhancing costs Raw Ore (blue crystal), Refined Ore (red crystal) and Rolla. Without enough, a toast says "Insufficient materials to enhance." The Enhance Gear screen has 4 tabs along the top, one per piece (weapon, head, chest, boots so far; no offhand yet), each showing "+N". The selected piece shows a big "+21 → +22" line at y≈0.42, the stat deltas, the cost (for example Raw Ore 7/720 and Rolla 43K/1.44K) and Enhance at (0.5, 0.85), plus a Resonance button and a Goals tab. On 2026-11-04 the levels were staff +21, hat +12, armour +9, boots +2, and ore was the bottleneck. How to spread levels: R-092. The screen isn't a detector state yet, so `go_home` gets stuck on it.
- **Confidence**: observed. **Source**: builder batch 1 and the final step 3 batch.
- **Images**: none yet (want: ore icon crops, Enhance Gear screen).
- **Related**: R-019, R-092, nodes `character`, `enhance_gear`.

### R-024 · Server time is UTC-5; achievements refresh Mondays
- **Rule**: The server clock is UTC-5 and is shown on the menu screen. Achievement quests refresh on Mondays at 8:00 server time. Dailies reset at 8:00 server time (UTC-5), going by the Daily Sign-in calendar (R-097).
- **Confidence**: observed. **Source**: builder batch 1; dailies batch 1.
- **Images**: `docs/screens/main_menu.png`, `docs/screens/daily_signin.png`.
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
- **Rule**: Stamina went from 51 to 55 in about 40 minutes, roughly 1 every 10 minutes ❓ (one sample). How to spend it: R-107. Later reading: about 1 per 11 to 12 minutes, cap 300 (R-108).
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
- **Rule**: Scroll the home scene up to reach the house. Its bed ("Sleep to earn AFK EXP and speed up AFK resource collection", unlocked free) shows Blessing Level, Activated Lost Goddess Statues, Base EXP Yield, Production Bonus, EXP/Hr (50), EXP Reserve and Yield Progress. "Today's Free Speedup" is a **daily task**: one free speed-up per day. Using it took the account from Lv 3 to Lv 5. The bed also stores AFK EXP to collect (R-101). Other furniture slots unlock by level (one at Lv 7).
- **Confidence**: observed. **Source**: builder batch 5.
- **Images**: `docs/screens/home_house.png`, `docs/screens/bed.png`, `docs/screens/furniture_unlock.png`, `docs/screens/unlocked.png`.
- **Related**: R-003 (blessed statues likely raise the bed's Blessing Level ❓), R-020, R-101, nodes `home_house`, `bed`.

### R-036 · How the tutorial points at the next tap
- **Rule**: The tutorial marks what to tap with (a) a bright yellow pulsing rounded frame around it, (b) a small Akane chibi bubble ("Tap to unlock", "Tap to speed up", "Upgrade skill to Lv. 5") about 0.08 of the screen height above the button, or sometimes (c) a white or pale frame instead of yellow. Step 3's tutorial follower handles (a) and (b). Unlock results show a full-screen "UNLOCKED ..." card; tap to continue.
- **Confidence**: observed. **Source**: builder batch 5.
- **Images**: `docs/screens/tutorial_highlight.png`, `docs/screens/tutorial_highlight_dim.png`, `docs/screens/unlocked.png`.
- **Related**: R-007, R-028, node `tap_to_continue`.

### R-037 · Techniques are upgraded with Battle Essence, capped by level
- **Rule**: Character, then Skill (0.41, 0.59), opens the loadout (4 technique slots, 4 charm slots). Tap a technique, then Enhance, to reach the Upgrade screen; the upgrade button is at (0.5, 0.85) and costs Battle Essence. A technique's level can't exceed what the character level allows ("Unlocks at Character Lv. 6" at Lv 5). An Ascend tab exists but is unexplored. A faster route: tap a skill, then the "Quick Upgrade" button beside the lower-right charm (R-104).
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
- **Rule**: The bot never presses Buy, Purchase, Refresh, Spend, Pray, Recharge or Top up, or any button mentioning Dawnium, unless a later policy rule explicitly allows it. Exception (R-061): buying or cooking healing food with Rolla or ingredients is allowed; skill pulls only through mae's own script (R-093); the first two guild donations of the day, even when they cost Dawnium (R-103). Also never: "Catch Up" on the sign-in calendar, "Advanced Trial", Dawnstar Prelude draws, Iron Hammer purchases, the main menu's event-banner packs (e.g. "Halloween Charmer", USD 2.99), and Link Account or anything else account-related.
- **Confidence**: told (policy). **Source**: builder batch 6, following mae's budget rules.
- **Images**: none.
- **Related**: R-018, R-042, R-093, R-095 to R-098.

## Added from builder batch 7 (2026-11-03)

### R-044 · Quest chain, side quests and claiming from the tracker
- **Rule**: After Trek III comes Wild Isle Trek IV (Originisle IV), then the boss quest "Fight the Guardian Colossi! Defeat Guardian Colossi 0/1". Side quests also show on the tracker ("Well Armed: Equip Gear x4", "Perfected Craft: Enhance Gear x1 to +10"). On Home, when the tracked quest shows a/b with a = b, tapping the tracker claims it; tapping an unfinished quest's title opens its detail card (Details, Goal, Rewards, and Go or Track); the ">" arrow on the tracker offers travel to its island.
- **Confidence**: observed. **Source**: builder batch 7.
- **Images**: `docs/screens/quest_detail_go.png`.
- **Related**: R-009, R-022, R-029, node `quest_detail`.

### R-045 · The tracker panel moves; bosses have their own pointer
- **Rule**: On the map the tracker panel's height and its tracking icon's x position change with the quest title's length (icon at x ≈ 287 px for "Wild Isle Trek III", ≈ 352 px for "Fight the Guardian Colossi!"), so find the icon by template, not a fixed spot. The gift icon at the panel's right end (`resource/image/explore/tracker_gift.png`) claims a finished quest more reliably than tapping the text. A boss target's off-screen pointer is a white ring with the boss portrait and a speech-bubble tail (template `resource/image/explore/marker_boss.png`), not the gold ring.
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
- **Rule**: At Lv 10 the menu gains Friends and the bottom row shifts (Friends 0.14, Photo 0.32, Notice 0.49, User Center 0.67, Settings 0.85, all at y 0.85). Find menu buttons by their label, not a fixed position. Friends holds 60; tabs Friends / Add Friends / Requests / Blocklist. Settings has Game, Graphics, Sound, Alerts and Other tabs. Later the menu has a second row (Friends, Gallery, Photo, Notice, User Center, Settings) and Quest and Mall cards; its event banner opens paid packs, never tap it (R-043).
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
- **Rule**: The Statue furniture ("Pray to the goddess and embrace her divine power") on home, next to the "Class to Unlock" stone, opens Prayer: Pray x1 / Pray x10 cost blue prayer tickets (counter top right, with "+" to buy more), Prayers Today n/10000, "200 Prayers Bonus: a Legendary skill of your choice", a pity counter ("Prayer x70 away from a guaranteed Legendary skill"), a banner selector (Mage) and tabs Prayer / Exchange / Goals. The tutorial gives 10 free tickets; one x10 pull gave Cyclone (Epic wind: pick a grid within 6, knock up and pull), Flame Jet (Rare fire, 3 hits in a 1x3 area), Heart of Flame, Dew's Blessing and shards (Tough Soul, Flame Jet, Insight); power rose to 6.79K once equipped. **The bot never taps Pray or any spend-looking button (Pray, Buy, Purchase, Refresh, Spend, Dawnium, Recharge, Top up) on its own.** The one exception is a dedicated pull script that mae (the handler) starts by hand (R-093).
- **Confidence**: observed. **Source**: builder batch 9.
- **Images**: `docs/screens/furniture_statue.png`, `docs/screens/prayer.png`, `docs/screens/prayer_result.png`.
- **Related**: R-043 (now with Pray, Recharge and Top up added), R-093, nodes `prayer`, `prayer_result`.

### R-056 · Equipping and levelling techniques
- **Rule**: Each loadout has 4 technique slots on the left. Equip from the Technique tab: card, Equip, then tap an empty slot. New techniques start at Lv 1; levelling Cyclone from 1 to 10 cost about 490 Battle Essence.
- **Confidence**: observed. **Source**: builder batch 9.
- **Images**: `docs/screens/skill_loadout.png`.
- **Related**: R-037, R-039.

### R-057 · Social requests are left alone
- **Rule**: A person icon with a badge on the map's left edge (0.06, 0.6) opens "Apply": tabs Friends / Team Up / Challenge / Room, incoming friend requests with x and check, Decline All and Agree All. The bot doesn't touch these; accepting or declining is mae's call. Friend Request toasts (X / check) that pop up on home near the tracker are left alone too (dailies batch 2).
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
- **Rule**: Popups close on a tap above them, at (0.5, 0.05), not below. Rating and feedback popups are fine to dismiss with their "Later" button (mae, 2026-11-04 08:27); never rate or open the store. The one seen so far: Akane asks "Dear adventurer, do you satisfy with your experience in Kanstein?" with Very Satisfied (0.50, 0.55), Dissatisfied (0.50, 0.62) and Later (0.50, 0.69); it appeared after skill pulls. Always press Later. The detector knows it as `RatingPopup`, and the navigator's toward-home step taps Later.
- **Confidence**: observed; rating popups told (mae). **Source**: builder batch 9; mae 2026-11-04 08:27; upgrade-systems builder. Earlier, (0.5, 0.95) closed the player profile, so either may work there.
- **Images**: `docs/screens/rating_popup.png`.
- **Related**: nodes `cart`, `player_profile`, `apply_requests`.

## Added from mae (2026-11-03, evening)

### R-061 · Heal and retry a lost fight at most twice
- **Rule**: Healing food (cooked from ingredients in the Alchemy Pot, or bought with Rolla) is cheap and fine to spend: eat it from the player portrait, then the button on the right ("Recover" or similar). While fights are being won, heal as freely as needed; Rolla is abundant early. **Dishes** are different: rarer items that give temporary stat boosts for a fight, so conserve them. If the same fight is lost twice in a row after healing, stop retrying: contact mae or go back to base to get stronger (gear, techniques, rank) first. **Before any fight, HP must be at least 70%**; if it's lower, heal first (read HP from the HUD bar, R-078). Decide heal need from the HP bar only. A red "!" over the player character does not by itself mean heal: it can also mean charms or other gear are ready to equip, among other things (R-080). (The step 3 explore loop heals below 80%, which already satisfies this.)
- **Confidence**: told. **Source**: mae, 2026-11-03; "!" correction 2026-11-04.
- **Images**: none yet (want: the profile's Recover button).
- **Related**: R-031, R-043, R-046, R-047, R-078, nodes `player_profile`, `wounded`, `alchemy_pot`.

### R-080 · A red "!" over the player means check the character panel
- **Rule**: A red "!" above the player character on the overworld is a general "something to do with your character" badge, not a heal signal. Causes include charms (or other gear) ready to equip, and possibly low HP among others. When it appears, open the character panel (HUD portrait), follow the badged tab and handle it (equip, upgrade or claim, within the spending rules); decide whether to heal only from the HP bar (R-061, R-078). On the character panel (tap your own character, or the HUD portrait), red badges mark empty Charm slots (row at y≈0.71) and blue badges on Equip mark available gear upgrades. To fill a charm slot: tap an empty charm slot, which opens the loadout editor "Edit" (techniques on the left, 4 charm slots on the right at x≈0.87, y≈0.21 / 0.30 / 0.39 / 0.48). It opens on the Technique tab; the Charm tab is at (0.56, 0.62). Tap a charm to open its card (for example "Heart of Flame", Rare, Fire Affinity 166, source Skill Prayer), press Equip (0.5, 0.70), then tap an empty slot. Once a slot is filled the button reads Replace. The 4th charm slot was still locked at Lv 13. The Rcmd button opens "Rcmd Loadouts" (Beginner's Pick, AoE DMG) with Apply; the bot doesn't use it. Filling the slots also completed "Combat Master: Equip 6 Skills 6/6". Any "!" on the character screen generally means an upgrade is available (skills, gear and so on): always check it and take the upgrade, within the spending rules (mae, 2026-11-04). Seen live: the badges sit on the gear slots, Skill, Class and the rank badge ("Apprentice I"), and inside the next screens they mark the exact tab or button to press. Badges pulse, so check 2 frames before deciding there's none. Code: `sxs/badges.py`, `sxs/upgrade.py`. Do not block fights on the "!" alone: the explore loop got stuck treating a charm "!" as a heal request. Also beware mis-taps: when the quest marker sits next to the player, a tap meant for the marker can land on the player sprite and open the character panel instead; aim off the sprite or move first.
- **Confidence**: told (mae); badge colours and the mis-tap observed by the builder. **Source**: mae, 2026-11-04; builder thread, 2026-11-04.
- **Images**: `docs/screens/player_profile_charm_badges.png`, `docs/screens/loadout_edit_charms.png`, `docs/screens/charm_detail.png`, `docs/screens/rcmd_loadouts.png` (step 3 branch).
- **Related**: R-061, R-063, R-078, nodes `player_profile`, `loadout_edit`, `charm_detail`, `rcmd_loadouts`, R-034, R-104, R-115 to R-119.

### R-062 · NPCs with a red "!" gate progress
- **Rule**: Quests can be locked behind NPC interactions. An NPC with a red exclamation mark above its head on the world map or overworld (Originisle, Verdantglade...) must be talked to first; it gives instructions on how to progress and then disappears, unlocking the objects around it (for example the Chief at the Originisle V pillar guards the boss loot row). When the tracker points at something that can't be reached, look for a red "!" NPC nearby and tap it first.
- **Confidence**: told. **Source**: mae, 2026-11-03.
- **Images**: none yet (want: an NPC with the red "!").
- **Related**: R-041, R-058, R-063 (the other kind of "!").

### R-063 · A red "!" in a UI menu means something to claim
- **Rule**: A red "!" badge on a menu button or tab (not above an NPC in the world) means there is something to claim inside. Follow the badges down to the claim button. Treat it differently from the NPC "!" of R-062, which means talk to them. Which menus carry badges changes over time as event banners roll over, so a claim sweep must find badges on screen each run (template or colour), not walk a fixed list of menus. Exception: on the Notice board (Menu, then Notice) red badges on the tabs mean unread posts, not claims (dailies batch 1).
- **Confidence**: told. **Source**: mae, 2026-11-03.
- **Images**: `docs/screens/notice_board.png` (unread badges).
- **Related**: R-062, R-044 (claiming quests), R-051.

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
  - **gold buildings**: interactable structures. The biggest are dungeons, which become daily challenges once cleared naturally the first time (step 1 doc's daily dungeons); smaller ones are mini-dungeons such as mines (R-071). (mae, 2026-11-03.)
  Other types exist and aren't catalogued yet. Shadowed walkable areas that connect to explored ground are reachable targets for exploration (R-065). mae asked the builder for a minimap reader that classifies these tiles and marks POIs, to plan walks with the coordinates (R-004).
- **Detail** (builder batch 10, `sxs/minimap.py` on the step 3 branch): about 8 px per tile; the player sits at the centre (0.856, 0.138), radius about 86 px. OpenCV HSV thresholds: walkable explored S<95, V>=115 (BGR about 103,144,128); walkable unexplored is the same colour shaded about 0.55x (BGR about 56,75,65); wall explored S>=95, V>=85 (BGR about 59,106,69); wall unexplored V<85 (BGR about 32,57,38); unspotted grey S<35, V about 35.
- **Confidence**: told (legend), observed (thresholds). **Source**: mae, 2026-11-03, with a marked-up screenshot of Verdantglade II (173, 104), not committed because it shows other players' chat; builder batch 10.
- **Images**: `docs/screens/minimap/minimap_verdantglade2.png` (raw), `docs/screens/minimap/minimap_classified.png`, tile crops `docs/screens/minimap/tile_walk_explored.png`, `docs/screens/minimap/tile_walk_unexplored.png`, `docs/screens/minimap/tile_wall_explored.png`, `docs/screens/minimap/tile_wall_unexplored.png`, `docs/screens/minimap/tile_unspotted.png`.
- **Related**: R-002, R-004, R-015, R-025, R-065, R-071.

### R-067 · Areas connect by land bridges: path-find, don't walk straight
- **Rule**: Areas join through land connections that can be far from the straight line to a target; for example, the way from Verdantglade II into Moonveil Woods is a land bridge at the bottom of the minimap. Straight-line walking will often hit walls or water, so the bot needs path-finding over the walkable tiles read from the minimap (R-066), heading for the connection first.
- **Confidence**: told. **Source**: mae, 2026-11-03.
- **Images**: none yet.
- **Related**: R-025, R-064, R-066.

### R-068 · Travel to a far or unexplored area through the full map
- **Rule**: To move somewhere distant or unexplored: tap the minimap to open the full area map; look for unexplored areas on it; tap the spot you want the camera over (this centres the camera there); close the map, and the camera now shows that spot; then tap the ground where you want to go and the player auto-paths there, around walls and through land bridges (R-067). This is the intended way to reach unexplored areas found on the map. The white box on the area map is the camera viewport. The map's zoom differs between openings, so labels land at different screen spots each time: pick places by their OCR'd label, never by fixed position. Match labels exactly, including trailing numerals: when OCR misses "Verdantglade III", a loose match picks "Verdantglade I" instead, so a different numeral means a different area. An area whose label sits in fog can't be reached this way (walking there fails with `no_move`); travel from home instead (R-089). Auto-pathing works even through gaps you can't see on screen. Code: `sxs/goto.py` (`python -m sxs.goto "Area Name"` or `X Y`); this route got the bot into Moonveil Woods.
- **Confidence**: told, then observed (builder batches 11 and 12). **Source**: mae, 2026-11-03; builder batches 11 and 12, 2026-11-04.
- **Images**: `docs/screens/world_area_map.png`, `docs/screens/world_map_moonveil_entry.png`, `docs/screens/world_area_map_stone_ruins.png` (step 3 branch).
- **Related**: R-025, R-032, R-065, R-066, R-067, node `area_map`.

## Added from builder batch 10 (2026-11-03, handoff)

### R-069 · The Voyage Obelisk travels to the next kingdom
- **Rule**: "A massive stone pillar etched with arcane symbols. Your pathway to the next kingdom." Tap the obelisk once to select it and again to open its card, then Activate to travel (Originisle to Verdantglade).
- **Confidence**: observed. **Source**: builder batch 10.
- **Images**: `docs/screens/interact_obelisk.png`.
- **Related**: R-006, R-030.

### R-070 · Goddess Statues bless a fully explored area
- **Rule**: A Goddess Statue's card requires "Reach 100% exploration in <area>" and rewards Blessing Level +1, with an Unlock button. The quest "The Goddess's Grace I/II" follows each Explore quest. It is reached through a white edge pointer with a statue icon (`resource/image/explore/pointer_statue.png`). Blessing Level 2 raised the Max Cart Level from 1 to 2 and the AFK EXP rate from 50 to 500, so blessing every area is worth it. A variant, the **Lost Goddess Statue** ("Activate this dim statue to dispel darkness... Blessed Land"), has the same 100% exploration requirement but its Unlock sits lower, at (0.5, 0.81); its rewards are home boosts (Highland Woods: Home EXP and Home Wood Yield Boost +1%; Moonveil Woods: Home EXP and Home Rolla Yield Boost +1%), then Tap to Continue. Match both with "(Lost )?Goddess Statue".
- **Confidence**: observed. **Source**: builder batches 10 and 12. Confirms R-003.
- **Images**: `docs/screens/interact_goddess_statue.png`, `docs/screens/blessing_level.png`, `docs/screens/lost_goddess_statue.png` (step 3 branch).
- **Related**: R-002, R-003, R-014, R-020, R-035.

### R-071 · Mines are mini-dungeons with first-clear rewards
- **Rule**: Mines such as "Ironvein Pit" ("A deserted mine swarming with monsters") show First Clear Rewards (Refined Ore 100, Raw Ore 640) and an Explore button lower on the card, at (0.5, 0.80). Mine battles run up to 25 rounds ("Round n/25"). The card policy treats as a mini-dungeon any card whose name ends in Ruins, Cave, Tower, Dungeon, Pit, Mine, Lair, Den or Fortress, or that shows "First Clear Rewards".
- **Confidence**: observed. **Source**: builder batch 10.
- **Images**: `docs/screens/interact_ironvein_pit.png`.
- **Related**: R-040, R-042, R-049 (Raw Ore limits gear).

### R-072 · Energy Circuits puzzle (not automated)
- **Rule**: In the Ancient Fortress, "Energy Circuits" asks you to "drag or tap to swap slabs, linking all nodes and powering the circuits": 3 slabs in a row; tap two to swap them. Swapping the end slabs solved the one seen. A reset button is top right. The bot doesn't solve these yet.
- **Confidence**: observed. **Source**: builder batch 10.
- **Images**: `docs/screens/puzzle_energy_circuits.png`.
- **Related**: node `puzzle_energy_circuits`.

### R-073 · Fight monsters that block the path
- **Rule**: Roaming monsters (spear wolves in Verdantglade, templates `resource/image/monsters/wolf_spear*.png`) can stand between the player and a pickup; fight them first (tap the monster, then battle prep).
- **Confidence**: observed. **Source**: builder batch 10.
- **Images**: none.
- **Related**: R-001, R-041.

### R-074 · Edge pointer types
- **Rule**: Off-screen targets show as pointers at the screen edge: the gold quest ring (R-022), the boss portrait (R-045), the Goddess Statue icon (R-070), a blue orb for "Unlock <area>" (`resource/image/explore/pointer_unlock.png`), and the player's own portrait when the camera has drifted away from them (R-032): a white ring with the player's face, and tapping it re-centres the camera on the player. Tap a pointer to pan the camera there.
- **Confidence**: observed. **Source**: builder batches 10 and 11.
- **Images**: `docs/screens/world_map_player_pointer.png` (player pointer).
- **Related**: R-022, R-032, R-045, R-070.

### R-075 · Home gains event and shop buttons; collect the Cart from its bubble
- **Rule**: After Originisle, home shows "Thrilling Events" and "Starter Pack" buttons at the top right. Starter Pack is a shop: never buy (R-043). The Cart's trophy loot bubble (`resource/image/home/cart_bubble.png`) on the sideways-scrolling home scene claims AFK loot directly.
- **Confidence**: observed. **Source**: builder batch 10.
- **Images**: `docs/screens/home_events.png`.
- **Related**: R-020, R-043, R-051.

### R-076 · The area map shows resources, progress and power gates
- **Rule**: The full area map (R-068) has a legend (Portal, Lost Statue, Gold Ore, Steel Ore, Sandstone) and shows each area's exploration % and any power gate (Highland Woods 9.6K, Verdantglade III 12K). Areas below the gate's power are not worth entering yet. Ore nodes cost 5 stamina each. At handoff (Lv 12, Mage, power 7.7K, Verdantglade I and II 100% and blessed) Moonveil Woods, Stone Ruins I and Damp Woods were at 0%, and the bot was blocked on "Moonveil Woods I: Unlock Moonveil Woods" (R-064, R-067; solved by R-082). A fully explored area with a red "!" on the area map (Moonveil Woods at 100%) most likely has its statue waiting to be blessed (R-070); not confirmed yet. "Sunrise Isle" shows at the bottom right of the Verdantglade area map.
- **Confidence**: observed. **Source**: builder batches 10 and 11.
- **Images**: `docs/screens/world_area_map.png`.
- **Related**: R-017, R-064, R-067, R-068, node `area_map`.

### R-077 · The Team panel is social; leave it alone
- **Rule**: The flag button at the top left of the map (0.08, 0.12) opens the Team panel: Players 1/9, Team Goal (Free Exploration), World Call / Invite / Nearby. Like friend requests (R-057), the bot doesn't touch it.
- **Confidence**: observed. **Source**: builder batch 10.
- **Images**: `docs/screens/team.png`.
- **Related**: R-057, node `team`.

### R-078 · Heal from the HUD portrait when the player's tile is crowded
- **Rule**: If the player sprite has a red bubble and other interactables share its tile, tapping the player opens a pick-one menu on the right instead of the heal menu, and tapping again just loops. To heal, either pick the entry with the character's name in that menu, or tap the character portrait in the top-left HUD, which opens the healing menu directly. The HUD portrait avoids the menu entirely, so it is the simpler path for a script. Current HP shows as the bar under the name at the top-left of the map HUD, so read it there to decide whether to heal, without opening any menu. Quick Heal works from any screen that shows the character portrait in the upper left (map, battle prep, dungeon floor cards and others): tap the portrait. There's no need to back out of a menu to heal (mae, 2026-11-04). On the map, the HUD HP bar sits at x 116-268, y 52-64 (in 720x1280 pixels).
- **Confidence**: told. **Source**: mae, 2026-11-03 and 2026-11-04.
- **Images**: none yet (want: the pick-one menu).
- **Related**: R-061, node `player_profile`.

### R-079 · Turn on Auto Challenge in Fantasia Ascent
- **Rule**: Whenever challenging Fantasia Ascent, the multi-floor tower (for example in Moonveil Woods), turn on Auto Challenge so floors run back to back. Auto Challenge unlocks after clearing floor 3; before that, climb floor by floor as in other mini-dungeons (R-040). The tower loop runs inside the exploration loop and hands back when it stops (`memory-bank/notes.md`, composable loops). The Auto Challenge checkbox only appears on the result screen, so it can't be ticked before a run's first fight: tick it after each win. A floor loss (DEFEAT screen with a Retry button) switches it off, and the bot leaves it off there, because ticking it on the defeat screen would start a retry. Tower losses are not retried, unlike the normal heal-and-retry rule (R-061): one challenge per day is enough, run as part of the daily missions, then hand back to the calling loop.
- **Flow** (builder batch 11): the quest "Into the Moon's Shadow I" asks to "Reach Fantasia Ascent - Moonveil Woods F3"; its Go opens a Confirm dialog, "Return to Home to challenge the Fantasia Ascent?", and OK (0.68, 0.57) travels home. The tower list has one card per tower showing "Current: Fn/110". Tapping a card opens its floors, F1 at the bottom, with tabs "Fantasia Ascent" and "Goals" (Goals can carry a red badge, R-063). The current floor shows its recommended power (F1: 6.5K) and Challenge at (0.85, 0.86). Then battle prep (15 rounds) and the result screen: VICTORY with "<Tower> Fn", Clear Rewards (e.g. Worn Knuckles, Refined Ore x15, Raw Ore x128) and Continue at (0.77, 0.95), which goes straight to the next floor's prep; a loss shows DEFEAT mid-screen with Retry in the same spot (don't press it). After F3 the Auto Challenge checkbox appears at (0.66, 0.90) with a tutorial ("battles keep running in the background") and Continue counts down "(3s)". At 8.1K power one run cleared F1 to F5 and lost F6. Code: `sxs/tower.py` (states `tower_list`, `tower_floors`, `tower_result`; the run date is kept in `logs/daily.json`).
- **Confidence**: told (mae); flow and loss behaviour observed (builder batch 11). **Source**: mae, 2026-11-04 (twice); builder batch 11, 2026-11-04.
- **Images**: `docs/screens/confirm_fantasia_home.png`, `docs/screens/fantasia_ascent.png`, `docs/screens/fantasia_floors.png`, `docs/screens/fantasia_victory.png`, `docs/screens/fantasia_defeat.png` (step 3 branch).
- **Related**: R-040, R-061, R-063, R-071, nodes `fantasia_ascent`, `fantasia_floors`, `fantasia_result`.

## Added from builder batch 11 (2026-11-04)

### R-081 · Map coordinates: x grows east, y shrinks south
- **Rule**: In map coordinates (as used by `sxs/goto.py`), x increases going east (screen right) and y decreases going south (screen down).
- **Confidence**: observed. **Source**: builder batch 11.
- **Images**: none.
- **Related**: R-066, R-068.

### R-082 · Counterless unlock quests: talk to the NPC, then the gate
- **Rule**: Some quests have no counter, for example "Moonveil Woods I: Unlock Moonveil Woods". It was done by talking to Molly (an NPC with a red "!", R-062) and then tapping the dungeon gate (red "!", glowing rune). The gate card is titled "Moonveil Woods" with First Clear Rewards and a free Challenge button at (0.5, 0.79). The gate fight was 20 rounds against a wolf boss and 3 wolves.
- **Confidence**: observed. **Source**: builder batch 11.
- **Images**: `docs/screens/quest_detail_unlock.png`, `docs/screens/dungeon_gate_moonveil.png` (step 3 branch).
- **Related**: R-040, R-062, R-064, R-083.

### R-083 · A gift icon on the tracker claims a finished quest
- **Rule**: When a tracked quest is done (counterless ones, and counter ones such as "Weapon Enhancement II: Main Weapon Enhancement Level 21/20"), the map tracker's olive panel shows a small gift icon at about (0.36, 0.77). Tapping it claims the quest. The gift animates, so template matches flicker; match over a few frames or with a looser threshold.
- **Confidence**: observed. **Source**: builder batches 11 and 12.
- **Images**: `docs/screens/world_map_tracker_gift.png` (step 3 branch).
- **Related**: R-022, R-082.

### R-084 · A recommended power far above yours is a wall: stop exploring there
- **Rule**: After Moonveil Woods the next main quest is "Verdant Wonders III: Explore Verdantglade III", recommended power 12K. At 8.1K every fight there ended "badly wounded", so the bot treats it as the natural wall for this stage (mae's scope cap) and stops exploring rather than retrying. Get stronger first (gear, charms, techniques, tower clears). Still lost at 10K (R-090). The tracker's next quest after Verdant Wonders III is "Path to Upgrade: Reach Lv. 20" (rewards Stellatie).
- **Confidence**: observed. **Source**: builder batch 11.
- **Images**: none.
- **Related**: R-061, R-076, R-079.

### R-085 · Stone tile floor puzzle: step on every tile to get chests
- **Rule**: Stone Ruins I has a 2x2 floor of stone tiles. Stepping on each tile lights it cyan; when all 4 are lit, two treasure chests appear. Loot seen: Dawnium 60 and 67, Abundance Leaf 30 x2, Rolla ~900 each, Explorer's Light Armor, Refined and Raw Ore. Each chest also popped a gear-swap prompt (+445 / +484 power, swap button bottom right), which closed when the reward popup was dismissed.
- **Confidence**: observed. **Source**: builder batch 11.
- **Images**: `docs/screens/world_map_tile_puzzle_chests.png`, `docs/screens/gear_swap_prompt.png` (step 3 branch).
- **Related**: R-072, node `gear_swap_prompt`.

## Added from builder batch 12 (2026-11-04)

### R-086 · Gate of Power: a hard power wall
- **Rule**: A stone pillar card "Gate of Power" (seen in Damp Woods) reads "Requires: Power reaches 15.5K (Current: 8.1K)" and has no button. It's a wall until power is high enough. Policy kind `power_gate`: dismiss the card, and the fog walk stops there.
- **Confidence**: observed. **Source**: builder batch 12.
- **Images**: `docs/screens/gate_of_power.png` (step 3 branch).
- **Related**: R-065, R-076, R-084.

### R-087 · Highland Woods: guard pack, ground pickups, paler minimap dots
- **Rule**: Highland Woods (9.6K recommended) is entered past a bracketed wolf-boss guard pack (beaten at 10K). Its pickups (orbs, a spellbook, crystals, a "Meat & Veggie Pot") lie on the ground near a cooking pot, and collecting them alone took the area to 100%. Its minimap item dots are paler than elsewhere (HSV saturation about 128, against 150+ in Verdantglade II), so the green-dot threshold of R-066 must allow for that.
- **Confidence**: observed. **Source**: builder batch 12.
- **Images**: `docs/screens/minimap/minimap_highland_items.png` (step 3 branch).
- **Related**: R-066, R-073, R-076.

### R-088 · Replace gear with better items from the profile
- **Rule**: In the profile, tap an Equip slot, then Replace on its card. The Replace Gear list shows candidates best first, with a green up arrow on upgrades. Tapping one opens a side-by-side compare (equipped on the left, new on the right) with power numbers, and Replace sits under the new item. Enhancement levels carry over to the new item (Beginner's Cap +10 to Adventurer's Leather Hat +10: 133 to 759 power; Novice Staff +15 to Seeker's Staff: 142 to 785). Two swaps took power from 8.1K to about 9K; Cart, enhancement and technique upgrades then reached 10K. Blue badges on Equip (R-080) point at these upgrades.
- **Confidence**: observed. **Source**: builder batch 12.
- **Images**: `docs/screens/replace_gear.png`, `docs/screens/gear_compare.png` (step 3 branch).
- **Related**: R-080, R-085, nodes `replace_gear`, `gear_compare`.

### R-089 · Travel from home through the quest tracker
- **Rule**: At home, tapping the tracker for a quest in another area asks "Travel to <Area> now?" with Cancel and OK; it's free. This is the way into an area whose area-map label is still in fog, where walking there via the area map fails (R-068).
- **Confidence**: observed. **Source**: builder batch 12.
- **Images**: `docs/screens/confirm_dialog.png`.
- **Related**: R-068, node `confirm_dialog`.

### R-090 · "Badly wounded" and "incapacitated" are both losses
- **Rule**: A map fight lost in Verdantglade III (recommended 12K, at 10K) ended with the "badly wounded" dialog (R-046) and the character back in Verdantglade II, not the "incapacitated" dialog (R-031). Treat either as a loss for the heal-and-retry count (R-061) and the power-wall check (R-084). In Verdantglade III a loss puts the character back at the area entrance (178, 88) or in Verdantglade II.
- **Confidence**: observed. **Source**: builder batch 12.
- **Images**: `docs/screens/wounded.png`.
- **Related**: R-031, R-046, R-061, R-084.

## Added from mae (2026-11-04, night)

### R-091 · Heal mid-run in mini-dungeons instead of leaving
- **Rule**: In mini-dungeons (Temple Ruins, mines and other floor-by-floor dungeons), the player can heal between floors, so low HP is not a reason to leave. Heal in place from the top-left portrait on the floor card or the battle prep screen, no backing out needed (R-078; Quick Heal or Recover, using healing food per R-061), then press Next Floor and carry on. After Next Floor, the battle prep screen shows an HP bar under the character model (x 314-406, y 866-876 in 720x1280 pixels, yellow-green when full): read HP there to decide whether to heal before starting (the 70% check of R-061 still applies), and that screen can also be backed out of. Mid-run healing only applies while the player is still alive and merely low (the HP bar, or a low-health "!" over the player, R-080). A defeat inside the dungeon (the fight lost, then the "badly wounded" or forced-heal dialog) resets the dungeon's progress: that run is dead, so count it as a loss (R-090) and don't try to continue it.
- **Confidence**: told. **Source**: mae, 2026-11-04 (three messages).
- **Images**: `docs/screens/dungeon_floor.png`.
- **Related**: R-040, R-061, R-071, R-078, node `dungeon_floor`.

### R-092 · Enhance gear evenly, in 5-level bands
- **Rule**: Don't pour enhancement into one piece. Raise gear in 5-level bands: bring every equipped piece to +5, then all to +10, then all to +15, and so on; a piece only goes past a band once every other piece has reached it. Within a band, a configurable priority order decides which piece reaches the threshold first. The default order is weapon, offhand (not unlocked yet), headpiece, chest, boots. Costs and limits are in R-023 (ore and Rolla). The current enhance script kept enhancing the same piece, which this rule replaces. Enhancement is now limited by ore (7/720 Raw Ore at staff +21; boots +2 to +3 was short too); Guidance quests (R-099) and Ironvein Pit (R-095) are ore sources. Confirmed live with the banded script: boots +2 to +5, chest +9 to +10, then boots to +7.
- **Confidence**: told. **Source**: mae, 2026-11-04.
- **Images**: none yet (want: the Enhance Gear screen).
- **Related**: R-020, R-023, R-088.

### R-093 · Skill pulls run only when the handler starts them
- **Rule**: This means the skill pulls (Pray x1 / x10) at the goddess Statue at home, the furniture that reads "Pray to the goddess" and opens Prayer (R-055), not the Goddess Statues on the map that bless areas (R-070). Pulling skills is needed to keep growing in strength, so the bot gets a dedicated pull script. That script runs only when the agent's handler (mae) starts it at a time they judge right. It is never part of a loop, and no loop or decision function may call it on its own. Everything else stays under the spend rules (R-043, R-055): no Dawnium, no other spend-looking buttons. Prayer is the goddess Statue on the left of the home scene, about (0.07, 0.63) on the default camera. Two banners: Standard uses Stellatie (blue crystal tickets; Pray x1 = 1, x10 = 10; pity "Prayer x60 away from a guaranteed Legendary"; "200 Prayers Bonus"), and Affection uses Affection Tokens (red; x1 = 25, x10 = 250; "Affection Tokens Earned This Week 0/1000"). Stellatie comes from the Daily Sign-in, 10 a day (R-097); the account had 20. The script pulls on the Standard banner with Stellatie only. **Pulls are only ever done in groups of ten (the Pray x10 button), never Pray x1** (mae, 2026-11-04 08:22): Pull counts are multiples of 10, and with fewer than 10 Stellatie there is no pull. `sxs.pray` enforces this (x10 only, since commit 04b95bd). The script is `python -m sxs.pray --pulls N --handler-approved`: it never presses "+" to buy tickets, cancels any purchase prompt and stops if the Dawnium counter changes. The Goals tab has "Total Standard Prayers" milestones at 10/20/30/40/50/60 with Claim buttons: the 10 milestone paid 3 Iron Hammers (R-095); later ones show a pickaxe, a helmet item and blue and purple scrolls.
- **Confidence**: told (mae); script and costs observed (dailies builder). **Source**: mae, 2026-11-04; dailies batch 1 addendum; x10-only amendment, mae 2026-11-04 08:22.
- **Images**: `docs/screens/prayer.png`, `docs/screens/prayer_result.png`, `docs/screens/prayer_tickets.png`, `docs/screens/prayer_affection.png`.
- **Related**: R-043, R-055, R-095, R-097, nodes `prayer`, `prayer_result`.

## Added from dailies batch 1 (2026-11-04)

### R-094 · The Journal tab is the home route into Fantasia Ascent
- **Rule**: The Journal (Travel Journal) is the second icon on the bottom bar (0.31, 0.97). Its cards: Fantasia Ascent (top right, tap (0.78, 0.23) for the tower list), Map Exploration, Material Realms (marked NEW), Weekly Events ("Void Rift starts in 4d"), and two Unavailable cards. This is how to reach the tower from home (R-079).
- **Confidence**: observed. **Source**: dailies batch 1.
- **Images**: `docs/screens/journal.png`.
- **Related**: R-079, R-095, nodes `travel_journal`, `fantasia_ascent`.

### R-095 · Material Realms: mining needs Iron Hammers; never buy them
- **Rule**: Material Realms lists realms; the first is Ironvein Pit (Raw and Refined Ore), three more are locked. Inside is a mining screen with a hammer button (0.5, 0.72), an "Iron Mined" counter and tabs Ironvein Pit / Rankings / Goals (Iron Mined 5/10/15/20/25 goals each pay a fruit item). Mining uses Iron Hammers (counter top right). With 0 hammers the button opens "Purchase Iron Hammer" (60 Dawnium each, daily limit 20): never buy, tap Cancel (0.32, 0.65). Free hammers come from the Prayer Goals milestones (R-093; the 10-prayer milestone paid 3). Owned hammers show on the hammer button and the top-right counter. One hammer gave about +115 Raw Ore (7 to 122), so hammers, and through them prayers, are an ore source. Mining Ironvein Pit with free hammers is a step in the daily loop.
- **Confidence**: observed. **Source**: dailies batch 1 and its addendum.
- **Images**: `docs/screens/material_realms.png`, `docs/screens/ironvein_pit.png`, `docs/screens/purchase_iron_hammer.png`.
- **Related**: R-043, R-071, nodes `material_realms`, `ironvein_pit`.

### R-096 · Thrilling Events: only Sign-in and Growth Trial are for the bot
- **Rule**: Thrilling Events (home, top right, (0.91, 0.125)) opens "Featured" with Dawnstar Prelude (10 draws a day; a gacha, never), Growth Trial (R-098), Daily Sign-in (R-097) and Link Account (account-related, never).
- **Confidence**: observed. **Source**: dailies batch 1.
- **Images**: none.
- **Related**: R-043, R-075, node `featured`.

### R-097 · Daily Sign-in: claim today's tile, never Catch Up
- **Rule**: A 30-tile calendar that refreshes at 8:00 UTC-5. Today's tile shows a green "Claim" label; tapping it gives "YOU RECEIVED" (e.g. 10 Stellatie). Missed days show "Catch Up": treat as spending, never. Days 5 and 20 give a gold card item x50, days 10 and 25 a red item, days 15 and 30 a purple crystal. A daily task (`python -m sxs.daily`).
- **Confidence**: observed. **Source**: dailies batch 1.
- **Images**: `docs/screens/daily_signin.png`, `docs/screens/daily_signin_received.png`.
- **Related**: R-024, R-043, R-096, node `daily_signin`.

### R-098 · Growth Trial: free trial quests, never the Advanced Trial
- **Rule**: A 19-day event with Day 1-7 tabs of trial quests (Reach Lv. 20, Arrive at Drasilgard, Total Resource Level 30, Enhance Gear x4 to +15) that pay trial points toward a 100-700 chest track. "Advanced Trial" (top right) is paid: never.
- **Confidence**: observed. **Source**: dailies batch 1.
- **Images**: `docs/screens/growth_trial.png`.
- **Related**: R-043, R-096, node `growth_trial`.

### R-099 · Guidance quests are an ore source
- **Rule**: The Guidance Quest list (Menu, then Quest) includes Helmet / Armor / Boots Enhancement I ("Enhance a helmet to +15", paying 80 Raw Ore and 50 Refined Ore), Cart Upgrade I (1K Rolla) and Skill Mastery. Their ore rewards feed gear enhancement (R-092), so they're worth steering toward. The Achievement tab holds weekly carry achievements (Daily Dungeon, Crucible of Hieromon, Split Mirage), refreshing Mondays 8:00 UTC-5 (R-024).
- **Confidence**: observed. **Source**: dailies batch 1.
- **Images**: none.
- **Related**: R-009, R-024, R-092, node `quests`.

## Added from dailies batch 2 (2026-11-04)

### R-100 · Home stuck on sky: restart the game
- **Rule**: After a long session the home scene can get stuck showing only sky: no swipe moves it, and neither the Cart bubble nor the goddess Statue can be found. Restarting the game fixes it. Treat "home, but no Cart bubble and no Statue" as a reason to restart rather than keep swiping.
- **Confidence**: observed. **Source**: dailies batch 2.
- **Images**: none.
- **Related**: R-020, R-075, R-093, node `home`.

## Added from mae (2026-11-04, morning)

### R-101 · Collect bed EXP daily, not every upgrade pass
- **Rule**: An icon appears over the bed in the house when AFK EXP is ready to collect: a blue orb in a yellow frame. The daily step `bed` in `sxs.daily` taps it once a day; tap the bed to collect it. EXP builds up slowly, so collecting it is a daily task (alongside the free speed-up of R-035), not a standard step of the upgrade loop. Exception: check it whenever the character is close to levelling up. Collecting it took the account from Lv 13 to Lv 20 (power 10.1K to 13.1K), which unlocked the Guild and its tutorial (R-011).
- **Confidence**: told. **Source**: mae, 2026-11-04; dailies builder's final batch.
- **Images**: `docs/screens/home_bed_xp.png` (template `resource/image/home/bed_xp_bubble.png`).
- **Related**: R-011, R-020, R-035, nodes `home_house`, `bed`, `guild`.

## Added from the guild thread (2026-11-04)

### R-102 · Joining a guild: join a random open one
- **Rule**: The Guild tutorial starts from the bottom bar's 4th icon (0.68, 0.97), then a short dialogue with Akane, then the no-guild screen with "Join Guild Go>>" (0.71, 0.38) and "Create Guild <<Go" (0.29, 0.77). The Join list has a search field at the top (a name or ID works) and Refresh; a red "50K+ Power" label on a row is a power requirement. Donations (R-016), the guild farm and the guild boss all need membership. The Join list shows mostly guilds with an instant "Join" button and some with "Apply" (needs approval). Creating a guild may cost Dawnium, so never create one (R-043). mae's decision for now: join a random open guild (an instant "Join"). Picking or leaving guilds beyond that is mae's call, like other social choices (R-057).
- **Confidence**: observed (tutorial and list); told (the choice). **Source**: guild thread and mae, 2026-11-04.
- **Images**: `docs/screens/guild_tutorial_intro.png`, `docs/screens/guild_no_guild.png`, `docs/screens/guild_join_list.png`.
- **Related**: R-011, R-016, R-043, R-057, nodes `guild_no_guild`, `guild_join_list`.

### R-103 · Donate to the guild twice a day, never more
- **Rule**: Donate to the guild up to twice per day and never more. These first two donations are an approved use of Dawnium, an exception to R-043: the Donation screen (Lobby, Donation (0.29, 0.82)) reads "Daily Donations: N/5"; the first is free, the second costs 20 Dawnium behind a confirm dialog, and the third 50, so stop after two. Each donation pays 300 Guild Tokens personally and 500 of each guild resource to the guild. Facility upgrades are for the guild leader only. The account joined guild karsa_1515 (ID 700460600036; 28/30 members, about 607K power, guild Lv 1) on 2026-11-04 (R-102). Buildings on the guild island: Lobby, Power Station (AFK gathering), Forge, Mine, Shop, Gate of Expedition and Donation.
- **Confidence**: told (the limit); observed (costs, buildings). **Source**: mae and the guild thread, 2026-11-04.
- **Images**: `docs/screens/guild_donation.png`, `docs/screens/guild_donation_confirm.png`, `docs/screens/guild_lobby.png`.
- **Related**: R-016, R-043, R-102, node `guild`.

## Added from mae (2026-11-04): upgrades and materials

### R-104 · Upgrade skills with Quick Upgrade
- **Rule**: To upgrade a skill, tap the skill, then the "Quick Upgrade" button beside the lower-right charm. It spends Battle Essence (R-039) and is capped by character level (R-037). Seen live: on the Skill page (Character > Skill) the Quick Upgrade icon sits at about (0.73, 0.47), captioned "Upgrade", and no skill needs to be selected first: one tap levels every skill it can. It spent 1.6K of 1.6K Battle Essence, the 4 charms went from Lv 1 to Lv 8 and 9, and power went from 13.1K to 13.2K. The button disappears when nothing more is affordable.
- **Confidence**: told (mae), then observed (upgrade-systems batch 1). **Source**: mae, 2026-11-04; upgrade builder.
- **Images**: `docs/screens/skill_page.png`, `docs/screens/skill_page_after_quick_upgrade.png`.
- **Related**: R-037, R-039, R-106, node `skill_loadout`.

### R-105 · Relics: enhance in bands of 1, element by element (not unlocked yet)
- **Rule**: Relics come in several elemental categories with 4 relics each. Enhance them with banding like gear (R-092) but with a step of 1, not 5: raise the 4 relics of one element together as a single band, bring every element to the same overall level, and only then go up another level. Element priority goes by the character's overall affinity for each element, highest first. Relics use Sand (R-106). Defined ahead of time; relics aren't unlocked on the account yet.
- **Confidence**: told. **Source**: mae, 2026-11-04.
- **Images**: none.
- **Related**: R-092, R-106.

### R-106 · Upgrade materials: ore, sand, battle essence, rolla
- **Rule**: Upgrade materials split into four resources: **ore** for gear and armour (R-023), **sand** for relics (R-105), **battle essence** for skills (R-039, R-104), and **rolla** as general coins (R-019). Each can be gathered on the overworld at 5 stamina per pickup (R-107). They also come from other sources, such as mining (R-095); usually each day brings a few resources that let the account gather each of the four types.
- **Confidence**: told. **Source**: mae, 2026-11-04.
- **Images**: none.
- **Related**: R-019, R-023, R-039, R-076, R-095, R-105, R-107.

### R-107 · Stamina budget: keep 70 for daily commissions, spend the rest on the priority material
- **Rule**: Stamina regenerates over time (R-033). Always keep at least 70 stamina for the daily commissions. Spend anything above that on gathering the priority material, currently **ore**; mae will switch it to sand later. Gathering route: R-108.
- **Confidence**: told. **Source**: mae, 2026-11-04.
- **Images**: none.
- **Related**: R-033, R-076, R-106, R-108.

### R-108 · Track a material through Journal > Map Exploration
- **Rule**: Open the second icon on the home bottom bar (the Journal, R-094), choose "Map Exploration", select the material to track and press Go. A tracking marker leads to the area that holds it, where the material lies scattered on the ground. Tap pickups (5 stamina each) until the budget of R-107 is reached, then stop. Seen live: Map Exploration is at (0.29, 0.47) on the Journal, then the Resource Hunt card. It shows stamina ("175/300") and the full-recovery time (about a day for 125, so roughly 1 stamina per 11 to 12 minutes). The material icons sit at y 0.24: Rolla x 0.08, ore 0.18, sand 0.29, Battle Essence 0.39. Go (0.84, 0.28) asks "Enter Verdantglade to explore?" with OK at (0.68, 0.57). Ore led to a mine in Verdantglade II around map (187, 97): grey rocks with blue crystals. The tracked rock sits in a yellow and white ring, also shown on the minimap and as an edge ring (tap it to pan there). Pickups near the character show a "lightning 5" label; one tap on a rock walks there and mines it for 5 stamina and about +178 Raw Ore. Boars with a "lightning 5" label also appear nearby; what they do isn't known yet ❓. Code: `sxs/gather.py` with `resource/policy/gather.json` (priority ["ore"], keep_stamina 70). First live run: 20 pickups in about 3 minutes, stamina 171 to 71.
- **Confidence**: told (mae), then observed (upgrade-systems batch 1). **Source**: mae, 2026-11-04; upgrade builder.
- **Images**: `docs/screens/journal.png`, `docs/screens/map_exploration.png`, `docs/screens/confirm_enter_explore.png`, `docs/screens/explore_ore_rocks.png`, `docs/screens/explore_ore_mined.png`, `docs/screens/explore_stamina_boar.png`.
- **Related**: R-094, R-106, R-107, R-109, node `travel_journal`.

### R-109 · Special nodes with a green timer circle: always tap them
- **Rule**: While gathering you may trigger "special nodes" or "special encounters", marked with a green timer circle at their upper right. They're high value and usually give a good reward, so tap them whenever they appear. Example: a "Grand Mine", which allows one material collection without spending stamina.
- **Confidence**: told. **Source**: mae, 2026-11-04.
- **Images**: none yet (want: a special node with its timer).
- **Related**: R-106, R-108.

## Added from the guild thread (2026-11-04, later)

### R-110 · Guild gathering: one slot per character
- **Rule**: The gathering facilities are the Forge (7800/h), the Power Station (5400/h) and the Mine (5400/h), with 10 slots each. Tap an empty "+" slot to open AFK Details (+600/h to the guild, AFK rewards capped at 36 h, personally 120 Guild Tokens/h plus a random item), then Start. A character holds only one slot at a time: switching asks "Currently AFK: ... Switch anyway?" and collects the old slot's rewards automatically. mae: gather at the **Forge** (gromb2 is there now). The island's bottom-right widget shows a sleeping figure when not gathering, or the character at a facility with a timer when gathering.
- **Confidence**: observed; Forge choice told by mae. **Source**: guild batch 1.
- **Images**: `docs/screens/guild_forge.png`, `docs/screens/guild_power_station.png`, `docs/screens/guild_afk_switch_confirm.png`.
- **Related**: R-103, R-113, node `guild_facility`.

### R-111 · Gate of Expedition: Conquest and Guild Clash
- **Rule**: The guild's Gate of Expedition opens Guild Events, with Conquest (the guild boss) and Guild Clash, which unlocks 8 days after 2026-11-04. Conquest is a shared boss per floor with "Daily Challenge Attempts: N/2" (OCR reads it as "Dailly Challenge Attempts:O/2", so match "Challenge Attempts" and read O as 0). A beaten floor has a reward chest (0.49, 0.57) (gave 1 Stellatie). Flow: Challenge (0.50, 0.77), battle prep Start Battle (0.50, 0.75), then a 50-round fight that can be sent to the background (R-112). The result screen shows damage dealt and participation rewards (10 Dawnium, 150 Guild Tokens), then Tap to Continue; a "Done Conquest F2" chip shows on home and on the guild island afterwards (left side, y≈0.75). Tabs: Rankings (karsa_1515 was 18th at F2, 85%) and Goals, with Serverwide goals (claim per server floor; 4 claimed) and Personal goals (total challenges 10/20/...). Code: `sxs/guild.py` (donate, afk, conquest) and the daily steps `guild_donate`, `guild_afk`, `guild_conquest`. Gotcha: the detector once read the Challenge button as a map object and wandered into Rankings; guild screens are now checked first and Rankings is a known state.
- **Confidence**: observed. **Source**: guild thread and guild batch 1.
- **Images**: `docs/screens/guild_events.png`, `docs/screens/guild_conquest.png`, `docs/screens/guild_conquest_battle.png`, `docs/screens/guild_conquest_result.png`, `docs/screens/guild_conquest_rankings.png`.
- **Related**: R-103, R-112, nodes `guild_events`, `guild_conquest`, `guild_conquest_result`.

### R-112 · Background fights: start them and move on
- **Rule**: A fight screen showing the "run in background" symbol (a square with an arrow pointing into its lower-left corner, `docs/screens/icons/background_battle.png`) keeps going without being watched. On the Conquest fight it sits at the bottom left (0.10, 0.95) (template `resource/image/state/background_fight.png`); tapping it minimises the fight. For such fights, Conquest for example, start the fight, then leave and do other things; come back later for the result. Fantasia Ascent's Auto Challenge also runs in the background (R-079).
- **Confidence**: told. **Source**: mae, 2026-11-04.
- **Images**: `docs/screens/icons/background_battle.png` (crop sent by mae).
- **Related**: R-079, R-111.

## Added from guild batch 1 (2026-11-04)

### R-113 · Guild island layout and the Lobby
- **Rule**: The guild island (state `guild`, bottom label "Guild") pans sideways, and its camera remembers the last pan. The Gate of Expedition label is often hidden behind the bottom-right AFK widget, so find the Gate from the Guild Lobby label instead: in the west view the Lobby label is at (0.44, 0.49) and the Gate is about (+0.38, +0.15) from it (274, 196 px). Buildings by label: Guild Lobby and Gate of Expedition on the west; Power Station, Forge, Warehouse and Shop on the east. The Lobby shows guild info and Activeness, with Donation (0.29, 0.82) (R-103), Guildmates and More. Its tabs are Guild, Territory (guild resources, facility levels, gathering speeds, AFK member counts) and Upgrade (leader and deputies only).
- **Confidence**: observed. **Source**: guild batch 1 and its addendum.
- **Images**: `docs/screens/guild_island.png`, `docs/screens/guild_lobby.png`, `docs/screens/guild_territory.png`, `docs/screens/guild_upgrade.png`.
- **Related**: R-103, R-110, R-111, nodes `guild`, `guild_lobby`.

### R-114 · Warehouse is leader-only; the Guild Shop is untouched for now
- **Rule**: The Warehouse is locked and only the leader or deputies can build it. The Shop (NEW badge) spends Guild Tokens; the bot buys nothing there until mae has marked items on the mapped stock table and a buy list exists (mae's shop policy, R-120).
- **Confidence**: observed. **Source**: guild batch 1.
- **Images**: `docs/screens/guild_warehouse_locked.png`.
- **Related**: R-043, R-113, R-120, node `guild`.

## Added from upgrade-systems batch 1 (2026-11-04)

### R-115 · Technique Ascension spends the technique's own shards
- **Rule**: A "!" on a technique means it can ascend. Tap it, then Enhance (0.68, 0.74), then the Ascend tab (bottom right), then Ascend (0.50, 0.85). Ice Spike used 10 of 10 shards to go from Rare to Rare 1 star; the next step, to Epic, needs 10 more. No Dawnium is involved. The Upgrade tab next to it spends Battle Essence (R-037).
- **Confidence**: observed. **Source**: upgrade-systems batch 1.
- **Images**: `docs/screens/technique_upgrade.png`, `docs/screens/technique_ascend.png`.
- **Related**: R-037, R-080, R-104, nodes `technique_card`, `technique_upgrade`.

### R-116 · Claim the free rewards on upgrade screens' Goals tabs
- **Rule**: Upgrade screens have Goals tabs with free rewards; claim them whenever they show "!". Several had been sitting unclaimed. Seen so far: Skill Goals (Level: Battle Essence used, pays Battle Essence; Quality: pays Iron Hammers and more), Enhance Gear Goals (Raw Ores Used, pays Rolla), Rank Goals (Level: character Lv 12 to 20, pays hammers, picks and more; Power), Class Goals (Total Class Level, 300 Battle Essence each).
- **Confidence**: observed. **Source**: upgrade-systems batch 1.
- **Images**: `docs/screens/skill_goals_quality.png`, `docs/screens/gear_goals.png`, `docs/screens/rank_level_goals.png`, `docs/screens/rank_power_goals.png`, `docs/screens/class_goals.png`.
- **Related**: R-063, R-080, R-093, R-095.

### R-117 · Class levels come from Class Badges; never Change Class
- **Rule**: Class, then Class Hierarchy: tapping a class card that shows "!" pops "Class Badge Received" (+2 per owned skill of that class; OK (0.50, 0.72)). That class's Upgrade tab spends 10 badges per class level, each level adding HP, ATK, DEF and SPD. Levelling another class (Warrior) also raises Total Class Level without changing class (Mage 1 to 3, Warrior 1 to 2, Total 2 to 5). "Change Class" (locked until character Lv 100, and also a button on the Warrior page) is mae's decision and is never tapped (R-054).
- **Confidence**: observed. **Source**: upgrade-systems batch 1.
- **Images**: `docs/screens/class_page.png`, `docs/screens/class_hierarchy.png`, `docs/screens/class_badge_received.png`, `docs/screens/class_info.png`, `docs/screens/class_upgrade.png`.
- **Related**: R-054, R-080, R-116, node `class_ascend`.

### R-118 · Rank Advancement raises the level cap; Bellflowers block it now
- **Rule**: Tapping the rank badge ("Apprentice I", about (0.82, 0.72)) on Character opens Rank Advancement (R-048). Apprentice I to II raises the max level from 20 to 30 and costs a grey stone item (18/5 owned), 20 Bellflowers (0 owned) and 5.5K Rolla. Bellflowers come from "Verdantglade Flower Harvest": on Character, tap the Apprentice badge, then the Bellflower icon, then Source "Verdantglade Flower Harvest" (»), then OK on "Enter Verdantglade to explore?". This adds a Bellflower tracker ("0/20") to the left panel and a ring pointing at the field in Moonveil Woods (about (0.23, 0.07) on screen): white-bell plants on green stems. Each pick adds 1 to the tracker. Other players can stand in the field (one seen: "Bellcranel"); never tap them (R-057). Picking Bellflowers costs no stamina, unlike other pickups (R-107). Gather them by tapping the flower plants themselves in the world, as with ore, sand and Rolla pickups. Tapping the tracker ring around the character or the Bellflower icon does nothing (mae, 09:02). Go to the nearest plant, taking blue-aura plants first (R-122). Following the item's source link first started the home tutorial that unlocks the Vendor Booth (R-120). mae's priority (08:58): the Bellflower hunt and Rank Advancement come before mapping the shops. gromb2 is at Lv 20/20, so Bellflowers block all further levelling. The bot advances only when the Advance button itself shows "!".
- **Confidence**: observed. **Source**: upgrade-systems batch 1.
- **Images**: `docs/screens/rank_advancement.png`, `docs/screens/item_bellflower.png`, `docs/screens/explore_bellflower_tracker.png`, `docs/screens/explore_bellflower_field.png`, `docs/screens/explore_bellflower_field_wide.png`, `docs/screens/explore_bellflower_picked.png` (upgrade-systems branch).
- **Related**: R-048, R-049, R-057, R-101, R-122, node `rank_advancement`.

### R-119 · Gear Resonance: free bonuses when all four pieces reach a band
- **Rule**: Enhance Gear, then Resonance (0.86, 0.20): each tier reads "Enhance Gear x4 to +N" (N = 5, 10, 15 ... 35 and up, with bonuses like HP +2% or ATK +2%) and shows Activate once all 4 equipped pieces reach +N. The tiers match the 5-level bands of R-092, so activate each tier as soon as a band completes. Fix note: the Enhance Gear level reader once read "+9 → +10" as 10 because OCR doesn't return text left to right; it now takes the leftmost number.
- **Confidence**: observed. **Source**: upgrade-systems batch 1.
- **Images**: `docs/screens/gear_resonance.png`.
- **Related**: R-023, R-092, node `enhance_gear`.

### R-120 · Molly's Vendor Booth: a daily-refresh shop on home
- **Rule**: Following the Bellflower item's source link (R-118) started a home tutorial with Akane and Molly that ends with "Vendor Booth (Furniture): Unlock" (Molly: "new goodies pop up every single day"), which is free, then "UNLOCKED". The booth now stands on the home scene with a "!". The booth is Molly's shop on the home scene, and its stock refreshes daily. What it sells and what it costs aren't known yet ❓. Shop policy (mae, 2026-11-04 08:17), for the Vendor Booth, the Guild Shop and every other shop: map every item (name, cost, currency, limits) into a table, mae marks which are buyable, and those become a per-shop buy list in the repo. The bot buys nothing in a shop until its buy list exists (R-043).
- **Confidence**: observed; shop policy told (mae). **Source**: upgrade-systems builder, 2026-11-04 08:18; mae 08:17.
- **Images**: `docs/screens/home_white_sheet_tutorial.png`, `docs/screens/vendor_booth_unlock.png`.
- **Related**: R-043, R-118, node `home`.

### R-121 · Mall: claim the free gift boxes, never the packs
- **Rule**: Every Mall pack costs real money (USD): Welcome Gift, Halloween Charmer, Little Devil, Pilgrimage Pass, Daily Deals, Weekly Deals, and Pathfinder Pack (USD 0.99 for stamina). The bot never taps a pack (R-043). Each pack page has a free gift box at the top left, marked "!" when it can be claimed, and mae says the bot may tap these (2026-11-04 08:49). Route: Home menu (0.92, 0.79), then Mall (0.72, 0.65), opens "Premium Picks" (state `mall`), with bottom tabs Event, Monthly Pass and Top Up (never Top Up). The box sits at the top left of each page with a red "!" just above and to its right, and one tap claims it. The boxes are Daily Gift (4 h refresh), Weekly Gift (5 d refresh), Welcome Benefit (claimable once, gave +30 Dawnium), plus boxes on Halloween Charmer and Little Devil. The bot claims each box once per refresh and taps nothing else on the page. Code: `sxs/mall.py`, daily step `mall_gifts`.
- **Confidence**: told (mae); pages observed (upgrade-systems builder, 08:48). **Source**: mae and the builder, 2026-11-04.
- **Images**: `docs/screens/mall_premium_picks.png`, `docs/screens/mall_premium_picks_2.png`, `docs/screens/mall_welcome_gift.png`, `docs/screens/mall_welcome_benefit.png`, `docs/screens/mall_halloween_charmer.png`, `docs/screens/mall_daily_deals.png`, `docs/screens/mall_weekly_deals.png` (upgrade-systems branch).
- **Related**: R-043, R-063, node `mall`.

### R-122 · Pickups with a blue aura are rarer: prefer them
- **Rule**: Overworld pickup items that have a blue aura around them are rarer and give bonus ingredients. The gather and harvest loops pick them before plain pickups whenever both are in reach.
- **Confidence**: told (mae). **Source**: mae, 2026-11-04 09:02.
- **Images**: none yet.
- **Related**: R-106, R-107, R-108, R-109, R-118.
