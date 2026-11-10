"""The item catalogue: every currency, material, ticket and consumable symbol we have seen, with its in-game name
and description, so the UI detector can learn and auto-label them (docs/detector-design.md, "Item symbols").

    python -m sxs items                              list the catalogue (unnamed symbols last)
    python -m sxs items add ID --screen KEY --box X Y W H [--name N] [--kind K] [--desc D] [--named-by B]
                                                     [--found-in "Home > Vendor Booth"] [--tight]
                                                     crop a symbol from a reference screen into the catalogue
    python -m sxs items find [SCREEN ...]            match every catalogued symbol on screens (default: all)

    resource/items/items.json    {"items": [item, ...]}, append only (the order sets detector class ids)
    resource/items/icons/*.png   one crop per sighting of an item: <id>.png, <id>_2.png, ...

An item is {"id", "name", "kind", "description", "uses", "named_by", "icons": [{"file", "screen", "box", "found_in"}]}.
- icons: one entry per sighting: the crop file, the reference screen it came from (docs/screens key), its box
  [x, y, w, h] there, and found_in, the menu path where it shows, e.g. "Home > Vendor Booth > Vault".
- id: lower case letters, digits and _, e.g. "raw_ore". A symbol we have not named yet gets "unknown_N" and
  name "" until someone taps it and reads the popup (or mae names it).
- kind: one of KINDS. "usage" is a symbol that only looks like a resource: a round glowing badge with a counter in
  Material Realms (crossed hammer and sword, "11"; docs/screens/icons/material_realm_usage_badge_mae.png) stands
  for uses or attempts, not a material you own (mae, 2026-11-10). Give it its own id (e.g. realm_attempts), never
  a sighting of the look-alike resource, so the detector keeps the two apart. named_by says how sure the name is: "popup" (read from the item's own name and description
  popup, the goal for every item), "screen" (a label next to it, e.g. a shop or cart row), "mae", or "guess".
- description: the popup text, word for word. uses: our own note (what it is for, rules that touch it).

Standing rule (mae, 2026-11-10): whenever a thread sees a material or currency symbol that is not in this
catalogue, it finds out what it is (tap the symbol, read the popup) and adds it here. Not every item matters to
the bot, but every one helps train the detector.

`find` and the pre-labeller use multi-scale template matching of the icon crops: the same art shows up at about
28 px in the top bar and 90-120 px on shop cards, so each crop is tried at sizes from MIN_SIZE to MAX_SIZE.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional

from ..core.paths import RESOURCE, SCREENS

ITEMS_DIR = RESOURCE / "items"
ITEMS_FILE = ITEMS_DIR / "items.json"
ICONS = ITEMS_DIR / "icons"
KINDS = ("currency", "material", "ticket", "consumable", "ingredient", "gift", "key_item", "gear", "usage", "other")
NAMED_BY = ("popup", "screen", "mae", "guess", "")
ID = re.compile(r"^[a-z][a-z0-9_]*$")
MATCH = 0.86  # normalised correlation needed for a hit
MIN_SIZE, MAX_SIZE = 22, 130  # icon sizes (longest side, px) tried by find()
SIZES = (22, 24, 26, 28, 30, 33, 36, 40, 44, 48, 53, 58, 64, 70, 77, 85, 93, 102, 112, 122, 132)


def load() -> dict:
    if not ITEMS_FILE.exists():
        return {"items": []}
    return json.loads(ITEMS_FILE.read_text(encoding="utf-8"))


def save(data: dict) -> None:
    ITEMS_DIR.mkdir(parents=True, exist_ok=True)
    ITEMS_FILE.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def ids() -> list[str]:
    return [it["id"] for it in load()["items"]]


def get(item_id: str) -> Optional[dict]:
    return next((it for it in load()["items"] if it["id"] == item_id), None)


def next_unknown(data: dict) -> str:
    n = 1
    have = {it["id"] for it in data["items"]}
    while f"unknown_{n}" in have:
        n += 1
    return f"unknown_{n}"


def tighten(img, box: list[int], thr: int = 45) -> list[int]:
    """Shrink a rough box to the symbol: pixels that differ from the box's left and right edge colour, row by row
    (shop cards and popups have a flat or gently shaded background)."""
    import cv2
    import numpy as np

    x, y, w, h = box
    r = img[y:y + h, x:x + w].astype(int)
    bg = np.median(np.concatenate([r[:, :3], r[:, -3:]], 1), axis=1, keepdims=True)
    m = (np.abs(r - bg).sum(2) > thr).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    ys, xs = np.nonzero(m)
    if len(xs) < 30:
        return box
    x0, y0 = max(0, x + int(xs.min()) - 2), max(0, y + int(ys.min()) - 2)
    return [x0, y0, min(img.shape[1], x + int(xs.max()) + 3) - x0, min(img.shape[0], y + int(ys.max()) + 3) - y0]


def add(item_id: str, screen: str, box: list[int], name: str = "", kind: str = "other", desc: str = "",
        named_by: str = "", uses: str = "", tight: bool = False, found_in: str = "") -> dict:
    """Crop `box` from docs/screens/<screen> into the catalogue, creating the item or adding a sighting.
    item_id "unknown" makes a new unknown_N. Fields given replace empty ones on an existing item."""
    import cv2

    if kind not in KINDS:
        raise ValueError(f"kind must be one of {', '.join(KINDS)}")
    if named_by not in NAMED_BY:
        raise ValueError(f"named_by must be one of {', '.join(n for n in NAMED_BY if n)}")
    img = cv2.imread(str(SCREENS / screen))
    if img is None:
        raise FileNotFoundError(SCREENS / screen)
    if tight:
        box = tighten(img, box)
    x, y, w, h = box
    if w < 8 or h < 8:
        raise ValueError("box too small for a symbol")
    data = load()
    if item_id == "unknown":
        item_id = next_unknown(data)
    if not ID.match(item_id):
        raise ValueError("id must be lower case letters, digits and _")
    it = next((i for i in data["items"] if i["id"] == item_id), None)
    if it is None:
        it = {"id": item_id, "name": name, "kind": kind, "description": desc, "uses": uses, "named_by": named_by,
              "icons": []}
        data["items"].append(it)
    else:
        for k, v in (("name", name), ("description", desc), ("uses", uses), ("named_by", named_by)):
            if v and not it.get(k):
                it[k] = v
        if kind != "other" and it.get("kind") in ("", "other"):
            it["kind"] = kind
    n = len(it["icons"]) + 1
    fname = f"{item_id}.png" if n == 1 else f"{item_id}_{n}.png"
    ICONS.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(ICONS / fname), img[y:y + h, x:x + w])
    it["icons"].append({"file": fname, "screen": screen, "box": [x, y, w, h], "found_in": found_in})
    save(data)
    return it


def _templates():
    import cv2

    out = []
    for it in load()["items"]:
        for ic in it["icons"]:
            t = cv2.imread(str(ICONS / ic["file"]))
            if t is not None:
                out.append((it["id"], t))
    return out


def find(frame, threshold: float = MATCH, templates=None) -> list[dict]:
    """Every catalogued symbol on the frame: [{"item", "x", "y", "w", "h", "score"}], best first, overlaps removed.
    A coarse pass on a half-size frame finds candidates; each is checked again at full size."""
    import cv2
    import numpy as np

    hits = []
    H, W = frame.shape[:2]
    small = cv2.resize(frame, (W // 2, H // 2), interpolation=cv2.INTER_AREA)
    for item_id, t in templates if templates is not None else _templates():
        side = max(t.shape[:2])
        for size in sorted(set(SIZES) | {side}):
            s = size / side
            if not (0.2 <= s <= 1.6):
                continue
            tw, th = max(4, round(t.shape[1] * s)), max(4, round(t.shape[0] * s))
            if tw >= W or th >= H:
                continue
            tt = cv2.resize(t, (tw, th), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_LINEAR)
            ts = cv2.resize(tt, (max(3, tw // 2), max(3, th // 2)), interpolation=cv2.INTER_AREA)
            res = cv2.matchTemplate(small, ts, cv2.TM_CCOEFF_NORMED)
            peak = (res >= threshold - 0.12) & (res == cv2.dilate(res, np.ones((5, 5), np.uint8)))
            for x, y in zip(*np.nonzero(peak)[::-1]):
                x0, y0 = max(0, 2 * x - 4), max(0, 2 * y - 4)
                win = frame[y0:min(H, 2 * y + th + 4), x0:min(W, 2 * x + tw + 4)]
                if win.shape[0] < th or win.shape[1] < tw:
                    continue
                r = cv2.matchTemplate(win, tt, cv2.TM_CCOEFF_NORMED)
                _, best, _, (bx, by) = cv2.minMaxLoc(r)
                if best >= threshold:
                    hits.append({"item": item_id, "x": x0 + bx, "y": y0 + by, "w": tw, "h": th, "score": float(best)})
    hits.sort(key=lambda h: -h["score"])
    kept: list[dict] = []
    for h in hits:
        if all(_iou(h, k) < 0.3 for k in kept):
            kept.append(h)
    return kept


def _iou(a: dict, b: dict) -> float:
    x0, y0 = max(a["x"], b["x"]), max(a["y"], b["y"])
    x1, y1 = min(a["x"] + a["w"], b["x"] + b["w"]), min(a["y"] + a["h"], b["y"] + b["h"])
    inter = max(0, x1 - x0) * max(0, y1 - y0)
    union = a["w"] * a["h"] + b["w"] * b["h"] - inter
    return inter / union if union else 0.0


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="python -m sxs items", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd")
    a = sub.add_parser("add", help="crop a symbol from a reference screen into the catalogue")
    a.add_argument("id", help='item id, e.g. raw_ore, or "unknown" for the next unknown_N')
    a.add_argument("--screen", required=True, help="docs/screens key, e.g. shops/vendor_booth_general.png")
    a.add_argument("--box", nargs=4, type=int, required=True, metavar=("X", "Y", "W", "H"))
    a.add_argument("--name", default="")
    a.add_argument("--kind", default="other", choices=KINDS)
    a.add_argument("--desc", default="", help="the popup's description, word for word")
    a.add_argument("--uses", default="", help="our note: what it is for")
    a.add_argument("--named-by", default="", choices=[n for n in NAMED_BY if n])
    a.add_argument("--found-in", default="", help='menu path, e.g. "Home > Vendor Booth > Vault"')
    a.add_argument("--tight", action="store_true", help="shrink the box to the symbol")
    f = sub.add_parser("find", help="match catalogued symbols on reference screens")
    f.add_argument("names", nargs="*", help="screen file names without .png (default: all)")
    f.add_argument("--threshold", type=float, default=MATCH)
    args = p.parse_args(argv)
    if args.cmd == "add":
        it = add(args.id, args.screen, args.box, args.name, args.kind, args.desc, args.named_by, args.uses,
                 args.tight, args.found_in)
        ic = it["icons"][-1]
        print(f"{it['id']}: {it['name'] or '(unnamed)'} · {it['kind']} · icon {ic['file']} {ic['box']}")
        return 0
    if args.cmd == "find":
        import cv2

        from ..core import screens

        tpl = _templates()
        for path in screens.reference_screens():
            if args.names and path.stem not in args.names:
                continue
            frame = cv2.imread(str(path))
            if frame is None:
                continue
            hits = find(frame, args.threshold, tpl)
            if hits:
                print(f"{path.relative_to(SCREENS).as_posix()}: " + ", ".join(
                    f"{h['item']} ({h['x']},{h['y']} {h['w']}x{h['h']} {h['score']:.2f})" for h in hits))
        return 0
    items = sorted(load()["items"], key=lambda i: (not i.get("name"), i["kind"], i["id"]))
    for it in items:
        print(f"{it['id']:<24} {it.get('name') or '(unnamed)':<24} {it['kind']:<11} "
              f"{it.get('named_by') or '-':<7} {len(it['icons'])} icon(s)  {it.get('uses', '')}")
    print(f"{len(items)} item(s); {sum(1 for i in items if not i.get('name'))} unnamed; "
          f"{sum(1 for i in items if i.get('named_by') != 'popup')} without a popup read")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
