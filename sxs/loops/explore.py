"""Explore Loop: finish "Explore <area>" quests by following the quest-tracker marker. No model calls.

    python -m sxs explore [--minutes 20] [--chain] [--choose REGEX]

On the island map, find the gold tracker ring (resource/pipeline/explore.json) and tap it. At a screen edge that pans
the camera to the target; on the map it walks there and collects or starts a fight. Fights, dialogue and reward
popups are handled as they come (`actions.common`), cards go through the card rules (`policy.decide`), stalls through
the unstick strategies (`actions.unstick`), HP through `actions.heal`. Stops when the tracker shows 100/100 (and
claims it), when no marker can be found, or on a screen it doesn't know. With --chain it carries on with the next
quest, and applies mae's retry rule to lost fights (2 retries, then strengthen once, then stop and ask).

`Explorer.step()` handles one detected screen; each `_on_<screen>` method returns None to keep going or a stop
reason (the loop's status).
"""

from __future__ import annotations

import logging
import re
import time
from typing import Optional

from ..actions import goto, heal
from ..actions.common import FIGHT_STATES, TOWER_STATES, pass_through
from ..actions.unstick import MARKER_TARGET_DYS, PAN_STEPS, npc_to_talk_to, unstick
from ..actions.watchdog import Heartbeat
from ..core import ui
from ..core.device import save_unknown
from ..core.loop import Loop, Result, banner
from ..core.nav import Navigator
from ..core.paths import LOGS
from ..policy.decide import Context, Decider
from ..vision.hp import HUD_HP_BAR, PREP_HP_BAR, bar_fraction
from ..vision.tracker import progress_signal, read_tracker, tracking_on, tracking_toggle
from . import tower
from .strengthen import Strengthener

log = logging.getLogger("sxs.loops.explore")

PAN_CENTER = (360, 560)  # where a hidden marker is dragged to
STALE_STEP_S = 15  # seconds of no progress per "stale" step (drives the tap-offset cycle)
STALE_LIMIT = 4  # stale steps (~1 min) before trying NPCs and guards
STALE_GIVE_UP_S = 300  # no progress for this long ends the run
SELF_TAP_LIMIT = 6  # own-profile opens without progress before the loop gives up
DECISION_OPTIONS = r"^(Ascend to|Change Class)"  # dialogue options a human decides
DIALOGUE_ROI = [0, 1020, 720, 230]  # speaker name and text in the story box
DIALOGUE_LOG = LOGS / "dialogue.log"
RETRIES = 2  # retries of a lost fight before strengthening (mae, 2026-11-03)
HEAL_BELOW = 80  # HP % under which the profile's Quick Heal (1 cooked dish) is used
REPEAT_LIMIT = 4  # same card title this many times in a row means the choice isn't working
CARD_STATES = ("defeated", "interact", "dungeon_floor", "confirm_dialog", "quest_detail")
LOSS_KINDS = ("wounded", "defeated")


def hud_hp(frame, bar=None) -> float:
    """HP as a fraction, from the HUD bar under our name (or another bar, e.g. PREP_HP_BAR)."""
    return bar_fraction(frame, bar or HUD_HP_BAR)


def log_dialogue(det) -> None:
    """Keep the story text: some quests are only explained in dialogue ("go see X in Y"), not in the tracker.
    Lines go to logs/dialogue.log (gitignored) for whoever gets stuck next: mae, or the model supervisor."""
    lines = [t for t, _ in det.read_text(DIALOGUE_ROI)]
    if lines:
        DIALOGUE_LOG.parent.mkdir(exist_ok=True)
        with DIALOGUE_LOG.open("a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {' | '.join(lines)}\n")


