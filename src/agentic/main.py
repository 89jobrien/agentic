from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from loguru import logger

from agentic.config import config
from agentic.rag_agent import RAGAgent
from agentic.session_store import SessionStore
from agentic.database import get_db_pool, close_db_pool
from agentic.logger import setup_logging
from agentic.api.v1 import general_router, chat_router


setup_logging(config.logging)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Code to run on startup ---
    logger.info("Application starting up...")

    # Create and store the database pool in the app state
    db_pool = await get_db_pool()
    app.state.db_pool = db_pool

    # Create and store the RAG agent instance
    app.state.rag_agent = RAGAgent(db_pool=db_pool, config_obj=config)
    logger.info("RAG Agent initialized.")

    # Create and store the session store
    app.state.session_store = SessionStore(redis_url=config.db.redis_url)
    logger.info("Session store initialized.")

    yield

    logger.info("Application shutting down...")
    await close_db_pool()
    await app.state.session_store.close()
    logger.info("Resources cleaned up.")


app = FastAPI(
    title="Agentic RAG Code Analysis API",
    description="Analyze code repos and suggest improvements using a RAG agent.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(general_router)
app.include_router(chat_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"An unhandled exception occurred: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."},
    )


# def get_rag_agent(request: Request) -> RAGAgent:
#     """Dependency to get the shared RAGAgent instance."""
#     return request.app.state.rag_agent


# def get_session_store(request: Request) -> SessionStore:
#     """Dependency to get the shared SessionStore instance."""
#     return request.app.state.session_store


# @app.get("/", tags=["General"])
# def root():
#     return {"message": "Welcome to Agentic - RAG codebase analyzer."}


# @app.get("/health", tags=["General"])
# def health():
#     return {"status": "ok"}


# @app.post("/chat", tags=["Chat"])
# async def chat(
#     request_data: dict,
#     agent: RAGAgent = Depends(get_rag_agent),
#     store: SessionStore = Depends(get_session_store),
# ):
#     """
#     Handles a chat interaction with the RAG agent.
#     It maintains conversation history using a session ID.
#     """
#     user_message = request_data.get("message")
#     if not user_message:
#         raise HTTPException(
#             status_code=400, detail="Missing 'message' in request body."
#         )

#     session_id = request_data.get("session_id")
#     if not session_id:
#         session_id = str(uuid4())
#         messages = []
#     else:
#         messages = await store.get(session_id)

#     messages.append(Message(role="user", content=user_message))

#     # Get the reply from the agent
#     assistant_reply = await agent.run_rag_chat(messages)

#     messages.append(Message(role="assistant", content=assistant_reply))

#     # Save the updated conversation history
#     await store.set(session_id, messages)

#     return {
#         "session_id": session_id,
#         "reply": assistant_reply,
#         "history": [msg.model_dump() for msg in messages],
#     }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "agentic.main:app",
        host=config.server.host,
        port=config.server.port,
        reload=config.server.reload,
    )
