"""Explore side areas that have no quest marker: walk to unexplored ground the minimap shows (falling back to the
fog edge). No model calls.

    python -m sxs fogwalk [--minutes 10] [--area NAME]

Each step finds where the fog (light, unsaturated grey) meets the map, taps a walkable spot just outside it, and
lets the explore loop's handlers deal with whatever happens (fights, cards, pickups). Many side areas give
resources and levels but have no quest (mae, 2026-11-03).
"""

from __future__ import annotations

import logging
import random
import re
import time
from typing import Optional

import cv2
import numpy as np

from ..actions import goto, heal, rewards
from ..actions.camera import PLAY_AREA, centre_player, recentre_on_player
from ..actions.common import TOWER_STATES, pass_through
from ..actions.unstick import attack_guard
from ..actions.watchdog import Heartbeat, UnknownScreens
from ..core import ui
from ..core.device import save_unknown
from ..core.interrupts import resume_with
from ..core.loop import progress, Loop, banner
from ..core.nav import Navigator
from ..core.marks import server_day
from ..core.paths import RESOURCE
from ..policy.decide import Context, Decider
from ..policy.zones import Tree
from ..vision import minimap
from ..vision.hp import PREP_HP_BAR
from ..vision import area_map, collectibles
from ..vision.hud import read_stamina
from ..vision.player import player_on_screen
from . import tower
from .explore import REPEAT_LIMIT, hud_hp

GATE_LIMIT = 3  # Gate of Power cards in one walk before the zone counts as walled off
from .gather import COST

log = logging.getLogger("sxs.loops.fogwalk")

FOG_S_MAX, FOG_V_MIN = 40, 150  # fog is pale grey
STEP_IN = 40  # px from the fog edge into clear ground
STILL_LIMIT = 4  # walk taps with unchanged coordinates before giving up (a tap takes 5-7 s; runs are 1-2 min)
STAMINA_KEEP = 70  # R-107: stamina kept for the daily commissions
REWARD_TAPS_MAX = 3  # tracker gift taps per walk: a gift that stays after this many taps isn't claimable from here


def fog_edge_target(frame: np.ndarray, valid=None) -> Optional[tuple[int, int]]:
    """A tap point on clear ground right next to the fog, nearest the screen centre (with a little randomness so
    repeated calls spread along the edge). None if there's no fog in view.

    R-146 (mae, 2026-11-10): never tap fog, and never a tree or rock beside it: the point must be walkable ground the
    game can path to. `valid(point)` (the minimap's verdict on the tile under it) filters the candidates."""
    x0, y0, w, h = PLAY_AREA
    hsv = cv2.cvtColor(frame[y0:y0 + h, x0:x0 + w], cv2.COLOR_BGR2HSV)
    fog = ((hsv[:, :, 1] < FOG_S_MAX) & (hsv[:, :, 2] > FOG_V_MIN)).astype(np.uint8)
    fog = cv2.morphologyEx(fog, cv2.MORPH_OPEN, np.ones((15, 15), np.uint8))  # drop small grey sprites
    if fog.mean() < 0.03:
        return None
    clear = 1 - fog
    # Clear pixels within STEP_IN of fog, but not touching it: the walkable band along the edge.
    near = cv2.dilate(fog, np.ones((STEP_IN * 2, STEP_IN * 2), np.uint8)) & clear
    band = near & (1 - cv2.dilate(fog, np.ones((STEP_IN, STEP_IN), np.uint8)))
    ys, xs = np.nonzero(band)
    if len(xs) == 0:
        return None
    cx, cy = w / 2, h / 2
    d = (xs - cx) ** 2 + (ys - cy) ** 2
    order = np.argsort(d)
    if valid is None:
        pick = random.choice(order[:200])
        return int(xs[pick] + x0), int(ys[pick] + y0)
    for k in order[::7][:300]:  # nearest first, thinned: neighbouring pixels share a tile
        p = (int(xs[k] + x0), int(ys[k] + y0))
        if valid(p):
            return p
    return None


def walkable_at(mm, player: Optional[tuple[int, int]], point: tuple[int, int]) -> bool:
    """True when the minimap tile under a screen point is walkable ground (not fog, not a wall, not a border)."""
    if player is None:
        return False
    pr, pc = mm.centre
    r = pr + round((point[1] - player[1]) / minimap.SCREEN_TILE)
    c = pc + round((point[0] - player[0]) / minimap.SCREEN_TILE)
    n = len(mm.grid)
    if not (0 <= r < n and 0 <= c < n) or (r, c) in mm.border:
        return False
    return mm.grid[r][c] in ("walk_explored", "walk_unexplored", "item")


def to_world(player_xy: Optional[tuple[int, int]], player: Optional[tuple[int, int]],
             point: tuple[int, int]) -> Optional[tuple[int, int]]:
    """Map coordinates of a screen point, from the player's map coordinates and screen position (x grows east, y
    grows north). Screen points go stale as soon as the camera moves; map coordinates don't."""
    if player_xy is None or player is None:
        return None
    return (player_xy[0] + round((point[0] - player[0]) / minimap.SCREEN_TILE),
            player_xy[1] - round((point[1] - player[1]) / minimap.SCREEN_TILE))


BORDER_KEEP = 1  # tiles: walk taps stay this far from a zone border line unless crossing is allowed (R-132)
AREA_MAP_TRIES = 12  # big-map walks to a dot or structure per run (each takes ~20 s)
OUTSIDE_RADIUS = 3  # map tiles around a spot found to be in another zone that are no longer goals
LAST_DIST = 99  # tiles along the path to what minimap_target headed for
DIRECT_TAPS_MAX = 2  # direct taps on the same near object before giving up on it
GUARD_TAPS_MAX = 6  # taps on monsters under guard markers per walk
LAST_GOAL_XY: Optional[tuple] = None  # map coordinates of the last minimap_target() goal tile
GOAL_TAPS_MAX = 3  # walk taps toward one goal tile before it counts as one we can't reach this way
LAST_GOAL: Optional[str] = None  # what the last minimap_target() headed for: "monster", "building" or None


def area_blessed(dev, det, area: Optional[str]) -> bool:
    """True when the area we're in (or `area`) shows no exploration percentage on the area map: explored (and, by
    the roam loop's order, blessed). Unreadable counts as not explored. Opens and closes the area map once."""
    from .roam import read_areas  # roam imports this module
    here = area or goto.area_name_here(det)
    dev.tap(*goto.MINIMAP)
    time.sleep(2.5)
    areas = read_areas(det, dev.screenshot())
    dev.tap(*ui.BACK_ARROW)
    time.sleep(2)
    # Exact name first: the loose match also takes the kingdom's title "Verdantglade" for "Verdantglade V" (seen
    # 2026-11-05: Verdantglade V at 71% was called explored and the walk took no pickups or fights).
    hits = [a for a in areas if goto.squeeze(a.name) == goto.squeeze(here)] or            [a for a in areas if goto.same_area(a.name, here)]
    if any(a.pct is not None for a in hits):
        return False
    return bool(hits) and any(goto.squeeze(a.name) == goto.squeeze(here) for a in hits)


