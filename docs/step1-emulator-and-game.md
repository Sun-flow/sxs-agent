# Step 1: emulator choice and game survey

_2026-11-02. Living copy: https://claude.ai/artifact/9GFhA9oaZMDx4G57ypLgAD_

## TL;DR

- **Game:** **Sword x Staff** by BOLTRAY GAMES (`com.zjcs.android.us`), confirmed by mae.
- **Emulator:** use **MuMu Player 12 on Windows**. It has the fastest screenshot path any bot framework supports (~10 ms via its IPC vs ~100 ms for plain `adb screencap`), a CLI for starting and stopping instances, and per-instance ADB ports. NetEase also publishes an official AI-agent control skill for it. BlueStacks 5 is the fallback.
- **Toolkit:** build the "hands and eyes" layer on **MaaFramework** (open source, used by MAA and many other game bots): JSON pipelines for deterministic flows, Python for custom logic, built-in template matching and OCR. Its companion **MaaMCP** lets Claude drive the device and save what it did as a reusable pipeline, which is the "agent writes its own scripts" pattern.
- **Good news for automation:** all combat in this game is auto-battle, PvE and PvP. The bot is a menu navigator and decision-maker, not a fighter.
- **Blocked:** the APK could not be downloaded from the cloud session (network policy refuses APKPure and APKMirror). Engine and network notes wait until the APK is pulled from the emulator on maes2024.

## 1. Emulator comparison

| Emulator | ADB access | Fast screenshots | Instance control | Bot-community standing | Verdict |
|---|---|---|---|---|---|
| **MuMu Player 12** (NetEase) | On by default, per-instance port | **Yes**: "nemu IPC" DLL capture, ~10 ms, supported by MaaFramework and arknights-mower | `mumu-cli.exe` (replaces MuMuManager): launch, stop, settings, import/export by `--vmindex` | Widely used by MAA / mower users; official `mumu-control` agent skill | **Recommended** |
| **BlueStacks 5** | Toggle in settings | No special path; adb screencap (~100 ms) or minicap/DroidCast | Multi-instance manager, little CLI | MAA's "most stable" option; Hyper-V edition changes ports often (workaround: read `bluestacks.conf`) | Fallback |
| **LDPlayer 9** | Yes | Has its own IPC, less tooling | `ldconsole.exe` | MAA dropped support: port changes, black or flipped screenshots, freezes | Avoid |
| **Nox / MEmu** | Yes | No | Basic | Supported but lightly tested, aging Android versions | Skip |
| **Android Studio AVD** | Cleanest ADB | gRPC/console screenshots | `emulator` CLI, scriptable | Fine for apps; ARM-only games run poorly on x86 images | Skip on Windows |
| **Windows Subsystem for Android** | Yes | Unreliable (white screenshots) | n/a | Discontinued by Microsoft | Skip |

**Linux, for later:** **Redroid** (Android in Docker, headless, one container per account) is the best path to fully unattended, server-style running, especially on an ARM box where the game's native code runs without translation. Waydroid works on a desktop but is fussier. Neither is worth it for iteration 1.

**MuMu settings:** 1280×720 (16:9, 240 dpi), the resolution most bot assets assume; fixed frame rate; one instance per account.

## 2. Architecture fit

1. **Hands and eyes (no model):** MaaFramework controller over ADB with MuMu IPC screenshots and MaaTouch/MuMu input. Recognition by template match (buttons, icons) and OCR (PaddleOCR via ONNX, for counts like "2/2 attempts", timers, quest text).
2. **Scripts (no model):** one pipeline per daily task, each node = "recognize X → act → next". State detector = a set of "where am I" nodes (home, map, dungeon menu, battle, reward popup, unknown).
3. **Supervisor (model only on failure):** when a pipeline hits an unknown screen or times out, hand the screenshot plus recent log to Claude (later a local vision model) via MaaMCP. Claude recovers and writes the fix back as a new or patched pipeline node, so the same situation costs zero tokens next time.
4. **Entertainment agent (later):** reads the same event log.

Plain-Python alternative if MaaFramework is too opinionated: `adbutils` + OpenCV + RapidOCR, same layering, no visual editor/debugger.

## 3. Game technical notes (Sword x Staff)

**Known:**
- Developer BOLTRAY GAMES (Singapore). Released 2026-05-13, last store update 2026-09-11. Android and iOS, no PC client. 1M+ downloads, 7 UI languages.
- Idle RPG with an open world (Verdantglade, Cinder Ridge, Aqualis, Loong Haven), Warrior/Mage dual class, AFK income from "the Cart".
- **All battles are automatic.**
- Servers cap at 5,000 players and later merge; guilds are per server.
- Seasons (first ~1 month, then 2–3 months) partly reset levels, so unlock assumptions must be re-checked each season.

