"""Draft detector boxes on the reference screens from the detectors the bot already has, for mae to fix in the
labeler instead of drawing every box (docs/detector-design.md, step 2).

    python -m sxs prelabel [NAME ...] [--ocr] [--items] [--only CLASSES] [--redraft CLASSES] [--dry-run]

For each screen in docs/screens/ (not icons/, minimap/, unlabeled/) with an expected state, runs the matching
colour/template detectors and writes their boxes into docs/screens/labels.json as drafts ("draft": true, with a
detector class). It never touches a box mae made or confirmed: old drafts on a screen are replaced, and a new draft
that overlaps a confirmed box of the same class is skipped. --ocr also boxes area-map zone labels and % lines and
Claim / "Tap to spin" buttons by their text (needs MaaFramework and the OCR models). Point detectors give centres
only, so their boxes use a typical size per class: drafts are meant to be checked. --items boxes every symbol from
the item catalogue (resource/items, matched at many sizes) as item_icon with the item's id; a run without --items
replaces those drafts too, so keep passing it once item drafts matter. --only limits a run to some classes or
groups (so drafts mae deleted for other classes do not come back), and --redraft turns her confirmed boxes of some
classes back into drafts first, kept where they are, to check them again (mae, 2026-11-10: the map markers).
"""

from __future__ import annotations

import argparse
import re
import sys
from typing import Optional

import cv2
import numpy as np

from ..core import labels, screens

# Typical box size (w, h) for detectors that only give a centre.
POINT_SIZE = {"badge_red_bang": (30, 30), "badge_blue_pip": (30, 30), "map_statue_bang": (30, 32),
              "player_character": (80, 120)}
CHARACTER_STATES = {"character", "class_page", "skill_page", "enhance_gear", "gear_resonance", "technique_upgrade",
                    "rank_advancement", "upgrade_goals"}
MAP_KINDS = {"player": "map_player", "item": "map_item", "monster": "map_monster", "building": "map_building"}
PCT = re.compile(r"(?:Exploration\s*:?\s*)?\d+\s*%$")
BUTTON_TEXT = [(re.compile(r"^Claim( All)?$"), "btn_claim"), (re.compile(r"^Tap to spin$"), "btn_tap_to_spin")]
BUTTON_PAD = (40, 14)  # OCR gives the caption's box; the button is wider and taller


def _point_box(cls: str, xy) -> dict:
    w, h = POINT_SIZE[cls]
    return {"cls": cls, "x": int(xy[0] - w / 2), "y": int(xy[1] - h / 2), "w": w, "h": h}


def area_map_objects(frame: np.ndarray) -> list[dict]:
    """Area-map dots and icons as boxes (sxs/vision/area_map.py's masks, with each blob's own extent)."""
    from ..vision import area_map as am

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    x0, y0, w, h = am.MAP_AREA
    lx, ly, lw, lh = am.LEGEND
    out = []
    for kind, mask in am._masks(hsv).items():
        m = np.zeros(mask.shape, np.uint8)
        m[y0:y0 + h, x0:x0 + w] = mask[y0:y0 + h, x0:x0 + w]
        m[ly:ly + lh, lx:lx + lw] = 0
        n, _, stats, _ = cv2.connectedComponentsWithStats(m)
        lo, hi = am.SIZES[kind]
        for i in range(1, n):
            bx, by, bw, bh, area = (int(v) for v in stats[i])
            # Dots and icons are compact; the glow round a selected zone and label edges make thin, sparse blobs.
            if lo <= area <= hi and max(bw, bh) <= 32 and area >= 0.35 * bw * bh and max(bw, bh) <= 2.2 * min(bw, bh):
                pad = 3
                out.append({"cls": MAP_KINDS[kind], "x": bx - pad, "y": by - pad, "w": bw + 2 * pad, "h": bh + 2 * pad})
    out = [b for b in out if not _in_text_row(b, out)]
    out += [_point_box("map_statue_bang", (x, y - am.STATUE_BELOW)) for x, y in am.blue_badges(frame)]
    return out


ROW = (6, 30, 3)  # same line within dy px, neighbours within dx px, how many make a text row


def _in_text_row(b: dict, boxes: list[dict]) -> bool:
    """True when ROW[2] or more blobs of the same class sit beside it on one line: letters of a coloured label
    (red CP numbers, zone names), not map icons. mae removed 44 of 61 monster drafts (2026-11-10); with ROW the
    drafts on her four area maps keep all 17 monsters she confirmed and the extras drop from 44 to 22."""
    cx, cy = b["x"] + b["w"] / 2, b["y"] + b["h"] / 2
    near = sum(1 for o in boxes if o is not b and o["cls"] == b["cls"]
               and abs(o["y"] + o["h"] / 2 - cy) <= ROW[0] and abs(o["x"] + o["w"] / 2 - cx) <= ROW[1])
    return near >= ROW[2]


