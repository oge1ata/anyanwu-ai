# ANYANWU — AI Coach

> A big sister. A coach. A system that doesn't let you off easy.

Anyanwu is a personal AI coaching app built to push you forward — not comfort you in place. She's direct, warm, and relentless about forward motion. Not a chatbot. Not a therapist. A big sister who's been through it and tells it straight.

Built and documented as a public series on Medium: [Part 1](https://medium.com/@yomacorp/️building-anyanwu-part-one-d53b445afb80) · [Part 2](https://medium.com/@yomacorp/️building-anyanwu-the-face-256cf4c7239a) · Part 3 (coming soon)

---

## What It Does

- Coaches you through procrastination, fear of failure, and avoidance — without sugarcoating
- Sends a **5am wake-up** and **9pm check-in** every day
- Tracks what you've done daily so you have a record for job applications and presentations
- Remembers your conversation history across sessions
- Runs as a chat interface in the browser, built to become a full PWA

---

## Tech Stack

| Layer | Tech |
|---|---|
| Backend | Python, FastAPI, uvicorn |
| AI | OpenAI API (gpt-4o-mini) |
| Scheduler | APScheduler (5am/9pm reminders) |
| Memory | JSON file storage |
| Frontend | Vanilla JS, HTML5, CSS3 |
| Fonts | Orbitron + Space Mono |

---

## Project Structure

```
AnyanwuAICoach/
├── backend/
│   ├── main.py                    # FastAPI app — routes, CORS, input validation
│   ├── services/
│   │   ├── ai_agent.py            # OpenAI call + memory context
│   │   ├── memory_manager.py      # Conversation history (500 msg cap)
│   │   ├── scheduler.py           # 5am + 9pm scheduled messages
│   │   └── daily_log.py           # Activity log manager
│   ├── utils/
│   │   └── system_prompt.py       # Anyanwu's personality
│   └── data/                      # Runtime data (gitignored)
│       ├── memory.json
│       ├── daily_log.json
│       └── pending_messages.json
├── frontend/
│   ├── index.html
│   ├── script.js
│   ├── style.css                  # Night Pink theme
│   ├── manifest.json
│   └── service_worker.js
├── requirements.txt
├── .env                           # gitignored
└── CLAUDE.md                      # Project context for AI assistant
```

---

## Running Locally

**1. Clone and set up environment**

```bash
git clone https://github.com/<your-username>/anyanwu-ai.git
cd anyanwu-ai
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**2. Add your API key**

Create a `.env` file in the root:

```
OPENAI_API_KEY=your_openai_key_here
```

**3. Start the backend**

```bash
uvicorn backend.main:app --reload
```

**4. Serve the frontend** (separate terminal)

```bash
cd frontend
python3 -m http.server 3000
```

Open `http://localhost:3000`.

---

## API Endpoints

| Method | Route | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `POST` | `/chat` | Send a message, get Anyanwu's reply |
| `GET` | `/check-in` | Fetch pending scheduled messages (clears on read) |
| `POST` | `/log` | Log an activity for today |
| `GET` | `/log` | Get full activity log (`?day=YYYY-MM-DD` for one day) |

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | — | Required. Your OpenAI key. |
| `ANYANWU_MODEL` | `gpt-4o-mini` | OpenAI model to use |
| `ALLOWED_ORIGINS` | `http://localhost:3000,...` | CORS allowed origins for production |

---

## Roadmap

- [x] FastAPI backend + OpenAI integration
- [x] Chat UI with localStorage persistence
- [x] Conversation memory (500 msg rolling window)
- [x] Daily scheduled reminders (5am + 9pm)
- [x] Activity log for tracking accomplishments
- [ ] Activity log UI (quick-log button in the chat)
- [ ] Deploy backend (Render / Railway)
- [ ] Deploy frontend (Vercel / Netlify)
- [ ] Real PWA — install prompt, home screen, standalone mode
- [ ] Push notifications (requires HTTPS + deployed service worker)
- [ ] User profile / persistent context (goals, name, background)
- [ ] Weekly digest — auto-generated summary every Sunday

---

**Author:** Oge Anyanwu · [Medium](https://medium.com/@yomacorp) · MIT License