def minimap_target(det, frame: np.ndarray, lookahead: int = 4, player_xy=None,
                   buildings_seen: Optional[set] = None, items_ok: bool = True,
                   player: Optional[tuple[int, int]] = None, monsters_ok: bool = True,
                   visited_xy: Optional[set] = None, outside_xy: Optional[set] = None,
                   cross_border: bool = False, home_light: Optional[bool] = None,
                   shaded_walk: bool = True) -> Optional[tuple[int, int]]:
    """Plan on the minimap: shortest walkable path to the nearest pickup or unexplored walkable tile, else to a gold
    building not visited yet this run (dungeons, mines: interactable; their cards go through the rules), then tap
    a few tiles along it (relative to the player, found by its name label). None if nothing is reachable.

    R-132 (mae, 2026-11-09): a zone's dotted border on the minimap is a wall for the plan unless cross_border (the
    caller allows it only when walking in from a finished neighbour into the zone it was sent to)."""
    global LAST_GOAL, LAST_DIST, LAST_GOAL_XY
    LAST_GOAL, LAST_DIST, LAST_GOAL_XY = None, 99, None
    mm = minimap.read(frame, home_light)
    # mae, 2026-11-05: exploration % comes from what you do, not where you walk: collect green dots, fight orange
    # ones, complete yellow structures; then the area's statue appears. So objects come first, in that order of
    # nearness; then walkable ground running into black fog (a lead); then shaded ground we haven't stood on, so
    # the walk doesn't bounce between two tiles it already visited (seen in Verdantglade III).
    objects = tuple(g for g in ("item", "monster") if (items_ok or g != "item") and (monsters_ok or g != "monster"))
    n = len(mm.grid)
    # Goals near a spot that turned out to be another zone are left alone (R-132: finish this zone first).
    off = {(r, c) for r in range(n) for c in range(n) if player_xy is not None and outside_xy and any(
        max(abs(wx - ox), abs(wy - oy)) <= OUTSIDE_RADIUS
        for (wx, wy) in [minimap.world_tile(mm, (r, c), player_xy)] for (ox, oy) in outside_xy)}
    if mm.border:
        log.debug("zone border on the minimap at %d tiles (%s)", len(mm.border), "crossing allowed" if cross_border
                  else "a wall: finish this zone first")
    # Our own marker and ring read as an orange "monster" right next to us (live 2026-11-10: "monster 1 tiles
    # away", then the tap opened our profile, over and over): tiles touching the centre are never object goals.
    pr, pc = mm.centre
    ring = {(pr + dr, pc + dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1)}
    path = minimap.path_to_nearest(mm, goals=objects, skip=off | ring, cross_border=cross_border) if objects else []
    if len(path) < 2 and player_xy is not None and buildings_seen is not None:
        skip = off | {tile for tile in mm.tiles("building") if minimap.world_tile(mm, tile, player_xy) in buildings_seen}
        path = minimap.path_to_nearest(mm, goals=("building",), skip=skip, cross_border=cross_border)
        if len(path) >= 2:
            spot = minimap.world_tile(mm, path[-1], player_xy)
            buildings_seen.add(spot)
            log.info("heading for a gold building at map %s", spot)
            LAST_GOAL = "building"
            lookahead = len(path)  # walk all the way: the tap on it opens its card
    if len(path) < 2:
        stood = set(off)
        if player_xy is not None and visited_xy:
            stood |= {(r, c) for r in range(n) for c in range(n) if minimap.world_tile(mm, (r, c), player_xy) in visited_xy}
        path = minimap.path_to_nearest(mm, goals=("fog_lead",), skip=stood, cross_border=cross_border)
        if len(path) < 2 and shaded_walk:
            # Not in a zone still being explored (live 2026-11-09, Verdantglade V at 78%): there every tile is drawn
            # shaded until the zone is blessed, so "unexplored ground" never runs out and the walk paced for 6
            # minutes without gaining a percent. The % comes from objects; the caller finds them on the big map.
            path = minimap.path_to_nearest(mm, goals=("walk_unexplored",), skip=stood, cross_border=cross_border)
    if len(path) < 2:
        return None
    LAST_DIST = len(path) - 1
    if player_xy is not None:
        LAST_GOAL_XY = minimap.world_tile(mm, path[-1], player_xy)
    if mm.grid[path[-1][0]][path[-1][1]] == "item":
        LAST_GOAL = "item"
    if mm.grid[path[-1][0]][path[-1][1]] == "monster":
        log.info("heading for a monster %d tiles away", len(path) - 1)
        LAST_GOAL = "monster"
        lookahead = len(path)  # tap the monster itself: walking onto it starts the fight
    step = min(lookahead, len(path) - 1)
    if mm.border and not cross_border:
        # Live 2026-11-09: a tap 2 tiles short of the border still carried the character over it (the game paths to
        # the tapped spot its own way). Tap no tile within BORDER_KEEP of the line; a goal right at it is walked to
        # one short step at a time.
        safe = [i for i, t in enumerate(path[:step + 1])
                if all(max(abs(t[0] - b[0]), abs(t[1] - b[1])) > BORDER_KEEP for b in mm.border)]
        if not safe or max(safe) == 0:
            return None  # every step toward it is at the line: no tap (the path already keeps a tile's buffer)
        step = max(safe)
    player = player or player_on_screen(det, frame)
    if player is None:
        return None
    return minimap.screen_point(player, mm, path[step])


MAP_LABELS_ROI = [0, 120, 720, 1060]  # area-map zone labels (legend and kingdom buttons excluded below)


QUEST_LOCATE_X = 330  # the locate (target) icon right of the tracker's progress line
QUEST_TARGET_DY = 80  # the quest ring floats this far above its target
_LOCATE_MISSES = 0  # locate taps since the last quest ring was seen (each tap toggles tracking)
APPROACH_DY = 75 # the ground tile just below a map object, walked to when a tap on the object itself did nothing
QUEST_FAILS_MAX = 3  # quest-pointer steps without the counter moving before the walk stops using it


def quest_counter(det, zone: str) -> Optional[int]:
    """The tracked quest's counter when it is "Explore <zone> N/100", else None."""
    prog = det.find("Explore.Progress")
    m = re.search(r"Explore\s*(.+?)\s*(\d+)\s*/\s*100", prog.text if prog else "")
    if not m or not goto.same_area(m.group(1), zone):
        return None
    return int(m.group(2))


def quest_moved_on(det, zone: str) -> bool:
    """The tracker shows another zone's Explore quest: this zone's quest was finished and claimed."""
    prog = det.find("Explore.Progress")
    m = re.search(r"Explore\s*(.+?)\s*(\d+)\s*/\s*100", prog.text if prog else "")
    return bool(m) and not goto.same_area(m.group(1), zone)


MARKER_TEMPLATES = ("marker.png", "marker_dim.png")  # resource/image/explore/: the gold quest ring
MARKER_MATCH = 0.75


