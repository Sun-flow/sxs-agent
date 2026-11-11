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


ME = (360, 549)  # our white dot (inside the white box in Verdantglade V)


def frontier(home, me=ME):
    others = [p for k, p in labels.items() if k != home]
    return area_map.frontier(frame, labels[home], others, me=me)


v = frontier("Verdantglade V")
check("V: a frontier on reachable ground", v is not None, True)
if v:
    (x, y), share = v
    check("V: its nearest fog, on the zone's north-east edge", 540 <= x <= 620 and 470 <= y <= 540, True)
    check("V: fog round it", share >= area_map.FRONTIER_MIN_FOG, True)
    again = area_map.frontier(frame, labels["Verdantglade V"],
                              [p for k, p in labels.items() if k != "Verdantglade V"], me=ME, skip=[(x, y)])
    check("a skipped frontier isn't picked again on the same opening", again is None or
          (again[0][0] - x) ** 2 + (again[0][1] - y) ** 2 > 60 ** 2, True)
    other = area_map.frontier(frame, labels["Verdantglade V"],
                              [p for k, p in labels.items() if k != "Verdantglade V"], me=ME, away=[(x - ME[0], y - ME[1])])
    print("   next frontier after an empty one:", other)
    if other:
        import math
        ox, oy = other[0][0] - ME[0], other[0][1] - ME[1]
        cos = (ox * (x - ME[0]) + oy * (y - ME[1])) / (math.hypot(ox, oy) * math.hypot(x - ME[0], y - ME[1]))
        check("after an empty frontier the next goes another way", cos < math.cos(math.radians(45)), True)
    check("fog_share measures what frontier() measured", abs(area_map.fog_share(frame, (x, y)) - share) < 1e-6, True)
check("no fog round our dot on explored ground", area_map.fog_share(frame, ME), 0.0)
jc = frontier("Jungle Camp")
check("Jungle Camp: the fog north of its label (its way in)", bool(jc) and jc[0][1] < labels["Jungle Camp"][1], True)
check("Verdantglade IV (no fog of its own beside reachable ground) has none", frontier("Verdantglade IV"), None)
check("no walkable ground near us: none", area_map.frontier(frame, labels["Verdantglade V"], [], me=(60, 300)), None)

# Run 22's capture: Grotto Peninsula at 63%, its dotted outline running north into fog, our dot at the label's south.
g = cv2.imread(str(SCREENS / "world/world_area_map_grotto_peninsula_63.png"))
gme = next((p for k, p in area_map.objects(g) if k == "player"), None)
check("our dot is found when its core is dimmer than V 235", gme is not None and abs(gme[0] - 354) + abs(gme[1] - 663) < 6,
      True)
gl = {"Grotto Peninsula": (290, 560), "Rabbit Vault": (482, 590), "Verdantglade VI": (338, 808),
      "Stagnant Jungle": (258, 1085), "Auroradrasil": (482, 1032)}
gf = area_map.frontier(g, gl["Grotto Peninsula"], [p for k, p in gl.items() if k != "Grotto Peninsula"], me=gme)
check("Grotto Peninsula: a frontier north of us, into the zone's fog", bool(gf) and gf[0][1] < gme[1] - 40, True)
if gf:
    check("fog round it", gf[1] >= area_map.FRONTIER_MIN_FOG, True)

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
c.judge(leg("minimap", ["cleared"]), 42, (0, 0))
check("an object gone from the minimap after the leg is a gain", c.legs[-1].result, "gain")
for _ in range(clear.PUZZLE_LEGS):
    lg = clear.Leg(len(c.legs) + 1, "minimap", "building 2 tiles away", (60, 60), ["cleared"])
    c.legs.append(lg)
    c.judge(lg, c.pct, (0, 0))
check("gold squares that open nothing and move no % add up to a puzzle", c.inert_gold, clear.PUZZLE_LEGS)
lg = clear.Leg(len(c.legs) + 1, "minimap", "building 1 tiles away", (61, 61), ["acted"])
c.legs.append(lg)
c.judge(lg, c.pct, (0, 0))
check("a gold square whose card we acted on is a structure, not a puzzle tile", c.inert_gold, 0)
check("a zone given by its first words matches its label", clear.mapnav.label_is("Lakeside Camp", "Lakeside"), True)
check("a different numeral is another zone", clear.mapnav.label_is("Verdantglade I", "Verdantglade II"), False)
check("another zone with a shared first word isn't ours", clear.mapnav.label_is("Lakeside Camp", "Lake"), False)
check("minimap targets reach the whole minimap", clear.MINIMAP_REACH >= 7, True)
check("a tile 2 right of us is on screen", clear.on_screen((360, 600), type("M", (), {"centre": (10, 10)})(), (10, 12)),
      (568, 600))
check("a tile 5 right of us is off screen", clear.on_screen((360, 600), type("M", (), {"centre": (10, 10)})(), (10, 15)),
      None)
check("a tile over the minimap HUD is off limits", clear.on_screen((360, 600), type("M", (), {"centre": (10, 10)})(),
                                                                   (8, 12)), None)
check("a guard group is a leg source of its own", hasattr(clear.Clearer, "try_guard"), True)
check("no % line counts as explored only near the end", clear.NO_PCT_DONE_FROM >= 90, True)
check("the loop's ok statuses", {"zone_done", "no_objective", "no_progress"} <= clear.OK, True)

print("all good" if not fails else f"{fails} failed")
sys.exit(1 if fails else 0)
