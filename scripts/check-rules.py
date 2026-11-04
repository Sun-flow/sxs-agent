"""Check the game rules in memory-bank/game/rules/: every rule ID is defined once, every ID cited anywhere in the
repo resolves (to a live rule, or to a retired ID listed in the index), every rules file is in the index, and
every image or path named in a rule exists.

Usage: python3 scripts/check-rules.py   (exits 1 if anything needs fixing)
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES = ROOT / "memory-bank" / "game" / "rules"
INDEX = RULES / "README.md"
SCREENS = ROOT / "docs" / "screens"

RULE_HEADING = re.compile(r"^### (R-\d{3}) · ", re.MULTILINE)
RULE_REF = re.compile(r"\bR-(\d{3})\b")
RETIRED_ROW = re.compile(r"^\|\s*(R-\d{3})\s*\|\s*(R-\d{3})\s*\|", re.MULTILINE)
CODE_SPAN = re.compile(r"`([^`\s]+)`")
FILE_EXT = (".png", ".jpg", ".json", ".py", ".md")
# Where rule IDs are cited outside the rules folder.
CITING = ["sxs", "resource", "scripts", "tests", "docs", "memory-bank"]
SKIP_DIRS = {"archive", "screens", "image", "model"}
CITING_EXT = {".py", ".json", ".md"}
# Runtime outputs (gitignored) and paths a pending PR adds.
RUNTIME = ("logs/", "captures/")
PLANNED = {"explore_bellflower_mae.png"}


def citing_files():
    for top in CITING:
        for f in (ROOT / top).rglob("*"):
            if f.is_file() and f.suffix in CITING_EXT and not SKIP_DIRS & set(f.relative_to(ROOT).parts):
                if RULES not in f.parents and f.name != "log.md":
                    yield f


def main():
    if not INDEX.exists():
        print(f"FAIL  {INDEX.relative_to(ROOT)} is missing")
        return 1
    problems = []
    index = INDEX.read_text(encoding="utf-8")
    defined = {}
    for f in sorted(RULES.glob("*.md")):
        if f == INDEX:
            continue
        if f"`{f.name}`" not in index:
            problems.append(f"rules/{f.name} isn't listed in rules/README.md")
        text = f.read_text(encoding="utf-8")
        for rid in RULE_HEADING.findall(text):
            if rid in defined:
                problems.append(f"{rid} is defined in both rules/{defined[rid]} and rules/{f.name}")
            defined[rid] = f.name
        for token in CODE_SPAN.findall(text):
            if not token.lower().endswith(FILE_EXT) or "*" in token or "<" in token:
                continue
            if token.startswith(RUNTIME) or token in PLANNED:
                continue
            if not any((base / token).exists() for base in (ROOT, SCREENS)):
                problems.append(f"rules/{f.name}: `{token}` doesn't exist")

    retired = dict(RETIRED_ROW.findall(index))
    for old, new in retired.items():
        if old in defined:
            problems.append(f"{old} is listed as retired but still defined in rules/{defined[old]}")
        if new not in defined:
            problems.append(f"retired {old} points to {new}, which isn't defined")
    for rid, fname in defined.items():
        if not re.search(rf"\b{rid}\b", index):
            problems.append(f"{rid} (rules/{fname}) is missing from the ID index in rules/README.md")

    sources = [f for f in RULES.glob("*.md") if f != INDEX] + list(citing_files())
    for f in sources:
        text = f.read_text(encoding="utf-8")
        for n in sorted(set(RULE_REF.findall(text))):
            rid = f"R-{n}"
            if rid == "R-000" or rid in defined:
                continue
            where = f.relative_to(ROOT)
            if rid in retired:
                problems.append(f"{where}: cites retired {rid}; use {retired[rid]}")
            elif not re.search(rf"next free\D*{rid}", index):
                problems.append(f"{where}: cites {rid}, which isn't a rule")

    for p in problems:
        print(f"FAIL  {p}")
    print(f"{'OK' if not problems else f'{len(problems)} problem(s)'}: {len(defined)} rules, {len(retired)} retired IDs")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
