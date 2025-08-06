import pytest
from src.agentic.embeddings.ollama import get_ollama_embedding

@pytest.mark.asyncio
async def test_get_ollama_embedding(patch_ollama_embedding):
    emb = await get_ollama_embedding("hello world")
    assert isinstance(emb, list)
    assert emb == [0.1, 0.2, 0.3]
