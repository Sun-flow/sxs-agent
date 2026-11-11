"""Offline checks for the Clear Zone loop (no emulator): python tests/check_clear.py

The frontier picker on a reference area map, the minimap planner's goals (objects only, no fog leads), and the leg
bookkeeping: what counts as a gain, spot skipping, the ring resting, a frontier that reveals nothing."""

import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sxs.loops import clear  # noqa: E402
from sxs.vision import area_map, minimap  # noqa: E402

SCREENS = Path(__file__).resolve().parent.parent / "docs" / "screens"
fails = 0


def check(name, got, want):
    global fails
    ok = got == want
    fails += not ok
    print(f"{'ok ' if ok else 'BAD'} {name}: {got!r}" + ("" if ok else f" (want {want!r})"))


# Frontier (docs/step6-clear-zone.md, source 5) on the survey-zoom area map: label centres as OCR places them.
frame = cv2.imread(str(SCREENS / "world/area_map_survey_zoom.png"))
labels = {"Verdantglade VI": (147, 525), "Verdantglade V": (485, 600), "Wildbloom Coast": (470, 375),
          "Monolith Ruins I": (597, 637), "Auroradrasil": (260, 700), "Zephyr Vale": (610, 762),
          "Troll Lair": (597, 875), "Verdantglade IV": (530, 912), "Jungle Camp": (397, 1110),
          "Drasilgard": (310, 885), "Highland Woods": (690, 675)}


def frontier(home):
    others = [p for k, p in labels.items() if k != home]
    return area_map.frontier(frame, labels[home], others)


vi = frontier("Verdantglade VI")
check("VI frontier found", vi is not None, True)
if vi:
    (x, y), share = vi
    check("VI frontier on its north-west edge, not on the label text", 150 <= x <= 240 and 470 <= y <= 515, True)
    check("VI frontier has fog round it", share >= area_map.FRONTIER_MIN_FOG, True)
    again = area_map.frontier(frame, labels["Verdantglade VI"], [p for k, p in labels.items() if k != "Verdantglade VI"],
                              skip=[(x, y)])
    check("a skipped frontier isn't picked again on the same opening", again is None or
          (again[0][0] - x) ** 2 + (again[0][1] - y) ** 2 > 60 ** 2, True)
jc = frontier("Jungle Camp")
check("Jungle Camp frontier north of its label (its way in)", bool(jc) and jc[0][1] < labels["Jungle Camp"][1], True)
check("Zephyr Vale (no fog of its own in reach) has no frontier", frontier("Zephyr Vale"), None)

# Minimap goals: objects only. Ground (fog leads, shaded tiles) is never a goal any more (R-143).
check("minimap goals", minimap.GOALS, ("item", "monster", "building"))
check("no fog_lead helper left", hasattr(minimap, "fog_lead"), False)

# Leg bookkeeping with a stand-in detector (no screen reads needed for these).


class Det:
    def find(self, name):
        return None

    def read_text(self, roi, frame=None):
        return []


c = clear.Clearer(None, Det(), "Verdantglade IX")
c.fail((10, 10))
check("one failed leg doesn't skip a spot", c.failed_spot((10, 11)), False)
c.fail((11, 10))
check("two failed legs at the same spot skip it", c.failed_spot((10, 10)), True)
check("a spot 3 tiles off is another spot", c.failed_spot((14, 10)), False)
c.skip_spot((50, 50))
check("a dismissed card's spot is skipped at once", c.failed_spot((51, 49)), True)

clear.goto.coords = lambda det: (20, 20)  # where we stand after each leg below
clear.mapnav.reset_locate = lambda: None


def leg(source, events=(), xy=(30, 30)):
    lg = clear.Leg(len(c.legs) + 1, source, "test", xy, list(events))
    c.legs.append(lg)
    return lg


c.pct = 40
lg = leg("big_map", ["fight"])
c.judge(lg, 40, (0, 0))
check("a fight is a gain", (lg.result, c.no_gain), ("gain", 0))
lg = leg("minimap")
c.judge(lg, 40, (20, 20))
check("a tap that didn't move us failed", (lg.result, c.no_gain), ("failed", 1))
c.pct = 42
lg = leg("known")
c.judge(lg, 40, (0, 0))
check("the % rising is a gain", (lg.result, c.no_gain), ("gain", 0))
for _ in range(clear.RING_MISSES):
    c.judge(leg("ring", xy=(20, 20)), 42, (0, 0))
check("ring legs without a gain rest the ring", c.ring_misses >= clear.RING_MISSES, True)
check("a ring miss doesn't skip the spot we stand on", c.failed_spot((20, 20)), False)
c.judge(leg("big_map", ["pickup"]), 42, (0, 0))
check("another source's gain wakes the ring", c.ring_misses, 0)
for _ in range(clear.STALL_LEGS):
    c.judge(leg("big_map", ["no_move"], xy=None), 42, (0, 0))
check("STALL_LEGS legs without a gain reach the stop count", c.no_gain >= clear.STALL_LEGS, True)
c.no_gain = 0
c.judge(leg("frontier", ["revealed"]), 42, (0, 0))
check("a frontier that revealed objects is a gain", c.legs[-1].result, "gain")
check("the loop's ok statuses", {"zone_done", "no_objective", "no_progress"} <= clear.OK, True)

print("all good" if not fails else f"{fails} failed")
sys.exit(1 if fails else 0)
