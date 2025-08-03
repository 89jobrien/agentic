import asyncio
from agentic.embeddings.ollama import get_ollama_embedding


async def test():
    emb = await get_ollama_embedding("hello world")
    print(emb)


asyncio.run(test())
