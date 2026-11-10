"""'Where am I' detector: checks the State.* pipeline nodes against one frame, no model calls.

Each screen the bot knows is a node named State.<Name> in resource/pipeline/state.json; its state id is the
snake_case name (State.MainMenu -> main_menu). State.Detect lists them in priority order and the DetectState
custom action below tries them one by one on one screenshot; the first hit wins, State.Unknown catches the rest.

Speed (docs/vision-upgrade.md, mae 2026-11-10). Running each OCR node on its own cost up to 52 OCR passes a check
(~2.8 s on the world map, ~5.5 s on an unknown screen, measured offline). So detect():
- reads each region in State.Detect's `strips` once per frame (today one: the whole screen, ~0.6-1.5 s offline
  against up to ~7 s for the old node-by-node chain), the first time a node inside it is tried, and matches that
  node's `expected` regexes against the lines whose centre falls in the node's roi (`path` "strip"). Nodes listed
  in `exact` (a whole-screen read misses them), and every node that is not plain OCR (templates, Or), still run
  their own recognition;
- returns the last detection again when the frame has not visibly changed and less than SAME_FRAME_S passed
  (`path` "cache"): the same pixels give the same answer;
- asks the emulator which app is in front only when the chain says unknown (a crashed game shows the launcher,
  so go_home can relaunch it). mae, 2026-11-10: no check on known screens. This is the app inside the emulator,
  not the emulator window on the desktop.
find(), find_all() and read_text() are unchanged: they run exactly the node they name.
"""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass, replace
from typing import Optional

import cv2
import numpy as np

from maa.context import Context
from maa.custom_action import CustomAction
from maa.resource import Resource
from maa.tasker import Tasker

from .device import PACKAGE, REPO_ROOT

RESOURCE_DIR = REPO_ROOT / "resource"
ENTRY = "State.Detect"
NOT_RUNNING = "not_running"
UNKNOWN = "unknown"
SAME_FRAME_S = 2.0  # reuse the last detection for an unchanged frame at most this long
THUMB = (45, 80)  # fingerprint size (w, h): one cell per 16x16 px of the 720x1280 frame
CELL_DIFF, CELLS_CHANGED = 24, 3  # a frame changed when this many cells moved by more than CELL_DIFF grey levels


@dataclass
class Detection:
    state: str
    node: str
    box: Optional[list[int]] = None
    text: Optional[str] = None
    foreground: Optional[str] = None
    elapsed_ms: int = 0
    path: Optional[str] = None  # how the answer was found: "cache", "strip" (shared strip read) or "node" (own run)

    def as_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}


def state_name(node: str) -> str:
    # "State.MainMenu" -> "main_menu"; "State.Loading.Title" -> "loading" (variants share a state)
    name = node.split(".")[1]
    return "".join("_" + c.lower() if c.isupper() else c for c in name).lstrip("_")


def fingerprint(frame: np.ndarray) -> np.ndarray:
    """A 45x80 grey thumbnail: enough to tell whether anything on screen moved (~0.5 ms)."""
    return cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), THUMB, interpolation=cv2.INTER_AREA).astype(np.int16)


def same_frame(a: Optional[np.ndarray], b: Optional[np.ndarray]) -> bool:
    return a is not None and b is not None and int((np.abs(a - b) > CELL_DIFF).sum()) < CELLS_CHANGED


def _inside(box, roi) -> bool:
    x, y, w, h = box
    cx, cy = x + w / 2, y + h / 2
    rx, ry, rw, rh = roi
    return rx <= cx <= rx + rw and ry <= cy <= ry + rh


def _contains(outer, inner) -> bool:
    ox, oy, ow, oh = outer
    x, y, w, h = inner
    return ox <= x and oy <= y and x + w <= ox + ow and y + h <= oy + oh


