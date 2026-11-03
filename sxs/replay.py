"""Offline stand-in for Device: feeds saved frames to MaaFramework so detectors can be tested without the emulator."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from maa.controller import CustomController

from .device import PACKAGE


class ImageController(CustomController):
    def __init__(self):
        super().__init__()
        self.image: Optional[np.ndarray] = None

    def connect(self) -> bool:
        return True

    def request_uuid(self) -> str:
        return "sxs-replay"

    def screencap(self) -> np.ndarray:
        return self.image

    def click(self, x: int, y: int) -> bool:
        return True

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int) -> bool:
        return True


class ImageDevice:
    """Quacks like Device for StateDetector; set_frame() picks what the 'emulator' shows."""

    def __init__(self):
        self.controller = ImageController()
        self.controller.post_connection().wait()

    def set_frame(self, frame: np.ndarray | str | Path) -> None:
        if not isinstance(frame, np.ndarray):
            frame = cv2.imread(str(frame))
        self.controller.image = frame

    def foreground_package(self) -> str:
        return PACKAGE
