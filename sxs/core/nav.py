"""Basic navigation built on the state detector: get the game to the home screen from wherever it is.

Coordinates are in the 720x1280 portrait frame. See docs/step2-hands-and-eyes.md for the screen map.
"""

from __future__ import annotations

import logging
import time

from .device import Device
from .state import NOT_RUNNING, Detection, StateDetector
from .ui import (ABOVE_POPUP, BACK_ARROW, BACKGROUND_FIGHT, CONFIRM_CANCEL, DIALOGUE_NEXT, NAV_HOME, REWARD_CLOSE,
                 TAP_TO_PLAY)

log = logging.getLogger("sxs.core.nav")

DEFEATED_OK = (490, 830)  # "Return to Home now?" OK

# What to tap on each screen to move one step closer to home. None means just wait.
TOWARD_HOME = {
    "title": TAP_TO_PLAY,
    "loading": None,
    "dialogue": DIALOGUE_NEXT,
    "reward_popup": REWARD_CLOSE,
    "tap_to_continue": REWARD_CLOSE,
    "confirm_dialog": CONFIRM_CANCEL,
    "defeated": DEFEATED_OK,
    "battle": None,  # auto battle, ends by itself
    "chat": (42, 1226),  # chat panel: the down chevron closes it
    "area_map": BACK_ARROW,
    "battle_prep": BACK_ARROW,
    "world_map": BACK_ARROW,
    "world_overview": NAV_HOME,
    "character": NAV_HOME,
    "main_menu": BACK_ARROW,
    "cart": (360, 1220),  # tap outside the panel
    "quests": BACK_ARROW,
    "tower_result": BACK_ARROW,
    "tower_floors": BACK_ARROW,
    "tower_list": BACK_ARROW,
    "enhance_gear": BACK_ARROW,
    "featured": BACK_ARROW,
    "daily_signin": BACK_ARROW,
    "growth_trial": BACK_ARROW,
    "material_realms": BACK_ARROW,
    "notice": BACK_ARROW,
    "journal": NAV_HOME,
    "guild": NAV_HOME,
    "guild_no_guild": NAV_HOME,
    "guild_join_list": BACK_ARROW,
    "guild_panel": BACK_ARROW,
    "guild_conquest": BACK_ARROW,
    "guild_donation": ABOVE_POPUP,
    "background_fight": BACKGROUND_FIGHT,
    "mall": BACK_ARROW,
    "rating_popup": (360, 882),  # "Later" (mae, 2026-11-04: popups like this are okay to press Later)
    "prayer": BACK_ARROW,
    "prayer_result": BACK_ARROW,
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
            if unknown_streak % 6 == 3:
                self.dev.tap(360, 1250)  # below most popups; on full pages this is the nav bar
            elif unknown_streak % 6 == 0:
                self.dev.tap(*BACK_ARROW)  # full pages without a known state (Mall deal pages, ...) have "<" here
            time.sleep(1.5)
        raise TimeoutError(f"Did not reach home in {timeout:.0f}s; states seen: {' > '.join(self.trail)}")

    def tap(self, xy, wait: float = 2.0) -> None:
        """Tap and give the screen time to react."""
        self.dev.tap(*xy)
        time.sleep(wait)

    def open(self, xy, state: str, timeout: float = 8.0) -> bool:
        """Tap, then wait up to `timeout` for `state`. True if it showed."""
        self.dev.tap(*xy)
        return self.det.wait_for({state}, timeout, interval=0.5).state == state

    def tap_and_expect(self, xy: tuple[int, int], state: str, timeout: float = 10) -> Detection:
        """Tap, then wait until `state` shows. Raises if it doesn't."""
        self.dev.tap(*xy)
        d = self.det.wait_for({state}, timeout, interval=0.5)
        self._seen(d)
        if d.state != state:
            raise RuntimeError(f"Expected {state} after tapping {xy}, got {d.state}")
        return d
