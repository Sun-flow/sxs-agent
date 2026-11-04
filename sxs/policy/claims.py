"""Press free claim buttons on the screen that is showing, and nothing else.

A claim is a button whose whole text is Claim / Claim All / Collect / Receive. Anything that looks like spending
(mae's rule: Pray, Buy, Purchase, Refresh, Spend, Dawnium, Recharge, Top up, prices, Catch Up, draws) is never
tapped, and a claim button with a spend word on the same row is skipped too. No model calls.
"""

from __future__ import annotations

import logging
import re
import time

from ..core import ui
from ..core.device import Device
from ..core.state import StateDetector

log = logging.getLogger("sxs.policy.claims")

CLAIM = re.compile(r"(Claim|Claim All|Collect|Collect All|Receive)", re.I)
SPEND = re.compile(r"Pray|Buy|Purchase|Refresh|Spend|Dawnium|Recharge|Top ?up|USD|\$|Catch ?Up|Draw|Advanced", re.I)
FULL = [0, 90, 720, 1090]  # below the currency bar, above the bottom bar


def claim_buttons(det: StateDetector, roi=FULL) -> list[tuple[int, int]]:
    """Centres of safe claim buttons on the current frame, top to bottom."""
    texts = det.read_text(roi)
    spend_rows = [b[1] + b[3] // 2 for t, b in texts if SPEND.search(t)]
    out = []
    for t, (x, y, w, h) in texts:
        if not CLAIM.fullmatch(t.strip()):
            continue
        cy = y + h // 2
        if any(abs(cy - r) < 45 for r in spend_rows):
            log.info("skipping %r at %d,%d: spend word on the same row", t, x, y)
            continue
        out.append((x + w // 2, cy))
    return sorted(out, key=lambda p: p[1])


def claim_all(dev: Device, det: StateDetector, roi=FULL, max_taps: int = 15, home_state: str = None) -> int:
    """Tap claim buttons one at a time, closing the reward popup after each, until none are left. Stops early if a
    tap changes nothing twice in a row (stuck check). Returns the number of claims."""
    claimed = misses = 0
    last = None
    for _ in range(max_taps):
        buttons = claim_buttons(det, roi)
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
