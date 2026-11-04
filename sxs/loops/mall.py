"""Mall free gifts: claim the free gift box on each Mall page, never buy (mae, 2026-11-04, R-121).

    python -m sxs mall

Home > menu > Mall opens Premium Picks: a list of real-money (USD) pages (Welcome Gift, Halloween Charmer, Little
Devil, Pilgrimage Pass, Daily Deals, Weekly Deals). Each page has a free gift box in its top-left part (Welcome
Benefit, Daily Gift, Weekly Gift, ...) with a red "!" while it's claimable; one tap claims it ("YOU RECEIVED").
Only that box is tapped: a badge in the left column of the page's upper half. Price buttons are never tapped.
No model calls.
"""

from __future__ import annotations

import logging
import time

from ..core import ui
from ..core.device import Device, save_unknown
from ..core.state import StateDetector
from ..core.loop import Loop, banner, progress
from ..core.nav import Navigator
from ..vision.badges import find_badges

log = logging.getLogger("sxs.loops.mall")

MENU_MALL = (520, 826)
LIST_TOP = [(360, 230), (360, 480), (360, 720), (360, 960)]  # first four banners before scrolling
LIST_SCROLLED = [(360, 260), (360, 510), (360, 760), (360, 1000)]  # after one swipe: Little Devil .. Weekly Deals
GIFT_ROI = [0, 150, 260, 700]  # where the free gift box sits on a page (left column, upper half)
GIFT_FROM_BADGE = (-40, 35)  # the box is below-left of its "!"


class Mall:
    def __init__(self, dev: Device, det: StateDetector):
        self.dev, self.det, self.nav = dev, det, Navigator(dev, det)

    def _tap(self, xy, wait=2.0):
        self.dev.tap(*xy)
        time.sleep(wait)

    def _open_mall(self) -> bool:
        self.nav.go_home()
        self._tap(ui.HOME_MENU_BUTTON, 2.5)
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
            log.info("gift badge at %s", (bx, by))
            self._tap((bx + GIFT_FROM_BADGE[0], by + GIFT_FROM_BADGE[1]), 3)
            self._tap(ui.REWARD_CLOSE, 2)  # close "YOU RECEIVED"
            n += 1
        return n

    def claim_gifts(self, part: int = 0) -> str:
        """part 0: every page; 1: the first four banners; 2: the four after one scroll. Each part fits a 2-minute
        task (a page takes about 17 s to open, check and leave)."""
        banner(log, "Mall Gifts", "claim the free gift box on each Mall page, buy nothing",
               "every page visited once, or an unexpected screen")
        if not self._open_mall():
            log.warning("Mall did not open; frame %s", save_unknown(self.dev, "mall"))
            return "unknown_screen"
        claimed = 0
        for scrolled, points in ((False, LIST_TOP), (True, LIST_SCROLLED)):
            if part and part != (2 if scrolled else 1):
                continue
            for xy in points:
                if scrolled:
                    self.dev.swipe(360, 1000, 360, 300, 600)
                    time.sleep(1.5)
                self._tap(xy, 4)
                if self.det.detect().state == "mall":
                    continue  # the tap didn't open a page
                got = self._claim_on_page()
                log.info("page at %s: %d gift(s) claimed", xy, got)
                progress((scrolled, xy))
                claimed += got
                self._tap(ui.BACK_ARROW, 3)
                if self.det.detect().state != "mall":
                    log.warning("not back on the Mall list; frame %s", save_unknown(self.dev, "mall_back"))
                    self._tap(ui.BACK_ARROW, 3)
        log.info("mall gifts claimed: %d", claimed)
        self._tap(ui.BACK_ARROW, 3)
        self.nav.go_home()
        return "done" if claimed else "nothing"


def _args(p) -> None:
    p.add_argument("--part", type=int, choices=(1, 2), help="only the first four pages (1) or the next four (2)")


def _run(ctx, opts):
    return Mall(ctx.dev, ctx.det).claim_gifts(opts.part or 0)


LOOP = Loop("mall", "Mall Gifts", "claim the free gift box on each Mall page, buy nothing", _run, _args,
            budget=200)  # all eight pages; `daily` runs the two halves as separate 2-minute steps
