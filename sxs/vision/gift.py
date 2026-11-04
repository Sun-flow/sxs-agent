"""Find a finished quest's reward gift on the tracker panel. No taps, no model calls.

When a tracked quest is done, the right end of the tracker panel (lower left of the island map, above the chat)
shows a yellow gift box with a red "!" badge above its right corner. mae, 2026-11-04: in the general exploration
loops, tap it when both are there, close the reward card and carry on. Reference: mae's crop
`docs/screens/icons/reward_gift_box_mae.png`; template `resource/image/explore/reward_gift.png` (the gift on the
dark panel, 36x36). It also matches the olive "finished" panel (`docs/screens/world/world_map_tracker_gift.png`).

The "!" pulses between red and a dull orange-brown, so the badge check is looser than `badges.find_badges`: warm
pixels in a disc with a white upright mark, in the box above and right of the gift (seen 21 px right, 69 px up).

    python -m sxs see gift [frame.png ...]     # report the gift and badge on frames (default: a live screenshot)
"""

from __future__ import annotations

from typing import Optional

import cv2
import numpy as np

from ..core.paths import RESOURCE

TEMPLATE = RESOURCE / "image" / "explore" / "reward_gift.png"
ROI = (0, 860, 520, 220)  # x, y, w, h: the tracker panel strip (same as Explore.TrackerGift, a little taller)
THRESHOLD = 0.8  # 0.83 to 0.91 on the tracker screens in docs/screens, under 0.75 elsewhere
BADGE_BOX = (-20, -110, 90, 110)  # badge search box relative to the gift centre: dx, dy, w, h

_tpl: Optional[np.ndarray] = None


def _template() -> np.ndarray:
    global _tpl
    if _tpl is None:
        _tpl = cv2.imread(str(TEMPLATE))
    return _tpl


def find_gift(frame: np.ndarray) -> Optional[tuple[int, int]]:
    """Centre of the tracker gift box, or None."""
    x0, y0, w, h = ROI
    tpl = _template()
    roi = frame[y0:y0 + h, x0:x0 + w]
    if roi.shape[0] < tpl.shape[0] or roi.shape[1] < tpl.shape[1]:
        return None  # not a 720x1280 game frame
    r = cv2.matchTemplate(roi, tpl, cv2.TM_CCOEFF_NORMED)
    _, score, _, (x, y) = cv2.minMaxLoc(r)
    if score < THRESHOLD:
        return None
    th, tw = tpl.shape[:2]
    return x0 + x + tw // 2, y0 + y + th // 2


def has_badge(frame: np.ndarray, gift: tuple[int, int]) -> bool:
    """A "!" badge (red or its dull pulse colour) in the box above and right of the gift."""
    dx, dy, w, h = BADGE_BOX
    x, y = max(0, gift[0] + dx), max(0, gift[1] + dy)
    hsv = cv2.cvtColor(frame[y:y + h, x:x + w], cv2.COLOR_BGR2HSV)
    hh, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    warm = (((hh >= 165) | (hh <= 20)) & (s >= 70) & (v >= 120)).astype(np.uint8)
    white = (s < 70) & (v > 200)
    n, _, stats, _ = cv2.connectedComponentsWithStats(warm, 8)
    for i in range(1, n):
        bx, by, bw, bh, area = stats[i]
        if not (14 <= bw <= 40 and 14 <= bh <= 40) or max(bw, bh) / max(1, min(bw, bh)) > 1.4:
            continue
        if area < 0.4 * bw * bh:
            continue
        ys, xs = np.nonzero(white[by:by + bh, bx:bx + bw])
        if len(xs) >= 6 and xs.max() - xs.min() + 1 <= 0.45 * bw and ys.max() - ys.min() + 1 >= 0.4 * bh:
            return True
    return False


def find_reward(frame: np.ndarray) -> Optional[tuple[int, int]]:
    """Tap point of a claimable tracker reward (gift and "!" both showing), or None."""
    gift = find_gift(frame)
    return gift if gift and has_badge(frame, gift) else None


def main(argv: list[str]) -> int:
    if argv:
        frames = [(p, cv2.imread(p)) for p in argv]
    else:
        from ..core.device import Device
        frames = [("live", Device().screenshot())]
    for name, frame in frames:
        gift = find_gift(frame)
        print(name, "gift", gift, "badge", bool(gift and has_badge(frame, gift)))
    return 0
