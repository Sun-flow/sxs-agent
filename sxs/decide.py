"""Decide what to do on a popup or card, given the current goal. No model calls.

Instead of "press the big button", read the card (title, body, buttons) and pick the option the rules in
resource/policy/cards.json say fits the goal and circumstances, which may be declining or dismissing it.
Cards no rule covers are dismissed and reported, so the supervisor (later, a model) can add a rule once.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Optional

from .device import REPO_ROOT
from .state import StateDetector

log = logging.getLogger("sxs.decide")

POLICY_PATH = REPO_ROOT / "resource" / "policy" / "cards.json"
CARD_ROI = [0, 250, 720, 820]  # where popups and cards sit
BACK_ARROW = (60, 1216)
OUTSIDE = (360, 1230)


@dataclass
class Context:
    goal: str = "idle"  # explore | daily | idle
    hp_ok: bool = True


@dataclass
class Card:
    title: str
    body: str
    buttons: dict[str, tuple[int, int]] = field(default_factory=dict)  # text -> tap point


@dataclass
class Choice:
    kind: str
    action: str  # "tap" or "dismiss"
    point: tuple[int, int]
    why: str


class Decider:
    def __init__(self, det: StateDetector):
        self.det = det
        self.policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
        self._buttons = re.compile(self.policy["buttons"])
        self._never = re.compile(self.policy["never"])

    def read_card(self, frame=None) -> Card:
        lines = self.det.read_text(CARD_ROI, frame)
        buttons, text = {}, []
        for t, (x, y, w, h) in lines:
            t = t.strip().rstrip(".")
            if self._buttons.match(t):
                buttons[t] = (x + w // 2, y + h // 2)
            elif t != "Confirm":
                text.append(t)
        return Card(title=text[0] if text else "", body=" ".join(text[1:]), buttons=buttons)

    def choose(self, card: Card, ctx: Context) -> Choice:
        for rule in self.policy["rules"]:
            when = rule.get("when", {})
            if "goal" in when and ctx.goal not in when["goal"]:
                continue
            if "hp_ok" in when and ctx.hp_ok != when["hp_ok"]:
                continue
            if not (re.search(rule["match"], card.title) or re.search(rule["match"], card.body)):
                continue
            pick = rule["choose"]
            if pick == "dismiss":
                point = BACK_ARROW if rule.get("dismiss_by") == "back" else OUTSIDE
                return Choice(rule["kind"], "dismiss", point, rule["why"])
            if pick == "cancel":
                pick = "^Cancel$"
            for text, point in card.buttons.items():
                if re.search(pick, text) and not self._never.search(text):
                    return Choice(rule["kind"], "tap", point, rule["why"])
        return Choice("unknown", "dismiss", OUTSIDE, f"no rule for card {card.title!r}")

    def decide(self, ctx: Context, frame=None) -> tuple[Card, Choice]:
        card = self.read_card(frame)
        choice = self.choose(card, ctx)
        log.info("card %r -> %s %s (%s)", card.title, choice.action, choice.point, choice.why)
        return card, choice
