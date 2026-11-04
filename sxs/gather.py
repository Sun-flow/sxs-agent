"""Gather Loop: spend spare stamina on overworld resource pickups of the priority material (R-106 to R-109).

    python -m sxs.gather                       # priority material from resource/policy/gather.json
    python -m sxs.gather --material sand       # one-off override
    python -m sxs.gather --check               # read stamina and the plan, tap nothing on the map

Route (mae, 2026-11-04): home > Journal (bottom bar, 2nd icon) > Map Exploration > Resource Hunt: pick the material,
Go, OK ("Enter Verdantglade to explore?"). The game drops us in the area that holds it with a tracking ring over
the nearest pickup. Each pickup costs 5 stamina; the bot keeps at least `keep_stamina` (70) for the daily
commissions and stops there. Special nodes (a green timer circle at the upper right, e.g. a Grand Mine) are free and
high value: always taken first.

How a pickup is found on the map, best first:
  1. a "bolt 5" cost label (template Gather.StaminaCost): shown under pickups close to the character; tap the
     pickup just above it;
  2. the tracking ring (a bright yellow/white circle round the material's icon) on the play area: tap it, the
     character walks there and mines it;
  3. the same ring on the minimap or clipped at a screen edge: tap it, the camera pans to the target.
Stuck checks: stamina must drop within STALE_ACTIONS taps; the coordinates must change while walking. No model calls.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import time
from typing import Optional

import cv2
import numpy as np

from . import fogwalk, nav
from .device import REPO_ROOT, Device, banner, save_unknown
from .state import StateDetector

log = logging.getLogger("sxs.gather")

POLICY = REPO_ROOT / "resource" / "policy" / "gather.json"
JOURNAL_MAP_EXPLORATION = (210, 600)  # Journal: Map Exploration card
MATERIALS = {"rolla": (58, 308), "ore": (132, 308), "sand": (206, 308), "essence": (280, 308)}  # Resource Hunt icons
HUNT_GO = (606, 364)
CONFIRM_OK = (490, 735)
HUNT_STAMINA_ROI = [40, 200, 200, 40]  # "175/300" on the Resource Hunt card
MAP_STAMINA_ROI = [540, 25, 180, 45]  # "171/300" top right on the world map
PLAY_ROI = (0, 130, 720, 870)  # x0, y0, x1, y1 where pickups can be tapped (HUD above, tracker/chat below)
MINIMAP_ROI = (520, 60, 720, 270)
MINIMAP_CENTRE = (616, 177)  # the character's spot on the minimap (sxs.minimap.CENTER)
WALK_STEP = 280  # px per walk tap toward a ring seen only on the minimap
LEFT_PANEL = (0, 700, 140, 1000)  # quest/resource tracker icons on the left: ring-shaped, never targets
LABEL_TO_PICKUP = (6, -33)  # from the cost label's centre to the pickup above it
COST = 5
STALE_ACTIONS = 6  # map taps without a stamina drop before the loop stops (stuck)
MAX_MINUTES = 15


def load_policy() -> dict:
    try:
        return json.loads(POLICY.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"priority": ["ore"], "keep_stamina": 70}


def read_stamina(det: StateDetector, roi=MAP_STAMINA_ROI, frame=None) -> Optional[int]:
    for t, _ in det.read_text(roi, frame):
        m = re.search(r"(\d+)\s*/\s*\d+", t)
        if m:
            return int(m.group(1))
    return None


def pickups_to_take(stamina: int, keep: int) -> int:
    """How many 5-stamina pickups fit above the reserve (R-107)."""
    return max(0, (stamina - keep) // COST)


def find_rings(frame: np.ndarray, colour: str = "track") -> list[tuple[int, int, int]]:
    """Circles (x, y, r) drawn round a target: the tracking ring is bright yellow pulsing to white; a special node's
    timer circle is green. Hough on a colour mask, radius 24-36 px."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    if colour == "green":
        mask = (h >= 40) & (h <= 85) & (s > 120) & (v > 150)
    else:
        mask = (v > 195) & (((h >= 18) & (h <= 40) & (s > 60)) | (s < 35))
    mask = mask.astype(np.uint8) * 255
    mask[:130, :140] = 0  # HUD portrait
    mask[1000:] = 0  # chat strip and bottom bar
    cs = cv2.HoughCircles(cv2.GaussianBlur(mask, (5, 5), 1), cv2.HOUGH_GRADIENT, dp=1, minDist=40, param1=100,
                          param2=22, minRadius=24 if colour != "green" else 14, maxRadius=36)
    if cs is None:
        return []
    out = []
    for x, y, r in np.round(cs[0]).astype(int):
        if LEFT_PANEL[0] <= x <= LEFT_PANEL[2] and LEFT_PANEL[1] <= y <= LEFT_PANEL[3]:
            continue
        if colour != "green" and not _ring_outline(hsv, x, y):
            continue  # a round glow (the teleport portal), not the drawn tracking ring
        out.append((int(x), int(y), int(r)))
    return out


