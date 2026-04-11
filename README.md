# Holiday Agent

AI-powered holiday reminder agent -- ask about holidays in natural language and manage your personal calendar through a web interface.

## Demo

Open **http://VM_IP:8083** in your browser. You'll see the dashboard by default with:

- Statistics and countdown to next holiday
- Visual calendar with color-coded badges
- Chat with natural language Q&A
- Export button to download .ics file for Google/Apple Calendar
- Notification bell for upcoming holidays within 3 days

### Adding a holiday
Click **+ Add** or type "Add Christmas on December 25 as international" -- the agent guides you through name, date, and category.

### Deleting a holiday
Click the red **x** button on the dashboard next to any holiday, or type "Remove Halloween" in chat.

## Product Context

### End users
Students and team members who need to track upcoming holidays without manually checking calendars or switching between apps.

### Problem
People forget upcoming holidays and need a quick way to check dates or add new ones. Opening a calendar app for a simple question like "what's the next holiday?" is too slow and friction-heavy.

### Solution
A conversational AI agent with a visual web UI and notification system. Just ask in plain English -- no commands to memorize. Each visitor gets their own personalized holiday database, isolated via browser cookies.

## Features

### Implemented
- **Dashboard** -- statistics, countdown timer, category pie chart, monthly bar chart
- **Calendar** -- visual month-by-month view with color-coded holiday badges
- **Chat** -- natural language Q&A powered by LLM (Qwen), guided 3-step flow for adding
- **Delete holidays** -- click button on dashboard or type "Remove [name]" in chat
- **In-page notifications** -- toast banners for upcoming holidays within 3 days
- **Export to .ics** -- download with built-in reminders (1 day and 1 hour before)
- **Per-user data** -- isolated holiday database via browser cookie
- **Category filtering** -- national, international, professional, personal
- **Dark theme** -- modern dark UI, responsive, sticky header and input bar

### Not yet implemented
- Proactive cron-based push notifications
- User login/authentication system
- Mobile app
- Recurring holidays

## Usage

### Web Interface (recommended)
1. Open `http://<VM_IP>:8083` in any browser
2. **Dashboard** -- statistics, countdown, charts (default page)
3. **Calendar** -- browse months, click holidays for descriptions
4. **Chat** -- ask in natural language, or use suggestion buttons
5. **Notifications** -- click bell icon to enable toast alerts
6. **Export** -- click download button for .ics file

### Example chat queries
- "Show me all holidays"
- "What is the nearest holiday?"
- "Any holidays this week?"
- "Add Teachers Day on October 5 as professional"
- "Show me national holidays only"
- "Remove Halloween"

## Deployment

### Which OS the VM should run on
Ubuntu 24.04 (same as university VMs)

### What should be installed on the VM
- **Docker** and **Docker Compose**
- **Git**
- Qwen OAuth credentials via `/qwen_auth` in the autochecker Telegram bot

### Step-by-step deployment instructions

1. **Clone the repository:**
```bash
git clone https://github.com/TimLih-h/se-toolkit-hackathon.git
cd se-toolkit-hackathon
```

2. **Create environment file:**
```bash
cp .env.docker.example .env.docker.secret
```
Edit `.env.docker.secret` and set your `QWEN_CODE_API_KEY`.

3. **Authenticate Qwen Code API:**
Run `/qwen_auth` in the autochecker Telegram bot to push OAuth credentials to your VM.

4. **Start all services:**
```bash
docker compose --env-file .env.docker.secret up -d --build
```

5. **Verify services:**
```bash
curl -s http://localhost:42002/docs          # Backend (200)
curl -s http://localhost:42005/health        # LLM proxy (healthy)
docker ps                                    # 4 containers
```

6. **Open web UI:** `http://<VM_IP>:8083`

### Services
| Service | Port | Purpose |
|---------|------|---------|
| Backend | 42002 | FastAPI LMS server |
| Qwen Code API | 42005 | LLM proxy (OpenAI-compatible) |
| Webchat | 8083 | Browser-based UI |
| PostgreSQL | 5432 | Database |

## Architecture

```
[User Browser] --> [Webchat UI :8083] --> [FastAPI Backend]
                                              |
                                        [LLM via Qwen API]
                                        [PostgreSQL]
                                              |
                                  [Per-user holiday data (cookies)]
```

## License

MIT License -- see [LICENSE](LICENSE) for details.
