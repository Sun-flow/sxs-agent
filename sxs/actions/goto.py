"""Walk to a place picked on the area map (mae's procedure, 2026-11-03).

The island map's camera doesn't follow the player, and tapping the ground auto-paths the character there. The
area map (tap the minimap) shows the whole island; tapping a spot on it moves the camera viewport (the white box)
there. So: open the area map, tap the destination, close the map, tap the middle of the screen, and the
character walks there, around cliffs and through gaps the player can't see.

    python -m sxs goto "Stone Ruins I"          # an area label on the area map
    python -m sxs goto 455 470                  # a point on the area map (720x1280 frame)
"""

from __future__ import annotations

import logging
import difflib
import re
import time
from typing import Optional

from ..core import ui
from ..core.device import save_unknown
from ..core.loop import Loop, banner
from ..vision.ocr import read_line

log = logging.getLogger("sxs.actions.goto")

MINIMAP = ui.MINIMAP  # tapping the minimap opens the area map
AREA_MAP_ZOOM_OUT = (682, 1113)  # the "-" under the area map's zoom slider
SCREEN_CENTRE = ui.SCREEN_CENTRE  # where the area-map point lands after the camera re-centres
COORDS = re.compile(r"\(?(\d+) ?[,.] ?(\d+)\)?")  # OCR reads the comma as "." sometimes
WALK_TIMEOUT_S = 60
LABEL_DY = 0  # tap the label itself: area labels sit on the area they name


def squeeze(t: str) -> str:
    """Area name for comparing: OCR reads a trailing roman "I" as l, 1 or | and drops spaces, so turn trailing
    runs of those into i's, then lowercase and drop spaces and dashes ("Verdantgladel" == "Verdantglade I")."""
    t = re.sub(r"[Il1|]+\s*$", lambda m: "i" * len(m.group(0).strip()), (t or "").strip())
    return re.sub(r"[\s\-]", "", t).lower()


AREA_NAME_ROI = [500, 255, 220, 36]  # area name above the coordinates, under the minimap


def area_name_here(det, frame=None) -> str:
    """The area name under the minimap (where the character stands). OCR sometimes reads an icon in front of it as a
    short token ("OA Verdantglade III", "R Verdantglade III", seen 2026-11-05), which made the fog walk think it had
    strayed: drop a leading token of one or two characters."""
    return re.sub(r"^\W*\w{1,2}\s+(?=[A-Z][a-z])", "", read_line(det, AREA_NAME_ROI, frame))


def close_name(a: str, b: str) -> bool:
    """OCR dropped or swapped a letter inside the name ("Drasi gard" for "Drasilgard", 2026-11-05), numerals equal."""
    x, y = squeeze(a), squeeze(b)
    if len(x) < 6 or len(y) < 6 or re.sub(r"[^i]+", "", x[-3:]) != re.sub(r"[^i]+", "", y[-3:]):
        return False
    return difflib.SequenceMatcher(None, x, y).ratio() >= 0.88


def same_area(a: str, b: str) -> bool:
    """Loose name match for OCR'd area names: equal after squeeze(), or one is the other missing up to two end
    characters (OCR drops or adds a trailing "I": "Highland Woods" / "Highland Woods I")."""
    x, y = squeeze(a), squeeze(b)
    if not x or not y:
        return False
    # Roman numerals at the end must agree: "Verdantglade V" is not "Verdantglade VI" (2026-11-05: the walk to V
    # went to VI's label and ended in Auroradrasil). Only when both names carry one; OCR often drops a final "I".
    nx, ny = re.search(r"(?<=[a-z]{4})([ivx]+)$", x), re.search(r"(?<=[a-z]{4})([ivx]+)$", y)
    if nx and ny and nx.group(1) != ny.group(1) and abs(len(nx.group(1)) - len(ny.group(1))) != 1:
        return False
    if nx and ny and {nx.group(1), ny.group(1)} in ({"v", "vi"}, {"iv", "v"}, {"ix", "x"}):
        return False
    short, long_ = sorted((x, y), key=len)
    # OCR drops or adds a trailing letter, including a stray "I" after a name without a numeral ("Highland Woods I"),
    # but a name that already ends in a numeral differs from the next one (Verdantglade I vs II vs III).
    return x == y or (long_.startswith(short) and len(long_) - len(short) <= 2
                      and not (short.endswith("i") and "i" in long_[len(short):]))


