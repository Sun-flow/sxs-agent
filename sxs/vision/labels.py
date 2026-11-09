"""Find the boxes mae marked in the labeling UI (`python -m sxs labeler`) on a live frame.

    from sxs.vision import labels
    labels.roi("cart", "upgrade_button")          # (x, y, w, h) where it was drawn, or None
    labels.find(frame, "cart", "upgrade_button")  # (x, y, w, h, score) where its crop matches now, or None
    labels.tap_point(frame, "cart", "upgrade_button")  # centre of the match, for dev.tap

    python -m sxs see labels [FRAME ...]           # every template box found on the frames (default: live screenshot)

Boxes and crops come from sxs/core/labels.py (docs/screens/labels.json, resource/image/labels/). `find` searches
the drawn box grown by `pad` pixels on each side, so a button that shifts a little is still found; pad=None
searches the whole frame. Only boxes ticked "template" have a crop. Never taps.
"""

from __future__ import annotations

import json
import sys
from typing import Optional

import cv2
import numpy as np

from ..core import labels as store

THRESHOLD = 0.85
_CACHE: dict[str, np.ndarray] = {}


def roi(screen: str, box: str) -> Optional[tuple[int, int, int, int]]:
    b = store.find_box(screen, box)
    return (b["x"], b["y"], b["w"], b["h"]) if b else None


def _template(screen: str, box: str) -> Optional[np.ndarray]:
    path = store.CROPS / screen / f"{box}.png"
    key = str(path)
    if key not in _CACHE:
        img = cv2.imread(key) if path.exists() else None
        if img is None:
            return None
        _CACHE[key] = img
    return _CACHE[key]


def find(frame: np.ndarray, screen: str, box: str, pad: Optional[int] = 40,
         threshold: float = THRESHOLD) -> Optional[tuple[int, int, int, int, float]]:
    tpl = _template(screen, box)
    b = store.find_box(screen, box)
    if tpl is None or b is None:
        return None
    fh, fw = frame.shape[:2]
    if pad is None:
        x0, y0, x1, y1 = 0, 0, fw, fh
    else:
        x0, y0 = max(0, b["x"] - pad), max(0, b["y"] - pad)
        x1, y1 = min(fw, b["x"] + b["w"] + pad), min(fh, b["y"] + b["h"] + pad)
    area = frame[y0:y1, x0:x1]
    th, tw = tpl.shape[:2]
    if area.shape[0] < th or area.shape[1] < tw:
        return None
    res = cv2.matchTemplate(area, tpl, cv2.TM_CCOEFF_NORMED)
    _, score, _, (mx, my) = cv2.minMaxLoc(res)
    if score < threshold:
        return None
    return x0 + mx, y0 + my, tw, th, float(score)


def tap_point(frame: np.ndarray, screen: str, box: str, **kw) -> Optional[tuple[int, int]]:
    hit = find(frame, screen, box, **kw)
    return (hit[0] + hit[2] // 2, hit[1] + hit[3] // 2) if hit else None


def find_all(frame: np.ndarray, threshold: float = THRESHOLD) -> list[dict]:
    """Every template box found on the frame, best score first."""
    entries = json.loads(store.MANIFEST.read_text(encoding="utf-8"))["entries"] if store.MANIFEST.exists() else []
    hits = []
    for e in entries:
        hit = find(frame, e["screen"], e["box"], threshold=threshold)
        if hit:
            hits.append({"screen": e["screen"], "box": e["box"], "kind": e["kind"], "at": list(hit[:4]),
                         "score": round(hit[4], 3)})
    return sorted(hits, key=lambda h: -h["score"])


def main(argv: list[str]) -> int:
    if argv:
        frames = [(p, cv2.imread(p)) for p in argv]
    else:
        from ..core.device import Device

        frames = [("live", Device().screenshot())]
    for name, frame in frames:
        if frame is None:
            print(f"{name}: cannot read", file=sys.stderr)
            continue
        print(json.dumps({"frame": name, "found": find_all(frame)}))
    return 0
