"""'Where am I' detector: runs the State.* pipeline nodes against one frame, no model calls.

Each screen the bot knows is a node named State.<Name> in resource/pipeline/state.json. State.Detect lists
them in priority order; the first that recognises the frame wins and State.Unknown catches the rest.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional

from maa.resource import Resource
from maa.tasker import Tasker

from .device import PACKAGE, REPO_ROOT, Device

RESOURCE_DIR = REPO_ROOT / "resource"
ENTRY = "State.Detect"
NOT_RUNNING = "not_running"
UNKNOWN = "unknown"


@dataclass
class Detection:
    state: str
    node: str
    box: Optional[list[int]] = None
    text: Optional[str] = None
    foreground: Optional[str] = None
    elapsed_ms: int = 0
    checked: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v not in (None, [])}


def _state_name(node: str) -> str:
    # "State.HomeScreen" -> "home_screen"
    name = node.split(".", 1)[1]
    return "".join("_" + c.lower() if c.isupper() else c for c in name).lstrip("_")


class StateDetector:
    def __init__(self, device: Device):
        self.device = device
        self.resource = Resource()
        if not self.resource.post_bundle(RESOURCE_DIR).wait().succeeded:
            raise RuntimeError(f"Failed to load MaaFramework resource bundle at {RESOURCE_DIR}")
        self.tasker = Tasker()
        if not self.tasker.bind(self.resource, device.controller):
            raise RuntimeError("Failed to bind tasker")

    def states(self) -> list[str]:
        nxt = self.resource.get_node_data(ENTRY)["next"]
        return [_state_name(n["name"] if isinstance(n, dict) else n) for n in nxt]

    def detect(self) -> Detection:
        start = time.perf_counter()
        foreground = self.device.foreground_package()
        if foreground != PACKAGE:
            return Detection(NOT_RUNNING, "", foreground=foreground,
                             elapsed_ms=int((time.perf_counter() - start) * 1000))
        detail = self.tasker.post_task(ENTRY).wait().get()
        hit = detail.nodes[-1] if detail and detail.nodes else None
        elapsed = int((time.perf_counter() - start) * 1000)
        if hit is None or hit.name == ENTRY:
            return Detection(UNKNOWN, "", foreground=foreground, elapsed_ms=elapsed)
        reco = hit.recognition
        best = reco.best_result if reco else None
        box = list(best.box) if best is not None and getattr(best, "box", None) else None
        text = getattr(best, "text", None) if best is not None else None
        return Detection(_state_name(hit.name), hit.name, box=box, text=text,
                         foreground=foreground, elapsed_ms=elapsed)

    def wait_for(self, states: set[str], timeout: float, interval: float = 1.0) -> Detection:
        """Poll until the detected state is in `states` or the timeout passes; returns the last detection."""
        deadline = time.monotonic() + timeout
        while True:
            det = self.detect()
            if det.state in states or time.monotonic() >= deadline:
                return det
            time.sleep(interval)
