# UI detector: Roboflow design

mae, 2026-11-10: "let's start designing a roboflow implementation ... recommend me the three best choices with pro
and con lists for each." Background and the case for a detector: `docs/vision-upgrade.md` (Part 2). This note is
the plan. Nothing here is built yet; the screen-check speed-ups (Part 1) are.

## What the detector is for

One pass over a frame that returns boxes with a class and a score, wherever the element sits. It finds things; it
does not read text and it does not replace the State chain.

First classes (about 30; grow from there):

| Group | Classes |
|---|---|
| Cards (one class per card type) | `card_chest`, `card_statue_visit`, `card_goddess_statue`, `card_sealed_gate`, `card_boulder`, `card_wheel`, `card_dungeon_gate`, `card_interact` (any other one-button card) |
| Buttons | `btn_primary` (the yellow action button), `btn_close_x`, `btn_back_arrow`, `btn_tap_to_spin`, `btn_claim`, `btn_quick_heal` (top-left portrait) |
| Badges | `badge_red_bang`, `badge_blue_pip`, `badge_gold_ring` (quest pointer), `badge_blue_bang` (statue on the area map), `badge_gift` |
| Area map | `map_player`, `map_chest`, `map_statue`, `map_wheel`, `map_gate`, `map_zone_label` (box only; OCR reads it), `map_pct_line` |
| World view | `player_character` (so we never tap ourselves), `monster`, `npc_alert`, `tracker_box` |

Not detector classes: minimap tiles and dots (4-8 px; `sxs/vision/minimap.py` stays), numbers and quest text (OCR),
whole screens (the State chain, now one text read per check).

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
      |  export-dataset command (new) YOLO-format zip; masks the account-name strip; train/valid/test split
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

1. **Class list in the labeler.** Add the class names above as the labeler's box kinds, so boxes carry a class, not
   free text. Boxes already drawn keep working as templates.
2. **Pre-labelling.** A script runs the detectors we already have on each banked frame and writes draft boxes for
   mae to correct rather than draw:
   - `area_map.objects` for map objects
   - `badges` for red "!" and blue pips
   - the tutorial highlight
   - OCR line boxes for zone labels
   - templates for buttons
3. **Exporter.** a new `export-dataset` command writes a YOLO-format zip (images plus one `.txt` per image).
   - It **blacks out the account-name and chat strips** before export (PII out of anything uploaded).
   - It splits about 80/10/10 by screen, never by box.
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