class _DetectState(CustomAction):
    """Runs each node of custom_action_param.order on `frame`; remembers the first hit.

    With `strips` in the param, a plain OCR node whose roi lies inside a strip is answered from one OCR of that
    strip (read once per frame) instead of its own OCR. Without it (find/find_all), every node runs as itself."""

    def __init__(self):
        super().__init__()
        self.frame = None  # set by StateDetector.detect() before posting the task
        self.hit = None  # (node name, RecognitionDetail) for a node's own run, (node name, None, box, text) from a strip
        self.specs: dict = {}  # node -> {"roi", "expected": [compiled], "threshold"} for plain OCR nodes

    def _strip_lines(self, context: Context, roi) -> list:
        override = {"Read.Text": {"recognition": "OCR", "roi": roi, "pre_delay": 0, "post_delay": 0}}
        detail = context.run_recognition("Read.Text", self.frame, override)
        if detail is None:
            return []
        return [(r.text, list(r.box), getattr(r, "score", 1.0)) for r in detail.all_results if r.text]

    def run(self, context: Context, argv: CustomAction.RunArg) -> CustomAction.RunResult:
        param = json.loads(argv.custom_action_param)
        order = param["order"]
        strips = param.get("strips") or {}
        exact = set(param.get("exact") or ())
        read: dict[str, list] = {}  # strip name -> its lines, read on first use
        self.hit = None
        for node in order:
            spec = self.specs.get(node)
            strip = None
            if spec and strips and node not in exact:
                strip = next((k for k, r in strips.items() if _contains(r, spec["roi"])), None)
            if strip is not None:
                if strip not in read:
                    read[strip] = self._strip_lines(context, strips[strip])
                for text, box, score in read[strip]:
                    if score >= spec["threshold"] and _inside(box, spec["roi"]) \
                            and any(rx.search(text) for rx in spec["expected"]):
                        self.hit = (node, None, box, text)
                        break
                if self.hit:
                    break
                continue
            detail = context.run_recognition(node, self.frame)
            if detail is not None and detail.hit:
                self.hit = (node, detail)
                break
        return CustomAction.RunResult(success=True)


