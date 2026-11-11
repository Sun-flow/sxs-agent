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
LABEL_DY = -26  # just above the label: it sits on its zone, and a Portal can sit right under it (mae, 2026-11-10: Verdantglade VI; the tap opened the portal card)


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


def area_labels(det, frame=None) -> dict[str, list[int]]:
    """Area-map OCR: name -> box, for lines that look like area names (not the legend or percentages). With a frame,
    the OCR is shared with the other area-map readers (`bigmap.map_text`: one read per frame)."""
    from . import bigmap
    out = {}
    # Up to the zoom slider (x 655): labels on the right third, such as Damp Woods at the survey zoom, were cut off
    # by the old x 540 limit (live 2026-11-10). The legend box (top right) is skipped.
    roi = [0, 120, 655, 1050]  # x, y, w, h
    lines = bigmap.map_text(det, frame, roi) if frame is not None else det.read_text(roi)
    for text, box in lines:
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


def _label_point(det, name: str, frame=None) -> Optional[tuple[int, int]]:
    labels = area_labels(det, frame)
    hit = ([b for t, b in labels.items() if t.lower() == name.lower()]
           or [b for t, b in labels.items() if squeeze(t) == squeeze(name)]
           or [b for t, b in labels.items() if same_area(t, name)])
    if not hit:
        return None
    x, y, w, h = hit[0]
    return x + w // 2, y + h // 2


def _widen(dev) -> bool:
    """A label wasn't on the area map. It used to zoom out to the survey zoom and look again; mae (2026-11-11,
    docs/big-map-survey.md): the survey zoom is only for seeing which zones exist, walking never needs it. Callers pan
    toward the label instead (`_pans`). Kept so callers read the same; always False."""
    return False


PAN_CENTRE, PAN_LEN, PAN_MS = (330, 620), 350, 1500  # directed pans: a slow drag from the map's middle


def _pans(toward) -> list:
    """Drags that bring a label in `toward` (a unit vector on the area map, from the location tree) into view: two
    along it. Without a direction, the old six-drag sweep."""
    if not toward:
        return LABEL_PANS
    cx, cy = PAN_CENTRE
    dx, dy = int(-toward[0] * PAN_LEN), int(-toward[1] * PAN_LEN)  # drag the map the other way to reveal it
    return [(cx, cy, cx + dx, cy + dy)] * 2


SLIDER_DRAG = (682, 1090, 682, 1030)  # zoom knob from full zoom-out a quarter up (`world/area_map_survey_zoom.png`)


def survey_zoom(dev) -> None:
    """Area map open: zoom out fully, then one step closer by dragging the knob (mae, 2026-11-09: fully zoomed out the
    labels merge; the "+" button jumps to the closest zoom). The whole kingdom then nearly fits the screen. Only the
    discovery survey uses it (mae, 2026-11-11); it skips the taps when the knob already shows the survey zoom."""
    from . import bigmap
    bigmap.set_zoom(dev, dev.screenshot(), bigmap.SURVEY_KNOB_Y)


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


EDGE_X, EDGE_TOP, EDGE_BOTTOM = 110, 260, 1000  # area-map taps outside this box are dragged to the middle first
ME_AT_CENTRE_PX = 70 # our character's point (just above its label) this close to the centre means a tap there hits us


def _me_at_centre(dev, det) -> bool:
    from ..vision.player import player_on_screen
    me = player_on_screen(det, dev.screenshot())
    return bool(me and abs(me[0] - SCREEN_CENTRE[0]) <= ME_AT_CENTRE_PX
                and abs(me[1] - SCREEN_CENTRE[1]) <= ME_AT_CENTRE_PX)


