"""The big map (area map) as one shared thing: glances for walking, a discovery survey once a day.

mae, 2026-11-11 (docs/big-map-survey.md): "survey zoom should be reserved for situations where we want to see what
zones are available, and no other. Walking should basically never require a full survey." So:

- a **glance** opens the map at the walking zoom (the game's default; the zoom knob is checked in the frame and the
  map is only re-zoomed when it isn't there), reads what is in view, and the caller taps and closes;
- a **discovery survey** (survey zoom and the full pan grid, `Roamer.survey`) runs once per server day, when the
  location tree has no zone left to pick, or on purpose (`roam --discover`);
- every opening goes through `BigMap.record`, which keeps the zone facts it read (%, power, ready statues, our dot)
  so later callers reuse them until an event in the stale table drops them, and logs one line saying what it was for.

Tap points (pixels) are never kept: the map reopens centred on the camera, so they're read in the opening that taps.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from ..core.marks import server_day
from ..core.paths import LOGS

log = logging.getLogger("sxs.actions.bigmap")

# The zoom slider right of the map (`docs/screens/world/*area_map*.png`): the knob is a white disc on the track.
# Measured on the 20 reference area maps: y 821 closest zoom, 955 the game's default (the zoom every Clear Zone leg
# used in run15 and the Grotto/XII captures), 1031 survey zoom, 1089 fully zoomed out.
KNOB_X = 682
KNOB_ROI = (670, 812, 25, 288)  # x, y, w, h of the track between "+" and "-"
WALK_KNOB_Y = 955
SURVEY_KNOB_Y = 1031
KNOB_TOLERANCE = 10  # px: the knob this close to a zoom's position is at that zoom
ZOOM_OUT = (682, 1113)  # the "-" under the slider
FULL_OUT_KNOB_Y = 1089

CURRENT_ZONE_S = 60  # the zone being cleared: a glance this old is still its "last look" (mae: good timeline)
OTHER_ZONES_S = 600  # other zones' %, power, ready statues
STATE_FILE = LOGS / "bigmap.json"  # the server day of the last discovery survey, kept across runs
OCR_ROI = [0, 120, 720, 1100]  # one OCR pass covers every reader's ROI (labels below y 1185 are kingdom buttons)


def knob_y(frame: np.ndarray) -> Optional[int]:
    """The zoom knob's centre y on the area map, or None when no knob shows (not the area map)."""
    import cv2
    x, y, w, h = KNOB_ROI
    hsv = cv2.cvtColor(frame[y:y + h, x:x + w], cv2.COLOR_BGR2HSV)
    white = (hsv[..., 2] > 200) & (hsv[..., 1] < 50)
    rows = np.where(white.sum(1) >= 8)[0]
    if len(rows) < 12 or rows.max() - rows.min() > 40:  # the disc is ~20 px tall; a longer run is something else
        return None
    return int(rows.mean()) + y


def at_zoom(frame: np.ndarray, target: int) -> bool:
    k = knob_y(frame)
    return k is not None and abs(k - target) <= KNOB_TOLERANCE


def set_zoom(dev, frame: Optional[np.ndarray], target: int) -> bool:
    """Area map open: bring the zoom to `target` (a knob y) unless the frame shows it there already. Drags the knob
    from where it is; when it can't be found, zooms fully out with "-" first and drags from the bottom (the old
    survey_zoom way). True when it changed the zoom."""
    k = knob_y(frame) if frame is not None else None
    if k is not None and abs(k - target) <= KNOB_TOLERANCE:
        return False
    if k is None:
        for _ in range(4):
            dev.tap(*ZOOM_OUT)
            time.sleep(0.4)
        k = FULL_OUT_KNOB_Y
    dev.swipe(KNOB_X, k, KNOB_X, target, 600)
    time.sleep(1.2)
    return True


# ---------------------------------------------------------------------------------------------- one OCR pass
_OCR: dict = {"key": None, "lines": []}


def _frame_key(frame: np.ndarray):
    return frame.shape, hash(frame[::23, ::23].tobytes())


def map_text(det, frame: np.ndarray, roi: list[int]) -> list[tuple[str, list[int]]]:
    """OCR lines of the area map inside roi. Every label reader (roam.read_areas, goto.area_labels,
    mapnav.map_labels) asks through here, so one frame is read once however many of them look at it."""
    key = _frame_key(frame)
    if _OCR["key"] != key:
        _OCR["key"], _OCR["lines"] = key, det.read_text(OCR_ROI, frame)
    x0, y0, w, h = roi
    return [(t, b) for t, b in _OCR["lines"] if b[0] >= x0 and b[1] >= y0 and b[0] + b[2] <= x0 + w + 2
            and b[1] + b[3] <= y0 + h + 2]


