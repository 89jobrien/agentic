from fastapi import Request
from agentic.rag_agent import RAGAgent
from agentic.session_store import SessionStore
from agentic.conversational_agent import ConversationalAgent

def get_rag_agent(request: Request) -> RAGAgent:
    """Dependency to get the shared RAGAgent instance."""
    return request.app.state.rag_agent

def get_conversational_agent(request: Request) -> ConversationalAgent:
    """Dependency to get the shared ConversationalAgent instance."""
    return request.app.state.conversational_agent

def get_session_store(request: Request) -> SessionStore:
    """Dependency to get the shared SessionStore instance."""
    return request.app.state.session_store
