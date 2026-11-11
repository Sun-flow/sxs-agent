"""Workbench relics: activate new relics, enhance displayed ones in bands of one level, ascend with own shards.

    python -m sxs relics           # activate, ascend, enhance, claim Goals
    python -m sxs relics --check   # read each element's displayed relic levels only

Rules: R-172 (activate; Enhance with Chrono Sand and Rolla; never Replace; Ascend with 20 own shards), R-105 (bands
of one level, element by element, highest affinity first: `upgrade.relic_plan`). Flowchart: docs/loops/gacha.md.

Enhance is pressed only while its blue pip shows and every cost reads have >= need, so the screen's ticked
"Auto-combine on material shortage" never has a shortage to fill (what it would combine is an open question).
The relic card's left button is Replace: the code taps the button whose text reads Enhance, never a fixed point.
No model calls.
"""

from __future__ import annotations

import logging
import re
import time
from typing import Optional

import cv2

from ..actions.home import find_on_home, template_finder
from ..core import ui
from ..core.device import save_unknown
from ..core.loop import Loop, banner, progress
from ..core.nav import Navigator
from ..policy import claims
from ..vision.badges import find_badges, find_up_pips, near_any
from ..vision.ocr import amount_in, boxes_of, read_fraction
from .upgrade import relic_plan

log = logging.getLogger("sxs.loops.relics")

# Relic screen (docs/screens/home/workbench_relic_activate.png)
TITLE_ROI = [20, 20, 330, 70]
RELIC_TITLE = re.compile(r"^([A-Z][a-z]+)\s*(\d+)\s*/\s*(\d+)")  # "Light 1/280"
AFFINITY_ROI = [60, 92, 135, 40]
TAB_XS = [80, 175, 268, 360, 452, 545, 637]  # element tabs along y = 1120
TAB_Y, TAB_BADGE_FROM = 1120, (34, -23)
GRID_ROI = [0, 490, 720, 570]  # owned relics under their rarity headers
ICON_FROM_BADGE = (-65, 50)
DISPLAY = [(110, 335), (277, 335), (443, 335), (610, 335)]  # Resonance display slots
RELIC_TAB, GOALS_TAB = (290, 1218), (563, 1218)
GOALS_BADGE, GOALS_BADGE_ROI = (690, 1194), [600, 1150, 120, 80]
CONTINUE = (360, 1200)  # "ACTIVATED ... Tap to Continue"
# Relic card (workbench_relic_card.png): Replace (233, 1041) | Enhance (486, 1041)
CARD_BUTTONS_ROI = [100, 1005, 520, 75]
# Enhance Relic / Relic Ascension (workbench_enhance_relic.png, workbench_relic_ascension.png)
TOP_SLOTS = [(165, 165), (295, 165), (423, 165), (552, 165)]
LEVEL_ROI = [150, 515, 420, 60]  # "+1 -> +2"
COST_ROI = [40, 990, 640, 40]  # "7.98K/1K", "188K/1.8K"; "3/20" on Ascension
ENHANCE_BUTTON = (360, 1084)
BUTTON_PIP, BUTTON_PIP_ROI = (502, 1062), [430, 1020, 140, 80]
SUB_ENHANCE, SUB_ASCEND = (290, 1218), (563, 1218)
FILLED_SAT = 60  # mean saturation round a slot centre: a relic icon above, the grey "+" below
MAX_PRESSES = 30
OK = {"done", "nothing", "check", "no_template"}


def relic_title(text: str) -> Optional[str]:
    """Element name from the Relic screen's title ("Light 1/280" -> "Light"), else None."""
    m = RELIC_TITLE.search(text.strip())
    return m.group(1) if m else None


def level_in(texts: list[tuple[str, list[int]]]) -> Optional[int]:
    """Current level from "+1 -> +2": the leftmost "+N" (OCR order is not left to right)."""
    for t, _ in sorted(texts, key=lambda tb: tb[1][0]):
        m = re.fullmatch(r"\+?(\d+)", t.strip())
        if m:
            return int(m.group(1))
    return None


