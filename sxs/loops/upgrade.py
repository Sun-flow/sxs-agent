"""Upgrade Loop: follow every red "!" on the Character screen and apply the free or soft-resource upgrade behind it.

    python -m sxs upgrade                 # all badges on the Character screen
    python -m sxs upgrade --only skills   # one pass: skills, gear, class, rank, relics

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

import logging
import re
import time
from typing import Optional

from ..core import ui
from ..core.device import save_unknown
from ..core.loop import Loop, banner, progress, task
from ..core.nav import Navigator
from ..core.ui import CLASS_BUTTON, RANK_BADGE, SKILL_BUTTON, TECHNIQUE_CARD_ENHANCE
from ..policy import claims
from ..vision.badges import find_badges, find_up_pips, near_any
from ..vision.ocr import boxes_of, read_line
from .strengthen import CHARM_LIST, CHARM_SLOTS, GEAR_SLOTS, ITEM_CARD_ENHANCE, Strengthener

log = logging.getLogger("sxs.loops.upgrade")

# Character screen (720x1280)
# Skill page
QUICK_UPGRADE_ROI = [440, 600, 170, 70]  # the "Upgrade" caption under the Quick Upgrade icon
TECHNIQUE_COLUMN = [(92, 270), (92, 386), (92, 502), (92, 618)]
SKILL_ICON_ROIS = [[0, 180, 220, 500], [520, 180, 200, 500]]  # equipped techniques (left), charms (right)
BAG_ROW_ROI = [0, 830, 720, 140]  # owned items under the Technique / Charm tabs
ICON_FROM_BADGE = (-40, 40)  # icon centre relative to its "!"
CARD_BUTTONS_ROI = [80, 860, 560, 120]  # technique / charm card: Replace|Remove, Enhance
TAB_TECHNIQUE, TAB_CHARM, TAB_SHARD = (110, 800), (276, 800), (442, 800)
BOTTOM_LEFT_TAB, BOTTOM_RIGHT_TAB = (280, 1216), (560, 1216)  # Skill | Goals, Upgrade | Ascend, Rank | Goals ...
GOALS_SUBTABS = [(260, 1120), (450, 1120)]  # Level | Quality (skills), Level | Power (rank)
ASCEND_BUTTON = (360, 1084)
# Class
CLASS_TABS = {"change": (230, 1216), "hierarchy": (428, 1216), "goals": (610, 1216)}
CLASS_CARD_FROM_BADGE = (-75, 125)  # class card centre relative to its "!" badge
BADGE_POPUP_OK = (360, 916)
CLASS_UPGRADE_BUTTON = (360, 1090)
# Rank (docs/screens/character/rank_advancement_apprentice3.png)
RANK_ADVANCE = (360, 1088)
RANK_LEVEL_ROI = [40, 595, 280, 40]  # "Level: 30/30" (left column; "Max Level: 40" is on the right)
RANK_COST_ROI = [130, 985, 460, 30]  # material costs "18/5", "14/30", "189K/10.5K", left to right
RANK_AVAILABLE_ROI = [130, 925, 460, 50]  # "Available" tag over a material with a free source (Bellflowers)
RANK_MIDDLE_X = 360  # the middle cost slot: Bellflowers (gather.RANK_BELLFLOWER_ICON)
# Enhance Gear
RESONANCE = (620, 256)

PASS_BUDGET_S = 90  # one pass (skills, gear, class, rank, relics)
PASS_BUDGET_OVERRIDE = {"gear": 180}  # live 2026-11-09: enhancing four slots took 60 s, then Resonance and Goals ran out
TAP_BUDGET = 25  # per button: far above any real need, so a dead button can't loop forever
RELIC_BAND = 1


PIP_FROM_SLOT, PIP_RADIUS = (30, -45), 50  # a slot's pip (or "!") rides on its top-right rim, as in gearswap


def gear_enhanceable(frame) -> list[int]:
    """Indexes of the Character screen's gear slots (GEAR_SLOTS order) showing the blue enhance pip."""
    pips = find_up_pips(frame)
    return [i for i, (x, y) in enumerate(GEAR_SLOTS)
            if near_any(pips, (x + PIP_FROM_SLOT[0], y + PIP_FROM_SLOT[1]), PIP_RADIUS)]


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


