"""Check the memory bank for drift: broken paths, unmapped files, missing dates, size budgets and
section references (§N) that no longer exist. Also lists commits that changed the repo since the
memory bank was last updated, so a new session knows what to re-check.

Usage: python3 scripts/check-memory.py   (exits 1 if anything needs fixing; stale-memory notes are warnings)
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BANK = ROOT / "memory-bank"
ENTRY_FILES = [ROOT / "AGENTS.md", ROOT / "CLAUDE.md"]

# Line budgets from memory-bank/README.md; log.md is budgeted in entries instead.
LINE_BUDGETS = {"README.md": 120, "context.md": 100, "status.md": 80, "notes.md": 100}
LOG_MAX_ENTRIES = 15

# Where log.md's oldest entries go once it passes LOG_MAX_ENTRIES (created the first time).
LOG_ARCHIVE = "docs/archive/memory-bank-log.md"

# Paths the docs name on purpose before they exist. Remove an entry once the path is real.
PLANNED_PATHS = {
    LOG_ARCHIVE,
}

PATH_EXTENSIONS = (".md", ".py", ".js", ".ts", ".html", ".txt", ".json", ".yml", ".yaml", ".toml", ".png", ".sh", ".css")
CODE_SPAN = re.compile(r"`([^`\s]+)`")
# memory-bank/README.md names the document that bare "§N" references point to, in a line like:
#   Section references (§N) point to `docs/spec.md`.
SECTION_TARGET = re.compile(r"Section references \(§N\) point to `([^`]+)`")
SECTION_REF = re.compile(r"§\s?(\d+)")


def looks_like_path(token):
    if token.startswith(("http", "@", "-")) or "*" in token or "..." in token:
        return False
    return token.endswith("/") or token.lower().endswith(PATH_EXTENSIONS)


def path_exists(token, doc):
    token = token.split("#")[0]
    return any((base / token).exists() for base in (ROOT, BANK, doc.parent))


def section_problems(docs, readme):
    match = SECTION_TARGET.search(readme)
    if not match:
        return []
    target = ROOT / match.group(1)
    if not target.exists():
        return [f"memory-bank/README.md: section references point to `{match.group(1)}`, which doesn't exist"]
    numbers = set(re.findall(r"^#+\s+(\d+)\.", target.read_text(encoding="utf-8"), re.MULTILINE))
    problems = []
    for doc in docs:
        for n in sorted(set(SECTION_REF.findall(doc.read_text(encoding="utf-8"))), key=int):
            if n not in numbers:
                problems.append(f"{doc.relative_to(ROOT)}: §{n} isn't a section of {match.group(1)}")
    return problems


def commits_since_memory():
    """Commits after the last one that touched memory-bank/ which changed files outside it."""
    def git(*args):
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    try:
        last = git("log", "-1", "--format=%H", "--", "memory-bank")
        if not last:
            return []
        return git("log", "--no-merges", "--format=%h %ad %s", "--date=short",
                   f"{last}..HEAD", "--", ".", ":(exclude)memory-bank").splitlines()
    except (OSError, subprocess.CalledProcessError):
        return []  # not a git checkout, or git isn't installed


def main():
    if not (BANK / "README.md").exists():
        print("FAIL  memory-bank/README.md is missing: set up the memory bank first")
        return 1
    problems = []
    bank_files = sorted(BANK.glob("*.md"))

    for doc in ENTRY_FILES + bank_files:
        if not doc.exists():
            problems.append(f"{doc.relative_to(ROOT)} is missing")
            continue
        for token in CODE_SPAN.findall(doc.read_text(encoding="utf-8")):
            if looks_like_path(token) and token not in PLANNED_PATHS and not path_exists(token, doc):
                problems.append(f"{doc.relative_to(ROOT)}: `{token}` doesn't exist")

    readme = (BANK / "README.md").read_text(encoding="utf-8")
    for f in bank_files:
        text = f.read_text(encoding="utf-8")
        if f"| `{f.name}` |" not in readme:
            problems.append(f"memory-bank/{f.name} isn't in the map in memory-bank/README.md")
        if "Last updated" not in text:
            problems.append(f"memory-bank/{f.name} has no 'Last updated' line")
        budget = LINE_BUDGETS.get(f.name)
        lines = len(text.splitlines())
        if budget and lines > budget:
            problems.append(f"memory-bank/{f.name} is {lines} lines (budget {budget}): trim or split it")

    problems += section_problems([d for d in ENTRY_FILES + bank_files if d.exists()], readme)

    log = BANK / "log.md"
    if log.exists():
        entries = sum(1 for line in log.read_text(encoding="utf-8").splitlines() if line.startswith("### "))
        if entries > LOG_MAX_ENTRIES:
            problems.append(f"memory-bank/log.md has {entries} entries (max {LOG_MAX_ENTRIES}): "
                            f"move the oldest to {LOG_ARCHIVE}")

    for p in problems:
        print(f"FAIL  {p}")
    stale = commits_since_memory()
    if stale:
        print(f"WARN  {len(stale)} commit(s) changed the repo after memory-bank/ was last updated. "
              "Check whether the memory still holds, then update it:")
        for line in stale:
            print(f"        {line}")
    print(f"{'OK' if not problems else f'{len(problems)} problem(s)'}: "
          f"checked {len(bank_files)} memory files and {len(ENTRY_FILES)} entry files")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
