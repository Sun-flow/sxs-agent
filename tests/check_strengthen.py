"""Offline checks for the strengthen additions (no emulator): python tests/check_strengthen.py

Aeonic Gacha readers and a replayed draw pass (R-167: x10 only when a full x10 is affordable, never x1 or a short
xN), Workbench relic readers (R-172, R-105), rank-first readers (R-118), the step order, and Device.pan's adb
fallback. Needs MaaFramework, OpenCV and the OCR models (scripts/fetch-ocr-models.py).

Needs: MaaFramework + OCR models, OpenCV
Checks: Aeonic Gacha readers and a replayed draw pass (x10 only, never x1 or short xN), result names, timed pack;
  Workbench relic readers; rank-first level and Bellflower check; strengthen step order; `Device.pan` adb fallback
  and the Home sweep
"""

import sys
import tempfile
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sxs.core.device import Device, adb_scale, frames_moved  # noqa: E402
from sxs.core.replay import ImageDevice  # noqa: E402
from sxs.core.state import StateDetector  # noqa: E402
from sxs.core import ui  # noqa: E402
from sxs.loops import gacha, relics, upgrade  # noqa: E402
from sxs.actions import home  # noqa: E402

S = Path(__file__).resolve().parent.parent / "docs" / "screens"
fails = 0


def check(name, got, want):
    global fails
    ok = got == want
    fails += not ok
    print(f"{'ok ' if ok else 'BAD'} {name}: {got!r}" + ("" if ok else f" (want {want!r})"))


def img(name):
    return cv2.imread(str(S / name))


# --- gacha parsers -------------------------------------------------------------------------------------------------
check("parse Drawx10 / 100", gacha.parse_draw(["Drawx10", "100"]), (10, 100))
check("parse Draw x4 / 40", gacha.parse_draw(["Draw x4", "40"]), (4, 40))
check("parse Draw ×10", gacha.parse_draw(["Draw ×10 100"]), (10, 100))
check("a price on the button is never a draw", gacha.parse_draw(["Draw x10", "$0.99"]), (None, None))
check("Dawnium on the button is never a draw", gacha.parse_draw(["Draw x10", "Dawnium 1000"]), (None, None))
check("held 235/10", gacha.held_in(["235/10"]), 235)
check("top count with a stray +", gacha.top_count(["4", "35", "H"]), 35)
check("counter 20/5", gacha.counter_points(["20/5"]), 20)
check("full x10 needs all four", gacha.TierView("Rare", 10, 100, 235, 235).full_x10(), True)
check("short top count -> no", gacha.TierView("Rare", 10, 100, 235, 35).full_x10(), False)
check("Draw x3 -> no", gacha.TierView("Rare", 3, 30, 35, 35).full_x10(), False)

dev = ImageDevice()
det = StateDetector(dev)
g = gacha.Gacha(dev, det)
for name, tier, want_full in (("aeonic_gacha_tiers.png", 0, True), ("aeonic_gacha_epic_tier.png", 1, False),
                              ("aeonic_gacha_ticket_counter.png", 0, False), ("aeonic_gacha.png", 0, True)):
    dev.set_frame(S / "home" / name)
    view = g.read_tier(tier)
    check(f"{name}: {view.line()} -> full x10", view.full_x10(), want_full)
dev.set_frame(S / "home/aeonic_gacha_tiers.png")
check("gacha title", g.on_gacha(), True)
dev.set_frame(S / "home/aeonic_gacha_result.png")
check("result screen is not the gacha screen", g.on_gacha(), False)
new, shards = gacha.relics_in(det.read_text(gacha.RESULT_NAMES_ROI))
check("result: one new relic (Star Ladybug)", [n[:4] for n in new], ["Star"])
check("result: shard bundles", shards, 9)
dev.set_frame(S / "home/aeonic_gacha_ticket_counter.png")
check("counter badge lit", g._badged(gacha.COUNTER_BADGE, gacha.COUNTER_BADGE_ROI), True)
dev.set_frame(S / "home/aeonic_gacha_tiers.png")
check("counter badge not lit at 0/5", g._badged(gacha.COUNTER_BADGE, gacha.COUNTER_BADGE_ROI), False)
dev.set_frame(S / "home/timed_pack_gacha_bonus.png")
check("timed pack popup seen", g.pack_showing(), True)
dev.set_frame(S / "home/aeonic_gacha_tiers.png")
check("no timed pack on the gacha screen", g.pack_showing(), False)


