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
| `companions_invite_tutorial.png` | | | | Companions list before Auroradrasil; tutorial glow on Akane's Invite (filled glow, not an outline); back arrow locked |
| `auroradrasil_tutorial_highlight.png` | | | | Island map, tutorial highlight framing the Auroradrasil tree |
