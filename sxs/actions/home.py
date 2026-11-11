"""Find an object on the sideways-panning Home scene and tap it (R-126): shared by the gacha and relic steps.

Home keeps its camera, so fixed taps miss. `find_on_home` checks the current view, then pans with slow drags (the
Cart's sweep, `strengthen.HOME_SWIPE_*`) one way until the scene stops moving, then the other way. Every pan goes
through `Device.pan`, which falls back to adb when MaaFramework's swipe stops working (stuck point 2026-11-11).

Finders take a frame and return a tap point or None. `template_finder(name)` matches `resource/image/home/<name>`
and is None when that template hasn't been captured yet, so callers can report `no_template` instead of guessing.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable, Optional

import cv2
import numpy as np

from ..core.loop import progress
from ..core.nav import Navigator
from ..core.paths import RESOURCE

log = logging.getLogger("sxs.actions.home")

Finder = Callable[[np.ndarray], Optional[tuple[int, int]]]
HOME_IMAGES = RESOURCE / "image" / "home"
SCENE_ROI = (0, 130, 720, 870)  # x, y, w, h: below the HUD, above the tracker and chat
MATCH = 0.75
# Slow drags over the ground (R-126): finger right = the view moves left. Same as strengthen.HOME_SWIPE_*.
VIEW_LEFT, VIEW_RIGHT = (240, 820, 390, 820), (390, 820, 240, 820)
SWIPE_MS = 1000
STEPS = {"left": 12, "right": 20}  # at most this many pans each way; a pan that moves nothing ends that way early


def match_template(frame: np.ndarray, tpl: np.ndarray, roi=SCENE_ROI, threshold: float = MATCH):
    """Centre of the best match of `tpl` inside roi, or None under the threshold."""
    x, y, w, h = roi
    region = frame[y:y + h, x:x + w]
    if region.shape[0] < tpl.shape[0] or region.shape[1] < tpl.shape[1]:
        return None
    _, score, _, loc = cv2.minMaxLoc(cv2.matchTemplate(region, tpl, cv2.TM_CCOEFF_NORMED))
    if score < threshold:
        return None
    return x + loc[0] + tpl.shape[1] // 2, y + loc[1] + tpl.shape[0] // 2


def template_finder(name: str, offset=(0, 0), folder: Path = HOME_IMAGES) -> Optional[Finder]:
    """A finder for resource/image/home/<name>.png (tap point = match centre + offset), or None if not captured."""
    path = folder / f"{name}.png"
    tpl = cv2.imread(str(path)) if path.exists() else None
    if tpl is None:
        return None

    def find(frame):
        hit = match_template(frame, tpl)
        return (hit[0] + offset[0], hit[1] + offset[1]) if hit else None
    return find


def find_on_home(dev, det, find: Finder, steps=STEPS) -> Optional[tuple[int, int]]:
    """Go home and look for `find` in the current view, then pan left, then right. Returns the tap point or None."""
    Navigator(dev, det).go_home()
    hit = find(dev.screenshot())
    if hit:
        return hit
    n = 0
    for name, swipe in (("left", VIEW_LEFT), ("right", VIEW_RIGHT)):
        for _ in range(steps[name]):
            moved = dev.pan(*swipe, SWIPE_MS)
            n += 1
            progress(("home_pan", n))
            hit = find(dev.screenshot())
            if hit:
                log.info("found after %d pans", n)
                return hit
            if not moved:
                log.info("home scene stopped moving %s after %d pans: its end", name, n)
                break
    return None
