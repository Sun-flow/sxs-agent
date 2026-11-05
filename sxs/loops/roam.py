"""Free exploration with no quest: pick an unexplored area on the area map, walk there, explore it, bless its statue.

    python -m sxs roam [--minutes 30] [--area "Verdantglade III"]

mae, 2026-11-04: "code general non-quest exploration". The pieces already existed one level down; this is the loop
over areas that strings them together:

1. Read the area map (R-076): every area label, and under the ones not finished yet an "Exploration: N%" line and
   sometimes a power gate ("12K"). Labels without a percentage are taken as done.
2. Pick the next area: under 100%, recommended power at most 25% above ours (HUD, `policy.fights`), not given up on this run. The
   Verdantglade cap (handoff: 4 to 7 areas, or stop at a natural wall) is enforced by stopping at the first
   power wall, and by `--max-areas`.
3. Walk there with the area map and explore it (`fogwalk.walk`: minimap dots and unexplored tiles, then fog edge;
   fights and cards go through the usual rules).
4. When the area shows no percentage any more (100%), walk to each Lost Statue icon near its label and open the
   statue's card; the card rules unlock it (R-070: free, +1 Blessing Level).

Ends when no area is left to explore, the time is up, or a lower loop stops for a reason that needs a person
(defeat, unfamiliar screen).
"""

