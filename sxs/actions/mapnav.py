"""Island-map helpers for exploration: which zone we're in, the zone's Explore quest and its gold ring, taps on map
objects, special cards (Gate of Elements, Lucky Wheel), keep-out areas for walk taps, and big-map pickers.

Kept from the Fog Walk when it was scrapped (mae, 2026-11-10; docs/fogwalk-postmortem.md). The Clear Zone loop
(`sxs/loops/clear.py`) and roam use them.
"""

from __future__ import annotations

import logging
import re
import time
from typing import Optional

import cv2

from . import goto
from .unstick import attack_guard
from ..core import ui
from ..core.paths import RESOURCE
from ..policy.zones import Tree
from ..vision import area_map, minimap
from ..vision.player import player_on_screen

log = logging.getLogger("sxs.actions.mapnav")


def to_world(player_xy: Optional[tuple[int, int]], player: Optional[tuple[int, int]],
             point: tuple[int, int]) -> Optional[tuple[int, int]]:
    """Map coordinates of a screen point, from the player's map coordinates and screen position (x grows east, y
    grows north). Screen points go stale as soon as the camera moves; map coordinates don't."""
    if player_xy is None or player is None:
        return None
    return (player_xy[0] + round((point[0] - player[0]) / minimap.SCREEN_TILE),
            player_xy[1] - round((point[1] - player[1]) / minimap.SCREEN_TILE))


MAP_LABELS_ROI = [0, 120, 720, 1060]  # area-map zone labels (legend and kingdom buttons excluded below)


QUEST_LOCATE_X = 330  # the locate (target) icon right of the tracker's progress line
QUEST_TARGET_DY = 80  # the quest ring floats this far above its target
_LOCATE_MISSES = 0  # locate taps since the last quest ring was seen (each tap toggles tracking)
APPROACH_DY = 75 # the ground tile just below a map object, walked to when a tap on the object itself did nothing


def quest_counter(det, zone: str) -> Optional[int]:
    """The tracked quest's counter when it is "Explore <zone> N/100", else None."""
    m = _explore_quest(det)
    if not m or not goto.same_area(m[0], zone):
        return None
    return m[1]


def _explore_quest(det) -> Optional[tuple[str, int]]:
    """The tracker's "Explore <zone> N/100" as (zone, N). OCR reads the numeral I as 1 or l before V/X
    ("ExploreVerdantglade1X26/100", live 2026-11-10): put the I back so IX doesn't read as another zone."""
    prog = det.find("Explore.Progress")
    m = re.search(r"Explore\s*(.+?)\s*(\d+)\s*/\s*100", prog.text if prog else "")
    if not m:
        return None
    name = re.sub(r"[1l|](?=[VX]\b)", "I", m.group(1).strip())
    name = re.sub(r"(?<=[a-z])(?=[IVX]+$)", " ", name)  # "VerdantgladeIX" -> "Verdantglade IX"
    return name, int(m.group(2))


def quest_moved_on(det, zone: str) -> bool:
    """The tracker shows another zone's Explore quest: this zone's quest was finished and claimed."""
    for i in range(2):  # twice: one misread must not end a walk (live 2026-11-10: "Verdantglade1X" ended IX at 17%)
        m = _explore_quest(det)
        if not m or goto.same_area(m[0], zone) or goto.close_name(m[0], zone):
            return False
        if i == 0:
            time.sleep(0.5)
    log.info("tracker reads %r, not %s", m, zone)
    return True


MARKER_TEMPLATES = ("marker.png", "marker_dim.png")  # resource/image/explore/: the gold quest ring
MARKER_MATCH = 0.75


def reset_locate() -> None:
    """A new run, or a gain that may have moved the quest's target: the locate icon may be tapped once again."""
    global _LOCATE_MISSES
    _LOCATE_MISSES = 0


