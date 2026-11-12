"""Gather Loop: one generic collector for every overworld material (R-106 to R-109; mae, 2026-11-04).

    python -m sxs gather                       # priority material from resource/policy/gather.json
    python -m sxs gather --material sand       # one-off override
    python -m sxs gather --check               # read stamina and the plan, tap nothing on the map
    python -m sxs gather --harvest [bellflower]  # already on the map with an item tracker: collect until full

Everything goes through `Gatherer.collect(target)`. A `Target` names the material, how its objects are found on
the ground (a template node, or the "bolt 5" stamina label under stamina pickups), how progress shows (stamina
drop or the left-panel tracker "a/b") and what one pickup costs. collect() paths toward the material's marker
(tracking ring on the map, edge ring, minimap ring), then taps the material objects themselves, never the tracker
icon or ring that floats over the character after a pick (mae: "click on the bellflowers themselves, like gathering
ore and sand and rolla"). Blue-aura objects (rarer, bonus ingredients) go first. Special nodes (a green timer circle,
e.g. a Grand Mine) are free and always taken.

Stamina route (mae, 2026-11-04): home > Journal > Map Exploration > Resource Hunt: pick the material, Go, OK
("Enter Verdantglade to explore?"). Each pickup costs 5 stamina; the bot keeps at least `keep_stamina` (70).
Stuck checks: progress within STALE_ACTIONS taps, at most 3 taps on ourselves, unknown screens get the back arrow
twice and then end the loop with the frame saved. No model calls.
"""

from __future__ import annotations

import json
import logging
import re
import time
from dataclasses import dataclass
from typing import Optional

import cv2

from ..actions.camera import centre_player
from ..actions.common import pass_through, start_fight
from ..core import ui
from ..core.device import save_unknown
from ..core.loop import Loop, banner
from ..core.nav import DEFEATED_OK, Navigator
from ..core.paths import POLICY
from ..vision.hud import read_stamina
from ..vision.ocr import read_fraction, read_line
from ..core.loop import progress as report_progress
from ..vision.pickups import LEFT_PANEL, blue_aura, find_rings
from ..vision.player import player_on_screen

log = logging.getLogger("sxs.loops.gather")

POLICY_FILE = POLICY / "gather.json"
JOURNAL_MAP_EXPLORATION = (210, 600)  # Journal: Map Exploration card
MATERIALS = {"rolla": (58, 308), "ore": (132, 308), "sand": (206, 308), "essence": (280, 308)}  # Resource Hunt icons
HUNT_GO = (606, 364)
RANK_BELLFLOWER_ICON = (360, 950)  # Rank Advancement: middle material-cost icon (Bellflower "a/20")
SOURCE_LINK = (590, 758)  # item card: the first Source row ("Verdantglade Flower Harvest >>")
HUNT_STAMINA_ROI = [40, 200, 200, 40]  # "175/300" on the Resource Hunt card
PLAY_ROI = (0, 130, 720, 870)  # x0, y0, x1, y1 where pickups can be tapped (HUD above, tracker/chat below)
MINIMAP_ROI = (520, 60, 720, 270)
TRACKER_COUNT_ROI = [50, 845, 180, 95]  # "2/20" beside the tracked item's icon, left of the map; sat at y~895 on 2026-11-11
MINIMAP_CENTRE = (616, 177)  # the character's spot on the minimap (sxs.vision.minimap.CENTER)
WALK_STEP = 280  # px per walk tap toward a ring seen only on the minimap
LABEL_TO_PICKUP = (6, -33)  # from the cost label's centre to the pickup above it
COST = 5
SELF_RADIUS = 70  # px round the character where nothing is tapped (the tracker icon/ring floats there after a pick)
AURA_MIN = 0.04  # share of light-blue pixels round an object that marks a rare (blue-aura) one
MAX_GUARD_FIGHTS = 3  # guard fights per run; more means something keeps attacking: stop and report
STALE_ACTIONS = 6  # map taps without progress before the loop stops (stuck)
MAX_MINUTES = 2  # mae, 2026-11-04: runs of 1-2 minutes; the next run carries on


@dataclass(frozen=True)
class Target:
    """A collectable material. node: template node of the object on the ground (None: find it by its "bolt 5"
    stamina label). progress: "stamina" (each pickup costs `cost`) or "tracker" (left-panel a/b count rises)."""
    name: str
    node: Optional[str] = None
    progress: str = "stamina"
    cost: int = COST


