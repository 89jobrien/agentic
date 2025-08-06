import pytest
from src.agentic.session_store import SessionStore
from src.agentic.models import Message

@pytest.mark.asyncio
async def test_session_store_get_set(mock_session_store):
    session_id = "testid"
    messages = [Message(role="user", content="hi")]
    await mock_session_store.set(session_id, messages)
    mock_session_store._redis.set.assert_called_once()
    # Simulate get
    mock_session_store._redis.get.return_value = '[{"role": "user", "content": "hi"}]'
    result = await mock_session_store.get(session_id)
    assert isinstance(result, list)
    assert result[0].role == "user"

@pytest.mark.asyncio
async def test_session_store_close(mock_session_store):
    await mock_session_store.close()
    mock_session_store._redis.close.assert_called_once()
