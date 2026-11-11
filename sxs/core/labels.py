"""Boxes mae draws on reference screens with the labeling UI (`python -m sxs labeler`), and the crops cut from them.

    docs/screens/labels.json            {"screens": {"<folder>/<file>.png": {"size": [w, h], "boxes": [box, ...]}}}
    resource/image/labels/<screen>/<box>.png   one crop per box marked "template" (a matchable reference)
    resource/image/labels/manifest.json        one row per crop: screen, box, kind, roi, source, template path

A box is {"name": "upgrade_button", "kind": "button", "x", "y", "w", "h", "note": "...", "template": true}, in
pixels of the screen file (reference frames are 720x1280, so these are frame coordinates). Kinds say what the
box is for: a button to tap, text to read with OCR, an icon or badge to match, or a region to watch.

For the UI detector (docs/detector-design.md) a box can also carry "cls", one of the detector classes in
resource/detect/classes.json, and "draft": true when the pre-labeller drew it and mae has not confirmed it yet.
A box of class item_icon can also carry "item", an id from the item catalogue (resource/items/items.json).
Only boxes with a cls go into a training dataset (`python -m sxs dataset`); drafts only when asked.

docs/screens/rejected.json remembers the drafts mae removed ({"screens": {key: [{"cls", "item", "x", "y", "w",
"h"}]}}), so `python -m sxs prelabel` never drafts the same thing again (docs/labeler-diagnosis.md, 2026-11-11).

The template path in the manifest is relative to resource/image/, so a pipeline node can use it as `template` and
code can use `sxs/vision/labels.py`. Needs Pillow only (no OpenCV, no MaaFramework).
"""

from __future__ import annotations

import json
import re
import shutil
from datetime import date
from pathlib import Path
from typing import Optional

from .paths import RESOURCE, SCREENS

LABELS_FILE = SCREENS / "labels.json"
IMAGE = RESOURCE / "image"
CROPS = IMAGE / "labels"
CLASSES_FILE = RESOURCE / "detect" / "classes.json"
MANIFEST = CROPS / "manifest.json"
KINDS = ("button", "text", "icon", "badge", "region", "other")
TEMPLATE_KINDS = ("button", "icon", "badge")  # ticked as templates by default in the UI
NAME = re.compile(r"^[a-z][a-z0-9_]*$")


def item_ids() -> list[str]:
    """Ids in the item catalogue (resource/items/items.json), in order."""
    from ..detect import items

    return items.ids()


def classes() -> list[dict]:
    """The detector classes, in id order: [{"name", "group", "kind", "about"}]."""
    if not CLASSES_FILE.exists():
        return []
    return json.loads(CLASSES_FILE.read_text(encoding="utf-8")).get("classes", [])


def load() -> dict:
    data = json.loads(LABELS_FILE.read_text(encoding="utf-8")) if LABELS_FILE.exists() else {}
    return {"screens": data.get("screens", {})}


