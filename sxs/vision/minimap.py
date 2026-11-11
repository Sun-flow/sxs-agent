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
from typing import Optional

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
    border: frozenset = frozenset()  # tiles a zone's dotted border line runs through (R-132)

    def tiles(self, kind: str) -> list[tuple[int, int]]:
        return [(r, c) for r, row in enumerate(self.grid) for c, k in enumerate(row) if k == kind]


# --- zone borders (R-132) ------------------------------------------------------------------------------------
# mae, 2026-11-09: before a walk crosses into another zone, see the border coming. On the minimap a zone border is a
# thin dotted line of light grey (HSV ~43/13/140 in mae's crop `minimap/legend_zone_boundary_mae.png`; S 4-37 and
# V 150-187 across a passage in `world/explore_bellflower_picked.png`): 1-2 px thick, running straight along a row or
# a column, often only across the walkable gap between two walls (2 tiles). Fog (unspotted) is grey too but dark and
# blotchy; white icons are brighter, and their anti-aliased edges sit next to bright pixels: both are dropped.
BORDER_S_MAX, BORDER_V = 50, (105, 200)  # live frames blur the line: S 25-49 (2026-11-09, Verdantglade V)
BORDER_BRIGHT_V = 205  # icon interiors (player, statues, trees): line pixels next to these are icon edges
BORDER_SIDE_S = 50  # ground on either side of the line is green (saturated)
BORDER_MIN_RUN = 12  # px: a straight light run at least this long (1.5 tiles) after bridging the dot gaps
BORDER_MAX_THICK = 3  # px: thicker light shapes are icons, labels or explored-ground blobs, not the line
BORDER_TILE_PX = 3  # line pixels inside a tile's 8x8 cell that make it a border tile


def border_mask(frame: np.ndarray) -> np.ndarray:
    """Pixels of dotted zone-border lines inside the minimap circle (uint8 0/1, the minimap crop's size)."""
    cx, cy = CENTER
    out = dotted_lines(frame[cy - RADIUS:cy + RADIUS, cx - RADIUS:cx + RADIUS])
    yy, xx = np.mgrid[0:out.shape[0], 0:out.shape[1]]
    d2 = (xx - RADIUS) ** 2 + (yy - RADIUS) ** 2
    out[(d2 > (RADIUS - 5) ** 2) | (d2 < (1.2 * TILE) ** 2)] = 0  # the ring rim, and the player's own marker
    return out


def dotted_lines(crop: np.ndarray) -> np.ndarray:
    """Dotted zone-border line pixels in any crop of map drawing (minimap or area map), uint8 0/1."""
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    light = ((hsv[..., 1] < BORDER_S_MAX) & (hsv[..., 2] >= BORDER_V[0]) & (hsv[..., 2] <= BORDER_V[1])).astype(np.uint8)
    bright = ((hsv[..., 1] < BORDER_S_MAX) & (hsv[..., 2] > BORDER_BRIGHT_V)).astype(np.uint8)
    light &= 1 - cv2.dilate(bright, np.ones((7, 7), np.uint8))
    out = np.zeros_like(light)
    for horizontal in (True, False):
        bridge = np.ones((1, 5) if horizontal else (5, 1), np.uint8)  # close the gaps between dashes
        run = np.ones((1, BORDER_MIN_RUN) if horizontal else (BORDER_MIN_RUN, 1), np.uint8)
        thick = np.ones((BORDER_MAX_THICK + 1, 1) if horizontal else (1, BORDER_MAX_THICK + 1), np.uint8)
        joined = cv2.morphologyEx(light, cv2.MORPH_CLOSE, bridge)
        lines = cv2.morphologyEx(joined, cv2.MORPH_OPEN, run)  # only long straight runs survive
        # Drop runs that are part of something thick (a label, the player ring, a blob of light ground).
        fat = cv2.morphologyEx(joined, cv2.MORPH_OPEN, thick)
        fat = cv2.dilate(fat, np.ones((3, 3), np.uint8))
        # The line is drawn over green ground: both sides of it (across the run) are saturated. The grey box behind
        # an icon (the Moonveil Woods trees) has grey on one side, so its edge doesn't count.
        sat = (hsv[..., 1] >= BORDER_SIDE_S).astype(np.uint8)
        k = BORDER_MAX_THICK
        before = np.roll(sat, k, axis=0 if horizontal else 1)
        after = np.roll(sat, -k, axis=0 if horizontal else 1)
        out |= lines & (1 - fat) & before & after
    return out


