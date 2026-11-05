"""Find our own character on the island map: by its name label, which sits just under its feet, or (when the
label isn't drawn or OCR misses it) by its head: white hair and brown horns, matched both ways round."""

from __future__ import annotations

from typing import Optional

import cv2
import numpy as np

from ..core.paths import RESOURCE
from ..core.ui import PLAYER_NAME

SPRITE = RESOURCE / "image" / "explore" / "player_sprite.png"  # gromb2's head, facing left (Verdantglade III)
SPRITE_MASK = RESOURCE / "image" / "explore" / "player_sprite_mask.png"  # hair and horns only, not the grass
SPRITE_MIN = 0.75  # the other way round scored 0.88, other screens at most 0.55 (2026-11-05)
SPRITE_TO_POINT = 55  # head centre to the point player_on_screen returns (just above the name label)
_sprites: list = []

LABEL_ROI = [0, 130, 720, 1100]  # down to the chat strip: after an area-map walk the character can stand low on screen


def player_label(det, frame, roi=LABEL_ROI) -> Optional[list[int]]:
    """Box of the "gromb2" label, or None."""
    me = [b for t, b in det.read_text(roi, frame) if PLAYER_NAME in t]
    return me[0] if me else None


def player_on_screen(det, frame, roi=LABEL_ROI, feet_dy: int = 40) -> Optional[tuple[int, int]]:
    """Screen point of our character (just above its name label), or None."""
    box = player_label(det, frame, roi)
    if box is None:
        return player_sprite(frame, roi)
    x, y, w, h = box
    return x + w // 2, y - feet_dy


def player_sprite(frame, roi=LABEL_ROI) -> Optional[tuple[int, int]]:
    """Our character by its head (seen 2026-11-05: standing still in Verdantglade III, no name label was drawn and
    the fog walk had no player to plan from). Same point convention as player_on_screen."""
    if not _sprites:
        tpl, mask = cv2.imread(str(SPRITE)), cv2.imread(str(SPRITE_MASK), cv2.IMREAD_GRAYSCALE)
        if tpl is None or mask is None:
            return None
        _sprites.extend([(tpl, mask), (cv2.flip(tpl, 1), cv2.flip(mask, 1))])
    x0, y0, w, h = roi
    region = frame[y0:y0 + h, x0:x0 + w]
    best = None
    for tpl, mask in _sprites:
        res = cv2.matchTemplate(region, tpl, cv2.TM_CCOEFF_NORMED, mask=mask)
        res[~np.isfinite(res)] = 0
        _, score, _, (mx, my) = cv2.minMaxLoc(res)
        if score >= SPRITE_MIN and (best is None or score > best[0]):
            best = (score, x0 + mx + tpl.shape[1] // 2, y0 + my + tpl.shape[0] // 2 + SPRITE_TO_POINT)
    return (best[1], best[2]) if best else None
