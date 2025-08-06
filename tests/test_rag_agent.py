import pytest
from src.agentic.agents.rag_agent import RAGAgent
from src.agentic.models import Message

@pytest.mark.asyncio
async def test_rag_agent_run_rag_chat(mock_db_pool, patch_ollama_embedding, patch_azure_chat, patch_config):
    agent = RAGAgent(db_pool=mock_db_pool)
    # Mock DB returns two code chunks
    mock_db_pool.fetch.return_value = [
        {"file_path": "foo.py", "chunk": "def foo(): pass"},
        {"file_path": "bar.py", "chunk": "def bar(): pass"},
    ]
    messages = [Message(role="user", content="What does foo do?")]
    reply = await agent.run_rag_chat(messages)
    assert reply == "Test Azure reply"
    mock_db_pool.fetch.assert_called()

@pytest.mark.asyncio
async def test_rag_agent_no_user_message(mock_db_pool, patch_config):
    agent = RAGAgent(db_pool=mock_db_pool)
    messages = []
    result = await agent.run_rag_chat(messages)
    assert "Please provide a user message." in result
