"""OCR readers: turn the detector's text lines in a region into strings and numbers.

All of them take `det` (a StateDetector), a region `[x, y, w, h]` and an optional frame (default: a fresh screenshot).
"""

from __future__ import annotations

import re
from typing import Optional

AMOUNT = re.compile(r"(\d+(?:\.\d+)?)\s*([KM]?)")
SCALE = {"": 1, "K": 1e3, "M": 1e6}


def read_line(det, roi, frame=None) -> str:
    """Every OCR line in the region joined with spaces, top to bottom."""
    return " ".join(t for t, _ in det.read_text(roi, frame))


def zoomed_lines(det, frame, box, scale: float = 3.0) -> list[str]:
    """OCR one small region after enlarging it onto a black canvas. Small white labels on dark badges ("+15",
    "Lv. 10", the top-bar amounts) are missed or misread at their real size and read cleanly enlarged.
    `frame` is required (a screenshot or saved image); `box` is [x, y, w, h]. Lines come back top to bottom."""
    import cv2
    import numpy as np

    x, y, w, h = box
    crop = frame[y:y + h, x:x + w]
    scale = max(1.0, min(scale, 680 / max(w, 1), 1180 / max(h, 1)))
    big = cv2.resize(crop, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    canvas = np.zeros((1280, 720, 3), np.uint8)
    canvas[50:50 + big.shape[0], 20:20 + big.shape[1]] = big
    return [t for t, _ in det.read_text([0, 0, 720, 1280], canvas)]


def int_in(text: str, pattern: str, ocr_fixes: bool = False) -> Optional[int]:
    """First capture group of `pattern` in `text` as an int. ocr_fixes: drop spaces and read O as 0 (counters such
    as "Attempts: O/2")."""
    if ocr_fixes:
        text = text.replace(" ", "").replace("O", "0")
    m = re.search(pattern, text or "")
    return int(m.group(1)) if m else None


def read_int(det, roi, pattern: str, frame=None, ocr_fixes: bool = False) -> Optional[int]:
    """int_in over each line of the region; the first line that matches wins."""
    for t, _ in det.read_text(roi, frame):
        n = int_in(t, pattern, ocr_fixes)
        if n is not None:
            return n
    return None


def amount_in(text: str, anchored: bool = False) -> Optional[float]:
    """A number with an optional K/M suffix ("16.9K" -> 16900). anchored: it must end the text (a leading icon
    often OCRs as a stray character)."""
    text = (text or "").replace(",", "")
    m = re.search(AMOUNT.pattern + ("$" if anchored else ""), text)
    return float(m.group(1)) * SCALE[m.group(2)] if m else None


def read_amount(det, roi, frame=None, anchored: bool = False) -> Optional[float]:
    for t, _ in det.read_text(roi, frame):
        n = amount_in(t, anchored)
        if n is not None:
            return n
    return None


def power_k(text: str) -> Optional[float]:
    """Power as shown on the HUD and power gates, in K: "16.9K" -> 16.9. None without a K."""
    m = re.search(r"(\d+(?:\.\d+)?)\s*K", (text or "").replace(",", "."))
    return float(m.group(1)) if m else None


def read_fraction(det, roi, frame=None, whole_line: bool = False) -> Optional[tuple[int, int]]:
    """An "a/b" counter (stamina "171/300", a tracker "2/20"). whole_line: the line must be only the counter."""
    for t, _ in det.read_text(roi, frame):
        t = t.strip()
        m = re.fullmatch(r"(\d+)\s*/\s*(\d+)", t) if whole_line else re.search(r"(\d+)\s*/\s*(\d+)", t)
        if m:
            return int(m.group(1)), int(m.group(2))
    return None


def has_text(det, roi, pattern: str, frame=None, whole: bool = False) -> bool:
    """Any line in the region matches `pattern` (whole: the whole stripped line)."""
    for t, _ in det.read_text(roi, frame):
        if (re.fullmatch(pattern, t.strip()) if whole else re.search(pattern, t)):
            return True
    return False


def boxes_of(det, roi, pattern: str, frame=None, whole: bool = True) -> list[list[int]]:
    """Boxes of lines matching `pattern` (whole line by default), top to bottom: buttons found by their caption."""
    return [b for t, b in det.read_text(roi, frame)
            if (re.fullmatch(pattern, t.strip()) if whole else re.search(pattern, t))]