def level_and_cap(text: str) -> Optional[tuple[int, int]]:
    """"Level: 30/30" -> (30, 30)."""
    m = re.search(r"Level\s*:?\s*(\d+)\s*/\s*(\d+)", text or "")
    return (int(m.group(1)), int(m.group(2))) if m else None


def cost_slots(texts: list[tuple[str, list[int]]]) -> list[tuple[float, float, int]]:
    """Material cost lines -> (have, need, x centre), left to right ("189K/10.5K" -> (189000, 10500, x))."""
    from ..vision.ocr import amount_in
    out = []
    for t, (x, y, w, h) in sorted(texts, key=lambda tb: tb[1][0]):
        m = re.fullmatch(r"\s*([\d.,]+\s*[KMB]?)\s*/\s*([\d.,]+\s*[KMB]?)\s*", t)
        if m:
            have, need = amount_in(m.group(1)), amount_in(m.group(2))
            if have is not None and need is not None:
                out.append((have, need, x + w // 2))
    return out


def bellflowers_short(costs: list[tuple[float, float, int]], available_xs: list[int]) -> bool:
    """The middle cost (Bellflowers) is short and carries the "Available" tag: a free Flower Harvest fixes it."""
    return any(have < need and abs(x - RANK_MIDDLE_X) < 60 and any(abs(x - a) < 60 for a in available_xs)
               for have, need, x in costs)


class Upgrader:
    def __init__(self, dev, det):
        self.dev, self.det = dev, det
        self.nav = Navigator(dev, det)
        self._tap = self.nav.tap
        self.st = Strengthener(dev, det)

    def _badges(self, roi=None, frames: int = 2) -> list[tuple[int, int]]:
        """Badges pulse: union over a couple of frames."""
        seen: list[tuple[int, int]] = []
        for i in range(frames):
            if i:
                time.sleep(0.4)
            for b in find_badges(self.dev.screenshot(), roi):
                if not near_any(seen, b, 12):
                    seen.append(b)
        return seen

    def _character(self) -> bool:
        self.nav.go_home()
        try:
            self.nav.tap_and_expect(ui.NAV_CHARACTER, "character")
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
            if not near_any(self._badges([max(0, x - 200), max(0, y - 80), 400, 160]), (x + 100, y - 20), 140):
                break
            if any(claims.SPEND.search(t) for t, _ in self.det.read_text([0, y - 60, 720, 120])):
                log.warning("spend word next to %s; not tapping", button)
                break
            self._tap(button, wait)
            n += 1
            progress(("pressed", button, n))
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
            caption = boxes_of(self.det, QUICK_UPGRADE_ROI, r"Upgrade", whole=False)
            if not caption:
                break
            x, y, w, h = caption[0]
            self._tap((x + w // 2, y - 30), 3)
            out["quick_upgrades"] += 1
        # Every badged skill icon, equipped (both columns) or in the bag rows of the Technique and Charm tabs, is
        # an ascension with its own shards (seen 2026-11-04: Ice Spike and Elemental Mystery, 10/10 shards each).
        out["ascended"] += self._ascend_badged(SKILL_ICON_ROIS)
        for tab, badge in ((TAB_TECHNIQUE, (165, 780)), (TAB_CHARM, (313, 780))):
            if near_any(self._badges([0, 740, 720, 80]), badge, 30):
                self._tap(tab, 1.5)
                out["ascended"] += self._ascend_badged([BAG_ROW_ROI])
        if near_any(self._badges([200, 740, 160, 80]), (313, 780), 30):
            self._tap(TAB_CHARM, 1.5)
            out["charms"] = self._fill_charms()
        if near_any(self._badges([620, 1150, 100, 80]), (688, 1193), 30):
            out["goals"] = self.claim_goals(BOTTOM_RIGHT_TAB, GOALS_SUBTABS)
        log.info("skills: %s", out)
        return out

    def _ascend_badged(self, rois, limit: int = 8) -> int:
        """Skill page: open each badged icon in `rois`, Enhance, and Ascend while the Ascend button keeps its "!".
        Icons already tried this pass are skipped, so a badge that stays (say, a level-up that needs more Essence)
        can't loop. Returns the number of ascensions."""
        tried: list[tuple[int, int]] = []
        n = 0
        for _ in range(limit):
            badges = [b for roi in rois for b in self._badges(roi) if not near_any(tried, b, 20)]
            if not badges:
                break
            bx, by = badges[0]
            tried.append((bx, by))
            self._tap((bx + ICON_FROM_BADGE[0], by + ICON_FROM_BADGE[1]), 2)
            enhance = boxes_of(self.det, CARD_BUTTONS_ROI, r"Enhance")
            if not enhance:
                log.info("icon at %s: no Enhance on its card; closing", (bx, by))
                self._tap(ui.BELOW_POPUP, 1.5)
                continue
            self._tap(ui.centre(enhance[0]), 2.5)
            if self.det.detect().state != "technique_upgrade":
                log.warning("Enhance did not open Upgrade/Ascension; frame %s", save_unknown(self.dev, "upgrade_ascend"))
                self.nav.go_home()
                return n
            if not re.search(r"Ascension", read_line(self.det, [20, 20, 300, 60])):
                self._tap(BOTTOM_RIGHT_TAB, 2)  # Upgrade page: go to the Ascend tab
            done = self._press_while_badged(ASCEND_BUTTON, wait=3.5)
            if done:
                self._tap(ui.BELOW_POPUP, 2)  # "TIER UP ... Tap to Continue"
            log.info("icon at %s: ascended %d time(s)", (bx, by), done)
            progress(("icon", bx, by))
            n += done
            self._tap(ui.BACK_ARROW, 2.5)
            if self.det.detect().state != "skill_page":
                log.warning("not back on the Skill page; frame %s", save_unknown(self.dev, "upgrade_ascend_back"))
                return n
        return n

    def _fill_charms(self) -> int:
        """Charm tab open on the Skill page: put owned charms into empty slots (the right column)."""
        equipped = 0
        for _ in range(len(CHARM_SLOTS)):
            frame = self.dev.screenshot()
            empty = [xy for xy in CHARM_SLOTS if not self.st._filled(frame, xy)]
            owned = [xy for xy in CHARM_LIST if self.st._filled(frame, xy)]
            if not empty or not owned:
                break
            self._tap(owned[0], 2)
            if not re.search(r"\bEquip\b", read_line(self.det, [60, 850, 300, 100])):
                self._tap(ui.BELOW_POPUP, 1.5)
                break
            self._tap((228, 898), 2)  # Equip (left button on the charm card)
            self._tap(empty[0], 2)
            equipped += 1
        return equipped

    def gear(self) -> dict:
        """Banded enhancement, then Resonance and Enhancement Goals."""
        self.st.enhance_gear()
        progress(("gear", "resonance"))
        if not self._character():
            return {"gear": "unknown_screen"}
        self._tap(GEAR_SLOTS[0], 2)
        self._tap(ITEM_CARD_ENHANCE, 2.5)
        if self.det.detect().state != "enhance_gear":
            return {"gear": f"unknown_screen ({save_unknown(self.dev, 'upgrade_gear')})"}
        out = {"resonance": 0, "goals": 0}
        if near_any(self._badges([560, 200, 160, 80]), (700, 236), 50):
            self._tap(RESONANCE, 2.5)
            if self.det.detect().state == "gear_resonance":
                for _ in range(8):
                    hits = boxes_of(self.det, [400, 120, 320, 1000], r"Activate")
                    if not hits:
                        break
                    self._tap(ui.centre(hits[0]), 2.5)
                    self._tap(ui.BELOW_POPUP, 1.5)  # the "Resonated" banner
                    out["resonance"] += 1
                self._tap(ui.BACK_ARROW, 2.5)
        if near_any(self._badges([620, 1150, 100, 80]), (688, 1193), 30):
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
            cards = [b for b in self._badges([0, 140, 720, 980]) if not near_any(done, b, 20)]
            if not cards:
                break
            bx, by = cards[0]
            done.append((bx, by))
            self._tap((bx + CLASS_CARD_FROM_BADGE[0], by + CLASS_CARD_FROM_BADGE[1]), 3)
            if re.search(r"Badge Received", read_line(self.det, [100, 160, 520, 80])):
                self._tap(BADGE_POPUP_OK, 2.5)
            if re.search(r"Change Class|Unlock", read_line(self.det, [0, 0, 720, 160])) and \
                    self.det.detect().state != "class_page":
                log.warning("class card opened something else; backing out")
                self._tap(ui.BACK_ARROW, 2)
                continue
            self._tap(BOTTOM_RIGHT_TAB, 2.5)  # Upgrade tab
            out["levels"] += self._press_while_badged(CLASS_UPGRADE_BUTTON, wait=3)
            self._tap(ui.BACK_ARROW, 2.5)
        if near_any(self._badges([560, 1150, 160, 80]), (688, 1193), 40):
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
        if near_any(self._badges([620, 1150, 100, 80]), (688, 1193), 30):
            out["goals"] = self.claim_goals(BOTTOM_RIGHT_TAB, GOALS_SUBTABS)
        log.info("rank: %s", out)
        return out

    def rank_first(self, gather: bool = True) -> dict:
        """Rank first at the level cap (mae, 2026-11-11 05:20, R-118): open Rank Advancement, read "Level: N/M";
        at the cap press Advance while it carries "!", tap through RANK UP, claim rank Goals, collect the bed's EXP.
        When the Bellflowers are short (blue pip, "Available" tag) gather them for free (R-123) and try once more.
        Anything else short is logged and strengthening carries on."""
        if not self._character():
            return {"end": "unknown_screen"}
        self._tap(RANK_BADGE, 2.5)
        if self.det.detect().state != "rank_advancement":
            return {"end": f"unknown_screen ({save_unknown(self.dev, 'rank_first')})"}
        lv = level_and_cap(" ".join(t for t, _ in self.det.read_text(RANK_LEVEL_ROI)))
        out: dict = {"level": lv}
        if not lv:
            log.warning("rank: could not read Level N/M; frame %s", save_unknown(self.dev, "rank_level"))
            return {**out, "end": "unknown_level"}
        if lv[0] < lv[1]:
            log.info("rank: level %d/%d, not at the cap; nothing to do first", *lv)
            return {**out, "end": "below_cap"}
        log.info("rank: level %d/%d is the cap: rank advancement first (R-118)", *lv)
        advanced = self._press_while_badged(RANK_ADVANCE, wait=4)
        if advanced:
            for _ in range(3):  # "RANK UP ... Tap to Continue", then a reward card
                if self.det.detect().state == "rank_advancement":
                    break
                self._tap(ui.BELOW_POPUP, 2)
            if near_any(self._badges([620, 1150, 100, 80]), (688, 1193), 30):
                out["goals"] = self.claim_goals(BOTTOM_RIGHT_TAB, GOALS_SUBTABS)
            self.nav.go_home()
            from .daily import Dailies
            out["bed"] = Dailies(self.dev, self.det).bed()  # banked EXP applies on the new cap
            log.info("rank: advanced %d time(s)", advanced)
            return {**out, "advanced": advanced, "end": "advanced"}
        costs = cost_slots(self.det.read_text(RANK_COST_ROI))
        tags = [b[0] + b[2] // 2 for t, b in self.det.read_text(RANK_AVAILABLE_ROI) if re.search(r"Available", t)]
        short = [(h, n) for h, n, _ in costs if h < n]
        out["costs"] = [(h, n) for h, n, _ in costs]
        log.info("rank: Advance has no \"!\"; costs %s, short %s", out["costs"], short or "none read")
        if gather and bellflowers_short(costs, tags):
            from .gather import TARGETS, Gatherer, load_policy
            log.info("rank: Bellflowers short and free to pick: gathering them (R-123), then trying again")
            g = Gatherer(self.dev, self.det)
            got = g.collect(TARGETS["bellflower"], keep=int(load_policy().get("keep_stamina", 70))) \
                if g.enter_bellflower_field() else {"end": "unknown_screen"}
            self.nav.go_home()
            out["gathered"] = got.get("end")
            again = self.rank_first(gather=False)
            return {**out, "retry": again, "end": again.get("end")}
        return {**out, "end": "short"}

    def goals(self, pages=("skills", "gear", "class_levels", "rank")) -> dict:
        """Claim every lit Goals tab first (mae, 2026-11-04, reversing R-116): a Goals "!" lights the Skill / Class /
        rank / gear badge on the Character screen too, so clearing them leaves only badges that mean a real
        upgrade. Each page is opened only when its Character-screen badge is lit; its Goals tab only when that tab
        carries "!". Free claims only (policy.claims)."""
        out = {}
        for page in pages:
            progress(("goals_page", page))
            if not self._character():
                return {**out, "end": "unknown_screen"}
            if page == "skills":
                self._tap(SKILL_BUTTON, 2.5)
                want, tab, subs, badge = "skill_page", BOTTOM_RIGHT_TAB, GOALS_SUBTABS, (688, 1193)
            elif page == "class_levels":
                self._tap(CLASS_BUTTON, 2.5)
                want, tab, subs, badge = "class_page", CLASS_TABS["goals"], (), (688, 1193)
            elif page == "rank":
                self._tap(RANK_BADGE, 2.5)
                want, tab, subs, badge = "rank_advancement", BOTTOM_RIGHT_TAB, GOALS_SUBTABS, (688, 1193)
            else:  # gear: Enhance Gear page, Enhancement Goals tab
                self._tap(GEAR_SLOTS[0], 2)
                self._tap(ITEM_CARD_ENHANCE, 2.5)
                want, tab, subs, badge = "enhance_gear", BOTTOM_RIGHT_TAB, (), (688, 1193)
            if self.det.detect().state != want:
                out[page] = f"unknown_screen ({save_unknown(self.dev, f'upgrade_goals_{page}')})"
                continue
            out[page] = self.claim_goals(tab, subs) if near_any(self._badges([560, 1150, 160, 80]), badge, 40) else 0
        log.info("goals: %s", out)
        return out

    def relics(self) -> dict:
        """Workbench relics (R-172, R-105): sxs.loops.relics. The Character screen carries no relic badge, so this
        pass runs only with --only relics; strengthen runs the relic step itself, after the gacha."""
        from .relics import RelicBench
        return RelicBench(self.dev, self.det).run()

    # --- the loop ---

    PASSES = ["goals", "skills", "gear", "class_levels", "rank", "relics"]

    def run(self, only: Optional[set] = None) -> dict:
        passes = [p for p in self.PASSES if not only or p in only]
        banner(log, "Upgrade", f"apply every upgrade the Character screen's \"!\" marks offer ({', '.join(passes)})",
               "each pass done once, its tap budget spent, or an unexpected screen")
        results: dict = {}
        if not self._character():
            return {"end": "unknown_screen"}
        def lit() -> dict:
            frame_badges = self._badges()
            log.info("character screen badges: %s", frame_badges)
            return {
                # Always open the Skill page: affordable skill levels show only blue arrows (no red "!" on the
                # Character screen), and the Quick Upgrade caption there is the real need check (2026-11-05: the
                # pass was skipped while Quick Upgrade raised every skill 2-4 levels by hand).
                "skills": True,
                # mae, 2026-11-09: a blue up-arrow pip on a gear slot means it can be enhanced (the red "!" in the same
                # place means a better piece to swap in: gearswap's job, R-088).
                "gear": bool(gear_enhanceable(self.dev.screenshot())),
                "class_levels": near_any(frame_badges, (CLASS_BUTTON[0] + 30, CLASS_BUTTON[1] - 30), 50),
                "rank": near_any(frame_badges, (RANK_BADGE[0] + 90, RANK_BADGE[1] - 30), 70),
                "relics": False,
            }
        wanted = lit()
        lit_pages = [k for k, v in wanted.items() if v]
        wanted["goals"] = bool(lit_pages)
        for p in passes:
            if p == "skills" and isinstance(results.get("goals"), dict) and any(results["goals"].values()):
                # Goals claimed: re-read, so a badge that only meant "Goals" no longer starts an upgrade pass.
                if self._character():
                    wanted.update(lit())
            if not wanted[p] and not only:
                results[p] = "no_badge"
                continue
            # Each pass is its own short task (mae, 2026-11-04: 1-2 minutes, cut it rather than bash on).
            budget = PASS_BUDGET_OVERRIDE.get(p, PASS_BUDGET_S)
            # A pass starting is progress: Strengthen's 60 s watchdog stopped it while the Goals pass was still
            # opening pages, before its first claim (live 2026-11-09).
            progress(("pass", p))
            with task(p, budget) as t:
                try:
                    results[p] = self.goals(lit_pages or ()) if p == "goals" and not only else getattr(self, p)()
                except Exception as e:  # noqa: BLE001  one pass must not take the loop down
                    log.warning("[%s] failed: %s; frame %s", p, e, save_unknown(self.dev, f"upgrade_{p}"))
                    results[p] = "error"
            if t.status:
                log.warning("[%s] %s after %g s; next pass", p, t.status, budget)
                results[p] = t.status
            self.nav.go_home()
        log.info("upgrade: %s", results)
        return results


STRENGTHEN_STEPS = ["cart", "rank", "gacha", "relics", "gear_swap", "charms", "upgrade"]
STEP_BUDGET_S = {"cart": 150, "rank": 360, "gacha": 180, "relics": 240, "gear_swap": 120, "charms": 90,
                 "upgrade": len(Upgrader.PASSES) * PASS_BUDGET_S + sum(PASS_BUDGET_OVERRIDE.values())}


def get_stronger(dev, det, only: Optional[set] = None, skip: frozenset = frozenset()) -> dict:
    """Everything that raises power with soft resources, in one call (mae, 2026-11-09; order 2026-11-11):
    claim the Cart; rank first when the level is at the cap (R-118, mae 05:20); Aeonic Gacha x10 draws whenever a
    full x10 is affordable (R-167, mae 05:22); Workbench relics, so new relics get activated and enhanced (R-172);
    then better gear where a slot shows a red "!" (gearswap, R-088), empty charm slots, and the Upgrade Loop.
    Each step has its own time budget and stall check; one step failing never stops the next. Used by explore
    after repeated losses, by the daily strengthen step and by `python -m sxs strengthen`. Flowchart:
    docs/loops/upgrade.md (Get stronger)."""
    from .gacha import Gacha
    from .gearswap import GearSwap
    from .relics import RelicBench

    st = Strengthener(dev, det)
    nav = Navigator(dev, det)

    def charms():
        nav.go_home()
        ui.tap(dev, ui.HUD_PORTRAIT, 2.5)  # -> player profile
        return st.equip_charms(from_profile=True) if det.detect().state == "player_profile" else 0

    steps = {
        "cart": st.claim_cart,
        "rank": lambda: Upgrader(dev, det).rank_first().get("end"),
        "gacha": lambda: Gacha(dev, det).run().get("end"),
        "relics": lambda: RelicBench(dev, det).run().get("end"),
        "gear_swap": lambda: GearSwap(dev, det).run().get("end"),
        "charms": charms,
        "upgrade": lambda: Upgrader(dev, det).run(),
    }
    out: dict = {}
    for name in STRENGTHEN_STEPS:
        if (only and name not in only) or name in skip:
            continue
        progress(("step", name))
        with task(name, STEP_BUDGET_S[name]) as t:
            try:
                out[name] = steps[name]()
            except Exception as e:  # noqa: BLE001  one step must not take the rest down
                log.warning("[strengthen %s] failed: %s; frame %s", name, e, save_unknown(dev, f"strengthen_{name}"))
                out[name] = "error"
        if t.status:
            log.warning("[strengthen %s] %s after %d s; next step", name, t.status, STEP_BUDGET_S[name])
            out[name] = t.status
        try:
            nav.go_home()
        except Exception as e:  # noqa: BLE001
            log.warning("could not get home after %s: %s", name, e)
        log.info("[strengthen %s] %s", name, out[name] if name != "upgrade" else "done")
    return out


def _args(p) -> None:
    p.add_argument("--only", help="comma-separated passes: " + ", ".join(Upgrader.PASSES))


def _run(ctx, opts):
    only = set(opts.only.split(",")) if opts.only else None
    results = Upgrader(ctx.dev, ctx.det).run(only)
    return {"end": results.pop("end", "done"), "passes": results}


LOOP = Loop("upgrade", "Upgrade", "apply every upgrade a red \"!\" on the Character screen offers", _run, _args,
            budget=len(Upgrader.PASSES) * PASS_BUDGET_S + sum(PASS_BUDGET_OVERRIDE.values()))  # only badged passes run; each is capped at PASS_BUDGET_S
