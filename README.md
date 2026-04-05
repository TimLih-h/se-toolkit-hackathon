# Holiday Agent

An AI-powered holiday reminder agent built with nanobot, MCP tools, and a FastAPI backend. Talk to it in natural language to view, add, and track holidays.

## Demo

![Screenshot](docs/screenshot.png)

## Context

**End users:** Students and team members who need to track upcoming holidays and important dates.

**Problem:** People forget upcoming holidays and need a quick way to check dates or add new ones without opening a calendar app.

**Solution:** A conversational agent that understands natural language requests like "what holidays are coming up?" or "add Teacher's Day on October 5th" and manages a holiday database through MCP tools.

## Features

### Implemented (V1)
- **List holidays** — ask "show me all holidays" to see the full calendar
- **Add a holiday** — say "add Valentine's Day on February 14" to insert into the database
- **Nearest holidays** — ask "what's the next holiday?" to find the closest upcoming date
- **Natural language interface** — powered by Qwen LLM via nanobot agent
- **MCP tool architecture** — clean separation between agent logic and data access

### Planned (V2)
- Proactive notifications via cron-scheduled health checks
- Holiday categories and custom calendars
- Persisted additions (JSON file → SQLite)
- Web chat UI via WebSocket channel

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

**Components:**
- **Backend** — FastAPI LMS server (provides labs data via MCP)
- **Database** — PostgreSQL (backend data) + JSON file (holidays)
- **Agent** — nanobot gateway with Qwen LLM, MCP tools, and skill prompts
- **LLM Proxy** — qwen-code-api (OpenAI-compatible endpoint)

## Usage

### CLI mode
```bash
cd nanobot
uv run nanobot agent --logs -c config.json -m "Show me all holidays"
uv run nanobot agent --logs -c config.json -m "Add New Year on January 1"
uv run nanobot agent --logs -c config.json -m "What is the nearest holiday?"
```

### Interactive session
```bash
cd nanobot
uv run nanobot agent --logs -c config.json
# Then type your questions interactively
```

## Deployment

### Requirements
- Ubuntu 24.04 VM
- Docker + Docker Compose
- Qwen Code API credentials (`~/.qwen/` directory with auth)

### Step-by-step

1. Clone the repository:
```bash
git clone https://github.com/your-username/se-toolkit-hackathon.git
cd se-toolkit-hackathon
```

2. Set up credentials:
```bash
# Copy your Qwen Code API credentials to ~/.qwen/
mkdir -p ~/.qwen
echo "your-api-key" > ~/.qwen/openai_api_key
```

3. Set environment variables:
```bash
export LLM_API_KEY="your-qwen-key"
export LMS_API_KEY="secret-key"
export POSTGRES_PASSWORD="postgres"
export QWEN_CODE_API_KEY="your-qwen-key"
```

4. Start all services:
```bash
docker compose up -d --build
```

5. Wait for services to be healthy (~30s), then test:
```bash
docker compose exec nanobot nanobot gateway --config /app/nanobot/config.resolved.json --workspace /app/nanobot/workspace -m "Show me all holidays"
```

### Services and ports
| Service | Port | Purpose |
|---------|------|---------|
| Backend | 42002 | LMS API |
| Qwen Code API | 42005 | LLM proxy |
| Nanobot Gateway | 8082 | Agent gateway |
| PostgreSQL | 5432 | Database |
