from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.services.ai_agent import chat_with_anyanwu
from pydantic import BaseModel


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # OK for local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatExampleRequest(BaseModel):
    message: str


@app.get("/")
def home():
    return {"message": "🌞 Anyanwu AI Coach is alive and shining!"}

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_input = data.get("message")

    if not user_input:
        raise HTTPException(status_code=400, detail="No message provided")

    reply = chat_with_anyanwu(user_input)
    return {"reply": reply}

@app.post("/chat/example")
def chat_example(payload: ChatExampleRequest):
    reply = chat_with_anyanwu(payload.message)

    return {
        "assistant": "Anyanwu",
        "user_message": payload.message,
        "reply": reply
    }
