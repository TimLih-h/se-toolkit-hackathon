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


class NearestHolidayArgs(BaseModel):
    limit: int = Field(
        default=5, ge=1, le=30, description="Max holidays to return (default 5)."
    )


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
    entry = store.add(args.name, args.month, args.day)
    return {"added": entry, "message": f"Added '{entry['name']}' on {entry['month']}/{entry['day']}"}


async def _nearest_holiday(store: HolidayStore, args: BaseModel) -> ToolPayload:
    assert isinstance(args, NearestHolidayArgs)
    items = store.nearest(from_date=date.today(), limit=args.limit)
    if not items:
        return {"message": "No upcoming holidays found."}
    return {"holidays": items, "count": len(items)}


TOOL_SPECS: tuple[ToolSpec, ...] = (
    ToolSpec(
        "holidays_list",
        "List all holidays stored in the holiday database.",
        NoArgs,
        _list_holidays,
    ),
    ToolSpec(
        "holidays_add",
        "Add a new holiday with a name, month, and day.",
        AddHolidayArgs,
        _add_holiday,
    ),
    ToolSpec(
        "holidays_nearest",
        "Get the nearest upcoming holidays sorted by days away.",
        NearestHolidayArgs,
        _nearest_holiday,
    ),
)

TOOLS_BY_NAME: dict[str, ToolSpec] = {spec.name: spec for spec in TOOL_SPECS}
