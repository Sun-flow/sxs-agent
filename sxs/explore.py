"""Finish an "Explore <area>" quest by following the quest-tracker marker. No model calls.

    python -m sxs.explore [--minutes 20]

Loop: on the island map, find the gold tracker ring (resource/pipeline/explore.json) and tap it. At a screen edge
that pans the camera to the target; on the map it walks there and collects or starts a fight. Fights, dialogue
and reward popups are handled as they come. Stops when the tracker shows 100/100 (and claims it), when no marker
can be found, or on a screen it doesn't know.
"""

from __future__ import annotations

import argparse
import logging
import sys
import time

import cv2
import numpy as np

from . import nav
from .device import Device
from .decide import Context, Decider
from .state import StateDetector

log = logging.getLogger("sxs.explore")

TRACKER_PANEL = (304, 982)  # quest tracker panel on the map; claims the reward at 100/100
TRACKING_TOGGLE = (290, 1012)  # target icon on the panel: Tracking On/Off
START_BATTLE = (360, 956)
PAN_CENTER = (360, 560)  # where a hidden marker is dragged to
MARKER_TARGET_DY = 100
STALE_LIMIT = 4
GUARD_DX, GUARD_DY = -35, 50  # from the top-right guard bracket to the monster  # the target sits about this far below the centre of the tracker ring


def tracking_on(frame: np.ndarray) -> bool:
    """The target icon on the tracker panel is bright yellow when tracking is on, dim grey when off."""
    x, y = TRACKING_TOGGLE
    patch = cv2.cvtColor(frame[y - 12:y + 12, x - 12:x + 12], cv2.COLOR_BGR2HSV)
    return float(np.percentile(patch[:, :, 2], 90)) > 150


def follow_tracker(dev: Device, det: StateDetector, minutes: float = 20, max_misses: int = 6) -> str:
    """Returns "complete", "defeated", "no_marker", "unknown_screen" or "timeout"."""
    decider, ctx = Decider(det), Context(goal="explore")
    deadline = time.monotonic() + minutes * 60
    misses = unknowns = unknown_total = 0
    last_progress = last_state = last_progress_seen = None
    stale = 0  # map visits in a row with no change in progress
    while time.monotonic() < deadline:
        d = det.detect()
        if d.state != last_state:
            log.info("state %s", d.state)
            last_state = d.state
        if d.state != "unknown":
            unknowns = 0
        if d.state == "world_map":
            prog = det.find("Explore.Progress")
            if prog and prog.text != last_progress:
                last_progress = prog.text
                log.info("progress: %s", prog.text)
            if det.find("Explore.Complete"):
                dev.tap(*TRACKER_PANEL)
                time.sleep(2)
                log.info("explore quest complete, reward claimed")
                return "complete"
            if prog and prog.text == last_progress_seen:
                stale += 1
            else:
                stale, last_progress_seen = 0, prog.text if prog else None
            if stale >= STALE_LIMIT:
                # Progress stuck while acting on the marker: the target may be guarded. Fight a bracketed monster.
                guard = det.find("Explore.GuardBracket")
                if guard:
                    log.info("progress stuck; attacking a guard at %s", guard.box)
                    dev.tap(guard.box[0] + GUARD_DX, guard.box[1] + GUARD_DY)
                    stale = 0
                    time.sleep(3)
                    continue
            marker = det.find("Explore.Marker")
            if marker:
                misses = 0
                x, y, w, h = marker.box
                cx, cy = x + w // 2, y + h // 2
                at_edge = cx < 60 or cx > 660 or cy < 150 or cy > 900
                # The ring floats above its target: tap the ring itself to pan, the spot under it to act.
                dev.tap(cx, cy if at_edge else cy + MARKER_TARGET_DY)
                time.sleep(3)
                continue
            hidden = det.find("Explore.MarkerAnywhere")
            if hidden:
                # The ring is under the HUD: drag the map so it moves toward the middle of the screen.
                x, y, w, h = hidden.box
                dx, dy = PAN_CENTER[0] - (x + w // 2), PAN_CENTER[1] - (y + h // 2)
                dev.swipe(PAN_CENTER[0] - dx // 2, PAN_CENTER[1] - dy // 2,
                          PAN_CENTER[0] + dx // 2, PAN_CENTER[1] + dy // 2, 500)
                time.sleep(1.5)
                continue
            misses += 1
            if misses >= max_misses:
                return "no_marker"
            if not tracking_on(dev.screenshot()):
                dev.tap(*TRACKING_TOGGLE)
            else:
                # Tracking is on but the ring is nowhere: re-toggle so the camera re-centres on the target.
                dev.tap(*TRACKING_TOGGLE)
                time.sleep(1.5)
                dev.tap(*TRACKING_TOGGLE)
            time.sleep(2)
        elif d.state == "battle_prep":
            dev.tap(*START_BATTLE)
            time.sleep(3)
        elif d.state in ("battle", "loading"):
            time.sleep(2)
        elif d.state in ("defeated", "interact", "dungeon_floor", "confirm_dialog"):
            # Cards and dialogs: pick the option that fits the goal (resource/policy/cards.json).
            card, choice = decider.decide(ctx)
            dev.tap(*choice.point)
            time.sleep(4)
            if choice.kind == "defeated":
                return "defeated"
            if choice.kind == "unknown":
                unknowns += 1
        elif d.state == "dialogue_choice":
            dev.tap(360, d.box[1] + d.box[3] // 2)
            time.sleep(1.5)
        elif d.state == "dialogue":
            dev.tap(*nav.DIALOGUE_NEXT)
            time.sleep(1.2)
        elif d.state in ("reward_popup", "tap_to_continue"):
            dev.tap(*nav.REWARD_CLOSE)
            time.sleep(1.2)
        elif d.state == "home":
            dev.tap(296, 994)  # tracker panel on home offers to travel to the quest's island
            time.sleep(2)
        else:
            unknowns += 1
            unknown_total += 1
            if unknowns >= 5 or unknown_total >= 20:  # the second catches unknown <-> map loops
                return "unknown_screen"
            if unknowns >= 2:
                dev.tap(360, 1220)  # close a popup by tapping outside it
            time.sleep(1.5)
    return "timeout"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--minutes", type=float, default=20)
    args = p.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    dev = Device()
    result = follow_tracker(dev, StateDetector(dev), args.minutes)
    print(result)
    return 0 if result == "complete" else 1


if __name__ == "__main__":
    sys.exit(main())
