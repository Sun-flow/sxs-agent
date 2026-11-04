"""Run and progress records, kept per server day under logs/ (gitignored, on the game PC).

    logs/runs.jsonl              one line per loop run: {"day", "at", "exit", "readout": {the run's JSON readout}}
    logs/progress/<day>.json     {"day", "snapshots": [{"at", "values"}], "notes": [{"at", "source", "values"}]}

A snapshot is what `python -m sxs progress` read off the screen. A note is a reading another loop made while it
was on a screen anyway (the Cart panel during the cart claim, a Fantasia Ascent floor after a win), so the
tracker needs no extra navigation for it. The server day is the dailies day (resets 13:00 UTC, `marks.server_day`).
Writing a record never raises: a full disk or a locked file must not stop a loop.
"""

from __future__ import annotations

import datetime as dt
import json
import logging
from pathlib import Path
from typing import Optional

from . import paths
from .marks import server_day

log = logging.getLogger("sxs.core.records")


def runs_file() -> Path:
    return paths.LOGS / "runs.jsonl"


def progress_dir() -> Path:
    return paths.LOGS / "progress"


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log_run(readout: dict, exit_code: int) -> None:
    """Append one loop run's readout to logs/runs.jsonl (the loop runner calls this after every run)."""
    try:
        runs_file().parent.mkdir(parents=True, exist_ok=True)
        with runs_file().open("a", encoding="utf-8") as f:
            f.write(json.dumps({"day": server_day(), "at": _now(), "exit": exit_code, "readout": readout},
                               default=str) + "\n")
    except OSError as e:
        log.warning("could not record the run: %s", e)


def runs(day: str) -> list[dict]:
    """Every recorded run on a server day, oldest first."""
    try:
        lines = runs_file().read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    out = []
    for line in lines:
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("day") == day:
            out.append(r)
    return out


def day_file(day: str) -> Path:
    return progress_dir() / f"{day}.json"


def load_day(day: str) -> dict:
    try:
        return json.loads(day_file(day).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"day": day, "snapshots": [], "notes": []}


def _save_day(data: dict) -> None:
    try:
        day_file(data["day"]).parent.mkdir(parents=True, exist_ok=True)
        day_file(data["day"]).write_text(json.dumps(data, indent=1, default=str), encoding="utf-8")
    except OSError as e:
        log.warning("could not save progress for %s: %s", data["day"], e)


def add_snapshot(values: dict, day: Optional[str] = None) -> dict:
    data = load_day(day or server_day())
    data["snapshots"].append({"at": _now(), "values": values})
    _save_day(data)
    return data


def note(source: str, values: dict) -> None:
    """A reading another loop made on the way (see the module docstring). Never raises."""
    try:
        data = load_day(server_day())
        data.setdefault("notes", []).append({"at": _now(), "source": source, "values": values})
        _save_day(data)
    except Exception as e:  # noqa: BLE001 - a note must never break the loop that makes it
        log.warning("could not note %s: %s", source, e)


def days() -> list[str]:
    """Server days with a progress file, oldest first."""
    try:
        return sorted(p.stem for p in progress_dir().glob("*.json"))
    except OSError:
        return []


def previous_day(day: str) -> Optional[str]:
    """The latest day before `day` that has a snapshot."""
    earlier = [d for d in days() if d < day and load_day(d)["snapshots"]]
    return earlier[-1] if earlier else None
