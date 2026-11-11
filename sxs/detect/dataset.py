"""Export the labelled boxes as a YOLO-format detection dataset for Roboflow (or local Ultralytics / RF-DETR
training), with mae's account name blacked out (docs/detector-design.md, step 3).

    python -m sxs dataset [--out DIR] [--drafts] [--include-private] [--minimap both|crop|full] [--items each|group|one]
                          [--zip]

Reads docs/screens/labels.json (boxes with a detector class; drafts only with --drafts) and writes:

    DIR/data.yaml                       class names in id order (resource/detect/classes.json)
    DIR/{train,valid,test}/images/*.png full frames, and enlarged minimap crops (*_minimap.png)
    DIR/{train,valid,test}/labels/*.txt one line per box: class cx cy w h (0-1)

Split: about 80/10/10 by screen (a hash of its path), so a screen's frame and its minimap crop stay together; then
screens are moved from train so every class on 3 or more screens has a valid and a test screen (--hash-split
turns that off). Classes on fewer screens are listed as not scored.
Minimap classes (group "minimap"): the dots are 2-10 px, near the limit of a detector fed a frame shrunk to ~640 px,
so by default (--minimap both) they go into an enlarged minimap crop (MINIMAP_SCALE times) *and* the full frame, and
training can compare the two (mae, 2026-11-10: "what makes you so sure"). crop or full keeps one. Every other class
goes only into the full frame.
Item symbols (class item_icon with an "item" id from resource/items/items.json): with --items each (default) every
catalogued item becomes its own class, item_<id>, numbered after the fixed classes in catalogue order, so the
model names the symbol (mae, 2026-11-10); a box without an item id stays item_icon. --items one keeps them all as
item_icon (the runtime then names them by matching the catalogue crops); --items group makes one class per material
type (the item's group, else its kind), a coarser model to compare against.

Privacy (nothing here may identify mae or other players): the HUD name strip is blacked out on every frame, and
with SXS_ACCOUNT_NAME set (an environment variable, never committed) every OCR line that reads as that name, such
as the label over our character, is blacked out too, and so is every chat line ("[Server] name: ...", which names
other players). Without it the export stops, unless --no-name-ocr says the
fixed strip is enough. Screens full of other players' names (chat, guild, friends, profiles) are left out unless
--include-private. Default DIR: captures/dataset/ (gitignored).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from ..core import labels, screens
from ..core.paths import CAPTURES, SCREENS

NAME_STRIP = (100, 8, 180, 44)  # x, y, w, h: the account name next to the HUD portrait (home, map, character)
PRIVATE_FOLDERS = {"guild"}
PRIVATE_STATES = {"chat", "player_profile", "guild", "guild_panel", "guild_join_list", "guild_no_guild",
                  "guild_donation", "guild_conquest"}
PRIVATE_PREFIXES = ("friends", "chat", "player_profile", "guild_", "rank")  # file names, e.g. rankings boards
CHAT_LINE = re.compile(r"^\W{0,2}(Server|Guild|Private|World|System|Team)\W", re.I)  # chat strip lines name players
MINIMAP_SCALE = 3
SPLITS = (("train", 80), ("valid", 10), ("test", 10))


def squeeze(t: str) -> str:
    return re.sub(r"[^a-z0-9]", "", t.lower())


def minimap_box() -> tuple[int, int, int, int]:
    from ..vision import minimap as mm

    r = mm.RADIUS
    return mm.CENTER[0] - r, mm.CENTER[1] - r, 2 * r, 2 * r


def split_of(key: str) -> str:
    n = int(hashlib.sha1(key.encode("utf-8")).hexdigest()[:8], 16) % 100
    acc = 0
    for name, share in SPLITS:
        acc += share
        if n < acc:
            return name
    return SPLITS[-1][0]


def balanced_splits(classes_of: dict[str, set]) -> dict[str, str]:
    """Splits per screen: the hash split (split_of), then, rarest class first, a train screen moved to valid
    and one to test for every class on 3+ screens that has none there, so every such class is scored
    (Roboflow: every split should include all classes). A move never takes the last train screen of a class.
    Deterministic: the same labels give the same splits."""
    split = {k: split_of(k) for k in classes_of}
    screens_of: dict = {}
    for k, cs in classes_of.items():
        for c in cs:
            screens_of.setdefault(c, []).append(k)
    order = lambda k: hashlib.sha1(k.encode("utf-8")).hexdigest()  # noqa: E731
    for c in sorted(screens_of, key=lambda c: (len(screens_of[c]), str(c))):
        ks = sorted(screens_of[c], key=order)
        if len(ks) < 3:
            continue
        for target in ("valid", "test"):
            if any(split[k] == target for k in ks):
                continue
            for k in ks:
                if split[k] == "train" and all(sum(split[j] == "train" for j in screens_of[d]) > 1
                                               for d in classes_of[k]):
                    split[k] = target
                    break
    return split


def is_private(key: str, state: Optional[str]) -> bool:
    folder, stem = (key.split("/")[0] if "/" in key else ""), Path(key).stem
    return folder in PRIVATE_FOLDERS or (state or "") in PRIVATE_STATES or stem.startswith(PRIVATE_PREFIXES)


def mask_names(frame: np.ndarray, lines: list, name: Optional[str]) -> int:
    """Black out the HUD name strip, every OCR line (text, [x, y, w, h]) that reads as `name`, and every chat line.
    Returns the number of lines masked besides the strip."""
    x, y, w, h = NAME_STRIP
    frame[y:y + h, x:x + w] = 0
    hits = 0
    want = squeeze(name or "")
    for text, (bx, by, bw, bh) in lines:
        got = squeeze(text)
        is_name = want and len(got) >= 3 and (want in got or (len(got) >= len(want) - 1 and got in want))
        if is_name or CHAT_LINE.match(text.strip()):
            x0 = 0 if CHAT_LINE.match(text.strip()) else max(0, bx - 6)
            frame[max(0, by - 4):by + bh + 4, x0:bx + bw + 6] = 0
            hits += 1
    return hits


def yolo_line(cls_id: int, box: dict, ox: int, oy: int, scale: float, W: int, H: int) -> Optional[str]:
    x0 = (box["x"] - ox) * scale
    y0 = (box["y"] - oy) * scale
    x1, y1 = x0 + box["w"] * scale, y0 + box["h"] * scale
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
    if x1 - x0 < 2 or y1 - y0 < 2:
        return None
    return f"{cls_id} {(x0 + x1) / 2 / W:.6f} {(y0 + y1) / 2 / H:.6f} {(x1 - x0) / W:.6f} {(y1 - y0) / H:.6f}"


def export(out: Path, drafts: bool = False, include_private: bool = False, name: Optional[str] = None,
           name_ocr: bool = True, det=None, minimap: str = "both", items: str = "each",
           balance: bool = True) -> dict:
    """Write the dataset. `det` (a StateDetector) reads each frame for name lines when name_ocr is on.
    Returns a summary: images and boxes per split, boxes per class, screens skipped and why."""
    classes = labels.classes()
    from . import items as catalogue

    cat = catalogue.load()["items"]
    if items == "each":  # one class per catalogued item after the fixed classes, in catalogue order
        label = {i["id"]: f"item_{i['id']}" for i in cat}
    elif items == "group":  # one class per material type (group, else kind), in order of first appearance
        label = {i["id"]: f"item_{i.get('group') or i['kind']}" for i in cat}
    else:
        label = {}
    classes = classes + [{"name": n, "group": "items"} for n in dict.fromkeys(label.values())]
    ids = {c["name"]: i for i, c in enumerate(classes)}

    def cid(b: dict) -> int:
        item = catalogue.resolve(b.get("item") or "")
        if b["cls"] == "item_icon" and item in label:
            return ids[label[item]]
        return ids[b["cls"]]

    mini = {c["name"] for c in classes if c["group"] == "minimap"}
    expected = screens.load_expected()["states"]
    if out.exists():
        shutil.rmtree(out)
    for split, _ in SPLITS:
        (out / split / "images").mkdir(parents=True)
        (out / split / "labels").mkdir(parents=True)
    summary = {"images": {s: 0 for s, _ in SPLITS}, "boxes": {s: 0 for s, _ in SPLITS}, "classes": {},
               "skipped": {}, "names_masked": 0}
    mx, my, mw, mh = minimap_box()
    todo = {}
    for key, entry in sorted(labels.load()["screens"].items()):
        boxes = [b for b in entry.get("boxes", []) if b.get("cls") in ids and (drafts or not b.get("draft"))]
        if not boxes:
            continue
        if not include_private and is_private(key, expected.get(Path(key).stem)):
            summary["skipped"][key] = "private (other players' names)"
            continue
        todo[key] = boxes
    splits = (balanced_splits({k: {cid(b) for b in bs} for k, bs in todo.items()}) if balance
              else {k: split_of(k) for k in todo})
    per_split: dict = {}
    for key, boxes in todo.items():
        frame = cv2.imread(str(SCREENS / key))
        if frame is None:
            summary["skipped"][key] = "image missing"
            continue
        lines = det.read_text([0, 0, frame.shape[1], frame.shape[0]], frame) if (det is not None and name_ocr) else []
        summary["names_masked"] += mask_names(frame, lines, name)
        split = splits[key]
        base = re.sub(r"[^a-z0-9_]+", "_", key[:-4].lower())
        H, W = frame.shape[:2]
        full = [yolo_line(cid(b), b, 0, 0, 1.0, W, H) for b in boxes
                if b["cls"] not in mini or minimap in ("both", "full")]
        full = [ln for ln in full if ln]
        crop_boxes = [b for b in boxes if b["cls"] in mini] if minimap in ("both", "crop") else []
        written = []
        if full:
            written.append((base, frame, full))
        if crop_boxes:
            crop = cv2.resize(frame[my:my + mh, mx:mx + mw], None, fx=MINIMAP_SCALE, fy=MINIMAP_SCALE,
                              interpolation=cv2.INTER_NEAREST)
            cl = [yolo_line(cid(b), b, mx, my, MINIMAP_SCALE, crop.shape[1], crop.shape[0]) for b in crop_boxes]
            cl = [ln for ln in cl if ln]
            if cl:
                written.append((base + "_minimap", crop, cl))
        for name_, img, lns in written:
            cv2.imwrite(str(out / split / "images" / f"{name_}.png"), img)
            (out / split / "labels" / f"{name_}.txt").write_text("\n".join(lns) + "\n", encoding="utf-8")
            summary["images"][split] += 1
            summary["boxes"][split] += len(lns)
            for ln in lns:
                c = classes[int(ln.split()[0])]["name"]
                summary["classes"][c] = summary["classes"].get(c, 0) + 1
                per_split.setdefault(c, set()).add(split)
    summary["not_scored"] = sorted(c for c, sp in per_split.items() if not {"valid", "test"} <= sp)
    names = [c["name"] for c in classes]
    (out / "data.yaml").write_text(
        "# Sword x Staff UI detector (docs/detector-design.md). Class ids follow resource/detect/classes.json.\n"
        "path: .\ntrain: train/images\nval: valid/images\ntest: test/images\n"
        f"nc: {len(names)}\nnames: {json.dumps(names)}\n", encoding="utf-8")
    return summary


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="python -m sxs dataset", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", type=Path, default=CAPTURES / "dataset")
    p.add_argument("--drafts", action="store_true", help="include draft boxes mae has not confirmed")
    p.add_argument("--include-private", action="store_true", help="include chat, guild, friends and profile screens")
    p.add_argument("--no-name-ocr", action="store_true", help="mask only the fixed HUD name strip (no OCR pass)")
    p.add_argument("--minimap", choices=("both", "crop", "full"), default="both",
                   help="where minimap boxes go: an enlarged crop, the full frame, or both (default)")
    p.add_argument("--items", choices=("each", "group", "one"), default="each",
                   help="item symbols: one class per item (default), per material type (group), or all item_icon")
    p.add_argument("--hash-split", action="store_true",
                   help="plain 80/10/10 hash split (default: also move screens so each class on 3+ screens is in "
                        "valid and test)")
    p.add_argument("--zip", action="store_true", help="also write DIR.zip for a Roboflow upload")
    args = p.parse_args(argv)
    name = os.environ.get("SXS_ACCOUNT_NAME", "").strip()
    det = None
    if not args.no_name_ocr:
        if not name:
            print("Set SXS_ACCOUNT_NAME to the in-game account name so every name label is blacked out "
                  "(or pass --no-name-ocr to mask only the HUD strip).", file=sys.stderr)
            return 2
        from ..core.replay import ImageDevice
        from ..core.state import StateDetector

        det = StateDetector(ImageDevice())
    s = export(args.out, args.drafts, args.include_private, name or None, not args.no_name_ocr, det, args.minimap, args.items, not args.hash_split)
    for split, _ in SPLITS:
        print(f"{split}: {s['images'][split]} image(s), {s['boxes'][split]} box(es)")
    print("by class: " + (", ".join(f"{c} {n}" for c, n in sorted(s["classes"].items())) or "none"))
    if s["not_scored"]:
        print(f"not in both valid and test ({len(s['not_scored'])} classes, too few screens): "
              + ", ".join(s["not_scored"]))
    print(f"name labels masked: {s['names_masked']} (plus the HUD strip on every frame)")
    for key, why in sorted(s["skipped"].items()):
        print(f"skipped {key}: {why}")
    if args.zip:
        print(shutil.make_archive(str(args.out), "zip", args.out))
    print(args.out)
    return 0 if sum(s["images"].values()) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
