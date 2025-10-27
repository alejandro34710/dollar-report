from __future__ import annotations

from datetime import datetime
from dateutil import tz


def now_iso(tz_name: str) -> str:
    zone = tz.gettz(tz_name)
    return datetime.now(zone).isoformat(timespec="seconds")


def today_ymd(tz_name: str) -> str:
    zone = tz.gettz(tz_name)
    return datetime.now(zone).date().isoformat()
