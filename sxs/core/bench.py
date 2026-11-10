"""Time the screen check on the reference screens: how long detect() takes per screen and per node, old against new.

    python -m sxs bench [NAME ...] [--one-per-state] [--per-node] [--inference cpu|directml|auto]

No emulator needed: frames come from docs/screens/ (screens with an expected state). For every screen it runs the
state chain twice on the same frame, the old way (each OCR node runs on its own) and the new way (shared strip reads,
docs/vision-upgrade.md), checks both against docs/screens/expected.json, and prints the timings. --per-node also
times every node of the chain alone on one world-map frame. --inference picks where OCR runs (same as the
SXS_INFERENCE environment variable); run it once per choice to compare CPU with DirectML on the same machine.
"""

from __future__ import annotations

import argparse
import os
import statistics
import sys
import time


def _summary(label: str, ms: list[int]) -> str:
    if not ms:
        return f"{label}: no screens"
    s = sorted(ms)
    return (f"{label}: median {statistics.median(s):.0f} ms, mean {statistics.mean(s):.0f}, "
            f"p90 {s[int(0.9 * (len(s) - 1))]}, max {s[-1]}")


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="python -m sxs bench", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("names", nargs="*", help="only these screens (file names without .png)")
    p.add_argument("--one-per-state", action="store_true", help="one screen per expected state (quicker)")
    p.add_argument("--per-node", action="store_true", help="also time each node alone on a world-map frame")
    p.add_argument("--inference", choices=("cpu", "directml", "auto"), help="where OCR runs (default: library's)")
    args = p.parse_args(argv)
    if args.inference:
        os.environ["SXS_INFERENCE"] = args.inference

    import cv2

    from .replay import ImageDevice
    from .screens import load_expected, reference_screens
    from .state import ENTRY, StateDetector, state_name

    dev = ImageDevice()
    det = StateDetector(dev)
    order = det.resource.get_node_data(ENTRY)["action"]["param"]["custom_action_param"]["order"]
    old_override = {ENTRY: {"custom_action_param": {"order": order}}}  # no strips: every node runs as itself
    expected = load_expected()["states"]
    screens = [s for s in reference_screens() if s.stem in expected and (not args.names or s.stem in args.names)]
    if args.one_per_state:
        seen, keep = set(), []
        for s in screens:
            if expected[s.stem] not in seen:
                seen.add(expected[s.stem])
                keep.append(s)
        screens = keep
    print(f"inference: {det.inference}; {len(screens)} screens")

    def chain(frame, override=None) -> tuple[str, int]:
        det._action.frame = frame
        t = time.perf_counter()
        det.tasker.post_task(ENTRY, override or {}).wait()
        ms = int((time.perf_counter() - t) * 1000)
        hit = det._action.hit
        return (state_name(hit[0]) if hit else "unknown"), ms

    if screens:
        chain(cv2.imread(str(screens[0])))  # warm up the OCR models
    old_ms, new_ms, wrong = [], [], []
    for s in screens:
        frame = cv2.imread(str(s))
        want = expected[s.stem]
        got_old, t_old = chain(frame, old_override)
        got_new, t_new = chain(frame)
        old_ms.append(t_old)
        new_ms.append(t_new)
        flag = "" if got_old == want and got_new == want else "  <-- WRONG"
        if flag:
            wrong.append(s.stem)
        print(f"{s.stem[:34]:34} {want:18} old {t_old:5d} ms ({got_old})  new {t_new:5d} ms ({got_new}){flag}",
              flush=True)
    print(_summary("old", old_ms))
    print(_summary("new", new_ms))
    if old_ms and new_ms:
        print(f"speed-up (median): {statistics.median(old_ms) / max(1, statistics.median(new_ms)):.1f}x")

    # The same frame twice: the second detect() is answered from the cache.
    if screens:
        dev.set_frame(screens[0])
        det.forget()
        det.detect()
        print(f"unchanged frame (cache): {det.detect().elapsed_ms} ms")

    if args.per_node:
        world = next((s for s in reference_screens() if expected.get(s.stem) == "world_map"), None)
        if world is not None:
            frame = cv2.imread(str(world))
            print(f"per node, alone, on {world.stem}:")
            total = 0.0
            for node in order:
                t = time.perf_counter()
                det.find(node, frame)
                ms = (time.perf_counter() - t) * 1000
                total += ms
                print(f"  {node:24} {ms:6.0f} ms")
            print(f"  total {total:.0f} ms")
    print("all good" if not wrong else f"{len(wrong)} wrong: {', '.join(wrong)}")
    return 1 if wrong else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
