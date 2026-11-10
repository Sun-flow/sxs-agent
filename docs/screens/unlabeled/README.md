# Unlabelled screens

Screens nobody has named yet. The loops save every screen they don't recognise to `captures/unknown/`, and
`python -m sxs bank` copies those frames here, one row each.

To label a screen, fill in its row:

- **Name**: a file name in lower case, such as `guild_shop_top`. The prefix picks the folder, so `guild_` goes
  in `guild/`. Leave it empty to keep the current name.
- **Folder**: optional. Use it to override the folder that the prefix picks.
- **State**: what the detector must report on this screen, such as `guild_panel`. Write `unknown` if no state fits
  yet, or `-` to keep the screen without a detector check.
- **What it is**: anything worth knowing. It is saved with the screen.

Then run `python -m sxs label`. Each row that has a State moves into its folder and is added to
`docs/screens/expected.json`.

| File | Name | Folder | State | What it is |
|---|---|---|---|---|
| `settings_graphics.png` | | | | |
| `battle_prep_group.png` | | | | |
| `home_wounded_tutorial.png` | | | | |
| `guild_power_station_info.png` | | | | |
| `settings_game.png` | | | | |
| `guild_afk_details.png` | | | | |
| `photo_mode.png` | | | | |
| `settings_other.png` | | | | |
| `area_map_resource.png` | | | | |
| `auroradrasil_entry.png` | | | | Auroradrasil dungeon card: Team 4/4, Enter Dungeon (no cost), Rating Bracket D-S, drop level 18-30 |
| `team_panel_companions.png` | | | | Team panel after inviting the NPC companions (Players 4/4, Allow Teammate Invites) |
| `auroradrasil_result.png` | | | | Auroradrasil result: rank B, team chests, Drops, Claim Rewards |
| `auroradrasil_claimed.png` | | | | Same after Claim Rewards: Beastclaw Boots, Beasthide Armor, Raw Ore |
| `drasilgard_portal_teleport.png` | | | | Drasilgard portal card: already activated, button Teleport |
| `area_map_verdantglade_zoomed_out.png` | | | | Verdantglade area map zoomed all the way out: every zone with power and Exploration % |
| `drasilgard_carol_dialogue.png` | | | | Carol the Black Cat (shapeshifting witch), first-meeting dialogue |
| `drasilgard_carol_gift.png` | | | | Carol's free Shapeshifting Mirror (reward popup) |
| `drasilgard_carol_menu.png` | | | | Carol menu: Transform! / Chat / Let me think about it |
| `drasilgard_carol_reshape.png` | | | | Reshape screen (appearance: General, Hair, Face, Trait); Complete costs 1 Shapeshifting Mirror; not pressed |
| `lost_goddess_statue_auroradrasil.png` | | | | Lost Goddess Statue card (Auroradrasil 100%): Unlock, rewards Home EXP/Stone Yield +1% |
| `lost_goddess_statue_blessed.png` | | | | After Unlock: Divine Power Awakens, Tap to Continue |
| `area_map_statue_badge_auroradrasil.png` | | | | Area map: small statue icon with red "!" in Auroradrasil (find_badges misses this size); gold ore "!" in Verdantglade V |
| `exploration_kit_pack.png` | | | | Paid pack popup "Exploration Kit" ($0.99, Value 700%), opened by the Timed Packs HUD button; never buy, close by a tap below the card (360, 1120) |
