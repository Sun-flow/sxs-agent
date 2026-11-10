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


SLIDER = (660, 770, 60, 360)  # x, y, w, h of the zoom slider and its +/- (not objects)
DOT_FILL = 0.5  # dots are round blobs: pixels / bounding box at least this; text glyphs are thinner
DOT_ASPECT = 1.8  # and about as wide as tall
BUILDING_MERGE = 40  # px: yellow pieces this close are one structure icon
LABEL_MARGIN = 0.75  # an object is another zone's only if that zone's label is under 0.75x as far as ours


def _text_rows(blobs: list[tuple[int, int, int, int]]) -> set[int]:
    """Indexes of blobs sitting in a row of 4+ close neighbours at the same height: text ("20.4K", "Exploration:
    0%" drawn green for zones over our power; seen 2026-11-09 as a dozen "items")."""
    out = set()
    for i, (x, y, w, h) in enumerate(blobs):
        row = [j for j, (x2, y2, w2, h2) in enumerate(blobs) if abs((y2 + h2 / 2) - (y + h / 2)) <= 4
               and abs(x2 - x) <= 60]
        if len(row) >= 4:
            out.update(row)
    return out


BLUE_BANG_PX = (60, 400)  # pixel count of the blue disc of a blue "!" badge on the area map
STATUE_BELOW = 14
SAFE_TAP_MAX_Y = 1080  # area-map taps below this can land on the back arrow or kingdom buttons  # the statue icon sits under its blue "!" badge


