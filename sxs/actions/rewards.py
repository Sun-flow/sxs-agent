"""Claim a finished quest's reward from the tracker panel while exploring (mae, 2026-11-04): when the tracker shows
the gift with a red "!", tap it, close the reward card and carry on. Detection: `sxs.vision.gift`. No model calls."""

from __future__ import annotations

import logging
import time
from typing import Optional

import numpy as np

from ..core import ui
from ..vision.gift import find_reward

log = logging.getLogger("sxs.actions.rewards")

CLOSE_TRIES = 4


def claim_tracker_reward(dev, det, frame: Optional[np.ndarray] = None) -> bool:
    """If the tracker shows a claimable gift, tap it and close the reward card(s). True if it tapped."""
    frame = dev.screenshot() if frame is None else frame
    point = find_reward(frame)
    if point is None:
        return False
    log.info("tracker reward ready (gift and '!' at %s): claiming", point)
    dev.tap(*point)
    time.sleep(2)
    for _ in range(CLOSE_TRIES):
        state = det.detect().state
        if state in ("reward_popup", "tap_to_continue"):
            dev.tap(*ui.REWARD_CLOSE)
        elif state == "dialogue":
            dev.tap(*ui.DIALOGUE_NEXT)
        else:
            break
        time.sleep(1.5)
    return True
