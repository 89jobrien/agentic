from fastapi import HTTPException, Depends, APIRouter
from uuid import uuid4
from loguru import logger

from src.agentic.rag_agent import RAGAgent
from src.agentic.models import Message, ChatRequest, ChatResponse
from src.agentic.session_store import SessionStore
from src.agentic.api.v1.deps import get_rag_agent, get_session_store
from src.agentic.conversational_agent import ConversationalAgent
from src.agentic.api.v1.deps import get_conversational_agent

chat_router = APIRouter(tags=["Chat"])


@chat_router.post(
    "/chat",
    response_model=ChatResponse,
    tags=["Chat"],
    summary="Chat with the RAG agent",
    response_description="The agent's reply and conversation history.",
)
async def chat(
    request_data: ChatRequest,
    agent: RAGAgent = Depends(get_rag_agent),
    store: SessionStore = Depends(get_session_store),
):
    """
    Handles a chat interaction with the RAG agent.

    Maintains conversation history using a session ID.  
    Returns the agent's reply and the full conversation history.

    - **message**: The user's message/question.
    - **session_id**: (Optional) The session to continue. If not provided, a new session is started.

    Returns:
        - **session_id**: The session identifier.
        - **reply**: The agent's reply.
        - **history**: The full conversation history as a list of Message objects.
    """
    try:
        user_message = request_data.message
        if not user_message:
            raise HTTPException(
                status_code=400, detail="Missing 'message' in request body."
            )

        session_id = request_data.session_id
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

        return ChatResponse(
            session_id=session_id,
            reply=assistant_reply,
            history=messages,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@chat_router.post(
    "/conversational-chat",
    response_model=ChatResponse,
    tags=["Chat"],
    summary="Chat with the Conversational AI agent (Azure OpenAI, no RAG)",
    response_description="The agent's reply and conversation history.",
)
async def conversational_chat(
    request_data: ChatRequest,
    agent: ConversationalAgent = Depends(get_conversational_agent),
    store: SessionStore = Depends(get_session_store),
):
    """
    Handles a chat interaction with the Conversational AI agent (Azure OpenAI, no retrieval).

    Maintains conversation history using a session ID.  
    Returns the agent's reply and the full conversation history.
    """
    try:
        user_message = request_data.message
        if not user_message:
            raise HTTPException(
                status_code=400, detail="Missing 'message' in request body."
            )

        session_id = request_data.session_id
        if not session_id:
            session_id = str(uuid4())
            messages = []
        else:
            messages = await store.get(session_id)

        messages.append(Message(role="user", content=user_message))

        # Get the reply from the agent
        assistant_reply = await agent.run_chat(messages)

        messages.append(Message(role="assistant", content=assistant_reply))

        # Save the updated conversation history
        await store.set(session_id, messages)

        return ChatResponse(
            session_id=session_id,
            reply=assistant_reply,
            history=messages,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Conversational chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
