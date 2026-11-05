# tests

| File | Needs | Checks |
|---|---|---|
| `check_repo.py` | Python only | Pipelines parse, every template and policy file exists, every `python -m sxs <loop>` / `sxs/.../X.py` / `scripts/X.py` named in docs exists (old `python -m sxs.X` flagged), all modules compile |
| `check_loops.py` | Python, OpenCV, MaaFramework (imports only) | Every registered loop meets the loop contract; pray refuses without approval |
| `check_states_offline.py` | MaaFramework + OCR models | State detector over `docs/screens/<folder>/*.png` against `docs/screens/expected.json` (add an entry with each new screen); `NAME ...` checks only those |
| `check_rewards_offline.py` | OpenCV | Tracker gift + "!" detector over `docs/screens` (claimable set, badge painted out) |
| `check_interrupts.py` | OpenCV | Interrupt layer: pause, handle, resume, owned rows, mutes, LoopStop through the runner; the tutorial row fires on no reference screen it watches |
| `check_upgrade_logic.py` | MaaFramework, OpenCV | Badge finder, gather pickup choice, relic banding plan |
| `check_progress.py` | MaaFramework + OCR models | Progress tracker: stat readers on reference screens, bands, the day report (temp logs), the home > profile > Journal route replayed |
| `smoke_test.py [--no-restart]` | Live emulator | Cold start → home → menus → home |

Run the first seven after any code change; `smoke_test.py` after changing navigation.
