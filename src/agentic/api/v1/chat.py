from fastapi import HTTPException, Depends, APIRouter
from uuid import uuid4

from agentic.rag_agent import RAGAgent
from agentic.models import Message
from agentic.session_store import SessionStore
from agentic.api.v1.deps import get_rag_agent, get_session_store


chat_router = APIRouter(tags=["Chat"])


@chat_router.post("/chat", tags=["Chat"])
async def chat(
    request_data: dict,
    agent: RAGAgent = Depends(get_rag_agent),
    store: SessionStore = Depends(get_session_store),
):
    """
    Handles a chat interaction with the RAG agent.
    It maintains conversation history using a session ID.
    """
    user_message = request_data.get("message")
    if not user_message:
        raise HTTPException(
            status_code=400, detail="Missing 'message' in request body."
        )

    session_id = request_data.get("session_id")
    if not session_id:
        session_id = str(uuid4())
        messages = []
    else:
        messages = await store.get(session_id)

    messages.append(Message(role="user", content=user_message))

    # Get the reply from the agent
    assistant_reply = await agent.run_rag_chat(messages)

    messages.append(Message(role="assistant", content=assistant_reply))

    # Save the updated conversation history
    await store.set(session_id, messages)

    return {
        "session_id": session_id,
        "reply": assistant_reply,
        "history": [msg.model_dump() for msg in messages],
    }
