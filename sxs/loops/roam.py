"""Free exploration with no quest: pick an unexplored area on the area map, walk there, explore it, bless its statue.

    python -m sxs roam [--minutes 30] [--area "Verdantglade III"]

mae, 2026-11-04: "code general non-quest exploration". The pieces already existed one level down; this is the loop
over areas that strings them together:

1. Read the area map (R-076): every area label, and under the ones not finished yet an "Exploration: N%" line and
   sometimes a power gate ("12K"). Labels without a percentage are taken as done. mae, 2026-11-09: fully zoomed out,
   OCR merges neighbouring labels and drops the % lines, so the survey zooms out fully, steps one zoom closer, and
   reads a 3x3 grid of pans, stitched by the measured pan shift (`survey`).
   Every reading goes into the location tree (`sxs/policy/zones.py`, `resource/world/zones.json`): zones, CP, %,
   blessed, map neighbours, and which neighbour a walk got in from.
2. Pick the next area (`Tree.next_zone`): the zone we stand in if it isn't finished (R-132: finish the zone you're in
   first), else the lowest-CP zone not yet explored with recommended power at most 25% above ours (R-135, R-127), not
   given up on. The Verdantglade cap (handoff: 4 to 7 areas, or stop at a natural wall) is enforced by stopping at
   the first power wall, and by `--max-areas`.
3. Walk there with the area map and explore it (`fogwalk.walk`: minimap dots and unexplored tiles, then fog edge;
   fights and cards go through the usual rules).
4. When the area shows no percentage any more (100%), walk to each Lost Statue icon near its label and open the
   statue's card; the card rules unlock it (R-070: free, +1 Blessing Level).

Ends when no area is left to explore, the time is up, or a lower loop stops for a reason that needs a person
(defeat, unfamiliar screen).
"""

from __future__ import annotations

import difflib
import json
import logging
import re
import time
from dataclasses import dataclass
from typing import Optional

import cv2
import numpy as np

from ..actions import goto
from ..actions.common import close_rewards
from ..core import ui
from ..core.device import save_unknown
from ..core.loop import Loop, banner, progress
from ..core.marks import server_day
from ..core.nav import Navigator
from ..core.paths import LOGS, RESOURCE
from ..policy.decide import Context, Decider
from ..policy import fights
from ..policy.zones import Tree
from ..vision.badges import SMALL_MIN_AREA, find_badges
from ..vision.hud import read_power
from ..vision.ocr import power_k
from . import fogwalk

log = logging.getLogger("sxs.loops.roam")

STATUE_TEMPLATE = RESOURCE / "image" / "areamap" / "lost_statue.png"  # from docs/screens/world/area_map_lv22.png
STATUE_THRESHOLD = 0.8
STATUE_NEAR_LABEL = 260  # px on the area map: statues this close to an area's label belong to it
MAP_ROI = [0, 120, 720, 1100]  # labels below y 1185 are the kingdom buttons
STOP_REASONS = {"defeated", "unknown_screen", "left_area:home"}
SURVEY_ZOOM_OUT = 4  # "-" taps: enough to reach full zoom-out from any opening
# mae, 2026-11-09: read one step closer than full zoom-out (OCR merged labels there). Live the same day: one "+" tap
# jumps to the closest zoom (labels clipped to "/erdanto", % lines lost), so drag the slider knob up a little instead.
NAME_RE = re.compile(r"^[A-Z][a-z]+(?: [A-Z][a-z]+)*(?: [IVX]+)?$")  # a zone name as printed ("Monolith Ruins I")
MISREAD_RATIO = 0.7  # a new name this similar to a known zone's is a misread of it
ENCLOSURE = "Auroradrasil"  # enclosed: walks from inside to far labels don't move the character (2026-11-10)
FINISHED_READS = 3  # surveys in a row with no % line before a zone the tree has under 100% counts as finished (2 let Troll Lair, whose label sits on Verdantglade IV's, flip to 100%)
PAN_FROM = (300, 620)  # drag start for survey pans: on the map, clear of the legend and the zoom slider
PAN_PX, PAN_MS = 250, 1500  # a slow drag so the map doesn't fling on
# Reveal directions (east, south) for a 3x3 grid around the opening view: N, NW, W, SW, S, SE, E, NE.
PANS = [(0, -1), (-1, 0), (0, 1), (0, 1), (1, 0), (1, 0), (0, -1), (0, -1)]
STITCH_ROI = (0, 120, 655, 940)  # x, y, w, h compared between pans (left of the slider, under the title)
PCT_ROOM = 70  # px under a label for its % line: a label nearer the bottom edge can't prove it's finished
KINGDOM_ROI = [20, 25, 400, 60]  # the kingdom's name, top left of the area map
MAX_ENTRY_TRIES = 3  # connected areas to try walking in from before giving up on an area for the day
STATE_FILE = LOGS / "roam.json"  # statues opened and areas given up on, kept across runs
VERDANTGLADE_ISLAND = (300, 640)  # world overview (kingdom picker): Verdantglade's island
RETRY_POWER_GAIN = 0.5  # K: an area given up on is tried again once power grew this much (or on a later day)


