"""The interrupt layer (sxs/core/interrupts.py) and its table (sxs/actions/interrupts.py), offline, no emulator.

    python tests/check_interrupts.py

Checks, with a scripted fake detector:
- a matching screen pauses the loop, runs the handler, and the loop gets the fresh detection after it;
- an owned interrupt (Loop.owns / owning()) passes through to the loop untouched;
- a handler's detect() calls don't trigger interrupts (no recursion);
- an interrupt that keeps firing is muted, and MUTE from a handler mutes it;
- LoopStop from a handler ends the run through the runner with that status and exit 1;
- resume_with() runs after a handler and is a no-op on a bare detector;
- the table's tutorial row fires on the live tutorial frames and on no other reference screen in the states it
  watches (docs/screens + expected.json), so the finder's known false matches (Mall, prayer, tower rows, furniture
  popups) can't pause a loop.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import cv2  # noqa: E402
import numpy as np  # noqa: E402

from sxs.core import interrupts as ix  # noqa: E402
from sxs.core.loop import Ctx, Loop, finish  # noqa: E402


class FakeDet:
    """Returns the scripted states in order (the last one repeats)."""

    def __init__(self, states):
        self.states, self.calls = list(states), 0
        self.last_frame = np.zeros((1280, 720, 3), np.uint8)

    def detect(self):
        s = self.states[min(self.calls, len(self.states) - 1)]
        self.calls += 1
        return SimpleNamespace(state=s, text=None, box=None)


# Live tutorials the row must catch (builder, 2026-11-05): the outline on the Auroradrasil tree, the filled glow on
# Akane's Invite. Every other reference screen in the row's states must not fire it.
TUTORIAL_FRAMES = {"auroradrasil_tutorial_highlight", "companions_invite_tutorial"}


def table(log, outcome=ix.RESUME, stop=None):
    def handler(dev, det, d):
        log.append(("handler", d.state))
        det.detect()  # a handler looking at the screen must not re-enter the table
        if stop:
            raise ix.LoopStop(stop, screen=d.state)
        return outcome
    return [ix.Interrupt("popup", frozenset({"popup"}), handler, budget=5)]


def main() -> int:
    bad = []

    # 1. pause, handle, hand back the fresh state
    log = []
    raw = FakeDet(["popup", "world_map"])
    det = ix.InterruptingDetector(raw, None, table(log), "Test")
    d = det.detect()
    if d.state != "world_map" or log != [("handler", "popup")]:
        bad.append(f"handled: got {d.state}, {log}")
    if not det.handled or det.handled[0]["interrupt"] != "popup":
        bad.append(f"handled record: {det.handled}")

    # 2. owned interrupts pass through
    log = []
    det = ix.InterruptingDetector(FakeDet(["popup"]), None, table(log), "Test", frozenset({"popup"}))
    if det.detect().state != "popup" or log:
        bad.append("owned interrupt was handled")
    det = ix.InterruptingDetector(FakeDet(["popup"]), None, table(log), "Test")
    with det.owning("popup"):
        if det.detect().state != "popup" or log:
            bad.append("owning() did not pass the screen through")
    if det.owned:
        bad.append("owning() left the name behind")

    # 3. a popup that never clears: handled a bounded number of times per check, then muted
    log = []
    det = ix.InterruptingDetector(FakeDet(["popup"]), None, table(log), "Test")
    for _ in range(4):
        det.detect()
    if len(log) > ix.BURST or det.records["popup"].muted_until <= time.monotonic():
        bad.append(f"burst not muted: {len(log)} handler runs")

    # 4. MUTE from a handler
    log = []
    det = ix.InterruptingDetector(FakeDet(["popup", "popup", "popup"]), None, table(log, ix.MUTE), "Test")
    if det.detect().state != "popup" or len(log) != 1:
        bad.append(f"MUTE: {len(log)} runs")

    # 5. resume_with
    seen = []
    det = ix.InterruptingDetector(FakeDet(["popup", "home"]), None, table([]), "Test")
    with ix.resume_with(det, lambda bare: seen.append(bare.detect().state)):
        det.detect()
    if not seen or det.resumers:
        bad.append(f"resume_with: {seen}, left {det.resumers}")
    with ix.resume_with(FakeDet(["home"]), lambda bare: seen.append("bare")):
        pass  # no-op on a bare detector

    # 6. LoopStop reaches the runner's readout
    det = ix.InterruptingDetector(FakeDet(["popup"]), None, table([], stop="needs_decision"), "Test")
    loop = Loop("test", "Test", "fake", lambda ctx, opts: ctx.det.detect() and "done")
    from sxs.core import records
    records.log_run = lambda readout, code: None  # keep logs/ untouched
    code = finish(loop, Ctx(None, det, None), argparse.Namespace(stall=30), 30, time.monotonic())
    if code != 1:
        bad.append(f"LoopStop exit code {code}")

    # 7. the tutorial row against the reference screens
    from sxs.actions.interrupts import TABLE
    from sxs.core.screens import reference_screens
    row = next(i for i in TABLE if i.name == "tutorial")
    expected = json.loads((ROOT / "docs/screens/expected.json").read_text())["states"]
    checked = 0
    for path in reference_screens():
        state = expected.get(path.stem)
        if state not in row.states:
            continue
        frame = cv2.imread(str(path))
        if frame is None or frame.shape[:2] != (1280, 720):
            continue
        checked += 1
        fires = row.matches(SimpleNamespace(state=state), frame)
        if fires != (path.stem in TUTORIAL_FRAMES):
            bad.append(f"tutorial row {'fires' if fires else 'misses'} on {path.relative_to(ROOT)} ({state})")
    for name in sorted(TUTORIAL_FRAMES - {p.stem for p in reference_screens()}):
        bad.append(f"tutorial reference screen {name}.png missing")
    if checked < 10:
        bad.append(f"only {checked} reference screens in the tutorial row's states")

    for b in bad:
        print("FAIL", b)
    print(f"interrupts: {'FAIL' if bad else 'ok'} ({checked} reference screens in watched states)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
