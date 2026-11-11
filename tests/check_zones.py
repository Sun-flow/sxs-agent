"""Offline checks for zone borders, the location tree, the area-map survey merge and the Cart unlock finder (no
emulator): python tests/check_zones.py"""

import sys
import tempfile
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sxs.loops.cart import CartUpgrader  # noqa: E402
from sxs.loops.roam import Area, merge_readings  # noqa: E402
from sxs.policy.zones import ZONES_FILE, Tree, same  # noqa: E402
from sxs.vision import minimap  # noqa: E402

SCREENS = Path(__file__).resolve().parent.parent / "docs" / "screens"
fails = 0


def check(name, got, want):
    global fails
    ok = got == want
    fails += not ok
    print(f"{'ok ' if ok else 'BAD'} {name}: {got!r}" + ("" if ok else f" (want {want!r})"))


# Zone borders on the minimap (R-132): the dotted line across the passage east of the player in Moonveil Woods.
frame = cv2.imread(str(SCREENS / "world/explore_bellflower_picked.png"))
mm = minimap.read(frame)
check("border tiles east of the player", {(10, 13), (11, 13)} <= set(mm.border), True)
for name in ("world_map", "world_map_explore", "world_map_monsters", "world_map_player_pointer"):
    check(f"no border on {name}", len(minimap.read(cv2.imread(str(SCREENS / f"world/{name}.png"))).border), 0)

# Live frames (2026-11-09) in Verdantglade V, unexplored and shaded, with explored Verdantglade IV light to the south:
# the planner must not reach the light zone, also when standing right on the line. Saved lossless on purpose: the\n# 256-colour reference format shifts the tiles next to the player from shaded to light.
for name in ("zone_edge_verdantglade_v", "zone_edge_verdantglade_v_on_line"):
    live = minimap.read(cv2.imread(str(SCREENS / f"world/{name}.png")), home_light=False)
    check(f"{name}: light zone unreachable", minimap.path_to_nearest(live, goals=("walk_explored",)), [])

# A border line is a wall for the planner unless crossing is allowed.
grid = [["walk_explored"] * 7 for _ in range(7)]
grid[3][6] = "item"
wall = minimap.Minimap(grid, (3, 1), frozenset((r, 4) for r in range(7)))
check("border blocks the path", minimap.path_to_nearest(wall, goals=("item",)), [])
check("crossing allowed reaches the item", len(minimap.path_to_nearest(wall, goals=("item",), cross_border=True)), 6)

# The location tree (resource/world/zones.json).
check("tree file exists", ZONES_FILE.exists(), True)
t = Tree.load()
t.zones["Verdantglade V"].update(pct=78, blessed=False)  # the checks below use V as an unfinished zone (it reached 100% live)
# ... and Jungle Camp as a zone with no known way in (live runs found one through Verdantglade III).
t.zones["Jungle Camp"].pop("entries", None)
t.zones["Jungle Camp"].update(pct=0, blessed=False)
t.links = [ln for ln in t.links if not ("Jungle Camp" in (ln["a"], ln["b"]) and ln["how"] == "walked")]
check("Jungle Camp is next at 22.4K (lowest-CP unexplored)", t.next_zone(22.4), "Jungle Camp")
check("finish the zone we stand in first (R-132)", t.next_zone(22.4, "Verdantglade V"), "Verdantglade V")
check("no crossing out of an unfinished zone", t.can_cross("Verdantglade V", "Jungle Camp", 22.4)[0], False)
check("1.25x power check on crossing", t.can_cross("Drasilgard", "Troll Lair", 12.0)[0], False)
check("crossing from a town into a zone in reach", t.can_cross("Drasilgard", "Jungle Camp", 22.4)[0], True)
check("Jungle Camp's missing way in is an open question",
      any(q.startswith("Jungle Camp: no known way in") for q in t.open_questions()), True)
t.zones["Jungle Camp"]["lost_at"] = 22.4  # a fight lost there at 22.4K (Clear Zone's defeated screen)
check("a zone we lost a fight in waits for more power", t.next_zone(22.6) != "Jungle Camp", True)
check("and is tried again once power grows", t.next_zone(22.9), "Jungle Camp")
t.zones["Jungle Camp"].pop("lost_at")
check("name match keeps numerals apart", same("Verdantglade V", "Verdantglade VI"), False)
check("name match takes a clipped label", same("tglade III", "Verdantglade III"), True)

with tempfile.TemporaryDirectory() as d:
    t2 = Tree.load()
    t2.path = Path(d) / "zones.json"
    t2.zones["Jungle Camp"].pop("entries", None)
    t2.zones["Jungle Camp"]["blessed"] = False  # a blessed zone keeps 100% (R-140); test an unblessed one
    t2.observe("Jungle Camp", pct=12, today="2026-11-09")
    t2.record_entry("Jungle Camp", "Verdantglade V", True, "2026-11-09", xy=(201, 80))
    t2.record_entry("Jungle Camp", "Drasilgard", True, "2026-11-09", xy=(120, 60))
    t2.save()
    t3 = Tree.load(t2.path)
    check("a working way in clears its failure", "Drasilgard" in t3.zones["Jungle Camp"].get("failed_via", {}), False)
    check("and becomes a walked link", "Verdantglade V" in t3.neighbours("Jungle Camp", ("walked",)), True)
    check("several ways in are kept", [e["via"] for e in t3.zones["Jungle Camp"]["entries"]], ["Verdantglade V", "Drasilgard"])
    check("the latest way in ranks first", t3.entry_candidates("Jungle Camp", "2026-11-09")[0], "Drasilgard")
    check("survey % updates the tree", t3.zones["Jungle Camp"]["pct"], 12)

# Survey merge: pans of one opening put into the first view's coordinates.
r0 = [Area("Verdantglade V", [100, 1110, 160, 30])]  # near the bottom: no room for its % line
r1 = [Area("Verdantglade V", [100, 810, 160, 30], pct=78, gate=14.8), Area("Jungle Camp", [300, 900, 120, 30])]
merged = merge_readings([(r0, (0, 0)), (r1, (0, -300))])
v = next(a for a in merged if a.name == "Verdantglade V")
check("merge keeps the % from the pan that read it", (v.pct, v.gate, v.unsure), (78, 14.8, False))
check("merge places pans in the first view", v.box[:2], [100, 1110])
check("a label with room and no % is finished, not unsure",
      [(a.pct, a.unsure) for a in merged if a.name == "Jungle Camp"], [(None, False)])
check("a label never seen with room is unsure",
      merge_readings([(r0, (0, 0))])[0].unsure, True)

# Cart unlock buttons (R-137): exact "Unlock" only, never "Unlocks at Lv. 45".
lines = [("Unlock", [520, 893, 140, 40]), ("Unlocks at Lv. 45", [450, 970, 200, 36]), ("+60/h", [190, 520, 90, 30])]
check("cart unlock button", CartUpgrader.unlock_buttons(lines), [(590, 913)])

# Blue "!" interactables on the area map (mae, 2026-11-10): found, and nothing else is.
from sxs.vision.area_map import blue_badges  # noqa: E402
check("blue ! on Jungle Camp", len(blue_badges(cv2.imread(str(SCREENS / "world/area_map_blue_bang.png"))) or []), 1)
for name in ("area_map_lv22", "area_map_survey_zoom", "area_map_v3", "world_area_map"):
    check(f"no blue ! on {name}", blue_badges(cv2.imread(str(SCREENS / f"world/{name}.png"))), [])

print("all good" if not fails else f"{fails} failed")
sys.exit(1 if fails else 0)
