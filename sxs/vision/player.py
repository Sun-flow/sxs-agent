"""Find our own character on the island map: by its name label, which sits just under its feet."""

from __future__ import annotations

from typing import Optional

from ..core.ui import PLAYER_NAME

LABEL_ROI = [0, 130, 720, 1100]  # down to the chat strip: after an area-map walk the character can stand low on screen


def player_label(det, frame, roi=LABEL_ROI) -> Optional[list[int]]:
    """Box of the "gromb2" label, or None."""
    me = [b for t, b in det.read_text(roi, frame) if PLAYER_NAME in t]
    return me[0] if me else None


def player_on_screen(det, frame, roi=LABEL_ROI, feet_dy: int = 40) -> Optional[tuple[int, int]]:
    """Screen point of our character (just above its name label), or None."""
    box = player_label(det, frame, roi)
    if box is None:
        return None
    x, y, w, h = box
    return x + w // 2, y - feet_dy
