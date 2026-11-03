"""Manual exploration helper: do one action, wait, save a numbered frame.

    python scripts/explore.py tap X Y [WAIT]
    python scripts/explore.py swipe X1 Y1 X2 Y2 [WAIT]
    python scripts/explore.py back [WAIT]
    python scripts/explore.py none [WAIT]

Frames go to captures/explore/NNN.png (gitignored, only the newest KEEP are kept); a half-size JPEG preview goes to
captures/latest.jpg.
Used to walk new screens by hand before writing pipeline nodes for them.
"""

import sys
import time
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sxs.device import REPO_ROOT, Device  # noqa: E402

KEEP = 40


def main(argv: list[str]) -> int:
    d = Device()
    a = list(argv)
    if a and a[0] == "tap":
        d.tap(int(a[1]), int(a[2]))
        a = a[3:]
    elif a and a[0] == "swipe":
        d.swipe(*map(int, a[1:5]), 400)
        a = a[5:]
    elif a and a[0] in ("back", "none"):
        if a[0] == "back":
            d.back()
        a = a[1:]
    time.sleep(float(a[0]) if a else 1.5)

    out = REPO_ROOT / "captures" / "explore"
    out.mkdir(parents=True, exist_ok=True)
    n = max((int(f.stem) for f in out.glob("*.png")), default=-1) + 1
    img = d.screenshot()
    path = out / f"{n:03d}.png"
    cv2.imwrite(str(path), img)
    cv2.imwrite(str(REPO_ROOT / "captures" / "latest.jpg"), cv2.resize(img, (360, 640)), [cv2.IMWRITE_JPEG_QUALITY, 70])
    for old in sorted(out.glob("*.png"))[:-KEEP]:
        old.unlink()
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
