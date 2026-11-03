"""'Where am I' detector: checks the State.* pipeline nodes against one frame, no model calls.

Each screen the bot knows is a node named State.<Name> in resource/pipeline/state.json; its state id is the
snake_case name (State.MainMenu -> main_menu). State.Detect lists them in priority order and the DetectState
custom action below tries them one by one on one screenshot; the first hit wins, State.Unknown catches the rest.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Optional

from maa.context import Context
from maa.custom_action import CustomAction
from maa.resource import Resource
from maa.tasker import Tasker

from .device import PACKAGE, REPO_ROOT

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

    def as_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}


def state_name(node: str) -> str:
    # "State.MainMenu" -> "main_menu"; "State.Loading.Title" -> "loading" (variants share a state)
    name = node.split(".")[1]
    return "".join("_" + c.lower() if c.isupper() else c for c in name).lstrip("_")


class _DetectState(CustomAction):
    """Runs each node of custom_action_param.order on `frame`; remembers the first hit."""

    def __init__(self):
        super().__init__()
        self.frame = None  # set by StateDetector.detect() before posting the task
        self.hit = None  # (node name, RecognitionDetail)

    def run(self, context: Context, argv: CustomAction.RunArg) -> CustomAction.RunResult:
        order = json.loads(argv.custom_action_param)["order"]
        self.hit = None
        for node in order:
            detail = context.run_recognition(node, self.frame)
            if detail is not None and detail.hit:
                self.hit = (node, detail)
                break
        return CustomAction.RunResult(success=True)


class StateDetector:
    def __init__(self, device):
        """device: a sxs.device.Device, or sxs.replay.ImageDevice for offline checks."""
        self.device = device
        self.resource = Resource()
        self._action = _DetectState()
        self.resource.register_custom_action("DetectState", self._action)
        if not self.resource.post_bundle(RESOURCE_DIR).wait().succeeded:
            raise RuntimeError(f"Failed to load MaaFramework resource bundle at {RESOURCE_DIR}")
        self.tasker = Tasker()
        if not self.tasker.bind(self.resource, device.controller):
            raise RuntimeError("Failed to bind tasker")

    def states(self) -> list[str]:
        order = self.resource.get_node_data(ENTRY)["action"]["param"]["custom_action_param"]["order"]
        return [state_name(n) for n in order]

    def detect(self) -> Detection:
        start = time.perf_counter()
        foreground = self.device.foreground_package()
        if foreground != PACKAGE:
            return Detection(NOT_RUNNING, "", foreground=foreground,
                             elapsed_ms=int((time.perf_counter() - start) * 1000))
        self._action.frame = self.device.screenshot()
        self.tasker.post_task(ENTRY).wait()
        elapsed = int((time.perf_counter() - start) * 1000)
        if self._action.hit is None:
            return Detection(UNKNOWN, "", foreground=foreground, elapsed_ms=elapsed)
        node, reco = self._action.hit
        best = reco.best_result
        box = list(best.box) if best is not None and getattr(best, "box", None) else None
        text = getattr(best, "text", None) if best is not None else None
        return Detection(state_name(node), node, box=box, text=text, foreground=foreground, elapsed_ms=elapsed)

    def wait_for(self, states: set[str], timeout: float, interval: float = 1.0) -> Detection:
        """Poll until the detected state is in `states` or the timeout passes; returns the last detection."""
        deadline = time.monotonic() + timeout
        while True:
            det = self.detect()
            if det.state in states or time.monotonic() >= deadline:
                return det
            time.sleep(interval)
