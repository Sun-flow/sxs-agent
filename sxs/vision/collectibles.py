"""Exploration collectibles: a growing reference store of what the bot has met on the map (R-131, mae 2026-11-05).

    python -m sxs see collectibles [FRAME ...]   # list known references found on frames (default: live screenshot)

Every time an exploration loop taps something on the island map and it turns out to be a card (an interactable:
mine, ruin, statue, chest...) or a fight (a monster), `save()` keeps a crop of what was tapped in
resource/image/explore/collectibles/ with a row in manifest.json (name, kind collectible / interactable / monster,
area, date, stamina cost if any). `find()` template-matches those crops on a frame so a loop can head for known
targets even when the minimap shows nothing.

The explored-state gate lives here, not in the callers (mae, 2026-11-05, R-065): in an area still being explored,
fights and pickups are free, so matches are returned; in an explored or blessed area, monsters respawn and pickups
cost stamina, so `find()` returns nothing unless the caller opts in with farm=True (e.g. farming Battle Essence).
No model calls.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Optional

import cv2
import numpy as np

from ..core.marks import server_day
from ..core.paths import RESOURCE

log = logging.getLogger("sxs.vision.collectibles")

STORE = RESOURCE / "image" / "explore" / "collectibles"
MANIFEST = STORE / "manifest.json"
KINDS = ("collectible", "interactable", "monster")
TAG = "exploration collectibles"
CROP = 80  # px square around the tapped point (an object is about one 104 px map tile)
PER_NAME = 3  # crops kept per (name, area): new looks replace the oldest
PLAY_AREA = (0, 300, 720, 700)  # x, y, w, h searched on the island map (below the HUD, above the tracker)
THRESHOLD = 0.82


def _load() -> dict:
    try:
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"tag": TAG, "entries": []}


def _save_manifest(m: dict) -> None:
    STORE.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(m, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def _slug(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", (t or "unknown").lower()).strip("_")[:40] or "unknown"


def save(frame: np.ndarray, xy: tuple[int, int], name: str, kind: str, area: str = "",
         stamina: Optional[int] = None) -> Optional[str]:
    """Keep a crop of what was tapped at `xy` on `frame` (taken just before the tap). Returns the file name."""
    if kind not in KINDS or frame is None:
        return None
    x, y = int(xy[0]), int(xy[1])
    h, w = frame.shape[:2]
    x0, y0 = max(0, x - CROP // 2), max(0, y - CROP // 2)
    crop = frame[y0:min(h, y0 + CROP), x0:min(w, x0 + CROP)]
    if crop.shape[0] < CROP // 2 or crop.shape[1] < CROP // 2:
        return None
    m = _load()
    same = [e for e in m["entries"] if e["name"] == name and e.get("area", "") == area]
    n = (max((e.get("n", 0) for e in same), default=-1) + 1)
    fname = f"{kind}_{_slug(name)}_{_slug(area) if area else 'any'}_{n % PER_NAME}.png"
    STORE.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(STORE / fname), crop)
    m["entries"] = [e for e in m["entries"] if e["file"] != fname]
    m["entries"].append({"file": fname, "name": name, "kind": kind, "area": area, "date": server_day(),
                         "stamina": stamina, "n": n})
    m["tag"] = TAG
    _save_manifest(m)
    log.info("collectibles: saved %s (%s, %s)", fname, kind, area or "any area")
    from ..core import preroll

    preroll.save(kind, name, area)  # the frames leading up to it, for detector training (core/preroll.py)
    return fname


def find(frame: np.ndarray, explored: bool, farm: bool = False, area: str = "",
         kinds=KINDS) -> list[tuple[str, str, tuple[int, int], float]]:
    """Known references on `frame`: (name, kind, screen point, score), best first. The explored gate: in an
    explored or blessed area nothing is returned unless farm is True (R-065)."""
    if explored and not farm:
        return []
    entries = [e for e in _load()["entries"] if e["kind"] in kinds and (not area or e.get("area") in ("", area))]
    if not entries:
        return []
    x0, y0, w, h = PLAY_AREA
    region = cv2.cvtColor(frame[y0:y0 + h, x0:x0 + w], cv2.COLOR_BGR2GRAY)
    hits = []
    for e in entries:
        tpl = cv2.imread(str(STORE / e["file"]), cv2.IMREAD_GRAYSCALE)
        if tpl is None or tpl.shape[0] > region.shape[0] or tpl.shape[1] > region.shape[1]:
            continue
        res = cv2.matchTemplate(region, tpl, cv2.TM_CCOEFF_NORMED)
        _, score, _, (mx, my) = cv2.minMaxLoc(res)
        if score >= THRESHOLD:
            hits.append((e["name"], e["kind"], (x0 + mx + tpl.shape[1] // 2, y0 + my + tpl.shape[0] // 2),
                         round(float(score), 3)))
    hits.sort(key=lambda t: -t[3])
    return hits


def main(argv: list[str]) -> int:
    frames = [cv2.imread(p) for p in argv] if argv else None
    if frames is None:
        from ..core.device import Device
        frames = [Device().screenshot()]
    print(f"{len(_load()['entries'])} references in {STORE}")
    for f in frames:
        print(find(f, explored=False))
    return 0
