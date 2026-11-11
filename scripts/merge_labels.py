"""Merge another copy of docs/screens/labels.json into this checkout's, box by box, without losing mae's work.

    python scripts/merge_labels.py OTHER.json [--dry-run]

Use it when two branches both changed labels.json (mae labelling in the labeler while another thread added boxes):
put the other side in a file (e.g. `git show origin/main:docs/screens/labels.json > other.json`), keep this
checkout's version (mae's), and run this. Per screen:
- every confirmed box here is kept as it is (mae's boxes always win);
- the other side's confirmed boxes are added unless one here already covers the same thing (same class and item,
  overlap > 0.5); a clashing name gets a number;
- drafts here are kept; the other side's drafts are added unless they overlap a kept box of the same class/item.
Template crops are refreshed for every screen that changed. Prints what it added.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sxs.core import labels  # noqa: E402


def iou(a: dict, b: dict) -> float:
    x0, y0 = max(a["x"], b["x"]), max(a["y"], b["y"])
    x1, y1 = min(a["x"] + a["w"], b["x"] + b["w"]), min(a["y"] + a["h"], b["y"] + b["h"])
    inter = max(0, x1 - x0) * max(0, y1 - y0)
    union = a["w"] * a["h"] + b["w"] * b["h"] - inter
    return inter / union if union else 0.0


def same(a: dict, b: dict, limit: float) -> bool:
    return a.get("cls") == b.get("cls") and a.get("item") == b.get("item") and iou(a, b) > limit


def merge_screen(mine: list[dict], other: list[dict]) -> tuple[list[dict], int]:
    out = list(mine)
    names = {b["name"] for b in out}
    added = 0
    for want_draft in (False, True):
        for b in other:
            if bool(b.get("draft")) != want_draft:
                continue
            kept = [k for k in out if not k.get("draft")] if want_draft else out
            if any(same(b, k, 0.3 if want_draft else 0.5) for k in kept) or any(
                    k == b for k in out):
                continue
            b = dict(b)
            if b["name"] in names:
                n = 2
                while f"{b['name']}_{n}" in names:
                    n += 1
                b["name"] = f"{b['name']}_{n}"
            names.add(b["name"])
            out.append(b)
            added += 1
    return out, added


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("other", type=Path)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args(argv)
    other = json.loads(args.other.read_text(encoding="utf-8"))["screens"]
    data = labels.load()
    changed = []
    for key, entry in sorted(other.items()):
        mine = data["screens"].get(key)
        boxes, added = merge_screen(mine["boxes"] if mine else [], entry.get("boxes", []))
        if added:
            data["screens"][key] = {"size": (mine or entry)["size"], "boxes": boxes}
            changed.append(key)
            print(f"{key}: +{added} box(es)")
    if not args.dry_run and changed:
        labels.save(data)
        for key in changed:
            labels.export_crops(key)
    total = sum(len(v["boxes"]) for v in data["screens"].values())
    print(f"{len(changed)} screen(s) changed; {total} box(es) in all" + (" (dry run)" if args.dry_run else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
