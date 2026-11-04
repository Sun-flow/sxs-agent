"""Read the minimap into a grid of tiles: what is walkable, explored, a wall, unspotted, or a point of interest.

    python -m sxs see minimap [FRAME.png] # classify a frame (or a live screenshot), write captures/minimap.png

The minimap (top right of the island map) is centred on the player (white dot) and draws the game's real tiles,
about 8 px each. Classes, from mae's legend (2026-11-03) and measured colours:

    walk_explored    light green
    walk_unexplored  light green under a shadow (darker, less saturated)
    wall_explored    mid green
    wall_unexplored  dark green
    unspotted        no colour, a faint cross pattern: unknown until you get near
    item             bright green dot (pickup)
    building         gold icon: an interactable building (dungeons, mines, ...; mae, 2026-11-04)
    monster          orange/red dot
    icon             white (player, statues, ...)

Colour thresholds are HSV (OpenCV ranges). They were measured in Verdantglade II and may need a second look in
other kingdoms.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass

import cv2
import numpy as np

CENTER = (616, 177)  # minimap centre = player position, in the 720x1280 frame
RADIUS = 86  # usable radius inside the ring
TILE = 8  # px per tile on the minimap

CLASSES = ["unspotted", "wall_unexplored", "wall_explored", "walk_unexplored", "walk_explored", "item", "building", "monster", "icon"]
COLOURS = {  # BGR for the debug image
    "unspotted": (30, 30, 30), "wall_unexplored": (20, 60, 20), "wall_explored": (40, 120, 40),
    "walk_unexplored": (90, 150, 200), "walk_explored": (150, 230, 150), "item": (0, 255, 0),
    "building": (0, 200, 255),
    "monster": (0, 80, 255), "icon": (255, 255, 255), "": (0, 0, 0),
}
WALKABLE = {"walk_explored", "walk_unexplored", "item", "building", "monster", "icon"}


def is_item(h: int, s: int, v: int) -> bool:
    """Pickup dots are bright green: S 150+ in Verdantglade II, but only ~128 in Highland Woods, so S > 110."""
    if 38 <= h <= 80 and s > 110 and v > 180:
        return True
    # Under the unexplored shadow they turn pale: HSV ~39/81/213 (Damp Woods, 2026-11-04). Walkable ground
    # is never that bright (V <= ~150).
    return 36 <= h <= 46 and s >= 65 and v >= 195


def is_building(h: int, s: int, v: int) -> bool:
    """Gold building icons (Moonveil Woods: HSV ~26/170/207); monsters are redder (H <= 22), pickups greener."""
    return 23 <= h <= 34 and s > 140 and v > 170


def classify_pixel(h: int, s: int, v: int) -> str:
    if s < 35 and v > 150:
        return "icon"
    if s < 35:
        return "unspotted"
    if 5 <= h <= 22 and s > 100 and v > 150:  # S ~116 under the shadow (Damp Woods); also a shaded gold building
        return "monster"
    if is_item(h, s, v):
        return "item"
    if s < 95 and v >= 115:
        return "walk_explored"
    if s < 95 and v >= 62:
        return "walk_unexplored"
    if v >= 85:
        return "wall_explored"
    return "wall_unexplored"


@dataclass
class Minimap:
    grid: list[list[str]]  # [row][col], "" outside the circle
    centre: tuple[int, int]  # (row, col) of the player

    def tiles(self, kind: str) -> list[tuple[int, int]]:
        return [(r, c) for r, row in enumerate(self.grid) for c, k in enumerate(row) if k == kind]


def read(frame: np.ndarray) -> Minimap:
    cx, cy = CENTER
    n = (RADIUS * 2) // TILE
    half = n // 2
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    grid = []
    for r in range(n):
        row = []
        for c in range(n):
            x, y = cx + (c - half) * TILE, cy + (r - half) * TILE
            if (x - cx) ** 2 + (y - cy) ** 2 > (RADIUS - 1.5 * TILE) ** 2:  # the ring darkens the rim
                row.append("")
                continue
            patch = hsv[y - 2:y + 3, x - 2:x + 3].reshape(-1, 3)
            # Pickup dots are smaller than a tile, so a median can wash them out: a few dot pixels make it an item.
            if sum(is_item(int(a), int(b), int(c)) for a, b, c in patch) >= 5:
                row.append("item")
                continue
            if sum(is_building(int(a), int(b), int(c)) for a, b, c in patch) >= 5:
                row.append("building")
                continue
            h, s, v = np.median(patch, axis=0).astype(int)
            row.append(classify_pixel(int(h), int(s), int(v)))
        grid.append(row)
    return Minimap(grid, (half, half))


def render(mm: Minimap, scale: int = 12) -> np.ndarray:
    n = len(mm.grid)
    img = np.zeros((n * scale, n * scale, 3), np.uint8)
    for r, row in enumerate(mm.grid):
        for c, k in enumerate(row):
            cv2.rectangle(img, (c * scale, r * scale), ((c + 1) * scale - 1, (r + 1) * scale - 1), COLOURS[k], -1)
    r, c = mm.centre
    cv2.circle(img, (c * scale + scale // 2, r * scale + scale // 2), scale // 2, (0, 0, 255), 2)
    return img


def main(argv: list[str]) -> int:
    if argv:
        frame = cv2.imread(argv[0])
    else:
        from ..core.device import Device
        frame = Device().screenshot()
    mm = read(frame)
    from ..core.paths import CAPTURES
    out = CAPTURES / "minimap.png"
    out.parent.mkdir(exist_ok=True)
    cv2.imwrite(str(out), np.hstack([cv2.resize(frame[CENTER[1] - RADIUS:CENTER[1] + RADIUS,
                                                       CENTER[0] - RADIUS:CENTER[0] + RADIUS],
                                                 (len(mm.grid) * 12,) * 2, interpolation=cv2.INTER_NEAREST),
                                      render(mm)]))
    counts = {k: sum(row.count(k) for row in mm.grid) for k in CLASSES}
    print(counts)
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))


# --- path planning -------------------------------------------------------------------------------------------

SCREEN_TILE = 104  # px per game tile on the island map at the default zoom (grid lines are this far apart)
GOALS = ("item", "monster", "walk_unexplored")  # what free exploration heads for (nearest first); orange monster
# dots are fought (mae, 2026-11-04: "orange minimap icons are monsters and should be fought")


def path_to_nearest(mm: Minimap, goals=GOALS, skip=frozenset()) -> list[tuple[int, int]]:
    """Breadth-first path over walkable tiles from the player to the nearest goal tile (unexplored walkable ground
    or a pickup). Goal tiles themselves count as walkable. Empty if nothing reachable."""
    from collections import deque

    n = len(mm.grid)
    start = mm.centre
    prev = {start: None}
    q = deque([start])
    while q:
        cur = q.popleft()
        r, c = cur
        if cur != start and mm.grid[r][c] in goals and cur not in skip:
            path = []
            while cur is not None:
                path.append(cur)
                cur = prev[cur]
            return path[::-1]
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n and (nr, nc) not in prev and mm.grid[nr][nc] in WALKABLE:
                prev[(nr, nc)] = cur
                q.append((nr, nc))
    return []


def world_tile(mm: Minimap, tile: tuple[int, int], player_xy: tuple[int, int]) -> tuple[int, int]:
    """Map coordinates of a minimap tile, from the player's coordinates (x grows east, y grows north)."""
    (pr, pc), (r, c) = mm.centre, tile
    return player_xy[0] + (c - pc), player_xy[1] - (r - pr)


def screen_point(player_xy: tuple[int, int], mm: Minimap, tile: tuple[int, int],
                 area=(20, 150, 680, 820)) -> tuple[int, int]:
    """Where to tap on the island map to walk toward a minimap tile, given the player's screen position.
    Points off screen are pulled back along the same direction into the play area (the game pathfinds the rest)."""
    pr, pc = mm.centre
    dx, dy = (tile[1] - pc) * SCREEN_TILE, (tile[0] - pr) * SCREEN_TILE
    x0, y0, w, h = area
    t = 1.0
    for _ in range(20):
        x, y = player_xy[0] + dx * t, player_xy[1] + dy * t
        if x0 <= x <= x0 + w and y0 <= y <= y0 + h:
            return int(x), int(y)
        t *= 0.8
    return player_xy
