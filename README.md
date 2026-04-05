# Holiday Agent

AI-powered holiday reminder agent -- ask about holidays in natural language and get instant answers.

## Product Context

**End users:** Students and team members who need to track upcoming holidays without checking calendars.

**Problem:** People forget holidays. Opening a calendar app for a simple question is too slow.

**Solution:** A conversational AI agent -- just ask in plain English, no commands to memorize.

## Architecture

- **Backend:** FastAPI LMS server (port 42002)
- **Database:** PostgreSQL (port 5432)
- **LLM Proxy:** qwen-code-api (port 42005) -- OpenAI-compatible endpoint for Qwen models
- **Webchat:** Browser-based chat UI with calendar, dashboard, ICS export (port 8083)

## Features

### Implemented

**Chat:**
- List holidays with category grouping
- Add holidays via 3-step flow (name -> date -> category)
- Remove holidays by name
- Find nearest upcoming holidays with countdown
- Check this week for holidays
- Category filtering (national, international, professional, personal)
- Strict holiday-only topic restriction

**Web UI:**
- Dashboard as default landing page
- Visual calendar with month navigation
- Per-user holiday data (isolated via cookies)
- Export to .ics file (Google/Apple Calendar)
- Dark theme by default
- Responsive layout with sticky header and input bar

**Infrastructure:**
- Dockerized (4 services)
- MIT License

### Not Yet Implemented
- Proactive cron-based notifications
- Mobile app
- Recurring holidays

## Usage

### Web Interface (recommended)
1. Open http://VM_IP:8083 in your browser
2. **Dashboard** -- statistics, countdown, charts
3. **Calendar** -- browse months, click holidays for descriptions
4. **Chat** -- ask questions in natural language
5. **Export** -- download .ics file for Google/Apple Calendar

### Example queries
- Show me all holidays
- What is the nearest holiday?
- Any holidays this week?
- Add Teachers Day on October 5 as professional

## Deployment

**OS:** Ubuntu 24.04

1. Clone: `git clone https://github.com/TimLih-h/se-toolkit-hackathon.git`
2. Create `.env.docker.secret` with your QWEN_CODE_API_KEY
3. Run `/qwen_auth` in the autochecker Telegram bot
4. Start: `docker compose --env-file .env.docker.secret up -d --build`
5. Open http://VM_IP:8083

### Services
| Service | Port | Purpose |
|---------|------|---------|
| Backend | 42002 | FastAPI LMS server |
| Qwen Code API | 42005 | LLM proxy |
| Webchat | 8083 | Browser-based UI |
| PostgreSQL | 5432 | Database |

## Per-User Data

Each visitor gets their own holiday database via browser cookie. First visit creates a unique ID with a copy of 11 base holidays. Changes only affect that user's data.

## Links

- **GitHub:** https://github.com/TimLih-h/se-toolkit-hackathon
