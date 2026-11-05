"""Progress Loop: read the account's numbers off a few screens, keep them per server day, report the day's changes.

    python -m sxs progress                       # snapshot (home, profile, Journal, guild lobby, area map) + report
    python -m sxs progress --only hud,profile    # just these sections
    python -m sxs progress --guild-shop          # also read Guild Tokens in the Guild Shop (read only, never a price)
    python -m sxs report [--day 2026-11-04]      # rebuild the report from saved snapshots, no emulator needed

Sections (each is a read-only visit with its own time budget; nothing here taps a button that spends or claims):
  hud      Home: level, power, Rolla, Dawnium, stamina (top bar).
  profile  Portrait -> player profile: power, class + class level, rank, level, gear +N per piece, technique and
           charm levels (reported as 5-level bands, mae's banding rule), then closed by tapping above it.
  journal  Journal tab: Fantasia Ascent tower and floor; the top bar again.
  guild    Guild island -> Guild Lobby: guild level, members, activeness. With --guild-shop also the Shop's
           token count (top right; the price buttons are never tapped).
  areas    World map -> area map: exploration % of each area in view (the Roam Loop's reader); 100 = finished.

Other loops add readings on the way (`core/records.note`): the Cart's row levels when the daily cart step opens
the panel, Fantasia Ascent floors cleared, Iron Hammers used. Every loop run's JSON readout is in logs/runs.jsonl
(the loop runner writes it), so the report also counts runs, outcomes and exit codes, daily steps, gather pickups.

Stored in logs/progress/<server day>.json; the report goes to logs/progress/<server day>.md and the log.
Deltas compare the newest reading of the day with the last reading of the previous day that has one (or, on the
first day, with the day's first snapshot). A reading that failed is "not read", never a change.
No model calls.
"""

from __future__ import annotations

import argparse
import logging
import time
from typing import Any, Optional

from ..core import records, ui
from ..core.loop import Loop, banner, task
from ..core.marks import server_day
from ..core.nav import Navigator
from ..vision import stats

log = logging.getLogger("sxs.loops.progress")

SECTIONS = ["hud", "profile", "journal", "guild", "areas"]
SECTION_BUDGET_S = 40  # a section that can't finish in this is cut; the others still run
STAMINA_PER_PICKUP = 5  # R-107: every material pickup costs 5 stamina (Bellflowers are free)

# --- reading ------------------------------------------------------------------------------------------------------


