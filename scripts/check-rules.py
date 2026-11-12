"""Check the game rules in memory-bank/game/rules/: every rule ID is defined once, every ID cited anywhere in the
repo resolves (to a live rule, or to a retired ID listed in the retired table), every rules file is in the
situation table, and every image or path named in a rule exists.

The ID index is not a file: it is built from the rule headings (`### R-NNN · Title`) whenever it is wanted, so
branches never edit a shared index. `python3 scripts/index.py rules` prints it, `python3 scripts/index.py rules R-130`
prints one rule.

Usage:
    python3 scripts/check-rules.py          (exits 1 if anything needs fixing)
    python3 scripts/check-rules.py --next   the next free rule ID: one past the highest ID on this branch, on main
                                            and on every fetched origin/* branch (run `git fetch` first to see
                                            IDs other open branches have taken)
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES = ROOT / "memory-bank" / "game" / "rules"
INDEX = RULES / "README.md"
SCREENS = ROOT / "docs" / "screens"

RULE_HEADING = re.compile(r"^### (R-\d{3}) · ", re.MULTILINE)
RULE_TITLE = re.compile(r"^### (R-\d{3}) · (.+)$", re.MULTILINE)
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
PLANNED: set[str] = set()


def citing_files():
    for top in CITING:
        for f in (ROOT / top).rglob("*"):
            if f.is_file() and f.suffix in CITING_EXT and not SKIP_DIRS & set(f.relative_to(ROOT).parts):
                if RULES not in f.parents and f.parent != ROOT / "memory-bank" / "log":  # history
                    yield f


def rule_headings():
    """{R-NNN: (file name, title)} for every live rule on disk."""
    rules = {}
    for f in sorted(RULES.glob("*.md")):
        if f == INDEX:
            continue
        for rid, title in RULE_TITLE.findall(f.read_text(encoding="utf-8")):
            rules.setdefault(rid, (f.name, title.strip()))
    return rules


def ids_on_other_branches():
    """Rule IDs defined on any fetched origin/* branch (best effort: empty without git)."""
    try:
        refs = subprocess.run(["git", "for-each-ref", "--format=%(refname)", "refs/remotes/origin"], cwd=ROOT,
                              capture_output=True, text=True, check=True).stdout.split()
        if not refs:
            return set()
        out = subprocess.run(["git", "grep", "-h", "-E", r"^### R-[0-9]{3} ", *refs, "--", "memory-bank/game/rules"],
                             cwd=ROOT, capture_output=True, text=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return set()
    return set(re.findall(r"R-\d{3}", out))


def next_free(rules=None):
    rules = rules if rules is not None else rule_headings()
    index = INDEX.read_text(encoding="utf-8") if INDEX.exists() else ""
    taken = set(rules) | set(dict(RETIRED_ROW.findall(index))) | set(dict(RETIRED_ROW.findall(index)).values())
    taken |= ids_on_other_branches()
    return f"R-{max(int(r[2:]) for r in taken) + 1:03d}" if taken else "R-001"


def main():
    if "--next" in sys.argv[1:]:
        print(next_free())
        return 0
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
    if re.search(r"^## ID index", index, re.MULTILINE):
        problems.append("rules/README.md has a hand-kept ID index: delete it (python3 scripts/index.py rules prints one)")

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
            else:
                problems.append(f"{where}: cites {rid}, which isn't a rule")

    for p in problems:
        print(f"FAIL  {p}")
    print(f"{'OK' if not problems else f'{len(problems)} problem(s)'}: {len(defined)} rules, {len(retired)} retired IDs, next free {next_free()}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
