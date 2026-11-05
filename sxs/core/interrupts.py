"""Interrupts: screens that pause whatever loop is running, get a short handler, then hand the loop back (mae,
2026-11-05: "transition between tasks, like explore and tutorial, when the detector sees a state change").

Every loop asks the detector "where am I" before it acts. The runner gives loops an `InterruptingDetector` instead
of the bare `StateDetector`: after each screen check it walks one priority table of `Interrupt`s (the table lives in
`sxs/actions/interrupts.py`, the only place screens like Choose Your Reward or a tutorial highlight are handled). When
one matches, the loop is paused where it stands (it is simply waiting inside its `detect()` call), the handler runs,
the screen is checked again, and the loop gets that fresh detection. The loop's goal, area and counters are its own
locals, so nothing has to be saved or rebuilt.

    [Interrupt] tutorial highlight on world_map: pausing Fog Walk
    [Resume Fog Walk] after tutorial: done (14 s)

Rules
- A handler runs under its own `task()` budget and reports progress, so a long tutorial doesn't trip the loop's
  stall check, and a stuck handler is cut and the loop carries on.
- A handler returns `RESUME` (carry on), `MUTE` (didn't work here: ignore this interrupt for MUTE_S) or raises
  `LoopStop(status)` when it needs mae (a spend prompt, a reward choice the rules don't settle). LoopStop is a
  BaseException so a loop's `except Exception` can't swallow it; the runner turns it into the run's status.
- An interrupt that fires more than BURST times in BURST_S seconds is muted for MUTE_S: a false match can't trap a loop.
- A loop that handles a screen itself names it in `Loop.owns` (the tutorial loop owns "tutorial"), or wraps a block in
  `with det.owning("name"):`.
- When a handler may leave the game somewhere else, a loop can register `with resume_with(det, fn):`; fn runs after
  every handler (bounded by the handler's budget) to put the loop back where its goal is, e.g. Fog Walk walks back to
  its area. It runs under its own RESUME_S budget.
- The unknown state stays explicit: no table entry matches `unknown` by itself.

Handlers get the bare detector, so nothing they do triggers another interrupt.
"""

from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Iterator, Optional

from .loop import progress, task

log = logging.getLogger("sxs.interrupts")

RESUME, MUTE = "resume", "mute"
BURST, BURST_S = 5, 90.0  # more than BURST firings in BURST_S seconds: mute it
MUTE_S = 120.0
RESUME_S = 90.0  # a loop's resume step (walking back to its area) gets its own budget


class LoopStop(BaseException):
    """Raised by a handler to end the current loop with `status` (it needs mae). Caught by the runner."""

    def __init__(self, status: str, **data: Any):
        super().__init__(status)
        self.status, self.data = status, data


@dataclass
class Interrupt:
    """One row of the table.

    name     short id, used in logs, `Loop.owns` and `owning()`
    states   detector states this interrupt can fire on
    handler  handler(dev, det, detection) -> RESUME | MUTE (or raises LoopStop). `det` is the bare detector.
    when     optional extra test on the frame the detector just used: when(frame, detection) -> bool. For overlays
             that aren't a state of their own (the tutorial highlight sits on top of the island map).
    budget   seconds the handler may take; its stall limit is half that
    """
    name: str
    states: frozenset
    handler: Callable[..., str]
    when: Optional[Callable[[Any, Any], bool]] = None
    budget: float = 30.0
    label: str = ""

    def matches(self, d, frame) -> bool:
        if d.state not in self.states:
            return False
        return self.when is None or (frame is not None and bool(self.when(frame, d)))


@dataclass
class _Record:
    fired: list = field(default_factory=list)  # monotonic times
    muted_until: float = 0.0