class GachaReplay(ImageDevice):
    """The gacha screens, each tap showing the screen it leads to. Rare holds 235 badges (one full x10); after the
    draw, the result's back arrow shows Rare at 35 (Draw x3). Epic shows 43 (Draw x4). Any other tap fails."""

    def __init__(self):
        super().__init__()
        self.taps = []
        self.rare = "home/aeonic_gacha_tiers.png"
        self.set_frame(S / self.rare)

    def tap(self, x, y):
        self.taps.append((x, y))
        go = {gacha.CARDS[0]: lambda: self.rare, gacha.CARDS[1]: lambda: "home/aeonic_gacha_epic_tier.png",
              gacha.CARDS[2]: lambda: "home/aeonic_gacha_ticket_counter.png",
              gacha.CARDS[3]: lambda: "home/aeonic_gacha_ticket_counter.png",
              gacha.DRAW_X10: lambda: "home/aeonic_gacha_result.png", ui.BACK_ARROW: lambda: self.rare}
        if (x, y) not in go:
            raise AssertionError(f"the draw pass tapped {(x, y)}")
        if (x, y) == gacha.DRAW_X10:
            self.rare = "home/aeonic_gacha_ticket_counter.png"  # 235 -> 35 badges
        self.set_frame(S / go[(x, y)]())


rdev = GachaReplay()
rg = gacha.Gacha(rdev, StateDetector(rdev))
gacha.CAPTURES = Path(tempfile.mkdtemp())
out = {"draws": [], "tiers": {}}
try:
    end = rg.draw_all(out)
except AssertionError as e:
    end = str(e)
check("replayed draw pass ends ok", end, "ok")
check("one Rare x10 drawn", [d["tier"] for d in out["draws"]], ["Rare"])
check("Draw x10 pressed once, Draw x1 never", (rdev.taps.count(gacha.DRAW_X10), (210, 1102) in rdev.taps), (1, False))
check("tiers read", out["tiers"], {"Rare": 35, "Epic": 43, "Legendary": 2, "Mythic": 0})

# --- relics -------------------------------------------------------------------------------------------------------
check("relic title", relics.relic_title("Light 1/280"), "Light")
check("not a relic title", relics.relic_title("Enhance Relic"), None)
check("costs 7.98K/1K, 188K/1.8K", relics.costs_in(["7.98K/1K", "188K/1.8K"]), [(7980.0, 1000.0), (188000.0, 1800.0)])
check("affordable", relics.affordable([(7980.0, 1000.0), (188000.0, 1800.0)]), True)
check("short sand", relics.affordable([(800.0, 1000.0), (188000.0, 1800.0)]), False)
check("nothing read is not affordable", relics.affordable([]), False)
dev.set_frame(S / "home/workbench_enhance_relic.png")
check("enhance screen level +1", relics.level_in(det.read_text(relics.LEVEL_ROI)), 1)
check("enhance screen costs", relics.costs_in([t for t, _ in det.read_text(relics.COST_ROI)]),
      [(7980.0, 1000.0), (188000.0, 1800.0)])
