"""The quest tracker: the panel on home (bottom left) and the tracking icon. Reading only, nothing taps."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Optional

import cv2
import numpy as np

if TYPE_CHECKING:
    from ..core.state import StateDetector

TRACKING_TOGGLE = (290, 1012)
TRACKER_ROI = [0, 860, 330, 180]  # quest tracker panel on home


def tracking_toggle(det: StateDetector, frame: np.ndarray) -> tuple[int, int]:
    """Where the tracking icon is on the panel (it shifts with the title's length)."""
    icon = det.find("Explore.TrackingIcon", frame)
    if icon is None:
        return TRACKING_TOGGLE
    x, y, w, h = icon.box
    return x + w // 2, y + h // 2


def tracking_on(frame: np.ndarray, at: tuple[int, int] = TRACKING_TOGGLE) -> bool:
    """The target icon on the tracker panel is bright yellow when tracking is on, dim grey when off."""
    x, y = at
    patch = cv2.cvtColor(frame[y - 12:y + 12, x - 12:x + 12], cv2.COLOR_BGR2HSV)
    return float(np.percentile(patch[:, :, 2], 90)) > 150


def read_tracker(det: StateDetector) -> Optional[dict]:
    """Quest tracker panel on home (bottom left). Its height changes when it shows rewards, so read it by OCR.
    Returns title, progress ("a/b"), done flag and the point to tap (the title), or None if no panel."""
    # The home scene's own labels (e.g. the stone's "Class to Unlock") can sit inside this region; drop them.
    lines = [(t, b) for t, b in det.read_text(TRACKER_ROI) if not re.search(r"Un\W?l\W?[oa]c?k|to ?Un", t)]
    prog = next(((t, b) for t, b in lines if re.search(r"\d+/\d+", t)), None)
    if prog is None:
        if not lines:
            return None
        # Quests like "Reach Apprentice I" have no counter; tapping the title claims or opens them.
        title, (x, y, w, h) = lines[0]
        return {"title": title, "progress": "", "done": None, "tap": (x + w // 2, y + h // 2)}
    above = [(t, b) for t, b in lines if b[1] < prog[1][1]]
    title, box = above[-1] if above else prog
    a, b = map(int, re.search(r"(\d+)/(\d+)", prog[0]).groups())
    return {"title": title, "progress": f"{a}/{b}", "done": a >= b, "tap": (box[0] + box[2] // 2, box[1] + box[3] // 2)}


def progress_signal(text: Optional[str]) -> Optional[str]:
    """What counts as quest progress on the map tracker: its n/m counter, or else its goal text with OCR noise
    (spaces, I/l/1 confusions) squeezed out, so a counterless quest still shows progress when its goal changes."""
    if not text:
        return None
    m = re.search(r"\d+/\d+", text)
    if m:
        return m.group(0)
    return re.sub(r"[\sIl1|]", "", text).lower()
