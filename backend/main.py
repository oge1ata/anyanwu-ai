import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.services.ai_agent import chat_with_anyanwu
from backend.services.scheduler import start_scheduler, stop_scheduler
from backend.services.daily_log import add_log_entry, get_log, pop_pending_messages

MAX_MESSAGE_LENGTH = 2000


# ── App lifespan ───────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    FastAPI lifespan handler — code before `yield` runs on startup, after `yield` on shutdown.
    We start the APScheduler here so the 5am/9pm jobs are registered as soon as the app boots.
    """
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(lifespan=lifespan)


# ── CORS ───────────────────────────────────────────────────────────────────────

# Read allowed origins from environment so this works both locally and in production.
# Locally: frontend runs on port 3000. In production: set ALLOWED_ORIGINS to your deployed URL.
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://127.0.0.1,http://localhost,http://127.0.0.1:3000,http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)


# ── Models ─────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str

class LogRequest(BaseModel):
    entry: str


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/")
def home():
    return {"message": "🌞 Anyanwu AI Coach is alive and shining!"}


@app.post("/chat")
async def chat(request: Request):
    """Main chat endpoint. Accepts a message, returns Anyanwu's reply."""
    data = await request.json()
    user_input = data.get("message")

    if not user_input:
        raise HTTPException(status_code=400, detail="No message provided")

    if len(user_input) > MAX_MESSAGE_LENGTH:
        raise HTTPException(status_code=400, detail=f"Message too long (max {MAX_MESSAGE_LENGTH} characters)")

    reply = chat_with_anyanwu(user_input)
    return {"reply": reply}


@app.get("/check-in")
def check_in():
    """
    Called by the frontend on every page load.
    Returns any pending scheduled messages (5am wake-up, 9pm check-in) that fired
    while the app wasn't open, then clears the queue so they only show once.
    """
    messages = pop_pending_messages()
    return {"messages": messages}


@app.post("/log")
def log_activity(payload: LogRequest):
    """
    Log an activity entry for today.
    The user (or the frontend) calls this to record what they did.
    These entries feed into Anyanwu's 9pm check-in context and build the long-term
    record that can be used for job applications or presentations.
    """
    if not payload.entry.strip():
        raise HTTPException(status_code=400, detail="Entry cannot be empty")
    add_log_entry(payload.entry.strip())
    return {"status": "logged"}


@app.get("/log")
def get_activity_log(day: str = None):
    """
    Retrieve the activity log.
    Pass ?day=YYYY-MM-DD for a specific day, or nothing for the full history.
    """
    return get_log(day)