frame = img("home/workbench_enhance_relic.png")
check("enhance top row filled", [relics.filled(frame, xy) for xy in relics.TOP_SLOTS], [True, False, False, False])
from sxs.vision.badges import find_badges, find_up_pips, near_any  # noqa: E402
check("Enhance button pip", near_any(find_up_pips(frame, relics.BUTTON_PIP_ROI), relics.BUTTON_PIP, 30), True)
frame = img("home/workbench_relic_activate.png")
check("display slot empty before activation", relics.filled(frame, relics.DISPLAY[0]), False)
lit = [x for x in relics.TAB_XS if near_any(find_badges(frame, [0, 1060, 720, 80]),
                                              (x + relics.TAB_BADGE_FROM[0], relics.TAB_Y + relics.TAB_BADGE_FROM[1]), 25)]
check("element tabs with !", lit, [80, 268, 360, 452])
bx, by = find_badges(frame, relics.GRID_ROI)[0]
check("new relic icon from its !", (bx + relics.ICON_FROM_BADGE[0], by + relics.ICON_FROM_BADGE[1]), (128, 633))
dev.set_frame(S / "home/workbench_relic_card.png")
check("relic card: Enhance found by text, right of Replace",
      [b[0] > 360 for t, b in det.read_text(relics.CARD_BUTTONS_ROI) if t.strip() == "Enhance"], [True])
dev.set_frame(S / "home/workbench_relic_ascension.png")
check("ascension 3/20: no pip on Ascend, so never pressed (the icon can OCR as a leading 1)",
      near_any(find_up_pips(img("home/workbench_relic_ascension.png"), relics.BUTTON_PIP_ROI), relics.BUTTON_PIP, 30), False)

# --- rank first ---------------------------------------------------------------------------------------------------
check("level at cap", upgrade.level_and_cap("Level: 30/30"), (30, 30))
# mae, 2026-11-11 18:15: open the rank page only on a bang or at the cap; gather materials early near the cap.
check("rank due: bang", upgrade.rank_due((38, 40), True), "advance")
check("rank due: at the cap", upgrade.rank_due((40, 40), False), "advance")
check("rank due: near the cap, no bang", upgrade.rank_due((38, 40), False), "precollect")
check("rank due: far below the cap", upgrade.rank_due((24, 40), False), "no_signal")
check("rank due: unreadable level, no bang", upgrade.rank_due(None, False), "no_signal")
dev.set_frame(S / "character/character.png")
check("Character level 2/10 (one OCR line)", upgrade.character_level(det.read_text(upgrade.CHAR_LEVEL_ROI)), (2, 10))
dev.set_frame(S / "character/character_pips_all4.png")
check("Character level 24/30 (split OCR, EXP counter ignored)",
      upgrade.character_level(det.read_text(upgrade.CHAR_LEVEL_ROI)), (24, 30))
f = img("character/character_pips_all4.png")
check("no bang on the rank badge there", near_any(find_badges(f, upgrade.RANK_BADGE_ROI), upgrade.RANK_BANG_AT, 50)
      or near_any(find_up_pips(f, upgrade.RANK_BADGE_ROI), upgrade.RANK_BANG_AT, 50), False)
bx, by = find_badges(img("home/aeonic_gacha_ticket_counter.png"), gacha.COUNTER_BADGE_ROI)[0]  # a real red "!"
f[upgrade.RANK_BANG_AT[1] - 16:upgrade.RANK_BANG_AT[1] + 16, upgrade.RANK_BANG_AT[0] - 16:upgrade.RANK_BANG_AT[0] + 16] = \
    img("home/aeonic_gacha_ticket_counter.png")[by - 16:by + 16, bx - 16:bx + 16]
