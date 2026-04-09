# Slide 1 — Title

# Holiday Agent

**Tim Lihonov**  
t.likhunov@innopolis.university  
Group: [your group]

---

# Slide 2 — Context

### End-user
Students and team members who need to track upcoming holidays without checking calendars.

### Problem
People forget holidays. Opening a calendar app for "what's next?" is too slow.

### Product idea
A conversational AI agent with a visual web UI — ask about holidays in plain English, get instant answers.

---

# Slide 3 — Implementation

### How I built it
- **Nanobot** — AI agent gateway with LLM tool calling (Qwen)
- **MCP Servers** — `mcp-holidays` (5 tools) + `mcp-lms` (9 tools) as separate processes
- **FastAPI Backend** + **PostgreSQL** — LMS infrastructure
- **Webchat** — custom FastAPI+HTML frontend with calendar, dashboard, notifications

### Version 1 (core feature)
- List all holidays via natural language
- Single MCP tool: `holidays_list`

### Version 2 (polished)
- Web UI with dashboard, calendar, and chat
- Per-user holiday data via browser cookies
- ICS export with built-in reminders
- In-page toast notifications
- Category filtering, delete holidays, 3-step add flow

### TA feedback addressed
- [Will fill after TA review]

---

# Slide 4 — Demo

### Pre-recorded video (2 min max)
*(Embed or link your recorded video here)*

**What to show in the video:**
1. Open `http://VM_IP:8083` — dashboard loads with statistics and countdown
2. Click Calendar tab — browse months, click a holiday for description
3. Switch to Chat — ask "Show me all holidays" → formatted response
4. Click **+ Add** → add a holiday via 3-step flow
5. Click 🔔 notifications → see toast alert for upcoming holiday
6. Click **Export** → download `.ics` file
7. Delete a holiday via ✕ button on dashboard

---

# Slide 5 — Links

### GitHub Repository
https://github.com/TimLih-h/se-toolkit-hackathon

### Deployed Product
http://<VM_IP>:8083

### QR Codes
*(Generate QR codes for both URLs and paste here)*

---
