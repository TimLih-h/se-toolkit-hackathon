# Holiday Agent — Development Guide

You are helping build a holiday reminder agent using nanobot as the AI framework. The goal is a working product that users can talk to in natural language about holidays.

## Project structure

- `nanobot/` — the nanobot AI agent (gateway, config, skills)
  - `nanobot/bot.py` — not used (legacy from lab)
  - `nanobot/config.json` — agent configuration
  - `nanobot/entrypoint.py` — Docker entrypoint
  - `nanobot/Dockerfile` — Docker build
  - `nanobot/workspace/skills/` — skill prompts (holidays, lms)
- `mcp/mcp-holidays/` — Holiday MCP server (list, add, nearest)
- `mcp/mcp-lms/` — LMS MCP server (labs, learners, scores)
- `backend/` — FastAPI LMS backend
- `qwen-code-api/` — Qwen Code API proxy for LLM
- `docker-compose.yml` — All services

## Architecture

```
[User] → [Nanobot Agent] → [Qwen LLM]
              |
        +-----+------+
        |            |
  [LMS MCP]   [Holidays MCP]
        |            |
   [LMS API]    [holidays.json]
        |
   [Postgres]
```

## Key patterns

- **MCP (Model Context Protocol)** — tools are separate processes that the agent discovers and calls. Each MCP server exposes typed tools via a standard protocol.
- **Skill prompts** — natural language instructions that teach the agent *how* to use tools (strategy, formatting, error handling).
- **Handler separation** — MCP tools are plain functions. They work from CLI, tests, or the agent — same code.
- **Docker networking** — containers use service names (`backend`, `qwen-code-api`), not `localhost`.

## What NOT to do

- Don't hardcode URLs or API keys.
- Don't commit secrets.
- Don't create `requirements.txt` or use `pip`. Use `uv` and `pyproject.toml`.
- Don't implement features not in the current version scope.
- Don't use regex or keyword matching to decide which tool to call — let the LLM decide based on tool descriptions.
