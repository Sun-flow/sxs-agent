"""Screens every map loop handles the same way: wait out fights and loading, step through dialogue, close rewards.

`pass_through(dev, d)` returns True when it handled the screen, so a loop only writes the cases it treats
differently:

    if pass_through(dev, d, on_dialogue=log_dialogue):
        continue
"""

from __future__ import annotations

import time
from typing import Callable, Optional

from ..core import ui

FIGHT_STATES = ("battle", "loading")
REWARD_STATES = ("reward_popup", "tap_to_continue")
TOWER_STATES = ("tower_list", "tower_floors", "tower_result")


def pass_through(dev, d, on_dialogue: Optional[Callable[[], None]] = None) -> bool:
    """Handle a fight, loading screen, dialogue line or reward popup. True if `d` was one of those."""
    if d.state in FIGHT_STATES:
        time.sleep(2)
    elif d.state == "dialogue":
        if on_dialogue:
            on_dialogue()
        ui.tap(dev, ui.DIALOGUE_NEXT, 1.2)
    elif d.state in REWARD_STATES:
        ui.tap(dev, ui.REWARD_CLOSE, 1.2)
    else:
        return False
    return True


def close_rewards(dev, det, tries: int = 3, wait: float = 1.5) -> int:
    """Close reward popups while they show. Returns how many were closed."""
    n = 0
    for _ in range(tries):
        if det.detect().state not in REWARD_STATES:
            break
        ui.tap(dev, ui.REWARD_CLOSE, wait)
        n += 1
    return n


def start_fight(dev, det) -> bool:
    """Battle prep showing: heal to 70% from the portrait (R-061, R-078), then Start Battle. Returns False (after
    backing out of prep) when HP stays low, so the caller must not fight. Any loop that meets a guard and wants the
    fight calls this, then carries on with its own goal (mae, 2026-11-09: gather fights a guard, then resumes the
    pickup)."""
    from . import heal  # heal imports nothing from here; kept local so common stays light

    if not heal.heal_via_portrait(dev, det, heal.PREP_HP_BAR):
        ui.tap(dev, ui.BACK_ARROW, 2)
        return False
    ui.tap(dev, ui.START_BATTLE, 3)
    return True