def area_labels(det) -> dict[str, list[int]]:
    """Area-map OCR: name -> box, for lines that look like area names (not the legend or percentages)."""
    out = {}
    # Up to the zoom slider (x 655): labels on the right third, such as Damp Woods at the survey zoom, were cut off
    # by the old x 540 limit (live 2026-11-10). The legend box (top right) is skipped.
    for text, box in det.read_text([0, 120, 655, 1050]):
        t = text.replace("-", " ").strip(" |")
        if re.search(r"Exploration|%|\d\.\dK", t) or len(t) < 4:
            continue
        if box[0] > 530 and box[1] < 260:
            continue
        out[t] = box
    return out


def coords(det) -> Optional[tuple[int, int]]:
    d = det.detect()
    if d.state != "world_map" or not d.text:
        return None
    m = COORDS.search(d.text)
    return (int(m.group(1)), int(m.group(2))) if m else None


def _label_point(det, name: str) -> Optional[tuple[int, int]]:
    labels = area_labels(det)
    hit = ([b for t, b in labels.items() if t.lower() == name.lower()]
           or [b for t, b in labels.items() if squeeze(t) == squeeze(name)]
           or [b for t, b in labels.items() if same_area(t, name)])
    if not hit:
        return None
    x, y, w, h = hit[0]
    return x + w // 2, y + h // 2


def _widen(dev) -> bool:
    """A label wasn't on the area map: it opens centred on the camera, so a far area can sit off screen (seen
    2026-11-04: from Moonveil Woods, Verdantglade II and Damp Woods were cut off). Zoom out one step and let the
    labels settle, then the caller reads again. Returns True when it tried."""
    # One "-" wasn't enough (live 2026-11-10: Damp Woods never showed from Jungle Camp): the survey zoom shows the
    # whole kingdom with readable labels.
    survey_zoom(dev)
    return True


SLIDER_DRAG = (682, 1090, 682, 1030)  # zoom knob from full zoom-out a quarter up (`world/area_map_survey_zoom.png`)


def survey_zoom(dev) -> None:
    """Area map open: zoom out fully, then one step closer by dragging the knob (mae, 2026-11-09: fully zoomed out the
    labels merge; the "+" button jumps to the closest zoom). The whole kingdom then nearly fits the screen."""
    for _ in range(4):
        dev.tap(*AREA_MAP_ZOOM_OUT)
        time.sleep(0.4)
    dev.swipe(*SLIDER_DRAG, 600)
    time.sleep(1.2)


LABEL_PANS = [(300, 900, 300, 450), (450, 620, 150, 620), (300, 400, 300, 850), (300, 400, 300, 850),
              (150, 620, 450, 620), (150, 620, 450, 620)]  # reveal south, east, north twice, west twice
LEGEND_FILTER_CLOSE = (360, 1150)  # a tap on the map below the legend's filter panel closes it


def open_area_map(dev, det) -> bool:
    """Tap the minimap and wait for the area map. Live 2026-11-10: a second tap sent while the map was still opening
    landed on the legend's search pill (the minimap sits under the legend) and opened the legend filter panel
    ("Select All"), which the state detector doesn't know; then nothing opened the map. Now: one tap, wait, retap only
    while still on the island map, and close the filter panel if it shows."""
    dev.tap(*MINIMAP)
    for i in range(6):
        time.sleep(1.2)
        state = det.detect().state
        if state == "area_map":
            return True
        if any(re.search(r"Select All", t) for t, _ in det.read_text([300, 700, 300, 80])):
            log.info("legend filter panel open: closing it")
            dev.tap(*LEGEND_FILTER_CLOSE)
            continue
        if state == "world_map" and i == 3:
            dev.tap(*MINIMAP)
    return det.detect().state == "area_map"


