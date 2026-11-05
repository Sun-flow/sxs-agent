"""Objects on the area map (tap the minimap): green pickups, orange monsters, gold structures, and our white dot.

mae, 2026-11-05: to reach a dot or a structure, open the big map, tap the target (the camera centres on it), close
the map and tap the element, now in the middle of the screen. `objects()` finds the targets; the walk itself is
`sxs.actions.goto.go_to(dev, det, pick)`. Colours are the minimap's (sxs.vision.minimap). No model calls.
"""

from __future__ import annotations

from typing import Optional

import cv2
import numpy as np

LEGEND = (530, 30, 190, 240)  # x, y, w, h of the legend box top right (its icons are not targets)
MAP_AREA = (0, 90, 720, 1060)  # below the title, above the kingdom buttons
MIN_PX = 25  # objects closer than this to our white dot are our own marker
SIZES = {"item": (15, 120), "monster": (15, 200), "building": (40, 400), "player": (30, 200)}


def _masks(hsv: np.ndarray) -> dict:
    h, s, v = (hsv[..., i].astype(int) for i in range(3))
    return {
        "item": (h >= 38) & (h <= 80) & (s > 110) & (v > 180),
        "monster": (h <= 22) & (s > 100) & (v > 150),
        "building": (h >= 23) & (h <= 34) & (s > 140) & (v > 170),
        "player": (s < 30) & (v > 235),
    }


def objects(frame: np.ndarray) -> list[tuple[str, tuple[int, int]]]:
    """(kind, centre) for each object blob on the area map."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    x0, y0, w, h = MAP_AREA
    lx, ly, lw, lh = LEGEND
    out = []
    for kind, mask in _masks(hsv).items():
        m = np.zeros(mask.shape, np.uint8)
        m[y0:y0 + h, x0:x0 + w] = mask[y0:y0 + h, x0:x0 + w]
        m[ly:ly + lh, lx:lx + lw] = 0
        n, _, stats, cents = cv2.connectedComponentsWithStats(m)
        lo, hi = SIZES[kind]
        out += [(kind, (int(cents[i][0]), int(cents[i][1]))) for i in range(1, n) if lo <= stats[i, 4] <= hi]
    return out


def nearest(frame: np.ndarray, kinds=("item", "monster", "building"), max_px: int = 260,
            skip=()) -> Optional[tuple[str, tuple[int, int]]]:
    """The object of `kinds` nearest our white dot (within max_px), or None."""
    objs = objects(frame)
    me = [p for k, p in objs if k == "player"]
    if not me:
        return None
    px, py = me[0]
    # Not our own dot: its glow reads as an object right on top of us (seen 2026-11-05: "centring on (360, 640)",
    # the player, over and over).
    cands = [(k, p) for k, p in objs if k in kinds and p not in skip
             and MIN_PX ** 2 < (p[0] - px) ** 2 + (p[1] - py) ** 2 <= max_px ** 2]
    return min(cands, key=lambda kp: (kp[1][0] - px) ** 2 + (kp[1][1] - py) ** 2) if cands else None
