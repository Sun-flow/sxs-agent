"""Vendor Booth (Molly's wagon on home): claim the Vault's free x30 Stamina once a day (mae, 2026-11-04, R-120).

    python -m sxs.vendor            # claim the free stamina if it's there
    python -m sxs.vendor --check    # open the Vault and report, tap no price

Only the Vault's first cell is ever tapped, and only when OCR reads its price button as exactly "Free". Every other
item in the booth costs Rolla or Dawnium and is never touched until mae's buy list exists (docs/shop-tables.md).
No model calls.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time

from . import nav
from .device import Device, banner, save_unknown
from .state import StateDetector

log = logging.getLogger("sxs.vendor")

TAB_GENERAL, TAB_VAULT = (140, 1216), (430, 1216)
FREE_CELL_PRICE = (130, 406)  # Vault row 1, col 1: the price button ("Free" for the daily stamina)
FREE_CELL_PRICE_ROI = [40, 380, 180, 52]
BOOTH_TAP_DY = 70  # from the template's centre (roof) down to the wagon body
PANS = [None, (600, 700, 250, 700), (600, 700, 250, 700), (150, 700, 600, 700), (150, 700, 600, 700),
        (150, 700, 600, 700)]


class Vendor:
    def __init__(self, dev: Device, det: StateDetector):
        self.dev, self.det, self.nav = dev, det, nav.Navigator(dev, det)

    def _tap(self, xy, wait=2.0):
        self.dev.tap(*xy)
        time.sleep(wait)

    def open_booth(self) -> bool:
        """Home, then pan the home scene sideways until the wagon template shows, and tap it."""
        self.nav.go_home()
        for pan in PANS:
            if pan:
                self.dev.swipe(*pan, 500)
                time.sleep(1.5)
            hits = self.det.find_all("Home.VendorBooth")
            if hits:
                x, y, w, h = hits[0]
                self._tap((x + w // 2, y + h // 2 + BOOTH_TAP_DY), 3)
                texts = " ".join(t for t, _ in self.det.read_text([0, 20, 400, 60]))
                if "vendor" in texts.lower():
                    return True
                log.warning("tapped the wagon but saw %r; frame %s", texts, save_unknown(self.dev, "vendor_open"))
                self.nav.go_home()
                return False
        log.warning("Vendor Booth not found on home; frame %s", save_unknown(self.dev, "vendor_find"))
        return False

    def claim_free_stamina(self, check: bool = False) -> str:
        banner(log, "Vendor Booth", "claim the Vault's free x30 Stamina (nothing else is tapped)",
               "claimed, not free today, or the booth/Vault not found")
        if not self.open_booth():
            return "unknown_screen"
        self._tap(TAB_VAULT, 2.5)
        price = " ".join(t for t, _ in self.det.read_text(FREE_CELL_PRICE_ROI)).strip()
        log.info("Vault first cell price: %r", price)
        if price.lower() != "free":
            self.nav.go_home()
            return "nothing"
        if check:
            self.nav.go_home()
            return "free_available"
        self._tap(FREE_CELL_PRICE, 2.5)
        d = self.det.detect()
        if d.state in ("reward_popup", "tap_to_continue"):
            self._tap(nav.REWARD_CLOSE, 2)
        elif d.state == "confirm_dialog":
            texts = " ".join(t for t, _ in self.det.read_text([60, 400, 600, 500]))
            log.warning("confirm after Free: %r; cancelling (frame %s)", texts, save_unknown(self.dev, "vendor_confirm"))
            self._tap(nav.CONFIRM_CANCEL, 2)
            self.nav.go_home()
            return "needs_decision"
        after = " ".join(t for t, _ in self.det.read_text(FREE_CELL_PRICE_ROI)).strip()
        log.info("after claim, first cell reads %r", after)
        self.nav.go_home()
        return "done"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    dev = Device()
    result = Vendor(dev, StateDetector(dev)).claim_free_stamina(args.check)
    print(json.dumps({"vendor_free_stamina": result}), flush=True)
    return 0 if result in ("done", "nothing", "free_available") else 1


if __name__ == "__main__":
    sys.exit(main())