def blue_badges(frame: np.ndarray) -> list[tuple[int, int]]:
    """mae, 2026-11-10: a new interactable, statues, shows on the area map as a blue disc with a white "!" (Jungle
    Camp's last 7%). Returns tap points (just under each badge, on the statue icon). Portals are blue too but have no
    white mark inside and are teal swirls, not discs."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    h, s, v = hsv[..., 0].astype(int), hsv[..., 1].astype(int), hsv[..., 2].astype(int)
    blue = ((h >= 96) & (h <= 112) & (s > 110) & (v > 120)).astype(np.uint8)  # disc: H 99-102, S 130-177, V 129-226
    white = (s < 30) & (v > 175)  # the "!": S 1-27, V 180-233
    x0, y0, w, hh = MAP_AREA
    lx, ly, lw, lh = LEGEND
    m = np.zeros(blue.shape, np.uint8)
    m[y0:y0 + hh, x0:x0 + w] = blue[y0:y0 + hh, x0:x0 + w]
    m[ly:ly + lh, lx:lx + lw] = 0
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    n, _, stats, cents = cv2.connectedComponentsWithStats(m)
    out = []
    for i in range(1, n):
        bx, by, bw, bh, area = stats[i]
        if not (BLUE_BANG_PX[0] <= area <= BLUE_BANG_PX[1]) or max(bw, bh) > 1.5 * max(1, min(bw, bh)):
            continue
        if area < 0.3 * bw * bh:  # 0.35 for a small badge at the survey zoom (white "!" fills the rest)
            continue  # not a filled disc (a portal swirl)
        if white[by:by + bh, bx:bx + bw].sum() < 6:
            continue  # no white "!" inside
        x, y = int(cents[i][0]), int(cents[i][1]) + STATUE_BELOW
        if y > SAFE_TAP_MAX_Y:
            continue  # too close to the back arrow and kingdom buttons to tap (live 2026-11-10): pan first
        out.append((x, y))
    return out


def objects(frame: np.ndarray) -> list[tuple[str, tuple[int, int]]]:
    """(kind, centre) for each object blob on the area map. Live 2026-11-09: green and orange text, the red "!" on
    structure icons and the zoom slider read as dots, so blobs must be round, not in a text row, not on a badge."""
    from .badges import SMALL_MIN_AREA, find_badges
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    x0, y0, w, h = MAP_AREA
    lx, ly, lw, lh = LEGEND
    sx, sy, sw, sh = SLIDER
    badges = find_badges(frame, min_area=SMALL_MIN_AREA)
    out = []
    for kind, mask in _masks(hsv).items():
        m = np.zeros(mask.shape, np.uint8)
        m[y0:y0 + h, x0:x0 + w] = mask[y0:y0 + h, x0:x0 + w]
        m[ly:ly + lh, lx:lx + lw] = 0
        m[sy:sy + sh, sx:sx + sw] = 0
        n, _, stats, cents = cv2.connectedComponentsWithStats(m)
        lo, hi = SIZES[kind]
        keep = [i for i in range(1, n) if lo <= stats[i, 4] <= hi]
        if kind in ("item", "monster"):
            boxes = [tuple(int(v) for v in stats[i, :4]) for i in keep]
            text = _text_rows(boxes)
            keep = [i for k, i in enumerate(keep) if k not in text
                    and stats[i, 4] >= DOT_FILL * stats[i, 2] * stats[i, 3]
                    and max(stats[i, 2], stats[i, 3]) <= DOT_ASPECT * max(1, min(stats[i, 2], stats[i, 3]))]
        if kind == "monster":  # a badge's red is not a monster
            keep = [i for i in keep if all(abs(cents[i][0] - bx) + abs(cents[i][1] - by) > 14 for bx, by in badges)]
        if kind == "building":
            # Yellow town names ("Drasilgard") are text rows; one structure icon splits into several yellow pieces:
            # merge pieces within BUILDING_MERGE px into one point.
            boxes = [tuple(int(v) for v in stats[i, :4]) for i in keep]
            text = _text_rows(boxes)
            pts: list[tuple[int, int]] = []
            for k, i in enumerate(keep):
                if k in text:
                    continue
                p = (int(cents[i][0]), int(cents[i][1]))
                if all(abs(p[0] - q[0]) + abs(p[1] - q[1]) > BUILDING_MERGE for q in pts):
                    pts.append(p)
            out += [(kind, p) for p in pts]
            continue
        out += [(kind, (int(cents[i][0]), int(cents[i][1]))) for i in keep]
    out += [("statue", p) for p in blue_badges(frame)]
    # Orange bits of a yellow structure icon aren't monsters.
    blds = [p for k, p in out if k == "building"]
    return [(k, p) for k, p in out
            if k != "monster" or all(abs(p[0] - q[0]) + abs(p[1] - q[1]) > BUILDING_MERGE for q in blds)]


def crosses_border(lines: np.ndarray, a: tuple[int, int], b: tuple[int, int], near: int = 3) -> bool:
    """True when the straight line a -> b on the area map passes within `near` px of a dotted zone border."""
    n = max(abs(b[0] - a[0]), abs(b[1] - a[1]), 1)
    h, w = lines.shape
    for i in range(n + 1):
        x, y = round(a[0] + (b[0] - a[0]) * i / n), round(a[1] + (b[1] - a[1]) * i / n)
        if lines[max(0, y - near):min(h, y + near + 1), max(0, x - near):min(w, x + near + 1)].any():
            return True
    return False


def nearest(frame: np.ndarray, kinds=("item", "monster", "building"), max_px: int = 260,
            skip=(), same_zone: bool = True, labels: Optional[dict] = None,
            home: Optional[str] = None) -> Optional[tuple[str, tuple[int, int]]]:
    """The object of `kinds` nearest our white dot (within max_px), or None. same_zone (R-132, live 2026-11-09: a
    big-map walk to the nearest dot from Verdantglade V ended in Zephyr Vale): skip objects whose straight line from
    us crosses a dotted zone border, and, given the map's zone labels {name: point} and our zone's name, objects
    whose nearest label is another zone's (labels sit in their zone's middle)."""
    objs = objects(frame)
    me = [p for k, p in objs if k == "player"]
    if not me:
        return None
    px, py = me[0]
    # Not our own dot: its glow reads as an object right on top of us (seen 2026-11-05: "centring on (360, 640)",
    # the player, over and over).
    cands = [(k, p) for k, p in objs if k in kinds and p not in skip
             and MIN_PX ** 2 < (p[0] - px) ** 2 + (p[1] - py) ** 2 <= max_px ** 2]
    if same_zone and cands:
        from .minimap import dotted_lines
        lines = dotted_lines(frame)
        lx, ly, lw, lh = LEGEND
        lines[ly:ly + lh, lx:lx + lw] = 0
        cands = [(k, p) for k, p in cands if not crosses_border(lines, (px, py), p)]
        if callable(labels) and home and cands:
            labels = labels()  # read the labels (OCR, ~3 s) only when there is a candidate to check
        if labels and home:
            from ..actions.goto import close_name, same_area as _same

            def same_area(a, b):  # OCR clips labels ("Jungle Car" for Jungle Camp, live 2026-11-10)
                return _same(a, b) or close_name(a, b) or (len(a) >= 6 and b.lower().startswith(a.lower()[:-1]))
            if not any(same_area(t, home) for t in labels):
                # Our zone's label wasn't read: nothing can be told apart, so pick nothing rather than anything
                # (the same day a walk "to the nearest object" kept ending in Drasilgard).
                return None
            if True:
                def d(t, p):
                    return ((labels[t][0] - p[0]) ** 2 + (labels[t][1] - p[1]) ** 2) ** 0.5

                def ours(p):
                    # Labels sit mid-zone, so nearest-label is only a rough zone test: drop an object only when
                    # another zone's label is clearly nearer (LABEL_MARGIN) than ours.
                    mine = min(d(t, p) for t in labels if same_area(t, home))
                    other = min((d(t, p) for t in labels if not same_area(t, home)), default=1e9)
                    return other >= LABEL_MARGIN * mine
                cands = [(k, p) for k, p in cands if ours(p)]
    # A blue-"!" statue first (mae, 2026-11-10: the interactable that finishes a zone), then the nearest object.
    return min(cands, key=lambda kp: (kp[0] != "statue", (kp[1][0] - px) ** 2 + (kp[1][1] - py) ** 2)) if cands else None
