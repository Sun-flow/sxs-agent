"""Find the game's red "!" notification badges on a frame (no templates, no model calls).

A badge is a small filled red disc (about 22 to 30 px across in the 720x1280 frame) with a white "!" in it. The game
puts one on any button, tab or item that has something to claim or upgrade (R-063, R-080). Other red art (enemy
HP bars, red UI chrome) is ruled out by size, roundness and the white mark inside.

    python -m sxs see badges [frame.png] # list badges on a frame (default: a fresh screenshot)
"""

from __future__ import annotations

import sys

import cv2
import numpy as np

MIN_AREA, MAX_AREA = 180, 1100  # red pixel count of one disc
SMALL_MIN_AREA = 120  # area-map badges (statues, ore) are smaller
MAX_ASPECT = 1.5  # 1.35 dropped a pip merged with the chest slot's rim (38x26, live 2026-11-09)


def find_badges(frame: np.ndarray, roi=None, min_area: int = MIN_AREA) -> list[tuple[int, int]]:
    """Centres (x, y) of red "!" badges, top to bottom then left to right. roi = [x, y, w, h] limits the search.
    min_area: the area map's badges are smaller (about 17 px, 175 red pixels): pass SMALL_MIN_AREA there."""
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
        if not (min_area <= r <= MAX_AREA) or r < 0.45 * bw * bh:
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


def find_tan_bangs(frame: np.ndarray, region=None) -> list[tuple[int, int]]:
    """Centres of tan "!" badges: a Lost Statue's ready mark on the area map is drawn tan, not red (live 2026-11-11,
    run 35, docs/screens/world/world_area_map_xii_statue_ready.png; Bubble Lake's was red). A thin upright white
    mark with a ring of tan (HSV ~15/99/167) round it. region: [x, y, w, h] to search, else the whole frame."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    h, s, v = (hsv[..., i].astype(int) for i in range(3))
    inside = np.zeros(h.shape, bool)
    if region:
        x, y, w, hh = region
        inside[y:y + hh, x:x + w] = True
    else:
        inside[:] = True
    tan = (h >= 6) & (h <= 22) & (s >= 70) & (v >= 100) & inside
    white = ((s < 70) & (v > 185) & inside).astype(np.uint8)
    n, _, stats, cents = cv2.connectedComponentsWithStats(white)
    yy, xx = np.mgrid[-12:13, -12:13]
    d = np.hypot(xx, yy)
    ring = (d >= 7) & (d <= 10)
    H, W = h.shape
    out = []
    for i in range(1, n):
        _, _, bw, bh, _ = stats[i]
        if not (7 <= bh <= 20 and bw <= 7 and bh >= 2 * bw):
            continue
        cx, cy = int(cents[i][0]), int(cents[i][1])
        if 12 <= cx < W - 12 and 12 <= cy < H - 12 and tan[cy - 12:cy + 13, cx - 12:cx + 13][ring].mean() >= 0.6:
            out.append((cx, cy))
    return out


def find_up_pips(frame: np.ndarray, roi=None) -> list[tuple[int, int]]:
    """Centres of the small light-blue discs with a white up arrow that sit where a red "!" would (mae, 2026-11-09):
    on a gear slot it means the piece can be enhanced (the red "!" means a better piece to swap in, R-088); skill
    icons show them too (R-104). About 22 px across: blue H 85-108, S 45-120 (the sky behind is paler, S 20-35), with
    a white arrow inside. Other light-blue art matches as well, so look only where a pip can sit (near_any)."""
    ox = oy = 0
    if roi:
        x, y, w, h = roi
        frame, ox, oy = frame[y:y + h, x:x + w], x, y
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    # Live 2026-11-09 on the Character screen the discs read H 98-114, S up to ~175 (bluer than the first crop): the
    # old S <= 120 cut found none and the Upgrade Loop skipped four enhanceable slots.
    blue = ((h >= 85) & (h <= 116) & (s >= 45) & (s <= 190) & (v >= 140)).astype(np.uint8)
    blue = cv2.morphologyEx(blue, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))  # the arrow splits the disc
    white = ((s < 30) & (v > 230)).astype(np.uint8)
    n, _, stats, cents = cv2.connectedComponentsWithStats(blue, 8)
    out = []
    for i in range(1, n):
        bx, by, bw, bh, area = stats[i]
        # Up to 40 px: next to a slot's blue rim the disc merges with it (chest slot, live 2026-11-09: 38x26).
        if not (14 <= bw <= 40 and 14 <= bh <= 40) or max(bw, bh) / max(1, min(bw, bh)) > MAX_ASPECT:
            continue
        if area < 0.4 * bw * bh or int(white[by:by + bh, bx:bx + bw].sum()) < 30:
            continue
        out.append((int(cents[i][0]) + ox, int(cents[i][1]) + oy))
    return sorted(out, key=lambda p: (p[1] // 20, p[0]))


def near_any(badges: list[tuple[int, int]], xy, radius: int = 70) -> bool:
    """True if a badge sits within radius of xy (badges ride on the upper right corner of their button)."""
    return any(abs(bx - xy[0]) <= radius and abs(by - xy[1]) <= radius for bx, by in badges)


def main(argv: list[str]) -> int:
    if argv:
        frame = cv2.imread(argv[0])
    else:
        from ..core.device import Device
        frame = Device().screenshot()
    for b in find_badges(frame):
        print("badge", b)
    for b in find_up_pips(frame):
        print("up pip", b)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
