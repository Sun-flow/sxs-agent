"""Clear Zone: bring one unexplored zone to 100%, one named objective at a time. No model calls.

    python -m sxs clear [--area NAME] [--minutes 20]

Replaces the Fog Walk (scrapped by mae, 2026-11-10: docs/fogwalk-postmortem.md). Design: docs/step6-clear-zone.md;
flowchart: docs/loops/clear.md. The rules in short:

1. Every walk is a *leg* toward one objective the log can name. Sources, best first: the zone's own Explore quest
   ring (R-142), a known object on screen (R-131), any dot or structure the minimap shows, the nearest
   thing in the zone on the big map that counts for exploration (R-068, R-148), and last a frontier: the nearest fog
   in the zone touching walkable ground we can reach, one long big-map walk.
2. Progress is the zone's % or an object cleared (a fight, a pickup, a card acted on, a wheel spin, a gate opened),
   never "a new tile".
3. No objective left: stop `no_objective`. STALL_LEGS legs in a row without progress: stop `no_progress`.
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass, field
from typing import Optional

from ..actions import goto, heal, mapnav, rewards
from ..actions.camera import centre_player
from ..actions.unstick import attack_guard
from ..actions.common import REWARD_STATES, TOWER_STATES, pass_through
from ..actions.watchdog import UnknownScreens
from ..core import ui
from ..core.device import save_unknown
from ..core.interrupts import resume_with
from ..core.loop import Loop, banner, progress
from ..core.marks import server_day
from ..core.nav import Navigator
from ..policy.decide import Context, Decider
from ..policy.zones import Tree
from ..vision import area_map, collectibles, minimap
from ..vision.hp import PREP_HP_BAR
from ..vision.hud import read_power
from ..vision.player import player_on_screen
from . import tower
from .explore import REPEAT_LIMIT, hud_hp

log = logging.getLogger("sxs.loops.clear")

STALL_LEGS = 4  # legs in a row with no % and no object cleared before the run stops (no_progress)
BIG_MAP_LEGS = 12  # big-map legs per run (each ~20-30 s)
NO_PCT_DONE_FROM = 90  # % a zone must have reached before its label showing no % line counts toward explored
FRONTIER_LEGS = 6  # frontier legs per run: fog matters only when it hides objects (3 ran short in Grotto Peninsula)
FOG_REVEALED = 0.05  # drop in the fog share round the frontier spot, before the walk to after, that counts as revealed
RING_MISSES = 2  # ring legs in a row without a gain before the ring waits for another source's gain
SPOT_FAILS = 2  # legs at one map spot without a gain before that spot is skipped for the run
SPOT_TILES = 2  # map tiles within which two spots are the same spot
GATE_LIMIT = 3  # Gate of Power cards in one run before the zone counts as walled off
REWARD_TAPS_MAX = 3  # tracker gift taps per run
SETTLE_S = 240  # longest a leg's aftermath may take (a mini-dungeon floor fights several rounds)
MINIMAP_REACH = 10  # path tiles: any dot or structure the minimap shows is a target (mae, 2026-11-11: 7-10 tiles)
MINIMAP_HOPS = 3  # walk taps toward a minimap target that is off screen before the leg gives up on it
TAP_AREA = (20, 320, 700, 920)  # x0, y0, x1, y1: on-screen taps land here (under the minimap, above the tracker)
MAP_PCT_EVERY = 3  # legs between area-map % reads in a zone with no tracker quest (each read ~6 s)
PUZZLE_LEGS = 3  # minimap legs at gold squares that open nothing and move no % before the zone counts as a puzzle
RETAPS = 2  # extra taps on a minimap object that is still there after the leg's tap (R-155)
GAIN_EVENTS = {"fight", "pickup", "acted", "wheel", "gate_open", "revealed", "cleared"}
ZONE_PICK_PX = 900  # big-map search radius for this zone's objects (the label check keeps it to the zone)


@dataclass
class Leg:
    n: int
    source: str  # ring, known, minimap, big_map, frontier
    what: str
    xy: Optional[tuple[int, int]] = None  # map coordinates of the objective when known
    events: list = field(default_factory=list)
    result: str = ""

    def __str__(self) -> str:
        return f"{self.source}: {self.what}" + (f" at map {self.xy}" if self.xy else "")


def _xy(det) -> Optional[tuple[int, int]]:
    return goto.coords(det)


def on_screen(me, mm, tile) -> Optional[tuple[int, int]]:
    """Screen point of a minimap tile, from our character's screen point; None when it is off screen or on the HUD."""
    pr, pc = mm.centre
    x = me[0] + (tile[1] - pc) * minimap.SCREEN_TILE
    y = me[1] + (tile[0] - pr) * minimap.SCREEN_TILE
    x0, y0, x1, y1 = TAP_AREA
    if not (x0 <= x <= x1 and y0 <= y <= y1):
        return None
    p = (int(x), int(y))
    return p if mapnav.off_hud(p) == p else None


def near(a, b, tiles: int = SPOT_TILES) -> bool:
    return bool(a and b) and max(abs(a[0] - b[0]), abs(a[1] - b[1])) <= tiles


def save_dialogue(dev, texts: str, zone: Optional[str]):
    """Save a story-choice dialogue to docs/screens/dialogs/choice_<zone>_<first words of the choices>.png (mae, 2026-11-11)."""
    import cv2
    from ..core.paths import SCREENS
    from ..core.ui import PLAYER_NAME
    # Our own name shows on the dialogue (live 2026-11-11, run 25): keep it out of the file name (PII rule).
    texts = re.sub(re.escape(PLAYER_NAME), " ", texts or "", flags=re.I)
    words = re.sub(r"[^a-z0-9]+", "_", f"{zone or ''} {texts}".lower()).strip("_")[:60] or "scene"
    out = SCREENS / "dialogs"
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"choice_{words}.png"
    if path.exists():
        path = out / f"choice_{words}_{time.strftime('%Y%m%d-%H%M%S')}.png"
    cv2.imwrite(str(path), dev.screenshot())
    return path


