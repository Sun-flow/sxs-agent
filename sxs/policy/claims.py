"""Press free claim buttons on the screen that is showing, and nothing else.

A claim is a button whose whole text is Claim / Claim All / Collect / Receive. Anything that looks like spending
(mae's rule: Pray, Buy, Purchase, Refresh, Spend, Dawnium, Recharge, Top up, prices, Catch Up, draws) is never
tapped, and a claim button with a spend word on the same row is skipped too. No model calls.
"""

from __future__ import annotations

import logging
import re
from typing import Optional
import time

from ..core.loop import progress

from ..core import ui
from ..core.device import Device
from ..core.state import StateDetector

log = logging.getLogger("sxs.policy.claims")

CLAIM = re.compile(r"(Claim|Claim All|Collect|Collect All|Receive)", re.I)
SPEND = re.compile(r"Pray|Buy|Purchase|Refresh|Spend|Dawnium|Recharge|Top ?up|USD|\$|Catch ?Up|Draw|Advanced", re.I)
FULL = [0, 90, 720, 1090]  # below the currency bar, above the bottom bar


def claim_buttons(det: StateDetector, roi=FULL, spend_dx: Optional[int] = None) -> list[tuple[int, int]]:
    """Centres of safe claim buttons on the current frame, top to bottom. A claim on the same row as a spend word is
    skipped; `spend_dx` narrows "same row" to spend words within that many px sideways, for grids of separate
    tiles (Daily Sign-in: day 01's "Catch Up" must not block day 03's "Claim" on the same row)."""
    texts = det.read_text(roi)
    spend_rows = [(b[0] + b[2] // 2, b[1] + b[3] // 2) for t, b in texts if SPEND.search(t)]
    out = []
    for t, (x, y, w, h) in texts:
        if not CLAIM.fullmatch(t.strip()):
            continue
        cy = y + h // 2
        cx = x + w // 2
        if any(abs(cy - ry) < 45 and (spend_dx is None or abs(cx - rx) < spend_dx) for rx, ry in spend_rows):
            log.info("skipping %r at %d,%d: spend word on the same row", t, x, y)
            continue
        out.append((x + w // 2, cy))
    return sorted(out, key=lambda p: p[1])


def claim_all(dev: Device, det: StateDetector, roi=FULL, max_taps: int = 15, home_state: str = None,
              spend_dx: Optional[int] = None) -> int:
    """Tap claim buttons one at a time, closing the reward popup after each, until none are left. Stops early if a
    tap changes nothing twice in a row (stuck check). Returns the number of claims."""
    claimed = misses = 0
    last = None
    for _ in range(max_taps):
        buttons = claim_buttons(det, roi, spend_dx)
        if not buttons:
            break
        if buttons[0] == last:
            misses += 1
            if misses >= 2:
                log.warning("claim at %s does nothing; stopping", last)
                break
        else:
            misses = 0
        last = buttons[0]
        dev.tap(*buttons[0])
        time.sleep(2)
        claimed += 1
        progress(("claimed", buttons[0], claimed))
        for _ in range(3):  # close "YOU RECEIVED" and similar popups
            s = det.detect().state
            if s not in ("reward_popup", "tap_to_continue"):
                break
            dev.tap(*ui.REWARD_CLOSE if s == "reward_popup" else (360, 1150))
            time.sleep(1.5)
        if home_state and det.detect().state != home_state:
            log.info("claim left %s; stopping", home_state)
            break
    if claimed:
        log.info("claimed %d", claimed)
    return claimed
