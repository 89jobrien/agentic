from types import SimpleNamespace
from src.agentic.api.v1.deps import get_rag_agent, get_conversational_agent, get_session_store

def test_deps_return_from_app_state():
    dummy = object()
    req = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(
        rag_agent=dummy, conversational_agent=dummy, session_store=dummy
    )))
    assert get_rag_agent(req) is dummy
    assert get_conversational_agent(req) is dummy
    assert get_session_store(req) is dummy
