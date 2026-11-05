"""Dailies loop: run each daily chore once per server day, then the character-upgrade passes.

    python -m sxs daily                     # everything not yet done today
    python -m sxs daily --only strengthen   # one step (comma-separated list)
    python -m sxs daily --force             # ignore today's done marks

Steps, in order (each starts from home and ends there):
  sign_in          Thrilling Events -> Daily Sign-in: claim today's tile (never Catch Up).
  mall_gifts       Mall: tap the free gift box on each page (Daily Gift, Weekly Gift, ...); never a price (sxs.loops.mall).
  vendor_stamina   Vendor Booth > Vault: claim the free x30 Stamina once a day (mae, 2026-11-04); nothing else (sxs.loops.vendor).
  cart             Claim the Cart's AFK loot.
  bed              Collect the bed's AFK EXP once a day (mae, 2026-11-04): tap the blue-orb bubble over the bed.
  growth_trial     Thrilling Events -> Growth Trial: claim finished trial quests.
  fantasia_ascent  Journal -> Fantasia Ascent: one climb, Auto Challenge on, no retries (mae, 2026-11-04).
  quests           Menu -> Quest: claim finished guidance quests (their rewards are ore for enhancing).
  guild_donate     Guild Lobby > Donation: up to 2 a day (Free, then 20 Dawnium: mae-approved), by the game's counter.
  guild_afk        Keep the character on a guild gather slot (Forge first).
  guild_conquest   Guild boss: claim beaten floors, use the 2 daily attempts in the background, claim goals.
  gather           Journal > Map Exploration: spend stamina above 70 on the priority material (sxs.loops.gather, R-107).
  gear_swap        Equip the better piece wherever a gear slot on the Character screen shows "!" (sxs.loops.gearswap).
  strengthen       Fill empty charm slots from the profile, then the Upgrade Loop (sxs.loops.upgrade): every "!" on the
                   Character screen (banded gear, resonance, Quick Upgrade, ascensions, class levels, rank, goals).
                   Repeated after quest claims, because enhancing finishes quests and quests pay ore.
  progress         Read the day's numbers (home, profile, Journal) for the progress report (sxs.loops.progress).

Once-a-day steps are recorded in logs/daily.json under the server date (UTC-5, resets 8:00 server time).
mae's rules hold throughout: no Dawnium, no spend buttons, no class choices, no social, no Rcmd Loadouts, heal
to 70% before fights, no Fantasia retries. Every step has a time budget; a step that fails or meets an
unfamiliar screen saves the frame to captures/unknown/, goes home and the loop moves on. Two failed recoveries
end the loop (needs_help). No model calls.
"""

from __future__ import annotations

import logging
import time
from typing import Callable

from ..actions.common import close_rewards
from ..core import records, ui
from ..core.device import save_unknown
from ..core.loop import OVER_BUDGET, Loop, banner, task
from ..core.marks import done_today, mark_done
from ..core.nav import Navigator
from ..policy import claims
from ..vision.ocr import boxes_of, read_int
from . import gather, guild, mall, tower, upgrade, vendor
from .gearswap import GearSwap
from .strengthen import Strengthener

log = logging.getLogger("sxs.loops.daily")

# mae, 2026-11-04: discrete tasks of 1-2 minutes. Each step gets STEP_BUDGET_S and is stopped (not retried) when it
# runs over or stops making progress; the whole sequence is capped at DAILY_BUDGET_S.
STEP_BUDGET_S = 120
DAILY_BUDGET_S = 20 * 60

FEATURED_SIGNIN = (360, 720)  # Featured list: Daily Sign-in card
FEATURED_GROWTH = (360, 470)  # Featured list: Growth Trial card
SIGNIN_TILE_W = 128  # Daily Sign-in tiles: a spend word blocks only a Claim in its own tile
FEATURED_LIST_ROI = [0, 100, 720, 1050]  # card titles on the Featured list
MENU_QUEST = (200, 820)  # main menu: Quest
GROWTH_DAY_TABS = [(100, 476), (176, 476), (266, 476), (356, 476), (446, 476), (536, 476), (626, 476)]
JOURNAL_REALMS = (210, 1020)  # Journal: Material Realms card
REALM_IRONVEIN = (180, 300)  # Material Realms: Ironvein Pit
MINE_BUTTON = (360, 920)  # Ironvein Pit: hammer button
HAMMERS_ROI = [596, 30, 70, 45]  # Iron Hammer count, top right
REALM_GOALS_TAB = (610, 1216)
OK = {"done", "nothing", "reached", "floors_done", "lost", "too_strong", "auto_running"}


