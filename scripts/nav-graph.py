"""Check, render and query the game's menu navigation graph (memory-bank/game/nav-graph.json).

Usage:
  python3 scripts/nav-graph.py check           exit 1 if the graph has errors
  python3 scripts/nav-graph.py render          rewrite memory-bank/game/nav-graph.md
  python3 scripts/nav-graph.py path FROM TO    print the shortest action sequence between two screens

Format: memory-bank/game/README.md. Standard library only, so it runs on maes2024 as is.
"""

import json
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GRAPH = ROOT / "memory-bank" / "game" / "nav-graph.json"
RENDERED = ROOT / "memory-bank" / "game" / "nav-graph.md"

KINDS = {"hub", "menu", "popup", "battle", "world", "overlay"}
CONFIDENCE = {"observed", "told", "reported"}
ACTIONS = {"tap", "back", "swipe", "wait", "auto"}
PSEUDO_FROM = {"*"}          # edge works from any screen
PSEUDO_TO = {"previous"}     # edge returns to whatever screen came before


def load():
    return json.loads(GRAPH.read_text(encoding="utf-8"))


def check(graph):
    problems = []
    ids = [n.get("id") for n in graph.get("nodes", [])]
    seen = set()
    for node in graph.get("nodes", []):
        nid = node.get("id")
        if not nid or nid in seen:
            problems.append(f"node id missing or duplicated: {nid!r}")
        seen.add(nid)
        if node.get("kind") not in KINDS:
            problems.append(f"node {nid}: kind {node.get('kind')!r} not in {sorted(KINDS)}")
        if node.get("confidence") not in CONFIDENCE:
            problems.append(f"node {nid}: confidence {node.get('confidence')!r} not in {sorted(CONFIDENCE)}")
        for img in node.get("images", []):
            if not img.startswith("http") and not (ROOT / img).exists():
                problems.append(f"node {nid}: image {img} doesn't exist")
    for i, edge in enumerate(graph.get("edges", [])):
        label = f"edge {i} ({edge.get('from')} -> {edge.get('to')})"
        if edge.get("from") not in seen | PSEUDO_FROM:
            problems.append(f"{label}: unknown from-node")
        if edge.get("to") not in seen | PSEUDO_TO:
            problems.append(f"{label}: unknown to-node")
        action = edge.get("action") or {}
        if action.get("type") not in ACTIONS:
            problems.append(f"{label}: action type {action.get('type')!r} not in {sorted(ACTIONS)}")
        pos = action.get("pos")
        if pos is not None and not (len(pos) == 2 and all(0 <= v <= 1 for v in pos)):
            problems.append(f"{label}: pos must be [x, y] fractions between 0 and 1, or null")
        if edge.get("confidence") not in CONFIDENCE:
            problems.append(f"{label}: confidence {edge.get('confidence')!r} not in {sorted(CONFIDENCE)}")
    reachable = {e["to"] for e in graph.get("edges", [])} | {"home"}
    for nid in ids:
        if nid not in reachable:
            problems.append(f"node {nid}: no edge leads to it yet (warning)")
    return problems


def describe(action):
    where = f" at {action['pos']}" if action.get("pos") else ""
    tmpl = f" [template {action['template']}]" if action.get("template") else ""
    return f"{action['type']} {action.get('target') or ''}{where}{tmpl}".strip()


def shortest_path(graph, start, goal):
    """BFS over concrete edges; '*' edges apply everywhere, 'previous' edges are skipped (no history)."""
    edges = [e for e in graph["edges"] if e["to"] not in PSEUDO_TO]
    queue, came = deque([start]), {start: None}
    while queue:
        cur = queue.popleft()
        if cur == goal:
            steps = []
            while came[cur]:
                prev, edge = came[cur]
                steps.append(edge)
                cur = prev
            return list(reversed(steps))
        for e in edges:
            if e["from"] in (cur, "*") and e["to"] not in came:
                came[e["to"]] = (cur, e)
                queue.append(e["to"])
    return None


def render(graph):
    names = {n["id"]: n["name"] for n in graph["nodes"]}
    out = [
        "# Navigation graph",
        "",
        f"> **Last updated**: {graph.get('updated', '?')}",
        "> Generated from `memory-bank/game/nav-graph.json` by `python3 scripts/nav-graph.py render`. Don't edit by hand.",
        "",
        "Solid arrows are observed in game; dashed arrows are told or reported and still need confirming.",
        "",
        "```mermaid",
        "flowchart TD",
    ]
    for n in graph["nodes"]:
        shape = ("([", "])") if n["kind"] == "hub" else ("[", "]")
        out.append(f'    {n["id"]}{shape[0]}"{n["name"]}"{shape[1]}')
    for e in graph["edges"]:
        if e["from"] in PSEUDO_FROM or e["to"] in PSEUDO_TO:
            continue
        arrow = "-->" if e["confidence"] == "observed" else "-.->"
        out.append(f'    {e["from"]} {arrow}|"{e["action"]["type"]}: {e["action"].get("target", "")}"| {e["to"]}')
    out += ["```", "", "## Screens", "", "| id | Name | Kind | Confidence | Unlock | Notes |", "|---|---|---|---|---|---|"]
    for n in graph["nodes"]:
        out.append(f'| `{n["id"]}` | {n["name"]} | {n["kind"]} | {n["confidence"]} | {n.get("unlock") or ""} | {n.get("notes", "")} |')
    out += ["", "## Actions", "", "| From | To | Action | Confidence | Notes |", "|---|---|---|---|---|"]
    for e in graph["edges"]:
        src = "any screen" if e["from"] == "*" else names.get(e["from"], e["from"])
        dst = "previous screen" if e["to"] == "previous" else names.get(e["to"], e["to"])
        out.append(f'| {src} | {dst} | {describe(e["action"])} | {e["confidence"]} | {e.get("notes", "")} |')
    RENDERED.write_text("\n".join(out) + "\n", encoding="utf-8")


def main(argv):
    if len(argv) < 2 or argv[1] not in {"check", "render", "path"}:
        print(__doc__)
        return 2
    graph = load()
    problems = check(graph)
    errors = [p for p in problems if not p.endswith("(warning)")]
    if argv[1] == "check":
        for p in problems:
            print(("WARN  " if p.endswith("(warning)") else "FAIL  ") + p.removesuffix(" (warning)"))
        if not problems:
            print(f"OK: {len(graph['nodes'])} screens, {len(graph['edges'])} actions")
        return 1 if errors else 0
    if errors:
        print("Graph has errors; run `check` first.")
        return 1
    if argv[1] == "render":
        render(graph)
        print(f"Wrote {RENDERED.relative_to(ROOT)}")
        return 0
    if len(argv) != 4:
        print("Usage: python3 scripts/nav-graph.py path FROM TO")
        return 2
    steps = shortest_path(graph, argv[2], argv[3])
    if steps is None:
        print(f"No known route from {argv[2]} to {argv[3]}")
        return 1
    for i, e in enumerate(steps, 1):
        print(f"{i}. {describe(e['action'])}  -> {e['to']}  ({e['confidence']})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
