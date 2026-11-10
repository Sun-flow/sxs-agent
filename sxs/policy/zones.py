"""The location tree: which zones exist, what they need, how far they're explored, and how they connect. No model calls.

    python -m sxs zones            # print the tree, then the open questions (zones with no known way in, ...)

mae, 2026-11-09: the bot should keep a map of the locations and explorations it knows: every zone, its recommended
power (CP), exploration %, blessed or not, and how zones connect (which zone you walk in from). The data lives in
`resource/world/zones.json` (committed, so it survives between sessions and machines); the roam loop reads it to pick
where to go and from where, and writes back what each area-map survey and each walk teaches it.

Rules this module carries:
- R-132: a dotted line is a zone border. Finish the zone you're in (100%) before crossing, and cross only into a zone
  that passes the 1.25x power check (R-127, `fights.within_reach`).
- R-135: the next zone is the lowest-CP zone not yet blessed, within reach.
- R-067 / mae 2026-11-04: enter a zone from a connected, explored neighbour; a neighbour that failed today goes last.

Zone fields (all optional except kingdom):
    kingdom       "Verdantglade", "Originisle", ...
    kind          "zone" (default), "town" (no exploration %), "dungeon"
    cp            recommended power in K (the area-map gate line), null if none read
    pct           exploration % (100 = explored: the area map shows no % line), null if never read
    blessed       true / false / null (unknown)
    map_point     [x, y] of the label on the stitched area-map survey (only comparable within one kingdom survey)
    entries       [{"via": zone, "xy": [x, y], "day": ...}]: every way in a walk has used, one per neighbour (map
                  coordinates on arrival). mae, 2026-11-09: zones have several ways in and out and border several zones.
    failed_via    {zone: day}: neighbours a walk in from made no progress, by server day
    first_seen, last_seen   dates
    notes         free text; gaps are open questions (shown by `python -m sxs zones`)
Links: {"a", "b", "how": "walked" | "map_adjacent" | "inside", "note"}; "walked" means a walk crossed it.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Iterable, Optional

from ..core.paths import RESOURCE
from . import fights

ZONES_FILE = RESOURCE / "world" / "zones.json"
LINK_RANK = {"map_adjacent": 0, "inside": 1, "walked": 2}
ADJACENT_PX = 200  # survey-zoom px between two labels that makes them likely neighbours (330 linked half the kingdom)


def squeeze(t: str) -> str:
    """Same normalisation as `sxs.actions.goto.squeeze` (kept here so policy doesn't import actions)."""
    t = re.sub(r"[Il1|]+\s*$", lambda m: "i" * len(m.group(0).strip()), (t or "").strip())
    return re.sub(r"[\s\-]", "", t).lower()


def same(a: str, b: str) -> bool:
    """Loose match for OCR'd zone names: equal after squeeze, one a 6+ letter suffix of the other (labels clipped on
    the left at the map edge), or one missing a trailing letter. Trailing roman numerals must agree."""
    x, y = squeeze(a), squeeze(b)
    if not x or not y:
        return False
    if x == y:
        return True
    nx, ny = re.search(r"(?<=[a-z]{4})([ivx]+)$", x), re.search(r"(?<=[a-z]{4})([ivx]+)$", y)
    if nx and ny and nx.group(1) != ny.group(1):
        return False
    short, long_ = sorted((x, y), key=len)
    if len(short) >= 6 and long_.endswith(short):
        return True
    return (long_.startswith(short) and len(long_) - len(short) <= 1 and not nx and not ny)


@dataclass
class Tree:
    zones: dict = field(default_factory=dict)
    links: list = field(default_factory=list)
    gaps: list = field(default_factory=list)  # open questions not tied to one field ("Jungle Camp: entry unknown")
    path: Path = ZONES_FILE

    # --- storage ------------------------------------------------------------------------------------------------

    @classmethod
    def load(cls, path: Path = ZONES_FILE) -> "Tree":
        try:
            d = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            d = {}
        return cls(d.get("zones", {}), d.get("links", []), d.get("gaps", []), path)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        d = {"about": "Location tree (sxs/policy/zones.py): zones, CP, exploration, blessing, connections.",
             "zones": dict(sorted(self.zones.items())), "links": self.links, "gaps": self.gaps}
        self.path.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    # --- lookups ------------------------------------------------------------------------------------------------

    def key(self, name: str) -> Optional[str]:
        """The stored name for an OCR'd one, or None."""
        if not name:
            return None
        if name in self.zones:
            return name
        exact = [k for k in self.zones if squeeze(k) == squeeze(name)]
        if exact:
            return exact[0]
        loose = [k for k in self.zones if same(k, name)]
        return max(loose, key=len) if len(loose) == 1 else None

    def get(self, name: str) -> Optional[dict]:
        k = self.key(name)
        return self.zones[k] if k else None

    def neighbours(self, name: str, how: Iterable[str] = ("walked", "map_adjacent", "inside")) -> list[str]:
        k = self.key(name) or name
        out = []
        for ln in self.links:
            if ln.get("how") in how and k in (ln["a"], ln["b"]):
                out.append(ln["b"] if ln["a"] == k else ln["a"])
        return out

    def explored(self, name: str) -> bool:
        z = self.get(name) or {}
        return z.get("kind") == "town" or z.get("pct") == 100 or bool(z.get("blessed"))

    def done(self, name: str) -> bool:
        """Nothing left to walk there for the exploration order (R-135): blessed, a town, or explored (100%). An explored
        zone's statue is blessed when its area-map "!" lights (roam's statue pass), not by walking it again."""
        return self.explored(name)

    # --- learning -----------------------------------------------------------------------------------------------

    def observe(self, name: str, kingdom: Optional[str] = None, pct=..., cp=..., point=None, today: str = "") -> str:
        """Record one area-map reading of a zone. pct=None means the label showed no % line (explored)."""
        today = today or date.today().isoformat()
        k = self.key(name)
        if k is None:
            k = name.strip()
            self.zones[k] = {"kingdom": kingdom or "", "first_seen": today}
        z = self.zones[k]
        if kingdom and not z.get("kingdom"):
            z["kingdom"] = kingdom
        if pct is not ...:
            new = 100 if pct is None else int(pct)
            if z.get("kind") != "town":
                z["pct"] = new
        if cp is not ... and cp is not None:
            old = z.get("cp")
            # A zone's CP doesn't change: a reading far from the known one is OCR ("1.0" for Troll Lair's 17K).
            if float(cp) <= 100 and (not old or abs(float(cp) - old) <= 0.3 * old):  # "204" is 20.4 with the dot lost
                z["cp"] = float(cp)
        if point is not None:
            z["map_point"] = [int(point[0]), int(point[1])]
        z["last_seen"] = today
        return k

    def mark_blessed(self, name: str) -> None:
        k = self.key(name)
        if k:
            self.zones[k]["blessed"] = True
            self.zones[k]["pct"] = 100

    def link(self, a: str, b: str, how: str, note: str = "") -> None:
        """Add a connection, or upgrade it (map_adjacent < inside < walked)."""
        a, b = self.key(a) or a, self.key(b) or b
        if a == b:
            return
        for ln in self.links:
            if {ln["a"], ln["b"]} == {a, b}:
                if LINK_RANK.get(how, 0) > LINK_RANK.get(ln.get("how"), 0):
                    ln["how"] = how
                if note and note not in (ln.get("note") or ""):
                    ln["note"] = ((ln.get("note") or "") + "; " + note).strip("; ")
                return
        self.links.append({"a": a, "b": b, "how": how, **({"note": note} if note else {})})

    def link_neighbours_by_map(self, kingdom: str) -> None:
        """Labels close together on one stitched survey are probably neighbours (a guess, kept as map_adjacent until a
        walk confirms it)."""
        pts = [(k, z["map_point"]) for k, z in self.zones.items()
               if z.get("kingdom") == kingdom and z.get("map_point")]
        for i, (a, pa) in enumerate(pts):
            for b, pb in pts[i + 1:]:
                if (pa[0] - pb[0]) ** 2 + (pa[1] - pb[1]) ** 2 <= ADJACENT_PX ** 2:
                    self.link(a, b, "map_adjacent")

    def record_entry(self, target: str, via: str, ok: bool, day: str, xy=None, why: str = "") -> None:
        """A walk into `target` from `via`: ok = it got in (or the % rose)."""
        k = self.key(target)
        if k is None:
            return
        z = self.zones[k]
        if ok:
            v = self.key(via) or via
            z["entries"] = [e for e in z.get("entries", []) if e.get("via") != v]
            z["entries"].append({"via": v, "day": day, **({"xy": list(xy)} if xy else {})})
            z.get("failed_via", {}).pop(self.key(via) or via, None)
            self.link(k, via, "walked", f"entered {k} from here" if not xy else f"entered {k} at {tuple(xy)}")
        else:
            z.setdefault("failed_via", {})[self.key(via) or via] = day + (f" ({why})" if why else "")

    # --- decisions ----------------------------------------------------------------------------------------------

    def can_cross(self, here: str, there: str, power: Optional[float]) -> tuple[bool, str]:
        """R-132: may a walk cross the border from `here` into `there`?"""
        if here and not self.explored(here):
            return False, f"finish {here} first ({(self.get(here) or {}).get('pct', '?')}%)"
        z = self.get(there) or {}
        if not fights.within_reach(z.get("cp"), power):
            return False, f"{there} needs {z.get('cp')}K, over 1.25x our {power}K"
        return True, ""

    def next_zone(self, power: Optional[float], here: str = "", skip: Iterable[str] = ()) -> Optional[str]:
        """R-132 then R-135: the zone we stand in if it's unfinished and in reach; else the lowest-CP zone not blessed
        and in reach (zones with no CP read go last)."""
        skip = {squeeze(s) for s in skip}
        # A zone whose way in needs an item we don't have (live 2026-11-10: Hidden Camp's Boulder Blockade needs a
        # Magic Drill) waits until someone clears `blocked`.
        ok = lambda k: (squeeze(k) not in skip and not self.zones[k].get("blocked")  # noqa: E731
                        and fights.within_reach(self.zones[k].get("cp"), power))
        h = self.key(here)
        if h and self.zones[h].get("kind", "zone") == "zone" and not self.explored(h) and ok(h):
            return h
        todo = [k for k, z in self.zones.items() if z.get("kind", "zone") == "zone" and not self.done(k) and ok(k)]
        # A zone never read on the big map (no % line, e.g. Sunrise Isle) goes after every zone that was read
        # (live 2026-11-10: roam picked it with nothing known and wandered toward it).
        todo.sort(key=lambda k: (self.zones[k].get("pct") is None, self.zones[k].get("cp") is None,
                                 self.zones[k].get("cp") or 0,
                                 -(self.zones[k].get("pct") or 0)))
        return todo[0] if todo else None

    def entry_candidates(self, target: str, day: str) -> list[str]:
        """Neighbours to walk in from, best first: known ways in (latest first), then walked links, then explored map
        neighbours;
        ones that failed today go last."""
        z = self.get(target) or {}
        failed = {k for k, v in z.get("failed_via", {}).items() if str(v).startswith(day)}
        known = [e["via"] for e in reversed(z.get("entries", []))]
        cands = self.neighbours(target)
        rank = lambda n: (n in failed, (known.index(n) if n in known else len(known)), self.neighbours(target, ("walked",)).count(n) == 0,  # noqa: E731
                          not self.explored(n))
        return sorted(dict.fromkeys(cands), key=rank)

    def open_questions(self) -> list[str]:
        out = list(self.gaps)
        for k, z in sorted(self.zones.items()):
            if z.get("kind", "zone") != "zone" or self.done(k):
                continue
            if not z.get("entries") and not self.neighbours(k, ("walked",)):
                out.append(f"{k}: no known way in" + (f" (failed from {', '.join(z['failed_via'])})"
                                                      if z.get("failed_via") else ""))
            if z.get("cp") is None and z.get("pct") != 100:
                out.append(f"{k}: recommended power not read")
        return list(dict.fromkeys(out))


def main(argv: list[str]) -> int:
    t = Tree.load()
    for kingdom in sorted({z.get("kingdom", "") for z in t.zones.values()}):
        print(kingdom or "(kingdom unknown)")
        for k, z in sorted(t.zones.items(), key=lambda kv: (kv[1].get("cp") or 0, kv[0])):
            if z.get("kingdom", "") != kingdom:
                continue
            state = "town" if z.get("kind") == "town" else (
                "blessed" if z.get("blessed") else f"{z['pct']}%" if z.get("pct") is not None else "?%")
            via = ", ".join(e["via"] for e in z.get("entries", []))
            print(f"  {k:<20} {(str(z['cp']) + 'K') if z.get('cp') else '-':>6}  {state:<8} "
                  f"next to: {', '.join(t.neighbours(k)) or '?'}" + (f"  (enter from {via})" if via else ""))
    q = t.open_questions()
    if q:
        print("open questions:")
        for line in q:
            print("  - " + line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
