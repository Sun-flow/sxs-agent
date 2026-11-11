# Labeler mislabels: diagnosis and the single-category review (2026-11-11)

<!-- index: Where the map mislabels came from (red text as monsters, zoom knob as Rolla), counts, and the single-category review: `prelabel --one`, category filter, review grid, rejected drafts -->

mae (2026-11-11 06:15): the map zoom control was drafted as Rolla and many red words on the map were drafted as
monsters. Where did those come from, and how do we make checking drafts fast? This note answers with counts, then
says what changed. Numbers come from PR #55 (`labels/check-drafts` at adf35ea) and from the labeler's own copy on
mae's PC (the `sxs-labels` worktree, `docs/screens/labels.json` saved 2026-11-11 04:22, not pushed yet).

## Where labeling stands

| | PR #55 | mae's PC copy (04:22) |
|---|---|---|
| Boxes | 611 confirmed + 191 drafts | 766 confirmed, 0 drafts |
| Screens with boxes | 127 | 127 |

mae's PC copy already holds her pass over all 191 drafts: 157 kept, 34 removed (20 `map_monster`, 12
`map_building`, 1 `mm_icon`, 1 `mm_monster`), plus the 2 zoom-knob "Rolla" boxes removed. PR #55 is behind it until
that file is committed.

Coverage of the PC copy (the coverage counter from PR #57, run on it; minimum for a first training is 50 boxes on 20
screens per class):

- 672 boxes the export would use, 94 more on private screens; 105 screens have a box; 223 of 328 public frames have
  none.
- 18 of 44 classes have no box at all (all 8 cards, `btn_close_x`, `btn_quick_heal`, `btn_price`, `monster`,
  `npc_alert`, `tracker_box`, `map_chest`, two anchors).
- Only `item_icon` (352 boxes on 85 screens) is past "good"; `badge_red_bang` (64 on 25) is at the minimum.
- Every map and minimap class is short: `map_monster` 19 boxes on 4 screens, `map_building` 15 on 3, `map_item` 11
  on 3, `map_zone_label` 39 on 7, `mm_icon` 10 on 4, `mm_item` 9 on 3, `mm_monster` 7 on 3, `mm_building` 1 on 1.
- The repo has only 7 area-map frames and 16 island-map frames in total, so map classes cannot reach 20 screens
  without new captures (see `docs/collectibles-capture-plan.md`).

## Where the mislabels came from

### 1. Red words drafted as monsters: the pre-labeller's own copy of the area-map reader

`sxs/detect/prelabel.py` `area_map_objects()` drafted every blob of the area map's colour masks
(`sxs/vision/area_map.py` `_masks`). The monster mask is hue 0-22, so it takes red as well as orange: the red CP
line and "Exploration: 0%" under a zone above our power, the red "!" on a structure, and orange bits of gold icons.
The bot's own reader, `area_map.objects()`, filters those out (zoom slider, text rows of 4+ blobs within 60 px, the
red "!" badges, monsters touching a building, round and compact blobs only). The pre-labeller had re-implemented it
with only part of that: a text-row test of 3 neighbours within 30 px, which misses spread-out letters, and none of
the other filters. The same gap let letters of yellow town names ("Drasilgard") through as `map_building`.

Counts on PR #55's drafts: 39 `map_monster` drafts, of which 24 are blobs the bot's own reader rejects (letters, %
signs, the sword icon, a red "!", building bits); mae removed 20. 27 `map_building` drafts, 15 of them rejected by
the reader (letters of "Drasilgard"); mae removed 12.

### 2. The zoom control drafted as Rolla: the item matcher ran over the whole map

`prelabel --items` (`sxs/detect/items.py` `find()`) template-matches every catalogued item crop, at 21 sizes, over
the whole frame, colour, threshold 0.86. On the area map, the zoom slider's knob (a white disc with a grey
four-point star, at 669,942) matches Rolla's 28 px top-bar coin at 0.89. It was drafted on 2 screens
(`world/area_map_blue_bang.png`, `world/area_map_legend_overlap.png`) in 269fa66, confirmed in the 2026-11-10 evening
pass (aee0169), and removed in mae's 04:22 pass. No other item box sits on a map area.

