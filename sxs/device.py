"""Device control over MaaFramework: connect to MuMu, screenshot, tap, swipe, start/stop the game."""

from __future__ import annotations

import os
import re
import subprocess
import time
from pathlib import Path
from typing import Optional

import numpy as np
from maa.controller import AdbController
from maa.toolkit import Toolkit

PACKAGE = "com.zjcs.android.us"
DEFAULT_ADDRESS = os.environ.get("SXS_ADB_ADDRESS", "127.0.0.1:16384")
REPO_ROOT = Path(__file__).resolve().parent.parent
MAA_USER_DIR = REPO_ROOT / ".maa"

_toolkit_ready = False


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

    @property
    def uses_mumu_ipc(self) -> bool:
        return bool(self.info.config.get("extras", {}).get("mumu", {}).get("enable"))

    def screenshot(self) -> np.ndarray:
        """Return the current frame as a BGR array, 720x1280x3."""
        self.controller.post_screencap().wait()
        return self.controller.cached_image

    def tap(self, x: int, y: int) -> None:
        self.controller.post_click(x, y).wait()

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300) -> None:
        self.controller.post_swipe(x1, y1, x2, y2, duration_ms).wait()

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
