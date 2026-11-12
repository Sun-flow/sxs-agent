# 2026-11-02 · MuMu Player 12 on Windows at 1280×720

- **Decision**: Run the game on MuMu Player 12 on maes2024, one instance per account, 1280×720 at 240 dpi.
- **Rationale**: fastest screenshot path (~10 ms IPC vs ~100 ms `adb screencap`), a CLI for instance control, per-instance ADB ports, wide use in bot communities. 1280×720 is what most bot assets assume.
- **Alternatives considered**: BlueStacks 5 (fallback; slower screenshots, little CLI); LDPlayer 9 (dropped by MAA for unstable screenshots); Android Studio AVD (ARM games run poorly on x86); Redroid on Linux (best for headless later, not worth it for iteration 1).
- **Status**: Accepted
