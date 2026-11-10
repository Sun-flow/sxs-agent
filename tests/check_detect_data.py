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
from sxs.detect import dataset, items, prelabel  # noqa: E402
from sxs.vision import minimap as mm  # noqa: E402

problems: list[str] = []


def check(ok: bool, what: str) -> None:
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        problems.append(what)


def point_at(tmp: Path) -> None:
    shots, image = tmp / "screens", tmp / "image"
    labels.SCREENS = screens.SCREENS = dataset.SCREENS = items.SCREENS = shots
    labels.LABELS_FILE = shots / "labels.json"
    labels.IMAGE, labels.CROPS = image, image / "labels"
    labels.MANIFEST = labels.CROPS / "manifest.json"
    screens.EXPECTED_FILE = shots / "expected.json"
    items.ITEMS_DIR = tmp / "items"
    items.ITEMS_FILE, items.ICONS = items.ITEMS_DIR / "items.json", items.ITEMS_DIR / "icons"


def check_splits() -> None:
    keys = {f"s/{i}.png": {"a"} for i in range(12)}
    keys.update({"s/x.png": {"a", "b"}, "s/y.png": {"b"}, "s/z.png": {"b"}, "s/w.png": {"c"}, "s/v.png": {"c"}})
    sp = dataset.balanced_splits(keys)
    for c in ("a", "b"):
        got = {sp[k] for k, cs in keys.items() if c in cs}
        check({"train", "valid", "test"} <= got, f"balanced split: class {c} in train, valid and test ({sorted(got)})")
    check(sp == dataset.balanced_splits(dict(reversed(list(keys.items())))), "balanced split is deterministic")
    check({sp["s/w.png"], sp["s/v.png"]} == {dataset.split_of("s/w.png"), dataset.split_of("s/v.png")},
          "a class on 2 screens keeps its hash split")


def check_items() -> None:
    real = items.load()["items"]
    check(len(real) >= 10 and all(items.ID.match(i["id"]) and i["kind"] in items.KINDS and i["icons"] for i in real),
          f"{len(real)} catalogued items, each with an id, a kind and an icon")
    check(all((items.ICONS / ic["file"]).exists() for i in real for ic in i["icons"]), "every item icon file exists")
    vault = cv2.imread(str(screens.SCREENS / "shops" / "vendor_booth_vault.png"))
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        point_at(tmp)
        (tmp / "screens" / "shops").mkdir(parents=True)
        cv2.imwrite(str(tmp / "screens" / "shops" / "vault.png"), vault)
        it = items.add("dawnium", "shops/vault.png", [465, 36, 31, 37], "Dawnium", "currency", named_by="screen",
                       tight=True, found_in="Home > Vendor Booth > Vault")
        x, y, w, h = it["icons"][0]["box"]
        check(abs(x - 463) <= 3 and abs(y - 37) <= 3 and w < 40 and h < 40,
              f"--tight shrinks the box ({x},{y} {w}x{h})")
        u = items.add("unknown", "shops/vault.png", [545, 523, 90, 102], tight=True)
        check(u["id"] == "unknown_1" and u["name"] == "", "an unnamed symbol becomes unknown_1")
        items.add("dawnium", "shops/vault.png", [463, 37, 35, 33], desc="Premium currency.", named_by="popup")
        d = items.get("dawnium")
        check(len(d["icons"]) == 2 and d["description"] == "Premium currency." and d["named_by"] == "screen",
              "a second sighting adds an icon and fills only empty fields")
        hits = items.find(cv2.resize(vault, None, fx=0.9, fy=0.9))
        check(any(h["item"] == "dawnium" for h in hits) and any(h["item"] == "unknown_1" for h in hits),
              "find matches catalogued symbols at another size")
        good, probs = labels.clean_boxes([
            {"name": "a", "kind": "icon", "x": 5, "y": 5, "w": 20, "h": 20, "cls": "item_icon", "item": "dawnium"},
            {"name": "b", "kind": "icon", "x": 5, "y": 5, "w": 20, "h": 20, "cls": "item_icon", "item": "nope"}],
            (720, 1280))
        check(good[0].get("item") == "dawnium" and "item" not in good[1] and len(probs) == 1,
              "item ids checked against the catalogue")
        labels.set_boxes("shops/vault.png", [
            {"name": "d", "kind": "icon", "x": 463, "y": 37, "w": 35, "h": 33, "cls": "item_icon", "item": "dawnium"},
            {"name": "e", "kind": "icon", "x": 545, "y": 523, "w": 90, "h": 102, "cls": "item_icon"}], (720, 1280))
        check(items.add_box("shops/vault.png", "btn_close_x", [650, 20, 40, 40]) == 0
              and labels.boxes_for("shops/vault.png")[-1]["cls"] == "btn_close_x"
              and len(labels.boxes_for("shops/vault.png")) == 3, "items box adds a confirmed box, keeps the others")
        check(items.add_box("shops/vault.png", "btn_nope", [10, 10, 40, 40]) == 1, "items box refuses an unknown class")
        labels.set_boxes("shops/vault.png", labels.boxes_for("shops/vault.png")[:2], (720, 1280))
        s = dataset.export(tmp / "ds", name_ocr=False)
        yaml = (tmp / "ds" / "data.yaml").read_text()
        n = len(labels.classes())
        lab = (tmp / "ds" / dataset.split_of("shops/vault.png") / "labels" / "shops_vault.txt").read_text().split("\n")
        got = sorted(int(ln.split()[0]) for ln in lab if ln)
        check("item_dawnium" in yaml and got == sorted([n, n - 1]),
              "--items each: item_<id> classes after the fixed ones; an unnamed item box stays item_icon")
        dataset.export(tmp / "ds1", name_ocr=False, items="one")
        lab1 = (tmp / "ds1" / dataset.split_of("shops/vault.png") / "labels" / "shops_vault.txt").read_text()
        check("item_dawnium" not in (tmp / "ds1" / "data.yaml").read_text()
              and {int(ln.split()[0]) for ln in lab1.split("\n") if ln} == {n - 1}, "--items one: all item_icon")
        check(s["classes"].get("item_dawnium") == 1, "summary counts item classes")
        d = items.load()
        d["aliases"] = {"old_beetle": "unknown_1"}
        items.save(d)
        good, probs = labels.clean_boxes([{"name": "z", "kind": "icon", "x": 5, "y": 5, "w": 20, "h": 20,
                                           "cls": "item_icon", "item": "old_beetle"}], (720, 1280))
        check(good[0].get("item") == "unknown_1" and not probs, "an aliased (renamed) item id resolves to the new id")
        sg = dataset.export(tmp / "dsg", name_ocr=False, items="group")
        check(sg["classes"].get("item_currency") == 1, "--items group: one class per material type (kind when no group)")


def main() -> int:
    check_items()
    check_splits()
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
