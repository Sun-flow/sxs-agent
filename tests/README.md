# tests

| File | Needs | Checks |
|---|---|---|
| `check_repo.py` | Python only | Pipelines parse, every template and policy file exists, every `python -m sxs <loop>` / `sxs/.../X.py` / `scripts/X.py` named in docs exists (old `python -m sxs.X` flagged), all modules compile |
| `check_loops.py` | Python, OpenCV, MaaFramework (imports only) | Every registered loop meets the loop contract; pray refuses without approval |
| `check_states_offline.py` | MaaFramework + OCR models | State detector over `docs/screens/<folder>/*.png` against `docs/screens/expected.json` (add an entry with each new screen); `NAME ...` checks only those |
| `check_rewards_offline.py` | OpenCV | Tracker gift + "!" detector over `docs/screens` (claimable set, badge painted out) |
| `check_interrupts.py` | OpenCV | Interrupt layer: pause, handle, resume, owned rows, mutes, LoopStop through the runner; the tutorial row fires on no reference screen it watches |
| `check_upgrade_logic.py` | MaaFramework, OpenCV | Badge finder, gather pickup choice, relic banding plan, Cart row pick and cost icons |
| `check_progress.py` | MaaFramework + OCR models | Progress tracker: stat readers on reference screens, bands, the day report (temp logs), the home > profile > Journal route replayed |
| `check_zones.py` | OpenCV, MaaFramework (imports only) | Minimap zone-border detector on reference frames, border blocks the planner, location tree decisions (R-132, R-135), area-map pan merge, Cart Unlock finder (R-137) |
| `check_clear.py` | OpenCV, MaaFramework (imports only) | Clear Zone: fog frontier on a reference area map, minimap goals are objects only, leg bookkeeping (gain, failed spots, ring resting, stall count) |
| `check_strengthen.py` | MaaFramework + OCR models, OpenCV | Aeonic Gacha readers and a replayed draw pass (x10 only, never x1 or short xN), result names, timed pack; Workbench relic readers; rank-first level and Bellflower check; strengthen step order; `Device.pan` adb fallback and the Home sweep |
| `check_labeler.py` | Pillow, OpenCV | Labeler page API in a temp copy: save boxes, crops and manifest, bank row, filing moves boxes and crops, paths outside docs/screens refused, `vision/labels.py` finds a crop |
| `check_detect_data.py` | Pillow, OpenCV | UI detector data: class list, `cls`/draft on boxes, pre-label merge keeps mae's boxes, YOLO export (format, split, minimap crop, name and chat masking, private screens left out) |
| `smoke_test.py [--no-restart]` | Live emulator | Cold start → home → menus → home |

Run the first twelve after any code change; `smoke_test.py` after changing navigation.
