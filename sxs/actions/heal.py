"""Heal before a fight (mae, 2026-11-03: at least 70% HP before any fight).

`quick_heal` is the one portrait Quick Heal sequence every loop uses; `heal_via_portrait` repeats it until the bar
reads 70% or more. HP itself is read by `sxs.vision.hp.bar_fraction`.
"""

from __future__ import annotations

import logging
import time

import numpy as np

from ..core import ui
from ..vision.hp import HUD_HP_BAR, PREP_HP_BAR, bar_fraction

__all__ = ["FIGHT_MIN_HP", "HUD_HP_BAR", "PREP_HP_BAR", "hp_ok", "quick_heal", "heal_via_portrait"]

log = logging.getLogger("sxs.actions.heal")

FIGHT_MIN_HP = 70  # %
RETRY, BACK_OUT, NOTHING = "retry", "back", "nothing"


def hp_ok(frame: np.ndarray, bar=HUD_HP_BAR) -> bool:
    return bar_fraction(frame, bar) * 100 >= FIGHT_MIN_HP


def quick_heal(dev, det, if_no_profile: str = RETRY) -> bool:
    """Open the player profile from the top-left portrait, press Quick Heal (one cooked dish), close it.
    if_no_profile, when the portrait didn't open the profile: RETRY (back arrow, then the portrait once more),
    BACK_OUT (back arrow and give up: the caller's map branch heals), or NOTHING. True if Quick Heal was pressed."""
    dev.tap(*ui.HUD_PORTRAIT)
    time.sleep(2)
    if det.detect().state != "player_profile":
        if if_no_profile == NOTHING:
            return False
        dev.tap(*ui.BACK_ARROW)
        time.sleep(2)
        if if_no_profile == BACK_OUT:
            return False
        dev.tap(*ui.HUD_PORTRAIT)
        time.sleep(2)
        if det.detect().state != "player_profile":
            return False
    dev.tap(*ui.QUICK_HEAL)
    time.sleep(2)
    dev.tap(*ui.ABOVE_POPUP)  # close the profile
    time.sleep(1.5)
    return True


def heal_via_portrait(dev, det, bar=HUD_HP_BAR, tries: int = 3) -> bool:
    """Quick Heal until the bar reads FIGHT_MIN_HP or more. False when HP stays low (no dishes), in which case the
    caller must not fight."""
    for _ in range(tries):
        if hp_ok(dev.screenshot(), bar):
            return True
        log.info("HP under %d%%: quick heal from the portrait", FIGHT_MIN_HP)
        quick_heal(dev, det, RETRY)
    return hp_ok(dev.screenshot(), bar)
