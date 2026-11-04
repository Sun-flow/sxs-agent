"""Every loop in the registry meets the loop contract (sxs/core/loop.py), offline, no emulator.

    python tests/check_loops.py

Checks: each module imports and exposes LOOP with the registered name, a title and a summary; its option parser
builds and parses a minimal command line; `as_result` maps str / dict / None the same way for every loop; and the pray
loop refuses (exit 2) without --pulls N --handler-approved or with a pull count that isn't a multiple of 10,
before it touches the device.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sxs.core.loop import REFUSED, Ctx, Result, as_result  # noqa: E402
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

    for b in bad:
        print("FAIL", b)
    print(f"{len(REGISTRY)} loops checked, {len(bad)} problems")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
