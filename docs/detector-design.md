# UI detector: Roboflow design

mae, 2026-11-10: "let's start designing a roboflow implementation ... recommend me the three best choices with pro
and con lists for each." Background and the case for a detector: `docs/vision-upgrade.md` (Part 2). This note is
the plan. Built so far: the screen-check speed-ups (Part 1, PR #48), and step 1 below (class list in the labeler,
pre-labeller, dataset exporter).

## What the detector is for

One pass over a frame that returns boxes with a class and a score, wherever the element sits. The class list is
`resource/detect/classes.json` (42 classes, 2026-11-10; ids follow its order, so new classes are appended):

| Group | Classes | For |
|---|---|---|
| cards | `card_chest`, `card_statue_visit`, `card_goddess_statue`, `card_sealed_gate`, `card_boulder`, `card_wheel`, `card_dungeon_gate`, `card_interact` | Which card is up, before the card rules |
| buttons | `btn_primary`, `btn_close_x`, `btn_back_arrow`, `btn_tap_to_spin`, `btn_claim`, `btn_quick_heal`, `btn_price` (spend buttons, never tapped; mae 2026-11-10) | Where to tap |
| badges | `badge_red_bang`, `badge_blue_pip`, `badge_gold_ring`, `badge_gift` | What needs attention |
| area_map | `map_player`, `map_item`, `map_monster`, `map_building`, `map_statue_bang`, `map_chest`, `map_zone_label`, `map_pct_line` | Big-map targets; label boxes for clean OCR |
| world | `player_character`, `monster`, `npc_alert`, `tracker_box` | Never tap ourselves; fights; NPCs |
| minimap | `mm_item`, `mm_monster`, `mm_building`, `mm_icon` | Minimap objects (mae, 2026-11-10), see below |
| screen | `anchor_minimap_ring`, `anchor_tab_bar`, `anchor_hud_portrait`, `anchor_battle_round`, `anchor_dialogue_box`, `anchor_popup_panel`, `anchor_page_title`, `anchor_area_map_legend` | Model-first screen checks, see below |

Still not detector work: numbers and quest text (OCR), and the minimap's terrain tiles. Explored, fog and walls are
per tile, not objects, and `sxs/vision/minimap.py` reads them in ~25 ms.

### Minimap objects (mae, 2026-11-10)

The minimap dots are 2-10 px on the 720x1280 frame (measured on the pre-labelled screens). A detector that shrinks
the frame to ~640 px sees them at 1-5 px, below its finest 8 px grid. So the dataset carries them two ways, and
training decides:

- **Enlarged minimap crop.** The 172x172 crop around the minimap at 3x (516x516). This is no extra screenshot: it is
  cut from the frame we already have. At runtime it is one extra model pass on a small image (estimated 10-15 ms on
  CPU), run only when a loop needs the minimap (fog walk steps), not on every screen check.
- **Full frame.** The same boxes on the full frame. This works only if the model runs at full resolution (about 3-4x
  the cost a pass).

`python -m sxs dataset --minimap both|crop|full` picks which (default both).

### Item symbols (mae, 2026-11-10)

Items, materials and currencies (Rolla, Dawnium, Stamina, Raw Ore, Stellatie, Gold Pickaxe, ...) each have fixed art,
and tapping one opens a popup with its name and description. mae wants the model to name them, so they get a
catalogue, `resource/items/` (`python -m sxs items`, `sxs/detect/items.py`):

- `items.json`: one entry per item (id, name, kind, the popup's description word for word, our `uses` note,
  `named_by` popup | screen | mae | guess) and one entry per sighting (icon crop, reference screen, box, menu path in
  `found_in`). Unnamed symbols are `unknown_N` with a blank name until someone reads the popup or mae names them.
  Append only: catalogue order sets the class ids below.
- Look-alikes (mae): in Material Realms some symbols look like resource icons but are usage symbols, e.g. a round
  glowing badge with crossed hammer and sword and a counter (`docs/screens/icons/material_realm_usage_badge_mae.png`).
  They get kind `usage` and their own id, so they are their own class, never a sighting of the resource.