def save(data: dict) -> None:
    screens = {k: v for k, v in sorted(data["screens"].items()) if v.get("boxes")}
    LABELS_FILE.write_text(json.dumps({"screens": screens}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def screen_key(path: Path) -> str:
    """'home/cart.png' for docs/screens/home/cart.png."""
    return path.relative_to(SCREENS).as_posix()


def clean_boxes(boxes: list, size: tuple[int, int]) -> tuple[list[dict], list[str]]:
    """Validate boxes from the UI: names, kinds, clamp to the image. Returns (boxes, problems)."""
    w, h = size
    known = {c["name"] for c in classes()}
    out, problems, seen = [], [], set()
    for i, b in enumerate(boxes):
        name = str(b.get("name", "")).strip()
        if not NAME.match(name):
            problems.append(f"box {i + 1}: name {name!r} must be lower case letters, digits and _")
            continue
        if name in seen:
            problems.append(f"box {i + 1}: two boxes named {name}")
            continue
        kind = b.get("kind") if b.get("kind") in KINDS else "other"
        x0, y0 = max(0, int(round(b["x"]))), max(0, int(round(b["y"])))
        x1, y1 = min(w, int(round(b["x"] + b["w"]))), min(h, int(round(b["y"] + b["h"])))
        if x1 - x0 < 2 or y1 - y0 < 2:
            problems.append(f"box {name}: too small")
            continue
        cls = str(b.get("cls") or "").strip()
        if cls and cls not in known:
            problems.append(f"box {name}: class {cls!r} is not in resource/detect/classes.json")
            cls = ""
        item = str(b.get("item") or "").strip()
        if item:
            from ..detect import items as catalogue

            item = catalogue.resolve(item)
        if item and (cls != "item_icon" or item not in item_ids()):
            problems.append(f"box {name}: item {item!r} is not in resource/items/items.json")
            item = ""
        seen.add(name)
        box = {"name": name, "kind": kind, "x": x0, "y": y0, "w": x1 - x0, "h": y1 - y0,
               "note": str(b.get("note", "")).strip(), "template": bool(b.get("template"))}
        if cls:
            box["cls"] = cls
        if item:
            box["item"] = item
        if b.get("draft"):
            box["draft"] = True
        out.append(box)
    return out, problems


def set_boxes(key: str, boxes: list, size: tuple[int, int]) -> list[str]:
    """Store a screen's boxes and refresh its crops. Returns problems (boxes with a problem are dropped)."""
    good, problems = clean_boxes(boxes, size)
    data = load()
    if good:
        data["screens"][key] = {"size": list(size), "boxes": good}
    else:
        data["screens"].pop(key, None)
    save(data)
    export_crops(key)
    return problems


def rejected_file() -> Path:
    return LABELS_FILE.with_name("rejected.json")


def load_rejected() -> dict:
    """{screen key: [{"cls", "item", "x", "y", "w", "h"}]}: drafts mae removed."""
    f = rejected_file()
    return json.loads(f.read_text(encoding="utf-8")).get("screens", {}) if f.exists() else {}


def add_rejected(key: str, boxes: list[dict]) -> int:
    """Remember removed drafts on a screen. Returns how many were new."""
    if not boxes:
        return 0
    data = load_rejected()
    rows = data.setdefault(key, [])
    n = 0
    for b in boxes:
        row = {"cls": b.get("cls", ""), "x": int(b["x"]), "y": int(b["y"]), "w": int(b["w"]), "h": int(b["h"])}
        if b.get("item"):
            row["item"] = b["item"]
        if row not in rows:
            rows.append(row)
            n += 1
    _save_rejected(data)
    return n


def _save_rejected(data: dict) -> None:
    out = {k: sorted(v, key=lambda r: (r["cls"], r["y"], r["x"])) for k, v in sorted(data.items()) if v}
    rejected_file().write_text(json.dumps({"screens": out}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def overlap(a: dict, b: dict) -> float:
    """Intersection over union of two boxes."""
    x0, y0 = max(a["x"], b["x"]), max(a["y"], b["y"])
    x1, y1 = min(a["x"] + a["w"], b["x"] + b["w"]), min(a["y"] + a["h"], b["y"] + b["h"])
    inter = max(0, x1 - x0) * max(0, y1 - y0)
    union = a["w"] * a["h"] + b["w"] * b["h"] - inter
    return inter / union if union else 0.0


def is_rejected(key: str, box: dict, rejected: Optional[dict] = None, limit: float = 0.5) -> bool:
    """True when mae already removed a draft of this class (and item) here."""
    rows = (rejected if rejected is not None else load_rejected()).get(key, [])
    return any(r["cls"] == box.get("cls") and r.get("item", "") == box.get("item", "") and overlap(r, box) > limit
               for r in rows)


def boxes_for(key: str) -> list[dict]:
    return load()["screens"].get(key, {}).get("boxes", [])


def _stem(key: str) -> str:
    return Path(key).stem


def _load_manifest() -> list[dict]:
    return json.loads(MANIFEST.read_text(encoding="utf-8")).get("entries", []) if MANIFEST.exists() else []


def _save_manifest(entries: list[dict]) -> None:
    CROPS.mkdir(parents=True, exist_ok=True)
    entries = sorted(entries, key=lambda e: (e["screen"], e["box"]))
    MANIFEST.write_text(json.dumps({"tag": "labeled screen regions", "entries": entries}, indent=1,
                                   ensure_ascii=False) + "\n", encoding="utf-8")


def export_crops(key: str) -> list[str]:
    """Rewrite the crops for one screen from its template boxes. Returns the template paths written."""
    from PIL import Image

    stem = _stem(key)
    folder = CROPS / stem
    if folder.exists():
        shutil.rmtree(folder)
    entries = [e for e in _load_manifest() if e["source"] != key]
    written = []
    src = SCREENS / key
    boxes = [b for b in boxes_for(key) if b.get("template") and not b.get("draft")]
    if boxes and src.exists():
        folder.mkdir(parents=True, exist_ok=True)
        with Image.open(src) as im:
            im = im.convert("RGB")
            for b in boxes:
                out = folder / f"{b['name']}.png"
                im.crop((b["x"], b["y"], b["x"] + b["w"], b["y"] + b["h"])).save(out, optimize=True)
                rel = out.relative_to(IMAGE).as_posix()
                entries.append({"screen": stem, "box": b["name"], "kind": b["kind"],
                                "roi": [b["x"], b["y"], b["w"], b["h"]], "template": rel, "source": key,
                                "note": b.get("note", ""), "date": date.today().isoformat()})
                written.append(rel)
    _save_manifest(entries)
    return written


def rename(old_key: str, new_key: str) -> None:
    """A screen moved (`python -m sxs label` files a banked screen): move its boxes and crops with it."""
    data = load()
    entry = data["screens"].pop(old_key, None)
    if entry is None:
        return
    data["screens"][new_key] = entry
    save(data)
    rej = load_rejected()
    if old_key in rej:
        rej[new_key] = rej.pop(old_key)
        _save_rejected(rej)
    old = CROPS / _stem(old_key)
    if old.exists():
        shutil.rmtree(old)
    _save_manifest([e for e in _load_manifest() if e["source"] != old_key])
    export_crops(new_key)


def find_box(screen: str, box: str) -> Optional[dict]:
    """A box by screen name (file stem, any folder) and box name."""
    for key, entry in load()["screens"].items():
        if _stem(key) == screen:
            for b in entry.get("boxes", []):
                if b["name"] == box:
                    return dict(b, source=key)
    return None
