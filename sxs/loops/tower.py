"""Fantasia Ascent: climb a tower's floors.

A tower (e.g. Moonveil Woods, 110 floors) is a ladder of fixed fights. Quests ask for "Reach <Tower> Fn", and every
floor cleared pays ores and gear for free. mae's rules (2026-11-04): Auto Challenge is always on, a lost floor is
not retried, and the climb is a daily: one challenge run per day, climbing until the first loss. `--to` stops
early at a given floor (for testing); the run date is kept in logs/daily.json.

    python -m sxs tower [--tower "Moonveil Woods"] [--to 3] [--floors 10] [--minutes 10]

Screens: tower_list -> tower_floors -> battle_prep -> battle -> tower_result (Continue goes straight to the next
floor's battle_prep). See docs/step3-explore.md and memory-bank/game/rules/.
"""

from __future__ import annotations

import logging
import re
import time
from typing import Optional

import cv2

from ..actions import heal
from ..actions.common import pass_through
from ..core import marks, ui
from ..core.device import save_unknown
from ..core.loop import Loop, banner
from ..core.nav import Navigator
from ..vision.ocr import read_line

log = logging.getLogger("sxs.loops.tower")

CONTINUE = (552, 1212)  # Continue (next floor) after a win, Retry after a loss
FLOORS_CHALLENGE_ROI = [380, 1040, 320, 120]  # the current floor's Challenge button on the floors screen
RESULT_FLOOR_ROI = [100, 280, 520, 50]  # "<Tower> Fn" under VICTORY
AUTO_TOGGLE = (476, 1158)  # Auto Challenge checkbox on the result screen (unlocked after F3)
AUTO_INNER = (469, 1151, 14, 14)  # inside the checkbox: flat when off, a check mark (or lock icon) otherwise
TOWER_CARDS_ROI = [0, 120, 720, 1040]  # tower names on the list


def floor_of(text: str) -> Optional[int]:
    m = re.search(r"F ?(\d+)", text or "")
    return int(m.group(1)) if m else None


def auto_challenge_off(frame) -> bool:
    """True when the Auto Challenge box is empty. An empty box is a flat disc; a ticked one shows a check mark
    and a locked one a padlock, so contrast inside the box tells them apart (std ~5-10 vs 45-75)."""
    x, y, w, h = AUTO_INNER
    return float(cv2.cvtColor(frame[y:y + h, x:x + w], cv2.COLOR_BGR2GRAY).std()) < 20


def ensure_auto_challenge(dev) -> None:
    """mae, 2026-11-04: Auto Challenge is always on when climbing Fantasia Ascent. A loss switches it off."""
    for _ in range(2):
        if not auto_challenge_off(dev.screenshot()):
            return
        log.info("switching Auto Challenge on")
        dev.tap(*AUTO_TOGGLE)
        time.sleep(1)


def done_today() -> bool:
    return marks.done_today("fantasia_ascent")


def mark_done() -> None:
    marks.mark_done("fantasia_ascent")


JOURNAL_FANTASIA = (560, 300)  # Journal tab: the Fantasia Ascent card (top right)


def open_from_home(dev, det) -> bool:
    """Home -> Journal tab -> Fantasia Ascent card -> tower list. False if the list doesn't show."""
    Navigator(dev, det).go_home()
    dev.tap(*ui.NAV_JOURNAL)
    if det.wait_for({"journal"}, 8, interval=0.5).state != "journal":
        return False
    dev.tap(*JOURNAL_FANTASIA)
    return det.wait_for({"tower_list"}, 8, interval=0.5).state == "tower_list"


