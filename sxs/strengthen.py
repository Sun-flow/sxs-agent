"""Get stronger between fights using only soft resources: claim the Cart, enhance gear, upgrade techniques.

    python -m sxs.strengthen

Each step starts from home and returns there. Spends Rolla, Raw/Refined Ore and Battle Essence only; stops tapping
an upgrade as soon as the game says materials are short. Never touches Dawnium, Prayer or the shop. No model calls.
"""

from __future__ import annotations

import logging
import sys
import time

from . import nav
from .device import Device
from .state import StateDetector

log = logging.getLogger("sxs.strengthen")

CLAIM_ALL = (360, 1098)
GEAR_SLOTS = [(84, 400), (646, 380), (646, 476), (646, 620)]  # Character screen: weapon, then right column
ITEM_CARD_ENHANCE = (490, 880)
GEAR_TABS = [(160, 166), (304, 166), (424, 166), (552, 166)]  # Enhance Gear screen, top row
GEAR_ENHANCE = (360, 1084)
SKILL_BUTTON = (296, 760)
TECHNIQUE_SLOT = (92, 270)
TECHNIQUE_CARD_ENHANCE = (490, 946)
TECHNIQUE_TABS = [(160, 190), (318, 190), (424, 190), (552, 190)]
TECHNIQUE_UPGRADE = (360, 1086)
SHORT = r"Insufficient|Unlocks at Character"


class Strengthener:
    def __init__(self, dev: Device, det: StateDetector):
        self.dev, self.det, self.nav = dev, det, nav.Navigator(dev, det)

    def _tap(self, xy, wait=1.5):
        self.dev.tap(*xy)
        time.sleep(wait)

    def _short(self) -> bool:
        import re
        return any(re.search(SHORT, t) for t, _ in self.det.read_text([0, 280, 720, 900]))

    def claim_cart(self) -> bool:
        """Find the Cart's loot bubble on the sideways-scrolling home scene and claim it. False if not found."""
        self.nav.go_home()
        right, left = (150, 600, 650, 600), (650, 600, 150, 600)
        for swipe in [None, right, right, right, left, left, left, left, left, left]:  # sweep the whole scene
            if swipe:
                self.dev.swipe(*swipe, 400)
                time.sleep(1.5)
            bubble = self.det.find("Home.CartBubble")
            if bubble:
                x, y, w, h = bubble.box
                self._tap((x + w // 2, y + h // 2), 2.5)
                state = self.det.detect().state
                if state in ("cart", "reward_popup"):
                    # The bubble claims straight away (reward popup); the cart itself opens the panel.
                    if state == "cart":
                        self._tap(CLAIM_ALL, 2)
                    self.nav.go_home()
                    log.info("cart claimed")
                    return True
        log.info("no cart loot bubble found")
        return False

    def enhance_gear(self, taps_per_item: int = 10) -> None:
        self.nav.go_home()
        self.nav.tap_and_expect(nav.NAV_CHARACTER, "character")
        self._tap(GEAR_SLOTS[0], 2)
        self._tap(ITEM_CARD_ENHANCE, 2.5)
        for tab in GEAR_TABS:
            self._tap(tab)
            for _ in range(taps_per_item):
                self._tap(GEAR_ENHANCE, 1.2)
                if self._short():
                    break
        self._tap(nav.BACK_ARROW, 2)
        log.info("gear enhanced")

    def upgrade_techniques(self, taps_per_item: int = 12) -> None:
        self.nav.go_home()
        self.nav.tap_and_expect(nav.NAV_CHARACTER, "character")
        self._tap(SKILL_BUTTON, 2.5)
        self._tap(TECHNIQUE_SLOT, 2)
        self._tap(TECHNIQUE_CARD_ENHANCE, 2.5)
        for tab in TECHNIQUE_TABS:
            self._tap(tab)
            for _ in range(taps_per_item):
                self._tap(TECHNIQUE_UPGRADE, 1.2)
                if self._short():
                    break
        self._tap(nav.BACK_ARROW, 2)
        self._tap(nav.BACK_ARROW, 2)
        log.info("techniques upgraded")

    def run(self) -> None:
        self.claim_cart()
        self.enhance_gear()
        self.upgrade_techniques()
        self.nav.go_home()


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    dev = Device()
    Strengthener(dev, StateDetector(dev)).run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