def minimap_objects(frame: np.ndarray) -> list[dict]:
    """Minimap dots and icons as boxes in frame coordinates (sxs/vision/minimap.py's colour rules, per blob).
    Our own marker in the centre is left out."""
    from ..vision import minimap as mm

    cx, cy, r = mm.CENTER[0], mm.CENTER[1], mm.RADIUS
    crop = frame[cy - r:cy + r, cx - r:cx + r]
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV).astype(int)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    yy, xx = np.mgrid[0:2 * r, 0:2 * r]
    d2 = (xx - r) ** 2 + (yy - r) ** 2
    inside = (d2 <= (r - 1.5 * mm.TILE) ** 2) & (d2 > (1.5 * mm.TILE) ** 2)
    masks = {
        "mm_item": (((h >= 38) & (h <= 80) & (s > 110) & (v > 180)) | ((h >= 36) & (h <= 46) & (s >= 65) & (v >= 195))),
        "mm_monster": (h >= 5) & (h <= 22) & (s > 100) & (v > 150),
        "mm_building": (h >= 23) & (h <= 34) & (s > 140) & (v > 170),
        "mm_icon": (s < 35) & (v > 215),
    }
    out = []
    for cls, mask in masks.items():
        m = (mask & inside).astype(np.uint8)
        n, _, stats, _ = cv2.connectedComponentsWithStats(m)
        for i in range(1, n):
            bx, by, bw, bh, area = (int(q) for q in stats[i])
            big = cls in ("mm_icon", "mm_building")  # statues, houses and gold buildings are ~20 px icons
            if 6 <= area <= (450 if big else 150) and bw <= (28 if big else 18) and bh <= (28 if big else 18):
                out.append({"cls": cls, "x": cx - r + bx - 2, "y": cy - r + by - 2, "w": bw + 4, "h": bh + 4})
    return out


# Screen anchors that sit at a fixed place on their screens (x, y, w, h), by detector state.
TITLE_STATES = {"enhance_gear", "mall", "companions", "map_exploration", "gear_resonance", "rank_advancement",
                "upgrade_goals", "technique_upgrade", "featured", "material_realms", "prayer_result", "prayer",
                "quests", "furniture_upgrade"}
TAB_STATES = {"home", "character", "world_overview", "guild", "skill_page"}
HUD_STATES = {"home", "world_map", "character"}


def anchor_drafts(state: str) -> list[dict]:
    from ..vision import area_map as am
    from ..vision import minimap as mm

    out = []
    if state == "world_map":
        r = mm.RADIUS + 6
        out.append({"cls": "anchor_minimap_ring", "x": mm.CENTER[0] - r, "y": mm.CENTER[1] - r, "w": 2 * r, "h": 2 * r})
    if state in TAB_STATES:
        out.append({"cls": "anchor_tab_bar", "x": 0, "y": 1185, "w": 720, "h": 95})
    if state in HUD_STATES:
        out.append({"cls": "anchor_hud_portrait", "x": 0, "y": 0, "w": 100, "h": 110})
    if state == "battle":
        out.append({"cls": "anchor_battle_round", "x": 200, "y": 10, "w": 320, "h": 60})
    if state in TITLE_STATES:
        out.append({"cls": "anchor_page_title", "x": 0, "y": 20, "w": 440, "h": 70})
    if state == "area_map":
        x, y, w, h = am.LEGEND
        out.append({"cls": "anchor_area_map_legend", "x": x, "y": y, "w": w, "h": h})
    return out


def colour_drafts(frame: np.ndarray, state: str) -> list[dict]:
    """Drafts from the colour and template detectors that need no OCR."""
    from ..vision import badges, gift, pickups, player

    out: list[dict] = []
    if state == "area_map":
        return area_map_objects(frame)
    out += [_point_box("badge_red_bang", p) for p in badges.find_badges(frame)]
    if state in CHARACTER_STATES:
        out += [_point_box("badge_blue_pip", p) for p in badges.find_up_pips(frame)]
    if state in ("world_map", "home"):
        g = gift.find_gift(frame)
        if g is not None:
            th, tw = gift._template().shape[:2]
            out.append({"cls": "badge_gift", "x": int(g[0] - tw / 2), "y": int(g[1] - th / 2), "w": tw, "h": th})
    if state == "world_map":
        out += minimap_objects(frame)
        out += [{"cls": "badge_gold_ring", "x": x - r, "y": y - r, "w": 2 * r, "h": 2 * r}
                for x, y, r in pickups.find_rings(frame)]
        me = player.player_sprite(frame)
        if me is not None:  # the point sits just above the name label; the body is above it
            out.append(_point_box("player_character", (me[0], me[1] - 30)))
    return out


