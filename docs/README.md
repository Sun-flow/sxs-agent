# docs

Design notes, one per plan step. The code is the source of truth; these explain how and why.

| File | Read when |
|---|---|
| `step1-emulator-and-game.md` | Emulator choice, architecture, daily-content catalogue, iteration 1 scope |
| `step2-hands-and-eyes.md` | Device layer, state detector, CLI, adding a screen |
| `step3-explore.md` | Explore loop, card decisions, tutorial follower, minimap (its fog walk was replaced by step 6) |
| `step4-dailies.md` | `sxs.loops.daily` steps and routes |
| `step5-upgrades.md` | Upgrade Loop and Gather Loop |
| `step6-clear-zone.md` | Clear Zone: goal-directed exploration (every leg a named objective, progress = % or objects), which replaced the Fog Walk |
| `big-map-survey.md` | Why the big map is surveyed again and again (every caller, measured costs) and the shared-survey design proposed to replace the repeats (2026-11-11, for mae's review) |
| `loops/` | Diagrams of every loop: goal, step order, checks, sub-loops, what it does on each screen; `loops/open-questions.md` lists where code and rules disagree (index `loops/README.md`) |
| `interrupts.md` | How a loop is paused for a tutorial, reward choice or popup and resumed (the interrupt table) |
| `function-check.md` | What each loop does, how to run it, what it reports, whether it has run live |
| `progress-tracker.md` | `python -m sxs progress` / `report`: what each stat is read from, what still needs a route, stats worth adding |
| `vision-upgrade.md` | How a screen check works and where its time goes (measured), no-ML speed-ups to approve, and whether to train a YOLO/Roboflow UI detector |
| `detector-design.md` | Plan for a Roboflow-trained UI detector: classes, the three model choices with pros and cons, dataset pipeline, adoption |
| `home-tap-pass-plan.md` | Plan for the Home tap pass (R-170): where it fits in the dailies, detection, captures, tests; not built yet |
| `shop-tables.md` | Shop stock and mae's Buy? marks |
| `screens/` | Reference screenshots in folders by situation, `expected.json`, the `unlabeled/` bank; index in `screens/README.md` |
| `archive/` | History only (old log entries), never instructions |
- `fogwalk-postmortem.md`: why the Fog Walk was scrapped (2026-11-10), where it lives, what depends on it, what to keep.
