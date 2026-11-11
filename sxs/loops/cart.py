"""Cart Upgrade: raise the AFK Cart's Stone and Wood rows, keeping their levels even (mae, 2026-11-05, R-136).

    python -m sxs cart              # claim the Cart, then upgrade Stone/Wood until something stops it
    python -m sxs cart --check      # claim, open the upgrade screen, read levels and the next cost; press nothing
    python -m sxs cart --max 4      # at most 4 upgrades this run

mae's priority: only Stone and Wood, kept level with each other: raise whichever is lower; when they are level, Stone
first. Every other row (Rolla, Raw Ore, Battle Essence, Gear, Chrono Sand...) is never upgraded.

R-137 (mae, 2026-11-09): a production row with an "Unlock" button (Chrono Sand at Lv 24) is free to unlock: press it
before the upgrades. Unlocked rows are not upgrade targets (R-136 still raises Stone and Wood only). A row that reads
"Unlocks at Lv. 45" (Treats) has no button and is left alone; an unlock that shows any cost or spend word is backed
out of with needs_decision.

Route: home -> claim the Cart bubble (Strengthener.claim_cart) -> tap the Cart (Home.Cart) -> Cart panel (State.Cart)
-> a row's upgrade arrow -> Furniture Upgrade (State.FurnitureUpgrade): one tab per row along the top, the selected
row's "Lv. N -> Lv. N+1", its Upgrade Cost (icon + have/need per item) and "Upgrade x1".

Before every press the cost is read: each cost item must be one of the ordinary materials we have templates for
(Wood, Stone, Rolla: resource/image/cart/cost_*.png) and have >= need. An unrecognised cost item (Dawnium or anything
new) ends the run with needs_decision and the frame saved; a short material ends it with "short". A press that
doesn't raise the level, a missing Upgrade button, or an unexpected screen ends it too. Rows are capped by the bed's
Blessing Level: at the cap the button reads "Unlocks at Blessing Lv. N" (seen at Stone Lv 5 -> 6, Blessing Lv 5) and
the run ends "capped". No model calls.
"""

from __future__ import annotations

import logging
import re
import time
from typing import Optional

import cv2

from ..core import ui
from ..core.device import REPO_ROOT, save_unknown
from ..core.loop import Loop, banner, progress
from ..core.nav import Navigator
from ..vision.ocr import amount_in, zoomed_lines
from .strengthen import (HOME_SWEEP_LEFT, HOME_SWEEP_RIGHT, HOME_SWIPE_LEFT, HOME_SWIPE_MS, HOME_SWIPE_RIGHT,
                         Strengthener)

log = logging.getLogger("sxs.loops.cart")

ROWS = ("stone", "wood")  # mae's rows; order is the tie-break (R-136: Stone first when level)
TABS = {"rolla": (92, 150), "wood": (212, 150), "stone": (326, 150), "raw_ore": (440, 150),
        "battle_essence": (560, 150)}  # Furniture Upgrade, top row (same order as the Cart panel)
PANEL_ARROWS = {"rolla": (632, 461), "wood": (632, 536), "stone": (632, 611)}  # Cart panel, right of each row
NAME_ROI = [160, 360, 400, 55]  # selected row's name ("Stone")
NAMES = {"stone": r"^Stone$", "wood": r"^Wood$"}
LEVEL_ROI = [170, 410, 380, 70]  # "Lv. 3 -> Lv. 4"
COST_ICON_ROI = [40, 930, 640, 85]  # Upgrade Cost icons (centred, 3 today at x 238 / 360 / 482)
COST_TEXT_ROI = [40, 1008, 640, 36]  # "3.27K/65" under each icon
UPGRADE_ROI = [200, 1075, 320, 65]
UPGRADE_BUTTON = (360, 1107)
PANEL_BUTTONS_ROI = [480, 420, 210, 640]  # right end of the Cart panel's rows: upgrade arrows and "Unlock" buttons
POPUP_ROI = [0, 560, 720, 560]  # an unlock confirmation, if the game shows one (furniture popups put "Unlock" low)
MAX_UNLOCKS = 3
COST_TEMPLATES = ("wood", "stone", "rolla")
TEMPLATE_DIR = REPO_ROOT / "resource" / "image" / "cart"
MATCH = 0.75
SPEND_WORDS = r"Dawnium|Buy|Purchase|Recharge|Top ?up|\$|USD"  # never on this screen; seen = stop (R-043)


