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

from . import nav
from .device import Device
from .state import StateDetector

log = logging.getLogger("sxs.explore")

TRACKER_PANEL = (304, 982)  # quest tracker panel on the map; claims the reward at 100/100
TRACKING_TOGGLE = (290, 1012)  # target icon on the panel: Tracking On/Off
START_BATTLE = (360, 956)
INTERACT_BUTTON = (360, 895)
DEFEATED_OK = (490, 830)
CONFIRM_OK = (490, 735)
PAN_CENTER = (360, 560)  # where a hidden marker is dragged to
MARKER_TARGET_DY = 100  # the target sits about this far below the centre of the tracker ring


def follow_tracker(dev: Device, det: StateDetector, minutes: float = 20, max_misses: int = 6) -> str:
    """Returns "complete", "defeated", "no_marker", "unknown_screen" or "timeout"."""
    deadline = time.monotonic() + minutes * 60
    misses = unknowns = 0
    last_progress = last_state = None
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
            # Tracking may be off, or the marker hidden behind a popup: toggle tracking off and on.
            dev.tap(*TRACKING_TOGGLE)
            time.sleep(1.5)
            if det.find("Explore.Marker") is None:
                dev.tap(*TRACKING_TOGGLE)
            time.sleep(1.5)
        elif d.state == "battle_prep":
            dev.tap(*START_BATTLE)
            time.sleep(3)
        elif d.state in ("battle", "loading"):
            time.sleep(2)
        elif d.state == "defeated":
            dev.tap(*DEFEATED_OK)  # back home; the character needs to get stronger before retrying
            time.sleep(4)
            return "defeated"
        elif d.state == "interact":
            dev.tap(*INTERACT_BUTTON)
            time.sleep(3)
        elif d.state == "dialogue":
            dev.tap(*nav.DIALOGUE_NEXT)
            time.sleep(1.2)
        elif d.state in ("reward_popup", "tap_to_continue"):
            dev.tap(*nav.REWARD_CLOSE)
            time.sleep(1.2)
        elif d.state == "confirm_dialog":
            # Only travel prompts are safe to accept blindly; anything else (spending currency...) is cancelled.
            body = det.find("Explore.ConfirmTravel")
            dev.tap(*(CONFIRM_OK if body else nav.CONFIRM_CANCEL))
            time.sleep(4)
        elif d.state == "home":
            dev.tap(296, 994)  # tracker panel on home offers to travel to the quest's island
            time.sleep(2)
        else:
            unknowns += 1
            if unknowns >= 5:
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
