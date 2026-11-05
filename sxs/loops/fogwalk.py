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
from ..core.loop import Loop, banner
from ..core.nav import Navigator
from ..policy.decide import Context, Decider
from ..vision import minimap
from ..vision.hp import PREP_HP_BAR
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


def minimap_target(det, frame: np.ndarray, lookahead: int = 4, player_xy=None,
                   buildings_seen: Optional[set] = None, items_ok: bool = True,
                   player: Optional[tuple[int, int]] = None) -> Optional[tuple[int, int]]:
    """Plan on the minimap: shortest walkable path to the nearest pickup or unexplored walkable tile, else to a gold
    building not visited yet this run (dungeons, mines: interactable; their cards go through the rules), then tap
    a few tiles along it (relative to the player, found by its name label). None if nothing is reachable."""
    mm = minimap.read(frame)
    goals = minimap.GOALS if items_ok else tuple(g for g in minimap.GOALS if g != "item")
    path = minimap.path_to_nearest(mm, goals=goals)
    if len(path) < 2 and player_xy is not None and buildings_seen is not None:
        skip = {tile for tile in mm.tiles("building") if minimap.world_tile(mm, tile, player_xy) in buildings_seen}
        path = minimap.path_to_nearest(mm, goals=("building",), skip=skip)
        if len(path) >= 2:
            spot = minimap.world_tile(mm, path[-1], player_xy)
            buildings_seen.add(spot)
            log.info("heading for a gold building at map %s", spot)
            lookahead = len(path)  # walk all the way: the tap on it opens its card
    if len(path) < 2:
        return None
    if mm.grid[path[-1][0]][path[-1][1]] == "monster":
        log.info("heading for a monster %d tiles away", len(path) - 1)
        lookahead = len(path)  # tap the monster itself: walking onto it starts the fight
    player = player or player_on_screen(det, frame)
    if player is None:
        return None
    return minimap.screen_point(player, mm, path[min(lookahead, len(path) - 1)])


def walk(dev, det, minutes: float = 10, area: Optional[str] = None,
         allowed: Optional[set[str]] = None, walk_there: bool = True) -> str:
    """Explore `area` (walking there first with the area map unless walk_there is False), or the area we're
    standing in. `allowed` names neighbouring areas it may stand in without walking back: mae, 2026-11-04, "try
    moving from areas you are connected to": enter a new area from the explored one next to it, not by a long
    area-map walk that lands at its fogged label."""
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
    stamina_unread = False
    if area and walk_there:
        goto.go_to(dev, det, area)
    # Map coordinates of walk taps that opened a card we dismissed (a blessed statue, a sign). Kept in map
    # coordinates: centre_player and the edge pointer move the camera, so screen points don't stay put.
    bumped: list[tuple[int, int]] = []
    beat = Heartbeat()
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
            if home_area is None and name:
                home_area = name
            elif (name and not goto.same_area(name, home_area) and not strayed
                  and not any(goto.same_area(name, a) or goto.squeeze(name)[:7] == goto.squeeze(a)[:7] for a in allowed)):
                # Wandered into a neighbouring area: walk back with the area map rather than exploring the wrong one.
                strayed = True
                log.info("left %s for %s; going back", home_area, name)
                goto.go_to(dev, det, home_area)
                continue
            elif name and goto.same_area(name, home_area):
                strayed = False
            # Watchdog: progress means standing on a tile we haven't stood on this run. Taps that don't move us,
            # or that bounce between the same few tiles, mean we're blocked: stop instead of idling.
            if d.text and d.text not in visited:
                visited.add(d.text)
                last_xy, still, progress_at = d.text, 0, time.monotonic()
            else:
                still += 1
                # Monsters in brackets guard the way into the area: fight one, then walk on.
                if still in (2, 3) and attack_guard(dev, det, frame):
                    continue
                if still >= STILL_LIMIT:
                    log.warning("no new tile for %d taps (at %s, %d tiles visited); stopping", still, d.text,
                                len(visited))
                    return "stuck"
            if centre_player(dev, det, frame):
                frame = dev.screenshot()
            # Pickups cost 5 stamina; keep the 70 the daily commissions need (R-107).
            stamina = read_stamina(det, frame=frame)
            if stamina is None and not stamina_unread:
                stamina_unread = True
                log.info("stamina not readable; skipping stamina pickups until it is")
            elif stamina is not None:
                stamina_unread = False
            items_ok = stamina is not None and stamina >= STAMINA_KEEP + COST
            xy = goto.COORDS.search(d.text or "")
            xy = (int(xy.group(1)), int(xy.group(2))) if xy else None
            player = player_on_screen(det, frame)
            target = minimap_target(det, frame, player_xy=xy, buildings_seen=buildings_seen, items_ok=items_ok,
                                    player=player)
            if target is None and recentre_on_player(dev, det, frame):
                frame = dev.screenshot()
                player = player_on_screen(det, frame)
                target = minimap_target(det, frame, player_xy=xy, buildings_seen=buildings_seen, items_ok=items_ok,
                                        player=player)
            spot = to_world(xy, player, target) if target else None
            if spot and any(max(abs(spot[0] - b[0]), abs(spot[1] - b[1])) <= 1 for b in bumped):
                # The path runs through something that opens a card (seen: a blessed Goddess Statue). Tapping it
                # again just reopens the card, so step one tile to the side; the game paths around the rest.
                side = minimap.SCREEN_TILE if len(bumped) % 2 else -minimap.SCREEN_TILE
                target = (min(690, max(30, target[0] + side)), target[1] + minimap.SCREEN_TILE // 2)
                spot = to_world(xy, player, target)
                log.info("map %s opened a card before; stepping aside to %s", spot, target)
            if target:
                log.info("walking toward unexplored ground at %s (map %s)", target, spot)
                last_tap = spot
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
        elif d.state == "battle_prep":
            if hud_hp(dev.screenshot(), PREP_HP_BAR) * 100 < heal.FIGHT_MIN_HP and heal_tries < 2:
                heal_tries += 1
                log.info("battle prep: HP under %d%%; healing from the portrait", heal.FIGHT_MIN_HP)
                # Quick Heal opens from the portrait on any screen that shows it (mae); without one, back out and
                # let the map branch heal.
                heal.quick_heal(dev, det, heal.BACK_OUT)
                continue
            ui.tap(dev, ui.START_BATTLE, 3)
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
            log.info("tower climb: %s", tower.climb(dev, det, minutes=max(1.0, (deadline - time.monotonic()) / 60)))
            Navigator(dev, det).go_home()
            if home_area:
                ui.tap(dev, ui.NAV_WORLD, 4)
                goto.go_to(dev, det, home_area)
        elif d.state == "home":
            return f"left_area:{d.state}"
        else:
            # Cards, dialogs and unknown popups: the same rules as the quest loop.
            card, choice = decider.decide(ctx)
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
    p.add_argument("--minutes", type=float, default=20,  # an outer ceiling only: the runner's progress check ends
                   help="upper limit; normally the 2-minute progress check ends the run")  # a stuck run (mae)
    p.add_argument("--area", help="area to explore, as named on the area map (walks there first)")


def _run(ctx, opts):
    return walk(ctx.dev, ctx.det, opts.minutes, opts.area)


# Ends that mean the area ran out of things to do, not that something went wrong.
OK = {"no_fog", "timeout", "power_gate", "stuck"}
LOOP = Loop("fogwalk", "Fog Walk", "explore one side area: minimap targets, then the fog edge", _run, _args, ok=OK)
