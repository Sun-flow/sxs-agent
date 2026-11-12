"""Progress tracker, offline: the screen readers against reference screens, and the day report from made-up
snapshots in a temporary logs folder.

    python tests/check_progress.py

Needs MaaFramework and the OCR models (like check_states_offline.py). Expected values were read by eye from each
screenshot. Writes nothing under the repo's logs/.

Needs: MaaFramework + OCR models
Checks: Progress tracker: stat readers on reference screens, bands, the day report (temp logs), the home > profile >
  Journal route replayed
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import cv2

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sxs.core import paths, records  # noqa: E402
from sxs.core.replay import ImageDevice  # noqa: E402
from sxs.core.state import StateDetector  # noqa: E402
from sxs.loops import progress  # noqa: E402
from sxs.vision import stats  # noqa: E402

S = ROOT / "docs" / "screens"

READERS = [  # (screen, reader, expected subset)
    ("home/home", "read_topbar", {"rolla": 1160, "dawnium": 145, "stamina": 51, "stamina_cap": 300}),
    ("home/home_bed_xp", "read_topbar", {"rolla": 43200, "dawnium": 1140, "stamina": 173}),
    ("home/journal", "read_topbar", {"rolla": 43000, "dawnium": 1090, "stamina": 153}),
    ("home/main_menu", "read_topbar", {"rolla": 1380, "dawnium": 145, "stamina": 51}),
    ("character/character", "read_topbar", {"rolla": 2600, "dawnium": 175, "stamina": None}),
    ("home/home", "read_hud", {"level": 1, "power_k": 0.819}),
    ("home/home_bed_xp", "read_hud", {"level": 20, "power_k": 13.1}),
    ("home/journal", "read_hud", {"level": 13, "power_k": 10.1}),
    ("home/journal", "read_journal", {"tower": "Moonveil Woods", "tower_floor": 6}),
    ("character/player_profile", "read_profile", {
        "power_k": 1.02, "class": "No Class", "class_level": 0, "rank": "No Rank", "level": 2,
        "gear": {"weapon": 4, "head": None, "chest": None, "boots": None},
        "techniques": [1, 1, None, None], "charms": [None, None, None, None]}),
    ("character/player_profile_hp", "read_profile", {
        "power_k": 5.24, "rank": "Apprentice I", "level": 10,
        "gear": {"weapon": 12, "head": 6, "chest": 5, "boots": 1},
        "techniques": [10, 10, None, None], "charms": [1, None, None, None]}),
    ("character/player_profile_charm_badges", "read_profile", {
        "power_k": 8.1, "class": "Mage", "class_level": 2, "rank": "Apprentice I", "level": 13,
        "gear": {"weapon": 15, "head": 10, "chest": 5, "boots": 1},
        "techniques": [10, 10, 10, 10], "charms": [1, None, None, None]}),
    ("home/cart", "read_cart", {"rolla": {"level": 1, "per_hour": 1000}, "wood": {"level": 1, "per_hour": 50},
                                "stone": {"level": 1, "per_hour": 50}, "raw_ore": "locked", "gear": "locked"}),
    ("guild/guild_lobby", "read_guild_lobby", {"guild_level": 1, "guild_members": 28, "guild_activeness": 2820}),
    ("guild/guild_shop_top", "read_guild_tokens", 760),
]


def check_readers(det) -> list[str]:
    bad = []
    for screen, reader, want in READERS:
        frame = cv2.imread(str(S / f"{screen}.png"))
        got = getattr(stats, reader)(det, frame)
        wrong = {k: (got.get(k) if isinstance(got, dict) else got, v)
                 for k, v in (want.items() if isinstance(want, dict) else [("value", want)])
                 if (got.get(k) if isinstance(got, dict) else got) != v}
        print(f"{'ok ' if not wrong else 'BAD'} {screen:40} {reader:18} {'' if not wrong else wrong}")
        if wrong:
            bad.append(f"{screen} {reader}: {wrong}")
    return bad


def check_bands() -> list[str]:
    cases = [([13, 13, 15, 13], {"band": 10, "next": 15, "in_next": 1, "of": 4}),
             ({"weapon": 21, "head": 20, "chest": 20, "boots": None}, {"band": 20, "next": 25, "in_next": 0, "of": 3}),
             ([None, None], None)]
    bad = [f"band({lv}) = {stats.band(lv)}, want {want}" for lv, want in cases if stats.band(lv) != want]
    print("ok  bands" if not bad else f"BAD bands {bad}")
    return bad


def check_report() -> list[str]:
    bad = []
    old_logs = paths.LOGS
    with tempfile.TemporaryDirectory() as tmp:
        paths.LOGS = Path(tmp)
        try:
            y = {"hud": {"level": 22, "power_k": 16.9},
                 "currency": {"rolla": 30000.0, "dawnium": 1170.0, "stamina": 150, "stamina_cap": 300},
                 "profile": {"power_k": 16.9, "level": 22, "class": "Mage", "class_level": 3, "rank": "Apprentice II",
                             "gear": {"weapon": 21, "head": 20, "chest": 20, "boots": 20},
                             "techniques": [13, 13, 13, 13], "charms": [9, 9, None, None]},
                 "journal": {"tower": "Moonveil Woods", "tower_floor": 6},
                 "areas": {"Damp Woods": 40, "Verdantglade III": 0, "Highland Woods": 100}}
            records.add_snapshot(y, "2026-11-03")
            t = json.loads(json.dumps(y))
            t["currency"].update(rolla=33600.0, stamina=None)  # stamina misread: must not count as a change
            t["profile"].update(power_k=17.4, level=23)
            t["profile"]["gear"].update(weapon=25, head=18)
            t["profile"]["techniques"] = [15, 15, 15, 15]
            t["journal"]["tower_floor"] = 9
            t["areas"].update({"Damp Woods": 100, "Verdantglade III": 5})
            records.add_snapshot(t, "2026-11-04")
            records.note("cart", {"rolla": {"level": 2, "per_hour": 1200}, "raw_ore": "locked"})
            records.log_run({"loop": "gather", "status": "budget_spent", "ok": True, "pickups": 10}, 0)
            records.log_run({"loop": "roam", "status": "stalled", "ok": False}, 1)
            day = records.server_day()
            if day != "2026-11-04":  # notes and runs land on the real server day; move them onto the test day
                (paths.LOGS / "runs.jsonl").write_text((paths.LOGS / "runs.jsonl").read_text().replace(day, "2026-11-04"))
                d = records.load_day(day)
                t_day = records.load_day("2026-11-04")
                t_day["notes"] = d["notes"]
                records.day_file("2026-11-04").write_text(json.dumps(t_day))
                records.day_file(day).unlink()
            text, summary = progress.build_report("2026-11-04")
            want = {"power_k": "+0.5", "level": "+1", "rolla": "+3.6K", "tower_floor": "+3",
                    "areas_cleared": "Damp Woods"}
            for k, v in want.items():
                if summary["changes"].get(k) != v:
                    bad.append(f"report change {k}: {summary['changes'].get(k)!r}, want {v!r}")
            if "stamina" in summary["changes"]:
                bad.append("a misread stamina showed as a change")
            if summary["not_read"] != ["currency.stamina"]:
                bad.append(f"not_read {summary['not_read']}, want ['currency.stamina']")
            for needle in ("Lv 15 band (4 pieces)", "weapon +21 -> +25", "head +20 -> +18", "usually means a new piece",
                           "Cleared today: Damp Woods", "Verdantglade III 0% -> 5%", "Cart rolla | 2",
                           "2 runs: 1 ok, 1 needed a look", "Gather pickups (standalone runs): 10 (about 50 stamina)",
                           "compared with: end of 2026-11-03".capitalize()):
                if needle not in text:
                    bad.append(f"report lacks {needle!r}")
            if bad:
                print(text)
        finally:
            paths.LOGS = old_logs
    print("ok  report" if not bad else f"BAD report {bad}")
    return bad


class ScriptedDevice(ImageDevice):
    """Replays the snapshot route on saved screens: each tap the route makes shows the screen it leads to."""

    SCREENS = {"home": "home/home", "profile": "character/player_profile_charm_badges", "journal": "home/journal"}

    def __init__(self):
        super().__init__()
        self.taps: list[tuple[int, int]] = []
        self.show("home")

    def show(self, name: str) -> None:
        self.set_frame(S / f"{self.SCREENS[name]}.png")

    def tap(self, x: int, y: int) -> None:
        from sxs.core import ui

        self.taps.append((x, y))
        target = {ui.HUD_PORTRAIT: "profile", ui.ABOVE_POPUP: "home", ui.NAV_JOURNAL: "journal",
                  ui.NAV_HOME: "home"}.get((x, y))
        if target is None:
            raise AssertionError(f"the snapshot route tapped {(x, y)}, which it has no business tapping")
        self.show(target)


def check_route() -> list[str]:
    """hud, profile and journal sections on replayed screens: the right values, and no tap outside the route."""
    dev = ScriptedDevice()
    det = StateDetector(dev)
    bad = []
    try:
        values, outcome = progress.Tracker(dev, det).snapshot(["hud", "profile", "journal"])
    except AssertionError as e:
        bad.append(str(e))
        values, outcome = {}, {}
    if outcome != {"hud": "read", "profile": "read", "journal": "read"}:
        bad.append(f"sections {outcome}")
    want = {("profile", "level"): 13, ("profile", "rank"): "Apprentice I", ("journal", "tower_floor"): 6,
            ("currency", "rolla"): 43000, ("hud", "level"): 1}
    for (sec, key), v in want.items():
        if (values.get(sec) or {}).get(key) != v:
            bad.append(f"route {sec}.{key} = {(values.get(sec) or {}).get(key)!r}, want {v!r}")
    print("ok  route (home > profile > Journal)" if not bad else f"BAD route {bad}")
    return bad


def main() -> int:
    det = StateDetector(ImageDevice())
    bad = check_readers(det) + check_bands() + check_report() + check_route()
    print("all good" if not bad else f"{len(bad)} problem(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
