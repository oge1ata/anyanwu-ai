# Anyanwu AI Coach — Full Project Overview

> Written for the author to re-orient quickly. Covers everything built, every decision made, and what comes next.

---

## What This Is

Anyanwu is a personal AI coaching app. Not a chatbot. Not a therapy assistant. The persona is a big sister — someone who is older, sharper, has been through it, and will not let you wallow. She's direct and warm, but zero fluff.

The project was built and documented publicly as a 3-part series on Medium by @yomacorp:

- **Part 1** (published): The Brain — FastAPI backend, Anyanwu's personality, AI prompt and response logic
- **Part 2** (published): The Face — Chat UI, localStorage persistence, PWA groundwork (manifest, service worker)
- **Part 3** (in progress): Deployment — Taking it from localhost to a real accessible app

The name "Anyanwu" is an Igbo word meaning "sun." The emoji ☀️ appears next to her name in every message.

---

## The Problem It Solves

Generic AI chatbots default to therapist mode. They say things like "It's really brave of you to share that," give you numbered bullet lists, ask five questions at the end of every message, and let you stay comfortable in the problem. That's not coaching — that's validation theater.

Anyanwu is built to do the opposite: name what's happening, give one clear take, suggest one concrete step, and ask the one question that matters. She pushes. She notices avoidance. She doesn't let you off easy.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend language | Python 3 |
| Web framework | FastAPI |
| Server | uvicorn |
| AI model | OpenAI API — gpt-4o-mini (configurable) |
| Scheduler | APScheduler (BackgroundScheduler) |
| Memory storage | JSON file — `backend/data/memory.json` |
| Daily log storage | JSON file — `backend/data/daily_log.json` |
| Scheduled message queue | JSON file — `backend/data/pending_messages.json` |
| Frontend | Vanilla JS, HTML5, CSS3 — no frameworks |
| Fonts | Orbitron (headers), Space Mono (body) — Google Fonts |
| PWA groundwork | manifest.json, service_worker.js (not yet active) |
| Environment | python-dotenv, `.env` file |

Everything is intentionally minimal. No database, no ORM, no frontend framework. JSON files for storage. Vanilla JS for the UI. This keeps the codebase readable for the Medium audience and easy to follow part by part.

---

## Project Structure

```
AnyanwuAICoach/
├── backend/
│   ├── main.py                    # FastAPI app — routes, CORS, validation, lifespan
│   ├── services/
│   │   ├── ai_agent.py            # chat_with_anyanwu() — the OpenAI call
│   │   ├── memory_manager.py      # Load/save conversation history (500 msg cap)
│   │   ├── scheduler.py           # APScheduler — 5am wake-up, 9pm check-in jobs
│   │   └── daily_log.py           # Daily activity log + pending message queue
│   ├── utils/
│   │   └── system_prompt.py       # Anyanwu's full personality prompt
│   └── data/                      # Runtime data — all gitignored
│       ├── memory.json            # Rolling conversation history
│       ├── daily_log.json         # Daily activity entries by date
│       └── pending_messages.json  # Scheduled messages waiting to be delivered
├── frontend/
│   ├── index.html                 # Single-page app shell
│   ├── script.js                  # All frontend logic
│   ├── style.css                  # Night Pink theme
│   ├── manifest.json              # PWA manifest (icons, name, display mode)
│   └── service_worker.js          # PWA service worker (exists, not yet registered)
├── requirements.txt               # Python dependencies
├── .env                           # gitignored — OPENAI_API_KEY lives here
├── .gitignore
├── COMMIT_NOTES.md                # Changelog for commits
├── PROJECT_OVERVIEW.md            # This file
└── CLAUDE.md                      # Context for the AI assistant (Claude Code)
```

---

## Backend — How It Works

### Entry point: `main.py`

FastAPI app with a lifespan handler. On startup, `start_scheduler()` is called — this registers the 5am and 9pm background jobs before the first request is served. On shutdown, `stop_scheduler()` cleans up the scheduler thread.

