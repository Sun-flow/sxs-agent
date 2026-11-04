# Step 1: emulator choice and game survey

_2026-11-02. Living copy: https://claude.ai/artifact/9GFhA9oaZMDx4G57ypLgAD_

## Decisions

- **Game:** Sword x Staff, BOLTRAY GAMES, package `com.zjcs.android.us`. All combat is auto-battle (R-001), so the bot navigates menus and makes decisions; it never fights by hand.
- **Emulator: MuMu Player 12 on Windows.** Fastest screenshot path any bot framework supports (nemu IPC, ~10 ms vs ~100 ms for `adb screencap`), `mumu-cli.exe` by `--vmindex`, ADB on by default with a port per instance. Settings: 1280×720, 240 dpi, fixed frame rate, one instance per account. (The game still renders portrait 720×1280: see step 2.)
- **Toolkit: MaaFramework.** JSON pipelines for fixed flows, Python for custom logic, template matching and OCR built in. MaaMCP lets a model drive the device and save what it did as a pipeline. Fallback if it proves too opinionated: `adbutils` + OpenCV + RapidOCR, same layering.

| Emulator | Verdict | Why |
|---|---|---|
| MuMu Player 12 | **Use** | IPC capture supported by MaaFramework; widely used by MAA/mower users; official `mumu-control` agent skill |
| BlueStacks 5 | Fallback | No fast capture path; Hyper-V edition changes ports (read `bluestacks.conf`) |
| LDPlayer 9 | Avoid | MAA dropped it: port changes, black/flipped screenshots, freezes |
| Nox / MEmu | Skip | Lightly tested, old Android |
| Android Studio AVD | Skip | ARM-only games run poorly on x86 images |
| WSA | Skip | Discontinued, white screenshots |

Later, for unattended running: Redroid (Android in Docker, one container per account, best on an ARM host); Waydroid is fussier.

## Architecture

1. **Hands and eyes (no model):** MaaFramework over ADB, MuMu IPC screenshots, template match + OCR (PaddleOCR ONNX).
2. **Scripts (no model):** one pipeline/loop per task; a state detector answers "where am I".
3. **Supervisor (model only on failure):** on an unknown screen or timeout, a model gets the screenshot and recent log, recovers, and writes the fix back as a pipeline node or policy rule, so the same case costs no tokens next time.
4. **Entertainment agent (later):** reads the same event log.

## Game facts

Released 2026-05-13, Android/iOS only. Idle RPG, open world, Warrior/Mage, AFK income from the Cart. Regions, server cap and merges: R-006. Unlock levels, and seasons partly resetting them: R-011.

Not yet known (needs the APK, pulled from the emulator with `adb shell pm path com.zjcs.android.us` then `adb pull` of base and split APKs; the cloud session can't download it): engine (`libil2cpp.so`/`libunity.so` = Unity, `libcocos*.so` = Cocos), whether UI text is in readable data files, network protocol (vision-first until then), anti-tamper or emulator detection.

## Daily content catalogue

From the community wiki and Prydwen (third party, not all verified in-game). Unlock levels are account levels.

| Task | Where | Notes | Difficulty |
|---|---|---|---|
| AFK / Cart rewards | Home | Cart caps | Easy |
| Wandering animals | Home | Random respawns | Medium |
| Free stamina, Daily Shop | Shop | Refresh costs Rolla; Vault needs Dawnium | Easy |
| Vendor Booth (Lv 18) | Vendor | Needs buy rules (`docs/shop-tables.md`) | Easy |
| Daily Quests / Commissions | Quests | Claim chests | Medium |
| Material Dungeons | Dungeons | 2 free attempts each (R-015); extras cost Dawnium | Easy |
| Daily Dungeons (Mythic gear) | Dungeons | Aim for A rank+ | Easy |
| Spend stamina on nodes | Map | Budget: R-107 | Medium |
| Goddess / Witch / Hero statues | Map | R-070 | Medium |
| Stone Tablet quiz | Map | Lore answers | Model or cached answers |
| Guild donation, Farm, Boss, island AFK | Guild | R-103 | Easy |
| Co-op Dungeons, 6-player Raids | Dungeons / Raids | Matchmaking | Medium |
| Solo Arena / 3v3 | PvP | Auto | Easy–medium |
| Guild War | Guild | Scheduled | Later |
| Gem synthesis 3:1 | Gems | | Easy |
| Mail, event check-ins, codes | Mail / Events | Events change | Easy; model fallback |

Iteration 1 scope: AFK collect, free stamina, daily shop, daily quests, material + daily dungeons, guild donation/farm/boss, arena, mail. Deferred: map exploration, statues, quiz, co-op, Guild War.

Open: is co-op content in scope?

## Host setup (maes2024)

CPU virtualization on in BIOS; MuMu Player 12, one 1280×720 instance; Play Store sign-in, install the game, finish the tutorial; Python 3.12 and Android platform-tools (`adb`).

## Sources

- Play listing: https://play.google.com/store/apps/details?id=com.zjcs.android.us
- Wiki daily routine: https://sword-x-staff-wiki.pages.dev/daily-routine
- Prydwen: https://www.prydwen.gg/sword-x-staff/guides/beginner-guide, https://prydwen.gg/sword-x-staff/guides/tips-and-tricks
- skich.app overview: https://skich.app/games/sword-x-staff
- MAA emulator support: https://github.onedrive11.workers.dev/john180/MaaAssistantArknights/blob/master/docs/en-us/1.3-EMULATOR_SUPPORTS.md
- arknights-mower device control: https://deepwiki.com/ArkMowers/arknights-mower/5.2-device-control-and-input
- MuMu control skill: https://www.skills.sh/site/skills.mumu.163.com/mumu-control
- MaaFramework: https://maafw.com/en/docs/1.1-QuickStarted
- MaaMCP: https://www.sourcepulse.org/projects/21493524
