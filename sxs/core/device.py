"""Device control over MaaFramework: connect to MuMu, screenshot, tap, swipe, start/stop the game."""

from __future__ import annotations

import os
import re
import subprocess
import time
from pathlib import Path
from typing import Optional

import logging

import numpy as np
from maa.controller import AdbController
from maa.toolkit import Toolkit

from .paths import CAPTURES, REPO_ROOT

PACKAGE = "com.zjcs.android.us"
DEFAULT_ADDRESS = os.environ.get("SXS_ADB_ADDRESS", "127.0.0.1:16384")
MAA_USER_DIR = REPO_ROOT / ".maa"

_toolkit_ready = False
log = logging.getLogger("sxs.core.device")

# Device.pan: a pan "moved" when the scene band differs by more than this (mean absolute grey difference on a 1/4
# scale copy, 0-255). Home's idle animation (clouds, the character, chat) stays under 4; a 150 px pan is above 20.
PAN_BAND = (260, 940)  # y range compared: below the HUD and top-right icons, above the chat strip
PAN_MOVED = 8.0


def frames_moved(before: np.ndarray, after: np.ndarray, band=PAN_BAND, threshold: float = PAN_MOVED) -> bool:
    """True when the scene between `band` rows changed enough to count as a pan, not just animation."""
    import cv2

    def small(f):
        g = cv2.cvtColor(f[band[0]:band[1]], cv2.COLOR_BGR2GRAY)
        return cv2.resize(g, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA).astype(np.int16)

    if before is None or after is None or before.shape != after.shape:
        return True  # can't compare: don't claim it failed
    return float(np.abs(small(before) - small(after)).mean()) > threshold


def adb_scale(wm_size: str, frame_width: int = 720) -> float:
    """Device pixels per frame pixel from `adb shell wm size` ("Physical size: 1080x1920", maybe an "Override size"
    line, which wins). MaaFramework frames are 720 wide; `input swipe` takes device pixels."""
    sizes = dict(re.findall(r"(Physical|Override) size: (\d+)x\d+", wm_size))
    width = int(sizes.get("Override") or sizes.get("Physical") or frame_width)
    return width / frame_width


def _init_toolkit() -> None:
    global _toolkit_ready
    if not _toolkit_ready:
        MAA_USER_DIR.mkdir(exist_ok=True)
        Toolkit.init_option(MAA_USER_DIR)
        _toolkit_ready = True


class Device:
    """One emulator instance. Uses MuMu's IPC screenshot path when MaaFramework detects MuMu."""

    def __init__(self, address: str = DEFAULT_ADDRESS):
        _init_toolkit()
        devices = Toolkit.find_adb_devices()
        matches = [d for d in devices if d.address == address]
        if not matches and "SXS_ADB_ADDRESS" not in os.environ and len(devices) == 1:
            # MuMu gives instance N port 16384 + 32*N; with one emulator running, use it.
            matches = list(devices)
            address = devices[0].address
        if not matches:
            found = ", ".join(d.address for d in devices) or "none"
            raise RuntimeError(f"No adb device at {address} (found: {found}). Is MuMu running?")
        info = matches[0]
        self.info = info
        self.address = address
        self.controller = AdbController(
            info.adb_path, info.address, info.screencap_methods, info.input_methods, info.config
        )
        if not self.controller.post_connection().wait().succeeded:
            raise RuntimeError(f"MaaFramework could not connect to {address}")
        # Set by pan() once MaaFramework's swipe stopped moving the scene while adb's did (seen 2026-11-11 after a
        # game restart): every later swipe of this run then goes through adb.
        self.swipe_via_adb = False
        self._adb_scale: Optional[float] = None

    def screenshot(self) -> np.ndarray:
        """Return the current frame as a BGR array, 720x1280x3."""
        self.controller.post_screencap().wait()
        return self.controller.cached_image

    def tap(self, x: int, y: int) -> None:
        self.controller.post_click(x, y).wait()

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300) -> None:
        if self.swipe_via_adb:
            self.adb_swipe(x1, y1, x2, y2, duration_ms)
        else:
            self.controller.post_swipe(x1, y1, x2, y2, duration_ms).wait()

    def adb_swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300) -> None:
        """The same swipe through `adb shell input swipe`, in device pixels."""
        if self._adb_scale is None:
            try:
                self._adb_scale = adb_scale(self.shell("wm", "size"))
            except Exception as e:  # noqa: BLE001 - a frame-sized device is the usual case
                log.warning("could not read the device size (%s); assuming 720 wide", e)
                self._adb_scale = 1.0
        k = self._adb_scale
        self.shell("input", "swipe", *(str(round(v * k)) for v in (x1, y1, x2, y2)), str(int(duration_ms)))
        time.sleep(duration_ms / 1000)  # `input swipe` returns at once on some images; wait out the gesture

    def pan(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 1000, settle: float = 1.5) -> bool:
        """A camera pan that checks it worked: swipe, then compare the scene before and after. If nothing moved,
        try the same swipe through adb; if that moves it, use adb for every swipe from now on (mae's stuck point,
        2026-11-11: after a game restart MaaFramework's swipe stopped panning Home, adb's still worked). Returns
        whether the scene moved: False at a scene's end too, which callers use to stop sweeping that way."""
        before = self.screenshot().copy()
        self.swipe(x1, y1, x2, y2, duration_ms)
        time.sleep(settle)
        if frames_moved(before, self.screenshot()):
            return True
        if self.swipe_via_adb:
            return False  # already on adb: the scene's end, or nothing to pan
        self.adb_swipe(x1, y1, x2, y2, duration_ms)
        time.sleep(settle)
        if frames_moved(before, self.screenshot()):
            log.warning("MaaFramework's swipe did not move the scene, adb's did: swiping through adb from now on")
            self.swipe_via_adb = True
            return True
        return False

    def back(self) -> None:
        self.controller.post_click_key(4).wait()  # KEYCODE_BACK

    def start_game(self) -> None:
        self.controller.post_start_app(PACKAGE).wait()

    def stop_game(self) -> None:
        self.controller.post_stop_app(PACKAGE).wait()

    def wait(self, seconds: float) -> None:
        time.sleep(seconds)

    def shell(self, *args: str) -> str:
        """Run an adb shell command (for queries MaaFramework does not expose)."""
        out = subprocess.run(
            [str(self.info.adb_path), "-s", self.address, "shell", *args],
            capture_output=True, text=True, timeout=15,
        )
        return out.stdout

    def foreground_package(self) -> Optional[str]:
        """Package of the focused window, or None if it can't be read."""
        m = re.search(r"mCurrentFocus=Window\{\S+ \S+ ([\w.]+)/", self.shell("dumpsys", "window"))
        return m.group(1) if m else None


def save_unknown(dev: "Device", why: str) -> Path:
    """Save the current frame to captures/unknown/ when a loop stops on a screen it doesn't recognise (mae,
    2026-11-04: an unfamiliar screen is flagged and the loop ends early, never idles). Returns the path."""
    import cv2
    out = CAPTURES / "unknown"
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{time.strftime('%Y%m%d-%H%M%S')}-{why}.png"
    cv2.imwrite(str(path), dev.screenshot())
    return path

