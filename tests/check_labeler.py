"""Screen labeling UI offline: the page's API saves boxes, cuts template crops, fills the bank row, files the screen
(boxes and crops follow it), refuses paths outside docs/screens, and sxs/vision/labels.py finds the crop again.

    python tests/check_labeler.py

Needs Pillow, OpenCV and numpy; no MaaFramework, no emulator. Works in a temp copy, never touches the repo's files.
"""

from __future__ import annotations

import json
import sys
import tempfile
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import cv2  # noqa: E402
import numpy as np  # noqa: E402

from sxs import labeler  # noqa: E402
from sxs.core import labels, screens  # noqa: E402
from sxs.vision import labels as vlabels  # noqa: E402

problems: list[str] = []


def check(ok: bool, what: str) -> None:
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        problems.append(what)


def point_at(tmp: Path) -> None:
    """Point every module at a temp docs/screens and resource/image."""
    shots, image = tmp / "screens", tmp / "image"
    labels.SCREENS = labeler.SCREENS = screens.SCREENS = shots
    labels.LABELS_FILE = shots / "labels.json"
    labels.IMAGE, labels.CROPS = image, image / "labels"
    labels.MANIFEST = labels.CROPS / "manifest.json"
    screens.UNLABELED = shots / "unlabeled"
    screens.BANK_INDEX = screens.UNLABELED / "README.md"
    screens.EXPECTED_FILE = shots / "expected.json"


def frame() -> np.ndarray:
    rng = np.random.default_rng(7)
    img = rng.integers(0, 60, (1280, 720, 3), dtype=np.uint8)
    cv2.rectangle(img, (300, 1080), (420, 1140), (40, 200, 250), -1)  # a "button"
    cv2.putText(img, "GO", (330, 1125), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 3)
    return img


def call(base: str, path: str, body=None):
    req = urllib.request.Request(base + path, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def main() -> int:
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        point_at(tmp)
        (tmp / "screens" / "unlabeled").mkdir(parents=True)
        (tmp / "screens" / "home").mkdir()
        img = frame()
        cv2.imwrite(str(tmp / "screens" / "unlabeled" / "mystery.png"), img)
        cv2.imwrite(str(tmp / "screens" / "home" / "home.png"), img)
        (tmp / "outside.png").write_bytes(b"x")
        screens.save_expected({"states": {"home": "home"}, "notes": {}})

        server = ThreadingHTTPServer(("127.0.0.1", 0), labeler.Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{server.server_address[1]}"
        try:
            listing = call(base, "/api/screens")
            keys = [s["key"] for s in listing["screens"]]
            check(keys[0] == "unlabeled/mystery.png", "the bank is listed first")
            check("home" in listing["states"] and "main_menu" in listing["states"], "known states offered")
            check(urllib.request.urlopen(base + "/").read().startswith(b"<!doctype html>"), "page served")
            try:
                urllib.request.urlopen(base + "/img/../outside.png")
                check(False, "path outside docs/screens refused")
            except urllib.error.HTTPError as e:
                check(e.code == 404, "path outside docs/screens refused")

            r = call(base, "/api/save", {"key": "unlabeled/mystery.png",
                                         "fields": {"name": "home_mystery", "folder": "", "state": "home",
                                                    "what": "test | screen"},
                                         "boxes": [{"name": "go_button", "kind": "button", "x": 299.6, "y": 1080,
                                                    "w": 121, "h": 61, "note": "tap", "template": True},
                                                   {"name": "Bad Name", "kind": "text", "x": 0, "y": 0, "w": 9,
                                                    "h": 9}]})
            check(len(r["problems"]) == 1 and r["crops"] == ["labels/mystery/go_button.png"],
                  "save keeps the good box, reports the bad name, cuts one crop")
            row = next(x for x in screens.bank_rows() if x["file"] == "mystery.png")
            check(row["name"] == "home_mystery" and row["state"] == "home" and "|" not in row["what"],
                  "bank row filled (pipes escaped)")
            d = call(base, "/api/screen?key=unlabeled/mystery.png")
            check(d["boxes"][0]["x"] == 300 and d["size"] == [720, 1280], "boxes rounded and read back")

            f = call(base, "/api/file", {})
            check(len(f["filed"]) == 1 and not f["problems"], "File labelled screens files it")
            moved = tmp / "screens" / "home" / "home_mystery.png"
            check(moved.exists(), "screen moved to home/")
            check(list(labels.load()["screens"]) == ["home/home_mystery.png"], "boxes follow the screen")
            man = json.loads(labels.MANIFEST.read_text())["entries"]
            check([e["template"] for e in man] == ["labels/home_mystery/go_button.png"]
                  and (labels.CROPS / "home_mystery" / "go_button.png").exists()
                  and not (labels.CROPS / "mystery").exists(), "crops renamed with it")
            check(screens.load_expected()["states"].get("home_mystery") == "home", "state recorded in expected.json")

            call(base, "/api/save", {"key": "home/home.png", "fields": {"state": "home", "what": "note"},
                                     "boxes": []})
            check(screens.load_expected()["notes"].get("home") == "note", "filed screen notes saved")

            shifted = np.roll(img, (12, -8), axis=(0, 1))
            hit = vlabels.find(shifted, "home_mystery", "go_button")
            check(hit is not None and (hit[0], hit[1]) == (292, 1092) and hit[4] > 0.95,
                  f"vision finds the crop on a shifted frame ({hit})")
            check(vlabels.tap_point(np.zeros_like(img), "home_mystery", "go_button") is None, "no false match")
            check(vlabels.roi("home_mystery", "go_button") == (300, 1080, 121, 61), "roi lookup")
        finally:
            server.shutdown()
    print(f"\n{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