PCT_LINE_H = 40  # px under a label where its "Exploration: N%" line sits


def reread_pct(det, frame: np.ndarray, box: list[int]) -> Optional[int]:
    """A label read with no % line under it: OCR the strip under the label again from an enlarged copy of the same
    frame (the strengthening thread's idea, 2026-11-11) instead of reopening the map. None if still unread."""
    import re
    import cv2
    x, y, w, h = box
    x0, y0 = max(0, x - 30), y + h
    x1, y1 = min(frame.shape[1], x + w + 30), min(frame.shape[0], y + h + PCT_LINE_H)
    if x1 - x0 < 10 or y1 - y0 < 10:
        return None
    crop = cv2.resize(frame[y0:y1, x0:x1], None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    canvas = np.zeros_like(frame)
    ch, cw = min(crop.shape[0], canvas.shape[0]), min(crop.shape[1], canvas.shape[1])
    canvas[:ch, :cw] = crop[:ch, :cw]
    for t, _ in det.read_text([0, 0, cw, ch], canvas):
        m = re.search(r"(\d{1,3})\s*%", t) or re.search(r"Explor\w*\s*:?\s*(\d{1,3})", t)
        if m and int(m.group(1)) <= 100:
            return int(m.group(1))
    return None


# ---------------------------------------------------------------------------------------------- kept facts
@dataclass
class Look:
    n: int
    at: float
    purposes: str
    areas: list  # roam.Area
    dot: Optional[tuple[int, int]]
    dot_how: str  # "found", "fallback", "none"
    statues: list  # zone names with a ready statue near their label
    zoom: Optional[int]
    frame: Optional[np.ndarray] = field(default=None, repr=False)


@dataclass
class Fact:
    value: object
    at: float


class BigMap:
    """Shared by roam and Clear Zone for a process (one emulator). `get(dev, det)` returns it."""

    def __init__(self, dev, det):
        self.dev, self.det = dev, det
        self.n = 0
        self.last: Optional[Look] = None
        self.pct: dict[str, Fact] = {}
        self.gate: dict[str, Fact] = {}
        self.statue: dict[str, Fact] = {}  # zone -> Fact(True) when a ready mark was seen near its label
        self.counts = {"glance": 0, "reuse": 0, "discovery": 0}
        self._t0: Optional[float] = None

    # ------------------------------------------------------------------ openings
    def open(self, purposes: str, zoom: int = WALK_KNOB_Y) -> Optional[np.ndarray]:
        """Open the map at `zoom` (walking zoom unless asked) and return its frame; the map stays open."""
        from . import goto
        t0 = time.monotonic()
        if not goto.open_area_map(self.dev, self.det):
            log.info("[map] %s: the area map did not open", purposes)
            return None
        time.sleep(0.5)
        frame = self.dev.screenshot()
        if set_zoom(self.dev, frame, zoom):
            frame = self.dev.screenshot()
        self._t0 = t0
        return frame

    def record(self, frame: np.ndarray, purposes: str, kind: str = "glance", t0: Optional[float] = None) -> Look:
        """Read one open-map frame for everything and keep the facts. Logs `[map] <kind> for: <purposes>`."""
        from ..vision import area_map
        areas = read_areas(self.det, frame)
        objs = area_map.objects(frame)
        dot = next((p for k, p in objs if k == "player"), None)
        how = "found" if dot is not None else "none"  # objects() falls back to area_map.player_dot itself
        statues = []
        try:
            from ..loops.roam import STATUE_NEAR_LABEL, statue_badges  # the red and tan "!" marks
            for p in statue_badges(frame):
                near = [a for a in areas if abs(a.point[0] - p[0]) + abs(a.point[1] - p[1]) < STATUE_NEAR_LABEL]
                if near:
                    name = min(near, key=lambda a: abs(a.point[0] - p[0]) + abs(a.point[1] - p[1])).name
                    if name not in statues:
                        statues.append(name)
        except Exception:  # noqa: BLE001 - a badge read never stops a walk
            log.debug("statue badge read failed", exc_info=True)
        now = time.monotonic()
        for a in areas:
            if a.pct is not None:
                self.pct[a.name] = Fact(a.pct, now)
            if a.gate is not None:
                self.gate[a.name] = Fact(a.gate, now)
        for s in statues:
            self.statue[s] = Fact(True, now)
        self.n += 1
        self.counts[kind] = self.counts.get(kind, 0) + 1
        zoom = knob_y(frame)
        start = t0 if t0 is not None else self._t0
        took = f" {now - start:.1f} s" if start else ""
        self._t0 = None
        log.info("[map] %s %d for: %s%s, zoom %s, %d labels%s, our dot: %s", kind, self.n, purposes, took,
                 "walking" if zoom and abs(zoom - WALK_KNOB_Y) <= KNOB_TOLERANCE else
                 "survey" if zoom and abs(zoom - SURVEY_KNOB_Y) <= KNOB_TOLERANCE else zoom,
                 len(areas), (", statues ready near " + ", ".join(statues)) if statues else "", how)
        self.last = Look(self.n, now, purposes, areas, dot, how, statues, zoom, frame)
        return self.last

    def glance(self, purposes: str) -> Optional[Look]:
        """Open at the walking zoom, read, close. For callers that need facts and tap nothing."""
        from ..core import ui
        frame = self.open(purposes)
        if frame is None:
            return None
        look = self.record(frame, purposes)
        ui.tap(self.dev, ui.BACK_ARROW, 2)
        if self.det.detect().state == "area_map":
            ui.tap(self.dev, ui.BACK_ARROW, 2)
        return look

    # ------------------------------------------------------------------ facts
    def recent(self, max_age: float = CURRENT_ZONE_S) -> Optional[Look]:
        """The last look if it is at most max_age seconds old."""
        if self.last and time.monotonic() - self.last.at <= max_age:
            return self.last
        return None

    def fact(self, table: str, zone: str, max_age: float = OTHER_ZONES_S):
        """A kept fact about `zone` ("pct", "gate", "statue") no older than max_age, matched by zone name."""
        from .mapnav import label_is
        now = time.monotonic()
        for name, f in getattr(self, table).items():
            if now - f.at <= max_age and (same(name, zone) or label_is(name, zone)):
                return f.value
        return None

    def reuse(self, purposes: str, look: Look) -> Look:
        self.counts["reuse"] += 1
        log.info("[map] reuse %d for: %s (%.0f s old, for %s)", look.n, purposes, time.monotonic() - look.at,
                 look.purposes)
        return look

    def invalidate(self, event: str, zone: Optional[str] = None) -> None:
        """Drop the facts an event makes stale (the table in docs/big-map-survey.md)."""
        from .mapnav import label_is
        tables = {"gain": ("pct",), "pct_changed": ("pct",), "blessed": ("statue",), "zone_run_ended":
                  ("pct", "statue"), "new_day": ("pct", "gate", "statue")}.get(event, ())
        for t in tables:
            d = getattr(self, t)
            for name in [k for k in d if zone is None or same(k, zone) or label_is(k, zone)]:
                d.pop(name, None)
        if event in ("zone_changed", "gain") and self.last is not None:
            self.last.at = float("-inf")  # the last look no longer stands in for a new one
        log.debug("[map] stale: %s %s", event, zone or "")

    # ------------------------------------------------------------------ discovery
    def discovery_due(self) -> Optional[str]:
        """Why a discovery survey should run now, or None (mae: one full pan per server day)."""
        try:
            day = json.loads(STATE_FILE.read_text(encoding="utf-8")).get("day")
        except (OSError, ValueError):
            day = None
        return None if day == server_day() else "first of server day " + server_day()

    def discovered(self) -> None:
        self.counts["discovery"] += 1
        try:
            STATE_FILE.parent.mkdir(exist_ok=True)
            STATE_FILE.write_text(json.dumps({"day": server_day(), "at": time.strftime("%Y-%m-%dT%H:%M:%S")}),
                                  encoding="utf-8")
        except OSError:
            log.warning("could not write %s", STATE_FILE)

    def summary(self) -> str:
        return ", ".join(f"{k} {v}" for k, v in self.counts.items())


_SHARED: dict = {}


def get(dev, det) -> BigMap:
    """The process's BigMap for this device (roam and Clear Zone share it; a new detector keeps the facts)."""
    bm = _SHARED.get(id(dev))
    if bm is None:
        bm = _SHARED[id(dev)] = BigMap(dev, det)
    bm.det = det
    return bm


def read_areas(det, frame):
    from ..loops.roam import read_areas as _read  # the area reader lives with roam's survey
    return _read(det, frame)


def same(a: str, b: str) -> bool:
    from ..loops.roam import same as _same
    return _same(a, b)
