import json
import threading
from datetime import date
from pathlib import Path

# Where we store the daily activity log and the queue of pending scheduled messages
LOG_PATH = Path(__file__).parent.parent / "data" / "daily_log.json"
PENDING_PATH = Path(__file__).parent.parent / "data" / "pending_messages.json"

# Thread lock so reading/writing files doesn't corrupt data if two requests hit at once
_lock = threading.Lock()


def _read_json(path: Path, default):
    """Read a JSON file, returning `default` if the file doesn't exist or is corrupt."""
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return default


def _write_json(path: Path, data):
    """Write data to a JSON file, creating parent directories if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


# ── Daily log ──────────────────────────────────────────────────────────────────

def add_log_entry(text: str):
    """
    Add an activity entry for today.
    The log is a dict keyed by date string: { "2026-03-21": ["did X", "did Y"], ... }
    This builds up a running record of what the user has accomplished each day.
    """
    today = str(date.today())
    with _lock:
        log = _read_json(LOG_PATH, {})
        if today not in log:
            log[today] = []
        log[today].append(text)
        _write_json(LOG_PATH, log)


def get_log(day: str = None) -> dict:
    """
    Return the full activity log, or just one day if `day` is provided (format: YYYY-MM-DD).
    Used by the /log GET endpoint so the user can review what they've done.
    """
    with _lock:
        log = _read_json(LOG_PATH, {})
    if day:
        return {day: log.get(day, [])}
    return log


def get_today_summary() -> str:
    """
    Return a plain-text summary of today's logged activity.
    This gets injected into Anyanwu's context on the 9pm check-in so she already
    knows what you've done and can ask about what's missing — not start from scratch.
    """
    today = str(date.today())
    with _lock:
        log = _read_json(LOG_PATH, {})
    entries = log.get(today, [])
    if not entries:
        return ""
    return f"Today ({today}) the user has logged: " + "; ".join(entries)


# ── Pending scheduled messages ─────────────────────────────────────────────────

def queue_pending_message(message: str):
    """
    Store a scheduled message from Anyanwu to be delivered next time the user opens the app.
    The scheduler calls this at 5am and 9pm — it doesn't push to the browser directly
    (that requires HTTPS + service worker, which needs deployment). Instead, messages
    sit here until the frontend polls /check-in on page load.
    """
    with _lock:
        pending = _read_json(PENDING_PATH, [])
        pending.append(message)
        _write_json(PENDING_PATH, pending)


def pop_pending_messages() -> list[str]:
    """
    Return all queued pending messages and clear the queue.
    Called by the /check-in endpoint — messages are delivered once and gone.
    """
    with _lock:
        pending = _read_json(PENDING_PATH, [])
        if pending:
            _write_json(PENDING_PATH, [])
        return pending
