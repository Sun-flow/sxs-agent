# docs

Design notes, one per plan step. The code is the source of truth; these explain how and why.

| File | Read when |
|---|---|
| `step1-emulator-and-game.md` | Emulator choice, architecture, daily-content catalogue, iteration 1 scope |
| `step2-hands-and-eyes.md` | Device layer, state detector, CLI, adding a screen |
| `step3-explore.md` | Explore loop, card decisions, tutorial follower, minimap, fog walk |
| `step4-dailies.md` | `sxs.loops.daily` steps and routes |
| `step5-upgrades.md` | Upgrade Loop and Gather Loop |
| `loops/` | Diagrams of every loop: goal, step order, checks, sub-loops, what it does on each screen; `loops/open-questions.md` lists where code and rules disagree (index `loops/README.md`) |
| `interrupts.md` | How a loop is paused for a tutorial, reward choice or popup and resumed (the interrupt table) |
| `function-check.md` | What each loop does, how to run it, what it reports, whether it has run live |
| `progress-tracker.md` | `python -m sxs progress` / `report`: what each stat is read from, what still needs a route, stats worth adding |
| `shop-tables.md` | Shop stock and mae's Buy? marks |
| `screens/` | Reference screenshots in folders by situation, `expected.json`, the `unlabeled/` bank; index in `screens/README.md` |
| `archive/` | History only (old log entries), never instructions |