TARGETS = {
    "ore": Target("ore"), "sand": Target("sand"), "essence": Target("essence"), "rolla": Target("rolla"),
    # Bellflowers (Rank Advancement): free to pick, counted on the item tracker (2026-11-04).
    "bellflower": Target("bellflower", node="Gather.Bellflower", progress="tracker", cost=0),
}


def load_policy() -> dict:
    try:
        return json.loads(POLICY_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"priority": ["ore"], "keep_stamina": 70}


def pickups_to_take(stamina: int, keep: int) -> int:
    """How many 5-stamina pickups fit above the reserve (R-107)."""
    return max(0, (stamina - keep) // COST)


class Gatherer:
    def __init__(self, dev, det):
        self.dev, self.det, self.nav = dev, det, Navigator(dev, det)
        self._tap = self.nav.tap

    # ---- stamina route: Journal > Map Exploration > Resource Hunt ----

    def open_hunt(self, material: str) -> Optional[int]:
        """Home > Journal > Map Exploration, select the material. Returns the stamina shown, None if the route
        failed (frame saved)."""
        self.nav.go_home()
        self._tap(ui.NAV_JOURNAL, 2.5)
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
        return self.enter_confirm()

    def enter_bellflower_field(self) -> bool:
        """Home > Character > rank badge > Bellflower cost icon > Source "Verdantglade Flower Harvest" > OK.
        Puts a Bellflower tracker (a/20) on the map with a ring toward the field (2026-11-04). True on the map."""
        self.nav.go_home()
        self._tap(ui.NAV_CHARACTER, 3)
        self._tap(ui.RANK_BADGE, 2.5)
        if self.det.detect().state != "rank_advancement":
            log.warning("Rank Advancement did not open; frame %s", save_unknown(self.dev, "collect_rank"))
            return False
        self._tap(RANK_BELLFLOWER_ICON, 2.5)
        texts = read_line(self.det, [80, 700, 560, 100])
        if not re.search(r"Flower Harvest", texts, re.I):
            log.warning("no Flower Harvest source (%r); frame %s", texts, save_unknown(self.dev, "collect_source"))
            return False
        self._tap(SOURCE_LINK, 3)
        return self.enter_confirm()

    def enter_confirm(self) -> bool:
        """OK on "Enter Verdantglade to explore?" (anything else: Cancel). True once on the world map."""
        if self.det.detect().state == "confirm_dialog":
            texts = read_line(self.det, [60, 500, 600, 220])
            if not re.search(r"explore", texts, re.I):
                log.warning("unexpected confirm %r; cancelling", texts)
                self._tap(ui.CONFIRM_CANCEL, 2)
                return False
            self._tap(ui.CONFIRM_OK, 3)
        return self.det.wait_for({"world_map"}, 30, interval=1).state == "world_map"

    # ---- seeing ----

    def _player(self, frame) -> Optional[tuple[int, int]]:
        """The character's body: just above the "gromb2" name label. Searched down to the chat strip, like Fog
        Walk: after an area-map walk the character can stand low on screen, and missing it there let the ring over
        the character look like a ring to tap (R-124 says never)."""
        return player_on_screen(self.det, frame)

    def tracked_count(self) -> Optional[tuple[int, int]]:
        """The item tracker on the left ("2/20" next to the tracked item's icon), e.g. Bellflowers."""
        return read_fraction(self.det, TRACKER_COUNT_ROI, whole_line=True)

    def ground_items(self, target: Target, frame, me) -> list[tuple[int, int]]:
        """The material objects themselves on the play area, best first: blue-aura ones (rarer, bonus ingredients)
        before plain ones, then nearest. Never the tracker icon/ring over the character, the side panels or the
        minimap."""
        if target.node:
            hits = [(x + w // 2, y + h // 2) for x, y, w, h in self.det.find_all(target.node, frame)]
        else:  # stamina pickups: the "bolt 5" label sits under the object
            hits = [(x + w // 2 + LABEL_TO_PICKUP[0], y + h // 2 + LABEL_TO_PICKUP[1])
                    for x, y, w, h in self.det.find_all("Gather.StaminaCost", frame)]
        hits = [h for h in hits if h[0] > 90 and PLAY_ROI[1] < h[1] < PLAY_ROI[3] and not ui.inside(h, MINIMAP_ROI)
                and not ui.inside(h, LEFT_PANEL) and not ui.near(h, me, SELF_RADIUS)]
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        return sorted(hits, key=lambda h: (blue_aura(hsv, h) <= AURA_MIN,
                                           (h[0] - me[0]) ** 2 + (h[1] - me[1]) ** 2))

    def plan(self, target: Target, frame) -> Optional[tuple[str, tuple[int, int]]]:
        """Next tap: special node > material object on the ground > tracking ring on the map (not over us) >
        edge ring (pans the camera) > minimap ring (walk toward it). None when nothing is visible."""
        me = self._player(frame) or (360, 600)
        for x, y, r in find_rings(frame, "green"):
            if ui.inside((x, y), PLAY_ROI) and not ui.inside((x, y), MINIMAP_ROI):
                return "special", (x - 30, y + 30)  # the timer circle sits at the node's upper right
        items = self.ground_items(target, frame, me)
        if items:
            return "item", items[0]
        rings = [(x, y) for x, y, _ in find_rings(frame) if not ui.inside((x, y), MINIMAP_ROI)]
        far = [xy for xy in rings if not ui.near(xy, me, SELF_RADIUS + 20)]
        on_map = [xy for xy in far if ui.inside(xy, PLAY_ROI) and 30 < xy[0] < 690 and xy[1] > 150]
        if on_map:
            return "ring", on_map[0]
        if far:
            return "pan", far[0]  # clipped at a screen edge: tapping pans the camera there
        mini = [(x, y) for x, y, _ in find_rings(frame) if ui.inside((x, y), MINIMAP_ROI)]
        if mini:
            # Tapping the minimap opens the area map, so walk a few tiles toward the ring instead.
            dx, dy = mini[0][0] - MINIMAP_CENTRE[0], mini[0][1] - MINIMAP_CENTRE[1]
            n = max(1.0, (dx * dx + dy * dy) ** 0.5)
            return "walk", (int(min(690, max(30, me[0] + WALK_STEP * dx / n))),
                            int(min(PLAY_ROI[3], max(PLAY_ROI[1] + 40, me[1] + WALK_STEP * dy / n))))
        return None

    def progress(self, target: Target) -> Optional[int]:
        """The number that rises (tracker count) or falls (stamina) when one is picked."""
        if target.progress == "tracker":
            c = self.tracked_count()
            return c[0] if c else None
        return read_stamina(self.det)

    # ---- the one collector ----

    def collect(self, target: Target, budget: Optional[int] = None, keep: int = 70,
                minutes: float = MAX_MINUTES) -> dict:
        """Collect `target` on the current world map until done: `budget` pickups (stamina targets) or the
        tracker reading a/b with a >= b (tracker targets). Stops early with a reason: stamina_reserve,
        stuck_progress, stuck_self, guarded (more than 3 guard fights), low_hp, defeated, unknown_screen, no_tracker, timeout."""
        goal = (f"pick {target.name} until its tracker is full" if target.progress == "tracker"
                else f"take {budget} {target.name} pickups ({target.cost} stamina each)")
        banner(log, f"Collect {target.name}", goal + ", blue-aura ones first, special nodes always",
               f"done, stamina at {keep}, {STALE_ACTIONS} taps without progress, an unknown screen, or {minutes:g} min")
        out = {"target": target.name, "pickups": 0}
        deadline = time.monotonic() + minutes * 60
        taken = stale = self_taps = unknown = fights = 0
        if target.progress == "tracker":
            c = self.tracked_count()
            log.info("tracker: %s", c)
            if c is None:
                return {**out, "end": "no_tracker"}
            if c[0] >= c[1]:
                return {**out, "end": "full", "count": list(c)}
        last = self.progress(target)
        while time.monotonic() < deadline:
            out["pickups"] = taken
            if target.progress == "stamina" and budget is not None and taken >= budget:
                return {**out, "end": "budget_spent"}
            d = self.det.detect()
            if d.state == "player_profile":  # tapped ourselves: the object under us is gone
                self_taps += 1
                self._tap(ui.BELOW_POPUP, 1.5)
                if self_taps >= 3:
                    return {**out, "end": "stuck_self"}
                continue
            if d.state in ("reward_popup", "tap_to_continue"):
                self._tap(ui.REWARD_CLOSE, 1.5)
                continue
            if d.state == "dialogue":  # e.g. Akane at 20/20 Bellflowers: "Go for that rank advancement!"
                self._tap(ui.DIALOGUE_NEXT, 1.5)
                continue
            if d.state == "battle_prep":
                # A guard stands on the pickup (R-073; mae, 2026-11-09): fight it at 70%+ HP, then carry on gathering.
                fights += 1
                if fights > MAX_GUARD_FIGHTS:
                    self._tap(ui.BACK_ARROW, 2)
                    return {**out, "end": "guarded", "fights": fights - 1}
                if not start_fight(self.dev, self.det):
                    return {**out, "end": "low_hp", "fights": fights - 1}
                log.info("guard fight %d started", fights)
                stale = 0
                continue
            if d.state == "defeated":  # lost to a guard: OK goes home (R-031)
                self._tap(DEFEATED_OK, 3)
                return {**out, "end": "defeated", "fights": fights}
            if pass_through(self.dev, d):  # the guard fight, loading
                continue
            if d.state != "world_map":
                unknown += 1
                log.warning("left the map (%s); frame %s; back arrow", d.state,
                            save_unknown(self.dev, f"collect_{target.name}"))
                if unknown > 2:
                    return {**out, "end": "unknown_screen", "state": d.state}
                self._tap(ui.BACK_ARROW, 2)
                continue
            unknown = 0
            if target.cost:
                stamina = read_stamina(self.det)
                if stamina is not None and stamina < keep + target.cost:
                    return {**out, "end": "stamina_reserve", "stamina": stamina}
            frame = self.dev.screenshot()
            action = self.plan(target, frame)
            if action is None:
                centre_player(self.dev, self.det, frame) or self.dev.swipe(360, 400, 360, 700, 400)
                time.sleep(1.5)
                stale += 1
            elif action[0] == "walk" and centre_player(self.dev, self.det, frame):
                continue  # plan again from the re-centred view
            else:
                kind, xy = action
                log.info("%s at %s", kind, xy)
                self._tap(xy, 5 if kind in ("item", "ring", "special") else 2.5)
                stale += 1
            now = self.progress(target)
            if now is not None and last is not None:
                if target.progress == "tracker":
                    gained = now - last
                else:
                    gained = (last - now + target.cost - 1) // target.cost if now < last else 0
                if gained > 0:
                    taken += gained
                    log.info("%s picked: %s -> %s (%d so far)", target.name, last, now, taken)
                    from ..core import preroll

                    preroll.save("pickup", target.name, "gather")  # the approach and the pick (core/preroll.py)
                    stale = self_taps = 0
                elif action and action[0] == "special":
                    log.info("special node taken (free)")
                    stale = 0
            if now is not None:
                last = now
            report_progress((target.name, taken, now))
            if target.progress == "tracker":
                c = self.tracked_count()
                if c and c[0] >= c[1]:
                    return {**out, "pickups": taken, "end": "full", "count": list(c)}
            if stale >= STALE_ACTIONS:
                log.warning("%d taps without progress; frame %s", stale,
                            save_unknown(self.dev, f"collect_{target.name}_stuck"))
                return {**out, "pickups": taken, "end": "stuck_progress"}
        return {**out, "pickups": taken, "end": "timeout"}

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
        result = self.collect(TARGETS[material], budget=budget, keep=keep)
        log.info("gather: %s", result)
        self.nav.go_home()
        return {**result, "material": material, "stamina_before": stamina}


def _args(p) -> None:
    p.add_argument("--material", choices=sorted(MATERIALS))
    p.add_argument("--check", action="store_true", help="read stamina and the budget only")
    p.add_argument("--harvest", nargs="?", const="bellflower", choices=sorted(TARGETS),
                   help="already on the map with an item tracker (default bellflower): collect until it's full")
    p.add_argument("--enter", action="store_true",
                   help="with --harvest bellflower: first go Home > Rank Advancement > Bellflower source > OK")


def _run(ctx, opts):
    g = Gatherer(ctx.dev, ctx.det)
    if opts.harvest:
        if opts.enter and opts.harvest == "bellflower" and not g.enter_bellflower_field():
            g.nav.go_home()
            return {"end": "unknown_screen"}
        return g.collect(TARGETS[opts.harvest], keep=int(load_policy().get("keep_stamina", 70)))
    return g.run(opts.material, opts.check)


OK = {"budget_spent", "no_spare_stamina", "check", "timeout", "full"}
LOOP = Loop("gather", "Gather", "spend stamina above the reserve on the priority material", _run, _args, ok=OK)
