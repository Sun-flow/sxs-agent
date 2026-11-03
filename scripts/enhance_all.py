"""Enhance every equipped gear piece a few times from the Enhance Gear screen (spends Raw/Refined Ore and Rolla only).

    python scripts/enhance_all.py [TAPS_PER_ITEM]

Start on the Enhance Gear screen. Stops tapping an item once the game says materials are insufficient.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sxs.device import Device  # noqa: E402
from sxs.state import StateDetector  # noqa: E402

ITEM_TABS = [(160, 166), (304, 166), (424, 166), (552, 166)]  # equipped items along the top
ENHANCE = (360, 1084)

taps = int(sys.argv[1]) if len(sys.argv) > 1 else 6
dev = Device()
det = StateDetector(dev)
for tab in ITEM_TABS:
    dev.tap(*tab)
    time.sleep(1.5)
    for _ in range(taps):
        dev.tap(*ENHANCE)
        time.sleep(1.2)
        if any("Insufficient" in t for t, _ in det.read_text([0, 280, 720, 120])):
            break
    print("item", tab, "level:", [t for t, _ in det.read_text([60, 500, 600, 80])])
