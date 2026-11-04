"""Get stronger between fights using only soft resources: claim the Cart, enhance gear, upgrade techniques.

    python -m sxs strengthen

Each step starts from home and returns there. Spends Rolla, Raw/Refined Ore and Battle Essence only; stops tapping
an upgrade as soon as the game says materials are short. Never touches Dawnium, Prayer or the shop. No model calls.
"""

from __future__ import annotations

import logging
import re

import cv2
import time
from typing import Optional

from ..core import ui
from ..core.device import Device
from ..core.state import StateDetector
from ..core.loop import Loop
from ..core.nav import Navigator

log = logging.getLogger("sxs.loops.strengthen")

CLAIM_ALL = (360, 1098)
GEAR_SLOTS = [(84, 400), (646, 380), (646, 476), (646, 620)]  # Character screen: weapon, then right column
ITEM_CARD_ENHANCE = (490, 880)
GEAR_TABS = [(160, 166), (304, 166), (424, 166), (552, 166)]  # Enhance Gear screen, top row
GEAR_ENHANCE = (360, 1084)
GEAR_LEVEL_ROI = [150, 510, 420, 70]  # Enhance Gear: "+21 -> +22" for the selected piece
GEAR_BAND = 5  # mae, 2026-11-04: enhance in 5-level bands, all pieces together
# Enhance order inside a band, as indexes into GEAR_TABS (shown weapon, head, chest, boots today). mae's priority is
# weapon > offhand > headpiece > chest > boots; when an offhand tab appears, insert its index after the weapon.
GEAR_PRIORITY = [0, 1, 2, 3]
SKILL_BUTTON = ui.SKILL_BUTTON
TECHNIQUE_SLOT = (92, 270)
TECHNIQUE_CARD_ENHANCE = ui.TECHNIQUE_CARD_ENHANCE
TECHNIQUE_TABS = [(160, 190), (318, 190), (424, 190), (552, 190)]
TECHNIQUE_UPGRADE = (360, 1086)
SHORT = r"Insufficient|Unlocks at Character"
PROFILE_CHARM_SLOTS = [(406, 910), (480, 910), (554, 910), (628, 910)]  # player profile: Charm row; an empty one opens the loadout editor
CHARM_SLOTS = [(626, 268), (626, 384), (626, 500), (626, 616)]  # loadout editor, right column
CHARM_LIST = [(100, 930), (230, 930), (360, 930), (490, 930), (620, 930)]  # Charm tab, owned and unequipped
CHARM_EQUIP = (360, 898)  # charm card's Equip button
CHARM_TAB = (400, 800)  # loadout editor opens on the Technique tab
PROFILE_GEAR_SLOTS = [(110, 754), (234, 754), (360, 754), (484, 754)]  # player profile: Equip row
GEAR_CARD_BUTTON = (360, 880)  # single gear card: Replace (or Equip)
GEAR_LIST_FIRST = (150, 345)  # Replace Gear list, sorted best first (green up arrow = upgrade)
GEAR_COMPARE_REPLACE = (536, 896)  # side-by-side compare: Replace under the new item
GEAR_POWER_ROIS = ([20, 520, 200, 100], [370, 520, 200, 100])  # power under each compared item: equipped, new
FILLED_SAT = 60  # mean HSV saturation over a slot/list icon: coloured icon above, empty grey disc below


