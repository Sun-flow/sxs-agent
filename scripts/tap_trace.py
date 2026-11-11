"""Run Clear Zone (or roam) with every tap logged (point, caller line) and the frame saved before it, to find
which tap causes a stuck point (2026-11-10: the player profile kept opening mid-walk).

    python scripts/tap_trace.py AREA MINUTES          # clear --area AREA, from where we stand; frames in captures/taps/
    python scripts/tap_trace.py roam AREA MINUTES     # roam --area AREA
"""
import logging
import sys
import time
import traceback
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sxs.core.device import Device  # noqa: E402
from sxs.core.state import StateDetector  # noqa: E402
from sxs.loops import clear  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
OUT = Path(__file__).resolve().parent.parent / "captures" / "taps"
OUT.mkdir(parents=True, exist_ok=True)
dev = Device()
det = StateDetector(dev)
real_tap = dev.tap
n = [0]


def traced_tap(x, y):
    n[0] += 1
    frame = dev.screenshot()
    stack = [f for f in traceback.extract_stack()[:-1] if "sxs" in f.filename and "ui.py" not in f.filename]
    caller = stack[-1]
    name = f"{n[0]:03d}_{int(x)}_{int(y)}.png"
    cv2.circle(frame, (int(x), int(y)), 14, (0, 0, 255), 3)
    cv2.imwrite(str(OUT / name), frame)
    logging.info("TAP %s at (%d, %d) from %s:%d %s", n[0], x, y, Path(caller.filename).name, caller.lineno,
                 caller.line)
    real_tap(x, y)


dev.tap = traced_tap
if sys.argv[1] == "roam":
    from sxs.loops.roam import Roamer
    print(Roamer(dev, det).run(float(sys.argv[3]), sys.argv[2], 1, 15))
else:
    print(clear.run(dev, det, minutes=float(sys.argv[2]), area=sys.argv[1], walk_there=False))
