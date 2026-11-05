"""Follow the game's own tutorial prompts: tap through dialogue and tap whatever the yellow highlight box frames.

    python -m sxs tutorial [--steps 40]

The tutorial marks the next thing to tap with a bright yellow rounded rectangle (docs/screens/dialogs/tutorial_highlight.png).
find_highlight() finds it by colour; no model calls. Stops when there is no dialogue, popup or highlight left.
"""

from __future__ import annotations

import re
import logging
import time
from typing import Optional

import cv2
import numpy as np

from ..core import ui
from ..core.device import Device
from ..core.state import StateDetector
from ..core.loop import Loop, progress
from ..vision.ocr import read_line

log = logging.getLogger("sxs.loops.tutorial")

# Highlight border colour in HSV (OpenCV ranges: H 0-179). Measured on live frames, not the 256-colour references.
HIGHLIGHT_LO = np.array([25, 100, 170])
HIGHLIGHT_HI = np.array([35, 255, 255])
GLOW_MAX_S, GLOW_MIN_V, GLOW_BAND_MIN = 40, 200, 0.35  # the white glow band inside a filled highlight
GLOW_STATES = ("companions",)  # screens whose tutorial highlight is the filled style
# The tutorial locks the Companions screen until Akane is invited. mae, 2026-11-05 02:23: inviting to parties and
# the social features are fine ("teaming up is an important part of this game"), so the follower taps Invite.
# False makes it stop there with "needs_decision" instead.
INVITE_COMPANIONS = True
HINT_TO_BUTTON_DY = 100
# Never tap a highlight whose text looks like spending: gacha pulls, shop buys, premium currency.
NEVER_TAP = r"Pray|Buy|Purchase|Refresh|Spend|Dawnium|Recharge|Top ?up"


def _glow_band(hsv_box: np.ndarray, b: int) -> bool:
    """The second highlight style (Companions "Invite", docs/screens/dialogs/companions_invite_tutorial.png): a yellow
    border with a white glow just inside it around a lime button. True when most of the band between the border
    and the button is near-white (low saturation, bright)."""
    h, w = hsv_box.shape[:2]
    lo, hi = max(2, b // 2), 2 * b
    if h <= 2 * hi or w <= 2 * hi:
        return False
    white = (hsv_box[..., 1] < GLOW_MAX_S) & (hsv_box[..., 2] > GLOW_MIN_V)
    band = np.zeros((h, w), bool)
    band[lo:h - lo, lo:w - lo] = True
    band[hi:h - hi, hi:w - hi] = False
    return white[band].mean() > GLOW_BAND_MIN


def find_highlight(frame: np.ndarray, glow: bool = False) -> Optional[tuple[int, int, int, int]]:
    """Box (x, y, w, h) of the largest yellow rounded-rectangle outline, or None.

    The border pulses and has gaps, so instead of looking for a closed shape this checks that the yellow pixels
    sit along the box's edges (not inside it, which rules out lime buttons, unless a white glow band separates
    the border from the button: the filled style on the Companions screen) and reach into its corners (which
    rules out round icons).

    glow=True also accepts the filled style. Only for screens in GLOW_STATES: furniture popups, the alchemy pot and
    the main menu have the same white-inside-yellow look and would match too."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, HIGHLIGHT_LO, HIGHLIGHT_HI)
    mask = cv2.dilate(mask, np.ones((5, 5), np.uint8))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    best = None
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if w < 40 or h < 30:
            continue
        if max(w, h) < 85 and abs(w - h) < 8:
            continue  # small round icons (battle_prep portraits, world-map buttons) pass the other tests
        m = mask[y:y + h, x:x + w] > 0
        b = max(6, min(w, h) // 8)
        inner = m[b:-b, b:-b]
        if inner.size == 0:
            continue
        if inner.mean() > 0.3 and not (glow and _glow_band(hsv[y:y + h, x:x + w], b)):
            continue  # filled yellow inside: a lime button, unless a white glow band sits inside the border
        k = max(8, min(w, h) // 5)
        corners = [m[:k, :k].mean(), m[:k, -k:].mean(), m[-k:, :k].mean(), m[-k:, -k:].mean()]
        if min(corners) < 0.1:
            continue
        if best is None or w * h > best[2] * best[3]:
            best = (x, y, w, h)
    return best


def follow(dev: Device, det: StateDetector, steps: int = 40) -> str:
    """Returns "done" (nothing left to follow), "stuck", "spend_prompt", "needs_decision" or "steps"."""
    idle = same = 0
    last_box = None
    for _ in range(steps):
        d = det.detect()
        if d.state == "dialogue_choice":
            dev.tap(360, d.box[1] + d.box[3] // 2)
        elif d.state == "dialogue":
            dev.tap(*ui.DIALOGUE_NEXT)
        elif d.state in ("reward_popup", "tap_to_continue"):
            dev.tap(*ui.REWARD_CLOSE)
        elif d.state == "loading":
            time.sleep(2)
            continue
        elif d.state == "companions" and not INVITE_COMPANIONS:
            log.warning("tutorial wants a companion invited; waiting on mae (INVITE_COMPANIONS)")
            return "needs_decision"
        else:
            frame = dev.screenshot()
            box = find_highlight(frame, glow=d.state in GLOW_STATES)
            hint = det.find("Tutorial.Hint", frame) if box is None else None
            if hint:
                # The wanted button sits about 100 px below Akane's bubble, centred on the screen.
                log.info("hint '%s' on %s", hint.text, d.state)
                dev.tap(360, hint.box[1] + HINT_TO_BUTTON_DY)
                idle = 0
                time.sleep(1.5)
                continue
            if box is None:
                idle += 1
                if idle >= 6:
                    return "done"
                time.sleep(1.5)
                continue
            x, y, w, h = box
            # Same box again and again means the screen isn't reacting (or it's not really a highlight).
            same = same + 1 if last_box and all(abs(a - b) < 10 for a, b in zip(box, last_box)) else 0
            last_box = box
            if same >= 3:
                return "stuck"
            words = read_line(det, [x, y, w, h], frame)
            if re.search(NEVER_TAP, words):
                log.warning("highlight on %r looks like a spend; not tapping", words)
                return "spend_prompt"
            log.info("highlight at %s on %s", box, d.state)
            progress(("tutorial", box))  # keeps a paused loop's stall check quiet while this runs as an interrupt
            dev.tap(x + w // 2, y + h // 2)
        idle = 0
        time.sleep(1.5)
    return "steps"


def _args(p) -> None:
    p.add_argument("--steps", type=int, default=40)


def _run(ctx, opts):
    return follow(ctx.dev, ctx.det, opts.steps)


# The tutorial row of the interrupt table (sxs/actions/interrupts.py) runs follow() inside other loops; this loop
# follows highlights itself, so it owns that row.
LOOP = Loop("tutorial", "Tutorial", "tap through the game's own tutorial highlights and dialogue", _run, _args,
            owns=frozenset({"tutorial"}))
