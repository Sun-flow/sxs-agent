"""Slow drag (default 1000 ms), then save a frame like probe.py: python scripts/drag.py X1 Y1 X2 Y2 [MS] [WAIT]"""
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sxs.core.device import Device  # noqa: E402

a = list(map(int, sys.argv[1:5]))
ms = int(sys.argv[5]) if len(sys.argv) > 5 else 1000
Device().swipe(*a, ms)
time.sleep(float(sys.argv[6]) if len(sys.argv) > 6 else 1.5)
subprocess.run([sys.executable, str(Path(__file__).parent / "probe.py"), "none", "0"], capture_output=True)
