# 2026-11-03 · OCR-first state detection, one node at a time

- **Decision**: Detect screens with MaaFramework OCR on fixed UI text (nav labels, titles, buttons), using templates only where there is no text. Run the `State.*` nodes one by one on a single screenshot (custom action `DetectState`) instead of through a `next` list. Commit reference screenshots as 256-colour PNGs in `docs/screens/` and check the detector against them offline.
- **Rationale**: OCR on UI text holds up better than image templates when art or colours change, and the game's English UI is clean. MaaFramework's batched OCR for `next` lists misread several screens. 256-colour PNGs are ~200 KB instead of ~550 KB and give the same detector results.
- **Alternatives considered**: a plain `next` list (fast but wrong); `only_rec` OCR (40% faster, but broke five screens); plain adb + OpenCV (not needed, since MaaFramework works).
- **Status**: Accepted
