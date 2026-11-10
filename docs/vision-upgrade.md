# Vision upgrade: faster screen checks, and whether to train a detector

mae, 2026-11-10: "I am curious about training a roboflow image detection model on many of the UI elements in the game,
so that we could have much faster state detection and tagging ... How are we determining what screen we are on
currently, each time we do a state check? I would like to start with optimizing our interface for even faster,
cheaper processing."

This note answers in two parts: how a screen check works today and where its time goes (with measurements), then
what a trained detector (YOLO / Roboflow) would add. It ends with a staged plan. Nothing here has been built yet.

**Short answer.** A screen check today is a chain of up to 52 OCR runs, one after another, on the same screenshot.
Almost all of the time is OCR, and most of it is spent on screens we already could have ruled out. Changing how we
use the OCR we already have (read a few shared strips once, try the last screen first, skip unchanged frames, use
templates where a picture settles it) should cut a typical check from seconds to a few hundred milliseconds with no
model training. A trained detector is worth doing after that, for the things OCR and colour masks are bad at
(finding buttons and icons wherever they sit, card types, our own marker, label boxes on the big map), not as the
first speed fix.

---

## Part 1. How a screen check works today

### What runs, in order

`StateDetector.detect()` (`sxs/core/state.py`) does this every time a loop asks "where am I":

1. **Foreground check.** `device.foreground_package()` runs `adb shell dumpsys window` as a subprocess and greps the
   focused window. If the game is not in front, the state is `not_running`.
2. **Screenshot.** One frame from MuMu over MaaFramework's IPC path (~7-10 ms, `docs/step2-hands-and-eyes.md`).
3. **The state chain.** MaaFramework runs the `State.Detect` node, whose custom action walks the 57 nodes in
   `resource/pipeline/state.json` in priority order (popups first, then screens) and **stops at the first hit**.
   Of those 57 nodes, **52 are OCR** (PP-OCRv4 detection + English recognition, ONNX, in `resource/model/ocr/`),
   3 are template matches (`dialogue`, `dialogue_choice`, `background_fight`), 1 is an OCR pair (`loading`), and
   the last is `unknown`, which always hits.
4. **Interrupt table.** The runner's `InterruptingDetector` (`sxs/core/interrupts.py`) checks the result against
   the interrupt rows. Rows such as the tutorial highlight run an extra image test on the same frame. When a row
   fires, the handler runs and the screen is detected again.

Each OCR node crops its `roi`, runs the text *detector* model to find text lines inside it, runs the *recogniser*
on each line, and matches the text against the node's `expected` regex. Nothing is cached between nodes, so 14
nodes that all read the title bar at `y 20-90` run OCR on that same strip 14 times.

Outside the detector, loops call more OCR through `det.read_text(roi)` (`sxs/vision/ocr.py`): HUD power and stamina,
tracker quest lines, card buttons, and the big-map survey (`roam.read_areas`, a 720x1100 OCR per pan, 9 pans per
survey). The minimap (`sxs/vision/minimap.py`) and area-map objects (`sxs/vision/area_map.py`) are HSV colour masks,
not OCR. The labeler's crops (`sxs/vision/labels.py`) are template matches, but no boxes have been drawn yet.

### Where the time goes (measured)

