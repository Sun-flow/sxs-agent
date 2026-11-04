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
Time      loops run briefly (mae, 2026-11-04: 1-2 minutes, never 10+). Every run has a budget (`Loop.budget`,
          `--budget SECONDS`) and ends "over_budget" when it passes it. A loop that reports progress with
          `progress(what)` also ends "stalled" when nothing has moved for `--stall` seconds, instead of bashing
          into the same obstacle. Inside a loop, `with task(name, seconds) as t:` gives one step its own budget
          and stall limit: the step stops, `t.status` says why, and the loop carries on with the next step.

Run any loop with `python -m sxs <name> [options]`; `python -m sxs --help` lists them.
"""

from __future__ import annotations

import _thread
import argparse
import json
import logging
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Iterator, Optional

log = logging.getLogger("sxs.loop")

LOG_FORMAT = "%(asctime)s %(message)s"
REFUSED = "refused"
OVER_BUDGET, STALLED, INTERRUPTED = "over_budget", "stalled", "interrupted"
DEFAULT_BUDGET_S = 120  # mae, 2026-11-04: 1-2 minutes per loop
DEFAULT_STALL_S = 60  # no progress for this long = stuck: stop and report instead of retrying
GRACE_S = 15  # a loop with its own timer gets this long to stop cleanly before the runner stops it


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
    budget: float = DEFAULT_BUDGET_S  # seconds; override per run with --budget


# --- time budget and progress watchdog -----------------------------------------------------------------------------

class _Watch:
    """One budget: a deadline, the last progress report, and why it fired (if it did)."""

    def __init__(self, name: str, budget: float, stall: float):
        now = time.monotonic()
        self.name, self.deadline, self.stall = name, now + budget, stall
        self.progress_at: Optional[float] = None  # None until the code reports progress at least once
        self.progress_what: Optional[str] = None
        self.status: Optional[str] = None  # OVER_BUDGET / STALLED once fired

    def due(self, now: float) -> Optional[str]:
        if now >= self.deadline:
            return OVER_BUDGET
        if self.progress_at is not None and now - self.progress_at >= self.stall:
            return STALLED
        return None


_watches: list[_Watch] = []
_lock = threading.Lock()
_fired: Optional[_Watch] = None
_ticker: Optional[threading.Thread] = None


def _tick() -> None:
    global _fired
    while True:
        time.sleep(0.5)
        with _lock:
            if _fired is None:
                now = time.monotonic()
                for w in reversed(_watches):  # innermost first
                    why = w.due(now)
                    if why:
                        w.status, _fired = why, w
                        log.warning("[%s] %s: stopping it (%s)", w.name, why, _detail(w, now))
                        _thread.interrupt_main()
                        break


def _detail(w: _Watch, now: float) -> str:
    if w.status == STALLED:
        return f"no progress for {now - w.progress_at:.0f} s; last: {w.progress_what}"
    return "time budget used up"


@contextmanager
def task(name: str, budget: float = DEFAULT_BUDGET_S, stall: float = DEFAULT_STALL_S) -> Iterator[_Watch]:
    """Give a block its own time budget and stall limit. If either fires, the block is stopped (an exception raised
    wherever it is, usually during a sleep or a screenshot) and `watch.status` is OVER_BUDGET or STALLED; the code
    after the `with` carries on. Runs only in the main thread."""
    global _ticker, _fired
    w = _Watch(name, budget, stall)
    with _lock:
        _watches.append(w)
        if _ticker is None:
            _ticker = threading.Thread(target=_tick, name="sxs-watchdog", daemon=True)
            _ticker.start()
    caught = False
    try:
        yield w
    except KeyboardInterrupt:
        caught = True
        with _lock:
            mine, outer = _fired is w, _fired is not None and _fired is not w
            if mine:
                _fired = None
        if not mine:
            if outer:
                raise  # an outer budget fired: let it reach its own `with`
            w.status = INTERRUPTED  # Ctrl+C from a person
            raise
    finally:
        with _lock:
            if w in _watches:
                _watches.remove(w)
            late = _fired is w  # fired just as the block finished; its interrupt is still on its way
            if late:
                _fired = None
        if late and not caught:
            try:
                time.sleep(1)  # absorb it here rather than in whatever runs next
            except KeyboardInterrupt:
                pass


def progress(what: Any = None) -> None:
    """Report where the current loop or task stands (a tracker reading, map coordinates, a pickup count). Only a
    change counts as progress. The first call arms the stall check: no change for --stall seconds ends the run (or
    the task) as "stalled". Loops that never call it are only bound by their time budget."""
    now = time.monotonic()
    with _lock:
        for w in _watches:
            if w.progress_what != what or w.progress_at is None:
                w.progress_at, w.progress_what = now, what


def seconds_left() -> Optional[float]:
    """Time left in the innermost budget, so a loop can skip starting something it can't finish."""
    with _lock:
        if not _watches:
            return None
        return min(w.deadline for w in _watches) - time.monotonic()


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


def _go_home(ctx: Ctx) -> None:
    """After a stopped run, try to leave the game on home for the next loop (bounded, best effort)."""
    if not ctx.nav:
        return
    with task("go home after stop", 45, 45) as w:
        try:
            ctx.nav.go_home()
        except Exception as e:  # noqa: BLE001
            log.warning("could not get home after the stop: %s", e)
    if w.status:
        log.warning("could not get home after the stop (%s)", w.status)


def run_cli(loop: Loop, argv: Optional[list[str]] = None, address: Optional[str] = None) -> int:
    """Parse the loop's options, connect, run it, print the readout. Returns the exit code."""
    p = argparse.ArgumentParser(prog=f"python -m sxs {loop.name}", description=loop.summary)
    if loop.args:
        loop.args(p)
    p.add_argument("--budget", type=float, default=None,
                   help=f"stop after this many seconds (default {loop.budget:g}; a --minutes option adds to it)")
    p.add_argument("--stall", type=float, default=DEFAULT_STALL_S,
                   help="stop when the loop reports no progress for this many seconds")
    opts = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt="%H:%M:%S")
    budget = opts.budget
    if budget is None:
        own = getattr(opts, "minutes", None)  # a loop with its own timer stops itself; the runner is the backstop
        budget = max(loop.budget, own * 60 + GRACE_S) if own else loop.budget
    t0 = time.monotonic()
    ctx = connect(address, loop.needs_detector)
    with task(loop.title, budget, opts.stall) as watch:
        raw = loop.run(ctx, opts)
    if watch.status:
        result = Result(watch.status, False, {"budget_s": round(budget), "last_progress": watch.progress_what})
        _go_home(ctx)
    else:
        result = as_result(raw, loop.ok)
    readout = result.readout(loop.name, time.monotonic() - t0)
    log.info("[Result %s] %s%s", loop.title, result.status, "" if result.ok else " (needs a look)")
    print(json.dumps(readout, default=str), flush=True)
    if result.status.startswith(REFUSED):
        return 2
    return 0 if result.ok else 1
