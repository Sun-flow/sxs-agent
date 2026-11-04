"""Getting unstuck on the island map when quest progress stalls: talk to a red-"!" NPC, fight what blocks the path,
attack a guard, pan to look around. Each round starts from a different strategy. No model calls."""

from __future__ import annotations

import logging
import time
from typing import Optional

from ..core.ui import PLAYER_NAME
from ..vision.ocr import read_line
from ..vision.player import player_label

log = logging.getLogger("sxs.unstick")

PAN_STEPS = [(360, 800, 360, 450), (360, 400, 360, 750), (550, 600, 200, 600), (200, 600, 550, 600)]
MARKER_TARGET_DYS = [100, 60, 140, 30]  # how far below the tracker ring its target usually sits, best guess first
NPC_DX, NPC_DY = 30, 50  # from the "!" bubble to the NPC's body
GUARD_DX, GUARD_DY = -35, 50  # from the top-right guard bracket to the monster


def attack_guard(dev, det, frame=None) -> bool:
    """Monsters in brackets guard a way through: tap one to fight it. True if one was there."""
    box = det.find("Explore.GuardBracket", frame)
    if box:
        log.info("attacking a guard at %s", box.box)
        dev.tap(box.box[0] + GUARD_DX, box.box[1] + GUARD_DY)
        time.sleep(3)
    return bool(box)


def npc_to_talk_to(det) -> Optional[tuple[int, int]]:
    """Tap point for an NPC showing a red "!" bubble, skipping the one over our own character (name label below)."""
    frame = det.device.screenshot()
    for x, y, w, h in det.find_all("Explore.NpcAlert", frame):
        label = read_line(det, [max(0, x - 80), y + 20, 180, 120], frame)
        if PLAYER_NAME in label:
            continue
        return x + w // 2 - NPC_DX, y + h // 2 + NPC_DY
    return None


def blocker_point(det) -> Optional[tuple[int, int]]:
    """Halfway between our character (found by its name label) and the marker's target: where a monster blocking
    the path usually stands (e.g. a wolf between the player and a sword pickup in Verdantglade I)."""
    frame = det.device.screenshot()
    marker = det.find("Explore.Marker", frame)
    me = player_label(det, frame, [0, 120, 720, 840])
    if not marker or not me:
        return None
    mx, my, mw, mh = marker.box
    tx, ty = mx + mw // 2, my + mh // 2 + MARKER_TARGET_DYS[0]
    monsters = det.find_all("Explore.Monster", frame)
    if monsters:
        # A known monster on screen: the one nearest the target is the likely blocker.
        x, y, w, h = min(monsters, key=lambda b: (b[0] + b[2] / 2 - tx) ** 2 + (b[1] + b[3] / 2 - ty) ** 2)
        return x + w // 2, y + h // 2
    px, py = me[0] + me[2] // 2, me[1] - 50  # the label sits under the character's feet
    return (px + tx) // 2, (py + ty) // 2


def unstick(dev, det, round_no: int) -> bool:
    """One unstick attempt when quest progress has stalled. Each round starts from a different strategy, so a
    strategy that acted but didn't help isn't simply repeated. Returns True if something was tapped."""

    def talk() -> bool:
        # The target may be gated behind an NPC or map object with a red "!" (Molly, then the Moonveil gate).
        npc = npc_to_talk_to(det)
        if not npc:
            return False
        log.info("unstick: tapping a red '!' at %s", npc)
        dev.tap(*npc)
        time.sleep(4)
        if det.detect().state == "world_map":
            dev.tap(*npc)  # the first tap may only walk there; the second opens it
            time.sleep(3)
        return True

    def blocker() -> bool:
        # A monster stands in the way between us and the target: tap the spot halfway there.
        point = blocker_point(det)
        if point:
            log.info("unstick: tapping between player and target at %s", point)
            dev.tap(*point)
            time.sleep(3)
        return bool(point)

    def guard() -> bool:
        return attack_guard(dev, det)

    def look_around() -> bool:
        # Something to talk to may be just off screen (or behind the chat panel): pan a step, look for a "!".
        sx, sy, ex, ey = PAN_STEPS[(round_no // len(strategies)) % len(PAN_STEPS)]
        log.info("unstick: panning to look for a red '!'")
        dev.swipe(sx, sy, ex, ey, 500)
        time.sleep(1.5)
        return talk() or True

    strategies = [talk, blocker, guard, look_around]
    first = (round_no - 1) % len(strategies)
    return any(f() for f in strategies[first:] + strategies[:first])
