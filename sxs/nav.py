"""Basic navigation built on the state detector: get the game to the home screen from wherever it is.

Coordinates are in the 720x1280 portrait frame. See docs/step2-hands-and-eyes.md for the screen map.
"""

from __future__ import annotations

import logging
import time

from .device import Device
from .state import NOT_RUNNING, Detection, StateDetector

log = logging.getLogger("sxs.nav")

# Bottom nav bar (y=1240) and the back arrow most full-screen pages have at the bottom left.
NAV_CHARACTER = (80, 1240)
NAV_HOME = (360, 1240)
NAV_WORLD = (640, 1240)
BACK_ARROW = (60, 1216)
HOME_MENU_BUTTON = (664, 1006)  # box icon above the chat strip on home -> main_menu
TAP_TO_PLAY = (360, 1056)
DIALOGUE_NEXT = (360, 1150)
REWARD_CLOSE = (360, 200)
CONFIRM_CANCEL = (232, 735)

# What to tap on each screen to move one step closer to home. None means just wait.
TOWARD_HOME = {
    "title": TAP_TO_PLAY,
    "loading": None,
    "dialogue": DIALOGUE_NEXT,
    "reward_popup": REWARD_CLOSE,
    "confirm_dialog": CONFIRM_CANCEL,
    "defeated": (490, 830),  # "Return to Home now?" OK
    "battle": None,  # auto battle, ends by itself
    "battle_prep": BACK_ARROW,
    "world_map": BACK_ARROW,
    "world_overview": NAV_HOME,
    "character": NAV_HOME,
    "main_menu": BACK_ARROW,
    "quests": BACK_ARROW,
}


class Navigator:
    def __init__(self, device: Device, detector: StateDetector):
        self.dev = device
        self.det = detector
        self.trail: list[str] = []  # states seen, for logs and test output

    def _seen(self, d: Detection) -> None:
        if not self.trail or self.trail[-1] != d.state:
            self.trail.append(d.state)
            log.info("state %s (%d ms)", d.state, d.elapsed_ms)

    def go_home(self, timeout: float = 240, max_unknown: int = 40) -> Detection:
        """Launch the game if needed and step toward home. Raises TimeoutError if it can't get there."""
        deadline = time.monotonic() + timeout
        unknown_streak = 0
        while time.monotonic() < deadline:
            d = self.det.detect()
            self._seen(d)
            if d.state == "home":
                return d
            if d.state == NOT_RUNNING:
                self.dev.start_game()
                time.sleep(5)
                continue
            if d.state == "agreement":
                raise RuntimeError("User Agreement dialog is showing; a human has to accept it once.")
            if d.state in TOWARD_HOME:
                unknown_streak = 0
                tap = TOWARD_HOME[d.state]
                if tap:
                    self.dev.tap(*tap)
                time.sleep(1.5 if tap else 2)
                continue
            # Unknown screen: give it time (animations, transitions), then try tapping outside a popup.
            unknown_streak += 1
            if unknown_streak >= max_unknown:
                raise RuntimeError(f"Stuck on an unknown screen; states seen: {' > '.join(self.trail)}")
            if unknown_streak % 3 == 0:
                self.dev.tap(360, 1250)  # below most popups; on full pages this is the nav bar
            time.sleep(1.5)
        raise TimeoutError(f"Did not reach home in {timeout:.0f}s; states seen: {' > '.join(self.trail)}")

    def tap_and_expect(self, xy: tuple[int, int], state: str, timeout: float = 10) -> Detection:
        """Tap, then wait until `state` shows. Raises if it doesn't."""
        self.dev.tap(*xy)
        d = self.det.wait_for({state}, timeout, interval=0.5)
        self._seen(d)
        if d.state != state:
            raise RuntimeError(f"Expected {state} after tapping {xy}, got {d.state}")
        return d