def go_to(dev, det, target, pan_for_target: bool = False) -> str:
    """target: an area name on the area map, or an (x, y) point there. Returns "arrived" (walked and stopped),
    "no_move" (coordinates didn't change: blocked or unreachable), "no_label", or "not_on_map"."""
    banner(log, "Go To", f"walk to {'the nearest object' if callable(target) else target} picked on the area map",
           f"the character stops moving, {WALK_TIMEOUT_S}s, or no movement at all after the tap")
    start = coords(det)
    for nudge in ((360, 600, 360, 760), (360, 600, 200, 600)):
        if start is not None:
            break
        # A quest ring or pointer can sit on the coordinates under the minimap: nudge the camera and look again.
        dev.swipe(*nudge, 400)
        time.sleep(1.5)
        start = coords(det)
    if start is None:
        return "not_on_map"
    dev.tap(*MINIMAP)
    time.sleep(2)
    if isinstance(target, tuple) and len(target) == 3 and isinstance(target[0], str):
        # (from_area, to_area, fraction): a point that far along from one label to the other, both read in this
        # same opening (the map's zoom changes between openings, so points from an earlier reading drift).
        a, b_, frac = target
        pa, pb = _label_point(det, a), _label_point(det, b_)
        if (pa is None or pb is None) and _widen(dev):
            pa, pb = _label_point(det, a), _label_point(det, b_)
        if pa is None or pb is None:
            log.warning("no %r or %r on the area map; frame %s", a, b_, save_unknown(dev, "goto"))
            dev.tap(*ui.BACK_ARROW)
            time.sleep(1.5)
            return "no_label"
        point = (int(pa[0] + (pb[0] - pa[0]) * frac), int(pa[1] + (pb[1] - pa[1]) * frac))
    elif isinstance(target, str):
        def find():
            labels = area_labels(det)
            # OCR swaps I, l and 1 and drops edge letters: match exactly first, then loosely.
            return labels, ([b for t, b in labels.items() if t.lower() == target.lower()]
                            or [b for t, b in labels.items() if squeeze(t) == squeeze(target)]
                            or [b for t, b in labels.items() if squeeze(target) in squeeze(t)]
                            or [b for t, b in labels.items() if squeeze(t) and squeeze(target).startswith(squeeze(t))
                                and same_area(t, target)]
                            or [b for t, b in labels.items() if close_name(t, target)])
        labels, hit = find()
        if not hit and _widen(dev):
            labels, hit = find()
        # Still not in view: the kingdom is bigger than the screen even zoomed out (live 2026-11-10: Damp Woods sat
        # off the bottom right while the map opened centred on Auroradrasil). Pan and look again.
        for drag in (LABEL_PANS if not hit else ()):
            dev.swipe(*drag, 1500)
            time.sleep(1.2)
            labels, hit = find()
            if hit:
                log.info("found %r after panning the area map", target)
                break
        if not hit:
            log.warning("no %r on the area map (saw %s); frame %s", target, list(labels), save_unknown(dev, "goto"))
            dev.tap(*ui.BACK_ARROW)
            time.sleep(1.5)
            return "no_label"
        x, y, w, h = hit[0]
        point = (x + w // 2, y + h // 2 + LABEL_DY)
    elif callable(target):
        # A picker reads this opening of the map (mae, 2026-11-05: tap the target on the big map, close it, tap the
        # element now in the middle of the screen).
        time.sleep(0.5)
        point = target(dev.screenshot())
        if point is None:
            # The map opens at whatever zoom it was left at, so the target may just be off screen (live 2026-11-09:
            # "no_target" for Verdantglade V while its dots were outside the view): look again zoomed out.
            survey_zoom(dev)
            point = target(dev.screenshot())
        for drag in (LABEL_PANS if point is None and pan_for_target else ()):
            # Off screen or under the dark bottom-left corner (live 2026-11-10: Jungle Camp's blue "!"): pan, look again.
            dev.swipe(*drag, 1500)
            time.sleep(1.2)
            point = target(dev.screenshot())
            if point is not None:
                break
        if point is None:
            dev.tap(*ui.BACK_ARROW)
            time.sleep(1.5)
            return "no_target"
    else:
        point = tuple(target)
    log.info("area map: centring on %s", point)
    dev.tap(*point)
    time.sleep(1.5)
    dev.tap(*ui.BACK_ARROW)
    time.sleep(2)
    dev.tap(*SCREEN_CENTRE)
    # Watch the coordinates: moving means the path was found; stopping means arrival (or a fight began).
    last, still, moved = start, 0, False
    deadline = time.monotonic() + WALK_TIMEOUT_S
    while time.monotonic() < deadline:
        time.sleep(2)
        c = coords(det)
        if c is None:
            st = det.detect().state
            log.info("left the map while walking (%s)", st)
            if st == "area_map":  # the map reopened (a tap on the minimap): close it again
                dev.tap(*ui.BACK_ARROW)
                time.sleep(1.5)
            return "arrived" if moved else "no_move"
        if c != last:
            moved, still, last = True, 0, c
        else:
            still += 1
            if still >= 2:
                break
    log.info("walk %s -> %s", start, last)
    return "arrived" if moved else "no_move"


def _args(p) -> None:
    p.add_argument("target", nargs="+", help="area name, or X Y on the area map")


def _run(ctx, opts):
    t = opts.target
    target = (int(t[0]), int(t[1])) if t[0].isdigit() else " ".join(t)
    return go_to(ctx.dev, ctx.det, target)


LOOP = Loop("goto", "Go To", "walk to an area (or an area-map point) via the area map", _run, _args, ok={"arrived"})