class StateDetector:
    def __init__(self, device):
        """device: a sxs.core.device.Device, or sxs.core.replay.ImageDevice for offline checks."""
        self.device = device
        self.resource = Resource()
        self._action = _DetectState()
        self.resource.register_custom_action("DetectState", self._action)
        self.inference = _choose_inference(self.resource)
        if not self.resource.post_bundle(RESOURCE_DIR).wait().succeeded:
            raise RuntimeError(f"Failed to load MaaFramework resource bundle at {RESOURCE_DIR}")
        self.last_frame = None  # the frame the last detect() used, for overlay checks (sxs/core/interrupts.py)
        self.tasker = Tasker()
        if not self.tasker.bind(self.resource, device.controller):
            raise RuntimeError("Failed to bind tasker")
        self._action.specs = self._ocr_specs()
        self._last: Optional[Detection] = None
        self._last_print = None
        self._last_at = 0.0

    def _ocr_specs(self) -> dict:
        """Plain OCR State nodes (no colour filter, replace or only_rec) that a strip read can answer."""
        specs = {}
        for node in self.resource.get_node_data(ENTRY)["action"]["param"]["custom_action_param"]["order"]:
            reco = (self.resource.get_node_data(node) or {}).get("recognition", {})
            p = reco.get("param", {})
            if reco.get("type") != "OCR" or p.get("color_filter") or p.get("replace") or p.get("only_rec"):
                continue
            if any(p.get("roi_offset") or []) or not isinstance(p.get("roi"), list):
                continue
            specs[node] = {"roi": p["roi"], "threshold": p.get("threshold", 0.3),
                           "expected": [re.compile(e) for e in p.get("expected") or []]}
        return {n: s for n, s in specs.items() if s["expected"]}

    def states(self) -> list[str]:
        order = self.resource.get_node_data(ENTRY)["action"]["param"]["custom_action_param"]["order"]
        return [state_name(n) for n in order]

    def detect(self) -> Detection:
        start = time.perf_counter()
        now = time.monotonic()
        ms = lambda: int((time.perf_counter() - start) * 1000)  # noqa: E731
        foreground = None
        frame = self.device.screenshot()
        self._action.frame = self.last_frame = frame
        fp = fingerprint(frame)
        if self._last is not None and now - self._last_at < SAME_FRAME_S and same_frame(fp, self._last_print):
            return replace(self._last, elapsed_ms=ms(), path="cache")
        self.tasker.post_task(ENTRY).wait()
        hit = self._action.hit
        if hit is None:
            foreground = self.device.foreground_package()  # unknown: is the game still the app in front?
            if foreground != PACKAGE:
                self.last_frame = None
                return Detection(NOT_RUNNING, "", foreground=foreground, elapsed_ms=ms())
            det = Detection(UNKNOWN, "", foreground=foreground, elapsed_ms=ms(), path="node")
        elif hit[1] is None:  # answered from a strip read
            node, _, box, text = hit
            det = Detection(state_name(node), node, box=box, text=text, foreground=foreground or PACKAGE,
                            elapsed_ms=ms(), path="strip")
        else:
            node, reco = hit
            best = reco.best_result
            box = list(best.box) if best is not None and getattr(best, "box", None) else None
            text = getattr(best, "text", None) if best is not None else None
            det = Detection(state_name(node), node, box=box, text=text, foreground=foreground or PACKAGE,
                            elapsed_ms=ms(), path="node")
        self._last, self._last_print, self._last_at = det, fp, time.monotonic()
        return det

    def forget(self) -> None:
        """Drop the cached detection (the next detect() runs the chain even on an unchanged frame)."""
        self._last = None

    def find(self, node: str, frame=None) -> Optional[Detection]:
        """Run one pipeline node's recognition (e.g. "Explore.Marker") on `frame` or a fresh screenshot.
        Returns a Detection whose state is the node name, or None if it doesn't match."""
        start = time.perf_counter()
        self._action.frame = self.device.screenshot() if frame is None else frame
        self.tasker.post_task(ENTRY, {ENTRY: {"custom_action_param": {"order": [node]}}}).wait()
        if self._action.hit is None:
            return None
        best = self._action.hit[1].best_result
        return Detection(node, node, box=list(best.box) if best is not None else None,
                         text=getattr(best, "text", None), elapsed_ms=int((time.perf_counter() - start) * 1000))

    def find_all(self, node: str, frame=None) -> list[list[int]]:
        """Boxes of every match of a node's recognition (best first), e.g. several NPC alert bubbles."""
        self._action.frame = self.device.screenshot() if frame is None else frame
        self.tasker.post_task(ENTRY, {ENTRY: {"custom_action_param": {"order": [node]}}}).wait()
        if self._action.hit is None:
            return []
        return [list(r.box) for r in self._action.hit[1].filtered_results]

    def read_text(self, roi: list[int], frame=None) -> list[tuple[str, list[int]]]:
        """Every OCR line inside roi as (text, box), top to bottom. For reading popups whose wording varies."""
        self._action.frame = self.device.screenshot() if frame is None else frame
        override = {ENTRY: {"custom_action_param": {"order": ["Read.Text"]}},
                    "Read.Text": {"recognition": "OCR", "roi": roi, "pre_delay": 0, "post_delay": 0}}
        self.tasker.post_task(ENTRY, override).wait()
        if self._action.hit is None:
            return []
        lines = [(r.text, list(r.box)) for r in self._action.hit[1].all_results if r.text]
        return sorted(lines, key=lambda t: (t[1][1], t[1][0]))

    def wait_for(self, states: set[str], timeout: float, interval: float = 1.0) -> Detection:
        """Poll until the detected state is in `states` or the timeout passes; returns the last detection."""
        deadline = time.monotonic() + timeout
        while True:
            det = self.detect()
            if det.state in states or time.monotonic() >= deadline:
                return det
            time.sleep(interval)


def _choose_inference(resource: Resource) -> str:
    """Where OCR runs: SXS_INFERENCE=cpu, directml (Windows GPU) or auto; unset keeps MaaFramework's default.
    Must run before the bundle loads. Returns what was asked for (the library falls back to CPU on failure)."""
    want = os.environ.get("SXS_INFERENCE", "").lower()
    if want == "directml":
        resource.use_directml()
    elif want == "auto":
        resource.use_auto_ep()
    elif want == "cpu":
        resource.use_cpu()
    else:
        want = "default"
    return want
