"""Offline checks for the shared big map (no emulator): python tests/check_bigmap.py

docs/big-map-survey.md: the zoom knob read from reference area maps, glances that don't re-zoom when the knob is
already at the walking zoom, one OCR pass per frame for every label reader, kept facts and what makes them stale,
the once-a-day discovery survey, the enlarged-crop % re-read, and walks that never zoom out to search.

Needs: OpenCV, MaaFramework (imports only)
Checks: Shared big map: zoom knob on reference area maps, no re-zoom at the walking zoom, one OCR pass for all label
  readers, kept facts and stale events, discovery once a server day, % re-read from an enlarged crop, walks pan
  instead of zooming out, roam surveys only when due
"""

import sys
import tempfile
import time
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sxs.actions import bigmap, goto, mapnav  # noqa: E402
from sxs.loops import roam  # noqa: E402

SCREENS = Path(__file__).resolve().parent.parent / "docs" / "screens"
fails = 0


def check(name, got, want):
    global fails
    ok = got == want
    fails += not ok
    print(f"{'ok ' if ok else 'BAD'} {name}: {got!r}" + ("" if ok else f" (want {want!r})"))


def img(name):
    return cv2.imread(str(SCREENS / "world" / name))


# ------------------------------------------------------------------ zoom knob on every reference area map
KNOBS = {"area_map_blue_bang.png": 955, "area_map_v3.png": 955, "world_area_map_grotto_peninsula_63.png": 955,
         "world_area_map_xii_statue_ready.png": 955, "area_map_survey_zoom.png": 1031,
         "world_area_map_zoomin0.png": 821, "world_area_map_zoomout1.png": 1089}
for name, want in KNOBS.items():
    k = bigmap.knob_y(img(name))
    check(f"knob on {name} within 4 px of {want}", k is not None and abs(k - want) <= 4, True)
check("no knob on the island map", bigmap.knob_y(img("world_map.png")), None)
check("walking zoom = the game's default", bigmap.at_zoom(img("area_map_v3.png"), bigmap.WALK_KNOB_Y), True)
check("survey reference is not at the walking zoom", bigmap.at_zoom(img("area_map_survey_zoom.png"),
                                                                     bigmap.WALK_KNOB_Y), False)


class FakeDev:
    def __init__(self, frames=None):
        self.taps, self.swipes, self.frames = [], [], list(frames or [])

    def tap(self, x, y):
        self.taps.append((x, y))

    def swipe(self, *a):
        self.swipes.append(a)

    def screenshot(self):
        return self.frames.pop(0) if len(self.frames) > 1 else self.frames[0]


real_sleep = time.sleep
time.sleep = lambda s: None  # offline: no waiting

dev = FakeDev()
check("set_zoom at the walking zoom: no taps, no drag",
      (bigmap.set_zoom(dev, img("area_map_v3.png"), bigmap.WALK_KNOB_Y), dev.taps, dev.swipes), (False, [], []))
dev = FakeDev()
bigmap.set_zoom(dev, img("area_map_survey_zoom.png"), bigmap.WALK_KNOB_Y)
check("from the survey zoom: one knob drag, no '-' taps", (dev.taps, dev.swipes[0][:4]),
      ([], (bigmap.KNOB_X, 1031, bigmap.KNOB_X, bigmap.WALK_KNOB_Y)))
dev = FakeDev()
bigmap.set_zoom(dev, img("area_map_v3.png"), bigmap.SURVEY_KNOB_Y)
check("survey zoom from the walking zoom: a drag, not 4 taps", (len(dev.taps), len(dev.swipes)), (0, 1))
dev = FakeDev()
bigmap.set_zoom(dev, None, bigmap.SURVEY_KNOB_Y)
check("knob unknown: 4 '-' taps then a drag from fully out", (dev.taps.count(bigmap.ZOOM_OUT), dev.swipes[0][1]),
      (4, bigmap.FULL_OUT_KNOB_Y))


# ------------------------------------------------------------------ one OCR pass shared by the readers
class FakeDet:
    def __init__(self, lines):
        self.lines, self.calls = lines, 0

    def read_text(self, roi, frame=None):
        self.calls += 1
        x, y, w, h = roi
        return [(t, b) for t, b in self.lines if b[0] >= x and b[1] >= y and b[0] + b[2] <= x + w
                and b[1] + b[3] <= y + h]


LINES = [("Grotto Peninsula", [300, 500, 150, 30]), ("Exploration: 63%", [300, 535, 150, 25]),
         ("Verdantglade IX", [80, 300, 160, 30]), ("23.0K", [330, 565, 60, 20]),
         ("Damp Woods", [560, 640, 90, 30])]
frame = img("world_area_map_grotto_peninsula_63.png")
det = FakeDet(LINES)
areas = roam.read_areas(det, frame)
labels = goto.area_labels(det, frame)
names = mapnav.map_labels(det, frame)
check("three readers, one OCR call for one frame", det.calls, 1)
check("roam reader pairs the % with its label", [(a.name, a.pct) for a in areas if a.name == "Grotto Peninsula"],
      [("Grotto Peninsula", 63)])
check("goto reader keeps right-third labels (x < 655)", "Damp Woods" in labels, True)
check("mapnav reader has the label centres", names.get("Verdantglade IX"), (160, 315))

