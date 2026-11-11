"""Command line: run a loop, look at the screen, or drive the device by hand.

    python -m sxs <loop> [options]           run a loop (list below; `python -m sxs <loop> --help` for its options)
    python -m sxs see badges|minimap|gift|collectibles|labels [FRAME ...]   run one detector on frames (default: a live screenshot)
    python -m sxs bank                       copy unfamiliar frames (captures/unknown/) into docs/screens/unlabeled/
    python -m sxs label                      file the screens mae labelled in docs/screens/unlabeled/README.md
    python -m sxs labeler [--port 8765]      web page for naming screens and boxing what matters on them
    python -m sxs report [--day YYYY-MM-DD]  the day's progress report from saved snapshots (no emulator)
    python -m sxs zones                      the location tree: zones, CP, %, blessed, connections, open questions
    python -m sxs prelabel [--ocr]           draft detector boxes on the reference screens for mae to check in the labeler
    python -m sxs prelabel --one CLASS       draft one class only, then check it in the labeler's review grid
    python -m sxs dataset [--zip]            export the labelled boxes as a YOLO dataset (account name blacked out)
    python -m sxs items [add|find]           the item and currency symbol catalogue (resource/items/)
    python -m sxs bench [--one-per-state]    time the screen check on the reference screens, old way vs new (no emulator)

    python -m sxs screenshot [out.png]       save the current frame
    python -m sxs tap X Y
    python -m sxs swipe X1 Y1 X2 Y2 [--ms 300]
    python -m sxs back
    python -m sxs start | stop               launch or kill the game
    python -m sxs state [--save DIR]         print the detected screen state as JSON
    python -m sxs capture NAME               save a reference screenshot to docs/screens/<folder>/NAME.png
    python -m sxs capture NAME --burst N [--every S]   N frames S seconds apart into captures/sequences/NAME/
                                             (approach sequences for training data, docs/collectibles-capture-plan.md)
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

from .core.device import DEFAULT_ADDRESS, Device
from .core.paths import SCREENS as SCREENS_DIR
from .loops import REGISTRY

SEE = {"badges": "sxs.vision.badges", "minimap": "sxs.vision.minimap", "gift": "sxs.vision.gift",
       "collectibles": "sxs.vision.collectibles", "labels": "sxs.vision.labels"}
DEVICE_COMMANDS = ("screenshot", "tap", "swipe", "back", "start", "stop", "state", "capture", "watch")


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


def _burst(dev, name: str, n: int, every: float) -> Path:
    """Save n frames, `every` seconds apart, as captures/sequences/<name>/NN.png with a frames.json (time of each).
    Used to record a walk up to a world collectible and its pickup (docs/collectibles-capture-plan.md). The folder
    is gitignored: frames go to docs/screens only after picking (`python -m sxs bank` style), never in bulk."""
    from .core.paths import CAPTURES
    from .core.screens import NAME

    if not NAME.match(name):
        raise SystemExit(f"capture name {name!r} must be lower case letters, digits and _")
    out = CAPTURES / "sequences" / name
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    start = time.time()
    for i in range(1, n + 1):
        t = time.time()
        frame = dev.screenshot()
        path = _save_reference(frame, out / f"{i:02d}.png")
        rows.append({"file": path.name, "t": round(t - start, 2)})
        print(f"{name} {i}/{n} {path.name} at {t - start:.1f} s", flush=True)
        if i < n:
            time.sleep(max(0.0, every - (time.time() - t)))
    (out / "frames.json").write_text(json.dumps({"name": name, "every": every, "frames": rows}, indent=1) + "\n",
                                     encoding="utf-8")
    return out


def _loop_list() -> str:
    from .loops import get

    lines = []
    for name in REGISTRY:
        try:
            lines.append(f"  {name:<11} {get(name).summary}")
        except Exception as e:  # a loop that fails to import is listed, not fatal
            lines.append(f"  {name:<11} (failed to load: {e})")
    return "loops:\n" + "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    address = None
    if len(argv) >= 2 and argv[0] == "--address":
        address, argv = argv[1], argv[2:]
    if argv and argv[0] in REGISTRY:
        from .core.loop import run_cli
        from .loops import get

        return run_cli(get(argv[0]), argv[1:], address)
    if argv and argv[0] == "see":
        import importlib

        if len(argv) < 2 or argv[1] not in SEE:
            print(f"usage: python -m sxs see {{{','.join(SEE)}}} [FRAME ...]", file=sys.stderr)
            return 2
        return importlib.import_module(SEE[argv[1]]).main(argv[2:])
    if argv and argv[0] == "zones":  # the location tree (resource/world/zones.json), no device needed
        from .policy.zones import main as zones_main

        return zones_main(argv[1:])
    if argv and argv[0] == "items":  # the item and currency symbol catalogue (resource/items/), no device needed
        from .detect import items

        return items.main(argv[1:])
    if argv and argv[0] in ("prelabel", "dataset"):  # UI detector data (docs/detector-design.md), no device needed
        from .detect import dataset, prelabel

        return (prelabel if argv[0] == "prelabel" else dataset).main(argv[1:])
    if argv and argv[0] == "bench":  # screen-check timings on the reference screens, no device needed
        from .core.bench import main as bench_main

        return bench_main(argv[1:])
    if argv and argv[0] == "report":
        from .loops.progress import report_main

        return report_main(argv[1:])
    if argv and argv[0] == "labeler":
        from .labeler import main as labeler_main

        return labeler_main(argv[1:])
    if argv and argv[0] in ("bank", "label"):
        from .core import screens

        if argv[0] == "bank":
            new = screens.bank(_save_reference)
            print(f"{len(new)} new screen(s) in docs/screens/unlabeled/: " + ", ".join(new) if new else
                  "nothing new to bank")
            return 0
        filed, problems = screens.label()
        for line in filed + problems:
            print(line)
        print(f"{len(filed)} filed, {len(problems)} left in the bank with a problem")
        return 1 if problems else 0
    if address:
        argv = ["--address", address, *argv]
    if not argv or argv[0] in ("-h", "--help") or argv[0] not in (*DEVICE_COMMANDS, "--address"):
        print(__doc__)
        print(_loop_list())
        return 0 if argv and argv[0] in ("-h", "--help") else 2
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
    s.add_argument("--burst", type=int, default=0, help="save N frames into captures/sequences/NAME/ instead")
    s.add_argument("--every", type=float, default=0.5, help="seconds between burst frames (default 0.5)")
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
    elif args.cmd == "capture" and args.burst:
        print(_burst(dev, args.name, args.burst, args.every))
    elif args.cmd == "capture":
        from .core.screens import folder_for

        folder = folder_for(args.name)  # by prefix; a name no folder takes goes to unlabeled/
        print(_save_reference(dev.screenshot(), SCREENS_DIR / folder / f"{args.name}.png"))
    elif args.cmd in ("state", "watch"):
        from .core.state import StateDetector
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
