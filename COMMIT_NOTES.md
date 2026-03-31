# Commit Notes — What's in this commit (Major Changes)

---

## Log UI — Activity Panel (March 2026)

### New LOG button in the input bar (`frontend/index.html`, `frontend/style.css`, `frontend/script.js`)
The `/log` backend endpoint existed but had no UI. Added a full activity log panel that toggles in place of the chat window.

**What was built:**
- LOG button in the input area, visually distinct from RUN (muted pink, brightens when active)
- Full `.log-panel` that slides in when LOG is toggled — replaces the chat box, restores it when closed
- TODAY'S LOG header, a scrollable entry list, and a quick-add input with an ADD button
- `loadTodayLog()` — calls `GET /log?day=YYYY-MM-DD` on panel open, renders entries
- `addLogEntry()` — calls `POST /log`, clears the input, re-renders the list immediately
- Empty state: "nothing logged yet today." message when no entries exist
- Error state: graceful fallback if backend isn't running
- Enter key works on the log input (same as chat)

**Why this matters:** The 9pm check-in already reads from the daily log to give Anyanwu context. This gives the user a place to actually populate it from the UI, not just via API. It also builds toward the job-application record use case described in the Part 2 article.

---

## Daily Reminder System (March 2026 — previous commit)

### Scheduler added (`backend/services/scheduler.py`)
APScheduler runs two background jobs while FastAPI is live:
- **5:00 AM** — queues "You should be up by now. What's the plan for today?"
- **9:00 PM** — checks `daily_log.json` for today's entries and crafts a context-aware message. If nothing was logged, she calls that out. If things were logged, she asks what didn't get done.

### Daily log service added (`backend/services/daily_log.py`)
Manages two JSON files:
- `daily_log.json` — dict keyed by date string, each entry is a list of activity strings
- `pending_messages.json` — queue of scheduled messages waiting to be delivered

`get_today_summary()` formats today's log into plain text that gets injected into Anyanwu's context at 9pm, so she already knows what you did and can ask about what's missing.

### `/log` endpoints added (`backend/main.py`)
- `POST /log` — adds an activity entry for today (with empty-string validation)
- `GET /log` — returns full log or single day via `?day=YYYY-MM-DD`

### `/check-in` endpoint added (`backend/main.py`)
Called by the frontend on every page load. Returns pending scheduled messages and clears the queue so they only appear once.

### Frontend polling added (`frontend/script.js`)
`checkScheduledMessages()` runs on page load, fetches `/check-in`, and appends any pending messages to the chat as Anyanwu messages. Silently skips if the backend isn't running.

---

## Security Fixes

### XSS vulnerability fixed (`frontend/script.js`)
The `appendMessage` function was using `innerHTML` to render messages, which allows any HTML or script in a message to execute. Replaced with safe DOM methods (`createElement`, `textContent`, `createTextNode`). User input can no longer inject scripts into the page.

### CORS locked down (`backend/main.py`)
Was using `allow_origins=["*"]` which allows any website to call your backend. Now reads from an `ALLOWED_ORIGINS` environment variable, defaulting to `http://127.0.0.1,http://localhost`. Also narrowed `allow_methods` and `allow_headers` to only what's needed.

---

## Code Quality Fixes

### Hardcoded backend URL removed (`frontend/script.js`)
`http://127.0.0.1:8000` was buried inside the fetch call. Moved to a `const BACKEND_URL` at the top of the file so it's easy to change for deployment.

### Input length limit added (`backend/main.py`)
No limit on message size before — could hit OpenAI token limits unexpectedly or be abused. Now capped at 2000 characters with a proper 400 error response.

### ChromaDB removed (`requirements.txt`)
Was listed as a dependency but never used anywhere in the codebase. Removing it speeds up installs significantly (ChromaDB is a heavy package).

### Dead service worker code removed (`frontend/script.js`)
The service worker registration code was commented out but still sitting there. Removed it entirely. `service_worker.js` still exists if you want to re-enable offline support later — just add the registration back and uncomment it in the HTML.

---

## UI Fix

### Responsive layout (`frontend/style.css`)
Chat container was fixed at `380px × 640px` — looked fine on one screen size, bad everywhere else. Changed to `width: 90%; max-width: 420px; height: 90vh; max-height: 700px` so it adapts to different screen sizes and phones.

---

## Data / Privacy Fix

### `memory.json` added to `.gitignore`
Conversation history was being tracked in git. That's a privacy problem — every chat message would be in version control history. Added `backend/data/memory.json` to `.gitignore`. The file will still exist locally, it just won't be committed.

> Note: You'll want to also remove it from git history if this is going public:
> `git rm --cached backend/data/memory.json`

---

## Personality Fix

### System prompt overhauled (`backend/utils/system_prompt.py`)
The previous prompt was already written with the right intent but the model kept defaulting back to therapist-speak. Looking at `memory.json`, the actual responses had:
- Numbered bullet lists on every single message (explicitly banned in the old prompt)
- Therapy phrases: "It's really brave of you", "Practice self-compassion", "What emotions come up for you"
- Multiple questions at the end of every response
- Warm-up validation before getting to the point

The new prompt is much more aggressive about enforcement:
- Explicitly lists banned phrases with direct replacements
- Before/after examples mirror exactly what the model was doing wrong
- Removes ambiguity — "no lists ever, not numbered, not bulleted, not 'here are a few things'"
- Tightens the greeting example (the model was responding to "hi" like a customer service bot)
- Shifts framing from "don't do therapy" to "you are a big sister texting, not facilitating"
