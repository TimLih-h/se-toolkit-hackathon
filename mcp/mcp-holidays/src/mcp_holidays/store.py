"""Holiday storage — simple JSON file backend with category support."""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Any


MONTH_NAMES = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

CATEGORY_DESC = {
    "national": "A national holiday celebrated",
    "international": "An internationally celebrated holiday",
    "professional": "A professional observance honoring",
    "personal": "A personal reminder for",
    "general": "A special day for",
}


class HolidayStore:
    """Read/write holidays from a JSON file with category support."""

    def __init__(self, data_file: Path) -> None:
        self._path = data_file
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._save([])

    def list_all(self) -> list[dict[str, Any]]:
        return self._load()

    @staticmethod
    def _auto_description(name: str, month: int, day: int, category: str) -> str:
        """Generate a short description if none provided."""
        month_name = MONTH_NAMES[month] if 1 <= month <= 12 else ""
        cat_text = CATEGORY_DESC.get(category, CATEGORY_DESC["general"])
        return f"{cat_text} {name}, observed on {month_name} {day}."

    def add(
        self, name: str, month: int, day: int, category: str = "general",
        description: str = ""
    ) -> dict[str, Any]:
        items = self._load()
        desc = description.strip() if description else ""
        if not desc:
            desc = self._auto_description(name, month, day, category)
        entry = {
            "name": name,
            "month": month,
            "day": day,
            "category": category,
            "description": desc,
        }
        items.append(entry)
        self._save(items)
        return entry

    def remove(self, name: str) -> bool:
        items = self._load()
        new_items = [i for i in items if i["name"].lower() != name.lower()]
        if len(new_items) == len(items):
            return False
        self._save(new_items)
        return True

    def nearest(
        self,
        from_date: date | None = None,
        limit: int = 5,
        category: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return upcoming holidays sorted by days-away, optionally filtered."""
        if from_date is None:
            from_date = date.today()

        items = self._load()
        if category:
            items = [i for i in items if i.get("category", "general") == category]

        scored: list[tuple[int, dict[str, Any]]] = []
        for item in items:
            m, d = item["month"], item["day"]
            try:
                holiday_date = date(from_date.year, m, d)
            except ValueError:
                continue
            delta = (holiday_date - from_date).days
            if delta < 0:
                try:
                    holiday_date = date(from_date.year + 1, m, d)
                    delta = (holiday_date - from_date).days
                except ValueError:
                    continue
            if delta < 0:
                continue
            scored.append((delta, item))

        scored.sort(key=lambda t: t[0])
        result = []
        for delta, item in scored[:limit]:
            result.append({**item, "days_away": delta})
        return result

    def upcoming_this_week(self) -> list[dict[str, Any]]:
        """Return holidays falling in the current week (Mon-Sun)."""
        today = date.today()
        monday = today - timedelta(days=today.weekday())
        sunday = monday + timedelta(days=6)

        items = self._load()
        result = []
        for item in items:
            m, d = item["month"], item["day"]
            try:
                holiday_date = date(today.year, m, d)
            except ValueError:
                continue
            if monday <= holiday_date <= sunday:
                delta = (holiday_date - today).days
                result.append({**item, "days_away": delta})
        return sorted(result, key=lambda x: x["days_away"])

    def _load(self) -> list[dict[str, Any]]:
        if not self._path.exists():
            return []
        with open(self._path, encoding="utf-8") as f:
            return json.load(f)

    def _save(self, items: list[dict[str, Any]]) -> None:
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
