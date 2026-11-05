"""Every loop in the registry meets the loop contract (sxs/core/loop.py), offline, no emulator.

    python tests/check_loops.py

Checks: each module imports and exposes LOOP with the registered name, a title and a summary; its option parser
builds and parses a minimal command line; `as_result` maps str / dict / None the same way for every loop; and the pray
loop refuses (exit 2) without --pulls N --handler-approved or with a pull count that isn't a multiple of 10,
before it touches the device. Also checks the time budget and stall watchdog (`task`, `progress`) stop a block
and let the code after it carry on (about 4 seconds).
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sxs.core.loop import OVER_BUDGET, REFUSED, STALLED, Ctx, Result, as_result, progress, task  # noqa: E402
from sxs.loops import REGISTRY, get  # noqa: E402


MINIMAL_ARGV = {"goto": ["Highland Woods"]}  # loops with required positionals


class NoDevice:
    """Fails the check if a refused run reaches the device."""

    def __getattr__(self, name):
        raise AssertionError(f"refused run touched the device ({name})")


def main() -> int:
    bad = []
    for name in REGISTRY:
        try:
            loop = get(name)
            assert loop.title and loop.summary, "missing title or summary"
            p = argparse.ArgumentParser()
            if loop.args:
                loop.args(p)
            p.parse_args(MINIMAL_ARGV.get(name, []))
        except Exception as e:
            bad.append(f"{name}: {e}")
    r = as_result({"end": "complete", "n": 3}, {"complete"})
    if (r.status, r.ok, r.data) != ("complete", True, {"n": 3}):
        bad.append(f"as_result dict: {r}")
    if as_result("timeout", {"done"}).ok or as_result(None, {"done"}).status != "done":
        bad.append("as_result str/None")
    if not isinstance(as_result(Result("x", True), set()), Result):
        bad.append("as_result Result")

    pray = get("pray")
    ctx = Ctx(NoDevice(), NoDevice(), None)
    for argv in ([], ["--pulls", "10"], ["--pulls", "15", "--handler-approved"]):
        p = argparse.ArgumentParser()
        pray.args(p)
        status = as_result(pray.run(ctx, p.parse_args(argv)), pray.ok).status
        if not status.startswith(REFUSED):
            bad.append(f"pray {argv}: not refused ({status})")

    with task("budget check", 1) as w:
        while True:
            time.sleep(0.1)
    if w.status != OVER_BUDGET:
        bad.append(f"task budget: {w.status}")
    with task("stall check", 30, stall=1) as w:
        progress(1)
        while True:
            progress(1)  # the same reading again is not progress
            time.sleep(0.1)
    if w.status != STALLED:
        bad.append(f"task stall: {w.status}")
    # The budget is a stuck check (mae): progress keeps a run going past it; once progress stops, it ends.
    t0 = time.monotonic()
    with task("extension check", 1, stall=2) as w:
        i = 0
        while True:
            i += 1
            progress(i)
            time.sleep(0.2)
            if time.monotonic() - t0 > 2.5:
                break  # still moving after 2.5 budgets' worth: the budget extended
        while True:
            time.sleep(0.1)  # now no progress: the next budget check (or the stall check) ends it
    if w.status not in (OVER_BUDGET, STALLED) or w.extensions < 2:
        bad.append(f"task extension: {w.status}, {w.extensions} extensions")
    with task("quick", 5) as w:
        progress("a")
    if w.status is not None:
        bad.append(f"task quick: {w.status}")

    for b in bad:
        print("FAIL", b)
    print(f"{len(REGISTRY)} loops checked, {len(bad)} problems")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
