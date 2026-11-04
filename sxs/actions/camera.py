"""Moving the island-map camera. It doesn't follow the player, so screen-relative planning starts by putting our
character back in view."""

from __future__ import annotations

import time

from ..vision.player import player_on_screen

PLAY_AREA = (0, 130, 720, 840)  # x, y, w, h of the map between the HUD and the chat/tracker strip
HUD_AVATAR = (130, 130)  # matches of the player's face inside this top-left box are the HUD, not the pointer


def centre_player(dev, det, frame) -> bool:
    """Drag the map so our character (found by its name label) sits mid-screen: targets planned from the minimap
    land a few tiles away, and near the edge they fall off screen or onto the HUD. True if it dragged."""
    me = player_on_screen(det, frame)
    if me is None:
        return False
    px, py = me
    cx, cy = PLAY_AREA[0] + PLAY_AREA[2] // 2, PLAY_AREA[1] + PLAY_AREA[3] // 2
    if abs(px - cx) < 160 and abs(py - cy) < 200:
        return False
    dev.swipe(px, py, cx, cy, 600)
    time.sleep(1.5)
    return True


def recentre_on_player(dev, det, frame) -> bool:
    """Tap our own edge pointer to bring the camera back to us. True if it was there."""
    for x, y, w, h in det.find_all("Explore.PlayerPointer", frame):
        if x < HUD_AVATAR[0] and y < HUD_AVATAR[1]:
            continue
        dev.tap(x + w // 2, y + h // 2)
        time.sleep(1.5)
        return True
    return False
