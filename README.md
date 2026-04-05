# Holiday Agent

AI-powered holiday reminder agent built with nanobot, MCP tools, and FastAPI. Talk to it in natural language to manage holidays — view, add, remove, and track upcoming dates.

## Context

**End users:** Students and team members who need to track upcoming holidays and important dates.

**Problem:** People forget upcoming holidays and need a quick way to check dates or add new ones without opening a calendar app.

**Solution:** A conversational AI agent that understands natural language requests like "what holidays are coming up?" or "add Teacher's Day on October 5th" and manages a holiday database through MCP tools.

## Architecture

```
[User] ──CLI / Webchat──> [Nanobot Agent] ──> [Qwen LLM via qwen-code-api]
                                │
                        ┌───────┴───────┐
                        │               │
                  [LMS MCP]      [Holidays MCP]
                        │               │
                   [LMS API]       [holidays.json]
                        │
                   [PostgreSQL]
```

**Components:**
- **backend** — FastAPI LMS server with PostgreSQL
- **qwen-code-api** — LLM proxy (OpenAI-compatible endpoint for Qwen models)
- **nanobot** — AI agent gateway with MCP tool calling
- **mcp-holidays** — Holiday management MCP server (5 tools)
- **mcp-lms** — LMS data MCP server (9 tools)

## Features

### V1 (Core)
- **List holidays** — "Show me all holidays" → formatted list with categories
- **Add holiday** — "Add Teacher's Day on October 5th" → stored in database
- **Nearest holidays** — "What's the next holiday?" → countdown in days
- **Natural language** — powered by Qwen LLM, no commands to memorize

### V2 (Enhanced)
- **Categories** — national, international, professional, personal
- **Remove holidays** — "Remove April Fools' Day"
- **This week check** — "Any holidays this week?"
- **Category filtering** — "Show me national holidays"
- **Grouped display** — holidays organized by category with emojis

## Usage

### CLI mode (quick queries)
```bash
cd /root/se-toolkit-hackathon
PATH=~/.local/bin:$PATH uv run --project nanobot nanobot agent \
  -c nanobot/config.json -m "Show me all holidays"
```

### Interactive session
```bash
cd /root/se-toolkit-hackathon
PATH=~/.local/bin:$PATH uv run --project nanobot nanobot agent \
  -c nanobot/config.json
# Then ask questions interactively
```

### Example queries
- "Show me all holidays"
- "What's the nearest holiday?"
- "Add my birthday on July 15 as personal"
- "Any holidays this week?"
- "Show me national holidays only"
- "Remove Halloween"

## Deployment

### Requirements
- Ubuntu 24.04 VM with Docker + Docker Compose
- Qwen OAuth credentials (via `/qwen_auth` in autochecker bot)

### Step-by-step

1. Clone the repository:
```bash
git clone https://github.com/your-username/se-toolkit-hackathon.git
cd se-toolkit-hackathon
```

2. Create `.env.docker.secret`:
```bash
cp .env.docker.example .env.docker.secret
# Edit and set your QWEN_CODE_API_KEY, POSTGRES_PASSWORD, etc.
```

3. Authenticate Qwen Code API:
```bash
# Run on your VM — use /qwen_auth in the autochecker Telegram bot
# to push OAuth credentials
```

4. Start all services:
```bash
docker compose --env-file .env.docker.secret up -d --build
```

5. Wait ~30 seconds, then verify:
```bash
curl -s http://localhost:42002/docs          # Backend Swagger UI
curl -s http://localhost:42005/health        # LLM proxy (should be "healthy")
docker ps                                    # All 4 containers should be running
```

6. Test the agent:
```bash
PATH=~/.local/bin:$PATH uv run --project nanobot nanobot agent \
  -c nanobot/config.json -m "Show me all holidays"
```

### Services and ports
| Service | Port | Purpose |
|---------|------|---------|
| Backend | 42002 | LMS API (Swagger UI at `/docs`) |
| Qwen Code API | 42005 | LLM proxy |
| Nanobot Gateway | 8082 | AI agent (CLI + webchat) |
| PostgreSQL | 5432 | Database |

### MCP Tools

**Holidays (5 tools):**
| Tool | Args | Description |
|------|------|-------------|
| `holidays_list` | — | List all holidays with categories |
| `holidays_add` | name, month, day, category | Add a holiday |
| `holidays_remove` | name | Remove by exact name |
| `holidays_nearest` | limit, category | Upcoming holidays |
| `holidays_this_week` | — | Check current week |

**LMS (9 tools):**
| Tool | Description |
|------|-------------|
| `lms_health` | Backend health + item count |
| `lms_labs` | List available labs |
| `lms_learners` | List all learners |
| `lms_pass_rates` | Pass rates for a lab |
| `lms_timeline` | Submission timeline |
| `lms_groups` | Group performance |
| `lms_top_learners` | Top learners by score |
| `lms_completion_rate` | Completion rate |
| `lms_sync_pipeline` | Trigger data sync |
