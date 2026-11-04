"""Gear Swap: put on a better piece wherever the Character screen flags a gear slot (mae, 2026-11-04).

    python -m sxs gearswap            # swap every flagged slot
    python -m sxs gearswap --check    # report which slots are flagged, tap nothing past the Character screen
    python -m sxs gearswap --all      # also look at unflagged slots (the compare still decides)

mae: a red "!" over a gear piece means a better piece is in the bag, and swapping it in is its own task,
separate from enhancing (that's `upgrade` / `strengthen`). Per flagged slot: tap the piece -> item card ->
Replace -> Replace Gear list (best first, R-088) -> first candidate -> compare; Replace only when the new piece's
power is higher. Enhancement carries over to the new piece (R-088). A slot whose flag doesn't clear after a swap
attempt is given up for this run (no retry). Never touches Rcmd Loadouts, Change Class, charms or techniques.
No model calls.
"""

from __future__ import annotations

import logging
import re

from ..core import ui
from ..core.device import save_unknown
from ..core.loop import Loop, banner, progress
from ..core.nav import Navigator
from ..vision.badges import find_badges, near_any
from .strengthen import GEAR_COMPARE_REPLACE, GEAR_LIST_FIRST, GEAR_POWER_ROIS, GEAR_SLOTS, Strengthener

log = logging.getLogger("sxs.loops.gearswap")

SLOT_NAMES = ["weapon", "head", "chest", "boots"]
BADGE_FROM_SLOT = (30, -45)  # a slot's "!" sits on the piece's top-right rim (tap points are off-centre)
BADGE_RADIUS = 50
CARD_BUTTONS_ROI = [0, 820, 720, 130]  # item card: Replace (left) / Enhance (right)


class GearSwap:
    def __init__(self, dev, det):
        self.dev, self.det = dev, det
        self.nav = Navigator(dev, det)
        self._tap = self.nav.tap
        self.st = Strengthener(dev, det)

    def _character(self) -> bool:
        self.nav.go_home()
        try:
            self.nav.tap_and_expect(ui.NAV_CHARACTER, "character")
            return True
        except RuntimeError as e:
            log.warning("%s; frame %s", e, save_unknown(self.dev, "gearswap_character"))
            return False

    def flagged(self) -> list[int]:
        """Indexes of gear slots with a badge on them (union over two frames: badges pulse)."""
        seen = find_badges(self.dev.screenshot()) + find_badges(self.dev.screenshot())
        out = []
        for i, (x, y) in enumerate(GEAR_SLOTS):
            if near_any(seen, (x + BADGE_FROM_SLOT[0], y + BADGE_FROM_SLOT[1]), BADGE_RADIUS):
                out.append(i)
        return out

    def swap(self, i: int) -> str:
        """Character screen showing: try to put a better piece in slot i. Returns swapped / kept / no_replace /
        unknown_screen; always ends back on the Character screen (or home after an unknown screen)."""
        name = SLOT_NAMES[i]
        self._tap(GEAR_SLOTS[i], 2)
        buttons = [(t, b) for t, b in self.det.read_text(CARD_BUTTONS_ROI) if re.fullmatch(r"Replace|Equip", t)]
        if not buttons:
            log.info("%s: the item card has no Replace button", name)
            self._tap(ui.BELOW_POPUP, 1.5)
            return "no_replace"
        self._tap(ui.centre(buttons[0][1]), 2.5)
        if not any("Replace Gear" in t for t, _ in self.det.read_text([150, 190, 420, 60])):
            log.warning("%s: Replace did not open the Replace Gear list; frame %s", name,
                        save_unknown(self.dev, "gearswap_list"))
            self.nav.go_home()
            return "unknown_screen"
        self._tap(GEAR_LIST_FIRST, 2)
        old, new = (self.st._power(r) for r in GEAR_POWER_ROIS)
        if new > 0 and new > old:
            hits = [b for t, b in self.det.read_text([370, 700, 350, 400]) if re.fullmatch(r"Replace", t)]
            self._tap(ui.centre(hits[0]) if hits else GEAR_COMPARE_REPLACE, 2.5)
            log.info("%s: replaced (power %g -> %g)", name, old, new)
            result = "swapped"
        else:
            log.info("%s: kept the equipped piece (%g vs %g)", name, old, new)
            result = "kept"
        for _ in range(3):  # compare -> list -> card -> Character screen
            if self.det.detect().state == "character":
                break
            self._tap(ui.BELOW_POPUP, 1.5)
        if self.det.detect().state != "character" and not self._character():
            return "unknown_screen"
        return result

    def run(self, check: bool = False, all_slots: bool = False) -> dict:
        banner(log, "Gear Swap", "equip the better piece in every gear slot the Character screen flags",
               "no flagged slot left (each tried once), an unknown screen, or the time budget")
        if not self._character():
            return {"end": "unknown_screen"}
        flags = self.flagged()
        log.info("flagged slots: %s", [SLOT_NAMES[i] for i in flags] or "none")
        if check:
            self.nav.go_home()
            return {"end": "checked", "flagged": [SLOT_NAMES[i] for i in flags]}
        todo = list(range(len(GEAR_SLOTS))) if all_slots else flags
        out = {"swapped": [], "kept": [], "given_up": []}
        for i in todo:
            r = self.swap(i)
            progress((i, r))
            if r == "unknown_screen":
                out["end"] = "unknown_screen"
                return out
            if r == "swapped":
                out["swapped"].append(SLOT_NAMES[i])
                if i in self.flagged():
                    log.info("%s still flagged after the swap; not retrying this run", SLOT_NAMES[i])
                    out["given_up"].append(SLOT_NAMES[i])
            else:
                out["kept"].append(SLOT_NAMES[i])
        self.nav.go_home()
        out["end"] = "done" if out["swapped"] else "nothing"
        return out


def _args(p) -> None:
    p.add_argument("--check", action="store_true", help="report flagged slots only")
    p.add_argument("--all", action="store_true", help="also open unflagged slots (the power compare still decides)")


def _run(ctx, opts):
    return GearSwap(ctx.dev, ctx.det).run(opts.check, opts.all)


LOOP = Loop("gearswap", "Gear Swap", "equip better gear wherever a gear slot shows a red \"!\"", _run, _args,
            ok={"done", "nothing", "checked"})