Measured 2026-11-10 in the cloud container (4 vCPU Linux, CPU only, same `maafw==5.15.0` and models as mae's PC),
over the reference screens in `docs/screens/`, one per expected state. mae's desktop CPU is likely faster, so treat
the absolute numbers as an upper bound; the *shape* (what is expensive, what is cheap) carries over. Before trusting
any number for mae's PC, rerun on it (step 0 below).

| What | Cost here |
|---|---|
| One small OCR node (title bar, tab label) | 50-110 ms |
| One large-ROI OCR node: `MainMenu` (720x320) / `TapToContinue` (420x380) / `ClassPage` (720x700) | 560 / 390 / 330 ms |
| Same small node with recognition only (`only_rec`, no text-detection model) | ~31 ms |
| Template match in a small ROI (the 3 template nodes) | 3-11 ms |
| Whole state chain on a screen nothing matches (`unknown`) | ~5.3-5.5 s |
| Full check on the **world map** (34th in the order, the screen exploring sits on most) | ~2.8 s |
| Full check on **home** / **battle** / **character** | ~2.3 / 2.3 / 2.8 s |
| Full check on pages near the end (quests, sign-in, notice, growth trial) | 6.7-7.7 s |
| Full check on popups near the top (loading, title, chat, choose reward, area map) | 0.2-0.7 s |
| `read_text` over the whole frame / the big-map survey ROI | 750 / 560 ms |
| Minimap tile read (`minimap.read`) / area-map objects | 25 / 25 ms |
| A tiny frame fingerprint (9x8 grey thumbnail) | 0.5 ms |
| `adb shell dumpsys window` (foreground check) | not measurable here (no emulator); typically 100-300 ms on Windows |

Two things stand out:

- **Cost grows with position in the order.** Every screen pays for every OCR node above it. The world map pays for
  33 failed OCR runs before its own, including `TapToContinue` (390 ms) and the loading pair (200 ms).
- **A few big ROIs cost as much as a dozen small ones.** `MainMenu`, `TapToContinue`, `ClassPage`, `Loading` and
  `TowerResult` together are ~1.6 s of the 5.5 s chain.

Also: `wait_for` polls every 0.5 s, but a world-map check takes ~2.8 s here, so polling is bound by the check, and
the bot reacts to a screen change seconds late. The big-map survey is slower for a different reason: 9 pans with
fixed sleeps (1.2 s settle + 0.9 s drag each, plus zoom taps with 0.5-0.6 s sleeps) are ~20 s of waiting, against
~5 s of OCR.

All 53 sampled screens were detected correctly, so accuracy of the chain is fine on known screens; the problem is
cost, plus OCR misreads on free text (big-map labels such as "Monpiitht", joined labels) that the chain does not
cover.

### Cheap wins, no ML (ranked by payoff for effort)

| # | Change | Payoff | Effort | Risk |
|---|---|---|---|---|
| 1 | **Read shared strips once.** Replace the 14 title-bar nodes with one OCR of `[0, 20, 720, 70]` and the 3-5 bottom-tab nodes with one OCR of `[0, 1230, 720, 50]`, then match every state's regex against those lines in Python. Measured: one title-bar read is 110-300 ms against ~900 ms for the 14 nodes; one tab-bar read is 100-160 ms against ~300 ms. | Large: removes ~1 s from every check below the title-bar group | Small: a custom recognition in `state.py`, states keep their regexes in `state.json` | Low; `check_states_offline.py` covers it |
| 2 | **Try the likely screen first.** Check the previous state's node (and the state the caller is waiting for in `wait_for`) before the full chain, with the popups that can cover it. A loop that sits on the world map then pays ~100 ms, not 2.8 s. Popups keep priority by checking the 8-10 overlay nodes first only when the frame changed (see 3). | Large in practice: most checks repeat the last state | Small | Medium: the overlay list must stay complete; a missed popup is caught on the next full check |
| 3 | **Skip unchanged frames.** Keep a 0.5 ms fingerprint (small grey thumbnail, ignoring animated regions such as the minimap and the character) of the last frame; if the new frame matches within a threshold and less than ~2 s passed, return the last detection. Also usable as a "screen settled" test to replace fixed sleeps (survey pans, zoom taps, card waits). | Large for polling and for the survey's ~20 s of sleeps | Small | Low with a time cap |
| 4 | **Picture anchors before OCR.** For the frequent screens, a template or a few anchor pixels settle the state in 1-10 ms: the minimap ring (world map), the tab bar icons (home/character/world), the round counter frame (battle), the legend box (area map). OCR only confirms when the anchor is unsure. The labeler (`python -m sxs labeler`) is the tool for cutting these crops; one session on ~15 screens covers the common ones. | Large | Medium: needs crops from mae's screens | Low: false matches show up in the offline check |
| 5 | **Shrink or reorder the big ROIs.** `MainMenu` (720x320), `TapToContinue` (420x380), `ClassPage` (720x700), `TowerResult`, `Loading`: tighten each to where its text really sits, or move it after cheaper nodes when it is not an overlay. | ~1.6 s off the worst case | Small | Low |
| 6 | **`only_rec` for fixed labels.** Where the text always sits in the same box (tab labels, "Tap to Play", page titles) skip the text-detection model: measured ~31 ms against ~64 ms. Needs a tight ROI around the text. | Medium | Small | Medium: a shifted label misreads; test per node |
| 7 | **Foreground check less often.** Run `dumpsys window` only when the chain says `unknown`, or at most every ~10 s, not on every check. | 100-300 ms a check (estimate) | Tiny | Low |
| 8 | **Try GPU inference for OCR.** MaaFramework can run the OCR models on DirectML (`Resource.use_directml()`) on Windows; the detector never chooses today, so it gets the library default. Measure CPU against DirectML on mae's PC. | Unknown; possibly 2-5x on OCR | Tiny to test | Low; keep CPU as fallback |
| 9 | **Big map: reuse labels once per run** (already planned) and cut the survey's sleeps with #3. | ~15-20 s a survey | Medium | Low |

Together, 1-5 and 7 should bring a typical check (world map, home, battle) to roughly 50-300 ms and the unknown
worst case to under ~1 s on this container's CPU, without changing what any state means. That is the "faster,
cheaper interface" step and needs no training.

### Proposal to approve (Part 1)

One PR, offline-tested, then one live readout run by the RC builder:

0. **Measure first on mae's PC.** Add a new bench command (proposed: `bench` loop) that times `detect()` on every reference screen and per
   node, and prints the table above for her machine (CPU and DirectML). Offline only; no emulator needed.
1. Shared-strip reads (#1) and tightened big ROIs (#5).
2. Last-state-first with the overlay guard (#2), plus the unchanged-frame skip (#3) with a 2 s cap.
3. Foreground check on unknown or every 10 s (#7).
4. `Detection` gains `path` ("cache", "fast", "full") so the readouts show which route answered and how long it took.
5. Pass condition: `tests/check_states_offline.py` still 100%, and median check time on mae's PC at least 5x lower
   than step 0's number. Then the builder runs one short roam with readouts.

Anchor crops (#4) follow once mae labels the common screens in the labeler, and the survey sleep cuts (#3, #9) go
with the picker label reuse already queued.

---

## Part 2. Training a UI detector (YOLO / Roboflow)

### What a detector would and would not fix

A detector looks at the whole frame once and returns boxes with a class ("claim_button", "chest_card",
"player_marker", "zone_label") in one pass, wherever the element is. That is a different job from the state chain:

| Problem | Does a detector help? |
|---|---|
| Slow screen checks | Partly. A screen *classifier* on a thumbnail (~5-20 ms on CPU) could replace the whole chain, but Part 1 gets most of the speed without training. |
| Finding buttons and icons that move (card buttons, red "!", blue pips, gold rings, chests, statues on the big map) | **Yes, the best use.** Today each has its own colour mask or template with hand-tuned thresholds per zone. |
| Card recognition (which card is up: chest, statue, gate, boulder, wheel) | Yes: card types are visually distinct; a class per card type, OCR only for the button text the rules need. |
| Taps on our own character / our own map dot | Yes: a `player_marker` class removes the `MIN_PX` distance hack in `area_map.py`. |
| Big-map label misreads ("Monpiitht", "…CoastHidden Camp" joined labels) | Indirectly: the detector finds each label's *box*, then OCR reads one clean crop at a time (recognition only), so labels stop merging. The text itself is still OCR. |
| Reading numbers and text: exploration %, CP, stamina, quest lines, card wording | **No.** Still OCR. |
| Minimap tiles and tiny dots (4-8 px) | No. Frames are shrunk to ~640 px for the model, dots become 2-3 px; the HSV minimap code is cheaper and already works (25 ms). |
| Unknown screens | No. A detector only knows classes it was trained on; unknown stays a state the chain reports. |

### Model choices (as of 2026-11)

| Family | Licence | CPU speed (nano) | Notes |
|---|---|---|---|
| **Ultralytics YOLO26** (Jan 2026) / YOLO11 / YOLOv8 | AGPL-3.0 (or paid Enterprise) | YOLO26n ~39 ms ONNX CPU at 640 px (Ultralytics' Xeon figure), 2.4 M params; NMS-free head optional | Easiest tooling: `pip install ultralytics`, `yolo train`, `yolo export format=onnx`. MaaFramework's `NeuralNetworkDetect` node runs YOLOv8/11-style ONNX models directly in a pipeline. |
| **RF-DETR** (Roboflow) | Apache 2.0 for Nano-Large | Fast on GPU (2.3 ms Nano on T4); CPU slower than YOLO nano, not published | Strong accuracy on small datasets; ONNX export. Training wants a CUDA GPU (6-8 GB). |
| **RT-DETR** / D-FINE / DEIM | Apache 2.0 (original repos) | Heavier than YOLO nano on CPU | Good accuracy, no NMS; tooling rougher. RT-DETR inside Ultralytics is AGPL. |
| **YOLO-NAS** | Code Apache 2.0, pretrained weights under Deci's own licence | Similar to YOLOv8 | Weight licence restricts use; no reason to pick it here. |
| **YOLOX-Nano** | Apache 2.0 | Fast on CPU | Older, still fine for flat UI; less tooling. |

**Licence.** The repo has no licence file today. AGPL obligations apply when the software is distributed or offered
as a network service; running Ultralytics on mae's own PC for a personal bot is fine. If the repo is ever published
under a permissive licence, or shared, an Apache model (RF-DETR Nano/Small, YOLOX) avoids the question. Recommendation:
prototype with YOLO26n because the tooling is fastest; keep the inference side engine-agnostic (plain ONNX through
MaaFramework or onnxruntime) so the model can be swapped for an Apache one later without touching loops.

**CPU inference on mae's PC.** No GPU assumed. A nano detector at 640 px is ~30-60 ms a frame on a desktop CPU via
ONNX Runtime, while MuMu shares the same CPU. That is fine for "once per decision", not for every poll; the fast
screen check from Part 1 stays the poll, and the detector runs when a loop needs to *find* something. DirectML on
Windows could make it a few ms if the PC has any GPU.

### Roboflow hosted vs local training

| | Roboflow (hosted) | Local Ultralytics / RF-DETR |
|---|---|---|
| Labelling | Good web annotator, label assist from a first model, dataset versions, augmentations | Our labeler (needs a box export), or Label Studio / CVAT locally |
| Training | Cloud GPU, billed in credits (free tier: 10 credits/month, projects private by default) | Free; Colab or Kaggle GPU for an hour, or mae's PC CPU (slow: hours for a nano model) |
| Output | Weights downloadable; export to ONNX | ONNX directly |
| Lock-in | Some (dataset lives there; hosted inference is the default path) | None |

Recommendation: label in our own labeler (it already stores boxes per screen in `docs/screens/labels.json`) plus a
small exporter to YOLO format; use Roboflow only if mae wants its annotator and label assist, and never its hosted
inference (every frame would be a network call and a cost). Train on Colab/Kaggle GPU or Roboflow, export ONNX,
commit nothing heavy: models are fetched like the OCR models.

### How much data

Game UI is the easy case for detection: the same sprites, same scale, no lighting or pose changes. Rough guide for
30-80 classes:

- **20-50 labelled instances per class** gets a usable first model on flat UI; 100+ for classes that vary (cards
  with different art, zone labels over different terrain).
- That is **~300-600 screenshots** in total, since one screen holds many boxes. The loops already save unknown
  frames, and `docs/screens/` holds 241 references.
- **Labelling time** ~30-60 s a screen once the classes are fixed: 4-8 hours for 500 screens. Pre-labelling cuts
  that in half: our existing detectors (templates, colour masks, OCR boxes) can draw the first boxes and mae only
  fixes them.
- Plan for a **second round**: run the model on live captures, bank the frames it was unsure on, label those.

### How it would plug in

- **As pipeline nodes.** MaaFramework already has `NeuralNetworkDetect` (model path, class ids, thresholds, ROI). A
  state node can be `NeuralNetworkDetect` on `card_chest` just like an OCR node today, so the State chain, nav graph
  and interrupt table keep working unchanged.
- **As a vision helper.** A new vision helper module (proposed name `ui`) with `find(frame, cls)` returning boxes; loops call it where they call
  colour masks or `labels.find` today. One model run per frame, cached on the frame, shared by every caller.
- **State from detections.** Later, a state can be "these classes are present" (e.g. `world_map` = minimap ring +
  joystick), which is cheap once the model ran for another reason.
- Readouts log the class and score of every detection used for a tap, so a wrong tap is traceable.

### Usefulness estimate (honest)

- For **speed**, Part 1 gives most of the gain: roughly a 10x cut in typical check time (more on screens late in the order) without training. A detector adds little
  speed on top for the state chain.
- For **robustness**, a detector is a real upgrade on the parts that break most: finding cards and buttons, map
  icons (chests, statues, wheels, gates), our own marker, label boxes for clean OCR. These are the stuck points in the
  run logs. Expect fewer per-zone threshold fixes and fewer "tapped the wrong thing" loops.
- It does not remove OCR: %, CP, stamina, quest text and card wording stay OCR (recognition-only on detected boxes,
  which is cheaper and cleaner).
- Cost: one labelling push (a day of mae's time spread out), an hour of GPU, and a model to keep current when the
  game's UI changes (a re-label round per big game update).

### Staged path

1. **Fast interface (Part 1).** Bench on mae's PC, shared strips, last-state-first, frame skip, foreground check,
   big ROIs. No ML. *This is the proposal to approve now.*
2. **Anchors from the labeler.** mae boxes the common screens' anchors and buttons in `python -m sxs labeler`; the
   detector uses them as templates. This is also the start of the training set.
3. **Box exporter + pre-labelling.** Export labeler boxes to YOLO format; pre-label banked frames with existing
   detectors. Pick ~30 classes for the first model: card types, card buttons, red "!", blue pip, gold ring, chest,
   statue, wheel, gate, player marker, zone label box, tracker box, HUD portrait, back arrow.
4. **First model.** YOLO26n (or RF-DETR Nano if the licence matters), trained on a free GPU, ONNX, run offline
   against the reference screens next to the current detectors; adopt class by class only where it beats them.
5. **Wire in** through `NeuralNetworkDetect` nodes and a new vision helper module (proposed name `ui`); live run with readouts; then grow the
   class list from the frames it was unsure on.

### Sources

- Ultralytics YOLO26 docs (release, CPU ONNX figures, AGPL-3.0): https://docs.ultralytics.com/models/yolo26/
- RF-DETR docs (Apache 2.0 for Nano-Large, latency, ONNX export, training GPU): https://rfdetr.roboflow.com/latest/
- Roboflow plans (free tier credits, private projects, weight download): https://docs.roboflow.com/billing/plans
- YOLO-NAS licensing: https://roboflow.com/model-licenses/yolo-nas
- MaaFramework 5.15 Python API (`NeuralNetworkDetect`, `Resource.use_directml`): the installed `maa` package
  (`maa/pipeline.py`, `maa/resource.py`).