check("a red ! pasted on the rank badge's corner is seen", near_any(find_badges(f, upgrade.RANK_BADGE_ROI), upgrade.RANK_BANG_AT, 50), True)
dev.set_frame(S / "character/rank_advancement_apprentice3.png")
check("rank page level", upgrade.level_and_cap(" ".join(t for t, _ in det.read_text(upgrade.RANK_LEVEL_ROI))), (30, 30))
costs = upgrade.cost_slots(det.read_text(upgrade.RANK_COST_ROI))
check("rank costs", [(h, n) for h, n, _ in costs], [(18.0, 5.0), (14.0, 30.0), (189000.0, 10500.0)])
tags = [b[0] + b[2] // 2 for t, b in det.read_text(upgrade.RANK_AVAILABLE_ROI) if "Available" in t]
check("Available tag over the middle cost", len(tags) == 1 and abs(tags[0] - 360) < 40, True)
check("Bellflowers short and gatherable", upgrade.bellflowers_short(costs, tags), True)
check("not gatherable without the tag", upgrade.bellflowers_short(costs, []), False)
check("strengthen order: cart, rank first, gacha, relics, then the rest", upgrade.STRENGTHEN_STEPS,
      ["cart", "rank", "gacha", "relics", "gear_swap", "charms", "upgrade"])

# --- swipe fallback -----------------------------------------------------------------------------------------------
base = img("home/home.png")
check("same frame: not moved", frames_moved(base, base.copy()), False)
check("150 px pan: moved", frames_moved(base, np.roll(base, 150, axis=1)), True)
noise = np.clip(base.astype(np.int16) + np.random.default_rng(0).integers(-6, 7, base.shape), 0, 255).astype(np.uint8)
check("pixel noise: not moved", frames_moved(base, noise), False)
check("adb scale 1080 wide", adb_scale("Physical size: 1080x1920\n"), 1.5)
check("adb scale override wins", adb_scale("Physical size: 1440x2560\nOverride size: 720x1280\n"), 1.0)


class FakePan:
    """Device stand-in for Device.pan: MaaFramework's swipe moves the scene or not; adb's does or not."""

    def __init__(self, maa_moves, adb_moves):
        self.maa_moves, self.adb_moves, self.swipe_via_adb = maa_moves, adb_moves, False
        self.frame, self.adb_calls = base.copy(), 0

    def screenshot(self):
        return self.frame

    def _move(self):
        self.frame = np.roll(self.frame, 150, axis=1)

    def swipe(self, *a):
        if self.swipe_via_adb:
            return self.adb_swipe(*a)
        if self.maa_moves:
            self._move()

    def adb_swipe(self, *a):
        self.adb_calls += 1
        if self.adb_moves:
            self._move()


for name, maa, adb, want in (("maa works", True, True, (True, False, 0)), ("maa dead, adb works", False, True, (True, True, 1)),
                             ("scene end", False, False, (False, False, 1))):
    f = FakePan(maa, adb)
    moved = Device.pan(f, 1, 2, 3, 4, 10, settle=0)
    check(f"pan {name}: moved, adb from now on, adb calls", (moved, f.swipe_via_adb, f.adb_calls), want)
f = FakePan(False, True)
Device.pan(f, 1, 2, 3, 4, 10, settle=0)
Device.pan(f, 1, 2, 3, 4, 10, settle=0)
check("after the fallback every swipe goes through adb", f.adb_calls, 2)


class SweepDev(FakePan):
    """find_on_home: the scene ends after 2 pans left; the object shows on the 4th pan right."""

    def __init__(self):
        super().__init__(True, True)
        self.pans = []

    def pan(self, *swipe):
        self.pans.append(swipe[:4])
        lefts = sum(1 for p in self.pans if p == home.VIEW_LEFT)
        return not (swipe[:4] == home.VIEW_LEFT and lefts > 2)


home.Navigator = lambda dev, det: type("N", (), {"go_home": lambda self: None})()
sd = SweepDev()
target = {"n": 0}


def finder(frame):
    rights = sum(1 for p in sd.pans if p == home.VIEW_RIGHT)
    return (100, 200) if rights == 4 else None


check("sweep finds it", home.find_on_home(sd, None, finder), (100, 200))
check("sweep stops a way at the scene's end", [p == home.VIEW_LEFT for p in sd.pans], [True] * 3 + [False] * 4)
check("no template yet -> None", home.template_finder("no_such_template_for_test"), None)

print("all good" if not fails else f"{fails} problem(s)")
sys.exit(1 if fails else 0)