CORS is locked down. `allow_origins` reads from the `ALLOWED_ORIGINS` environment variable, which defaults to localhost ports 3000 and 80. In production, this gets updated to the deployed frontend URL. Methods are restricted to `POST` and `GET`. Headers are restricted to `Content-Type`.

Input validation: messages over 2000 characters return HTTP 400. Empty `/log` entries also return 400.

### API Endpoints

| Method | Route | What it does |
|---|---|---|
| `GET` | `/` | Health check — returns a confirmation message |
| `POST` | `/chat` | Sends a message to Anyanwu, gets her reply |
| `GET` | `/check-in` | Returns pending scheduled messages and clears the queue |
| `POST` | `/log` | Logs an activity entry for today |
| `GET` | `/log` | Returns the full activity log, or one day via `?day=YYYY-MM-DD` |

### AI Agent: `ai_agent.py`

`chat_with_anyanwu(user_message)` is the core function. It:
1. Loads conversation history from `memory.json`
2. Appends the new user message
3. Calls the OpenAI API with the full history + system prompt
4. Appends Anyanwu's reply to the history
5. Saves the updated history back to `memory.json`
6. Returns the reply text

The OpenAI model is configurable via the `ANYANWU_MODEL` environment variable. Defaults to `gpt-4o-mini`.

### Memory: `memory_manager.py`

Conversation history is stored as a list of `{role, content}` dicts in `memory.json`. A 500-message rolling cap prevents the file from growing unbounded. When the cap is hit, the oldest messages are dropped first. The system prompt is NOT stored in the file — it's injected fresh on every API call so it can be updated without clearing history.

### Scheduler: `scheduler.py`

APScheduler's `BackgroundScheduler` runs two jobs in a background thread while FastAPI serves requests normally:

**5:00 AM — `morning_checkin()`**
Queues the message: *"You should be up by now. What's the plan for today?"*

**9:00 PM — `evening_checkin()`**
Calls `get_today_summary()` to check what the user logged today. Two paths:
- If entries exist: queues a message that includes the summary and asks what didn't get done
- If no entries: calls it out directly — *"9pm. You haven't logged anything today..."*

The scheduler doesn't push directly to the browser (that requires HTTPS + service worker, which needs deployment). Instead, messages sit in `pending_messages.json` until the user opens the app.

### Daily Log: `daily_log.py`

Manages two JSON files with a threading lock to prevent corruption on concurrent requests.

**`daily_log.json`** — structure:
```json
{
  "2026-03-27": ["finished the log UI", "wrote commit notes"],
  "2026-03-26": ["deployed to Render"]
}
```

**`pending_messages.json`** — a flat list of strings:
```json
["You should be up by now. What's the plan for today?"]
```

`pop_pending_messages()` returns the list and immediately clears the file — messages are delivered exactly once.

`get_today_summary()` returns a plain-text string like: *"Today (2026-03-27) the user has logged: finished the log UI; wrote commit notes"* — this gets injected into Anyanwu's 9pm context.

### System Prompt: `system_prompt.py`

The core of Anyanwu's personality. The full prompt covers:

1. **Identity** — big sister, not therapist, not a customer service bot
2. **Voice rules** — short, direct, casual, no lists ever, one question at the end
3. **Banned phrases** — an explicit list: "It's really brave of you", "Practice self-compassion", "What emotions come up for you", "Let's explore that", "I hear you", "Hold space", "Unpack", "Validate", and more
4. **Tone examples** — before/after pairs showing exactly what BAD looks like vs. what GOOD looks like. These mirror the actual patterns the model defaulted to before the overhaul.
5. **Core directive** — "You are not here to make the user feel better about staying stuck. You are here to move them."

The prompt was overhauled after reviewing `memory.json` and seeing that every response had numbered lists and therapy phrases, even though the original prompt explicitly banned them. The new prompt is more aggressive: it names banned phrases individually, shows examples of them being used wrong, and makes the no-lists rule impossible to miss.

---

## Frontend — How It Works

### `index.html`

