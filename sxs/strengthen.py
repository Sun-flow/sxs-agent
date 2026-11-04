"""Get stronger between fights using only soft resources: claim the Cart, enhance gear, upgrade techniques.

    python -m sxs.strengthen

Each step starts from home and returns there. Spends Rolla, Raw/Refined Ore and Battle Essence only; stops tapping
an upgrade as soon as the game says materials are short. Never touches Dawnium, Prayer or the shop. No model calls.
"""

from __future__ import annotations

import logging
import re

import cv2
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
PROFILE_CHARM_SLOTS = [(406, 910), (480, 910), (554, 910), (628, 910)]  # player profile: Charm row; an empty one opens the loadout editor
CHARM_SLOTS = [(626, 268), (626, 384), (626, 500), (626, 616)]  # loadout editor, right column
CHARM_LIST = [(100, 930), (230, 930), (360, 930), (490, 930), (620, 930)]  # Charm tab, owned and unequipped
CHARM_EQUIP = (360, 898)  # charm card's Equip button
CHARM_TAB = (400, 800)  # loadout editor opens on the Technique tab
FILLED_SAT = 60  # mean HSV saturation over a slot/list icon: coloured icon above, empty grey disc below


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

    @staticmethod
    def _filled(frame, xy) -> bool:
        x, y = xy
        hsv = cv2.cvtColor(frame[y - 15:y + 15, x - 15:x + 15], cv2.COLOR_BGR2HSV)
        return float(hsv[..., 1].mean()) > FILLED_SAT

    def equip_charms(self, from_profile: bool = False) -> int:
        """Put owned, unequipped charms into empty charm slots (a red "!" on the character, its Charm slots and
        the Charm tab). Only fills empty slots, never swaps an equipped charm, never touches techniques or the
        Rcmd loadouts. Starts from the player profile (tap own character) or goes there via the map. Returns the
        number equipped."""
        if not from_profile:
            return 0  # TODO: reach the loadout editor from home (Character -> Skill) when needed
        frame = self.dev.screenshot()
        empty = [xy for xy in PROFILE_CHARM_SLOTS if not self._filled(frame, xy)]
        if not empty:
            return 0
        self._tap(empty[0], 2.5)  # an equipped one would open that charm's card instead
        if not any(re.fullmatch(r"Edit", t) for t, _ in self.det.read_text([20, 20, 200, 70])):
            log.warning("loadout editor did not open")
            return 0
        self._tap(CHARM_TAB, 1.5)
        equipped = 0
        for _ in range(len(CHARM_SLOTS)):
            frame = self.dev.screenshot()
            empty = [xy for xy in CHARM_SLOTS if not self._filled(frame, xy)]
            owned = [xy for xy in CHARM_LIST if self._filled(frame, xy)]
            if not empty or not owned:
                break
            self._tap(owned[0], 2)
            if not any(re.fullmatch(r"Equip", t) for t, _ in self.det.read_text([200, 850, 320, 100])):
                log.warning("charm card has no Equip button; stopping")
                self._tap((360, 1230), 1.5)
                break
            self._tap(CHARM_EQUIP, 2)
            self._tap(empty[0], 2)  # equip mode highlights the slots: pick an empty one
            equipped += 1
            log.info("charm equipped into slot %s", empty[0])
        self._tap(nav.BACK_ARROW, 2)
        return equipped

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
