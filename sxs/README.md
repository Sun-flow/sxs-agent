# sxs: the bot package

## How to run and where things live

Run from the repo root on the Windows PC (`.venv\Scripts\python`, shown below as `python`):

    python -m sxs --help                    # every loop and device command
    python -m sxs <loop> [options]          # run a loop, e.g. python -m sxs daily --only guild
    python -m sxs <loop> --help             # that loop's options
    python -m sxs see badges|minimap|gift [FRAME ...]   # run one detector on saved frames or a live screenshot
    python -m sxs bank | label             # unlabelled-screens bank (docs/screens/README.md)
    python -m sxs state | screenshot | tap X Y | swipe ... | back | start | stop | capture NAME | watch

Coordinates are in the 720×1280 portrait frame. No module calls a model.

| Folder | Holds | Rule |
|---|---|---|
| `core/` | Device, state detector, navigator, paths, shared screen coordinates (`ui.py`), daily marks, the loop contract (`loop.py`) | Knows nothing about any one game system |
| `vision/` | Reading the screen: OCR helpers, HP bar, HUD numbers, player label, tracker, pickups, badges, minimap, gift | Never taps |
| `policy/` | Decisions from `resource/policy/*.json`: card/popup decider, free-claim presser | The spend blocklists live here (**safeguard**) |
| `actions/` | Small reusable steps that tap: heal, close rewards / step dialogue, go to an area, unstick, camera, watchdog | No loop of its own, except `goto` |
| `loops/` | Goal-driven loops, one module each, each exposing `LOOP` | Registered in `loops/__init__.py` |

## The loop contract (`core/loop.py`, mae 2026-11-04)

Every loop has the same inputs, outputs and readouts:

- **Inputs.** A module-level `LOOP = Loop(name, title, summary, run, args=None, ok={...})`. `args(parser)` adds the
  loop's options; `run(ctx, opts)` gets `ctx.dev`, `ctx.det`, `ctx.nav`, built once by the runner.
- **Outputs.** `run` returns a `Result(status, ok, data)`, or a plain status string or a dict with `end`/`status`
  (converted by `as_result`). `ok` is whether `status` is in the loop's `ok` set.
- **Readouts.** At start the loop logs mae's banner (`[Running X Loop]` / `[Goal: ...]` / `[End condition: ...]`).
  At the end the runner logs `[Result X] status` and prints one JSON line:
  `{"loop": "explore", "status": "complete", "ok": true, "seconds": 812, ...}`.
  Exit code 0 ok, 1 needs a look, 2 refused (a `refused: ...` status, e.g. pray without approval).

- **Time.** Runs are short (mae, 2026-11-04: 1-2 minutes, never 10+). Every run has a budget (`Loop.budget`,
  default 120 s; `--budget SECONDS`; a loop's own `--minutes` plus 15 s grace) and ends `over_budget` when it
  passes it, then goes home. Code that calls `progress(reading)` (the Heartbeat in explore and fogwalk, the
  collector in gather) also ends `stalled` when the reading hasn't changed for `--stall` seconds (default 60;
  fights and loading screens count as moving). `with task(name, seconds) as t:` gives one step its own budget:
  daily runs each step that way (120 s each, 20 min in all), so a stuck step is cut and the next one starts.

`tests/check_loops.py` checks every registered loop against this offline, including the budget and stall stops.

## Loops

