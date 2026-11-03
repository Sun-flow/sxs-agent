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

from . import nav
from .device import Device
from .decide import Context, Decider
from .state import StateDetector

log = logging.getLogger("sxs.explore")

TRACKING_TOGGLE = (290, 1012)
TRACKER_ROI = [0, 860, 330, 180]  # quest tracker panel on home
START_BATTLE = (360, 956)
PAN_CENTER = (360, 560)  # where a hidden marker is dragged to
MARKER_TARGET_DYS = [100, 60, 140, 30]  # how far below the tracker ring its target usually sits, best guess first
STALE_LIMIT = 4
STALE_GIVE_UP = 16  # map visits with no progress before the run stops
DECISION_OPTIONS = r"^(Ascend to|Change Class)"  # dialogue options a human decides
HEAL_BELOW = 80  # HP % under which the profile's Quick Heal (1 cooked dish) is used
QUICK_HEAL = (510, 1064)
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


def follow_tracker(dev: Device, det: StateDetector, minutes: float = 20, max_misses: int = 6,
                   choose: Optional[str] = None) -> str:
    """Returns "complete", "defeated", "no_marker", "no_tracker", "unknown_card", "repeating_card", "needs_decision", "stuck_home", "stuck_progress", "unknown_screen" or
    "timeout"."""
    decider, ctx = Decider(det), Context(goal="explore")
    deadline = time.monotonic() + minutes * 60
    misses = unknowns = unknown_total = unknown_cards = repeats = home_taps = 0
    last_kind = None
    last_progress = last_state = last_progress_seen = None
    stale = 0  # map visits in a row with no change in progress
    while time.monotonic() < deadline:
        d = det.detect()
        if d.state != last_state:
            log.info("state %s", d.state)
            last_state = d.state
        if d.state != "unknown":
            unknowns = 0
        if d.state not in ("home", "unknown", "loading"):
            home_taps = 0
        if d.state == "world_map":
            prog = det.find("Explore.Progress")
            if prog and prog.text != last_progress:
                last_progress = prog.text
                log.info("progress: %s", prog.text)
            done = det.find("Explore.Complete")
            if done:
                x, y, w, h = done.box
                dev.tap(x + w // 2, y + h // 2)
                time.sleep(2)
                log.info("explore quest complete, reward claimed")
                return "complete"
            if prog and prog.text == last_progress_seen:
                stale += 1
            else:
                stale, last_progress_seen = 0, prog.text if prog else None
            if stale >= STALE_GIVE_UP:
                return "stuck_progress"
            if stale >= STALE_LIMIT:
                # Progress stuck while acting on the marker: the target may be guarded. Fight a bracketed monster.
                guard = det.find("Explore.GuardBracket")
                if guard:
                    log.info("progress stuck; attacking a guard at %s", guard.box)
                    dev.tap(guard.box[0] + GUARD_DX, guard.box[1] + GUARD_DY)
                    stale = 0
                    time.sleep(3)
                    continue
            marker = det.find("Explore.Marker")
            if marker:
                misses = 0
                x, y, w, h = marker.box
                cx, cy = x + w // 2, y + h // 2
                at_edge = cx < 60 or cx > 660 or cy < 150 or cy > 900
                # The ring floats above its target: tap the ring itself to pan, the spot under it to act.
                # If progress hasn't moved, the target may sit nearer or farther below the ring: vary the offset.
                dy = MARKER_TARGET_DYS[(stale // 2) % len(MARKER_TARGET_DYS)]
                dev.tap(cx, cy if at_edge else cy + dy)
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
        elif d.state == "battle_prep":
            dev.tap(*START_BATTLE)
            time.sleep(3)
        elif d.state in ("battle", "loading"):
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
            # Opened by tapping our own character. Top up HP here if it's low, then close.
            hp = int(re.search(r"(\d+)%", d.text).group(1)) if d.text else 100
            if hp < HEAL_BELOW:
                log.info("HP %d%%: quick heal", hp)
                dev.tap(*QUICK_HEAL)
                time.sleep(2)
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
            home_taps += 1
            if home_taps > REPEAT_LIMIT * 2:
                return "stuck_home"  # tapping the tracker keeps landing back on home
            dev.tap(*tracked["tap"])
            time.sleep(2.5)
        else:
            unknowns += 1
            unknown_total += 1
            if unknowns >= 5 or unknown_total >= 20:  # the second catches unknown <-> map loops
                return "unknown_screen"
            if unknowns >= 2:
                # Maybe a popup the detector doesn't know: a rule may still cover it, otherwise it's dismissed.
                card, choice = decider.decide(ctx)
                dev.tap(*choice.point)
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
    while True:
        # Quests chain: after claiming one the tracker shows the next, so keep going until something else stops us.
        left = (deadline - time.monotonic()) / 60
        result = follow_tracker(dev, det, left, choose=args.choose) if left > 0 else "timeout"
        print(result, flush=True)
        if result != "complete" or not args.chain:
            return 0 if result == "complete" else 1
        time.sleep(3)


if __name__ == "__main__":
    sys.exit(main())
