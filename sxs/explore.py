"""Finish an "Explore <area>" quest by following the quest-tracker marker. No model calls.

    python -m sxs.explore [--minutes 20]

Loop: on the island map, find the gold tracker ring (resource/pipeline/explore.json) and tap it. At a screen edge
that pans the camera to the target; on the map it walks there and collects or starts a fight. Fights, dialogue
and reward popups are handled as they come. Stops when the tracker shows 100/100 (and claims it), when no marker
can be found, or on a screen it doesn't know.
"""

from __future__ import annotations

import argparse
import logging
import sys
import re
import time
from typing import Optional

import cv2
import numpy as np

from . import nav, tower
from .device import REPO_ROOT, Device, banner, save_unknown
from .decide import Context, Decider
from .state import StateDetector
from .strengthen import Strengthener

log = logging.getLogger("sxs.explore")

TRACKING_TOGGLE = (290, 1012)
TRACKER_ROI = [0, 860, 330, 180]  # quest tracker panel on home
START_BATTLE = (360, 956)
PAN_CENTER = (360, 560)  # where a hidden marker is dragged to
PAN_STEPS = [(360, 800, 360, 450), (360, 400, 360, 750), (550, 600, 200, 600), (200, 600, 550, 600)]
MARKER_TARGET_DYS = [100, 60, 140, 30]  # how far below the tracker ring its target usually sits, best guess first
STALE_STEP_S = 15  # seconds of no progress per "stale" step (drives the tap-offset cycle)
STALE_LIMIT = 4  # stale steps (~1 min) before trying NPCs and guards
STALE_GIVE_UP_S = 300  # no progress for this long ends the run
SELF_TAP_LIMIT = 6  # own-profile opens without progress before the loop gives up
HEARTBEAT_S = 30  # liveness log line and stuck check interval
DECISION_OPTIONS = r"^(Ascend to|Change Class)"  # dialogue options a human decides
PLAYER_NAME = "gromb2"  # our character's name label, to tell our own "!" from an NPC's
NPC_DX, NPC_DY = 30, 50  # from the "!" bubble to the NPC's body
DIALOGUE_ROI = [0, 1020, 720, 230]  # speaker name and text in the story box
DIALOGUE_LOG = REPO_ROOT / "logs" / "dialogue.log"
RETRIES = 2  # retries of a lost fight before strengthening (mae, 2026-11-03)
HEAL_BELOW = 80  # HP % under which the profile's Quick Heal (1 cooked dish) is used
QUICK_HEAL = (510, 1064)
HUD_PORTRAIT = (70, 60)  # top-left avatar: opens the player profile (HP, Quick Heal, charms)
REPEAT_LIMIT = 4  # same card title this many times in a row means the choice isn't working
GUARD_DX, GUARD_DY = -35, 50  # from the top-right guard bracket to the monster


def tracking_toggle(det: StateDetector, frame: np.ndarray) -> tuple[int, int]:
    """Where the tracking icon is on the panel (it shifts with the title's length)."""
    icon = det.find("Explore.TrackingIcon", frame)
    if icon is None:
        return TRACKING_TOGGLE
    x, y, w, h = icon.box
    return x + w // 2, y + h // 2


def tracking_on(frame: np.ndarray, at: tuple[int, int] = TRACKING_TOGGLE) -> bool:
    """The target icon on the tracker panel is bright yellow when tracking is on, dim grey when off."""
    x, y = at
    patch = cv2.cvtColor(frame[y - 12:y + 12, x - 12:x + 12], cv2.COLOR_BGR2HSV)
    return float(np.percentile(patch[:, :, 2], 90)) > 150


