"""Settings for the holidays MCP server."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel


class Settings(BaseModel):
    data_file: str = "holidays.json"


def resolve_data_file() -> Path:
    """Return the path to the holidays JSON file."""
    # Default: data/holidays.json relative to this package
    package_dir = Path(__file__).resolve().parent
    return package_dir.parent.parent / "data" / "holidays.json"
