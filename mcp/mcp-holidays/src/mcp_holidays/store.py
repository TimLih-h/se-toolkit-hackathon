"""Holiday storage — simple JSON file backend."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any


class HolidayStore:
    """Read/write holidays from a JSON file."""

    def __init__(self, data_file: Path) -> None:
        self._path = data_file
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._save([])

    def list_all(self) -> list[dict[str, Any]]:
        return self._load()

    def add(self, name: str, month: int, day: int) -> dict[str, Any]:
        items = self._load()
        entry = {"name": name, "month": month, "day": day}
        items.append(entry)
        self._save(items)
        return entry

    def nearest(self, from_date: date | None = None, limit: int = 5) -> list[dict[str, Any]]:
        """Return holidays closest to *from_date*, sorted by days-away."""
        if from_date is None:
            from_date = date.today()

        items = self._load()
        scored: list[tuple[int, dict[str, Any]]] = []
        for item in items:
            m, d = item["month"], item["day"]
            try:
                holiday_date = date(from_date.year, m, d)
            except ValueError:
                # skip invalid dates (e.g. Feb 30)
                continue
            delta = (holiday_date - from_date).days
            if delta < 0:
                # try next year
                try:
                    holiday_date = date(from_date.year + 1, m, d)
                    delta = (holiday_date - from_date).days
                except ValueError:
                    continue
            scored.append((delta, item))

        scored.sort(key=lambda t: t[0])
        result = []
        for delta, item in scored[:limit]:
            result.append({**item, "days_away": delta})
        return result

    def _load(self) -> list[dict[str, Any]]:
        if not self._path.exists():
            return []
        with open(self._path, encoding="utf-8") as f:
            return json.load(f)

    def _save(self, items: list[dict[str, Any]]) -> None:
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