def climb(dev, det, tower: Optional[str] = None, to_floor: Optional[int] = None,
          max_floors: int = 110, minutes: float = 15) -> str:
    """Returns "reached" (to_floor cleared), "floors_done" (max_floors cleared, or no Challenge left), "lost"
    (the day's climb ended at a loss: not retried), "timeout", "not_tower" (started somewhere else) or "unknown_screen". Leaves the game on the floors or
    result screen; nav.go_home() or the back arrow leaves the tower."""
    banner(log, "Fantasia Ascent", f"daily tower climb{' in ' + tower if tower else ''} with Auto Challenge on",
           f"first loss (no retries), {f'clearing F{to_floor}, ' if to_floor else ''}{max_floors} floors, "
           f"{minutes:g} minutes, or an unfamiliar screen")
    deadline = time.monotonic() + minutes * 60
    cleared = unknowns = 0
    last_state = last_floor = None
    while time.monotonic() < deadline:
        d = det.detect()
        if d.state != last_state:
            log.info("state %s", d.state)
            last_state = d.state
        unknowns = unknowns + 1 if d.state == "unknown" else 0
        if d.state == "tower_list":
            # Open the asked-for tower, else the first one (the list grows as areas unlock).
            cards = det.read_text(TOWER_CARDS_ROI)
            pick = [b for t, b in cards if tower and tower.lower() in t.lower()] or \
                   [b for t, b in cards if t.startswith("Current")]
            if not pick:
                return "unknown_screen"
            ui.tap_box(dev, pick[0], 2.5)  # the name and the "Current" line are both on the card
        elif d.state == "tower_floors":
            button = [b for t, b in det.read_text(FLOORS_CHALLENGE_ROI) if re.fullmatch(r"Challenge", t)]
            if not button:
                log.info("no Challenge button on the floors screen: tower finished or locked")
                return "floors_done"
            ui.tap_box(dev, button[0], 3)
        elif d.state == "battle_prep":
            # mae: at least 70% HP before any fight. Heal from the portrait; never start a floor hurt.
            if not heal.heal_via_portrait(dev, det, heal.PREP_HP_BAR):
                log.warning("HP stays under %d%% (no healing dishes?); not starting the floor", heal.FIGHT_MIN_HP)
                dev.tap(*ui.BACK_ARROW)
                time.sleep(2)
                return "low_hp"
            dev.tap(*ui.START_BATTLE)
            time.sleep(4)
        elif d.state == "tower_result":
            line = read_line(det, RESULT_FLOOR_ROI)
            floor = floor_of(line)
            if d.text == "VICTORY" and floor is not None and floor == last_floor:
                time.sleep(1.5)  # same result still showing (Auto Challenge counts down before moving on)
                continue
            last_floor = floor
            if d.text == "VICTORY":
                cleared += 1
                ensure_auto_challenge(dev)  # not after a loss: ticking it there would start a retry
                log.info("cleared %s (%d this run)", line or "a floor", cleared)
                if to_floor and floor and floor >= to_floor:
                    dev.tap(*ui.BACK_ARROW)  # back to the floors, not on to the next fight
                    time.sleep(2.5)
                    return "reached"
                if cleared >= max_floors:
                    dev.tap(*ui.BACK_ARROW)
                    time.sleep(2.5)
                    return "floors_done"
            else:
                # No retries in Fantasia Ascent (mae): today's climb is over.
                log.info("lost after clearing %d floors; done for today", cleared)
                mark_done()
                dev.tap(*ui.BACK_ARROW)
                time.sleep(2.5)
                return "lost"
            dev.tap(*CONTINUE)  # Continue to the next floor (Auto Challenge also moves on by itself)
            time.sleep(3)
        elif pass_through(dev, d):
            pass  # fights, loading, dialogue, reward popups
        elif d.state == "unknown":
            if unknowns >= 5:
                log.warning("unfamiliar screen; frame saved to %s", save_unknown(dev, "tower"))
                return "unknown_screen"
            time.sleep(1.5)
        else:
            return "not_tower"
    return "timeout"


def _args(p) -> None:
    p.add_argument("--tower", help="tower name on the Fantasia Ascent list, e.g. 'Moonveil Woods'")
    p.add_argument("--to", type=int, help="stop after clearing this floor (a quest's 'Reach <Tower> Fn')")
    p.add_argument("--floors", type=int, default=110, help="most floors to clear in one run")
    p.add_argument("--minutes", type=float, default=15)


def _run(ctx, opts):
    return climb(ctx.dev, ctx.det, opts.tower, opts.to, opts.floors, opts.minutes)


OK = {"reached", "floors_done", "lost"}
LOOP = Loop("tower", "Fantasia Ascent", "daily tower climb, Auto Challenge on, no retries", _run, _args, ok=OK)
