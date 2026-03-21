# Commit Notes — What's in this commit (Major Changes)

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
