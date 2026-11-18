"""Check the knowledge base in knowledge/: python3 scripts/kb_check.py [--index] [--terms]

Fails (exit 1) on:
- a markdown page without a `# Title` or without the `<!-- index: ... -->` line under it
- a relative markdown link whose target file (or `#heading` anchor) doesn't exist
- a source tag `[S-NN]` that knowledge/sources/README.md doesn't define, or a rule ID `R-NNN` that isn't a live rule
- a data/*.json file that doesn't parse, lacks `_meta`, or has a record without `id` or with a repeated `id`

    --index    print the page index (| Page | Read when |) built from the index lines, grouped by folder
    --terms    print every glossary term with the page it links to

Standard library only, no network.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KB = ROOT / "knowledge"
RULES = ROOT / "memory-bank" / "game" / "rules"
INDEX = re.compile(r"<!--\s*index:\s*(.+?)\s*-->")
LINK = re.compile(r"(?<!\!)\[[^\]\n]*\]\(([^)\s]+)\)")
TAG = re.compile(r"\bS-\d{2,3}\b")
RULE = re.compile(r"\bR-\d{3}\b")
FENCE = re.compile(r"```.*?```", re.S)


def pages() -> list[Path]:
    return sorted(p for p in KB.rglob("*.md") if "raw" not in p.relative_to(KB).parts)


def anchor(heading: str) -> str:
    """GitHub's heading anchor: lowercase, punctuation dropped, spaces to hyphens."""
    h = re.sub(r"[`*_\[\]()]", "", heading.strip().lower())
    h = re.sub(r"[^\w\- ]", "", h)
    return h.replace(" ", "-")


def anchors(path: Path) -> set[str]:
    out: set[str] = set()
    for line in FENCE.sub("", path.read_text(encoding="utf-8")).splitlines():
        m = re.match(r"#{1,6}\s+(.*)", line)
        if m:
            a = anchor(m.group(1))
            n = 0
            while (a if not n else f"{a}-{n}") in out:
                n += 1
            out.add(a if not n else f"{a}-{n}")
    return out


def index_line(path: Path) -> str | None:
    m = INDEX.search(path.read_text(encoding="utf-8")[:1500])
    return m.group(1) if m else None


def defined_tags() -> set[str]:
    reg = KB / "sources" / "README.md"
    if not reg.is_file():
        return set()
    return set(re.findall(r"^\|\s*(S-\d{2,3})\s*\|", reg.read_text(encoding="utf-8"), re.M))


def live_rules() -> set[str]:
    out: set[str] = set()
    for p in RULES.glob("*.md"):
        out |= set(re.findall(r"^### (R-\d{3})\b", p.read_text(encoding="utf-8"), re.M))
    return out


def check() -> list[str]:
    problems: list[str] = []
    tags, rules = defined_tags(), live_rules()
    cache: dict[Path, set[str]] = {}
    for p in pages():
        rel = p.relative_to(ROOT)
        text = p.read_text(encoding="utf-8")
        if not re.match(r"# \S", text):
            problems.append(f"{rel}: first line is not a '# Title'")
        if index_line(p) is None:
            problems.append(f"{rel}: no <!-- index: ... --> line under the title")
        body = FENCE.sub("", text)
        for target in sorted(set(LINK.findall(body))):
            if re.match(r"[a-z][a-z0-9+.-]*:", target):  # http:, https:, mailto:
                continue
            file, _, frag = target.partition("#")
            dest = (p.parent / file).resolve() if file else p
            if not dest.exists():
                problems.append(f"{rel}: link to {target} (no such file)")
            elif frag and dest.suffix == ".md":
                if frag not in cache.setdefault(dest, anchors(dest)):
                    problems.append(f"{rel}: link to {target} (no such heading)")
        if p.name != "CONVENTIONS.md":
            for t in sorted(set(TAG.findall(body)) - tags):
                problems.append(f"{rel}: source tag {t} is not defined in knowledge/sources/README.md")
            for r in sorted(set(RULE.findall(body)) - rules):
                problems.append(f"{rel}: {r} is not a live rule in memory-bank/game/rules/")
    for p in sorted((KB / "data").glob("*.json")):
        rel = p.relative_to(ROOT)
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except ValueError as e:
            problems.append(f"{rel}: does not parse ({e})")
            continue
        if not isinstance(d, dict) or "_meta" not in d:
            problems.append(f"{rel}: needs a top-level object with _meta")
            continue
        for key, val in d.items():
            if key == "_meta" or not isinstance(val, list):
                continue
            seen: set[str] = set()
            for i, rec in enumerate(val):
                if not isinstance(rec, dict):
                    continue
                rid = rec.get("id")
                if not rid:
                    problems.append(f"{rel}: {key}[{i}] has no id")
                elif rid in seen:
                    problems.append(f"{rel}: {key} repeats id {rid}")
                seen.add(rid or "")
    return problems


def print_index() -> None:
    folder = None
    for p in sorted(pages(), key=lambda q: (len(q.relative_to(KB).parts) > 1, str(q.relative_to(KB)))):
        rel = p.relative_to(KB)
        f = str(rel.parent) if len(rel.parts) > 1 else "."
        if f != folder:
            folder = f
            print(f"\n## {'knowledge/' if f == '.' else 'knowledge/' + f + '/'}\n\n| Page | Read when |\n|---|---|")
        print(f"| `{rel}` | {index_line(p) or '(no index line)'} |")


def print_terms() -> None:
    g = KB / "glossary.md"
    if not g.is_file():
        print("no glossary yet")
        return
    for m in re.finditer(r"^\| \*\*(.+?)\*\* \|.*?\]\(([^)]+)\)", g.read_text(encoding="utf-8"), re.M):
        print(f"{m.group(1)} -> {m.group(2)}")


def main() -> int:
    if "--index" in sys.argv:
        print_index()
        return 0
    if "--terms" in sys.argv:
        print_terms()
        return 0
    problems = check()
    if problems:
        print("\n".join(problems))
        print(f"\n{len(problems)} problem(s)")
        return 1
    n_json = len(list((KB / "data").glob("*.json")))
    print(f"knowledge ok: {len(pages())} pages, {n_json} data files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
