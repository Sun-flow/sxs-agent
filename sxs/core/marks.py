"""Once-a-day marks: logs/daily.json maps a chore name to the server day it last ran (resets 8:00 UTC-5)."""

from __future__ import annotations

import json

from .paths import LOGS

DAILY = LOGS / "daily.json"


def server_day() -> str:
    """The game's day for dailies: server time is UTC-5 and dailies refresh at 8:00 server time (13:00 UTC)."""
    import datetime as dt
    return (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=13)).strftime("%Y-%m-%d")


def _load() -> dict:
    try:
        return json.loads(DAILY.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def done_today(key: str) -> bool:
    return _load().get(key) == server_day()


def mark_done(key: str) -> None:
    data = _load()
    data[key] = server_day()
    DAILY.parent.mkdir(exist_ok=True)
    DAILY.write_text(json.dumps(data, indent=2), encoding="utf-8")