class Explorer:
    """One run of the quest follower. Stop reasons: complete, defeated, no_marker, no_tracker, unknown_card,
    repeating_card, needs_decision, stuck_home, stuck_progress, stuck_self, low_hp, unknown_screen, timeout."""

    def __init__(self, dev, det, minutes: float = 20, max_misses: int = 10, choose: Optional[str] = None):
        self.dev, self.det = dev, det
        self.decider, self.ctx = Decider(det), Context(goal="explore")
        self.deadline = time.monotonic() + minutes * 60
        self.max_misses, self.choose = max_misses, choose
        self.misses = self.unknowns = self.unknown_total = self.unknown_cards = self.repeats = self.home_taps = 0
        self.last_kind = self.last_progress = self.last_state = self.last_progress_seen = None
        self.stale, self.progress_at, self.unstick_round = 0, time.monotonic(), 0
        self.beat = Heartbeat()
        self.hit_self = False  # the last marker tap landed on our own character
        self.self_taps, self.charms_tried = 0, False
        self.after_fight = self.via_portrait = False
        self.heal_tries = self.prep_backouts = 0

    # --- the loop ---

    def run(self) -> str:
        while time.monotonic() < self.deadline:
            stop = self.step()
            if stop:
                return stop
        return "timeout"

    def step(self) -> Optional[str]:
        d = self.det.detect()
        self.beat.check(d, self.last_progress, self.progress_at)
        if d.state != self.last_state:
            log.info("state %s", d.state)
            self.last_state = d.state
        if d.state != "unknown":
            self.unknowns = 0
        if d.state not in ("home", "unknown", "loading"):
            self.home_taps = 0
        if d.state == "world_map":
            return self._on_world_map(d)
        if d.state in TOWER_STATES:
            return self._on_tower()
        if d.state == "battle_prep":
            return self._on_battle_prep()
        if d.state in FIGHT_STATES:
            self.after_fight = self.after_fight or d.state == "battle"
        if pass_through(self.dev, d, on_dialogue=lambda: log_dialogue(self.det)):
            return None
        if d.state in CARD_STATES:
            return self._on_card()
        if d.state == "player_profile":
            return self._on_profile(d)
        if d.state == "dialogue_choice":
            return self._on_dialogue_choice(d)
        if d.state == "home":
            return self._on_home()
        return self._on_unfamiliar()

    # --- island map ---

    def _on_world_map(self, d) -> Optional[str]:
        stop = self._hp_check()
        if stop is not False:
            return stop
        prog = self.det.find("Explore.Progress")
        if prog and prog.text != self.last_progress:
            self.last_progress = prog.text
            log.info("progress: %s", prog.text)
        done = self.det.find("Explore.Complete") or self.det.find("Explore.TrackerGiftMap")
        if done:
            gift = self.det.find("Explore.TrackerGift") or self.det.find("Explore.TrackerGiftMap")
            ui.tap_box(self.dev, (gift or done).box, 2)
            log.info("explore quest complete, reward claimed")
            return "complete"
        stop = self._watch_progress(prog)
        if stop is not False:
            return stop
        return self._follow_marker()

    def _hp_check(self):
        """mae, 2026-11-04: never start a fight under 70% HP; every map tap can start one. Returns False to carry on
        with the map, None to come back next step, or a stop reason."""
        if not self.via_portrait and hud_hp(self.dev.screenshot()) * 100 < heal.FIGHT_MIN_HP:
            self.heal_tries += 1
            if self.heal_tries > 3:
                # Quick Heal isn't raising HP (out of cooked dishes?): don't fight hurt; stop and say why.
                log.warning("HP still under %d%% after %d heals; stopping before any fight", heal.FIGHT_MIN_HP,
                            self.heal_tries - 1)
                return "low_hp"
            log.info("HP under %d%% on the HUD bar; healing before any fight", heal.FIGHT_MIN_HP)
            self.after_fight, self.via_portrait = False, True
            ui.tap(self.dev, ui.HUD_PORTRAIT, 2)
            return None
        if self.heal_tries and not self.via_portrait and hud_hp(self.dev.screenshot()) * 100 >= heal.FIGHT_MIN_HP:
            self.heal_tries = 0
        if self.after_fight:
            # mae, 2026-11-04: read HP from the HUD bar; open the profile through the HUD portrait (tapping the
            # character opens a picker when several things share its tile) only to heal, or once to fill charms.
            self.after_fight = False
            hp = hud_hp(self.dev.screenshot())
            if hp * 100 < HEAL_BELOW or not self.charms_tried:
                log.info("after the fight: HP %d%% from the HUD bar; opening the profile", hp * 100)
                self.via_portrait = True
                ui.tap(self.dev, ui.HUD_PORTRAIT, 2)
                return None
        return False

    def _watch_progress(self, prog):
        """Watchdog. "Stale" is time since progress last changed (walking to a far target takes many marker taps).
        Only the counter is compared: OCR flips "II" and "ll" in the area name from frame to frame; quests without
        a counter still change their goal text when they advance. Returns False to carry on, None or a stop reason."""
        signal = progress_signal(prog.text if prog else None)
        if signal != self.last_progress_seen:
            self.last_progress_seen, self.progress_at = signal, time.monotonic()
            self.unstick_round = self.self_taps = 0
        stale_s = time.monotonic() - self.progress_at
        self.stale = int(stale_s // STALE_STEP_S)
        if stale_s >= STALE_GIVE_UP_S:
            log.warning("no progress for %ds after %d unstick rounds; stopping", stale_s, self.unstick_round)
            return "stuck_progress"
        # mae, 2026-11-04: each ~minute without progress, try the next unstick strategy rather than repeating the
        # same marker tap until the give-up timer runs out.
        if self.stale < STALE_LIMIT * (self.unstick_round + 1):
            return False
        self.unstick_round += 1
        log.info("no progress for %ds: unstick round %d", stale_s, self.unstick_round)
        # The quest's area may be out of walking reach of the marker taps (a cliff or fog in between): walk there
        # with the area map first (mae's procedure), once per stall.
        area = re.search(r"Explore (.+?) \d+/\d+", self.last_progress or "")
        here = goto.area_name_here(self.det)
        if area and self.unstick_round == 1 and not goto.same_area(here, area.group(1)):
            log.info("unstick: walking to the quest's area %r with the area map", area.group(1))
            if goto.go_to(self.dev, self.det, area.group(1).strip()) == "arrived":
                return None
            # Unreachable on foot (its label sits in fog): go home, where the tracker offers to travel there.
            log.info("unstick: can't walk there; going home to travel via the tracker")
            return self._go_home_or_stop()
        if unstick(self.dev, self.det, self.unstick_round):
            return None
        return False

    def _follow_marker(self) -> Optional[str]:
        dev, det = self.dev, self.det
        pointer = det.find("Explore.EdgePointer")
        if pointer:
            # Boss or statue off screen: tapping the pointer pans the camera there; then tap what it shows.
            ui.tap_box(dev, pointer.box, 2.5)
            npc = npc_to_talk_to(det)
            if npc:
                ui.tap(dev, npc, 4)
                ui.tap(dev, npc, 3)  # the first tap selects and walks; the second opens it
            return None
        marker = det.find("Explore.Marker")
        if marker:
            self.misses = 0
            cx, cy = ui.centre(marker.box)
            at_edge = cx < 30 or cx > 690 or cy < 130 or cy > 930  # ring clipped by the screen edge
            # The ring floats above its target: tap the ring itself to pan, the spot under it to act. If progress
            # hasn't moved, the target may sit nearer or farther below the ring: vary the offset. If the last tap
            # below the ring opened our own profile, the ring is an edge pointer next to us: tap the ring.
            dy = MARKER_TARGET_DYS[(self.stale // 2) % len(MARKER_TARGET_DYS)]
            ui.tap(dev, (cx, cy if at_edge or self.hit_self else cy + dy), 3)
            self.hit_self = False
            return None
        hidden = det.find("Explore.MarkerAnywhere")
        if hidden:
            # The ring is under the HUD: drag the map so it moves toward the middle of the screen.
            x, y = ui.centre(hidden.box)
            dx, dy = PAN_CENTER[0] - x, PAN_CENTER[1] - y
            dev.swipe(PAN_CENTER[0] - dx // 2, PAN_CENTER[1] - dy // 2, PAN_CENTER[0] + dx // 2,
                      PAN_CENTER[1] + dy // 2, 500)
            time.sleep(1.5)
            return None
        self.misses += 1
        if self.misses >= self.max_misses:
            return "no_marker"
        if self.misses % 2 == 1:
            # The ring may be off screen or behind the chat panel: pan the map a step in turn up/down/left/right.
            sx, sy, ex, ey = PAN_STEPS[(self.misses // 2) % len(PAN_STEPS)]
            dev.swipe(sx, sy, ex, ey, 500)
            time.sleep(1.5)
            return None
        frame = dev.screenshot()
        toggle = tracking_toggle(det, frame)
        if not tracking_on(frame, toggle):
            dev.tap(*toggle)
        else:
            # Tracking is on but the ring is nowhere: re-toggle so the camera re-centres on the target.
            ui.tap(dev, toggle, 1.5)
            dev.tap(*toggle)
        time.sleep(2)
        return None

    # --- other screens ---

    def _go_home_or_stop(self) -> Optional[str]:
        try:
            Navigator(self.dev, self.det).go_home()
            return None
        except (RuntimeError, TimeoutError) as e:
            log.warning("%s; frame saved to %s", e, save_unknown(self.dev, "explore_home"))
            return "unknown_screen"

    def _on_tower(self) -> Optional[str]:
        # The quest's Go brought us to Fantasia Ascent ("Reach <Tower> Fn"): hand over to the tower loop, which
        # climbs with Auto Challenge until the first loss (no retries there), then carry on with the quest line.
        m = re.search(r"Reach (.+?) F ?(\d+)", self.last_progress or "")
        result = tower.climb(self.dev, self.det, m.group(1).strip() if m else None,
                             minutes=max(1.0, (self.deadline - time.monotonic()) / 60))
        log.info("tower climb: %s", result)
        if result not in tower.OK:
            return result
        stop = self._go_home_or_stop()
        if stop:
            return stop
        self.progress_at = time.monotonic()
        return None

    def _on_battle_prep(self) -> Optional[str]:
        hp = hud_hp(self.dev.screenshot(), PREP_HP_BAR)
        if hp * 100 < heal.FIGHT_MIN_HP and self.prep_backouts < 2:
            # mae, 2026-11-04: the bar under our character shows HP before the fight; heal first (also mid-way
            # through a mini-dungeon). Quick Heal opens from the portrait on any screen that shows it.
            self.prep_backouts += 1
            log.info("battle prep: HP %d%% < %d%%; healing first", hp * 100, heal.FIGHT_MIN_HP)
            self.via_portrait = True
            heal.quick_heal(self.dev, self.det, heal.RETRY)
            self.via_portrait = False
            return None
        self.prep_backouts = 0
        ui.tap(self.dev, ui.START_BATTLE, 3)
        return None

    def _on_card(self) -> Optional[str]:
        # Cards and dialogs: pick the option that fits the goal (resource/policy/cards.json).
        card, choice = self.decider.decide(self.ctx)
        self.repeats = self.repeats + 1 if card.title == self.last_kind else 0
        self.last_kind = card.title
        if self.repeats >= REPEAT_LIMIT:
            # The same choice keeps bringing the same card back: it isn't working, so stop and report.
            log.warning("card %r keeps coming back after %s; stopping", card.title, choice.action)
            return "repeating_card"
        ui.tap(self.dev, choice.point, 4)
        if choice.kind == "wounded":
            # "Badly wounded" comes after a lost fight (mae, 2026-11-04): a dead run, not a reason to carry on.
            log.info("lost the fight (badly wounded); healed, counting it as a loss")
            return "defeated"
        if choice.kind == "defeated":
            return "defeated"
        if choice.kind == "unknown":
            return self._unknown_card(card)
        return None

    def _unknown_card(self, card) -> Optional[str]:
        self.unknown_cards += 1
        if self.unknown_cards >= 3:
            log.warning("no rule for card %r; stopping so a rule can be added", card.title)
            return "unknown_card"
        return None

    def _on_profile(self, d) -> Optional[str]:
        if self.via_portrait:
            self.via_portrait = False  # opened on purpose: not a marker tap landing on us
        else:
            self.hit_self = True
            self.self_taps += 1
        if self.self_taps >= SELF_TAP_LIMIT:
            # The marker keeps landing on our own character and nothing moves. Stop and say so.
            log.warning("opened our own profile %d times without progress; stopping", self.self_taps)
            self.dev.tap(*ui.ABOVE_POPUP)
            return "stuck_self"
        # A red "!" over the character is not only low HP: it also means empty charm slots or gear to equip
        # (mae, 2026-11-04). Heal by the HP bar; fill charm slots once.
        hp = int(re.search(r"(\d+)%", d.text).group(1)) if d.text else 100
        if hp < HEAL_BELOW:
            log.info("HP %d%%: quick heal", hp)
            ui.tap(self.dev, ui.QUICK_HEAL, 2)
        elif not self.charms_tried:
            self.charms_tried = True
            n = Strengthener(self.dev, self.det).equip_charms(from_profile=True)
            log.info("profile: HP %d%%, equipped %d charm(s)", hp, n)
        else:
            ui.tap(self.dev, ui.ABOVE_POPUP, 1.5)  # above the popup; a tap below it doesn't close it
        return None

    def _on_dialogue_choice(self, d) -> Optional[str]:
        lines = self.det.read_text([60, 300, 600, 750])
        options = [t for t, _ in lines]
        picked = [b for t, b in lines if self.choose and re.search(self.choose, t)]
        if picked:
            # A human already made this call (--choose): take it.
            log.info("taking the chosen option %r", self.choose)
            ui.tap_box(self.dev, picked[0], 2)
            return None
        if any(re.search(DECISION_OPTIONS, t) for t in options):
            # A choice with lasting consequences (class): not the bot's call. Leave and report.
            leave = [b for t, b in self.det.read_text([60, 300, 600, 750]) if re.search(r"^Leave$", t)]
            if leave:
                self.dev.tap(*ui.centre(leave[0]))
            log.warning("needs a human decision: %s", options)
            return "needs_decision"
        ui.tap(self.dev, (360, d.box[1] + d.box[3] // 2), 1.5)  # the lowest option, nearest the speaker box
        return None

    def _on_home(self) -> Optional[str]:
        # The tracker panel on home either claims a finished quest or offers travel to the quest's island.
        tracked = read_tracker(self.det)
        if tracked is None:
            return "no_tracker"
        log.info("tracker: %s %s", tracked["title"], tracked["progress"])
        gift = self.det.find("Explore.TrackerGift")
        if gift:
            tracked["tap"] = ui.centre(gift.box)  # finished: the gift claims it
        self.home_taps += 1
        if self.home_taps > REPEAT_LIMIT * 2:
            return "stuck_home"  # tapping the tracker keeps landing back on home
        ui.tap(self.dev, tracked["tap"], 2.5)
        return None

    def _on_unfamiliar(self) -> Optional[str]:
        self.unknowns += 1
        self.unknown_total += 1
        if self.unknowns >= 5 or self.unknown_total >= 20:  # the second catches unknown <-> map loops
            log.warning("unfamiliar screen; frame saved to %s", save_unknown(self.dev, "explore"))
            return "unknown_screen"
        if self.unknowns >= 2:
            # Maybe a popup the detector doesn't know: a rule may still cover it, otherwise it's dismissed.
            card, choice = self.decider.decide(self.ctx)
            self.dev.tap(*choice.point)
            if choice.kind in LOSS_KINDS:
                # The loss dialog can show while the detector still reads "unknown": still a lost fight.
                time.sleep(3)
                log.info("lost the fight (%s); counting it as a loss", choice.kind)
                return "defeated"
            if choice.kind == "unknown" and card.buttons:  # a real card has buttons; battle damage numbers do not
                stop = self._unknown_card(card)
                if stop:
                    return stop
        time.sleep(1.5)
        return None


def follow_tracker(dev, det, minutes: float = 20, max_misses: int = 10, choose: Optional[str] = None) -> str:
    """One quest: see `Explorer` for the stop reasons."""
    return Explorer(dev, det, minutes, max_misses, choose).run()


def explore(dev, det, minutes: float = 20, chain: bool = False, choose: Optional[str] = None) -> Result:
    """The Explore Loop: follow quests until time runs out or something stops it (mae's retry rule with --chain)."""
    deadline = time.monotonic() + minutes * 60
    losses, strengthened, completed = 0, False, 0
    banner(log, "Explore", "follow the tracked quest line: walk to its marker, fight, open cards by the rules, "
           "hand tower and dungeon screens to their loops, claim finished quests" + (" and chain to the next" if chain else ""),
           f"{minutes:g} minutes, or a stop reason: unknown screen or card, no progress for "
           f"{STALE_GIVE_UP_S // 60} min after rotating unstick tries, a human decision, or still losing after "
           f"{RETRIES} retries and strengthening")
    while True:
        # Quests chain: after claiming one the tracker shows the next, so keep going until something else stops us.
        left = (deadline - time.monotonic()) / 60
        result = follow_tracker(dev, det, left, choose=choose) if left > 0 else "timeout"
        log.info("quest run: %s", result)
        if result == "complete":
            completed += 1
            losses, strengthened = 0, False
        elif result == "defeated" and chain:
            # mae's rule: heal and retry a lost fight up to 2 times; still losing means go home and get stronger,
            # and if that doesn't do it either, stop and ask.
            losses += 1
            if losses <= RETRIES:
                log.info("lost a fight; retry %d of %d after healing", losses, RETRIES)
            elif not strengthened:
                log.info("lost %d times in a row; getting stronger before one more try", losses)
                Strengthener(dev, det).run()
                strengthened = True
            else:
                return Result("needs_help", False, {"completed": completed, "why": "still losing after strengthening"})
            time.sleep(3)
            continue
        if result != "complete" or not chain:
            return Result(result, result == "complete", {"completed": completed})
        time.sleep(3)


def _args(p) -> None:
    p.add_argument("--minutes", type=float, default=2)  # mae, 2026-11-04: runs of 1-2 minutes
    p.add_argument("--chain", action="store_true", help="after a quest completes, carry on with the next one")
    p.add_argument("--choose", help="regex for a decision a human has made, e.g. '^Ascend to Mage$'")


def _run(ctx, opts) -> Result:
    return explore(ctx.dev, ctx.det, opts.minutes, opts.chain, opts.choose)


LOOP = Loop("explore", "Explore", "follow the tracked quest line (fights, cards, unstick, claims)", _run, _args,
            ok={"complete"})
