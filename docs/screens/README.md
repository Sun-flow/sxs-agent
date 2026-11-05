# docs/screens: reference screenshots

Full 720×1280 frames, saved as 256-colour PNGs by `python -m sxs capture NAME`. Each screen is one file, sorted
into a folder by situation. The name's prefix picks the folder (`sxs/core/screens.py` FOLDERS), so
`capture guild_shop_top` writes `guild/guild_shop_top.png`.

| Folder | Screens |
|---|---|
| `home/` | Home scene, bed, Cart, furniture, main menu, notices, Prayer, Journal |
| `character/` | Character, gear, skills, techniques, class, rank, charms, loadouts, player profile |
| `world/` | World and area maps, exploring, gathering, gates, dungeons, statues and other interactables |
| `battle/` | Battle, battle prep, defeat, wounded |
| `dailies/` | Quests, sign-in, Fantasia Ascent, Growth Trial, Material Realms |
| `guild/` | Every guild screen |
| `shops/` | Mall, Vendor Booth, purchase prompts |
| `dialogs/` | Confirm dialogs, dialogue, reward popups, tutorial highlights, rating popup |
| `system/` | Title, loading, settings, photo mode |
| `icons/` | Crops and pictures mae sent (not full frames); not run by the detector test |
| `minimap/` | Minimap crops and tile samples for the minimap classifier; `legend_*` are mae's legend screenshots and crops (R-066, R-130) |
| `unlabeled/` | **The bank:** screens nobody has named yet, with a table for mae to fill in (`unlabeled/README.md`) |

`expected.json` holds what the state detector must report on each screen (`states`) and mae's notes on labelled
screens (`notes`). `tests/check_states_offline.py` runs the detector over every folder except `icons/`, `minimap/`
and `unlabeled/`.

## Labelling unfamiliar screens

1. The loops save every screen they don't recognise to `captures/unknown/` (gitignored, on the PC that ran them).
2. `python -m sxs bank` copies the new ones into `unlabeled/`, adds a row for each, and leaves the row empty.
3. mae fills in the row: a name, the state, and what it is. Commit it, or tell an agent what to write.
4. `python -m sxs label` moves each filled row's screen into its folder and records its state and notes in
   `expected.json`. Then run `python tests/check_states_offline.py NAME` to see whether the detector agrees.
