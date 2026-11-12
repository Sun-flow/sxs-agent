"""Read and add memory-bank entries that live one per file, so branches never edit the same lines.

Kinds: `log` (memory-bank/log/, session handoffs) and `decisions` (memory-bank/decisions/, decisions with lasting
consequences). Each entry is its own file named `YYYY-MM-DD-HHMM-slug.md` (UTC), whose first line is
`# YYYY-MM-DD HH:MM · Title`. Files sort by name, so the newest is last on disk and first in every view.

Usage:
    python3 scripts/entries.py log                   # the newest 3 session entries, newest first
    python3 scripts/entries.py log -n 10             # the newest 10
    python3 scripts/entries.py decisions --titles    # one line per decision, newest first
    python3 scripts/entries.py decisions --grep rank # entries that mention a word (case-insensitive)
    python3 scripts/entries.py log --all             # every entry (older log history: docs/archive/memory-bank-log.md)
    python3 scripts/entries.py new log "Portals: teleport rule built (Claude Code, cloud)"
    python3 scripts/entries.py check                 # file names and headings (also run by check-memory.py)

`new` writes the file with the current UTC time and prints its path; fill in the bullets and commit it with the work.
Never edit another session's entry to add news: write a new one. Correcting a mistake in an entry is fine.
"""

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BANK = ROOT / "memory-bank"
KINDS = {"log": BANK / "log", "decisions": BANK / "decisions"}
ARCHIVE = {"log": "docs/archive/memory-bank-log.md"}

NAME = re.compile(r"^(\d{4}-\d\d-\d\d)-(\d{4})-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
HEADING = re.compile(r"^# (\d{4}-\d\d-\d\d)(?: (\d\d):(\d\d))? · \S")

TEMPLATES = {
    "log": "- What changed (link the PR or commit):\n- Where it ran:\n- Open:\n",
    "decisions": ("- **Decision**: one line\n- **Rationale**: why\n"
                  "- **Alternatives considered**: what we didn't pick and why\n"
                  "- **Status**: Accepted / Superseded by [title]\n"),
}


def entry_files(kind):
    folder = KINDS[kind]
    return sorted(f for f in folder.glob("*.md") if f.name != "README.md") if folder.exists() else []


def problems():
    found = []
    for kind, folder in KINDS.items():
        if not folder.exists():
            found.append(f"memory-bank/{folder.name}/ is missing")
            continue
        for f in entry_files(kind):
            where = f"memory-bank/{folder.name}/{f.name}"
            m = NAME.match(f.name)
            if not m:
                found.append(f"{where}: name should be YYYY-MM-DD-HHMM-slug.md (lowercase slug)")
                continue
            first = f.read_text(encoding="utf-8").split("\n", 1)[0]
            h = HEADING.match(first)
            if not h:
                found.append(f"{where}: first line should be '# YYYY-MM-DD HH:MM · Title'")
                continue
            if h.group(1) != m.group(1):
                found.append(f"{where}: heading date {h.group(1)} doesn't match the file name")
            if h.group(2) and h.group(2) + h.group(3) != m.group(2):
                found.append(f"{where}: heading time {h.group(2)}:{h.group(3)} doesn't match the file name")
    return found


def slugify(title, words=6):
    title = re.sub(r"\s*\([^)]*\)\s*$", "", title)  # drop a trailing "(Claude Code, cloud)"
    return "-".join(re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-").split("-")[:words]) or "entry"


def new(kind, title):
    now = datetime.now(timezone.utc)
    folder = KINDS[kind]
    folder.mkdir(exist_ok=True)
    path = folder / f"{now:%Y-%m-%d-%H%M}-{slugify(title)}.md"
    if path.exists():
        print(f"{path.relative_to(ROOT)} already exists; pick another title", file=sys.stderr)
        return 1
    path.write_text(f"# {now:%Y-%m-%d %H:%M} · {title}\n\n{TEMPLATES[kind]}", encoding="utf-8")
    print(path.relative_to(ROOT))
    return 0


def show(kind, count, titles, grep):
    files = list(reversed(entry_files(kind)))
    if grep:
        files = [f for f in files if grep.lower() in f.read_text(encoding="utf-8").lower()]
    if count is not None:
        files = files[:count]
    for f in files:
        text = f.read_text(encoding="utf-8").strip()
        if titles:
            print(f"{text.split(chr(10), 1)[0][2:]}   ({f.relative_to(ROOT)})")
        else:
            print(f"{text}\n\n({f.relative_to(ROOT)})\n")
    total = len(entry_files(kind))
    if not titles and count is not None and total > len(files) and not grep:
        print(f"... {total - len(files)} older {kind} entries: add -n N or --all")
    if kind in ARCHIVE and (count is None or not files):
        print(f"Older history (frozen, newest first): {ARCHIVE[kind]}")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows consoles
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("kind", choices=[*KINDS, "new", "check"])
    parser.add_argument("args", nargs="*", help="for new: KIND TITLE")
    parser.add_argument("-n", type=int, default=None, help="how many entries (default 3 full, or all titles)")
    parser.add_argument("--all", action="store_true", help="every entry")
    parser.add_argument("--titles", action="store_true", help="one line per entry")
    parser.add_argument("--grep", help="only entries containing this text")
    a = parser.parse_args()
    if a.kind == "check":
        found = problems()
        for p in found:
            print(f"FAIL  {p}")
        print("OK" if not found else f"{len(found)} problem(s)")
        return 1 if found else 0
    if a.kind == "new":
        if len(a.args) != 2 or a.args[0] not in KINDS:
            parser.error('usage: entries.py new log|decisions "Title (who, where)"')
        return new(*a.args)
    count = None if a.all or a.grep else a.n if a.n is not None else (None if a.titles else 3)
    show(a.kind, count, a.titles, a.grep)
    return 0


if __name__ == "__main__":
    sys.exit(main())
