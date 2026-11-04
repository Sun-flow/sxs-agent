# sxs: the bot package

Run from the repo root on the Windows PC: `.venv\Scripts\python -m sxs.<module> ...` (shown below as `python -m`).
Coordinates are in the 720×1280 portrait frame. No module calls a model. Each loop prints its
`[Running X Loop]` / `[Goal]` / `[End condition]` banner, saves unfamiliar frames to `captures/unknown/`, and goes home on failure.

## Core (device, eyes, navigation)

| Module | What | Design doc |
|---|---|---|
| `device.py` | adb/MaaFramework device: screenshot, tap, swipe, start/stop; `banner`, `save_unknown`, `server_day` | step2 |
| `state.py` | "Where am I" detector over the `State.*` nodes in `resource/pipeline/state.json`; OCR helper | step2 |
| `nav.py` | `go_home()` from anywhere; back-arrow fallback | step2 |
| `replay.py` | Offline stand-in for `Device` (feeds saved frames); used by the offline tests | step2 |
| `cli.py` | `python -m sxs screenshot | tap | swipe | back | start | stop | state | capture NAME | watch` | step2 |
| `badges.py` | Red "!" badge finder (pixels, no templates) | step5 |
| `rewards.py` | Finished-quest gift + "!" on the tracker panel; claimed by Fog Walk; `python -m sxs.rewards [frame.png ...]` | step3 |
| `minimap.py` | Minimap tile classifier and path planner; `python -m sxs.minimap [frame.png]` | step3 |
| `marks.py` | Once-a-day marks in `logs/daily.json` (server day, resets 8:00 UTC-5) | step4 |
| `heal.py` | HP bar reader and Quick Heal via the portrait (70% rule) | step3 |
| `decide.py` | Card/popup decisions from `resource/policy/cards.json` | step3 |
| `claims.py` | Presses free Claim/Collect buttons only; spend-word blocklist (**safeguard, don't loosen**) | step4 |

## Loops (each has `python -m sxs.<name>`)

| Module | Loop | Common commands |
|---|---|---|
| `daily.py` | Dailies: every once-a-day step, then upgrades | `python -m sxs.daily [--only a,b] [--force]` |
| `explore.py` | Quest follower (tracker marker) | `python -m sxs.explore --chain --minutes 10` |
| `roam.py` | Roam: unexplored areas under our power, bless statues | `python -m sxs.roam [--minutes 30] [--area NAME]` |
| `fogwalk.py` | Fog Walk inside one side area | `python -m sxs.fogwalk --area "Stone Ruins I" --minutes 5` |
| `goto.py` | Walk somewhere via the area map | `python -m sxs.goto "Highland Woods"` |
| `gather.py` | Gather: generic `collect(Target)` for ore, sand, essence, rolla, bellflower | `python -m sxs.gather [--material sand] [--check] [--harvest]` |
| `upgrade.py` | Upgrade: every "!" on the Character screen | `python -m sxs.upgrade [--only skills]` |
| `strengthen.py` | Cart, gear/charm equip, enhance, techniques | `python -m sxs.strengthen` |
| `tower.py` | Fantasia Ascent, one run a day | `python -m sxs.tower --tower "Moonveil Woods"` |
| `guild.py` | Guild donate x2, Forge AFK, Conquest | `python -m sxs.guild [--only donate,afk]` |
| `mall.py` | Mall free gift boxes, never a price (**safeguard**) | `python -m sxs.mall` |
| `vendor.py` | Vendor Vault free x30 stamina only (**safeguard**) | `python -m sxs.vendor [--check]` |
| `tutorial.py` | Follow tutorial highlights | `python -m sxs.tutorial --steps 40` |
| `pray.py` | Skill pulls. **Only when mae authorises a run**; never called by any loop | `python -m sxs.pray --check` / `--pulls N --handler-approved` (x10 only) |

Who calls whom: `daily` → `claims`, `mall`, `vendor`, `tower`, `guild`, `gather`, `strengthen`, `upgrade`.
`roam` → `goto`, `fogwalk`; `fogwalk` → `explore` (handlers, watchdog), `rewards`; `gather` → `fogwalk`; `explore` → `tower`, `strengthen`.
All loops → `device`, `state`, `nav`.

Read logs without MaaFramework's chatter: `grep -v -i "nemu\|product:\|same day\|^x:\|after convert"`.

## Adding things

- A new screen: capture it (`python -m sxs capture NAME`), add a `State.*` node, add it to `tests/check_states_offline.py` EXPECTED. Steps in `docs/step2-hands-and-eyes.md` "Adding a screen".
- A new loop: a module with `main()`, the banner from `device.banner`, a time budget and `save_unknown` on unfamiliar screens; wire it into `daily.py` if it's once a day.
