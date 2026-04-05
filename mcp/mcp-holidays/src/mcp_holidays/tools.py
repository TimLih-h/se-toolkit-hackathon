"""Tool schemas, handlers, and registry for the holidays MCP server."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass
from datetime import date
from typing import Any

from mcp.types import Tool
from pydantic import BaseModel, Field

from mcp_holidays.store import HolidayStore

ToolPayload = BaseModel | Sequence[BaseModel] | dict[str, Any]
ToolHandler = Callable[[HolidayStore, BaseModel], Awaitable[ToolPayload]]


class NoArgs(BaseModel):
    """Empty input model for tools that don't need arguments."""


class AddHolidayArgs(BaseModel):
    name: str = Field(description="Name of the holiday, e.g. 'New Year's Day'.")
    month: int = Field(description="Month number (1-12).", ge=1, le=12)
    day: int = Field(description="Day of month (1-31).", ge=1, le=31)
    category: str = Field(
        default="general",
        description="Category: national, international, professional, personal.",
    )


class RemoveHolidayArgs(BaseModel):
    name: str = Field(description="Exact name of the holiday to remove.")


class NearestHolidayArgs(BaseModel):
    limit: int = Field(
        default=5, ge=1, le=30, description="Max holidays to return (default 5)."
    )
    category: str | None = Field(
        default=None,
        description="Filter by category (optional).",
    )


class UpcomingThisWeekArgs(BaseModel):
    pass


@dataclass(frozen=True, slots=True)
class ToolSpec:
    name: str
    description: str
    model: type[BaseModel]
    handler: ToolHandler

    def as_tool(self) -> Tool:
        schema = self.model.model_json_schema()
        schema.pop("$defs", None)
        schema.pop("title", None)
        return Tool(name=self.name, description=self.description, inputSchema=schema)


async def _list_holidays(store: HolidayStore, _args: BaseModel) -> ToolPayload:
    items = store.list_all()
    return {"holidays": items, "count": len(items)}


async def _add_holiday(store: HolidayStore, args: BaseModel) -> ToolPayload:
    assert isinstance(args, AddHolidayArgs)
    entry = store.add(args.name, args.month, args.day, category=args.category)
    return {
        "added": entry,
        "message": f"Added '{entry['name']}' ({entry['category']}) on {entry['month']}/{entry['day']}",
    }


async def _remove_holiday(store: HolidayStore, args: BaseModel) -> ToolPayload:
    assert isinstance(args, RemoveHolidayArgs)
    removed = store.remove(args.name)
    if removed:
        return {"message": f"Removed '{args.name}'."}
    return {"message": f"Holiday '{args.name}' not found."}


async def _nearest_holiday(store: HolidayStore, args: BaseModel) -> ToolPayload:
    assert isinstance(args, NearestHolidayArgs)
    items = store.nearest(
        from_date=date.today(), limit=args.limit, category=args.category
    )
    if not items:
        filter_msg = f" in category '{args.category}'" if args.category else ""
        return {"message": f"No upcoming holidays found{filter_msg}."}
    return {"holidays": items, "count": len(items)}


async def _upcoming_this_week(store: HolidayStore, _args: BaseModel) -> ToolPayload:
    items = store.upcoming_this_week()
    if not items:
        return {"message": "No holidays this week."}
    return {"holidays": items, "count": len(items)}


TOOL_SPECS: tuple[ToolSpec, ...] = (
    ToolSpec(
        "holidays_list",
        "List all holidays stored in the holiday database with their categories.",
        NoArgs,
        _list_holidays,
    ),
    ToolSpec(
        "holidays_add",
        "Add a new holiday to the database. Requires name, month (1-12), day (1-31), and optional category (national, international, professional, personal).",
        AddHolidayArgs,
        _add_holiday,
    ),
    ToolSpec(
        "holidays_remove",
        "Remove a holiday by its exact name.",
        RemoveHolidayArgs,
        _remove_holiday,
    ),
    ToolSpec(
        "holidays_nearest",
        "Get upcoming holidays sorted by days away from today. Optionally filter by category.",
        NearestHolidayArgs,
        _nearest_holiday,
    ),
    ToolSpec(
        "holidays_this_week",
        "Check if there are any holidays in the current week (Mon-Sun).",
        UpcomingThisWeekArgs,
        _upcoming_this_week,
    ),
)

TOOLS_BY_NAME: dict[str, ToolSpec] = {spec.name: spec for spec in TOOL_SPECS}