def ocr_drafts(det, frame: np.ndarray, state: str) -> list[dict]:
    """Drafts found by text: zone labels and % lines on the area map, Claim / Tap to spin buttons anywhere."""
    out = []
    lines = det.read_text([0, 0, 720, 1280], frame)
    for text, (x, y, w, h) in lines:
        t = text.replace("-", " ").strip(" |")
        if state == "area_map" and 120 <= y < 1185:
            if PCT.search(t):
                out.append({"cls": "map_pct_line", "x": x - 4, "y": y - 3, "w": w + 8, "h": h + 6})
            elif len(t) >= 4 and x < 540 and not re.search(r"Ore$|Sandstone|Portal|Statue|Ahead of|\dK$", t):
                out.append({"cls": "map_zone_label", "x": x - 4, "y": y - 3, "w": w + 8, "h": h + 6})
            continue
        for rx, cls in BUTTON_TEXT:
            if rx.match(t.strip()):
                px, py = BUTTON_PAD
                out.append({"cls": cls, "x": x - px, "y": y - py, "w": w + 2 * px, "h": h + 2 * py})
    return out


def _iou(a: dict, b: dict) -> float:
    x0, y0 = max(a["x"], b["x"]), max(a["y"], b["y"])
    x1, y1 = min(a["x"] + a["w"], b["x"] + b["w"]), min(a["y"] + a["h"], b["y"] + b["h"])
    inter = max(0, x1 - x0) * max(0, y1 - y0)
    union = a["w"] * a["h"] + b["w"] * b["h"] - inter
    return inter / union if union else 0.0


def merge(existing: list[dict], drafts: list[dict], size: tuple[int, int], keep_drafts: frozenset = frozenset()
          ) -> list[dict]:
    """Keep mae's boxes, replace the old drafts, skip drafts that overlap a kept box of the same class.
    Drafts of a class in keep_drafts (boxes turned back into drafts by --redraft) are kept too."""
    kind = {c["name"]: c["kind"] for c in labels.classes()}
    kept = [b for b in existing if not b.get("draft") or b.get("cls") in keep_drafts]
    names = {b["name"] for b in kept}
    out = list(kept)
    W, H = size
    for d in drafts:
        x0, y0 = max(0, d["x"]), max(0, d["y"])
        x1, y1 = min(W, d["x"] + d["w"]), min(H, d["y"] + d["h"])
        if x1 - x0 < 4 or y1 - y0 < 4:
            continue
        d = dict(d, x=x0, y=y0, w=x1 - x0, h=y1 - y0)
        if any(b.get("cls") == d["cls"] and b.get("item") == d.get("item") and _iou(b, d) > 0.3 for b in out):
            continue
        base = d.get("item") or d["cls"]
        n = 1
        while f"{base}_{n}" in names:
            n += 1
        name = f"{base}_{n}"
        names.add(name)
        out.append({"name": name, "kind": kind.get(d["cls"], "other"), "x": d["x"], "y": d["y"], "w": d["w"],
                    "h": d["h"], "note": "pre-labelled", "template": False, "cls": d["cls"], "draft": True,
                    **({"item": d["item"]} if d.get("item") else {})})
    return out


def item_drafts(frame: np.ndarray, templates=None) -> list[dict]:
    """item_icon drafts for every catalogued symbol found on the frame (resource/items, sxs/detect/items.py)."""
    from . import items

    return [{"cls": "item_icon", "item": h["item"], "x": h["x"], "y": h["y"], "w": h["w"], "h": h["h"]}
            for h in items.find(frame, templates=templates)]


def class_set(spec: str) -> frozenset:
    """Class names from a comma list of class names and/or groups (classes.json "group"), e.g. "area_map,minimap"."""
    want = {w.strip() for w in spec.split(",") if w.strip()}
    cls = labels.classes()
    got = {c["name"] for c in cls if c["name"] in want or c["group"] in want}
    unknown = want - {c["name"] for c in cls} - {c["group"] for c in cls}
    if unknown:
        raise ValueError(f"not a class or group: {', '.join(sorted(unknown))}")
    return frozenset(got)


