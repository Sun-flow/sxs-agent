"""Loops: goal-driven runs built on core, vision, policy and actions. Each module exposes `LOOP` (a
`sxs.core.loop.Loop`), and `python -m sxs <name>` runs it through `sxs.core.loop.run_cli`.

REGISTRY maps each command name to its module. Modules are imported only when their loop is run or listed, so
`python -m sxs --help` stays fast and one broken loop can't stop the others.
"""

from __future__ import annotations

import importlib

from ..core.loop import Loop

REGISTRY = {
    "daily": "sxs.loops.daily",
    "explore": "sxs.loops.explore",
    "roam": "sxs.loops.roam",
    "clear": "sxs.loops.clear",
    "goto": "sxs.actions.goto",
    "gather": "sxs.loops.gather",
    "upgrade": "sxs.loops.upgrade",
    "strengthen": "sxs.loops.strengthen",
    "gearswap": "sxs.loops.gearswap",
    "cart": "sxs.loops.cart",
    "tower": "sxs.loops.tower",
    "guild": "sxs.loops.guild",
    "mall": "sxs.loops.mall",
    "vendor": "sxs.loops.vendor",
    "tutorial": "sxs.loops.tutorial",
    "progress": "sxs.loops.progress",
    "pray": "sxs.loops.pray",  # handler-triggered only; no loop imports it
}


def get(name: str) -> Loop:
    loop = importlib.import_module(REGISTRY[name]).LOOP
    assert loop.name == name, f"{REGISTRY[name]}.LOOP is named {loop.name!r}, registered as {name!r}"
    return loop
