"""Heal before a fight (mae, 2026-11-03: at least 70% HP before any fight).

Shared by loops that start fights outside the explore loop (the tower, dailies). explore and fogwalk use its constants
and bar reader but still run the heal taps inline (moving them here changes retry behaviour; test live first).
"""

from __future__ import annotations

import logging
import time

import numpy as np

from . import nav
from .device import Device
from .state import StateDetector

log = logging.getLogger("sxs.heal")

FIGHT_MIN_HP = 70  # %
QUICK_HEAL = (510, 1064)  # player profile: Quick Heal (one cooked dish)
HUD_PORTRAIT = (70, 60)  # top-left avatar: opens the player profile
PREP_HP_BAR = (314, 406, 866, 876)  # battle prep: the bar under our character
HUD_HP_BAR = (116, 268, 52, 64)  # map HUD: the bar under our name


def bar_fraction(frame: np.ndarray, bar=HUD_HP_BAR) -> float:
    """Filled fraction of an HP bar (explore.hud_hp wraps it): the fill is bright and saturated, the empty track dull."""
    import cv2
    x0, x1, y0, y1 = bar
    hsv = cv2.cvtColor(frame[y0:y1, x0:x1], cv2.COLOR_BGR2HSV)
    filled = (hsv[..., 1] > 100) & (hsv[..., 2] > 150)
    return float(filled.any(axis=0).mean())


def heal_via_portrait(dev: Device, det: StateDetector, bar=HUD_HP_BAR, tries: int = 3) -> bool:
    """Quick Heal from the profile until the bar reads FIGHT_MIN_HP or more. False when HP stays low (no dishes),
    in which case the caller must not fight."""
    for _ in range(tries):
        if bar_fraction(dev.screenshot(), bar) * 100 >= FIGHT_MIN_HP:
            return True
        log.info("HP under %d%%: quick heal from the portrait", FIGHT_MIN_HP)
        dev.tap(*HUD_PORTRAIT)
        time.sleep(2)
        if det.detect().state != "player_profile":
            dev.tap(*nav.BACK_ARROW)
            time.sleep(2)
            dev.tap(*HUD_PORTRAIT)
            time.sleep(2)
        if det.detect().state == "player_profile":
            dev.tap(*QUICK_HEAL)
            time.sleep(2)
            dev.tap(360, 60)  # close the profile
            time.sleep(1.5)
    return bar_fraction(dev.screenshot(), bar) * 100 >= FIGHT_MIN_HP
