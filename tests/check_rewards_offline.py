"""Offline check of the tracker reward detector (sxs/vision/gift.py) on docs/screens. Prints "all good" or the misses.

    python tests/check_rewards_offline.py

Needs: OpenCV
Checks: Tracker gift + "!" detector over `docs/screens` (claimable set, badge painted out)
"""

from __future__ import annotations

import sys
from pathlib import Path

import cv2

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sxs.core.screens import reference_screens  # noqa: E402
from sxs.vision import gift  # noqa: E402

SCREENS = ROOT / "docs" / "screens"
# Frames with a finished quest's gift and "!" on the tracker (the badge pulses red / dull orange between frames).
CLAIMABLE = {
    "explore_bellflower_field", "explore_bellflower_tracker", "explore_ore_mined", "explore_ore_rocks_near",
    "explore_resource_tracker", "explore_resource_tracker2", "world_map_boss_beaten", "world_map_quest_complete",
    "world_map_tracker_gift",
}


def main() -> int:
    bad = []
    for p in reference_screens():
        frame = cv2.imread(str(p))
        if frame is None or frame.shape[:2] != (1280, 720):
            continue
        got = gift.find_reward(frame) is not None
        if got != (p.stem in CLAIMABLE):
            bad.append(f"{p.name}: expected {p.stem in CLAIMABLE}, got {got}")
    # Same frame with the badge painted over: the gift alone is not enough.
    frame = cv2.imread(str(SCREENS / "world/world_map_tracker_gift.png"))
    gx, gy = gift.find_gift(frame)
    dx, dy, w, h = gift.BADGE_BOX
    frame[gy + dy:gy - 25, gx + dx:gx + dx + w] = frame[gy + 20, gx + 60]
    assert gift.find_gift(frame), "painting the badge out hid the gift"
    if gift.find_reward(frame) is not None:
        bad.append("world_map_tracker_gift with the badge removed: still claimable")
    print("\n".join(bad) if bad else "all good")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
