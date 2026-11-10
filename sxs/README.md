# sxs: the bot package

## How to run and where things live

Run from the repo root on the Windows PC (`.venv\Scripts\python`, shown below as `python`):

    python -m sxs --help                    # every loop and device command
    python -m sxs <loop> [options]          # run a loop, e.g. python -m sxs daily --only guild
    python -m sxs <loop> --help             # that loop's options
    python -m sxs see badges|minimap|gift [FRAME ...]   # run one detector on saved frames or a live screenshot
    python -m sxs bank | label             # unlabelled-screens bank (docs/screens/README.md)
    python -m sxs labeler                  # web page: name screens, box buttons/text/icons, save crops as templates
    python -m sxs report [--day DAY]       # the day's progress report from saved snapshots (no emulator)
    python -m sxs prelabel [--ocr]         # draft detector boxes on the reference screens (no emulator)
    python -m sxs dataset [--zip]          # YOLO dataset for Roboflow, account name and chat blacked out (no emulator)
    python -m sxs bench [--one-per-state]  # screen-check timings on the reference screens, old way vs new (no emulator)
    python -m sxs state | screenshot | tap X Y | swipe ... | back | start | stop | capture NAME | watch

Coordinates are in the 720×1280 portrait frame. No module calls a model.

| Folder | Holds | Rule |
|---|---|---|
| `core/` | Device, state detector, navigator, paths, shared screen coordinates (`ui.py`), daily marks, run and progress records (`records.py`), the loop contract (`loop.py`) | Knows nothing about any one game system |
| `vision/` | Reading the screen: OCR helpers, HP bar, HUD numbers, account stats (`stats.py`), player label, tracker, pickups, badges, minimap, gift | Never taps |
| `detect/` | UI detector data (docs/detector-design.md): `prelabel.py` drafts boxes from the existing detectors, `dataset.py` exports the YOLO dataset with names blacked out | Never taps; no model yet |
| `policy/` | Decisions from `resource/policy/*.json`: card/popup decider, free-claim presser; `fights.py` (1.25x power rule), `zones.py` (location tree in `resource/world/zones.json`: next zone, crossing check, ways in) | The spend blocklists live here (**safeguard**) |
| `actions/` | Small reusable steps that tap: heal, close rewards / step dialogue, go to an area, unstick, camera, watchdog | No loop of its own, except `goto` |
| `loops/` | Goal-driven loops, one module each, each exposing `LOOP` | Registered in `loops/__init__.py` |

## The loop contract (`core/loop.py`, mae 2026-11-04)

Every loop has the same inputs, outputs and readouts:

- **Inputs.** A module-level `LOOP = Loop(name, title, summary, run, args=None, ok={...})`. `args(parser)` adds the
  loop's options; `run(ctx, opts)` gets `ctx.dev`, `ctx.det`, `ctx.nav`, built once by the runner.
- **Outputs.** `run` returns a `Result(status, ok, data)`, or a plain status string or a dict with `end`/`status`
  (converted by `as_result`). `ok` is whether `status` is in the loop's `ok` set.
- **Readouts.** At start the loop logs mae's banner (`[Running X Loop]` / `[Goal: ...]` / `[End condition: ...]`).
  At the end the runner logs `[Result X] status`, appends the readout to `logs/runs.jsonl`, and prints one JSON line:
  `{"loop": "explore", "status": "complete", "ok": true, "seconds": 812, ...}`.
  Exit code 0 ok, 1 needs a look, 2 refused (a `refused: ...` status, e.g. pray without approval).

- **Time.** Runs are short (mae, 2026-11-04: 1-2 minutes), but the budget is a stuck check, not a hard stop
  (mae, 2026-11-05). Every `--budget` seconds (default 120) the runner asks whether the loop reported progress in
  the last `--stall` seconds (default 60): if yes it carries on for another budget (up to 10 times), if not it ends
  `over_budget` and goes home. Code that calls `progress(reading)` (Heartbeat in explore and fogwalk, the collector
  in gather, claims, upgrade presses, tower floors, mall pages, gear swaps) also ends `stalled` when the reading
  hasn't changed for `--stall` seconds; a loop that never reports progress stops at its first budget. A loop's own
  `--minutes` is only its outer ceiling. `with task(name, seconds) as t:` gives one step its own check: daily runs
  each step that way (120 s each), so a stuck step is cut and the next one starts.