from __future__ import annotations

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
from ..core.loop import Loop, banner, progress
from ..core.marks import server_day
from ..core.nav import Navigator
from ..core.paths import LOGS, RESOURCE
from ..policy.decide import Context, Decider
from ..policy import fights
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
    """Area-map OCR into areas. A percentage or a power line belongs to the nearest label above it."""
    lines = det.read_text(MAP_ROI, frame)
    areas: list[Area] = []
    extras = []
    for text, box in lines:
        t = text.replace("-", " ").strip(" |")
        pct = re.search(r"(?:Exploration\s*:?\s*)?(\d+)\s*%$", t)
        if pct:
            extras.append(("pct", int(pct.group(1)), box))
        elif re.fullmatch(r"\D{0,2}\d+(\.\d)?K", t):
            extras.append(("gate", power_k(t), box))
        elif len(t) >= 4 and box[0] < 540 and box[1] < 1185 and not re.search(r"%|Ore$|Sandstone|Portal|Statue|Ahead of", t):
            areas.append(Area(t, box))
    for kind, value, (x, y, w, h) in extras:
        above = [a for a in areas if 0 < y - a.box[1] < 70 and abs((a.box[0] + a.box[2] / 2) - (x + w / 2)) < 120]
        if above:
            target = min(above, key=lambda a: y - a.box[1])
            setattr(target, kind, value)
    return areas


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
        self.nav.go_home()
        self.dev.tap(*ui.NAV_WORLD)
        time.sleep(5)
        d = self.det.detect()
        if d.state == "world_overview":  # the kingdom picker: tap Verdantglade's island
            self.dev.tap(*VERDANTGLADE_ISLAND)
            time.sleep(8)
            d = self.det.detect()
        return d.state == "world_map"

    def survey(self) -> tuple[list[Area], list[tuple[int, int]], Optional[float]]:
        """Open the area map, read it, close it. Returns areas, statue icons (area-map points) and power."""
        power = read_power(self.det)
        self.power = power or self.power
        self.dev.tap(*goto.MINIMAP)
        time.sleep(2.5)
        frame = self.dev.screenshot()
        areas = read_areas(self.det, frame)
        statues = statue_badges(frame)  # statues ready to bless (red "!"), as area-map points
        self.dev.tap(*ui.BACK_ARROW)
        time.sleep(2)
        log.info("power %s; areas %s; %d statues ready to bless", power,
                 [(a.name, a.pct, a.gate) for a in areas], len(statues))
        return areas, statues, power

    def bless_ready(self, statues: list[tuple[int, int]]) -> int:
        """mae, 2026-11-05: a statue with a red "!" on the area map is ready: walk there the big-map way (tap it on
        the area map, close the map, tap the middle of the screen) and unlock it through the card rules."""
        done = 0
        for p in statues[:3]:
            log.info("statue ready to bless at area-map %s", p)
            if goto.go_to(self.dev, self.det, p) == "not_on_map":
                break
            self.dev.tap(*goto.SCREEN_CENTRE)
            time.sleep(4)
            if self.det.detect().state in ("world_map", "unknown") and not self.det.read_text([60, 560, 600, 80]):
                continue
            card, choice = Decider(self.det).decide(Context(goal="explore"))
            log.info("statue card %r -> %s", card.title, choice.kind)
            self.dev.tap(*choice.point)
            time.sleep(3)
            close_rewards(self.dev, self.det)
            progress(("blessed", p))
            done += 1
        return done

    def pick(self, areas: list[Area], power: Optional[float]) -> tuple[Optional[Area], Optional[Area]]:
        """(next area to explore, first area behind a power wall)."""
        todo = [a for a in areas if a.pct is not None and a.pct < 100 and not self.skipped(a.name)]
        walled = [a for a in todo if not fights.within_reach(a.gate, power)]  # up to 25% above us (mae)
        open_ = [a for a in todo if a not in walled]
        # mae, 2026-11-05: the lowest-CP zone not yet blessed first (no power line counts as the lowest), then the one
        # nearest done; explore it until its statue is blessed, then the next.
        open_.sort(key=lambda a: (a.gate or 0, -a.pct))
        return (open_[0] if open_ else None), (walled[0] if walled else None)

    def approach(self, areas: list[Area], target: Area) -> Optional[Area]:
        """mae, 2026-11-04: "try moving from areas you are connected to". Walk into the explored area whose label
        sits nearest the target's on the area map, then toward the target as far as the explored ground goes; the
        fog walk takes it from there. Returns the neighbour used (None if there is none: walk to the label)."""
        done = [a for a in areas if a.pct is None and a.name != target.name]
        if not done:
            goto.go_to(self.dev, self.det, target.name)
            return None
        tx, ty = target.point
        # Nearest neighbour first; one that already failed today for this target is tried last (2026-11-04:
        # Verdantglade III can't be entered from Moonveil Woods, its nearest label, so try Damp Woods or
        # Verdantglade II next, in the next short run).
        tried = self.tried_from(target.name)
        done.sort(key=lambda a: (any(same(a.name, t) for t in tried), (a.point[0] - tx) ** 2 + (a.point[1] - ty) ** 2))
        via = done[0]
        here = goto.area_name_here(self.det)
        log.info("approaching %s from the connected area %s (standing in %s)", target.name, via.name, here)
        # Most of the way from the neighbour's label toward the target's, so the walk ends on the shared border.
        if (goto.go_to(self.dev, self.det, (via.name, target.name, 0.6)) != "arrived"
                and not goto.same_area(here, via.name)):
            goto.go_to(self.dev, self.det, via.name)
        return via

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
            if statues and self.bless_ready(statues):
                continue  # blessed something: read the map again
            if area:
                target = next((a for a in areas if same(a.name, area)), None)
                if target is None or target.pct is None:
                    log.info("%s shows no percentage: finished", area)
                    self.bless_near(area)
                    return "area_done"
                wall = None
            else:
                target, wall = self.pick(areas, power)
            if target is None:
                if wall:
                    log.info("next area %s needs %sK (power %sK): natural wall", wall.name, wall.gate, power)
                    return "power_wall"
                # Every zone in reach is blessed (mae): one last fog walk for ground nobody has walked yet.
                why = fogwalk.walk(self.dev, self.det, minutes=walk_minutes)
                log.info("all zones blessed; fog walk for leftover ground ended: %s", why)
                return "exploration_concluded" if why == "no_fog" else "all_explored"
            log.info("exploring %s (%s%%)", target.name, target.pct)
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
            elif now.pct is None:
                log.info("%s finished; looking for its statue", target.name)
                self.bless_near(target.name)
                done += 1
            elif now.pct == target.pct:
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
