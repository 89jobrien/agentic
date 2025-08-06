import pytest
from unittest.mock import patch

from agentic.embeddings.ollama import get_ollama_embedding

@pytest.mark.asyncio
@patch('tests.test_embeddings_ollama.get_ollama_embedding', return_value=[0.1, 0.2, 0.3])
async def test_get_ollama_embedding(mock_embed):
    emb = await get_ollama_embedding("hello world")
    assert isinstance(emb, list)
    assert emb == [0.1, 0.2, 0.3]