def border_tiles(frame: np.ndarray, n: int) -> frozenset:
    """Grid tiles (row, col) the border line runs through."""
    mask = border_mask(frame)
    half = n // 2
    out = set()
    for r in range(n):
        for c in range(n):
            x, y = RADIUS + (c - half) * TILE, RADIUS + (r - half) * TILE
            if mask[max(0, y - TILE // 2):y + TILE // 2, max(0, x - TILE // 2):x + TILE // 2].sum() >= BORDER_TILE_PX:
                out.add((r, c))
    return frozenset(out)


LIGHT = {"walk_explored": "walk", "wall_explored": "wall"}  # a blessed zone's brightened tiles
SHADED = {"walk_unexplored": "walk", "wall_unexplored": "wall"}  # a zone not yet blessed (striped, darker)
SHADE_MIN_RUN = 4  # tiles: a straight light/shaded edge at least this long is a zone border


def shade_border(grid: list[list[str]], centre: tuple[int, int], home_light: Optional[bool] = None) -> frozenset:
    """mae, 2026-11-09: zone borders also show as the edge between a brightened (blessed, explored) zone and a
    shaded one; such edges are regular and straight. Finds straight runs of SHADE_MIN_RUN+ tile pairs along a row or
    column where one side is light and the other shaded (walls or ground, either side), and returns the
    tiles on the far side from the player's own shading, so the planner sees a wall there. A ragged edge (the fog
    frontier inside a zone) doesn't make a long straight run.

    home_light: whether the zone we're exploring is the light one (blessed) or the shaded one. The caller usually
    knows (Clear Zone: shaded while the zone is unexplored). Guessed from the tiles round the player otherwise,
    which goes wrong right at the edge (live 2026-11-09: standing on the line, the light side won the count)."""
    n = len(grid)
    pr, pc = centre
    if home_light is None:
        near = [grid[r][c] for r in range(max(0, pr - 2), min(n, pr + 3)) for c in range(max(0, pc - 2), min(n, pc + 3))]
        home_light = sum(k in LIGHT for k in near) > sum(k in SHADED for k in near)
    mine_light = home_light
    # The player's marker and its white ring hide the tiles under and round it ("icon"/"unspotted"); they're our own
    # zone's ground, and a border right under us must still count (live 2026-11-09, standing on V's south edge).
    own = "walk_explored" if mine_light else "walk_unexplored"
    grid = [[own if max(abs(r - pr), abs(c - pc)) <= 2 and k in ("icon", "unspotted") else k
             for c, k in enumerate(row)] for r, row in enumerate(grid)]

    def pair(a: str, b: str) -> Optional[tuple[int, int]]:
        """(index of the light tile, of the shaded tile) within (a, b), or None."""
        if a in LIGHT and b in SHADED:  # walls included: the edge runs through both
            return 0, 1
        if b in LIGHT and a in SHADED:
            return 1, 0
        return None

    out = set()
    for horizontal in (True, False):  # edges between rows r/r+1 (run along c), then between columns
        for i in range(n - 1):
            run: list[tuple[int, int]] = []
            for j in range(n + 1):
                hit = None
                if j < n:
                    t = [(i, j), (i + 1, j)] if horizontal else [(j, i), (j, i + 1)]
                    p_ = pair(grid[t[0][0]][t[0][1]], grid[t[1][0]][t[1][1]])
                    if p_:
                        far = p_[1] if mine_light else p_[0]  # the side that isn't our zone's shading
                        hit = t[far]
                if hit:
                    run.append(hit)
                    continue
                if len(run) >= SHADE_MIN_RUN:
                    out.update(run)
                run = []
    return frozenset(out)


def read(frame: np.ndarray, home_light: Optional[bool] = None) -> Minimap:
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
    return Minimap(grid, (half, half), border_tiles(frame, n) | shade_border(grid, (half, half), home_light))


def render(mm: Minimap, scale: int = 12) -> np.ndarray:
    n = len(mm.grid)
    img = np.zeros((n * scale, n * scale, 3), np.uint8)
    for r, row in enumerate(mm.grid):
        for c, k in enumerate(row):
            cv2.rectangle(img, (c * scale, r * scale), ((c + 1) * scale - 1, (r + 1) * scale - 1), COLOURS[k], -1)
    for r, c in mm.border:  # zone border line (R-132): magenta outline
        cv2.rectangle(img, (c * scale, r * scale), ((c + 1) * scale - 1, (r + 1) * scale - 1), (255, 0, 255), 2)
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

CLOSE_TILES = 4  # objects this many tiles away or nearer are tapped on screen, not reached by a big-map walk
SCREEN_TILE = 104  # px per game tile on the island map at the default zoom (grid lines are this far apart)
GOALS = ("item", "monster", "building")  # map objects: pickups, monsters (mae, 2026-11-04: fight orange dots),
# structures. Ground is never a goal: the % comes from objects (R-143; the fog walk's "fog leads" and shaded-tile
# goals were scrapped with it, 2026-11-10).


BORDER_BUFFER = 1  # tiles round a border line that are walls too: the line is drawn to within a tile (live 2026-11-09)


def path_to_nearest(mm: Minimap, goals=GOALS, skip=frozenset(), cross_border: bool = False) -> list[tuple[int, int]]:
    """Breadth-first path over walkable tiles from the player to the nearest goal tile (a map object by default).
    Goal tiles themselves count as walkable. Empty if nothing reachable.

    A zone's dotted border line (R-132) is a wall unless cross_border: finish the zone you're in first, and cross
    only into a zone that passes the 1.25x power check (the caller decides, `sxs.core.zones`)."""
    from collections import deque

    n = len(mm.grid)
    start = mm.centre
    blocked = set() if cross_border else {(r + dr, c + dc) for r, c in mm.border
                                          for dr in range(-BORDER_BUFFER, BORDER_BUFFER + 1)
                                          for dc in range(-BORDER_BUFFER, BORDER_BUFFER + 1)} - {start}
    prev = {start: None}
    q = deque([start])
    while q:
        cur = q.popleft()
        r, c = cur
        if cur != start and cur not in skip and mm.grid[r][c] in goals:
            path = []
            while cur is not None:
                path.append(cur)
                cur = prev[cur]
            return path[::-1]
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            # The player's white ring reads as grey "unspotted" on the tiles around it (seen 2026-11-05 in
            # Verdantglade III: it walled the player in and no path was ever found), so they count as walkable.
            ring = max(abs(nr - start[0]), abs(nc - start[1])) <= 1
            if (nr, nc) in blocked:
                continue
            if 0 <= nr < n and 0 <= nc < n and (nr, nc) not in prev and (mm.grid[nr][nc] in WALKABLE or ring):
                prev[(nr, nc)] = cur
                q.append((nr, nc))
    return []


def world_tile(mm: Minimap, tile: tuple[int, int], player_xy: tuple[int, int]) -> tuple[int, int]:
    """Map coordinates of a minimap tile, from the player's coordinates (x grows east, y grows north)."""
    (pr, pc), (r, c) = mm.centre, tile
    return player_xy[0] + (c - pc), player_xy[1] - (r - pr)


def screen_point(player_xy: tuple[int, int], mm: Minimap, tile: tuple[int, int],
                 area=(20, 320, 680, 600)) -> tuple[int, int]:
    # area starts under the minimap and the area name (a tap at y ~200 opened the area map, 2026-11-05) and ends
    # above the quest tracker and chat strip.
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