def go_to(dev, det, target, pan_for_target: bool = False, toward=None, purpose: str = "") -> str:
    """target: an area name on the area map, or an (x, y) point there. Returns "arrived" (walked and stopped),
    "no_move" (coordinates didn't change: blocked or unreachable), "no_label", or "not_on_map".

    The map opens at the walking zoom (docs/big-map-survey.md): its frame is recorded in the shared BigMap (a glance)
    before anything is tapped. A label or target not in view is looked for by drags `toward` it (a unit vector from
    the location tree) when given, else by the six-drag sweep; never by zooming out."""
    from . import bigmap
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
    t0 = time.monotonic() - 2
    bm = bigmap.get(dev, det)
    frame = dev.screenshot()
    if bigmap.knob_y(frame) is not None and bigmap.set_zoom(dev, frame, bigmap.WALK_KNOB_Y):
        frame = dev.screenshot()  # only with the knob seen: a blind "-" tap on the island map hits the tracker
    what = purpose or ("pick" if callable(target) else f"walk to {target if not isinstance(target, tuple) else 'a point'}")
    if bigmap.knob_y(frame) is not None:
        bm.record(frame, what, t0=t0)
    if isinstance(target, tuple) and len(target) == 3 and isinstance(target[0], str):
        # (from_area, to_area, fraction): a point that far along from one label to the other, both read in this
        # same opening (the map's zoom changes between openings, so points from an earlier reading drift).
        a, b_, frac = target
        pa, pb = _label_point(det, a, frame), _label_point(det, b_, frame)
        for drag in (_pans(toward) if pa is None or pb is None else ()):
            dev.swipe(*drag, PAN_MS)
            time.sleep(1.2)
            cur = dev.screenshot()
            pa, pb = _label_point(det, a, cur), _label_point(det, b_, cur)
            if pa is not None and pb is not None:
                break
        if pa is None or pb is None:
            log.warning("no %r or %r on the area map; frame %s", a, b_, save_unknown(dev, "goto"))
            dev.tap(*ui.BACK_ARROW)
            time.sleep(1.5)
            return "no_label"
        point = (int(pa[0] + (pb[0] - pa[0]) * frac), int(pa[1] + (pb[1] - pa[1]) * frac))
    elif isinstance(target, str):
        def find(fr):
            labels = area_labels(det, fr)
            # OCR swaps I, l and 1 and drops edge letters: match exactly first, then loosely.
            return labels, ([b for t, b in labels.items() if t.lower() == target.lower()]
                            or [b for t, b in labels.items() if squeeze(t) == squeeze(target)]
                            or [b for t, b in labels.items() if squeeze(target) in squeeze(t)]
                            or [b for t, b in labels.items() if squeeze(t) and squeeze(target).startswith(squeeze(t))
                                and same_area(t, target)]
                            or [b for t, b in labels.items() if close_name(t, target)])
        labels, hit = find(frame)
        # Not in view (live 2026-11-10: Damp Woods sat off the bottom right while the map opened centred on
        # Auroradrasil): pan toward it and look again; never zoom out to search (mae, 2026-11-11).
        for drag in (_pans(toward) if not hit else ()):
            dev.swipe(*drag, PAN_MS)
            time.sleep(1.2)
            labels, hit = find(dev.screenshot())
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
        # A picker reads this same opening (recorded above). Not found: no zoom-out any more (mae, 2026-11-11);
        # callers that may need it pan (pan_for_target), toward the target when they know the way.
        point = target(frame)
        for drag in (_pans(toward) if point is None and pan_for_target else ()):
            # Off screen or under the dark bottom-left corner (live 2026-11-10: Jungle Camp's blue "!"): pan, look again.
            dev.swipe(*drag, PAN_MS)
            time.sleep(1.2)
            point = target(dev.screenshot())
            if point is not None:
                break
        if point is None:
            dev.tap(*ui.BACK_ARROW)
            time.sleep(1.5)
            return "no_target"
        if not (EDGE_X <= point[0] <= 720 - EDGE_X and EDGE_TOP <= point[1] <= EDGE_BOTTOM):
            # Live 2026-11-10 (Verdantglade VII's statue at (671, 575), twice): a tap near the map's edge didn't
            # centre the camera on it and the walk went nowhere; the same statue tapped mid-screen worked at once.
            # Drag the map so the target comes to the middle, then pick again on the new view.
            dx, dy = SCREEN_CENTRE[0] - point[0], SCREEN_CENTRE[1] - point[1]
            sx, sy = SCREEN_CENTRE[0] - dx // 2, SCREEN_CENTRE[1] - dy // 2
            dev.swipe(sx, sy, sx + dx, sy + dy, 1500)
            time.sleep(1.2)
            again = target(dev.screenshot())
            if again is not None:
                log.info("target near the map edge at %s: dragged it to %s", point, again)
                point = again
    else:
        point = tuple(target)
    log.info("area map: centring on %s", point)
    dev.tap(*point)
    time.sleep(1.5)
    dev.tap(*ui.BACK_ARROW)
    time.sleep(2)
    for _ in range(2):
        # Live 2026-11-10 (VII, 4 times): the back arrow didn't close the map (the tap on the target had selected
        # it, and the first back only cleared that), so the centre tap landed on the map. Close it for sure.
        if det.detect().state != "area_map":
            break
        dev.tap(*ui.BACK_ARROW)
        time.sleep(1.5)
    if _me_at_centre(dev, det):
        # Live 2026-11-10 (Verdantglade VII, twice in a row): the camera came back to our character instead of
        # staying on the picked object, so the centre tap hit us and opened the profile. Tap nothing: the caller
        # falls back to its minimap step toward the object.
        log.info("our character is at the screen centre after closing the map: not tapping it")
        return "under_me"
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
            elif st == "player_profile":
                # Our own profile: close it here, or the caller's next walk tap lands on its charm row and opens a
                # charm card with a Replace button (live 2026-11-10).
                ui.tap(dev, ui.ABOVE_POPUP, 1.5)
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
