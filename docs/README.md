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
| `loops/` | Diagrams of every loop: goal, step order, checks, sub-loops, what it does on each screen; `loops/open-questions.md` lists where code and rules disagree (index `loops/README.md`) |
| `interrupts.md` | How a loop is paused for a tutorial, reward choice or popup and resumed (the interrupt table) |
| `function-check.md` | What each loop does, how to run it, what it reports, whether it has run live |
| `progress-tracker.md` | `python -m sxs progress` / `report`: what each stat is read from, what still needs a route, stats worth adding |
| `vision-upgrade.md` | How a screen check works and where its time goes (measured), no-ML speed-ups to approve, and whether to train a YOLO/Roboflow UI detector |
| `detector-design.md` | Plan for a Roboflow-trained UI detector: classes, the three model choices with pros and cons, dataset pipeline, adoption |
| `detector-coverage.md` | Training-set coverage: boxes and images per detector class, item and item group, Roboflow's guidance and our minimum, and the labeling and capture plan for short classes |
| `labeler-diagnosis.md` | Where the map mislabels came from (red text as monsters, zoom knob as Rolla), counts, and the single-category review: `prelabel --one`, category filter, review grid, rejected drafts |
| `collectibles-capture-plan.md` | Training data for world collectibles: what they are, class options, burst capture of approach sequences, session plan, pre-roll buffer |
| `home-tap-pass-plan.md` | Plan for the Home tap pass (R-170): where it fits in the dailies, detection, captures, tests; not built yet |
| `strengthen-live-test-plan.md` | Live test steps for the gacha, relic, rank-first and swipe-fallback build: commands, expected readouts, stop conditions |
| `shop-tables.md` | Shop stock and mae's Buy? marks |
| `screens/` | Reference screenshots in folders by situation, `expected.json`, the `unlabeled/` bank; index in `screens/README.md` |
| `archive/` | History only (old log entries), never instructions |
- `fogwalk-postmortem.md`: why the Fog Walk was scrapped (2026-11-10), where it lives, what depends on it, what to keep.