class Tracker:
    def __init__(self, dev, det):
        self.dev, self.det = dev, det
        self.nav = Navigator(dev, det)

    def hud(self) -> dict:
        self.nav.go_home()
        frame = self.dev.screenshot()
        return {"hud": stats.read_hud(self.det, frame), "currency": stats.read_topbar(self.det, frame)}

    def profile(self) -> dict:
        self.nav.go_home()
        if not self.nav.open(ui.HUD_PORTRAIT, "player_profile"):
            return {"profile": "not_opened"}
        time.sleep(0.8)  # the panel slides in; numbers settle
        values = stats.read_profile(self.det, self.dev.screenshot())
        ui.tap(self.dev, ui.ABOVE_POPUP, 1.5)
        return {"profile": values}

    def journal(self) -> dict:
        self.nav.go_home()
        if not self.nav.open(ui.NAV_JOURNAL, "journal"):
            return {"journal": "not_opened"}
        time.sleep(0.8)
        frame = self.dev.screenshot()
        out = {"journal": stats.read_journal(self.det, frame)}
        bar = stats.read_topbar(self.det, frame)
        if any(v is not None for v in bar.values()):
            out["currency"] = bar
        return out

    def guild(self, shop: bool = False) -> dict:
        from .guild import Guild

        g = Guild(self.dev, self.det)
        if not g.open_island():
            return {"guild": "not_opened"}
        values: dict[str, Any] = {}
        if g.open_building("Guild Lobby") and self.det.wait_for({"guild_panel"}, 6, 0.5).state == "guild_panel":
            values.update(stats.read_guild_lobby(self.det, self.dev.screenshot()))
            ui.tap(self.dev, ui.BACK_ARROW, 2)
        if shop:
            # Read only: the Shop's price buttons spend Guild Tokens and are never tapped (mae: buy nothing yet).
            if self.det.detect().state != "guild":
                g.open_island()
            if g.open_building("Shop"):
                time.sleep(1)
                values["guild_tokens"] = stats.read_guild_tokens(self.det, self.dev.screenshot())
                ui.tap(self.dev, ui.BACK_ARROW, 2)
        self.nav.go_home()
        return {"guild": values or "not_read"}

    def areas(self) -> dict:
        from .roam import Roamer

        r = Roamer(self.dev, self.det)
        if not r._to_world():
            return {"areas": "not_opened"}
        areas, _, _ = r.survey()
        self.nav.go_home()
        return {"areas": {a.name: (100 if a.pct is None else a.pct) for a in areas}}

    def snapshot(self, sections: list[str], guild_shop: bool = False) -> tuple[dict, dict]:
        """Run each section under its own budget. Returns (values, {section: outcome})."""
        values: dict[str, Any] = {}
        outcome: dict[str, str] = {}
        for name in sections:
            with task(f"progress {name}", SECTION_BUDGET_S) as w:
                try:
                    got = self.guild(guild_shop) if name == "guild" else getattr(self, name)()
                    for k, v in got.items():
                        if isinstance(v, dict) and isinstance(values.get(k), dict):
                            values[k] = {**values[k], **{kk: vv for kk, vv in v.items() if vv is not None}}
                        else:
                            values[k] = v
                    outcome[name] = "read" if all(not isinstance(v, str) for v in got.values()) else "not_opened"
                except Exception as e:  # noqa: BLE001 - one bad section must not lose the others
                    log.warning("[progress %s] failed: %s", name, e)
                    outcome[name] = "error"
            if w.status:
                outcome[name] = w.status
        try:
            self.nav.go_home()
        except Exception as e:  # noqa: BLE001
            log.warning("could not get home after the snapshot: %s", e)
        return values, outcome


# --- the report ---------------------------------------------------------------------------------------------------


def merge(snapshots: list[dict], notes: list[dict] = ()) -> dict:
    """The day's newest value of every reading: later snapshots override earlier ones, but a reading that failed
    (None or a "not_opened" marker) never hides a good earlier one. Notes go under "notes": {source: values}."""
    out: dict[str, Any] = {}
    for s in snapshots:
        for k, v in s["values"].items():
            if isinstance(v, dict):
                cur = out.get(k) if isinstance(out.get(k), dict) else {}
                out[k] = _merge_dict(cur, v)
            elif k not in out or not isinstance(v, str):
                out[k] = v
    for n in notes:
        cur = out.setdefault("notes", {}).get(n["source"], {})
        out["notes"][n["source"]] = _merge_dict(cur, n["values"]) if isinstance(n["values"], dict) else n["values"]
    return out


def _merge_dict(old: dict, new: dict) -> dict:
    out = dict(old)
    for k, v in new.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge_dict(out[k], v)
        elif v is not None:
            out[k] = v
    return out


def _fmt(v) -> str:
    if v is None:
        return "not read"
    if isinstance(v, float):
        if v >= 1000:
            return f"{v / 1000:.3g}K"
        return f"{v:g}"
    return str(v)


def _delta(new, old) -> str:
    if isinstance(new, (int, float)) and isinstance(old, (int, float)) and not isinstance(new, bool):
        d = new - old
        if not d:
            return "no change"
        sign = "+" if d > 0 else "-"
        return f"{sign}{_fmt(abs(float(d)) if isinstance(d, float) else abs(d))}"
    if old is None or new is None:
        return ""
    return "no change" if new == old else f"was {_fmt(old)}"


def _get(d: Optional[dict], *path):
    for p in path:
        if not isinstance(d, dict):
            return None
        d = d.get(p)
    return d


