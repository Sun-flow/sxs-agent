"""Fantasia Ascent: climb a tower's floors.

A tower (e.g. Moonveil Woods, 110 floors) is a ladder of fixed fights. Quests ask for "Reach <Tower> Fn", and every
floor cleared pays ores and gear for free, so the policy is: keep climbing while we win, stop at the quest's floor
if one is asked for and `--past-goal` is off, and follow mae's loss rule (retry a lost floor at most RETRIES times,
then stop so the caller can strengthen or ask).

    python -m sxs.tower [--tower "Moonveil Woods"] [--to 3] [--floors 10] [--minutes 10]

Screens: tower_list -> tower_floors -> battle_prep -> battle -> tower_result (Continue goes straight to the next
floor's battle_prep). See docs/step3-explore.md and memory-bank/game/rules.md.
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
import time
from typing import Optional

from . import nav
from .device import Device
from .state import StateDetector

log = logging.getLogger("sxs.tower")

RETRIES = 2  # mae, 2026-11-03: retry a lost fight at most twice
START_BATTLE = (360, 956)
CONTINUE = (552, 1212)  # on the result screen; goes to the next floor (or back to the floors after a loss)
FLOORS_CHALLENGE_ROI = [380, 1040, 320, 120]  # the current floor's Challenge button on the floors screen
RESULT_FLOOR_ROI = [100, 280, 520, 50]  # "<Tower> Fn" under VICTORY
TOWER_CARDS_ROI = [0, 120, 720, 1040]  # tower names on the list


def floor_of(text: str) -> Optional[int]:
    m = re.search(r"F ?(\d+)", text or "")
    return int(m.group(1)) if m else None


def climb(dev: Device, det: StateDetector, tower: Optional[str] = None, to_floor: Optional[int] = None,
          max_floors: int = 10, minutes: float = 10) -> str:
    """Returns "reached" (to_floor cleared), "floors_done" (max_floors cleared this run), "lost" (RETRIES used
    up), "timeout", "not_tower" (started somewhere else) or "unknown_screen". Leaves the game on the floors or
    result screen; nav.go_home() or the back arrow leaves the tower."""
    deadline = time.monotonic() + minutes * 60
    cleared = losses = unknowns = 0
    last_state = None
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
            x, y, w, h = pick[0]
            dev.tap(x + w // 2, y + h // 2)  # the name and the "Current" line are both on the card
            time.sleep(2.5)
        elif d.state == "tower_floors":
            button = [b for t, b in det.read_text(FLOORS_CHALLENGE_ROI) if re.fullmatch(r"Challenge", t)]
            if not button:
                log.info("no Challenge button on the floors screen: tower finished or locked")
                return "floors_done"
            x, y, w, h = button[0]
            dev.tap(x + w // 2, y + h // 2)
            time.sleep(3)
        elif d.state == "battle_prep":
            dev.tap(*START_BATTLE)
            time.sleep(4)
        elif d.state in ("battle", "loading"):
            time.sleep(2)
        elif d.state == "tower_result":
            line = " ".join(t for t, _ in det.read_text(RESULT_FLOOR_ROI))
            floor = floor_of(line)
            if d.text == "VICTORY":
                cleared += 1
                losses = 0
                log.info("cleared %s (%d this run)", line or "a floor", cleared)
                if to_floor and floor and floor >= to_floor:
                    dev.tap(*nav.BACK_ARROW)  # back to the floors, not on to the next fight
                    time.sleep(2.5)
                    return "reached"
                if cleared >= max_floors:
                    dev.tap(*nav.BACK_ARROW)
                    time.sleep(2.5)
                    return "floors_done"
            else:
                losses += 1
                log.info("lost %s (%d of %d retries)", line or "a floor", losses, RETRIES)
                if losses > RETRIES:
                    dev.tap(*nav.BACK_ARROW)
                    time.sleep(2.5)
                    return "lost"
            dev.tap(*CONTINUE)
            time.sleep(3)
        elif d.state in ("reward_popup", "tap_to_continue"):
            dev.tap(*nav.REWARD_CLOSE)
            time.sleep(1.5)
        elif d.state == "dialogue":
            dev.tap(*nav.DIALOGUE_NEXT)
            time.sleep(1.2)
        elif d.state == "unknown":
            if unknowns >= 5:
                return "unknown_screen"
            time.sleep(1.5)
        else:
            return "not_tower"
    return "timeout"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--tower", help="tower name on the Fantasia Ascent list, e.g. 'Moonveil Woods'")
    p.add_argument("--to", type=int, help="stop after clearing this floor (a quest's 'Reach <Tower> Fn')")
    p.add_argument("--floors", type=int, default=10, help="most floors to clear in one run")
    p.add_argument("--minutes", type=float, default=10)
    args = p.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    dev = Device()
    result = climb(dev, StateDetector(dev), args.tower, args.to, args.floors, args.minutes)
    print(result, flush=True)
    return 0 if result in ("reached", "floors_done") else 1


if __name__ == "__main__":
    sys.exit(main())
