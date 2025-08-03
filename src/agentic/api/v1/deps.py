from fastapi import Request
from agentic.rag_agent import RAGAgent
from agentic.session_store import SessionStore


def get_rag_agent(request: Request) -> RAGAgent:
    """Dependency to get the shared RAGAgent instance."""
    return request.app.state.rag_agent


def get_session_store(request: Request) -> SessionStore:
    """Dependency to get the shared SessionStore instance."""
    return request.app.state.session_store