**Unknown until we have the APK** (plan: install from Play Store on MuMu, `adb shell pm path com.zjcs.android.us`, `adb pull` base and split APKs):
- Engine: `libil2cpp.so` + `libunity.so` (Unity → Il2CppDumper) or `libcocos*.so` (Cocos).
- Whether UI text lives in readable data files.
- Network protocol (state from traffic is a later optimization; vision-first baseline).
- Anti-tamper or emulator detection.

## 4. Daily content catalogue

Sources: community wiki and Prydwen guides (third party, not verified in-game). Unlock levels are account levels.

| Task | Where | Limit / notes | Type | Automation difficulty |
|---|---|---|---|---|
| Collect AFK / Cart rewards | Login, Home | Cart caps | Solo | Easy |
| Click wandering animals at Home | Home | Random respawns | Solo | Medium |
| Free daily stamina + Daily Shop | Shop | Refresh costs Rolla; Vault needs Dawnium | Solo | Easy |
| Vendor Booth (Lv 18) | Vendor | Buy materials, a few refreshes | Solo | Easy, needs buy rules |
| Daily Quests / Commissions | Quest menu | Complete all, claim chests | Solo | Medium |
| Material Dungeons | Dungeon menu | 2/2/2/2 free attempts; extras cost Dawnium | Solo | Easy |
| Daily Dungeons (Mythic gear) | Dungeon menu | Aim for A rank+ | Solo | Easy |
| Spend stamina (cap 300) on nodes | Map | Rolla first early on | Solo | Medium |
| Goddess / Witch / Hero statues | Map | One interaction daily | Solo | Medium |
| Stone Tablet quiz | Map | Once daily, lore answers | Solo | Model fallback (or cached answers) |
| Guild donation (Lv 15) | Guild | 3 basic donations daily | Guild | Easy |
| Guild Farm | Guild | Plant + harvest once daily | Guild | Easy |
| Guild Boss | Guild | Auto battle | Guild/co-op | Easy |
| Guild floating-island AFK farm | Guild | Set and forget | Guild | Easy |
| Co-op Dungeons | Dungeon menu | Matchmaking | Co-op | Medium |
| 6-player Raids / Raid Bosses | Raid menu | Solo or group | Co-op | Medium |
| Solo Arena / 3v3 Tournament | PvP | Auto battle | PvP | Easy–medium |
| Guild War | Guild | When scheduled | Guild/PvP | Later |
| Gem synthesis 3:1 | Gem menu | Housekeeping | Solo | Easy |
| Mail, event check-ins, codes | Mail / Events | Varies | Solo | Easy; events change (model fallback) |

**Suggested iteration 1 scope:** AFK collect, free stamina, daily shop, daily quests, material + daily dungeons, guild donation/farm/boss, arena attempts, mail. Defer map exploration, statues, quiz, co-op queues, and Guild War to iteration 2.

## 5. Open questions

1. Test account level and server (guilds unlock at 15, vendor at 18, Fantomons at 51).
2. Daily reset time on the server.
3. Is co-op content in iteration 1?

## 6. Getting maes2024 ready

1. CPU virtualization on in BIOS.
2. Install MuMu Player 12, one instance at 1280×720.
3. Play Store sign-in with the test account, install Sword x Staff, finish the tutorial.
4. Install Python 3.12 and Android platform-tools (`adb`).

## Sources

- Google Play listing: https://play.google.com/store/apps/details?id=com.zjcs.android.us
- Community wiki, Daily Routine: https://sword-x-staff-wiki.pages.dev/daily-routine
- Prydwen beginner guide: https://www.prydwen.gg/sword-x-staff/guides/beginner-guide
- Prydwen tips and tricks: https://prydwen.gg/sword-x-staff/guides/tips-and-tricks
- skich.app game overview: https://skich.app/games/sword-x-staff
- MAA emulator support: https://github.onedrive11.workers.dev/john180/MaaAssistantArknights/blob/master/docs/en-us/1.3-EMULATOR_SUPPORTS.md
- arknights-mower device control: https://deepwiki.com/ArkMowers/arknights-mower/5.2-device-control-and-input
- MuMu control agent skill: https://www.skills.sh/site/skills.mumu.163.com/mumu-control
- MaaFramework quick start: https://maafw.com/en/docs/1.1-QuickStarted
- MaaMCP: https://www.sourcepulse.org/projects/21493524
