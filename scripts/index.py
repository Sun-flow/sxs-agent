"""Print a folder's index, built from the files on disk, so no branch ever edits a shared index table.

Each listing reads metadata that lives in the files themselves:

    python3 scripts/index.py docs          # docs/*.md and docs/*/README.md: the `<!-- index: ... -->` line under the title
    python3 scripts/index.py tests         # tests/*.py: the `Needs:` and `Checks:` lines in the module docstring
    python3 scripts/index.py rules         # every rule heading `### R-NNN · Title` in memory-bank/game/rules/, and the next free ID
    python3 scripts/index.py rules R-130   # print one rule (or several IDs)
    python3 scripts/index.py work          # memory-bank/work/*.md: workstreams in progress (title and branch line)
    python3 scripts/index.py check         # every doc and test carries its metadata (also run by tests/check_repo.py)

Add a doc, test or rule by giving the new file its metadata line; never add a row to a README table for it.
"""

import argparse
import ast
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
TESTS = ROOT / "tests"
RULES = ROOT / "memory-bank" / "game" / "rules"
WORK = ROOT / "memory-bank" / "work"

DOC_INDEX = re.compile(r"<!--\s*index:\s*(.*?)\s*-->", re.S)
FIELD = re.compile(r"^(Needs|Checks): (.*(?:\n  .*)*)", re.M)


def load_check_rules():
    spec = importlib.util.spec_from_file_location("check_rules", ROOT / "scripts" / "check-rules.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def doc_entries():
    files = sorted(f for f in DOCS.glob("*.md") if f.name != "README.md")
    files += sorted(d / "README.md" for d in DOCS.iterdir() if d.is_dir() and (d / "README.md").exists())
    for f in files:
        head = "\n".join(f.read_text(encoding="utf-8").split("\n")[:12])
        m = DOC_INDEX.search(head)
        name = f.parent.name + "/" if f.name == "README.md" else f.name
        yield name, (" ".join(m.group(1).split()) if m else None)


def test_entries():
    for f in sorted(TESTS.glob("*.py")):
        doc = ast.get_docstring(ast.parse(f.read_text(encoding="utf-8"))) or ""
        fields = {k: " ".join(v.split()) for k, v in FIELD.findall(doc)}
        yield f.name, fields.get("Needs"), fields.get("Checks")


def work_entries():
    for f in sorted(WORK.glob("*.md")) if WORK.exists() else []:
        lines = [l for l in f.read_text(encoding="utf-8").split("\n") if l.strip()]
        title = lines[0].lstrip("# ") if lines else f.stem
        meta = lines[1] if len(lines) > 1 else ""
        yield f.name, title, meta


def problems():
    found = []
    for name, desc in doc_entries():
        if not desc:
            found.append(f"docs/{name}: no `<!-- index: ... -->` line in its first 12 lines")
    for name, needs, checks in test_entries():
        if not needs or not checks:
            found.append(f"tests/{name}: module docstring needs `Needs:` and `Checks:` lines")
    for name, title, meta in work_entries():
        if "Branch:" not in meta:
            found.append(f"memory-bank/work/{name}: second line should be 'Branch: ... · PR: ... · Where: ...'")
    return found


def show_rules(ids):
    cr = load_check_rules()
    rules = cr.rule_headings()
    if ids:
        for rid in ids:
            if rid not in rules:
                print(f"{rid}: not a live rule (retired IDs: memory-bank/game/rules/README.md)")
                continue
            fname, _ = rules[rid]
            text = (RULES / fname).read_text(encoding="utf-8")
            m = re.search(rf"^### {rid} · .*?(?=^### |^## |\Z)", text, re.M | re.S)
            print(f"[{fname}]\n{m.group(0).strip()}\n")
        return
    print("| ID | File | Title |\n|---|---|---|")
    for rid in sorted(rules):
        fname, title = rules[rid]
        print(f"| {rid} | `{fname}` | {title} |")
    print(f"\nnext free: {cr.next_free(rules)}")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows consoles
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("what", choices=["docs", "tests", "rules", "work", "check"])
    parser.add_argument("ids", nargs="*", help="rules only: R-NNN to print")
    a = parser.parse_args()
    if a.what == "docs":
        print("| File | Read when |\n|---|---|")
        for name, desc in doc_entries():
            print(f"| `{name}` | {desc or '(no index line)'} |")
    elif a.what == "tests":
        print("| File | Needs | Checks |\n|---|---|---|")
        for name, needs, checks in test_entries():
            print(f"| `{name}` | {needs or '?'} | {checks or '?'} |")
        print("\nRun every test whose Needs doesn't say live emulator after any code change; "
              "the live ones after changing navigation.")
    elif a.what == "rules":
        show_rules(a.ids)
    elif a.what == "work":
        entries = list(work_entries())
        for name, title, meta in entries:
            print(f"- {title} ({meta}) -> memory-bank/work/{name}")
        if not entries:
            print("No workstreams in progress.")
    else:
        found = problems()
        for p in found:
            print(f"FAIL  {p}")
        print("OK" if not found else f"{len(found)} problem(s)")
        return 1 if found else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
