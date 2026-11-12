"""Pre-roll buffer: the last few frames the bot saw, saved as a sequence when it collects or fights something
(mae, 2026-11-11: "pre-roll buffer is a great idea ... do it"; docs/collectibles-capture-plan.md).

Every Device.screenshot() pushes its frame here (a reference, no copy work beyond numpy's). When a loop meets a
collectible, an interactable or a monster (the R-131 moments: sxs/vision/collectibles.save, a gather pickup), it
calls `save(...)`, which writes the buffer to captures/sequences/<name>/NN.png plus frames.json (the same layout as
`python -m sxs capture NAME --burst N`). captures/ is gitignored; frames reach docs/screens only after picking.

    SXS_PREROLL=12        frames kept (default 12; 0 turns it off)
    SXS_PREROLL_MAX_MB=500  stop writing once captures/sequences/ holds this much (default 500 MB)

At ~0.5-1.5 s between screenshots in the loops, 12 frames cover roughly the last 6-15 s before the event. Each
saved frame is a PNG of about 0.5-1 MB, so a sequence is about 6-12 MB; the size cap keeps a long run from filling
the disk (mae: shorten it if the frames bloat).
"""

from __future__ import annotations

import json
import logging
import os
import re
import threading
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Optional

from .paths import CAPTURES

log = logging.getLogger("sxs.preroll")
OUT = CAPTURES / "sequences"
MIN_GAP_S = 20.0  # one sequence per event: the same kind and area within this many seconds is skipped


def _size() -> int:
    try:
        return max(0, int(os.environ.get("SXS_PREROLL", "12")))
    except ValueError:
        return 12


def _cap_bytes() -> int:
    try:
        return int(float(os.environ.get("SXS_PREROLL_MAX_MB", "500")) * 1024 * 1024)
    except ValueError:
        return 500 * 1024 * 1024


_lock = threading.Lock()
_frames: deque = deque(maxlen=_size() or 1)
_last: dict[str, float] = {}


def push(frame) -> None:
    """Keep this frame (called by Device.screenshot)."""
    if frame is None or _size() == 0:
        return
    with _lock:
        _frames.append((time.time(), frame.copy()))


def clear() -> None:
    with _lock:
        _frames.clear()
        _last.clear()


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_") or "any"


def _used(out: Path) -> int:
    return sum(f.stat().st_size for f in out.rglob("*.png")) if out.exists() else 0


def save(kind: str, name: str = "", area: str = "", out: Optional[Path] = None) -> Optional[Path]:
    """Write the buffered frames as one sequence: seq_<kind>_<name>_<area>_<time>/. Returns its folder, or None
    (buffer off or empty, the same event saved under MIN_GAP_S ago, or the size cap reached)."""
    out = out or OUT
    with _lock:
        frames = list(_frames)
        key = f"{kind}|{name}|{area}"
        now = time.time()
        if not frames or now - _last.get(key, 0) < MIN_GAP_S:
            return None
        _last[key] = now
    if _used(out) >= _cap_bytes():
        log.warning("preroll: %s holds over SXS_PREROLL_MAX_MB; sequence not saved", out)
        return None
    import cv2

    folder = out / f"seq_{_slug(kind)}_{_slug(name)}_{_slug(area)}_{datetime.now():%Y%m%d_%H%M%S}"
    folder.mkdir(parents=True, exist_ok=True)
    rows = []
    t0 = frames[0][0]
    for i, (t, frame) in enumerate(frames, 1):
        f = folder / f"{i:02d}.png"
        cv2.imwrite(str(f), frame)
        rows.append({"file": f.name, "t": round(t - t0, 2)})
    (folder / "frames.json").write_text(json.dumps({"name": folder.name, "kind": kind, "what": name, "area": area,
                                                    "frames": rows, "preroll": True}, indent=1) + "\n",
                                        encoding="utf-8")
    log.info("preroll: saved %d frame(s) to %s", len(rows), folder)
    return folder
