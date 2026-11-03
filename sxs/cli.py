"""Command line for the hands-and-eyes layer.

    python -m sxs screenshot [out.png]       save the current frame
    python -m sxs tap X Y
    python -m sxs swipe X1 Y1 X2 Y2 [--ms 300]
    python -m sxs back
    python -m sxs start | stop               launch or kill the game
    python -m sxs state [--save DIR]         print the detected screen state as JSON
    python -m sxs capture NAME               save a reference screenshot to docs/screens/NAME.png
    python -m sxs watch [--interval 2]       print the state whenever it changes (Ctrl+C to stop)

Coordinates are in the game's portrait frame, 720 wide by 1280 tall.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import cv2

from .device import DEFAULT_ADDRESS, REPO_ROOT, Device

SCREENS_DIR = REPO_ROOT / "docs" / "screens"


def _save_png(img, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), img, [cv2.IMWRITE_PNG_COMPRESSION, 9])
    return path


def _save_reference(img, path: Path) -> Path:
    """Reference screenshots are committed, so store them as 256-colour PNGs (~200 KB instead of ~550 KB).
    Detectors and OCR give the same results on them (checked by tests/check_states_offline.py)."""
    from PIL import Image

    path.parent.mkdir(parents=True, exist_ok=True)
    rgb = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    rgb.quantize(256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(path, optimize=True)
    return path


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="sxs", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--address", default=DEFAULT_ADDRESS, help="adb address of the MuMu instance")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("screenshot"); s.add_argument("out", nargs="?")
    s = sub.add_parser("tap"); s.add_argument("x", type=int); s.add_argument("y", type=int)
    s = sub.add_parser("swipe")
    for a in ("x1", "y1", "x2", "y2"):
        s.add_argument(a, type=int)
    s.add_argument("--ms", type=int, default=300)
    sub.add_parser("back"); sub.add_parser("start"); sub.add_parser("stop")
    s = sub.add_parser("state"); s.add_argument("--save", metavar="DIR", help="also save the frame here")
    s = sub.add_parser("capture"); s.add_argument("name")
    s = sub.add_parser("watch"); s.add_argument("--interval", type=float, default=2.0)
    args = p.parse_args(argv)

    dev = Device(args.address)
    if args.cmd == "screenshot":
        out = Path(args.out or f"screenshot-{datetime.now():%Y%m%d-%H%M%S}.png")
        print(_save_png(dev.screenshot(), out))
    elif args.cmd == "tap":
        dev.tap(args.x, args.y)
    elif args.cmd == "swipe":
        dev.swipe(args.x1, args.y1, args.x2, args.y2, args.ms)
    elif args.cmd == "back":
        dev.back()
    elif args.cmd == "start":
        dev.start_game()
    elif args.cmd == "stop":
        dev.stop_game()
    elif args.cmd == "capture":
        print(_save_reference(dev.screenshot(), SCREENS_DIR / f"{args.name}.png"))
    elif args.cmd in ("state", "watch"):
        from .state import StateDetector
        det = StateDetector(dev)
        if args.cmd == "state":
            d = det.detect()
            out = d.as_dict()
            if args.save:
                out["frame"] = str(_save_png(dev.screenshot(), Path(args.save) / f"{d.state}-{datetime.now():%H%M%S}.png"))
            print(json.dumps(out))
        else:
            last = None
            try:
                while True:
                    d = det.detect()
                    if d.state != last:
                        print(f"{datetime.now():%H:%M:%S} {json.dumps(d.as_dict())}", flush=True)
                        last = d.state
                    time.sleep(args.interval)
            except KeyboardInterrupt:
                pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