def find_quest_ring(frame) -> Optional[tuple[int, int]]:
    """Centre of the gold quest ring anywhere below the very top (live 2026-11-09: as an edge ring it sat at y 50,
    above the pipeline node's region, so the step thought there was none)."""
    best = (0.0, None)
    for name in MARKER_TEMPLATES:
        tpl = cv2.imread(str(RESOURCE / "image" / "explore" / name))
        if tpl is None:
            continue
        r = cv2.matchTemplate(frame[20:960], tpl, cv2.TM_CCOEFF_NORMED)
        _, score, _, (x, y) = cv2.minMaxLoc(r)
        if score > best[0]:
            best = (score, (x + tpl.shape[1] // 2, 20 + y + tpl.shape[0] // 2))
    return best[1] if best[0] >= MARKER_MATCH else None


def quest_step(dev, det, fight: bool) -> bool:
    """One step toward the tracked Explore quest's next target. The tracker's locate icon toggles tracking ("Tracking
    On"/off), so it is tapped only when no gold ring shows. An edge ring is tapped to pan the camera to the target;
    then the target under the ring is tapped. A monster guarding it (red skull marker) is fought first. True when a
    step was taken."""
    prog = det.find("Explore.Progress")
    if not prog:
        return False
    global _LOCATE_MISSES
    ring = find_quest_ring(dev.screenshot())
    if ring is None:
        if _LOCATE_MISSES >= 1:
            # Live 2026-11-10: three locate taps in a row, 15 s apart, none showing a ring (the camera had drifted
            # off our character); each tap flips tracking, so tapping again only turns it back off. Once a tap
            # brought no ring, leave the pointer until a ring is seen again.
            return False
        ui.tap(dev, (QUEST_LOCATE_X, ui.centre(prog.box)[1]), 2)  # tracking was off: turn it on
        ring = find_quest_ring(dev.screenshot())
        if ring is None:
            _LOCATE_MISSES += 1
            log.info("locate tap showed no quest ring: not tapping it again until one shows")
            return False
    _LOCATE_MISSES = 0
    for _ in range(2):
        if ring is None:
            return False
        cx, cy = ring
        if cy < 130 and cx < 300:
            # An edge ring over the HUD (name, power, portrait): a tap there opens the profile or class page (live
            # 2026-11-10, a "Mage" card and the Class page). Leave the quest pointer for now.
            log.info("quest ring under the HUD at %s: not tapping it", ring)
            return False
        me = player_on_screen(det, dev.screenshot())
        on_me = me is not None and (cx - me[0]) ** 2 + (cy - me[1]) ** 2 < 90 ** 2
        # Traced live 2026-11-10 (scripts/tap_trace.py, tap 37): with us at the screen edge, the quest ring floated
        # over our own character at x 667; taken for an edge ring, the tap hit us and opened the profile. A ring on us
        # marks a target next to us, not an off-screen one.
        if not on_me and (cx < 70 or cx > 650 or cy < 150 or cy > 900):  # an edge ring: tapping it pans the camera
            ui.tap(dev, (cx, cy), 2)
            ring = find_quest_ring(dev.screenshot())
            continue
        if fight and attack_guard(dev, det):
            return True
        log.info("quest pointer: tapping the target under the ring at %s", (cx, cy))
        tap_object(dev, det, (cx, cy + QUEST_TARGET_DY))
        return True
    return False


def tap_object(dev, det, point: tuple[int, int], wait: float = 4) -> str:
    """Tap a map object (monster, pot, pickup). Live 2026-11-10 (Verdantglade VII, mae: "stuck at a monster fight
    again"): a tap on a monster several tiles away did nothing at all, the character didn't even walk, and the quest
    step tapped it again and again; from the tile beside it the same tap started the fight at once (62 -> 64 -> 67%).
    So when a tap leaves us on the map at the same coordinates, walk to the tile just below the object first, then
    tap it again. Returns "left_map" (a fight or card opened), "moved", "approached" or "nothing"."""
    before = goto.coords(det)
    tapped = off_me(det, point)
    dev.tap(*tapped)
    time.sleep(wait)
    after = goto.coords(det)
    if after is None:
        return "left_map"
    if before is None or after != before:
        return "moved"
    beside = off_me(det, (point[0], min(900, point[1] + APPROACH_DY)))
    log.info("tap on the object at %s didn't move us: walking beside it (%s) first", point, beside)
    dev.tap(*beside)
    for _ in range(6):  # walk until the coordinates stop changing
        time.sleep(1.5)
        now = goto.coords(det)
        if now is None:
            return "left_map"  # walking there started the fight (a monster that charges)
        if now == after:
            break
        after = now
    # The camera doesn't follow the walk, so the object stays where it was on screen.
    dev.tap(*off_me(det, point))
    time.sleep(wait)
    return "left_map" if goto.coords(det) is None else "approached"


WHEEL_SPIN = (360, 1100)  # "Tap to spin" on the Wheel of Destiny


def lucky_wheel_free(det) -> bool:
    """The Wheel of Destiny is open and its spin button shows no cost (just "Tap to spin")."""
    title = " ".join(t for t, _ in det.read_text([150, 130, 420, 70]))
    if "Wheel of Destiny" not in title:
        return False
    button = " ".join(t for t, _ in det.read_text([180, 1060, 360, 80]))
    return bool(re.fullmatch(r"\s*Tap to spin\s*", button))


COMPANION_TAB = (608, 1216)  # the friend picker's bottom tabs: Friends / Guild / Companion
COMPANION_PICKS = ((626, 230), (626, 348), (626, 466))  # select circles of the three companion rows
PICKER_OK = (360, 1104)
GATE_SLOT_DX = 136  # px between the card's friend slots; the first "+" sits this far right of our own portrait


def elemental_gate(dev, det) -> Optional[str]:
    """Gate of Wind (and the other Gates of Elements): "Total Wind Affinity reaches 1", with up to 3 friend slots.
    Affinity comes from relics (not unlocked) or helpers; our NPC companions (Akane, Qin, Killian) carry 101 each and
    adding them is free (R-057). Live 2026-11-10, Zephyr Vale: Akane alone opened it. Returns None when this isn't
    such a card, else "opened" or "short" (the requirement still not met after three helpers)."""
    lines = det.read_text([30, 520, 660, 520])
    text = " ".join(t for t, _ in lines)
    if not re.search(r"Gate of \w+", text) or not re.search(r"Affinity|Aegis", text) or "Power reaches" in text:
        return None
    taken = 0
    for _ in range(len(COMPANION_PICKS) + 1):
        lines = det.read_text([30, 520, 660, 640])
        opened = [b for t, b in lines if re.fullmatch(r"\s*Open\s*", t)]
        if opened:
            x, y, w, h = opened[0]
            ui.tap(dev, (x + w // 2, y + h // 2), 6)
            log.info("Gate of Elements: requirement met with companions; opened it")
            return "opened"
        friends = [b for t, b in lines if "Select Friends" in t]
        if not friends:
            break
        # The first empty "+" slot: our portrait sits at x ~150, the slots follow at GATE_SLOT_DX spacing.
        slot_y = friends[0][1] + 82
        if taken >= len(COMPANION_PICKS):
            break
        plus = sorted((b for t, b in lines if t.strip() == "+"), key=lambda b: b[0])
        slot = ((plus[0][0] + plus[0][2] // 2, plus[0][1] + plus[0][3] // 2) if plus
                else (152 + GATE_SLOT_DX * (taken + 1), slot_y))
        ui.tap(dev, slot, 3)
        ui.tap(dev, COMPANION_TAB, 2)
        ui.tap(dev, COMPANION_PICKS[taken], 1)
        ui.tap(dev, PICKER_OK, 3)
        taken += 1
        log.info("Gate of Elements: added companion %d", taken)
    log.warning("Gate of Elements: still short after adding companions; leaving it")
    ui.tap(dev, ui.ABOVE_POPUP, 2)
    return "short"


ME_RADIUS = 70  # px round our character on screen: a tap there opens our profile ("Mage", Class Level 8)


# Island-map HUD buttons a walk tap must never land on (x0, y0, x1, y1 at 720x1280). Live 2026-11-10: a walk tap
# toward a monster at (671, 376) hit the "Timed Packs" button and opened a paid pack popup.
HUD_KEEP_OUT = (
    (0, 0, 330, 200),      # portrait, name, power
    (0, 200, 110, 260),    # flag button under the portrait
    (500, 0, 720, 450),    # minimap, zone name and coordinates, Timed Packs
    (0, 700, 90, 820),     # Team / Apply button on the left edge
    (0, 950, 720, 1280),   # quest tracker, chat strip, bottom buttons
)
HUD_MARGIN = 12


def off_hud(point: tuple[int, int]) -> tuple[int, int]:
    """Move a walk tap out of any HUD button area, to the nearest edge of that area that is open map."""
    x, y = int(point[0]), int(point[1])
    for _ in range(3):  # leaving one area can land in another (rare); settle in a few moves
        hit = next((r for r in HUD_KEEP_OUT if r[0] <= x <= r[2] and r[1] <= y <= r[3]), None)
        if hit is None:
            break
        x0, y0, x1, y1 = hit
        options = [(x0 - HUD_MARGIN, y), (x1 + HUD_MARGIN, y), (x, y0 - HUD_MARGIN), (x, y1 + HUD_MARGIN)]
        options = [(a, b) for a, b in options if 20 <= a <= 700 and 20 <= b <= 1260]
        x, y = min(options, key=lambda p: abs(p[0] - x) + abs(p[1] - y))
    return x, y


def off_me(det, point: tuple[int, int], frame=None) -> tuple[int, int]:
    """A walk tap that would land on our own character opens the profile (live 2026-11-09 and -10, again and
    again). Push such a point out of ME_RADIUS, away from the character, so the tap still walks that way."""
    point = off_hud(point)
    me = player_on_screen(det, frame if frame is not None else det.device.screenshot())
    if me is None:
        return point
    dx, dy = point[0] - me[0], point[1] - me[1]
    d = (dx * dx + dy * dy) ** 0.5
    if d >= ME_RADIUS:
        return point
    if d < 1:
        dx, dy, d = 0, 1, 1  # straight on top of us: step down a little
    k = (ME_RADIUS + 15) / d
    return int(me[0] + dx * k), int(me[1] + dy * k)


def zone_here(dev, det, tree: Optional[Tree] = None) -> str:
    """The zone the player is in. R-140 as amended by mae (2026-11-10): the name under the minimap is always a valid
    description of the zone and is the first check. The big map's player dot (`zone_by_map`) is the fallback, for
    when that name is unreadable or isn't a zone the location tree knows."""
    name = goto.area_name_here(det)
    tree = tree or Tree.load()
    if name and tree.key(name):
        return tree.key(name)
    return zone_by_map(dev, det, name) or name


def zone_by_map(dev, det, hint: str = "") -> Optional[str]:
    """Where the player is by the white dot on the big map: the fallback for `zone_here` (R-140) when the name under
    the minimap can't be read or matched. A glance at the walking zoom (docs/big-map-survey.md: no survey zoom for
    this): the zone whose label is nearest our dot (the hint stands unless another label is clearly nearer). Always a
    fresh glance: an earlier look's dot is from before the last walk. None if unreadable."""
    from . import bigmap
    look = bigmap.get(dev, det).glance("where am I")
    if look is None or look.frame is None:
        return None
    frame = look.frame
    me = [look.dot] if look.dot else []
    labels = map_labels(det, frame)
    if not me or not labels:
        return None
    px, py = me[0]
    dist = {t: ((labels[t][0] - px) ** 2 + (labels[t][1] - py) ** 2) ** 0.5 for t in labels}
    best = min(dist, key=dist.get)
    # Labels sit mid-zone, so near an edge another zone's label can be the nearest (live 2026-11-09: at Verdantglade
    # V's east edge, Highland Woods). The name under the minimap stands unless the dot is clearly in another zone.
    hinted = [t for t in labels if hint and goto.same_area(t, hint)]
    if hinted and dist[best] >= area_map.LABEL_MARGIN * min(dist[t] for t in hinted):
        return hinted[0]
    return best


def map_labels(det, frame) -> dict:
    """Zone labels on the area map: name -> centre. Not % lines, power lines or the legend."""
    out = {}
    from . import bigmap
    lines = bigmap.map_text(det, frame, MAP_LABELS_ROI) if frame is not None else det.read_text(MAP_LABELS_ROI)
    for t, b in lines:
        t = t.replace("-", " ").strip(" |")
        if len(t) < 4 or re.search(r"%|\d\.?\d?K$|Exploration", t) or (b[0] > 530 and b[1] < 270):
            continue
        out[t] = ui.centre(b)
    return out


def label_is(label: str, zone: str) -> bool:
    """An area-map label names `zone`: the same name as OCR reads it (goto.same_area, close_name), or the full name
    of a zone given by its first words (live 2026-11-11, run 19: `clear --area "Lakeside"` never matched the label
    "Lakeside Camp", so the big map found nothing "in our zone" beside ten dots). The extra words must be words, not
    a roman numeral (numerals are goto.same_area's call)."""
    if not label or not zone:
        return False
    if goto.same_area(label, zone) or goto.close_name(label, zone):
        return True
    a, b = sorted((label.strip(), zone.strip()), key=len)
    if len(goto.squeeze(a)) < 6 or not b.lower().startswith(a.lower() + " "):
        return False
    return not re.fullmatch(r"[IVXl1|]+", b[len(a):].strip())


CROSSING_HOPS = 5  # walk taps toward the nearest light-to-shaded crossing before giving up


def enter_next_zone(dev, det, arrived=None, hops: int = CROSSING_HOPS) -> bool:
    """Walk into the unexplored zone beside us (mae, 2026-11-11): from the minimap, the nearest light (explored)
    ground that runs up to shaded (unexplored) ground over walkable tiles only, never toward a wall; walk there and
    step across. `arrived(name)` says whether the area name under the minimap is the zone we want (default: any
    change of name). True once it is."""
    start = goto.area_name_here(det)
    arrived = arrived or (lambda name: bool(name) and not goto.same_area(name, start))
    skip: set = set()
    for hop in range(1, hops + 1):
        frame = dev.screenshot()
        name = goto.area_name_here(det, frame)
        if arrived(name):
            log.info("zone entry: now in %s", name)
            return True
        mm = minimap.read(frame, True)  # we stand on the light (explored) side
        pr, pc = mm.centre
        near = [mm.grid[r][c] for r in range(pr - 3, pr + 4) for c in range(pc - 3, pc + 4)
                if 0 <= r < len(mm.grid) and 0 <= c < len(mm.grid) and max(abs(r - pr), abs(c - pc)) > 1]
        if sum(k == "walk_explored" for k in near) < sum(k == "walk_unexplored" for k in near):
            # Live 2026-11-11: in Grotto Peninsula (63%, not blessed) the "crossing" was the zone's own fog, three taps
            # at the same tile. A crossing means standing on an explored zone's light ground.
            log.info("zone entry: we stand on shaded ground (this zone isn't explored): no crossing to look for")
            return False
        path = minimap.path_to_crossing(mm, skip)
        me = player_on_screen(det, frame)
        if not path or me is None:
            log.info("zone entry: no crossing from light to shaded ground on the minimap (hop %d)", hop)
            return False
        xy = goto.coords(det)
        point = off_me(det, minimap.screen_point(me, mm, path[-1]), frame)
        log.info("zone entry hop %d: crossing %d tiles away, toward shaded ground at minimap %s: tap %s", hop,
                 len(path) - 1, path[-1], point)
        dev.tap(*point)
        time.sleep(4)
        if xy is None or goto.coords(det) == xy:
            # mae (2026-11-11, watching XIII): the walk reached the fog edge, but monsters stood in the entrance and
            # the character couldn't pass without beating them. A walk that didn't move with a monster on or beside
            # the way in: fight it (the caller's settle handles battle prep), then try the same crossing again.
            if block_fight(dev, det, mm, path, me):
                return False
            skip.add(path[-1])  # that crossing didn't take us anywhere: try the next one
    name = goto.area_name_here(det)
    return arrived(name)


def walk_to_entrance(dev, det, zone: str) -> str:
    """mae (2026-11-11): the minimap shows ~10 tiles; when no crossing shows there, find it on the big map. Opens the
    area map, picks the light-to-shaded entrance nearest `zone`'s label (area_map.crossings), walks to its light
    side. Returns goto.go_to's result, or "no_entrance" when the map shows none near that label."""
    chosen: dict = {}

    def pick(frame):
        labels = map_labels(det, frame)
        target = next((p for name, p in labels.items() if label_is(name, zone)), None)
        found = area_map.crossings(frame)
        if target is None or not found:
            log.info("zone entry (big map): %s", "no label for " + zone if target is None else "no entrances shown")
            return None
        c, box = min(found, key=lambda e: (e[0][0] - target[0]) ** 2 + (e[0][1] - target[1]) ** 2)
        chosen.update(centre=c, box=box)
        p = area_map.light_side(frame, c)
        log.info("zone entry (big map): entrance %s nearest the %s label at %s; walking to its light side %s",
                 box, zone, target, p)
        return p

    why = goto.go_to(dev, det, pick)
    return why if chosen else "no_entrance"


BLOCK_TILES = 2  # a monster this many minimap tiles from the way in blocks it


def block_fight(dev, det, mm, path, me) -> bool:
    """Tap a monster standing in or beside the way into a zone (a bracketed guard first). True when a fight (or any
    screen off the map) started: the caller's settle handles it."""
    if attack_guard(dev, det):
        return det.detect().state != "world_map"
    mons = [t for t in mm.tiles("monster") if any(abs(t[0] - p[0]) + abs(t[1] - p[1]) <= BLOCK_TILES for p in path)]
    if not mons or me is None:
        return False
    t = min(mons, key=lambda t: abs(t[0] - mm.centre[0]) + abs(t[1] - mm.centre[1]))
    point = off_me(det, minimap.screen_point(me, mm, t))
    log.info("zone entry: the walk didn't move and a monster stands by the way in (minimap %s): fighting it at %s",
             t, point)
    dev.tap(*point)
    time.sleep(4)
    return det.detect().state != "world_map"
