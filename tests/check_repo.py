"""Offline structure check, no emulator and no MaaFramework needed: python3 tests/check_repo.py

- every pipeline and policy JSON file parses
- every template a pipeline names exists under resource/image/
- every State.* node is in State.Detect's order list, and every name in the list is a node
- every `python -m sxs <loop>`, `sxs/.../X.py`, `scripts/X.py` and `tests/X.py` named in docs, memory-bank and module
  docstrings exists (the retired `python -m sxs.X` form is flagged)
- every Python file compiles

Exits 1 and lists the problems if anything fails.
"""

from __future__ import annotations

import json
import py_compile
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
problems: list[str] = []


def templates(node) -> list[str]:
    """Template paths anywhere inside a pipeline node (including Or/And sub-recognitions)."""
    out: list[str] = []
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "template":
                out += [v] if isinstance(v, str) else list(v)
            else:
                out += templates(v)
    elif isinstance(node, list):
        for v in node:
            out += templates(v)
    return out


nodes: dict[str, dict] = {}
for path in sorted((ROOT / "resource" / "pipeline").glob("*.json")):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as e:
        problems.append(f"{path.relative_to(ROOT)}: does not parse ({e})")
        continue
    for name, node in data.items():
        if name in nodes:
            problems.append(f"{path.relative_to(ROOT)}: node {name} defined twice")
        nodes[name] = node
        for t in templates(node):
            if not (ROOT / "resource" / "image" / t).is_file():
                problems.append(f"{path.relative_to(ROOT)}: {name} names missing template image/{t}")

order = nodes.get("State.Detect", {}).get("custom_action_param", {}).get("order", [])
for name in order:
    if name not in nodes:
        problems.append(f"State.Detect order names {name}, which is not a node")
for name in nodes:
    if name.startswith("State.") and name not in ("State.Detect", "State.Unknown") and name not in order:
        problems.append(f"{name} is not in State.Detect's order list (it can never be detected)")

for path in sorted((ROOT / "resource" / "policy").glob("*.json")):
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except ValueError as e:
        problems.append(f"{path.relative_to(ROOT)}: does not parse ({e})")

# Commands: `python -m sxs <name>` must be a registered loop (sxs/loops/__init__.py REGISTRY, read as text so this
# check needs no MaaFramework), a device command in sxs/cli.py or `see`. The old `python -m sxs.<module>` form is gone.
REGISTRY = set(re.findall(r'^\s+"([a-z_]+)": "sxs\.', (ROOT / "sxs" / "loops" / "__init__.py").read_text(), re.M))
CLI_WORDS = {"see", "--help", "-h", "--address", "<loop>", "<name>"}
CLI_WORDS |= set(re.findall(r'"([a-z]+)"', re.search(r"DEVICE_COMMANDS = \(([^)]*)\)",
                                                       (ROOT / "sxs" / "cli.py").read_text()).group(1)))
OLD_REF = re.compile(r"python3? -m sxs\.([a-z_.]+)")
CMD_REF = re.compile(r"python3? -m sxs ([a-z<>_-]+)")
CODE_REF = re.compile(r"\b(sxs/[a-z_/]+\.py)\b")
SCRIPT_REF = re.compile(r"\b((?:scripts|tests)[/\\][a-z][\w-]*\.py)\b")
texts = [p for p in ROOT.glob("*.md")] + list((ROOT / "docs").glob("*.md")) + list((ROOT / "memory-bank").rglob("*.md"))
texts += list((ROOT / "sxs").rglob("*.py")) + list((ROOT / "scripts").glob("*.py")) + list((ROOT / "tests").glob("*.py"))
texts += list((ROOT / "sxs").glob("README.md")) + list((ROOT / "scripts").glob("README.md")) + list((ROOT / "tests").glob("README.md"))
texts += list((ROOT / "resource").rglob("*.md")) + [ROOT / "AGENTS.md"]
for path in sorted(set(texts)):
    if "archive" in path.parts or path.name == "log.md" or path == Path(__file__).resolve():
        continue  # history may name things that are gone
    text = path.read_text(encoding="utf-8", errors="replace")
    for m in sorted(set(OLD_REF.findall(text))):
        problems.append(f"{path.relative_to(ROOT)}: names python -m sxs.{m}; loops now run as python -m sxs <name>")
    for m in sorted(set(CMD_REF.findall(text))):
        if m not in REGISTRY and m not in CLI_WORDS:
            problems.append(f"{path.relative_to(ROOT)}: names python -m sxs {m}, which is not a loop or command")
    for m in sorted(set(CODE_REF.findall(text))):
        if not (ROOT / m).is_file():
            problems.append(f"{path.relative_to(ROOT)}: names {m}, which doesn't exist")
    for m in sorted(set(SCRIPT_REF.findall(text))):
        if not (ROOT / m.replace("\\", "/")).is_file():
            problems.append(f"{path.relative_to(ROOT)}: names {m}, which doesn't exist")

for path in sorted(list((ROOT / "sxs").rglob("*.py")) + list((ROOT / "scripts").glob("*.py")) + list((ROOT / "tests").glob("*.py"))):
    try:
        py_compile.compile(str(path), doraise=True, cfile=str(ROOT / ".maa" / "pycheck.pyc"))
    except py_compile.PyCompileError as e:
        problems.append(f"{path.relative_to(ROOT)}: does not compile ({e.msg})")

if problems:
    print("\n".join(problems))
    sys.exit(1)
print(f"repo ok: {len(nodes)} pipeline nodes, {len(order)} detectable states")
