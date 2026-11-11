"""Reference screenshots in docs/screens/: which folder a screen goes in, the detector's expected states, and the
bank of unlabelled screens mae labels by hand.

    docs/screens/<folder>/<name>.png   reference screens, sorted by situation (FOLDERS)
    docs/screens/expected.json         {"states": {name: state the detector must report}, "notes": {name: text}}
    docs/screens/unlabeled/            screens nobody has named yet, listed in unlabeled/README.md

`python -m sxs bank` copies the frames the loops saved to captures/unknown/ into the bank and adds a row for each.
mae fills in the row. `python -m sxs label` then files every filled row into its folder and records its state.
Only reads and writes files; needs no MaaFramework.
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Optional

from . import labels
from .paths import CAPTURES, SCREENS

# Folder by name prefix, first match wins. Exact names in FOLDER_OF override the prefixes.
FOLDERS = (
    ("home", ("home", "bed", "cart", "furniture_", "alchemy_", "cooked", "main_menu", "notice", "friends", "team",
              "prayer", "journal")),
    ("character", ("character", "charm_", "class_", "enhance_", "gear_", "loadout_", "player_profile", "rank_",
                   "rcmd_", "replace_gear", "skill_", "technique_")),
    ("battle", ("battle", "defeated", "wounded")),
    ("dailies", ("achievement_", "daily_", "quest_", "fantasia_", "growth_", "material_")),
    ("guild", ("guild_",)),
    ("shops", ("mall_", "vendor_", "purchase_")),
    ("dialogs", ("confirm_", "dialogue", "reward_", "tutorial_", "rating_", "unlocked")),
    ("system", ("title", "loading", "logging_in", "splash", "settings_", "photo_")),
    ("world", ("world_", "area_map", "explore_", "gate_", "dungeon_", "interact_", "ironvein_", "lost_", "puzzle_",
               "blessing_", "map_", "exploration_", "destiny_", "item_")),
)
FOLDER_OF = {"apply_requests": "guild"}
SPECIAL = ("icons", "items", "minimap", "sequences", "unlabeled")  # not checked by the detector test (items: popup captures)
UNLABELED = SCREENS / "unlabeled"
BANK_INDEX = UNLABELED / "README.md"
EXPECTED_FILE = SCREENS / "expected.json"
UNKNOWN_FRAMES = CAPTURES / "unknown"

NAME = re.compile(r"^[a-z][a-z0-9_]*$")
BANK_HEADER = """# Unlabelled screens

Screens nobody has named yet. The loops save every screen they don't recognise to `captures/unknown/`, and
`python -m sxs bank` copies those frames here, one row each.

To label a screen, fill in its row:

- **Name**: a file name in lower case, such as `guild_shop_top`. The prefix picks the folder, so `guild_` goes
  in `guild/`. Leave it empty to keep the current name.
- **Folder**: optional. Use it to override the folder that the prefix picks.
- **State**: what the detector must report on this screen, such as `guild_panel`. Write `unknown` if no state fits
  yet, or `-` to keep the screen without a detector check.
- **What it is**: anything worth knowing. It is saved with the screen.

Then run `python -m sxs label`. Each row that has a State moves into its folder and is added to
`docs/screens/expected.json`.

| File | Name | Folder | State | What it is |
|---|---|---|---|---|
"""


def folder_for(name: str) -> str:
    if name in FOLDER_OF:
        return FOLDER_OF[name]
    for folder, prefixes in FOLDERS:
        if name.startswith(prefixes):
            return folder
    return "unlabeled"


def reference_screens() -> list[Path]:
    """Every screen the detector test runs over (everything except icons/, minimap/ and unlabeled/)."""
    return sorted(p for p in SCREENS.rglob("*.png") if p.relative_to(SCREENS).parts[0] not in SPECIAL)


def find(name: str, banked: bool = False) -> Optional[Path]:
    """A filed screen by name, whichever folder it is in (banked=True also looks in unlabeled/)."""
    hits = sorted(p for p in SCREENS.rglob(f"{name}.png") if banked or UNLABELED not in p.parents)
    return hits[0] if hits else None


def load_expected() -> dict:
    data = json.loads(EXPECTED_FILE.read_text(encoding="utf-8")) if EXPECTED_FILE.exists() else {}
    return {"states": data.get("states", {}), "notes": data.get("notes", {})}


def save_expected(data: dict) -> None:
    out = {"states": dict(sorted(data["states"].items())), "notes": dict(sorted(data["notes"].items()))}
    EXPECTED_FILE.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


# --- the unlabelled bank -------------------------------------------------------------------------------------------

def _rows() -> list[dict]:
    if not BANK_INDEX.exists():
        return []
    rows = []
    for line in BANK_INDEX.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 5 and cells[0].startswith("`") and cells[0].endswith(".png`"):
            rows.append(dict(zip(("file", "name", "folder", "state", "what"), cells), file=cells[0].strip("`")))
    return rows


def _write_rows(rows: list[dict]) -> None:
    UNLABELED.mkdir(parents=True, exist_ok=True)
    body = "".join(f"| `{r['file']}` | {r['name']} | {r['folder']} | {r['state']} | {r['what']} |\n" for r in rows)
    BANK_INDEX.write_text(BANK_HEADER + body, encoding="utf-8")


def bank_rows() -> list[dict]:
    """The bank's rows: {file, name, folder, state, what}."""
    return _rows()