def _templates() -> dict:
    return {n: cv2.imread(str(TEMPLATE_DIR / f"cost_{n}.png")) for n in COST_TEMPLATES}


def cost_icons(frame) -> list[tuple[str, int]]:
    """Known cost icons in the Upgrade Cost row as (name, x centre), left to right."""
    x0, y0, w, h = COST_ICON_ROI
    roi = frame[y0:y0 + h, x0:x0 + w]
    found = []
    for name, t in _templates().items():
        if t is None:
            continue
        res = cv2.matchTemplate(roi, t, cv2.TM_CCOEFF_NORMED)
        _, best, _, loc = cv2.minMaxLoc(res)
        if best >= MATCH:
            found.append((name, x0 + loc[0] + t.shape[1] // 2))
    return sorted(found, key=lambda f: f[1])


def cost_fractions(det, frame) -> list[tuple[float, float, int]]:
    """(have, need, x centre) for every "have/need" under the cost icons, left to right."""
    out = []
    for t, box in sorted(det.read_text(COST_TEXT_ROI, frame=frame), key=lambda tb: tb[1][0]):
        m = re.fullmatch(r"\s*([\d.,]+\s*[KMB]?)\s*/\s*([\d.,]+\s*[KMB]?)\s*", t)
        if m:
            have, need = amount_in(m.group(1)), amount_in(m.group(2))
            if have is not None and need is not None:
                out.append((have, need, box[0] + box[2] // 2))
    return out


def levels_in(text: str) -> list[int]:
    return [int(n) for n in re.findall(r"Lv\.?\s*(\d+)", text)]


class CartUpgrader:
    def __init__(self, dev, det):
        self.dev, self.det = dev, det
        self.nav = Navigator(dev, det)
        self.st = Strengthener(dev, det)

    def _tap(self, xy, wait=1.5):
        self.dev.tap(*xy)
        time.sleep(wait)

    # --- reaching the screens -----------------------------------------------------------------------------------

    def open_panel(self, restart: bool = True) -> bool:
        """From anywhere: home, find the Cart on the sideways-scrolling scene, tap it until the Cart panel shows.
        Home can get stuck showing only sky, where no swipe moves it (R-100): if a full sweep finds no Cart,
        restart the game once and sweep again."""
        if self._sweep_for_cart():
            return True
        if not restart:
            return False
        log.info("no Cart on home after a full sweep (stuck on sky?, R-100): restarting the game")
        self.dev.stop_game()
        time.sleep(2)
        self.dev.start_game()
        progress("restarted")
        time.sleep(30)
        return self._sweep_for_cart()

    def _sweep_for_cart(self) -> bool:
        self.nav.go_home()
        right, left = HOME_SWIPE_RIGHT, HOME_SWIPE_LEFT
        # Home keeps its pan, and claim_cart's own sweep can end several screens off: sweep wide both ways.
        for i, swipe in enumerate([None] + [right] * HOME_SWEEP_RIGHT + [left] * HOME_SWEEP_LEFT):
            if swipe:
                self.dev.pan(*swipe, HOME_SWIPE_MS)  # adb fallback when MaaFramework's swipe stops (2026-11-11)
                progress(("sweep", i))
            hit = self.det.find("Home.Cart")
            if not hit:
                continue
            self._tap(ui.centre(hit.box), 2.5)
            state = self.det.detect().state
            if state == "reward_popup":  # loot came back between claim and tap: take it and tap again
                self._tap(ui.BELOW_POPUP, 2)
                self._tap(ui.centre(hit.box), 2.5)
                state = self.det.detect().state
            if state == "cart":
                progress("cart_panel")
                return True
            log.info("tapping the Cart gave %s", state)
            if state != "home":
                self.nav.go_home()
        return False

    def open_upgrade(self) -> bool:
        """Cart panel showing: open Furniture Upgrade through the Stone row's arrow."""
        self._tap(PANEL_ARROWS["stone"], 2.5)
        return self.det.detect().state == "furniture_upgrade"

    # --- R-137: free row unlocks --------------------------------------------------------------------------------

    @staticmethod
    def unlock_buttons(lines) -> list[tuple[int, int]]:
        """Centres of row buttons that read exactly "Unlock" (not "Unlocks at Lv. 45"), from OCR lines of the panel."""
        return [(b[0] + b[2] // 2, b[1] + b[3] // 2) for t, b in lines if re.fullmatch(r"\s*Unlock\s*!?\s*", t)]

    def unlock_rows(self) -> list[str]:
        """Cart panel showing: press every row's free Unlock (R-137). Returns what was unlocked; leaves the panel open
        (reopened if the unlock closed it). Stops on any cost or spend word."""
        done: list[str] = []
        for _ in range(MAX_UNLOCKS):
            frame = self.dev.screenshot()
            buttons = self.unlock_buttons(self.det.read_text(PANEL_BUTTONS_ROI, frame=frame))
            if not buttons:
                break
            x, y = buttons[0]
            row = " ".join(t for t, _ in self.det.read_text([150, y - 35, 330, 70], frame=frame)).strip() or f"row@{y}"
            log.info("Cart row %r has a free Unlock: pressing it (R-137)", row)
            self._tap((x, y), 2.5)
            state = self.det.detect().state
            if state != "cart":
                # A confirmation popup: read it before pressing anything (R-043: never spend).
                words = " ".join(t for t, _ in self.det.read_text(POPUP_ROI))
                if re.search(SPEND_WORDS, words, re.I) or re.search(r"\d+\s*/\s*\d+", words):
                    log.warning("unlock of %r asks for something (%s); backing out. frame %s", row, words,
                                save_unknown(self.dev, "cart_unlock"))
                    self.dev.back()
                    time.sleep(1.5)
                    done.append("needs_decision")
                    break
                confirm = self.unlock_buttons(self.det.read_text(POPUP_ROI))
                if confirm:
                    self._tap(confirm[0], 2.5)
                self._tap(ui.ABOVE_POPUP, 1.5)  # unlocked banner / reward card
            elif (x, y) in self.unlock_buttons(self.det.read_text(PANEL_BUTTONS_ROI)):
                log.warning("the Unlock on %r is still there after pressing it; leaving it. frame %s", row,
                            save_unknown(self.dev, "cart_unlock"))
                break
            done.append(row)
            progress(("unlocked", row))
            if self.det.detect().state != "cart" and not self.open_panel(restart=False):
                break
        return done

    # --- reading the Furniture Upgrade screen -------------------------------------------------------------------

    def select(self, row: str) -> Optional[int]:
        """Select a row's tab; return its current level, or None if the tab didn't switch to that row."""
        self._tap(TABS[row], 1.5)
        frame = self.dev.screenshot()
        name = " ".join(t for t, _ in self.det.read_text(NAME_ROI, frame=frame))
        if not re.search(NAMES[row], name.strip()):
            log.warning("tab %s shows %r", row, name)
            return None
        lv = levels_in(" ".join(zoomed_lines(self.det, frame, LEVEL_ROI)))
        return min(lv) if lv else None

    def read_cost(self) -> dict:
        """The selected row's next upgrade: {"items": [(name, have, need)], "ok": bool, "why": str}."""
        frame = self.dev.screenshot()
        icons, fracs = cost_icons(frame), cost_fractions(self.det, frame)
        words = " ".join(t for t, _ in self.det.read_text([0, 880, 720, 280], frame=frame))
        items = []
        for have, need, x in fracs:
            near = [n for n, ix in icons if abs(ix - x) < 60]
            items.append((near[0] if near else "unknown", have, need))
        button = " ".join(t for t, _ in self.det.read_text(UPGRADE_ROI, frame=frame))
        if re.search(SPEND_WORDS, words, re.I):
            return {"items": items, "ok": False, "why": "spend_word", "text": words}
        if not items:
            return {"items": items, "ok": False, "why": "no_cost", "text": words}
        if any(n == "unknown" for n, _, _ in items) or len(icons) < len(items):
            return {"items": items, "ok": False, "why": "unknown_currency", "text": words}
        if any(have < need for _, have, need in items):
            return {"items": items, "ok": False, "why": "short"}
        if re.search(r"Unlocks at", button):  # "Unlocks at Blessing Lv. 6": capped by the bed's Blessing Level
            return {"items": items, "ok": False, "why": "capped", "text": button}
        if not re.search(r"Upgrade", button):
            return {"items": items, "ok": False, "why": "no_button", "text": button}
        return {"items": items, "ok": True, "why": ""}

    # --- the task -----------------------------------------------------------------------------------------------

    @staticmethod
    def pick(levels: dict) -> str:
        """The row to raise: the lowest level; ties go in ROWS order (Stone first)."""
        return min(ROWS, key=lambda r: (levels[r], ROWS.index(r)))

    def run(self, check: bool = False, max_upgrades: int = 50) -> dict:
        banner(log, "Cart Upgrade", "raise the Cart's Stone and Wood rows evenly with ordinary materials (R-136)",
               "a cost we can't pay or don't recognise, a level that won't rise, or an unexpected screen")
        out = {"upgrades": [], "costs": []}
        out["claimed"] = self.st.claim_cart()
        progress(("claimed", out["claimed"]))
        if not self.open_panel():
            out["end"] = "no_cart"
            log.warning("Cart panel not found; frame %s", save_unknown(self.dev, "cart_panel"))
            self.nav.go_home()
            return out
        out["unlocked"] = self.unlock_rows() if not check else []
        if "needs_decision" in out["unlocked"]:
            out["end"] = "needs_decision"
            self.nav.go_home()
            return out
        if self.det.detect().state != "cart" and not self.open_panel(restart=False):
            out["end"] = "no_cart"
            self.nav.go_home()
            return out
        if not self.open_upgrade():
            out["end"] = "unknown_screen"
            log.warning("Furniture Upgrade did not open; frame %s", save_unknown(self.dev, "cart_upgrade"))
            self.nav.go_home()
            return out
        levels = {}
        for r in ROWS:
            lv = self.select(r)
            if lv is None:
                out["end"] = "unreadable_level"
                log.warning("could not read the %s level; frame %s", r, save_unknown(self.dev, "cart_level"))
                self.nav.go_home()
                return out
            levels[r] = lv
        out["start"] = dict(levels)
        log.info("Cart levels: %s", levels)
        while len(out["upgrades"]) < max_upgrades:
            row = self.pick(levels)
            if self.select(row) != levels[row]:
                out["end"] = "unreadable_level"
                break
            cost = self.read_cost()
            out["costs"].append({"row": row, "level": levels[row], **cost})
            log.info("%s Lv %d -> %d costs %s", row, levels[row], levels[row] + 1,
                     ", ".join(f"{n} {have:g}/{need:g}" for n, have, need in cost["items"]) or "nothing read")
            if not cost["ok"]:
                out["end"] = {"unknown_currency": "needs_decision", "spend_word": "needs_decision"}.get(
                    cost["why"], cost["why"])
                if out["end"] == "needs_decision":
                    log.warning("cost not ordinary materials (%s); frame %s", cost.get("text", ""),
                                save_unknown(self.dev, "cart_cost"))
                break
            if check:
                out["end"] = "checked"
                break
            self._tap(UPGRADE_BUTTON, 2.5)
            state = self.det.detect().state
            if state != "furniture_upgrade":
                self._tap(ui.BELOW_POPUP, 2)  # a level-up banner or reward overlay, if any
                if self.det.detect().state != "furniture_upgrade":
                    out["end"] = "unknown_screen"
                    log.warning("after Upgrade: %s; frame %s", state, save_unknown(self.dev, "cart_after"))
                    break
            new = self.select(row)
            if new is None or new <= levels[row]:
                out["end"] = "no_change"
                log.info("%s stayed at Lv %s after Upgrade: stopping", row, new)
                break
            levels[row] = new
            out["upgrades"].append(f"{row} {new}")
            progress((row, new))
            log.info("[Cart] %s -> Lv %d (stone %d, wood %d)", row, new, levels["stone"], levels["wood"])
        else:
            out["end"] = "max_upgrades"
        out["levels"] = levels
        self.nav.go_home()
        if out["end"] in ("short", "capped") and out["upgrades"]:
            out["end"] = "done"
        return out


def _args(p) -> None:
    p.add_argument("--check", action="store_true", help="read levels and the next cost, press nothing")
    p.add_argument("--max", type=int, default=50, help="most upgrades this run")


def _run(ctx, opts):
    return CartUpgrader(ctx.dev, ctx.det).run(opts.check, opts.max)


LOOP = Loop("cart", "Cart Upgrade", "upgrade the Cart's Stone and Wood rows evenly (R-136)", _run, _args,
            ok={"done", "short", "capped", "checked", "max_upgrades"})
