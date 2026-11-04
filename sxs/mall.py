"""Mall free gifts: claim the free gift box on each Mall page, never buy (mae, 2026-11-04, R-121).

    python -m sxs.mall

Home > menu > Mall opens Premium Picks: a list of real-money (USD) pages (Welcome Gift, Halloween Charmer, Little
Devil, Pilgrimage Pass, Daily Deals, Weekly Deals). Each page has a free gift box in its top-left part (Welcome
Benefit, Daily Gift, Weekly Gift, ...) with a red "!" while it's claimable; one tap claims it ("YOU RECEIVED").
Only that box is tapped: a badge in the left column of the page's upper half. Price buttons are never tapped.
No model calls.
"""

from __future__ import annotations

import json
import logging
import sys
import time

from . import nav
from .badges import find_badges
from .device import Device, banner, save_unknown
from .state import StateDetector

log = logging.getLogger("sxs.mall")

MENU_MALL = (520, 826)
LIST_TOP = [(360, 230), (360, 480), (360, 720), (360, 960)]  # first four banners before scrolling
LIST_SCROLLED = [(360, 260), (360, 510), (360, 760), (360, 1000)]  # after one swipe: Little Devil .. Weekly Deals
GIFT_ROI = [0, 150, 260, 700]  # where the free gift box sits on a page (left column, upper half)
GIFT_FROM_BADGE = (-40, 35)  # the box is below-left of its "!"


class Mall:
    def __init__(self, dev: Device, det: StateDetector):
        self.dev, self.det, self.nav = dev, det, nav.Navigator(dev, det)

    def _tap(self, xy, wait=2.0):
        self.dev.tap(*xy)
        time.sleep(wait)

    def _open_mall(self) -> bool:
        self.nav.go_home()
        self._tap(nav.HOME_MENU_BUTTON, 2.5)
        self._tap(MENU_MALL, 4)
        return self.det.detect().state == "mall"

    def _claim_on_page(self) -> int:
        n = 0
        for _ in range(2):
            gifts = []
            for _ in range(5):  # badges pulse: look over a couple of seconds
                gifts = find_badges(self.dev.screenshot(), GIFT_ROI)
                if gifts:
                    break
                time.sleep(0.4)
            if not gifts:
                break
            bx, by = gifts[0]
            self._tap((bx + GIFT_FROM_BADGE[0], by + GIFT_FROM_BADGE[1]), 3)
            self._tap(nav.REWARD_CLOSE, 2)  # close "YOU RECEIVED"
            n += 1
        return n

    def claim_gifts(self) -> str:
        banner(log, "Mall Gifts", "claim the free gift box on each Mall page, buy nothing",
               "every page visited once, or an unexpected screen")
        if not self._open_mall():
            log.warning("Mall did not open; frame %s", save_unknown(self.dev, "mall"))
            return "unknown_screen"
        claimed = 0
        for scrolled, points in ((False, LIST_TOP), (True, LIST_SCROLLED)):
            for xy in points:
                if scrolled:
                    self.dev.swipe(360, 1000, 360, 300, 600)
                    time.sleep(1.5)
                self._tap(xy, 4)
                if self.det.detect().state == "mall":
                    continue  # the tap didn't open a page
                claimed += self._claim_on_page()
                self._tap(nav.BACK_ARROW, 3)
                if self.det.detect().state != "mall":
                    log.warning("not back on the Mall list; frame %s", save_unknown(self.dev, "mall_back"))
                    self._tap(nav.BACK_ARROW, 3)
        log.info("mall gifts claimed: %d", claimed)
        self._tap(nav.BACK_ARROW, 3)
        self.nav.go_home()
        return "done" if claimed else "nothing"


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    dev = Device()
    print(json.dumps({"end": Mall(dev, StateDetector(dev)).claim_gifts()}), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
