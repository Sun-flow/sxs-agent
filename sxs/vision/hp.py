"""HP bars: how full a bar is, from its colour. The filled part is bright and saturated (yellow-green at full HP),
the empty track dull (V ~110-120)."""

from __future__ import annotations

import numpy as np

HUD_HP_BAR = (116, 268, 52, 64)  # x0, x1, y0, y1: map HUD, the bar under our name (mae, 2026-11-04)
PREP_HP_BAR = (314, 406, 866, 876)  # battle prep: the bar under our character


def bar_fraction(frame: np.ndarray, bar=None) -> float:
    """Filled fraction (0..1) of an HP bar; default the HUD bar."""
    import cv2
    x0, x1, y0, y1 = bar or HUD_HP_BAR
    hsv = cv2.cvtColor(frame[y0:y1, x0:x1], cv2.COLOR_BGR2HSV)
    filled = (hsv[..., 1] > 100) & (hsv[..., 2] > 150)
    return float(filled.any(axis=0).mean())
