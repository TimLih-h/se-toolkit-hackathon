"""Web chat interface for the Holiday Agent — v2 with calendar, dashboard, countdown, descriptions, and ICS export.

Self-contained: FastAPI + HTML + CSS + JS. No external dependencies beyond fastapi, uvicorn, httpx.
To remove: delete webchat/ directory and remove 'webchat' service from docker-compose.yml.
"""
import httpx
import json
import os
import uuid
from datetime import date, timedelta, datetime
from pathlib import Path
from email.utils import formatdate

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse

app = FastAPI()

# ── Config ──────────────────────────────────────────────────────────────
LLM_BASE_URL = os.environ.get("LLM_API_BASE_URL", "http://qwen-code-api:8080/v1")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "my-secret-qwen-key")
MODEL = os.environ.get("LLM_API_MODEL", "coder-model")

# ── Per-user holiday data ──────────────────────────────────────────────
USERS_DIR = Path("/app/data/users")
USERS_DIR.mkdir(parents=True, exist_ok=True)

# Default holidays template (copied for new users)
DEFAULT_HOLIDAYS = [
  {"name": "New Year's Day", "month": 1, "day": 1, "category": "international"},
  {"name": "Valentine's Day", "month": 2, "day": 14, "category": "international"},
  {"name": "International Women's Day", "month": 3, "day": 8, "category": "international"},
  {"name": "April Fools' Day", "month": 4, "day": 1, "category": "international"},
  {"name": "Labour Day", "month": 5, "day": 1, "category": "international"},
  {"name": "Victory Day", "month": 5, "day": 9, "category": "national"},
  {"name": "Russia Day", "month": 6, "day": 12, "category": "national"},
  {"name": "Halloween", "month": 10, "day": 31, "category": "international"},
  {"name": "Unity Day", "month": 11, "day": 4, "category": "national"},
  {"name": "Christmas", "month": 12, "day": 25, "category": "international"},
  {"name": "New Year's Eve", "month": 12, "day": 31, "category": "international"},
]

def _user_path(uid: str) -> Path:
    """Get or create a user's holiday data file."""
    p = USERS_DIR / f"{uid}.json"
    if not p.exists():
        with open(p, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_HOLIDAYS, f, indent=2)
    return p


