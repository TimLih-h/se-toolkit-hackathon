# Holiday Agent

AI-powered holiday reminder agent — ask about holidays in natural language and get instant answers.

## Demo

**List all holidays:**
```
$ nanobot agent -c nanobot/config.json -m "Show me all holidays"

Here are all the holidays stored in the database:

🌍 International
| Date    | Holiday                     |
|---------|-----------------------------|
| Jan 1   | New Year's Day              |
| Feb 14  | Valentine's Day             |
| Mar 8   | International Women's Day   |
...

🏳️ National
| Date    | Holiday                     |
|---------|-----------------------------|
| May 9   | Victory Day                 |
| Jun 12  | Russia Day                  |
...

11 holidays in total.
```

**Add a new holiday:**
```
$ nanobot agent -c nanobot/config.json -m "Add my birthday on July 15 as personal"

Done! I've added your birthday on July 15 as a personal holiday. 🎂
```

**Find the nearest holiday:**
```
$ nanobot agent -c nanobot/config.json -m "What's the nearest holiday?"

The nearest upcoming holiday is Labour Day on May 1, which is 26 days away. 🎉
```

**Check this week:**
```
$ nanobot agent -c nanobot/config.json -m "Any holidays this week?"

There's one holiday this week: April Fools' Day (April 1).
```

## Product Context

**End users:** Students and team members who need to track upcoming holidays and important dates without manually checking calendars.

**Problem:** People forget upcoming holidays and need a quick way to check dates or add new ones — opening a calendar app is too slow for a simple question like "what's the next holiday?"

**Solution:** A conversational AI agent that understands natural language requests and manages a holiday database. Just ask in plain English — no commands to memorize.

## Features

### Implemented
- **List holidays** with category grouping (national, international, professional, personal)
- **Add holidays** via natural language with automatic category detection
- **Remove holidays** by exact name
- **Nearest upcoming holidays** with days-away countdown
- **This week check** — are there any holidays Mon-Sun?
- **Category filtering** — "Show me national holidays only"
- **Formatted output** — tables, emojis, grouped by category
- **Dockerized deployment** — all services run via docker-compose

### Not yet implemented
- Proactive scheduled notifications (cron-based reminders)
- Web chat interface (currently CLI-only)
- Recurring holidays (e.g., "every second Monday")
- Multi-user support with personal calendars

## Usage

### Quick query (one-shot)
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
# Then ask questions naturally:
# "What holidays are coming up?"
# "Add Teacher's Day on October 5th"
# "Any national holidays this month?"
```

## Deployment

**OS:** Ubuntu 24.04 (same as university VMs)

**Requirements:**
- Docker + Docker Compose
- Qwen OAuth credentials (via `/qwen_auth` in the autochecker Telegram bot)
- Python 3.14 + uv (for CLI testing)

### Step-by-step

1. **Clone the repository:**
```bash
git clone https://github.com/TimLih-h/se-toolkit-hackathon.git
cd se-toolkit-hackathon
```

2. **Create environment file:**
```bash
cp .env.docker.example .env.docker.secret
# Edit .env.docker.secret and set your values:
#   - QWEN_CODE_API_KEY (from autochecker bot)
#   - POSTGRES_PASSWORD
#   - LMS_API_KEY
```

3. **Authenticate Qwen Code API:**
Run `/qwen_auth` in the autochecker Telegram bot to push OAuth credentials to your VM.

4. **Start all services:**
```bash
docker compose --env-file .env.docker.secret up -d --build
```

5. **Verify services:**
```bash
curl -s http://localhost:42002/docs          # Backend Swagger UI (200)
curl -s http://localhost:42005/health        # LLM proxy (should show "healthy")
docker ps                                    # All 4 containers running
```

6. **Test the agent:**
```bash
PATH=~/.local/bin:$PATH uv run --project nanobot nanobot agent \
  -c nanobot/config.json -m "Show me all holidays"
```

### Services

| Service | Port | Purpose |
|---------|------|---------|
| Backend | 42002 | FastAPI LMS server |
| Qwen Code API | 42005 | LLM proxy (OpenAI-compatible) |
| Nanobot Gateway | 8082 | AI agent (CLI + webchat) |
| PostgreSQL | 5432 | Database |
