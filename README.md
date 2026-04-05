# Holiday Agent

AI-powered holiday reminder agent -- ask about holidays in natural language and get instant answers via web UI.

## Demo

Open **http://VM_IP:8083** in your browser. You'll see:

- **Dashboard** (default page) -- statistics, countdown to next holiday, charts
- **Calendar** -- visual month-by-month view with color-coded holidays
- **Chat** -- natural language Q&A about holidays
- **Export** -- download your holidays as `.ics` for Google/Apple Calendar

### Example chat queries
- "Show me all holidays"
- "What is the nearest holiday?"
- "Any holidays this week?"
- "Add Teachers Day on October 5 as professional"
- "Show me national holidays only"

### Adding a holiday (3-step flow)
1. Click **+ Add** or type any add request
2. Bot asks for **name** -> you reply
3. Bot asks for **date** -> you reply (e.g., "October 5")
4. Bot asks for **category** -> you reply (e.g., "professional")
5. Holiday added to your personal database

## Product Context

**End users:** Students and team members who need to track upcoming holidays without checking calendars.

**Problem:** People forget holidays. Opening a calendar app for a simple question is too slow.

**Solution:** A conversational AI agent with a visual web UI -- just ask in plain English, no commands to memorize. Each visitor gets their own personalized holiday database.

## Architecture

- **Backend** -- FastAPI LMS server (port 42002)
- **Database** -- PostgreSQL (port 5432)
- **LLM Proxy** -- qwen-code-api (port 42005) -- OpenAI-compatible endpoint for Qwen models
- **Webchat** -- Browser-based UI with chat, calendar, dashboard, ICS export (port 8083)

## Features

### Chat
- List holidays grouped by category
- Add holidays via guided 3-step flow (name -> date -> category)
- Remove holidays by name
- Find nearest upcoming holiday with countdown
- Check current week for holidays
- Category filtering (national, international, professional, personal)
- Holiday-only topic restriction (short replies always pass through)

### Web UI
- Dashboard as default landing page (stats, countdown, bar charts, category pie)
- Visual calendar with month navigation and color-coded holiday badges
- Per-user holiday data via browser cookie -- each visitor gets their own isolated database
- Export all holidays to `.ics` file (import into Google/Apple Calendar)
- Dark theme by default
- Responsive layout with sticky header and input bar

### Infrastructure
- Docker Compose with 4 services
- MIT License
- Open-source on GitHub

### Not Yet Implemented
- Proactive cron-based push notifications
- User login/authentication system
- Mobile app
- Recurring holidays (e.g., "every second Monday")

## Usage

### Web Interface (recommended)
1. Open `http://<VM_IP>:8083` in any browser
2. Browse the dashboard, calendar, or chat
3. Click the `.ics` button to export your holidays

### CLI (advanced)
```bash
cd /root/se-toolkit-hackathon
PATH=~/.local/bin:$PATH uv run --project nanobot nanobot agent \
  -c nanobot/config.json -m "Show me all holidays"
```

## Deployment

**OS:** Ubuntu 24.04

**Requirements:**
- Docker + Docker Compose
- Qwen OAuth credentials (via `/qwen_auth` in the autochecker Telegram bot)

### Step-by-step

1. Clone:
```bash
git clone https://github.com/TimLih-h/se-toolkit-hackathon.git
cd se-toolkit-hackathon
```

2. Create `.env.docker.secret` with your `QWEN_CODE_API_KEY`

3. Authenticate: run `/qwen_auth` in the autochecker Telegram bot

4. Start:
```bash
docker compose --env-file .env.docker.secret up -d --build
```

5. Verify:
```bash
curl -s http://localhost:42002/docs          # Backend (200)
curl -s http://localhost:42005/health        # LLM proxy (healthy)
docker ps                                    # 4 containers
```

6. Open `http://<VM_IP>:8083`

### Services
| Service | Port | Purpose |
|---------|------|---------|
| Backend | 42002 | FastAPI LMS server |
| Qwen Code API | 42005 | LLM proxy (OpenAI-compatible) |
| Webchat | 8083 | Browser-based UI (chat + calendar + dashboard) |
| PostgreSQL | 5432 | Database |

## Per-User Data

Каждый пользователь получает персональную базу праздников, автоматически привязанную к уникальному cookie браузера -- добавления и удаления влияют только на его данные.

- First visit: unique ID generated, copy of 11 base holidays
- Adding/removing: affects only that user's file
- Next visit (same browser): same personalized data
- Different browser/device: fresh database

## Links

- **GitHub:** https://github.com/TimLih-h/se-toolkit-hackathon
