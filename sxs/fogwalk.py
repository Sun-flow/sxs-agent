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

from . import minimap, nav
from .decide import Context, Decider
from .device import Device
from .explore import PLAYER_NAME
from .state import StateDetector

log = logging.getLogger("sxs.fogwalk")

PLAY_AREA = (0, 130, 720, 840)  # x, y, w, h of the map between the HUD and the chat/tracker strip
FOG_S_MAX, FOG_V_MIN = 40, 150  # fog is pale grey
STEP_IN = 40  # px from the fog edge into clear ground


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


def minimap_target(det: StateDetector, frame: np.ndarray, lookahead: int = 4) -> Optional[tuple[int, int]]:
    """Plan on the minimap: shortest walkable path to the nearest pickup or unexplored walkable tile, then tap a
    few tiles along it (relative to the player, found by its name label). None if nothing is reachable."""
    mm = minimap.read(frame)
    path = minimap.path_to_nearest(mm)
    if len(path) < 2:
        return None
    me = [b for t, b in det.read_text([0, 130, 720, 840], frame) if PLAYER_NAME in t]
    if not me:
        return None
    x, y, w, h = me[0]
    player = (x + w // 2, y - 40)  # the label sits under the character's feet
    return minimap.screen_point(player, mm, path[min(lookahead, len(path) - 1)])


def walk(dev: Device, det: StateDetector, minutes: float = 10) -> str:
    decider, ctx = Decider(det), Context(goal="explore")
    deadline = time.monotonic() + minutes * 60
    no_fog = 0
    while time.monotonic() < deadline:
        d = det.detect()
        if d.state == "world_map":
            frame = dev.screenshot()
            target = minimap_target(det, frame)
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
        else:
            # Cards, dialogs and unknown popups: the same rules as the quest loop.
            card, choice = decider.decide(ctx)
            dev.tap(*choice.point)
            time.sleep(3)
    return "timeout"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--minutes", type=float, default=10)
    args = p.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    dev = Device()
    print(walk(dev, StateDetector(dev), args.minutes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
