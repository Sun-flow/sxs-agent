"""Save a frame every INTERVAL seconds for DURATION seconds to captures/record/NNN.png (for catching short-lived screens)."""

import sys
import time
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sxs.core.device import REPO_ROOT, Device  # noqa: E402

duration = float(sys.argv[1]) if len(sys.argv) > 1 else 20
interval = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
out = REPO_ROOT / "captures" / "record"
out.mkdir(parents=True, exist_ok=True)
for f in out.glob("*.png"):
    f.unlink()
d = Device()
end = time.monotonic() + duration
n = 0
while time.monotonic() < end:
    cv2.imwrite(str(out / f"{n:03d}.png"), d.screenshot())
    n += 1
    time.sleep(interval)
print(n, "frames")
