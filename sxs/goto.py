"""Walk to a place picked on the area map (mae's procedure, 2026-11-03).

The island map's camera doesn't follow the player, and tapping the ground auto-paths the character there. The
area map (tap the minimap) shows the whole island; tapping a spot on it moves the camera viewport (the white box)
there. So: open the area map, tap the destination, close the map, tap the middle of the screen, and the
character walks there, around cliffs and through gaps the player can't see.

    python -m sxs.goto "Stone Ruins I"          # an area label on the area map
    python -m sxs.goto 455 470                  # a point on the area map (720x1280 frame)
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
import time
from typing import Optional

from . import nav
from .device import Device, banner, save_unknown
from .state import StateDetector

log = logging.getLogger("sxs.goto")

MINIMAP = (610, 170)  # tapping the minimap opens the area map
SCREEN_CENTRE = (360, 640)  # where the area-map point lands after the camera re-centres
COORDS = re.compile(r"\(?(\d+), ?(\d+)\)?")
WALK_TIMEOUT_S = 60
LABEL_DY = 0  # tap the label itself: area labels sit on the area they name


def squeeze(t: str) -> str:
    """Area name for comparing: OCR reads a trailing roman "I" as l, 1 or | and drops spaces, so turn trailing
    runs of those into i's, then lowercase and drop spaces and dashes ("Verdantgladel" == "Verdantglade I")."""
    t = re.sub(r"[Il1|]+\s*$", lambda m: "i" * len(m.group(0).strip()), (t or "").strip())
    return re.sub(r"[\s\-]", "", t).lower()


AREA_NAME_ROI = [500, 255, 220, 36]  # area name above the coordinates, under the minimap


def area_name_here(det: StateDetector, frame=None) -> str:
    return " ".join(t for t, _ in det.read_text(AREA_NAME_ROI, frame)).strip()


def same_area(a: str, b: str) -> bool:
    """Loose name match for OCR'd area names: equal after squeeze(), or one is the other missing up to two end
    characters (OCR drops or adds a trailing "I": "Highland Woods" / "Highland Woods I")."""
    x, y = squeeze(a), squeeze(b)
    if not x or not y:
        return False
    short, long_ = sorted((x, y), key=len)
    # OCR drops or adds a trailing letter, including a stray "I" after a name without a numeral ("Highland Woods I"),
    # but a name that already ends in a numeral differs from the next one (Verdantglade I vs II vs III).
    return x == y or (long_.startswith(short) and len(long_) - len(short) <= 2
                      and not (short.endswith("i") and "i" in long_[len(short):]))


def area_labels(det: StateDetector) -> dict[str, list[int]]:
    """Area-map OCR: name -> box, for lines that look like area names (not the legend or percentages)."""
    out = {}
    for text, box in det.read_text([0, 120, 540, 1050]):
        t = text.replace("-", " ").strip(" |")
        if re.search(r"Exploration|%|\d\.\dK", t) or len(t) < 4:
            continue
        out[t] = box
    return out


def coords(det: StateDetector) -> Optional[tuple[int, int]]:
    d = det.detect()
    if d.state != "world_map" or not d.text:
        return None
    m = COORDS.search(d.text)
    return (int(m.group(1)), int(m.group(2))) if m else None


def go_to(dev: Device, det: StateDetector, target) -> str:
    """target: an area name on the area map, or an (x, y) point there. Returns "arrived" (walked and stopped),
    "no_move" (coordinates didn't change: blocked or unreachable), "no_label", or "not_on_map"."""
    banner(log, "Go To", f"walk to {target} picked on the area map",
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
    if isinstance(target, str):
        labels = area_labels(det)
        # OCR swaps I, l and 1 and drops edge letters: match exactly first, then loosely.
        hit = ([b for t, b in labels.items() if t.lower() == target.lower()]
               or [b for t, b in labels.items() if squeeze(t) == squeeze(target)]
               or [b for t, b in labels.items() if squeeze(target) in squeeze(t)]
               or [b for t, b in labels.items() if squeeze(t) and squeeze(target).startswith(squeeze(t))
                   and same_area(t, target)])
        if not hit:
            log.warning("no %r on the area map (saw %s); frame %s", target, list(labels), save_unknown(dev, "goto"))
            dev.tap(*nav.BACK_ARROW)
            time.sleep(1.5)
            return "no_label"
        x, y, w, h = hit[0]
        point = (x + w // 2, y + h // 2 + LABEL_DY)
    else:
        point = tuple(target)
    log.info("area map: centring on %s", point)
    dev.tap(*point)
    time.sleep(1.5)
    dev.tap(*nav.BACK_ARROW)
    time.sleep(2)
    dev.tap(*SCREEN_CENTRE)
    # Watch the coordinates: moving means the path was found; stopping means arrival (or a fight began).
    last, still, moved = start, 0, False
    deadline = time.monotonic() + WALK_TIMEOUT_S
    while time.monotonic() < deadline:
        time.sleep(2)
        c = coords(det)
        if c is None:
            log.info("left the map while walking (%s)", det.detect().state)
            return "arrived" if moved else "no_move"
        if c != last:
            moved, still, last = True, 0, c
        else:
            still += 1
            if still >= 2:
                break
    log.info("walk %s -> %s", start, last)
    return "arrived" if moved else "no_move"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("target", nargs="+", help="area name, or X Y on the area map")
    args = p.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    target = (int(args.target[0]), int(args.target[1])) if args.target[0].isdigit() else " ".join(args.target)
    dev = Device()
    result = go_to(dev, StateDetector(dev), target)
    print(result, flush=True)
    return 0 if result == "arrived" else 1


if __name__ == "__main__":
    sys.exit(main())
