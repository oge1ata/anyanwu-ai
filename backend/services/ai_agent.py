import os
from dotenv import load_dotenv
from openai import OpenAI
from typing import Optional
import logging

from backend.utils.system_prompt import SYSTEM_PROMPT
from backend.services.memory_manager import load_memory, add_message

# Load .env file
load_dotenv()

# Initialize client if API key present
_API_KEY = os.getenv("OPENAI_API_KEY")
client: Optional[OpenAI]
if _API_KEY:
    client = OpenAI(api_key=_API_KEY)
else:
    client = None

# Configurable model and context size
MODEL = os.getenv("ANYANWU_MODEL", "gpt-4o-mini")
MAX_MEMORY_CONTEXT = 10

def chat_with_anyanwu(user_message: str):
    history = load_memory()

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history[-MAX_MEMORY_CONTEXT:])  # memory
    messages.append({"role": "user", "content": user_message})

    if client is None:
        logging.error("OpenAI API key not configured.")
        raise RuntimeError("OpenAI API key not configured")

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.7
        )

        # Safely extract reply
        reply = None
        choices = getattr(response, "choices", None)
        if choices and len(choices) > 0:
            msg = getattr(choices[0], "message", None)
            if msg is not None and getattr(msg, "content", None) is not None:
                reply = msg.content

        if not reply:
            logging.warning("Empty reply from OpenAI, returning fallback message.")
            reply = "I'm sorry — I couldn't generate a response right now."

    except Exception as e:
        logging.exception("OpenAI request failed")
        return "⚠️ Anyanwu couldn't reach the assistant right now. Try again later."

    # Persist conversation (only if reply was generated)
    add_message("user", user_message)
    add_message("assistant", reply)

    return reply