| Command | Module | Loop | Common options |
|---|---|---|---|
| `daily` | `loops/daily.py` | Every once-a-day step, then upgrades | `--only a,b`, `--force` |
| `explore` | `loops/explore.py` | Quest follower (tracker marker) | `--chain --minutes 10`, `--choose REGEX` |
| `roam` | `loops/roam.py` | Unexplored areas under our power, bless statues | `--minutes 30`, `--area NAME` |
| `fogwalk` | `loops/fogwalk.py` | Fog Walk inside one side area | `--area "Stone Ruins I" --minutes 5` |
| `goto` | `actions/goto.py` | Walk somewhere via the area map | `"Highland Woods"` or `X Y` |
| `gather` | `loops/gather.py` | Generic `collect(Target)` for ore, sand, essence, rolla, bellflower | `--material sand`, `--check`, `--harvest` |
| `upgrade` | `loops/upgrade.py` | Every "!" on the Character screen | `--only skills` |
| `strengthen` | `loops/strengthen.py` | Cart, gear/charm equip, enhance, techniques | |
| `tower` | `loops/tower.py` | Fantasia Ascent, one run a day | `--tower "Moonveil Woods"` |
| `guild` | `loops/guild.py` | Donate x2, Forge AFK, Conquest | `--only donate,afk` |
| `mall` | `loops/mall.py` | Mall free gift boxes, never a price (**safeguard**) | |
| `vendor` | `loops/vendor.py` | Vault free x30 stamina only (**safeguard**) | `--check` |
| `tutorial` | `loops/tutorial.py` | Follow tutorial highlights | `--steps 40` |
| `pray` | `loops/pray.py` | Skill pulls. **Only when mae authorises a run**; no loop imports it | `--check` / `--pulls N --handler-approved` (x10 only) |

Who calls whom: `daily` → `mall`, `vendor`, `tower`, `guild`, `gather`, `strengthen`, `upgrade`, `policy.claims`.
`roam` → `actions.goto`, `fogwalk`; `fogwalk` → `explore` (HP reader), `gather` (stamina cost), `actions.rewards`;
`explore` → `tower`, `strengthen`. Everything → `core`.

## Shared pieces worth knowing

| Need | Use |
|---|---|
| A fixed button position | `core/ui.py` (bottom nav, back arrow, popup edges, OK/Cancel, portrait, Quick Heal); `ui.tap(dev, xy, wait)` |
| Tap and wait for a screen | `Navigator.tap(xy, wait)`, `Navigator.open(xy, state)`; `go_home()` from anywhere |
| Read a line, number, amount, a/b | `vision/ocr.py`: `read_line`, `read_int`, `read_amount`, `read_fraction`, `boxes_of` |
| Fight / loading / dialogue / reward screens in a loop | `actions/common.py`: `pass_through(dev, d)`, `close_rewards(dev, det)` |
| HP before a fight | `actions/heal.py`: `hp_ok`, `quick_heal`, `heal_via_portrait` (70% rule) |
| Stuck or unfamiliar screens | `actions/watchdog.py` (`Heartbeat`, `UnknownScreens`), `actions/unstick.py`, `device.save_unknown` → `captures/unknown/` |
| Repo paths | `core/paths.py` (`RESOURCE`, `POLICY`, `SCREENS`, `CAPTURES`, `LOGS`) |
| Reference screenshots | `core/screens.py`: `folder_for(name)`, `find(name)`, `reference_screens()`, `load_expected()`, the bank |

Read logs without MaaFramework's chatter: `grep -v -i "nemu\|product:\|same day\|^x:\|after convert"`.

## Adding things

- A new screen: capture it (`python -m sxs capture NAME`), add a `State.*` node, add it to
  `docs/screens/expected.json`. Steps in `docs/step2-hands-and-eyes.md` "Adding a screen".
- An unfamiliar screen from a run: `python -m sxs bank`, mae labels it in `docs/screens/unlabeled/README.md`,
  then `python -m sxs label` (see `docs/screens/README.md`).
- A new loop: a module in `loops/` with `LOOP = Loop(...)` and a line in `loops/__init__.py` REGISTRY. Log the banner
  at start, keep a time budget, `save_unknown` on unfamiliar screens, return a status. Wire it into `daily.py` if
  it's once a day. Then run `python tests/check_loops.py`.
- A coordinate or OCR pattern two modules need: put it in `core/ui.py` or `vision/`, not in both modules.
