"""The loop contract: every loop has the same inputs, outputs and readouts (mae, 2026-11-04).

Inputs    a `Loop` spec: name, title, one-line summary, its own command-line options (`args`), and `run(ctx, opts)`.
          `ctx` carries the device, the state detector and the navigator, so no loop builds its own.
Outputs   `run` returns a `Result`: `status` (a machine-readable end reason such as "done", "timeout",
          "unknown_screen"), `ok` (did it end the way it should), and `data` (loop-specific counts and readings).
          A plain string or dict is accepted and converted (see `as_result`), so inner helpers can keep simple returns.
Readouts  when it starts, the loop prints mae's banner ([Running X Loop] / [Goal] / [End condition]) via `banner`.
          When it ends, the runner logs `[Result X] status` and prints one JSON line to stdout:
          {"loop": "explore", "status": "complete", "ok": true, "seconds": 812, ...data}.
          Exit code: 0 ok, 1 stopped for a reason that needs a look, 2 refused (bad or unauthorised input).

Run any loop with `python -m sxs <name> [options]`; `python -m sxs --help` lists them.
"""

from __future__ import annotations

import argparse
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

log = logging.getLogger("sxs.loop")

LOG_FORMAT = "%(asctime)s %(message)s"
REFUSED = "refused"


@dataclass
class Result:
    status: str
    ok: bool
    data: dict = field(default_factory=dict)

    def readout(self, loop: str, seconds: float) -> dict:
        return {"loop": loop, "status": self.status, "ok": self.ok, "seconds": round(seconds), **self.data}


def as_result(raw: Any, ok_statuses: set[str]) -> Result:
    """Normalise what a loop returned. str -> that status. dict -> its "end" or "status" key (else "done"), the
    rest as data. A Result passes through."""
    if isinstance(raw, Result):
        return raw
    if isinstance(raw, str):
        return Result(raw, raw in ok_statuses)
    if isinstance(raw, dict):
        data = dict(raw)
        status = str(data.pop("end", None) or data.pop("status", None) or "done")
        return Result(status, status in ok_statuses, data)
    if raw is None:
        return Result("done", "done" in ok_statuses)
    return Result(str(raw), str(raw) in ok_statuses)


@dataclass
class Ctx:
    """What every loop gets: the device, the detector and a navigator, built once per run."""
    dev: Any
    det: Any
    nav: Any


@dataclass
class Loop:
    name: str  # command name: python -m sxs <name>
    title: str  # banner name: [Running <title> Loop]
    summary: str  # one line for --help
    run: Callable[[Ctx, argparse.Namespace], Any]
    args: Optional[Callable[[argparse.ArgumentParser], None]] = None
    ok: set[str] = field(default_factory=lambda: {"done", "nothing"})
    needs_detector: bool = True


def banner(logger, name: str, goal: str, end: str) -> None:
    """mae's loop banner (2026-11-04), logged when a loop starts so a watcher can see what it's for and when it
    stops: [Running X Loop] / [Goal: ...] / [End condition: ...]."""
    for line in (f"[Running {name} Loop]", f"[Goal: {goal}]", f"[End condition: {end}]"):
        logger.info(line)


def connect(address: Optional[str] = None, detector: bool = True) -> Ctx:
    from .device import DEFAULT_ADDRESS, Device
    from .nav import Navigator
    from .state import StateDetector

    dev = Device(address or DEFAULT_ADDRESS)
    det = StateDetector(dev) if detector else None
    return Ctx(dev, det, Navigator(dev, det) if det else None)


def run_cli(loop: Loop, argv: Optional[list[str]] = None, address: Optional[str] = None) -> int:
    """Parse the loop's options, connect, run it, print the readout. Returns the exit code."""
    p = argparse.ArgumentParser(prog=f"python -m sxs {loop.name}", description=loop.summary)
    if loop.args:
        loop.args(p)
    opts = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt="%H:%M:%S")
    t0 = time.monotonic()
    ctx = connect(address, loop.needs_detector)
    result = as_result(loop.run(ctx, opts), loop.ok)
    readout = result.readout(loop.name, time.monotonic() - t0)
    log.info("[Result %s] %s%s", loop.title, result.status, "" if result.ok else " (needs a look)")
    print(json.dumps(readout, default=str), flush=True)
    if result.status.startswith(REFUSED):
        return 2
    return 0 if result.ok else 1
