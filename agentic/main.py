from fastapi import FastAPI, Request, HTTPException

from fastapi.responses import JSONResponse
from uuid import uuid4
from typing import List, Dict

from loguru import logger
from agentic.config import Config

from agentic.rag_agent import run_rag_query, run_rag_chat
from agentic.models import Message
from agentic.logging import setup_logging

setup_logging()

app = FastAPI(
    title="Agentic RAG Code Analysis API",
    description="Analyze code repos and suggest improvements using PydanticAI and FastAPI.",
    version="0.1.0",
)
Config.load()

sessions: Dict[str, List[Message]] = {}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Exception occurred", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"error": str(exc)},
    )

@app.get("/")
def root():
    return {"message": "Welcome to Agentic - RAG codebase analyzer."}


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/info")
def info():
    return {"version": "0.1.0"}

@app.post("/analyze")
async def analyze(request: Request):
    data = await request.json()
    question = data.get("question")
    if not question:
        return {"error": "Missing 'question' in request body."}
    result = await run_rag_query(question)
    return {"result": result}


@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    session_id = data.get("session_id")
    user_message = data.get("message")
    if not user_message:
        return {"error": "Missing 'message' in request body."}
    messages: List[Message]
    if not session_id:
        session_id = str(uuid4())
        messages = []
    else:
        messages = sessions.get(session_id, [])
    messages.append(Message(role="user", content=user_message))
    assistant_reply = await run_rag_chat(messages)
    messages.append(Message(role="assistant", content=assistant_reply))
    sessions[session_id] = messages
    try:
        history = [msg.model_dump() for msg in messages]
    except AttributeError:
        logger.error("Failed to serialize messages", exc_info=True)
        history = []
    return {
        "session_id": session_id,
        "reply": assistant_reply,
        "history": history,
    }
