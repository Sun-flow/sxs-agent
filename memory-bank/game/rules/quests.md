# Quest rules

Read when using the quest tracker: what comes next, tracking a target, progressing a quest, or claiming one.

## Following the quest chain

### R-007 · Follow the quest guide to finish the tutorial
Do each quest the quest guide shows, in order.
*told* · node `quests` · R-044

### R-044 · The main chain, side quests and claiming from the tracker
- **Chain**: Wild Isle Trek I-IV (Explore Originisle I-IV; each can roll over to the next with no claim screen), "Fight the Guardian Colossi!", "Crossroads of Classes" (class choice is mae's, R-054), Trek V. "The Goddess's Grace" follows each Explore quest (R-070). Later: "Moonveil Woods I: Unlock Moonveil Woods" (R-082), "Into the Moon's Shadow I" (tower, R-079), "Verdant Wonders III" (12K wall, R-084), "Path to Upgrade: Reach Lv. 20" (pays Stellatie).
- **Side quests** also show on the tracker ("Well Armed: Equip Gear x4").
- **Claim** a finished quest (a/b with a = b, or a counterless one done) with the gift icon at the tracker's right end, not the text. Templates `resource/image/explore/tracker_gift.png` (home and map) and the smaller `resource/image/explore/tracker_gift_map.png` (map's olive panel, about (0.36-0.42, 0.77)). It moves with title length and animates: match by template over a few frames or with a looser threshold. A claimable gift carries a "!" badge about +21 px right and -69 px above the gift centre; the badge pulses red to dull orange. Dark and olive panels use the same gift. Exploration loops claim it whenever gift and "!" both show (mae): `sxs/actions/rewards.py` (template `resource/image/explore/reward_gift.png`, called from Fog Walk and Roam).
- **Unfinished**: tapping the title opens its detail card (Details, Goal, Rewards, Go or Track); the ">" arrow offers travel to its island (R-089).
- On home, scene labels can pollute the tracker's OCR (R-059).
*observed, told* · `dailies/quest_detail_go.png`, `world/world_map_tracker_gift.png`, `icons/reward_gift_box_mae.png` · node `quest_detail` · R-022, R-059, R-089

### R-099 · Guidance quests are an ore source
Menu > Quest > Guidance: Helmet / Armor / Boots Enhancement I ("Enhance a helmet to +15": 80 Raw Ore, 50 Refined Ore), Cart Upgrade I (1K Rolla), Skill Mastery. Steer toward them; the ore feeds gear (R-092). The Achievement tab's weekly achievements (Daily Dungeon, Crucible of Hieromon, Split Mirage) refresh Mondays 8:00 UTC-5 (R-024).
*observed* · node `quests` · R-024, R-092

## Tracking a target

### R-022 · Track a quest: a gold ring marks its next target
The target icon on the tracker (about (0.40, 0.79); yellow on, grey off) toggles tracking. Its x and the panel height change with the title length (icon at about 287 px for "Wild Isle Trek III", 352 px for "Fight the Guardian Colossi!"): find it by template (`resource/image/explore/tracking_on.png`, `resource/image/explore/tracking_off.png`). While on, a gold ring (`resource/image/explore/marker.png` lit, `resource/image/explore/marker_dim.png` shadowed) marks the next target, or sits at the screen edge pointing to it: tap it to pan, then tap the target. The ring floats about 100 px (0.08 of screen height) above the target: tap below it.
- Hidden under the top-left avatar or level badge: drag the map.
- Covering the area name and coordinates under the minimap (breaks `world_map` detection): nudge the camera.
- Next to the player: a tap can open the character panel instead; aim off the sprite or move first (R-080).
*told, observed* · nodes `quests`, `world_map` · R-044, R-074, R-080

## Progressing a quest

### R-021 · The Explore counter rises with fog, pickups, fights and objects
"Explore Originisle I n/100" gains from walking into fog, pickups (gold piles, plants, chests), beating roaming monsters and using map objects (R-030). At 100/100 claim from the tracker gift (R-044). It's separate from the area map's % (R-076).
*observed* · `world/world_map_explore.png`, `world/world_map_quest_complete.png` · node `world_map` · R-002, R-044

### R-041 · Beat a target's bracketed guards before it responds
Some targets (the Pink Bird on Originisle III) are ringed by monsters with gold corner brackets (`resource/image/explore/guard_bracket.png`; the monster is about (-35, +50) px from the corner). The target only repeats a line ("Chirp! Chirp!") until all of them are beaten. Dialogue reply options are white pills with a black arrow.
*observed* · `dialogs/dialogue_choice.png` · R-022, R-062

### R-082 · Counterless unlock quests: talk to the NPC, then the gate
E.g. "Moonveil Woods I: Unlock Moonveil Woods": talk to the red "!" NPC (Molly, R-062), then tap the dungeon gate (red "!", glowing rune). Its card, titled with the area name, has First Clear Rewards and a free Challenge at (0.5, 0.79) (20 rounds: wolf boss and 3 wolves). Then claim from the tracker gift (R-044).
*observed* · `dailies/quest_detail_unlock.png`, `world/dungeon_gate_moonveil.png` · R-044, R-062, R-064
