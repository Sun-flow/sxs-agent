"""Dailies loop: run each daily chore once per server day, then the character-upgrade passes.

    python -m sxs.daily                     # everything not yet done today
    python -m sxs.daily --only strengthen   # one step (comma-separated list)
    python -m sxs.daily --force             # ignore today's done marks

Steps, in order (each starts from home and ends there):
  sign_in          Thrilling Events -> Daily Sign-in: claim today's tile (never Catch Up).
  cart             Claim the Cart's AFK loot.
  growth_trial     Thrilling Events -> Growth Trial: claim finished trial quests.
  fantasia_ascent  Journal -> Fantasia Ascent: one climb, Auto Challenge on, no retries (mae, 2026-11-04).
  quests           Menu -> Quest: claim finished guidance quests (their rewards are ore for enhancing).
  strengthen       Better gear and charms from the profile, banded gear enhancement, techniques. Repeated after
                   quest claims, because enhancing finishes quests and quests pay ore.

Once-a-day steps are recorded in logs/daily.json under the server date (UTC-5, resets 8:00 server time).
mae's rules hold throughout: no Dawnium, no spend buttons, no class choices, no social, no Rcmd Loadouts, heal
to 70% before fights, no Fantasia retries. Every step has a time budget; a step that fails or meets an
unfamiliar screen saves the frame to captures/unknown/, goes home and the loop moves on. Two failed recoveries
end the loop (needs_help). No model calls.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from typing import Callable

from . import claims, nav, tower
from .device import REPO_ROOT, Device, banner, save_unknown, server_day
from .state import StateDetector
from .strengthen import Strengthener

log = logging.getLogger("sxs.daily")

DAILY = REPO_ROOT / "logs" / "daily.json"
FEATURED_SIGNIN = (360, 720)  # Featured list: Daily Sign-in card
FEATURED_GROWTH = (360, 470)  # Featured list: Growth Trial card
MENU_QUEST = (200, 820)  # main menu: Quest
QUEST_TAB = (290, 1216)  # quest list: Quest (guidance) tab
GROWTH_DAY_TABS = [(100, 476), (176, 476), (266, 476), (356, 476), (446, 476), (536, 476), (626, 476)]
OK = {"done", "nothing", "reached", "floors_done", "lost"}


def _load() -> dict:
    try:
        return json.loads(DAILY.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def done_today(key: str) -> bool:
    return _load().get(key) == server_day()


def mark_done(key: str) -> None:
    data = _load()
    data[key] = server_day()
    DAILY.parent.mkdir(exist_ok=True)
    DAILY.write_text(json.dumps(data, indent=2), encoding="utf-8")


class Dailies:
    def __init__(self, dev: Device, det: StateDetector):
        self.dev, self.det = dev, det
        self.nav = nav.Navigator(dev, det)
        self.st = Strengthener(dev, det)

    def _tap(self, xy, wait=2.0):
        self.dev.tap(*xy)
        time.sleep(wait)

    def _open(self, xy, state: str, wait=8.0) -> bool:
        self.dev.tap(*xy)
        return self.det.wait_for({state}, wait, interval=0.5).state == state

    def _featured(self) -> bool:
        self.nav.go_home()
        return self._open(nav.HOME_EVENTS_BUTTON, "featured")

    # --- steps: each returns "done", "nothing" (ran, nothing to do), or a failure reason ---

    def sign_in(self) -> str:
        if not self._featured() or not self._open(FEATURED_SIGNIN, "daily_signin"):
            return "unknown_screen"
        n = claims.claim_all(self.dev, self.det, max_taps=2, home_state="daily_signin")
        return "done" if n else "nothing"

    def cart(self) -> str:
        return "done" if self.st.claim_cart() else "nothing"

    def growth_trial(self) -> str:
        if not self._featured() or not self._open(FEATURED_GROWTH, "growth_trial"):
            return "unknown_screen"
        n = 0
        for tab in GROWTH_DAY_TABS:  # locked days show a padlock; tapping them does nothing
            self._tap(tab, 1.5)
            n += claims.claim_all(self.dev, self.det, roi=[0, 500, 720, 620], home_state="growth_trial")
        return "done" if n else "nothing"

    def fantasia_ascent(self) -> str:
        if tower.done_today():
            return "nothing"
        if not tower.open_from_home(self.dev, self.det):
            return "unknown_screen"
        result = tower.climb(self.dev, self.det)
        if result in OK:
            tower.mark_done()
        return result

    def quests(self) -> str:
        self.nav.go_home()
        self._tap(nav.HOME_MENU_BUTTON, 2.5)
        if not self._open(MENU_QUEST, "quests"):
            return "unknown_screen"
        n = 0
        for _ in range(4):  # the list scrolls; finished quests may sit lower down
            n += claims.claim_all(self.dev, self.det, home_state="quests")
            self.dev.swipe(360, 1000, 360, 400, 500)
            time.sleep(1.5)
        return "done" if n else "nothing"

    def strengthen(self) -> str:
        self.st.claim_cart()
        self.nav.go_home()
        self._tap((70, 60), 2.5)  # HUD portrait -> player profile
        if self.det.detect().state == "player_profile":
            self.st.equip_better_gear()
            self.st.equip_charms(from_profile=True)
        self.st.enhance_gear()
        self.st.upgrade_techniques()
        return "done"

    # --- the loop ---

    STEPS: list[tuple[str, bool]] = [  # (name, once a day)
        ("sign_in", True), ("cart", False), ("growth_trial", False), ("fantasia_ascent", True),
        ("quests", False), ("strengthen", False), ("quests", False), ("strengthen", False),
    ]

    def run(self, only: set = None, force: bool = False, step_minutes: float = 12) -> dict:
        names = [n for n, _ in self.STEPS if not only or n in only]
        banner(log, "Dailies", f"run the daily chores and upgrade passes: {', '.join(dict.fromkeys(names))}",
               f"every step tried once (budget {step_minutes:g} min each), or 2 failed recoveries to home")
        results, failures = {}, 0
        repeat_ok = True  # the second quests/strengthen pass runs only if the first quests pass claimed something
        for name, once in self.STEPS:
            if name not in names:
                continue
            if name in results and not repeat_ok:
                continue
            if once and not force and done_today(name):
                log.info("[%s] already done today", name)
                results.setdefault(name, "skipped")
                continue
            log.info("[step %s]", name)
            fn: Callable[[], str] = getattr(self, name)
            t0 = time.monotonic()
            try:
                result = fn()
            except Exception as e:  # noqa: BLE001  a step must not take the loop down
                log.warning("[%s] failed: %s; frame %s", name, e, save_unknown(self.dev, f"daily_{name}"))
                result = "error"
            if time.monotonic() - t0 > step_minutes * 60:
                log.warning("[%s] ran over its %g min budget", name, step_minutes)
            if result not in OK:
                failures += 1
            elif once:
                mark_done(name)
            if name == "quests" and name not in results:
                repeat_ok = result == "done"
            log.info("[%s] %s", name, result)
            results[name] = result if name not in results else f"{results[name]}, {result}"
            try:
                self.nav.go_home(timeout=90)
            except Exception as e:  # noqa: BLE001
                log.warning("could not get home after %s: %s; frame %s", name, e, save_unknown(self.dev, "daily_home"))
                failures += 1
            if failures >= 2 and result not in OK:
                results["end"] = "needs_help"
                break
        log.info("dailies: %s", results)
        return results


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--only", help="comma-separated steps: " + ", ".join(dict.fromkeys(n for n, _ in Dailies.STEPS)))
    p.add_argument("--force", action="store_true", help="ignore today's done marks")
    args = p.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    dev = Device()
    only = set(args.only.split(",")) if args.only else None
    results = Dailies(dev, StateDetector(dev)).run(only, args.force)
    print(json.dumps(results), flush=True)
    return 1 if results.get("end") == "needs_help" else 0


if __name__ == "__main__":
    sys.exit(main())
