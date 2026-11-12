"""Memory bank tool: check it, add entries, print indexes, confirm work landed, assign IDs.

One file, Python 3.8+ standard library only. Copy it to `scripts/bank.py` in any repo that follows
`.agents/prompts/memory-bank.md` (v2). Everything repo-specific is in CONFIG below or in an optional
`memory-bank/bank.json` that overrides it key by key.

    python3 scripts/bank.py                       # = check: fail on problems, warn on stale items, show newest log
    python3 scripts/bank.py check --quiet         # problems only (for tests and hooks)
    python3 scripts/bank.py new log "Title"       # new entry file in log/ (also: decisions, work, stuck, questions, inbox)
    python3 scripts/bank.py log [-n 5]            # newest log entries, newest first
    python3 scripts/bank.py index docs            # | File | Read when | from each file's <!-- index: ... --> line
    python3 scripts/bank.py index stuck           # ledger sorted by `seen:` count, highest first
    python3 scripts/bank.py landed                # merged work with commits missing from the default branch
    python3 scripts/bank.py ids [--assign]        # provisional IDs (R-new-slug) and the numbers they would get
    python3 scripts/bank.py seen stuck SLUG       # bump a ledger item's count and add today's date

Exit code: 0 clean (warnings allowed), 1 problems found.

Design rules this tool enforces (from a retrospective of a repo with many parallel agent threads):
- Anything appended per session is its own file. Indexes are printed, never committed.
- No stored "next free ID": branches use provisional IDs; `ids --assign` numbers them on the default branch.
- Budgets are lines AND bytes, and lines have a maximum length.
- Status items and ledger entries are dated so stale ones can be listed.
- Retired terms (scrapped features, retired IDs) are flagged wherever they are still mentioned.
- Work only counts as done when its commits are on the default branch.
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BANK = ROOT / "memory-bank"

CONFIG = {
    "default_branch": "main",
    "remote": "origin",
    # Singleton files: [max lines, max bytes]. Any other *.md directly in memory-bank/ is a problem unless listed.
    "singletons": {
        "README.md": [120, 8000],
        "context.md": [100, 6000],
        "status.md": [60, 6000],
        "notes.md": [100, 8000],
    },
    # Entry folders: one file per entry, named YYYY-MM-DD-HHMM-slug.md (log, decisions, inbox) or slug.md (others).
    "entry_folders": {
        "log": {"dated": True, "max_lines": 15},
        "decisions": {"dated": True, "max_lines": 30},
        "inbox": {"dated": True, "max_lines": 15},
        "work": {"dated": False, "max_lines": 20},
        "stuck": {"dated": False, "max_lines": 25},
        "questions": {"dated": False, "max_lines": 15},
    },
    "max_line_chars": 300,
    "stale_days": 7,
    # Files whose bullets must carry a (YYYY-MM-DD) date; undated or old bullets are listed as warnings.
    "dated_bullets": ["status.md"],
    # One term per line; mentions outside these paths are problems.
    "retired_file": "memory-bank/retired.txt",
    "retired_allowed_in": ["docs/archive/", "memory-bank/retired.txt", "memory-bank/decisions/", "memory-bank/log/"],
    # Provisional IDs look like R-new-some-slug. Real IDs look like R-123. Prefixes listed here are managed.
    "id_prefixes": ["R"],
    "id_digits": 3,
    # Where IDs are defined (a heading like "### R-123 · Title") and where they may be cited.
    "id_definitions": ["memory-bank/**/*.md"],
    "id_citations": ["**/*.md", "**/*.py", "**/*.json"],
    # Folders `index` can print, from a `<!-- index: ... -->` line in each .md (or README.md of a subfolder).
    "index_folders": ["docs"],
    # Text checked for broken paths (backticked names that should exist).
    "path_scan": ["AGENTS.md", "CLAUDE.md", "memory-bank/**/*.md"],
    # Text checked for retired terms.
    "scan": ["AGENTS.md", "CLAUDE.md", "memory-bank/**/*.md", "docs/**/*.md"],
    "path_extensions": [".md", ".py", ".js", ".ts", ".json", ".yml", ".yaml", ".toml", ".png", ".sh", ".txt"],
    # Paths named on purpose before they exist (runtime output, planned files).
    "planned_paths": [],
    # Extra folders a backticked path may be relative to (besides the repo root, memory-bank/ and the file's folder).
    "path_bases": [],
    "log_show": 3,
    # Git checks look back this far: PRs merged without a log entry, branches with unlanded commits.
    "recent_days": 7,
}

TEMPLATES = {
    "log": "# {stamp} · {title}\n\n- What changed (PR or commit):\n- Where it ran:\n- Open:\n",
    "decisions": ("# {stamp} · {title}\n\n- **Decision**:\n- **Why**:\n- **Rejected**:\n"
                  "- **Status**: Accepted\n"),
    "inbox": ("# {stamp} · {title}\n\n- **Said by / when**:\n- **Exact words**:\n- **Situation**:\n"
              "- **Filed as**: (rule ID once filed; then delete this file)\n"),
    "work": "# {title}\n\nBranch: `{branch}` · PR: none yet · Where: \n\n- Started {today}.\n",
    "stuck": ("# {title}\n\nseen: 1 · first: {today} · last: {today} · status: open · owner: \n\n"
              "- What happens:\n- Where (loop, screen, place):\n- Dates seen: {today}\n"),
    "questions": "# {title}\n\nasked: {today} · for: \n\n- Question:\n- Options:\n- Answer:\n",
}

DATE = re.compile(r"\b(20\d\d-\d\d-\d\d)\b")
CODE_SPAN = re.compile(r"`([^`\s]+)`")
INDEX_LINE = re.compile(r"<!--\s*index:\s*(.*?)\s*-->", re.S)
DATED_NAME = re.compile(r"^(\d{4}-\d\d-\d\d)-(\d{4})-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
SLUG_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
SEEN = re.compile(r"^seen:\s*(\d+)", re.M)
BRANCH_LINE = re.compile(r"Branch:\s*`([^`]+)`")
PR_MERGE = re.compile(r"Merge pull request #(\d+) from [^/\s]+/(\S+)")


# ---------------------------------------------------------------- helpers

def load_config():
    cfg = dict(CONFIG)
    override = BANK / "bank.json"
    if override.exists():
        cfg.update(json.loads(override.read_text(encoding="utf-8")))
    return cfg


def git(*args):
    try:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def rel(path):
    return path.relative_to(ROOT).as_posix()


def files(globs):
    seen = {Path(__file__).resolve()}  # never scan or rewrite this tool (its docs show example IDs)
    for g in globs:
        for p in ROOT.glob(g):
            if p.is_file() and ".git" not in p.parts and p.resolve() not in seen:
                seen.add(p.resolve())
                yield p


def read(path):
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return ""


def slugify(title, words=6):
    return "-".join(re.findall(r"[a-z0-9]+", title.lower())[:words]) or "entry"


def current_branch():
    return git("rev-parse", "--abbrev-ref", "HEAD") or ""


def entries(cfg, kind):
    folder = BANK / kind
    if not folder.exists():
        return []
    return sorted(f for f in folder.glob("*.md") if f.name != "README.md")


def title_of(path):
    first = read(path).split("\n", 1)[0]
    return re.sub(r"^#\s*", "", first).strip()


# ---------------------------------------------------------------- check

def check(cfg, quiet=False):
    problems, warnings = [], []
    today = date.today()
    stale = today - timedelta(days=cfg["stale_days"])
    readme = read(BANK / "README.md")

    # 1. Layout: singletons exist, carry a date, stay in budget; nothing unexpected at the top level.
    for name, (max_lines, max_bytes) in cfg["singletons"].items():
        p = BANK / name
        if not p.exists():
            problems.append(f"memory-bank/{name} is missing")
            continue
        text = read(p)
        if name != "README.md" and name not in readme:
            problems.append(f"memory-bank/{name} isn't named in memory-bank/README.md")
        if "Last updated" not in text[:600]:
            problems.append(f"memory-bank/{name}: no 'Last updated' date near the top")
        lines = text.count("\n") + 1
        size = len(text.encode("utf-8"))
        if lines > max_lines:
            problems.append(f"memory-bank/{name}: {lines} lines, budget {max_lines}")
        if size > max_bytes:
            problems.append(f"memory-bank/{name}: {size} bytes, budget {max_bytes} (long lines count too)")
    for p in BANK.glob("*.md"):
        if p.name not in cfg["singletons"]:
            problems.append(f"memory-bank/{p.name}: not a known singleton; make it an entry folder or add it to "
                            f"CONFIG['singletons'] and the README map")
    for kind, spec in cfg["entry_folders"].items():
        folder = BANK / kind
        if not folder.exists():
            continue
        if f"{kind}/" not in readme:
            problems.append(f"memory-bank/{kind}/ isn't named in memory-bank/README.md")
        for f in entries(cfg, kind):
            where = rel(f)
            pattern = DATED_NAME if spec["dated"] else SLUG_NAME
            if not pattern.match(f.name):
                want = "YYYY-MM-DD-HHMM-slug.md" if spec["dated"] else "slug.md (lowercase, hyphens)"
                problems.append(f"{where}: name should be {want}")
            text = read(f)
            if not text.startswith("# "):
                problems.append(f"{where}: first line should be a '# ' title")
            n = text.count("\n") + 1
            if n > spec["max_lines"]:
                problems.append(f"{where}: {n} lines, budget {spec['max_lines']}")

    # 2. Line length: a problem in singletons (budgets would be meaningless), a warning in entry files.
    long_lines = [(BANK / n, problems) for n in cfg["singletons"]]
    long_lines += [(f, warnings) for k in cfg["entry_folders"] for f in entries(cfg, k)]
    for p, bucket in long_lines:
        in_code = False
        for i, line in enumerate(read(p).splitlines(), 1):
            if line.startswith("```"):
                in_code = not in_code
            if not in_code and len(line) > cfg["max_line_chars"] and not line.lstrip().startswith("|"):
                bucket.append(f"{rel(p)}:{i}: line is {len(line)} chars (max {cfg['max_line_chars']}); "
                                f"split it or move the detail to its own file")

    # 3. Paths named in backticks exist.
    planned = set(cfg["planned_paths"])
    bases = [ROOT, BANK] + [ROOT / b for b in cfg["path_bases"]]
    exts = tuple(cfg["path_extensions"])
    for p in files(cfg["path_scan"]):
        for token in set(CODE_SPAN.findall(read(p))):
            t = token.split("#")[0].rstrip(":,.")
            if t.startswith(("http", "@", "-", "~", "$")) or "*" in t or "..." in t or "<" in t:
                continue
            if not (t.endswith("/") or t.lower().endswith(exts)) or t in planned:
                continue
            if not any((base / t).exists() for base in bases + [p.parent]):
                problems.append(f"{rel(p)}: names `{t}`, which doesn't exist")

    # 4. Dated bullets: undated or older than stale_days are listed for re-checking.
    for name in cfg["dated_bullets"]:
        p = BANK / name
        for i, line in enumerate(read(p).splitlines(), 1):
            if not re.match(r"^\s*(?:[-*]|\d+\.)\s", line):
                continue
            dates = DATE.findall(line)
            label = line.strip()[:90]
            if not dates:
                warnings.append(f"memory-bank/{name}:{i}: undated item: {label}")
            elif max(dates) < stale.isoformat():
                warnings.append(f"memory-bank/{name}:{i}: last dated {max(dates)}, re-verify or close: {label}")

    # 5. Retired terms.
    retired_path = ROOT / cfg["retired_file"]
    if retired_path.exists():
        terms = [t.strip() for t in read(retired_path).splitlines() if t.strip() and not t.startswith("#")]
        for p in files(cfg["scan"]):
            r = rel(p)
            if any(r.startswith(a) for a in cfg["retired_allowed_in"]):
                continue
            text = read(p)
            for term in terms:
                for i, line in enumerate(text.splitlines(), 1):
                    if re.search(rf"(?<![\w-]){re.escape(term)}(?![\w-])", line) and "retired" not in line.lower():
                        problems.append(f"{r}:{i}: mentions retired '{term}'")

    # 6. IDs: duplicates are problems; provisional IDs are problems on the default branch.
    defs, provisional = id_scan(cfg)
    for full, places in defs.items():
        if len(places) > 1:
            problems.append(f"{full} is defined {len(places)} times: {', '.join(places)}")
    if provisional:
        msg = f"{len(provisional)} provisional ID(s) ({', '.join(sorted(provisional)[:5])}...)"
        if current_branch() == cfg["default_branch"]:
            problems.append(msg + ": run `bank.py ids --assign` and commit")
        else:
            warnings.append(msg + ": fine on a branch; numbered on the default branch after merge")

    # 7. Git-aware: work that merged, PRs no log entry mentions, commits that didn't land.
    w, p2 = git_checks(cfg)
    warnings += w
    problems += p2

    for line in problems:
        print("PROBLEM:", line)
    for line in warnings:
        print("warning:", line)
    if not problems:
        print(f"OK: memory bank checked ({len(warnings)} warning(s))")
    if not quiet:
        print()
        show_log(cfg, cfg["log_show"])
    return 1 if problems else 0


def git_checks(cfg):
    warnings, problems = [], []
    main = f"{cfg['remote']}/{cfg['default_branch']}"
    if git("rev-parse", "--verify", "--quiet", main) is None:
        return [f"no {main} ref; run `git fetch` for the landing and PR checks"], []

    # Work files whose branch has merged into the default branch should be deleted.
    merged_branches = {}
    for line in (git("log", main, "--merges", "--format=%s", f"--since={cfg['recent_days'] * 4} days ago") or "").splitlines():
        m = PR_MERGE.search(line)
        if m:
            merged_branches.setdefault(m.group(2), m.group(1))
    for f in entries(cfg, "work"):
        m = BRANCH_LINE.search(read(f))
        if m and m.group(1) in merged_branches:
            warnings.append(f"{rel(f)}: branch {m.group(1)} merged in #{merged_branches[m.group(1)]}; "
                            f"delete this file if the work is finished")

    # Merged PRs that no log entry mentions.
    since = (date.today() - timedelta(days=cfg["recent_days"])).isoformat()
    logged = " ".join(read(f) for f in entries(cfg, "log"))
    for line in (git("log", main, "--merges", "--format=%s", f"--since={since}") or "").splitlines():
        m = PR_MERGE.search(line)
        if m and not re.search(rf"#{m.group(1)}\b", logged) and m.group(2).split("/")[-1] not in logged:
            warnings.append(f"PR #{m.group(1)} ({m.group(2)}) merged but no log entry mentions it or its branch")

    hard, soft = landed(cfg, print_out=False)
    return warnings + soft, problems + hard


def landed(cfg, print_out=True):
    """Two failure shapes: a PR merged into a branch that isn't the default (so it never lands), and a branch whose
    PR merged into the default branch but which got more commits afterwards that were never merged."""
    remote, main_name = cfg["remote"], cfg["default_branch"]
    main = f"{remote}/{main_name}"
    hard, soft = [], []
    since = (date.today() - timedelta(days=cfg["recent_days"])).isoformat()
    refs = (git("for-each-ref", "--format=%(refname:short) %(committerdate:short)",
                f"refs/remotes/{remote}/") or "").splitlines()
    # Only branches with a commit in the window: old abandoned branches are history, not news.
    refs = [r.split()[0] for r in refs if len(r.split()) == 2 and r.split()[1] >= since]
    merged_into_main = {}
    for line in (git("log", main, "--merges", "--format=%s") or "").splitlines():
        m = PR_MERGE.search(line)
        if m:
            merged_into_main.setdefault(m.group(2), m.group(1))
    for ref in refs:
        if ref in (main, f"{remote}/HEAD") or ref == remote:
            continue
        branch = ref[len(remote) + 1:]
        # PR merges that live on this branch but not on main.
        for line in (git("log", f"{main}..{ref}", "--merges", "--format=%h %s", f"--since={since}") or "").splitlines():
            m = PR_MERGE.search(line)
            if m and m.group(2) != branch:
                hard.append(f"PR #{m.group(1)} ({m.group(2)}) was merged into {branch}, not {main_name}: "
                           f"its code is not on {main_name} until {branch} merges")
        # Commits added after this branch's PR merged.
        if branch in merged_into_main:
            extra = (git("log", "--no-merges", "--format=%h %s", f"{main}..{ref}") or "").splitlines()
            if extra:
                soft.append(f"{branch}: PR #{merged_into_main[branch]} merged, but {len(extra)} later commit(s) are "
                            f"not on {main_name} (newest: {extra[0][:60]}); fine only if an open PR carries them")
    if print_out:
        for line in hard:
            print("PROBLEM:", line)
        for line in soft:
            print("warning:", line)
        if not hard and not soft:
            print(f"OK: every recently merged branch's commits are on {main_name}")
    return hard, soft


# ---------------------------------------------------------------- IDs

def id_scan(cfg):
    defs, provisional = {}, set()
    for prefix in cfg["id_prefixes"]:
        head = re.compile(rf"^#+\s+({re.escape(prefix)}-\d+)\b", re.M)
        prov = re.compile(rf"\b{re.escape(prefix)}-new-[a-z0-9]+(?:-[a-z0-9]+)*\b")
        for p in files(cfg["id_definitions"]):
            for full in head.findall(read(p)):
                defs.setdefault(full, []).append(rel(p))
        for p in files(cfg["id_citations"]):
            provisional.update(prov.findall(read(p)))
    return defs, provisional


def ids(cfg, assign=False):
    defs, provisional = id_scan(cfg)
    if not provisional:
        print("No provisional IDs.")
        return 0
    if assign and current_branch() != cfg["default_branch"]:
        print(f"Refusing to assign on '{current_branch()}': assign on {cfg['default_branch']} after merging, "
              f"so two branches never take the same number.")
        return 1
    plan = {}
    for prefix in cfg["id_prefixes"]:
        used = [int(k.split("-")[1]) for k in defs if k.startswith(prefix + "-")]
        retired = BANK / "retired.txt"
        used += [int(n) for n in re.findall(rf"\b{re.escape(prefix)}-(\d+)\b", read(retired))]
        nxt = max(used, default=0) + 1
        for token in sorted(t for t in provisional if t.startswith(prefix + "-new-")):
            plan[token] = f"{prefix}-{nxt:0{cfg['id_digits']}d}"
            nxt += 1
    for old, new in plan.items():
        print(f"{old} -> {new}")
    if assign:
        changed = 0
        for p in files(cfg["id_citations"]):
            text = read(p)
            new_text = text
            for old, new in plan.items():
                new_text = re.sub(rf"\b{re.escape(old)}\b", new, new_text)
            if new_text != text:
                p.write_text(new_text, encoding="utf-8")
                changed += 1
        print(f"Rewrote {changed} file(s). Commit them as one change.")
    return 0


# ---------------------------------------------------------------- entries, ledgers, indexes

def new_entry(cfg, kind, title):
    spec = cfg["entry_folders"].get(kind)
    if spec is None:
        print(f"Unknown kind '{kind}'; known: {', '.join(cfg['entry_folders'])}")
        return 1
    now = datetime.now(timezone.utc)
    folder = BANK / kind
    folder.mkdir(parents=True, exist_ok=True)
    name = (f"{now:%Y-%m-%d-%H%M}-{slugify(title)}.md" if spec["dated"] else
            f"{slugify(current_branch().split('/')[-1]) if kind == 'work' else slugify(title)}.md")
    path = folder / name
    if path.exists():
        print(f"{rel(path)} already exists; edit it (or bump it with `bank.py seen {kind} {path.stem}`).")
        return 1
    path.write_text(TEMPLATES[kind].format(stamp=f"{now:%Y-%m-%d %H:%M}", title=title, today=now.date(),
                                           branch=current_branch()), encoding="utf-8")
    print(rel(path))
    return 0


def seen(cfg, kind, slug):
    path = BANK / kind / f"{slug}.md"
    text = read(path)
    m = SEEN.search(text)
    if not m:
        print(f"{rel(path)} has no 'seen:' line")
        return 1
    today = date.today().isoformat()
    text = SEEN.sub(f"seen: {int(m.group(1)) + 1}", text, count=1)
    text = re.sub(r"last: \S+", f"last: {today}", text, count=1)
    text = re.sub(r"(- Dates seen: .*)", rf"\1, {today}", text, count=1)
    path.write_text(text, encoding="utf-8")
    print(f"{rel(path)}: seen {int(m.group(1)) + 1}")
    return 0


def show_log(cfg, n):
    items = entries(cfg, "log")[-n:][::-1]
    if not items:
        print("(no log entries)")
    for f in items:
        print(read(f).rstrip(), "\n")
    return 0


def index(cfg, what):
    if what in cfg["entry_folders"]:
        items = entries(cfg, what)
        if what == "stuck":
            items.sort(key=lambda f: -int((SEEN.search(read(f)) or [0, 0])[1]))
            print("| Seen | Stuck point | Status |\n|---|---|---|")
            for f in items:
                t = read(f)
                status = re.search(r"status:\s*([^·\n]+)", t)
                print(f"| {(SEEN.search(t) or [0, '?'])[1]} | {title_of(f)} (`{f.stem}`) | "
                      f"{status.group(1).strip() if status else '?'} |")
        else:
            for f in (items[::-1] if cfg["entry_folders"][what]["dated"] else items):
                b = BRANCH_LINE.search(read(f))
                print(f"- {title_of(f)}" + (f" — `{b.group(1)}`" if b else ""))
        return 0
    folder = ROOT / what
    if not folder.is_dir():
        print(f"No folder or entry kind '{what}'")
        return 1
    print("| File | Read when |\n|---|---|")
    missing = []
    for p in sorted(folder.glob("*.md")) + sorted(folder.glob("*/README.md")):
        if p == folder / "README.md":
            continue
        m = INDEX_LINE.search(read(p))
        name = p.parent.name + "/" if p.name == "README.md" else p.name
        if m:
            print(f"| `{name}` | {m.group(1)} |")
        else:
            missing.append(name)
    for name in missing:
        print(f"PROBLEM: {what}/{name} has no <!-- index: ... --> line", file=sys.stderr)
    return 1 if missing else 0


# ---------------------------------------------------------------- main

def main():
    cfg = load_config()
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd")
    c = sub.add_parser("check")
    c.add_argument("--quiet", action="store_true")
    n = sub.add_parser("new")
    n.add_argument("kind")
    n.add_argument("title")
    lg = sub.add_parser("log")
    lg.add_argument("-n", type=int, default=cfg["log_show"])
    ix = sub.add_parser("index")
    ix.add_argument("what")
    sub.add_parser("landed")
    i = sub.add_parser("ids")
    i.add_argument("--assign", action="store_true")
    s = sub.add_parser("seen")
    s.add_argument("kind")
    s.add_argument("slug")
    a = ap.parse_args()
    if a.cmd in (None, "check"):
        return check(cfg, quiet=getattr(a, "quiet", False))
    if a.cmd == "new":
        return new_entry(cfg, a.kind, a.title)
    if a.cmd == "log":
        return show_log(cfg, a.n)
    if a.cmd == "index":
        return index(cfg, a.what)
    if a.cmd == "landed":
        return 1 if landed(cfg)[0] else 0
    if a.cmd == "ids":
        return ids(cfg, a.assign)
    if a.cmd == "seen":
        return seen(cfg, a.kind, a.slug)
    return 0


if __name__ == "__main__":
    sys.exit(main())