- Detector class `item_icon` (group items). A labeler box of that class carries `item`, the catalogue id (the
  labeler shows a "which item?" menu).
- Auto-labelling: `python -m sxs prelabel --items` finds every catalogued symbol on the reference screens by
  template matching at sizes from 22 to 132 px (the same art is ~30 px in the top bar and ~100 px on shop cards),
  coarse on a half-size frame and checked at full size, and drafts an `item_icon` box with its id. About 10 s a
  screen with 15 items; it grows with the catalogue.
- Export: `python -m sxs dataset --items each` (default) makes each item its own class `item_<id>`, after the fixed
  classes; `--items one` keeps them all as `item_icon`, and the bot would then name a found symbol by matching the
  catalogue crops (cheap: one small crop, a few templates). Which one trains better is left to the first run.
- Standing rule (mae): any material or currency symbol a thread sees that is not in the catalogue gets identified
  (tap it, read the popup) and added with `python -m sxs items add`. Not all of them matter to the bot; all of
  them help the model.

### Working with the screen check (hybrid, mae 2026-11-10)

mae: "why don't they work together?" They should. The model is faster: one ~40-60 ms pass against a ~1 s text read
(1.0-1.3 s median on her PC after #48). The text check keeps four things the model can't give:

- wording safety: a card counts only if its button says an allowed verb, so a "Purchase" card stays unknown;
- one-line additions for new screens, where the model needs 20+ examples and a retrain;
- unknown screens staying unknown, where a model tends to name the closest class it knows;
- reading numbers.

The plan for `StateDetector.detect()` once a model exists:

1. Run the model on the frame (cached by the frame fingerprint). When a screen's anchor classes are present with
   high confidence (for example `anchor_minimap_ring` + `anchor_hud_portrait` and no `anchor_popup_panel` = world map),
   that is the state, `path` "model".
2. When the model is unsure, or the screen is a spend-risk one (cards, shops, prayer, confirm dialogs), the text
   check decides as today.
3. Unknown stays the text check's call.
4. A screen moves to model-first only after the offline check shows model and text agree on every reference screen
   of that state.

## The three best choices

All three train on Roboflow from the same dataset version, so we can train two and compare them on our own
screens before choosing.

### 1. YOLO26 Nano (Ultralytics, Jan 2026), recommended to start

Pros
- Fastest on CPU of the three: Ultralytics quotes ~39 ms ONNX CPU at 640 px for the nano model (2.4 M parameters).
  This matters because MuMu shares the same CPU.
- A plain CNN: easy ONNX export, runs with onnxruntime on any Windows PC, with DirectML on a GPU if there is one.
- Roboflow trains it hosted, and its weights can be downloaded as ONNX or `.pt` on the free tier.
- Huge user base and tooling: if Roboflow ever becomes inconvenient, `pip install ultralytics` trains the same
  model locally from the same dataset export.
- An NMS-free head is optional, so the post-processing is simple.

Cons
- AGPL-3.0. That is fine for a personal bot on mae's own PC. Publishing or selling the bot would mean releasing its
  code under AGPL, or paying for a licence. On Roboflow's free tier the included commercial licence covers Roboflow
  Cloud only, not self-hosting.
- Less accurate than RF-DETR on small, varied datasets. This matters most for card art and zone labels over
  terrain.
- Small objects suffer at 640 px input. We would train at 640x1152 (the frame's shape), which costs about 2x the
  quoted time.

### 2. RF-DETR Nano / Small (Roboflow), the Apache alternative

Pros
- Apache 2.0 for Nano to Large: no licence question if the bot is ever shared or published.
- The strongest fine-tuning accuracy per labelled image. It uses a DINOv2 backbone, and Roboflow reports
  convergence in few epochs. That suits a first dataset of a few hundred screens.
- No NMS (transformer set prediction): one box per object, so duplicate taps on one button don't happen.
- Roboflow's own model, so its hosted training gets first-class support. Weights download as ONNX, and the open
  `rfdetr` package trains locally too (with a CUDA GPU of 6-8 GB).

Cons
- Slower on CPU. It is built for GPUs: 2.3 ms on a T4, but Roboflow publishes no CPU figures, and its own write-up
  recommends YOLO for CPU-only machines. Expect several times YOLO26n's CPU time. Measure it on mae's PC before
  choosing.
- Local training needs an NVIDIA GPU. Without one, training means Roboflow credits or Colab.
- A heavier ONNX graph than YOLO, and newer tooling with fewer users.

### 3. Roboflow 3.0 Object Detection (or the newer YOLOLite), the managed option

Pros
- The simplest Roboflow path: one click in Train, tuned defaults, label assist and auto-label inside the Roboflow
  annotator.
- Fast on CPU (YOLOv8-derived). YOLOLite is Roboflow's 2026 edge family with standard and edge variants, n to xl.
- Roboflow 3.0 weights download as ONNX, and its YOLOv8-style output is the format MaaFramework's
  `NeuralNetworkDetect` node already reads, so a pipeline node could use it with no Python glue.

Cons
- Roboflow licence: it is AGPL-derived, and self-hosted use outside Roboflow needs the Enterprise add-on for
  commercial use. The model's terms are tied to keeping the plan.
- Lock-in: the architecture and training recipe are Roboflow's, so it can't be retrained locally without them.
  YOLOLite's docs don't yet list weight download or licence terms, and it is beta.
- Few public benchmarks to judge it by beyond Roboflow's own.

### Recommendation

**Agreed by mae (2026-11-10):** train options 1 and 2 on the same dataset and keep the winner.

Train **YOLO26n and RF-DETR Nano on the same Roboflow dataset version**. Run both offline on the reference screens
with a new `see detect` view, and keep the one that wins on our screens at a CPU cost we accept (target
≤ 80 ms a frame on mae's PC). Pick RF-DETR if the bot might ever be shared publicly and its CPU time is acceptable;
otherwise YOLO26n. Skip Roboflow 3.0 unless mae wants the fully managed path more than portability.

## Pipeline

```
captures/ + docs/screens/         frames the loops saved, reference screens
      |  python -m sxs labeler    mae draws boxes (classes from a fixed list), plus pre-labels to fix
      v
docs/screens/labels.json          boxes per screen (already stored here)
      |  python -m sxs dataset --zip   YOLO format; account name and chat blacked out; train/valid/test split
      v
Roboflow project (private)        upload via the roboflow Python SDK (API key in an env var, never committed)
      |  Train: YOLO26n, RF-DETR Nano   free-tier credits first; augmentations off except brightness/blur
      v
ONNX weights                      downloaded with a fetch script (new) into resource/model/detect/ (gitignored)
      |  vision detect module (new)   onnxruntime, letterbox 720x1280, decode both output formats, cache per frame
      v
loops / pipeline nodes            detect.find(frame, "card_chest"); later NeuralNetworkDetect nodes in resource/pipeline/
```

Steps in order:

1. **Class list in the labeler.** *Built.* Each box has a "detector class" menu (from `resource/detect/classes.json`),
   stored as `cls` on the box in `docs/screens/labels.json`. Boxes already drawn keep working as templates.
2. **Pre-labelling.** *Built.* `python -m sxs prelabel [--ocr]` (`sxs/detect/prelabel.py`) runs the detectors we
   already have on every reference screen with an expected state, and writes **draft** boxes. The labeler shows
   drafts dashed: fix one and press Confirm (or `C`), move or resize it (which confirms it), or delete it. Re-running
   replaces only drafts and never touches a confirmed box. Sources:
   - area-map masks for map objects, and blue "!" statues
   - the minimap colour rules for minimap objects
   - badges for red "!" and blue pips
   - the gift template, the gold quest ring, the character sprite
   - fixed screen anchors per state
   - with `--ocr`, area-map label and % line boxes, and Claim / Tap to spin buttons by text
   First run (2026-11-10, no OCR): 365 drafts on 76 screens.
3. **Exporter.** *Built.* `python -m sxs dataset [--zip] [--drafts] [--minimap both|crop|full]`
   (`sxs/detect/dataset.py`) writes YOLO format: images and labels per split, plus `data.yaml`. Only boxes with a
   class go in, and only confirmed boxes unless `--drafts`.
   - Every frame has the HUD name strip blacked out.
   - With `SXS_ACCOUNT_NAME` set (environment only), every OCR line reading as the name, and every chat line, is
     blacked out too.
   - Chat, guild, friends, profile and ranking screens are left out unless `--include-private`.
   - The split is about 80/10/10 by screen, never by box. Checked by `tests/check_detect_data.py`.
4. **Roboflow.** One private project and one dataset version per export. Keep augmentation light (brightness, small
   blur, JPEG noise), because the UI never rotates or flips.
5. **Train both models** on the same version. Record mAP, per-class recall and CPU time in this file.
6. **Runtime module.** A new `detect` vision module loads the ONNX with onnxruntime (CPU, or DirectML via
   `SXS_INFERENCE`) and runs once per frame, cached by the frame fingerprint the State detector already computes.
   It returns `(cls, score, box)` and logs every detection used for a tap.
7. **Offline check.** A new offline detector check compares detections against the labelled boxes of held-out
   screens (recall per class, false positives per screen). A class is adopted only when it beats the colour mask or
   template it would replace.
8. **Adoption, class by class.** These are the first targets, because they are the current stuck points:
   - card type before the card rules (`resource/policy/cards.json`)
   - `player_character`, which replaces the `MIN_PX` hack in `area_map.py`
   - `map_zone_label` boxes, followed by recognition-only OCR on each box (ends merged labels such as
     "…CoastHidden Camp")
   - chest, statue and wheel icons on the area map
9. **Live run** by the RC builder with readouts, then a second labelling round on the frames the model was unsure
   on (score 0.3-0.6), banked automatically.

## Data budget

- First model: ~300 screens (the 241 references plus banked frames), 20-50 boxes per class.
- With pre-labels, about 3-4 hours of mae's time; without, 4-8.
- Second round: ~200 screens chosen by the model's own uncertainty.
- Re-label after a game update that restyles the UI.

## What it costs to run

- Inference: one model run per decision, not per poll. The poll stays the State chain plus the frame cache.
- Training: Roboflow free tier (10 credits a month) for the first models. Colab or local Ultralytics if credits
  run out.
- Repo: no weights committed, the same as the OCR models. Fetched by script; the Roboflow API key is read from an
  environment variable.

## Open questions for mae

- Will the bot ever be shared publicly? If yes, prefer RF-DETR (Apache).
- Does her PC have a GPU DirectML can use? `python -m sxs bench --inference directml` answers it for OCR, and the
  same applies to the detector.
- Is she happy to box screens in the labeler with a fixed class list, or does she prefer Roboflow's annotator (with
  label assist) for this part?

## Sources

- Roboflow supported models, hosted training, weight download and licences: https://docs.roboflow.com/models/supported-models
- Downloading Roboflow weights (formats, plans, licence unchanged by download): https://docs.roboflow.com/models/model-weights/download-roboflow-model-weights
- Roboflow licensing (Roboflow 3.0 and AGPL models; self-hosted commercial use needs Enterprise): https://roboflow.com/licensing
- YOLO26 in Roboflow (Jan 2026): https://docs.roboflow.com/reference/changelog/changelog/january-2026/yolo26-model-support.md
- YOLOLite: https://docs.roboflow.com/models/supported-models/yololite
- YOLO26 numbers and licence: https://docs.ultralytics.com/models/yolo26/
- RF-DETR licence, sizes, latency, training hardware: https://rfdetr.roboflow.com/latest/
- RF-DETR against alternatives (CPU caveat): https://roboflow.com/blog/rf-detr-vs-alternatives
