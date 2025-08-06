import pytest
from unittest.mock import patch
import src.agentic.embeddings.ollama  # Import the module, not the function

@pytest.mark.asyncio
@patch('src.agentic.embeddings.ollama.get_ollama_embedding', return_value=[0.1, 0.2, 0.3])
async def test_get_ollama_embedding(mock_embed):
    emb = await src.agentic.embeddings.ollama.get_ollama_embedding("hello world")
    assert isinstance(emb, list)
    assert emb == [0.1, 0.2, 0.3]
