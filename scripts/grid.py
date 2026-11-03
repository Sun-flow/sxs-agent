"""Tile frames from a captures/ subfolder into captures/grid.jpg: python scripts/grid.py record 0 3 6 9 ..."""

import sys
from pathlib import Path

import cv2
import numpy as np

root = Path(__file__).resolve().parent.parent / "captures"
folder, idx = sys.argv[1], sys.argv[2:]
ims = [cv2.resize(cv2.imread(str(root / folder / f"{int(i):03d}.png")), (180, 320)) for i in idx]
while len(ims) % 6:
    ims.append(np.zeros_like(ims[0]))
rows = [np.hstack(ims[i:i + 6]) for i in range(0, len(ims), 6)]
cv2.imwrite(str(root / "grid.jpg"), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 70])
