"""Aeonic Gacha: draw x10 on every tier that can pay a full x10 with badges, claim the ticket counter and Goals.

    python -m sxs gacha           # draw, claim, report
    python -m sxs gacha --check   # read the tiers and the counter only

mae, 2026-11-11 05:22 (R-167): pull whenever a full 10x pull is affordable on any tier, paying only with Auroral
Badges or tickets, never Dawnium; never Draw x1, never a short "Draw xN" (N < 10). Flowchart: docs/loops/gacha.md.

A draw is pressed only when four readings agree: the right button reads exactly "Draw x10", its cost reads 100, the
tier card reads held >= 100, and the top-right badge count reads >= 100 (with fewer badges the same button turns
into "Draw x3 / 30"). The result screen's own Draw buttons are never pressed: back out and check again. Spend
words (claims.SPEND, a price) anywhere on a screen the draw opens stop the loop. No model calls.
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass
from typing import Optional

import cv2

from ..actions.home import HOME_IMAGES, find_on_home, match_template, template_finder
from ..core import records, ui
from ..core.device import save_unknown
from ..core.loop import Loop, banner, progress
from ..core.nav import Navigator
from ..core.paths import CAPTURES
from ..policy import claims
from ..vision.badges import find_badges, near_any
from ..vision.ocr import zoomed_lines

log = logging.getLogger("sxs.loops.gacha")

TIERS = ["Rare", "Epic", "Legendary", "Mythic"]
CARDS = [(160, 930), (293, 930), (427, 930), (560, 930)]  # tier cards under the globe
CARD_TEXT_DY, CARD_TEXT_BOX = 70, (110, 30)  # "held/10" strip at the foot of each card
DRAW_X10 = (510, 1102)  # right Draw button: "Draw x10 / 100", or "Draw xN / 10N" when short
DRAW_ROI = [370, 1070, 280, 65]
TOP_COUNT_BOX = [440, 35, 160, 40]  # the selected tier's badge count, top right (Dawnium sits right of it)
COUNTER = (95, 185)  # ticket counter, upper left: "n/5" under it, "!" on it when n >= 5
COUNTER_TEXT_BOX = [45, 252, 100, 36]
COUNTER_BADGE, COUNTER_BADGE_ROI = (122, 155), [60, 110, 120, 90]
TITLE_ROI = [20, 20, 330, 70]
TABS = {"kingdom": (245, 1218), "element": (428, 1218), "goals": (608, 1218)}
GOALS_BADGE, GOALS_BADGE_ROI = (690, 1193), [620, 1150, 100, 80]
GOALS_SUBTABS = [(260, 1120), (460, 1120)]  # Kingdom | Element
GOALS_CLAIM_ROI = [480, 100, 240, 900]  # Claim buttons only (the row titles say "Draws")
RESULT_ROI = [30, 30, 400, 50]  # "Draws Today: 10/10000" on the result screen
RESULT_NAMES_ROI = [0, 120, 720, 920]
PACK_ROI = [80, 480, 560, 480]  # timed pack card: "Pack disappears in ...", "$0.99"
PACK_CLOSE = (360, 1120)  # tap below the card (R-157)
# Fallback until home/aeonic_gacha.png is captured: the machine stands left of the Vendor Booth. Booth template
# centre (518, 795) and the stone's centre (363, 855) on docs/screens/home/home_stone_open.png.
BOOTH_TO_GACHA = (-155, 60)
FULL = 10  # draws per press
FULL_COST = 100  # badges per x10
MAX_DRAWS = 10  # x10 draws per run: a guard against a reading gone wrong, far above a day's badges
RESULT_WAIT_S = 12
OK = {"done", "nothing", "check"}


@dataclass
class TierView:
    tier: str
    button: Optional[int]  # N in "Draw xN" on the right button, None if unreadable
    cost: Optional[int]
    held: Optional[int]  # from the card's "held/10"
    top: Optional[int]  # the top-right badge count

    def full_x10(self) -> bool:
        """All four readings say a full x10 with badges (R-167)."""
        return (self.button == FULL and self.cost == FULL_COST and (self.held or 0) >= FULL_COST
                and (self.top or 0) >= FULL_COST)

    def line(self) -> str:
        return f"{self.tier} {self.held}/10, top {self.top}: Draw x{self.button} ({self.cost})"


def parse_draw(texts: list[str]) -> tuple[Optional[int], Optional[int]]:
    """("Draw x10", "100") -> (10, 100); ("Draw x4", "40") -> (4, 40). OCR drops the space ("Drawx10") or reads
    the x as ×. A spend word or a price on the button reads as (None, None): never a draw."""
    joined = " ".join(texts)
    if claims.SPEND.search(joined.replace("Draw", "")):
        return None, None
    m = re.search(r"Draw\s*[x×X]\s*(\d+)", joined)
    n = int(m.group(1)) if m else None
    rest = joined[m.end():] if m else joined
    c = re.search(r"(\d+)", rest)
    return n, (int(c.group(1)) if c else None)


def held_in(lines: list[str]) -> Optional[int]:
    """"235/10" -> 235."""
    for t in lines:
        m = re.search(r"(\d+)\s*/\s*10", t.replace(" ", ""))
        if m:
            return int(m.group(1))
    return None


def top_count(lines: list[str]) -> Optional[int]:
    """The badge count top right; the "+" beside it OCRs as a stray "4" or "+", so take the largest number."""
    nums = [int(n) for t in lines for n in re.findall(r"\d+", t.replace(",", ""))]
    return max(nums) if nums else None


def counter_points(lines: list[str]) -> Optional[int]:
    """"20/5" -> 20 (ticket counter points)."""
    for t in lines:
        m = re.search(r"(\d+)\s*/\s*5\b", t.replace(" ", ""))
        if m:
            return int(m.group(1))
    return None


def relics_in(texts: list[tuple[str, list[int]]]) -> tuple[list[str], int]:
    """Result screen OCR (text, box) -> (new relic names, shard bundles). Duplicates come as "<name> Shard" (R-167),
    the label's second line sitting under the first; a label with no "Shard" under or in it is a new relic."""
    lines = [(t.strip(), b) for t, b in texts
             if len(t.strip()) > 2 and not re.search(r"Draws Today|^\d+$|^Draw|^NEW$", t.strip())]
    used: set = set()
    labels: list[str] = []
    for i, (t, (x, y, w, h)) in enumerate(lines):
        if i in used:
            continue
        cx, label = x + w // 2, t
        for j, (u, (x2, y2, w2, h2)) in enumerate(lines):  # its second line: same column, just below
            if j != i and j not in used and abs(x2 + w2 // 2 - cx) < 70 and 0 < y2 - y < 2.2 * h + 10:
                label = f"{t} {u}"
                used.add(j)
                break
        used.add(i)
        labels.append(label)
    shards = sum(1 for t in labels if re.search(r"Shard$", t))
    return [t for t in labels if not re.search(r"Shard$", t)], shards


class Gacha:
    def __init__(self, dev, det):
        self.dev, self.det = dev, det
        self.nav = Navigator(dev, det)
        self._tap = self.nav.tap

    # --- reading -------------------------------------------------------------------------------------------------

    def _title(self, frame=None) -> str:
        return " ".join(t for t, _ in self.det.read_text(TITLE_ROI, frame))

    def on_gacha(self, frame=None) -> bool:
        return "Aeonic Gacha" in self._title(frame)

    def read_tier(self, i: int, frame=None) -> TierView:
        frame = self.dev.screenshot() if frame is None else frame
        x, y = CARDS[i]
        w, h = CARD_TEXT_BOX
        held = held_in(zoomed_lines(self.det, frame, [x - w // 2, y + CARD_TEXT_DY - h // 2, w, h]))
        n, cost = parse_draw([t for t, _ in self.det.read_text(DRAW_ROI, frame)])
        return TierView(TIERS[i], n, cost, held, top_count(zoomed_lines(self.det, frame, TOP_COUNT_BOX)))

    def _badged(self, xy, roi) -> bool:
        seen = []
        for k in range(2):  # badges pulse
            if k:
                time.sleep(0.4)
            seen += find_badges(self.dev.screenshot(), roi)
        return near_any(seen, xy, 30)

    # --- steps ---------------------------------------------------------------------------------------------------

    def pack_showing(self) -> bool:
        text = " ".join(t for t, _ in self.det.read_text(PACK_ROI))
        return bool(re.search(r"Pack disappears|Bonus ?Pack|\$\s*\d", text))

    def dismiss_pack(self) -> bool:
        """The $0.99 "Gacha Bonus Pack" timed popup (R-157): tap below the card, never on it."""
        if self.pack_showing():
            log.info("timed pack popup: dismissing (tap below the card, R-157)")
            self._tap(PACK_CLOSE, 2)
            return True
        return False

    def open(self) -> str:
        """Home > the gacha machine. Returns "ok", "not_found" or "unknown_screen"."""
        find = template_finder("aeonic_gacha")
        if find is None:
            booth = cv2.imread(str(HOME_IMAGES / "vendor_booth.png"))

            def find(frame):
                hit = match_template(frame, booth, threshold=0.7) if booth is not None else None
                return (hit[0] + BOOTH_TO_GACHA[0], hit[1] + BOOTH_TO_GACHA[1]) if hit else None
            log.info("no home/aeonic_gacha.png yet: finding the machine beside the Vendor Booth")
        at = find_on_home(self.dev, self.det, find)
        if not at:
            return "not_found"
        self._tap(at, 3)
        for _ in range(2):
            if self.on_gacha():
                return "ok"
            if not self.dismiss_pack():
                break
        log.warning("the tap at %s did not open the Aeonic Gacha (%r); frame %s", at, self._title(),
                    save_unknown(self.dev, "gacha_open"))
        return "unknown_screen"

    def claim_counter(self) -> int:
        """Tap the ticket counter while its "!" shows: each tap turns 5 points into Epic badges (R-167)."""
        before = counter_points(zoomed_lines(self.det, self.dev.screenshot(), COUNTER_TEXT_BOX))
        taps = 0
        for _ in range(6):
            if not self._badged(COUNTER_BADGE, COUNTER_BADGE_ROI):
                break
            self._tap(COUNTER, 2)
            taps += 1
            progress(("counter", taps))
            state = self.det.detect().state
            if state == "reward_popup":
                self._tap(ui.REWARD_CLOSE, 1.5)
            elif state == "tap_to_continue":
                self._tap(ui.DIALOGUE_NEXT, 1.5)
            if not self.on_gacha():
                log.warning("the counter tap left the gacha; frame %s", save_unknown(self.dev, "gacha_counter"))
                break
        after = counter_points(zoomed_lines(self.det, self.dev.screenshot(), COUNTER_TEXT_BOX))
        log.info("ticket counter: %s/5 -> %s/5 (%d taps)", before, after, taps)
        return taps

    def draw(self, view: TierView) -> Optional[dict]:
        """Press Draw x10 once (the caller has checked `view.full_x10()`), save and log the result, back out.
        None if the result screen didn't show."""
        log.info("%s: drawing x10", view.line())
        self.dev.tap(*DRAW_X10)
        deadline = time.monotonic() + RESULT_WAIT_S
        frame = None
        while time.monotonic() < deadline:
            time.sleep(1.5)
            frame = self.dev.screenshot()
            if re.search(r"Draws Today", " ".join(t for t, _ in self.det.read_text(RESULT_ROI, frame))):
                break
            if claims.SPEND.search(" ".join(t for t, _ in self.det.read_text([0, 300, 720, 700], frame)).replace("Draw", "")):
                log.warning("a spend word showed after Draw x10: stopping; frame %s", save_unknown(self.dev, "gacha_spend"))
                return None
        else:
            log.warning("no result screen after Draw x10; frame %s", save_unknown(self.dev, "gacha_result"))
            return None
        new, shards = relics_in(self.det.read_text(RESULT_NAMES_ROI, frame))
        out = CAPTURES / "gacha"
        out.mkdir(parents=True, exist_ok=True)
        path = out / f"{time.strftime('%Y%m%d-%H%M%S')}-{view.tier.lower()}.png"
        cv2.imwrite(str(path), frame)  # the result screen shows no account name
        log.info("%s x10: new relics %s, %d shard bundles (saved %s)", view.tier, new or "none", shards, path.name)
        self._tap(ui.BACK_ARROW, 2.5)  # never the result screen's own Draw buttons
        return {"tier": view.tier, "new": new, "shards": shards, "screen": path.name}

    def claim_goals(self) -> int:
        if not self._badged(GOALS_BADGE, GOALS_BADGE_ROI):
            return 0
        self._tap(TABS["goals"], 2.5)
        n = 0
        for sub in GOALS_SUBTABS:
            self._tap(sub, 1.5)
            n += claims.claim_all(self.dev, self.det, roi=GOALS_CLAIM_ROI)
        self._tap(TABS["kingdom"], 2)
        log.info("gacha goals claimed: %d", n)
        return n

    def draw_all(self, out: dict, check: bool = False) -> str:
        """Gacha screen open: each tier card in turn, Draw x10 while all four readings allow it. Fills out["tiers"]
        and out["draws"]. Returns "ok" or "unknown_screen"."""
        for i in range(len(TIERS)):
            self._tap(CARDS[i], 1.5)
            view = self.read_tier(i)
            log.info(view.line())
            out["tiers"][view.tier] = view.held
            while not check and view.full_x10() and len(out["draws"]) < MAX_DRAWS:
                got = self.draw(view)
                if got is None:
                    return "unknown_screen"
                out["draws"].append(got)
                progress(("draw", len(out["draws"])))
                if not self.on_gacha():
                    self.dismiss_pack()
                    if not self.on_gacha():
                        log.warning("not back on the gacha after a draw; frame %s", save_unknown(self.dev, "gacha_back"))
                        return "unknown_screen"
                view = self.read_tier(i)
                log.info(view.line())
                out["tiers"][view.tier] = view.held
        return "ok"

    def run(self, check: bool = False) -> dict:
        banner(log, "Gacha", "draw x10 on every Aeonic Gacha tier that can pay a full x10 with badges; claim the "
               "ticket counter and Goals (never Dawnium, x1 or a short xN)",
               f"no tier can pay a full x10, {MAX_DRAWS} draws, or an unexpected screen")
        opened = self.open()
        if opened != "ok":
            self.nav.go_home()
            return {"end": opened}
        progress("gacha_open")
        out: dict = {"counter": 0, "draws": [], "goals": 0, "tiers": {}}
        if not check:
            out["counter"] = self.claim_counter()
        if self.draw_all(out, check) != "ok":
            self.nav.go_home()
            return {**out, "end": "unknown_screen"}
        if not check:
            out["goals"] = self.claim_goals()
        self._tap(ui.BACK_ARROW, 2.5)
        self.dismiss_pack()  # leaving once popped the $0.99 Gacha Bonus Pack (R-167)
        self.nav.go_home()
        records.note("gacha", {"tiers": out["tiers"], "draws": len(out["draws"]), "counter": out["counter"]})
        drew = len(out["draws"])
        by_tier = {t: sum(1 for d in out["draws"] if d["tier"] == t) for t in TIERS}
        log.info("gacha: %d draws %s, counter %d taps, goals %d", drew, {k: v for k, v in by_tier.items() if v},
                 out["counter"], out["goals"])
        end = "check" if check else ("done" if drew or out["counter"] or out["goals"] else "nothing")
        return {**out, "end": end}


def _args(p) -> None:
    p.add_argument("--check", action="store_true", help="read the four tiers and the ticket counter only")


def _run(ctx, opts):
    return Gacha(ctx.dev, ctx.det).run(check=opts.check)


LOOP = Loop("gacha", "Gacha", "Aeonic Gacha: x10 draws whenever a full x10 is affordable with badges, never Dawnium",
            _run, _args, ok=OK, budget=180)