### 3. Why they got through, and came back

- **Confirm all drafts** confirmed every draft on a screen, across classes, in one click. An area map carried up to
  30 drafts of 7 classes, so a few wrong ones in the pile went through with the right ones.
- **Removals were not remembered.** Deleting a draft only dropped it from labels.json; the next `prelabel` run (and
  `--redraft`) drafted it again. mae removed 44 of 61 monster drafts on 2026-11-10, and the 18:58 re-draft brought
  most of that kind back.
- **Mixed classes on one screen.** Checking 30 boxes of 7 classes on one frame is slow and error-prone; checking one
  class across all frames side by side is fast, and odd ones stand out.

### Still in mae's confirmed boxes (worth one look in the review grid)

Boxes the bot's reader rejects, still confirmed in the 04:22 copy: `map_monster` on 2 pieces of gold structures, 1
gold winged structure and 1 red "!" badge (these look wrong); 3 grey discs with red rims and 1 small brown mark
(unclear what they are). `map_building` on 2 letters of "Drasgard" (wrong) and 2 yellow four-point sparkles
(unclear: an interactable, or a pickup?).

## What changed (this PR)

1. **The drafter follows the bot.** `area_map_objects()` now drafts a blob only where `area_map.objects()` reports an
   object of that kind; a building is the union of its pieces. Measured on mae's 7 reviewed area maps: the old
   drafter produced 32 boxes she removed; the new one produces 4 she has not got (3 stacked yellow bars on
   `area_map_v3`, 1 yellow bar), and re-finds 38 of the 50 boxes she kept. The 12 it no longer finds are the
   unclear or wrong ones listed above. On PR #55's data, `map_monster` drafts go from 39 to 14.
2. **No item symbols on maps.** `item_drafts()` drops hits on the area map's map, slider and legend and on the
   minimap (`no_item_regions()`).
3. **Removals are remembered.** A draft removed in the labeler (on a screen or in the grid) is written to
   `docs/screens/rejected.json`; `prelabel` never drafts the same class (and item) there again. Moving a box to
   another class remembers the old class as wrong there.
4. **Single-category drafting:** `python -m sxs prelabel --one map_monster` drafts just that class, only on the
   screens where it can be (area-map classes on area maps, minimap classes on island maps), and prints the review
   link. Add `--redraft map_monster` to re-check already confirmed boxes of the class too.
5. **Category filter in the labeler.** A Category menu (a class, a class group like `area_map`, an item, or an item
   group) keeps only screens with that category in the list (with a count) and shows only those boxes on the
   screen. "Confirm all drafts" now confirms only the shown category.
6. **Review grid.** Every box of the category from every screen as a zoomed crop with its context. `Y` keep, `N`
   reject, `U` undo, arrows to move, "move selected to class…" to relabel, `Enter` opens the screen, Apply saves.
   http://127.0.0.1:8765/#review=map_monster opens straight into it.

## How to run a pass (mae's PC, labeler worktree)

```
git pull                                  # this PR's code, once merged
python -m sxs prelabel --one map_monster --redraft map_monster
python -m sxs labeler                     # then http://127.0.0.1:8765/#review=map_monster
```

Suggested order: `map_monster`, `map_building`, `map_item`, `map_statue_bang`, then `mm_monster`, `mm_item`,
`mm_icon`, `mm_building`. Each is one grid of 5-40 tiles. The grid has "drafts only" ticked; untick it to see
confirmed boxes of the class as well.

## Open questions for mae

1. The grey discs with a red rim and the yellow four-point sparkles on the area map: what are they? If they are a
   kind of their own (ore? a sparkle pickup?), they may need a class (append only).
2. Commit the 04:22 labels from the PC so PR #55 matches it (the owning thread can do it on `labels/check-drafts`).