class Clearer:
    def __init__(self, dev, det, area: Optional[str] = None, allowed=()):
        self.dev, self.det = dev, det
        self.tree = Tree.load()
        self.home = self.tree.key(area) if area and self.tree.key(area) else area
        self.allowed = set(allowed or ())
        self.decider, self.ctx = Decider(det), Context(goal="explore")
        self.unknown = UnknownScreens(in_a_row=5)
        self.legs: list[Leg] = []
        self.leg: Optional[Leg] = None
        self.pct: Optional[int] = None  # the zone's % as last read (tracker or area map)
        self.pct_start: Optional[int] = None
        self.own_quest = False  # the tracker showed this zone's own Explore quest this run
        self.no_gain = 0
        self.ring_misses = 0
        self.big_map_used = self.frontier_used = 0
        self.frontier_away: list[tuple[int, int]] = []  # area-map directions of frontier legs that revealed nothing
        self.big_map_off = False  # big-map objects keep leading back to a failed spot: object source off
        self.fails: list[tuple[tuple[int, int], int]] = []  # [(map spot, legs there without a gain)]
        self.arrivals: list[tuple[str, tuple[int, int]]] = []  # (source, where a big-map leg ended)
        self.gates = 0
        self.power: Optional[float] = None  # K, read from the HUD when the run starts
        self.no_pct_reads = 0  # area-map reads in a row of our label with no % line under it
        self.map_read_leg = 0  # leg count at the last map_pct
        self.inert_gold = 0  # minimap legs at gold squares that opened no card or fight and moved no % (puzzle tiles)
        self.repeats, self.last_card = 0, None
        self.heal_tries = 0
        self.reward_taps = 0
        self.wheel_spun = False
        self.strays = 0
        self.seen_names: dict = {}
        self.tapped = None  # (frame, screen point, kind) of the last tap at an object, for the R-131 crop store
        self.saved_fight = False

    # ---------------------------------------------------------------- spots and readouts
    def failed_spot(self, xy) -> bool:
        return any(near(xy, s) and n >= SPOT_FAILS for s, n in self.fails)

    def fail(self, xy) -> None:
        if not xy:
            return
        for i, (s, n) in enumerate(self.fails):
            if near(xy, s):
                self.fails[i] = (s, n + 1)
                if n + 1 == SPOT_FAILS:
                    log.info("map spot %s: %d legs without a gain; skipped for the rest of this run", s, n + 1)
                return
        self.fails.append((tuple(xy), 1))

    def skip_spot(self, xy) -> None:
        """A spot whose card can only be dismissed (or a gate we can't open): no more legs there this run."""
        if xy:
            self.fails.append((tuple(xy), SPOT_FAILS))

    def event(self, name: str) -> None:
        if self.leg is not None:
            self.leg.events.append(name)
        progress(("event", len(self.legs), name))

    def map_pct(self) -> None:
        """No tracker quest for this zone (a side zone): read its label's "Exploration: N%" on the area map at the
        survey zoom (live 2026-11-11, run 20: the % stayed None all run, so it could never show progress or 100%).
        A label read three times running with room for a % line and none under it means the zone is explored, once
        it has read NO_PCT_DONE_FROM% or more."""
        from .roam import merge_readings, read_areas, same  # roam imports this module
        if not self.home or not goto.open_area_map(self.dev, self.det):
            return
        goto.survey_zoom(self.dev)
        time.sleep(1)
        areas = merge_readings([(read_areas(self.det, self.dev.screenshot()), (0, 0))])
        ui.tap(self.dev, ui.BACK_ARROW, 2)
        if self.det.detect().state == "area_map":
            ui.tap(self.dev, ui.BACK_ARROW, 2)
        mine = [a for a in areas if same(a.name, self.home) or mapnav.label_is(a.name, self.home)]
        if not mine:
            log.info("area map: %s's label not read", self.home)
            return
        a = next((m for m in mine if m.pct is not None), mine[0])
        if a.pct is not None:
            self.no_pct_reads = 0
            if self.pct is None or a.pct > self.pct:
                self.pct = a.pct
            log.info("area map: %s at %d%%", self.home, a.pct)
        elif not a.unsure and (self.pct or 0) < NO_PCT_DONE_FROM:
            # A label that hasn't shown its % yet (run 22: Grotto Peninsula at 0% read "no % line" twice, then 63%):
            # a missing line means explored only for a zone already near the end.
            log.info("area map: %s shows no %% line, not counted (last %s%%)", self.home, self.pct)
        elif not a.unsure:
            self.no_pct_reads += 1
            log.info("area map: %s shows no %% line (%d of 3 reads)", self.home, self.no_pct_reads)
            if self.no_pct_reads >= 3:  # roam needs 3 too (2 once flipped Troll Lair)
                self.pct = 100
        progress(("pct", self.pct))

    def read_pct(self) -> Optional[int]:
        """The tracker's "Explore <zone> N/100" when it is this zone's quest; else the last area-map reading."""
        if not self.home:
            return self.pct
        n = mapnav.quest_counter(self.det, self.home)
        if n is not None:
            self.own_quest = True
            self.pct = n if self.pct is None else max(self.pct, n)
        return self.pct

    def summary(self, status: str) -> str:
        by = {}
        for leg in self.legs:
            by.setdefault(leg.source, [0, 0])
            by[leg.source][0] += 1
            by[leg.source][1] += leg.result == "gain"
        log.info("[Result] %s: %s; %s%% -> %s%%; %d legs (%s)", self.home, status, self.pct_start, self.pct,
                 len(self.legs), ", ".join(f"{k} {g}/{n} gained" for k, (n, g) in by.items()) or "none")
        return status

    # ---------------------------------------------------------------- zone checks
    def in_home(self, name: str) -> bool:
        if not self.home or not name:
            return True
        if goto.same_area(name, self.home) or goto.close_name(name, self.home) or mapnav.label_is(name, self.home):
            return True
        h, z = goto.squeeze(self.home), goto.squeeze(name)
        if len(h) >= 6 and h[:-1] in z:  # labels OCR joined ("Wildbloom CoastHidden Camp")
            return True
        hs, cs = (re.sub(r"[^a-z]", "", t) for t in (h, z))
        if hs.startswith(cs) and len(hs) - len(cs) == 1 and hs[-1] == "i":  # "Monolith Ruins I ." for II
            return True
        if any(goto.same_area(name, a) for a in self.allowed):
            return True
        key = self.tree.key(name)
        if key:
            return goto.same_area(key, self.home)
        if name not in self.seen_names:  # R-140: an unknown name is checked once on the big map
            self.seen_names[name] = mapnav.zone_by_map(self.dev, self.det, self.home) or name
        return goto.same_area(self.seen_names[name], self.home)

    def check_zone(self) -> Optional[str]:
        """Between legs: still in our zone? Two reads elsewhere in a row walk back; failing that, stop."""
        name = goto.area_name_here(self.det)
        if self.in_home(name):
            self.strays = 0
            return None
        self.strays += 1
        if self.strays < 2:
            return None
        log.info("left %s for %s: walking back", self.home, name)
        self.strays = 0
        if self.leg is not None:
            self.fail(self.leg.xy)  # the objective that led out is not this zone's
        back = goto.go_to(self.dev, self.det, self.home)
        if back == "no_move":
            mapnav.quest_step(self.dev, self.det, True)  # an enclosure (Auroradrasil): the quest pointer leads out
            back = goto.go_to(self.dev, self.det, self.home)
        return None if back == "arrived" else "not_in_zone"

    # ---------------------------------------------------------------- objective sources
    def start_leg(self, source: str, what: str, xy=None) -> Leg:
        leg = Leg(len(self.legs) + 1, source, what, xy)
        self.legs.append(leg)
        self.leg = leg
        log.info("[leg %d] goal: %s | zone %s at %s%%", leg.n, leg, self.home, self.pct)
        progress(("leg", leg.n, source))
        return leg

    def try_ring(self) -> Optional[Leg]:
        if not self.home or self.ring_misses >= RING_MISSES:
            return None
        n = mapnav.quest_counter(self.det, self.home)
        if n is None:
            return None
        here = _xy(self.det)
        if not mapnav.quest_step(self.dev, self.det, True):  # taps the target under the ring when there is one
            return None
        return self.start_leg("ring", f"Explore {self.home} {n}/100 (target under the gold ring)", here)

    def try_guard(self, frame, xy) -> Optional[Leg]:
        """A monster group in gold corner brackets, or a monster under a red skull marker, guards what lies behind it
        (R-139; live 2026-11-11, run 21: Lakeside Camp's chest and pickups sat behind a bracketed boss and its
        guards, and the run ended no_objective). Fight it first: it is the zone's next objective."""
        if self.failed_spot(xy) or not attack_guard(self.dev, self.det, frame):
            return None
        return self.start_leg("guard", "guard group in brackets (or under a skull marker)", xy)

    def try_known(self, frame, xy, me) -> Optional[Leg]:
        for name, kind, point, score in collectibles.find(frame, explored=False, area=self.home or ""):
            spot = mapnav.to_world(xy, me, point)
            if self.failed_spot(spot):
                continue
            leg = self.start_leg("known", f"{kind} {name!r} ({score:.2f})", spot)
            self.tapped = (frame, point, kind)
            self.leg_tap(point)
            return leg
        return None

    def try_minimap(self, frame, xy, me) -> Optional[Leg]:
        """A dot or structure anywhere on the minimap (mae, 2026-11-11: if it shows there, it is close enough). The
        leg walks toward it along the minimap path until it is on screen, then taps it."""
        if xy is None or me is None:
            return None
        mm = minimap.read(frame, False)
        pr, pc = mm.centre
        ring = {(pr + dr, pc + dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1)}  # our own marker reads as a dot
        n = len(mm.grid)
        skip = ring | {(r, c) for r in range(n) for c in range(n)
                       if self.failed_spot(minimap.world_tile(mm, (r, c), xy))}
        path = minimap.path_to_nearest(mm, goals=("item", "monster", "building"), skip=skip)
        if len(path) < 2 or len(path) - 1 > MINIMAP_REACH:
            return None
        goal = mm.grid[path[-1][0]][path[-1][1]]
        spot = minimap.world_tile(mm, path[-1], xy)
        leg = self.start_leg("minimap", f"{goal} {len(path) - 1} tiles away", spot)
        for hop in range(MINIMAP_HOPS + 1):
            point = on_screen(me, mm, path[-1])
            if point is not None:
                self.tapped = (frame, point, goal)
                self.leg_tap(point)
                self.finish_object(leg, spot, goal)
                return leg
            if hop == MINIMAP_HOPS:
                break
            # Off screen: walk to the farthest tile of the path that is on screen, then look again.
            step = next((on_screen(me, mm, t) for t in reversed(path[1:-1]) if on_screen(me, mm, t)), None)
            if step is None:
                break
            log.info("[leg %d] %s off screen: walking toward it (%s)", leg.n, goal, step)
            self.dev.tap(*mapnav.off_me(self.det, step, frame))
            self.wait_still()
            if self.det.detect().state != "world_map":
                return leg  # a fight or a card on the way: the leg's aftermath handles it
            frame = self.dev.screenshot()
            if centre_player(self.dev, self.det, frame):
                frame = self.dev.screenshot()
            xy, me = _xy(self.det), player_on_screen(self.det, frame)
            if xy is None or me is None:
                break
            mm = minimap.read(frame, False)
            pr, pc = mm.centre
            gr, gc = pr - (spot[1] - xy[1]), pc + (spot[0] - xy[0])
            path = minimap.path_to_nearest(mm, goals=(mm.grid[gr][gc],), skip=ring) if (
                0 <= gr < len(mm.grid) and 0 <= gc < len(mm.grid)) else []
            if len(path) < 2 or path[-1] != (gr, gc):
                path = [mm.centre, (gr, gc)]  # aim straight at the spot; the game paths there itself
        log.info("[leg %d] couldn't bring the %s on screen", leg.n, goal)
        leg.events.append("no_move")
        return leg

    def finish_object(self, leg: Leg, spot, goal: str) -> None:
        """Live 2026-11-11 (run 15, IX): a tap that walked us next to a pickup didn't collect it; pickups start only
        from a tap on the sprite itself once beside it (R-155). While we're still on the map and the minimap still
        shows the object at its spot, tap it again where it now is (up to RETAPS times). When it's gone from the
        minimap, it was taken: that's the object cleared."""
        for i in range(RETAPS + 1):
            self.wait_still()
            if self.det.detect().state != "world_map" or leg.events:
                return  # a fight, a card or a reward popup: the aftermath handles it
            frame = self.dev.screenshot()
            if centre_player(self.dev, self.det, frame):
                frame = self.dev.screenshot()
            xy, me = _xy(self.det), player_on_screen(self.det, frame)
            if xy is None or me is None:
                return
            mm = minimap.read(frame, False)
            pr, pc = mm.centre
            here = [(pr - (spot[1] - xy[1]) + dr, pc + (spot[0] - xy[0]) + dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1)]
            left = [t for t in here if 0 <= t[0] < len(mm.grid) and 0 <= t[1] < len(mm.grid)
                    and mm.grid[t[0]][t[1]] == goal]
            if not left:
                log.info("[leg %d] the %s at map %s is gone from the minimap: taken", leg.n, goal, spot)
                leg.events.append("cleared")
                return
            if i == RETAPS:
                break
            t = min(left, key=lambda t: abs(t[0] - (pr - (spot[1] - xy[1]))) + abs(t[1] - (pc + (spot[0] - xy[0]))))
            point = on_screen(me, mm, t)
            if point is None:
                return
            log.info("[leg %d] the %s is still there: tapping it again at %s", leg.n, goal, point)
            self.dev.tap(*mapnav.off_me(self.det, point, frame))
        log.info("[leg %d] the %s at map %s is still on the minimap after %d taps", leg.n, goal, spot, RETAPS + 1)

    def wait_still(self, most: float = 12) -> None:
        """Wait until the map coordinates stop changing (a walk ended) or the screen leaves the map."""
        last, until = _xy(self.det), time.monotonic() + most
        while time.monotonic() < until:
            time.sleep(1.5)
            now = _xy(self.det)
            if now is None or now == last:
                return
            last = now

    def leg_tap(self, point) -> None:
        how = mapnav.tap_object(self.dev, self.det, point, wait=3)
        log.info("[leg %d] tap at %s: %s", self.leg.n, point, how)
        if how == "nothing":
            self.leg.events.append("no_move")

    def picker(self, choice: dict):
        """Big-map picker for one opening: reads the zone's %, then picks the nearest object in our zone, else (when
        allowed) the frontier. Writes what it chose into `choice`."""
        from .roam import read_areas, same  # roam imports this module

        def pick(frame):
            areas = read_areas(self.det, frame)
            mine = [a for a in areas if self.home and (same(a.name, self.home) or mapnav.label_is(a.name, self.home))]
            if mine and not self.tree.key(self.home) and len(mine[0].name) > len(self.home):
                # A zone given by its first words ("Lakeside"): go by the full name the map shows ("Lakeside Camp").
                log.info("zone %r is %r on the area map", self.home, mine[0].name)
                self.home = mine[0].name
            pct = next((a.pct for a in mine if a.pct is not None), None)
            if pct is not None and not self.own_quest:
                choice["pct"] = pct
            labels = {a.name: a.point for a in areas}
            if not self.big_map_off and self.big_map_used < BIG_MAP_LEGS:
                hit = area_map.nearest(frame, ("statue", "item", "monster", "building"), max_px=ZONE_PICK_PX,
                                       labels=labels, home=self.home, is_home=mapnav.label_is)
                if hit:
                    choice.update(kind="big_map", what=f"{hit[0]} on the big map")
                    return hit[1]
            if mine and self.frontier_used < FRONTIER_LEGS:
                others = [a.point for a in areas if a not in mine]
                me = next((p for k, p in area_map.objects(frame) if k == "player"), None)
                hit = area_map.frontier(frame, mine[0].point, others, me=me, away=self.frontier_away)
                if hit:
                    sx, sy = me or mine[0].point
                    choice.update(kind="frontier", what=f"nearest fog in the zone beside reachable ground "
                                  f"(fog {hit[1]:.0%} round it)", dir=(hit[0][0] - sx, hit[0][1] - sy),
                                  fog=hit[1])
                    return hit[0]
            return None
        return pick

    def try_big_map(self) -> Optional[Leg]:
        objects_left = not self.big_map_off and self.big_map_used < BIG_MAP_LEGS
        if not objects_left and self.frontier_used >= FRONTIER_LEGS:
            return None
        choice: dict = {}
        why = goto.go_to(self.dev, self.det, self.picker(choice))
        if "pct" in choice and (self.pct is None or choice["pct"] > self.pct):
            self.pct = choice["pct"]
        if "kind" not in choice:
            log.info("big map: nothing left to aim for in %s (%s)", self.home, why)
            return None
        kind = choice["kind"]
        if kind == "frontier":
            self.frontier_used += 1
        else:
            self.big_map_used += 1
        here = _xy(self.det)
        leg = self.start_leg(kind, choice["what"], here)
        log.info("[leg %d] big-map walk: %s, now at %s", leg.n, why, here)
        if why not in ("arrived", "under_me"):
            leg.events.append("no_move")
            return leg
        if any(k == kind and near(here, a) for k, a in self.arrivals):
            # The walk keeps ending at the same spot: whatever it aims at isn't taken by walking onto it.
            log.warning("STUCK %s: the %s walk ended at %s again", self.home, kind, here)
            self.fail(here)
            if kind == "big_map" and self.failed_spot(here):
                log.warning("big-map objects keep leading to %s: big-map objects off for this run", here)
                self.big_map_off = True
        if here:
            self.arrivals.append((kind, here))
        if kind == "frontier":
            self.frontier_result(leg, here, choice)
        return leg

    def frontier_result(self, leg: Leg, here, choice: dict) -> None:
        """A frontier leg uncovers objects (a gain), or at least fog (the next frontier lies past it), or nothing.
        Live 2026-11-11, run 22 (Grotto Peninsula, 63%): the one frontier leg found no object on the minimap, and
        "revealed nothing" then ended every frontier leg while the zone's ground ran on north into fog. Walking to
        the fog's edge is what uncovers it, so fog that shrank means the leg worked: the next frontier, farther in,
        follows (capped by FRONTIER_LEGS, and by STALL_LEGS when none of them finds an object). Only a patch whose
        fog didn't shrink is spent, and the next one is looked for in another direction."""
        frame = self.dev.screenshot()
        mm = minimap.read(frame, False)
        pr, pc = mm.centre
        found = [t for t in mm.tiles("item") + mm.tiles("monster") + mm.tiles("building")
                 if max(abs(t[0] - pr), abs(t[1] - pc)) > 1
                 and not (here and self.failed_spot(minimap.world_tile(mm, t, here)))]
        if found:
            leg.events.append("revealed")
            log.info("[leg %d] frontier revealed %d object tiles on the minimap", leg.n, len(found))
            return
        after = self.fog_here()
        before = choice.get("fog")
        if after is not None and before is not None and after <= before - FOG_REVEALED:
            leg.events.append("fog_revealed")
            log.info("[leg %d] frontier uncovered fog (%.0f%% -> %.0f%% round us), no object yet: the next frontier "
                     "goes on from here", leg.n, 100 * before, 100 * after)
            return
        if "dir" in choice:
            self.frontier_away.append(choice["dir"])
        log.info("[leg %d] frontier uncovered nothing (fog round us %s -> %s): the next one goes another way "
                 "(%d of %d used)", leg.n, before, after, self.frontier_used, FRONTIER_LEGS)

    def fog_here(self) -> Optional[float]:
        """The fog share round our dot on the area map, at the zoom the frontier was picked at (the map opens at the
        zoom it was left at), or None when the map or our dot isn't read."""
        if not goto.open_area_map(self.dev, self.det):
            return None
        time.sleep(0.5)
        frame = self.dev.screenshot()
        me = next((p for k, p in area_map.objects(frame) if k == "player"), None)
        ui.tap(self.dev, ui.BACK_ARROW, 2)
        if self.det.detect().state == "area_map":
            ui.tap(self.dev, ui.BACK_ARROW, 2)
        return area_map.fog_share(frame, me) if me else None

    def plan(self) -> Optional[Leg]:
        """Start the next leg from the first source that has an objective; None when none has."""
        leg = self.try_ring()
        if leg:
            return leg
        name = goto.area_name_here(self.det)
        key = self.tree.key(name) if name else None
        at_home = bool(name) and (goto.same_area(name, self.home or "") or goto.close_name(name, self.home or "")
                                  or bool(key and goto.same_area(key, self.home or "")))
        if at_home:
            # On-screen and minimap objects only inside the zone: in the explored neighbour we walked in from
            # (roam's way in) they are respawns that cost stamina (R-065).
            frame = self.dev.screenshot()
            xy, me = _xy(self.det), player_on_screen(self.det, frame)
            leg = self.try_known(frame, xy, me) or self.try_guard(frame, xy) or self.try_minimap(frame, xy, me)
            if leg:
                return leg
        return self.try_big_map()

    # ---------------------------------------------------------------- what a leg opens
    def settle(self, deadline: float) -> Optional[str]:
        """Handle every screen until we're back on the island map. Returns a stop status or None."""
        until = min(deadline, time.monotonic() + SETTLE_S)
        while time.monotonic() < until:
            d = self.det.detect()
            if self.unknown.seen(d.state):
                log.warning("unfamiliar screen; frame saved to %s", save_unknown(self.dev, "clear"))
                return "unknown_screen"
            if d.state == "world_map":
                return None
            stop = self.handle(d, deadline)
            if stop:
                return stop
        return None if time.monotonic() < deadline else "timeout"

    def handle(self, d, deadline: float) -> Optional[str]:
        dev, det = self.dev, self.det
        if d.state == "battle_prep":
            if self.tapped and self.tapped[2] == "monster" and not self.saved_fight:
                collectibles.save(self.tapped[0], self.tapped[1], "monster", "monster", self.home or "")
                self.saved_fight = True
            if hud_hp(dev.screenshot(), PREP_HP_BAR) * 100 < heal.FIGHT_MIN_HP and self.heal_tries < 2:
                self.heal_tries += 1
                log.info("battle prep: HP under %d%%; healing from the portrait", heal.FIGHT_MIN_HP)
                heal.quick_heal(dev, det, heal.BACK_OUT)
                return None
            ui.tap(dev, ui.START_BATTLE, 3)
            self.tapped, self.saved_fight = None, False
            self.event("fight")
        elif d.state in REWARD_STATES:
            pass_through(dev, d)
            self.event("pickup")
        elif d.state in ("battle", "loading"):
            # An auto battle (a mini-dungeon floor) or a loading screen: wait; it ends by itself.
            time.sleep(3)
            progress(("battle", d.text or "", int(time.monotonic() // 20)))
        elif pass_through(dev, d):
            pass  # dialogue
        elif d.state == "puzzle":
            # Live 2026-11-11 (run 24, Grotto Peninsula): a minimap leg walked onto the Ancient Fortress gate and its
            # "Energy Circuits" slab puzzle opened (unknown_screen then). Puzzles are skipped for now (R-153): back
            # out, skip the spot, and end the run `puzzle` with the gate noted on the zone.
            here = _xy(self.det) or (self.leg.xy if self.leg else None)
            ui.tap(dev, ui.BACK_ARROW, 2)
            title = (d.text or "").strip() or "a puzzle screen"
            log.warning("STUCK %s: %s at %s (R-153), stopping", self.home, title, here)
            self.note_objective(f"Puzzle ({title})", "dismiss", here)
            if here:
                self.skip_spot(here)
            k = self.tree.key(self.home or "")
            if k and not self.tree.zones[k].get("blocked"):
                self.tree.zones[k]["blocked"] = f"puzzle gate near {list(here) if here else '?'} (R-153)"
                self.tree.save()
            return "puzzle"
        elif d.state == "defeated":
            card, choice = self.decider.decide(self.ctx)
            dev.tap(*choice.point)
            # A fight we lost walls the zone off until we're stronger (live 2026-11-11, Lakeside Camp's guarded boss
            # at 28.5K): roam skips it until power grows (zones.Tree.lost_wall, LOST_RETRY_GAIN).
            # No power read, no wall: it could never be lifted.
            k = self.tree.key(self.home or "")
            if k and self.power is not None:
                self.tree.zones[k]["lost_at"] = self.power
                self.tree.zones[k]["lost_note"] = (f"lost a fight at {self.power}K near {self.leg.xy if self.leg else '?'}"
                                                  f" ({self.leg.what if self.leg else 'no leg'}), {server_day()}")
                self.tree.save()
                log.warning("STUCK %s: %s; roam skips it until power grows", self.home,
                            self.tree.zones[k]["lost_note"])
            return "defeated"
        elif d.state == "player_profile":
            ui.tap(dev, ui.ABOVE_POPUP, 1.5)
        elif d.state in TOWER_STATES:
            if tower.done_today():  # R-079: one climb a day, never retry a loss
                log.info("tower already climbed today; leaving it")
            else:
                climbed = tower.climb(dev, det, minutes=max(1.0, (deadline - time.monotonic()) / 60))
                log.info("tower climb: %s", climbed)
                if climbed in tower.OK:
                    tower.mark_done()
            Navigator(dev, det).go_home()
            if self.home:
                ui.tap(dev, ui.NAV_WORLD, 4)
                goto.go_to(dev, det, self.home)
        elif d.state == "area_map":
            ui.tap(dev, ui.BACK_ARROW, 2)  # left open by a big-map walk
        elif d.state == "home":
            return f"left_area:{d.state}"
        elif d.state == "dialogue_choice":
            return self.dialogue_choice()
        elif not self.wheel_spun and mapnav.lucky_wheel_free(det):
            # R-147: each wheel's first spin is free while its zone is unexplored; pressed only when no cost shows.
            log.info("Lucky Wheel in an unexplored zone, no cost shown: taking the free spin")
            self.wheel_spun = True
            ui.tap(dev, mapnav.WHEEL_SPIN, 8)
            ui.tap(dev, ui.BELOW_POPUP, 2)  # "YOU RECEIVED"
            self.event("wheel")
        elif (gate := mapnav.elemental_gate(dev, det)) is not None:
            # Gates of Elements: free with our companions' affinity (R-057).
            self.note_objective("Gate of Elements", gate, _xy(det))
            if gate == "opened":
                self.event("gate_open")
            else:
                self.skip_spot(self.leg.xy if self.leg else _xy(det))
        else:
            return self.card()
        return None

    def dialogue_choice(self) -> Optional[str]:
        """A puzzle NPC (Fonik, R-153): take Leave and note the puzzle; skip the spot."""
        lines = self.det.read_text([60, 300, 600, 750])
        leave = [b for t, b in lines if re.fullmatch(r"\s*Leave\.?\s*", t)]
        texts = " / ".join(t for t, _ in lines)
        if not leave:
            # mae, 2026-11-11: story choices are mae's call for now. Stop, and save the dialogue as a
            # reference under docs/screens/dialogs/, named for the scene; her pick is recorded there afterwards.
            path = save_dialogue(self.dev, texts, self.home)
            log.warning("dialogue choice with no Leave option (%s); stopping for mae. Screenshot: %s", texts, path)
            return "needs_decision"
        puzzle = bool(re.search(r"puzzle|Golden Beetle", texts + " " + " ".join(
            t for t, _ in self.det.read_text([0, 1150, 720, 130])), re.I))
        log.info("dialogue choice (%s): taking Leave%s", texts, " (a puzzle: noted)" if puzzle else "")
        here = _xy(self.det) or (self.leg.xy if self.leg else None)
        if puzzle:
            self.note_objective("Puzzle (Fonik: Golden Beetle solves it)", "dismiss", here)
        self.skip_spot(here)
        ui.tap(self.dev, ui.centre(leave[0]), 2)
        return None

    def card(self) -> Optional[str]:
        """Cards, dialogs and popups: the card rules (resource/policy/cards.json, goal explore)."""
        card, choice = self.decider.decide(self.ctx)
        here = _xy(self.det) or (self.leg.xy if self.leg else None)
        self.note_objective(card.title, choice.action, here)
        if self.tapped and self.tapped[2] == "building" and card.title and choice.action != "dismiss":
            collectibles.save(self.tapped[0], self.tapped[1], card.title, "interactable", self.home or "")
        self.tapped = None
        self.repeats = self.repeats + 1 if card.title == self.last_card else 0
        self.last_card = card.title
        if choice.action == "dismiss":
            if (re.search(r"Required Item|Insufficient items", card.body or "")
                    or re.search(r"Blockade|Sealing Pillar", card.title or "")):
                # A blocker that needs an item we don't have (Boulder Blockade: a Magic Drill, R-151; Sealing Pillar:
                # a Gateway Key, live 2026-11-11 in Rabbit Vault).
                need = re.search(r"Use an? ([A-Z][\w ]+?) to", card.body or "")
                why = f"{card.title.strip()} needs {need.group(1) if need else 'an item'}"
                log.warning("STUCK %s: %s", self.home, why)
                k = self.tree.key(self.home or "")
                if k:
                    self.tree.zones[k]["blocked"] = why
                    self.tree.save()
                ui.tap(self.dev, choice.point, 2)
                return "blocked_item"
            if not re.search(r"Goddess Statue", card.title or ""):
                # Nothing to do here: no more legs at this spot. A statue that isn't ready yet is the exception:
                # the pickups round it are what it waits for (live 2026-11-10, Zephyr Vale).
                self.skip_spot(here)
            k = self.tree.key(self.home or "")
            if k and here and card.title and re.search(r"Statue|Gate|Wheel|Rankings", card.title):
                spots = self.tree.zones[k].setdefault("dismissed_spots", [])
                if list(here) not in spots:
                    spots.append(list(here))
                    self.tree.save()
            log.info("card %r dismissed at map %s", card.title, here)
        elif choice.kind != "power_gate":
            self.event("acted")
        ui.tap(self.dev, choice.point, 3)
        if choice.kind == "power_gate":
            # A Gate of Power walls off one way, not the whole zone: skip its spot; stop when gates keep coming.
            self.gates += 1
            self.skip_spot(here)
            if self.gates >= GATE_LIMIT:
                log.info("blocked by %r (needs more power) %d times: this zone's wall", card.title, self.gates)
                return "power_gate"
            log.info("blocked by %r (needs more power) near %s: skipping that spot", card.title, here)
        if self.repeats >= REPEAT_LIMIT:
            log.warning("card %r keeps coming back; stopping", card.title)
            return "repeating_card"
        return None

    def note_objective(self, title: str, action: str, xy) -> None:
        """mae, 2026-11-10: every objective a zone has goes in the location tree, so what a run missed shows there."""
        k = self.tree.key(self.home or "")
        t = (title or "").strip()
        if not k or len(t) < 4 or not xy or re.search(r"^\d+$|Mage|Settings|Friend|Request|Chat", t):
            return
        objs = self.tree.zones[k].setdefault("objectives", [])
        for o in objs:
            if o["title"] == t and near(o["xy"], xy):
                if action != "dismiss":
                    o["done"] = True
                    self.tree.save()
                return
        objs.append({"title": t, "xy": list(xy), "done": action != "dismiss", "day": server_day()})
        self.tree.save()

    # ---------------------------------------------------------------- between legs
    def judge(self, leg: Leg, pct_before: Optional[int], xy_before) -> None:
        pct = self.read_pct()
        gained = (pct is not None and pct_before is not None and pct > pct_before) or bool(
            GAIN_EVENTS & set(leg.events))
        if gained:
            leg.result = "gain"
        elif "no_move" in leg.events or (xy_before and _xy(self.det) == xy_before and leg.source != "ring"):
            leg.result = "failed"
        else:
            leg.result = "reached"
        if leg.source == "minimap" and leg.what.startswith("building"):
            moved = pct is not None and pct_before is not None and pct > pct_before
            if moved or {"acted", "fight", "pickup"} & set(leg.events):
                self.inert_gold = 0
            else:
                self.inert_gold += 1
        log.info("[leg %d] result: %s | %s%% -> %s%% | events %s", leg.n, leg.result, pct_before, pct,
                 ", ".join(e for e in leg.events if e != "no_move") or "none")
        if gained:
            self.no_gain = 0
            self.ring_misses = 0
            if "acted" in leg.events and leg.source != "ring":
                self.skip_spot(leg.xy)  # a structure we acted on stays on the map: don't open it again this run
            mapnav.reset_locate()  # a gain may have moved the ring: ask the tracker again
        else:
            self.no_gain += 1
            if leg.source == "ring":
                self.ring_misses += 1  # the ring rests until another source gains; its spot isn't ours to skip
            elif leg.source != "frontier":
                self.fail(leg.xy)
        progress(("pct", self.pct, "legs", len(self.legs), "gains", sum(x.result == "gain" for x in self.legs)))

    def done(self) -> bool:
        if self.pct is not None and self.pct >= 100:
            return True
        return bool(self.home and self.own_quest and mapnav.quest_moved_on(self.det, self.home))

    def finish_zone(self) -> str:
        log.info("%s explored (100%% or the tracker moved on): done", self.home)
        if self.home and self.tree.key(self.home):
            self.tree.observe(self.home, pct=100)
            self.tree.save()
        rewards.claim_tracker_reward(self.dev, self.det, self.dev.screenshot())
        self.pct = 100
        # Live 2026-11-11 (run 16, IX): at 100% the zone's statue showed its red "!" and waited for a hand. Bless it
        # now (R-070: free, +1 Blessing Level) the way roam does: the ready badge nearest us on the big map.
        from .roam import Roamer  # roam imports this module
        time.sleep(2)
        n = Roamer(self.dev, self.det).bless_ready([self.home])
        log.info("%s: %s", self.home, "statue blessed" if n else "no statue ready to bless on the big map yet")
        return "zone_done"

    def map_chores(self) -> bool:
        """On the map between legs: heal under 70% (R-061), claim a finished quest's gift. True if it did one."""
        frame = self.dev.screenshot()
        if hud_hp(frame) * 100 < heal.FIGHT_MIN_HP and self.heal_tries < 2:
            self.heal_tries += 1
            log.info("HP under %d%%; healing from the profile", heal.FIGHT_MIN_HP)
            heal.quick_heal(self.dev, self.det, heal.NOTHING)
            return True
        if hud_hp(frame) * 100 >= heal.FIGHT_MIN_HP:
            self.heal_tries = 0
        if self.reward_taps < REWARD_TAPS_MAX and rewards.claim_tracker_reward(self.dev, self.det, frame):
            self.reward_taps += 1
            return True
        return False

    def back_to_zone(self, bare_det) -> None:
        # After an interrupt handler (a tutorial, a reward choice) that left us at home: walk back to the zone.
        if not self.home or bare_det.detect().state != "home":
            return
        log.info("an interrupt left us at home; walking back to %s", self.home)
        ui.tap(self.dev, ui.NAV_WORLD, 4)
        goto.go_to(self.dev, bare_det, self.home)

    # ---------------------------------------------------------------- the run
    def run(self, minutes: float, walk_there: bool = True) -> str:
        banner(log, "Clear Zone", "bring one zone to 100%, one named objective at a time (quest ring, objects on "
               "screen, the minimap and the big map, then the fog frontier)",
               f"100%, no objective left, {STALL_LEGS} legs in a row without progress, {minutes:g} minutes, "
               "a lost fight or an unfamiliar screen")
        deadline = time.monotonic() + minutes * 60
        mapnav.reset_locate()
        if self.det.detect().state != "world_map":
            from .roam import Roamer  # roam imports this module
            if not Roamer(self.dev, self.det)._to_world():
                return "not_on_map"
        if self.home and walk_there:
            goto.go_to(self.dev, self.det, self.home)
        if not self.home:
            self.home = mapnav.zone_here(self.dev, self.det, self.tree) or None
        if self.home and self.tree.get(self.home) and self.tree.explored(self.home):
            # The live tracker beats the tree (live 2026-11-11, run 14: a misread 100% for IX ended the run as
            # "explored" while the tracker said 35/100).
            live = mapnav.quest_counter(self.det, self.home)
            if live is None or live >= 100:
                log.info("%s is explored already (location tree): nothing to clear", self.home)
                return "explored"
            log.info("the location tree has %s explored but the tracker reads %d/100: clearing it", self.home, live)
            self.tree.observe(self.home, pct=live)
            self.tree.save()
        self.pct = (self.tree.get(self.home or "") or {}).get("pct") if self.home else None
        self.power = read_power(self.det)
        self.pct = self.read_pct()
        if not self.own_quest:
            self.map_pct()
            self.map_read_leg = 0
        self.pct_start = self.pct
        log.info("clearing %s from %s%%", self.home, self.pct)
        with resume_with(self.det, self.back_to_zone):
            while time.monotonic() < deadline:
                stop = self.settle(deadline)
                if stop:
                    return self.summary(stop)
                if self.map_chores():
                    continue
                self.read_pct()
                if not self.own_quest and len(self.legs) - self.map_read_leg >= MAP_PCT_EVERY:
                    self.map_pct()
                    self.map_read_leg = len(self.legs)
                if self.done():
                    return self.summary(self.finish_zone())
                stop = self.check_zone()
                if stop:
                    return self.summary(stop)
                if self.inert_gold >= PUZZLE_LEGS:
                    # Live 2026-11-11 (run 18, Stone Ruins II): the gold squares on the minimap were the tiles of a
                    # floor puzzle; stepping on them opens nothing and moves no %. Puzzles are skipped for now (R-153).
                    log.warning("STUCK %s: %d gold squares in a row opened nothing and moved no %%: a floor puzzle "
                                "(R-153), stopping", self.home, self.inert_gold)
                    self.note_objective("Puzzle (stone floor tiles)", "dismiss", _xy(self.det))
                    k = self.tree.key(self.home or "")
                    if k and not self.tree.zones[k].get("blocked"):
                        self.tree.zones[k]["blocked"] = "floor puzzle (R-153)"
                        self.tree.save()
                    return self.summary("puzzle")
                if self.no_gain >= STALL_LEGS:
                    log.warning("STUCK %s: %d legs in a row without progress (%s)", self.home, self.no_gain,
                                "; ".join(f"{x.source} {x.result}" for x in self.legs[-STALL_LEGS:]))
                    return self.summary("no_progress")
                pct_before, xy_before = self.pct, _xy(self.det)
                leg = self.plan()
                if leg is None:
                    left = [o["title"] for o in ((self.tree.get(self.home or "") or {}).get("objectives") or [])
                            if not o.get("done")]
                    log.warning("STUCK %s: no objective left at %s%% (open objectives in the tree: %s)", self.home,
                                self.pct, ", ".join(left) or "none")
                    return self.summary("no_objective")
                stop = self.settle(deadline)
                self.judge(leg, pct_before, xy_before)
                self.leg = None
                if stop:
                    return self.summary(stop)
        return self.summary("timeout")


def run(dev, det, minutes: float = 10, area: Optional[str] = None, allowed=None, walk_there: bool = True) -> str:
    """Clear `area` (walking there first unless walk_there is False), or the zone we stand in. `allowed` names
    neighbouring zones the run may stand in without walking back (roam's way in, R-150)."""
    return Clearer(dev, det, area, allowed).run(minutes, walk_there)


def _args(p) -> None:
    p.add_argument("--minutes", type=float, default=20, help="upper limit; the leg rules normally end the run")
    p.add_argument("--area", help="zone to clear, as named on the area map (walks there first)")


def _run(ctx, opts):
    return run(ctx.dev, ctx.det, opts.minutes, opts.area)


# Ends that mean the zone ran out of things to do or is walled, not that something went wrong.
OK = {"zone_done", "no_objective", "puzzle", "no_progress", "power_gate", "blocked_item", "explored", "timeout"}
LOOP = Loop("clear", "Clear Zone", "bring one zone to 100%: every leg toward a named objective", _run, _args, ok=OK)