# ------------------------------------------------------------------ kept facts and stale events
with tempfile.TemporaryDirectory() as tmp:
    bigmap.STATE_FILE = Path(tmp) / "bigmap.json"
    bm = bigmap.BigMap(FakeDev([frame]), FakeDet(LINES))
    look = bm.record(frame, "pick (test)")
    check("a glance keeps the zone's %", bm.fact("pct", "Grotto Peninsula"), 63)
    check("matched by first words too (label_is)", bm.fact("pct", "Grotto"), 63)
    check("our dot found on the Grotto capture (fallback detector)", look.dot is not None, True)
    check("recent look reused within a minute", bm.recent() is look, True)
    bm.invalidate("gain", "Grotto Peninsula")
    check("a gain drops that zone's %", bm.fact("pct", "Grotto Peninsula"), None)
    check("a gain retires the last look", bm.recent(), None)
    bm.record(frame, "again")
    bm.pct["Grotto Peninsula"].at -= bigmap.OTHER_ZONES_S + 1
    check("older than 10 minutes: gone", bm.fact("pct", "Grotto Peninsula"), None)
    bm.statue["Verdantglade XII"] = bigmap.Fact(True, time.monotonic())
    bm.invalidate("blessed", "Verdantglade XII")
    check("blessed drops the ready statue", bm.fact("statue", "Verdantglade XII"), None)
    check("discovery due on a fresh day", bool(bm.discovery_due()), True)
    bm.discovered()
    check("not due again the same server day", bm.discovery_due(), None)
    check("counts by kind", bm.counts["glance"] >= 2 and bm.counts["discovery"] == 1, True)


# ------------------------------------------------------------------ % re-read from an enlarged crop
class CropDet:
    def __init__(self):
        self.shapes = []

    def read_text(self, roi, frame=None):
        self.shapes.append(frame.shape)
        return [("Exploration: 41%", [0, 0, 100, 20])]


cd = CropDet()
check("enlarged-crop re-read", bigmap.reread_pct(cd, frame, [300, 500, 150, 30]), 41)
check("same frame size handed to OCR", cd.shapes[0], frame.shape)

# ------------------------------------------------------------------ walks never zoom out to search
d = FakeDev([img("area_map_v3.png")])
check("_widen: one knob drag to the survey zoom, no '-' taps", (goto._widen(d) is not None, d.taps, len(d.swipes)),
      (True, [], 1))
check("_widen: already at survey zoom, nothing", goto._widen(FakeDev([img("area_map_survey_zoom.png")])), None)
check("_widen: no knob seen (not the map), no blind taps", goto._widen(FakeDev([img("world_map.png")])), None)
pans = goto._pans((1.0, 0.0))
check("two drags toward a label to the east (map dragged west)", (len(pans), pans[0][2] < pans[0][0]), (2, True))
check("no direction: no sweep at all", goto._pans(None), [])


class TreeOnly(roam.Roamer):
    def __init__(self, tree):
        self.tree = tree


class FakeTree:
    zones = {"A": {"map_point": [100, 100]}, "B": {"map_point": [100, 400]}, "C": {}}

    def get(self, k):
        return self.zones.get(k)


r = TreeOnly(FakeTree())
v = r.toward("B", "A")
check("toward: from A's label down to B's", (round(v[0], 2), round(v[1], 2)), (0.0, 1.0))
check("toward: unknown point gives no direction", r.toward("C", "A"), None)

# ------------------------------------------------------------------ roam: a survey only when one is due
class LookRoamer(roam.Roamer):
    def __init__(self, bm, tree):
        self.bm, self.tree, self.det, self.power = bm, tree, None, None
        self.discover_asked = self.discovered_this_run = False
        self.surveys = 0

    def survey(self):
        self.surveys += 1
        self.bm.discovered()
        return [roam.Area("X", [0, 0, 0, 0], 5)], [], 28.5


class LookTree(FakeTree):
    zones = {"A": {"map_point": [100, 100], "pct": 40}, "B": {"pct": 100}, "Kingdom": {"kind": "kingdom"}}

    def explored(self, k):
        return (self.zones[k].get("pct") or 0) >= 100


roam.read_power = lambda det: 28.5
with tempfile.TemporaryDirectory() as tmp:
    bigmap.STATE_FILE = Path(tmp) / "bigmap.json"
    lr = LookRoamer(bigmap.BigMap(FakeDev([frame]), FakeDet(LINES)), LookTree())
    lr.look_around()
    check("first pass of the day: the discovery survey", lr.surveys, 1)
    areas, statues, power = lr.look_around()
    check("next pass: no survey, the tree's zones", (lr.surveys, sorted((a.name, a.pct) for a in areas)),
          (1, [("A", 40), ("B", None)]))
    lr.bm.pct["A"] = bigmap.Fact(55, time.monotonic())
    check("a fresher glance % beats the tree's", next(a.pct for a in lr.look_around()[0] if a.name == "A"), 55)
    lr.discover_asked = True
    lr.discovered_this_run = False
    lr.look_around()
    check("--discover: one survey on purpose", lr.surveys, 2)

time.sleep = real_sleep
print("all good" if not fails else f"{fails} problem(s)")
sys.exit(1 if fails else 0)
