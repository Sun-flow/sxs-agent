"""Tap through dialogue and reward popups until something else shows, then save the frame for review.

    python scripts/advance.py [MAX_TAPS]

Prints each state it saw. The final frame goes to captures/latest.jpg (half size) and captures/explore/NNN.png.
"""

import sys
import time
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sxs.device import REPO_ROOT, Device  # noqa: E402
from sxs.state import StateDetector  # noqa: E402

TAP = {"dialogue": (360, 1150), "reward_popup": (360, 200)}

dev = Device()
det = StateDetector(dev)
max_taps = int(sys.argv[1]) if len(sys.argv) > 1 else 30
seen = []
for _ in range(max_taps):
    d = det.detect()
    seen.append(d.state)
    if d.state == "loading":
        time.sleep(2)
        continue
    if d.state not in TAP:
        break
    dev.tap(*TAP[d.state])
    time.sleep(1.2)
print(" ".join(seen))
out = REPO_ROOT / "captures" / "explore"
out.mkdir(parents=True, exist_ok=True)
img = dev.screenshot()
path = out / f"{max((int(f.stem) for f in out.glob('*.png')), default=-1) + 1:03d}.png"
cv2.imwrite(str(path), img)
cv2.imwrite(str(REPO_ROOT / "captures" / "latest.jpg"), cv2.resize(img, (360, 640)), [cv2.IMWRITE_JPEG_QUALITY, 70])
print(path)
