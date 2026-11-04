"""Find the game's red "!" notification badges on a frame (no templates, no model calls).

A badge is a small filled red disc (about 22 to 30 px across in the 720x1280 frame) with a white "!" in it. The game
puts one on any button, tab or item that has something to claim or upgrade (R-063, R-080). Other red art (enemy
HP bars, red UI chrome) is ruled out by size, roundness and the white mark inside.

    python -m sxs.badges [frame.png]     # list badges on a frame (default: a fresh screenshot)
"""

from __future__ import annotations

import sys

import cv2
import numpy as np

MIN_AREA, MAX_AREA = 180, 1100  # red pixel count of one disc
MAX_ASPECT = 1.35


def find_badges(frame: np.ndarray, roi=None) -> list[tuple[int, int]]:
    """Centres (x, y) of red "!" badges, top to bottom then left to right. roi = [x, y, w, h] limits the search."""
    ox = oy = 0
    if roi:
        x, y, w, h = roi
        frame, ox, oy = frame[y:y + h, x:x + w], x, y
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    red = (((h >= 165) | (h <= 6)) & (s > 110) & (v > 150)).astype(np.uint8)
    white = ((s < 60) & (v > 220)).astype(np.uint8)
    # The red ring around the "!" is one blob (the mark only dents it); the white mark is checked inside its box.
    n, _, stats, cents = cv2.connectedComponentsWithStats(red, 8)
    out = []
    for i in range(1, n):
        bx, by, bw, bh, area = stats[i]
        if not (14 <= bw <= 40 and 14 <= bh <= 40):
            continue
        if max(bw, bh) / max(1, min(bw, bh)) > MAX_ASPECT:
            continue
        r = int(red[by:by + bh, bx:bx + bw].sum())
        if not (MIN_AREA <= r <= MAX_AREA) or r < 0.45 * bw * bh:
            continue
        # White inside the disc only (the box corners show the background): the "!" is a thin upright mark, not a
        # wider white glyph such as a class icon's sword.
        yy, xx = np.mgrid[0:bh, 0:bw]
        inside = (xx - bw / 2 + 0.5) ** 2 + (yy - bh / 2 + 0.5) ** 2 <= (0.42 * min(bw, bh)) ** 2
        ys, xs = np.nonzero(white[by:by + bh, bx:bx + bw] & inside)
        if len(xs) < 8 or xs.max() - xs.min() + 1 > 0.4 * bw or ys.max() - ys.min() + 1 < 0.45 * bh:
            continue
        out.append((int(cents[i][0]) + ox, int(cents[i][1]) + oy))
    return sorted(out, key=lambda p: (p[1] // 20, p[0]))


def near(badges: list[tuple[int, int]], xy, radius: int = 70) -> bool:
    """True if a badge sits within radius of xy (badges ride on the upper right corner of their button)."""
    return any(abs(bx - xy[0]) <= radius and abs(by - xy[1]) <= radius for bx, by in badges)


def main() -> int:
    if len(sys.argv) > 1:
        frame = cv2.imread(sys.argv[1])
    else:
        from .device import Device
        frame = Device().screenshot()
    for b in find_badges(frame):
        print(b)
    return 0


if __name__ == "__main__":
    sys.exit(main())
