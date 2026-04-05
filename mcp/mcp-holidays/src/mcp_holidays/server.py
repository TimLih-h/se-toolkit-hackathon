"""Stdio MCP server exposing holiday management as typed tools."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from pydantic import BaseModel

from mcp_holidays.settings import resolve_data_file
from mcp_holidays.store import HolidayStore
from mcp_holidays.tools import TOOL_SPECS, TOOLS_BY_NAME, ToolPayload


def _text(data: ToolPayload) -> list[TextContent]:
    if isinstance(data, BaseModel):
        payload = data.model_dump()
    else:
        payload = data
    return [TextContent(type="text", text=json.dumps(payload, ensure_ascii=False))]


def create_server(store: HolidayStore) -> Server:
    server = Server("holidays")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [spec.as_tool() for spec in TOOL_SPECS]

    @server.call_tool()
    async def call_tool(
        name: str, arguments: dict[str, Any] | None
    ) -> list[TextContent]:
        spec = TOOLS_BY_NAME.get(name)
        if spec is None:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
        try:
            args = spec.model.model_validate(arguments or {})
            return _text(await spec.handler(store, args))
        except Exception as exc:
            return [
                TextContent(type="text", text=f"Error: {type(exc).__name__}: {exc}")
            ]

    _ = list_tools, call_tool
    return server


async def main() -> None:
    data_file = resolve_data_file()
    store = HolidayStore(data_file)
    server = create_server(store)
    async with stdio_server() as (read_stream, write_stream):
        init_options = server.create_initialization_options()
        await server.run(read_stream, write_stream, init_options)


if __name__ == "__main__":
    asyncio.run(main())