Single-page app. One `div.chat-container` holds everything: the `h1` header, the `div.chat-box` for messages, the `div.log-panel` for the activity log, and the `div.input-area` at the bottom.

Structure:
```
.chat-container
  h1 — "ANYANWU"
  .chat-box — chat messages live here
  .log-panel — activity log panel (toggled, replaces chat-box)
    .log-header — "TODAY'S LOG"
    .log-entries — scrollable list of entries
    .log-input-row — quick-add input + ADD button
  .input-area
    #user-input — text field
    #log-btn — toggles log panel
    #send-btn — sends chat message ("RUN")
```

### `script.js`

All frontend logic. Key functions:

**Chat:**
- `loadStoredMessages()` — reads `localStorage` on page load and repopulates the chat box without re-saving
- `saveMessage(sender, text, type)` — pushes to `storedMessages` array and writes to `localStorage`
- `sendMessage()` — reads input, calls `POST /chat`, appends both user message and Anyanwu's reply
- `appendMessage(sender, text, type, save)` — creates DOM elements safely (no `innerHTML` — XSS fixed). `save` parameter prevents double-saving when loading from localStorage

**Scheduled messages:**
- `checkScheduledMessages()` — runs on page load, calls `GET /check-in`, appends any pending messages as bot messages

**Log panel:**
- `toggleLog()` — toggles `.log-panel.active` and hides/shows `.chat-box`. Also toggles `.active` on the LOG button for styling. Calls `loadTodayLog()` when opening.
- `loadTodayLog()` — calls `GET /log?day=YYYY-MM-DD`, renders entries or empty/error state
- `addLogEntry()` — calls `POST /log`, clears input, re-renders list

**Event listeners:**
- Send button click → `sendMessage()`
- Enter on chat input → `sendMessage()`
- LOG button click → `toggleLog()`
- ADD button click → `addLogEntry()`
- Enter on log input → `addLogEntry()`

### `style.css` — Night Pink Theme

Visual identity: dark background (`#0d0d0d`), deep charcoal container (`#181818`), pink accent (`#E06196`), light pink text (`#FFC1EF`), purple-tinted borders (`#442342`). Subtle diagonal grid pattern on the body background.

Two fonts: **Orbitron** (geometric, sci-fi — used for headers and buttons) and **Space Mono** (monospace — used for all text content).

The container is responsive: `width: 90%; max-width: 440px; height: 90vh; max-height: 720px`. Was previously fixed at `380px × 640px`.

Message types:
- `.user` — right-aligned, dark pink background, pink border
- `.bot` — left-aligned, dark background, pink left border accent
- `.system` — centered, very muted, used for error states

Log panel matches the chat aesthetic: same scrollbar, same font, same color language. LOG button is intentionally muted (60% opacity) compared to RUN, brightens on hover and when active.

### PWA Files

**`manifest.json`** — declares the app's name, icons, theme color, and `display: standalone` so it runs without browser chrome when installed. Not yet fully active.

**`service_worker.js`** — exists but is not yet registered. Offline caching and push notifications require HTTPS, which requires deployment. This gets activated in Part 3.

---

## Security Decisions

### XSS fixed
`appendMessage()` originally used `innerHTML` to render messages. Replaced with `createElement`, `textContent`, and `createTextNode`. User input cannot inject HTML or scripts into the page.

### CORS locked down
Was `allow_origins=["*"]`. Now reads from `ALLOWED_ORIGINS` env var. Only the frontend origin can call the backend. Methods and headers are narrowed to exactly what's needed.

### Input length cap
Messages over 2000 characters return HTTP 400. Prevents unexpected OpenAI token overruns and potential abuse.

### Data gitignored
`memory.json`, `daily_log.json`, and `pending_messages.json` are all gitignored. Conversation history and activity data don't end up in version control.

### No secrets in code
`OPENAI_API_KEY` lives in `.env` only. `python-dotenv` loads it at runtime.

---

## Data Flow — A Full Request

