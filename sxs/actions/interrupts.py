"""The interrupt table: screens any loop may meet that get the same short handler wherever they show (mae,
2026-11-05). The mechanism is `sxs/core/interrupts.py`; this file is the one place these screens are handled.

Order is priority: the first row that matches wins. Add a row here instead of a special case in a loop.

| Row           | Fires on                                   | Handler                                       | Stops the loop when            |
|---------------|--------------------------------------------|-----------------------------------------------|--------------------------------|
| choose_reward | choose_reward                              | R-129 class-matched pick (actions/choose_reward) | both or neither usable: needs_decision |
| rating_popup  | rating_popup                               | "Later" (R-060)                               | never                          |
| chat          | chat                                       | close the panel (R-027)                       | never                          |
| tutorial      | world_map or home with a yellow highlight  | the tutorial loop's `follow` (bounded)        | highlight on a spend word      |

Not in the table, on purpose: fights, loading, dialogue and reward popups (every loop passes through them already,
`actions/common.pass_through`); defeated, battle prep and cards (a loop's goal decides those); unknown (explicit,
mae's rule).

The tutorial row checks only world_map and home: on the reference screens `find_highlight` also matches Mall buttons,
prayer tabs, tower floor rows, the bed bubble and popups (18 false matches, none on world_map or home). Tutorials
elsewhere (unknown overlays, the Companions "Invite" glow) stay with `python -m sxs tutorial` until live frames
let the finder tell them apart. See docs/interrupts.md.
"""

from __future__ import annotations

import logging

from ..core import ui
from ..core.interrupts import MUTE, RESUME, Interrupt, LoopStop

log = logging.getLogger("sxs.actions.interrupts")

RATING_LATER = (360, 882)  # same as nav.TOWARD_HOME
CHAT_CLOSE = (42, 1226)
TUTORIAL_STEPS = 20


def _choose_reward(dev, det, d) -> str:
    from . import choose_reward
    if choose_reward.choose(dev, det) != "chosen":
        raise LoopStop("needs_decision", screen="choose_reward")
    return RESUME


def _tap(xy, wait=1.5):
    def handler(dev, det, d) -> str:
        ui.tap(dev, xy, wait)
        return RESUME
    return handler


def _tutorial_on_screen(frame, d) -> bool:
    from ..loops.tutorial import find_highlight
    return find_highlight(frame) is not None


def _tutorial(dev, det, d) -> str:
    from ..loops import tutorial
    end = tutorial.follow(dev, det, TUTORIAL_STEPS)
    if end == "spend_prompt":
        raise LoopStop("tutorial_spend_prompt")
    if end == "stuck":
        return MUTE  # same box, screen not reacting: probably not a tutorial; let the loop carry on
    return RESUME


TABLE = [
    Interrupt("choose_reward", frozenset({"choose_reward"}), _choose_reward, budget=30,
              label="Choose Your Reward"),
    Interrupt("rating_popup", frozenset({"rating_popup"}), _tap(RATING_LATER), budget=15, label="rating popup"),
    Interrupt("chat", frozenset({"chat"}), _tap(CHAT_CLOSE), budget=15, label="chat panel"),
    Interrupt("tutorial", frozenset({"world_map", "home"}), _tutorial, when=_tutorial_on_screen, budget=90,
              label="tutorial highlight"),
]
