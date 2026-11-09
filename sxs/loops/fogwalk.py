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
from ..policy.decide import Context, Decider
from ..policy.zones import Tree
from ..vision import minimap
from ..vision.hp import PREP_HP_BAR
from ..vision import area_map, collectibles
from ..vision.hud import read_stamina
from ..vision.player import player_on_screen
from . import tower
from .explore import REPEAT_LIMIT, hud_hp
from .gather import COST

log = logging.getLogger("sxs.loops.fogwalk")

FOG_S_MAX, FOG_V_MIN = 40, 150  # fog is pale grey
STEP_IN = 40  # px from the fog edge into clear ground
STILL_LIMIT = 4  # walk taps with unchanged coordinates before giving up (a tap takes 5-7 s; runs are 1-2 min)
STAMINA_KEEP = 70  # R-107: stamina kept for the daily commissions
REWARD_TAPS_MAX = 3  # tracker gift taps per walk: a gift that stays after this many taps isn't claimable from here


def fog_edge_target(frame: np.ndarray) -> Optional[tuple[int, int]]:
    """A tap point on clear ground right next to the fog, nearest the screen centre (with a little randomness so
    repeated calls spread along the edge). None if there's no fog in view."""
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
    pick = random.choice(np.argsort(d)[:200])
    return int(xs[pick] + x0), int(ys[pick] + y0)


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
    global LAST_GOAL
    LAST_GOAL = None
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
    path = minimap.path_to_nearest(mm, goals=objects, skip=off, cross_border=cross_border) if objects else []
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
        labels = map_labels(det, frame) if home else None
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
    decider, ctx = Decider(det), Context(goal="explore")
    deadline = time.monotonic() + minutes * 60
    unknown = UnknownScreens(in_a_row=5)
    no_fog = still = 0
    last_xy, progress_at = None, time.monotonic()
    home_area, strayed = area, False
    visited: set[str] = set()
    repeats, last_card = 0, None
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
    map_arrivals: list = []  # where big-map walks to an object ended (a repeat means we can't take it)
    outside: set = set()  # map coordinates where we found ourselves in another zone (R-132)
    tapped, saved_fight = None, False  # (frame, screen point) of the last walk tap, for the collectibles store
    free = not area_blessed(dev, det, area)  # unexplored: fights and pickups cost nothing (R-065)
    fight = free or farm
    log.info("area %s: pickups %s, fights %s", "still unexplored" if free else "explored",
             "free" if free else ("farming" if farm else "off"), "on" if fight else "off")
    # Map coordinates of walk taps that opened a card we dismissed (a blessed statue, a sign). Kept in map
    # coordinates: centre_player and the edge pointer move the camera, so screen points don't stay put.
    bumped: list[tuple[int, int]] = []
    beat = Heartbeat()
    tree = Tree.load()  # the location tree: crossings a walk makes are written back (zones.py)
    last_zone: Optional[str] = None  # area name read on the previous map step
    last_plan = None  # the frame the last minimap walk tap was planned on

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
                      and not any(goto.same_area(name, a) or goto.squeeze(name)[:7] == goto.squeeze(a)[:7] for a in allowed)):
                    # Wandered into a neighbouring area: walk back with the area map rather than exploring the wrong one.
                    strayed = True
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
                    if fight and still in (2, 3) and attack_guard(dev, det, frame):
                        continue
                    if still >= STILL_LIMIT and map_tries < AREA_MAP_TRIES:
                        # Blocked on the minimap plan: try mae's big-map walk to the nearest dot before giving up.
                        map_tries += 1
                        kinds = tuple(k for k in ("item", "monster", "building")
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
                target = minimap_target(det, frame, player_xy=xy, buildings_seen=buildings_seen, items_ok=items_ok,
                                        player=player, monsters_ok=fight,
                                        visited_xy=stood_on, outside_xy=outside, cross_border=cross,
                                        home_light=not free, shaded_walk=not free)
                if target is None and recentre_on_player(dev, det, frame):
                    frame = dev.screenshot()
                    player = player_on_screen(det, frame)
                    target = minimap_target(det, frame, player_xy=xy, buildings_seen=buildings_seen, items_ok=items_ok,
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
                # mae, 2026-11-05: reaching an object needs only the camera, not a path from the player. A known
                # reference on screen is tapped directly; any other object the minimap shows is reached the big-map
                # way (tap it on the area map, close, tap the middle). Player-relative steps are only for fog.
                known = collectibles.find(frame, explored=not free, farm=farm, area=home_area or "")
                if known:
                    name, kind, target, score = known[0]
                    goal = None
                    log.info("known %s %r on screen at %s (%.2f): tapping it", kind, name, target, score)
                elif goal in ("item", "monster", "building") and map_tries < AREA_MAP_TRIES:
                    map_tries += 1
                    kinds = tuple(k for k in ("item", "monster", "building")
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
                    if map_tries < AREA_MAP_TRIES:
                        # mae, 2026-11-05: open the big map, tap the nearest dot or structure (the camera centres on
                        # it), close the map and tap the middle of the screen, where the element now is.
                        map_tries += 1
                        kinds = tuple(k for k in ("item", "monster", "building")
                                      if (items_ok or k != "item") and (fight or k != "monster"))
                        pick = zone_picker(det, kinds, home_area)
                        why = goto.go_to(dev, det, pick)
                        log.info("area-map walk to the nearest %s: %s", "/".join(kinds), why)
                        if why == "no_target" and free and not goto.same_area(goto.area_name_here(det), home_area):
                            log.info("no object found from outside %s; walking back first", home_area)
                            goto.go_to(dev, det, home_area)
                            continue
                        if why == "no_target" and free:
                            # Nothing left on the minimap or the big map for this zone: say so instead of pacing
                            # (live 2026-11-09). The roam loop records it as this zone's stuck point.
                            log.warning("STUCK %s: no dot, monster or structure left in this zone on the minimap or "
                                        "the big map, and the %% isn't 100: the rest is behind something we don't "
                                        "handle yet (a gate card, a puzzle, fog the map doesn't show)", home_area)
                            return "no_objects"
                        if why == "arrived":
                            here_xy = goto.coords(det)
                            if here_xy and any(max(abs(here_xy[0] - a[0]), abs(here_xy[1] - a[1])) <= 2
                                               for a in map_arrivals):
                                log.warning("STUCK %s: the big-map walk keeps ending at %s; the object there isn't "
                                            "taken by walking onto it", home_area, here_xy)
                                return "object_unreachable"
                            if here_xy:
                                map_arrivals.append(here_xy)
                            continue
                if target:
                    log.info("walking toward unexplored ground at %s (map %s)", target, spot)
                    last_tap = spot
                    last_plan = frame
                    # Only taps aimed at an object feed the store (a walk can be interrupted by anything).
                    tapped = (frame, target, goal) if goal and target else None
                    dev.tap(*target)
                    time.sleep(3)
                    continue
                target = fog_edge_target(frame)
                if target is None:
                    no_fog += 1
                    if no_fog >= 4:
                        return "no_fog"
                    dev.swipe(*random.choice([(360, 800, 360, 450), (360, 400, 360, 750),
                                              (550, 600, 200, 600), (200, 600, 550, 600)]), 500)
                    time.sleep(1.5)
                    continue
                no_fog = 0
                log.info("walking to fog edge at %s", target)
                last_tap = to_world(xy, player_on_screen(det, frame), target)
                dev.tap(*target)
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
            else:
                # Cards, dialogs and unknown popups: the same rules as the quest loop.
                card, choice = decider.decide(ctx)
                if (tapped and tapped[2] == "building" and card.title and card.title != last_card
                        and choice.action != "dismiss"):  # a card we act on: not a social popup or an unknown one
                    collectibles.save(tapped[0], tapped[1], card.title, "interactable", home_area or "")
                tapped = None
                repeats = repeats + 1 if card.title == last_card else 0
                last_card = card.title
                if choice.action == "dismiss" and last_tap and last_tap not in bumped:
                    bumped.append(last_tap)
                    log.info("card %r opened from the tap at map %s: walking around that spot from now on",
                             card.title, last_tap)
                ui.tap(dev, choice.point, 3)
                if choice.kind == "power_gate":
                    log.info("blocked by %r (needs more power): this area's wall", card.title)
                    return "power_gate"
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
OK = {"no_fog", "timeout", "power_gate", "stuck", "no_objects", "object_unreachable"}
LOOP = Loop("fogwalk", "Fog Walk", "explore one side area: minimap targets, then the fog edge", _run, _args, ok=OK)