class Strengthener:
    def __init__(self, dev: Device, det: StateDetector):
        self.dev, self.det, self.nav = dev, det, Navigator(dev, det)

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

    def _gear_level(self) -> Optional[int]:
        """Current level of the selected piece on Enhance Gear, from the big "+21 -> +22" line."""
        # OCR order is not left to right ("+10" can come before "+9"): the current level is the leftmost number.
        for t, _ in sorted(self.det.read_text(GEAR_LEVEL_ROI), key=lambda tb: tb[1][0]):
            m = re.fullmatch(r"\+?(\d+)", t.strip())
            if m:
                return int(m.group(1))
        return None

    def enhance_gear(self, max_taps: int = 60) -> None:
        """Enhance gear in 5-level bands so all pieces level together (mae, 2026-11-04): raise every piece below the
        next multiple of 5 above the lowest level up to it, in GEAR_PRIORITY order, then the next band, until
        materials run short. Spends Rolla and ore only."""
        self.nav.go_home()
        self.nav.tap_and_expect(ui.NAV_CHARACTER, "character")
        self._tap(GEAR_SLOTS[0], 2)
        self._tap(ITEM_CARD_ENHANCE, 2.5)
        if self.det.detect().state != "enhance_gear":
            log.warning("Enhance Gear did not open; skipping gear")
            self.nav.go_home()
            return
        levels = {}
        for i, tab in enumerate(GEAR_TABS):
            self._tap(tab)
            lv = self._gear_level()
            if lv is not None:
                levels[i] = lv
        log.info("gear levels: %s", levels)
        taps, short = 0, False
        while levels and not short and taps < max_taps:
            target = (min(levels.values()) // GEAR_BAND + 1) * GEAR_BAND
            for i in [i for i in GEAR_PRIORITY if i in levels]:
                if levels[i] >= target:
                    continue
                self._tap(GEAR_TABS[i])
                while levels[i] < target and taps < max_taps:
                    self._tap(GEAR_ENHANCE, 1.2)
                    taps += 1
                    if self._short():
                        short = True
                        break
                    lv = self._gear_level()
                    if lv is None or lv <= levels[i]:
                        short = True  # nothing changed: stop rather than tap blindly
                        break
                    levels[i] = lv
                if short:
                    break
        self._tap(ui.BACK_ARROW, 2)
        log.info("gear enhanced: %s (%d taps%s)", levels, taps, ", materials short" if short else "")

    def upgrade_techniques(self, taps_per_item: int = 12) -> None:
        self.nav.go_home()
        self.nav.tap_and_expect(ui.NAV_CHARACTER, "character")
        self._tap(SKILL_BUTTON, 2.5)
        self._tap(TECHNIQUE_SLOT, 2)
        self._tap(TECHNIQUE_CARD_ENHANCE, 2.5)
        for tab in TECHNIQUE_TABS:
            self._tap(tab)
            for _ in range(taps_per_item):
                self._tap(TECHNIQUE_UPGRADE, 1.2)
                if self._short():
                    break
        self._tap(ui.BACK_ARROW, 2)
        self._tap(ui.BACK_ARROW, 2)
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
        self._tap(ui.BACK_ARROW, 2)
        return equipped

    def _power(self, roi) -> float:
        for t, _ in self.det.read_text(roi):
            m = re.search(r"(\d+(?:\.\d+)?)(K?)$", t.replace(",", ""))  # the swords icon OCRs as a stray char
            if m:
                return float(m.group(1)) * (1000 if m.group(2) else 1)
        return 0.0

    def equip_better_gear(self) -> int:
        """From the player profile: for each Equip slot, open Replace Gear, take the top candidate (the list is sorted
        best first) and replace only if the comparison shows a higher power number for it. Enhancement levels carry
        over to the new item (Beginner's Cap +10 -> Adventurer's Leather Hat +10). Returns the number replaced."""
        replaced = 0
        for slot in PROFILE_GEAR_SLOTS:
            self._tap(slot, 2)
            if not any(re.fullmatch(r"Replace|Equip", t) for t, _ in self.det.read_text([200, 840, 320, 90])):
                self._tap((360, 1230), 1.5)  # nothing to change here: close the card
                continue
            self._tap(GEAR_CARD_BUTTON, 2.5)
            if not any("Replace Gear" in t for t, _ in self.det.read_text([150, 190, 420, 60])):
                self._tap((360, 1230), 1.5)
                continue
            self._tap(GEAR_LIST_FIRST, 2)
            old, new = (self._power(r) for r in GEAR_POWER_ROIS)
            if new > old > 0 or (new > 0 and old == 0):
                # The cards' height depends on the item's stat lines: find the new item's Replace button.
                button = [b for t, b in self.det.read_text([370, 700, 350, 400]) if re.fullmatch(r"Replace", t)]
                x, y, w, h = button[0] if button else (*GEAR_COMPARE_REPLACE, 0, 0)
                self._tap((x + w // 2, y + h // 2), 2.5)
                replaced += 1
                log.info("gear slot %s: replaced (%g -> %g power)", slot, old, new)
            else:
                log.info("gear slot %s: kept (%g vs %g)", slot, old, new)
                self._tap((360, 1250), 1.5)
                self._tap((360, 1250), 1.5)
            if self.det.detect().state != "player_profile":
                self._tap((360, 1250), 1.5)
        return replaced

    def run(self) -> None:
        self.claim_cart()
        self.enhance_gear()
        self.upgrade_techniques()
        self.nav.go_home()


def _run(ctx, opts):
    Strengthener(ctx.dev, ctx.det).run()


LOOP = Loop("strengthen", "Strengthen", "claim the Cart, enhance gear and upgrade techniques with soft resources",
            _run)