def read_tracker(det: StateDetector) -> Optional[dict]:
    """Quest tracker panel on home (bottom left). Its height changes when it shows rewards, so read it by OCR.
    Returns title, progress ("a/b"), done flag and the point to tap (the title), or None if no panel."""
    # The home scene's own labels (e.g. the stone's "Class to Unlock") can sit inside this region; drop them.
    lines = [(t, b) for t, b in det.read_text(TRACKER_ROI) if not re.search(r"Un\W?l\W?[oa]c?k|to ?Un", t)]
    prog = next(((t, b) for t, b in lines if re.search(r"\d+/\d+", t)), None)
    if prog is None:
        if not lines:
            return None
        # Quests like "Reach Apprentice I" have no counter; tapping the title claims or opens them.
        title, (x, y, w, h) = lines[0]
        return {"title": title, "progress": "", "done": None, "tap": (x + w // 2, y + h // 2)}
    above = [(t, b) for t, b in lines if b[1] < prog[1][1]]
    title, box = above[-1] if above else prog
    a, b = map(int, re.search(r"(\d+)/(\d+)", prog[0]).groups())
    return {"title": title, "progress": f"{a}/{b}", "done": a >= b, "tap": (box[0] + box[2] // 2, box[1] + box[3] // 2)}


def progress_signal(text: Optional[str]) -> Optional[str]:
    """What counts as quest progress on the map tracker: its n/m counter, or else its goal text with OCR noise
    (spaces, I/l/1 confusions) squeezed out, so a counterless quest still shows progress when its goal changes."""
    if not text:
        return None
    m = re.search(r"\d+/\d+", text)
    if m:
        return m.group(0)
    return re.sub(r"[\sIl1|]", "", text).lower()


class Heartbeat:
    """Regular liveness check for long runs (mae, 2026-11-04: loops check for being stuck even when automated).
    Logs a line every HEARTBEAT_S with screen, map coordinates and time since progress, and warns when the screen
    and coordinates haven't changed at all for several beats, so a log shows at a glance where a loop idles."""

    def __init__(self) -> None:
        self.next_at = time.monotonic() + HEARTBEAT_S
        self.last = None
        self.same = 0

    def check(self, d, progress: Optional[str], progress_at: float) -> None:
        if time.monotonic() < self.next_at:
            return
        self.next_at = time.monotonic() + HEARTBEAT_S
        snap = (d.state, d.text)
        self.same = self.same + 1 if snap == self.last else 0
        self.last = snap
        log.info("heartbeat: %s %s | tracker %r | %ds since progress%s", d.state, d.text or "", progress,
                 time.monotonic() - progress_at, f" | unchanged x{self.same}" if self.same >= 2 else "")


def npc_to_talk_to(det: StateDetector) -> Optional[tuple[int, int]]:
    """Tap point for an NPC showing a red "!" bubble, skipping the one over our own character (name label below)."""
    frame = det.device.screenshot()
    for x, y, w, h in det.find_all("Explore.NpcAlert", frame):
        label = " ".join(t for t, _ in det.read_text([max(0, x - 80), y + 20, 180, 120], frame))
        if PLAYER_NAME in label:
            continue
        return x + w // 2 - NPC_DX, y + h // 2 + NPC_DY
    return None


def blocker_point(det: StateDetector) -> Optional[tuple[int, int]]:
    """Halfway between our character (found by its name label) and the marker's target: where a monster blocking
    the path usually stands (e.g. a wolf between the player and a sword pickup in Verdantglade I)."""
    frame = det.device.screenshot()
    marker = det.find("Explore.Marker", frame)
    me = [b for t, b in det.read_text([0, 120, 720, 840], frame) if PLAYER_NAME in t]
    if not marker or not me:
        return None
    mx, my, mw, mh = marker.box
    tx, ty = mx + mw // 2, my + mh // 2 + MARKER_TARGET_DYS[0]
    monsters = det.find_all("Explore.Monster", frame)
    if monsters:
        # A known monster on screen: the one nearest the target is the likely blocker.
        x, y, w, h = min(monsters, key=lambda b: (b[0] + b[2] / 2 - tx) ** 2 + (b[1] + b[3] / 2 - ty) ** 2)
        return x + w // 2, y + h // 2
    px, py = me[0][0] + me[0][2] // 2, me[0][1] - 50  # the label sits under the character's feet
    return (px + tx) // 2, (py + ty) // 2


def unstick(dev: Device, det: StateDetector, round_no: int) -> bool:
    """One unstick attempt when quest progress has stalled. Each round starts from a different strategy, so a
    strategy that acted but didn't help isn't simply repeated. Returns True if something was tapped."""

    def talk() -> bool:
        # The target may be gated behind an NPC or map object with a red "!" (Molly, then the Moonveil gate).
        npc = npc_to_talk_to(det)
        if not npc:
            return False
        log.info("unstick: tapping a red '!' at %s", npc)
        dev.tap(*npc)
        time.sleep(4)
        if det.detect().state == "world_map":
            dev.tap(*npc)  # the first tap may only walk there; the second opens it
            time.sleep(3)
        return True

    def blocker() -> bool:
        # A monster stands in the way between us and the target: tap the spot halfway there.
        point = blocker_point(det)
        if point:
            log.info("unstick: tapping between player and target at %s", point)
            dev.tap(*point)
            time.sleep(3)
        return bool(point)

    def guard() -> bool:
        box = det.find("Explore.GuardBracket")
        if box:
            log.info("unstick: attacking a guard at %s", box.box)
            dev.tap(box.box[0] + GUARD_DX, box.box[1] + GUARD_DY)
            time.sleep(3)
        return bool(box)

    def look_around() -> bool:
        # Something to talk to may be just off screen (or behind the chat panel): pan a step, look for a "!".
        sx, sy, ex, ey = PAN_STEPS[(round_no // len(strategies)) % len(PAN_STEPS)]
        log.info("unstick: panning to look for a red '!'")
        dev.swipe(sx, sy, ex, ey, 500)
        time.sleep(1.5)
        return talk() or True

    strategies = [talk, blocker, guard, look_around]
    first = (round_no - 1) % len(strategies)
    return any(f() for f in strategies[first:] + strategies[:first])


def log_dialogue(det: StateDetector) -> None:
    """Keep the story text: some quests are only explained in dialogue ("go see X in Y"), not in the tracker.
    Lines go to logs/dialogue.log (gitignored) for whoever gets stuck next: mae, or the model supervisor."""
    lines = [t for t, _ in det.read_text(DIALOGUE_ROI)]
    if lines:
        DIALOGUE_LOG.parent.mkdir(exist_ok=True)
        with DIALOGUE_LOG.open("a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {' | '.join(lines)}\n")


def follow_tracker(dev: Device, det: StateDetector, minutes: float = 20, max_misses: int = 10,
                   choose: Optional[str] = None) -> str:
    """Returns "complete", "defeated", "no_marker", "no_tracker", "unknown_card", "repeating_card", "needs_decision", "stuck_home", "stuck_progress", "unknown_screen" or
    "timeout"."""
    decider, ctx = Decider(det), Context(goal="explore")
    deadline = time.monotonic() + minutes * 60
    misses = unknowns = unknown_total = unknown_cards = repeats = home_taps = 0
    last_kind = None
    last_progress = last_state = last_progress_seen = None
    stale, progress_at, unstick_round = 0, time.monotonic(), 0
    beat = Heartbeat()
    hit_self = False  # the last marker tap landed on our own character
    self_taps, charms_tried = 0, False
    after_fight = via_portrait = False
    while time.monotonic() < deadline:
        d = det.detect()
        beat.check(d, last_progress, progress_at)
        if d.state != last_state:
            log.info("state %s", d.state)
            last_state = d.state
        if d.state != "unknown":
            unknowns = 0
        if d.state not in ("home", "unknown", "loading"):
            home_taps = 0
        if d.state == "world_map" and after_fight:
            # mae, 2026-11-04: check HP through the HUD portrait, not by tapping the character (several things on
            # one tile open a picker instead of the profile). The player_profile branch heals or fills charms.
            after_fight, via_portrait = False, True
            dev.tap(*HUD_PORTRAIT)
            time.sleep(2)
            continue
        if d.state == "world_map":
            prog = det.find("Explore.Progress")
            if prog and prog.text != last_progress:
                last_progress = prog.text
                log.info("progress: %s", prog.text)
            done = det.find("Explore.Complete") or det.find("Explore.TrackerGiftMap")
            if done:
                gift = det.find("Explore.TrackerGift") or det.find("Explore.TrackerGiftMap")
                x, y, w, h = (gift or done).box
                dev.tap(x + w // 2, y + h // 2)
                time.sleep(2)
                log.info("explore quest complete, reward claimed")
                return "complete"
            # "Stale" is time since progress last changed (walking to a far target takes many marker taps).
            # Compare only the counter: OCR flips "II" and "ll" in the area name from frame to frame.
            # Quests without a counter ("Unlock Moonveil Woods") still change their goal text when they advance.
            signal = progress_signal(prog.text if prog else None)
            if signal != last_progress_seen:
                last_progress_seen, progress_at = signal, time.monotonic()
                unstick_round = self_taps = 0
            stale_s = time.monotonic() - progress_at
            stale = int(stale_s // STALE_STEP_S)
            if stale_s >= STALE_GIVE_UP_S:
                log.warning("no progress for %ds after %d unstick rounds; stopping", stale_s, unstick_round)
                return "stuck_progress"
            # Watchdog (mae, 2026-11-04): each ~minute without progress, try the next unstick strategy rather
            # than repeating the same marker tap until the give-up timer runs out.
            if stale >= STALE_LIMIT * (unstick_round + 1):
                unstick_round += 1
                log.info("no progress for %ds: unstick round %d", stale_s, unstick_round)
                # The quest's area may be out of walking reach of the marker taps (a cliff or fog in between):
                # walk there with the area map first (mae's procedure), once per stall.
                area = re.search(r"Explore (.+?) \d+/\d+", last_progress or "")
                if area and unstick_round == 1:
                    from . import goto
                    log.info("unstick: walking to the quest's area %r with the area map", area.group(1))
                    if goto.go_to(dev, det, area.group(1).strip()) == "arrived":
                        continue
                    # Unreachable on foot (its label sits in fog): go home, where the tracker offers to travel there.
                    log.info("unstick: can't walk there; going home to travel via the tracker")
                    try:
                        nav.Navigator(dev, det).go_home()
                        continue
                    except (RuntimeError, TimeoutError) as e:
                        log.warning("%s; frame saved to %s", e, save_unknown(dev, "explore_home"))
                        return "unknown_screen"
                if unstick(dev, det, unstick_round):
                    continue
            pointer = det.find("Explore.EdgePointer")
            if pointer:
                # Boss or statue off screen: tapping the pointer pans the camera there; then tap what it shows.
                x, y, w, h = pointer.box
                dev.tap(x + w // 2, y + h // 2)
                time.sleep(2.5)
                npc = npc_to_talk_to(det)
                if npc:
                    dev.tap(*npc)
                    time.sleep(4)
                    dev.tap(*npc)  # the first tap selects and walks; the second opens it
                    time.sleep(3)
                continue
            marker = det.find("Explore.Marker")
            if marker:
                misses = 0
                x, y, w, h = marker.box
                cx, cy = x + w // 2, y + h // 2
                at_edge = cx < 30 or cx > 690 or cy < 130 or cy > 930  # ring clipped by the screen edge
                # The ring floats above its target: tap the ring itself to pan, the spot under it to act.
                # If progress hasn't moved, the target may sit nearer or farther below the ring: vary the offset.
                dy = MARKER_TARGET_DYS[(stale // 2) % len(MARKER_TARGET_DYS)]
                # If the last tap below the ring opened our own profile, the ring is an edge pointer next to us: tap it.
                dev.tap(cx, cy if at_edge or hit_self else cy + dy)
                hit_self = False
                time.sleep(3)
                continue
            hidden = det.find("Explore.MarkerAnywhere")
            if hidden:
                # The ring is under the HUD: drag the map so it moves toward the middle of the screen.
                x, y, w, h = hidden.box
                dx, dy = PAN_CENTER[0] - (x + w // 2), PAN_CENTER[1] - (y + h // 2)
                dev.swipe(PAN_CENTER[0] - dx // 2, PAN_CENTER[1] - dy // 2,
                          PAN_CENTER[0] + dx // 2, PAN_CENTER[1] + dy // 2, 500)
                time.sleep(1.5)
                continue
            misses += 1
            if misses >= max_misses:
                return "no_marker"
            if misses % 2 == 1:
                # The ring may be off screen or behind the chat panel: pan the map a step in turn up/down/left/right.
                sx, sy, ex, ey = PAN_STEPS[(misses // 2) % len(PAN_STEPS)]
                dev.swipe(sx, sy, ex, ey, 500)
                time.sleep(1.5)
                continue
            frame = dev.screenshot()
            toggle = tracking_toggle(det, frame)
            if not tracking_on(frame, toggle):
                dev.tap(*toggle)
            else:
                # Tracking is on but the ring is nowhere: re-toggle so the camera re-centres on the target.
                dev.tap(*toggle)
                time.sleep(1.5)
                dev.tap(*toggle)
            time.sleep(2)
        elif d.state in ("tower_list", "tower_floors", "tower_result"):
            # The quest's Go brought us to Fantasia Ascent ("Reach <Tower> Fn"): hand over to the tower loop, which
            # climbs with Auto Challenge until the first loss (no retries there), then carry on with the quest line.
            m = re.search(r"Reach (.+?) F ?(\d+)", last_progress or "")
            result = tower.climb(dev, det, m.group(1).strip() if m else None,
                                 minutes=max(1.0, (deadline - time.monotonic()) / 60))
            log.info("tower climb: %s", result)
            if result not in ("reached", "floors_done", "lost"):
                return result
            try:
                nav.Navigator(dev, det).go_home()
            except (RuntimeError, TimeoutError) as e:
                log.warning("%s; frame saved to %s", e, save_unknown(dev, "explore_home"))
                return "unknown_screen"
            progress_at = time.monotonic()
        elif d.state == "battle_prep":
            dev.tap(*START_BATTLE)
            time.sleep(3)
        elif d.state in ("battle", "loading"):
            after_fight = after_fight or d.state == "battle"
            time.sleep(2)
        elif d.state in ("defeated", "interact", "dungeon_floor", "confirm_dialog", "quest_detail"):
            # Cards and dialogs: pick the option that fits the goal (resource/policy/cards.json).
            card, choice = decider.decide(ctx)
            repeats = repeats + 1 if card.title == last_kind else 0
            last_kind = card.title
            if repeats >= REPEAT_LIMIT:
                # The same choice keeps bringing the same card back: it isn't working, so stop and report.
                log.warning("card %r keeps coming back after %s; stopping", card.title, choice.action)
                return "repeating_card"
            dev.tap(*choice.point)
            time.sleep(4)
            if choice.kind == "defeated":
                return "defeated"
            if choice.kind == "unknown":
                unknown_cards += 1
                if unknown_cards >= 3:
                    log.warning("no rule for card %r; stopping so a rule can be added", card.title)
                    return "unknown_card"
        elif d.state == "player_profile":
            if via_portrait:
                via_portrait = False  # opened on purpose: not a marker tap landing on us
            else:
                hit_self = True
                self_taps += 1
            if self_taps >= SELF_TAP_LIMIT:
                # Watchdog: the marker keeps landing on our own character and nothing moves. Stop and say so.
                log.warning("opened our own profile %d times without progress; stopping", self_taps)
                dev.tap(360, 60)
                return "stuck_self"
            # Opened by tapping our own character. A red "!" over the character is not only low HP: it also means
            # empty charm slots or gear to equip (mae, 2026-11-04). Heal by the HP bar; fill charm slots once.
            hp = int(re.search(r"(\d+)%", d.text).group(1)) if d.text else 100
            if hp < HEAL_BELOW:
                log.info("HP %d%%: quick heal", hp)
                dev.tap(*QUICK_HEAL)
                time.sleep(2)
            elif not charms_tried:
                charms_tried = True
                n = Strengthener(dev, det).equip_charms(from_profile=True)
                log.info("profile: HP %d%%, equipped %d charm(s)", hp, n)
            else:
                dev.tap(360, 60)  # above the popup; a tap below it doesn't close it
                time.sleep(1.5)
        elif d.state == "dialogue_choice":
            lines = det.read_text([60, 300, 600, 750])
            options = [t for t, _ in lines]
            picked = [b for t, b in lines if choose and re.search(choose, t)]
            if picked:
                # A human already made this call (--choose): take it.
                x, y, w, h = picked[0]
                log.info("taking the chosen option %r", choose)
                dev.tap(x + w // 2, y + h // 2)
                time.sleep(2)
                continue
            if any(re.search(DECISION_OPTIONS, t) for t in options):
                # A choice with lasting consequences (class): not the bot's call. Leave and report.
                leave = [b for t, b in det.read_text([60, 300, 600, 750]) if re.search(r"^Leave$", t)]
                if leave:
                    x, y, w, h = leave[0]
                    dev.tap(x + w // 2, y + h // 2)
                log.warning("needs a human decision: %s", options)
                return "needs_decision"
            dev.tap(360, d.box[1] + d.box[3] // 2)  # the lowest option, nearest the speaker box
            time.sleep(1.5)
        elif d.state == "dialogue":
            log_dialogue(det)
            dev.tap(*nav.DIALOGUE_NEXT)
            time.sleep(1.2)
        elif d.state in ("reward_popup", "tap_to_continue"):
            dev.tap(*nav.REWARD_CLOSE)
            time.sleep(1.2)
        elif d.state == "home":
            # The tracker panel on home either claims a finished quest or offers travel to the quest's island.
            tracked = read_tracker(det)
            if tracked is None:
                return "no_tracker"
            log.info("tracker: %s %s", tracked["title"], tracked["progress"])
            gift = det.find("Explore.TrackerGift")
            if gift:
                x, y, w, h = gift.box
                tracked["tap"] = (x + w // 2, y + h // 2)  # finished: the gift claims it
            home_taps += 1
            if home_taps > REPEAT_LIMIT * 2:
                return "stuck_home"  # tapping the tracker keeps landing back on home
            dev.tap(*tracked["tap"])
            time.sleep(2.5)
        else:
            unknowns += 1
            unknown_total += 1
            if unknowns >= 5 or unknown_total >= 20:  # the second catches unknown <-> map loops
                log.warning("unfamiliar screen; frame saved to %s", save_unknown(dev, "explore"))
                return "unknown_screen"
            if unknowns >= 2:
                # Maybe a popup the detector doesn't know: a rule may still cover it, otherwise it's dismissed.
                card, choice = decider.decide(ctx)
                dev.tap(*choice.point)
                if choice.kind == "unknown" and card.buttons:  # a real card has buttons; battle damage numbers do not
                    unknown_cards += 1
                    if unknown_cards >= 3:
                        log.warning("no rule for card %r; stopping so a rule can be added", card.title)
                        return "unknown_card"
            time.sleep(1.5)
    return "timeout"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--minutes", type=float, default=20)
    p.add_argument("--chain", action="store_true", help="after a quest completes, carry on with the next one")
    p.add_argument("--choose", help="regex for a decision a human has made, e.g. '^Ascend to Mage$'")
    args = p.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    dev = Device()
    det = StateDetector(dev)
    deadline = time.monotonic() + args.minutes * 60
    losses, strengthened = 0, False
    banner(log, "Explore", "follow the tracked quest line: walk to its marker, fight, open cards by the rules, "
           "hand tower and dungeon screens to their loops, claim finished quests"
           + (" and chain to the next" if args.chain else ""),
           f"{args.minutes:g} minutes, or a stop reason: unknown screen or card, no progress for "
           f"{STALE_GIVE_UP_S // 60} min after rotating unstick tries, a human decision, or still losing after "
           f"{RETRIES} retries and strengthening")
    while True:
        # Quests chain: after claiming one the tracker shows the next, so keep going until something else stops us.
        left = (deadline - time.monotonic()) / 60
        result = follow_tracker(dev, det, left, choose=args.choose) if left > 0 else "timeout"
        print(result, flush=True)
        if result == "complete":
            losses, strengthened = 0, False
        elif result == "defeated" and args.chain:
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
                print("needs_help: still losing after strengthening", flush=True)
                return 1
            time.sleep(3)
            continue
        if result != "complete" or not args.chain:
            return 0 if result == "complete" else 1
        time.sleep(3)


if __name__ == "__main__":
    sys.exit(main())