def find_quest_ring(frame) -> Optional[tuple[int, int]]:
    """Centre of the gold quest ring anywhere below the very top (live 2026-11-09: as an edge ring it sat at y 50,
    above the pipeline node's region, so the step thought there was none)."""
    best = (0.0, None)
    for name in MARKER_TEMPLATES:
        tpl = cv2.imread(str(RESOURCE / "image" / "explore" / name))
        if tpl is None:
            continue
        r = cv2.matchTemplate(frame[20:960], tpl, cv2.TM_CCOEFF_NORMED)
        _, score, _, (x, y) = cv2.minMaxLoc(r)
        if score > best[0]:
            best = (score, (x + tpl.shape[1] // 2, 20 + y + tpl.shape[0] // 2))
    return best[1] if best[0] >= MARKER_MATCH else None


def quest_step(dev, det, fight: bool) -> bool:
    """One step toward the tracked Explore quest's next target. The tracker's locate icon toggles tracking ("Tracking
    On"/off), so it is tapped only when no gold ring shows. An edge ring is tapped to pan the camera to the target;
    then the target under the ring is tapped. A monster guarding it (red skull marker) is fought first. True when a
    step was taken."""
    prog = det.find("Explore.Progress")
    if not prog:
        return False
    global _LOCATE_MISSES
    ring = find_quest_ring(dev.screenshot())
    if ring is None:
        if _LOCATE_MISSES >= 1:
            # Live 2026-11-10: three locate taps in a row, 15 s apart, none showing a ring (the camera had drifted
            # off our character); each tap flips tracking, so tapping again only turns it back off. Once a tap
            # brought no ring, leave the pointer until a ring is seen again.
            return False
        ui.tap(dev, (QUEST_LOCATE_X, ui.centre(prog.box)[1]), 2)  # tracking was off: turn it on
        ring = find_quest_ring(dev.screenshot())
        if ring is None:
            _LOCATE_MISSES += 1
            log.info("locate tap showed no quest ring: not tapping it again until one shows")
            return False
    _LOCATE_MISSES = 0
    for _ in range(2):
        if ring is None:
            return False
        cx, cy = ring
        if cy < 130 and cx < 300:
            # An edge ring over the HUD (name, power, portrait): a tap there opens the profile or class page (live
            # 2026-11-10, a "Mage" card and the Class page). Leave the quest pointer for now.
            log.info("quest ring under the HUD at %s: not tapping it", ring)
            return False
        me = player_on_screen(det, dev.screenshot())
        on_me = me is not None and (cx - me[0]) ** 2 + (cy - me[1]) ** 2 < 90 ** 2
        # Traced live 2026-11-10 (scripts/tap_trace.py, tap 37): with us at the screen edge, the quest ring floated
        # over our own character at x 667; taken for an edge ring, the tap hit us and opened the profile. A ring on us
        # marks a target next to us, not an off-screen one.
        if not on_me and (cx < 70 or cx > 650 or cy < 150 or cy > 900):  # an edge ring: tapping it pans the camera
            ui.tap(dev, (cx, cy), 2)
            ring = find_quest_ring(dev.screenshot())
            continue
        if fight and attack_guard(dev, det):
            return True
        log.info("quest pointer: tapping the target under the ring at %s", (cx, cy))
        tap_object(dev, det, (cx, cy + QUEST_TARGET_DY))
        return True
    return False


def tap_object(dev, det, point: tuple[int, int], wait: float = 4) -> str:
    """Tap a map object (monster, pot, pickup). Live 2026-11-10 (Verdantglade VII, mae: "stuck at a monster fight
    again"): a tap on a monster several tiles away did nothing at all, the character didn't even walk, and the quest
    step tapped it again and again; from the tile beside it the same tap started the fight at once (62 -> 64 -> 67%).
    So when a tap leaves us on the map at the same coordinates, walk to the tile just below the object first, then
    tap it again. Returns "left_map" (a fight or card opened), "moved", "approached" or "nothing"."""
    before = goto.coords(det)
    tapped = off_me(det, point)
    dev.tap(*tapped)
    time.sleep(wait)
    after = goto.coords(det)
    if after is None:
        return "left_map"
    if before is None or after != before:
        return "moved"
    beside = off_me(det, (point[0], min(900, point[1] + APPROACH_DY)))
    log.info("tap on the object at %s didn't move us: walking beside it (%s) first", point, beside)
    dev.tap(*beside)
    for _ in range(6):  # walk until the coordinates stop changing
        time.sleep(1.5)
        now = goto.coords(det)
        if now is None:
            return "left_map"  # walking there started the fight (a monster that charges)
        if now == after:
            break
        after = now
    # The camera doesn't follow the walk, so the object stays where it was on screen.
    dev.tap(*off_me(det, point))
    time.sleep(wait)
    return "left_map" if goto.coords(det) is None else "approached"


WHEEL_SPIN = (360, 1100)  # "Tap to spin" on the Wheel of Destiny


def lucky_wheel_free(det) -> bool:
    """The Wheel of Destiny is open and its spin button shows no cost (just "Tap to spin")."""
    title = " ".join(t for t, _ in det.read_text([150, 130, 420, 70]))
    if "Wheel of Destiny" not in title:
        return False
    button = " ".join(t for t, _ in det.read_text([180, 1060, 360, 80]))
    return bool(re.fullmatch(r"\s*Tap to spin\s*", button))


COMPANION_TAB = (608, 1216)  # the friend picker's bottom tabs: Friends / Guild / Companion
COMPANION_PICKS = ((626, 230), (626, 348), (626, 466))  # select circles of the three companion rows
PICKER_OK = (360, 1104)
GATE_SLOT_DX = 136  # px between the card's friend slots; the first "+" sits this far right of our own portrait


def elemental_gate(dev, det) -> Optional[str]:
    """Gate of Wind (and the other Gates of Elements): "Total Wind Affinity reaches 1", with up to 3 friend slots.
    Affinity comes from relics (not unlocked) or helpers; our NPC companions (Akane, Qin, Killian) carry 101 each and
    adding them is free (R-057). Live 2026-11-10, Zephyr Vale: Akane alone opened it. Returns None when this isn't
    such a card, else "opened" or "short" (the requirement still not met after three helpers)."""
    lines = det.read_text([30, 520, 660, 520])
    text = " ".join(t for t, _ in lines)
    if not re.search(r"Gate of \w+", text) or not re.search(r"Affinity|Aegis", text) or "Power reaches" in text:
        return None
    taken = 0
    for _ in range(len(COMPANION_PICKS) + 1):
        lines = det.read_text([30, 520, 660, 640])
        opened = [b for t, b in lines if re.fullmatch(r"\s*Open\s*", t)]
        if opened:
            x, y, w, h = opened[0]
            ui.tap(dev, (x + w // 2, y + h // 2), 6)
            log.info("Gate of Elements: requirement met with companions; opened it")
            return "opened"
        friends = [b for t, b in lines if "Select Friends" in t]
        if not friends:
            break
        # The first empty "+" slot: our portrait sits at x ~150, the slots follow at GATE_SLOT_DX spacing.
        slot_y = friends[0][1] + 82
        if taken >= len(COMPANION_PICKS):
            break
        plus = sorted((b for t, b in lines if t.strip() == "+"), key=lambda b: b[0])
        slot = ((plus[0][0] + plus[0][2] // 2, plus[0][1] + plus[0][3] // 2) if plus
                else (152 + GATE_SLOT_DX * (taken + 1), slot_y))
        ui.tap(dev, slot, 3)
        ui.tap(dev, COMPANION_TAB, 2)
        ui.tap(dev, COMPANION_PICKS[taken], 1)
        ui.tap(dev, PICKER_OK, 3)
        taken += 1
        log.info("Gate of Elements: added companion %d", taken)
    log.warning("Gate of Elements: still short after adding companions; leaving it")
    ui.tap(dev, ui.ABOVE_POPUP, 2)
    return "short"


ME_RADIUS = 70  # px round our character on screen: a tap there opens our profile ("Mage", Class Level 8)


# Island-map HUD buttons a walk tap must never land on (x0, y0, x1, y1 at 720x1280). Live 2026-11-10: a walk tap
# toward a monster at (671, 376) hit the "Timed Packs" button and opened a paid pack popup.
HUD_KEEP_OUT = (
    (0, 0, 330, 200),      # portrait, name, power
    (0, 200, 110, 260),    # flag button under the portrait
    (500, 0, 720, 450),    # minimap, zone name and coordinates, Timed Packs
    (0, 700, 90, 820),     # Team / Apply button on the left edge
    (0, 950, 720, 1280),   # quest tracker, chat strip, bottom buttons
)
HUD_MARGIN = 12


def off_hud(point: tuple[int, int]) -> tuple[int, int]:
    """Move a walk tap out of any HUD button area, to the nearest edge of that area that is open map."""
    x, y = int(point[0]), int(point[1])
    for _ in range(3):  # leaving one area can land in another (rare); settle in a few moves
        hit = next((r for r in HUD_KEEP_OUT if r[0] <= x <= r[2] and r[1] <= y <= r[3]), None)
        if hit is None:
            break
        x0, y0, x1, y1 = hit
        options = [(x0 - HUD_MARGIN, y), (x1 + HUD_MARGIN, y), (x, y0 - HUD_MARGIN), (x, y1 + HUD_MARGIN)]
        options = [(a, b) for a, b in options if 20 <= a <= 700 and 20 <= b <= 1260]
        x, y = min(options, key=lambda p: abs(p[0] - x) + abs(p[1] - y))
    return x, y


def off_me(det, point: tuple[int, int], frame=None) -> tuple[int, int]:
    """A walk tap that would land on our own character opens the profile (live 2026-11-09 and -10, again and
    again). Push such a point out of ME_RADIUS, away from the character, so the tap still walks that way."""
    point = off_hud(point)
    me = player_on_screen(det, frame if frame is not None else det.device.screenshot())
    if me is None:
        return point
    dx, dy = point[0] - me[0], point[1] - me[1]
    d = (dx * dx + dy * dy) ** 0.5
    if d >= ME_RADIUS:
        return point
    if d < 1:
        dx, dy, d = 0, 1, 1  # straight on top of us: step down a little
    k = (ME_RADIUS + 15) / d
    return int(me[0] + dx * k), int(me[1] + dy * k)


def zone_here(dev, det, tree: Optional[Tree] = None) -> str:
    """The zone the player is in. R-140 as amended by mae (2026-11-10): the name under the minimap is always a valid
    description of the zone and is the first check. The big map's player dot (`zone_by_map`) is the fallback, for
    when that name is unreadable or isn't a zone the location tree knows."""
    name = goto.area_name_here(det)
    tree = tree or Tree.load()
    if name and tree.key(name):
        return tree.key(name)
    return zone_by_map(dev, det, name) or name


def zone_by_map(dev, det, hint: str = "") -> Optional[str]:
    """Where the player is by the white dot on the big map: the fallback for `zone_here` (R-140) when the name under
    the minimap can't be read or matched. Opens the area map zoomed out, takes the zone whose label is nearest our dot
    (the hint stands unless another label is clearly nearer), closes the map. None if unreadable."""
    dev.tap(*goto.MINIMAP)
    time.sleep(2.5)
    if det.detect().state != "area_map":
        return None
    goto.survey_zoom(dev)
    frame = dev.screenshot()
    me = [p for k, p in area_map.objects(frame) if k == "player"]
    labels = map_labels(det, frame)
    dev.tap(*ui.BACK_ARROW)
    time.sleep(2)
    if not me or not labels:
        return None
    px, py = me[0]
    dist = {t: ((labels[t][0] - px) ** 2 + (labels[t][1] - py) ** 2) ** 0.5 for t in labels}
    best = min(dist, key=dist.get)
    # Labels sit mid-zone, so near an edge another zone's label can be the nearest (live 2026-11-09: at Verdantglade
    # V's east edge, Highland Woods). The name under the minimap stands unless the dot is clearly in another zone.
    hinted = [t for t in labels if hint and goto.same_area(t, hint)]
    if hinted and dist[best] >= area_map.LABEL_MARGIN * min(dist[t] for t in hinted):
        return hinted[0]
    return best


def map_labels(det, frame) -> dict:
    """Zone labels on the area map: name -> centre. Not % lines, power lines or the legend."""
    out = {}
    for t, b in det.read_text(MAP_LABELS_ROI, frame):
        t = t.replace("-", " ").strip(" |")
        if len(t) < 4 or re.search(r"%|\d\.?\d?K$|Exploration", t) or (b[0] > 530 and b[1] < 270):
            continue
        out[t] = ui.centre(b)
    return out


ZONE_PICK_PX = 900  # big-map search radius for this zone's objects (the label check keeps it to the zone)


def zone_picker(det, kinds, home: Optional[str], skip=()):
    """Big-map picker: the nearest object of `kinds` that is in our zone (R-132), anywhere on the map (live
    2026-11-09: a 260 px radius found nothing while Verdantglade V still had dots at its far edge)."""
    def pick(frame):
        labels = (lambda: map_labels(det, frame)) if home else None  # OCR only if there's something to check
        return (area_map.nearest(frame, kinds, max_px=ZONE_PICK_PX, labels=labels, home=home, skip=skip)
                or (None, None))[1]
    return pick


def walk(dev, det, minutes: float = 10, area: Optional[str] = None,
         allowed: Optional[set[str]] = None, walk_there: bool = True, farm: bool = False) -> str:
    """Explore `area` (walking there first with the area map unless walk_there is False), or the area we're
    standing in. `allowed` names neighbouring areas it may stand in without walking back: mae, 2026-11-04, "try
    moving from areas you are connected to": enter a new area from the explored one next to it, not by a long
    area-map walk that lands at its fogged label."

    mae, 2026-11-05 (R-065): in an area still being explored, pickups and fights are free, so take them. In an
    explored or blessed area (no percentage on the area map) monsters respawn and pickups cost stamina, so neither
    is touched unless the caller opts in with farm=True (then pickups keep the 70-stamina reserve, R-107)."""
    allowed = set(allowed or ())
    banner(log, "Fog Walk", "explore a side area with no quest marker: walk to unexplored tiles the minimap shows, "
           "else to the fog edge; fight and open cards on the way",
           f"{minutes:g} minutes, no fog in view after 4 pans, no new tile reached in "
           f"{STILL_LIMIT} walk taps, a lost fight, or an unfamiliar screen")
    global _LOCATE_MISSES
    _LOCATE_MISSES = 0
    decider, ctx = Decider(det), Context(goal="explore")
    deadline = time.monotonic() + minutes * 60
    unknown = UnknownScreens(in_a_row=5)
    no_fog = still = 0
    last_xy, progress_at = None, time.monotonic()
    home_area, strayed = area, False
    visited: set[str] = set()
    repeats, last_card = 0, None
    gates = 0  # Gate of Power cards met this walk
    buildings_seen: set = set()
    heal_tries = 0
    last_tap = None  # map coordinates of the last walk tap (None when the player wasn't found on screen)
    reward_taps = 0
    if det.detect().state != "world_map":
        from .roam import Roamer  # roam imports this module
        if not Roamer(dev, det)._to_world():  # started from home or a menu: open the island map first
            return "not_on_map"
    if area and walk_there:
        goto.go_to(dev, det, area)
    stood_on: set = set()  # map coordinates the character has stood on this run
    map_tries = 0
    guard_taps = 0
    fog_misses = 0  # fog-edge looks in a row that found no walkable edge

    def fog_worked() -> bool:
        """mae, 2026-11-10: a zone is explored from revealed ground toward the fog, never by jumping into its middle
        (big-map walks went deep, past monsters guarding the entrance, and stalled). Big-map walks only once the fog
        edge around us is worked out (no walkable fog edge in view twice in a row), or in an explored zone."""
        return not free or fog_misses >= 2
    wheel_spun = False  # one free Lucky Wheel spin per walk, in an unexplored zone only
    objects_done = False  # no object left on either map: only fog edges remain (then stop)
    goal_taps: dict = {}  # minimap goal tile (map coordinates) -> walk taps aimed at it
    direct_taps: dict = {}  # map spot -> direct taps at a near object there (a repeat means it isn't taken that way)
    own_quest_seen = False  # the tracker showed this zone's own Explore quest during this walk
    quest_fails = 0  # quest-pointer steps in a row that didn't move the zone's Explore counter
    buildings_ok = True  # structures are goals until one's card can only be dismissed (a blocker)
    dismissed: dict = {}  # card title -> times dismissed this walk
    map_arrivals: list = []  # where big-map walks to an object ended (a repeat means we can't take it)
    outside: set = set()  # map coordinates where we found ourselves in another zone (R-132)
    tapped, saved_fight = None, False  # (frame, screen point) of the last walk tap, for the collectibles store
    # Unexplored: fights and pickups cost nothing (R-065). The location tree knows; reading the area map here at
    # whatever zoom it opens with called Verdantglade V at 88% "explored" (live 2026-11-09).
    tree = Tree.load()
    known = tree.get(area or goto.area_name_here(det))
    free = (not tree.explored(area or goto.area_name_here(det))) if known else not area_blessed(dev, det, area)
    fight = free or farm
    log.info("area %s: pickups %s, fights %s", "still unexplored" if free else "explored",
             "free" if free else ("farming" if farm else "off"), "on" if fight else "off")
    # Map coordinates of walk taps that opened a card we dismissed (a blessed statue, a sign). Kept in map
    # coordinates: centre_player and the edge pointer move the camera, so screen points don't stay put.
    bumped: list[tuple[int, int]] = []
    # mae, 2026-11-10: it kept re-opening statues it had already checked. Spots whose card could only be dismissed
    # (a statue not ready, "Visited Today", a blessed statue) are kept per zone in the location tree and are no
    # longer goals in later walks either.
    seen_spots = {tuple(p) for z in tree.zones.values() for p in z.get("dismissed_spots", [])}
    outside |= seen_spots
    beat = Heartbeat()
    # `tree` (the location tree, loaded above): crossings a walk makes are written back (zones.py)
    last_zone: Optional[str] = None  # area name read on the previous map step
    last_plan = None  # the frame the last minimap walk tap was planned on
    seen_names: dict = {}  # name under the minimap -> zone the big map's player dot put us in (R-140)

    def note_objective(title: str, action: str, xy) -> None:
        k = tree.key(home_area or "")
        t = (title or "").strip()
        if not k or len(t) < 4 or not xy or re.search(r"^\d+$|Mage|Settings|Friend|Request|Chat", t):
            return
        objs = tree.zones[k].setdefault("objectives", [])
        for o in objs:
            if o["title"] == t and max(abs(o["xy"][0] - xy[0]), abs(o["xy"][1] - xy[1])) <= 2:
                if action != "dismiss":
                    o["done"] = True
                return
        objs.append({"title": t, "xy": list(xy), "done": action != "dismiss", "day": server_day()})
        tree.save()

    def in_home(zone: str) -> bool:
        """True when `zone` is the zone being explored, also when OCR joined two labels ("Wildbloom CoastHidden Camo"
        for Hidden Camp, live 2026-11-10: the walk left the zone it was in to 'go back' to it)."""
        if not home_area or not zone:
            return False
        h, z = goto.squeeze(home_area), goto.squeeze(zone)
        return goto.same_area(zone, home_area) or (len(h) >= 6 and h[:-1] in z)

    def map_zone(name: str) -> str:
        # R-140 (amended 2026-11-10): a name under the minimap that the tree knows is the zone; only unknown names
        # are checked on the big map.
        clean = re.sub(r"[\s.,:;'|]+$", "", name or "")
        hs, cs = (re.sub(r"[^a-z]", "", goto.squeeze(t)) for t in (home_area or "", clean))
        if hs and cs and hs != cs and hs.startswith(cs) and len(hs) - len(cs) == 1 and hs[-1] == "i":
            # Live 2026-11-10 (Monolith Ruins II, twice): the minimap's "Monolith Ruins II" read as "Monolith Ruins
            # I ." and the big map's label as "Monolith Ruin", so the walk thought it had left the zone and walked
            # out and back. A name one trailing "I" short of the zone being explored is that zone.
            return tree.key(home_area) or home_area
        if tree.key(name):
            return tree.key(name)
        if home_area and clean and goto.close_name(clean, home_area):
            # Live 2026-11-10 (Troll Lair): the minimap read "Croll Lair", the big map's label "roILall", and the walk
            # thought it had left. A name one OCR slip from the zone being explored (and no other zone) is that zone.
            return tree.key(home_area) or home_area
        if name not in seen_names:
            seen_names[name] = zone_by_map(dev, det, home_area or "") or name
            if seen_names[name] != name:
                log.info("the minimap says %r, the big map puts us in %s (R-140)", name, seen_names[name])
        return seen_names[name]

    def note_crossing(was: Optional[str], now: str, xy) -> None:
        """A walk took us from one zone into another: that border is passable, and if `now` is the zone we were
        sent to, `was` is a way in (with the coordinates just inside)."""
        if not was or not now or goto.same_area(was, now) or not tree.key(now) or not tree.key(was):
            return
        if home_area and goto.same_area(now, home_area):
            # Any walk into the zone is a way in, a walk back from a wrong turn included: zones have several ways in
            # and out and border several zones (mae, 2026-11-09).
            tree.record_entry(now, was, True, server_day(), xy=xy)
            log.info("entered %s from %s at %s: saved as its way in", now, was, xy)
        else:
            tree.link(was, now, "walked")
        tree.save()

    def back_to_area(bare_det) -> None:
        # Runs after an interrupt handler (a tutorial, a reward choice; sxs/actions/interrupts.py): if it left us at
        # home (where this loop would end "left_area"), walk back to this area so the walk resumes where its goal is.
        # Fights, dialogue and cards it led into are this loop's normal work; the wrong area is the stray check's job.
        if not home_area or bare_det.detect().state != "home":
            return
        log.info("an interrupt left us at home; walking back to %s", home_area)
        ui.tap(dev, ui.NAV_WORLD, 4)
        goto.go_to(dev, bare_det, home_area)

    with resume_with(det, back_to_area):
        while time.monotonic() < deadline:
            d = det.detect()
            beat.check(d, last_xy, progress_at)
            if unknown.seen(d.state):
                log.warning("unfamiliar screen; frame saved to %s", save_unknown(dev, "fogwalk"))
                return "unknown_screen"
            if d.state == "world_map":
                frame = dev.screenshot()
                if hud_hp(frame) * 100 < heal.FIGHT_MIN_HP and heal_tries < 2:
                    # mae, 2026-11-04: heal before any fight; walking can bump into one. The profile opens from the HUD.
                    heal_tries += 1
                    log.info("HP under %d%%; healing from the profile", heal.FIGHT_MIN_HP)
                    heal.quick_heal(dev, det, heal.NOTHING)
                    continue
                heal_tries = 0 if hud_hp(frame) * 100 >= heal.FIGHT_MIN_HP else heal_tries
                # mae, 2026-11-04: a gift box with a red "!" on the tracker is a finished quest's reward: claim it.
                if reward_taps < REWARD_TAPS_MAX and rewards.claim_tracker_reward(dev, det, frame):
                    reward_taps += 1
                    continue
                name = goto.area_name_here(det, frame)
                here_xy = goto.COORDS.search(d.text or "")
                if name and last_zone and name != last_zone:
                    note_crossing(last_zone, name, (int(here_xy.group(1)), int(here_xy.group(2))) if here_xy else None)
                last_zone = name or last_zone
                if home_area is None and name:
                    home_area = name
                elif (name and not goto.same_area(name, home_area) and not strayed
                      and not any(goto.same_area(name, a) or goto.squeeze(name)[:7] == goto.squeeze(a)[:7] for a in allowed)
                      and not in_home(map_zone(name))):
                    # The name under the minimap changed; the big map's player dot (R-140) confirmed we left.
                    # Wandered into a neighbouring area: walk back with the area map rather than exploring the wrong one.
                    strayed = True
                    # A big-map walk that ends in another zone means the picker can't tell this zone's objects apart
                    # here: no more big-map walks this run (live 2026-11-10: Jungle Camp -> Drasilgard, three times).
                    if map_tries:
                        log.info("a big-map walk left %s: no more big-map walks this run", home_area)
                        map_tries = AREA_MAP_TRIES
                    if last_plan is not None:  # the frame the crossing tap was planned on, for tuning the border check
                        try:
                            from ..core.paths import CAPTURES
                            (CAPTURES / "border").mkdir(parents=True, exist_ok=True)
                            path = CAPTURES / "border" / f"crossed_{name.replace(' ', '_')}_{int(time.time())}.png"
                            cv2.imwrite(str(path), last_plan)
                            log.info("crossed a border the planner didn't stop; planning frame saved to %s", path)
                        except Exception as e:  # never let a debug save end the walk
                            log.debug("could not save the planning frame: %s", e)
                    # mae, 2026-11-05 (R-132): the dotted line is a zone edge; finish this zone before crossing. The
                    # walk that crossed it ended past the edge, so ground around where we stand now is off limits
                    # as a goal for the rest of the run.
                    here = goto.COORDS.search(d.text or "")
                    if here:
                        outside.add((int(here.group(1)), int(here.group(2))))
                    log.info("left %s for %s; going back (no goals near %s from now on)", home_area, name,
                             sorted(outside)[-1] if outside else "?")
                    if goto.go_to(dev, det, home_area) == "no_move":
                        # Inside an enclosure (Auroradrasil) big-map walks don't route out: the quest pointer does.
                        quest_step(dev, det, fight)
                        goto.go_to(dev, det, home_area)
                    continue
                elif name and goto.same_area(name, home_area):
                    strayed = False
                # Watchdog: progress means standing on a tile we haven't stood on this run. Taps that don't move us,
                # or that bounce between the same few tiles, mean we're blocked: stop instead of idling.
                if d.text and d.text not in visited:
                    visited.add(d.text)
                    m_ = goto.COORDS.search(d.text)
                    if m_:
                        stood_on.add((int(m_.group(1)), int(m_.group(2))))
                    last_xy, still, progress_at = d.text, 0, time.monotonic()
                else:
                    still += 1
                    if last_tap:
                        stood_on.add(last_tap)  # a tap that didn't move us: plan somewhere else next time
                    # Monsters in brackets guard the way into the area: fight one, then walk on.
                    if fight and still in (2, 3) and name and home_area and goto.same_area(name, home_area)                             and attack_guard(dev, det, frame):
                        continue
                    if still >= STILL_LIMIT and map_tries < AREA_MAP_TRIES and fog_worked():
                        # Blocked on the minimap plan: try mae's big-map walk to the nearest dot before giving up.
                        map_tries += 1
                        kinds = tuple(k for k in ("statue", "item", "monster") + (("building",) if buildings_ok else ())
                                      if (free or k != "item") and (fight or k != "monster"))
                        why = goto.go_to(dev, det, zone_picker(det, kinds, home_area))
                        log.info("blocked; area-map walk to the nearest %s: %s", "/".join(kinds), why)
                        if why == "arrived":
                            still = 0
                            continue
                    if still >= STILL_LIMIT:
                        log.warning("no new tile for %d taps (at %s, %d tiles visited); stopping", still, d.text,
                                    len(visited))
                        return "stuck"
                # The zone's own Explore quest knows where the next % is (live 2026-11-09: a flower in a fog pocket
                # neither map showed gave 85 -> 88% in one tap): follow its pointer first while it moves the counter.
                if free and home_area and own_quest_seen and quest_moved_on(det, home_area):
                    # Live 2026-11-10 (Verdantglade VIII): a big-map walk took the last %, the quest gift was claimed
                    # and the tracker moved on to "Explore Verdantglade IX"; the walk carried on into IX's border.
                    log.info("%s's Explore quest is finished (the tracker moved on): walk done", home_area)
                    if tree.key(home_area):
                        tree.observe(home_area, pct=100)
                        tree.save()
                    return "zone_done"
                if free and home_area and quest_fails < QUEST_FAILS_MAX:
                    before = quest_counter(det, home_area)
                    own_quest_seen = own_quest_seen or before is not None
                    if before is not None and quest_step(dev, det, fight):
                        after = quest_counter(det, home_area)
                        if after is not None and after > before:
                            log.info("quest pointer: %s %d -> %d%%", home_area, before, after)
                            progress(("quest", after))
                            quest_fails = 0
                            if after >= 100:
                                # Live 2026-11-09: Verdantglade V reached 100% and the walk carried on for 3 minutes.
                                log.info("%s explored (100%%): walk done", home_area)
                                if tree.key(home_area):
                                    tree.observe(home_area, pct=100)
                                    tree.save()
                                rewards.claim_tracker_reward(dev, det, dev.screenshot())
                                return "zone_done"
                        else:
                            quest_fails += 1
                        continue
                if centre_player(dev, det, frame):
                    frame = dev.screenshot()
                # Pickups cost 5 stamina; only a loop that opted in takes them, and it keeps the 70 reserve (R-107).
                items_ok = free
                if not free and farm:
                    stamina = read_stamina(det, frame=frame)
                    items_ok = stamina is not None and stamina >= STAMINA_KEEP + COST
                xy = goto.COORDS.search(d.text or "")
                xy = (int(xy.group(1)), int(xy.group(2))) if xy else None
                player = player_on_screen(det, frame)
                # R-132: the border out of the zone we were sent to is a wall until it's finished; standing in the
                # neighbour we walk in from (roam's `allowed`), the border into that zone may be crossed (roam already
                # checked its power, R-127).
                cross = bool(home_area and name and not goto.same_area(name, home_area))
                target = None if objects_done else minimap_target(
                    det, frame, player_xy=xy, buildings_seen=buildings_seen if buildings_ok else None, items_ok=items_ok,
                    player=player, monsters_ok=fight, visited_xy=stood_on, outside_xy=outside, cross_border=cross,
                    home_light=not free, shaded_walk=not free)
                if target is None and not objects_done and recentre_on_player(dev, det, frame):
                    frame = dev.screenshot()
                    player = player_on_screen(det, frame)
                    target = minimap_target(det, frame, player_xy=xy, buildings_seen=buildings_seen if buildings_ok else None, items_ok=items_ok,
                                            player=player, monsters_ok=fight,
                                            visited_xy=stood_on, outside_xy=outside, cross_border=cross,
                                        home_light=not free, shaded_walk=not free)
                spot = to_world(xy, player, target) if target else None
                if spot and any(max(abs(spot[0] - b[0]), abs(spot[1] - b[1])) <= 1 for b in bumped):
                    # The path runs through something that opens a card (seen: a blessed Goddess Statue). Tapping it
                    # again just reopens the card, so step one tile to the side; the game paths around the rest.
                    side = minimap.SCREEN_TILE if len(bumped) % 2 else -minimap.SCREEN_TILE
                    target = (min(690, max(30, target[0] + side)), target[1] + minimap.SCREEN_TILE // 2)
                    spot = to_world(xy, player, target)
                    log.info("map %s opened a card before; stepping aside to %s", spot, target)
                goal = LAST_GOAL  # what minimap_target headed for (None for a known reference: already stored)
                # A monster guarding an item (red skull marker): fight it first (mae, 2026-11-09: in every exploring
                # loop). Its battle prep goes through this loop's fight branch.
                # Only inside the zone being explored (mae, 2026-11-10: it fought guards in a neighbouring, explored
                # zone it was only walking through, where nothing needed them gone).
                in_zone = bool(name and home_area and goto.same_area(name, home_area))
                if fight and in_zone and guard_taps < GUARD_TAPS_MAX and attack_guard(dev, det, frame):
                    guard_taps += 1
                    continue
                # An object a few tiles away is tapped directly; the big-map walk is for ones out of reach (live
                # 2026-11-09: a monster 1 tile away got a 25 s big-map walk that ended beside it, twice).
                if goal in ("item", "monster") and target and minimap.CLOSE_TILES >= LAST_DIST:
                    log.info("%s %d tiles away: tapping it directly", goal, LAST_DIST)
                    goal_direct = True
                    if spot:
                        direct_taps[spot] = direct_taps.get(spot, 0) + 1
                        if direct_taps[spot] > DIRECT_TAPS_MAX:
                            # Live 2026-11-10 (Jungle Camp): the same "monster 2 tiles away" tapped 6 times, each tap
                            # landing on our own character (profile). Give up on goals around that spot.
                            log.warning("STUCK %s: %s at map %s doesn't start anything after %d taps; skipping it",
                                        home_area, goal, spot, DIRECT_TAPS_MAX)
                            outside.add(spot)
                            continue
                else:
                    goal_direct = False
                # mae, 2026-11-05: reaching an object needs only the camera, not a path from the player. A known
                # reference on screen is tapped directly; any other object the minimap shows is reached the big-map
                # way (tap it on the area map, close, tap the middle). Player-relative steps are only for fog.
                known = collectibles.find(frame, explored=not free, farm=farm, area=home_area or "")
                if known:
                    name, kind, target, score = known[0]
                    goal = None
                    log.info("known %s %r on screen at %s (%.2f): tapping it", kind, name, target, score)
                elif goal in ("item", "monster", "building") and map_tries < AREA_MAP_TRIES and not goal_direct                         and fog_worked():
                    map_tries += 1
                    kinds = tuple(k for k in ("statue", "item", "monster") + (("building",) if buildings_ok else ())
                                  if (items_ok or k != "item") and (fight or k != "monster"))
                    why = goto.go_to(dev, det, zone_picker(det, kinds, home_area))
                    log.info("big-map walk to the nearest %s: %s", "/".join(kinds), why)
                    if why == "arrived":
                        progress(("map_walk", map_tries))
                        continue
                    # Not on the big map (or blocked): fall back to the minimap step toward it.
                if target is None:
                    # Nothing on the minimap: anything we've met before and can see on screen (R-131; the store's
                    # explored gate decides whether it's worth tapping here).
                    if map_tries < AREA_MAP_TRIES and not objects_done and fog_worked():
                        # mae, 2026-11-05: open the big map, tap the nearest dot or structure (the camera centres on
                        # it), close the map and tap the middle of the screen, where the element now is.
                        map_tries += 1
                        kinds = tuple(k for k in ("statue", "item", "monster") + (("building",) if buildings_ok else ())
                                      if (items_ok or k != "item") and (fight or k != "monster"))
                        pick = zone_picker(det, kinds, home_area)
                        why = goto.go_to(dev, det, pick)
                        log.info("area-map walk to the nearest %s: %s", "/".join(kinds), why)
                        if why == "no_target" and free and not goto.same_area(goto.area_name_here(det), home_area):
                            log.info("no object found from outside %s; walking back first", home_area)
                            back = goto.go_to(dev, det, home_area)
                            if back != "arrived":
                                log.warning("STUCK %s: can't walk back into it (%s)", home_area, back)
                                return "not_in_zone"
                            continue
                        if why == "no_target" and free and not objects_done:
                            # Nothing left on the minimap or the big map for this zone: what's left is under fog
                            # (live 2026-11-10: Jungle Camp at 93% stopped here without a single fog-edge step).
                            # Sweep the zone's fog edges (R-146: walkable ground next to fog), then stop.
                            log.info("no object left in %s on either map: sweeping its fog edges", home_area)
                            objects_done = True
                        if why == "arrived":
                            here_xy = goto.coords(det)
                            if here_xy and any(max(abs(here_xy[0] - a[0]), abs(here_xy[1] - a[1])) <= 2
                                               for a in map_arrivals):
                                log.warning("STUCK %s: the big-map walk keeps ending at %s; the object there isn't "
                                            "taken by walking onto it (a statue icon reads as a monster dot): "
                                            "sweeping fog edges instead", home_area, here_xy)
                                objects_done = True
                                continue
                            if here_xy:
                                map_arrivals.append(here_xy)
                            continue
                if target and goal and LAST_GOAL_XY is not None:
                    # Live 2026-11-10 (Verdantglade VII, 87%): a "monster 6 tiles away" on the minimap pulled the walk
                    # back and forth between (83,110) and (85,108) for 2 minutes while the monster on screen stood
                    # elsewhere. A goal tile that several taps don't reach is left for this walk.
                    g = tuple(LAST_GOAL_XY)
                    goal_taps[g] = goal_taps.get(g, 0) + 1
                    if goal_taps[g] > GOAL_TAPS_MAX:
                        log.warning("STUCK %s: %d walk taps toward the %s at map %s didn't reach it; leaving it",
                                    home_area, GOAL_TAPS_MAX, goal, g)
                        outside.add(g)
                        continue
                if target:
                    log.info("walking toward unexplored ground at %s (map %s)", target, spot)
                    last_tap = spot
                    last_plan = frame
                    # Only taps aimed at an object feed the store (a walk can be interrupted by anything).
                    tapped = (frame, target, goal) if goal and target else None
                    if goal_direct and goal == "monster":
                        tap_object(dev, det, target, wait=3)  # walks beside it when the tap alone does nothing
                        continue
                    dev.tap(*off_me(det, target, frame))
                    time.sleep(3)
                    continue
                me = player_on_screen(det, frame)
                mm_now = minimap.read(frame, not free)
                target = fog_edge_target(frame, valid=lambda p: walkable_at(mm_now, me, p))
                fog_misses = fog_misses + 1 if target is None else 0
                if target is None:
                    no_fog += 1
                    if no_fog >= 4:
                        if objects_done:
                            log.warning("STUCK %s: no object on either map and no walkable fog edge in view, and the "
                                        "%% isn't 100: the rest is behind something we don't handle yet (a gate "
                                        "card, a puzzle)", home_area)
                            return "no_objects"
                        return "no_fog"
                    dev.swipe(*random.choice([(360, 800, 360, 450), (360, 400, 360, 750),
                                              (550, 600, 200, 600), (200, 600, 550, 600)]), 500)
                    time.sleep(1.5)
                    continue
                no_fog = 0
                log.info("walking to fog edge at %s", target)
                last_tap = to_world(xy, player_on_screen(det, frame), target)
                dev.tap(*off_me(det, target, frame))
                time.sleep(3)
            elif d.state == "battle_prep" and tapped and tapped[2] == "monster" and not saved_fight:
                collectibles.save(tapped[0], tapped[1], "monster", "monster", home_area or "")
                saved_fight = True  # once per fight; the next branch handles the prep screen itself
            elif d.state == "battle_prep" and not fight:
                log.info("battle prep in an explored area: backing out (monsters there respawn; R-065)")
                ui.tap(dev, ui.BACK_ARROW, 2)
            elif d.state == "battle_prep":
                if hud_hp(dev.screenshot(), PREP_HP_BAR) * 100 < heal.FIGHT_MIN_HP and heal_tries < 2:
                    heal_tries += 1
                    log.info("battle prep: HP under %d%%; healing from the portrait", heal.FIGHT_MIN_HP)
                    # Quick Heal opens from the portrait on any screen that shows it (mae); without one, back out and
                    # let the map branch heal.
                    heal.quick_heal(dev, det, heal.BACK_OUT)
                    continue
                ui.tap(dev, ui.START_BATTLE, 3)
                tapped, saved_fight = None, False
            elif pass_through(dev, d):
                pass  # fights, loading, dialogue, reward popups
            elif d.state == "defeated":
                card, choice = decider.decide(ctx)
                dev.tap(*choice.point)
                return "defeated"
            elif d.state == "player_profile":
                ui.tap(dev, ui.ABOVE_POPUP, 1.5)
            elif d.state in TOWER_STATES:
                # A tower opened from here: hand over to the tower loop, then come back to this area (mae: loops call
                # each other). Mini-dungeon floors need no hand-over: their cards and fights are handled below.
                if tower.done_today():  # R-079: one climb a day, never retry a loss
                    log.info("tower already climbed today; leaving it")
                else:
                    climbed = tower.climb(dev, det, minutes=max(1.0, (deadline - time.monotonic()) / 60))
                    log.info("tower climb: %s", climbed)
                    if climbed in tower.OK:
                        tower.mark_done()
                Navigator(dev, det).go_home()
                if home_area:
                    ui.tap(dev, ui.NAV_WORLD, 4)
                    goto.go_to(dev, det, home_area)
            elif d.state == "area_map":
                ui.tap(dev, ui.BACK_ARROW, 2)  # left open by a big-map walk that didn't move us: close it
            elif d.state == "home":
                return f"left_area:{d.state}"
            elif d.state == "dialogue_choice":
                # Live 2026-11-10 (Monolith Ruins II): a box puzzle's NPC, Fonik ("Present a Golden Beetle, and I
                # shall unveil its truth": Help me solve this! / Reset the puzzle. / Leave). The card decider tapped
                # above it five times (it doesn't close) and the walk stopped. Using the rare Golden Beetle is mae's
                # call: take "Leave", note the puzzle as the zone's objective, and walk around it.
                lines = det.read_text([60, 300, 600, 750])
                leave = [b for t, b in lines if re.fullmatch(r"\s*Leave\.?\s*", t)]
                texts = " / ".join(t for t, _ in lines)
                if not leave:
                    log.warning("dialogue choice with no Leave option (%s); stopping", texts)
                    return "needs_decision"
                puzzle = bool(re.search(r"puzzle|Golden Beetle", texts + " " + " ".join(
                    t for t, _ in det.read_text([0, 1150, 720, 130])), re.I))
                log.info("dialogue choice (%s): taking Leave%s", texts, " (a puzzle: noted, walking around it)"
                         if puzzle else "")
                if puzzle:
                    note_objective("Puzzle (Fonik: Golden Beetle solves it)", "dismiss", goto.coords(det) or last_tap)
                if last_tap:
                    outside.add(tuple(last_tap))
                    if last_tap not in bumped:
                        bumped.append(last_tap)
                ui.tap(dev, ui.centre(leave[0]), 2)
            elif d.state in ("battle", "loading"):
                # An auto battle (a mini-dungeon floor, "Round 3/25") or a loading screen: wait. Live 2026-11-10
                # (Ironvein Pit): the battle went to the card decider, which read the damage numbers as card titles
                # ("1159", "1140") and tapped the round counter to "dismiss" them.
                time.sleep(3)
                progress(("battle", d.text or ""))
            elif (gate := elemental_gate(dev, det)) is not None:
                # Gate of Wind and the other Gates of Elements: free with our companions' affinity (R-057).
                note_objective("Gate of Elements", gate, goto.coords(det) or last_tap)
                if gate == "short" and last_tap:
                    outside.add(tuple(last_tap))
                progress(("elemental_gate", gate))
                # mae, 2026-11-10: each Lucky Wheel's first spin is free while its zone is unexplored (once explored a
                # spin costs). Jungle Camp's last 7% was this spin. Pressed only when the button shows no cost.
                log.info("Lucky Wheel in an unexplored zone, no cost shown: taking the free spin")
                wheel_spun = True
                ui.tap(dev, WHEEL_SPIN, 8)
                ui.tap(dev, ui.BELOW_POPUP, 2)  # "YOU RECEIVED"
                progress(("wheel_spin", home_area))
            else:
                # Cards, dialogs and unknown popups: the same rules as the quest loop.
                card, choice = decider.decide(ctx)
                # mae, 2026-11-10: keep a list of every objective a zone has (statues, chests, wheels, portals,
                # gates...) in the location tree, so what a walk missed shows up there.
                note_objective(card.title, choice.action, goto.coords(det))
                if (tapped and tapped[2] == "building" and card.title and card.title != last_card
                        and choice.action != "dismiss"):  # a card we act on: not a social popup or an unknown one
                    collectibles.save(tapped[0], tapped[1], card.title, "interactable", home_area or "")
                tapped = None
                repeats = repeats + 1 if card.title == last_card else 0
                last_card = card.title
                if choice.action == "dismiss" and last_tap and last_tap not in bumped:
                    bumped.append(last_tap)
                    if not re.search(r"Goddess Statue", card.title or ""):
                        # No more goals around it this walk. Not for a statue that isn't ready yet: the pickups
                        # round it are what it waits for (live 2026-11-10, Zephyr Vale at 66%: a chest, a Destiny
                        # Fruit and an ore pile beside its Lost Goddess Statue were left; by hand they made 100%).
                        outside.add(tuple(last_tap))
                    k = tree.key(home_area or "")
                    if k and card.title and re.search(r"Statue|Gate|Wheel|Rankings", card.title):
                        spots = tree.zones[k].setdefault("dismissed_spots", [])
                        if list(last_tap) not in spots:
                            spots.append(list(last_tap))
                            tree.save()
                    log.info("card %r opened from the tap at map %s: walking around that spot from now on",
                             card.title, last_tap)
                if choice.action == "dismiss" and re.search(r"Required Item|Insufficient items", card.body or ""):
                    # A blocker that needs an item we don't have (Boulder Blockade: a Magic Drill). The zone waits for
                    # it; say so instead of circling (live 2026-11-10, Hidden Camp).
                    need = re.search(r"Use an? ([A-Z][\w ]+?) to", card.body or "")
                    why = f"{card.title.strip()} needs {need.group(1) if need else 'an item'}"
                    log.warning("STUCK %s: %s", home_area, why)
                    k = tree.key(home_area or "")
                    if k:
                        tree.zones[k]["blocked"] = why
                        tree.save()
                    ui.tap(dev, choice.point, 2)
                    return "blocked_item"
                if choice.action == "dismiss" and card.title:
                    dismissed[card.title] = dismissed.get(card.title, 0) + 1
                    if dismissed[card.title] == 2 and buildings_ok:
                        # Live 2026-11-09: the Sealed Stone Gate (the gold "!" structure on Verdantglade V's north
                        # edge) was the nearest structure again and again; every walk reopened its card. A structure
                        # whose card we can only dismiss is a blocker, not a goal: skip that spot (and others like it),
                        # not every structure (live 2026-11-10: after a Lost Goddess Statue it skipped all structures
                        # and walked past Wildbloom Coast's chest).
                        here_xy = goto.coords(det)
                        if here_xy:
                            outside.add(tuple(here_xy))
                        log.warning("STUCK %s: %r can only be dismissed (no rule); skipping it, not other structures",
                                    home_area, card.title)
                        if home_area and tree.key(home_area):
                            z = tree.zones[tree.key(home_area)]
                            note = f"blocked: {card.title.strip()} near {here_xy} (no rule; dismissed)"
                            if note.split(" near ")[0] not in (z.get("notes") or ""):
                                z["notes"] = ((z.get("notes") or "") + " " + note).strip()
                                tree.save()
                ui.tap(dev, choice.point, 3)
                if choice.kind == "power_gate":
                    # A Gate of Power walls off one way, not the whole zone (live 2026-11-10: Verdantglade VIII at 50%
                    # stopped at a 30.5K gate by Bubble Lake with half the zone left elsewhere). Walk around its spot
                    # from now on; stop only when gates keep coming back.
                    gates += 1
                    here_xy = goto.coords(det)
                    for spot in (here_xy, last_tap):
                        if spot:
                            outside.add(tuple(spot))
                    if gates >= GATE_LIMIT:
                        log.info("blocked by %r (needs more power) %d times: this area's wall", card.title, gates)
                        return "power_gate"
                    log.info("blocked by %r (needs more power) near %s: walking around it", card.title, here_xy)
                    continue
                if repeats >= REPEAT_LIMIT:
                    log.warning("card %r keeps coming back; stopping", card.title)
                    return "repeating_card"
        return "timeout"


def _args(p) -> None:
    p.add_argument("--farm", action="store_true",
                   help="in an explored area, fight and take stamina pickups too (keeps 70 stamina)")
    p.add_argument("--minutes", type=float, default=20,  # an outer ceiling only: the runner's progress check ends
                   help="upper limit; normally the 2-minute progress check ends the run")  # a stuck run (mae)
    p.add_argument("--area", help="area to explore, as named on the area map (walks there first)")


def _run(ctx, opts):
    return walk(ctx.dev, ctx.det, opts.minutes, opts.area, farm=opts.farm)


# Ends that mean the area ran out of things to do, not that something went wrong.
OK = {"no_fog", "timeout", "power_gate", "stuck", "no_objects", "object_unreachable", "zone_done", "not_in_zone", "blocked_item"}
LOOP = Loop("fogwalk", "Fog Walk", "explore one side area: minimap targets, then the fog edge", _run, _args, ok=OK)
