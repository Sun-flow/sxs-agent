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
| `items/` | Item symbol survey: screens the catalogue's icons were cropped from and each item's info card (`items/README.md`) |
| `icons/` | Crops and pictures mae sent (not full frames); not run by the detector test |
| `minimap/` | Minimap crops and tile samples for the minimap classifier; `legend_*` are mae's legend screenshots and crops (R-066, R-130) |
| `unlabeled/` | **The bank:** screens nobody has named yet, with a table for mae to fill in (`unlabeled/README.md`) |

`labels.json` holds the boxes mae drew on screens in the labeler (see below); `rejected.json` the drafts she removed,
so the pre-labeller never drafts them again.

`expected.json` holds what the state detector must report on each screen (`states`) and mae's notes on labelled
screens (`notes`). `tests/check_states_offline.py` runs the detector over every folder except `icons/`, `items/` (item popup captures), `minimap/`
and `unlabeled/`.

## Labelling unfamiliar screens

1. The loops save every screen they don't recognise to `captures/unknown/` (gitignored, on the PC that ran them).
2. `python -m sxs bank` copies the new ones into `unlabeled/`, adds a row for each, and leaves the row empty.
3. mae fills in the row: a name, the state, and what it is. Commit it, or tell an agent what to write.
4. `python -m sxs label` moves each filled row's screen into its folder and records its state and notes in
   `expected.json`. Then run `python tests/check_states_offline.py NAME` to see whether the detector agrees.

## The labeler (mae, 2026-11-09)

`python -m sxs labeler` opens a page at http://127.0.0.1:8765 (stdlib server plus Pillow, local only). It lists
every screen, the bank first. On a screen:

- **Drag to draw a box** around anything that matters, name it (`claim_button`), and pick what it is: button,
  text (a line to read with OCR), icon, badge or region. Add a note on how to handle it if useful.
- **Fill in the screen**: name, folder, state, what it is (the same fields as the bank table).
- **Detector class** (menu under each box) says which UI-detector class the box is (`resource/detect/classes.json`); only boxes with a class go into the training set (`python -m sxs dataset`). Dashed boxes are drafts from `python -m sxs prelabel`: fix them and press **Confirm** (or `C`; moving or resizing also confirms), **Confirm all drafts**, or delete them. Tick "only screens with draft boxes to check" to work through them.
- **Save** writes the boxes to `docs/screens/labels.json`, cuts a crop of each box ticked "save crop as template"
  into `resource/image/labels/<screen>/<box>.png` with a row in its `manifest.json`, and writes the screen's row in
  `unlabeled/README.md` (bank) or its state and notes in `expected.json` (filed screens).
- **File labelled screens** runs `python -m sxs label`; boxes and crops follow the screen to its new name.
- **Category** menu and **Review grid** (mae, 2026-11-11): show one label category at a time (a class, a class group,
  an item or an item group); the grid shows every box of it from every screen as zoomed crops to keep (`Y`), reject
  (`N`) or move to another class, then Apply. `python -m sxs prelabel --one CLASS` drafts one class for it
  (`docs/labeler-diagnosis.md`).

The bot uses them through `sxs/vision/labels.py` (`find(frame, "cart", "upgrade_button")`, `python -m sxs see
labels FRAME`), and a pipeline node can use the crop as `template: "labels/<screen>/<box>.png"`. Boxes are in the
screen file's pixels: 720x1280 frame coordinates for reference frames.
