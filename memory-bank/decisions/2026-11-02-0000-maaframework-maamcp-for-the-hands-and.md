# 2026-11-02 · MaaFramework + MaaMCP for the hands-and-eyes layer

- **Decision**: Build device control, recognition and flows on MaaFramework JSON pipelines with Python custom logic; use MaaMCP for Claude to drive the device and save pipelines.
- **Rationale**: open source and proven in game bots; built-in template matching and OCR; supports MuMu's fast screenshot path; MaaMCP fits the "agent writes its own scripts" pattern.
- **Alternatives considered**: plain Python (`adbutils` + OpenCV + RapidOCR), kept as the fallback if MaaFramework proves too opinionated.
- **Status**: Accepted