def _load(uid: str):
    if not uid:
        return DEFAULT_HOLIDAYS[:]
    p = _user_path(uid)
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _save(uid: str, items):
    if not uid:
        return
    with open(_user_path(uid), "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


# Holiday descriptions
DESCRIPTIONS = {
    "New Year's Day": "Celebrates the start of the Gregorian calendar year with fireworks, family gatherings, and resolutions.",
    "Valentine's Day": "A day of love — exchange cards, flowers, and chocolates with your special someone.",
    "International Women's Day": "Honors women's achievements worldwide. Often marked with flowers, gifts, and social events.",
    "April Fools' Day": "A lighthearted day of pranks, jokes, and harmless deception. Don't believe everything you hear!",
    "Labour Day": "Celebrates workers and the labor movement. A day of rest and solidarity in many countries.",
    "Victory Day": "Commemorates the end of WWII in Europe. Marked by military parades, fireworks, and remembrance.",
    "Russia Day": "Russia's national day, celebrating the adoption of the Declaration of State Sovereignty in 1990.",
    "Halloween": "Spooky costumes, trick-or-treating, and carved pumpkins. A fun evening of frights and delights.",
    "Unity Day": "Celebrates national unity and the liberation of Moscow from Polish invaders in 1612.",
    "Christmas": "Celebrates the birth of Jesus Christ with family, gifts, decorated trees, and festive meals.",
    "New Year's Eve": "The last day of the year — countdown to midnight, champagne, and fresh beginnings!",
    "Teachers Day": "Honors educators and their dedication to shaping future generations. Say thank you to a teacher!",
    "Programmer's Day": "Celebrated on the 256th day of the year (Sep 13). Honors the binary-loving coders among us.",
}

def holidays_list(uid: str):
    items = _load(uid)
    return {"holidays": items, "count": len(items)}


def holidays_add(uid: str, name: str, month: int, day: int, category: str = "general"):
    items = _load(uid)
    entry = {"name": name, "month": month, "day": day, "category": category}
    items.append(entry)
    _save(uid, items)
    return {"added": entry}


def holidays_remove(uid: str, name: str):
    items = _load(uid)
    new = [i for i in items if i["name"].lower() != name.lower()]
    if len(new) == len(items):
        return {"message": f"Holiday '{name}' not found."}
    _save(uid, new)
    return {"message": f"Removed '{name}'."}


def holidays_nearest(uid: str, limit: int = 5, category: str | None = None):
    today = date.today()
    items = _load(uid)
    if category:
        items = [i for i in items if i.get("category") == category]
    scored = []
    for item in items:
        try:
            d = date(today.year, item["month"], item["day"])
        except ValueError:
            continue
        delta = (d - today).days
        if delta < 0:
            try:
                d = date(today.year + 1, item["month"], item["day"])
                delta = (d - today).days
            except ValueError:
                continue
        if delta < 0:
            continue
        scored.append((delta, item))
    scored.sort(key=lambda t: t[0])
    return {"holidays": [{**i, "days_away": d} for d, i in scored[:limit]]}


def holidays_this_week(uid: str):
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    items = _load(uid)
    result = []
    for item in items:
        try:
            d = date(today.year, item["month"], item["day"])
        except ValueError:
            continue
        if monday <= d <= sunday:
            result.append({**item, "days_away": (d - today).days})
    return sorted(result, key=lambda x: x["days_away"])


# ── Dashboard data ──────────────────────────────────────────────────────
def dashboard_data(uid: str):
    """Return statistics for the dashboard."""
    items = _load(uid)
    today = date.today()

    # Count by month
    by_month = [0] * 12
    for item in items:
        if 1 <= item["month"] <= 12:
            by_month[item["month"] - 1] += 1

    # Count by category
    by_cat = {}
    for item in items:
        cat = item.get("category", "general")
        by_cat[cat] = by_cat.get(cat, 0) + 1

    # Nearest holiday
    nearest = holidays_nearest(uid, limit=1)
    nearest_info = None
    if nearest.get("holidays"):
        h = nearest["holidays"][0]
        nearest_info = {**h, "description": DESCRIPTIONS.get(h["name"], "")}

    # Next 3 for countdown
    upcoming = holidays_nearest(uid, limit=3)

    return {
        "total": len(items),
        "by_month": by_month,
        "by_category": by_cat,
        "nearest": nearest_info,
        "upcoming": upcoming.get("holidays", []),
        "month_names": ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
        "today": today.isoformat(),
    }


# ── Calendar data ───────────────────────────────────────────────────────
def calendar_data(uid: str, year: int = None, month: int = None):
    today = date.today()
    if not year or not month:
        year, month = today.year, today.month

    items = _load(uid)
    holiday_map = {}
    for item in items:
        key = (item["month"], item["day"])
        holiday_map.setdefault(key, []).append(item)

    first_day = date(year, month, 1)
    if month == 12:
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(year, month + 1, 1) - timedelta(days=1)

    days = []
    start_weekday = first_day.weekday()  # 0=Mon
    for _ in range(start_weekday):
        days.append(None)
    for d in range(1, last_day.day + 1):
        key = (month, d)
        day_holidays = holiday_map.get(key, [])
        is_today = (year, month, d) == (today.year, today.month, today.day)
        days.append({
            "day": d,
            "holidays": day_holidays,
            "is_today": is_today,
        })

    return {
        "year": year,
        "month": month,
        "month_name": first_day.strftime("%B %Y"),
        "days": days,
    }


# ── ICS export ──────────────────────────────────────────────────────────
def generate_ics(uid: str):
    """Generate ICS file content for all holidays."""
    items = _load(uid)
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Holiday Agent//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
    ]
    for item in items:
        y = date.today().year
        try:
            d = date(y, item["month"], item["day"])
        except ValueError:
            continue
        dt = d.strftime("%Y%m%d")
        name = item["name"].replace(",", "\\,").replace(";", "\\;")
        cat = item.get("category", "general")
        desc = DESCRIPTIONS.get(item["name"], "").replace(",", "\\,")
        lines.extend([
            "BEGIN:VEVENT",
            f"DTSTART;VALUE=DATE:{dt}",
            f"SUMMARY:{name}",
            f"DESCRIPTION:{cat}: {desc}",
            f"CATEGORIES:{cat}",
            f"UID:holiday-{item['name'].lower().replace(' ','-')}@holidayagent",
            "END:VEVENT",
        ])
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)