@dataclass
class Area:
    name: str
    box: list[int]
    pct: Optional[int] = None  # None: no percentage shown (finished)
    gate: Optional[float] = None  # power needed, in K
    unsure: bool = False  # no % read, but the label was never far enough from the bottom edge to show one

    @property
    def point(self) -> tuple[int, int]:
        return ui.centre(self.box)


def same(a: str, b: str) -> bool:
    """Area names from two area-map readings. Labels near the edge come back clipped on the left ("tglade III"
    for "Verdantglade III"), so a suffix of 6+ letters also counts; trailing numerals must still agree."""
    if goto.same_area(a, b):
        return True
    x, y = goto.squeeze(a), goto.squeeze(b)
    short, long_ = sorted((x, y), key=len)
    return len(short) >= 6 and long_.endswith(short)


def read_areas(det, frame=None) -> list[Area]:
    """Area-map OCR into areas. A percentage or a power line belongs to the label right above it.

    Live 2026-11-09: OCR joins a % line with the neighbouring label ("Exploration: 78%onolith Ruins !"), and a
    neighbour's "Exploration: 0%" sat within reach of the Verdantglade V label, so it read 0%. Now the % is found
    anywhere in a line, its x is estimated from where it sits in the joined text, and it goes to the label whose
    width covers it (nearest above), not merely one within 120 px."""
    lines = det.read_text(MAP_ROI, frame)
    areas: list[Area] = []
    extras = []
    for text, box in lines:
        t = text.replace("-", " ").strip(" |")
        pct = (re.search(r"(?:Explor\w*\s*:?\s*)?(\d+)\s*%", t)
               # Live 2026-11-09: "Exploration: 83Monolith Ruins !" (the % sign lost where two labels touch).
               or re.search(r"Explor\w*\s*:?\s*(\d{1,3})(?=[A-Za-z])", t))
        if pct:
            x, y, w, h = box
            # Joined text: place the % part by its share of the characters.
            a0, a1 = pct.start() / max(1, len(t)), pct.end() / max(1, len(t))
            extras.append(("pct", int(pct.group(1)), [int(x + w * a0), y, max(1, int(w * (a1 - a0))), h]))
        elif re.fullmatch(r"\D{0,2}\d+(\.\d)?K", t):
            extras.append(("gate", power_k(t), box))
        elif len(t) >= 4 and box[0] < 540 and box[1] < 1185 and not re.search(r"%|Ore$|Sandstone|Portal|Statue|Ahead of", t):
            areas.append(Area(t, box))
    for kind, value, (x, y, w, h) in extras:
        cx = x + w / 2
        above = [a for a in areas if 0 < y - a.box[1] < 70
                 and abs((a.box[0] + a.box[2] / 2) - cx) < max(a.box[2] / 2, 50)]
        if above:
            target = min(above, key=lambda a: (y - a.box[1], abs((a.box[0] + a.box[2] / 2) - cx)))
            if getattr(target, kind) is None:
                setattr(target, kind, value)
    return areas


PATCH = (250, 380, 160, 360)  # x, y, w, h of the previous view matched in the next one to measure a pan
PAN_MATCH = 0.6  # below this the pan is not trusted and that view's reading is dropped (live 2026-11-09: guessed
# shifts put Zephyr Vale and Troll Lair 530 px west of where they are)


