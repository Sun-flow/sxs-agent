"""UI detector data offline (docs/detector-design.md): the class list, detector classes and drafts on labeler boxes,
the pre-labeller's merge rules, and the YOLO dataset export (format, split, minimap crop, privacy masking).

    python tests/check_detect_data.py

Needs Pillow, OpenCV and numpy; no MaaFramework, no emulator. Works in a temp copy, never touches the repo's files
(it reads the real resource/detect/classes.json).
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import cv2  # noqa: E402
import numpy as np  # noqa: E402

from sxs.core import labels, screens  # noqa: E402
from sxs.detect import dataset, prelabel  # noqa: E402
from sxs.vision import minimap as mm  # noqa: E402

problems: list[str] = []


def check(ok: bool, what: str) -> None:
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        problems.append(what)


def point_at(tmp: Path) -> None:
    shots, image = tmp / "screens", tmp / "image"
    labels.SCREENS = screens.SCREENS = dataset.SCREENS = shots
    labels.LABELS_FILE = shots / "labels.json"
    labels.IMAGE, labels.CROPS = image, image / "labels"
    labels.MANIFEST = labels.CROPS / "manifest.json"
    screens.EXPECTED_FILE = shots / "expected.json"


def main() -> int:
    cls = labels.classes()
    names = [c["name"] for c in cls]
    check(len(names) == len(set(names)) and len(names) >= 30, f"{len(names)} unique detector classes")
    check(all(c["kind"] in labels.KINDS and c["group"] for c in cls), "every class has a labeler kind and a group")
    check(any(c["group"] == "minimap" for c in cls) and any(c["group"] == "screen" for c in cls),
          "minimap and screen-anchor classes listed")

    good, probs = labels.clean_boxes([
        {"name": "a", "kind": "badge", "x": 10, "y": 10, "w": 20, "h": 20, "cls": "badge_red_bang", "draft": True},
        {"name": "b", "kind": "icon", "x": 10, "y": 10, "w": 20, "h": 20, "cls": "no_such_class"},
        {"name": "c", "kind": "button", "x": 10, "y": 10, "w": 20, "h": 20}], (720, 1280))
    check(good[0].get("cls") == "badge_red_bang" and good[0].get("draft") is True, "cls and draft kept on a box")
    check("cls" not in good[1] and len(probs) == 1, "an unknown class is dropped with a problem")
    check("cls" not in good[2] and "draft" not in good[2], "plain boxes stay as they were")

    mine = {"name": "my_bang", "kind": "badge", "x": 100, "y": 100, "w": 30, "h": 30, "note": "", "template": True,
            "cls": "badge_red_bang"}
    old_draft = dict(mine, name="badge_red_bang_9", x=500, draft=True)
    merged = prelabel.merge([mine, old_draft], [{"cls": "badge_red_bang", "x": 102, "y": 101, "w": 30, "h": 30},
                                                {"cls": "badge_red_bang", "x": 300, "y": 300, "w": 30, "h": 30}],
                            (720, 1280))
    check(merged[0] == mine, "mae's box kept as is")
    check(not any(b["name"] == "badge_red_bang_9" for b in merged), "old drafts replaced")
    drafts = [b for b in merged if b.get("draft")]
    check(len(drafts) == 1 and drafts[0]["x"] == 300, "a draft overlapping mae's box of the same class is skipped")

    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        point_at(tmp)
        (tmp / "screens" / "world").mkdir(parents=True)
        (tmp / "screens" / "guild").mkdir()
        img = np.full((1280, 720, 3), 90, np.uint8)
        cv2.imwrite(str(tmp / "screens" / "world" / "world_test.png"), img)
        cv2.imwrite(str(tmp / "screens" / "guild" / "guild_lobby.png"), img)
        screens.save_expected({"states": {"world_test": "world_map", "guild_lobby": "guild"}, "notes": {}})
        cx, cy = mm.CENTER
        labels.set_boxes("world/world_test.png", [
            {"name": "bang", "kind": "badge", "x": 200, "y": 400, "w": 30, "h": 30, "cls": "badge_red_bang"},
            {"name": "dot", "kind": "icon", "x": cx + 20, "y": cy - 10, "w": 8, "h": 8, "cls": "mm_item"},
            {"name": "maybe", "kind": "icon", "x": 50, "y": 600, "w": 40, "h": 40, "cls": "monster", "draft": True},
        ], (720, 1280))
        labels.set_boxes("guild/guild_lobby.png", [
            {"name": "bang", "kind": "badge", "x": 200, "y": 400, "w": 30, "h": 30, "cls": "badge_red_bang"}],
            (720, 1280))
        out = tmp / "ds"
        name_line = [("Someone", [300, 500, 60, 20]), ("other text", [300, 700, 80, 20]),
                     ("[Server] Player: hi", [60, 1100, 300, 24])]

        class FakeDet:
            def read_text(self, roi, frame):
                return name_line

        s = dataset.export(out, name="someone", det=FakeDet())
        split = dataset.split_of("world/world_test.png")
        lab = (out / split / "labels" / "world_world_test.txt").read_text().split("\n")
        lines = [ln for ln in lab if ln]
        ids = {n: i for i, n in enumerate(names)}
        check(sorted(int(ln.split()[0]) for ln in lines) == sorted([ids["badge_red_bang"], ids["mm_item"]]),
              "confirmed boxes exported; the draft left out; minimap box on the full frame too (both)")
        check(all(0 <= float(v) <= 1 for ln in lines for v in ln.split()[1:]), "YOLO coordinates within 0-1")
        crop_lab = (out / split / "labels" / "world_world_test_minimap.txt").read_text().split()
        crop = cv2.imread(str(out / split / "images" / "world_world_test_minimap.png"))
        check(crop is not None and crop.shape[0] == 2 * mm.RADIUS * dataset.MINIMAP_SCALE, "minimap crop enlarged")
        check(int(crop_lab[0]) == ids["mm_item"] and abs(float(crop_lab[1]) - (0.5 + 24 / (2 * mm.RADIUS))) < 0.02,
              "minimap box placed in the crop")
        full = cv2.imread(str(out / split / "images" / "world_world_test.png"))
        x, y, w, h = dataset.NAME_STRIP
        check(full[y + 5:y + h - 5, x + 5:x + w - 5].max() == 0, "HUD name strip blacked out")
        check(full[505:515, 310:350].max() == 0 and full[705:715, 310:370].max() > 0,
              "the account-name line blacked out, other text kept")
        check(full[1105:1120, 0:350].max() == 0, "chat lines blacked out (other players' names)")
        check("guild/guild_lobby.png" in s["skipped"], "guild screen left out as private")
        check((out / "data.yaml").read_text().count(names[0]) == 1 and f"nc: {len(names)}" in (out / "data.yaml").read_text(),
              "data.yaml lists the classes")
        s2 = dataset.export(tmp / "ds2", drafts=True, name="someone", det=FakeDet(), minimap="crop")
        check(s2["classes"].get("monster") == 1 and "mm_item" in s2["classes"], "--drafts includes drafts")
        lab2 = (tmp / "ds2" / split / "labels" / "world_world_test.txt").read_text()
        check(f"{ids['mm_item']} " not in lab2, "minimap=crop keeps minimap boxes off the full frame")

    print("all good" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
