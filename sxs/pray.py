"""Skill pulls at the Goddess Statue (Prayer), run only when the handler asks for it.

    python -m sxs.pray --pulls 20 --handler-approved
    python -m sxs.pray --check          # read the ticket count only, no pulls

mae, 2026-11-04: pulls are how the character gets new skills, but they're the handler's call: this script is
never called from an autonomous loop (sxs.daily, sxs.explore and the others don't import it), and it refuses to
pull without --pulls and --handler-approved.

Standard banner only. A pull costs Stellatie (the blue crystal prayer ticket; Pray x1 = 1, Pray x10 = 10).
Stellatie comes free from the Daily Sign-in and quests; the "+" next to it buys more and is never touched.
Dawnium is never spent: the script reads the Dawnium counter before and after each pull and stops at once if it
moved, and a purchase dialog is cancelled and ends the run. It stops when tickets run out rather than buying.
After pulling it claims the Goals tab (Total Standard Prayers milestones pay Iron Hammers and other items).
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
import time
from typing import Optional

from . import claims, nav
from .device import Device, banner, save_unknown
from .state import StateDetector

log = logging.getLogger("sxs.pray")

HOME_STATUE = (50, 810)  # Goddess Statue at the left of the home scene (default camera after a fresh start)
BANNER_STANDARD = (190, 1124)
PRAY_X1 = (250, 968)
PRAY_X10 = (530, 968)
GOALS_TAB = (608, 1216)
PRAYER_TAB = (246, 1216)
TICKETS_ROI = [470, 30, 90, 45]  # Stellatie count, top right
DAWNIUM_ROI = [560, 30, 160, 45]  # Dawnium count, right of the "+"
BANNER_LINE_ROI = [0, 870, 720, 60]  # "Prayer xN away from a guaranteed Legendary" (Standard) vs "Affection Tokens"
WOULD_SPEND = re.compile(r"Purchase|Dawnium|Recharge|Top ?up|Insufficient|Not enough", re.I)


def _number(text: str) -> Optional[float]:
    m = re.search(r"(\d+(?:\.\d+)?)\s*([KM]?)", text.replace(",", ""))
    if not m:
        return None
    return float(m.group(1)) * {"": 1, "K": 1e3, "M": 1e6}[m.group(2)]


class Prayer:
    def __init__(self, dev: Device, det: StateDetector):
        self.dev, self.det, self.nav = dev, det, nav.Navigator(dev, det)

    def _read(self, roi) -> Optional[float]:
        for t, _ in self.det.read_text(roi):
            n = _number(t)
            if n is not None:
                return n
        return None

    def tickets(self) -> Optional[int]:
        n = self._read(TICKETS_ROI)
        return int(n) if n is not None else None

    def dawnium(self) -> Optional[float]:
        return self._read(DAWNIUM_ROI)

    def open(self) -> bool:
        self.nav.go_home()
        self.dev.tap(*HOME_STATUE)
        if self.det.wait_for({"prayer"}, 8, interval=0.5).state != "prayer":
            return False
        self.dev.tap(*BANNER_STANDARD)
        time.sleep(1.5)
        line = " ".join(t for t, _ in self.det.read_text(BANNER_LINE_ROI))
        return "Affection" not in line

    def _spend_dialog(self) -> bool:
        """A purchase or shortage dialog is showing: cancel it. True if one was there."""
        texts = self.det.read_text([0, 200, 720, 900])
        if not any(WOULD_SPEND.search(t) for t, _ in texts):
            return False
        cancel = [b for t, b in texts if re.fullmatch(r"Cancel", t.strip())]
        x, y, w, h = cancel[0] if cancel else (*nav.CONFIRM_CANCEL, 0, 0)
        self.dev.tap(x + w // 2, y + h // 2)
        time.sleep(1.5)
        return True

    def _wait_result(self, timeout: float = 25) -> bool:
        """Wait out the pull animation until the result screen shows; tap the top edge to skip animations."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            s = self.det.detect().state
            if s == "prayer_result":
                return True
            if s in ("reward_popup", "tap_to_continue"):
                self.dev.tap(*nav.REWARD_CLOSE)
            elif s != "prayer":
                self.dev.tap(360, 60)
            time.sleep(1.5)
        return False

    def pull(self, pulls: int) -> str:
        """Returns "done", "out_of_tickets", "would_spend", "dawnium_changed", "no_statue" or "unknown_screen"."""
        banner(log, "Prayer", f"{pulls} Standard skill pulls with Stellatie tickets (handler-approved)",
               "pulls done, tickets run out, any purchase prompt, the Dawnium counter moving, or an unfamiliar screen")
        if not self.open():
            log.warning("Prayer (Standard banner) did not open; frame %s", save_unknown(self.dev, "pray_open"))
            return "no_statue"
        left, result, got = pulls, "done", []
        while left > 0:
            tickets, gems = self.tickets(), self.dawnium()
            if tickets is None:
                log.warning("can't read the ticket count; stopping")
                result = "unknown_screen"
                break
            x10 = left >= 10 and tickets >= 10
            cost = 10 if x10 else 1
            if tickets < cost:
                log.info("%d tickets left, %d pulls not done: stopping (never buying tickets)", tickets, left)
                result = "out_of_tickets"
                break
            log.info("Pray x%d (%d tickets, %d pulls to go)", cost, tickets, left)
            self.dev.tap(*(PRAY_X10 if x10 else PRAY_X1))
            time.sleep(2.5)
            if self._spend_dialog():
                log.warning("a purchase prompt appeared; cancelled and stopping")
                result = "would_spend"
                break
            if not self._wait_result():
                log.warning("no prayer result screen; frame %s", save_unknown(self.dev, "pray_result"))
                result = "unknown_screen"
                break
            names = [t for t, _ in self.det.read_text([0, 120, 720, 900]) if re.search(r"[A-Za-z]{3}", t)]
            got.extend(names)
            log.info("got: %s", ", ".join(names))
            after = self.dawnium()
            if gems is not None and after is not None and after < gems:
                log.error("Dawnium went from %g to %g: stopping now", gems, after)
                result = "dawnium_changed"
                break
            left -= cost
            self.dev.tap(*nav.BACK_ARROW)  # result -> Prayer
            if self.det.wait_for({"prayer"}, 8, interval=0.5).state != "prayer":
                result = "unknown_screen"
                break
        self.dev.tap(*GOALS_TAB)
        time.sleep(2)
        claims.claim_all(self.dev, self.det)
        log.info("prayer: %s after %d pulls; results: %s", result, pulls - left, "; ".join(got))
        self.nav.go_home()
        return result


def main() -> int:
    p = argparse.ArgumentParser(description="Skill pulls at the Goddess Statue. Handler-triggered only.")
    p.add_argument("--pulls", type=int, help="number of pulls (x10 is used while 10 or more remain)")
    p.add_argument("--handler-approved", action="store_true", help="required: the handler asked for these pulls")
    p.add_argument("--check", action="store_true", help="open Prayer and print the ticket count, no pulls")
    args = p.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    dev = Device()
    pr = Prayer(dev, StateDetector(dev))
    if args.check:
        ok = pr.open()
        print({"opened": ok, "tickets": pr.tickets(), "dawnium": pr.dawnium()}, flush=True)
        pr.nav.go_home()
        return 0
    if not args.pulls or not args.handler_approved:
        print("refusing: pulls are the handler's call; pass --pulls N --handler-approved", flush=True)
        return 2
    print(pr.pull(args.pulls), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
