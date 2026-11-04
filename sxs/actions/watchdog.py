"""Stuck checks shared by the long-running loops (mae, 2026-11-04: loops check for being stuck even when automated)."""

from __future__ import annotations

import logging
import time
from typing import Optional

from ..core.loop import progress

log = logging.getLogger("sxs.watchdog")

HEARTBEAT_S = 30  # liveness log line and stuck check interval
BUSY_STATES = ("battle", "loading", "background_fight")  # waiting here is not being stuck
BUSY_TICK_S = 20


class Heartbeat:
    """Regular liveness check for long runs (mae, 2026-11-04: loops check for being stuck even when automated).
    Logs a line every HEARTBEAT_S with screen, map coordinates and time since progress, and warns when the screen
    and coordinates haven't changed at all for several beats, so a log shows at a glance where a loop idles."""

    def __init__(self) -> None:
        self.next_at = time.monotonic() + HEARTBEAT_S
        self.last = None
        self.same = 0

    def check(self, d, progress_text: Optional[str], progress_at: float) -> None:
        # Tell the runner's stall check where we are: the tracker reading, the screen and the map coordinates.
        # A fight or a loading screen counts as moving (it ends by itself), so a long battle isn't "stalled".
        busy = int(time.monotonic() // BUSY_TICK_S) if d.state in BUSY_STATES else None
        progress((progress_text, d.state, d.text, busy))
        if time.monotonic() < self.next_at:
            return
        self.next_at = time.monotonic() + HEARTBEAT_S
        snap = (d.state, d.text)
        self.same = self.same + 1 if snap == self.last else 0
        self.last = snap
        log.info("heartbeat: %s %s | tracker %r | %ds since progress%s", d.state, d.text or "", progress_text,
                 time.monotonic() - progress_at, f" | unchanged x{self.same}" if self.same >= 2 else "")


class UnknownScreens:
    """Counts unfamiliar screens in a row (and in total, which catches unknown <-> map loops). `seen(state)` returns
    True when the loop should stop: mae's rule is flag, recover a bounded number of times, then end and report."""

    def __init__(self, in_a_row: int = 5, total: Optional[int] = None):
        self.in_a_row, self.total_limit = in_a_row, total
        self.streak = self.total = 0

    def seen(self, state: str) -> bool:
        if state != "unknown":
            self.streak = 0
            return False
        self.streak += 1
        self.total += 1
        return self.streak >= self.in_a_row or (self.total_limit is not None and self.total >= self.total_limit)
