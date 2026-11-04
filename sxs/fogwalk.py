"""Explore side areas that have no quest marker: walk to unexplored ground the minimap shows (falling back to the
fog edge). No model calls.

    python -m sxs.fogwalk [--minutes 10]

Each step finds where the fog (light, unsaturated grey) meets the map, taps a walkable spot just outside it, and
lets the explore loop's handlers deal with whatever happens (fights, cards, pickups). Many side areas give
resources and levels but have no quest (mae, 2026-11-03).
"""

from __future__ import annotations

import argparse
import logging
import random
import sys
import time
from typing import Optional

import cv2
import numpy as np

from . import goto, minimap, nav, tower
from .decide import Context, Decider
from .device import Device, banner, save_unknown
from .explore import (FIGHT_MIN_HP, GUARD_DX, GUARD_DY, HUD_PORTRAIT, PLAYER_NAME, QUICK_HEAL, REPEAT_LIMIT,
                      Heartbeat, hud_hp)
from .state import StateDetector

log = logging.getLogger("sxs.fogwalk")

PLAY_AREA = (0, 130, 720, 840)  # x, y, w, h of the map between the HUD and the chat/tracker strip
FOG_S_MAX, FOG_V_MIN = 40, 150  # fog is pale grey
STEP_IN = 40  # px from the fog edge into clear ground
STILL_LIMIT = 8  # walk taps with unchanged coordinates before giving up
AREA_NAME_ROI = [500, 255, 220, 36]  # area name above the coordinates, under the minimap
HUD_AVATAR = (130, 130)  # matches of the player's face inside this top-left box are the HUD, not the pointer


def area_name(det: StateDetector, frame) -> str:
    return " ".join(t for t, _ in det.read_text(AREA_NAME_ROI, frame)).strip()


def centre_player(dev: Device, det: StateDetector, frame) -> bool:
    """Drag the map so our character (found by its name label) sits mid-screen: targets planned from the minimap
    land a few tiles away, and near the edge they fall off screen or onto the HUD."""
    me = [b for t, b in det.read_text([0, 130, 720, 840], frame) if PLAYER_NAME in t]
    if not me:
        return False
    x, y, w, h = me[0]
    px, py = x + w // 2, y - 40
    cx, cy = PLAY_AREA[0] + PLAY_AREA[2] // 2, PLAY_AREA[1] + PLAY_AREA[3] // 2
    if abs(px - cx) < 160 and abs(py - cy) < 200:
        return False
    dev.swipe(px, py, cx, cy, 600)
    time.sleep(1.5)
    return True