class Dailies:
    def __init__(self, dev, det):
        self.dev, self.det = dev, det
        self.nav = Navigator(dev, det)
        self._tap, self._open = self.nav.tap, self.nav.open
        self.st = Strengthener(dev, det)
        self.guild = guild.Guild(dev, det)
        self.gatherer = gather.Gatherer(dev, det)
        self.vendor = vendor.Vendor(dev, det)
        self.upgrader = upgrade.Upgrader(dev, det)
        self.mall = mall.Mall(dev, det)

    def _featured(self) -> bool:
        self.nav.go_home()
        return self._open(ui.HOME_EVENTS_BUTTON, "featured")

    def _featured_card(self, title: str, fallback, state: str) -> bool:
        """Featured list: open the card whose title reads `title`. New events push the cards down (2026-11-04:
        Dawnstar Prelude and Haunted Carnival on top moved Daily Sign-in to the 4th card), so find it by its text
        and use the old position only if OCR misses it."""
        hits = boxes_of(self.det, FEATURED_LIST_ROI, title, whole=False)
        if not hits:
            log.info("Featured: %r not read; trying its usual place %s", title, fallback)
        return self._open(ui.centre(hits[0]) if hits else fallback, state)

    # --- steps: each returns "done", "nothing" (ran, nothing to do), or a failure reason ---

    def sign_in(self) -> str:
        if not self._featured() or not self._featured_card(r"Daily Sign", FEATURED_SIGNIN, "daily_signin"):
            return "unknown_screen"
        n = claims.claim_all(self.dev, self.det, max_taps=2, home_state="daily_signin", spend_dx=SIGNIN_TILE_W)
        return "done" if n else "nothing"

    def cart(self) -> str:
        return "done" if self.st.claim_cart() else "nothing"

    def bed(self) -> str:
        """Bed AFK EXP: once a day (XP builds slowly; mae collects by hand when close to a level-up). The bubble
        sits over the bed in the house; if the camera is elsewhere, pan the home scene up to the house first."""
        self.nav.go_home()
        # The house sits to the right of the cart (seen 2026-11-04 on rif-love-su: one right-to-left drag from the
        # cart view shows the bed); older notes said up. Try right first, then up.
        pans = [(600, 600, 150, 600), (600, 600, 150, 600), (360, 400, 360, 900), (360, 400, 360, 900)]
        for attempt in range(len(pans) + 1):
            hits = self.det.find_all("Home.BedXP")
            if hits:
                self._tap(ui.centre(hits[0]), 3)
                close_rewards(self.dev, self.det, tries=1, wait=2)
                return "done"
            if attempt == len(pans):
                break
            self.dev.swipe(*pans[attempt], 600)
            time.sleep(1.5)
        return "nothing"

    def growth_trial(self) -> str:
        if not self._featured() or not self._featured_card(r"Growth Trial", FEATURED_GROWTH, "growth_trial"):
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

    def material_realms(self) -> str:
        """Ironvein Pit: use owned Iron Hammers (about +115 Raw Ore each). With 0 hammers the button opens a Dawnium
        purchase, so it's only tapped while the counter reads 1 or more; any purchase dialog is cancelled."""
        self.nav.go_home()
        if not self._open(ui.NAV_JOURNAL, "journal") or not self._open(JOURNAL_REALMS, "material_realms"):
            return "unknown_screen"
        self._tap(REALM_IRONVEIN, 3)
        used = 0
        for _ in range(30):
            hammers = read_int(self.det, HAMMERS_ROI, r"^\s*(\d+)\s*$")
            if not hammers:
                break
            self._tap(MINE_BUTTON, 3)
            texts = self.det.read_text([0, 200, 720, 900])
            if any(claims.SPEND.search(t) for t, _ in texts):
                log.warning("purchase prompt at the pit; cancelling")
                self._tap((228, 830), 2)
                break
            used += 1
        self._tap(REALM_GOALS_TAB, 2)
        claims.claim_all(self.dev, self.det, home_state="material_realms")
        log.info("Ironvein Pit: %d hammers used", used)
        records.note("iron_hammers", {"used": used})  # progress tracker
        return "done" if used else "nothing"

    def quests(self) -> str:
        self.nav.go_home()
        self._tap(ui.HOME_MENU_BUTTON, 2.5)
        if not self._open(MENU_QUEST, "quests"):
            log.warning("Quest did not open; frame %s", save_unknown(self.dev, "daily_quests"))
            return "unknown_screen"
        n = 0
        for _ in range(4):  # the list scrolls; finished quests may sit lower down
            n += claims.claim_all(self.dev, self.det, home_state="quests")
            self.dev.swipe(360, 1000, 360, 400, 500)
            time.sleep(1.5)
        return "done" if n else "nothing"

    def guild_donate(self) -> str:
        return self.guild.donate()

    def guild_afk(self) -> str:
        return self.guild.afk()

    def guild_conquest(self) -> str:
        return self.guild.conquest()

    def gather(self) -> str:
        """Spend stamina above the 70 reserve on the priority material (R-107, resource/policy/gather.json)."""
        result = self.gatherer.run()
        return {"budget_spent": "done", "no_spare_stamina": "nothing", "timeout": "done"}.get(result["end"],
                                                                                              result["end"])

    def vendor_stamina(self) -> str:
        """The Vendor Booth Vault's free x30 Stamina (mae, 2026-11-04, R-120). Before gather, so it gets spent."""
        return self.vendor.claim_free_stamina()

    def mall_gifts(self) -> str:
        """Free gift boxes on the Mall pages (Daily Gift, Weekly Gift, event pages; mae, 2026-11-04, R-121)."""
        return self.mall.claim_gifts(part=1)

    def mall_gifts_2(self) -> str:
        """The Mall pages below the first four (a second short task, so neither runs past 2 minutes)."""
        return self.mall.claim_gifts(part=2)

    def gear_swap(self) -> str:
        """Put on the better piece wherever a gear slot shows "!" (mae, 2026-11-04; sxs.loops.gearswap)."""
        return GearSwap(self.dev, self.det).run()["end"]

    def strengthen(self) -> str:
        self.st.claim_cart()
        self.nav.go_home()
        # mae, 2026-11-04: a portrait "!" can mean many things, so nothing here assumes it means gear. Each upgrade
        # type has its own function and its own need-check: better gear is the gear_swap step (a gear slot's "!"),
        # empty charm slots are filled only when one is empty, and the Upgrade Loop runs one pass per badge it
        # sees on the Character screen (goals, skills, gear, class, rank).
        self._tap(ui.HUD_PORTRAIT, 2.5)  # -> player profile
        if self.det.detect().state == "player_profile":
            self.st.equip_charms(from_profile=True)  # returns at once when every charm slot is filled
        self.upgrader.run()
        return "done"

    def progress(self) -> str:
        """Read the day's numbers for the progress tracker (sxs.loops.progress: read only, no taps that act)."""
        from . import progress as tracker

        values, outcome = tracker.Tracker(self.dev, self.det).snapshot(["hud", "profile", "journal"])
        records.add_snapshot(values)
        tracker.write_report(records.server_day())
        return "done" if all(v == "read" for v in outcome.values()) else "nothing"

    # --- the loop ---

    STEPS: list[tuple[str, bool]] = [  # (name, once a day)
        ("sign_in", True), ("mall_gifts", True), ("mall_gifts_2", True), ("vendor_stamina", True), ("cart", False), ("bed", True), ("growth_trial", False), ("fantasia_ascent", True),
        ("material_realms", False), ("guild_donate", True), ("guild_afk", False), ("guild_conquest", True),
        ("quests", False), ("gather", False), ("gear_swap", False), ("strengthen", False), ("quests", False),
        ("strengthen", False), ("progress", False),
    ]

    def run(self, only: set = None, force: bool = False, step_s: float = STEP_BUDGET_S) -> dict:
        names = [n for n, _ in self.STEPS if not only or n in only]
        banner(log, "Dailies", f"run the daily chores and upgrade passes: {', '.join(dict.fromkeys(names))}",
               f"every step tried once (budget {step_s:g} s each), or 2 failed recoveries to home")
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
            result = "error"
            with task(name, step_s) as watch:
                try:
                    result = fn()
                except Exception as e:  # noqa: BLE001  a step must not take the loop down
                    log.warning("[%s] failed: %s; frame %s", name, e, save_unknown(self.dev, f"daily_{name}"))
            if watch.status:  # over its budget or stalled: stopped, not retried; the next run picks it up
                log.warning("[%s] %s after %.0f s; frame %s", name, watch.status, time.monotonic() - t0,
                            save_unknown(self.dev, f"daily_{name}_{watch.status}"))
                result = watch.status
            # A step that ends on an unknown screen or runs out of time is reported and the loop moves on; only a
            # crash (error) or a failed trip home counts toward needs_help. Only a finished step is marked done, so a
            # step cut for time runs again next time.
            if result == "error":
                failures += 1
            elif once and result in OK:
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
            if failures >= 2:
                results["end"] = "needs_help"
                break
        log.info("dailies: %s", results)
        return results


def _args(p) -> None:
    p.add_argument("--only", help="comma-separated steps: " + ", ".join(dict.fromkeys(n for n, _ in Dailies.STEPS)))
    p.add_argument("--force", action="store_true", help="ignore today's done marks")


def _run(ctx, opts):
    only = set(opts.only.split(",")) if opts.only else None
    results = Dailies(ctx.dev, ctx.det).run(only, opts.force)
    status = results.pop("end", "done")
    return {"end": status, "steps": results}


LOOP = Loop("daily", "Dailies", "every daily chore not done today, then the upgrade passes", _run, _args,
            ok={"done"}, budget=DAILY_BUDGET_S)
