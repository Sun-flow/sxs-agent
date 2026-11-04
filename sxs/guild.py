"""Guild dailies (unlocked at Lv 20; gromb2 joined karsa_1515 on 2026-11-04 with mae's go-ahead).

    python -m sxs.guild                       # all three steps
    python -m sxs.guild --only donate,afk     # some of them

Steps (each starts from home, ends on a guild screen; sxs.daily takes it home):
  donate    Lobby > Donation. At most 2 a day (mae, 2026-11-04): the first is Free, the second costs 20 Dawnium,
            which mae approved for those two only. The game's "Daily Donations: N/5" counter is the source of truth,
            so a rerun never donates a third time; a cost above 20 is never paid.
  afk       Park the character on a gather slot, Forge first (mae, 2026-11-04). One slot per character; moving
            collects the old slot's rewards automatically. Already in the Forge -> nothing to do.
  conquest  Gate of Expedition > Conquest: claim a beaten floor's reward chest, step to the live floor, use the
            daily attempts (2), each started and then sent to the background with the minimise icon (mae: such
            fights don't need watching), then claim Serverwide and Personal Conquest Goals.

Nothing social: no chat, no requests, no Guildmates actions. Never Create, Upgrade or Construction (leader only
anyway). The guild Shop spends Guild Tokens and is not touched until mae says so. No model calls.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import time

from . import claims, nav
from .device import Device, banner, save_unknown
from .state import StateDetector

log = logging.getLogger("sxs.guild")

NAV_GUILD = (490, 1242)  # bottom bar, 4th icon (crest)
ISLAND_LABELS = [0, 80, 720, 900]  # where building labels sit on the guild island
LOBBY_HOME = (316, 624)  # where the "Guild Lobby" label sits in the west view (docs/screens/guild_island_west.png)
FROM_LOBBY = {"Gate of Expedition": (274, 196)}  # building tap point relative to the Lobby label in that view
LOBBY_DONATION = (212, 1052)
DONATION_COUNT_ROI = [160, 860, 400, 50]  # "Daily Donations: N/5"
DONATION_BUTTON_ROI = [200, 905, 320, 70]  # "Free" / "Donate <cost>"
DONATION_BUTTON = (360, 940)
DONATION_MAX = 2  # mae, 2026-11-04
DONATION_MAX_COST = 20  # Dawnium; the 2nd donation's price. The 3rd costs 50.
CONFIRM_OK = (492, 734)
CONFIRM_TEXT_ROI = [80, 480, 560, 200]
POPUP_CLOSE = (360, 60)
AFK_TITLE_ROI = [160, 250, 400, 70]  # "AFK Details"
AFK_START = (360, 964)
AFK_FACILITIES = ["Forge", "Mine", "Power Station"]  # mae: Forge first
EVENTS_CONQUEST = (360, 540)  # Guild Events: Conquest card (Guild Clash above it unlocks later)
CONQUEST_ATTEMPTS_ROI = [220, 30, 320, 40]
CONQUEST_STATUS_ROI = [180, 180, 360, 40]  # "Boss defeated" / "No Challengers Yet" under "Conquest Fn"
CONQUEST_CHEST = (356, 732)
CONQUEST_NEXT = (684, 472)
CONQUEST_CHALLENGE = (360, 982)
PREP_START = (360, 956)
BACKGROUND_ICON = (72, 1216)
TAB_CONQUER, TAB_GOALS = (160, 1216), (608, 1216)
GOALS_SERVER, GOALS_PERSONAL = (260, 1120), (460, 1120)
BACK = (74, 1216)


def _num(texts, pattern: str):
    for t, _ in texts:
        m = re.search(pattern, t.replace(" ", "").replace("O", "0"))  # OCR reads 0/2 as O/2
        if m:
            return int(m.group(1))
    return None


class Guild:
    def __init__(self, dev: Device, det: StateDetector):
        self.dev, self.det = dev, det
        self.nav = nav.Navigator(dev, det)

    def _tap(self, xy, wait=2.0):
        self.dev.tap(*xy)
        time.sleep(wait)

    def _expect(self, xy, state: str, wait=8.0) -> bool:
        self.dev.tap(*xy)
        return self.det.wait_for({state}, wait, interval=0.5).state == state

    def open_island(self) -> bool:
        self.nav.go_home()
        return self._expect(NAV_GUILD, "guild", 10)

    def open_building(self, label: str) -> bool:
        """Tap a building on the island by its OCR'd label; pan the island both ways to find it."""
        for swipe in (None, (200, 600, 650, 600), (600, 600, 100, 600), (600, 600, 100, 600)):
            if swipe:
                self.dev.swipe(*swipe, 400)
                time.sleep(1.5)
            for t, (x, y, w, h) in self.det.read_text(ISLAND_LABELS):
                t = t.strip().lower()  # labels can be half hidden by the AFK widget: match the start
                if t == label.lower() or (len(t) >= 8 and label.lower().startswith(t[:8]) and t[:8] == label.lower()[:8]):
                    self._tap((x + w // 2, max(100, y - 60)), 3)
                    return self.det.detect().state != "guild"
        if label in FROM_LOBBY:  # label hidden (the AFK widget covers the Gate's): place it from the Lobby's
            for _ in range(4):
                lobby = [b for t, b in self.det.read_text(ISLAND_LABELS) if t.strip().lower() == "guild lobby"]
                if not lobby:
                    self.dev.swipe(200, 600, 650, 600, 400)
                    time.sleep(1.5)
                    continue
                x, y, w, h = lobby[0]
                dx = LOBBY_HOME[0] - (x + w // 2)
                if abs(dx) > 30:
                    self.dev.swipe(360, 600, 360 + dx, 600, 800)
                    time.sleep(1.5)
                    continue
                ox, oy = FROM_LOBBY[label]
                self._tap((x + w // 2 + ox, y + h // 2 + oy), 3)
                return self.det.detect().state != "guild"
        log.warning("building %r not found on the island", label)
        return False

    def back_to_island(self, tries: int = 5) -> bool:
        for _ in range(tries):
            s = self.det.detect().state
            if s == "guild":
                return True
            self._tap(POPUP_CLOSE if s in {"guild_donation", "reward_popup", "tap_to_continue"} else BACK, 2.5)
        return False

    # --- steps ---

    def donate(self) -> str:
        if not self.open_island() or not self.open_building("Guild Lobby"):
            return "unknown_screen"
        if not self._expect(LOBBY_DONATION, "guild_donation"):
            return "unknown_screen"
        made = 0
        for _ in range(DONATION_MAX + 1):
            n = _num(self.det.read_text(DONATION_COUNT_ROI), r"Donations:(\d+)/")
            if n is None:
                log.warning("donation counter unreadable; stopping")
                break
            if n >= DONATION_MAX:
                break
            button = " ".join(t for t, _ in self.det.read_text(DONATION_BUTTON_ROI))
            cost = _num([(button, None)], r"(\d+)")
            if not re.search(r"Free", button, re.I) and (cost is None or cost > DONATION_MAX_COST):
                log.info("donation button %r is over the %d Dawnium cap; stopping", button, DONATION_MAX_COST)
                break
            self._tap(DONATION_BUTTON, 2.5)
            if self.det.detect().state == "confirm_dialog":
                text = " ".join(t for t, _ in self.det.read_text(CONFIRM_TEXT_ROI))
                c = _num([(text, None)], r"[x×](\d+)")
                if "donation" in text.lower() and c is not None and c <= DONATION_MAX_COST:
                    self._tap(CONFIRM_OK, 2.5)
                else:
                    log.warning("unexpected confirm %r; cancelling", text)
                    self._tap(nav.CONFIRM_CANCEL, 2)
                    break
            made += 1
        log.info("donations made: %d", made)
        return "done" if made else "nothing"

    def _our_name(self) -> str:
        self.nav.go_home()
        texts = self.det.read_text([100, 8, 220, 40])  # HUD name next to the portrait
        return texts[0][0].strip() if texts else ""

    def afk(self) -> str:
        me = self._our_name()
        for facility in AFK_FACILITIES:
            if not self.open_island() or not self.open_building(facility):
                return "unknown_screen"
            for page in range(2):  # the Forge has a second screen of slots below
                names = [t.strip() for t, _ in self.det.read_text([0, 100, 720, 1050])]
                if me and me in names:
                    log.info("already gathering in %s", facility)
                    return "nothing"
                slots = self.det.find_all("Guild.EmptySlot")
                if slots:
                    x, y, w, h = slots[0]
                    self._tap((x + w // 2, y + h // 2), 2.5)
                    if not any("AFK Details" in t for t, _ in self.det.read_text(AFK_TITLE_ROI)):
                        log.warning("slot tap did not open AFK Details; frame %s", save_unknown(self.dev, "guild_afk"))
                        return "unknown_screen"
                    self._tap(AFK_START, 3)
                    if self.det.detect().state == "confirm_dialog":  # "Currently AFK: ... Switch anyway?"
                        text = " ".join(t for t, _ in self.det.read_text(CONFIRM_TEXT_ROI))
                        if "switch" in text.lower():
                            self._tap(CONFIRM_OK, 3)
                        else:
                            self._tap(nav.CONFIRM_CANCEL, 2)
                            return "unknown_screen"
                    self._tap(POPUP_CLOSE, 2)  # "You received" (rewards from the old slot)
                    log.info("now gathering in %s", facility)
                    return "done"
                self.dev.swipe(360, 1000, 360, 400, 500)
                time.sleep(1.5)
            log.info("%s is full", facility)
        return "nothing"

    def conquest(self) -> str:
        if not self.open_island() or not self.open_building("Gate of Expedition"):
            return "unknown_screen"
        if not self._expect(EVENTS_CONQUEST, "guild_conquest", 10):
            return "unknown_screen"
        for _ in range(6):  # beaten floors: claim the chest, then step right to the live floor
            status = " ".join(t for t, _ in self.det.read_text(CONQUEST_STATUS_ROI))
            if "defeated" not in status.lower():
                break
            self._tap(CONQUEST_CHEST, 2.5)
            if self.det.detect().state != "guild_conquest":
                self._tap(POPUP_CLOSE, 2)
            self._tap(CONQUEST_NEXT, 2.5)
        fights = 0
        for _ in range(3):
            left = _num(self.det.read_text(CONQUEST_ATTEMPTS_ROI), r"Attempts:(\d+)/")
            if not left:
                break
            if not self._expect(CONQUEST_CHALLENGE, "battle_prep", 10):
                log.warning("Challenge did not open battle prep; frame %s", save_unknown(self.dev, "guild_conquest"))
                break
            self._tap(PREP_START, 3)
            if self.det.wait_for({"background_fight"}, 15, interval=1).state == "background_fight":
                self._tap(BACKGROUND_ICON, 3)
            fights += 1
            self.det.wait_for({"guild_conquest"}, 15, interval=1)
        n = 0
        self._tap(TAB_GOALS, 2.5)
        for tab in (GOALS_SERVER, GOALS_PERSONAL):
            self._tap(tab, 2)
            n += claims.claim_all(self.dev, self.det, home_state="guild_panel")
        log.info("conquest: %d fights started, %d goals claimed", fights, n)
        return "done" if fights or n else "nothing"

    STEPS = ["donate", "afk", "conquest"]

    def run(self, only=None) -> dict:
        names = [n for n in self.STEPS if not only or n in only]
        banner(log, "Guild", f"guild dailies: {', '.join(names)}", "each step tried once, then home")
        out = {}
        for name in names:
            try:
                out[name] = getattr(self, name)()
            except Exception as e:  # noqa: BLE001
                log.warning("[%s] failed: %s; frame %s", name, e, save_unknown(self.dev, f"guild_{name}"))
                out[name] = "error"
            log.info("[%s] %s", name, out[name])
        self.back_to_island()
        self.nav.go_home()
        return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--only", help="comma-separated: " + ", ".join(Guild.STEPS))
    args = p.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    dev = Device()
    print(json.dumps(Guild(dev, StateDetector(dev)).run(set(args.only.split(",")) if args.only else None)), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