class InterruptingDetector:
    """Quacks like StateDetector. `detect()` and `wait_for()` run the interrupt table; everything else (find,
    read_text, ...) goes straight to the bare detector."""

    def __init__(self, det, dev, table: list[Interrupt], loop_title: str = "", owns: frozenset = frozenset()):
        self.raw, self.dev, self.table = det, dev, list(table)
        self.loop_title = loop_title or "loop"
        self.owned: list[str] = list(owns)
        self.records = {i.name: _Record() for i in self.table}
        self.resumers: list[Callable[[Any], None]] = []
        self.handled: list[dict] = []  # what ran, for the run's readout
        self._busy = False

    def __getattr__(self, name):
        return getattr(self.raw, name)

    # --- the hook ---

    def detect(self):
        d = self.raw.detect()
        if self._busy:
            return d
        for _ in range(3):  # a handler can uncover another interrupt (a reward behind the tutorial); bounded
            hit = self._match(d)
            if hit is None:
                return d
            self._run(hit, d)
            d = self.raw.detect()
        return d

    def wait_for(self, states: set[str], timeout: float, interval: float = 1.0):
        deadline = time.monotonic() + timeout
        while True:
            d = self.detect()
            if d.state in states or time.monotonic() >= deadline:
                return d
            time.sleep(interval)

    @contextmanager
    def owning(self, *names: str) -> Iterator[None]:
        """The block handles these interrupts itself."""
        self.owned.extend(names)
        try:
            yield
        finally:
            for n in names:
                self.owned.remove(n)

    # --- internals ---

    def _match(self, d) -> Optional[Interrupt]:
        now = time.monotonic()
        frame = getattr(self.raw, "last_frame", None)
        for i in self.table:
            if i.name in self.owned or self.records[i.name].muted_until > now:
                continue
            if i.matches(d, frame):
                return i
        return None

    def _run(self, i: Interrupt, d) -> None:
        rec = self.records[i.name]
        now = time.monotonic()
        rec.fired = [t for t in rec.fired if now - t < BURST_S] + [now]
        if len(rec.fired) > BURST:
            rec.muted_until, rec.fired = now + MUTE_S, []
            log.warning("[Interrupt] %s fired %d times in %.0f s without clearing; ignoring it for %.0f s",
                        i.name, BURST, BURST_S, MUTE_S)
            return
        log.info("[Interrupt] %s on %s: pausing %s", i.label or i.name, d.state, self.loop_title)
        progress(("interrupt", i.name, now))  # the loop isn't stuck: it's waiting on a handler
        self._busy = True
        t0 = time.monotonic()
        outcome = "?"
        try:
            with task(f"{i.name} handler", i.budget, max(10.0, i.budget / 2)) as w:
                outcome = i.handler(self.dev, self.raw, d) or RESUME
            if w.status:
                outcome = w.status
            if self.resumers:
                with task(f"resume {self.loop_title}", RESUME_S, RESUME_S / 2) as r:
                    for fn in list(self.resumers):
                        fn(self.raw)
                if r.status:
                    log.warning("[Resume %s] getting back after %s: %s", self.loop_title, i.name, r.status)
        finally:
            self._busy = False
        if outcome == MUTE:
            rec.muted_until = time.monotonic() + MUTE_S
        progress(("interrupt", i.name, "done", time.monotonic()))
        took = time.monotonic() - t0
        self.handled.append({"interrupt": i.name, "on": d.state, "outcome": outcome, "seconds": round(took)})
        log.info("[Resume %s] after %s: %s (%.0f s)", self.loop_title, i.name, outcome, took)


@contextmanager
def resume_with(det, fn: Callable[[Any], None]) -> Iterator[None]:
    """Register fn(bare_detector) to run after any interrupt handler while the block runs, to get the loop back to
    where its goal is. A no-op on a bare detector (offline tools, scripts)."""
    resumers = getattr(det, "resumers", None)
    if resumers is None:
        yield
        return
    resumers.append(fn)
    try:
        yield
    finally:
        resumers.remove(fn)


def wrap(det, dev, loop_title: str = "", owns=frozenset()):
    """The detector loops get from the runner: the bare one wrapped with the interrupt table."""
    from ..actions.interrupts import TABLE  # actions know the game; core only knows the mechanism
    return InterruptingDetector(det, dev, TABLE, loop_title, frozenset(owns))