# ── Tool definitions for LLM ────────────────────────────────────────────
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "holidays_list",
            "description": "List all holidays in the database with their categories.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "holidays_add",
            "description": "Add a new holiday. Requires name, month (1-12), day (1-31), optional category.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Holiday name"},
                    "month": {"type": "integer", "minimum": 1, "maximum": 12, "description": "Month number"},
                    "day": {"type": "integer", "minimum": 1, "maximum": 31, "description": "Day of month"},
                    "category": {"type": "string", "description": "national, international, professional, or personal", "default": "general"},
                },
                "required": ["name", "month", "day"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "holidays_nearest",
            "description": "Get upcoming holidays sorted by days away from today.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 5, "description": "Max results"},
                    "category": {"type": "string", "description": "Filter by category (optional)"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "holidays_this_week",
            "description": "Check for any holidays in the current week (Mon-Sun).",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "holidays_remove",
            "description": "Remove a holiday by exact name.",
            "parameters": {
                "type": "object",
                "properties": {"name": {"type": "string", "description": "Exact holiday name"}},
                "required": ["name"],
            },
        },
    },
]

TOOL_FUNCTIONS = {
    "holidays_list": lambda uid, _: holidays_list(uid),
    "holidays_add": lambda uid, a: holidays_add(uid, a["name"], a["month"], a["day"], a.get("category", "general")),
    "holidays_nearest": lambda uid, a: holidays_nearest(uid, a.get("limit", 5), a.get("category")),
    "holidays_this_week": lambda uid, _: holidays_this_week(uid),
    "holidays_remove": lambda uid, a: holidays_remove(uid, a["name"]),
}

SYSTEM = (
    "You are a holiday reminder assistant. You MUST ONLY answer questions about holidays. "
    "If the user asks about politics, weather, coding, math, or anything unrelated to holidays, "
    "respond exactly: 'I only answer questions about holidays.' "
    "Never call tools for non-holiday topics. Always use the available tools to provide accurate holiday information. "
    "Be concise and friendly, but never deviate from the holiday topic."
)

HOLIDAY_KEYWORDS = [
    "holiday", "holidays", "праздник", "праздники", "day", "день", "date", "дата",
    "upcoming", "ближайш", "calendar", "календарь", "add ", "удали", "remove",
    "list", "список", "show", "покажи", "when", "когда", "what day", "какой день",
    "add my", "add a", "add new", "add teacher", "add valentine", "add new year",
    "this week", "эта недел", "may ", "june", "july", "august", "september",
    "october", "november", "december", "january", "february", "march", "april",
    "май ", "июн", "июл", "август", "сентябр", "октябр", "ноябр", "декабр",
    "январ", "феврал", "март", "апрел",
]

def _is_holiday_topic(msg: str) -> bool:
    """Check if the message is related to holidays or likely a follow-up answer."""
    lower = msg.lower()
    # Short messages (1-3 words) are likely follow-up answers
    # e.g. "personal", "October 5", "yes", "March 15"
    word_count = len(lower.split())
    if word_count <= 3:
        return True
    # Check for holiday-related keywords
    return any(kw in lower for kw in HOLIDAY_KEYWORDS)


async def agent_loop(user_message: str, uid: str, max_iterations: int = 5) -> str:
    """Run the LLM tool-calling agent loop and return the final response."""
    if not _is_holiday_topic(user_message):
        return "I only answer questions about holidays. 🎄"

    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": user_message},
    ]

    async with httpx.AsyncClient(timeout=30) as http:
        for _ in range(max_iterations):
            try:
                resp = await http.post(
                    f"{LLM_BASE_URL}/chat/completions",
                    json={"model": MODEL, "messages": messages, "tools": TOOLS},
                    headers={"Authorization": f"Bearer {LLM_API_KEY}", "Content-Type": "application/json"},
                )
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                return f"Sorry, the LLM service is unavailable: {e}"

            choice = data.get("choices", [{}])[0].get("message", {})

            if choice.get("tool_calls"):
                messages.append(choice)
                for tc in choice["tool_calls"]:
                    fn_name = tc["function"]["name"]
                    try:
                        fn_args = json.loads(tc["function"]["arguments"])
                    except json.JSONDecodeError:
                        fn_args = {}
                    try:
                        result = TOOL_FUNCTIONS[fn_name](uid, fn_args)
                        content = json.dumps(result, ensure_ascii=False, indent=2)
                    except KeyError:
                        content = f"Error: Unknown tool '{fn_name}'"
                    except Exception as e:
                        content = f"Error: {type(e).__name__}: {e}"
                    messages.append({"role": "tool", "tool_call_id": tc["id"], "content": content})
            else:
                return choice.get("content") or "I don't have a response for that."

    return "Sorry, I couldn't complete that request."


