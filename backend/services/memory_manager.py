import json
from pathlib import Path
from threading import Lock

# Use a path relative to this file so the code works regardless of CWD
MEMORY_FILE = Path(__file__).resolve().parents[1] / "data" / "memory.json"
MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)

# Simple in-process lock to reduce race conditions when writing the file.
_LOCK = Lock()
# Keep memory bounded to prevent unbounded file growth
MAX_MEMORY_MESSAGES = 500

def load_memory():
    if not MEMORY_FILE.exists():
        return []
    try:
        with MEMORY_FILE.open("r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # Corrupt or empty file — return empty history instead of raising
        return []

def save_memory(conversations):
    with MEMORY_FILE.open("w") as f:
        json.dump(conversations, f, indent=2)

def add_message(role, content):
    with _LOCK:
        memory = load_memory()
        memory.append({"role": role, "content": content})
        # truncate older messages if needed
        if len(memory) > MAX_MEMORY_MESSAGES:
            memory = memory[-MAX_MEMORY_MESSAGES:]
        save_memory(memory)
