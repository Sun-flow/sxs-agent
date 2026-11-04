"""Offline checks for the upgrade and gather decision logic (no emulator): python tests/check_upgrade_logic.py"""

import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sxs.badges import find_badges  # noqa: E402
from sxs.gather import pickups_to_take  # noqa: E402
from sxs.upgrade import relic_plan  # noqa: E402

SCREENS = Path(__file__).resolve().parent.parent / "docs" / "screens"
fails = 0


def check(name, got, want):
    global fails
    ok = got == want
    fails += not ok
    print(f"{'ok ' if ok else 'BAD'} {name}: {got!r}" + ("" if ok else f" (want {want!r})"))


# Relics (R-105): bands of 1, one element's 4 relics together, highest affinity first, all elements level together.
aff = {"fire": 30, "water": 50, "wind": 10}
check("relic first: water (highest affinity), relic 0", relic_plan({"fire": [0] * 4, "water": [0] * 4, "wind": [0] * 4}, aff), ("water", 0))
check("relic finish water's band first", relic_plan({"fire": [0] * 4, "water": [1, 1, 0, 0], "wind": [0] * 4}, aff), ("water", 2))
check("relic then fire", relic_plan({"fire": [0] * 4, "water": [1] * 4, "wind": [0] * 4}, aff), ("fire", 0))
check("relic no element passes the band early", relic_plan({"fire": [1] * 4, "water": [1] * 4, "wind": [0, 1, 1, 1]}, aff), ("wind", 0))
check("relic next band starts with water again", relic_plan({"fire": [1] * 4, "water": [1] * 4, "wind": [1] * 4}, aff), ("water", 0))
check("relic nothing owned", relic_plan({}, aff), None)

# Stamina (R-107): keep 70, 5 per pickup.
check("stamina 171 -> 20 pickups", pickups_to_take(171, 70), 20)
check("stamina 74 -> 0 pickups", pickups_to_take(74, 70), 0)
check("stamina 50 -> 0 pickups", pickups_to_take(50, 70), 0)

# Badges ("!") on reference screens.
check("badges skill_page", len(find_badges(cv2.imread(str(SCREENS / "skill_page.png")))), 4)
check("badges rank_level_goals", len(find_badges(cv2.imread(str(SCREENS / "rank_level_goals.png")))), 8)
check("badges class_hierarchy (not the red class icons)", len(find_badges(cv2.imread(str(SCREENS / "class_hierarchy.png")))), 3)

print("all good" if not fails else f"{fails} failed")
sys.exit(1 if fails else 0)
