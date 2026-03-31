# CLAUDE.md — Anyanwu AI Coach

## What This Project Is

Anyanwu is a personalized AI life coaching chat app. The persona is a "big sister coach" — direct, warm, zero fluff — not a therapist or generic chatbot. Built and documented publicly as a 3-part Medium series by @yomacorp.

**Series arc:**
- Part 1 (published): The Brain — FastAPI backend, Anyanwu's personality, AI prompt + response logic
- Part 2 (published): The Face — Chat UI, localStorage, PWA concepts (manifest, service worker)
- Part 3 (in progress): Deployment — Taking it from localhost to a real accessible app (tunneling → Render/Railway backend, Vercel/Netlify frontend, real PWA install)

---

## Tech Stack

| Layer | Tech |
|---|---|
| Backend | Python, FastAPI, uvicorn |
| AI | OpenAI API (gpt-4o-mini by default) |
| Memory | JSON file (`backend/data/memory.json`) |
| Daily Log | JSON file (`backend/data/daily_log.json`) |
| Frontend | Vanilla JS, HTML5, CSS3 |
| PWA | manifest.json, service_worker.js (not yet active) |
| Environment | python-dotenv, `.env` for API key |

---

## Key Files

```
AnyanwuAICoach/
├── backend/
│   ├── main.py                    # FastAPI app, routes, CORS, input validation
│   ├── services/
│   │   ├── ai_agent.py            # chat_with_anyanwu() — OpenAI call + memory
│   │   ├── memory_manager.py      # load/save conversation history (500 msg cap)
│   │   ├── scheduler.py           # APScheduler — 5am wake-up, 9pm check-in
│   │   └── daily_log.py           # Daily activity log manager
│   ├── utils/
│   │   └── system_prompt.py       # Anyanwu's full personality prompt
│   └── data/
│       ├── memory.json            # Conversation history (gitignored)
│       ├── daily_log.json         # Daily activity entries (gitignored)
│       └── pending_messages.json  # Scheduled messages queue (gitignored)
├── frontend/
│   ├── index.html
│   ├── script.js
│   ├── style.css
│   ├── manifest.json
│   └── service_worker.js
├── requirements.txt
├── .env                           # gitignored — contains OPENAI_API_KEY
├── .gitignore
├── COMMIT_NOTES.md                # Pre-commit changelog (can delete after committing)
└── CLAUDE.md                      # This file
```

---

## Running Locally

```bash
# Backend (from project root)
source ogenv/bin/activate
uvicorn backend.main:app --reload

# Frontend (separate terminal)
cd frontend
python3 -m http.server 3000
```

Then open `http://localhost:3000`.

**Environment variables** (in `.env`):
```
OPENAI_API_KEY=your_key_here
ANYANWU_MODEL=gpt-4o-mini         # optional override
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000  # optional override
```

---

## Fixes Made (March 2026)

### Security
- **XSS fixed** — `appendMessage()` was using `innerHTML` with user input. Replaced with safe DOM methods (`createElement`, `textContent`, `createTextNode`).
- **CORS locked down** — Was `allow_origins=["*"]`. Now reads from `ALLOWED_ORIGINS` env var. Defaults include localhost with port 3000. `allow_methods` and `allow_headers` narrowed to only what's needed.

### Code quality
- **Hardcoded backend URL removed** — `http://127.0.0.1:8000` moved to `const BACKEND_URL` at top of `script.js`.
- **Input length limit** — Messages over 2000 chars now return HTTP 400.
- **ChromaDB removed** — Was in `requirements.txt` but never imported. Removing saves significant install time.
- **Dead service worker code removed** — Commented-out SW registration was cluttering `script.js`.

### UI
- **Responsive layout** — Fixed `380px × 640px` replaced with `width: 90%; max-width: 420px; height: 90vh; max-height: 700px`.

### Privacy
- **`memory.json` gitignored** — Conversation history no longer tracked in git. Run `git rm --cached backend/data/memory.json` to scrub it from history.

### Anyanwu's tone
- **System prompt overhauled** — The old prompt had the right intent but the model kept defaulting to therapist-speak. The `memory.json` showed every response had numbered lists, phrases like "It's really brave of you", "Practice self-compassion", "What emotions come up for you" — all explicitly banned in the old prompt but ignored.
- New prompt explicitly lists banned phrases by name, adds before/after examples mirroring what the model was actually doing wrong, and makes the no-lists rule impossible to miss.

---

## Reminder & Daily Log System (March 2026)

Anyanwu sends two scheduled messages daily:
- **5:00 AM** — Wake-up nudge ("You should be up by now.")
- **9:00 PM** — End-of-day check-in ("What did you do today?")

These are stored as pending messages in `backend/data/pending_messages.json`. When the user opens the app, the frontend calls `/check-in` and any pending messages from Anyanwu appear automatically.

The daily log (`/log` endpoint) accumulates what the user has done each day. This feeds into Anyanwu's context so she can reference recent activity, and it builds a record the user can export for job applications or presentations.

**Push notifications** (real phone alerts) are deferred to Part 3 — they require HTTPS + service worker, which needs deployment first.

---

## Current Status (March 2026)

All features through Part 2 are complete. The activity log UI was the last feature before deployment. The project is now ready for Part 3.

**What was just built (log UI):**
- LOG button in the input bar (styled distinct from RUN — muted, brightens when active)
- `.log-panel` that toggles in place of `.chat-box` — restores chat when closed
- `loadTodayLog()` — calls `GET /log?day=YYYY-MM-DD`, renders entries or empty/error state
- `addLogEntry()` — calls `POST /log`, clears input, re-renders list
- Enter key works on log input

**Roadmap status:**
- [x] FastAPI backend + OpenAI integration
- [x] Chat UI with localStorage persistence
- [x] Conversation memory (500 msg rolling window)
- [x] Daily scheduled reminders (5am + 9pm)
- [x] Activity log backend (`/log` POST + GET)
- [x] Activity log UI (LOG panel in the chat)
- [ ] Deploy backend (Render) — **this is next**
- [ ] Deploy frontend (Vercel / Netlify)
- [ ] Real PWA — install prompt, home screen, standalone mode
- [ ] Push notifications (requires HTTPS + deployed service worker)

**For full detail on everything built:** see `PROJECT_OVERVIEW.md`

---

## Part 3 Deployment Plan

The goal is to take Anyanwu from `localhost` to a real accessible URL.

**Backend:** Deploy to Render, Railway, or Fly.io (FastAPI + uvicorn)
**Frontend:** Deploy to Vercel, Netlify, or GitHub Pages (static files)
**Key change:** `BACKEND_URL` in `script.js` and `ALLOWED_ORIGINS` in `.env` need to point to production URLs

**Story hook for the article:** "It only lives on my laptop." → tunneling (ngrok/cloudflare) → proper deployment → real PWA install on phone

**PWA becomes real in Part 3:**
- Service worker caching that actually works
- Install prompt on mobile
- Home screen icon
- Standalone mode
- Push notifications (requires HTTPS + deployed backend)

---

## Anyanwu's Personality — Key Rules

- Talk like a real person texting their sister. Short. Direct. Casual.
- **No lists. Ever.** Not numbered, not bulleted, not "here are a few things."
- One clear take. One question at the end. That's it.
- Banned phrases (see `system_prompt.py` for full list): "It's really brave", "Practice self-compassion", "What emotions come up", "Let's explore that", "I hear you", "Hold space", etc.
- Push. Notice avoidance. Name it. Don't let them stay comfortable in the problem.