def _ring_outline(hsv: np.ndarray, x: int, y: int) -> bool:
    """The tracking ring is a crisp circle: at some radius 20-38 px nearly the whole circumference is white (r ~26)
    or yellow (r ~28). The portal's glow and flowers never close a circle like that."""
    a = np.linspace(0, 2 * np.pi, 72, endpoint=False)
    for r in range(20, 40, 2):
        px = np.clip((x + r * np.cos(a)).astype(int), 0, hsv.shape[1] - 1)
        py = np.clip((y + r * np.sin(a)).astype(int), 0, hsv.shape[0] - 1)
        hh, ss, vv = hsv[py, px, 0], hsv[py, px, 1], hsv[py, px, 2]
        yellow = ((hh >= 15) & (hh <= 40) & (ss > 60) & (vv > 180)).mean()
        white = ((ss < 40) & (vv > 225)).mean()
        if yellow >= 0.6 or white >= 0.8:
            return True
    return False


def _in(xy, box) -> bool:
    return box[0] <= xy[0] <= box[2] and box[1] <= xy[1] <= box[3]


class Gatherer:
    def __init__(self, dev: Device, det: StateDetector):
        self.dev, self.det, self.nav = dev, det, nav.Navigator(dev, det)

    def _tap(self, xy, wait=2.0):
        self.dev.tap(*xy)
        time.sleep(wait)

    def open_hunt(self, material: str) -> Optional[int]:
        """Home > Journal > Map Exploration, select the material. Returns the stamina shown, None if the route
        failed (frame saved)."""
        self.nav.go_home()
        self._tap(nav.NAV_JOURNAL, 2.5)
        if self.det.detect().state != "journal":
            log.warning("Journal did not open; frame %s", save_unknown(self.dev, "gather_journal"))
            return None
        self._tap(JOURNAL_MAP_EXPLORATION, 3)
        if self.det.detect().state != "map_exploration":
            log.warning("Map Exploration did not open; frame %s", save_unknown(self.dev, "gather_hunt"))
            return None
        self._tap(MATERIALS[material], 1.5)
        return read_stamina(self.det, HUNT_STAMINA_ROI)

    def enter(self) -> bool:
        """Go, then OK on "Enter Verdantglade to explore?". True once on the world map."""
        self._tap(HUNT_GO, 3)
        if self.det.detect().state == "confirm_dialog":
            texts = " ".join(t for t, _ in self.det.read_text([60, 500, 600, 220]))
            if not re.search(r"explore", texts, re.I):
                log.warning("unexpected confirm %r; cancelling", texts)
                self._tap(nav.CONFIRM_CANCEL, 2)
                return False
            self._tap(CONFIRM_OK, 3)
        return self.det.wait_for({"world_map"}, 30, interval=1).state == "world_map"

    def next_action(self, frame) -> Optional[tuple[str, tuple[int, int]]]:
        """What to tap next on the map: ("special" | "pickup" | "ring" | "pan", point), or None."""
        for x, y, r in find_rings(frame, "green"):
            if _in((x, y), PLAY_ROI) and not _in((x, y), MINIMAP_ROI):
                # The timer circle sits at the node's upper right: tap the node itself.
                return "special", (x - 30, y + 30)
        labels = self.det.find_all("Gather.StaminaCost", frame)
        if labels:
            me = fogwalk.PLAY_AREA[0] + fogwalk.PLAY_AREA[2] // 2, fogwalk.PLAY_AREA[1] + fogwalk.PLAY_AREA[3] // 2
            x, y, w, h = min(labels, key=lambda b: (b[0] - me[0]) ** 2 + (b[1] - me[1]) ** 2)
            return "pickup", (x + w // 2 + LABEL_TO_PICKUP[0], y + h // 2 + LABEL_TO_PICKUP[1])
        rings = find_rings(frame)
        on_map = [(x, y) for x, y, _ in rings if _in((x, y), PLAY_ROI) and not _in((x, y), MINIMAP_ROI)
                  and 30 < x < 690 and 150 < y]
        if on_map:
            return "ring", on_map[0]
        edge = [(x, y) for x, y, _ in rings if not _in((x, y), MINIMAP_ROI)]
        if edge:
            return "pan", edge[0]  # clipped at the top edge: tapping pans the camera there
        mini = [(x, y) for x, y, _ in rings if _in((x, y), MINIMAP_ROI)]
        if mini:
            # Tapping the minimap opens the area map, so walk toward the ring instead: a few tiles from the
            # character in its direction (the camera is re-centred on the character first).
            dx, dy = mini[0][0] - MINIMAP_CENTRE[0], mini[0][1] - MINIMAP_CENTRE[1]
            n = max(1.0, (dx * dx + dy * dy) ** 0.5)
            cx, cy = fogwalk.PLAY_AREA[0] + fogwalk.PLAY_AREA[2] // 2, fogwalk.PLAY_AREA[1] + fogwalk.PLAY_AREA[3] // 2
            return "walk", (int(min(690, max(30, cx + WALK_STEP * dx / n))),
                            int(min(PLAY_ROI[3], max(PLAY_ROI[1] + 40, cy + WALK_STEP * dy / n))))
        return None

    def gather(self, budget: int, minutes: float = MAX_MINUTES) -> tuple[str, int]:
        """Take up to `budget` pickups on the current map. Returns (reason, pickups)."""
        deadline = time.monotonic() + minutes * 60
        taken = stale = self_taps = 0
        last = read_stamina(self.det)
        while taken < budget and time.monotonic() < deadline:
            d = self.det.detect()
            if d.state == "player_profile":  # tapped our own character: the pickup is under us or gone
                self_taps += 1
                self._tap((360, 1230), 1.5)
                if self_taps >= 3:
                    return "stuck_self", taken
                continue
            if d.state in ("reward_popup", "tap_to_continue"):
                self._tap(nav.REWARD_CLOSE, 1.5)
                continue
            if d.state == "battle_prep":
                # A pickup can be guarded; fights are explore's job (HP rules). Back out and stop.
                self._tap(nav.BACK_ARROW, 2)
                return "guarded", taken
            if d.state != "world_map":
                log.warning("left the map (%s); frame %s", d.state, save_unknown(self.dev, "gather_state"))
                return "unknown_screen", taken
            frame = self.dev.screenshot()
            action = self.next_action(frame)
            if action is None:
                fogwalk.centre_player(self.dev, self.det, frame) or self.dev.swipe(360, 400, 360, 700, 400)
                time.sleep(1.5)
                stale += 1
            else:
                kind, xy = action
                if kind == "walk" and fogwalk.centre_player(self.dev, self.det, frame):
                    continue  # plan again from the re-centred view
                log.info("%s at %s", kind, xy)
                self._tap(xy, 5 if kind in ("pickup", "ring", "special") else 2.5)
                stale += 1
            now = read_stamina(self.det)
            if now is not None and last is not None and now < last:
                taken += (last - now + COST - 1) // COST
                log.info("pickup taken: stamina %d -> %d (%d/%d)", last, now, taken, budget)
                stale = self_taps = 0
            elif action and action[0] == "special" and now == last:
                log.info("special node taken (no stamina cost)")
                stale = 0
            if now is not None:
                last = now
            if stale >= STALE_ACTIONS:
                log.warning("%d map taps without a pickup; frame %s", stale, save_unknown(self.dev, "gather_stuck"))
                return "stuck_progress", taken
        return ("budget_spent" if taken >= budget else "timeout"), taken

    def run(self, material: Optional[str] = None, check: bool = False) -> dict:
        policy = load_policy()
        material = material or policy["priority"][0]
        keep = int(policy.get("keep_stamina", 70))
        banner(log, "Gather", f"spend stamina above {keep} on {material} pickups (5 each), special nodes first",
               f"stamina at {keep}, {STALE_ACTIONS} taps without a pickup, an unknown screen, or {MAX_MINUTES} min")
        stamina = self.open_hunt(material)
        if stamina is None:
            return {"end": "unknown_screen"}
        budget = pickups_to_take(stamina, keep)
        log.info("stamina %d, keep %d: %d %s pickups", stamina, keep, budget, material)
        if check or budget == 0:
            self.nav.go_home()
            return {"end": "check" if check else "no_spare_stamina", "stamina": stamina, "budget": budget}
        if not self.enter():
            self.nav.go_home()
            return {"end": "unknown_screen", "stamina": stamina}
        reason, taken = self.gather(budget)
        log.info("gather: %s, %d pickups", reason, taken)
        self.nav.go_home()
        return {"end": reason, "material": material, "pickups": taken, "stamina_before": stamina}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--material", choices=sorted(MATERIALS))
    p.add_argument("--check", action="store_true", help="read stamina and the budget only")
    args = p.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    dev = Device()
    result = Gatherer(dev, StateDetector(dev)).run(args.material, args.check)
    print(json.dumps(result), flush=True)
    return 0 if result["end"] in ("budget_spent", "no_spare_stamina", "check", "timeout") else 1


if __name__ == "__main__":
    sys.exit(main())
