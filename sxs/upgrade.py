"""Upgrade Loop: follow every red "!" on the Character screen and apply the free or soft-resource upgrade behind it.

    python -m sxs.upgrade                 # all badges on the Character screen
    python -m sxs.upgrade --only skills   # one pass: skills, gear, class, rank, relics

mae, 2026-11-04: any "!" on the character screen means an upgrade is available: always check and apply (R-080).
What each badge leads to (rules R-080, R-104, R-115 to R-119):

  gear slots   Enhance Gear in 5-level bands (Strengthener.enhance_gear), then Resonance (Activate the bonus
               for all 4 pieces at +5/+10/...), then the Enhancement Goals tab.
  Skill        Quick Upgrade (beside the lower-right charm: levels every skill with Battle Essence in one tap),
               Ascend techniques whose card shows "!" (10 of their own shards), fill empty charm slots with
               owned charms, claim the Skill Goals tabs (Level, Quality).
  Class        Claim class badges (tap a class card with "!"), level the class with them (Upgrade tab), claim
               Total Class Level goals. Never "Change Class": that's mae's decision.
  Apprentice   Rank Advancement: claim the Level and Power goals; Advance only when its button carries "!"
               (the game says every material is there).
  Relics       Not unlocked yet: banded in steps of 1, element by element in affinity order (relic_plan).

Spends only Rolla, ore, Battle Essence, shards, class badges and (later) sand. Never Dawnium, never a button with a
spend word (claims.SPEND), never Rcmd Loadouts. Every pass has a tap budget, checks that each tap changed
something, and saves the frame to captures/unknown/ when a screen isn't the expected one. No model calls.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import time
from typing import Optional

from . import claims, nav
from .badges import find_badges, near
from .device import Device, banner, save_unknown
from .state import StateDetector
from .strengthen import CHARM_EQUIP, CHARM_LIST, CHARM_SLOTS, GEAR_SLOTS, ITEM_CARD_ENHANCE, Strengthener

log = logging.getLogger("sxs.upgrade")

# Character screen (720x1280)
SKILL_BUTTON = (296, 760)
CLASS_BUTTON = (424, 760)
RANK_BADGE = (590, 916)  # "Apprentice I" rank badge right of the level bar
# Skill page
QUICK_UPGRADE_ROI = [440, 600, 170, 70]  # the "Upgrade" caption under the Quick Upgrade icon
QUICK_UPGRADE = (524, 600)
TECHNIQUE_COLUMN = [(92, 270), (92, 386), (92, 502), (92, 618)]
TAB_TECHNIQUE, TAB_CHARM, TAB_SHARD = (110, 800), (276, 800), (442, 800)
BOTTOM_LEFT_TAB, BOTTOM_RIGHT_TAB = (280, 1216), (560, 1216)  # Skill | Goals, Upgrade | Ascend, Rank | Goals ...
GOALS_SUBTABS = [(260, 1120), (450, 1120)]  # Level | Quality (skills), Level | Power (rank)
TECHNIQUE_CARD_ENHANCE = (490, 946)
ASCEND_BUTTON = (360, 1084)
# Class
CLASS_TABS = {"change": (230, 1216), "hierarchy": (428, 1216), "goals": (610, 1216)}
CLASS_CARD_FROM_BADGE = (-75, 125)  # class card centre relative to its "!" badge
BADGE_POPUP_OK = (360, 916)
CLASS_UPGRADE_BUTTON = (360, 1090)
# Rank
RANK_ADVANCE = (360, 1088)
# Enhance Gear
RESONANCE = (620, 256)
CLOSE_BELOW = (360, 1230)

TAP_BUDGET = 25  # per button: far above any real need, so a dead button can't loop forever
ELEMENT_RELICS = 4  # relics per element (R-105)
RELIC_BAND = 1


def relic_plan(levels: dict[str, list[int]], affinity: dict[str, float]) -> Optional[tuple[str, int]]:
    """Which relic to enhance next (mae, 2026-11-04, R-105): bands of 1 level; inside a band, finish one element's
    4 relics before the next element; elements in order of the character's affinity, highest first; every element
    reaches the band before any relic goes past it. Returns (element, relic index) or None when nothing is owned."""
    owned = {e: lv for e, lv in levels.items() if lv}
    if not owned:
        return None
    target = min(min(lv) for lv in owned.values()) + RELIC_BAND
    for element in sorted(owned, key=lambda e: -affinity.get(e, 0)):
        for i, lv in enumerate(owned[element]):
            if lv < target:
                return element, i
    return None  # unreachable: the lowest relic is always below target


class Upgrader:
    def __init__(self, dev: Device, det: StateDetector):
        self.dev, self.det = dev, det
        self.nav = nav.Navigator(dev, det)
        self.st = Strengthener(dev, det)

    def _tap(self, xy, wait=2.0):
        self.dev.tap(*xy)
        time.sleep(wait)

    def _badges(self, roi=None, frames: int = 2) -> list[tuple[int, int]]:
        """Badges pulse: union over a couple of frames."""
        seen: list[tuple[int, int]] = []
        for i in range(frames):
            if i:
                time.sleep(0.4)
            for b in find_badges(self.dev.screenshot(), roi):
                if not near(seen, b, 12):
                    seen.append(b)
        return seen

    def _text(self, roi) -> str:
        return " ".join(t for t, _ in self.det.read_text(roi))

    def _character(self) -> bool:
        self.nav.go_home()
        try:
            self.nav.tap_and_expect(nav.NAV_CHARACTER, "character")
            return True
        except RuntimeError as e:
            log.warning("%s; frame %s", e, save_unknown(self.dev, "upgrade_character"))
            return False

    def claim_goals(self, tab=BOTTOM_RIGHT_TAB, subtabs=()) -> int:
        """Open a Goals tab and press its free Claim buttons, sub-tab by sub-tab."""
        self._tap(tab, 2.5)
        n = 0
        for sub in subtabs or [None]:
            if sub:
                self._tap(sub, 1.5)
            n += claims.claim_all(self.dev, self.det)
        log.info("goals claimed: %d", n)
        return n

    def _press_while_badged(self, button, roi_pad=70, wait=2.5) -> int:
        """Tap a button while the "!" on it stays (the game shows it only while the upgrade is affordable)."""
        n = 0
        for _ in range(TAP_BUDGET):
            x, y = button
            if not near(self._badges([max(0, x - 200), max(0, y - 80), 400, 160]), (x + 100, y - 20), 140):
                break
            if any(claims.SPEND.search(t) for t, _ in self.det.read_text([0, y - 60, 720, 120])):
                log.warning("spend word next to %s; not tapping", button)
                break
            self._tap(button, wait)
            n += 1
        return n

    # --- passes ---

    def skills(self) -> dict:
        """Skill page: Quick Upgrade, ascend badged techniques, fill empty charm slots, claim Skill Goals."""
        if not self._character():
            return {"skills": "unknown_screen"}
        self._tap(SKILL_BUTTON, 2.5)
        if self.det.detect().state != "skill_page":
            return {"skills": f"unknown_screen ({save_unknown(self.dev, 'upgrade_skill')})"}
        out = {"quick_upgrades": 0, "ascended": 0, "charms": 0, "goals": 0}
        for _ in range(5):  # one tap usually spends all the essence; the button vanishes when nothing is affordable
            caption = [b for t, b in self.det.read_text(QUICK_UPGRADE_ROI) if re.search(r"Upgrade", t)]
            if not caption:
                break
            x, y, w, h = caption[0]
            self._tap((x + w // 2, y - 30), 3)
            out["quick_upgrades"] += 1
        for slot in TECHNIQUE_COLUMN:
            if not near(self._badges([0, 180, 220, 500]), (slot[0] + 40, slot[1] - 40), 40):
                continue
            self._tap(slot, 2)
            self._tap(TECHNIQUE_CARD_ENHANCE, 2.5)
            if self.det.detect().state != "technique_upgrade":
                log.warning("technique card did not open Upgrade; frame %s", save_unknown(self.dev, "upgrade_tech"))
                self.nav.go_home()
                return out
            self._tap(BOTTOM_RIGHT_TAB, 2)  # Ascend tab
            out["ascended"] += self._press_while_badged(ASCEND_BUTTON, wait=3.5)
            self._tap(nav.BACK_ARROW, 2.5)
        if near(self._badges([200, 740, 160, 80]), (313, 780), 30):
            self._tap(TAB_CHARM, 1.5)
            out["charms"] = self._fill_charms()
        if near(self._badges([620, 1150, 100, 80]), (688, 1193), 30):
            out["goals"] = self.claim_goals(BOTTOM_RIGHT_TAB, GOALS_SUBTABS)
        log.info("skills: %s", out)
        return out

    def _fill_charms(self) -> int:
        """Charm tab open on the Skill page: put owned charms into empty slots (the right column)."""
        import cv2  # noqa: F401  (Strengthener._filled uses it)
        equipped = 0
        for _ in range(len(CHARM_SLOTS)):
            frame = self.dev.screenshot()
            empty = [xy for xy in CHARM_SLOTS if not self.st._filled(frame, xy)]
            owned = [xy for xy in CHARM_LIST if self.st._filled(frame, xy)]
            if not empty or not owned:
                break
            self._tap(owned[0], 2)
            if not re.search(r"\bEquip\b", self._text([60, 850, 300, 100])):
                self._tap(CLOSE_BELOW, 1.5)
                break
            self._tap((228, 898), 2)  # Equip (left button on the charm card)
            self._tap(empty[0], 2)
            equipped += 1
        return equipped

    def gear(self) -> dict:
        """Banded enhancement, then Resonance and Enhancement Goals."""
        self.st.enhance_gear()
        if not self._character():
            return {"gear": "unknown_screen"}
        self._tap(GEAR_SLOTS[0], 2)
        self._tap(ITEM_CARD_ENHANCE, 2.5)
        if self.det.detect().state != "enhance_gear":
            return {"gear": f"unknown_screen ({save_unknown(self.dev, 'upgrade_gear')})"}
        out = {"resonance": 0, "goals": 0}
        if near(self._badges([560, 200, 160, 80]), (700, 236), 50):
            self._tap(RESONANCE, 2.5)
            if self.det.detect().state == "gear_resonance":
                for _ in range(8):
                    hits = [b for t, b in self.det.read_text([400, 120, 320, 1000]) if t.strip() == "Activate"]
                    if not hits:
                        break
                    x, y, w, h = hits[0]
                    self._tap((x + w // 2, y + h // 2), 2.5)
                    self._tap(CLOSE_BELOW, 1.5)  # the "Resonated" banner
                    out["resonance"] += 1
                self._tap(nav.BACK_ARROW, 2.5)
        if near(self._badges([620, 1150, 100, 80]), (688, 1193), 30):
            out["goals"] = self.claim_goals()
        log.info("gear: %s", out)
        return out

    def class_levels(self) -> dict:
        """Class Hierarchy: claim badges and level each class card that shows "!"; claim Total Class Level goals."""
        if not self._character():
            return {"class": "unknown_screen"}
        self._tap(CLASS_BUTTON, 2.5)
        if self.det.detect().state != "class_page":
            return {"class": f"unknown_screen ({save_unknown(self.dev, 'upgrade_class')})"}
        out = {"levels": 0, "goals": 0}
        self._tap(CLASS_TABS["hierarchy"], 2.5)
        done: list[tuple[int, int]] = []
        for _ in range(6):
            cards = [b for b in self._badges([0, 140, 720, 980]) if not near(done, b, 20)]
            if not cards:
                break
            bx, by = cards[0]
            done.append((bx, by))
            self._tap((bx + CLASS_CARD_FROM_BADGE[0], by + CLASS_CARD_FROM_BADGE[1]), 3)
            if re.search(r"Badge Received", self._text([100, 160, 520, 80])):
                self._tap(BADGE_POPUP_OK, 2.5)
            if re.search(r"Change Class|Unlock", self._text([0, 0, 720, 160])) and \
                    self.det.detect().state != "class_page":
                log.warning("class card opened something else; backing out")
                self._tap(nav.BACK_ARROW, 2)
                continue
            self._tap(BOTTOM_RIGHT_TAB, 2.5)  # Upgrade tab
            out["levels"] += self._press_while_badged(CLASS_UPGRADE_BUTTON, wait=3)
            self._tap(nav.BACK_ARROW, 2.5)
        if near(self._badges([560, 1150, 160, 80]), (688, 1193), 40):
            out["goals"] = self.claim_goals(CLASS_TABS["goals"])
        log.info("class: %s", out)
        return out

    def rank(self) -> dict:
        """Rank Advancement: claim goals; Advance only when its button carries "!"."""
        if not self._character():
            return {"rank": "unknown_screen"}
        self._tap(RANK_BADGE, 2.5)
        if self.det.detect().state != "rank_advancement":
            return {"rank": f"unknown_screen ({save_unknown(self.dev, 'upgrade_rank')})"}
        out = {"advanced": self._press_while_badged(RANK_ADVANCE, wait=4), "goals": 0}
        if near(self._badges([620, 1150, 100, 80]), (688, 1193), 30):
            out["goals"] = self.claim_goals(BOTTOM_RIGHT_TAB, GOALS_SUBTABS)
        log.info("rank: %s", out)
        return out

    def relics(self) -> dict:
        """Relics aren't unlocked on the account yet (2026-11-04). When they are: map the screen, read each
        element's 4 relic levels and the affinities, and enhance one level at a time with relic_plan()."""
        log.info("relics: not unlocked yet; nothing to do")
        return {"relics": "not_unlocked"}

    # --- the loop ---

    PASSES = ["skills", "gear", "class_levels", "rank", "relics"]

    def run(self, only: Optional[set] = None) -> dict:
        passes = [p for p in self.PASSES if not only or p in only]
        banner(log, "Upgrade", f"apply every upgrade the Character screen's \"!\" marks offer ({', '.join(passes)})",
               "each pass done once, its tap budget spent, or an unexpected screen")
        results: dict = {}
        if not self._character():
            return {"end": "unknown_screen"}
        frame_badges = self._badges()
        log.info("character screen badges: %s", frame_badges)
        wanted = {
            "skills": near(frame_badges, (SKILL_BUTTON[0] + 30, SKILL_BUTTON[1] - 30), 50),
            "gear": any(near(frame_badges, (x + 40, y - 40), 50) for x, y in GEAR_SLOTS),
            "class_levels": near(frame_badges, (CLASS_BUTTON[0] + 30, CLASS_BUTTON[1] - 30), 50),
            "rank": near(frame_badges, (RANK_BADGE[0] + 90, RANK_BADGE[1] - 30), 70),
            "relics": False,
        }
        for p in passes:
            if not wanted[p] and not only:
                results[p] = "no_badge"
                continue
            try:
                results[p] = getattr(self, p)()
            except Exception as e:  # noqa: BLE001  one pass must not take the loop down
                log.warning("[%s] failed: %s; frame %s", p, e, save_unknown(self.dev, f"upgrade_{p}"))
                results[p] = "error"
            self.nav.go_home()
        log.info("upgrade: %s", results)
        return results


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--only", help="comma-separated passes: " + ", ".join(Upgrader.PASSES))
    args = p.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    dev = Device()
    only = set(args.only.split(",")) if args.only else None
    print(json.dumps(Upgrader(dev, StateDetector(dev)).run(only), default=str), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
