# Holiday Agent — Presentation Slides

---

## Slide 1: Title

# Holiday Agent

**AI-powered holiday reminder via natural language**

Tim Lihonov
t.likhunov@innopolis.university
Group: [your group]

---

## Slide 2: Context

### End-user
Students and team members who need to track holidays

### Problem
People forget upcoming holidays. Opening a calendar app for a simple question ("what's next?") is too slow.

### Product idea in one sentence
Ask about holidays in plain English — get instant, formatted answers with no commands to memorize.

---

## Slide 3: Implementation

### How I built it
- **Nanobot** — AI agent gateway that calls LLM (Qwen) with MCP tools
- **MCP Servers** — `mcp-holidays` (5 tools) + `mcp-lms` (9 tools) as separate processes
- **FastAPI Backend** + **PostgreSQL** — existing LMS infrastructure
- **Skill prompts** — teach the agent how to use tools and format responses

### Version 1 (core)
- List all holidays via natural language
- Single MCP tool: `holidays_list`

### Version 2 (polished)
- Added 4 more tools: `holidays_add`, `holidays_remove`, `holidays_nearest`, `holidays_this_week`
- Holiday categories (national, international, professional, personal)
- Category filtering and grouped display
- Dockerized all 4 services (backend, postgres, qwen-code-api, nanobot)
- Deployed and accessible on VM

### TA feedback addressed
- [Will fill after TA review]

---

## Slide 4: Demo

**Pre-recorded video** (2 min max) showing:
1. `docker ps` — all 4 services running
2. `"Show me all holidays"` — formatted list with categories
3. `"Add my birthday on July 15 as personal"` — confirmation
4. `"What's the nearest holiday?"` — countdown response
5. `"Any holidays this week?"` — week check

*(Record this video separately and embed/link here)*

---

## Slide 5: Links

### GitHub Repository
https://github.com/TimLih-h/se-toolkit-hackathon

### Deployed Product
- Backend: http://<VM_IP>:42002/docs
- LLM Proxy: http://<VM_IP>:42005/health
- Agent: CLI via `nanobot agent -c nanobot/config.json`

### QR Codes
*(Generate QR codes for the URLs above)*