def set_row(file: str, name: str = "", folder: str = "", state: str = "", what: str = "") -> None:
    """Fill in (or add) one bank row, as the labeling UI does. `python -m sxs label` files it later."""
    clean = {k: v.replace("|", "/").replace("\n", " ").strip()
             for k, v in dict(name=name, folder=folder, state=state, what=what).items()}
    rows = _rows()
    for r in rows:
        if r["file"] == file:
            r.update(clean)
            break
    else:
        rows.append(dict(clean, file=file))
    _write_rows(rows)


def bank(save_png, source: Path = UNKNOWN_FRAMES) -> list[str]:
    """Copy each frame in captures/unknown/ that isn't banked yet into unlabeled/ (as a small reference PNG via
    `save_png(img, path)`), and add an empty row for it. Returns the new file names."""
    import cv2

    rows = _rows()
    have = {r["file"] for r in rows} | {p.name for p in UNLABELED.glob("*.png")}
    new = []
    for src in sorted(source.glob("*.png")) if source.exists() else []:
        name = re.sub(r"[^a-z0-9_]+", "_", src.stem.lower()).strip("_") + ".png"
        if name in have:
            continue
        img = cv2.imread(str(src))
        if img is None:
            continue
        save_png(img, UNLABELED / name)
        rows.append({"file": name, "name": "", "folder": "", "state": "", "what": ""})
        have.add(name)
        new.append(name)
    # Frames dropped into unlabeled/ by hand get a row too.
    for p in sorted(UNLABELED.glob("*.png")):
        if p.name not in {r["file"] for r in rows}:
            rows.append({"file": p.name, "name": "", "folder": "", "state": "", "what": ""})
            new.append(p.name)
    _write_rows(rows)
    return new


def label() -> tuple[list[str], list[str]]:
    """File every bank row that has a State. Returns (filed, problems); a row with a problem stays in the bank."""
    rows, keep, filed, problems = _rows(), [], [], []
    expected = load_expected()
    for r in rows:
        if not r["state"]:
            keep.append(r)
            continue
        src = UNLABELED / r["file"]
        name = r["name"].strip("`") or Path(r["file"]).stem
        folder = r["folder"].strip("`/") or folder_for(name)
        if not src.exists():
            problems.append(f"{r['file']}: file not in unlabeled/")
        elif not NAME.match(name):
            problems.append(f"{r['file']}: name {name!r} must be lower case letters, digits and _")
        elif folder in SPECIAL or not re.match(r"^[a-z]+$", folder):
            problems.append(f"{r['file']}: no folder for {name!r}; fill in Folder")
        elif find(name):
            problems.append(f"{r['file']}: a screen named {name} already exists ({find(name).relative_to(SCREENS)})")
        else:
            dest = SCREENS / folder / f"{name}.png"
            dest.parent.mkdir(exist_ok=True)
            shutil.move(str(src), dest)
            labels.rename(f"unlabeled/{r['file']}", f"{folder}/{name}.png")  # boxes drawn in the labeler follow
            if r["state"] != "-":
                expected["states"][name] = r["state"]
            if r["what"]:
                expected["notes"][name] = r["what"]
            filed.append(f"{r['file']} -> {dest.relative_to(SCREENS)} ({r['state']})")
            continue
        keep.append(r)
    save_expected(expected)
    _write_rows(keep)
    return filed, problems
