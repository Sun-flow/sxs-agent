"""World collectible catalogue: the kinds a `world_collectible` detector box can be (mae, 2026-11-11).

    resource/world/collectibles.json   {"families": [...], "collectibles": [{"id", "name", "family", "resource",
                                        "cost", "look", "seen"}]}, append only (order sets export class ids)

Two tiers (docs/collectibles-capture-plan.md): every collectible is boxed once as class world_collectible with the
kind in the box's "collectible" field (and "cost" when the frame shows a cost other than the kind's default). The
export trains one class per kind, per family, or one for all (`python -m sxs dataset --collectibles`); the bot
rolls kinds up into families or "any collectible" from this table. Not to be confused with
sxs/vision/collectibles.py, the bot's own crop store of things it met (R-131).
"""

from __future__ import annotations

import json

from ..core.paths import RESOURCE

FILE = RESOURCE / "world" / "collectibles.json"
COSTS = ("free", "stamina")


def load() -> dict:
    data = json.loads(FILE.read_text(encoding="utf-8")) if FILE.exists() else {}
    return {"families": data.get("families", []), "collectibles": data.get("collectibles", [])}


def ids() -> list[str]:
    return [c["id"] for c in load()["collectibles"]]


def family(cid: str) -> str:
    return next((c["family"] for c in load()["collectibles"] if c["id"] == cid), "")
