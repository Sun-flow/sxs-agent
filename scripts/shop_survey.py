"""Read a shop grid without buying: tap each item's icon (opens the info card, never the price button), OCR the card,
tap outside to close. Prints one JSON line per item plus the OCR of the grid cell (multiplier, limit, price).

    python scripts/shop_survey.py NAME [rows]   # rows: y of each icon row, default 290,580,860

Columns are x = 130, 360, 590 (720x1280 frame). Safe: the price buttons sit ~100 px below the icons and are never
tapped. Card text is read from [60, 160, 600, 760]."""

import json
import sys
import time

sys.path.insert(0, ".")
from sxs.device import Device  # noqa: E402
from sxs.state import StateDetector  # noqa: E402

COLS = (130, 360, 590)
CLOSE = (360, 80)  # outside the info card


def main() -> None:
    name = sys.argv[1]
    rows = [int(y) for y in (sys.argv[2].split(",") if len(sys.argv) > 2 else ("290", "580", "860"))]
    dev = Device()
    det = StateDetector(dev)
    grid = dev.screenshot()
    for r, y in enumerate(rows):
        for c, x in enumerate(COLS):
            cell = [t for t, _ in det.read_text([x - 110, y - 120, 220, 260], grid)]
            if not cell:
                continue
            dev.tap(x, y)
            time.sleep(2.0)
            card = [t for t, _ in det.read_text([60, 160, 600, 760])]
            dev.tap(*CLOSE)
            time.sleep(1.2)
            print(json.dumps({"shop": name, "row": r, "col": c, "cell": cell, "card": card}, ensure_ascii=False),
                  flush=True)


if __name__ == "__main__":
    main()