# ── HTML UI ─────────────────────────────────────────────────────────────
HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Holiday Agent</title>
<style>
:root{--bg:#0d1117;--surface:#161b22;--surface2:#21262d;--border:#30363d;--text:#e6edf3;--text2:#8b949e;--accent:#58a6ff;--accent2:#1f6feb;--green:#3fb950;--orange:#f0883e;--red:#f85149;--pink:#f778ba;--purple:#bc8cff}
*{margin:0;padding:0;box-sizing:border-box}
html,body{height:100vh;overflow:hidden}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:var(--bg);color:var(--text);display:flex;flex-direction:column}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}

/* Header */
.hdr{background:var(--surface);border-bottom:1px solid var(--border);padding:12px 20px;display:flex;align-items:center;justify-content:space-between}
.hdr h1{font-size:1.1rem;font-weight:600;display:flex;align-items:center;gap:8px}
.hdr h1 span{font-size:1.3rem}
.tabs{display:flex;gap:4px}
.tabs button{padding:6px 14px;background:transparent;border:1px solid var(--border);border-radius:8px;color:var(--text2);cursor:pointer;font-size:.82rem;transition:all .15s}
.tabs button:hover{color:var(--text);border-color:var(--text2)}
.tabs button.on{background:var(--accent2);border-color:var(--accent2);color:#fff}

/* Views */
.view{display:none;flex:1;overflow:hidden;flex-direction:column}
.view.on{display:flex}

/* Countdown */
.countdown{background:linear-gradient(135deg,var(--accent2),#6e40c9);border-radius:16px;padding:24px;text-align:center;margin-bottom:16px;position:relative;overflow:hidden}
.countdown::before{content:'';position:absolute;top:-50%;left:-50%;width:200%;height:200%;background:radial-gradient(circle,rgba(255,255,255,.05) 0%,transparent 60%);animation:shimmer 8s infinite}
@keyframes shimmer{0%,100%{transform:translate(-30%,-30%)}50%{transform:translate(30%,30%)}}
.countdown .days{font-size:3.5rem;font-weight:700;line-height:1}
.countdown .label{font-size:.85rem;opacity:.8;margin-top:4px}
.countdown .holiday-name{font-size:1.1rem;font-weight:500;margin-bottom:8px}
.countdown .desc{font-size:.78rem;opacity:.7;margin-top:8px;font-style:italic}

/* Calendar */
.cal{background:var(--surface);border-radius:12px;padding:16px;margin-bottom:16px}
.cal-hdr{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px}
.cal-hdr h3{font-size:1rem;font-weight:600}
.cal-hdr button{background:var(--surface2);border:1px solid var(--border);color:var(--text);border-radius:6px;padding:4px 10px;cursor:pointer;font-size:.85rem}
.cal-hdr button:hover{background:var(--border)}
.cal-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:2px}
.cal-grid .dh{padding:6px;text-align:center;font-size:.72rem;color:var(--text2);font-weight:600}
.cal-grid .dc{min-height:56px;background:var(--surface2);border-radius:6px;padding:4px;position:relative}
.cal-grid .dc .dn{font-size:.78rem;font-weight:500;color:var(--text2)}
.cal-grid .dc.today{background:var(--accent2);border:1px solid var(--accent)}
.cal-grid .dc.today .dn{color:#fff}
.cal-grid .dc .hd{font-size:.6rem;padding:1px 3px;border-radius:3px;margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.cal-grid .dc .hd.national{background:#1a3a1a;color:var(--green)}
.cal-grid .dc .hd.international{background:#1a2a3a;color:var(--accent)}
.cal-grid .dc .hd.professional{background:#3a2a1a;color:var(--orange)}
.cal-grid .dc .hd.personal{background:#3a1a2a;color:var(--pink)}
.cal-grid .dc .hd.general{background:var(--border);color:var(--text2)}
.cal-grid .dc.empty{background:transparent;pointer-events:none}
.cal-grid .dc .hd:hover{filter:brightness(1.3)}

/* Dashboard */
.dash{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px}
.dash-card{background:var(--surface);border-radius:12px;padding:16px;border:1px solid var(--border)}
.dash-card h4{font-size:.82rem;color:var(--text2);margin-bottom:8px;font-weight:500}
.dash-card .big{font-size:2rem;font-weight:700;color:var(--accent)}
.dash-card .bar{height:8px;background:var(--surface2);border-radius:4px;overflow:hidden;margin-top:4px}
.dash-card .bar-fill{height:100%;background:var(--accent);border-radius:4px;transition:width .5s}
.cat-list{list-style:none}
.cat-list li{display:flex;justify-content:space-between;padding:4px 0;font-size:.85rem}
.cat-list li span{padding:2px 8px;border-radius:10px;font-size:.72rem}
.cat-list li .national{background:#1a3a1a;color:var(--green)}
.cat-list li .international{background:#1a2a3a;color:var(--accent)}
.cat-list li .professional{background:#3a2a1a;color:var(--orange)}
.cat-list li .personal{background:#3a1a2a;color:var(--pink)}
.upcoming-list{list-style:none}
.upcoming-list li{padding:6px 0;border-bottom:1px solid var(--border);font-size:.85rem;display:flex;justify-content:space-between}
.upcoming-list li:last-child{border:none}
.upcoming-list .daway{color:var(--orange);font-weight:600;font-size:.78rem}

/* ICS button */
.ics-btn{display:block;width:100%;padding:12px;background:var(--surface);border:1px solid var(--border);border-radius:12px;color:var(--text);cursor:pointer;text-align:center;font-size:.9rem;margin-bottom:16px;transition:all .15s}
.ics-btn:hover{background:var(--surface2);border-color:var(--accent)}
.ics-btn span{font-size:1.2rem;margin-right:6px}

/* Chat */
.chat{flex:1;display:flex;flex-direction:column;overflow:hidden;min-height:0}
.msgs{flex:1;overflow-y:auto;padding:4px 0;display:flex;flex-direction:column;gap:10px;min-height:0}
.msg{max-width:80%;padding:10px 14px;border-radius:16px;line-height:1.5;font-size:.9rem;word-wrap:break-word}
.msg.u{align-self:flex-end;background:var(--accent2);color:#fff;border-bottom-right-radius:4px}
.msg.b{align-self:flex-start;background:var(--surface);color:var(--text);border-bottom-left-radius:4px;border:1px solid var(--border)}
.typing{align-self:flex-start;background:var(--surface);padding:10px 14px;border-radius:16px;border:1px solid var(--border);color:var(--text2);font-size:.82rem}
.typing::after{content:'';animation:d 1.5s infinite}
@keyframes d{0%,33%{content:'.'}66%{content:'..'}100%{content:'...'}}
.inp{flex-shrink:0;background:var(--bg);padding:12px 0;display:flex;gap:8px;border-top:1px solid var(--border)}
.inp input{flex:1;padding:10px 16px;background:var(--surface);border:1px solid var(--border);border-radius:24px;color:var(--text);font-size:.9rem;outline:none}
.inp input:focus{border-color:var(--accent)}
.inp input::placeholder{color:var(--text2)}
.inp button{padding:10px 20px;background:var(--accent2);color:#fff;border:none;border-radius:24px;cursor:pointer;font-size:.9rem}
.inp button:hover{background:var(--accent)}
.inp button:disabled{background:var(--surface2);color:var(--text2);cursor:not-allowed}
.sug{flex-shrink:0;padding:8px 0;display:flex;gap:6px;flex-wrap:wrap}
.sug button{padding:4px 12px;background:var(--surface2);border:1px solid var(--border);border-radius:16px;color:var(--text2);cursor:pointer;font-size:.75rem;transition:all .15s}
.sug button:hover{color:var(--text);border-color:var(--accent)}

/* Responsive */
@media(max-width:640px){.dash{grid-template-columns:1fr}.cal{padding:12px}.countdown .days{font-size:2.5rem}}
</style>
</head>
<body>
<div class="hdr">
  <h1><span>&#127881;</span> Holiday Agent</h1>
  <div class="tabs">
    <button onclick="tab('chat')">&#128172; Chat</button>
    <button onclick="tab('cal')">&#128197; Calendar</button>
    <button class="on" onclick="tab('dash')">&#128202; Dashboard</button>
  </div>
</div>

<!-- Chat View -->
<div class="view" id="v-chat">
  <div class="chat">
    <div class="msgs" id="c"></div>
    <div class="sug">
      <button onclick="s('Show me all holidays')">&#128203; All holidays</button>
      <button onclick="s('What is the nearest holiday?')">&#128197; Next holiday</button>
      <button onclick="s('Any holidays this week?')">&#128198; This week</button>
      <button onclick="startAdd()">➕ Add</button>
    </div>
    <div class="inp">
      <input id="i" placeholder="Ask about holidays..." onkeydown="if(event.key==='Enter')send()">
      <button id="b" onclick="send()">Send</button>
    </div>
  </div>
</div>

<!-- Calendar View -->
<div class="view" id="v-cal">
  <div class="cal">
    <div class="cal-hdr">
      <button onclick="calNav(-1)">&#9664;</button>
      <h3 id="cal-title"></h3>
      <button onclick="calNav(1)">&#9654;</button>
    </div>
    <div class="cal-grid" id="cal-grid"></div>
  </div>
  <div id="cal-desc" style="font-size:.85rem;color:var(--text2);padding:0 4px"></div>
</div>

<!-- Dashboard View -->
<div class="view on" id="v-dash">
  <div id="dash-content">Loading...</div>
</div>

<script>
const sid='web:'+Math.random().toString(36).slice(2,11);
let calYear, calMonth;
let allHolidays=[];

// ── Add-holiday multi-turn state ──
let addState={step:0, name:'', month:'', day:'', category:''};

// ── Tab switching ──
function tab(name){
  document.querySelectorAll('.view').forEach(v=>v.classList.remove('on'));
  document.querySelectorAll('.tabs button').forEach(b=>b.classList.remove('on'));
  document.getElementById('v-'+name).classList.add('on');
  event.target.classList.add('on');
  if(name==='cal'){initCal();if(!allHolidays.length)loadDash()}
  if(name==='dash')loadDash();
}

// ── Chat ──
const c=document.getElementById('c'),i=document.getElementById('i'),b=document.getElementById('b');
function m(t,u){const d=document.createElement('div');d.className='msg '+(u?'u':'b');d.innerHTML=t.replace(/\*\*(.+?)\*\*/g,'<b>$1</b>').replace(/\n/g,'<br>');c.appendChild(d);c.scrollTop=c.scrollHeight}
function tp(){const d=document.createElement('div');d.className='typing';d.id='t';c.appendChild(d);c.scrollTop=c.scrollHeight}
function rt(){const e=document.getElementById('t');if(e)e.remove()}

// Handle add-holiday flow locally
function tryAddFlow(t){
  if(addState.step===1){
    // Got name
    addState.name=t;addState.step=2;
    m('What date? Reply like <b>October 5</b> or <b>month: 10, day: 5</b>.',false);
    return true;
  }
  if(addState.step===2){
    // Parse date
    const months={january:1,february:2,march:3,april:4,may:5,june:6,july:7,august:8,september:9,october:10,november:11,december:12,январь:1,февраль:2,март:3,апрель:4,май:5,июнь:6,июль:7,август:8,сентябрь:9,октябрь:10,ноябрь:11,декабрь:12};
    const lower=t.toLowerCase();
    let month=0,day=0;
    // Try "Month Day" format
    for(const[mn,mv] of Object.entries(months)){
      if(lower.includes(mn)){month=mv;break}
    }
    const dm=lower.match(/(\d{1,2})/);
    if(dm)day=parseInt(dm[1]);
    // Try "month: N, day: N" format
    const mm=lower.match(/month:\s*(\d+)/);
    const dd=lower.match(/day:\s*(\d+)/);
    if(mm)month=parseInt(mm[1]);
    if(dd)day=parseInt(dd[1]);
    if(!month||!day||month<1||month>12||day<1||day>31){
      m('Could not parse the date. Please use <b>Month Day</b> (e.g., <b>October 5</b>) or <b>month: 10, day: 5</b>.',false);
      return true; // stay in step 2
    }
    addState.month=month;addState.day=day;addState.step=3;
    m('What category? Reply: <b>national</b>, <b>international</b>, <b>professional</b>, or <b>personal</b>.',false);
    return true;
  }
  if(addState.step===3){
    const cats=['national','international','professional','personal','general'];
    const cat=cats.find(c=>t.toLowerCase().includes(c))||'general';
    addState.category=cat;addState.step=0;
    // Now call API to add
    (async()=>{
      try{
        const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:`Add ${addState.name} on month:${addState.month}, day:${addState.day}, category:${addState.category}`})});
        const d=await r.json();rt();m(d.response,false);
        addState={step:0,name:'',month:'',day:'',category:''};
      }catch(e){rt();m('Error: '+e.message,false)}
      i.disabled=false;b.disabled=false;i.focus();
    })();
    return true;
  }
  return false; // not in add flow
}

async function send(){
  const t=i.value.trim();if(!t)return;i.value='';m(t,true);
  // Check if we're in the add-holiday flow
  if(tryAddFlow(t))return;
  i.disabled=true;b.disabled=true;tp();
  try{const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:t,session_id:sid})});const d=await r.json();rt();m(d.response,false)}catch(e){rt();m('Error: '+e.message,false)}
  i.disabled=false;b.disabled=false;i.focus()
}
function s(t){
  // If user clicks an add suggestion, start the add flow
  if(t.startsWith('Add ')){addState.step=1;addState.name=''}
  i.value=t;send()
}

// Override the add suggestion button to start the flow
function startAdd(){
  addState={step:1,name:'',month:'',day:'',category:''};
  m("Let's add a new holiday! What should it be called?",false);
  i.focus();
}
m("Hi! I'm your Holiday Agent &#127881;<br>Ask about upcoming holidays or add new ones!",false);
loadDash();

// ── Calendar ──
function initCal(){
  const now=new Date();calYear=now.getFullYear();calMonth=now.getMonth()+1;
  renderCal();
}
function calNav(dir){calMonth+=dir;if(calMonth>12){calMonth=1;calYear++}if(calMonth<1){calMonth=12;calYear--}renderCal()}
async function renderCal(){
  const r=await fetch('/api/calendar?year='+calYear+'&month='+calMonth);
  const d=await r.json();
  document.getElementById('cal-title').textContent=d.month_name;
  const g=document.getElementById('cal-grid');
  g.innerHTML='<div class="dh">Mon</div><div class="dh">Tue</div><div class="dh">Wed</div><div class="dh">Thu</div><div class="dh">Fri</div><div class="dh">Sat</div><div class="dh">Sun</div>';
  d.days.forEach(day=>{
    if(!day){g.innerHTML+='<div class="dc empty"></div>';return}
    const el=document.createElement('div');
    el.className='dc'+(day.is_today?' today':'');
    let h='';
    day.holidays.forEach(hd=>{
      const cat=(hd.category||'general').toLowerCase();
      const desc=DESCRIPTIONS[hd.name]||'';
      h+=`<div class="hd ${cat}" title="${hd.name}: ${desc}">${hd.name}</div>`;
    });
    el.innerHTML=`<div class="dn">${day.day}</div>`+h;
    el.onclick=()=>{if(day.holidays.length)showCalDesc(day.holidays)};
    g.appendChild(el);
  });
  document.getElementById('cal-desc').innerHTML='';
}
function showCalDesc(holidays){
  const el=document.getElementById('cal-desc');
  el.innerHTML=holidays.map(h=>{
    const desc=DESCRIPTIONS[h.name]||'No description available.';
    return `<div style="margin-bottom:12px"><b>${h.name}</b> (${h.category||'general'})<br><span style="font-size:.78rem;color:var(--text2)">${desc}</span></div>`;
  }).join('');
}

// ── Dashboard ──
async function loadDash(){
  const r=await fetch('/api/dashboard');const d=await r.json();
  allHolidays=d;
  const maxMonth=Math.max(...d.by_month,1);
  const catHTML=Object.entries(d.by_category).map(([cat,cnt])=>{
    const pct=Math.round(cnt/d.total*100);
    return `<li>${cat} <span class="${cat}">${cnt} (${pct}%)</span></li>`;
  }).join('');
  const monthBars=d.by_month.map((cnt,i)=>{
    const pct=Math.round(cnt/maxMonth*100);
    return `<div style="display:flex;align-items:center;gap:6px;font-size:.75rem"><span style="width:24px">${d.month_names[i]}</span><div class="bar" style="flex:1"><div class="bar-fill" style="width:${pct}%"></div></div><span style="width:16px;text-align:right;color:var(--text2)">${cnt}</span></div>`;
  }).join('');
  const upcomingHTML=d.upcoming.map(h=>{
    const desc=DESCRIPTIONS[h.name]||'';
    return `<li><div><b>${h.name}</b> <span style="color:var(--text2);font-size:.75rem">(${h.category||''})</span><br><span style="font-size:.75rem;color:var(--text2);font-style:italic">${desc}</span></div><span class="daway">${h.days_away}d</span></li>`;
  }).join('');
  const nearest=d.nearest?`<div class="countdown"><div class="holiday-name">Next: ${d.nearest.name}</div><div class="days">${d.nearest.days_away}</div><div class="label">days away</div>${d.nearest.description?`<div class="desc">"${d.nearest.description}"</div>`:''}</div>`:'';
  document.getElementById('dash-content').innerHTML=`
    ${nearest}
    <button class="ics-btn" onclick="downloadICS()"><span>&#128190;</span>Export all holidays to Calendar (.ics)</button>
    <div class="dash">
      <div class="dash-card"><h4>Total Holidays</h4><div class="big">${d.total}</div></div>
      <div class="dash-card"><h4>By Category</h4><ul class="cat-list">${catHTML}</ul></div>
      <div class="dash-card"><h4>Upcoming Holidays</h4><ul class="upcoming-list">${upcomingHTML}</ul></div>
      <div class="dash-card"><h4>Holidays by Month</h4>${monthBars}</div>
    </div>`;
}
async function downloadICS(){
  const r=await fetch('/api/ics');const text=await r.text();
  const blob=new Blob([text],{type:'text/calendar'});
  const url=URL.createObjectURL(blob);
  const a=document.createElement('a');a.href=url;a.download='holidays.ics';a.click();URL.revokeObjectURL(url);
}

// ── Holiday descriptions ──
const DESCRIPTIONS = __DESC_PLACEHOLDER__;
</script>
</body>
</html>"""


# ── Routes ──────────────────────────────────────────────────────────────
def _get_uid(request: Request) -> str:
    """Get or create user ID from cookie."""
    uid = request.cookies.get("holiday_uid")
    if not uid:
        uid = str(uuid.uuid4())[:12]
    return uid


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    uid = _get_uid(request)
    page = HTML_PAGE.replace("__DESC_PLACEHOLDER__", json.dumps(DESCRIPTIONS))
    resp = HTMLResponse(content=page)
    resp.set_cookie("holiday_uid", uid, max_age=365*24*3600, httponly=True)
    return resp


@app.post("/api/chat")
async def chat_endpoint(request: Request):
    uid = _get_uid(request)
    body = await request.json()
    msg = body.get("message", "").strip()
    if not msg:
        return {"response": "Please type a message."}
    resp = await agent_loop(msg, uid)
    return {"response": resp}


@app.get("/api/dashboard")
async def dashboard_endpoint(request: Request):
    uid = _get_uid(request)
    return dashboard_data(uid)


@app.get("/api/calendar")
async def calendar_endpoint(request: Request, year: int = 0, month: int = 0):
    uid = _get_uid(request)
    return calendar_data(uid, year or None, month or None)


@app.get("/api/ics")
async def ics_endpoint(request: Request):
    uid = _get_uid(request)
    ics_content = generate_ics(uid)
    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={
            "Content-Disposition": "attachment; filename=holidays.ics",
            "Last-Modified": formatdate(usegmt=True),
        },
    )
