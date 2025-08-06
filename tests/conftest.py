
import asyncio
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# --- Event loop fixture for async tests ---
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# --- Path fixtures ---
@pytest.fixture
def sample_repo_path(tmp_path):
    """Returns a temporary directory to act as a sample repo path."""
    return tmp_path / "repo"

@pytest.fixture
def sample_file(tmp_path):
    """Creates a sample Python file in a temp directory."""
    file = tmp_path / "test.py"
    file.write_text("def foo():\n    return 42\n")
    return file

# --- Pydantic model fixtures ---
@pytest.fixture
def sample_message():
    from src.agentic.models import Message
    return Message(role="user", content="Hello, world!")

@pytest.fixture
def sample_chat_request():
    from src.agentic.models import ChatRequest
    return ChatRequest(message="Test message", session_id=None)

@pytest.fixture
def sample_chat_response(sample_message):
    from src.agentic.models import ChatResponse
    return ChatResponse(session_id="abc123", reply="Hi!", history=[sample_message])

@pytest.fixture
def sample_embedding():
    from src.agentic.models import Embedding
    return Embedding(vector=[0.1, 0.2, 0.3])

@pytest.fixture
def sample_code_chunk(sample_embedding):
    from src.agentic.models import CodeChunk
    return CodeChunk(file_path="foo.py", chunk="def foo(): pass", embedding=sample_embedding)

# --- Asyncpg pool mock ---
@pytest.fixture
def mock_db_pool():
    pool = MagicMock()
    pool.fetch = AsyncMock()
    pool.execute = AsyncMock()
    pool.fetch.return_value = []
    return pool

# --- Redis/session store mock ---
@pytest.fixture
def mock_redis():
    redis = MagicMock()
    redis.get = AsyncMock()
    redis.set = AsyncMock()
    redis.close = AsyncMock()
    return redis

@pytest.fixture
def mock_session_store(mock_redis):
    from src.agentic.session_store import SessionStore
    store = SessionStore(redis_url="redis://localhost:6379/0")
    store._redis = mock_redis
    return store

# --- Patch config for isolation ---
@pytest.fixture(autouse=True)
def patch_config(monkeypatch):
    """Patch config to avoid loading real config files during tests."""
    with patch("src.agentic.config.config") as mock_config:
        mock_config.db.database_url = "postgresql://user:pass@localhost:5432/test"
        mock_config.db.redis_url = "redis://localhost:6379/0"
        mock_config.llm.ollama.embedding_url = "http://localhost:11434/api/embeddings"
        mock_config.llm.ollama.embedder_model = "nomic-embed-text"
        mock_config.llm.request_timeout = 5.0
        mock_config.llm.retriever_top_k = 3
        mock_config.llm.temperature = 0.0
        mock_config.rag.system_prompt = "You are a helpful assistant."
        mock_config.splitter.language = "python"
        mock_config.splitter.chunk_size = 40
        mock_config.splitter.chunk_overlap = 5
        mock_config.rag.ingestor_ignore_patterns = []
        yield mock_config

# --- Patch logger to silence output during tests ---
@pytest.fixture(autouse=True)
def silence_loguru(monkeypatch):
    with patch("loguru.logger.info"), patch("loguru.logger.success"), patch("loguru.logger.warning"), patch("loguru.logger.error"), patch("loguru.logger.trace"):
        yield

# --- Patch httpx.AsyncClient for embedding/chat API calls ---
@pytest.fixture
def patch_httpx_post(monkeypatch):
    """Patch httpx.AsyncClient.post to return a dummy embedding/chat response."""
    class DummyResponse:
        def __init__(self, json_data):
            self._json = json_data
        def raise_for_status(self): pass
        def json(self): return self._json

    async def dummy_post(*args, **kwargs):
        if "embeddings" in str(args[0]):
            return DummyResponse({"embedding": [0.1, 0.2, 0.3]})
        elif "chat/completions" in str(args[0]):
            return DummyResponse({"choices": [{"message": {"content": "Test reply"}}]})
        return DummyResponse({})

    monkeypatch.setattr("httpx.AsyncClient.post", dummy_post)
    yield

# --- Patch get_db_pool and close_db_pool for isolation ---
@pytest.fixture
def patch_db_pool(monkeypatch, mock_db_pool):
    monkeypatch.setattr("src.agentic.database.get_db_pool", AsyncMock(return_value=mock_db_pool))
    monkeypatch.setattr("src.agentic.database.close_db_pool", AsyncMock())
    yield

# --- Patch aioredis.from_url for session store isolation ---
@pytest.fixture
def patch_aioredis(monkeypatch, mock_redis):
    monkeypatch.setattr("aioredis.from_url", MagicMock(return_value=mock_redis))
    yield

# --- Patch Azure chat and Ollama embedding for agent tests ---
@pytest.fixture
def patch_azure_chat(monkeypatch):
    async def dummy_azure_chat(messages, temperature=0.0):
        return "Test Azure reply"
    monkeypatch.setattr("src.agentic.chat.azure.azure_chat", dummy_azure_chat)
    yield

@pytest.fixture
def patch_ollama_embedding(monkeypatch):
    async def dummy_embedding(text):
        return [0.1, 0.2, 0.3]
    monkeypatch.setattr("src.agentic.embeddings.ollama.get_ollama_embedding", dummy_embedding)
    yield

# --- Utility: Clean up temp files/dirs if needed ---
@pytest.fixture(autouse=True)
def cleanup_tmp_path(tmp_path):
    yield
    # Optionally, cleanup logic here if needed