def recentre_on_player(dev: Device, det: StateDetector, frame) -> bool:
    """The camera doesn't follow the player. Tap our own edge pointer to bring the camera back to us."""
    for x, y, w, h in det.find_all("Explore.PlayerPointer", frame):
        if x < HUD_AVATAR[0] and y < HUD_AVATAR[1]:
            continue
        dev.tap(x + w // 2, y + h // 2)
        time.sleep(1.5)
        return True
    return False


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


def minimap_target(det: StateDetector, frame: np.ndarray, lookahead: int = 4, player_xy=None,
                   buildings_seen: Optional[set] = None) -> Optional[tuple[int, int]]:
    """Plan on the minimap: shortest walkable path to the nearest pickup or unexplored walkable tile, else to a gold
    building not visited yet this run (dungeons, mines: interactable; their cards go through the rules), then tap
    a few tiles along it (relative to the player, found by its name label). None if nothing is reachable."""
    mm = minimap.read(frame)
    path = minimap.path_to_nearest(mm)
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
    me = [b for t, b in det.read_text([0, 130, 720, 840], frame) if PLAYER_NAME in t]
    if not me:
        return None
    x, y, w, h = me[0]
    player = (x + w // 2, y - 40)  # the label sits under the character's feet
    return minimap.screen_point(player, mm, path[min(lookahead, len(path) - 1)])


def walk(dev: Device, det: StateDetector, minutes: float = 10, area: Optional[str] = None) -> str:
    """Explore `area` (walking there first with the area map), or the area we're standing in."""
    banner(log, "Fog Walk", "explore a side area with no quest marker: walk to unexplored tiles the minimap shows, "
           "else to the fog edge; fight and open cards on the way",
           f"{minutes:g} minutes, no fog in view after 4 pans, no new tile reached in "
           f"{STILL_LIMIT} walk taps, a lost fight, or an unfamiliar screen")
    decider, ctx = Decider(det), Context(goal="explore")
    deadline = time.monotonic() + minutes * 60
    no_fog = unknowns = still = 0
    last_xy, progress_at = None, time.monotonic()
    home_area, strayed = area, False
    visited: set[str] = set()
    repeats, last_card = 0, None
    buildings_seen: set = set()
    heal_tries = 0
    if area:
        goto.go_to(dev, det, area)
    beat = Heartbeat()
    while time.monotonic() < deadline:
        d = det.detect()
        beat.check(d, last_xy, progress_at)
        unknowns = unknowns + 1 if d.state == "unknown" else 0
        if unknowns >= 5:
            log.warning("unfamiliar screen; frame saved to %s", save_unknown(dev, "fogwalk"))
            return "unknown_screen"
        if d.state == "world_map":
            frame = dev.screenshot()
            if hud_hp(frame) * 100 < FIGHT_MIN_HP and heal_tries < 2:
                # mae, 2026-11-04: heal before any fight; walking can bump into one. The profile opens from the HUD.
                heal_tries += 1
                log.info("HP under %d%%; healing from the profile", FIGHT_MIN_HP)
                dev.tap(*HUD_PORTRAIT)
                time.sleep(2)
                if det.detect().state == "player_profile":
                    dev.tap(*QUICK_HEAL)
                    time.sleep(2)
                    dev.tap(360, 60)
                    time.sleep(1.5)
                continue
            heal_tries = 0 if hud_hp(frame) * 100 >= FIGHT_MIN_HP else heal_tries
            name = area_name(det, frame)
            if home_area is None and name:
                home_area = name
            elif name and not goto.same_area(name, home_area) and not strayed:
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
                guard = det.find("Explore.GuardBracket", frame) if still in (3, 6) else None
                if guard:
                    # Monsters in brackets guard the way into the area: fight one, then walk on.
                    log.info("blocked; attacking a guard at %s", guard.box)
                    dev.tap(guard.box[0] + GUARD_DX, guard.box[1] + GUARD_DY)
                    time.sleep(3)
                    continue
                if still >= STILL_LIMIT:
                    log.warning("no new tile for %d taps (at %s, %d tiles visited); stopping", still, d.text,
                                len(visited))
                    return "stuck"
            if centre_player(dev, det, frame):
                frame = dev.screenshot()
            xy = goto.COORDS.search(d.text or "")
            xy = (int(xy.group(1)), int(xy.group(2))) if xy else None
            target = minimap_target(det, frame, player_xy=xy, buildings_seen=buildings_seen)
            if target is None and recentre_on_player(dev, det, frame):
                frame = dev.screenshot()
                target = minimap_target(det, frame, player_xy=xy, buildings_seen=buildings_seen)
            if target:
                log.info("walking toward unexplored ground at %s", target)
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
            dev.tap(*target)
            time.sleep(3)
        elif d.state == "battle_prep":
            dev.tap(360, 956)
            time.sleep(3)
        elif d.state in ("battle", "loading"):
            time.sleep(2)
        elif d.state in ("dialogue",):
            dev.tap(*nav.DIALOGUE_NEXT)
            time.sleep(1.2)
        elif d.state in ("reward_popup", "tap_to_continue"):
            dev.tap(*nav.REWARD_CLOSE)
            time.sleep(1.2)
        elif d.state == "defeated":
            card, choice = decider.decide(ctx)
            dev.tap(*choice.point)
            return "defeated"
        elif d.state == "player_profile":
            dev.tap(360, 60)
            time.sleep(1.5)
        elif d.state in ("tower_list", "tower_floors", "tower_result"):
            # A tower opened from here: hand over to the tower loop, then come back to this area (mae: loops call
            # each other). Mini-dungeon floors need no hand-over: their cards and fights are handled below.
            log.info("tower climb: %s", tower.climb(dev, det, minutes=max(1.0, (deadline - time.monotonic()) / 60)))
            nav.Navigator(dev, det).go_home()
            if home_area:
                dev.tap(*nav.NAV_WORLD)
                time.sleep(4)
                goto.go_to(dev, det, home_area)
        elif d.state == "home":
            return f"left_area:{d.state}"
        else:
            # Cards, dialogs and unknown popups: the same rules as the quest loop.
            card, choice = decider.decide(ctx)
            repeats = repeats + 1 if card.title == last_card else 0
            last_card = card.title
            dev.tap(*choice.point)
            time.sleep(3)
            if choice.kind == "power_gate":
                log.info("blocked by %r (needs more power): this area's wall", card.title)
                return "power_gate"
            if repeats >= REPEAT_LIMIT:
                log.warning("card %r keeps coming back; stopping", card.title)
                return "repeating_card"
    return "timeout"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--minutes", type=float, default=10)
    p.add_argument("--area", help="area to explore, as named on the area map (walks there first)")
    args = p.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    dev = Device()
    print(walk(dev, StateDetector(dev), args.minutes, args.area), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
