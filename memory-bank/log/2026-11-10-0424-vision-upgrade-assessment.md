# 2026-11-10 04:24 · Vision upgrade assessment (Claude Code, cloud)

- mae asked how screen checks work and whether a Roboflow/YOLO UI detector would help. New `docs/vision-upgrade.md`. Measured offline (cloud CPU, reference screens): a check is up to 52 OCR nodes in sequence, ~60-110 ms each and 330-560 ms for the big ROIs (MainMenu, TapToContinue, ClassPage); world map ~2.8 s, unknown ~5.5 s, late pages ~7 s; template nodes 3-11 ms; all 53 sampled screens correct. 14 nodes OCR the same title strip.
- Proposal for mae to approve: a bench command on her PC, shared title/tab strip reads, last-state-first with an overlay guard, unchanged-frame skip, foreground check only on unknown, tighter big ROIs, try DirectML. Detector (YOLO26n or Apache RF-DETR Nano via MaaFramework `NeuralNetworkDetect`) is stage 3-5: for finding cards, buttons, map icons, our marker, label boxes; not for %/CP text or minimap dots.
- Open: mae's approval of Part 1; numbers on her PC.
