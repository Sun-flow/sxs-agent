"""Smoke test on the live emulator: cold-start the game, reach home, walk to a few screens and back.

    python tests/smoke_test.py [--no-restart]

Needs MuMu running with the game installed and signed in. Exits 0 on success. On failure the last frame is saved
to captures/smoke-failure.png.

Needs: Live emulator
Checks: Cold start → home → menus → home
"""

import argparse
import logging
import sys
import time
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sxs.core import ui  # noqa: E402
from sxs.core.nav import Navigator  # noqa: E402
from sxs.core.device import REPO_ROOT, Device  # noqa: E402
from sxs.core.state import StateDetector  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--no-restart", action="store_true", help="don't kill and relaunch the game first")
    args = p.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")

    dev = Device()
    det = StateDetector(dev)
    n = Navigator(dev, det)
    start = time.monotonic()
    try:
        if not args.no_restart:
            dev.stop_game()
            time.sleep(2)
            dev.start_game()
        n.go_home()
        print(f"reached home in {time.monotonic() - start:.0f}s")

        # Home -> menu -> back, home -> world -> home, home -> character -> home.
        n.tap_and_expect(ui.HOME_MENU_BUTTON, "main_menu")
        n.tap_and_expect(ui.BACK_ARROW, "home")
        n.tap_and_expect(ui.NAV_WORLD, "world_overview")
        n.tap_and_expect(ui.NAV_HOME, "home")
        n.tap_and_expect(ui.NAV_CHARACTER, "character")
        n.tap_and_expect(ui.NAV_HOME, "home")
    except Exception as e:  # noqa: BLE001 - report any failure the same way
        cv2.imwrite(str(REPO_ROOT / "captures" / "smoke-failure.png"), dev.screenshot())
        print(f"FAIL: {e}\nstates: {' > '.join(n.trail)}")
        return 1
    print(f"PASS in {time.monotonic() - start:.0f}s\nstates: {' > '.join(n.trail)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