def _band_text(b: Optional[dict], plus: str = "") -> str:
    if not b:
        return "not read"
    extra = f", {b['in_next']}/{b['of']} already at {plus}{b['next']}" if b["in_next"] else ""
    return f"{plus}{b['band']} band ({b['of']} pieces{extra})"


def build_report(day: str) -> tuple[str, dict]:
    """Markdown report for a server day and a summary dict for the JSON readout."""
    data = records.load_day(day)
    if not data["snapshots"] and not data.get("notes") and not records.runs(day):
        return f"# Progress {day}\n\nNo snapshots, notes or runs recorded for this day.\n", {"day": day, "empty": True}
    now = merge(data["snapshots"], data.get("notes", []))
    prev_day = records.previous_day(day)
    if prev_day:
        p = records.load_day(prev_day)
        base, base_name = merge(p["snapshots"], p.get("notes", [])), f"end of {prev_day}"
    elif len(data["snapshots"]) > 1:
        base, base_name = merge(data["snapshots"][:1]), "first reading today"
    else:
        base, base_name = {}, None
    lines = [f"# Progress {day}", "",
             f"Compared with: {base_name}." if base_name else "First day on record: no deltas yet.", ""]
    changes: dict[str, str] = {}

    def row(label, new, old, key=None):
        d = _delta(new, old) if base_name else ""
        lines.append(f"| {label} | {_fmt(new)} | {d} |")
        if d and d != "no change" and key:
            changes[key] = d

    # Character
    lines += ["## Character", "", "| Stat | Now | Change |", "|---|---|---|"]
    power = _get(now, "profile", "power_k") or _get(now, "hud", "power_k")
    power_old = _get(base, "profile", "power_k") or _get(base, "hud", "power_k")
    row("Power (K)", power, power_old, "power_k")
    row("Level", _get(now, "profile", "level") or _get(now, "hud", "level"),
        _get(base, "profile", "level") or _get(base, "hud", "level"), "level")
    row("Class", _get(now, "profile", "class"), _get(base, "profile", "class"), "class")
    row("Class level", _get(now, "profile", "class_level"), _get(base, "profile", "class_level"), "class_level")
    row("Rank", _get(now, "profile", "rank"), _get(base, "profile", "rank"), "rank")
    lines.append("")

    # Gear and skills, as bands
    gear, gear_old = _get(now, "profile", "gear"), _get(base, "profile", "gear")
    lines += ["## Gear and skills (bands of 5)", "", "| What | Now | Change |", "|---|---|---|"]
    for label, key, plus in (("Gear", "gear", "+"), ("Techniques", "techniques", "Lv "), ("Charms", "charms", "Lv ")):
        b, bo = stats.band(_get(now, "profile", key) or []), stats.band(_get(base, "profile", key) or [])
        d = ""
        if base_name and b and bo:
            if (b["band"], b["in_next"], b["of"]) == (bo["band"], bo["in_next"], bo["of"]):
                d = "no change"
            else:
                d = f"was {_band_text(bo, plus)}"
                changes[key + "_band"] = d
        lines.append(f"| {label} | {_band_text(b, plus)} | {d} |")
    if isinstance(gear, dict):
        moved = [f"{k} +{gear_old.get(k)} -> +{v}" for k, v in gear.items()
                 if isinstance(gear_old, dict) and isinstance(v, int) and isinstance(gear_old.get(k), int)
                 and v != gear_old[k]]
        swapped = [k for k, v in gear.items() if isinstance(gear_old, dict) and isinstance(v, int)
                   and isinstance(gear_old.get(k), int) and v < gear_old[k]]
        if moved:
            lines.append("")
            lines.append("Gear pieces changed: " + ", ".join(moved) +
                         (f" (a lower level on {', '.join(swapped)} usually means a new piece was equipped)"
                          if swapped else "") + ".")
            changes["gear"] = ", ".join(moved)
    lines += ["", "Relics: not unlocked on the account yet (2026-11-04); no screen route to read them.", ""]

    # Resources
    lines += ["## Resources", "", "| Pool | Now | Change |", "|---|---|---|"]
    for label, path in (("Rolla", ("currency", "rolla")), ("Dawnium", ("currency", "dawnium")),
                        ("Stamina", ("currency", "stamina")), ("Guild Tokens", ("guild", "guild_tokens"))):
        row(label, _get(now, *path), _get(base, *path), path[-1])
    hammer_notes = [n["values"].get("used") for n in data.get("notes", []) if n["source"] == "iron_hammers"]
    hammers = sum(h for h in hammer_notes if isinstance(h, int)) if hammer_notes else None
    if hammers is not None:
        lines.append(f"| Iron Hammers used today | {hammers} | |")
    lines += ["", "Amounts over 1,000 are as the top bar shows them (rounded, e.g. 43.2K), so small changes can "
              "hide. Lumium and Material Realm tools (pickaxes, shovels, gloves) need the bag screen, which has "
              "no route yet.", ""]

    # Exploration
    areas, areas_old = _get(now, "areas"), _get(base, "areas")
    lines += ["## Exploration", ""]
    if isinstance(areas, dict) and areas:
        old = areas_old if isinstance(areas_old, dict) else {}
        cleared = [a for a, v in areas.items() if v == 100 and isinstance(old.get(a), int) and old[a] < 100]
        gained = [f"{a} {old[a]}% -> {v}%" for a, v in areas.items()
                  if isinstance(old.get(a), int) and v != old[a] and v != 100]
        new = [a for a in areas if a not in old] if old else []
        lines.append(f"Cleared today: {', '.join(cleared) if cleared else 'none'}.")
        if gained:
            lines.append(f"Explored further: {', '.join(gained)}.")
        if new:
            lines.append(f"Newly on the area map: {', '.join(new)}.")
        todo = [f"{a} {v}%" for a, v in sorted(areas.items(), key=lambda kv: -kv[1]) if v < 100]
        lines.append(f"Still to explore (in view): {', '.join(todo) if todo else 'none'}.")
        if cleared:
            changes["areas_cleared"] = ", ".join(cleared)
    else:
        lines.append("Area map not read today.")
    lines.append("")

    # Fantasia Ascent, Cart, guild
    lines += ["## Tower, Cart, guild", "", "| What | Now | Change |", "|---|---|---|"]
    row(f"Fantasia Ascent floor ({_get(now, 'journal', 'tower') or 'tower'})", _get(now, "journal", "tower_floor"),
        _get(base, "journal", "tower_floor"), "tower_floor")
    cleared_floor = _get(now, "notes", "tower", "floor_cleared")
    if cleared_floor:
        lines.append(f"| Highest floor cleared today | F{cleared_floor} | |")
    cart, cart_old = _get(now, "notes", "cart"), _get(base, "notes", "cart")
    if isinstance(cart, dict):
        for k, v in cart.items():
            lv = v.get("level") if isinstance(v, dict) else v
            lvo = (cart_old or {}).get(k) if isinstance(cart_old, dict) else None
            lvo = lvo.get("level") if isinstance(lvo, dict) else lvo
            row(f"Cart {k.replace('_', ' ')}", lv, lvo, f"cart_{k}")
    else:
        lines.append("| Cart | not read today (read when the daily cart step opens the panel) | |")
    row("Guild level", _get(now, "guild", "guild_level"), _get(base, "guild", "guild_level"), "guild_level")
    row("Guild activeness", _get(now, "guild", "guild_activeness"), _get(base, "guild", "guild_activeness"))
    lines.append("")

    # Runs
    rs = records.runs(day)
    lines += ["## Bot runs today", ""]
    if rs:
        per: dict[str, list[str]] = {}
        exits = {0: 0, 1: 0, 2: 0}
        pickups = 0
        steps: dict[str, str] = {}
        for r in rs:
            ro = r.get("readout", {})
            per.setdefault(ro.get("loop", "?"), []).append(str(ro.get("status")))
            exits[r.get("exit", 1)] = exits.get(r.get("exit", 1), 0) + 1
            if ro.get("loop") == "gather" or ro.get("target"):
                pickups += int(ro.get("pickups") or 0)
            if ro.get("loop") == "daily" and isinstance(ro.get("steps"), dict):
                steps.update(ro["steps"])
        lines.append(f"{len(rs)} runs: {exits.get(0, 0)} ok, {exits.get(1, 0)} needed a look, "
                     f"{exits.get(2, 0)} refused.")
        lines.append("")
        lines += ["| Loop | Runs | Outcomes |", "|---|---|---|"]
        for loop, sts in per.items():
            counts = {s: sts.count(s) for s in dict.fromkeys(sts)}
            lines.append(f"| {loop} | {len(sts)} | {', '.join(f'{s} x{n}' if n > 1 else s for s, n in counts.items())} |")
        lines.append("")
        if steps:
            lines.append("Daily steps: " + ", ".join(f"{k} {v}" for k, v in steps.items()) + ".")
        if pickups:
            lines.append(f"Gather pickups (standalone runs): {pickups} (about {pickups * STAMINA_PER_PICKUP} stamina).")
    else:
        lines.append("No loop runs recorded today.")
    lines.append("")

    last = data["snapshots"][-1]["values"] if data["snapshots"] else {}
    missed = sorted(k for k, v in _flat(last).items() if v is None or isinstance(v, str) and v.startswith("not_"))
    if missed:
        lines += ["Not read this time: " + ", ".join(missed) + ".", ""]
    summary = {"day": day, "compared_with": base_name, "snapshots": len(data["snapshots"]),
               "changes": changes, "not_read": missed}
    return "\n".join(lines), summary