def pan_shift(prev: np.ndarray, cur: np.ndarray, expected: tuple[int, int] = (0, 0)) -> Optional[tuple[int, int]]:
    """How far the map content moved between two survey frames: patches of the previous view found in the current one
    by template matching on edges (labels and tile borders); the best match wins. Live 2026-11-09 the same drag moved
    the map 353 px, or 7 px at the map's edge, so the shift is measured, never assumed. None when nothing matches
    well."""
    x0, y0, w, h = PATCH
    sx, sy, sw, sh = STITCH_ROI
    edges = lambda im: cv2.Canny(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), 40, 120)  # noqa: E731
    a = edges(prev)
    b = edges(cur)[sy:sy + sh, sx:sx + sw]
    starts = {(int(min(max(sx, x0 - expected[0] / 2), sx + sw - w)), int(min(max(sy, y0 - expected[1] / 2), sy + sh - h)))}
    starts |= {(x, y) for x in (sx, sx + (sw - w) // 2, sx + sw - w) for y in (sy, sy + (sh - h) // 2, sy + sh - h)}
    best = (0.0, None)
    for x, y in starts:
        tpl = a[y:y + h, x:x + w]
        if tpl.mean() < 2:  # featureless (all fog): nothing to match on
            continue
        _, score, _, loc = cv2.minMaxLoc(cv2.matchTemplate(b, tpl, cv2.TM_CCOEFF_NORMED))
        if score > best[0]:
            best = (score, (sx + loc[0] - x, sy + loc[1] - y))
    return best[1] if best[0] >= PAN_MATCH else None


def merge_readings(readings: list, bottom: int = 1185) -> list[Area]:
    """Areas from several pans of one area-map opening, in the first view's coordinates. `readings` holds each pan's
    areas and how far the content had moved by then. The same label read twice keeps its % and gate from whichever
    reading had them; a label only ever read with no room under it for a % line is `unsure`, not finished."""
    out: list[Area] = []
    for areas, (ox, oy) in readings:
        for a in areas:
            x, y, w, h = a.box
            room = y + h + PCT_ROOM <= bottom
            g = Area(a.name, [x - ox, y - oy, w, h], a.pct, a.gate, unsure=a.pct is None and not room)
            # Same label: same name read the same way, or a clipped/loosely read name at about the same place (live
            # 2026-11-09: a loose name match alone gave Verdantglade VI the 78% of Verdantglade V).
            hit = next((m for m in out if goto.squeeze(m.name) == goto.squeeze(g.name)
                        or (same(m.name, g.name) and abs(m.point[0] - g.point[0]) + abs(m.point[1] - g.point[1]) < 80)),
                       None)
            if hit is None:
                out.append(g)
                continue
            if len(g.name) > len(hit.name):
                hit.name = g.name  # the reading not clipped by an edge
            if g.pct is not None and (hit.pct is None or g.pct > hit.pct):
                hit.pct, hit.unsure = g.pct, False
            elif hit.pct is None and not g.unsure:
                hit.unsure = False
            hit.gate = hit.gate or g.gate
    return out


def nearest_badge(frame: np.ndarray) -> Optional[tuple[int, int]]:
    """Area-map picker: the ready statue nearest our white dot (or the screen centre)."""
    from ..vision import area_map
    me = [p for k, p in area_map.objects(frame) if k == "player"]
    cx, cy = me[0] if me else goto.SCREEN_CENTRE
    pts = statue_badges(frame)
    return min(pts, key=lambda p: (p[0] - cx) ** 2 + (p[1] - cy) ** 2) if pts else None


ORE_YELLOW_PX = 250  # yellow pixels left of a badge that mean a gold ore icon


def statue_badges(frame: np.ndarray) -> list[tuple[int, int]]:
    """Area-map points of statues that can be blessed now: a small red "!" on a grey (unsaturated) statue icon
    (mae, 2026-11-05: the "!" means the zone is explored and its statue is ready; seen in Auroradrasil). The "!" on
    a gold ore icon is skipped by its size. Returns the icon's point, just below-left of the badge."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    out = []
    for bx, by in find_badges(frame, min_area=SMALL_MIN_AREA):
        # The statue icon is small and mostly hidden under its badge; a gold ore icon is a big yellow block.
        near = hsv[max(0, by - 10):by + 40, max(0, bx - 45):bx]
        yellow = ((near[..., 0] >= 15) & (near[..., 0] <= 35) & (near[..., 1] > 120) & (near[..., 2] > 150)).sum()
        if yellow < ORE_YELLOW_PX:
            out.append((bx - 4, by + 5))
    return out


def statue_points(frame: np.ndarray) -> list[tuple[int, int]]:
    tpl = cv2.imread(str(STATUE_TEMPLATE))
    r = cv2.matchTemplate(frame, tpl, cv2.TM_CCOEFF_NORMED)
    th, tw = tpl.shape[:2]
    out: list[tuple[int, int]] = []
    for y, x in zip(*np.where(r >= STATUE_THRESHOLD)):
        p = (int(x) + tw // 2, int(y) + th // 2)
        if all(abs(p[0] - q[0]) > tw or abs(p[1] - q[1]) > th for q in out):
            out.append(p)
    return out


def _load_state() -> dict:
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"statues": []}


def _save_state(s: dict) -> None:
    STATE_FILE.parent.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(s, indent=1), encoding="utf-8")


class Roamer:
    def __init__(self, dev, det):
        self.dev, self.det = dev, det
        self.nav = Navigator(dev, det)
        self.state = _load_state()
        self.given_up: set[str] = set()
        self.power: Optional[float] = None
        self.tree = Tree.load()
        self.no_pct: dict[str, int] = {}  # zone -> surveys in a row that showed it with no % line

    def give_up(self, name: str, why: str) -> None:
        """Skip `name` for the rest of this run, and in later runs the same server day until power grows (seen 2026-11-04:
        Verdantglade III has no way in on foot, and every new run spent its fog-walk budget at the same fog)."""
        log.info("giving up on %s: %s", name, why)
        self.given_up.add(name)
        self.state.setdefault("given_up", {})[name] = {"day": server_day(), "power": self.power, "why": why}
        _save_state(self.state)

    def tried_from(self, target: str) -> list[str]:
        """Neighbours a fog walk into `target` started from today without making progress."""
        t = self.state.get("tried_from", {}).get(target, {})
        return t.get("via", []) if t.get("day") == server_day() else []

    def failed_from(self, target: str, via: str) -> int:
        """Record a neighbour that didn't lead into `target`; returns how many untried neighbours remain."""
        rec = self.state.setdefault("tried_from", {})
        t = rec.get(target) if rec.get(target, {}).get("day") == server_day() else None
        t = t or {"day": server_day(), "via": []}
        if via not in t["via"]:
            t["via"].append(via)
        rec[target] = t
        _save_state(self.state)
        return len(t["via"])

    def skipped(self, name: str) -> bool:
        if name in self.given_up:
            return True
        g = next((v for k, v in self.state.get("given_up", {}).items() if same(k, name)), None)
        if not g or g.get("day") != server_day():
            return False
        return not (self.power and g.get("power") and self.power >= g["power"] + RETRY_POWER_GAIN)

    def _to_world(self) -> bool:
        if self.det.detect().state == "world_map":
            return True
        progress("to_world")
        self.nav.go_home()
        progress("home")
        self.dev.tap(*ui.NAV_WORLD)
        # Loading the island can take longer than 5 s (live 2026-11-10: "not_on_map" while it was still loading).
        d = self.det.detect()
        for _ in range(8):
            time.sleep(2)
            d = self.det.detect()
            if d.state in ("world_map", "world_overview"):
                break
        if d.state == "world_overview":  # the kingdom picker: tap Verdantglade's island
            self.dev.tap(*VERDANTGLADE_ISLAND)
            time.sleep(8)
            d = self.det.detect()
        return d.state == "world_map"

    def survey(self) -> tuple[list[Area], list[str], Optional[float]]:
        """Open the area map, read it, close it. Returns areas, zones with a statue ready to bless, and power.

        mae, 2026-11-09: zoomed all the way out, OCR merged neighbouring labels and lost the % lines. So zoom out
        fully, step one zoom closer, and read a 3x3 grid of pans; labels are placed in the first view's coordinates
        by the measured pan shift. Everything read goes into the location tree."""
        power = read_power(self.det)
        self.power = power or self.power
        if not goto.open_area_map(self.dev, self.det):
            log.warning("the area map did not open; frame %s", save_unknown(self.dev, "roam_survey"))
            return [], [], power
        goto.survey_zoom(self.dev)
        time.sleep(1)
        frame = self.dev.screenshot()
        kingdom = " ".join(t for t, _ in self.det.read_text(KINGDOM_ROI, frame)).strip()
        readings = [(read_areas(self.det, frame), (0, 0))]
        badges = [(p, (0, 0)) for p in statue_badges(frame)]
        shift, pending = (0, 0), (0, 0)
        # mae, 2026-11-10: the 3x3 pan grid (40-50 s per survey) wasted time; the survey zoom shows nearly the whole
        # kingdom. Pan only when a zone the location tree still has work in wasn't read in this view.
        first = [a.name for a in readings[0][0]]
        missing = [k for k, z in self.tree.zones.items() if z.get("kind", "zone") == "zone"
                   and not self.tree.done(k) and not any(same(n, k) for n in first)]
        pans = PANS if missing else []
        if missing:
            log.info("survey: %s not in view; panning", ", ".join(missing[:4]))
        for rx, ry in pans:
            fx, fy = PAN_FROM
            self.dev.swipe(fx, fy, fx - rx * PAN_PX, fy - ry * PAN_PX, PAN_MS)
            time.sleep(1.2)
            cur = self.dev.screenshot()
            pending = (pending[0] - rx * PAN_PX, pending[1] - ry * PAN_PX)  # drags since the last trusted view
            moved = pan_shift(frame, cur, pending)
            if moved is None:
                # Not sure where this view sits (or the map stopped at its edge): drop it, and measure the next pan
                # from the last trusted view.
                log.info("survey pan %s: couldn't match it to the last view; reading skipped", (rx, ry))
                continue
            pending = (0, 0)
            shift = (shift[0] + moved[0], shift[1] + moved[1])
            readings.append((read_areas(self.det, cur), shift))
            badges += [(p, shift) for p in statue_badges(cur)]
            frame = cur
            progress(("survey_pan", shift))
        self.dev.tap(*ui.BACK_ARROW)
        time.sleep(2)
        areas = merge_readings(readings)
        ready = self.statue_zones(areas, [(x - ox, y - oy) for (x, y), (ox, oy) in badges])
        self.remember(areas, kingdom)
        log.info("power %s; %s areas %s; statues ready in %s", power, kingdom or "?",
                 [(a.name, a.pct, a.gate) + (("unsure",) if a.unsure else ()) for a in areas], ready)
        return areas, ready, power

    @staticmethod
    def statue_zones(areas: list[Area], points: list[tuple[int, int]]) -> list[str]:
        """The zone each ready statue belongs to: the nearest label within STATUE_NEAR_LABEL."""
        out = []
        for p in points:
            near = [a for a in areas if abs(a.point[0] - p[0]) + abs(a.point[1] - p[1]) < STATUE_NEAR_LABEL]
            if near:
                name = min(near, key=lambda a: abs(a.point[0] - p[0]) + abs(a.point[1] - p[1])).name
                if name not in out:
                    out.append(name)
        return out

    def remember(self, areas: list[Area], kingdom: str) -> None:
        """Write a survey into the location tree (resource/world/zones.json)."""
        kingdom = re.sub(r"[^A-Za-z ]", "", kingdom).strip()
        for a in areas:
            if len(goto.squeeze(a.name)) < 5 or (kingdom and goto.squeeze(a.name) == goto.squeeze(kingdom)):
                continue  # the kingdom title, or an OCR scrap
            known = self.tree.key(a.name) or self.label_prefix_zone(a.name)
            near = [k for k in self.tree.zones
                    if difflib.SequenceMatcher(None, goto.squeeze(k), goto.squeeze(a.name)).ratio() >= MISREAD_RATIO]
            if not known and near:
                # Close to a zone we know but not it: an OCR misread ("Verdantgladeto", "Iden Camp", live
                # 2026-11-09), not a new zone.
                continue
            if not known and (not NAME_RE.match(a.name) or re.search(r"Explor|%", a.name)
                              or len(goto.squeeze(a.name)) < 7):
                log.info("not adding %r to the location tree: doesn't read as a zone name", a.name)
                continue  # live 2026-11-09: "/erdanto", "Exploratio", "ildbloom Coastdden Camp" went in
            pct = ... if a.unsure else a.pct
            z = self.tree.zones.get(known) if known else None
            if pct is None and z and (z.get("pct") or 0) < 100:
                # No % line read for a zone we know is unfinished: OCR drops lines, so one reading isn't proof
                # (live 2026-11-09: Verdantglade V at 78% was declared finished). Count it; trust it the second time.
                n = self.no_pct.get(known, 0) + 1
                self.no_pct[known] = n
                if n < FINISHED_READS:
                    log.info("%s showed no %% line (%s%% before): finished only if the next survey agrees", known,
                             z.get("pct"))
                    pct = ...
            elif known:
                self.no_pct.pop(known, None)
            self.tree.observe(known or a.name, kingdom or None, pct=pct, cp=a.gate if a.gate else ..., point=a.point)
        if kingdom:
            self.tree.link_neighbours_by_map(kingdom)
        self.tree.save()

    def bless_ready(self, zones: list[str]) -> int:
        """mae, 2026-11-05: a statue with a red "!" on the area map is ready. Walk to its zone, then to the badge
        nearest us the big-map way (tap it on the area map, close the map, tap the middle of the screen) and unlock it
        through the card rules."""
        done = 0
        for name in zones[:3]:
            # The zone is only a guess from the nearest label (live 2026-11-10: Verdantglade V's statue was put in
            # "Wildbloom Coast" and the walk to that label went nowhere). Walk straight to the badge nearest us.
            log.info("statue ready to bless (near the %s label)", name)
            progress(("bless", name))
            why = goto.go_to(self.dev, self.det, nearest_badge)
            progress(("bless_walk", why))
            if why in ("not_on_map", "no_target"):
                continue
            self.dev.tap(*goto.SCREEN_CENTRE)
            time.sleep(4)
            if self.det.detect().state in ("world_map", "unknown") and not self.det.read_text([60, 560, 600, 80]):
                continue
            card, choice = Decider(self.det).decide(Context(goal="explore"))
            log.info("statue card %r -> %s", card.title, choice.kind)
            self.dev.tap(*choice.point)
            time.sleep(3)
            close_rewards(self.dev, self.det)
            self.tree.mark_blessed(name)
            self.tree.save()
            progress(("blessed", name))
            done += 1
        return done

    def pick(self, areas: list[Area], power: Optional[float], here: str = "") -> tuple[Optional[Area], Optional[Area]]:
        """(next area to explore, first area behind a power wall), by the location tree (`Tree.next_zone`):

        - R-132 (mae, 2026-11-09): the zone we stand in comes first while it's under 100% and in reach; a walk
          doesn't cross a dotted border out of an unfinished zone.
        - R-135: else the lowest-CP zone not yet explored, at most 25% above our power (zones with no CP last).
        The tree was just updated from this survey; zones it knows but this survey didn't read still count (walked to
        by name), except ones given up on."""
        skip = [k for k in self.tree.zones if self.skipped(k)]
        name = self.tree.next_zone(power, here, skip=skip)
        target = None
        if name:
            target = next((a for a in areas if goto.squeeze(a.name) == goto.squeeze(name)), None) or                 next((a for a in areas if same(a.name, name)), None)
            if target is not None and target.name != name:
                # The tree's name, not the label read (live 2026-11-10: "Wildbloom CoastHidden Camp", two labels OCR
                # joined, became the zone to explore and no walk or zone check could ever match it).
                target = Area(name, target.box, target.pct if goto.squeeze(target.name) == goto.squeeze(name) else
                              (self.tree.get(name) or {}).get("pct"), target.gate, target.unsure)
            if target is None:
                z = self.tree.zones[name]
                target = Area(name, [0, 0, 0, 0], z.get("pct"), z.get("cp"))
                log.info("%s is next by the location tree but wasn't read on this survey", name)
            elif target.pct is None:
                target.pct = (self.tree.get(name) or {}).get("pct")
        todo = [k for k, z in self.tree.zones.items() if z.get("kind", "zone") == "zone" and not self.tree.done(k)]
        walled = [k for k in todo if not fights.within_reach(self.tree.zones[k].get("cp"), power)]
        walled.sort(key=lambda k: self.tree.zones[k].get("cp") or 0)
        wall = None
        if walled:
            z = self.tree.zones[walled[0]]
            wall = Area(walled[0], [0, 0, 0, 0], z.get("pct"), z.get("cp"))
        return target, wall

    def approach(self, areas: list[Area], target: Area) -> Optional[Area]:
        """mae, 2026-11-04: "try moving from areas you are connected to". Walk into the explored area whose label
        sits nearest the target's on the area map, then toward the target as far as the explored ground goes; the
        fog walk takes it from there. Returns the neighbour used (None if there is none: walk to the label)."""
        here = fogwalk.zone_here(self.dev, self.det, self.tree)  # R-140: the minimap name first, then the big map
        progress(("zone_here", here))
        if here and same(here, target.name):
            log.info("already in %s: finishing it here first (R-132)", target.name)
            return None
        # R-150 (mae, 2026-11-10): start a new zone at its entrance, the explored ground nearest it on the big map;
        # the fog walk then steps onto the tiles beside its fog. Only for a zone not yet walked into.
        if not (self.tree.get(target.name) or {}).get("entries"):
            progress(("entrance", target.name))
            why = goto.go_to(self.dev, self.det, self.entrance_picker(target.name), pan_for_target=True)
            log.info("walk to %s's entrance (explored ground nearest it): %s", target.name, why)
            if why == "arrived":
                # The entrance is on the neighbour's ground: the fog walk may stand there and cross into the target
                # (live 2026-11-10: without this it "went back" to Wildbloom Coast by a big-map jump at once).
                now = goto.area_name_here(self.det)
                if now and not same(now, target.name):
                    return Area(self.tree.key(now) or now, [0, 0, 0, 0])
                return None
        # Try the plain big-map walk to the zone's label first: most zones can be walked into from where we are
        # (live 2026-11-09: from Verdantglade VI the walk "via Verdantglade IV" landed in Auroradrasil instead).
        progress(("walk_to", target.name))
        first = goto.go_to(self.dev, self.det, target.name)
        if first == "no_move" or (here and same(here, ENCLOSURE)):
            # Live 2026-11-10: from inside Auroradrasil (an enclosed clearing inside Verdantglade V) big-map walks to
            # far labels don't move the character. Step out first: the tracked quest's pointer led out before.
            if self.escape():
                first = goto.go_to(self.dev, self.det, target.name)
        if first == "arrived":
            now = goto.area_name_here(self.det)
            if now and same(now, target.name):
                log.info("walked into %s from %s directly", target.name, here or "?")
                if here:
                    self.tree.record_entry(target.name, here, True, server_day(), xy=goto.coords(self.det))
                    self.tree.save()
                return None
            log.info("the walk to %s's label ended in %s; trying a connected area", target.name, now or "?")
        # Only zones the location tree knows, explored (live 2026-11-10: the kingdom's title "Verdantglade" and a
        # clipped "Verdant" were picked as the neighbour to walk in from).
        done = [a for a in areas if a.pct is None and not a.unsure and not same(a.name, target.name)
                and self.tree.key(a.name) and self.tree.explored(a.name)]
        if not done:
            goto.go_to(self.dev, self.det, target.name)
            return None
        tx, ty = target.point
        # Nearest neighbour first; one that already failed today for this target is tried last (2026-11-04:
        # Verdantglade III can't be entered from Moonveil Woods, its nearest label, so try Damp Woods or
        # Verdantglade II next, in the next short run).
        # The location tree knows better than label distance: the neighbour a walk got in from before, then walked
        # links, then map neighbours (zones.Tree.entry_candidates); those not in the tree keep the distance order.
        tried = self.tried_from(target.name)
        ranked = self.tree.entry_candidates(target.name, server_day())
        rank = lambda a: next((i for i, n in enumerate(ranked) if same(n, a.name)), len(ranked))  # noqa: E731
        done.sort(key=lambda a: (any(same(a.name, t) for t in tried), rank(a),
                                 (a.point[0] - tx) ** 2 + (a.point[1] - ty) ** 2))
        via = done[0]
        progress(("approach", target.name, via.name))
        log.info("approaching %s from the connected area %s (standing in %s)", target.name, via.name, here)
        # Most of the way from the neighbour's label toward the target's, so the walk ends on the shared border.
        if (goto.go_to(self.dev, self.det, (via.name, target.name, 0.6)) != "arrived"
                and not goto.same_area(here, via.name)):
            goto.go_to(self.dev, self.det, via.name)
        return via

    def label_prefix_zone(self, label: str) -> Optional[str]:
        """The known zone a joined label starts with ("Wildboom CoastHidden" -> Wildbloom Coast, live 2026-11-10: its
        92% was dropped as a misread and roam gave the zone up)."""
        sq = goto.squeeze(label)
        best = None
        for k in self.tree.zones:
            kk = goto.squeeze(k)
            if (len(kk) >= 6 and len(sq) >= len(kk) + 3 and not re.fullmatch(r"[ivx]+", sq[len(kk):])
                    and difflib.SequenceMatcher(None, kk, sq[:len(kk)]).ratio() >= 0.85):
                if best is None or len(kk) > len(goto.squeeze(best)):
                    best = k
        return best

    def entrance_picker(self, name: str):
        """Area-map picker: the explored-ground point nearest `name`'s label (R-150)."""
        from ..vision import area_map

        def pick(frame):
            labels = fogwalk.map_labels(self.det, frame)
            hits = [p for k, p in labels.items() if same(k, name) or goto.close_name(k, name)]
            return area_map.entrance(frame, hits[0]) if hits else None
        return pick

    def escape(self) -> bool:
        """Leave an enclosed area the big-map walks can't route out of, by following the tracked quest's pointer (one
        or two steps). True if the zone under the minimap changed."""
        before = goto.area_name_here(self.det)
        for _ in range(2):
            if not fogwalk.quest_step(self.dev, self.det, fight=True):
                break
            now = goto.area_name_here(self.det)
            if now and not same(now, before):
                log.info("left %s by the quest pointer (now in %s)", before, now)
                return True
        log.info("could not leave %s by the quest pointer", before)
        return False

    def bless_near(self, area_name: str) -> int:
        """Walk to each statue icon near the area's label that this bot hasn't opened yet and open its card."""
        opened = 0
        for _ in range(3):
            self.dev.tap(*goto.MINIMAP)
            time.sleep(2.5)
            frame = self.dev.screenshot()
            areas = {a.name: a for a in read_areas(self.det, frame)}
            label = next((a for n, a in areas.items() if same(n, area_name)), None)
            statues = statue_badges(frame) + [p for p in statue_points(frame)]
            self.dev.tap(*ui.BACK_ARROW)
            time.sleep(2)
            if label is None:
                return opened
            key = lambda p: f"{area_name}@{p[0] // 20},{p[1] // 20}"
            near = [p for p in statues if abs(p[0] - label.point[0]) + abs(p[1] - label.point[1]) < STATUE_NEAR_LABEL
                    and key(p) not in self.state["statues"]]
            if not near:
                return opened
            p = min(near, key=lambda q: abs(q[0] - label.point[0]) + abs(q[1] - label.point[1]))
            log.info("statue near %s at area-map %s: walking there", area_name, p)
            goto.go_to(self.dev, self.det, p)
            # The camera stays where the area map put it, so the statue is mid-screen: select it, then open it.
            for _ in range(2):
                self.dev.tap(*goto.SCREEN_CENTRE)
                time.sleep(3)
            d = self.det.detect()
            if d.state not in ("world_map", "unknown"):
                card, choice = Decider(self.det).decide(Context(goal="explore"))
                log.info("statue card %r -> %s", card.title, choice.kind)
                self.dev.tap(*choice.point)
                time.sleep(3)
                close_rewards(self.dev, self.det)  # blessing rewards: tap to continue
                opened += 1
            self.state["statues"].append(key(p))
            _save_state(self.state)
        return opened

    def run(self, minutes: float, area: Optional[str], max_areas: int, walk_minutes: float) -> str:
        banner(log, "Roam", "free exploration: pick an unexplored area on the area map, walk there, explore it "
               "(minimap dots, unexplored tiles, fog), then bless its statue",
               f"{minutes:g} minutes, {max_areas} areas, no area left under its power gate, a lost fight or an "
               "unfamiliar screen")
        deadline = time.monotonic() + minutes * 60
        done = 0
        if not self._to_world():
            return "not_on_map"
        while time.monotonic() < deadline and done < max_areas:
            areas, statues, power = self.survey()
            if not areas:
                return "no_area_map"  # nothing read: not evidence that anything is finished
            if statues and self.bless_ready(statues):
                continue  # blessed something: read the map again
            if area:
                target = next((a for a in areas if same(a.name, area)), None)
                if self.tree.explored(area) or (self.tree.get(area) is None and target and target.pct is None
                                                 and not target.unsure):
                    log.info("%s is explored (location tree): finished", area)
                    self.bless_near(area)
                    return "area_done"
                z = self.tree.get(area) or {}
                if target is None or target.pct is None:  # the label or its % line wasn't read: the tree knows
                    target = Area(self.tree.key(area) or area, target.box if target else [0, 0, 0, 0],
                                  z.get("pct"), z.get("cp"))
                wall = None
            else:
                target, wall = self.pick(areas, power, goto.area_name_here(self.det))
            if target is None:
                if wall:
                    log.info("next area %s needs %sK (power %sK): natural wall", wall.name, wall.gate, power)
                    return "power_wall"
                # Every zone in reach is blessed (mae): one last fog walk for ground nobody has walked yet.
                why = fogwalk.walk(self.dev, self.det, minutes=walk_minutes)
                log.info("all zones blessed; fog walk for leftover ground ended: %s", why)
                return "exploration_concluded" if why == "no_fog" else "all_explored"
            log.info("exploring %s (%s%%, %sK)", target.name, target.pct, target.gate)
            via = self.approach(areas, target)
            left = (deadline - time.monotonic()) / 60
            why = fogwalk.walk(self.dev, self.det, minutes=min(walk_minutes, max(1.0, left)), area=target.name,
                               allowed={via.name} if via else None, walk_there=False)
            log.info("fog walk in %s ended: %s", target.name, why)
            if why in STOP_REASONS:
                return why
            if not self._to_world():
                return "not_on_map"
            areas, _, _ = self.survey()
            now = next((a for a in areas if same(a.name, target.name)), None)
            if now is None:
                # Label not read this time (clipped by the edge, or OCR): not evidence that it's finished.
                # Label not read: only this run, it says nothing about the area itself.
                log.info("%s not on this reading of the area map; giving up on it this run", target.name)
                self.given_up.add(target.name)
                if area:
                    return "no_progress"
            elif now.pct is None and now.unsure:
                log.info("%s: %% line not readable this time; trying again next pass", target.name)
            elif now.pct is None and not self.tree.explored(target.name):
                # The tree still has it unfinished: one reading without a % line isn't proof (live 2026-11-09: run 5
                # declared Verdantglade V finished when OCR joined its "83%" to Monolith Ruins' label).
                log.info("%s showed no %% line but the location tree has it at %s%%: not finished", target.name,
                         (self.tree.get(target.name) or {}).get("pct"))
            elif now.pct is None:
                if via:
                    self.tree.record_entry(target.name, via.name, True, server_day())
                    self.tree.save()
                log.info("%s finished; looking for its statue", target.name)
                self.bless_near(target.name)
                done += 1
            elif target.pct is not None and now.pct > target.pct:
                if via:
                    self.tree.record_entry(target.name, via.name, True, server_day())
                    self.tree.save()
            elif now.pct == target.pct:
                if via:
                    self.tree.record_entry(target.name, via.name, False, server_day(), why=f"fog walk {why}")
                    self.tree.save()
                if via and self.failed_from(target.name, via.name) < MAX_ENTRY_TRIES:
                    # Not in from this side: the next run tries the next-nearest connected area instead.
                    log.info("no way into %s from %s; the next run tries another neighbour", target.name, via.name)
                    self.given_up.add(target.name)
                else:
                    self.give_up(target.name, f"fog walk ended {why!r} without moving off {now.pct}% "
                                 f"(tried from {', '.join(self.tried_from(target.name)) or 'its label'})")
                if area:
                    return "no_progress"
        return "timeout" if time.monotonic() >= deadline else "max_areas"


def _args(p) -> None:
    p.add_argument("--minutes", type=float, default=20,  # an outer ceiling only: the runner's progress check ends
                   help="upper limit; normally the 2-minute progress check ends the run")  # a stuck run (mae)
    p.add_argument("--area", help="explore only this area (as named on the area map)")
    p.add_argument("--max-areas", type=int, default=10)
    p.add_argument("--walk-minutes", type=float, default=2, help="fog walk budget per pass")


def _run(ctx, opts):
    return Roamer(ctx.dev, ctx.det).run(opts.minutes, opts.area, opts.max_areas, opts.walk_minutes)


OK = {"area_done", "power_wall", "all_explored", "timeout", "max_areas", "exploration_concluded"}
LOOP = Loop("roam", "Roam", "free exploration: unexplored areas under our power, then their statues", _run, _args,
            ok=OK)
