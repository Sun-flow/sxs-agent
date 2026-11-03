"""Tile several captures/explore frames side by side into captures/sheet.jpg for quick review."""

import sys
from pathlib import Path

import cv2
import numpy as np

root = Path(__file__).resolve().parent.parent / "captures"
ims = [cv2.resize(cv2.imread(str(root / "explore" / f"{int(i):03d}.png")), (270, 480)) for i in sys.argv[1:]]
cv2.imwrite(str(root / "sheet.jpg"), np.hstack(ims), [cv2.IMWRITE_JPEG_QUALITY, 70])
