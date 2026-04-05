"""Entry point for running the MCP server via python -m mcp_holidays."""

import asyncio

from mcp_holidays.server import main

if __name__ == "__main__":
    asyncio.run(main())