def redraft(classes: frozenset, dry_run: bool = False) -> dict:
    """Turn every confirmed box of these classes back into a draft (same place and size) on every screen, so mae
    checks them again in the labeler. Returns {screen key: boxes turned}."""
    data = labels.load()
    report = {}
    for key, entry in data["screens"].items():
        n = 0
        for b in entry.get("boxes", []):
            if b.get("cls") in classes and not b.get("draft"):
                b["draft"] = True
                n += 1
        if n:
            report[key] = n
    if report and not dry_run:
        labels.save(data)
    return report


def run(names: Optional[set] = None, ocr: bool = False, dry_run: bool = False, with_items: bool = False,
        only: Optional[frozenset] = None, keep_drafts: frozenset = frozenset()) -> dict:
    """Pre-label the reference screens. Returns {screen key: number of drafts written}.
    only: draft just these classes (other classes' drafts are left as they are)."""
    det = None
    if ocr:
        from ..core.paths import RESOURCE

        missing = [f for f in ("det.onnx", "rec.onnx") if not (RESOURCE / "model" / "ocr" / f).exists()]
        if missing:
            raise SystemExit(f"--ocr needs the OCR models in resource/model/ocr/ ({', '.join(missing)} missing; they "
                             "are gitignored, so every new clone or worktree needs them): run "
                             "python scripts/fetch-ocr-models.py, or copy them from another checkout.")
        from ..core.replay import ImageDevice
        from ..core.state import StateDetector

        det = StateDetector(ImageDevice())
    tpl = None
    if with_items:
        from . import items

        tpl = items._templates()
    expected = screens.load_expected()["states"]
    report = {}
    for path in screens.reference_screens():
        if names and path.stem not in names:
            continue
        state = expected.get(path.stem)
        if not state:
            continue
        frame = cv2.imread(str(path))
        if frame is None:
            continue
        drafts = colour_drafts(frame, state) + anchor_drafts(state)
        if det is not None:
            drafts += ocr_drafts(det, frame, state)
        if tpl:
            drafts += item_drafts(frame, tpl)
        key = labels.screen_key(path)
        size = (frame.shape[1], frame.shape[0])
        keep = keep_drafts
        if only is not None:
            drafts = [d for d in drafts if d["cls"] in only]
            keep = keep | frozenset(b.get("cls") for b in labels.boxes_for(key) if b.get("cls") not in only)
        boxes = merge(labels.boxes_for(key), drafts, size, keep)
        new = sum(1 for b in boxes if b.get("draft"))
        old = labels.boxes_for(key)
        if new or any(b.get("draft") for b in old):
            report[key] = new
            if not dry_run:
                labels.set_boxes(key, boxes, size)
    return report


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="python -m sxs prelabel", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("names", nargs="*", help="only these screens (file names without .png)")
    p.add_argument("--ocr", action="store_true", help="also box zone labels and buttons by their text (MaaFramework)")
    p.add_argument("--items", action="store_true",
                   help="also box every catalogued item/currency symbol (resource/items; ~10 s a screen)")
    p.add_argument("--only", default="", help="draft only these classes or groups, e.g. area_map,minimap "
                   "(drafts of other classes are left alone; mae's rejections of them are not undone)")
    p.add_argument("--redraft", default="",
                   help="first turn every confirmed box of these classes or groups back into a draft for re-checking")
    p.add_argument("--dry-run", action="store_true", help="count the drafts, write nothing")
    args = p.parse_args(argv)
    keep = frozenset()
    if args.redraft:
        keep = class_set(args.redraft)
        turned = redraft(keep, args.dry_run)
        print(f"turned back into drafts: {sum(turned.values())} box(es) on {len(turned)} screen(s)")
    only = class_set(args.only) if args.only else None
    report = run(set(args.names) or None, args.ocr, args.dry_run, args.items, only, keep)
    by_cls: dict[str, int] = {}
    for key in report:
        for b in labels.boxes_for(key) if not args.dry_run else []:
            if b.get("draft"):
                by_cls[b["cls"]] = by_cls.get(b["cls"], 0) + 1
    for key, n in sorted(report.items()):
        print(f"{key}: {n} draft(s)")
    if by_cls:
        print("by class: " + ", ".join(f"{c} {n}" for c, n in sorted(by_cls.items())))
    print(f"{sum(report.values())} draft box(es) on {sum(1 for n in report.values() if n)} screen(s)"
          + (" (dry run, nothing written)" if args.dry_run else "; check them in python -m sxs labeler"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