1. User types a message and presses Enter or clicks RUN
2. `sendMessage()` appends the user message to the chat box and saves it to `localStorage`
3. `fetch POST /chat` hits the FastAPI backend
4. `chat_with_anyanwu()` loads history from `memory.json`, appends the new message, sends to OpenAI
5. OpenAI returns a reply — history is saved back to `memory.json`
6. Reply comes back to the frontend, `appendMessage()` renders it and saves to `localStorage`

---

## Data Flow — Scheduled Message Delivery

1. APScheduler fires `morning_checkin()` at 5am on the server
2. `queue_pending_message()` writes the message string to `pending_messages.json`
3. User opens the app — `checkScheduledMessages()` runs immediately
4. `fetch GET /check-in` hits the backend, `pop_pending_messages()` returns the list and clears the file
5. Each message is appended to the chat as a bot message

---

## Running Locally

```bash
# 1. Activate venv (the venv is named "ogenv" in this project)
source ogenv/bin/activate

# 2. Start the backend (from project root)
uvicorn backend.main:app --reload

# 3. Start the frontend (separate terminal)
cd frontend
python3 -m http.server 3000
```

Open `http://localhost:3000`.

**Environment variables (`.env`):**
```
OPENAI_API_KEY=your_key_here
ANYANWU_MODEL=gpt-4o-mini          # optional
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000  # optional override
```

---

## What's Complete

- [x] FastAPI backend with OpenAI integration
- [x] Anyanwu's personality — system prompt overhauled, no more therapist-speak
- [x] Conversation memory — 500-message rolling window in `memory.json`
- [x] Chat UI — vanilla JS, Night Pink theme, localStorage persistence
- [x] XSS fix — safe DOM rendering
- [x] CORS lockdown — env-based allowed origins
- [x] Responsive layout — adapts to phone and desktop
- [x] Daily reminder system — 5am wake-up, 9pm check-in via APScheduler
- [x] Activity log backend — `/log` POST and GET endpoints
- [x] Activity log UI — LOG panel with quick-add, today's entries, toggle from chat
- [x] PWA groundwork — manifest.json and service_worker.js in place

---

## What's Next (Part 3)

### 1. Deploy backend to Render
- `pip freeze > requirements.txt` to pin versions
- Create Web Service on Render, connect GitHub repo
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- Set `OPENAI_API_KEY` as environment variable on Render
- Render gives you a URL like `https://your-app.onrender.com`

### 2. Deploy frontend to Vercel or Netlify
- Update `BACKEND_URL` in `script.js` to the Render URL
- Update `ALLOWED_ORIGINS` on Render to include the Vercel/Netlify URL
- Deploy the `frontend/` folder as a static site

### 3. Activate the PWA
- Register the service worker in `index.html` (the script is already written)
- Add caching strategy to `service_worker.js`
- Test install prompt on mobile
- App icon on home screen, standalone mode (no browser chrome)

### 4. Push notifications
- Requires HTTPS (handled by deployment) + registered service worker
- User subscribes to push via the browser Push API
- Backend sends pushes via Web Push protocol instead of just queuing to JSON
- This replaces the current "messages appear when you open the app" system with real phone alerts

### 5. User profile (stretch)
- Name, goals, background — stored and injected into Anyanwu's context
- Makes her responses more specific and personal over time

### 6. Weekly digest (stretch)
- Every Sunday, auto-generate a summary of the week's logged activities
- Useful for job application prep, presentations, performance reviews

---

## The Medium Series Arc

**Part 1 — The Brain**
Focus: What makes Anyanwu different. The system prompt as the real product. How the memory system works. OpenAI integration from scratch with FastAPI.

**Part 2 — The Face**
Focus: Building a chat UI that matches the persona. CSS theming, localStorage persistence, PWA concepts (manifest, what a service worker does and why we need HTTPS for it to matter).

**Part 3 — The Deployment**
Story hook: *"It only lives on my laptop right now."*
Arc: tunneling via ngrok to show it on a phone → proper backend deployment on Render → frontend on Vercel → real PWA install on the home screen → push notifications that work without the app being open.

---

*Last updated: March 2026*