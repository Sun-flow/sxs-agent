""""Choose Your Reward": the skill pick after clearing a Realm / mini-dungeon (seen 2026-11-05, Temple Ruins).

Two skill cards, one radio circle under each, OK below. R-129 (mae, 2026-11-05, on by default): when exactly one
card is marked "Class Mismatch", take the other (the skill our class can use); when both are usable (or both
mismatch), stop and ask. AUTO_PICK = False makes it always ask. Screen: docs/screens/dialogs/choose_reward_skill.png. No model calls.
"""

from __future__ import annotations

import logging
import time

from ..core import ui
from ..core.device import save_unknown

log = logging.getLogger("sxs.actions.choose_reward")

CARD_ROIS = [[190, 480, 170, 330], [370, 480, 170, 330]]  # left and right skill cards
RADIOS = [(276, 765), (450, 765)]
OK = (360, 993)
AUTO_PICK = True  # R-129 (mae, 2026-11-05: on by default): class-matched pick when exactly one is a mismatch


def options(det, frame=None) -> list[tuple[str, bool]]:
    """(skill name, usable) per card; usable is False when the card says Class Mismatch."""
    out = []
    for roi in CARD_ROIS:
        lines = [t for t, _ in det.read_text(roi, frame)]
        mismatch = any("mismatch" in t.lower() for t in lines)
        name = next((t for t in reversed(lines) if t.strip() and "class" not in t.lower()
                     and "mismatch" not in t.lower() and not t.strip().isdigit()), "?")
        out.append((name, not mismatch))
    return out


def choose(dev, det) -> str:
    """Pick by mae's rule. Returns "chosen" or "needs_decision" (nothing tapped)."""
    opts = options(det)
    usable = [i for i, (_, ok) in enumerate(opts) if ok]
    log.info("reward choice: %s", opts)
    if not AUTO_PICK or len(usable) != 1:
        log.warning("reward choice needs mae: %s; frame %s", opts, save_unknown(dev, "choose_reward"))
        return "needs_decision"
    i = usable[0]
    log.info("taking %s (the other card is a class mismatch)", opts[i][0])
    ui.tap(dev, RADIOS[i], 1)
    ui.tap(dev, OK, 2.5)
    time.sleep(0.5)
    return "chosen"
