"""Run the state detector over the reference screenshots in docs/screens/<folder>/ and check each against its
expected state.

    python tests/check_states_offline.py [NAME ...]     # all screens, or only these

No emulator needed. Expected states are in docs/screens/expected.json ("states"); a screen without an entry is
run but not checked. `python -m sxs label` adds entries for screens mae labels. icons/, minimap/ and unlabeled/
are skipped.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sxs.core.replay import ImageDevice  # noqa: E402
from sxs.core.screens import load_expected, reference_screens  # noqa: E402
from sxs.core.state import StateDetector  # noqa: E402


def main() -> int:
    dev = ImageDevice()
    det = StateDetector(dev)
    failures = 0
    expected = load_expected()["states"]
    only = set(sys.argv[1:])
    for png in reference_screens():
        if only and png.stem not in only:
            continue
        want = expected.get(png.stem)
        dev.set_frame(png)
        got = det.detect()
        ok = want is None or got.state == want
        failures += not ok
        mark = "ok " if ok else "BAD"
        print(f"{mark} {png.stem:24} -> {got.state:16} (want {want}) {got.elapsed_ms} ms")
    print("all good" if not failures else f"{failures} wrong")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
