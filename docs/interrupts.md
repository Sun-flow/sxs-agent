# Interrupts: switching tasks when the screen changes

mae, 2026-11-05: the state detector should let the bot move between tasks (explore and tutorial, say) when it sees
the screen change. Seen that night: a yellow tutorial highlight framed the Auroradrasil tree, Fog Walk kept tapping
the map underneath it, and the builder had to stop Fog Walk and run the tutorial loop by hand.

## How it works

Every loop asks the detector "where am I" before it acts. The runner (`sxs/core/loop.py`, `connect(..., loop)`) wraps
the detector in `InterruptingDetector` (`sxs/core/interrupts.py`). After each screen check it walks one table,
`sxs/actions/interrupts.py`, in priority order. When a row matches:

1. `[Interrupt] tutorial highlight on world_map: pausing Fog Walk` is logged. The loop is paused simply because it is
   still waiting inside its `detect()` call; its goal, area and counters are its own locals and stay intact.
2. The row's handler runs under its own `task()` budget, with the bare detector (so it can't trigger another
   interrupt), and reports progress so the paused loop's stall check stays quiet.
3. Any resume step the loop registered (`with resume_with(det, fn):`) runs, to put the loop back where its goal is.
   Fog Walk walks back to its area if the handler left it at home.
4. The screen is checked again and that detection goes to the loop: `[Resume Fog Walk] after tutorial: resume (14 s)`.
   The run's JSON readout lists what ran under `interrupts`.

A handler returns `RESUME`, or `MUTE` (it didn't work here: ignore the row for 2 minutes), or raises
`LoopStop(status)` when it needs mae; the runner ends the run with that status (exit 1). A row that fires more than
5 times in 90 s is muted for 2 minutes, so a false match can't trap a loop. A loop that handles a screen itself
names the row in `Loop.owns` (the tutorial loop owns `tutorial`) or wraps a block in `with det.owning("name"):`.

## The table

| Row | Fires on | Handler | Stops the loop when |
|---|---|---|---|
| `choose_reward` | `choose_reward` | R-129 class-matched pick | both or neither card usable: `needs_decision` |
| `rating_popup` | `rating_popup` | Later (R-060) | never |
| `chat` | `chat` | close the panel (R-027) | never |
| `tutorial` | `world_map` or `home` with a yellow highlight box | `tutorial.follow`, 20 steps | highlight on a spend word: `tutorial_spend_prompt` |

Left out on purpose: fights, loading, dialogue and reward popups (every loop already passes through them with
`actions/common.pass_through`); defeated, battle prep and cards (the loop's goal decides those); `unknown` (explicit,
mae's rule: recover a bounded number of times, then stop and report).

## Why the tutorial row only watches the island map and home

`tutorial.find_highlight` looks for a yellow rounded outline. On the reference screens it also matches 18 ordinary
screens: Mall gift and deal buttons, prayer tabs, tower floor rows, gear resonance, class hierarchy, the bed bubble,
the rating popup and the wounded dialog. None of the 15 reference screens in `world_map` or `home` match, so the row
is limited to those states (`tests/check_interrupts.py` checks this on every run). Tested brightness inside versus
around the box as a second signal; popups dim the screen the same way, so it doesn't separate them.

Not covered yet, and handled by running `python -m sxs tutorial` as before:

- Tutorial overlays the detector reads as `unknown` (the post-rank overlays, R-036; `tutorial_highlight*.png`).
- The Companions screen, where the highlight is a filled glow around "Invite" instead of an outline (builder,
  2026-11-05); that screen also locks the back arrow.

Next step for both: capture live frames (`python -m sxs capture NAME`) of a real tutorial on those screens, then
either add a second highlight style to the finder or give the overlay a state of its own, and widen the row.

## Adding a row

Write a handler `handler(dev, det, detection) -> RESUME | MUTE` (or raise `LoopStop`), add an `Interrupt(...)` to
`TABLE` in priority order, remove the matching special case from any loop, and run `python tests/check_interrupts.py`.