- **Interrupts** (mae, 2026-11-05). The runner wraps the detector so that after every screen check one table,
  `actions/interrupts.py`, can pause the loop for a tutorial highlight, Choose Your Reward, the rating popup or chat,
  run that row's short handler (tutorial highlights on the island map, home and Companions), and hand the loop the screen after it (`[Interrupt] ...` / `[Resume X] ...`). A
  handler that needs mae raises `LoopStop(status)` and the run ends with that status. `Loop.owns` names rows a loop
  handles itself; `resume_with(det, fn)` registers a step that puts the loop back where its goal is. Mechanism in
  `core/interrupts.py`, design in `docs/interrupts.md`. Add a screen every loop should handle the same way as a row
  there, not as a special case in a loop.

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
| `cart` | `loops/cart.py` | Claim the Cart, then raise its Stone and Wood rows evenly (R-136); ends when capped or short | `--check`, `--max N` |
| `gearswap` | `loops/gearswap.py` | Equip the better piece wherever a gear slot shows "!" (separate from enhancing) | `--check`, `--all` |
| `strengthen` | `loops/strengthen.py` | `upgrade.get_stronger`: Cart, gear swap, charms, Upgrade Loop | |
| `tower` | `loops/tower.py` | Fantasia Ascent, one run a day | `--tower "Moonveil Woods"` |
| `guild` | `loops/guild.py` | Donate x2, Forge AFK, Conquest | `--only donate,afk` |
| `mall` | `loops/mall.py` | Mall free gift boxes, never a price (**safeguard**) | |
| `vendor` | `loops/vendor.py` | Vault free x30 stamina only (**safeguard**) | `--check` |
| `tutorial` | `loops/tutorial.py` | Follow tutorial highlights | `--steps 40` |
| `progress` | `loops/progress.py` | Read the account's numbers (read only), keep them per day, report the changes | `--only hud,profile`, `--guild-shop` |
| `pray` | `loops/pray.py` | Skill pulls. **Only when mae authorises a run**; no loop imports it | `--check` / `--pulls N --handler-approved` (x10 only) |

Who calls whom: `daily` → `mall`, `vendor`, `gearswap`, `tower`, `guild`, `gather`, `strengthen`, `upgrade`, `policy.claims`, `progress`.
`progress` → `guild` (island and building taps), `roam` (area map reader).
`roam` → `actions.goto`, `fogwalk`; `fogwalk` → `explore` (HP reader), `gather` (stamina cost), `actions.rewards`;
`explore` → `tower`, `upgrade.get_stronger` (→ `gearswap`, `upgrade`). Everything → `core`.

## Shared pieces worth knowing

| Need | Use |
|---|---|
| A fixed button position | `core/ui.py` (bottom nav, back arrow, popup edges, OK/Cancel, portrait, Quick Heal); `ui.tap(dev, xy, wait)` |
| Tap and wait for a screen | `Navigator.tap(xy, wait)`, `Navigator.open(xy, state)`; `go_home()` from anywhere |
| Read a line, number, amount, a/b | `vision/ocr.py`: `read_line`, `read_int`, `read_amount`, `read_fraction`, `boxes_of` |
| Fight / loading / dialogue / reward screens in a loop | `actions/common.py`: `pass_through(dev, d)`, `close_rewards(dev, det)` |
| HP before a fight | `actions/heal.py`: `hp_ok`, `quick_heal`, `heal_via_portrait` (70% rule) |
| A screen any loop may meet (tutorial, reward choice, popup) | a row in `actions/interrupts.py` (`docs/interrupts.md`) |
| Stuck or unfamiliar screens | `actions/watchdog.py` (`Heartbeat`, `UnknownScreens`), `actions/unstick.py`, `device.save_unknown` → `captures/unknown/` |
| Account numbers off a screen (top bar, profile, Journal, Cart, guild) | `vision/stats.py`; small badge labels: `ocr.zoomed_lines` |
| Per-day records (`logs/runs.jsonl`, `logs/progress/`) | `core/records.py`: `note(source, values)` from any loop that sees a stat on the way |
| Repo paths | `core/paths.py` (`RESOURCE`, `POLICY`, `SCREENS`, `CAPTURES`, `LOGS`) |
| Screen-check speed (one text read per frame, frame cache, `SXS_INFERENCE`) | `core/state.py` docstring; timings with `core/bench.py`; why in `docs/vision-upgrade.md` |
| Reference screenshots | `core/screens.py`: `folder_for(name)`, `find(name)`, `reference_screens()`, `load_expected()`, the bank |
| A button, text line or icon mae boxed in the labeler | `vision/labels.py`: `roi(screen, box)`, `find(frame, screen, box)`, `tap_point(...)`; data in `core/labels.py` |

Read logs without MaaFramework's chatter: `grep -v -i "nemu\|product:\|same day\|^x:\|after convert"`.

## Adding things

- A new screen: capture it (`python -m sxs capture NAME`), add a `State.*` node, add it to
  `docs/screens/expected.json`. Steps in `docs/step2-hands-and-eyes.md` "Adding a screen".
- An unfamiliar screen from a run: `python -m sxs bank`, then mae labels it in the labeler (`python -m sxs labeler`)
  or in `docs/screens/unlabeled/README.md`, then `python -m sxs label` (see `docs/screens/README.md`).
- A new loop: a module in `loops/` with `LOOP = Loop(...)` and a line in `loops/__init__.py` REGISTRY. Log the banner
  at start, keep a time budget, `save_unknown` on unfamiliar screens, return a status. Wire it into `daily.py` if
  it's once a day. Then run `python tests/check_loops.py`.
- A coordinate or OCR pattern two modules need: put it in `core/ui.py` or `vision/`, not in both modules.