def _flat(d: Any, prefix: str = "") -> dict:
    out = {}
    if isinstance(d, dict):
        for k, v in d.items():
            if k == "notes":
                continue
            out.update(_flat(v, f"{prefix}{k}."))
    elif isinstance(d, list):
        pass  # technique / charm slots: None is an empty slot, not a failed read
    elif prefix:
        out[prefix[:-1]] = d
    return out


def write_report(day: str) -> tuple[str, dict]:
    text, summary = build_report(day)
    path = records.day_file(day).with_suffix(".md")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        summary["report"] = str(path)
    except OSError as e:
        log.warning("could not write the report: %s", e)
    return text, summary


# --- loop and command ---------------------------------------------------------------------------------------------


def _args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--only", help="comma-separated sections: " + ", ".join(SECTIONS))
    p.add_argument("--guild-shop", action="store_true",
                   help="also open the Guild Shop to read Guild Tokens (read only)")


def _run(ctx, opts):
    sections = [s for s in (opts.only.split(",") if opts.only else SECTIONS) if s in SECTIONS]
    if not sections:
        return {"end": f"refused: --only takes {', '.join(SECTIONS)}"}
    banner(log, "Progress", f"read {', '.join(sections)} and record today's numbers (read only)",
           f"every section tried once ({SECTION_BUDGET_S} s each), then the day's report")
    values, outcome = Tracker(ctx.dev, ctx.det).snapshot(sections, opts.guild_shop)
    day = server_day()
    records.add_snapshot(values, day)
    text, summary = write_report(day)
    for line in text.splitlines():
        if line.strip():
            log.info(line)
    status = "done" if all(v == "read" for v in outcome.values()) else "partial"
    return {"end": status, "sections": outcome, **summary}


def report_main(argv: list[str]) -> int:
    """python -m sxs report [--day YYYY-MM-DD]: print and save the report from saved snapshots (no emulator)."""
    p = argparse.ArgumentParser(prog="python -m sxs report", description="progress report from saved snapshots")
    p.add_argument("--day", default=None, help="server day (default: today, resets 13:00 UTC)")
    opts = p.parse_args(argv)
    text, _ = write_report(opts.day or server_day())
    print(text)
    return 0


LOOP = Loop("progress", "Progress", "read the account's numbers (read only), keep them per day, report the changes",
            _run, _args, ok={"done", "partial"})