def costs_in(texts: list[str]) -> list[tuple[float, float]]:
    """(have, need) for every "have/need" cost ("7.98K/1K" -> (7980, 1000))."""
    out = []
    for t in texts:
        m = re.fullmatch(r"\s*([\d.,]+\s*[KMB]?)\s*/\s*([\d.,]+\s*[KMB]?)\s*", t)
        if m:
            have, need = amount_in(m.group(1)), amount_in(m.group(2))
            if have is not None and need is not None:
                out.append((have, need))
    return out


def affordable(costs: list[tuple[float, float]]) -> bool:
    """Every cost covered, so auto-combine never kicks in. No readable cost means no."""
    return bool(costs) and all(have >= need for have, need in costs)


def filled(frame, xy) -> bool:
    x, y = xy
    hsv = cv2.cvtColor(frame[y - 15:y + 15, x - 15:x + 15], cv2.COLOR_BGR2HSV)
    return float(hsv[..., 1].mean()) > FILLED_SAT


class RelicBench:
    def __init__(self, dev, det):
        self.dev, self.det = dev, det
        self.nav = Navigator(dev, det)
        self._tap = self.nav.tap
        self.presses = 0

    # --- reading -------------------------------------------------------------------------------------------------

    def _title(self) -> str:
        return " ".join(t for t, _ in self.det.read_text(TITLE_ROI))

    def element(self) -> Optional[str]:
        return relic_title(self._title())

    def _badges(self, roi) -> list[tuple[int, int]]:
        seen: list[tuple[int, int]] = []
        for k in range(2):  # badges pulse
            if k:
                time.sleep(0.4)
            seen += [b for b in find_badges(self.dev.screenshot(), roi) if not near_any(seen, b, 12)]
        return seen

    def _level(self) -> Optional[int]:
        return level_in(self.det.read_text(LEVEL_ROI))

    # --- navigation ----------------------------------------------------------------------------------------------

    def open(self) -> str:
        find = template_finder("workbench")
        if find is None:
            log.warning("no resource/image/home/workbench.png yet: capture it (live test plan, step 1)")
            return "no_template"
        at = find_on_home(self.dev, self.det, find)
        if not at:
            return "not_found"
        self._tap(at, 3)
        if self.element():
            return "ok"
        log.warning("the Workbench tap did not open the Relic screen (%r); frame %s", self._title(),
                    save_unknown(self.dev, "relics_open"))
        return "unknown_screen"

    def open_enhance(self, tab_x: int) -> bool:
        """Relic screen: element tab, display slot 1, the card's Enhance (found by its text, never Replace)."""
        self._tap((tab_x, TAB_Y), 1.5)
        if not filled(self.dev.screenshot(), DISPLAY[0]):
            return False
        self._tap(DISPLAY[0], 2)
        buttons = [b for t, b in self.det.read_text(CARD_BUTTONS_ROI) if re.fullmatch(r"\s*Enhance\s*", t)]
        if not buttons:
            log.warning("relic card without an Enhance button; closing; frame %s", save_unknown(self.dev, "relics_card"))
            self._tap(ui.BELOW_POPUP, 1.5)
            return False
        self._tap(ui.centre(buttons[0]), 2.5)
        title = self._title()
        if "Relic Ascension" in title:
            self._tap(SUB_ENHANCE, 1.5)
            title = self._title()
        if "Enhance Relic" not in title:
            log.warning("Enhance Relic did not open (%r); frame %s", title, save_unknown(self.dev, "relics_enhance"))
            return False
        return True

    def back_to_relics(self) -> bool:
        self._tap(ui.BACK_ARROW, 2.5)
        return self.element() is not None

    # --- steps ---------------------------------------------------------------------------------------------------

    def activate_all(self) -> int:
        """Each element tab with "!": tap every relic that carries "!" (Activate); close "ACTIVATED"."""
        n = 0
        lit = [x for x in TAB_XS if near_any(self._badges([0, 1060, 720, 80]), (x + TAB_BADGE_FROM[0], TAB_Y + TAB_BADGE_FROM[1]), 25)]
        for x in lit:
            self._tap((x, TAB_Y), 1.5)
            tried: list[tuple[int, int]] = []
            for _ in range(8):
                badges = [b for b in self._badges(GRID_ROI) if not near_any(tried, b, 20)]
                if not badges:
                    break
                bx, by = badges[0]
                tried.append((bx, by))
                self._tap((bx + ICON_FROM_BADGE[0], by + ICON_FROM_BADGE[1]), 2.5)
                text = " ".join(t for t, _ in self.det.read_text([100, 260, 520, 120]))
                if re.search(r"ACTIVATED", text):
                    self._tap(CONTINUE, 2)
                    n += 1
                    progress(("activated", n))
                    log.info("relic activated (%s tab)", self.element())
                elif not self.element():
                    self._tap(ui.BELOW_POPUP, 1.5)  # opened its card instead: close it, try the next one
        log.info("relics activated: %d", n)
        return n

    def read_levels(self) -> list[Optional[int]]:
        """Enhance Relic open: +level of each filled top-row slot (None for an empty "+" slot)."""
        frame = self.dev.screenshot()
        out: list[Optional[int]] = []
        for xy in TOP_SLOTS:
            if not filled(frame, xy):
                out.append(None)
                continue
            self._tap(xy, 1.2)
            out.append(self._level())
        return out

    def ascend_ready(self, slots: list[int]) -> int:
        """Enhance Relic open: Ascension sub-tab, Ascend each listed slot whose own shards read n/20 with n >= 20
        (never "universal materials", which the bot leaves unticked)."""
        self._tap(SUB_ASCEND, 1.5)
        n = 0
        for i in slots:
            self._tap(TOP_SLOTS[i], 1.2)
            frame = self.dev.screenshot()
            frac = read_fraction(self.det, COST_ROI, frame)
            # Two signals: the shard icon can OCR as a leading "1" ("3/20" read as "13/20"), so the Ascend
            # button's own blue pip must agree that it is affordable.
            pip = near_any(find_up_pips(frame, BUTTON_PIP_ROI), BUTTON_PIP, 30)
            if pip and frac and frac[1] > 0 and frac[0] >= frac[1]:
                self._tap(ENHANCE_BUTTON, 3)  # Ascend sits where Enhance does
                if self.det.detect().state in ("tap_to_continue", "reward_popup"):
                    self._tap(CONTINUE, 2)
                n += 1
                log.info("relic slot %d ascended (%s shards)", i, frac)
        self._tap(SUB_ENHANCE, 1.5)
        return n

    def enhance_once(self, slot: int) -> str:
        """Enhance Relic open: one press on `slot`. "up", "short" (no pip, or a cost not covered) or "stuck"."""
        self._tap(TOP_SLOTS[slot], 1.2)
        before = self._level()
        frame = self.dev.screenshot()
        costs = costs_in([t for t, _ in self.det.read_text(COST_ROI, frame)])
        if not near_any(find_up_pips(frame, BUTTON_PIP_ROI), BUTTON_PIP, 30) or not affordable(costs):
            log.info("relic slot %d at +%s: short (costs %s)", slot, before, costs)
            return "short"
        if not boxes_of(self.det, [250, 1050, 220, 70], r"Enhance"):
            log.warning("the button under the costs doesn't read Enhance; not pressing")
            return "stuck"
        self._tap(ENHANCE_BUTTON, 2.5)
        self.presses += 1
        if self.det.detect().state in ("tap_to_continue", "reward_popup"):
            self._tap(CONTINUE, 1.5)
        after = self._level()
        progress(("relic", slot, after))
        if before is not None and after is not None and after > before:
            log.info("relic slot %d: +%d -> +%d", slot, before, after)
            return "up"
        return "stuck"

    def survey(self, ascend: bool) -> tuple[dict, dict, dict]:
        """Every element tab with a relic on display: its affinity and displayed levels (R-105 needs both).
        Returns (levels {element: [lv]}, affinity {element: n}, tabs {element: tab x})."""
        levels, affinity, tabs = {}, {}, {}
        for x in TAB_XS:
            self._tap((x, TAB_Y), 1.5)
            element = self.element()
            if not element or element in levels or not filled(self.dev.screenshot(), DISPLAY[0]):
                continue
            aff = re.search(r"(\d+)", " ".join(t for t, _ in self.det.read_text(AFFINITY_ROI)).replace("O", "0"))
            if not self.open_enhance(x):
                self.nav.go_home()
                raise RuntimeError("enhance screen")
            slots = self.read_levels()
            owned = [i for i, lv in enumerate(slots) if lv is not None]
            if ascend and owned:
                self.ascend_ready(owned)
                slots = self.read_levels()
            levels[element] = [lv for lv in slots if lv is not None]
            affinity[element] = int(aff.group(1)) if aff else 0
            tabs[element] = x
            log.info("%s: affinity %s, displayed relics %s", element, affinity[element], levels[element])
            progress(("survey", element))
            if not self.back_to_relics():
                raise RuntimeError("relic screen")
        return levels, affinity, tabs

    def enhance_banded(self, levels: dict, affinity: dict, tabs: dict) -> int:
        """relic_plan (R-105) one press at a time; a relic that is short or doesn't move is left at its level."""
        work = {e: list(lv) for e, lv in levels.items()}
        left_out: set = set()
        here = None
        ups = 0
        BIG = 10 ** 6
        while self.presses < MAX_PRESSES:
            view = {e: [BIG if (e, i) in left_out else lv for i, lv in enumerate(lvs)] for e, lvs in work.items()}
            if not view or all(v == BIG for lvs in view.values() for v in lvs):
                break
            element, i = relic_plan(view, affinity)
            if element != here:
                if here is not None and not self.back_to_relics():
                    break
                if not self.open_enhance(tabs[element]):
                    left_out.update((element, k) for k in range(len(work[element])))
                    here = None
                    continue
                here = element
            got = self.enhance_once(i)
            if got == "up":
                work[element][i] += 1
                ups += 1
            else:
                left_out.add((element, i))
        if here is not None:
            self.back_to_relics()
        log.info("relic levels after: %s (%d presses)", work, self.presses)
        return ups

    def claim_goals(self) -> int:
        if not near_any(self._badges(GOALS_BADGE_ROI), GOALS_BADGE, 40):
            return 0
        self._tap(GOALS_TAB, 2.5)
        n = claims.claim_all(self.dev, self.det)
        self._tap(RELIC_TAB, 1.5)
        return n

    def run(self, check: bool = False) -> dict:
        banner(log, "Relics", "activate new relics, ascend with own shards, enhance displayed relics in bands of one "
               "level with Chrono Sand and Rolla (never Replace)",
               f"nothing lit, materials short, {MAX_PRESSES} presses, or an unexpected screen")
        opened = self.open()
        if opened != "ok":
            if opened != "no_template":
                self.nav.go_home()
            return {"end": opened}
        progress("relics_open")
        out: dict = {"activated": 0, "enhanced": 0, "goals": 0}
        try:
            if not check:
                out["activated"] = self.activate_all()
            levels, affinity, tabs = self.survey(ascend=not check)
            out["levels"] = levels
            if not check:
                out["enhanced"] = self.enhance_banded(levels, affinity, tabs)
                out["goals"] = self.claim_goals()
        except RuntimeError as e:
            log.warning("relics: lost the %s; frame %s", e, save_unknown(self.dev, "relics_lost"))
            self.nav.go_home()
            return {**out, "end": "unknown_screen"}
        self.nav.go_home()
        end = "check" if check else ("done" if any(out[k] for k in ("activated", "enhanced", "goals")) else "nothing")
        log.info("relics: %s", out)
        return {**out, "end": end}


def _args(p) -> None:
    p.add_argument("--check", action="store_true", help="read each element's displayed relic levels only")


def _run(ctx, opts):
    return RelicBench(ctx.dev, ctx.det).run(check=opts.check)


LOOP = Loop("relics", "Relics", "Workbench: activate new relics, enhance in bands with Chrono Sand, never Replace",
            _run, _args, ok=OK, budget=240)
