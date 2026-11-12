# Live test plan: gacha, relics, rank-first strengthen, swipe fallback

<!-- index: Live test steps for the gacha, relic, rank-first and swipe-fallback build: commands, expected readouts, stop conditions -->

For the builder session on the emulator, at a time mae approves. Code: PR for branch `claude/project-thread-6napxz`
(`sxs/loops/gacha.py`, `sxs/loops/relics.py`, `sxs/actions/home.py`, `Upgrader.rank_first` and `get_stronger` in
`sxs/loops/upgrade.py`, `Device.pan` in `sxs/core/device.py`). Flowcharts: `docs/loops/gacha.md`,
`docs/loops/upgrade.md` (Get stronger), `docs/loops/runner.md` (Swipe fallback). Offline checks:
`python tests/check_strengthen.py`.

READOUT RULE: before each step post the command, goal, target and stop condition; readouts about every 2 minutes
(no account name); `[Result]` at the end of each step. Stop the whole plan on any spend screen (Dawnium, a price,
"Purchase") and report with the saved frame.

## 0. Before

- `git pull`, then `python tests/check_strengthen.py` and `python tests/check_loops.py`: both end "all good" / 0
  problems.
- Note the starting numbers in the readout: power, level N/M, Rolla, Chrono Sand, the four badge counts if known.

## 1. Templates for Home (needed by steps 3 and 4)

Neither the unlocked gacha machine nor the Workbench has a template yet (only locked-crate pictures exist).

1. Home, pan with `python scripts/drag.py 240 820 390 820` until the gacha machine (between the Goddess Statue and the
   Vendor Booth) is in view. `python -m sxs capture home_aeonic_gacha_machine`.
2. Crop the machine only (no HUD, no chat) with `python scripts/crop.py <that capture> X Y W H <template>`, the
   template being resource/image/home/aeonic_gacha.png, about 150 x 170 px round the machine's body.
3. Same for the Workbench on the house's upper floor (pan the other way, `python scripts/drag.py 390 820 240 820`):
   capture `home_workbench_furniture`, crop to resource/image/home/workbench.png.
4. Add both to `resource/README.md`'s template list and `docs/screens/README.md`, commit.

Stop if: the machine or Workbench can't be found by hand (report with a screenshot).

## 2. Swipe fallback (`Device.pan`)

- Command: `python -m sxs strengthen --only cart`
- Goal: the Cart sweep uses `Device.pan`. Expected readouts: `found after N pans` or `home scene stopped moving
  left after N pans: its end`, then `cart claimed`.
- If MaaFramework's swipe has stopped again (after a game restart), expect one warning line
  "MaaFramework's swipe did not move the scene, adb's did: swiping through adb from now on" and the sweep to go on.
- Stop if: the sweep ends `no cart loot bubble found` while the Cart is visibly on screen (save a frame).

## 3. Aeonic Gacha

1. `python -m sxs gacha --check`. Goal: open the gacha and read the tiers, no draws. Expected:
   `Rare 35/10, top 35: Draw x3 (30)` style lines for all four tiers, `[Result Gacha] check`.
   Stop if: `not_found` (template step 1), `unknown_screen` (frame in captures/unknown/).
2. Only if some tier shows 100 or more badges (or the ticket counter shows "!"): `python -m sxs gacha`.
   Goal: counter claimed, a Draw x10 on each tier that reads "Draw x10 (100)", Goals claimed. Expected readouts:
   `ticket counter: 20/5 -> 0/5 (4 taps)`, `Rare x10: new relics [...], 9 shard bundles (saved ...png)`,
   `gacha: N draws`. Result screens are saved in `captures/gacha/`.
   Stop if: any button other than Draw x10 is pressed, a Dawnium or price screen shows, or the run ends
   `unknown_screen`.
   If no tier can afford x10, the run ends `nothing` after claiming the counter and Goals: that is a pass.

## 4. Workbench relics

1. `python -m sxs relics --check`. Goal: open the Workbench and read each element's displayed relics. Expected:
   `Light: affinity N, displayed relics [3, ...]` per element with relics, `[Result Relics] check`.
   Stop if: `no_template` (step 1 not done), `unknown_screen`, or the levels read don't match the screen.
2. `python -m sxs relics`. Goal: activate any new relic, ascend where shards read 20/20 with the button's pip,
   enhance in bands of one level, letting auto-combine fill a short material (mae, always allowed). Expected:
   `relic activated (Light tab)`, `relic slot 0: +3 -> +4`, possibly `a cost is short (...); auto-combine fills it`
   and `auto-combine dialog (...): accepting` (its frame saved to captures/unknown/ as a reference), then
   `relic slot N at +4: no pip, short even with auto-combine` at the end; `[Result Relics] done` or `nothing`.
   Stop if: Replace is pressed (it must never be), the "universal materials" option changes, or more than 30
   presses.

## 5. Rank (on its bang or at the cap) and the whole pass

1. `python -m sxs strengthen --only rank`. Goal: read "Level N/M" and the rank badge's corner on the Character
   screen; open the rank page only on a red "!" or blue pip, at the cap, or within 3 levels of it (materials early).
   Expected at 38/40 with the red "!" mae saw: `rank: level (38, 40), bang True: advance now`, then the rank page:
   Goals claimed if lit, the costs line, and a Flower Harvest gather if Bellflowers are short and tagged Available.
   Far below the cap with no bang: `rank: ... no bang on the rank badge: nothing to do` and the rank page stays shut.
   At the cap with "!" on Advance: `rank: advanced 1 time(s)` (bed EXP collected after).
   Stop if: the level or the bang reads wrong against the screen (save a frame for the test).
   Stop if: Advance is pressed while its button shows only the blue pip (it must not be).
2. `python -m sxs strengthen`. Goal: the whole pass in order cart, rank, gacha, relics, gear_swap, charms, upgrade,
   each with `[strengthen <step>] <status>`. Expected end: `[Result Strengthen] done` within about 15 minutes.
   Stop if: a step repeats, a step ends `error`, or a step runs past its budget twice.

## After

- Report power before and after, and every step's status.
- Commit the two templates (aeonic_gacha, workbench) and the captures to the PR branch; update
  `memory-bank/status.md` (live-tested items) and `docs/function-check.md`.
