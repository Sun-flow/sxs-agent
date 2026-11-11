"""Label coverage of the detector training set: boxes and images per class, item and item group.

    python3 scripts/label_coverage.py            # print the tables (markdown)
    python3 scripts/label_coverage.py --write    # refresh the generated block in docs/detector-coverage.md

Reads docs/screens/labels.json, resource/detect/classes.json and resource/items/items.json, and counts what
`python -m sxs dataset` would export: confirmed boxes only (no drafts), screens the export leaves out as private
(guild, chat, profiles, rankings) counted separately. Image counts are distinct screens. The split column uses the
export's own 80/10/10 hash split (sxs/detect/dataset.py), so it shows which classes have no valid or test image.
Read-only: changes no labels and no export code.
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sxs.detect.dataset import is_private, split_of  # noqa: E402  (needs opencv, as the export does)

DOC = ROOT / "docs" / "detector-coverage.md"
START, END = "<!-- coverage:start -->", "<!-- coverage:end -->"
MIN_BOXES, MIN_IMAGES = 50, 20  # minimum per class for the first training run (docs/detector-coverage.md)
GOOD_BOXES, GOOD_IMAGES = 100, 50


def status(boxes: int, images: int) -> str:
    if boxes == 0:
        return "**none**"
    if boxes >= GOOD_BOXES and images >= GOOD_IMAGES:
        return "good"
    if boxes >= MIN_BOXES and images >= MIN_IMAGES:
        return "minimum"
    return "short"


def pct(n: int, total: int) -> str:
    return f"{100 * n / total:.1f}%" if total else "-"


def gather() -> dict:
    labels = json.loads((ROOT / "docs/screens/labels.json").read_text(encoding="utf-8"))["screens"]
    classes = json.loads((ROOT / "resource/detect/classes.json").read_text(encoding="utf-8"))["classes"]
    items = json.loads((ROOT / "resource/items/items.json").read_text(encoding="utf-8"))["items"]
    states = json.loads((ROOT / "docs/screens/expected.json").read_text(encoding="utf-8"))["states"]
    names = {c["name"] for c in classes}
    group_of = {i["id"]: i.get("group") or i["kind"] for i in items}
    box = collections.Counter()
    img = collections.defaultdict(set)
    split = collections.defaultdict(lambda: collections.defaultdict(set))
    ibox, iimg = collections.Counter(), collections.defaultdict(set)
    gbox, gimg = collections.Counter(), collections.defaultdict(set)
    private, drafts, labelled = collections.Counter(), 0, set()
    for key, entry in labels.items():
        priv = is_private(key, states.get(Path(key).stem))
        for b in entry.get("boxes", []):
            c = b.get("cls")
            if b.get("draft"):
                drafts += 1
                continue
            if c not in names:
                continue
            if priv:
                private[c] += 1
                continue
            labelled.add(key)
            box[c] += 1
            img[c].add(key)
            split[c][split_of(key)].add(key)
            if c == "item_icon":
                it = b.get("item") or "(no item id)"
                g = group_of.get(it, "(id not in catalogue)")
                ibox[it] += 1
                iimg[it].add(key)
                gbox[g] += 1
                gimg[g].add(key)
    frames = [p.relative_to(ROOT / "docs/screens").as_posix() for p in (ROOT / "docs/screens").rglob("*.png")]
    frames = [p for p in frames if p.split("/")[0] not in ("icons", "minimap")]
    public = [p for p in frames if not is_private(p, states.get(Path(p).stem))]
    return dict(classes=classes, items=items, group_of=group_of, box=box, img=img, split=split, ibox=ibox,
                iimg=iimg, gbox=gbox, gimg=gimg, private=private, drafts=drafts, labelled=labelled,
                frames=frames, public=public)


def render(d: dict) -> str:
    total = sum(d["box"].values())
    fixed = [c for c in d["classes"]]
    out = []
    unboxed = [p for p in d["public"] if p not in d["labelled"]]
    unboxed_by = collections.Counter(p.split("/")[0] for p in unboxed)
    out.append("### Totals\n")
    out.append("| Measure | Count |\n|---|---|")
    out.append(f"| Boxes the export would use (confirmed, not private) | {total} |")
    out.append(f"| Boxes on private screens (guild, chat, profiles; left out of the export) | "
               f"{sum(d['private'].values())} |")
    out.append(f"| Draft boxes (not exported) | {d['drafts']} |")
    out.append(f"| Screens with at least one exported box | {len(d['labelled'])} |")
    out.append(f"| Reference frames, excluding icons/ and minimap/ crops | {len(d['frames'])} |")
    out.append(f"| ... of them public (exportable) | {len(d['public'])} |")
    out.append(f"| ... public with no box yet | {len(unboxed)} ("
               + ", ".join(f"{k} {v}" for k, v in unboxed_by.most_common()) + ") |")
    n_zero = sum(1 for c in fixed if d["box"][c["name"]] == 0)
    out.append(f"| Element classes (resource/detect/classes.json) | {len(fixed)}, {n_zero} with no box |")
    out.append(f"| Catalogued items (resource/items/items.json) | {len(d['items'])}, "
               f"{sum(1 for i in d['items'] if d['ibox'][i['id']] == 0)} with no box |")
    out.append("")
    out.append("### Element classes\n")
    out.append(f"Status: **none** = no box; short = under {MIN_BOXES} boxes or {MIN_IMAGES} images; "
               f"minimum = at least that; good = {GOOD_BOXES}+ boxes on {GOOD_IMAGES}+ images. "
               "Split = images in train / valid / test (the export's hash split).\n")
    out.append("| # | Class | Group | Boxes | Images | Share of boxes | Split (tr/va/te) | Private boxes | Status |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    for i, c in enumerate(fixed):
        n = c["name"]
        s = d["split"][n]
        out.append(f"| {i} | `{n}` | {c['group']} | {d['box'][n]} | {len(d['img'][n])} | {pct(d['box'][n], total)} | "
                   f"{len(s['train'])}/{len(s['valid'])}/{len(s['test'])} | {d['private'][n] or ''} | "
                   f"{status(d['box'][n], len(d['img'][n]))} |")
    out.append("")
    out.append("### Item groups (`python -m sxs dataset --items group`)\n")
    out.append("One class per group in this mode. Share is of all item_icon boxes.\n")
    itotal = d["box"]["item_icon"]
    members = collections.Counter(d["group_of"].values())
    boxed = collections.Counter(d["group_of"][i] for i in d["ibox"] if i in d["group_of"])
    out.append("| Group | Items in catalogue | Items with a box | Boxes | Images | Share of item boxes | Status |")
    out.append("|---|---|---|---|---|---|---|")
    groups = sorted(set(members) | set(d["gbox"]), key=lambda g: (-d["gbox"][g], g))
    for g in groups:
        out.append(f"| `{g}` | {members[g]} | {boxed[g]} | {d['gbox'][g]} | {len(d['gimg'][g])} | "
                   f"{pct(d['gbox'][g], itotal)} | {status(d['gbox'][g], len(d['gimg'][g]))} |")
    out.append("")
    out.append("### Items (`python -m sxs dataset --items each`)\n")
    out.append("One class per item in this mode. Sorted by boxes; items with no box are listed after the table.\n")
    out.append("| Item | Group | Boxes | Images | Share of item boxes | Status |")
    out.append("|---|---|---|---|---|---|")
    for it, n in sorted(d["ibox"].items(), key=lambda kv: (-kv[1], kv[0])):
        out.append(f"| `{it}` | {d['group_of'].get(it, '(id not in catalogue)')} | {n} | {len(d['iimg'][it])} | {pct(n, itotal)} | "
                   f"{status(n, len(d['iimg'][it]))} |")
    missing = [i for i in d["items"] if d["ibox"][i["id"]] == 0]
    out.append("")
    out.append(f"No box yet ({len(missing)}): " + ", ".join(f"`{i['id']}` ({d['group_of'][i['id']]})"
                                                          for i in missing) + ".")
    return "\n".join(out) + "\n"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--write", action="store_true", help=f"replace the generated block in {DOC.relative_to(ROOT)}")
    args = p.parse_args()
    text = render(gather())
    if not args.write:
        print(text)
        return 0
    doc = DOC.read_text(encoding="utf-8")
    a, b = doc.index(START) + len(START), doc.index(END)
    DOC.write_text(doc[:a] + "\n\n" + text + "\n" + doc[b:], encoding="utf-8")
    print(f"wrote {DOC.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
