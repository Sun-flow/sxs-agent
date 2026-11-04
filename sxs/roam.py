"""Free exploration with no quest: pick an unexplored area on the area map, walk there, explore it, bless its statue.

    python -m sxs.roam [--minutes 30] [--area "Verdantglade III"]

mae, 2026-11-04: "code general non-quest exploration". The pieces already existed one level down; this is the loop
over areas that strings them together:

1. Read the area map (R-076): every area label, and under the ones not finished yet an "Exploration: N%" line and
   sometimes a power gate ("12K"). Labels without a percentage are taken as done.
2. Pick the next area: under 100%, power gate at or under our power (HUD), not given up on this run. The
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

import argparse
import json
import logging
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from . import fogwalk, goto, nav
from .decide import Context, Decider
from .device import Device, banner
from .state import StateDetector

log = logging.getLogger("sxs.roam")

ROOT = Path(__file__).resolve().parent.parent
STATUE_TEMPLATE = ROOT / "resource" / "image" / "areamap" / "lost_statue.png"  # from docs/screens/area_map_lv22.png
STATUE_THRESHOLD = 0.8
STATUE_NEAR_LABEL = 260  # px on the area map: statues this close to an area's label belong to it
HUD_POWER_ROI = [110, 70, 170, 40]  # "16.9K" next to the crossed-swords icon on the map and home HUDs
MAP_ROI = [0, 120, 720, 1100]  # labels below y 1185 are the kingdom buttons
STOP_REASONS = {"defeated", "unknown_screen", "left_area:home"}
STATE_FILE = ROOT / "logs" / "roam.json"  # statues opened, so a later run doesn't walk back to them


@dataclass
class Area:
    name: str
    box: list[int]
    pct: Optional[int] = None  # None: no percentage shown (finished)
    gate: Optional[float] = None  # power needed, in K

    @property
    def point(self) -> tuple[int, int]:
        x, y, w, h = self.box
        return x + w // 2, y + h // 2


def parse_power(text: str) -> Optional[float]:
    m = re.search(r"(\d+(?:\.\d+)?)\s*K", text.replace(",", "."))
    return float(m.group(1)) if m else None


def read_power(det: StateDetector, frame=None) -> Optional[float]:
    return parse_power(" ".join(t for t, _ in det.read_text(HUD_POWER_ROI, frame)))


def read_areas(det: StateDetector, frame=None) -> list[Area]:
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
            extras.append(("gate", parse_power(t), box))
        elif len(t) >= 4 and box[0] < 540 and box[1] < 1185 and not re.search(r"%|Ore$|Sandstone|Portal|Statue|Ahead of", t):
            areas.append(Area(t, box))
    for kind, value, (x, y, w, h) in extras:
        above = [a for a in areas if 0 < y - a.box[1] < 70 and abs((a.box[0] + a.box[2] / 2) - (x + w / 2)) < 120]
        if above:
            target = min(above, key=lambda a: y - a.box[1])
            setattr(target, kind, value)
    return areas


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
    def __init__(self, dev: Device, det: StateDetector):
        self.dev, self.det = dev, det
        self.nav = nav.Navigator(dev, det)
        self.given_up: set[str] = set()
        self.state = _load_state()

    def _to_world(self) -> bool:
        if self.det.detect().state == "world_map":
            return True
        self.nav.go_home()
        self.dev.tap(*nav.NAV_WORLD)
        time.sleep(5)
        d = self.det.detect()
        if d.state == "world_overview":  # the kingdom picker: tap Verdantglade's island
            self.dev.tap(300, 640)
            time.sleep(8)
            d = self.det.detect()
        return d.state == "world_map"

    def survey(self) -> tuple[list[Area], list[tuple[int, int]], Optional[float]]:
        """Open the area map, read it, close it. Returns areas, statue icons (area-map points) and power."""
        power = read_power(self.det)
        self.dev.tap(*goto.MINIMAP)
        time.sleep(2.5)
        frame = self.dev.screenshot()
        areas = read_areas(self.det, frame)
        statues = statue_points(frame)
        self.dev.tap(*nav.BACK_ARROW)
        time.sleep(2)
        log.info("power %s; areas %s; %d statue icons", power,
                 [(a.name, a.pct, a.gate) for a in areas], len(statues))
        return areas, statues, power

    def pick(self, areas: list[Area], power: Optional[float]) -> tuple[Optional[Area], Optional[Area]]:
        """(next area to explore, first area behind a power wall)."""
        todo = [a for a in areas if a.pct is not None and a.pct < 100 and a.name not in self.given_up]
        walled = [a for a in todo if a.gate and (power is None or a.gate > power)]
        open_ = [a for a in todo if a not in walled]
        open_.sort(key=lambda a: -a.pct)  # nearly done first: finishing an area unlocks its statue
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
        via = min(done, key=lambda a: (a.point[0] - tx) ** 2 + (a.point[1] - ty) ** 2)
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
            label = next((a for n, a in areas.items() if goto.same_area(n, area_name)), None)
            statues = statue_points(frame)
            self.dev.tap(*nav.BACK_ARROW)
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
                for _ in range(3):  # blessing rewards: tap to continue
                    if self.det.detect().state in ("reward_popup", "tap_to_continue"):
                        self.dev.tap(*nav.REWARD_CLOSE)
                        time.sleep(1.5)
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
            areas, _, power = self.survey()
            if area:
                target = next((a for a in areas if goto.same_area(a.name, area)), None)
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
                return "all_explored"
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
            now = next((a for a in areas if goto.same_area(a.name, target.name)), None)
            if now is None or now.pct is None:
                log.info("%s finished; looking for its statue", target.name)
                self.bless_near(target.name)
                done += 1
            elif now.pct == target.pct:
                log.info("%s didn't move off %s%%; giving up on it this run", target.name, now.pct)
                self.given_up.add(target.name)
                if area:
                    return "no_progress"
        return "timeout" if time.monotonic() >= deadline else "max_areas"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--minutes", type=float, default=30)
    p.add_argument("--area", help="explore only this area (as named on the area map)")
    p.add_argument("--max-areas", type=int, default=2)
    p.add_argument("--walk-minutes", type=float, default=10, help="fog walk budget per pass")
    args = p.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    dev = Device()
    print(Roamer(dev, StateDetector(dev)).run(args.minutes, args.area, args.max_areas, args.walk_minutes), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
